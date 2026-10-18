import os
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from .common import OUTPUT, ROOT, canonical, file_sha, manifest, read_json, sha, write_json
from .provider import request_anthropic_direct, request_gemini_api, request_gemini_vertex, request_vertex
from .settings import model_settings
from .validation import parse_archive_response, parse_response


def prompt_data(target="archive"):
    if target == "archive":
        schema = read_json(ROOT / "config/archive.schema.json")
        template = (ROOT / "config/prompt_archive_v2.txt").read_text(encoding="utf-8")
        age_choices = [value for value in schema["properties"]["contributor"]["properties"]["age_bucket"]["enum"] if value is not None]
        return template.replace("{AGE_BUCKETS}", ", ".join(age_choices)), schema
    if target == "regions":
        labels = read_json(ROOT / "config/labels.json")["labels"]
        template = (ROOT / "config/prompt_v1.txt").read_text(encoding="utf-8")
        label_lines = "\n".join("- %s: %s" % (key, definition) for key, definition in labels.items())
        return template.replace("{LABELS}", label_lines), labels
    raise ValueError("target must be archive or regions")


def prompt_fingerprint(target="archive"):
    prompt, _ = prompt_data(target)
    schema_file = "archive.schema.json" if target == "archive" else "annotation.schema.json"
    fingerprint = {"system_prompt_sha256": sha(prompt), "schema_sha256": file_sha(ROOT / "config" / schema_file)}
    if target == "regions":
        fingerprint["labels_sha256"] = file_sha(ROOT / "config/labels.json")
    return fingerprint


def freeze_prompt(target="archive"):
    lock = {"target": target, "prompt_version": "archive_v2" if target == "archive" else "regions_v1", **prompt_fingerprint(target), "frozen_at": datetime.now(timezone.utc).isoformat()}
    lock_file = "prompt_archive.lock.json" if target == "archive" else "prompt.lock.json"
    write_json(ROOT / "config" / lock_file, lock)
    return lock


def predict(selected_doc=None, selected_model=None, phase="development", dry_run=False, resume=True, target="archive"):
    if phase not in ("development", "evaluation"):
        raise ValueError("phase must be development or evaluation")
    config = model_settings()
    prompt, contract = prompt_data(target)
    fingerprint = prompt_fingerprint(target)
    runner_versions = {"anthropic_sdk_version": anthropic.__version__, "runner_sha256": file_sha(Path(__file__)), "provider_adapter_sha256": file_sha(ROOT / "folklore_eval/provider.py"), "settings_loader_sha256": file_sha(ROOT / "folklore_eval/settings.py"), "validation_sha256": file_sha(ROOT / "folklore_eval/validation.py")}
    if phase == "evaluation":
        lock_path = ROOT / "config" / ("prompt_archive.lock.json" if target == "archive" else "prompt.lock.json")
        if not lock_path.exists():
            raise ValueError("Evaluation requires freeze-prompt first")
        lock = read_json(lock_path)
        if any(lock.get(k) != v for k, v in fingerprint.items()):
            raise ValueError("Prompt or schema changed since freeze-prompt for " + target)
    docs = manifest()
    if selected_doc:
        docs = [d for d in docs if d["doc_id"] == selected_doc]
        if not docs:
            raise ValueError("Unknown document: " + selected_doc)
    models = config["models"]
    if selected_model:
        if selected_model not in models:
            raise ValueError("Unknown model alias: " + selected_model)
        models = {selected_model: models[selected_model]}
    else:
        models = {alias: model for alias, model in models.items() if model.get("default", True)}
    project = os.getenv(config.get("project_env", "GOOGLE_CLOUD_PROJECT"))
    outcomes = []
    for doc in docs:
        input_path = OUTPUT / "inputs" / (Path(doc["doc_id"]).stem + ".json")
        if not input_path.exists():
            raise FileNotFoundError("Run prepare first: " + str(input_path))
        input_bytes = input_path.read_bytes()
        prepared = read_json(input_path)
        if prepared["pdf_sha256"] != file_sha(ROOT / doc["pdf"]):
            raise ValueError("PDF changed since prepare: " + doc["doc_id"])
        if target == "archive" and prepared.get("source_pdf") != doc["pdf"]:
            raise ValueError("Run prepare again to include source_pdf for archive output")
        # This user message contains only the prepared PDF text layer and geometry.
        user_input = input_bytes.decode("utf-8")
        for alias, model in models.items():
            provider = model.get("provider", config["provider"])
            location = model.get("location")
            provider_project = project if provider in ("anthropic_vertex", "gemini_vertex") else None
            request = {"model": model["id"], "max_tokens": config["generation"]["max_tokens"], "system": prompt, "messages": [{"role": "user", "content": user_input}]}
            if provider in ("anthropic_vertex", "gemini_vertex"):
                request["temperature"] = config["generation"]["temperature"]
            if model.get("thinking_level"):
                request["thinking_level"] = model["thinking_level"]
            cache_basis = {"target": target, "phase": phase, "provider": provider, "project_id": provider_project, "location": location, "request": request, "transport": config["transport"], **fingerprint, **runner_versions}
            key = sha(canonical(cache_basis))
            run_root = OUTPUT / "runs" / "archive" / phase if target == "archive" else OUTPUT / "runs" / phase
            run_dir = run_root / alias / Path(doc["doc_id"]).stem / key
            record_path = run_dir / "run.json"
            if resume:
                prior_records = list(run_dir.parent.glob(key + "-retry-*/run.json"))
                if record_path.exists():
                    prior_records.append(record_path)
                prior_records.sort(key=lambda path: path.stat().st_mtime, reverse=True)
                completed = next((path for path in prior_records if read_json(path).get("request_completed")), None)
                if completed:
                    outcomes.append({"doc_id": doc["doc_id"], "model": alias, "status": "resumed", "run": str(completed)})
                    continue
            # Keep every actual response, including invalid JSON and failed attempts.
            if record_path.exists():
                suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                run_dir = run_dir.with_name(run_dir.name + "-retry-" + suffix)
                record_path = run_dir / "run.json"
            envelope = {"target": target, "project_id": provider_project, "location": location, "provider": provider, "request": request}
            if dry_run:
                write_json(run_dir / "request.preview.json", envelope)
                outcomes.append({"doc_id": doc["doc_id"], "model": alias, "status": "dry_run", "request": str(run_dir / "request.preview.json")})
                continue
            if provider in ("anthropic_vertex", "gemini_vertex") and not project:
                raise ValueError("Set GOOGLE_CLOUD_PROJECT to a GCP project with Vertex model access")
            if provider == "anthropic_direct" and not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("Set ANTHROPIC_API_KEY to use the direct Anthropic API")
            if provider == "gemini_api" and not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
                raise ValueError("Set GEMINI_API_KEY to use the Google Gemini API")
            run_dir.mkdir(parents=True, exist_ok=True)
            write_json(run_dir / "request.json", envelope)
            if provider == "gemini_api":
                raw, latency, error, attempts = request_gemini_api(request, config["transport"])
            elif provider == "gemini_vertex":
                raw, latency, error, attempts = request_gemini_vertex(project, location, request, config["transport"])
            elif provider == "anthropic_direct":
                raw, latency, error, attempts = request_anthropic_direct(request, config["transport"])
            else:
                raw, latency, error, attempts = request_vertex(project, location, request, config["transport"])
            if raw is not None:
                write_json(run_dir / "response.json", raw)
            text_blocks = [block.get("text", "") for block in (raw or {}).get("content", []) if block.get("type") == "text"]
            raw_text = "".join(text_blocks)
            if raw is not None:
                (run_dir / "response.txt").write_text(raw_text, encoding="utf-8")
            if raw is None:
                parsed, validation_errors, json_parsed = None, [], False
            elif target == "archive":
                parsed, validation_errors, json_parsed = parse_archive_response(raw_text, contract, prepared["source_pdf"])
            else:
                parsed, validation_errors, json_parsed = parse_response(raw_text, contract, len(prepared["pages"]))
            stop_reason = (raw or {}).get("stop_reason")
            if stop_reason == "max_tokens":
                validation_errors.append("Output truncated at max_tokens")
                parsed = None
            if parsed is not None:
                write_json(run_dir / ("archive.json" if target == "archive" else "predictions.json"), parsed)
            record = {"target": target, "doc_id": doc["doc_id"], "model_alias": alias, "requested_model": model["id"], "returned_model": (raw or {}).get("model"), "provider": provider, "project_id": provider_project, "location": location, "phase": phase, "timestamp_utc": datetime.now(timezone.utc).isoformat(), "request_sha256": sha(canonical(request)), "input_sha256": sha(user_input), **fingerprint, **runner_versions, "cache_key": key, "generation": config["generation"], "transport": config["transport"], "latency_seconds": latency, "attempts": attempts, "usage": (raw or {}).get("usage"), "finish_reason": stop_reason, "truncated": stop_reason == "max_tokens", "request_completed": raw is not None, "json_parsed": json_parsed, "schema_compliant": parsed is not None, "errors": validation_errors, "request_error": error}
            write_json(record_path, record)
            outcome = {"doc_id": doc["doc_id"], "model": alias, "status": "complete" if raw else "transport_error", "run": str(record_path)}
            if error:
                outcome["error_category"] = error.get("category", "provider_error")
                outcome["error_message"] = error.get("message")
                outcome["next_step"] = error.get("next_step")
                if error.get("status_code") is not None:
                    outcome["http_status"] = error["status_code"]
                if error.get("provider_request_id"):
                    outcome["provider_request_id"] = error["provider_request_id"]
            outcomes.append(outcome)
    return outcomes

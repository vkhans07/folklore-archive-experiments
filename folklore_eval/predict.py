import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from .common import OUTPUT, ROOT, canonical, file_sha, manifest, read_json, run_directory, sha, write_json
from .provider import request_anthropic_direct, request_gemini_api, request_gemini_vertex, request_vertex
from .settings import model_settings
from .validation import parse_archive_response, parse_response


def resolve_prompt_version(target, prompt_version=None):
    versions = {"archive": ("archive_v2", "archive_v3"), "regions": ("regions_v1", "regions_v3", "regions_v4")}
    if target not in versions:
        raise ValueError("target must be archive or regions")
    version = prompt_version or versions[target][0]
    if version not in versions[target]:
        raise ValueError("Prompt version %s is incompatible with target %s" % (version, target))
    return version


def prompt_lock_file(target, prompt_version=None):
    version = resolve_prompt_version(target, prompt_version)
    return {"archive_v2": "prompt_archive.lock.json", "archive_v3": "prompt_archive_v3.lock.json",
            "regions_v1": "prompt.lock.json", "regions_v3": "prompt_regions_v3.lock.json",
            "regions_v4": "prompt_regions_v4.lock.json"}[version]


def prompt_data(target="archive", prompt_version=None):
    version = resolve_prompt_version(target, prompt_version)
    if target == "archive":
        schema = read_json(ROOT / "config/archive.schema.json")
        prompt_files = {"archive_v2": "prompt_archive_v2.txt", "archive_v3": "prompt_archive_v3_draft.txt"}
        if version not in prompt_files:
            raise ValueError("Unknown archive prompt version: " + version)
        template = (ROOT / "config" / prompt_files[version]).read_text(encoding="utf-8")
        age_choices = [value for value in schema["properties"]["contributor"]["properties"]["age_bucket"]["enum"] if value is not None]
        return template.replace("{AGE_BUCKETS}", ", ".join(age_choices)), schema
    if target == "regions":
        labels_file = "labels_regions_v4.json" if version == "regions_v4" else "labels.json"
        labels = read_json(ROOT / "config" / labels_file)["labels"]
        filename = {"regions_v1": "prompt_v1.txt", "regions_v3": "prompt_regions_v3.txt",
                    "regions_v4": "prompt_regions_v4.txt"}[version]
        template = (ROOT / "config" / filename).read_text(encoding="utf-8")
        label_lines = "\n".join("- %s: %s" % (key, definition) for key, definition in labels.items())
        return template.replace("{LABELS}", label_lines), labels
    raise ValueError("target must be archive or regions")


def prompt_fingerprint(target="archive", prompt_version=None):
    prompt, _ = prompt_data(target, prompt_version)
    schema_file = "archive.schema.json" if target == "archive" else "annotation.schema.json"
    fingerprint = {"system_prompt_sha256": sha(prompt), "schema_sha256": file_sha(ROOT / "config" / schema_file)}
    if target == "regions":
        labels_file = "labels_regions_v4.json" if resolve_prompt_version(target, prompt_version) == "regions_v4" else "labels.json"
        fingerprint["labels_sha256"] = file_sha(ROOT / "config" / labels_file)
    return fingerprint


def freeze_prompt(target="archive", prompt_version=None):
    version = resolve_prompt_version(target, prompt_version)
    lock = {"target": target, "prompt_version": version, **prompt_fingerprint(target, version), "frozen_at": datetime.now(timezone.utc).isoformat()}
    lock_file = prompt_lock_file(target, version)
    write_json(ROOT / "config" / lock_file, lock)
    return lock


def predict(selected_doc=None, selected_model=None, phase="development", dry_run=False, resume=True, target="archive", prompt_version=None,
            concurrency=1, timeout_seconds=None, max_attempts=None, initial_backoff_seconds=None):
    if phase not in ("development", "evaluation"):
        raise ValueError("phase must be development or evaluation")
    config = model_settings()
    if type(concurrency) is not int or concurrency < 1:
        raise ValueError("concurrency must be a positive integer")
    transport = dict(config["transport"])
    if timeout_seconds is not None:
        if timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")
        transport["timeout_seconds"] = float(timeout_seconds)
    if max_attempts is not None:
        if type(max_attempts) is not int or max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")
        transport["max_attempts"] = max_attempts
    if initial_backoff_seconds is not None:
        if initial_backoff_seconds < 0:
            raise ValueError("initial_backoff_seconds cannot be negative")
        transport["initial_backoff_seconds"] = float(initial_backoff_seconds)
    version = resolve_prompt_version(target, prompt_version)
    prompt, contract = prompt_data(target, version)
    fingerprint = prompt_fingerprint(target, version)
    runner_versions = {"anthropic_sdk_version": anthropic.__version__, "runner_sha256": file_sha(Path(__file__)), "provider_adapter_sha256": file_sha(ROOT / "folklore_eval/provider.py"), "settings_loader_sha256": file_sha(ROOT / "folklore_eval/settings.py"), "validation_sha256": file_sha(ROOT / "folklore_eval/validation.py")}
    if phase == "evaluation":
        lock_name = prompt_lock_file(target, version)
        lock_path = ROOT / "config" / lock_name
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
    tasks = []
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
            tasks.append((doc, alias, model, prepared, user_input))

    def run_task(task):
        doc, alias, model, prepared, user_input = task
        provider = model.get("provider", config["provider"])
        location = model.get("location")
        provider_project = project if provider in ("anthropic_vertex", "gemini_vertex") else None
        request = {"model": model["id"], "max_tokens": config["generation"]["max_tokens"], "system": prompt, "messages": [{"role": "user", "content": user_input}]}
        if provider in ("anthropic_vertex", "gemini_vertex"):
            request["temperature"] = config["generation"]["temperature"]
        if model.get("thinking_level"):
            request["thinking_level"] = model["thinking_level"]
        cache_basis = {"target": target, "phase": phase, "provider": provider, "project_id": provider_project, "location": location,
                       "request": request, "transport": transport, **fingerprint, **runner_versions}
        key = sha(canonical(cache_basis))
        run_root = run_directory(OUTPUT, phase, target, version)
        run_dir = run_root / alias / Path(doc["doc_id"]).stem / key
        record_path = run_dir / "run.json"
        if resume:
            prior_records = list(run_dir.parent.glob(key + "-retry-*/run.json"))
            if record_path.exists():
                prior_records.append(record_path)
            prior_records.sort(key=lambda path: path.stat().st_mtime, reverse=True)
            completed = next((path for path in prior_records if read_json(path).get("request_completed")), None)
            if completed:
                return {"doc_id": doc["doc_id"], "model": alias, "status": "resumed", "run": str(completed)}
        if record_path.exists():
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            run_dir = run_dir.with_name(run_dir.name + "-retry-" + suffix)
            record_path = run_dir / "run.json"
        envelope = {"target": target, "project_id": provider_project, "location": location, "provider": provider, "request": request}
        if dry_run:
            write_json(run_dir / "request.preview.json", envelope)
            return {"doc_id": doc["doc_id"], "model": alias, "status": "dry_run", "request": str(run_dir / "request.preview.json")}
        if provider in ("anthropic_vertex", "gemini_vertex") and not project:
            raise ValueError("Set GOOGLE_CLOUD_PROJECT to use Vertex")
        if provider == "anthropic_direct" and not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("Set ANTHROPIC_API_KEY to use the direct Anthropic API")
        if provider == "gemini_api" and not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Set GEMINI_API_KEY to use the Google Gemini API")
        run_dir.mkdir(parents=True, exist_ok=True)
        write_json(run_dir / "request.json", envelope)
        if provider == "gemini_api":
            raw, latency, error, attempts = request_gemini_api(request, transport)
        elif provider == "gemini_vertex":
            raw, latency, error, attempts = request_gemini_vertex(project, location, request, transport)
        elif provider == "anthropic_direct":
            raw, latency, error, attempts = request_anthropic_direct(request, transport)
        else:
            raw, latency, error, attempts = request_vertex(project, location, request, transport)
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
        record = {"target": target, "doc_id": doc["doc_id"], "model_alias": alias, "requested_model": model["id"],
                  "returned_model": (raw or {}).get("model"), "provider": provider, "project_id": provider_project,
                  "location": location, "phase": phase, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "request_sha256": sha(canonical(request)), "input_sha256": sha(user_input), **fingerprint, **runner_versions,
                  "cache_key": key, "generation": config["generation"], "transport": transport, "latency_seconds": latency,
                  "attempts": attempts, "usage": (raw or {}).get("usage"), "finish_reason": stop_reason,
                  "truncated": stop_reason == "max_tokens", "request_completed": raw is not None, "json_parsed": json_parsed,
                  "schema_compliant": parsed is not None, "errors": validation_errors, "request_error": error,
                  "max_concurrency": concurrency}
        record["prompt_version"] = version
        write_json(record_path, record)
        outcome = {"doc_id": doc["doc_id"], "model": alias, "status": "complete" if raw else "transport_error", "run": str(record_path)}
        if error:
            outcome.update({"error_category": error.get("category", "provider_error"), "error_message": error.get("message"),
                            "next_step": error.get("next_step")})
            if error.get("status_code") is not None:
                outcome["http_status"] = error["status_code"]
            if error.get("provider_request_id"):
                outcome["provider_request_id"] = error["provider_request_id"]
        print("Finished %s / %s: %s" % (alias, Path(doc["doc_id"]).stem, outcome["status"]), file=sys.stderr, flush=True)
        return outcome

    if concurrency == 1:
        return [run_task(task) for task in tasks]
    outcomes = [None] * len(tasks)
    with ThreadPoolExecutor(max_workers=min(concurrency, max(1, len(tasks)))) as executor:
        futures = {executor.submit(run_task, task): index for index, task in enumerate(tasks)}
        for future, index in futures.items():
            outcomes[index] = future.result()
    return outcomes

from collections import defaultdict
from pathlib import Path

from .common import OUTPUT, ROOT, evaluation_directory, manifest, read_json, write_json
from .evaluate import _csv
from .predict import prompt_fingerprint, resolve_prompt_version
from .settings import model_settings
from .matching import prf


def _estimate_request_cost(row, pricing_models):
    input_tokens, output_tokens = row.get("input_tokens"), row.get("output_tokens")
    cached_input_tokens, cache_write_5m, cache_write_1h, thinking_tokens = 0, 0, 0, 0
    response_path = Path(row["run_path"]).parent / "response.json" if row.get("run_path") else None
    if response_path is not None and response_path.exists():
        response = read_json(response_path)
        if response.get("provider_response"):
            provider_response = response["provider_response"]
            usage = provider_response.get("usage_metadata") or provider_response.get("usageMetadata")
            if usage is not None:
                input_tokens = usage.get("prompt_token_count", usage.get("promptTokenCount", input_tokens))
                output_tokens = usage.get("candidates_token_count", usage.get("candidatesTokenCount", output_tokens))
                cached_input_tokens = usage.get("cached_content_token_count", usage.get("cachedContentTokenCount", 0)) or 0
                thinking_tokens = usage.get("thoughts_token_count", usage.get("thoughtsTokenCount", 0)) or 0
                output_tokens = (output_tokens or 0) + thinking_tokens
            else:
                usage = provider_response.get("usage") or {}
                input_tokens = usage.get("input_tokens", input_tokens)
                output_tokens = usage.get("output_tokens", output_tokens)
                cached_input_tokens = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0
        else:
            usage = response.get("usage") or {}
            input_tokens = usage.get("input_tokens", input_tokens)
            output_tokens = usage.get("output_tokens", output_tokens)
            cached_input_tokens = usage.get("cache_read_input_tokens", 0) or 0
            creation = usage.get("cache_creation") or {}
            cache_write_5m = creation.get("ephemeral_5m_input_tokens", 0) or 0
            cache_write_1h = creation.get("ephemeral_1h_input_tokens", 0) or 0
            thinking_tokens = (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
    model = pricing_models.get(row.get("requested_model"))
    result = {"billable_input_tokens": None, "cached_input_tokens": None,
              "billable_output_tokens": None, "thinking_output_tokens": None,
              "estimated_input_cost_usd": None, "estimated_output_cost_usd": None,
              "estimated_cost_usd": None, "pricing_tier": None,
              "cache_storage_cost_included": False}
    if model is None or input_tokens is None or output_tokens is None:
        return result
    input_rate = model["input_per_million"]
    output_rate = model["output_per_million"]
    threshold = model.get("long_prompt_threshold_tokens")
    if threshold is not None and input_tokens > threshold:
        input_rate = model["long_prompt_input_per_million"]
        output_rate = model["long_prompt_output_per_million"]
        result["pricing_tier"] = "over_%d_input_tokens" % threshold
    else:
        result["pricing_tier"] = "standard"
    cached_rate = model.get("cached_input_per_million", model.get("cache_read_per_million", input_rate))
    if threshold is not None and input_tokens > threshold:
        cached_rate = model.get("long_prompt_cache_read_per_million", cached_rate)
    if cache_write_5m:
        write_rate = model.get("cache_write_5m_per_million", input_rate)
        if threshold is not None and input_tokens > threshold:
            write_rate = model.get("long_prompt_cache_write_5m_per_million", write_rate)
        write_5m_cost = cache_write_5m * write_rate / 1_000_000
    else:
        write_5m_cost = 0
    if cache_write_1h:
        write_rate = model.get("cache_write_1h_per_million", input_rate)
        if threshold is not None and input_tokens > threshold:
            write_rate = model.get("long_prompt_cache_write_1h_per_million", write_rate)
        write_1h_cost = cache_write_1h * write_rate / 1_000_000
    else:
        write_1h_cost = 0
    uncached_input_tokens = max(0, input_tokens - cached_input_tokens - cache_write_5m - cache_write_1h)
    result["billable_input_tokens"] = uncached_input_tokens
    result["cached_input_tokens"] = cached_input_tokens
    result["billable_output_tokens"] = output_tokens
    result["thinking_output_tokens"] = thinking_tokens
    result["estimated_input_cost_usd"] = (
        uncached_input_tokens * input_rate + cached_input_tokens * cached_rate
    ) / 1_000_000 + write_5m_cost + write_1h_cost
    result["estimated_output_cost_usd"] = output_tokens * output_rate / 1_000_000
    result["estimated_cost_usd"] = result["estimated_input_cost_usd"] + result["estimated_output_cost_usd"]
    return result


def _rate_label(model):
    base = "$%g / $%g per MTok" % (model["input_per_million"], model["output_per_million"])
    if "long_prompt_threshold_tokens" in model:
        base += "; over %s tokens: $%g / $%g" % (
            format(model["long_prompt_threshold_tokens"], ","),
            model["long_prompt_input_per_million"],
            model["long_prompt_output_per_million"],
        )
    return base


def report(phase="evaluation", prompt_version=None):
    version = resolve_prompt_version("regions", prompt_version)
    path = evaluation_directory(OUTPUT, phase, "regions", version) / "per_document.json"
    rows = read_json(path)
    pricing_config = read_json(ROOT / "config/model_pricing.json")
    pricing_models = pricing_config["models"]
    for row in rows:
        row.update(_estimate_request_cost(row, pricing_models))
    write_json(path, rows)
    _csv(path.parent / "per_document.csv", [{k: v for k, v in row.items() if not isinstance(v, (list, dict))} for row in rows])
    expected_hash = prompt_fingerprint("regions", version)["system_prompt_sha256"]
    if any(row["prompt_sha256"] != expected_hash for row in rows):
        raise ValueError("Report contains a different region prompt; rerun evaluate for " + version)
    groups = defaultdict(list)
    for row in rows:
        groups[(row["model_alias"], row["prompt_sha256"])].append(row)
    aggregate = []
    for (alias, prompt_hash), group in sorted(groups.items()):
        completed = [r for r in group if r["request_completed"]]
        parsed = [r for r in completed if r["json_parsed"]]
        compliant = [r for r in completed if r["schema_compliant"]]
        missing_records = [r for r in group if r.get("missing_run_record")]
        summary = {"phase": phase, "model_alias": alias, "prompt_sha256": prompt_hash, "expected_combinations": len(group), "run_records": len(group) - len(missing_records), "request_completed": len(completed), "transport_failures": sum(bool(r.get("transport_failure")) for r in group), "missing_run_records": len(missing_records), "unrecorded_request_artifacts": sum(bool(r.get("request_artifact_exists")) for r in missing_records), "json_parsed": len(parsed), "schema_compliant": len(compliant), "request_completion_rate": len(completed) / len(group), "json_parsing_rate_of_completed": len(parsed) / len(completed) if completed else None, "schema_compliance_rate_of_completed": len(compliant) / len(completed) if completed else None}
        priced = [r for r in completed if r.get("estimated_cost_usd") is not None]
        summary.update({
            "pricing_as_of": pricing_config["pricing_as_of"],
            "pricing_source": pricing_models.get(model_settings()["models"][alias]["id"], {}).get("source"),
            "priced_requests": len(priced),
            "estimated_input_cost_usd": sum(r["estimated_input_cost_usd"] for r in priced) if priced else None,
            "estimated_output_cost_usd": sum(r["estimated_output_cost_usd"] for r in priced) if priced else None,
            "estimated_cost_usd": sum(r["estimated_cost_usd"] for r in priced) if priced else None,
            "average_estimated_cost_per_priced_request_usd": sum(r["estimated_cost_usd"] for r in priced) / len(priced) if priced else None,
        })
        for family, tp_key, fp_key, fn_key in (
            ("text", "text_tp", "text_fp", "text_fn"),
            ("box", "box_tp", "box_fp", "box_fn"),
            ("word_label", "word_label_tp", "word_label_fp", "word_label_fn"),
        ):
            if not completed:
                summary.update({family + "_tp": None, family + "_fp": None, family + "_fn": None, family + "_precision": None, family + "_recall": None, family + "_f1": None})
                continue
            tp = sum(r[tp_key] for r in completed)
            fp = sum(r[fp_key] for r in completed)
            fn = sum(r[fn_key] for r in completed)
            p, rec, f1 = prf(tp, tp + fp, tp + fn)
            summary.update({family + "_tp": tp, family + "_fp": fp, family + "_fn": fn, family + "_precision": p, family + "_recall": rec, family + "_f1": f1})
        box_tp = sum(r["box_tp"] for r in completed)
        summary["matched_mean_iou"] = sum((r["matched_mean_iou"] or 0) * r["box_tp"] for r in completed) / box_tp if completed and box_tp else None
        summary["box_matched_char_edit_total"] = sum(r["box_matched_char_edit_total"] for r in completed) if completed else None
        summary["box_matched_char_edit_mean"] = summary["box_matched_char_edit_total"] / box_tp if completed and box_tp else None
        summary["box_matched_reference_char_count"] = sum(r["box_matched_reference_char_count"] for r in completed) if completed else None
        summary["box_matched_char_error_rate"] = summary["box_matched_char_edit_total"] / summary["box_matched_reference_char_count"] if summary["box_matched_reference_char_count"] else None
        aggregate.append(summary)
    destination = path.parent
    write_json(destination / "aggregate.json", aggregate)
    _csv(destination / "aggregate.csv", aggregate)
    _write_model_summary(destination, aggregate, rows)
    return aggregate


def _write_model_summary(destination, aggregate, rows):
    """Write a readable model-level view and each model's weakest box-F1 document."""
    doc_names = {doc["doc_id"]: Path(doc["pdf"]).stem for doc in manifest()}
    per_model = defaultdict(list)
    for row in rows:
        if row.get("request_completed") and row.get("box_f1") is not None:
            per_model[row["model_alias"]].append(row)

    lines = [
        "# Model-wide region evaluation summary",
        "",
        "Precision, recall, and F1 are micro-aggregated across documents. The weakest document is the one with the lowest per-document box F1; its box F1 and OCR word-label F1 are shown.",
        "Estimated costs use recorded token usage and the rates in [`model_pricing.json`](../../../../config/model_pricing.json) (USD, as of 2026-10-19). Thinking tokens and cached-input rates are included where recorded; cache-storage charges and timed-out attempts without usage data are excluded.",
        "",
        "| Model | Completed | Text P | Text R | Text F1 | Box P | Box R | Box F1 | Word-label P | Word-label R | Word-label F1 | Est. cost | Avg. / priced request | Weakest document (box F1; word-label F1) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for summary in sorted(aggregate, key=lambda row: row["model_alias"]):
        candidates = per_model.get(summary["model_alias"], [])
        if candidates:
            lowest = min(row["box_f1"] for row in candidates)
            weakest = [row for row in candidates if row["box_f1"] == lowest]
            weakest_text = "; ".join(
                "%s (%.3f; %.3f)" % (
                    doc_names.get(row["doc_id"], row["doc_id"]),
                    row["box_f1"],
                    row["word_label_f1"] if row.get("word_label_f1") is not None else float("nan"),
                )
                for row in weakest
            )
        else:
            weakest_text = "—"
        def metric(value):
            return "%.3f" % value if value is not None else "—"
        def dollars(value, digits=4):
            return "$%.*f" % (digits, value) if value is not None else "—"
        lines.append(
            "| {model} | {done}/{expected} | {tp} | {tr} | {tf} | {bp} | {br} | {bf} | {wp} | {wr} | {wf} | {cost} | {average} | {weak} |".format(
                model=summary["model_alias"],
                done=summary["request_completed"],
                expected=summary["expected_combinations"],
                tp=metric(summary.get("text_precision")),
                tr=metric(summary.get("text_recall")),
                tf=metric(summary.get("text_f1")),
                bp=metric(summary.get("box_precision")),
                br=metric(summary.get("box_recall")),
                bf=metric(summary.get("box_f1")),
                wp=metric(summary.get("word_label_precision")),
                wr=metric(summary.get("word_label_recall")),
                wf=metric(summary.get("word_label_f1")),
                cost=dollars(summary.get("estimated_cost_usd")),
                average=dollars(summary.get("average_estimated_cost_per_priced_request_usd"), 5),
                weak=weakest_text,
            )
        )
    lines.extend([
        "",
        "## Aggregate scores excluding Thailand",
        "",
        "Micro-aggregated across the other four documents; this is a diagnostic view of how much Thailand affects the overall scores.",
        "",
        "| Model | Completed | Text P | Text R | Text F1 | Box P | Box R | Box F1 | Word-label P | Word-label R | Word-label F1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    without_thailand = defaultdict(list)
    for row in rows:
        if "Thailand" not in row.get("doc_id", "") and row.get("request_completed"):
            without_thailand[row["model_alias"]].append(row)
    for alias in sorted(without_thailand):
        group = without_thailand[alias]
        values = {"model": alias, "done": len(group)}
        for family in ("text", "box", "word_label"):
            tp = sum(row[family + "_tp"] for row in group)
            fp = sum(row[family + "_fp"] for row in group)
            fn = sum(row[family + "_fn"] for row in group)
            precision, recall, f1 = prf(tp, tp + fp, tp + fn)
            values[family + "_p"] = precision
            values[family + "_r"] = recall
            values[family + "_f1"] = f1
        lines.append(
            "| {model} | {done}/4 | {text_p} | {text_r} | {text_f1} | {box_p} | {box_r} | {box_f1} | {word_label_p} | {word_label_r} | {word_label_f1} |".format(
                **{key: ("%.3f" % value if key.endswith(("_p", "_r", "_f1")) else value)
                   for key, value in values.items()}
            )
        )
    lines.extend(["", "See [`per_document.csv`](per_document.csv) for every document/model score and request record.", "Read the [metric and matching methods](../../../../model_methods.md) for formulas and validation rules.", ""])
    (destination / "model_summary.md").write_text("\n".join(lines), encoding="utf-8")


def report_archive(phase="evaluation", prompt_version=None):
    if prompt_version is not None:
        resolve_prompt_version("archive", prompt_version)
    path = evaluation_directory(OUTPUT, phase, "archive", prompt_version) / "per_document.json"
    rows = read_json(path)
    if prompt_version is not None:
        expected_hash = prompt_fingerprint("archive", prompt_version)["system_prompt_sha256"]
        if any(row["prompt_sha256"] != expected_hash for row in rows):
            raise ValueError("Report contains a different archive prompt; rerun evaluate")
    groups = defaultdict(list)
    for row in rows:
        groups[(row["model_alias"], row["prompt_sha256"])].append(row)
    aggregate = []
    for (alias, prompt_hash), group in sorted(groups.items()):
        completed = [row for row in group if row["request_completed"]]
        parsed = [row for row in completed if row["json_parsed"]]
        compliant = [row for row in completed if row["schema_compliant"]]
        aggregate.append({"target": "archive", "phase": phase, "model_alias": alias, "prompt_sha256": prompt_hash, "attempted": len(group), "request_completed": len(completed), "transport_failures": len(group) - len(completed), "json_parsed": len(parsed), "schema_compliant": len(compliant), "request_completion_rate": len(completed) / len(group), "json_parsing_rate_of_completed": len(parsed) / len(completed) if completed else None, "schema_compliance_rate_of_completed": len(compliant) / len(completed) if completed else None})
    write_json(path.parent / "aggregate.json", aggregate)
    _csv(path.parent / "aggregate.csv", aggregate)
    return aggregate

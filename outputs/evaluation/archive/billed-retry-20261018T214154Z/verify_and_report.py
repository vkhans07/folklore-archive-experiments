"""Verify this scoped rerun and refresh local reports after its four calls finish."""
import hashlib
import json
from pathlib import Path
import sys

SCOPE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from folklore_eval.common import manifest, read_json, write_json
from folklore_eval.evaluate import evaluate_archive
from folklore_eval.report import report_archive
from folklore_eval.validation import parse_archive_response


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    snapshot = read_json(SCOPE / "scope.json")
    latest = {}
    for path in (ROOT / "outputs/runs/archive/evaluation").glob("*/*/*/run.json"):
        record = read_json(path)
        key = (record["doc_id"], record["model_alias"])
        if key not in latest or path.stat().st_mtime > latest[key][0].stat().st_mtime:
            latest[key] = (path, record)
    assert len(latest) == 20, "Unexpected selected pair inventory"
    for relative, expected in snapshot["source_hashes"].items():
        assert digest(ROOT / relative) == expected, "Source/config changed: " + relative
    for previous in snapshot["selected"] + snapshot["other_selected_pairs"]:
        assert digest(ROOT / previous["run_path"]) == previous["record_sha256"], "Historical run changed"
    for previous in snapshot["other_selected_pairs"]:
        path, _ = latest[(previous["doc_id"], previous["model_alias"])]
        assert path == ROOT / previous["run_path"], "Unselected pair changed"

    schema = read_json(ROOT / "config/archive.schema.json")
    sources = {doc["doc_id"]: doc["pdf"] for doc in manifest()}
    results = []
    for previous in snapshot["selected"]:
        path, record = latest[(previous["doc_id"], previous["model_alias"])]
        assert path != ROOT / previous["run_path"], "Selected retry has not finished"
        for field in ("input_sha256", "system_prompt_sha256", "schema_sha256", "requested_model"):
            assert record[field] == previous["record"][field], "Experiment content changed: " + field
        assert record["generation"]["max_tokens"] == snapshot["planned_settings"]["max_tokens"]
        for field in ("max_attempts", "initial_backoff_seconds", "timeout_seconds"):
            assert record["transport"][field] == snapshot["planned_settings"][field]
        if record["request_completed"]:
            raw = read_json(path.parent / "response.json")
            parsed, errors, json_parsed = parse_archive_response(
                (path.parent / "response.txt").read_text(), schema, sources[record["doc_id"]]
            )
            assert json_parsed == record["json_parsed"]
            expected_valid = parsed is not None and not record["truncated"]
            assert expected_valid == record["schema_compliant"]
            if expected_valid:
                assert parsed == read_json(path.parent / "archive.json")
        else:
            raw = {}
        results.append({
            "doc_id": record["doc_id"], "model_alias": record["model_alias"],
            "run_path": str(path.relative_to(ROOT)),
            "previous_run_path": previous["run_path"],
            **{field: record.get(field) for field in (
                "request_completed", "json_parsed", "schema_compliant", "truncated",
                "finish_reason", "attempts", "latency_seconds", "errors", "request_error",
                "generation", "transport", "usage")},
            "provider_usage": (raw.get("provider_response") or {}).get("usageMetadata", raw.get("usage")),
        })
    rows = evaluate_archive("evaluation")
    aggregate = report_archive("evaluation")
    summary = {
        "scope": str(SCOPE.relative_to(ROOT)), "results": results,
        "unchanged_other_pairs": len(snapshot["other_selected_pairs"]),
        "source_config_and_prior_runs_unchanged": True,
        "valid_before": 16, "valid_after": sum(row["schema_compliant"] for row in rows),
        "aggregate": aggregate,
        "limits": [
            "Strict validity is not extraction accuracy.",
            "Billing change was reported by the user; no billing dashboard was inspected.",
            "This aggregate combines older runs and the selected reruns with different token/transport settings.",
            "Prompt v3 remains a draft; no new region benchmark or prompt-comparison run was performed."
        ],
    }
    diagnostic = SCOPE / "haiku-wrapper-diagnostic.json"
    if diagnostic.exists():
        summary["separate_haiku_wrapper_diagnostic"] = read_json(diagnostic)
    write_json(SCOPE / "comparison.json", summary)
    print(json.dumps({"valid_before": 16, "valid_after": summary["valid_after"],
                      "unchanged_other_pairs": summary["unchanged_other_pairs"],
                      "results": [{key: row[key] for key in (
                          "model_alias", "doc_id", "schema_compliant", "truncated",
                          "attempts", "latency_seconds")} for row in results]}, indent=2))


if __name__ == "__main__":
    main()

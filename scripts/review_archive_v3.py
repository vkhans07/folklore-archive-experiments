"""Build a local evidence bundle from the exact frozen v3 run; no provider calls."""
import difflib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from folklore_eval.common import file_sha, manifest, read_json, sha, write_json
from folklore_eval.validation import parse_archive_response

DEST = ROOT / "outputs/reviews/archive_v3"
MODELS = ("sonnet", "haiku", "gemini_flash", "gemini_flash_high")
NAMES = {
    "00003_Legend_Vietnam__38.pdf": "Vietnam",
    "00001_09_Taiwan_holiday_lore__93.pdf": "Taiwan",
    "00002_86_Turkey_Proverbs_III__147.pdf": "Turkey",
    "00002_56_Thailand_Folkspeech__38.pdf": "Thailand",
    "00003_Anglo_Folkspeech_VI_A67_C6__74.pdf": "Anglo",
}
ADDRESSES = {"Vietnam": "2219 Channing", "Taiwan": "1811 Carleton", "Turkey": "2601 Warring", "Thailand": "10420 Trabuco", "Anglo": "2729 Dwight"}


def link(path):
    return str(path.resolve())


def changes(source, output):
    a, b = source.split(), output.split()
    return [dict(operation=op, source=" ".join(a[i:j]), output=" ".join(b[k:l]),
                 source_token_start=i, source_token_end=j,
                 preceding_source=" ".join(a[max(0, i - 12):i]),
                 following_source=" ".join(a[j:j + 12]))
            for op, i, j, k, l in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
            if op != "equal"]


def main():
    lock = read_json(ROOT / "config/prompt_archive_v3.lock.json")
    schema = read_json(ROOT / "config/archive.schema.json")
    if file_sha(ROOT / "config/archive.schema.json") != lock["schema_sha256"]:
        raise ValueError("Schema no longer matches the v3 lock")
    selected = {}
    for path in sorted((ROOT / "outputs/runs/archive/development").glob("*/*/*/run.json")):
        record = read_json(path)
        if record.get("system_prompt_sha256") != lock["system_prompt_sha256"]:
            continue
        key = record["doc_id"], record["model_alias"]
        if key in selected:
            raise ValueError("Multiple matching runs; explicitly adjudicate selection: %r" % (key,))
        selected[key] = path, record
    expected = {(d["doc_id"], m) for d in manifest() for m in MODELS}
    if set(selected) != expected:
        raise ValueError("Expected exactly the five-document, four-model v3 matrix")
    DEST.mkdir(parents=True, exist_ok=True)
    audit = []
    for doc in manifest():
        name = NAMES[doc["doc_id"]]
        input_path = ROOT / "outputs/inputs" / (Path(doc["doc_id"]).stem + ".json")
        prepared = read_json(input_path)
        pages = [" ".join(w["text"] for w in page["words"]) for page in prepared["pages"]]
        source = " ".join(pages)
        lines = [f"# {name}: v3 source and output evidence", "",
                 "This bundle reproduces supplied OCR and saved outputs. Source PDF pixels were not reviewed. Token differences are diagnostics, not error counts: header removal and whitespace changes may be intended.", "",
                 f"[Original PDF](<{link(ROOT / doc['pdf'])}>) | [Prepared input](<{link(input_path)}>)", "",
                 "## Source OCR (one-based page numbers)", ""]
        for number, page in enumerate(pages, 1):
            lines.extend([f"### Page {number}", "", page, ""])
        for model in MODELS:
            path, record = selected[doc["doc_id"], model]
            request = read_json(path.parent / "request.json")["request"]
            archive = read_json(path.parent / "archive.json")
            raw_text = (path.parent / "response.txt").read_text(encoding="utf-8")
            provider_response = read_json(path.parent / "response.json")
            provider_text = "".join(block.get("text", "") for block in provider_response.get("content", []) if block.get("type") == "text")
            parsed, errors, json_ok = parse_archive_response(raw_text, schema, prepared["source_pdf"])
            checks = {
                "raw_response_matches_archive": parsed == archive,
                "provider_text_matches_saved_text": provider_text == raw_text,
                "json_parsed": json_ok, "validation_errors": errors,
                "prompt_hash_matches": sha(request["system"]) == lock["system_prompt_sha256"],
                "input_hash_matches": sha(request["messages"][0]["content"]) == record["input_sha256"] == file_sha(input_path),
                "schema_hash_matches": record["schema_sha256"] == lock["schema_sha256"],
            }
            if errors or not all(v for k, v in checks.items() if k != "validation_errors"):
                raise ValueError(f"Artifact integrity failure: {path}: {checks}")
            diff = changes(source, archive["cleaned_full_text"])
            row = {"document": name, "doc_id": doc["doc_id"], "model": model,
                   "run_path": str(path.relative_to(ROOT)), "archive_path": str((path.parent / "archive.json").relative_to(ROOT)),
                   "timestamp_utc": record["timestamp_utc"], "latency_seconds": record["latency_seconds"],
                   "attempts": record["attempts"], "request_completed": record["request_completed"],
                   "truncated": record["truncated"], "schema_compliant": record["schema_compliant"],
                   "generation": record["generation"], "transport": record["transport"],
                   "temperature_in_request": request.get("temperature"), "usage": record["usage"],
                   "cleaned_full_text_chars": len(archive["cleaned_full_text"]),
                   "address_retained_in_full_text": ADDRESSES[name] in archive["cleaned_full_text"],
                   "full_text_token_changes": diff, "checks": checks}
            audit.append(row)
            lines.extend([f"## {model}", "", f"[Raw response](<{link(path.parent / 'response.txt')}>) | [Archive JSON](<{link(path.parent / 'archive.json')}>) | [Run record](<{link(path)}>)", "",
                          f"Latency: {record['latency_seconds']} seconds; attempts: {record['attempts']}; schema valid: {record['schema_compliant']}.", "",
                          "### Structured fields", "", "```json", json.dumps({k: v for k, v in archive.items() if k != "cleaned_full_text"}, ensure_ascii=False, indent=2), "```", "",
                          "### cleaned_full_text", "", archive["cleaned_full_text"], "", "### Changes from supplied OCR", ""])
            if not diff:
                lines.extend(["No differences after splitting on whitespace: the full OCR was retained.", ""])
            for d in diff:
                lines.extend([f"- {d['operation']}: `{d['source']}` → `{d['output']}`"])
            lines.append("")
        (DEST / (name + ".md")).write_text("\n".join(lines), encoding="utf-8")
    models = {}
    for model in MODELS:
        rows = [r for r in audit if r["model"] == model]
        models[model] = {"records": len(rows), "schema_valid": sum(r["schema_compliant"] for r in rows),
                         "total_latency_seconds": round(sum(r["latency_seconds"] for r in rows), 3),
                         "median_latency_seconds": statistics.median(r["latency_seconds"] for r in rows),
                         "attempts": [r["attempts"] for r in rows],
                         "full_text_with_address": sum(r["address_retained_in_full_text"] for r in rows)}
    summary = {"prompt_sha256": lock["system_prompt_sha256"], "schema_sha256": lock["schema_sha256"],
               "scope": "20 exact-fingerprint v3 development runs; no model requests or accuracy scores", "models": models,
               "records": audit}
    write_json(DEST / "evidence.json", summary)
    print(json.dumps(models, indent=2))
    print("Evidence bundle:", DEST)


if __name__ == "__main__":
    main()

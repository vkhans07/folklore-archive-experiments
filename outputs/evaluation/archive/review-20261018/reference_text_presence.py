#!/usr/bin/env python3
"""Reproduce a narrow exact-presence diagnostic; not an annotation scorer."""
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REVIEW = Path(__file__).resolve().parent
SELECTION = ROOT / "outputs/evaluation/archive/retry-20261018/before-selected-runs.json"
REFERENCE_EXPORT = ROOT / "JSONs/Taiwan Holiday Lore.json"  # duplicate exports are byte-identical


def norm(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value)).strip()


def string_leaves(value, path=""):
    if isinstance(value, str):
        if path != "cleaned_full_text":
            yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield from string_leaves(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from string_leaves(child, f"{path}[{index}]")


def main():
    selection = json.loads(SELECTION.read_text())
    refs_all = json.loads(REFERENCE_EXPORT.read_text())
    by_doc = collections.defaultdict(list)
    for ref in refs_all:
        if ref.get("deleted_at") is None:
            by_doc[ref["doc_id"]].append(ref)

    entries, excluded = [], []
    for selected in (selection.get("selected", []) + selection.get("other_selected_pairs", [])):
        run_path = ROOT / selected["run_path"]
        run = json.loads(run_path.read_text())
        if not run.get("schema_compliant"):
            excluded.append({"run_path": selected["run_path"], "reason": "not_schema_compliant"})
            continue
        pred_path = run_path.parent / "archive.json"
        if not pred_path.exists():
            excluded.append({"run_path": selected["run_path"], "reason": "missing_archive_json"})
            continue
        pred = json.loads(pred_path.read_text())
        leaves = [(p, norm(s)) for p, s in string_leaves(pred) if norm(s)]
        full_text = norm(pred.get("cleaned_full_text", ""))
        for ref in by_doc[selected["doc_id"]]:
            raw = ref.get("text_joined_final") or ref.get("text_joined_user") or ref.get("text_joined_original") or ref.get("text_joined_derived") or ref.get("text_joined") or ""
            needle = norm(raw)
            if not needle:
                excluded.append({"doc_id": selected["doc_id"], "model_alias": selected["model_alias"], "annotation_id": ref.get("annotation_id"), "reason": "empty_reference_text"})
                continue
            hits = [path for path, value in leaves if needle in value]
            text_hit = needle in full_text
            entries.append({
                "doc_id": selected["doc_id"], "model_alias": selected["model_alias"],
                "run_path": selected["run_path"], "annotation_id": ref["annotation_id"],
                "label": ref["label"], "page_num": ref["page_num"],
                "reference_text": raw, "normalized_reference_text": needle,
                "present_in_structured_string_leaf": bool(hits), "matching_leaf_paths": hits,
                "present_in_cleaned_full_text": text_hit,
                "reference_text_source": next((k for k in ("text_joined_final", "text_joined_user", "text_joined_original", "text_joined_derived", "text_joined") if isinstance(ref.get(k), str) and ref[k].strip()), "none"),
                "bbox": ref.get("region_bbox_norm"),
            })

    groups = collections.defaultdict(lambda: {"references": 0, "leaf_present": 0, "full_text_present": 0})
    for row in entries:
        for key in ((row["model_alias"], row["doc_id"], row["label"]), (row["model_alias"], row["doc_id"], "ALL_LABELS")):
            g = groups[key]
            g["references"] += 1
            g["leaf_present"] += int(row["present_in_structured_string_leaf"])
            g["full_text_present"] += int(row["present_in_cleaned_full_text"])
    result = {
        "diagnostic": "reference-text presence (exact substring after NFC + whitespace normalization)",
        "not_a_benchmark": True,
        "selection_file": str(SELECTION.relative_to(ROOT)),
        "selected_run_count": len(selection.get("selected", []) + selection.get("other_selected_pairs", [])),
        "included_valid_run_count": len({r["run_path"] for r in entries}),
        "included_reference_comparisons": len(entries),
        "excluded": excluded,
        "normalization": "Unicode NFC then collapse all whitespace runs to one ASCII space and strip; case and punctuation retained.",
        "structured_fields": "Any nonempty string leaf recursively within archive JSON except cleaned_full_text; no field-label mapping.",
        "full_text_field": "cleaned_full_text checked separately.",
        "group_counts": [{"model_alias": k[0], "doc_id": k[1], "label": k[2], **v} for k, v in sorted(groups.items())],
        "examples": {
            "leaf_matches": [r for r in entries if r["present_in_structured_string_leaf"]][:12],
            "leaf_misses_but_full_text_hits": [r for r in entries if not r["present_in_structured_string_leaf"] and r["present_in_cleaned_full_text"]][:12],
            "misses_both": [r for r in entries if not r["present_in_structured_string_leaf"] and not r["present_in_cleaned_full_text"]][:12],
        },
        "all_comparisons": entries,
        "limitations": [
            "Presence ignores labels, page numbers, boxes, duplication, and semantic role; it is neither precision/recall/F1 nor correctness.",
            "Substring presence may count incidental containment; absence may reflect paraphrase, OCR/text differences, or extraction choices.",
            "The reference annotations are regional snippets; archive text is a document-level structured extraction. This diagnostic does not resolve unconfirmed field mappings.",
        ],
    }
    (REVIEW / "reference_text_presence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("selected_run_count", "included_valid_run_count", "included_reference_comparisons", "excluded")}, ensure_ascii=False, indent=2))
    print("group_count_rows", len(result["group_counts"]))
    for category, rows in result["examples"].items():
        print(category, len(rows))


if __name__ == "__main__":
    main()

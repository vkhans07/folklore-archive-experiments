from collections import defaultdict
from pathlib import Path

from .common import ROOT, file_sha, read_json
from .matching import iou, normalized_text


def load_references(docs, prepared_by_doc):
    """Only evaluator code calls this; source JSON exports are never changed."""
    paths = sorted((ROOT / "JSONs").glob("*.json"))
    if not paths:
        raise FileNotFoundError("No annotation export in JSONs/")
    by_hash = defaultdict(list)
    for path in paths:
        by_hash[file_sha(path)].append(path)
    records, seen_ids = [], set()
    for group in by_hash.values():
        rows = read_json(group[0])
        if not isinstance(rows, list):
            raise ValueError("Reference export must be a list: " + str(group[0]))
        for row in rows:
            annotation_id = row.get("annotation_id")
            if not annotation_id or annotation_id in seen_ids:
                raise ValueError("Missing or duplicate annotation_id: " + str(annotation_id))
            seen_ids.add(annotation_id)
            if row.get("deleted_at") is None:
                records.append(row)
    target = {d["doc_id"] for d in docs}
    refs, flags, fallbacks = defaultdict(list), [], []
    for row in records:
        doc_id = row.get("doc_id")
        if doc_id not in target:
            continue
        page = row.get("page_num")
        prepared = prepared_by_doc[doc_id]
        if type(page) is not int or not 0 <= page < len(prepared["pages"]):
            raise ValueError("Reference page unavailable: %s %s" % (doc_id, page))
        box = row.get("region_bbox_norm")
        if not isinstance(box, list) or len(box) != 4 or any(type(v) not in (int, float) or not 0 <= v <= 1 for v in box) or box[0] >= box[2] or box[1] >= box[3]:
            raise ValueError("Invalid reference bbox: " + str(row["annotation_id"]))
        text, source = None, None
        for field in ("text_joined_final", "text_joined_user", "text_joined_original", "text_joined_derived", "text_joined"):
            if isinstance(row.get(field), str) and row[field].strip():
                text, source = row[field], field
                break
        if text is None:
            text, source = "", "none"
            flags.append({"doc_id": doc_id, "annotation_id": row["annotation_id"], "type": "missing_reference_text"})
        if source != "text_joined_final":
            fallbacks.append({"doc_id": doc_id, "annotation_id": row["annotation_id"], "source_field": source})
        refs[doc_id].append({"page_num": page, "label": row["label"], "bbox": box, "text": text, "annotation_id": row["annotation_id"]})
    for doc_id in target:
        page_words = prepared_by_doc[doc_id]["pages"]
        for i, ref in enumerate(refs[doc_id]):
            same_page = page_words[ref["page_num"]]["words"]
            touching = [w["text"] for w in same_page if iou(w["bbox"], ref["bbox"]) > 0]
            if not touching:
                flags.append({"doc_id": doc_id, "annotation_id": ref["annotation_id"], "type": "reference_box_has_no_ocr_words"})
            elif ref["text"]:
                # A low word overlap is a review hint, not a correction or score.
                ref_tokens = set(normalized_text(ref["text"]).casefold().split())
                ocr_tokens = set(normalized_text(" ".join(touching)).casefold().split())
                if ref_tokens and len(ref_tokens & ocr_tokens) / len(ref_tokens) < 0.2:
                    flags.append({"doc_id": doc_id, "annotation_id": ref["annotation_id"], "type": "reference_text_ocr_mismatch_candidate"})
            for other in refs[doc_id][i + 1:]:
                if ref["page_num"] == other["page_num"] and ref["label"] == other["label"] and iou(ref["bbox"], other["bbox"]) >= 0.8:
                    flags.append({"doc_id": doc_id, "annotation_id": ref["annotation_id"], "other_annotation_id": other["annotation_id"], "type": "ambiguous_overlapping_references"})
    audit = {"source_exports": [{"sha256": digest, "canonical_file": str(group[0].relative_to(ROOT)), "duplicate_files": [str(p.relative_to(ROOT)) for p in group[1:]]} for digest, group in by_hash.items()], "unique_annotation_ids_all_documents": len(seen_ids), "fallbacks": fallbacks}
    return refs, flags, audit

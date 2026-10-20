import csv
from collections import defaultdict
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

from .common import OUTPUT, ROOT, evaluation_directory, manifest, read_json, run_directory, write_json
from .predict import prompt_fingerprint, resolve_prompt_version
from .matching import edit_distance, normalized_text, prf, region_pairs, text_exact_count
from .references import load_references
from .settings import model_settings


def _word_label_memberships(rows, pages):
    """Expand boxes to page-local OCR words using word-center containment."""
    memberships = set()
    for row in rows:
        page_num = row["page_num"]
        if page_num >= len(pages):
            continue
        x0, y0, x1, y1 = row["bbox"]
        for word_index, word in enumerate(pages[page_num]["words"]):
            wx0, wy0, wx1, wy1 = word["bbox"]
            center_x, center_y = (wx0 + wx1) / 2, (wy0 + wy1) / 2
            if x0 <= center_x <= x1 and y0 <= center_y <= y1:
                memberships.add((page_num, word_index, row["label"]))
    return memberships


def _box_fp_containment_exemptions(refs, preds, matched_pred_indices):
    """Return unmatched predictions fully contained by a same-page/label reference."""
    exempt = set()
    for pred_index, pred in enumerate(preds):
        if pred_index in matched_pred_indices:
            continue
        px0, py0, px1, py1 = pred["bbox"]
        for ref in refs:
            if ref["page_num"] != pred["page_num"] or ref["label"] != pred["label"]:
                continue
            rx0, ry0, rx1, ry1 = ref["bbox"]
            if rx0 <= px0 and ry0 <= py0 and px1 <= rx1 and py1 <= ry1:
                exempt.add(pred_index)
                break
    return exempt


def score_document(refs, preds, pages=None):
    text_tp = text_exact_count(refs, preds)
    pairs = region_pairs(refs, preds)
    box_tp = len(pairs)
    matched_pred_indices = {pred_index for _, pred_index, _ in pairs}
    containment_exemptions = _box_fp_containment_exemptions(refs, preds, matched_pred_indices)
    box_fp = len(preds) - box_tp - len(containment_exemptions)
    box_fn = len(refs) - box_tp
    text_p, text_r, text_f1 = prf(text_tp, len(preds), len(refs))
    box_p, box_r, box_f1 = prf(box_tp, box_tp + box_fp, box_tp + box_fn)
    pages = pages or []
    reference_words = _word_label_memberships(refs, pages)
    predicted_words = _word_label_memberships(preds, pages)
    word_label_tp = len(reference_words & predicted_words)
    word_label_fp = len(predicted_words - reference_words)
    word_label_fn = len(reference_words - predicted_words)
    word_label_p, word_label_r, word_label_f1 = prf(
        word_label_tp, len(predicted_words), len(reference_words)
    )
    distances = [edit_distance(refs[i]["text"], preds[j]["text"]) for i, j, _ in pairs]
    matched_reference_chars = sum(len(normalized_text(refs[i]["text"])) for i, _, _ in pairs)
    edit_total = sum(distances)
    return {"reference_count": len(refs), "prediction_count": len(preds), "text_tp": text_tp, "text_fp": len(preds) - text_tp, "text_fn": len(refs) - text_tp, "text_precision": text_p, "text_recall": text_r, "text_f1": text_f1, "box_tp": box_tp, "box_fp": box_fp, "box_fn": box_fn, "box_containment_fp_exempt": len(containment_exemptions), "box_precision": box_p, "box_recall": box_r, "box_f1": box_f1, "word_label_tp": word_label_tp, "word_label_fp": word_label_fp, "word_label_fn": word_label_fn, "word_label_precision": word_label_p, "word_label_recall": word_label_r, "word_label_f1": word_label_f1, "reference_ocr_word_label_count": len(reference_words), "prediction_ocr_word_label_count": len(predicted_words), "matched_mean_iou": sum(v for _, _, v in pairs) / box_tp if box_tp else None, "box_matched_char_edit_total": edit_total, "box_matched_char_edit_mean": edit_total / len(distances) if distances else None, "box_matched_reference_char_count": matched_reference_chars, "box_matched_char_error_rate": edit_total / matched_reference_chars if matched_reference_chars else None, "box_matched_char_edit_distances": distances}


def render_overlays(doc, refs, preds, destination):
    source = fitz.open(ROOT / doc["pdf"])
    destination.mkdir(parents=True, exist_ok=True)
    for page_num, page in enumerate(source):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        draw = ImageDraw.Draw(image)
        for color, rows, prefix in (("#008441", refs, "R"), ("#e12323", preds, "P")):
            for row in rows:
                if row["page_num"] != page_num:
                    continue
                x0, y0, x1, y1 = row["bbox"]
                box = (x0 * pix.width, y0 * pix.height, x1 * pix.width, y1 * pix.height)
                draw.rectangle(box, outline=color, width=2)
                title = prefix + ":" + row["label"]
                draw.text((box[0] + 2, max(0, box[1] - 12)), title, fill=color, font=ImageFont.load_default())
        image.save(destination / ("page_%02d.png" % page_num))


def _csv(path, rows):
    if not rows:
        Path(path).write_text("", encoding="utf-8")
        return
    keys = sorted(set().union(*(row.keys() for row in rows)))
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in keys})


def evaluate(phase="evaluation", selected_doc=None, selected_model=None, prompt_version=None):
    version = resolve_prompt_version("regions", prompt_version)
    fingerprint = prompt_fingerprint("regions", version)
    docs = manifest()
    if selected_doc:
        docs = [d for d in docs if d["doc_id"] == selected_doc]
        if not docs:
            raise ValueError("Unknown document: " + selected_doc)
    prepared = {}
    for doc in docs:
        path = OUTPUT / "inputs" / (Path(doc["doc_id"]).stem + ".json")
        prepared[doc["doc_id"]] = read_json(path)
    refs, flags, audit = load_references(docs, prepared)
    integrity = read_json(ROOT / "config/integrity.json")
    for doc in docs:
        doc_id = doc["doc_id"]
        if len(refs[doc_id]) != integrity["expected_counts"][doc_id]:
            raise ValueError("Reference count integrity failure: " + doc_id)
        if sorted(set(r["page_num"] for r in refs[doc_id])) != integrity["expected_pages"][doc_id]:
            raise ValueError("Reference page integrity failure: " + doc_id)
    result_dir = evaluation_directory(OUTPUT, phase, "regions", version)
    result_dir.mkdir(parents=True, exist_ok=True)
    write_json(result_dir / "reference_audit.json", audit)
    write_json(result_dir / "review_flags.json", flags)
    rows = []
    expected_models = model_settings()["models"]
    if selected_model:
        expected_models = {selected_model: expected_models[selected_model]}
    for doc in docs:
        doc_id = doc["doc_id"]
        run_root = run_directory(OUTPUT, phase, "regions", version)
        found = list(run_root.glob("*/" + Path(doc_id).stem + "/*/run.json")) if run_root.exists() else []
        selected = {}
        for path in found:
            record = read_json(path)
            if any(record.get(k) != v for k, v in fingerprint.items()):
                continue
            alias = record["model_alias"]
            if selected_model and alias != selected_model:
                continue
            if alias not in selected or path.stat().st_mtime > selected[alias][0].stat().st_mtime:
                selected[alias] = (path, record)
        if not selected:
            render_overlays(doc, refs[doc_id], [], result_dir / "overlays" / "reference_only" / Path(doc_id).stem)
        for alias, (path, record) in selected.items():
            pred_path = path.parent / "predictions.json"
            preds = read_json(pred_path)["annotations"] if record.get("schema_compliant") and pred_path.exists() else []
            metrics = score_document(refs[doc_id], preds, prepared[doc_id]["pages"]) if record.get("request_completed") else None
            row = {"phase": phase, "doc_id": doc_id, "model_alias": alias, "requested_model": record["requested_model"], "returned_model": record.get("returned_model"), "run_path": str(path), "prompt_sha256": record["system_prompt_sha256"], "request_completed": record["request_completed"], "json_parsed": record["json_parsed"], "schema_compliant": record["schema_compliant"], "transport_failure": not record["request_completed"], "truncated": record["truncated"], "latency_seconds": record["latency_seconds"], "finish_reason": record["finish_reason"], "input_tokens": (record.get("usage") or {}).get("input_tokens"), "output_tokens": (record.get("usage") or {}).get("output_tokens"), "request_error": record.get("request_error"), "validation_errors": record.get("errors")}
            if metrics is not None:
                row.update(metrics)
            row["prompt_version"] = version
            rows.append(row)
            render_overlays(doc, refs[doc_id], preds, result_dir / "overlays" / alias / Path(doc_id).stem)
        for alias, model in expected_models.items():
            if alias in selected:
                continue
            model_dir = run_root / alias / Path(doc_id).stem
            has_request = any(model_dir.glob("*/request.json")) if model_dir.exists() else False
            rows.append({
                "phase": phase,
                "doc_id": doc_id,
                "model_alias": alias,
                "requested_model": model["id"],
                "returned_model": None,
                "run_path": None,
                "prompt_sha256": fingerprint["system_prompt_sha256"],
                "request_completed": False,
                "json_parsed": False,
                "schema_compliant": False,
                "transport_failure": False,
                "missing_run_record": True,
                "request_artifact_exists": has_request,
                "run_status": "interrupted_request_artifact" if has_request else "no_run_record",
                "truncated": False,
                "latency_seconds": None,
                "finish_reason": None,
                "input_tokens": None,
                "output_tokens": None,
                "request_error": None,
                "validation_errors": [],
                "prompt_version": version,
            })
    if not rows and prompt_version is not None:
        raise ValueError("No matching region runs for " + version + "; run predict with this version first")
    write_json(result_dir / "per_document.json", rows)
    _csv(result_dir / "per_document.csv", [{k: v for k, v in row.items() if not isinstance(v, (list, dict))} for row in rows])
    return rows


def evaluate_archive(phase="evaluation", selected_doc=None, selected_model=None, prompt_version=None):
    """Archive outputs have no field-level references; report request/schema status only."""
    fingerprint = prompt_fingerprint("archive", prompt_version) if prompt_version is not None else None
    docs = manifest()
    if selected_doc:
        docs = [d for d in docs if d["doc_id"] == selected_doc]
        if not docs:
            raise ValueError("Unknown document: " + selected_doc)
    run_root = OUTPUT / "runs" / "archive" / phase
    rows = []
    for doc in docs:
        found = list(run_root.glob("*/" + Path(doc["doc_id"]).stem + "/*/run.json")) if run_root.exists() else []
        selected = {}
        for path in found:
            record = read_json(path)
            if fingerprint and any(record.get(k) != v for k, v in fingerprint.items()):
                continue
            alias = record["model_alias"]
            if selected_model and alias != selected_model:
                continue
            if alias not in selected or path.stat().st_mtime > selected[alias][0].stat().st_mtime:
                selected[alias] = (path, record)
        for alias, (path, record) in selected.items():
            rows.append({"target": "archive", "phase": phase, "doc_id": doc["doc_id"], "model_alias": alias, "requested_model": record["requested_model"], "returned_model": record.get("returned_model"), "run_path": str(path), "prompt_sha256": record["system_prompt_sha256"], "request_completed": record["request_completed"], "json_parsed": record["json_parsed"], "schema_compliant": record["schema_compliant"], "transport_failure": not record["request_completed"], "truncated": record["truncated"], "latency_seconds": record["latency_seconds"], "finish_reason": record["finish_reason"], "input_tokens": (record.get("usage") or {}).get("input_tokens"), "output_tokens": (record.get("usage") or {}).get("output_tokens"), "request_error": record.get("request_error"), "validation_errors": record.get("errors")})
    if not rows and prompt_version is not None:
        raise ValueError("No matching archive runs for " + prompt_version)
    destination = evaluation_directory(OUTPUT, phase, "archive", prompt_version)
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "per_document.json", rows)
    _csv(destination / "per_document.csv", [{k: v for k, v in row.items() if not isinstance(v, (list, dict))} for row in rows])
    return rows

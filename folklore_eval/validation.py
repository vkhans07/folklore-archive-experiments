import json
import math

from jsonschema import Draft202012Validator


def validate_object(value, labels, page_count):
    errors = []
    if not isinstance(value, dict) or set(value) != {"annotations"} or not isinstance(value.get("annotations"), list):
        return ["Top level must contain only an annotations array"]
    for i, row in enumerate(value["annotations"]):
        prefix = "annotations[%d]" % i
        if not isinstance(row, dict) or set(row) != {"page_num", "label", "text", "bbox"}:
            errors.append(prefix + ": expected exactly page_num, label, text, bbox")
            continue
        page = row["page_num"]
        if type(page) is not int or not 0 <= page < page_count:
            errors.append(prefix + ": page_num out of range or not integer")
        if not isinstance(row["label"], str) or row["label"] not in labels:
            errors.append(prefix + ": label outside vocabulary")
        if not isinstance(row["text"], str):
            errors.append(prefix + ": text must be string")
        box = row["bbox"]
        if not isinstance(box, list) or len(box) != 4 or any(type(v) not in (float, int) or not math.isfinite(v) or not 0 <= v <= 1 for v in box):
            errors.append(prefix + ": invalid normalized bbox")
        elif box[0] >= box[2] or box[1] >= box[3]:
            errors.append(prefix + ": bbox must have positive dimensions")
    return errors


def parse_response(raw_text, labels, page_count):
    try:
        value = json.loads(raw_text)
    except (ValueError, TypeError) as exc:
        return None, ["JSON parsing: " + str(exc)], False
    errors = validate_object(value, labels, page_count)
    return value if not errors else None, errors, True


def parse_archive_response(raw_text, schema, source_pdf):
    try:
        value = json.loads(raw_text)
    except (ValueError, TypeError) as exc:
        return None, ["JSON parsing: " + str(exc)], False
    validator = Draft202012Validator(schema)
    errors = ["%s: %s" % (".".join(map(str, error.absolute_path)) or "root", error.message) for error in validator.iter_errors(value)]
    if isinstance(value, dict):
        if value.get("filename") != source_pdf:
            errors.append("filename must copy source_pdf exactly")
        if value.get("_id") is not None:
            errors.append("_id must be null until storage assigns it")
        if value.get("storage_medium") != "PDF":
            errors.append("storage_medium must be PDF for this input")
    return value if not errors else None, errors, True

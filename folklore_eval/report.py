from collections import defaultdict
from pathlib import Path

from .common import OUTPUT, read_json, write_json
from .evaluate import _csv
from .matching import prf


def report(phase="evaluation"):
    path = OUTPUT / "evaluation" / phase / "per_document.json"
    rows = read_json(path)
    groups = defaultdict(list)
    for row in rows:
        groups[(row["model_alias"], row["prompt_sha256"])].append(row)
    aggregate = []
    for (alias, prompt_hash), group in sorted(groups.items()):
        completed = [r for r in group if r["request_completed"]]
        parsed = [r for r in completed if r["json_parsed"]]
        compliant = [r for r in completed if r["schema_compliant"]]
        summary = {"phase": phase, "model_alias": alias, "prompt_sha256": prompt_hash, "attempted": len(group), "request_completed": len(completed), "transport_failures": len(group) - len(completed), "json_parsed": len(parsed), "schema_compliant": len(compliant), "request_completion_rate": len(completed) / len(group), "json_parsing_rate_of_completed": len(parsed) / len(completed) if completed else None, "schema_compliance_rate_of_completed": len(compliant) / len(completed) if completed else None}
        for family, tp_key, fp_key, fn_key in (("text", "text_tp", "text_fp", "text_fn"), ("box", "box_tp", "box_fp", "box_fn")):
            tp = sum(r[tp_key] for r in completed)
            fp = sum(r[fp_key] for r in completed)
            fn = sum(r[fn_key] for r in completed)
            p, rec, f1 = prf(tp, tp + fp, tp + fn)
            summary.update({family + "_tp": tp, family + "_fp": fp, family + "_fn": fn, family + "_precision": p, family + "_recall": rec, family + "_f1": f1})
        box_tp = sum(r["box_tp"] for r in completed)
        summary["matched_mean_iou"] = sum((r["matched_mean_iou"] or 0) * r["box_tp"] for r in completed) / box_tp if box_tp else None
        summary["box_matched_char_edit_total"] = sum(r["box_matched_char_edit_total"] for r in completed)
        summary["box_matched_char_edit_mean"] = summary["box_matched_char_edit_total"] / box_tp if box_tp else None
        aggregate.append(summary)
    destination = path.parent
    write_json(destination / "aggregate.json", aggregate)
    _csv(destination / "aggregate.csv", aggregate)
    return aggregate


def report_archive(phase="evaluation"):
    path = OUTPUT / "evaluation" / "archive" / phase / "per_document.json"
    rows = read_json(path)
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

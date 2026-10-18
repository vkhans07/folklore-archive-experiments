#!/usr/bin/env python3
"""Build dependency-free SVG charts from a folklore_eval archive evaluation."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


COLORS = {
    "ink": "#182230",
    "muted": "#667085",
    "grid": "#e4e7ec",
    "blue": "#3777e8",
    "green": "#159570",
    "amber": "#d98b14",
    "red": "#d44848",
    "light": "#f5f7fa",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_start(title: str, subtitle: str, width: int = 1100, height: int = 640) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        '<style>text{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#182230}.title{font-size:27px;font-weight:700}.sub{font-size:14px;fill:#667085}.label{font-size:15px}.small{font-size:12px;fill:#667085}.value{font-size:14px;font-weight:700}.axis{font-size:12px;fill:#667085}</style>',
        f'<rect width="{width}" height="{height}" rx="18" fill="white"/>',
        f'<text x="42" y="48" class="title">{esc(title)}</text>',
        f'<text x="42" y="76" class="sub">{esc(subtitle)}</text>',
    ]


def text(x: float, y: float, value: object, klass: str = "label", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{klass}" text-anchor="{anchor}">{esc(value)}</text>'


def rect(x: float, y: float, width: float, height: float, color: str, radius: float = 5) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(width, 0):.1f}" height="{height:.1f}" rx="{radius}" fill="{color}"/>'


def model_note(alias: str, details: list[dict]) -> str:
    rows = [r for r in details if r.get("model_alias") == alias]
    failures = [r for r in rows if not r.get("request_completed")]
    invalid = [r for r in rows if r.get("request_completed") and not r.get("schema_compliant")]
    notes = []
    codes = sorted({str(r.get("request_error", {}).get("status_code")) for r in failures if r.get("request_error") and r["request_error"].get("status_code")})
    categories = sorted({r.get("request_error", {}).get("category", "provider error") for r in failures if r.get("request_error")})
    if failures:
        notes.append(f"{len(failures)} request error(s)" + (f" (HTTP {', '.join(codes)})" if codes else f" ({', '.join(categories)})"))
    if invalid:
        n_truncated = sum(bool(r.get("truncated")) for r in invalid)
        notes.append(f"{len(invalid)} invalid output(s)" + (f", {n_truncated} truncated" if n_truncated else ""))
    return "; ".join(notes) if notes else "All responses passed schema validation"


def pipeline_chart(rows: list[dict], details: list[dict], out: Path) -> None:
    lines = svg_start(
        "Evaluation run: request and output validity",
        "Five documents per model · completion and schema rates describe this run only",
        height=620,
    )
    x0, plot_w, top, row_h = 210, 580, 142, 90
    for tick in range(6):
        x = x0 + plot_w * tick / 5
        lines.append(f'<path d="M{x:.1f} 122 V{top + 4 * row_h - 15}" stroke="{COLORS["grid"]}"/>')
        lines.append(text(x, 116, f"{tick}", "axis", "middle"))
    for i, row in enumerate(rows):
        y = top + i * row_h
        alias = row["model_alias"]
        completed = int(row.get("request_completed", 0))
        parsed = int(row.get("json_parsed", 0))
        valid = int(row.get("schema_compliant", 0))
        attempted = int(row.get("attempted", 0))
        fail_n = max(attempted - completed, 0)
        lines.append(text(42, y + 14, alias, "label"))
        lines.append(text(42, y + 36, f"{completed}/{attempted} completed", "small"))
        # Full attempts track; filled stages represent completed requests.
        lines.append(rect(x0, y - 3, plot_w * attempted / 5, 18, "#edf0f4", 6))
        if completed:
            lines.append(rect(x0, y - 3, plot_w * completed / 5, 18, COLORS["blue"], 6))
            lines.append(rect(x0, y + 22, plot_w * parsed / 5, 12, COLORS["amber"], 5))
            lines.append(rect(x0, y + 42, plot_w * valid / 5, 12, COLORS["green"], 5))
            lines.append(text(x0 + plot_w * completed / 5 + 10, y + 11, f"request {completed}/{attempted}", "value"))
            lines.append(text(x0 + plot_w * parsed / 5 + 10, y + 33, f"JSON {parsed}/{attempted}", "small"))
            lines.append(text(x0 + plot_w * valid / 5 + 10, y + 53, f"schema {valid}/{attempted}", "small"))
            note = model_note(alias, details)
            if note != "All responses passed schema validation":
                lines.append(text(42, y + 74, note, "small"))
        else:
            lines.append(rect(x0, y - 3, plot_w * fail_n / 5, 18, "#f9dede", 6))
            lines.append(text(x0 + 12, y + 11, f"0/{attempted} completed", "value"))
            lines.append(text(x0, y + 38, model_note(alias, details), "small"))
    lines.extend([
        text(42, 545, "Rates are operational readiness signals, not extraction accuracy.", "small"),
        text(42, 568, "Schema compliance rate is conditional on provider requests that completed; bars also show end-to-end valid outputs.", "small"),
        "</svg>",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def performance_chart(rows: list[dict], out: Path) -> None:
    successful = [r for r in rows if r.get("model_alias") == "gemini_flash" and r.get("request_completed")]
    successful.sort(key=lambda r: float(r.get("latency_seconds") or 0), reverse=True)
    lines = svg_start(
        "Gemini Flash: observed time per document",
        "Successful requests · bars show provider request latency; token counts shown at right",
        height=470,
    )
    x0, plot_w, top, row_h = 365, 400, 142, 62
    max_latency = max((float(r.get("latency_seconds") or 0) for r in successful), default=1)
    max_latency = max(80, max_latency)
    for tick in range(5):
        val = max_latency * tick / 4
        x = x0 + plot_w * tick / 4
        lines.append(f'<path d="M{x:.1f} 120 V{top + len(successful) * row_h - 17}" stroke="{COLORS["grid"]}"/>')
        lines.append(text(x, 112, f"{val:.0f}s", "axis", "middle"))
    for i, row in enumerate(successful):
        y = top + i * row_h
        doc = Path(row["doc_id"]).stem
        latency = float(row.get("latency_seconds") or 0)
        in_tok = int(row.get("input_tokens") or 0)
        out_tok = int(row.get("output_tokens") or 0)
        short = doc.replace("00003_", "").replace("00002_", "").replace("00001_", "")
        lines.append(text(42, y + 15, short[:39], "label"))
        lines.append(rect(x0, y - 2, plot_w * latency / max_latency, 18, COLORS["blue"], 6))
        lines.append(text(x0 + plot_w + 18, y + 12, f"{latency:.1f}s", "value"))
        lines.append(text(42, y + 35, f"{in_tok:,} input · {out_tok:,} output tokens", "small"))
    lines.extend([
        text(42, 430, "Latency varies with document size and provider load; this sample is too small for a stable speed ranking.", "small"),
        "</svg>",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def write_summary(aggregate: list[dict], details: list[dict], out: Path) -> None:
    lines = [
        "# Archive evaluation graph notes", "",
        "This run measures request availability, JSON parsing, and archive schema validity. It does not measure whether extracted folklore is factually correct or complete: there are no field-level reference answers in this evaluation set.", "",
        "## Run results", "",
        "| Model alias | Requests completed | JSON parsed | Schema valid | What constrained the result |", "|---|---:|---:|---:|---|",
    ]
    detail_by_model: dict[str, list[dict]] = {}
    for row in details:
        detail_by_model.setdefault(row["model_alias"], []).append(row)
    for row in aggregate:
        name = row["model_alias"]
        attempted = int(row.get("attempted", 0))
        done = int(row.get("request_completed", 0))
        parsed = int(row.get("json_parsed", 0))
        valid = int(row.get("schema_compliant", 0))
        note = model_note(name, details)
        lines.append(f"| {name} | {done}/{attempted} ({done / attempted:.0%}) | {parsed}/{attempted} | {valid}/{attempted} | {note} |")
    flash = [r for r in details if r.get("model_alias") == "gemini_flash" and r.get("request_completed")]
    total_input = sum(int(r.get("input_tokens") or 0) for r in flash)
    total_output = sum(int(r.get("output_tokens") or 0) for r in flash)
    lines.extend([
        "", "## Charts", "",
        "![Request completion and output validity](request-validity.svg)", "",
        "![Gemini Flash latency by document](gemini-flash-latency.svg)", "",
        "## Reading the charts", "",
        *[f"- **{r['model_alias']}**: {int(r.get('schema_compliant', 0))}/{int(r.get('attempted', 0))} schema-valid outputs ({(r.get('schema_compliance_rate_of_completed') or 0):.0%} of completed responses)" + (f"; {model_note(r['model_alias'], details)}." if model_note(r['model_alias'], details) != "All responses passed schema validation" else ".") for r in aggregate],
        f"- Gemini Flash’s {len(flash)} successful responses used {total_input:,} input tokens and {total_output:,} output tokens. Latency ranges {min((float(r.get('latency_seconds') or 0) for r in flash), default=0):.1f}–{max((float(r.get('latency_seconds') or 0) for r in flash), default=0):.1f} seconds.",
        "", "## What efficacy is established", "",
        "Current evidence supports only operational reliability and output-contract compliance. It does not establish that any model extracted the right folklore or captured all relevant records. To compare extraction efficacy, add a reviewed gold set with expected records and score per-field precision, recall, and F1, plus citation/source-span accuracy and human review for cultural interpretation.",
        "", "Generated by `scripts/plot_evaluation.py` from `aggregate.json` and `per_document.json`.", "",
    ])
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("outputs/evaluation/archive/evaluation"))
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    out = args.output_dir or args.input_dir / "graphs"
    out.mkdir(parents=True, exist_ok=True)
    aggregate = json.loads((args.input_dir / "aggregate.json").read_text(encoding="utf-8"))
    details = json.loads((args.input_dir / "per_document.json").read_text(encoding="utf-8"))
    pipeline_chart(aggregate, details, out / "request-validity.svg")
    performance_chart(details, out / "gemini-flash-latency.svg")
    write_summary(aggregate, details, out / "README.md")
    print(f"Wrote charts and notes to {out}")


if __name__ == "__main__":
    main()

# Region v4: candidate aligned to the supplied annotation task

`regions_v4` keeps the prediction contract and all 20 label names unchanged. It preserves the frozen `regions_v1` and `regions_v3` prompts and locks. The update focuses on how to label, segment, transcribe, and box regions in a way that can be compared with the supplied annotation export.

## Reference contract

The raw export rows contain provenance and workflow metadata. The evaluator projects active rows to `page_num`, `label`, `text` (using `text_joined_final` with logged fallbacks), and `bbox` (from `region_bbox_norm`). Each prediction is scoped to one document by its run metadata, so it does not need a `doc_id` field. The prediction schema already matches these four evaluation fields.

The five target documents contain 104 active references across 20 labels. The full export contains 228 active annotations, including documents outside the current manifest. No reference rows, expected counts, or answer examples are included in provider requests.

## Prompt decisions

- Keep the existing 20 labels and the strict `annotations` array schema.
- Treat one coherent, visually contiguous source block as one annotation. Split at paragraph/layout boundaries and page boundaries; do not merge a multi-paragraph narrative into one large region.
- Return all supported repeated regions; there is no one-per-label limit.
- Copy source OCR faithfully and use its word coordinates. The reference audit flags candidate OCR/text discrepancies for human review; do not silently reproduce a reference-side OCR correction.
- Preserve distinctions among item, translation, informant explanation, collector analysis, learning/collection context, folklore origin, informant background, and addresses.
- Keep the label definitions versioned in `labels_regions_v4.json`; the earlier candidate definitions are unchanged.

The annotation export is the benchmark convention for labels and region boundaries, but its labels are still being interpreted from examples. In particular, `informant_region` has mixed-looking examples and should be reviewed before describing its definition as authoritative.

## Evaluation

Use `.venv/bin/python -m folklore_eval predict --phase evaluation --target regions --prompt-version regions_v4 --concurrency 4 --timeout-seconds 300`, then evaluate and report with the same target and prompt version. Concurrency defaults to 1; the four-request cap reduces wall time without an unbounded request burst. Gemini medium/high aliases share one model quota. The five documents have already informed prompt revisions, so report the result as development-set performance rather than a held-out estimate. Text and box scores are reported separately; reference/OCR mismatch flags remain visible in `review_flags.json`.

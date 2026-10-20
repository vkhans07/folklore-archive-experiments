# Annotation benchmark compatibility audit (2026-10-18)

## Finding

The existing region benchmark cannot legitimately score any archive-target prediction. There are zero region prediction artifacts (`predictions.json` or JSON objects containing an `annotations` array) under `outputs/`. The 92 run records under `outputs/runs/archive/evaluation/` are archive-target requests; 19 have a schema-compliant `archive.json`, and these contain the nested archive record contract, not region annotations. No output carries a page-local labeled box. A region precision/recall/F1, text match, IoU, or matched edit-distance score cannot be computed from these outputs. Creating boxes from the archive text or assigning region labels to archive fields would fabricate predictions and/or use unresolved mappings.

The region evaluator in `folklore_eval/evaluate.py` requires predictions with `page_num`, `label`, `text`, and normalized `bbox`; its region matching and metrics live in `folklore_eval/matching.py`. The independent schema in `config/annotation.schema.json` enforces those fields. The archive prompt and schema (`config/prompt_archive_v2.txt`, `config/archive.schema.json`) explicitly return a nested record with no labels or boxes. This is a task-contract mismatch, not merely a missing optional metric.

## Concrete example

A schema-compliant existing archive output at `outputs/runs/archive/evaluation/gemini_flash/00001_09_Taiwan_holiday_lore__93/fff8d665b86d3ae416da1f8bd5d9945e4fb8845a07973aa3efee1f8c76d02d99/archive.json` has keys such as `contributor`, `folklore`, `collector`, `analysis`, and `cleaned_full_text`; it has no `annotations` array, page number, or box. Its `folklore.item` contains the primary folklore content as one field, rather than a page-local `folklore_item` prediction.

The actual reference export `JSONs/Taiwan Holiday Lore.json` includes a row for that same document with `page_num: 0`, `label: "folklore_genre"`, `text_joined_final: "Legend"`, and `region_bbox_norm: [0.1042413, 0.0874756, 0.1724154, 0.1168518]`. The archive prompt has no `folklore_genre` field and the archive output has no location for that label or box. The candidate mapping document `config/archive_region_relationship.md` explicitly describes possible mappings as unconfirmed review candidates and lists unresolved repeated-region, identity, normalization, and field-selection decisions. Applying any of those candidates as if confirmed would not be a defensible reference transformation.

## Reference inventory

The five JSON exports in `JSONs/` each contain 226 rows and are byte-identical duplicates by the export loader's SHA-256 deduplication behavior. Against the five locally prepared document IDs, there are 102 active reference rows: Taiwan 17, Turkey 18, Thailand 19, Anglo Folkspeech 17, and Legend Vietnam 31. Their labels include 20 distinct region types. These are real region references with text and normalized boxes, but they do not turn the archive records into region predictions.

## What can be reported from existing archive outputs

- For the archive task: request completion, JSON parsing, and archive-schema compliance (the existing archive evaluation reports these operational metrics). These are not annotation accuracy metrics.
- For the region task: no prediction-dependent metric is available because the count of compatible region predictions is zero.
- OCR/reference diagnostics such as reference-box-to-OCR overlap can be assessed separately as reference quality checks; they do not score archive predictions and must not be presented as model accuracy.
- A source-text comparison between `cleaned_full_text` and OCR/reference text is not a region benchmark: reference rows are snippets selected and labeled for different semantic roles, and archive source-text output is a document-level transcription. It would be misleading to treat those fields as comparable truth without a separately specified diagnostic protocol.

## Missing requirements for a valid region benchmark

1. A region-target generation run on the exact prepared OCR input, producing an `annotations` array with configured labels, zero-based page numbers, source text, and normalized boxes.
2. Compatible reference rows for the same document IDs and pages (already present locally), with canonical references deduplicated and integrity checked.
3. A frozen region prompt/schema/model-run record tied to the prediction artifacts, then evaluation using the existing region matcher.
4. If archive-target field accuracy is desired instead, a reviewed archive reference set and explicit decisions for every field mapping, repeated-region aggregation, date/age handling, contributor identity, collector-comment destination, and location derivation. Those requirements are not met by current exports or candidate mapping notes.

No annotation or reference content was added to model inputs during this audit. No source/configuration, predictions, or aggregate reports were modified. Existing prepared inputs and references were read locally; any stale absolute source paths should be resolved through local manifest-relative paths for future reruns, without editing archived request inputs.

## Recommended next step

Treat the current annotation benchmark as blocked on target incompatibility. If the objective is region annotation quality, generate genuine `--target regions` predictions for the chosen evaluation documents and score those against the existing matched reference rows. Keep the archive benchmark limited to request/parse/schema status until a reviewed archive reference and mapping protocol exists.

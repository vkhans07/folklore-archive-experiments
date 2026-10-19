# Folklore extraction and region evaluation

This small Python package prepares five OCR'd folklore PDFs for zero-shot extraction. The current default prompt produces the supplied **nested archive JSON**. The original labeled-region prompt and evaluator remain available with `--target regions`. It **extracts the existing PDF text layer** and word coordinates; it does not run OCR. Original PDFs and annotation exports stay in `JSONs/`. Generated files go to ignored `outputs/`.

## Setup

Python 3.9+ is required. From this repository:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

The repository has a Git-ignored `.env` starter and a tracked `.env.example`. Copy the example to `.env`, then add a Google AI Studio Gemini API key and an Anthropic API key. If the Anthropic key can access multiple workspaces, also set `ANTHROPIC_WORKSPACE_ID` from Claude Console → Settings → Workspaces. The shell environment takes precedence over `.env`. Model IDs, Gemini thinking levels, generation settings, and transport settings can be overridden there; `config/models.json` supplies defaults. The configured models are Claude Sonnet 5.5 and Haiku 5.5 through the [Anthropic Python SDK](https://platform.claude.com/docs/en/api/sdks/python), plus [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) at medium and high thinking levels through Google's Gemini API. Gemini's high thinking setting is the supported extended reasoning option for text extraction; Gemini 3.8 Live Extended Thinking is for real time audio sessions. Each provider uses its own API key, billing, and rate limits. API keys are never saved in run artifacts.

## Exact workflow

```bash
# Extract all five PDF text layers and normalized word boxes.
.venv/bin/python -m folklore_eval prepare

# Default archive target: run one document first.
.venv/bin/python -m folklore_eval predict --phase development --doc 00003_Legend_Vietnam__38.pdf --model sonnet --dry-run
.venv/bin/python -m folklore_eval predict --phase development --doc 00003_Legend_Vietnam__38.pdf --model sonnet
.venv/bin/python -m folklore_eval evaluate --phase development --doc 00003_Legend_Vietnam__38.pdf --model sonnet
.venv/bin/python -m folklore_eval report --phase development

# Run the same document with Gemini at medium or high thinking effort.
.venv/bin/python -m folklore_eval predict --phase development --doc 00003_Legend_Vietnam__38.pdf --model gemini_flash
.venv/bin/python -m folklore_eval predict --phase development --doc 00003_Legend_Vietnam__38.pdf --model gemini_flash_high

# Run it with Anthropic Haiku.
.venv/bin/python -m folklore_eval predict --phase development --doc 00003_Legend_Vietnam__38.pdf --model haiku

# Freeze the archive prompt and schema for evaluation.
.venv/bin/python -m folklore_eval freeze-prompt
.venv/bin/python -m folklore_eval predict --phase evaluation --dry-run
.venv/bin/python -m folklore_eval predict --phase evaluation
.venv/bin/python -m folklore_eval evaluate --phase evaluation
.venv/bin/python -m folklore_eval report --phase evaluation

# Original region labeling/scoring condition, kept separate.
.venv/bin/python -m folklore_eval predict --target regions --phase development --doc 00003_Legend_Vietnam__38.pdf --model sonnet --dry-run
.venv/bin/python -m folklore_eval predict --target regions --phase development --doc 00003_Legend_Vietnam__38.pdf --model sonnet
.venv/bin/python -m folklore_eval evaluate --target regions --phase development --doc 00003_Legend_Vietnam__38.pdf --model sonnet
.venv/bin/python -m folklore_eval report --target regions --phase development

# Benchmark-aligned region candidate with bounded parallel requests.
.venv/bin/python -m folklore_eval predict --target regions --prompt-version regions_v4 --phase evaluation --concurrency 4 --timeout-seconds 300 --max-attempts 3 --initial-backoff-seconds 10
.venv/bin/python -m folklore_eval evaluate --target regions --prompt-version regions_v4 --phase evaluation
.venv/bin/python -m folklore_eval report --target regions --prompt-version regions_v4 --phase evaluation
```

`predict` resumes completed responses by default, **including malformed outputs**. `--no-resume` makes a new preserved attempt. Transport errors are retried with bounded exponential backoff. A failed attempt is also preserved. The command summary and `run.json` include an error category, HTTP status, provider request ID (when returned), provider message/body, and a suggested next check. A dry run saves an exact request preview and never calls a provider. When `--doc` or `--model` is omitted, all manifest documents or all four configured models are selected. Evaluation-phase inference refuses to run if that target's frozen prompt or schema changes. Archive and region runs, and development and evaluation runs, use separate directories.

`--concurrency` sets a global cap on in-flight requests for one `predict` command; the default is 1. `--timeout-seconds`, `--max-attempts`, and `--initial-backoff-seconds` override transport settings for that invocation only. These settings are recorded with each run and affect cache identity. Higher concurrency can shorten wall time but may hit provider rate limits; Gemini medium and high aliases share the same underlying model quota.

## Files and data boundary

- `config/manifest.json` maps each local PDF path to its original `doc_id`. Preparation checks for missing files, repeated PDF mappings, and ambiguous duplicate PDF basenames. Evaluation checks page availability and the private integrity counts in `config/integrity.json`.
- `config/prompt_archive_v2.txt` is the **current default system prompt**. It requests the complete nested archive object, explains each field, sets `_id` to null until storage assigns one, copies `filename` from the prepared input, and uses null or empty arrays for unsupported values. `config/archive.schema.json` validates its output. The schema's literal `45-4` age bucket is treated in the v3 discussion draft as ages 45–54; the schema itself is unchanged.
- `config/prompt_archive_v3_draft.txt` is the clarified zero-shot prompt, selectable with `--prompt-version archive_v3`; its separate lock is `config/prompt_archive_v3.lock.json`, leaving the v2 baseline lock untouched. `config/prompt_archive_v3_notes.md` records the archive owner's field-rule decisions and the remaining few-shot example need for item/translation boundaries. The five-document development run completed for all four configured models; benchmark evaluation is still pending.
- [The v3 findings and review checklist](reviews/archive_v3_findings.md) covers all 20 outputs, with source/output dossiers, transcription examples, and prioritized human review cases. Rebuild the local evidence bundle with `.venv/bin/python scripts/review_archive_v3.py`; this makes no provider calls.
- [Saved archive v3 results — all 20 outputs, NO bounding boxes](SAVED_RESULTS_ARCHIVE_V3_NO_BOUNDING_BOXES_ALL_20_OUTPUTS_2026-10-19.json) bundles the outputs, metadata, prompt/schema, and findings. [Bounding-box next steps](reviews/bounding_box_next_steps.md) explains the existing region task and the changes needed for a clarified or combined output contract.
- [Region v3 instructions and rule mapping](config/prompt_regions_v3_notes.md) carry archive clarifications into labeled bounding-box prediction. The benchmark-aligned [region v4 prompt notes](config/prompt_regions_v4_notes.md) refine region boundaries and label guidance while preserving the reference's 20-label prediction contract. Use `--target regions --prompt-version regions_v4` consistently on `predict`, `evaluate`, and `report`; its results are isolated under `outputs/runs/regions_v4/` and `outputs/evaluation/<phase>/regions_v4/`. V1 and v3 remain available as separate baselines; the default region version remains v1.
- `config/labels.json` contains the **20 label names found in the export**. Its definitions are provisional interpretations for review; they are not claimed to be authoritative. The original versioned `config/prompt_v1.txt` expands them for `--target regions`. No reference annotations, document-specific label lists, or expected counts enter either model request.
- `config/annotation.schema.json` describes the region prediction contract. Runtime validation additionally checks configured label membership, finite coordinates, positive dimensions, and page bounds. A prediction has `page_num`, `label`, `text`, and normalized top-left `bbox`; repeated labels are valid.
- `config/archive_region_relationship.md` lists possible relationships between the archive fields and region labels. No automatic transformation is implemented.
- `outputs/inputs/*.json` are canonical OCR inputs with the source PDF path, displayed page dimensions, and rotation. PyMuPDF text boxes are mapped through the page rotation matrix before normalization. `outputs/runs/archive/<phase>/...` and `outputs/runs/<phase>/...` keep archive and region runs separate. Each run saves the exact request, raw response, raw response text, parsed output if valid, and status/usage/latency metadata. The cache key covers target, phase, project, location, full request, prompt/schema/label hashes as applicable, and transport settings.
- Only the evaluator reads `JSONs/*.json`. It hashes all exports, ingests byte-identical files once, rejects repeated annotation IDs across distinct exports, and excludes `deleted_at` records. It uses `text_joined_final` when present, then `text_joined_user`, `text_joined_original`, `text_joined_derived`, and `text_joined`, in that order; every fallback is logged in `reference_audit.json`.
- `outputs/evaluation/archive/<phase>/` reports request completion, JSON parsing, and archive schema compliance. No field-level archive references were supplied, so it does not invent accuracy scores. `outputs/evaluation/<phase>/` contains the original region metrics, reference audit, manual review flags, and PNG overlays. Green boxes are references; red boxes are region predictions.

The region labels still come from the annotation export, and their definitions remain provisional: the archive field descriptions do not establish authoritative definitions for all 20 region labels. To evaluate regions after a prompt change, run `freeze-prompt --target regions` before an evaluation-phase region run.

## Scoring details

Request completion means the API returned a response. JSON parsing and target-specific schema compliance are separate rates over completed responses. Truncation (`stop_reason=max_tokens`) is recorded and is unusable. Invalid outputs are saved without automatic repair. Archive outputs have schema status only; the following extraction metrics apply only to `--target regions`.

Text exact matching uses a multiset intersection of `(document, page, label, text)` after Unicode NFC and whitespace normalization. Case and punctuation remain significant. This gives one-to-one matching even for repeated identical text. Region matching groups by document, page, and label; within each group it uses a Hungarian assignment with dummy unmatched nodes. Qualified edges have IoU at least 0.5, and the assignment maximizes **qualified match count first**, then total IoU. Unmatched predictions are false positives and unmatched references are false negatives. Character Levenshtein distance is reported for region-matched text pairs as a diagnostic; it does not determine either match set. Precision, recall, and F1 are micro-aggregated from counts; mean IoU and raw mean edit distance are weighted by matched region count. The report also includes a normalized character error rate: total edits divided by normalized reference characters in spatially matched regions. It excludes text from regions without a qualifying box match.

The five JSON export filenames in this repository are byte-identical. `reference_audit.json` records the canonical copy and all duplicate filenames without changing them. The five-document integrity counts are checked only by the evaluator and never sent to a model.

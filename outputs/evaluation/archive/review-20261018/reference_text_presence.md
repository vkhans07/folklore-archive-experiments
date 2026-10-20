# Reference-text presence diagnostic

This is a limited local comparison for the fixed pre-retry selection in `outputs/evaluation/archive/retry-20261018/before-selected-runs.json`. It includes the 14 schema-compliant archive outputs in that snapshot; six of its 20 selected runs were excluded because they were not schema-compliant. For each active reference row whose text was nonempty, the script checks exact substring presence after Unicode NFC normalization and whitespace collapsing. Case and punctuation are retained. It checks recursively in structured archive string leaves, excluding `cleaned_full_text`, then checks `cleaned_full_text` separately.

Across 276 reference/run comparisons (all references used `text_joined_final`; none were empty), text was present in at least one structured string leaf in 143 comparisons (51.8%) and in `cleaned_full_text` in 217 (78.6%). These are presence counts only. They are not precision, recall, F1, localization, or correctness: the check ignores reference label, page, box, duplication, and semantic role. Substring presence can be incidental, while absence can reflect paraphrase, OCR differences, or extraction choices. In particular, the checks do not assign any region label to an archive field.

| Model | Comparisons | Present in structured leaves | Present in `cleaned_full_text` |
|---|---:|---:|---:|
| gemini_flash | 85 | 46 | 68 |
| gemini_flash_high | 18 | 11 | 15 |
| haiku | 71 | 32 | 52 |
| sonnet | 102 | 54 | 82 |

Examples illustrate the distinction. For Taiwan / `informant_name` = “Linda Wei Chen”, the phrase occurs in `contributor.name` and in `cleaned_full_text`. For Taiwan / `folklore_genre` = “Legend”, it occurs in `cleaned_full_text` but not in any structured string leaf. A long `folklore_item` reference can miss both checks because the archive's source transcription differs in characters/formatting; that miss does not establish the folklore content is absent. The JSON report contains 12 examples each of structured-leaf hits, full-text-only hits, and misses in both, plus every comparison and grouped model/document/label counts.

Reference quality caveat: the existing evaluation reference audit reports 13 `reference_text_ocr_mismatch_candidate` flags across the full five-document set. These are review hints, not corrections. The diagnostic uses each row's existing `text_joined_final` and does not modify reference text. The five local export files are byte-identical; the evaluator deduplicates them by hash. No annotation or reference text was included in model inputs.

Reproduce with:

```sh
.venv/bin/python outputs/evaluation/archive/review-20261018/reference_text_presence.py
```

The script reads the fixed pre-retry selection and local reference export, then rewrites `reference_text_presence.json`. The JSON includes grouped counts by model/document/label, all 276 comparisons, example rows, excluded invalid runs, and limitations. This diagnostic is useful as a transparent text-presence probe alongside request/schema results, while the full region benchmark remains incompatible with archive outputs because there are no predicted labels or boxes.

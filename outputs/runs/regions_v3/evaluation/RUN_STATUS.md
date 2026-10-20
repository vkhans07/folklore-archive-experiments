# Region v3 inference run status

Run scope: 5 source documents × 4 model aliases, with prompt version `regions_v3`. Predictions are stored under this directory. Benchmark metrics were refreshed after retrying the four incomplete combinations; transport failures and invalid model output remain in the inventory below.

## Status by document and model

| Document | Sonnet | Haiku | Gemini medium | Gemini high |
|---|---|---|---|---|
| Legend Vietnam | Completed | Completed | Completed | Completed |
| Taiwan holiday lore | Completed | Completed | Completed | Completed |
| Turkey proverbs | Completed | Completed | Completed | Transport error after 3 attempts (timeout) |
| Thailand folkspeech | Completed | Completed | Completed | Transport error after 5 attempts (connection reset) |
| Anglo folkspeech | Completed | Completed | Response returned, invalid JSON | Completed |

## Inventory

- 17 of 20 combinations produced a schema-compliant prediction; 18 provider responses completed, one of which (Anglo/Gemini medium) was invalid JSON.
- 2 combinations have saved transport-error records: Turkey/Gemini high (read timeout after 3 attempts) and Thailand/Gemini high (connection reset after 5 attempts).
- All 20 expected document/model pairs have run records; there are no missing run records or unrecorded request artifacts.
- Anglo/Gemini medium returned a response, but its text did not parse as JSON. The raw response and error are preserved; it has no prediction and contributes no extraction matches.
- Evaluation output: `outputs/evaluation/evaluation/regions_v3/`. It contains per-document and aggregate JSON/CSV, reference audit, review flags, and prediction/reference box overlays.
- Request completion is 5/5 for Sonnet, Haiku, and Gemini medium, and 3/5 for Gemini high. Schema-compliant coverage is 5/5 for Sonnet and Haiku, 4/5 for Gemini medium, and 3/5 for Gemini high.
- Thirteen reference records are flagged as `reference_text_ocr_mismatch_candidate`; inspect `review_flags.json` before drawing conclusions from text metrics.

## Aggregate extraction metrics

Scores below micro-aggregate the schema-compliant predictions available for each model. Box matches require IoU ≥ 0.5; edit distance is measured only on box-matched text. Coverage differs across models.

| Model | Completed requests | Schema-compliant | Text F1 | Box F1 | Matched mean IoU | Matched character error rate | Raw edits / matched region |
|---|---:|---:|---:|---:|---:|---:|---:|
| Gemini medium | 5/5 | 4/5 | 0.306 | 0.437 | 0.660 | 15.03% | 13.48 |
| Gemini high | 3/5 | 3/5 | 0.349 | 0.635 | 0.677 | 8.80% | 10.28 |
| Haiku | 5/5 | 5/5 | 0.378 | 0.468 | 0.660 | 7.09% | 5.53 |
| Sonnet | 5/5 | 5/5 | 0.330 | 0.454 | 0.662 | 10.10% | 7.91 |

The character error rate is total Levenshtein edits divided by normalized reference characters in spatially matched regions. It excludes text from unmatched regions. Raw edit counts and the raw mean per matched region remain available in the CSV/JSON.

For visual inspection, open [`outputs/evaluation/evaluation/regions_v3/index.html`](../../../evaluation/evaluation/regions_v3/index.html). It contains the 38 rendered page overlays; green outlines are reference boxes and red outlines are predictions.

The retry and connectivity problems are recorded as run findings for review. A schema-compliant result only confirms output structure; it does not indicate annotation quality. These aggregate scores have incomplete and differing document coverage, so they are descriptive of available outputs rather than a complete four-model comparison.

# Region v4 evaluation status

Prompt: `regions_v4` (`3e0a3f912a54ba699833e3e3da9494b31776970df435552f422bc0c6e053e994`).
Scope: five documents, four model aliases, 104 active reference regions. All five documents informed prompt development, so these are development results rather than held-out performance.

## Aggregate results

For aggregate text, box, and OCR-word-label precision/recall, plus each model's weakest document, see [`model_summary.md`](model_summary.md).
Metric formulas and matching rules are documented in [`model_methods.md`](../../../../model_methods.md).

| Model | Completed | Schema-valid | Text F1 | Box F1 | Mean IoU | Matched-text CER |
|---|---:|---:|---:|---:|---:|---:|
| Gemini medium | 5/5 | 5/5 | 0.465 | 0.595 | 0.700 | 7.18% |
| Gemini high | 5/5 | 5/5 | 0.477 | 0.604 | 0.711 | 2.74% |
| Haiku | 5/5 | 5/5 | 0.381 | 0.577 | 0.698 | 4.58% |
| Sonnet | 5/5 | 5/5 | 0.414 | 0.550 | 0.705 | 5.12% |

All 20 model/document requests completed. Every response parsed as JSON and passed the region schema; all 40 prediction/reference overlay images were regenerated against the corrected references.

## Taiwan reference correction

The source export now includes the missing page 2 (`page_num: 1`) `informant_name` “Linda Wei Chen” and the final paragraph labeled `collector_annotation`. Both reference boxes are the unions of the supplied OCR word boxes. The updated sample has 19 active Taiwan regions and 104 active regions across the five-document evaluation. See [`reference_corrections.md`](../../../../config/reference_corrections.md) for provenance.

The existing model predictions were rescored against the corrected references; no new model requests were needed. Taiwan per-document scores are in `per_document.csv`.

## Interpretation and comparison limits

The v4 prompt was tuned using these same five documents. Treat these scores as development feedback rather than an estimate of performance on unseen documents. The v3 comparison is not a controlled prompt-only comparison: transport settings differed, and some v4 results were generated on retries with longer timeouts and request concurrency. Per-request settings and response records are retained with the run artifacts. The v3 aggregate and per-document results were also rescored against the corrected sample.

## Parallel requests

The predictor supports bounded request-level parallelism with `--concurrency N`. For example, `--concurrency 3 --timeout-seconds 300` runs up to three document requests at once. Provider rate limits and latency still affect throughput. Successful responses are cached, so retries can target only failed requests.

## Visual review

Open [`index.html`](index.html) for prediction/reference box overlays. Green is reference; red is prediction. Machine-readable metrics and audits are in `aggregate.csv`, `per_document.csv`, `review_flags.json`, and `reference_audit.json`.

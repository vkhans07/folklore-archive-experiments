# Model-wide region evaluation summary

Precision, recall, and F1 are micro-aggregated across documents. The weakest document is the one with the lowest per-document box F1; its text F1 is shown for context.
Estimated costs use recorded token usage and the rates in [`model_pricing.json`](../../../../config/model_pricing.json) (USD, as of 2026-10-19). Thinking tokens and cached-input rates are included where recorded; cache-storage charges and timed-out attempts without usage data are excluded.

| Model | Completed | Text P | Text R | Text F1 | Box P | Box R | Box F1 | Word-label P | Word-label R | Word-label F1 | Est. cost | Avg. / priced request | Weakest document (box F1; text F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gemini_flash | 5/5 | 0.450 | 0.481 | 0.465 | 0.577 | 0.615 | 0.595 | 0.795 | 0.789 | 0.792 | $0.4992 | $0.09984 | Thailand Folkspeech (0.324; 0.324) |
| gemini_flash_high | 5/5 | 0.449 | 0.510 | 0.477 | 0.568 | 0.644 | 0.604 | 0.851 | 0.853 | 0.852 | $1.0231 | $0.20463 | Thailand Folkspeech (0.263; 0.316) |
| haiku | 5/5 | 0.369 | 0.394 | 0.381 | 0.559 | 0.596 | 0.577 | 0.786 | 0.784 | 0.785 | $0.2038 | $0.04076 | Thailand Folkspeech (0.222; 0.222) |
| sonnet | 5/5 | 0.390 | 0.442 | 0.414 | 0.517 | 0.587 | 0.550 | 0.789 | 0.779 | 0.784 | $0.6048 | $0.12096 | Thailand Folkspeech (0.205; 0.256) |

See [`per_document.csv`](per_document.csv) for every document/model score and request record.
Read the [metric and matching methods](../../../../model_methods.md) for formulas and validation rules.

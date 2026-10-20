# Model-wide region evaluation summary

Precision, recall, and F1 are micro-aggregated across documents. The weakest document is the one with the lowest per-document box F1; its text F1 is shown for context.
Estimated costs use recorded token usage and the rates in [`model_pricing.json`](../../../../config/model_pricing.json) (USD, as of 2026-10-19). Thinking tokens and cached-input rates are included where recorded; cache-storage charges and timed-out attempts without usage data are excluded.

| Model | Completed | Text P | Text R | Text F1 | Box P | Box R | Box F1 | Word-label P | Word-label R | Word-label F1 | Est. cost | Avg. / priced request | Weakest document (box F1; text F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gemini_flash | 5/5 | 0.370 | 0.288 | 0.324 | 0.519 | 0.404 | 0.454 | 0.793 | 0.732 | 0.761 | $0.5457 | $0.10914 | Anglo Folkspeech VI (0.000; 0.000) |
| gemini_flash_high | 3/5 | 0.393 | 0.358 | 0.375 | 0.689 | 0.627 | 0.656 | 0.886 | 0.890 | 0.888 | $0.6203 | $0.20676 | Legend Vietnam 38 (0.519; 0.222) |
| haiku | 5/5 | 0.384 | 0.365 | 0.374 | 0.485 | 0.462 | 0.473 | 0.771 | 0.748 | 0.759 | $0.1726 | $0.03451 | Thailand Folkspeech (0.343; 0.400) |
| sonnet | 5/5 | 0.348 | 0.308 | 0.327 | 0.489 | 0.433 | 0.459 | 0.757 | 0.736 | 0.746 | $0.5441 | $0.10881 | Thailand Folkspeech (0.235; 0.294) |

See [`per_document.csv`](per_document.csv) for every document/model score and request record.
Read the [metric and matching methods](../../../../model_methods.md) for formulas and validation rules.

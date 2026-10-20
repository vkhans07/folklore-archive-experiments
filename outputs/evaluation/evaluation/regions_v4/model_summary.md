# Model-wide region evaluation summary

Precision, recall, and F1 are micro-aggregated across documents. The weakest document is the one with the lowest per-document box F1; its box F1 and OCR word-label F1 are shown.
Estimated costs use recorded token usage and the rates in [`model_pricing.json`](../../../../config/model_pricing.json) (USD, as of 2026-10-19). Thinking tokens and cached-input rates are included where recorded; cache-storage charges and timed-out attempts without usage data are excluded.

| Model | Completed | Text P | Text R | Text F1 | Box P | Box R | Box F1 | Word-label P | Word-label R | Word-label F1 | Est. cost | Avg. / priced request | Weakest document (box F1; word-label F1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| astra | 5/5 | 0.432 | 0.519 | 0.472 | 0.633 | 0.663 | 0.648 | 0.873 | 0.893 | 0.882 | $2.2755 | $0.45509 | Thailand Folkspeech (0.343; 0.741) |
| gemini_flash | 5/5 | 0.450 | 0.481 | 0.465 | 0.674 | 0.615 | 0.643 | 0.795 | 0.789 | 0.792 | $0.4992 | $0.09984 | Thailand Folkspeech (0.364; 0.701) |
| gemini_flash_high | 5/5 | 0.449 | 0.510 | 0.477 | 0.650 | 0.644 | 0.647 | 0.851 | 0.853 | 0.852 | $1.0231 | $0.20463 | Thailand Folkspeech (0.303; 0.649) |
| haiku | 5/5 | 0.369 | 0.394 | 0.381 | 0.646 | 0.596 | 0.620 | 0.786 | 0.784 | 0.785 | $0.2038 | $0.04076 | Thailand Folkspeech (0.242; 0.505) |
| opus | 5/5 | 0.431 | 0.481 | 0.455 | 0.677 | 0.644 | 0.660 | 0.826 | 0.831 | 0.829 | $1.2043 | $0.24087 | Thailand Folkspeech (0.364; 0.746) |
| sonnet | 5/5 | 0.390 | 0.442 | 0.414 | 0.642 | 0.587 | 0.613 | 0.789 | 0.779 | 0.784 | $0.6048 | $0.12096 | Thailand Folkspeech (0.250; 0.660) |

## Aggregate scores excluding Thailand

Micro-aggregated across the other four documents; this is a diagnostic view of how much Thailand affects the overall scores.

| Model | Completed | Text P | Text R | Text F1 | Box P | Box R | Box F1 | Word-label P | Word-label R | Word-label F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| astra | 4/4 | 0.456 | 0.553 | 0.500 | 0.677 | 0.741 | 0.708 | 0.881 | 0.902 | 0.891 |
| gemini_flash | 4/4 | 0.473 | 0.518 | 0.494 | 0.716 | 0.682 | 0.699 | 0.798 | 0.797 | 0.798 |
| gemini_flash_high | 4/4 | 0.475 | 0.553 | 0.511 | 0.697 | 0.729 | 0.713 | 0.861 | 0.868 | 0.864 |
| haiku | 4/4 | 0.394 | 0.435 | 0.413 | 0.707 | 0.682 | 0.695 | 0.806 | 0.800 | 0.803 |
| opus | 4/4 | 0.458 | 0.518 | 0.486 | 0.718 | 0.718 | 0.718 | 0.831 | 0.837 | 0.834 |
| sonnet | 4/4 | 0.418 | 0.482 | 0.448 | 0.695 | 0.671 | 0.683 | 0.793 | 0.790 | 0.791 |

See [`per_document.csv`](per_document.csv) for every document/model score and request record.
Read the [metric and matching methods](../../../../model_methods.md) for formulas and validation rules.

# Model evaluation methods

This note describes the region evaluation used for the v1, v3, and v4 reports. The current v4 run covers five development documents and 104 active reference regions. Because the prompt was revised using these documents, these scores are development results, not held-out estimates.

## Predictions and references

- **Prediction:** a region annotation returned by the model for a document: its page, label, text, and box.
- **Reference:** a region annotation in the supplied sample data, used as the comparison target. References are human-provided labels and boxes; they can still have omissions or errors, which is why the Taiwan sample was corrected.

The evaluator compares predictions with references. It does not independently determine which annotation is factually right: the score measures agreement with the current references under the matching rules below. The OCR boxes are model input; they are not themselves predictions unless the model returns them as annotations.

## Box matching and box precision/recall

Each annotation has a zero-based page number, a label, text, and a normalized box `[x0, y0, x1, y1]`. A predicted region can match a reference region only when both its page and label are the same. The evaluator calculates intersection-over-union (IoU):

`IoU = area(prediction ∩ reference) / area(prediction ∪ reference)`

Pairs with IoU of at least `0.50` are eligible. Within each page-and-label group, the evaluator chooses a one-to-one assignment that first maximizes the number of eligible pairs, then maximizes their total IoU. A prediction and reference can each be used in at most one pair.

- **Box TP:** number of matched pairs.
- **Box FP:** predicted regions left unmatched, except that an unmatched prediction fully contained by any same-page, same-label reference is exempt from FP counting. This directional exception reflects the observed looser reference boxes. It does not create a TP, affect FN counting, or apply when a reference is contained by a prediction. Thus a contained prediction can be exempt from FP while its reference remains an FN if no prediction reaches the IoU threshold.
- **Box FN:** reference regions left unmatched.
- **Box precision:** `box TP / (box TP + box FP)`; after the containment exception, this denominator can be smaller than the raw prediction count.
- **Box recall:** `box TP / (box TP + box FN)`, equivalently `box TP / reference count`.
- **Box F1:** harmonic mean of box precision and box recall: `2 × P × R / (P + R)`.

Thus “box” scoring checks localization and label together. Text does not affect whether a box pair matches. Mean IoU is the average IoU among matched pairs; it describes overlap quality after matching and does not count unmatched regions.

## Text matching and text precision/recall

Text matching is calculated separately from box matching. A prediction is an exact-text match when it has the same page, label, and text as a reference. Text comparison applies Unicode NFC normalization and collapses whitespace; it remains case- and punctuation-sensitive. Duplicate identical annotations are counted as a multiset, so each reference or prediction can contribute at most once.

- **Text TP:** exact-text matches.
- **Text FP:** predictions without an exact-text match.
- **Text FN:** references without an exact-text match.
- **Text precision, recall, and F1:** calculated from those counts with the same formulas as the box metrics.

An annotation can count as a box match and still fail exact-text matching. Conversely, matching text does not require a matching box.

The report also includes character error rate for box-matched pairs. It sums character-level Levenshtein edit distance over matched pairs and divides by the total normalized character count in those matched references. It is a transcription measure conditioned on box matches; lower is better.

## OCR-word label coverage (boundary-tolerant)

This parallel metric asks whether the model assigned the right label to the OCR words, without requiring the prediction to use the same paragraph or line grouping as the reference. For each annotation, a page-local OCR word is covered when the word-box center falls inside the annotation box. The metric then compares sets of `(page number, OCR word index, label)` from references and predictions.

- **Word-label TP:** OCR word/label pairs covered by both a prediction and a reference.
- **Word-label FP:** predicted OCR word/label pairs absent from the references.
- **Word-label FN:** reference OCR word/label pairs absent from the predictions.
- **Word-label precision, recall, and F1:** computed from those counts using the standard formulas above.

The same OCR word may carry more than one label when the source annotations overlap. Duplicate boxes with the same label do not count a word-label pair more than once. Splitting or merging boxes does not change this metric if the same words remain covered by the same labels. This score evaluates label coverage and approximate localization on OCR words; it does not evaluate the model's transcription. It also depends on the supplied OCR and its word boxes, so OCR omissions or bad word boxes limit what it can measure.

## JSON and schema compliance

For region responses, the validator requires exactly one top-level `annotations` array. Each annotation must contain exactly `page_num`, `label`, `text`, and `bbox`. The page number must be an integer on the document; the label must be in the allowed vocabulary; text must be a string; and the box must have four finite normalized coordinates in `[0, 1]` with positive width and height.

- **JSON parsed:** response text was valid JSON.
- **Schema compliant:** the parsed response passed all region structure, label, page, text-type, and box checks.
- **Schema compliance rate:** compliant completed responses divided by completed requests.

These checks evaluate output format, not annotation accuracy. For a completed but schema-invalid response, the evaluator records the request as completed but scores its annotations as empty. A request that did not complete has unavailable content metrics and is shown in the coverage counts.

## Model-wide aggregates

Model-wide text, box, and word-label precision, recall, and F1 are **micro-averaged**: the evaluator sums TP, FP, and FN counts over completed documents for a model, then computes the metrics from those totals. It does not average the five document-level scores. Coverage and schema rates are reported separately, so an incomplete model run is visible and its content scores use only completed requests.

The model summary identifies the weakest document as the completed document with the lowest box F1 and shows that document’s text F1 for context. Per-document rows remain available in `per_document.csv`.

## Estimated API cost

Cost estimates multiply each request's recorded token usage by the listed standard paid API rates. Prices are USD per million tokens and were checked on 2026-10-19:

| Model | Input / output rate |
|---|---|
| Gemini 3.8 Flash (medium and high thinking aliases) | $0.75 / $3.75; cached input $0.075 |
| Claude Haiku 5.5 | $0.10 / $0.50 for prompts up to 100,000 input tokens; $0.50 / $2.50 above that threshold |
| Claude Sonnet 5.5 | $2 / $10 |
| Claude Opus 5.5 | $4 / $20; cached input $0.20 |
| GPT-6 Astra | $10 / $50; cached input $1 |

The Gemini rate is the Standard tier introductory price through December 31, 2026. Gemini output pricing includes thinking tokens, so where the raw response records them they are included. Gemini cached input is billed at the context-cache rate; the additional cache-storage charge is excluded because cache storage duration is not in the run records. Anthropic prompt length uses all input tokens; the Taiwan calls for Haiku fall in the lower rate tier, while the 124,728-token Vietnam call uses the over-100,000-token tier. Anthropic thinking tokens are included in its recorded output-token count.

These are estimates from successful responses' recorded usage, not invoice totals. Timed-out attempts without usage metadata are excluded, as are account-specific discounts, credits, taxes, and any free-tier treatment. OpenAI output usage includes reasoning tokens. The per-document CSV contains the input/output cost components and estimated total for each completed run. Current rates and source URLs are recorded in `config/model_pricing.json`.

Pricing sources: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [Anthropic Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Anthropic Haiku 5.5 pricing announcement](https://www.anthropic.com/claude-haiku-5-5), and [GPT-6 Astra pricing](https://developers.openai.com/api/docs/models/gpt-6-astra).

## Current files

- [v4 model-wide summary](outputs/evaluation/evaluation/regions_v4/model_summary.md)
- [v4 per-document results](outputs/evaluation/evaluation/regions_v4/per_document.csv)
- [v4 aggregate metrics](outputs/evaluation/evaluation/regions_v4/aggregate.csv)
- [v4 box overlay gallery](outputs/evaluation/evaluation/regions_v4/index.html)

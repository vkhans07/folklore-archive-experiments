# Archive v3: findings and review checklist

Reviewed October 19, 2026 UTC. Scope: the 20 saved development outputs from five documents and four models, selected by frozen v3 prompt hash `b82d16d17fcdbef0dc02715d86c90a02709e23b24f7efacb80659fe494dc07ba`.

All 20 responses are valid JSON and pass the archive schema. The substantive issues are transcription fidelity, boundaries of the relevant document body, tentative identity assignments, and placement/attribution of interpretation. A few-shot set should demonstrate these specific cases. No extraction accuracy ranking or region precision/recall/F1 is established by this review.

## Evidence and limits

I reviewed structured outputs across all 20 runs against all supplied OCR pages, and compared each complete `cleaned_full_text` with the input word sequence. The companion script re-parses the provider text, checks it against saved archive JSON, validates the schema, and checks input/prompt/schema hashes. The input is the PDF text layer; scanned page pixels were not inspected. Questions about garbled Thai text and the meaning of unlabeled header rows need the original page images. Differences between models are review leads, not a majority-vote ground truth.

The source-and-output dossiers contain every field, source OCR grouped by page, raw-output links, and full-text differences:

- [Thailand dossier](../outputs/reviews/archive_v3/Thailand.md)
- [Vietnam dossier](../outputs/reviews/archive_v3/Vietnam.md)
- [Taiwan dossier](../outputs/reviews/archive_v3/Taiwan.md)
- [Anglo Folkspeech dossier](../outputs/reviews/archive_v3/Anglo.md)
- [Turkey dossier](../outputs/reviews/archive_v3/Turkey.md)

[Machine-readable evidence and exact run paths](../outputs/reviews/archive_v3/evidence.json). Reproduce with `.venv/bin/python scripts/review_archive_v3.py`. No provider calls are made.

## Findings to flag

### 1. Full-text boundaries remain inconsistent — high priority

**16/20 `cleaned_full_text` values retain a source street-address block.** The count uses one explicit address marker per document and is reproducible in the evidence JSON. Retention occurs in Sonnet 5/5, Haiku 3/5, Gemini medium 4/5, and Gemini high 4/5. Introductory contributor/header material also remains in 19/20; Haiku/Taiwan is the sole output starting directly with the tale.

This is inconsistent with the requested relevant-body transcription, especially when addresses interrupt sentences:

- **Taiwan, Sonnet and Gemini medium:** the page-one footer survives between “the month and the” and “day, as in the seventh day…”. The inserted collector/address block breaks a body sentence. Gemini high and Haiku remove it correctly.
- **Vietnam, Sonnet and Gemini high:** the first-page collector/address block remains in the full text, although later repeating page labels are removed.
- **Thailand, all four; Turkey, all four; Anglo, all four:** closing street-address blocks remain. Sonnet/Thailand also retains the marginal OCR `Aaland “Fore sfeecn`.

**What to review:** mark a concrete example of body start/end and the treatment of embedded page footers. Decide from that example whether relevant contextual/analysis paragraphs belong in the body transcription; the models generally preserve them. Do not use “every source word retained” as a success metric for this field under the clarified rule.

### 2. Some fields silently rewrite OCR — confirmed fidelity issues

Whitespace cleanup is allowed. Adding words or changing source characters is not covered by that allowance. Concrete examples:

| Document/model | Field | Source → output | Assessment |
|---|---|---|---|
| Thailand / Sonnet | `contributor.ethnicity` | `‘Thai and 4" generation Chinese in Thailand` → `Thai and 4th generation Chinese in Thailand` | Repairs suspect OCR despite the preservation rule. Full text retains the original, so the two fields disagree. |
| Vietnam / Haiku | `cleaned_full_text`, `analysis.context.collection_context` | `This one was very popular story among the kids.` → `This one was a very popular story among the kids.` | Adds `a`; grammatical cleanup rather than verbatim extraction. Source p. 3. |
| Taiwan / Haiku | `cleaned_full_text`, `analysis.collector_comments` | `world, Also,` → `world. Also,` in full text; the extracted comment ends `world.` | Changes punctuation. Source p. 2. |
| Taiwan / Sonnet | `analysis.context.collection_context` | `Linda Wei was born…` → `Linda Wei Chen was born…` | Expands the name from the header. The identity is supported, but the passage is rewritten. Source p. 1. |
| Turkey / Haiku | `analysis.context.collection_context` | Adds the assembled sentence `Collected at dorm, Berkeley, Ca., November 19, 1997.` | Facts are in the header, but the sentence is synthesized. |
| Anglo / Haiku | `cleaned_full_text`, `analysis.interpretation` | `it’s` → `it's` | Changes apostrophe characters; a small but real fidelity discrepancy. |

These examples are not an exhaustive error count. Changes such as `long- established` → `long-established` or removing a space before punctuation are whitespace differences and should not be penalized under the current allowance.

**Positive control:** all four Turkey outputs preserve `Erench` in `languages_spoken`. A reviewer should not correct that to French when assessing compliance with the current OCR-preservation rule.

### 3. Thailand is the best first few-shot example — multiple unresolved boundaries

See [Thailand, source p. 1 and all four outputs](../outputs/reviews/archive_v3/Thailand.md).

| Model | Contributor | Collector | Word-by-word gloss |
|---|---|---|---|
| Sonnet | null | Varinthorn Nakkeow | Puts `three /day /good/ —_four/ day / fever/` in `item`; only the fluent translation is in `translation`. |
| Haiku | Varinthorn Nakkeow | null | Gloss and fluent translation are both in `translation`. |
| Gemini medium | Varinthorn Nakkeow | Varinthorn Nakkeow | Gloss and fluent translation are both in `translation`. |
| Gemini high | Varinthorn Nakkeow | Varinthorn Nakkeow | Gloss and fluent translation are both in `translation`. |

The source has `Myself, Age 21. Female` at the top and `Varinthorn Nakkeow, Age 21.` at the bottom. The Gemini interpretations fit a plausible self-collected account; the Anthropic models explain their uncertainty but each leaves one role blank. Because you left attribution to model judgment, these are candidates to adjudicate, not automatic errors. They do show that your preference for potential answers has not produced consistent behavior.

The two Gemini outputs put `mutual aly` into `item`; Sonnet and Haiku leave it out of that field. All retain it in full text. Gemini high further proposes the Thai string `สำนวนไทย` in an uncertainty comment; those characters are absent from the supplied OCR. Treat this as an unverified reconstruction, not extracted source text, even though it is explicitly hedged.

Sonnet also puts the roommate's behavior into `analysis.interpretation`, while the explicit statement “This bit of folk speech is a personality description…” is in `use_context`. The other three put that meaning statement in `interpretation`.

**What to review:** the original page image for heading versus proverb; item/transliteration/gloss boundaries; whether to fill both person roles with a doubt note; and which sentence expresses the proverb's meaning. Approve one complete example demonstrating all of these together.

### 4. Vietnam interpretation fields blur who said what — high priority

See [Vietnam, source pp. 4–5 and all four analyses](../outputs/reviews/archive_v3/Vietnam.md).

The source explicitly introduces the contributor's explanation with “My mom, the contributor of this story, believes…”, followed by reincarnation, karma, and fish symbolism. The surrounding feminist reading is the document author's analysis.

- **Gemini medium:** keeps the contributor explanation together in `interpretation` and puts much of the author's evaluation in `analysis.collector_comments`.
- **Sonnet:** keeps only the introductory contributor sentence in `interpretation`; the following reincarnation/karma/fish explanations appear in `analysis.collector_comments`. The original link to the contributor is weakened by the split.
- **Haiku:** also leaves the introductory sentence in `interpretation` but moves the explanation into `cultural_background`.
- **Gemini high:** puts the contributor explanation into `cultural_background`, while the author's feminist reading occupies `interpretation`.

These passages are present in the source; the problem is attribution and field placement, rather than invented analysis. Flexible comment fields do not by themselves preserve speaker identity. Sonnet additionally repeats the bedtime-use passage in both `use_context` and analysis comments, and repeats Turkey's age-of-users sentence in `use_context` and analysis comments.

**What to review:** approve a passage-level allocation for the contributor explanation and the author's analysis, retaining the attribution sentence with its explanation. This should be a second few-shot example. Give uncertainty notes an identifiable prefix within the existing fields so they can be distinguished from source collector remarks.

There is also an instruction conflict to resolve in a future prompt: it globally requires copying source wording, but separately asks for newly written uncertainty notes. The latter needs an explicit, labeled exception so a model's doubt cannot be mistaken for a quotation from the source collector. The frozen v3 prompt was not changed during this review.

### 5. Header-derived information is uneven — domain review needed

| Case | Observed difference | Review target |
|---|---|---|
| Vietnam p. 1 | Gemini medium/high return `languages_spoken: ["Vietnamese"]`; Sonnet/Haiku return `[]`. | Inspect the standalone `Vietnamese` row, distinct from the folklore genre label. |
| Anglo p. 1 | Only Gemini high returns Vietnamese as a spoken language. | Inspect the repeated `Vietnamese` rows and their layout; these cannot be decided solely from the proverb's language. |
| Turkey p. 1 | Haiku leaves ethnicity null despite `Turkish-American`, and explains the ambiguity in comments; other models populate ethnicity. | Decide whether the header supports a potential ethnicity answer under your best-attempt rule. |
| Taiwan, Thailand, Vietnam | Haiku leaves collection location entirely null; the other models use San Jose, Bellflower, and San Diego respectively. | Inspect the location/date blocks. Taiwan's uncertainty is explicitly noted by the other models; a residence alone does not prove a collection event location. |

**Do not automatically mark a null as wrong:** an accepted archive-field interpretation is still needed for these header rows. Conversely, a cautious null is not automatically better when you prefer plausible candidates plus doubts.

### 6. Transmission mode varies; define an example-based threshold

| Document | Sonnet | Haiku | Gemini medium | Gemini high |
|---|---|---|---|---|
| Vietnam | oral | oral | oral | oral |
| Taiwan | null | null | oral | Oral |
| Thailand | null | oral | null | null |
| Turkey | null | oral | null | null |
| Anglo | null | null | null | null |

Vietnam describes a spoken performance clearly. Taiwan includes “heard this story” and a question/reply exchange; Gemini high cites those clues in a comment. Thailand and Turkey describe learning/hearing a saying. These are source clues, so the non-null values should not be labeled unsupported merely because there is no literal `oral` label. A worked example should distinguish sufficient evidence from an assumption. `oral` versus `Oral` is a vocabulary normalization issue; the schema permits both.

## What appears stable

- All 20 raw responses re-parse and match the saved archive objects; all pass the current schema and filename/ID/storage checks. No truncations or transport failures are recorded.
- All eight Taiwan/Vietnam age outputs use the schema's literal `45-4`, consistently with the intended 45–54 interpretation. This spelling originates in the schema, not model invention.
- The main Vietnam narrative and Taiwan tale agree across models apart from whitespace. Turkey's proverb and its two translation lines, and Anglo's proverb/phonetic rendering and translation lines, also agree across all four after whitespace normalization.
- All collection dates preserve the source strings. All 20 `place_mentioned` arrays are empty, consistent with keeping biography/collection-place mentions out of the folklore fields in these cases.
- The bibliography and feminist commentary in Vietnam are in the input. Their appearance in outputs is not evidence of external research or hallucination.

## Runtime and corrections to previous reporting

| Model | Valid outputs | Total request latency | Median request latency | Full-text outputs retaining an address |
|---|---:|---:|---:|---:|
| Sonnet | 5/5 | 105.5 s | 17.8 s | 5/5 |
| Haiku | 5/5 | 211.4 s | 24.7 s | 3/5 |
| Gemini medium | 5/5 | 262.9 s | 59.0 s | 4/5 |
| Gemini high | 5/5 | 928.4 s | 192.8 s | 4/5 |

**Correction:** every saved v3 record has `attempts: 1`. Earlier status messages and notes incorrectly described Gemini timeouts/retries; `attempt 1/5 starting` was the start of another request, not evidence of a retry. Total recorded request latency is 1,508.148 seconds, approximately 25.1 minutes. Gemini high's total was about 3.53 times medium's in this small run. That does not establish an accuracy benefit or deficit.

**Configuration caveat:** the run records say configured temperature 0, but the saved direct-provider requests omit `temperature`, and the Gemini adapter's `generationConfig` also omits it. Thus this run did not explicitly enforce temperature 0. The 65,536-token ceiling and the transport settings were recorded uniformly. For a controlled follow-up, record settings actually sent to the provider, not just local defaults.

The old v2 validity tally and this v3 tally use different run conditions and development exposure; they are not a controlled estimate of prompt improvement. There is no defensible overall accuracy winner yet. Sonnet was fastest here, but it still changed OCR and misplaced a gloss; Gemini high supplied useful header interpretations but also added an unverified Thai reconstruction.

## Suggested review order

1. **Thailand p. 1:** approve one full example covering identity roles, uncertain OCR heading, gloss placement, and meaning versus context.
2. **Taiwan pp. 1–2, then Vietnam pp. 1–2:** mark the document body and demonstrate footer removal across page breaks. Compare the four full-text outputs.
3. **Vietnam pp. 4–5:** keep speaker attribution attached to interpretation; distinguish source comments from model uncertainty notes.
4. **Vietnam/Anglo p. 1 and Taiwan/Thailand headers:** adjudicate language rows, tentative person information, and collection versus residence locations.
5. **Turkey p. 1:** use as a simpler example of preserved OCR (`Erench`), explicit collection location, original/gloss/translation separation, and collector versus contributor commentary.

For each reviewed example, record the accepted field value or acceptable alternatives and a short reason. These are development examples; reserve unseen documents for the eventual few-shot evaluation. The supplied region annotations remain a separate benchmark contract and have not been converted into archive accuracy scores here.

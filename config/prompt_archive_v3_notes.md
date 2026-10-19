# Clarified archive prompt: discussion draft

Status: clarified zero-shot candidate, 2026-10-19. The runner selects v2 by default; v3 is selectable with `--prompt-version archive_v3` and has a separate lock at `config/prompt_archive_v3.lock.json`. The v2 baseline lock, schema, and previous results are unchanged. The candidate has explicit rules but no worked input/output examples.

## Rule decisions incorporated in the draft

| Decision | Draft treatment | Why it matters |
|---|---|---|
| Output contract | Keep the existing archive schema. | User confirmed. |
| Suspect OCR | Preserve supplied characters; whitespace may be made readable. | User confirmed. |
| Primary folklore text | Include original wording, romanization, and phonetic rendering in item. | Makes completeness requirements explicit. |
| Translations | Separate source-provided translations/glosses; never generate them. | Avoids omission, duplication, or invented translations. Embedded narrative glosses may remain in the item. |
| Contributor and collector | Make a best reasonable attribution; record uncertainty in existing comment fields. | User confirmed best-effort answers with doubts noted. |
| Collector commentary | Keep both existing comment fields and use them for suspect things and doubts. | User confirmed; specific distribution can follow model judgment. |
| Interpretation | Extract source-stated interpretations, with collector evaluations handled separately. | Removes the invitation to create analysis while supposedly using source evidence only. |
| Places | `place_mentioned` includes places in item/translation only; collection location remains separate. | User confirmed. |
| Dates and collection location | Preserve source wording. | User confirmed. |
| Full text | Include only the relevant body of the folklore document; preserve its supplied OCR. | User confirmed. |
| Empty values | Follow the existing schema's type and nullability requirements. | User confirmed. |

The user also directed that `45-4` most likely means ages 45–54, while retaining the schema. The prompt therefore uses literal schema value `45-4` for ages 45–54. Multiple items/people are left to model discretion within the existing schema. Mentioned places are restricted to item/translation. Collection date and location wording is preserved. `folklore.medium` remains null without evidence of transmission mode.

These decisions define prompt behavior but do not adjudicate every reference annotation. The draft uses no document-specific names, expected answers, or annotation counts, and includes no source/reference excerpts as examples. Its rules were informed by the five inspected documents: treat those as development cases when comparing this revision, and reserve unseen documents for final evaluation.

## Archive owner decisions (2026-10-18)

The user supplied these decisions for the discussion draft:

1. **Age bucket `45-4`:** The user confirmed this is probably a schema typo for ages 45–54. Keep the current schema; when a source age falls in 45–54, emit the schema's literal enum value `45-4`. Do not change the schema in this prompt revision. The enum spelling remains a known defect.
2. **Schema scope:** Keep the current schema. No fields are added in this revision.
3. **Multiple items or people:** Use the model's discretion to make a reasonable representation within the existing one-record schema.
4. **Item/translation boundary:** The boundary is not fully specified by this decision; it is evidence that few-shot examples are needed. Keep it marked for the zero-shot/few-shot comparison and settle the operational cases with development examples before evaluation.
5. **OCR:** Preserve suspect OCR as supplied; do not silently correct it.
6. **Contributor/collector attribution:** Make the best attempt based on the source's description. When a reasonable attribution is uncertain, return the potential answer and record the uncertainty/doubt in an existing comments field rather than omitting it automatically.
7. **Comments:** Keep both collector-comment fields. Use them to record suspect attributions, uncertainty, and doubts, without adding schema fields.
8. **Places mentioned:** Limit `folklore.place_mentioned` to places in the folklore and its translation.
9. **Collection date/location:** Preserve source wording as written.
10. **Full text:** Include only the relevant body of the folklore document, not every header, footer, or other page element. Preserve source wording/OCR within that body.
11. **Empty values and transmission medium:** Follow the schema's requirements for nulls, arrays, and strings. Do not populate `folklore.medium` without evidence of transmission mode.

## Remaining operational issue

Few-shot examples are still needed to make the item/translation distinction consistent, especially for romanization, phonetic rendering, and embedded versus separately presented glosses. Examples should come from development material and must not include an evaluated document's reference answer. The zero-shot v3 task has now been run and reviewed qualitatively; adjudicated accuracy evaluation remains pending. See [the findings and review checklist](../reviews/archive_v3_findings.md).

## Initial zero-shot run (2026-10-19)

- The archive v3 draft was frozen under its own lock. The existing archive v2 lock was not changed.
- Ran all five manifest documents against all four configured model aliases (20 requests) in the development phase. Maximum tokens was 65,536. Temperature 0 was configured locally, but the direct-provider requests did not send temperature; it was not explicitly enforced. Temporary transport overrides were five maximum attempts, 10-second initial backoff, and 300-second request timeout.
- All 20 requests completed, parsed as JSON, and passed the existing archive schema; none were truncated. This checks output format only, not extraction accuracy or adherence to the clarified rules.
- Total recorded latency across requests was 1,508.148 seconds (25.1 minutes). Every saved v3 record reports one attempt. Earlier commentary and the original version of these notes incorrectly claimed Gemini timeouts/retries; high-thinking Gemini calls were slower, but no retries are recorded for this run.
- Outputs are under `outputs/runs/archive/development/<model>/<document>/<request-hash>/`. Each run records its prompt hash, settings, usage, latency, attempts, and validation status. The subsequent qualitative review found retained address blocks in 16/20 full-text outputs, specific OCR rewrites, and attribution/field-placement disagreements. Evidence dossiers are under `outputs/reviews/archive_v3/`; no benchmark accuracy score has been computed.

## How to evaluate after the rules are settled

1. Write expected archive-field outputs or adjudicated field checks for development documents under these exact rules. Region annotations remain useful evidence, but are not automatically interchangeable with archive fields.
2. The draft is selectable with `--prompt-version archive_v3`; its separate lock preserves the frozen v2 baseline. Use that version when evaluating these saved outputs.
3. Compare baseline and clarified zero-shot with recorded, consistent model/input/generation settings and the same archive-field rubric. This establishes the effect of the combined prompt clarifications, not of each rule independently.
4. For the zero-shot versus few-shot comparison, use the same clarified instructions, schema, and settings, adding only worked examples from the development set. Never include an evaluated document's reference answer as its example.
5. Report field omissions, unsupported values, incorrect placement, transcription coverage, and operational failures separately. The new prompt is longer and still asks for full-text transcription; measure token use and truncation rather than assuming improvement.

Few-shot examples demonstrate how to apply the rules. They are not model fine-tuning, and a blank JSON structure alone is not a few-shot example.

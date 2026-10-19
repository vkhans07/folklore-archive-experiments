# Region v3: archive clarifications adapted to labeled boxes

The zero-shot candidate is `config/prompt_regions_v3.txt`, selected explicitly as `regions_v3`. It retains the existing region schema and all 20 benchmark labels. Its separate frozen lock is `config/prompt_regions_v3.lock.json`; the original region and archive locks are preserved. This implements the user's request to carry archive v3 clarifications into region prediction/evaluation. It does not generate new model results by itself.

## How the eleven decisions carry over

| Decision | Region v3 treatment |
|---|---|
| Age typo / ages 45–54 | Regions copy literal source ages into `informant_age` or `collector_age`. There is no bucket enum, so the archive `45-4` spelling is irrelevant to region text. |
| Keep schema | Keep `annotations` with `page_num`, `label`, `text`, `bbox`; no extra fields. |
| Multiple items/people | Use model judgment, with separate source regions as appropriate; never merge unrelated people or distant passages into a single region. |
| Item versus translation | Carry the draft's original/phonetic versus supplied-translation/gloss distinction. The embedded-gloss exception remains. No worked examples have been added; their need is documented. |
| Preserve OCR | Preserve characters, wording, case, punctuation, and suspect OCR. Only whitespace may change. |
| Best-attempt attribution | Allow reasonable source-supported candidates from descriptions, signatures, and context without requiring explicit role labels. Omit only when there is no reasonable candidate. |
| Doubts in existing comments | The region schema has no generated-comments field. `collector_annotation` labels actual source commentary; it must not contain invented doubt text. The best-attempt behavior transfers, but generated uncertainty notes cannot be carried over without a separate schema change. |
| Places limited to item/translation | Do not label biographical places as folklore-item text. Preserve existing meanings of `folklore_origin`, `informant_region`, and the two address labels; they are not aliases for archive `place_mentioned`. |
| Dates as written | Copy collection-date text without normalization; distinguish learning dates and story/holiday dates. |
| Relevant body only | Keep unrelated furniture out of `folklore_item`. Continue annotating legitimate header/footer name, age, address, genre, and language regions because these are benchmark categories. No `cleaned_full_text` is produced. |
| Schema requirements / transmission evidence | Unsupported annotations are omitted, empty result is `annotations: []`. There is no transmission-medium label, so do not invent one. |

## Coordinates and source attribution

Boxes use normalized top-left-origin coordinates `[x0, y0, x1, y1]` and zero-based page numbers. Text must correspond to source words inside that page's region. Split across page boundaries and physically separate blocks. Copy source interpretations while retaining speaker attribution; do not generate interpretations, translations, or OCR repairs.

## Commands and selection

```bash
.venv/bin/python -m folklore_eval predict --phase evaluation --target regions --prompt-version regions_v3
.venv/bin/python -m folklore_eval evaluate --phase evaluation --target regions --prompt-version regions_v3
.venv/bin/python -m folklore_eval report --phase evaluation --target regions --prompt-version regions_v3
```

The lock is already frozen. Any future edit to this candidate needs an explicit new freeze before evaluation-phase inference. `--target regions` without a version continues to select the original `regions_v1`; incompatible archive/region version combinations now fail instead of silently selecting another prompt.

Predictions are saved separately under `outputs/runs/regions_v3/<phase>/<model>/<document>/<hash>/predictions.json`, with the version recorded in `run.json`. Evaluation selects matching prompt, schema, and label hashes before choosing a run. V3 metrics and overlays are written under `outputs/evaluation/<phase>/regions_v3/`; aggregation uses that same folder and rejects a different prompt hash. This prevents an unrelated newer v1 run from becoming the v3 result. Explicit archive-version evaluation/reporting is also supported with separate versioned result folders.

## Verification

The 20 local request previews in `outputs/reviews/regions_v3_dry_run.json` were checked against the new lock, the region JSON/box contract, and supplied word coordinates. They contain prepared document data rather than benchmark annotations. A mocked provider-to-prediction-to-evaluation/report test checks that v3 is selected even when a v1 run has a newer timestamp, and that overlays receive the predicted boxes. Additional checks reject incompatible versions, changed frozen prompts, and mixed-prompt reports. Existing box/text metric tests are also run. Those implementation checks preceded live inference. The subsequent inference inventory and connectivity issues are documented in [`outputs/runs/regions_v3/evaluation/RUN_STATUS.md`](../outputs/runs/regions_v3/evaluation/RUN_STATUS.md); benchmark evaluation remains pending.

The existing five documents are development material; the runner's `evaluation` phase name does not make them an unseen test set. A prompt/label definition is still a candidate interpretation of the benchmark until adjudicated against the source annotations.

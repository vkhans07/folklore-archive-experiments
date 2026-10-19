# Folklore evaluation: conversation record and challenges

Updated: 2026-10-18 (America/Los_Angeles).

This records the substantive conversation available in this session: user requests, work performed, reported results, mistakes, corrections, recommendations, and outstanding work. It is a chronological account rather than a verbatim transcript of every assistant message or tool output. The earliest work is available through conversation summaries and repository artifacts; unavailable wording is not reconstructed as a quotation. No API keys or workspace identifier values are included.

## Current state after the October 18 continuation

- The user asked to carry v3 clarifications into region evaluation. Added `config/prompt_regions_v3.txt` and a separate frozen lock, preserving the existing region schema, all 20 labels, and baseline locks. CLI version selection now covers freeze/predict/evaluate/report and rejects target/version mismatches. Region evaluation filters prompt/schema/label hashes and v3 reports/overlays use a separate folder. `config/prompt_regions_v3_notes.md` documents the adaptation: exact ages instead of archive buckets, supported header/address regions retained, best-attempt attribution, source OCR preservation, item/gloss and interpretation boundaries. Generated uncertainty comments cannot be represented in the existing region contract and are not fabricated as collector annotations. Twenty request previews were prepared locally and checked; mocked workflow tests cover version selection, score/overlay routing, and freeze/report guards. A later live inference pass populated the separate `outputs/runs/regions_v3/evaluation/` tree. It produced 16 schema-compliant responses, two saved transport errors, and two interrupted/skipped Anglo requests after repeated connectivity failures. The region evaluator and aggregate report have now run; they include all 20 expected document/model pairs so missing outputs are visible rather than counted as full coverage. See [`outputs/runs/regions_v3/evaluation/RUN_STATUS.md`](outputs/runs/regions_v3/evaluation/RUN_STATUS.md) for run status and the descriptive metrics; the coverage gaps and 13 OCR mismatch review flags require human consideration.
- The user pointed out that the supplied results already include bounding boxes and asked to preserve the current outputs before explaining the change needed. All 20 archive v3 objects were exported with run metadata, prompt/schema/lock, and findings to the root-level `SAVED_RESULTS_ARCHIVE_V3_NO_BOUNDING_BOXES_ALL_20_OUTPUTS_2026-10-19.json`, with object equality checked against their originals. `reviews/bounding_box_next_steps.md` explains that the existing `--target regions` path produces predicted page/label/text/box annotations, uses the prepared word coordinates, and already has evaluation/overlay support. Its frozen fingerprints still match. That path uses the older region prompt, so carrying v3 clarifications requires a separately versioned region candidate; a combined archive-plus-regions JSON would require a schema/prompt/validator change. No new provider calls were made. Running archive extraction had not fulfilled the original region-benchmark objective.
- The user requested review and compiled findings for the 20 v3 outputs. `reviews/archive_v3_findings.md` documents a source-text review of all runs, with five complete source/output dossiers and machine-readable evidence under `outputs/reviews/archive_v3/`, reproducible with `scripts/review_archive_v3.py`. All 20 provider texts re-parse, match their archive objects, and pass the schema and recorded input/prompt/schema hash checks. Findings include retained street-address blocks in 16/20 full-text outputs, definite OCR rewrites (including Sonnet/Thailand ethnicity and Haiku/Vietnam's added word), and disagreements in Thai gloss/role assignment, Vietnamese interpretation attribution, header-derived fields, and transmission medium. The report lists prioritized passages for owner adjudication. Review used supplied OCR, not scanned page pixels; no archive accuracy ranking or region benchmark score was computed.
- Correction to v3 execution reporting: all 20 saved records have `attempts: 1`; earlier claims of v3 Gemini timeouts/retries were incorrect. Total recorded request latency is 1,508.148 seconds. Temperature 0 was a local configuration value but was omitted from the direct-provider requests, so it was not explicitly enforced. These corrections are reflected in the v3 notes and review report.
- After the user authorized running the clarified task, `archive_v3` was made selectable with `--prompt-version archive_v3` and frozen to a separate `config/prompt_archive_v3.lock.json`; the v2 baseline lock was left unchanged. The development run covered all five documents and four configured models (20 requests). All 20 completed, parsed as JSON, passed the archive schema, and were not truncated. Generation used max tokens 65,536, with temporary transport overrides of five maximum attempts, 10-second initial backoff, and 300-second timeout; the actual attempt and temperature details are corrected above. Total recorded latency was about 1,508 seconds (25.1 minutes). Outputs are saved under `outputs/runs/archive/development/`. Qualitative review is now recorded above; adjudicated accuracy evaluation remains outstanding.
- The user clarified the archive prompt's rules. Decisions are recorded in `config/prompt_archive_v3_notes.md` and incorporated in `config/prompt_archive_v3_draft.txt`: keep the schema; interpret its `45-4` option as 45–54 but emit the unchanged literal enum; use model discretion for multiple items/people; preserve suspect OCR; make best-effort uncertain role assignments and note doubts in existing comment fields; restrict mentioned places to item/translation; preserve collection date/location wording; transcribe only the relevant body; follow schema empty-value requirements; and leave medium null without transmission evidence. The item/translation boundary remains a reason to develop few-shot examples. The active v2 prompt/schema remain unchanged; v3 is selectable and has its own frozen lock. No few-shot examples have been added.
- The user authorized retrying the two remaining quota-failed pairs while comparing well-formed existing outputs with annotations, and explicitly requested smaller Luna agents with the parent orchestrating. Three Luna agents handled the scoped retries, annotation compatibility/text-presence diagnostic, and qualitative output review.
- Both archive retries recovered: Gemini medium / Anglo Folkspeech returned schema-valid output in 24.303 seconds on one attempt; Gemini high / Thailand returned schema-valid output in 478.755 seconds across two attempts. Thailand's first attempt timed out at the configured 300-second request timeout, then the adapter waited 10 seconds before retrying. The saved total latency includes the failed attempt and backoff; it is not the successful generation time alone.
- The initial sandbox invocation encountered local DNS/network errors and was interrupted; network-enabled commands then ran with approval. The interruption is recorded separately from provider results, without credentials.
- The two selected requests used temporary overrides of 65,536 maximum tokens, five attempts, 10-second initial backoff, and 300-second timeout. Source code and global settings were unchanged. All other 18 selected run paths were independently verified unchanged.
- Latest archive schema validity is **16/20**: Sonnet 5/5, Haiku 4/5, Gemini medium 5/5, Gemini high 2/5. All 20 selected requests have completed responses. Four earlier truncated outputs remain: Haiku / Vietnam and Gemini high / Vietnam, Taiwan, and Anglo Folkspeech. No reruns of those four were made.
- Archive aggregate reports and output-validity graphs were refreshed. Scoped retry evidence is under `outputs/evaluation/archive/retry-20261018/`, including `summary.json` and independent `orchestrator_validation.json`.
- The compatibility audit confirmed 102 active reference annotations across five documents and zero compatible region prediction artifacts. Existing archive outputs lack predicted page-local labels and boxes. **No full region benchmark, precision/recall/F1, or extraction accuracy ranking was computed.** The user was asked whether to authorize fresh region-target inference; no such inference was launched during this continuation.
- A fixed pre-retry diagnostic compared the 14 existing schema-valid outputs with reference text: 276 nonempty reference/run comparisons, with exact NFC/whitespace-normalized substring presence in structured string leaves for 143 comparisons and in `cleaned_full_text` for 217. These counts ignore labels, boxes, semantic roles, and duplication; they are not accuracy or recall. Different models cover different document subsets. The parent checked reference text against the canonical loader and corrected an initial prose arithmetic error (211 was corrected to 217).
- All 14 pre-retry valid outputs and both recovered outputs were independently revalidated against the archive schema; saved parsed objects matched their raw responses. Qualitative review of the 14 prior outputs and a supplementary recovered-Anglo review used OCR/PDF text layers, not scanned page pixels. Findings include item/translation boundary differences, contributor/collector attribution ambiguity, potential collection-location omissions, and suspect source OCR such as Turkey's `Erench`. These require source evidence and adjudicated field rules, not automatic assignment of model errors.
- Review artifacts and the reproducible text-presence script are under `outputs/evaluation/archive/review-20261018/`. The archive-to-region mapping remains unresolved. The user later clarified that the schema's literal `45-4` age bucket most likely means 45–54; the schema remains unchanged. The aggregate still mixes generation ceilings and transport conditions and is not a controlled model ranking.

## Historical state after the October 16 selected retry

- The user authorized retrying only Gemini medium on Taiwan and Anglo Folkspeech, and Gemini high on Thailand. No other document/model pair was sent to a provider.
- Taiwan recovered: valid JSON/schema, 49.743 seconds on one fresh attempt, 3,442 thinking tokens and 1,411 answer tokens. An earlier Taiwan process had to be interrupted during a long quota-related sleep; its time is separate from that successful call.
- Anglo Folkspeech and Thailand returned HTTP 429 for the Gemini free-tier daily limit of 20 requests per project/model. Provider-directed waits were 18,470 and 18,457 seconds (about 5 hours 8 minutes when received).
- Latest archive validity is **14/20**, up from 13/20: Sonnet 5/5, Haiku 4/5, Gemini medium 4/5, Gemini high 1/5. The other 17 selected run records are unchanged.
- The effective environment already supplied **65,536** tokens at the start of this retry. The three selected requests used that setting; earlier requests used 16,384. No global environment/config file was changed in this retry.
- The selected calls used temporary overrides for five attempts, 10-second initial exponential backoff, and a 300-second request timeout. Global transport defaults remain unchanged.
- The Gemini adapter now prints attempt/retry status and defers provider-directed retry waits above 300 seconds, preserving the error instead of sleeping for hours or retrying early. Random jitter and general HTTP Retry-After header handling are still not implemented.
- Two focused mocked tests passed: long provider waits are deferred without sleeping/retrying early, and five successive 503s use the 10/20/40/80-second schedule.
- Region benchmark scores are still **not computed**. This was the explicitly limited archive retry, not a new benchmark run. The latest aggregate mixes token/transport settings and must not be treated as a controlled model ranking.
- Before/after results, scope, interruption metadata, and comparison are saved under `outputs/evaluation/archive/scoped-retry-20261016T075710Z/`.

## State when this record was first written

- The user wants to compare folklore extraction against their own annotated benchmarks, with useful graphs.
- Direct Google Gemini and Anthropic APIs are configured. Anthropic access worked after the user supplied a workspace ID.
- The completed model runs used the **archive** target, which checks request completion, JSON parsing, and archive schema validity.
- **No model scores against the user's labeled-region benchmarks have been computed.** No region evaluation predictions are saved, and the region aggregate is empty.
- The user's benchmarks already exist: 102 active annotations across the five selected documents. Asking the user to create a new reference set was misleading for the region benchmark they supplied.
- The latest archive results are Sonnet 5/5 valid, Haiku 4/5 valid, Gemini medium 3/5 valid, Gemini high 1/5 valid. These are output-validity counts, not extraction accuracy scores.
- The generation limit used was 16,384 tokens. Larger limits of 32,768 and then 65,536 were discussed but have **not** been applied.
- Retry settings remain three attempts, one-second initial backoff, and a 120-second per-request timeout. Longer backoff and jitter were proposed but have **not** been implemented.
- Creation of the initial conversation record made no provider calls and changed no runtime settings.

## Chronological conversation account

### 1. Resuming the project and choosing providers

The user asked, "where did we leave off", then asked about trying Gemini 3.8 Flash, why the quota default was zero, and whether Anthropic APIs could be used directly.

The user then requested replacing `.env.example` with configuration for Google Gemini models, including a higher-thinking comparison, and direct Anthropic Sonnet and Haiku.

The resulting model configuration uses:

| Alias | Provider | Model ID | Reasoning setting in our configuration |
|---|---|---|---|
| `sonnet` | Direct Anthropic API | `claude-sonnet-5-5` | No explicit thinking/effort override |
| `haiku` | Direct Anthropic API | `claude-haiku-5-5` | No explicit thinking/effort override |
| `gemini_flash` | Google Gemini Developer API | `gemini-3.8-flash` | `medium` |
| `gemini_flash_high` | Google Gemini Developer API | `gemini-3.8-flash` | `high` |

The user's initial idea included extended versus non-extended thinking. The actual Gemini comparison is **medium versus high thinking**, not thinking enabled versus disabled. Anthropic's lack of an explicit thinking parameter does not imply thinking is off; the later Haiku response confirms thinking occurred.

Earlier session work updated `.env.example`, `config/models.json`, provider routing, environment loading, and README instructions. The provider adapter gained direct Gemini REST support, Anthropic workspace-header support, and handling for Google's camelCase usage/finish fields. Resume handling was extended to consider saved retry folders.

The original zero-quota question did not establish one universal cause for every zero shown in a console. Later saved Gemini errors specifically identified free-tier quota limits. Direct API access also has separate account configuration, billing, and limits from cloud-hosted provider access.

### 2. Keys supplied; first evaluation requested

The user said the API keys were in and asked to run the evaluation and present the results as visually as possible.

The first reported archive evaluation attempted five documents on four model aliases:

| Model | Requests completed | JSON/schema valid | Blocker |
|---|---:|---:|---|
| Gemini medium | 4/5 | 4/5 | Thailand request hit quota |
| Gemini high | 0/5 | 0/5 | Gemini quota errors |
| Haiku | 0/5 | 0/5 | Missing Anthropic workspace header |
| Sonnet | 0/5 | 0/5 | Missing Anthropic workspace header |

The four successful Gemini medium responses used 230,668 input tokens and 7,489 reported answer tokens. Their recorded latencies were 52.967 seconds for Vietnam, 23.794 for Taiwan, 27.475 for Turkey, and 76.516 for Anglo Folkspeech.

Google errors included free-tier limits for requests and input tokens: 5 requests/minute, 250,000 input tokens/minute, and a 20-request daily limit were encountered in the earlier work. These are observations from those errors, not a claim about all accounts or current paid-tier limits. The earlier explanation referenced billing and the daily quota reset; neither should be assumed to resolve a later 503 overload error.

Anthropic returned HTTP 400 stating the API key was not scoped to a workspace and required `anthropic-workspace-id`. An attempted workspace listing returned 403. The earlier browser attempt had no available browser backend. The user needed to obtain a workspace ID through the Console or use appropriately scoped credentials.

### 3. Rundown and reusable graphs

The user asked, "give me a rundown, what efficacies are we looking at? potentially build out files to produce relevant graphs".

The assistant read the saved aggregate and per-document results and created `scripts/plot_evaluation.py`. It generates dependency-free SVG charts and Markdown notes in `outputs/evaluation/archive/evaluation/graphs/`:

- `request-validity.svg`: request completion, JSON parsing, and schema-valid output counts.
- `gemini-flash-latency.svg`: observed latency for completed Gemini medium requests, with token counts.
- `README.md`: table, interpretation, and chart links.

The script was run successfully. A first draft incorrectly labeled the partially successful Gemini medium row as having no successful response; that label was corrected. Later, after the rerun, several hardcoded explanations about quota/workspace failures were replaced with descriptions derived from the current report. The charts still describe archive output validity and latency; they do not visualize benchmark accuracy.

The assistant reported 80% end-to-end valid output for Gemini medium and 100% schema validity among its four completed responses. Those denominators were correct for that run, but they were not scores against the user's annotations. Generated outputs are Git-ignored; the reusable script is a project file. `git diff --check` was run, but it is not visual inspection or a benchmark correctness test, and untracked files are not covered by a normal Git diff.

### 4. User challenged delayed diagnosis

The user said the assistant spent about 20 minutes without noticing or raising that Anthropic setup was insufficient.

The assistant accepted that it should have surfaced the immediate workspace-header errors before continuing a full evaluation or presenting model comparisons. At that point Anthropic had produced no model outputs to evaluate. Repeating requests across every document did not help diagnose the shared configuration error.

Lesson: verify one real request per provider early, distinguish HTTP completion from output validity, and surface authentication/configuration failures as soon as they appear.

### 5. Workspace ID instructions

The user asked, "how do i set up a workspace id".

The assistant verified the current provider documentation and explained that workspace IDs are assigned by Anthropic. They can be copied from the ID column at Claude Console → Settings → Workspaces, including the Default workspace. IDs begin with `wrkspc_`.

The project reads `ANTHROPIC_WORKSPACE_ID` from `.env` and sends it in the `anthropic-workspace-id` request header. A key scoped to a single workspace can omit that header; the user's observed error specifically required it. Account access may require an organization administrator.

### 6. User supplied the ID and said "now run"

The assistant checked only whether the value was set and had the expected prefix; it did not print the identifier or key. It then ran `predict --phase evaluation`, which defaults to the archive target.

The initial attempt ran inside the network-restricted sandbox and failed with connection/DNS errors. Those failures did not validate the workspace setup. The command was rerun with the required network permission. The user had already authorized the evaluation; the permission step was an environment restriction, not a new product decision.

The network-enabled run completed across all 20 document/model pairs. Anthropic succeeded in returning responses for all five documents on each model. Gemini returned some HTTP 503 high-demand errors. The runner emitted its full outcome list at the end, so progress was monitored through saved run files. Future reporting should emit individual completions/errors promptly rather than requiring manual file inspection.

The assistant ran the archive evaluation and aggregate reporting commands and regenerated the graphs.

### 7. Archive results before the selected retry

| Model | Requests completed | Parsed JSON | Schema-valid outputs | Observed failure |
|---|---:|---:|---:|---|
| Sonnet | 5/5 | 5/5 | 5/5 | None in these format checks |
| Haiku | 5/5 | 4/5 | 4/5 | Vietnam exhausted its generation allowance |
| Gemini medium | 3/5 | 3/5 | 3/5 | HTTP 503 on Taiwan and Anglo Folkspeech |
| Gemini high | 4/5 | 1/5 | 1/5 | Truncated Vietnam, Taiwan, Anglo Folkspeech; HTTP 503 on Thailand |

For Gemini medium, all three completed responses passed schema validation; for Gemini high, one of four did. The three successful Gemini medium responses used 183,587 input tokens and 6,016 answer tokens, with observed latencies of 28.122–73.257 seconds.

The prior successful Gemini medium responses remain saved, but the current aggregate selects the latest run file for each model/document. It does not combine all historically successful responses into a cumulative success rate. This explains why the latest medium completion count fell from four to three despite some earlier successful answers being available.

### 8. Interpretation requested

The user asked, "interpret the results".

The assistant described Sonnet as the strongest candidate under the current configuration because it produced valid archive outputs for every document. It distinguished provider availability failures from incomplete answers and suggested reviewing Sonnet's answers against the PDFs.

That interpretation was limited to output formatting and operational behavior. It did not establish Sonnet's extraction accuracy. The advice to create reference answers overlooked that the user's region annotations already existed. A nested archive reference set would be a different evaluation target; it was not a prerequisite to using the supplied region benchmarks.

### 9. User asked for actual benchmark values, budget changes, and overload handling

The user asked, "what were the actual evaluation values based on the benchmarks i produced? and do i need to increase budgets? how do i get around the overload errors considering this isn't a ton of data?"

Inspection confirmed a target mismatch:

- `predict`, `evaluate`, and `report` default to `archive`.
- Archive prediction requests a nested record containing contributor, folklore, collector, analysis, and other fields. It has no annotation labels/page boxes.
- The existing benchmark evaluator expects `annotations` with page number, label, source text, and bounding box, generated using `--target regions`.
- No region evaluation prediction runs exist. Both the region per-document results and aggregate are empty.
- The frozen region prompt still matches its lock. There is no need to invent a mapping or new reference data to run that existing benchmark.

The benchmark counts, checked against the active annotations in the actual export, are:

| Document | Reference annotations | Annotated pages |
|---|---:|---:|
| Vietnam | 31 | 5 |
| Taiwan | 17 | 2 |
| Turkey | 18 | 1 |
| Thailand | 19 | 1 |
| Anglo Folkspeech | 17 | 1 |
| Total | **102** | **10** |

The five JSON export files are byte-identical copies of an export containing multiple documents. They must be deduplicated rather than counted five times. The reference loader already does that and filters to the manifest's documents.

The existing evaluator supports exact-text precision/recall/F1 after Unicode and whitespace normalization; labeled-region precision/recall/F1 with IoU ≥ 0.5 and one-to-one matching; mean overlap for matched boxes; and character edit distance for box-matched text. Case and punctuation remain significant in exact text matching. All model benchmark values are currently **not computed**, not zero.

The correct workflow, documented here but not executed in this conversation, is:

```bash
.venv/bin/python -m folklore_eval predict --phase evaluation --target regions
.venv/bin/python -m folklore_eval evaluate --phase evaluation --target regions
.venv/bin/python -m folklore_eval report --phase evaluation --target regions
```

The first command makes new paid provider requests. Scoring the archive outputs directly against region references would require an explicit mapping, and the existing archive outputs lack the necessary boxes and labels. `config/archive_region_relationship.md` records possible relationships and their ambiguities; no such transformation is implemented.

### 10. Raw usage clarified the token-budget failures

All latest requests used `max_tokens=16384` (sent as `maxOutputTokens` to Gemini).

| Failed response | Thinking tokens in raw usage | Visible answer tokens | Recorded finish reason |
|---|---:|---:|---|
| Haiku, Vietnam | 16,384 | 0 | `max_tokens` |
| Gemini high, Vietnam | 15,727 | 650 | `max_tokens` |
| Gemini high, Taiwan | 15,729 | 648 | `max_tokens` |
| Gemini high, Anglo Folkspeech | 15,728 | 649 | `max_tokens` |

The high-thinking responses used almost all their allowance on reasoning, leaving incomplete JSON. Haiku's Vietnam result contained no answer text. Calling that merely a malformed JSON response misses the budget cause.

The assistant initially recommended trying 32,768 tokens, or reducing thinking effort, and verifying the effect. Sonnet and Gemini medium did not hit the existing generation cap in the latest run. A larger cap does not force a model to consume every token and does not guarantee better extraction.

Gemini's normalized `output_tokens` currently records candidate/answer tokens only. Raw responses preserve `thoughtsTokenCount`, but the summary omits it. Anthropic usage includes thinking within output usage. Consequently the current cross-provider output-token columns are not equivalent measures of total generation or cost. Future reports should expose reasoning and answer usage separately where available.

The prepared payload contains verbose word-level JSON with coordinates and metadata. Vietnam alone counted as 143,259 Gemini input tokens, despite being five pages. Reducing repeated JSON keys/whitespace while preserving geometry was proposed. That optimization has not been implemented or evaluated; it should be recorded as a new input condition if adopted.

### 11. Infinite-token question

The user asked, "why not do like infinite tokens allowed, just let the llms think?"

The assistant explained that effective generation allowances are finite and provider/model limits still apply. An API may allow omission of an explicit token-limit parameter, but that uses a finite default; it does not enable infinite generation.

The assistant then proposed **65,536 tokens** for the next benchmark, with a suitable timeout and separate tracking of reasoning tokens, answer tokens, latency, and accuracy. This superseded the earlier 32,768 starting suggestion in the discussion; neither recommendation changed the repository or `.env` settings. The user has not yet observed results with either larger limit. Increasing token capacity addresses truncation, not HTTP 503 overload.

### 12. Longer-retry question and request for this file

The user asked how longer retries work, what needs to be retried, and to note every part of the conversation in `challenges.md`.

The unit of retry is **one document × one model × one prompt/settings combination**. After a transient request failure, the runner waits and resends the complete request: system prompt, prepared document input, model ID, and generation settings. It starts a fresh generation. It does not continue a hidden reasoning process, resume a partially generated JSON string, rerun local scoring, or require redoing every document.

Current behavior is up to three total attempts, with fallback waits of 1 and 2 seconds. Google's saved 503 failures each exhausted those attempts in roughly five seconds. The proposed schedule is:

```text
Attempt 1 → transient failure → wait about 10 seconds
Attempt 2 → transient failure → wait about 20 seconds
Attempt 3 → transient failure → wait about 40 seconds
Attempt 4 → transient failure → wait about 80 seconds
Attempt 5 → if still failing, record failure and continue
```

That is five attempts and four waits: 150 seconds of base waiting, plus request durations and any jitter/provider-directed delay. Jitter means a small random variation so clients do not all retry at the same instant. A transient overload might clear during that interval; there is no guarantee. Longer backoff is different from increasing the time allowed for one successful generation to finish.

The existing Gemini adapter already honors certain retry hints in the JSON error body. It does not implement random jitter or general HTTP `Retry-After` header handling. Those were discussed improvements, not existing behavior.

The pending archive requests have different recovery needs:

| Problem | Affected document/model pairs | Appropriate action |
|---|---|---|
| Final HTTP 503 | Gemini medium: Taiwan and Anglo Folkspeech; Gemini high: Thailand | Resend these three requests with longer bounded backoff |
| Generation cap reached | Haiku: Vietnam; Gemini high: Vietnam, Taiwan, Anglo Folkspeech | Rerun these four with a revised generation allowance/effort; waiting alone does not fix truncation |
| Wrong evaluation target | All model comparisons against the user's region benchmarks | Generate region predictions and run the region evaluator; this is new inference, not an overload retry |
| Earlier missing workspace ID | Sonnet and Haiku | Resolved by configuration; repeating the old bad request would not have helped |
| Earlier 429 quota exhaustion | Google requests in the first run | Respect the applicable quota window/reset or account configuration; short repeated retries cannot remove a daily cap |

The three 503 requests already received the configured short retries before being recorded as failed. A later retry would be an additional preserved run attempt. For network timeouts, the server may have continued processing after the client stopped waiting, so resending can duplicate computation; successful responses should be reused when appropriate. A fully processed retry can incur its own token usage.

### 13. User authorized only the selected documents/pairs

The user said, "ok try on those documents and those documents only, after which we'll evaluate the progress made thus far". The assistant stated the scope as the three overload failures listed above. The separate four truncated responses and all region benchmark requests were outside this retry.

The assistant snapshotted the previous aggregate and per-document reports, then inspected effective settings. The environment now supplied 65,536 tokens. It retained that allowance and used temporary five-attempt, 10-second-backoff, 300-second-timeout overrides. No `.env` or global transport setting was edited.

The first Taiwan process produced no live error output. Progress messages initially described a pending request without knowing whether it was generating or waiting. After prolonged waiting, process inspection showed no open TCP connection and a sampled Python wait. The assistant interrupted it; the resulting traceback confirmed HTTP 429 followed by the adapter's retry sleep. The request was preserved, with `interrupted.json` recording 1,658 elapsed seconds (27 minutes 38 seconds at metadata capture), HTTP 429, and the interruption reason. The full error body of that interrupted process had not been persisted.

This exposed a second delay-management mistake: limiting attempt count does not bound elapsed time when `_provider_retry_delay` accepts arbitrarily long provider delays. The assistant should have checked the wait path and ensured live error reporting before allowing another long silent run. That delay was not evidence of the model thinking for 28 minutes. It must not be hidden behind the later successful request's 49.743-second latency.

To complete the scoped task, the assistant added Gemini attempt/retry logging to stderr and a five-minute maximum permitted retry sleep. When the provider asks for more, the adapter returns the original error plus `retry_deferred` and `retry_after_seconds`, allowing the caller to save the result and move on. It does not shorten the provider's requested delay and retry prematurely. The configurable internal transport key is `max_retry_delay_seconds`, defaulting to 300; it is not exposed as an environment setting.

A syntax check using `py_compile` initially could not write to macOS's cache directory within the sandbox. An in-memory AST parse then succeeded without cache writes. Two focused tests in `tests/test_provider_retries.py` passed, using mocked HTTP errors and sleeps so they made no provider calls.

The subsequent selected calls returned:

| Pair | Previous final result | New final result | Attempts in final run | Final run time |
|---|---|---|---:|---:|
| Gemini medium / Taiwan | HTTP 503 | JSON/schema valid, no truncation | 1 | 49.743 seconds |
| Gemini medium / Anglo Folkspeech | HTTP 503 | HTTP 429 daily quota, deferred | 1 | 0.258 seconds |
| Gemini high / Thailand | HTTP 503 | HTTP 429 daily quota, deferred | 1 | 0.323 seconds |

The quota responses specify `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit 20. Both Gemini aliases use `gemini-3.8-flash`, so they are not separate underlying model quota pools. The reported delays of 18,470 and 18,457 seconds are observations from those responses, not a promise of future availability.

Taiwan's fresh successful call used 40,974 input tokens, 3,442 thinking tokens, and 1,411 answer tokens. It used only one attempt and far less than the new 65,536-token ceiling, so this recovery does not establish that either longer exponential backoff or the larger ceiling caused the success.

The archive reports and graphs were refreshed locally. A comparison of every selected run path verified that exactly the three authorized pairs changed; the other 17 remained unchanged. No new region predictions or annotation metrics were generated. The record in `comparison.json` includes settings, paths, attempt counts, raw Taiwan usage, final errors, and before/after validity counts. The interrupted Taiwan request is recorded separately in `scope.json` and its run directory.

## Implementation caveats discovered during this review

1. **Resume skips completed responses even when invalid.** `predict.py` uses `request_completed` for cache reuse. A truncated response will be resumed under the same cache key. A deliberate rerun needs `--no-resume` for the selected document/model or changed generation settings.
2. **Transport settings are part of the cache key.** Changing retry count, backoff, or timeout creates a new key. Running the whole suite after that change can resend successful requests too. To retry only failures with new transport settings, select the failed document/model pairs, or first revise cache/resume behavior while preserving provenance.
3. **Implementation hashes also affect cache reuse.** Editing provider/predict/settings/validation code can invalidate reuse for otherwise identical requests. Claims that a rerun will automatically preserve every successful response must account for this.
4. **Aggregates select the latest run per document/model by file modification time.** They can replace a historical success with a later provider failure and may combine settings if not controlled. For fair comparisons, record which attempts and settings belong to each experiment.
5. **Retries lack full attempt-level artifacts.** A run records its attempt count, final response/error, and combined latency; the adapter does not save each internal failed attempt as a separate run. A top-level rerun creates a separate preserved run directory.
6. **Generation settings are global in the current wrapper.** The existing environment setting `FOLKLORE_MAX_TOKENS` affects all selected aliases. Per-model effort/budget controls would require implementation or separate invocations with documented overrides. There is no existing Anthropic effort environment variable.
7. **No accuracy ranking is established.** Sonnet's 5/5 result supports format reliability for five archive outputs under one configuration. It does not establish that Sonnet extracts the benchmark annotations more accurately than the others.

## Outstanding work and decisions before the selected retry

- Run the actual region benchmark and publish the text and region metrics per document and model, including failed/malformed-output handling.
- Decide and record the next experiment's generation ceiling; 65,536 was the latest proposal, not an applied setting.
- Add bounded backoff with jitter and appropriate provider retry hints, and distinguish daily quota exhaustion from short-lived throttling/overload.
- Preserve successful work when changing transport settings; explicitly select failed pairs until resume semantics support that reliably.
- Expose thinking-token accounting and consistent total-usage measures before cost comparisons.
- Report provider errors and per-document progress immediately, including a real provider smoke check before a long run.
- Consider compacting input JSON while preserving the coordinates needed for region scoring; version and measure that input change.
- Generate accuracy graphs only after actual benchmark scores exist, and label output-validity graphs explicitly.

## Evidence and references

Local project evidence:

- `JSONs/*.json`: supplied annotation exports; byte-identical copies, deduplicated by the evaluator.
- `config/integrity.json`: expected benchmark counts/pages.
- `config/models.json`, `.env.example`, `folklore_eval/settings.py`: model defaults and supported environment settings.
- `config/prompt_archive_v2.txt`, `config/archive.schema.json`: archive target.
- `config/prompt_v1.txt`, `config/annotation.schema.json`, `config/prompt.lock.json`: region target and frozen prompt.
- `config/archive_region_relationship.md`: unresolved archive-to-region mappings.
- `folklore_eval/cli.py`, `predict.py`, `provider.py`, `evaluate.py`, `matching.py`: target selection, cache behavior, retries, and scoring.
- `outputs/evaluation/archive/evaluation/aggregate.json` and `per_document.json`: latest archive results.
- `outputs/evaluation/evaluation/aggregate.json` and `per_document.json`: empty region evaluation results at this writing.
- `outputs/runs/archive/evaluation/`: preserved requests, raw responses, extracted text, predictions where valid, and run metadata.
- `scripts/plot_evaluation.py` and `outputs/evaluation/archive/evaluation/graphs/`: graph generator and latest generated artifacts.

Official documentation consulted during the discussion:

- [Anthropic workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)
- [Anthropic authentication and workspace selection](https://platform.claude.com/docs/en/manage-claude/authentication)
- [Haiku 5.5 migration and thinking/token limits](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide)
- [Anthropic thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)
- [Gemini 3.8 Flash model limits](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
- [Gemini thinking](https://ai.google.dev/gemini-api/docs/generate-content/thinking)
- [Gemini API error definitions](https://ai.google.dev/gemini-api/docs/api-errors)
- [Gemini retry guidance](https://ai.google.dev/gemini-api/docs/troubleshooting)
- [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

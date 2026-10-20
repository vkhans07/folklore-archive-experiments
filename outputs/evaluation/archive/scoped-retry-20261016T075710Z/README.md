# Selected retry results

Only Gemini medium on Taiwan and Anglo Folkspeech, and Gemini high on Thailand were requested. The other 17 selected run records are unchanged.

| Pair | Before | After | Final attempt latency |
|---|---|---|---|
| gemini_flash / 00001_09_Taiwan_holiday_lore__93.pdf | HTTP 503 | Schema valid | 49.743s |
| gemini_flash / 00003_Anglo_Folkspeech_VI_A67_C6__74.pdf | HTTP 503 | HTTP 429; deferred for quota | 0.258s |
| gemini_flash_high / 00002_56_Thailand_Folkspeech__38.pdf | HTTP 503 | HTTP 429; deferred for quota | 0.323s |

Latest archive validity increased from 13/20 to 14/20. Gemini medium improved from 3/5 to 4/5. Sonnet remains 5/5, Haiku 4/5, and Gemini high 1/5.

Google returned a free-tier daily limit of 20 requests per project/model for the two remaining failures, with waits of 18,470 and 18,457 seconds (approximately 5 hours 8 minutes at the time of those errors). Both aliases use the same underlying model.

The current .env supplied a 65,536-token cap; prior results used 16,384. Selected retries used 5 attempts, 10-second initial backoff, and a 300-second timeout. A provider-directed wait above 300 seconds now defers the request rather than blocking the process or retrying early. Jitter was not added.

An earlier Taiwan process was interrupted after 1658 seconds; its traceback confirmed HTTP 429 followed by a retry sleep. Its request and interruption metadata are retained. The fresh successful Taiwan attempt took 49.743 seconds, on one attempt. The successful call alone therefore does not demonstrate that exponential backoff or the higher token ceiling caused the recovery.

These are archive request/schema results. No region benchmark predictions or accuracy metrics were generated. Settings now differ across selected/latest rows, so this aggregate is progress tracking, not a controlled model ranking.

See comparison.json, scope.json, before-* and after-* artifacts for provenance.

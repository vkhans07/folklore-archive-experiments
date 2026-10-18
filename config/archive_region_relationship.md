# Archive document and region annotations

`archive.schema.json` records the user-supplied nested archive structure and is the default prediction target. The archive prompt extracts it directly from the prepared PDF text layer. `annotation.schema.json` remains the separate `--target regions` contract for page-local labeled regions with source text and boxes. Archive outputs are validated for shape; field accuracy cannot be scored without archive references.

The annotation export supplies 20 region labels. Several names suggest archive fields, but the archive structure does not establish how to resolve repeated regions, normalize ages or dates, distinguish contributor from informant, choose between the two `collector_comments` fields, or derive locations. No mapping is implemented. The following are **review candidates only**, not transformation rules:

| Region label(s) | Possible archive destination | Open decision |
|---|---|---|
| `folklore_item`, `folklore_translation` | `folklore.item`, `folklore.translation` | How should repeated items or translations be combined? |
| `informant_name`, `informant_age`, `informant_gender`, `informant_ethnicity`, `informant_languages`, `informant_occupation` | `contributor.*` | Confirm that the source informant is the archive contributor; define age bucketing. |
| `collector_name`, `collector_annotation` | `collector.name`, `collector.collector_comments` or `analysis.collector_comments` | Which collector comments field is intended? |
| `collection_context`, `collection_date` | `analysis.context.collection_context`, `date_collected` | Define any text cleaning or date conversion. |
| `informant_explanation` | `analysis.context.use_context` or `analysis.interpretation` | Distinguish use from interpretation. |

Labels with no direct, unambiguous field in the supplied archive structure include `folklore_genre`, `folklore_language`, `folklore_origin`, `informant_address`, `informant_region`, `collector_address`, and `collector_age`. The archive fields `folklore.medium`, `folklore.place_mentioned`, `collector.gender`, `contributor.nationality`, `storage_medium`, `cleaned_full_text`, and `location_collected` likewise have no automatic region mapping here.

The supplied age-bucket list says `45-4`; that literal value is preserved in the archive schema pending confirmation. The region evaluator does not use age buckets.

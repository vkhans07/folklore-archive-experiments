# Producing bounding-box predictions for the supplied annotations

## Current results saved

All 20 v3 archive outputs, their run metadata, the prompt template/schema/lock, and the review findings are bundled in [`SAVED_RESULTS_ARCHIVE_V3_NO_BOUNDING_BOXES_ALL_20_OUTPUTS_2026-10-19.json`](../SAVED_RESULTS_ARCHIVE_V3_NO_BOUNDING_BOXES_ALL_20_OUTPUTS_2026-10-19.json). The exported archive objects were checked against all 20 original `archive.json` files. This is a snapshot of the archive run, not a region-prediction result.

## Minimum change: select the existing regions task

The supplied benchmark already contains bounding boxes (`region_bbox_norm`), labels, pages, and text. Prepared model inputs already contain normalized word boxes and page geometry. The missing artifact is model-predicted labeled regions.

The runner supports this through `--target regions`. That selects `config/prompt_v1.txt` and the region contract instead of the archive prompt/schema. Predictions contain:

```json
{
  "annotations": [
    {
      "page_num": 0,
      "label": "folklore_item",
      "text": "source passage",
      "bbox": [0.1, 0.2, 0.8, 0.4]
    }
  ]
}
```

The example coordinates are illustrative. The array means left, top, right, bottom as fractions of the page; page numbers start at zero. Each region belongs to one page, so passages spanning pages need separate annotations. `bbox` is the prediction field; the evaluator already reads the supplied reference field `region_bbox_norm` into the same coordinate representation.

No new annotation work, coordinate preparation, or model adapter is needed to run the existing region baseline. The region prompt/schema/label fingerprints were checked against `config/prompt.lock.json` and still match.

The existing commands for that baseline are:

```bash
.venv/bin/python -m folklore_eval predict --phase evaluation --target regions
.venv/bin/python -m folklore_eval evaluate --phase evaluation --target regions
.venv/bin/python -m folklore_eval report --phase evaluation --target regions
```

These commands have not been executed as part of this save/explanation request. Prediction makes new provider calls. The phase name is a runner setting; these five documents have already been inspected during development and should not be described as an unseen test set.

The baseline runner saves `predictions.json` alongside each run under `outputs/runs/evaluation/`; v3 predictions are isolated under `outputs/runs/regions_v3/evaluation/`. The evaluator compares labels/boxes with the supplied annotations (one-to-one matching, IoU at least 0.5), calculates region/text metrics, and renders reference boxes in green and prediction boxes in red. V3 overlays are isolated under `outputs/evaluation/evaluation/regions_v3/`.

## Keeping the recent clarifications

The clarified candidate is now implemented as `regions_v3`, with its own prompt and lock. Use `--target regions --prompt-version regions_v3` for prediction, evaluation, and reporting. The full [mapping of archive decisions to regions](../config/prompt_regions_v3_notes.md) records applicable rules and schema limitations. The unversioned `--target regions` command continues to use the old region baseline; an archive-version flag with the region target now fails explicitly.

Retain the benchmark's label set, including header/address annotations. The archive rule about excluding headers/addresses from `cleaned_full_text` should not suppress regions that the supplied benchmark labels. Archive uncertainty-comment fields also have no direct counterpart in the current region schema.

## If both nested archive fields and squares are wanted together

For the supplied benchmark, a separate region JSON is already sufficient and can be linked to the archive results by document ID and model alias. A single combined JSON would require an explicit schema extension (for example a region array), corresponding prompt instructions, validation updates, and evaluator routing. Appending reference boxes to the old archive outputs would not constitute predicted boxes; locating old extracted strings would be a separate alignment method with ambiguity for repeated or rewritten text.

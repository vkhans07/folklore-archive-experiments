import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from folklore_eval.common import ROOT, file_sha, read_json, write_json
from folklore_eval.predict import prompt_data, prompt_fingerprint, predict
from folklore_eval.references import load_references

prediction = importlib.import_module("folklore_eval.predict")
evaluation = importlib.import_module("folklore_eval.evaluate")
reporting = importlib.import_module("folklore_eval.report")
DOC = {"doc_id": "00002_56_Thailand_Folkspeech__38.pdf", "pdf": "JSONs/Thailand Folkspeech.pdf"}
CONFIG = {"provider": "anthropic_direct", "models": {"test": {"id": "fake-model", "provider": "anthropic_direct"}},
          "generation": {"max_tokens": 4096, "temperature": 0},
          "transport": {"max_attempts": 1, "timeout_seconds": 1, "initial_backoff_seconds": 0}}


class RegionVersionTests(unittest.TestCase):
    def test_target_version_mismatch_is_rejected_and_baselines_match(self):
        for target, version in [("regions", "archive_v3"), ("archive", "regions_v3")]:
            with self.assertRaisesRegex(ValueError, "incompatible"):
                prompt_data(target, version)
        for target, version, filename in [("regions", "regions_v1", "prompt.lock.json"),
                                           ("archive", "archive_v2", "prompt_archive.lock.json"),
                                           ("archive", "archive_v3", "prompt_archive_v3.lock.json")]:
            lock = read_json(ROOT / "config" / filename)
            self.assertTrue(all(lock.get(k) == v for k, v in prompt_fingerprint(target, version).items()))
        prompt, labels = prompt_data("regions", "regions_v3")
        self.assertNotIn("{LABELS}", prompt)
        self.assertEqual(len(labels), 20)
        self.assertNotEqual(prompt, prompt_data("regions", "regions_v1")[0])

    def test_evaluation_selects_v3_even_when_v1_run_is_newer(self):
        prepared = {"doc_id": DOC["doc_id"], "source_pdf": DOC["pdf"],
                    "pdf_sha256": file_sha(ROOT / DOC["pdf"]),
                    "pages": [{"page_num": 0, "words": []}]}
        refs, _, _ = load_references([DOC], {DOC["doc_id"]: prepared})
        annotation = {k: refs[DOC["doc_id"]][0][k] for k in ("page_num", "label", "text", "bbox")}
        raw = {"model": "fake-model", "content": [{"type": "text", "text": json.dumps({"annotations": [annotation]})}],
               "stop_reason": "end_turn", "usage": {"input_tokens": 1, "output_tokens": 1}}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_json(output / "inputs" / (Path(DOC["doc_id"]).stem + ".json"), prepared)
            with patch.object(prediction, "OUTPUT", output), patch.object(prediction, "model_settings", return_value=CONFIG), \
                 patch.object(prediction, "manifest", return_value=[DOC]), \
                 patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-test-key"}), \
                 patch.object(prediction, "request_anthropic_direct", return_value=(raw, 0.1, None, 1)) as provider:
                paths = {}
                for version in ("regions_v1", "regions_v3"):
                    paths[version] = Path(predict(DOC["doc_id"], "test", target="regions", prompt_version=version)[0]["run"])
                self.assertEqual(provider.call_count, 2)
                self.assertEqual(read_json(paths["regions_v3"])["prompt_version"], "regions_v3")
                self.assertEqual(read_json(paths["regions_v3"].parent / "predictions.json")["annotations"], [annotation])
            os.utime(paths["regions_v1"], (2000000000, 2000000000))
            with patch.object(evaluation, "OUTPUT", output), patch.object(evaluation, "render_overlays") as render:
                rows = evaluation.evaluate("development", DOC["doc_id"], "test", "regions_v3")
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["run_path"], str(paths["regions_v3"]))
                self.assertEqual(rows[0]["box_tp"], 1)
                self.assertEqual(render.call_args.args[2], [annotation])
            folder = output / "evaluation/development/regions_v3"
            self.assertTrue((folder / "per_document.json").exists())
            self.assertFalse((output / "evaluation/development/per_document.json").exists())
            with patch.object(reporting, "OUTPUT", output):
                aggregate = reporting.report("development", "regions_v3")
                self.assertEqual(aggregate[0]["box_tp"], 1)
                altered = read_json(folder / "per_document.json")
                altered[0]["prompt_sha256"] = "other-prompt"
                write_json(folder / "per_document.json", altered)
                with self.assertRaisesRegex(ValueError, "different region prompt"):
                    reporting.report("development", "regions_v3")

    def test_changed_v3_prompt_cannot_start_frozen_evaluation(self):
        with patch.object(prediction, "model_settings", return_value=CONFIG), \
             patch.object(prediction, "prompt_fingerprint", return_value={"system_prompt_sha256": "changed"}), \
             patch.object(prediction, "request_anthropic_direct") as provider:
            with self.assertRaisesRegex(ValueError, "changed since freeze"):
                predict(phase="evaluation", target="regions", prompt_version="regions_v3")
            provider.assert_not_called()


if __name__ == "__main__":
    unittest.main()

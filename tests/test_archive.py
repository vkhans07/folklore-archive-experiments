import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from folklore_eval.common import ROOT, file_sha, read_json, write_json
from folklore_eval.predict import predict, prompt_data
from folklore_eval.validation import parse_archive_response


SOURCE = "JSONs/Legend Vietnam 38.pdf"


def archive_record():
    return {"_id": None, "filename": SOURCE, "contributor": {"name": None, "age_bucket": None, "gender": None, "ethnicity": None, "nationality": None, "languages_spoken": [], "occupation": None}, "folklore": {"item": "A tale", "medium": None, "translation": None, "place_mentioned": []}, "collector": {"name": None, "gender": None, "collector_comments": None}, "analysis": {"context": {"use_context": None, "cultural_background": None, "collection_context": None}, "interpretation": None, "collector_comments": None}, "storage_medium": "PDF", "cleaned_full_text": "A tale", "date_collected": None, "location_collected": {"city": None, "state": None, "country": None, "geolocation": None}}


class ArchiveContractTests(unittest.TestCase):
    def setUp(self):
        self.schema = read_json(ROOT / "config/archive.schema.json")

    def test_archive_prompt_is_current_default(self):
        prompt, contract = prompt_data()
        self.assertIn('"cleaned_full_text"', prompt)
        self.assertIn('"location_collected"', prompt)
        self.assertNotIn('"annotations"', prompt)
        self.assertEqual(contract, self.schema)

    def test_valid_archive_record(self):
        value, errors, parsed = parse_archive_response(json.dumps(archive_record()), self.schema, SOURCE)
        self.assertTrue(parsed)
        self.assertEqual(errors, [])
        self.assertIsNotNone(value)

    def test_wrong_filename_and_age_bucket_fail(self):
        row = archive_record()
        row["filename"] = "made-up.pdf"
        row["contributor"]["age_bucket"] = "45-54"
        value, errors, parsed = parse_archive_response(json.dumps(row), self.schema, SOURCE)
        self.assertTrue(parsed)
        self.assertIsNone(value)
        self.assertGreaterEqual(len(errors), 2)

    def test_generated_database_id_is_rejected(self):
        row = archive_record()
        row["_id"] = "invented-id"
        self.assertIsNone(parse_archive_response(json.dumps(row), self.schema, SOURCE)[0])

    def test_malformed_and_missing_nested_field_fail(self):
        self.assertFalse(parse_archive_response("{", self.schema, SOURCE)[2])
        row = archive_record()
        del row["analysis"]["context"]
        self.assertIsNone(parse_archive_response(json.dumps(row), self.schema, SOURCE)[0])

    def test_archive_run_saves_validated_response_without_live_call(self):
        doc_id = "00003_Legend_Vietnam__38.pdf"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            prepared = {"doc_id": doc_id, "source_pdf": SOURCE, "pdf_sha256": file_sha(ROOT / SOURCE), "pages": [{"page_num": 0, "words": []}]}
            write_json(output / "inputs" / (Path(doc_id).stem + ".json"), prepared)
            raw = {"model": "claude-sonnet-5-5", "content": [{"type": "text", "text": json.dumps(archive_record())}], "stop_reason": "end_turn", "usage": {"input_tokens": 1, "output_tokens": 2}}
            with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}), patch("folklore_eval.predict.OUTPUT", output), patch("folklore_eval.predict.request_vertex", return_value=(raw, 0.1, None, 1)):
                result = predict(doc_id, "sonnet", "development", target="archive")
            run_path = Path(result[0]["run"])
            self.assertTrue(read_json(run_path)["schema_compliant"])
            self.assertEqual(read_json(run_path.parent / "archive.json")["filename"], SOURCE)


if __name__ == "__main__":
    unittest.main()

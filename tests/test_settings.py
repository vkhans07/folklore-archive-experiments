import os
import unittest
from unittest.mock import patch

from folklore_eval.settings import model_settings


class SettingsTests(unittest.TestCase):
    def test_dotenv_defaults_load(self):
        # Keep the user's local .env (which may intentionally override locations)
        # from changing the repository-defaults assertion.
        with patch.dict(os.environ, {}, clear=True), patch("folklore_eval.settings.load_dotenv"):
            config = model_settings()
            self.assertEqual(config["models"]["sonnet"]["id"], "claude-sonnet-5-5")
            self.assertEqual(config["models"]["haiku"]["location"], "global")
            self.assertEqual(config["generation"]["max_tokens"], 16384)

    def test_shell_overrides_dotenv_and_model_specific_location_wins(self):
        with patch.dict(os.environ, {"FOLKLORE_VERTEX_LOCATION": "europe", "FOLKLORE_SONNET_LOCATION": "global", "FOLKLORE_HAIKU_MODEL": "test-model", "FOLKLORE_MAX_TOKENS": "2000", "FOLKLORE_TEMPERATURE": "0.25"}, clear=True):
            config = model_settings()
            self.assertEqual(config["models"]["sonnet"]["location"], "global")
            self.assertEqual(config["models"]["haiku"]["location"], "europe")
            self.assertEqual(config["models"]["haiku"]["id"], "test-model")
            self.assertEqual(config["generation"], {"max_tokens": 2000, "temperature": 0.25})

    def test_invalid_override_is_rejected(self):
        with patch.dict(os.environ, {"FOLKLORE_MAX_TOKENS": "0"}, clear=True):
            with self.assertRaises(ValueError):
                model_settings()


if __name__ == "__main__":
    unittest.main()

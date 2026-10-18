import contextlib
import io
import json
import unittest
from unittest.mock import call, patch
from urllib.error import HTTPError

from folklore_eval.provider import request_gemini_api


class GeminiRetryTests(unittest.TestCase):
    request = {
        "model": "gemini-3.8-flash", "max_tokens": 65536,
        "system": "test", "messages": [{"content": "test"}],
    }
    transport = {"max_attempts": 5, "initial_backoff_seconds": 10, "timeout_seconds": 300}

    @staticmethod
    def error(status, delay=None):
        body = {"error": {"code": status, "message": "provider failure"}}
        if delay is not None:
            body["error"]["details"] = [{"retryDelay": "%ss" % delay}]
        return HTTPError("https://example.invalid", status, "error", {}, io.BytesIO(json.dumps(body).encode()))

    def test_long_provider_wait_is_deferred_without_sleeping_or_retrying_early(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}), \
                patch("folklore_eval.provider.urlopen", side_effect=self.error(429, 36000)) as send, \
                patch("folklore_eval.provider.time.sleep") as sleep, \
                contextlib.redirect_stderr(io.StringIO()):
            raw, _, error, attempts = request_gemini_api(self.request, self.transport)
        self.assertIsNone(raw)
        self.assertEqual(attempts, 1)
        self.assertEqual(error["status_code"], 429)
        self.assertTrue(error["retry_deferred"])
        self.assertEqual(error["retry_after_seconds"], 36000)
        self.assertEqual(send.call_count, 1)
        sleep.assert_not_called()

    def test_overload_exhausts_five_attempts_with_bounded_backoff(self):
        def overloaded(*args, **kwargs):
            raise self.error(503)

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}), \
                patch("folklore_eval.provider.urlopen", side_effect=overloaded) as send, \
                patch("folklore_eval.provider.time.sleep") as sleep, \
                contextlib.redirect_stderr(io.StringIO()):
            raw, _, error, attempts = request_gemini_api(self.request, self.transport)
        self.assertIsNone(raw)
        self.assertEqual(attempts, 5)
        self.assertEqual(error["status_code"], 503)
        self.assertEqual(send.call_count, 5)
        self.assertEqual(sleep.call_args_list, [call(10), call(20), call(40), call(80)])

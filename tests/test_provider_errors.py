import unittest

from folklore_eval.provider import _error_details


class FakeProviderError(Exception):
    def __init__(self, message, status_code=None, body=None, request_id=None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.request_id = request_id


class ProviderErrorTests(unittest.TestCase):
    def test_quota_error_has_actionable_classification_and_metadata(self):
        error = FakeProviderError(
            "429 RESOURCE_EXHAUSTED",
            429,
            {"message": "quota exceeded for global endpoint"},
            "req-123",
        )
        details = _error_details(error)
        self.assertEqual(details["category"], "quota_or_capacity")
        self.assertEqual(details["status_code"], 429)
        self.assertEqual(details["provider_request_id"], "req-123")
        self.assertIn("quota", details["next_step"].lower())

    def test_permission_error_is_not_mislabeled_as_quota(self):
        details = _error_details(FakeProviderError("PERMISSION_DENIED", 403))
        self.assertEqual(details["category"], "authentication_or_permission")


if __name__ == "__main__":
    unittest.main()

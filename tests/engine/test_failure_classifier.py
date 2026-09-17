import unittest

from kmj_forge.engine.failure_classifier import FailureCategory, classify_failure


class FailureClassifierTests(unittest.TestCase):
    def test_classifies_common_failure_signals_deterministically(self):
        cases = (
            ("AssertionError: expected 2 got 3", FailureCategory.TEST),
            ("ModuleNotFoundError: No module named 'x'", FailureCategory.DEPENDENCY),
            ("PermissionError: [Errno 13] Permission denied", FailureCategory.PERMISSION),
            ("TimeoutError: operation timed out", FailureCategory.TIMEOUT),
            ("ConnectionError: connection refused", FailureCategory.NETWORK),
            ("SyntaxError: invalid syntax", FailureCategory.CODE),
        )
        for message, expected in cases:
            with self.subTest(message=message):
                result = classify_failure(message)
                self.assertEqual(result.category, expected)
                self.assertTrue(result.reason)

    def test_unknown_and_empty_fail_closed_to_unknown(self):
        self.assertEqual(classify_failure("unexpected failure").category, FailureCategory.UNKNOWN)
        self.assertEqual(classify_failure("   ").category, FailureCategory.UNKNOWN)

    def test_precedence_prefers_permission_over_generic_network_wording(self):
        result = classify_failure("Permission denied while opening network socket")
        self.assertEqual(result.category, FailureCategory.PERMISSION)


if __name__ == "__main__":
    unittest.main()

import unittest

from kmj_forge.engine.regression import RegressionEngine, RegressionResult


class RegressionEngineTests(unittest.TestCase):
    def test_requires_full_plan_coverage(self):
        engine = RegressionEngine()
        commands = ("python -m unittest tests.test_a", "python -m unittest discover -s tests")
        result = RegressionResult(command="python -m unittest tests.test_a", passed=True, test_count=1, failure_count=0)
        with self.assertRaisesRegex(ValueError, "missing regression evidence"):
            engine.verify(commands, (result,))

    def test_rejects_any_regression_failure(self):
        engine = RegressionEngine()
        command = "python -m unittest discover -s tests"
        result = RegressionResult(command=command, passed=False, test_count=87, failure_count=1)
        with self.assertRaisesRegex(ValueError, "regression verification failed"):
            engine.verify((command,), (result,))

    def test_accepts_complete_passing_evidence_deterministically(self):
        engine = RegressionEngine()
        commands = ("python -m unittest discover -s tests", "npm test")
        results = (
            RegressionResult(command="npm test", passed=True, test_count=12, failure_count=0),
            RegressionResult(command="python -m unittest discover -s tests", passed=True, test_count=87, failure_count=0),
        )
        verified = engine.verify(commands, results)
        self.assertEqual([item.command for item in verified], sorted(item.command for item in results))
        self.assertEqual(sum(item.test_count for item in verified), 99)


if __name__ == "__main__":
    unittest.main()


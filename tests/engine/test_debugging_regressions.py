import unittest

from kmj_forge.engine.debugger import DebugDiagnosis
from kmj_forge.engine.failure_classifier import FailureCategory, classify_failure
from kmj_forge.engine.hypothesis import Hypothesis
from kmj_forge.engine.second_opinion import SecondOpinionAgent


class DebuggingRegressionTests(unittest.TestCase):
    """Permanent regression cases for previously verified Phase-05 boundaries."""

    def test_classifier_precedence_keeps_permission_failures_out_of_code_bucket(self):
        failure = classify_failure("PermissionError: access denied while handling ValueError")
        self.assertEqual(FailureCategory.PERMISSION, failure.category)

    def test_second_opinion_rejects_whitespace_only_independent_evidence(self):
        hypothesis = Hypothesis(
            category=FailureCategory.CODE,
            rank=1,
            statement="implementation violates the expected behavior contract",
        )
        diagnosis = DebugDiagnosis(
            category=FailureCategory.CODE,
            hypothesis=hypothesis,
            experiment="trace the failing input and state against the implementation contract",
        )
        opinion = SecondOpinionAgent().review(
            diagnosis,
            category=FailureCategory.CODE,
            hypothesis_statement="   ",
        )
        self.assertFalse(opinion.agrees)
        self.assertFalse(opinion.mutation_allowed)

    def test_second_opinion_never_authorizes_mutation_even_on_agreement(self):
        hypothesis = Hypothesis(
            category=FailureCategory.CODE,
            rank=1,
            statement="implementation violates the expected behavior contract",
        )
        diagnosis = DebugDiagnosis(
            category=FailureCategory.CODE,
            hypothesis=hypothesis,
            experiment="trace the failing input and state against the implementation contract",
        )
        opinion = SecondOpinionAgent().review(
            diagnosis,
            category=FailureCategory.CODE,
            hypothesis_statement=hypothesis.statement,
        )
        self.assertTrue(opinion.agrees)
        self.assertFalse(opinion.mutation_allowed)


if __name__ == "__main__":
    unittest.main()

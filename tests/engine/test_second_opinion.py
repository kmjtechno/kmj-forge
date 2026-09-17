import unittest

from kmj_forge.engine.debugger import DebugDiagnosis
from kmj_forge.engine.failure_classifier import FailureCategory
from kmj_forge.engine.hypothesis import Hypothesis
from kmj_forge.engine.second_opinion import SecondOpinionAgent


class SecondOpinionAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = SecondOpinionAgent()
        self.hypothesis = Hypothesis(
            category=FailureCategory.CODE,
            rank=1,
            statement="implementation violates the expected behavior contract",
        )
        self.diagnosis = DebugDiagnosis(
            category=FailureCategory.CODE,
            hypothesis=self.hypothesis,
            experiment="trace the failing input and state against the implementation contract",
        )

    def test_agrees_only_with_independently_matching_evidence(self):
        opinion = self.agent.review(
            self.diagnosis,
            category=FailureCategory.CODE,
            hypothesis_statement=self.hypothesis.statement,
        )
        self.assertTrue(opinion.agrees)
        self.assertFalse(opinion.mutation_allowed)

    def test_disagrees_when_independent_category_differs(self):
        opinion = self.agent.review(
            self.diagnosis,
            category=FailureCategory.TEST,
            hypothesis_statement=self.hypothesis.statement,
        )
        self.assertFalse(opinion.agrees)

    def test_disagrees_when_independent_hypothesis_differs(self):
        opinion = self.agent.review(
            self.diagnosis,
            category=FailureCategory.CODE,
            hypothesis_statement="a different root cause",
        )
        self.assertFalse(opinion.agrees)


if __name__ == "__main__":
    unittest.main()

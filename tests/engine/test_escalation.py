import unittest

from kmj_forge.engine.escalation import EscalationAction, EscalationEngine


class EscalationEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = EscalationEngine()

    def test_no_escalation_before_two_failed_attempts(self):
        decision = self.engine.decide(failed_attempts=1, second_opinion_disagrees=False)
        self.assertEqual(decision.action, EscalationAction.CONTINUE)
        self.assertFalse(decision.human_approval_required)

    def test_two_failed_attempts_require_deeper_diagnosis(self):
        decision = self.engine.decide(failed_attempts=2, second_opinion_disagrees=False)
        self.assertEqual(decision.action, EscalationAction.DEEPER_DIAGNOSIS)

    def test_three_failed_attempts_require_independent_agent(self):
        decision = self.engine.decide(failed_attempts=3, second_opinion_disagrees=False)
        self.assertEqual(decision.action, EscalationAction.INDEPENDENT_AGENT)

    def test_persistent_disagreement_fails_closed_to_human(self):
        decision = self.engine.decide(failed_attempts=3, second_opinion_disagrees=True)
        self.assertEqual(decision.action, EscalationAction.HUMAN_REVIEW)
        self.assertTrue(decision.human_approval_required)
        self.assertFalse(decision.mutation_allowed)

    def test_invalid_attempt_count_fails_closed(self):
        with self.assertRaises(ValueError):
            self.engine.decide(failed_attempts=-1, second_opinion_disagrees=False)


if __name__ == "__main__":
    unittest.main()

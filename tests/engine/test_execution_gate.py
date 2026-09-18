import unittest

from kmj_forge.engine.execution_gate import ExecutionGate, ExecutionSignal


class ExecutionGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = ExecutionGate()

    def test_read_only_security_approved_action_can_proceed(self):
        decision = self.gate.evaluate(
            mutates=False, security_allowed=True, security_requires_approval=False,
            approval_granted=False,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.signals, ())

    def test_reversible_mutation_requires_explicit_approval(self):
        decision = self.gate.evaluate(
            mutates=True, security_allowed=False, security_requires_approval=False,
            approval_granted=False,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(ExecutionSignal.APPROVAL_REQUIRED, decision.signals)

    def test_reversible_mutation_can_proceed_only_after_explicit_approval(self):
        decision = self.gate.evaluate(
            mutates=True, security_allowed=False, security_requires_approval=False,
            approval_granted=True,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.signals, ())

    def test_security_denial_cannot_be_overridden_by_approval(self):
        decision = self.gate.evaluate(
            mutates=True, security_allowed=False, security_requires_approval=True,
            approval_granted=True,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(ExecutionSignal.SECURITY_BLOCKED, decision.signals)

    def test_malformed_inputs_fail_closed(self):
        decision = self.gate.evaluate(
            mutates=None, security_allowed=True, security_requires_approval=False,
            approval_granted=True,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(ExecutionSignal.MALFORMED_INPUT, decision.signals)


if __name__ == "__main__":
    unittest.main()

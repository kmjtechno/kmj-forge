import unittest

from kmj_forge.engine.security_gate import SecurityGate, SecuritySignal


class SecurityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = SecurityGate()

    def test_clean_read_only_action_can_proceed_without_approval(self):
        decision = self.gate.evaluate(
            action="read", target="workspace", mutates=False,
            sandbox_allowed=True, network_allowed=True,
            secret_allowed=True, prompt_safe=True,
        )
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.requires_approval)
        self.assertEqual(decision.signals, ())

    def test_any_failed_boundary_blocks_fail_closed(self):
        boundaries = ("sandbox_allowed", "network_allowed", "secret_allowed", "prompt_safe")
        for boundary in boundaries:
            kwargs = dict(
                action="read", target="workspace", mutates=False,
                sandbox_allowed=True, network_allowed=True,
                secret_allowed=True, prompt_safe=True,
            )
            kwargs[boundary] = False
            with self.subTest(boundary=boundary):
                decision = self.gate.evaluate(**kwargs)
                self.assertFalse(decision.allowed)
                self.assertTrue(decision.requires_approval)
                self.assertIn(SecuritySignal.BOUNDARY_DENIED, decision.signals)

    def test_high_risk_action_blocks_and_requires_approval(self):
        decision = self.gate.evaluate(
            action="delete", target="workspace", mutates=True, destructive=True,
            sandbox_allowed=True, network_allowed=True,
            secret_allowed=True, prompt_safe=True,
        )
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_approval)
        self.assertIn(SecuritySignal.HIGH_RISK, decision.signals)

    def test_medium_risk_reversible_local_mutation_is_not_authorized_by_gate(self):
        decision = self.gate.evaluate(
            action="write", target="workspace", mutates=True,
            sandbox_allowed=True, network_allowed=True,
            secret_allowed=True, prompt_safe=True,
        )
        self.assertFalse(decision.allowed)
        self.assertFalse(decision.requires_approval)
        self.assertIn(SecuritySignal.MUTATION_REQUIRES_EXECUTION_GATE, decision.signals)

    def test_malformed_boundary_signal_fails_closed(self):
        decision = self.gate.evaluate(
            action="read", target="workspace", mutates=False,
            sandbox_allowed=None, network_allowed=True,
            secret_allowed=True, prompt_safe=True,
        )
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_approval)
        self.assertIn(SecuritySignal.MALFORMED_INPUT, decision.signals)


if __name__ == "__main__":
    unittest.main()

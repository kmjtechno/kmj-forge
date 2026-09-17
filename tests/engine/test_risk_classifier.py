import unittest

from kmj_forge.engine.risk_classifier import RiskClassifier, RiskLevel


class RiskClassifierTests(unittest.TestCase):
    def setUp(self):
        self.classifier = RiskClassifier()

    def test_read_only_local_action_is_low_risk(self):
        decision = self.classifier.classify(action="read", target="workspace", mutates=False)
        self.assertEqual(decision.level, RiskLevel.LOW)
        self.assertFalse(decision.requires_approval)

    def test_workspace_mutation_is_medium_risk(self):
        decision = self.classifier.classify(action="write", target="workspace", mutates=True)
        self.assertEqual(decision.level, RiskLevel.MEDIUM)
        self.assertFalse(decision.requires_approval)

    def test_sensitive_targets_require_approval(self):
        for target in ("credentials", "billing", "production", "security_policy"):
            with self.subTest(target=target):
                decision = self.classifier.classify(action="change", target=target, mutates=True)
                self.assertEqual(decision.level, RiskLevel.HIGH)
                self.assertTrue(decision.requires_approval)

    def test_destructive_action_requires_approval(self):
        decision = self.classifier.classify(action="delete", target="workspace", mutates=True, destructive=True)
        self.assertEqual(decision.level, RiskLevel.HIGH)
        self.assertTrue(decision.requires_approval)

    def test_unknown_or_malformed_input_fails_closed(self):
        for kwargs in (
            dict(action="", target="workspace", mutates=False),
            dict(action="read", target="", mutates=False),
            dict(action="read", target="unknown_external_system", mutates=False),
        ):
            with self.subTest(kwargs=kwargs):
                decision = self.classifier.classify(**kwargs)
                self.assertEqual(decision.level, RiskLevel.HIGH)
                self.assertTrue(decision.requires_approval)


if __name__ == "__main__":
    unittest.main()

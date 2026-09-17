import unittest

from kmj_forge.engine.secret_isolation import SecretIsolationPolicy


class SecretIsolationPolicyTests(unittest.TestCase):
    def test_secret_access_is_denied_by_default(self):
        policy = SecretIsolationPolicy()
        self.assertFalse(policy.allows("github_token", "git"))

    def test_secret_allowlist_requires_explicit_approval(self):
        with self.assertRaisesRegex(ValueError, "explicit approval"):
            SecretIsolationPolicy(allowed_bindings=(("github_token", "git"),))

    def test_approved_binding_is_exact(self):
        policy = SecretIsolationPolicy(
            explicit_approval=True,
            allowed_bindings=(("github_token", "git"),),
        )
        self.assertTrue(policy.allows("github_token", "git"))
        self.assertFalse(policy.allows("github_token", "terminal"))
        self.assertFalse(policy.allows("other_token", "git"))

    def test_invalid_secret_or_consumer_names_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "identifier"):
            SecretIsolationPolicy(
                explicit_approval=True,
                allowed_bindings=(("../token", "git"),),
            )
        policy = SecretIsolationPolicy(
            explicit_approval=True,
            allowed_bindings=(("github_token", "git"),),
        )
        self.assertFalse(policy.allows("github_token", "../git"))

    def test_policy_never_returns_secret_material(self):
        policy = SecretIsolationPolicy(
            explicit_approval=True,
            allowed_bindings=(("github_token", "git"),),
        )
        decision = policy.allows("github_token", "git")
        self.assertIs(decision, True)
        self.assertNotIsInstance(decision, str)


if __name__ == "__main__":
    unittest.main()

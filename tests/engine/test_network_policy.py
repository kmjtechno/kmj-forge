import unittest

from kmj_forge.engine.network_policy import NetworkPolicy


class NetworkPolicyTests(unittest.TestCase):
    def test_network_is_denied_by_default(self):
        policy = NetworkPolicy()
        self.assertFalse(policy.allows("https", "api.example.com", 443))

    def test_allowlisted_destination_requires_explicit_approval(self):
        with self.assertRaisesRegex(ValueError, "explicit approval"):
            NetworkPolicy(allowed_hosts=("api.example.com",))

    def test_approved_allowlist_is_exact_and_https_only_by_default(self):
        policy = NetworkPolicy(explicit_approval=True, allowed_hosts=("api.example.com",))
        self.assertTrue(policy.allows("https", "api.example.com", 443))
        self.assertFalse(policy.allows("http", "api.example.com", 80))
        self.assertFalse(policy.allows("https", "evil.example.com", 443))
        self.assertFalse(policy.allows("https", "api.example.com.evil.test", 443))

    def test_local_and_metadata_targets_fail_closed_even_if_allowlisted(self):
        policy = NetworkPolicy(
            explicit_approval=True,
            allowed_hosts=("localhost", "127.0.0.1", "169.254.169.254"),
        )
        self.assertFalse(policy.allows("https", "localhost", 443))
        self.assertFalse(policy.allows("https", "127.0.0.1", 443))
        self.assertFalse(policy.allows("https", "169.254.169.254", 443))

    def test_invalid_host_entries_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "host"):
            NetworkPolicy(explicit_approval=True, allowed_hosts=("https://api.example.com/path",))


if __name__ == "__main__":
    unittest.main()

import unittest

from kmj_forge.engine.sandbox import SandboxMode, SandboxPolicy


class SandboxPolicyTests(unittest.TestCase):
    def test_default_mode_is_restricted_and_fail_closed(self):
        policy = SandboxPolicy()
        self.assertEqual(policy.mode, SandboxMode.RESTRICTED)
        self.assertFalse(policy.network_allowed)
        self.assertFalse(policy.host_filesystem_allowed)
        self.assertFalse(policy.privileged_execution_allowed)

    def test_restricted_mode_allows_only_workspace_paths(self):
        policy = SandboxPolicy(workspace_root="/workspace/project")
        self.assertTrue(policy.allows_path("/workspace/project/src/app.py"))
        self.assertTrue(policy.allows_path("/workspace/project"))
        self.assertFalse(policy.allows_path("/workspace/project-escape/secret"))
        self.assertFalse(policy.allows_path("/etc/passwd"))
        self.assertFalse(policy.allows_path("../secret"))

    def test_none_mode_requires_explicit_approval(self):
        with self.assertRaises(ValueError):
            SandboxPolicy(mode=SandboxMode.NONE)
        policy = SandboxPolicy(mode=SandboxMode.NONE, explicit_approval=True)
        self.assertTrue(policy.host_filesystem_allowed)

    def test_stronger_isolation_stays_non_privileged_by_default(self):
        for mode in (SandboxMode.CONTAINER, SandboxMode.VM, SandboxMode.REMOTE_EPHEMERAL):
            policy = SandboxPolicy(mode=mode)
            self.assertFalse(policy.privileged_execution_allowed)
            self.assertFalse(policy.network_allowed)


if __name__ == "__main__":
    unittest.main()

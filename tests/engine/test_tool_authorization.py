import unittest

from kmj_forge.engine.execution_gate import ExecutionSignal
from kmj_forge.engine.tool_authorization import authorize_tool_execution
from kmj_forge.engine.tool_contract import PermissionClass, ToolContract


def contract(permission_class: PermissionClass) -> ToolContract:
    return ToolContract.create(
        name="example",
        permission_class=permission_class,
        timeout_seconds=1,
        cancellable=True,
        max_retries=0,
        input_schema="tool-input.v1",
        output_schema="tool-output.v1",
        audit_event="tool.example",
        error_schema="error.v1",
        evidence_schema="evidence.v1",
    )


class ToolAuthorizationTests(unittest.TestCase):
    def test_read_only_tool_can_run_without_mutation_approval(self):
        decision = authorize_tool_execution(
            contract(PermissionClass.READ_ONLY),
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.signals, ())

    def test_workspace_write_requires_explicit_approval(self):
        decision = authorize_tool_execution(
            contract(PermissionClass.WORKSPACE_WRITE),
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.signals, (ExecutionSignal.APPROVAL_REQUIRED,))

    def test_workspace_write_can_run_after_explicit_approval(self):
        decision = authorize_tool_execution(
            contract(PermissionClass.WORKSPACE_WRITE),
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=True,
        )
        self.assertTrue(decision.allowed)

    def test_external_write_and_privileged_never_bypass_security_approval_gate(self):
        for permission in (PermissionClass.EXTERNAL_WRITE, PermissionClass.PRIVILEGED):
            with self.subTest(permission=permission):
                decision = authorize_tool_execution(
                    contract(permission),
                    security_allowed=True,
                    security_requires_approval=True,
                    approval_granted=True,
                )
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.signals, (ExecutionSignal.SECURITY_BLOCKED,))

    def test_invalid_contract_is_rejected_fail_closed(self):
        with self.assertRaises(TypeError):
            authorize_tool_execution(
                object(),
                security_allowed=True,
                security_requires_approval=False,
                approval_granted=True,
            )


if __name__ == "__main__":
    unittest.main()

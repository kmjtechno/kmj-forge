import unittest
from dataclasses import FrozenInstanceError

from kmj_forge.engine.execution_gate import ExecutionSignal
from kmj_forge.engine.tool_contract import PermissionClass, ToolContract
from kmj_forge.engine.tool_registry import ToolRegistry
from kmj_forge.engine.tool_runtime import ToolInvocationPlan, ToolRuntime


def contract(name: str, permission: PermissionClass) -> ToolContract:
    return ToolContract.create(
        name=name,
        permission_class=permission,
        timeout_seconds=1,
        cancellable=True,
        max_retries=0,
        input_schema="tool-input.v1",
        output_schema="tool-output.v1",
        audit_event=f"tool.{name}",
        error_schema="error.v1",
        evidence_schema="evidence.v1",
    )


class ToolRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.read_contract = contract("read_file", PermissionClass.READ_ONLY)
        self.write_contract = contract("write_file", PermissionClass.WORKSPACE_WRITE)
        self.registry.register(self.read_contract)
        self.registry.register(self.write_contract)
        self.runtime = ToolRuntime(self.registry)

    def test_read_only_registered_tool_can_be_authorized(self):
        decision = self.runtime.authorize(
            "read_file",
            expected_permission=PermissionClass.READ_ONLY,
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.signals, ())

    def test_mutating_registered_tool_still_requires_execution_approval(self):
        decision = self.runtime.authorize(
            "write_file",
            expected_permission=PermissionClass.WORKSPACE_WRITE,
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.signals, (ExecutionSignal.APPROVAL_REQUIRED,))

    def test_prepare_binds_exact_contract_to_authorization_decision(self):
        plan = self.runtime.prepare(
            "read_file",
            expected_permission=PermissionClass.READ_ONLY,
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        self.assertIsInstance(plan, ToolInvocationPlan)
        self.assertIs(plan.contract, self.read_contract)
        self.assertTrue(plan.decision.allowed)
        self.assertEqual(plan.contract.audit_event, "tool.read_file")
        self.assertEqual(plan.contract.evidence_schema, "evidence.v1")

    def test_prepare_preserves_denial_with_same_contract(self):
        plan = self.runtime.prepare(
            "write_file",
            expected_permission=PermissionClass.WORKSPACE_WRITE,
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        self.assertIs(plan.contract, self.write_contract)
        self.assertFalse(plan.decision.allowed)
        self.assertEqual(plan.decision.signals, (ExecutionSignal.APPROVAL_REQUIRED,))

    def test_invocation_plan_is_immutable(self):
        plan = self.runtime.prepare(
            "read_file",
            expected_permission=PermissionClass.READ_ONLY,
            security_allowed=True,
            security_requires_approval=False,
            approval_granted=False,
        )
        with self.assertRaises(FrozenInstanceError):
            plan.contract = self.write_contract

    def test_permission_mismatch_fails_before_authorization(self):
        with self.assertRaises(PermissionError):
            self.runtime.authorize(
                "write_file",
                expected_permission=PermissionClass.READ_ONLY,
                security_allowed=True,
                security_requires_approval=False,
                approval_granted=True,
            )

    def test_unknown_tool_fails_closed(self):
        with self.assertRaises(KeyError):
            self.runtime.authorize(
                "missing",
                expected_permission=PermissionClass.READ_ONLY,
                security_allowed=True,
                security_requires_approval=False,
                approval_granted=False,
            )

    def test_runtime_requires_registry(self):
        with self.assertRaises(TypeError):
            ToolRuntime(object())


if __name__ == "__main__":
    unittest.main()

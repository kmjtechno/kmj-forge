"""Side-effect-free runtime authorization boundary for registered tools."""

from __future__ import annotations

from dataclasses import dataclass

from .execution_gate import ExecutionDecision
from .tool_authorization import authorize_tool_execution
from .tool_contract import PermissionClass, ToolContract
from .tool_registry import ToolRegistry


@dataclass(frozen=True, slots=True)
class ToolInvocationPlan:
    """Immutable binding between the exact registered contract and its decision."""

    contract: ToolContract
    decision: ExecutionDecision

    @property
    def timeout_seconds(self) -> int:
        return self.contract.timeout_seconds

    @property
    def cancellable(self) -> bool:
        return self.contract.cancellable

    @property
    def max_retries(self) -> int:
        return self.contract.max_retries

    @property
    def audit_event(self) -> str:
        return self.contract.audit_event

    @property
    def error_schema(self) -> str:
        return self.contract.error_schema

    @property
    def evidence_schema(self) -> str:
        return self.contract.evidence_schema


class ToolRuntime:
    """Resolve a registered tool contract and authorize it without executing it."""

    def __init__(self, registry: ToolRegistry) -> None:
        if not isinstance(registry, ToolRegistry):
            raise TypeError("registry must be a ToolRegistry")
        self._registry = registry

    def prepare(self, name: str, *, expected_permission: PermissionClass, security_allowed: bool, security_requires_approval: bool, approval_granted: bool) -> ToolInvocationPlan:
        """Bind the exact registered contract to its fail-closed authorization result."""
        contract = self._registry.require_permission(name, expected_permission)
        decision = authorize_tool_execution(contract, security_allowed=security_allowed, security_requires_approval=security_requires_approval, approval_granted=approval_granted)
        return ToolInvocationPlan(contract=contract, decision=decision)

    def authorize(self, name: str, *, expected_permission: PermissionClass, security_allowed: bool, security_requires_approval: bool, approval_granted: bool) -> ExecutionDecision:
        """Compatibility boundary returning only the authorization decision."""
        return self.prepare(name, expected_permission=expected_permission, security_allowed=security_allowed, security_requires_approval=security_requires_approval, approval_granted=approval_granted).decision

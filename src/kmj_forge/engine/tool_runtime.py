"""Side-effect-free runtime authorization boundary for registered tools."""

from __future__ import annotations

from .execution_gate import ExecutionDecision
from .tool_authorization import authorize_tool_execution
from .tool_contract import PermissionClass
from .tool_registry import ToolRegistry


class ToolRuntime:
    """Resolve a registered tool contract and authorize it without executing it."""

    def __init__(self, registry: ToolRegistry) -> None:
        if not isinstance(registry, ToolRegistry):
            raise TypeError("registry must be a ToolRegistry")
        self._registry = registry

    def authorize(
        self,
        name: str,
        *,
        expected_permission: PermissionClass,
        security_allowed: bool,
        security_requires_approval: bool,
        approval_granted: bool,
    ) -> ExecutionDecision:
        """Fail closed unless registration, permission and execution gates all pass."""
        contract = self._registry.require_permission(name, expected_permission)
        return authorize_tool_execution(
            contract,
            security_allowed=security_allowed,
            security_requires_approval=security_requires_approval,
            approval_granted=approval_granted,
        )

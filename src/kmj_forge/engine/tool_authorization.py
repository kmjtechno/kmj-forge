"""Permission-aware authorization boundary for validated tool contracts."""

from __future__ import annotations

from .execution_gate import ExecutionDecision, ExecutionGate
from .tool_contract import PermissionClass, ToolContract


_MUTATING_PERMISSIONS = frozenset(
    {
        PermissionClass.WORKSPACE_WRITE,
        PermissionClass.EXTERNAL_WRITE,
        PermissionClass.PRIVILEGED,
    }
)


def authorize_tool_execution(
    contract: ToolContract,
    *,
    security_allowed: bool,
    security_requires_approval: bool,
    approval_granted: bool,
) -> ExecutionDecision:
    """Authorize a validated tool contract without performing side effects.

    Permission class is the source of truth for whether the operation mutates.
    The existing execution gate then enforces security and explicit approval.
    """
    if not isinstance(contract, ToolContract):
        raise TypeError("contract must be a ToolContract")

    return ExecutionGate().evaluate(
        mutates=contract.permission_class in _MUTATING_PERMISSIONS,
        security_allowed=security_allowed,
        security_requires_approval=security_requires_approval,
        approval_granted=approval_granted,
    )

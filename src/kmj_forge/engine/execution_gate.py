from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionSignal(str, Enum):
    SECURITY_BLOCKED = "security_blocked"
    APPROVAL_REQUIRED = "approval_required"
    MALFORMED_INPUT = "malformed_input"


@dataclass(frozen=True)
class ExecutionDecision:
    allowed: bool
    signals: tuple[ExecutionSignal, ...]


@dataclass(frozen=True)
class ExecutionGate:
    """Fail-closed authorization boundary between security review and execution.

    This component is side-effect free. It never performs an action; it only
    decides whether a separately executed action has cleared the required gates.
    """

    def evaluate(
        self,
        *,
        mutates: bool,
        security_allowed: bool,
        security_requires_approval: bool,
        approval_granted: bool,
    ) -> ExecutionDecision:
        values = (mutates, security_allowed, security_requires_approval, approval_granted)
        if any(type(value) is not bool for value in values):
            return ExecutionDecision(False, (ExecutionSignal.MALFORMED_INPUT,))

        # A security denial or high-risk finding is not an approval bypass.
        if security_requires_approval:
            return ExecutionDecision(False, (ExecutionSignal.SECURITY_BLOCKED,))

        if not mutates:
            if security_allowed:
                return ExecutionDecision(True, ())
            return ExecutionDecision(False, (ExecutionSignal.SECURITY_BLOCKED,))

        # The aggregate security gate deliberately does not authorize mutations;
        # reversible mutation proceeds only through an explicit execution approval.
        if not approval_granted:
            return ExecutionDecision(False, (ExecutionSignal.APPROVAL_REQUIRED,))
        return ExecutionDecision(True, ())

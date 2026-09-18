from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class SecurityAuditSignal(str, Enum):
    SECURITY_BLOCKED = "security_blocked"
    APPROVAL_REQUIRED = "approval_required"
    MALFORMED_INPUT = "malformed_input"


_ACTION_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
_TARGET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:_.@/-]{0,127}$")
_SECRET_LIKE = re.compile(
    r"(?i)(?:token|secret|password|passwd|api[_-]?key|authorization|bearer)\s*[:=]"
)


@dataclass(frozen=True)
class SecurityAuditRecord:
    """Immutable, secret-safe metadata for a security/execution decision.

    The record intentionally accepts identifiers and decision signals only. It
    never accepts arbitrary payloads, command output, environment values, or
    credential material.
    """

    action_id: str
    target_id: str
    allowed: bool
    requires_approval: bool
    signals: tuple[SecurityAuditSignal, ...]

    @classmethod
    def create(
        cls,
        *,
        action_id: str,
        target_id: str,
        allowed: bool,
        requires_approval: bool,
        signals: tuple[SecurityAuditSignal, ...],
    ) -> "SecurityAuditRecord":
        if type(action_id) is not str or not _ACTION_ID.fullmatch(action_id):
            raise ValueError("invalid action identifier")
        if type(target_id) is not str or not _TARGET_ID.fullmatch(target_id):
            raise ValueError("invalid target identifier")
        if _SECRET_LIKE.search(action_id) or _SECRET_LIKE.search(target_id):
            raise ValueError("secret-like material is forbidden in audit metadata")
        if type(allowed) is not bool or type(requires_approval) is not bool:
            raise ValueError("decision flags must be booleans")
        if not isinstance(signals, tuple) or any(not isinstance(item, SecurityAuditSignal) for item in signals):
            raise ValueError("signals must be SecurityAuditSignal values")
        if allowed and requires_approval:
            raise ValueError("an allowed decision cannot still require approval")

        canonical = tuple(sorted(set(signals), key=lambda item: item.value))
        return cls(
            action_id=action_id,
            target_id=target_id,
            allowed=allowed,
            requires_approval=requires_approval,
            signals=canonical,
        )

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RiskDecision:
    level: RiskLevel
    requires_approval: bool
    reason: str


@dataclass(frozen=True)
class RiskClassifier:
    """Conservative action-risk classifier used before execution authorization.

    Classification never authorizes an action. Unknown targets and destructive or
    security-sensitive actions fail closed and require a separate approval gate.
    """

    sensitive_targets: frozenset[str] = frozenset(
        {"credentials", "billing", "production", "security_policy"}
    )
    known_targets: frozenset[str] = frozenset(
        {"workspace", "repository", "tests", "documentation", "credentials", "billing", "production", "security_policy"}
    )

    def classify(
        self,
        *,
        action: str,
        target: str,
        mutates: bool,
        destructive: bool = False,
    ) -> RiskDecision:
        if not isinstance(action, str) or not action.strip():
            return RiskDecision(RiskLevel.HIGH, True, "malformed action")
        if not isinstance(target, str) or not target.strip() or target not in self.known_targets:
            return RiskDecision(RiskLevel.HIGH, True, "unknown or malformed target")
        if destructive:
            return RiskDecision(RiskLevel.HIGH, True, "destructive action")
        if target in self.sensitive_targets:
            return RiskDecision(RiskLevel.HIGH, True, "security-sensitive target")
        if mutates:
            return RiskDecision(RiskLevel.MEDIUM, False, "reversible local mutation")
        return RiskDecision(RiskLevel.LOW, False, "read-only known target")

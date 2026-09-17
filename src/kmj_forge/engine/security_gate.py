from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .risk_classifier import RiskClassifier, RiskLevel


class SecuritySignal(str, Enum):
    BOUNDARY_DENIED = "boundary_denied"
    HIGH_RISK = "high_risk"
    MUTATION_REQUIRES_EXECUTION_GATE = "mutation_requires_execution_gate"
    MALFORMED_INPUT = "malformed_input"


@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    requires_approval: bool
    signals: tuple[SecuritySignal, ...]


@dataclass(frozen=True)
class SecurityGate:
    """Aggregate fail-closed security review boundary.

    This gate does not execute actions and never authorizes mutations. It combines
    already-computed policy outcomes with conservative action-risk classification.
    """

    risk_classifier: RiskClassifier = RiskClassifier()

    def evaluate(
        self,
        *,
        action: str,
        target: str,
        mutates: bool,
        sandbox_allowed: bool,
        network_allowed: bool,
        secret_allowed: bool,
        prompt_safe: bool,
        destructive: bool = False,
    ) -> SecurityDecision:
        boundaries = (sandbox_allowed, network_allowed, secret_allowed, prompt_safe)
        if any(type(value) is not bool for value in boundaries):
            return SecurityDecision(False, True, (SecuritySignal.MALFORMED_INPUT,))

        signals: list[SecuritySignal] = []
        if not all(boundaries):
            signals.append(SecuritySignal.BOUNDARY_DENIED)

        risk = self.risk_classifier.classify(
            action=action, target=target, mutates=mutates, destructive=destructive
        )
        if risk.level is RiskLevel.HIGH:
            signals.append(SecuritySignal.HIGH_RISK)

        if mutates and risk.level is not RiskLevel.HIGH:
            signals.append(SecuritySignal.MUTATION_REQUIRES_EXECUTION_GATE)

        requires_approval = bool(
            SecuritySignal.BOUNDARY_DENIED in signals
            or risk.requires_approval
        )
        allowed = not signals and risk.level is RiskLevel.LOW
        return SecurityDecision(allowed, requires_approval, tuple(signals))

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EscalationAction(str, Enum):
    CONTINUE = "continue"
    DEEPER_DIAGNOSIS = "deeper_diagnosis"
    INDEPENDENT_AGENT = "independent_agent"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class EscalationDecision:
    action: EscalationAction
    failed_attempts: int
    human_approval_required: bool = False
    mutation_allowed: bool = False


class EscalationEngine:
    """Choose the next diagnostic escalation without executing or mutating work."""

    def decide(
        self,
        *,
        failed_attempts: int,
        second_opinion_disagrees: bool,
    ) -> EscalationDecision:
        if failed_attempts < 0:
            raise ValueError("failed_attempts must be non-negative")

        if second_opinion_disagrees and failed_attempts >= 3:
            action = EscalationAction.HUMAN_REVIEW
            human_approval_required = True
        elif failed_attempts >= 3:
            action = EscalationAction.INDEPENDENT_AGENT
            human_approval_required = False
        elif failed_attempts >= 2:
            action = EscalationAction.DEEPER_DIAGNOSIS
            human_approval_required = False
        else:
            action = EscalationAction.CONTINUE
            human_approval_required = False

        return EscalationDecision(
            action=action,
            failed_attempts=failed_attempts,
            human_approval_required=human_approval_required,
        )

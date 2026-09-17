from __future__ import annotations

from dataclasses import dataclass

from .failure_classifier import FailureCategory, FailureClassification
from .hypothesis import Hypothesis
from .reproduction import ReproductionResult


@dataclass(frozen=True)
class DebugDiagnosis:
    category: FailureCategory
    hypothesis: Hypothesis
    experiment: str
    mutation_allowed: bool = False


_EXPERIMENTS: dict[FailureCategory, str] = {
    FailureCategory.TEST: "inspect implementation behavior against the failing assertion",
    FailureCategory.DEPENDENCY: "compare declared dependencies with the active environment",
    FailureCategory.PERMISSION: "inspect the requested resource against the active permission boundary",
    FailureCategory.TIMEOUT: "measure the blocked operation against its configured time budget",
    FailureCategory.NETWORK: "inspect endpoint reachability and connection establishment evidence",
    FailureCategory.CODE: "trace the failing input and state against the implementation contract",
}


class DebuggerAgent:
    """Select a deterministic diagnostic experiment without executing or mutating anything."""

    def diagnose(
        self,
        failure: FailureClassification,
        reproduction: ReproductionResult,
        hypotheses: tuple[Hypothesis, ...],
    ) -> DebugDiagnosis | None:
        if not reproduction.reproduced:
            return None
        if failure.category is FailureCategory.UNKNOWN:
            return None
        if reproduction.category is not failure.category:
            return None
        if not hypotheses:
            return None
        if any(item.category is not failure.category for item in hypotheses):
            return None
        expected_ranks = tuple(range(1, len(hypotheses) + 1))
        if tuple(item.rank for item in hypotheses) != expected_ranks:
            return None
        experiment = _EXPERIMENTS.get(failure.category)
        if experiment is None:
            return None
        return DebugDiagnosis(
            category=failure.category,
            hypothesis=hypotheses[0],
            experiment=experiment,
        )

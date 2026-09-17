from __future__ import annotations

from dataclasses import dataclass

from .failure_classifier import FailureCategory, FailureClassification
from .reproduction import ReproductionResult


@dataclass(frozen=True)
class Hypothesis:
    rank: int
    category: FailureCategory
    statement: str


_HYPOTHESES: dict[FailureCategory, tuple[str, ...]] = {
    FailureCategory.TEST: (
        "implementation behavior disagrees with the verified test expectation",
        "test fixture or setup does not represent the intended behavior",
    ),
    FailureCategory.DEPENDENCY: (
        "required dependency is absent or unresolved in the active environment",
        "dependency version or import path is incompatible with the project",
    ),
    FailureCategory.PERMISSION: (
        "required resource access is denied by the active permission boundary",
        "operation targets a path or resource outside the allowed scope",
    ),
    FailureCategory.TIMEOUT: (
        "operation exceeds its deterministic time budget",
        "upstream work is blocked or slower than the configured timeout permits",
    ),
    FailureCategory.NETWORK: (
        "required endpoint is unreachable from the active environment",
        "network name resolution or connection establishment is failing",
    ),
    FailureCategory.CODE: (
        "executed code violates a runtime or language invariant",
        "input or state does not satisfy the implementation contract",
    ),
}


class HypothesisEngine:
    """Generate ranked diagnostic hypotheses without executing or mutating anything."""

    def generate(
        self,
        failure: FailureClassification,
        reproduction: ReproductionResult,
    ) -> tuple[Hypothesis, ...]:
        if not reproduction.reproduced:
            return ()
        if failure.category is FailureCategory.UNKNOWN:
            return ()
        if reproduction.category is not failure.category:
            return ()
        statements = _HYPOTHESES.get(failure.category, ())
        return tuple(
            Hypothesis(rank=index, category=failure.category, statement=statement)
            for index, statement in enumerate(statements, start=1)
        )

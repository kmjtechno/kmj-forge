from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .failure_classifier import FailureCategory, FailureClassification, classify_failure


@dataclass(frozen=True)
class ReproductionAttempt:
    command: str
    output: str
    exit_code: int


@dataclass(frozen=True)
class ReproductionResult:
    reproduced: bool
    category: FailureCategory
    matching_attempts: tuple[ReproductionAttempt, ...]


class ReproductionManager:
    """Evaluate captured attempts without executing commands or mutating the workspace."""

    def evaluate(
        self,
        expected: FailureClassification,
        attempts: Iterable[ReproductionAttempt],
    ) -> ReproductionResult:
        matching: list[ReproductionAttempt] = []
        for attempt in attempts:
            if attempt.exit_code == 0:
                continue
            observed = classify_failure(attempt.output)
            if observed.category is expected.category and observed.category is not FailureCategory.UNKNOWN:
                matching.append(attempt)
        return ReproductionResult(bool(matching), expected.category, tuple(matching))

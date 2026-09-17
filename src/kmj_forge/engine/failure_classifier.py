from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureCategory(str, Enum):
    TEST = "test"
    DEPENDENCY = "dependency"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    NETWORK = "network"
    CODE = "code"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FailureClassification:
    category: FailureCategory
    reason: str


_RULES: tuple[tuple[FailureCategory, tuple[str, ...]], ...] = (
    (FailureCategory.PERMISSION, ("permissionerror", "permission denied", "access denied", "forbidden")),
    (FailureCategory.TIMEOUT, ("timeouterror", "timed out", "timeout")),
    (FailureCategory.DEPENDENCY, ("modulenotfounderror", "importerror", "no module named", "dependency")),
    (FailureCategory.TEST, ("assertionerror", "assert failed", "test failed", "failed test")),
    (FailureCategory.NETWORK, ("connectionerror", "connection refused", "connection reset", "network unreachable", "dns")),
    (FailureCategory.CODE, ("syntaxerror", "typeerror", "nameerror", "attributeerror", "valueerror")),
)


def classify_failure(error: str) -> FailureClassification:
    normalized = " ".join(error.strip().lower().split())
    if not normalized:
        return FailureClassification(FailureCategory.UNKNOWN, "no failure signal provided")
    for category, signals in _RULES:
        matched = next((signal for signal in signals if signal in normalized), None)
        if matched is not None:
            return FailureClassification(category, f"matched deterministic signal: {matched}")
    return FailureClassification(FailureCategory.UNKNOWN, "no known deterministic failure signal matched")

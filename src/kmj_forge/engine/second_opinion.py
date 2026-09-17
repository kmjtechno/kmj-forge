from __future__ import annotations

from dataclasses import dataclass

from .debugger import DebugDiagnosis
from .failure_classifier import FailureCategory


@dataclass(frozen=True)
class SecondOpinion:
    category: FailureCategory
    hypothesis_statement: str
    agrees: bool
    mutation_allowed: bool = False


class SecondOpinionAgent:
    """Compare independent diagnostic evidence without executing or mutating anything."""

    def review(
        self,
        diagnosis: DebugDiagnosis,
        *,
        category: FailureCategory,
        hypothesis_statement: str,
    ) -> SecondOpinion:
        statement = hypothesis_statement.strip()
        agrees = (
            category is not FailureCategory.UNKNOWN
            and category is diagnosis.category
            and bool(statement)
            and statement == diagnosis.hypothesis.statement
        )
        return SecondOpinion(
            category=category,
            hypothesis_statement=statement,
            agrees=agrees,
        )

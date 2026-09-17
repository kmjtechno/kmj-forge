from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TDDPhase(str, Enum):
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"


@dataclass(frozen=True, slots=True)
class TDDEvent:
    phase: TDDPhase
    command: str
    passed: bool


class TDDWorkflow:
    """Fail-closed evidence state machine for red/green/refactor TDD."""

    def __init__(self, task_id: str) -> None:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id must be non-empty")
        self.task_id = task_id
        self._events: list[TDDEvent] = []

    @property
    def events(self) -> tuple[TDDEvent, ...]:
        return tuple(self._events)

    @property
    def phase(self) -> TDDPhase | None:
        return self._events[-1].phase if self._events else None

    @property
    def is_verified(self) -> bool:
        return bool(self._events) and self.phase in (TDDPhase.GREEN, TDDPhase.REFACTOR) and self._events[-1].passed

    def _record(self, phase: TDDPhase, command: str, passed: bool) -> None:
        if not isinstance(command, str) or not command.strip():
            raise ValueError("verification command must be non-empty")
        self._events.append(TDDEvent(phase, command, passed))

    def record_red(self, command: str, *, passed: bool) -> None:
        if passed:
            raise ValueError("RED requires an observed failing verification")
        if self._events:
            raise ValueError("RED must be the first TDD phase")
        self._record(TDDPhase.RED, command, passed)

    def record_green(self, command: str, *, passed: bool) -> None:
        if self.phase is not TDDPhase.RED or not passed:
            raise ValueError("GREEN requires RED evidence followed by a passing verification")
        self._record(TDDPhase.GREEN, command, passed)

    def record_refactor(self, command: str, *, passed: bool) -> None:
        if self.phase is not TDDPhase.GREEN or not passed:
            raise ValueError("REFACTOR requires GREEN and a passing verification")
        self._record(TDDPhase.REFACTOR, command, passed)


__all__ = ["TDDEvent", "TDDPhase", "TDDWorkflow"]

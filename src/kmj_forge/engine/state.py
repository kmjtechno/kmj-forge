from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RunState(str, Enum):
    RECEIVE = "RECEIVE"
    CLASSIFY = "CLASSIFY"
    DISCOVER = "DISCOVER"
    IMPLEMENT = "IMPLEMENT"
    TEST = "TEST"
    REVIEW = "REVIEW"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class InvalidTransitionError(RuntimeError):
    pass


_ALLOWED_TRANSITIONS: dict[RunState, frozenset[RunState]] = {
    RunState.RECEIVE: frozenset({RunState.CLASSIFY, RunState.BLOCKED}),
    RunState.CLASSIFY: frozenset({RunState.DISCOVER, RunState.BLOCKED}),
    RunState.DISCOVER: frozenset({RunState.IMPLEMENT, RunState.BLOCKED}),
    RunState.IMPLEMENT: frozenset({RunState.TEST, RunState.BLOCKED}),
    RunState.TEST: frozenset({RunState.REVIEW, RunState.IMPLEMENT, RunState.BLOCKED}),
    RunState.REVIEW: frozenset({RunState.COMPLETE, RunState.IMPLEMENT, RunState.BLOCKED}),
    RunState.COMPLETE: frozenset(),
    RunState.BLOCKED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class RunSnapshot:
    run_id: str
    task_id: str
    state: RunState
    history: tuple[RunState, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id.strip():
            raise ValueError("run_id must be a non-empty string")
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not self.history or self.history[-1] is not self.state:
            raise ValueError("history must end with the current state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "state": self.state.value,
            "history": [state.value for state in self.history],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunSnapshot":
        return cls(
            run_id=data["run_id"],
            task_id=data["task_id"],
            state=RunState(data["state"]),
            history=tuple(RunState(value) for value in data["history"]),
        )


def transition_state(snapshot: RunSnapshot, target: RunState) -> RunSnapshot:
    if not isinstance(target, RunState):
        raise TypeError("target must be a RunState")
    if target not in _ALLOWED_TRANSITIONS[snapshot.state]:
        raise InvalidTransitionError(
            f"illegal run transition: {snapshot.state.value} -> {target.value}"
        )
    return RunSnapshot(
        run_id=snapshot.run_id,
        task_id=snapshot.task_id,
        state=target,
        history=(*snapshot.history, target),
    )

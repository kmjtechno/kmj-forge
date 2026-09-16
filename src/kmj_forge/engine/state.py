from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


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


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError(
            "run_id must be 1-128 characters using only letters, digits, '.', '_' or '-', and start with a letter or digit"
        )
    return run_id


@dataclass(frozen=True, slots=True)
class RunSnapshot:
    run_id: str
    task_id: str
    state: RunState
    history: tuple[RunState, ...]

    def __post_init__(self) -> None:
        validate_run_id(self.run_id)
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

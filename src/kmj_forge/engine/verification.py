from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kmj_forge.protocol import Task


@dataclass(frozen=True, slots=True)
class VerificationPlan:
    task_id: str
    acceptance_criteria: tuple[str, ...]
    commands: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be non-empty")
        if any(not isinstance(item, str) or not item.strip() for item in self.acceptance_criteria):
            raise ValueError("acceptance criteria must be non-empty strings")
        if not self.commands or any(not isinstance(item, str) or not item.strip() for item in self.commands):
            raise ValueError("at least one verification command is required")

    @property
    def is_complete(self) -> bool:
        return bool(self.commands)

    def to_dict(self) -> dict[str, Any]:
        return {"task_id": self.task_id, "acceptance_criteria": list(self.acceptance_criteria),
                "commands": list(self.commands)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationPlan":
        return cls(data["task_id"], tuple(data.get("acceptance_criteria", ())),
                   tuple(data.get("commands", ())))


def build_verification_plan(task: Task, commands: tuple[str, ...]) -> VerificationPlan:
    return VerificationPlan(task.task_id, task.acceptance_criteria, tuple(commands))


__all__ = ["VerificationPlan", "build_verification_plan"]

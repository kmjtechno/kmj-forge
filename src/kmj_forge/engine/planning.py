from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from kmj_forge.protocol.models import Task


@dataclass(frozen=True, slots=True)
class PlanStep:
    step_id: str
    objective: str
    dependencies: tuple[str, ...] = ()
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.step_id.strip() or not self.objective.strip():
            raise ValueError("step_id and objective must be non-empty")
        if self.step_id in self.dependencies:
            raise ValueError("a step cannot depend on itself")

    def to_dict(self) -> dict[str, Any]:
        return {"step_id": self.step_id, "objective": self.objective,
                "dependencies": list(self.dependencies), "completed": self.completed}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlanStep":
        return cls(data["step_id"], data["objective"],
                   tuple(data.get("dependencies", ())), bool(data.get("completed", False)))

@dataclass(frozen=True, slots=True)
class Plan:
    task_id: str
    steps: tuple[PlanStep, ...]
    acceptance_criteria: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.steps:
            raise ValueError("task_id and steps are required")
        ids = [step.step_id for step in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("step ids must be unique")
        known = set(ids)
        if any(dep not in known for step in self.steps for dep in step.dependencies):
            raise ValueError("plan contains an unknown dependency")
        self._validate_acyclic()

    def _validate_acyclic(self) -> None:
        deps = {step.step_id: set(step.dependencies) for step in self.steps}
        remaining = set(deps)
        while remaining:
            ready = {sid for sid in remaining if not (deps[sid] & remaining)}
            if not ready:
                raise ValueError("plan dependency graph must be acyclic")
            remaining -= ready

    def step(self, step_id: str) -> PlanStep:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        raise KeyError(step_id)

    def ready_step_ids(self) -> tuple[str, ...]:
        done = {step.step_id for step in self.steps if step.completed}
        return tuple(step.step_id for step in self.steps
                     if not step.completed and set(step.dependencies) <= done)

    def complete_step(self, step_id: str) -> "Plan":
        step = self.step(step_id)
        done = {item.step_id for item in self.steps if item.completed}
        if not set(step.dependencies) <= done:
            raise ValueError("step dependencies are not complete")
        updated = tuple(replace(item, completed=True) if item.step_id == step_id else item
                        for item in self.steps)
        return replace(self, steps=updated)

    def to_dict(self) -> dict[str, Any]:
        return {"task_id": self.task_id, "steps": [step.to_dict() for step in self.steps],
                "acceptance_criteria": list(self.acceptance_criteria),
                "constraints": list(self.constraints)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Plan":
        return cls(data["task_id"], tuple(PlanStep.from_dict(item) for item in data["steps"]),
                   tuple(data.get("acceptance_criteria", ())),
                   tuple(data.get("constraints", ())))


def _join(items: tuple[str, ...], fallback: str) -> str:
    return "; ".join(items) if items else fallback

def build_plan(task: Task) -> Plan:
    constraints = _join(task.constraints, "declared task constraints")
    acceptance = _join(task.acceptance_criteria, "declared acceptance criteria")
    steps = (
        PlanStep("discover", f"Discover repository context for: {task.objective}"),
        PlanStep("implement", f"Implement: {task.objective}. Constraints: {constraints}", ("discover",)),
        PlanStep("verify", f"Verify acceptance criteria: {acceptance}", ("implement",)),
        PlanStep("review", "Review evidence and completion gates", ("verify",)),
    )
    return Plan(task.task_id, steps, task.acceptance_criteria, task.constraints)

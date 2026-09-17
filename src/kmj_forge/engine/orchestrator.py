from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TaskSpec:
    """A manager-owned task description; execution remains outside this boundary."""

    task_id: str
    dependencies: tuple[str, ...] = ()
    mutation_allowed: bool = False


@dataclass(frozen=True)
class SubagentAssignment:
    """A side-effect-free assignment of one ready task to one subagent."""

    subagent_id: str
    task_id: str
    mutation_allowed: bool = False


class Manager:
    """Deterministically select and assign dependency-ready tasks without executing work."""

    def ready_tasks(
        self,
        *,
        tasks: Iterable[TaskSpec],
        completed_task_ids: frozenset[str],
    ) -> tuple[TaskSpec, ...]:
        task_list = tuple(tasks)
        task_ids = tuple(task.task_id for task in task_list)

        if any(not task_id.strip() for task_id in task_ids):
            raise ValueError("task_id must be non-empty")
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("task_id values must be unique")

        known_ids = set(task_ids) | set(completed_task_ids)
        for task in task_list:
            if any(not dependency.strip() for dependency in task.dependencies):
                raise ValueError("dependencies must be non-empty")
            if task.task_id in task.dependencies:
                raise ValueError("task cannot depend on itself")
            unknown = set(task.dependencies) - known_ids
            if unknown:
                raise ValueError("dependencies must reference known tasks")

        ready = (
            task
            for task in task_list
            if task.task_id not in completed_task_ids
            and set(task.dependencies).issubset(completed_task_ids)
        )
        return tuple(sorted(ready, key=lambda task: task.task_id))

    def assign_subagents(
        self,
        *,
        tasks: Iterable[TaskSpec],
        completed_task_ids: frozenset[str],
        subagent_ids: Iterable[str],
    ) -> tuple[SubagentAssignment, ...]:
        """Assign ready tasks deterministically without starting or mutating any work."""

        agent_ids = tuple(subagent_ids)
        if any(not agent_id.strip() for agent_id in agent_ids):
            raise ValueError("subagent_id must be non-empty")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("subagent_id values must be unique")

        ready = self.ready_tasks(tasks=tasks, completed_task_ids=completed_task_ids)
        ordered_agents = tuple(sorted(agent_ids))
        return tuple(
            SubagentAssignment(subagent_id=agent_id, task_id=task.task_id)
            for agent_id, task in zip(ordered_agents, ready)
        )

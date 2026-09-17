from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
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


@dataclass(frozen=True)
class WorktreeAssignment:
    """A deterministic worktree plan; creating the worktree remains outside this boundary."""

    subagent_id: str
    task_id: str
    path: str
    mutation_allowed: bool = False


@dataclass(frozen=True)
class ParallelExecutionPlan:
    """A validated parallel batch plan; starting workers remains outside this boundary."""

    worktrees: tuple[WorktreeAssignment, ...]
    mutation_allowed: bool = False


def _safe_component(value: str, *, field: str) -> str:
    if not value.strip():
        raise ValueError(f"{field} must be non-empty")
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError(f"{field} must be a safe path component")
    return value


class Manager:
    """Deterministically plan isolated orchestration without executing work."""

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

    def assign_worktrees(
        self,
        *,
        assignments: Iterable[SubagentAssignment],
        root: str,
    ) -> tuple[WorktreeAssignment, ...]:
        """Plan one unique isolated worktree per assignment without touching the filesystem."""

        if not root.strip():
            raise ValueError("root must be non-empty")
        assignment_list = tuple(assignments)
        task_ids = tuple(assignment.task_id for assignment in assignment_list)
        agent_ids = tuple(assignment.subagent_id for assignment in assignment_list)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("task assignments must be unique")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("subagent assignments must be unique")

        for assignment in assignment_list:
            _safe_component(assignment.task_id, field="task_id")
            _safe_component(assignment.subagent_id, field="subagent_id")

        ordered = sorted(assignment_list, key=lambda item: (item.task_id, item.subagent_id))
        root_path = PurePosixPath(root)
        return tuple(
            WorktreeAssignment(
                subagent_id=assignment.subagent_id,
                task_id=assignment.task_id,
                path=str(root_path / f"{assignment.task_id}--{assignment.subagent_id}"),
            )
            for assignment in ordered
        )

    def plan_parallel_execution(
        self,
        *,
        worktrees: Iterable[WorktreeAssignment],
    ) -> ParallelExecutionPlan:
        """Validate a collision-free parallel batch without starting workers or mutating worktrees."""

        worktree_list = tuple(worktrees)
        task_ids = tuple(item.task_id for item in worktree_list)
        agent_ids = tuple(item.subagent_id for item in worktree_list)
        paths = tuple(item.path for item in worktree_list)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("parallel task assignments must be unique")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("parallel subagent assignments must be unique")
        if len(set(paths)) != len(paths):
            raise ValueError("parallel worktree paths must be unique")
        if any(not path.strip() for path in paths):
            raise ValueError("parallel worktree paths must be non-empty")

        ordered = tuple(sorted(worktree_list, key=lambda item: (item.task_id, item.subagent_id, item.path)))
        return ParallelExecutionPlan(worktrees=ordered)

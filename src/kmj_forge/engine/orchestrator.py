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


@dataclass(frozen=True)
class IntegrationPlan:
    """A dependency-ordered integration plan; merging remains outside this boundary."""

    worktrees: tuple[WorktreeAssignment, ...]
    required_checks: tuple[str, ...] = ("targeted_tests", "conflict_resolution", "full_regression")
    mutation_allowed: bool = False


@dataclass(frozen=True)
class CrossReviewAssignment:
    """A task authored by one subagent and reviewed by a distinct peer."""

    task_id: str
    author_subagent_id: str
    reviewer_subagent_id: str
    worktree_path: str
    mutation_allowed: bool = False


@dataclass(frozen=True)
class CrossReviewPlan:
    """A deterministic peer-review plan; review execution remains outside this boundary."""

    assignments: tuple[CrossReviewAssignment, ...]
    required_checks: tuple[str, ...] = ("requirements_review", "architecture_review", "diff_review", "regression_analysis")
    mutation_allowed: bool = False


def _safe_component(value: str, *, field: str) -> str:
    if not value.strip():
        raise ValueError(f"{field} must be non-empty")
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError(f"{field} must be a safe path component")
    return value


class Manager:
    """Deterministically plan isolated orchestration without executing work."""

    def ready_tasks(self, *, tasks: Iterable[TaskSpec], completed_task_ids: frozenset[str]) -> tuple[TaskSpec, ...]:
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
            if set(task.dependencies) - known_ids:
                raise ValueError("dependencies must reference known tasks")
        ready = (task for task in task_list if task.task_id not in completed_task_ids and set(task.dependencies).issubset(completed_task_ids))
        return tuple(sorted(ready, key=lambda task: task.task_id))

    def assign_subagents(self, *, tasks: Iterable[TaskSpec], completed_task_ids: frozenset[str], subagent_ids: Iterable[str]) -> tuple[SubagentAssignment, ...]:
        agent_ids = tuple(subagent_ids)
        if any(not agent_id.strip() for agent_id in agent_ids):
            raise ValueError("subagent_id must be non-empty")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("subagent_id values must be unique")
        ready = self.ready_tasks(tasks=tasks, completed_task_ids=completed_task_ids)
        return tuple(SubagentAssignment(subagent_id=agent_id, task_id=task.task_id) for agent_id, task in zip(sorted(agent_ids), ready))

    def assign_worktrees(self, *, assignments: Iterable[SubagentAssignment], root: str) -> tuple[WorktreeAssignment, ...]:
        if not root.strip():
            raise ValueError("root must be non-empty")
        assignment_list = tuple(assignments)
        task_ids = tuple(a.task_id for a in assignment_list)
        agent_ids = tuple(a.subagent_id for a in assignment_list)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("task assignments must be unique")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("subagent assignments must be unique")
        for assignment in assignment_list:
            _safe_component(assignment.task_id, field="task_id")
            _safe_component(assignment.subagent_id, field="subagent_id")
        root_path = PurePosixPath(root)
        return tuple(WorktreeAssignment(a.subagent_id, a.task_id, str(root_path / f"{a.task_id}--{a.subagent_id}")) for a in sorted(assignment_list, key=lambda item: (item.task_id, item.subagent_id)))

    def plan_parallel_execution(self, *, worktrees: Iterable[WorktreeAssignment]) -> ParallelExecutionPlan:
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
        return ParallelExecutionPlan(worktrees=tuple(sorted(worktree_list, key=lambda item: (item.task_id, item.subagent_id, item.path))))

    def plan_integration(self, *, worktrees: Iterable[WorktreeAssignment], dependency_order: Iterable[str]) -> IntegrationPlan:
        """Validate dependency-ordered integration without merging or mutating worktrees."""
        worktree_list = tuple(worktrees)
        order = tuple(dependency_order)
        task_ids = tuple(item.task_id for item in worktree_list)
        agent_ids = tuple(item.subagent_id for item in worktree_list)
        paths = tuple(item.path for item in worktree_list)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("integration task assignments must be unique")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("integration subagent assignments must be unique")
        if len(set(paths)) != len(paths):
            raise ValueError("integration worktree paths must be unique")
        if any(not path.strip() for path in paths):
            raise ValueError("integration worktree paths must be non-empty")
        if len(set(order)) != len(order) or set(order) != set(task_ids) or len(order) != len(task_ids):
            raise ValueError("dependency_order must match integration tasks exactly")
        by_task = {item.task_id: item for item in worktree_list}
        return IntegrationPlan(worktrees=tuple(by_task[task_id] for task_id in order))

    def plan_cross_review(self, *, worktrees: Iterable[WorktreeAssignment]) -> CrossReviewPlan:
        """Assign each worktree to a distinct peer reviewer without executing review actions."""
        worktree_list = tuple(sorted(worktrees, key=lambda item: (item.task_id, item.subagent_id, item.path)))
        if len(worktree_list) < 2:
            raise ValueError("cross-review requires at least two distinct subagents")
        task_ids = tuple(item.task_id for item in worktree_list)
        agent_ids = tuple(item.subagent_id for item in worktree_list)
        paths = tuple(item.path for item in worktree_list)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("cross-review task assignments must be unique")
        if len(set(agent_ids)) != len(agent_ids):
            raise ValueError("cross-review subagent assignments must be unique")
        if len(set(paths)) != len(paths) or any(not path.strip() for path in paths):
            raise ValueError("cross-review worktree paths must be unique and non-empty")
        assignments = tuple(
            CrossReviewAssignment(
                task_id=item.task_id,
                author_subagent_id=item.subagent_id,
                reviewer_subagent_id=worktree_list[(index + 1) % len(worktree_list)].subagent_id,
                worktree_path=item.path,
            )
            for index, item in enumerate(worktree_list)
        )
        return CrossReviewPlan(assignments=assignments)

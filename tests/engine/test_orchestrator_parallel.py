import unittest

from kmj_forge.engine.orchestrator import Manager, WorktreeAssignment, ParallelExecutionPlan


class ParallelExecutionPlanTests(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_plans_parallel_batch_deterministically(self):
        worktrees = (
            WorktreeAssignment("worker-b", "review", ".kmj/worktrees/review--worker-b"),
            WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),
        )
        plan = self.manager.plan_parallel_execution(worktrees=worktrees)
        self.assertEqual(
            plan,
            ParallelExecutionPlan(
                worktrees=(
                    WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),
                    WorktreeAssignment("worker-b", "review", ".kmj/worktrees/review--worker-b"),
                )
            ),
        )

    def test_duplicate_task_or_agent_fails_closed(self):
        cases = (
            (
                WorktreeAssignment("worker-a", "build", ".kmj/worktrees/a"),
                WorktreeAssignment("worker-b", "build", ".kmj/worktrees/b"),
            ),
            (
                WorktreeAssignment("worker-a", "build", ".kmj/worktrees/a"),
                WorktreeAssignment("worker-a", "review", ".kmj/worktrees/b"),
            ),
        )
        for worktrees in cases:
            with self.subTest(worktrees=worktrees):
                with self.assertRaises(ValueError):
                    self.manager.plan_parallel_execution(worktrees=worktrees)

    def test_duplicate_worktree_path_fails_closed(self):
        with self.assertRaises(ValueError):
            self.manager.plan_parallel_execution(
                worktrees=(
                    WorktreeAssignment("worker-a", "build", ".kmj/worktrees/shared"),
                    WorktreeAssignment("worker-b", "review", ".kmj/worktrees/shared"),
                )
            )

    def test_parallel_plan_never_authorizes_mutation(self):
        plan = self.manager.plan_parallel_execution(
            worktrees=(WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),)
        )
        self.assertFalse(plan.mutation_allowed)


if __name__ == "__main__":
    unittest.main()

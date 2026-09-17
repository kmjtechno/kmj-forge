import unittest

from kmj_forge.engine.orchestrator import IntegrationPlan, Manager, WorktreeAssignment


class IntegrationPlanTests(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_plans_dependency_ordered_integration_deterministically(self):
        worktrees = (
            WorktreeAssignment("worker-b", "review", ".kmj/worktrees/review--worker-b"),
            WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),
        )
        plan = self.manager.plan_integration(
            worktrees=worktrees,
            dependency_order=("build", "review"),
        )
        self.assertEqual(
            plan,
            IntegrationPlan(
                worktrees=(
                    WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),
                    WorktreeAssignment("worker-b", "review", ".kmj/worktrees/review--worker-b"),
                ),
                required_checks=("targeted_tests", "conflict_resolution", "full_regression"),
            ),
        )

    def test_dependency_order_must_match_worktree_tasks_exactly(self):
        worktrees = (WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),)
        for dependency_order in ((), ("build", "unknown"), ("build", "build")):
            with self.subTest(dependency_order=dependency_order):
                with self.assertRaises(ValueError):
                    self.manager.plan_integration(worktrees=worktrees, dependency_order=dependency_order)

    def test_duplicate_agent_or_path_fails_closed(self):
        cases = (
            (
                WorktreeAssignment("worker-a", "build", ".kmj/worktrees/a"),
                WorktreeAssignment("worker-a", "review", ".kmj/worktrees/b"),
            ),
            (
                WorktreeAssignment("worker-a", "build", ".kmj/worktrees/shared"),
                WorktreeAssignment("worker-b", "review", ".kmj/worktrees/shared"),
            ),
        )
        for worktrees in cases:
            with self.subTest(worktrees=worktrees):
                with self.assertRaises(ValueError):
                    self.manager.plan_integration(
                        worktrees=worktrees,
                        dependency_order=tuple(item.task_id for item in worktrees),
                    )

    def test_integration_plan_never_authorizes_mutation(self):
        plan = self.manager.plan_integration(
            worktrees=(WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),),
            dependency_order=("build",),
        )
        self.assertFalse(plan.mutation_allowed)


if __name__ == "__main__":
    unittest.main()

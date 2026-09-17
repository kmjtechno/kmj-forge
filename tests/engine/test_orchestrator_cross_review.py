import unittest

from kmj_forge.engine.orchestrator import CrossReviewPlan, Manager, WorktreeAssignment


class CrossReviewPlanTests(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_assigns_each_task_to_a_distinct_reviewer_deterministically(self):
        worktrees = (
            WorktreeAssignment("worker-b", "review", ".kmj/worktrees/review--worker-b"),
            WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),
        )
        plan = self.manager.plan_cross_review(worktrees=worktrees)
        self.assertEqual(tuple((item.task_id, item.author_subagent_id, item.reviewer_subagent_id) for item in plan.assignments), (("build", "worker-a", "worker-b"), ("review", "worker-b", "worker-a")))
        self.assertEqual(plan.required_checks, ("requirements_review", "architecture_review", "diff_review", "regression_analysis"))

    def test_single_worktree_cannot_cross_review_itself(self):
        with self.assertRaises(ValueError):
            self.manager.plan_cross_review(worktrees=(WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),))

    def test_duplicate_task_agent_or_path_fails_closed(self):
        cases = (
            (WorktreeAssignment("worker-a", "build", ".kmj/worktrees/a"), WorktreeAssignment("worker-b", "build", ".kmj/worktrees/b")),
            (WorktreeAssignment("worker-a", "build", ".kmj/worktrees/a"), WorktreeAssignment("worker-a", "review", ".kmj/worktrees/b")),
            (WorktreeAssignment("worker-a", "build", ".kmj/worktrees/shared"), WorktreeAssignment("worker-b", "review", ".kmj/worktrees/shared")),
        )
        for worktrees in cases:
            with self.subTest(worktrees=worktrees):
                with self.assertRaises(ValueError):
                    self.manager.plan_cross_review(worktrees=worktrees)

    def test_cross_review_plan_never_authorizes_mutation(self):
        plan = self.manager.plan_cross_review(worktrees=(WorktreeAssignment("worker-a", "build", ".kmj/worktrees/a"), WorktreeAssignment("worker-b", "review", ".kmj/worktrees/b")))
        self.assertIsInstance(plan, CrossReviewPlan)
        self.assertFalse(plan.mutation_allowed)
        self.assertTrue(all(not assignment.mutation_allowed for assignment in plan.assignments))


if __name__ == "__main__":
    unittest.main()

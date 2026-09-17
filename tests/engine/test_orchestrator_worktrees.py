import unittest

from kmj_forge.engine.orchestrator import Manager, SubagentAssignment, WorktreeAssignment


class WorktreeAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_assigns_unique_deterministic_worktrees(self):
        assignments = (
            SubagentAssignment(subagent_id="worker-b", task_id="review"),
            SubagentAssignment(subagent_id="worker-a", task_id="build"),
        )
        worktrees = self.manager.assign_worktrees(assignments=assignments, root=".kmj/worktrees")
        self.assertEqual(
            worktrees,
            (
                WorktreeAssignment("worker-a", "build", ".kmj/worktrees/build--worker-a"),
                WorktreeAssignment("worker-b", "review", ".kmj/worktrees/review--worker-b"),
            ),
        )

    def test_duplicate_task_assignment_fails_closed(self):
        with self.assertRaises(ValueError):
            self.manager.assign_worktrees(
                assignments=(
                    SubagentAssignment("worker-a", "build"),
                    SubagentAssignment("worker-b", "build"),
                ),
                root=".kmj/worktrees",
            )

    def test_blank_or_unsafe_identifiers_fail_closed(self):
        for assignment in (
            SubagentAssignment("worker-a", " "),
            SubagentAssignment("../worker", "build"),
        ):
            with self.subTest(assignment=assignment):
                with self.assertRaises(ValueError):
                    self.manager.assign_worktrees(assignments=(assignment,), root=".kmj/worktrees")

    def test_blank_root_fails_closed(self):
        with self.assertRaises(ValueError):
            self.manager.assign_worktrees(
                assignments=(SubagentAssignment("worker-a", "build"),),
                root=" ",
            )

    def test_worktree_assignment_never_authorizes_mutation(self):
        assignment = self.manager.assign_worktrees(
            assignments=(SubagentAssignment("worker-a", "build"),),
            root=".kmj/worktrees",
        )[0]
        self.assertFalse(assignment.mutation_allowed)


if __name__ == "__main__":
    unittest.main()

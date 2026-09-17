import unittest

from kmj_forge.engine.orchestrator import Manager, SubagentAssignment, TaskSpec


class SubagentAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_assigns_ready_tasks_deterministically_to_distinct_subagents(self):
        tasks = (
            TaskSpec(task_id="review"),
            TaskSpec(task_id="build"),
            TaskSpec(task_id="integrate", dependencies=("build", "review")),
        )
        assignments = self.manager.assign_subagents(
            tasks=tasks,
            completed_task_ids=frozenset(),
            subagent_ids=("worker-b", "worker-a"),
        )
        self.assertEqual(
            assignments,
            (
                SubagentAssignment(subagent_id="worker-a", task_id="build"),
                SubagentAssignment(subagent_id="worker-b", task_id="review"),
            ),
        )

    def test_assignment_never_authorizes_mutation(self):
        assignment = self.manager.assign_subagents(
            tasks=(TaskSpec(task_id="build"),),
            completed_task_ids=frozenset(),
            subagent_ids=("worker-a",),
        )[0]
        self.assertFalse(assignment.mutation_allowed)

    def test_duplicate_subagent_ids_fail_closed(self):
        with self.assertRaises(ValueError):
            self.manager.assign_subagents(
                tasks=(TaskSpec(task_id="build"),),
                completed_task_ids=frozenset(),
                subagent_ids=("worker-a", "worker-a"),
            )

    def test_blank_subagent_id_fails_closed(self):
        with self.assertRaises(ValueError):
            self.manager.assign_subagents(
                tasks=(TaskSpec(task_id="build"),),
                completed_task_ids=frozenset(),
                subagent_ids=(" ",),
            )

    def test_excess_ready_tasks_remain_unassigned(self):
        assignments = self.manager.assign_subagents(
            tasks=(TaskSpec(task_id="a"), TaskSpec(task_id="b")),
            completed_task_ids=frozenset(),
            subagent_ids=("worker-a",),
        )
        self.assertEqual(assignments, (SubagentAssignment(subagent_id="worker-a", task_id="a"),))


if __name__ == "__main__":
    unittest.main()

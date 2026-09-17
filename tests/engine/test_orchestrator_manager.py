import unittest

from kmj_forge.engine.orchestrator import Manager, TaskSpec


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_ready_tasks_respect_dependencies_and_are_deterministic(self):
        tasks = (
            TaskSpec(task_id="integrate", dependencies=("build", "review")),
            TaskSpec(task_id="review"),
            TaskSpec(task_id="build"),
        )
        ready = self.manager.ready_tasks(tasks=tasks, completed_task_ids=frozenset())
        self.assertEqual(tuple(task.task_id for task in ready), ("build", "review"))

    def test_completed_dependencies_unlock_task(self):
        tasks = (TaskSpec(task_id="integrate", dependencies=("build",)),)
        ready = self.manager.ready_tasks(tasks=tasks, completed_task_ids=frozenset({"build"}))
        self.assertEqual(tuple(task.task_id for task in ready), ("integrate",))

    def test_duplicate_task_ids_fail_closed(self):
        tasks = (TaskSpec(task_id="build"), TaskSpec(task_id="build"))
        with self.assertRaises(ValueError):
            self.manager.ready_tasks(tasks=tasks, completed_task_ids=frozenset())

    def test_unknown_dependency_fails_closed(self):
        tasks = (TaskSpec(task_id="integrate", dependencies=("missing",)),)
        with self.assertRaises(ValueError):
            self.manager.ready_tasks(tasks=tasks, completed_task_ids=frozenset())

    def test_manager_only_plans_and_never_authorizes_mutation(self):
        task = TaskSpec(task_id="build")
        self.assertFalse(task.mutation_allowed)


if __name__ == "__main__":
    unittest.main()

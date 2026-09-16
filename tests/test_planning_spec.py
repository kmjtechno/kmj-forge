import unittest

from kmj_forge.engine.planning import build_plan
from kmj_forge.protocol.models import Task


class PlanningSpecTests(unittest.TestCase):
    def test_plan_carries_acceptance_and_constraints_into_executable_steps(self):
        task = Task(
            task_id="task-42",
            objective="Add safe login",
            acceptance_criteria=("invalid password is rejected", "valid login succeeds"),
            constraints=("do not change public API",),
        )

        plan = build_plan(task)

        self.assertEqual(plan.task_id, task.task_id)
        self.assertEqual(plan.acceptance_criteria, task.acceptance_criteria)
        self.assertEqual(plan.constraints, task.constraints)
        self.assertIn("invalid password is rejected", plan.step("verify").objective)
        self.assertIn("do not change public API", plan.step("implement").objective)

    def test_plan_round_trip_preserves_specification(self):
        task = Task("task-7", "Refactor parser", ("tests pass",), ("no new dependency",))
        plan = build_plan(task)

        restored = type(plan).from_dict(plan.to_dict())

        self.assertEqual(restored, plan)
        self.assertEqual(restored.step("discover").step_id, "discover")


if __name__ == "__main__":
    unittest.main()

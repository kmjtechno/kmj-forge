import unittest

from kmj_forge.engine.planning import Plan, PlanStep, build_plan
from kmj_forge.protocol.models import Task


class PlanningEngineTests(unittest.TestCase):
    def test_build_plan_creates_dependency_ordered_resumable_dag(self):
        task = Task(
            task_id="phase03",
            objective="Implement planning engine with tests and verification",
            acceptance_criteria=("tests pass", "plan is resumable"),
            constraints=("free-only",),
        )
        plan = build_plan(task)
        self.assertEqual(plan.task_id, "phase03")
        self.assertGreaterEqual(len(plan.steps), 3)
        self.assertEqual(plan.ready_step_ids(), (plan.steps[0].step_id,))
        completed = plan.complete_step(plan.steps[0].step_id)
        self.assertNotEqual(completed, plan)
        self.assertTrue(completed.steps[0].completed)
        self.assertEqual(Plan.from_dict(completed.to_dict()), completed)

    def test_plan_rejects_unknown_and_cyclic_dependencies(self):
        with self.assertRaises(ValueError):
            Plan(task_id="t", steps=(PlanStep("a", "A", ("missing",)),))
        with self.assertRaises(ValueError):
            Plan(task_id="t", steps=(
                PlanStep("a", "A", ("b",)),
                PlanStep("b", "B", ("a",)),
            ))

    def test_complete_step_requires_dependencies_first(self):
        plan = Plan(task_id="t", steps=(
            PlanStep("discover", "Discover"),
            PlanStep("implement", "Implement", ("discover",)),
        ))
        with self.assertRaises(ValueError):
            plan.complete_step("implement")
        with self.assertRaises(KeyError):
            plan.complete_step("unknown")


if __name__ == "__main__":
    unittest.main()

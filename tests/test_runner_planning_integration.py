import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine.runner import ForgeRunner
from kmj_forge.protocol.models import Task


class RunnerPlanningIntegrationTests(unittest.TestCase):
    def test_runner_starts_with_persisted_executable_plan_and_resumes_it(self):
        task = Task("task-plan", "Add safe login", ("valid login succeeds",), ("no API break",))
        with tempfile.TemporaryDirectory() as temp:
            state_dir = Path(temp)
            runner = ForgeRunner.start(task, state_dir=state_dir, run_id="plan-run")

            self.assertEqual(runner.plan.task_id, task.task_id)
            self.assertEqual(runner.plan.ready_step_ids(), ("discover",))
            runner.complete_plan_step("discover")

            restored = ForgeRunner.load(state_dir, "plan-run")
            self.assertTrue(restored.plan.step("discover").completed)
            self.assertEqual(restored.plan.ready_step_ids(), ("implement",))


if __name__ == "__main__":
    unittest.main()

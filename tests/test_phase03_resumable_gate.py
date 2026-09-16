import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine.runner import ForgeRunner
from kmj_forge.protocol.models import Task


class Phase03ResumableGateTests(unittest.TestCase):
    def test_complex_task_plan_preserves_spec_and_verification_after_resume(self):
        task = Task(
            "complex-1",
            "Add authenticated API with migration and regression coverage",
            ("API accepts valid token", "regression suite passes"),
            ("preserve public API", "no paid dependency"),
        )
        with tempfile.TemporaryDirectory() as temp:
            state_dir = Path(temp)
            runner = ForgeRunner.start(task, state_dir=state_dir, run_id="complex-run")
            self.assertTrue(runner.plan.is_executable())
            self.assertEqual(runner.plan.verification_criteria(), task.acceptance_criteria)
            runner.complete_plan_step("discover")

            restored = ForgeRunner.load(state_dir, "complex-run")
            self.assertTrue(restored.plan.is_executable())
            self.assertEqual(restored.plan.verification_criteria(), task.acceptance_criteria)
            self.assertEqual(restored.plan.ready_step_ids(), ("implement",))


if __name__ == "__main__":
    unittest.main()

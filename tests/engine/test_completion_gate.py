import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine.evidence import VerificationRequiredError
from kmj_forge.engine.runner import ForgeRunner
from kmj_forge.engine.state import RunState
from kmj_forge.engine.verification import VerificationPlan
from kmj_forge.protocol import EvidenceRecord, Task


class CompletionGateTests(unittest.TestCase):
    def _review_runner(self, root):
        task = Task("task-gate", "verify completion", acceptance_criteria=("tests pass",))
        runner = ForgeRunner.start(task, state_dir=Path(root), run_id="gate")
        for state in (RunState.CLASSIFY, RunState.DISCOVER, RunState.IMPLEMENT, RunState.TEST, RunState.REVIEW):
            runner.transition(state)
        for step in runner.plan.steps:
            runner.complete_plan_step(step.step_id)
        runner.set_verification_plan(VerificationPlan(task.task_id, task.acceptance_criteria, ("unit", "regression")))
        return runner

    def test_completion_requires_every_planned_verification_command(self):
        with tempfile.TemporaryDirectory() as root:
            runner = self._review_runner(root)
            runner.record_evidence(EvidenceRecord("e1", runner.task.task_id, "verification", "PASS", "2026-09-17T00:00:00Z", command="unit"))
            with self.assertRaisesRegex(VerificationRequiredError, "missing verification evidence: regression"):
                runner.complete()
            self.assertEqual(runner.snapshot.state, RunState.REVIEW)

    def test_complete_succeeds_and_verification_plan_survives_reload(self):
        with tempfile.TemporaryDirectory() as root:
            runner = self._review_runner(root)
            for index, command in enumerate(("unit", "regression"), 1):
                runner.record_evidence(EvidenceRecord(f"e{index}", runner.task.task_id, "verification", "PASS", "2026-09-17T00:00:00Z", command=command))
            loaded = ForgeRunner.load(Path(root), "gate")
            self.assertEqual(loaded.verification_plan.commands, ("unit", "regression"))
            loaded.complete()
            self.assertEqual(loaded.snapshot.state, RunState.COMPLETE)


if __name__ == "__main__":
    unittest.main()

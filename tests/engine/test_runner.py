import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine import (
    ApprovalRequiredError,
    ForgeRunner,
    RunState,
    VerificationRequiredError,
)
from kmj_forge.protocol import EvidenceRecord, Task


REVIEW_PATH = (
    RunState.CLASSIFY,
    RunState.DISCOVER,
    RunState.IMPLEMENT,
    RunState.TEST,
    RunState.REVIEW,
)


def evidence(evidence_id: str, status: str) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        task_id="task-1",
        kind="test",
        status=status,
        timestamp="2026-09-16T00:00:00Z",
        command="python -m unittest",
    )


class ForgeRunnerTests(unittest.TestCase):
    def test_runner_persists_and_recovers_interrupted_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ForgeRunner.start(
                Task(task_id="task-1", objective="Fix the failing test"),
                state_dir=Path(tmp),
                run_id="run-1",
            )
            runner.transition(RunState.CLASSIFY)
            runner.transition(RunState.DISCOVER)
            runner.approve("write")
            runner.record_evidence(evidence("e1", "FAIL"))

            recovered = ForgeRunner.load(Path(tmp), "run-1")

            self.assertEqual(recovered.snapshot.state, RunState.DISCOVER)
            self.assertEqual(recovered.task.task_id, "task-1")
            self.assertEqual(recovered.evidence[-1].status, "FAIL")
            self.assertIn("write", recovered.approvals)

    def test_write_terminal_and_git_require_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ForgeRunner.start(Task("task-1", "change code"), state_dir=Path(tmp), run_id="run-2")
            runner.require_action("read")
            runner.require_action("test")

            for action in ("write", "terminal", "git"):
                with self.subTest(action=action):
                    with self.assertRaises(ApprovalRequiredError):
                        runner.require_action(action)

            runner.approve("write")
            runner.require_action("write")
            with self.assertRaises(ValueError):
                runner.require_action("unclassified")

    def test_complete_requires_latest_verification_to_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ForgeRunner.start(Task("task-1", "fix"), state_dir=Path(tmp), run_id="run-3")
            for state in REVIEW_PATH:
                runner.transition(state)

            with self.assertRaises(VerificationRequiredError):
                runner.complete()

            runner.record_evidence(evidence("e-fail", "FAIL"))
            with self.assertRaises(VerificationRequiredError):
                runner.complete()

            runner.record_evidence(evidence("e-pass", "PASS"))
            runner.complete()
            self.assertEqual(runner.snapshot.state, RunState.COMPLETE)

            recovered = ForgeRunner.load(Path(tmp), "run-3")
            self.assertEqual(recovered.snapshot.state, RunState.COMPLETE)

    def test_block_records_reason_and_terminates_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ForgeRunner.start(Task("task-1", "fix"), state_dir=Path(tmp), run_id="run-4")
            runner.block("missing dependency")

            self.assertEqual(runner.snapshot.state, RunState.BLOCKED)
            self.assertEqual(runner.evidence[-1].kind, "block")
            self.assertEqual(runner.evidence[-1].details["reason"], "missing dependency")


if __name__ == "__main__":
    unittest.main()

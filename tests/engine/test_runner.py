import sys
import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine import (
    ApprovalRequiredError,
    ForgeRunner,
    InvalidTransitionError,
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

    def test_block_on_terminal_run_is_atomic_and_does_not_add_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            runner = ForgeRunner.start(Task("task-1", "fix"), state_dir=state_dir, run_id="run-5")
            for state in REVIEW_PATH:
                runner.transition(state)
            runner.record_evidence(evidence("e-pass", "PASS"))
            runner.complete()
            before = tuple(runner.evidence)

            with self.assertRaises(InvalidTransitionError):
                runner.block("too late")

            self.assertEqual(tuple(runner.evidence), before)
            recovered = ForgeRunner.load(state_dir, "run-5")
            self.assertEqual(recovered.snapshot.state, RunState.COMPLETE)
            self.assertEqual(tuple(recovered.evidence), before)

    def test_verification_execution_requires_terminal_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ForgeRunner.start(Task("task-1", "verify"), state_dir=Path(tmp), run_id="run-6")
            with self.assertRaises(ApprovalRequiredError):
                runner.run_verification((sys.executable, "-c", "print('ok')"))

    def test_verification_execution_records_pass_and_fail_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            runner = ForgeRunner.start(Task("task-1", "verify"), state_dir=state_dir, run_id="run-7")
            runner.approve("terminal")

            passed = runner.run_verification((sys.executable, "-c", "print('ok')"), cwd=state_dir)
            failed = runner.run_verification((sys.executable, "-c", "import sys; print('bad'); sys.exit(3)"), cwd=state_dir)

            self.assertEqual(passed.status, "PASS")
            self.assertEqual(passed.details["exit_code"], 0)
            self.assertEqual(passed.details["argv"], [sys.executable, "-c", "print('ok')"])
            self.assertIn("ok", passed.details["stdout"])
            self.assertEqual(failed.status, "FAIL")
            self.assertEqual(failed.details["exit_code"], 3)
            self.assertIn("bad", failed.details["stdout"])

            recovered = ForgeRunner.load(state_dir, "run-7")
            self.assertEqual(recovered.evidence[-2].status, "PASS")
            self.assertEqual(recovered.evidence[-1].status, "FAIL")

    def test_run_id_cannot_escape_state_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp)
            for unsafe in ("../escape", "nested/run", r"nested\run", ".."):
                with self.subTest(run_id=unsafe):
                    with self.assertRaises(ValueError):
                        ForgeRunner.start(Task("task-1", "fix"), state_dir=state_dir, run_id=unsafe)
                    with self.assertRaises(ValueError):
                        ForgeRunner.load(state_dir, unsafe)

    def test_retry_invalidates_old_pass_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ForgeRunner.start(Task("task-1", "fix"), state_dir=Path(tmp), run_id="run-8")
            for state in REVIEW_PATH:
                runner.transition(state)
            runner.record_evidence(evidence("e-pass-old", "PASS"))

            runner.transition(RunState.IMPLEMENT)
            runner.transition(RunState.TEST)
            runner.transition(RunState.REVIEW)

            with self.assertRaises(VerificationRequiredError):
                runner.complete()
            self.assertEqual(runner.evidence[-1].kind, "verification")
            self.assertEqual(runner.evidence[-1].status, "STALE")

            runner.record_evidence(evidence("e-pass-new", "PASS"))
            runner.complete()
            self.assertEqual(runner.snapshot.state, RunState.COMPLETE)


if __name__ == "__main__":
    unittest.main()

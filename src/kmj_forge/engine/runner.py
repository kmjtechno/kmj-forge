from __future__ import annotations

import json
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from kmj_forge.protocol import EvidenceRecord, Task

from .evidence import VerificationRequiredError, latest_verification, require_completion_evidence
from .state import RunSnapshot, RunState, transition_state, validate_run_id


class ApprovalRequiredError(PermissionError):
    pass


AUTO_APPROVED_ACTIONS = frozenset({"read", "test"})
PROTECTED_ACTIONS = frozenset({"write", "terminal", "git"})
KNOWN_ACTIONS = AUTO_APPROVED_ACTIONS | PROTECTED_ACTIONS
OUTPUT_LIMIT = 20_000
PASS_STATUSES = frozenset({"PASS", "SUCCESS", "OK"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ForgeRunner:
    def __init__(
        self,
        *,
        task: Task,
        snapshot: RunSnapshot,
        state_dir: Path,
        evidence: list[EvidenceRecord] | None = None,
        approvals: set[str] | None = None,
    ) -> None:
        self.task = task
        self.snapshot = snapshot
        self.state_dir = Path(state_dir)
        self.evidence = list(evidence or [])
        self.approvals = set(approvals or set())

    @property
    def state_path(self) -> Path:
        return self.state_dir / f"{self.snapshot.run_id}.json"

    @classmethod
    def start(
        cls,
        task: Task,
        *,
        state_dir: Path,
        run_id: str | None = None,
    ) -> "ForgeRunner":
        resolved_run_id = validate_run_id(run_id or uuid.uuid4().hex)
        snapshot = RunSnapshot(
            run_id=resolved_run_id,
            task_id=task.task_id,
            state=RunState.RECEIVE,
            history=(RunState.RECEIVE,),
        )
        runner = cls(task=task, snapshot=snapshot, state_dir=Path(state_dir))
        if runner.state_path.exists():
            raise FileExistsError(f"run already exists: {resolved_run_id}")
        runner._persist()
        return runner

    @classmethod
    def load(cls, state_dir: Path, run_id: str) -> "ForgeRunner":
        safe_run_id = validate_run_id(run_id)
        path = Path(state_dir) / f"{safe_run_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        runner = cls(
            task=Task.from_dict(data["task"]),
            snapshot=RunSnapshot.from_dict(data["snapshot"]),
            state_dir=Path(state_dir),
            evidence=[EvidenceRecord.from_dict(item) for item in data.get("evidence", [])],
            approvals=set(data.get("approvals", [])),
        )
        if runner.snapshot.run_id != safe_run_id:
            raise ValueError("persisted snapshot run_id does not match requested run_id")
        if runner.snapshot.task_id != runner.task.task_id:
            raise ValueError("persisted snapshot task_id does not match task")
        unknown_approvals = runner.approvals - PROTECTED_ACTIONS
        if unknown_approvals:
            raise ValueError(f"persisted state has unknown approvals: {sorted(unknown_approvals)}")
        return runner

    def _persist(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "task": self.task.to_dict(),
            "snapshot": self.snapshot.to_dict(),
            "evidence": [record.to_dict() for record in self.evidence],
            "approvals": sorted(self.approvals),
        }
        temporary = self.state_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(self.state_path)

    def transition(self, target: RunState) -> None:
        next_snapshot = transition_state(self.snapshot, target)
        stale_record: EvidenceRecord | None = None
        latest = latest_verification(self.evidence)
        if (
            target is RunState.IMPLEMENT
            and latest is not None
            and latest.status.upper() in PASS_STATUSES
        ):
            stale_record = EvidenceRecord(
                evidence_id=f"verification-stale-{len(self.evidence) + 1}",
                task_id=self.task.task_id,
                kind="verification",
                status="STALE",
                timestamp=_utc_now(),
                details={
                    "reason": "implementation resumed after passing verification",
                    "run_id": self.snapshot.run_id,
                },
            )
        self.snapshot = next_snapshot
        if stale_record is not None:
            self.evidence.append(stale_record)
        self._persist()

    def approve(self, action: str) -> None:
        self._validate_action(action)
        if action in PROTECTED_ACTIONS:
            self.approvals.add(action)
            self._persist()

    def require_action(self, action: str) -> None:
        self._validate_action(action)
        if action in PROTECTED_ACTIONS and action not in self.approvals:
            raise ApprovalRequiredError(f"explicit approval required for action: {action}")

    def _validate_action(self, action: str) -> None:
        if action not in KNOWN_ACTIONS:
            raise ValueError(f"unknown action classification: {action}")

    def record_evidence(self, record: EvidenceRecord) -> None:
        if record.task_id != self.task.task_id:
            raise ValueError("evidence task_id does not match runner task")
        self.evidence.append(record)
        self._persist()

    def run_verification(
        self,
        command: tuple[str, ...],
        *,
        cwd: Path | None = None,
        timeout_seconds: float = 300.0,
    ) -> EvidenceRecord:
        self.require_action("terminal")
        if not isinstance(command, tuple) or not command or any(
            not isinstance(part, str) or not part for part in command
        ):
            raise ValueError("command must be a non-empty tuple of non-empty strings")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        resolved_cwd = Path(cwd or self.state_dir).resolve()
        started = _utc_now()
        try:
            completed = subprocess.run(
                list(command),
                cwd=resolved_cwd,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            exit_code = completed.returncode
            stdout = completed.stdout[-OUTPUT_LIMIT:]
            stderr = completed.stderr[-OUTPUT_LIMIT:]
            status = "PASS" if exit_code == 0 else "FAIL"
        except subprocess.TimeoutExpired as exc:
            exit_code = -1
            stdout = (exc.stdout or "")[-OUTPUT_LIMIT:] if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "")[-OUTPUT_LIMIT:] if isinstance(exc.stderr, str) else ""
            status = "FAIL"

        record = EvidenceRecord(
            evidence_id=f"verification-{len(self.evidence) + 1}",
            task_id=self.task.task_id,
            kind="test",
            status=status,
            timestamp=started,
            command=subprocess.list2cmdline(list(command)),
            environment={
                "cwd": str(resolved_cwd),
                "platform": platform.system(),
                "python": sys.version.split()[0],
            },
            details={
                "argv": list(command),
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
            },
        )
        self.record_evidence(record)
        return record

    def complete(self) -> None:
        require_completion_evidence(self.evidence)
        self.transition(RunState.COMPLETE)

    def block(self, reason: str) -> None:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("block reason must be a non-empty string")
        blocked_snapshot = transition_state(self.snapshot, RunState.BLOCKED)
        record = EvidenceRecord(
            evidence_id=f"block-{len(self.evidence) + 1}",
            task_id=self.task.task_id,
            kind="block",
            status="BLOCKED",
            timestamp=_utc_now(),
            details={"reason": reason, "run_id": self.snapshot.run_id},
        )
        self.snapshot = blocked_snapshot
        self.evidence.append(record)
        self._persist()


__all__ = [
    "ApprovalRequiredError",
    "ForgeRunner",
    "VerificationRequiredError",
]

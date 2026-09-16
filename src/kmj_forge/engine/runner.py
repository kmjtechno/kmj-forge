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


class UnsafeCommandError(PermissionError):
    pass


AUTO_APPROVED_ACTIONS = frozenset({"read", "test"})
PROTECTED_ACTIONS = frozenset({"write", "terminal", "git"})
KNOWN_ACTIONS = AUTO_APPROVED_ACTIONS | PROTECTED_ACTIONS
OUTPUT_LIMIT = 20_000
PASS_STATUSES = frozenset({"PASS", "SUCCESS", "OK"})
POSIX_SHELLS = frozenset({"bash", "sh", "zsh", "dash", "ksh"})
POSIX_DESTRUCTIVE_PATTERNS = (
    "rm ",
    "rm\t",
    "rmdir ",
    "git reset --hard",
    "git clean -f",
    "git clean -df",
    "git clean -fd",
    "mkfs",
    "shutdown",
    "reboot",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _command_parts(command: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    if not isinstance(command, tuple) or not command or any(
        not isinstance(part, str) or not part for part in command
    ):
        raise ValueError("command must be a non-empty tuple of non-empty strings")
    executable = Path(command[0]).name.lower()
    return executable, tuple(part.lower() for part in command[1:])


def classify_command_risk(command: tuple[str, ...]) -> str:
    executable, args = _command_parts(command)
    joined = " ".join(args)

    if executable in {"rm", "rmdir", "del", "erase", "format", "shutdown", "reboot"}:
        return "destructive"

    if executable in {"git", "git.exe"} and args:
        subcommand = args[0]
        if subcommand == "reset" and "--hard" in args:
            return "destructive"
        if subcommand == "clean" and any("f" in arg.lstrip("-") for arg in args[1:] if arg.startswith("-")):
            return "destructive"

    if executable in POSIX_SHELLS and args:
        shell_text = joined
        if any(pattern in shell_text for pattern in POSIX_DESTRUCTIVE_PATTERNS):
            return "destructive"

    if executable in {"powershell", "powershell.exe", "pwsh", "pwsh.exe"}:
        destructive_terms = (
            "remove-item",
            "format-volume",
            "clear-disk",
            "stop-computer",
            "restart-computer",
        )
        if any(term in joined for term in destructive_terms):
            return "destructive"

    if executable in {"cmd", "cmd.exe"}:
        destructive_terms = (" del ", " erase ", " rmdir ", " rd ", " format ", " shutdown ")
        padded = f" {joined} "
        if any(term in padded for term in destructive_terms):
            return "destructive"

    if executable.startswith("python") and "-m" in args:
        module_index = args.index("-m") + 1
        if module_index < len(args) and args[module_index] in {"unittest", "pytest", "compileall"}:
            return "verification"
    if executable in {"pytest", "pytest.exe"}:
        return "verification"
    if executable in {"cargo", "cargo.exe"} and args and args[0] in {"test", "check"}:
        return "verification"
    if executable in {"npm", "npm.cmd", "yarn", "yarn.cmd", "pnpm", "pnpm.cmd"} and args:
        if args[0] == "test" or args[:2] in (("run", "test"), ("run", "build")):
            return "verification"
    if executable in {"go", "go.exe", "dotnet", "dotnet.exe"} and args and args[0] == "test":
        return "verification"
    if executable in {"mvn", "mvn.cmd", "gradle", "gradle.bat", "gradlew", "gradlew.bat"} and "test" in args:
        return "verification"

    return "protected"


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

    def write_text_file(
        self,
        workspace_root: str | Path,
        relative_path: str,
        content: str,
    ) -> EvidenceRecord:
        self.require_action("write")
        if self.snapshot.state is not RunState.IMPLEMENT:
            raise RuntimeError("text edits are only allowed in IMPLEMENT state")
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError("relative_path must be a non-empty string")
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        root = Path(workspace_root).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"workspace root is not a directory: {root}")

        relative = Path(relative_path)
        if relative.is_absolute() or relative == Path(".") or ".." in relative.parts:
            raise ValueError("relative_path must stay inside the workspace")

        target = (root / relative).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError("relative_path escapes the workspace") from exc

        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.parent / f".{target.name}.kmj-forge.tmp"
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)

        normalized_path = target.relative_to(root).as_posix()
        record = EvidenceRecord(
            evidence_id=f"change-{len(self.evidence) + 1}",
            task_id=self.task.task_id,
            kind="change",
            status="PASS",
            timestamp=_utc_now(),
            changed_files=(normalized_path,),
            details={
                "operation": "write_text_file",
                "characters": len(content),
                "run_id": self.snapshot.run_id,
            },
        )
        self.record_evidence(record)
        return record

    def run_verification(
        self,
        command: tuple[str, ...],
        *,
        cwd: Path | None = None,
        timeout_seconds: float = 300.0,
    ) -> EvidenceRecord:
        self.require_action("terminal")
        _command_parts(command)
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if classify_command_risk(command) == "destructive":
            raise UnsafeCommandError(
                f"destructive command is not allowed in verification: {subprocess.list2cmdline(list(command))}"
            )

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
    "UnsafeCommandError",
    "VerificationRequiredError",
    "classify_command_risk",
]

from __future__ import annotations

from collections.abc import Sequence

from kmj_forge.protocol import EvidenceRecord


VERIFICATION_KINDS = frozenset({"test", "verification"})
PASS_STATUSES = frozenset({"PASS", "SUCCESS", "OK"})


class VerificationRequiredError(RuntimeError):
    pass


def latest_verification(records: Sequence[EvidenceRecord]) -> EvidenceRecord | None:
    for record in reversed(records):
        if record.kind.lower() in VERIFICATION_KINDS:
            return record
    return None


def require_completion_evidence(records: Sequence[EvidenceRecord]) -> EvidenceRecord:
    record = latest_verification(records)
    if record is None:
        raise VerificationRequiredError("completion requires verification evidence")
    if record.status.upper() not in PASS_STATUSES:
        raise VerificationRequiredError(
            f"latest verification did not pass: {record.status}"
        )
    return record


def require_plan_completion_evidence(plan, records: Sequence[EvidenceRecord]) -> tuple[EvidenceRecord, ...]:
    """Require latest passing evidence for every command in a verification plan."""
    latest_by_command: dict[str, EvidenceRecord] = {}
    for record in records:
        if record.task_id != plan.task_id or record.kind.lower() not in VERIFICATION_KINDS:
            continue
        if record.command in plan.commands:
            latest_by_command[record.command] = record

    missing = [command for command in plan.commands if command not in latest_by_command]
    if missing:
        raise VerificationRequiredError("missing verification evidence: " + ", ".join(missing))

    failed = [command for command in plan.commands
              if latest_by_command[command].status.upper() not in PASS_STATUSES]
    if failed:
        raise VerificationRequiredError("verification did not pass: " + ", ".join(failed))

    return tuple(latest_by_command[command] for command in plan.commands)

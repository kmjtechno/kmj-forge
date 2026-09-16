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

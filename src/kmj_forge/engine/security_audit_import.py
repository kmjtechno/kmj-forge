from __future__ import annotations

import json

from kmj_forge.engine.security_audit import SecurityAuditRecord, SecurityAuditSignal
from kmj_forge.engine.security_audit_log import SecurityAuditLog


_SCHEMA = "kmj-forge.security-audit.v1"
_DOCUMENT_FIELDS = {"schema", "entries"}
_ENTRY_FIELDS = {"sequence", "previous_digest", "digest", "record"}
_RECORD_FIELDS = {"action_id", "target_id", "allowed", "requires_approval", "signals"}


def import_audit_log(serialized: str) -> SecurityAuditLog:
    """Restore a verified audit export without trusting serialized digests.

    The importer is deliberately strict: unknown fields and schemas are
    rejected, records are reconstructed through the secret-safe validation
    boundary, and every serialized chain value must match the locally
    recomputed append-only chain.
    """
    if type(serialized) is not str:
        raise TypeError("audit import accepts JSON strings only")
    try:
        document = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid audit JSON") from exc
    if type(document) is not dict or set(document) != _DOCUMENT_FIELDS:
        raise ValueError("invalid audit document shape")
    if document["schema"] != _SCHEMA or type(document["entries"]) is not list:
        raise ValueError("unsupported audit schema or entries")

    log = SecurityAuditLog()
    for raw_entry in document["entries"]:
        if type(raw_entry) is not dict or set(raw_entry) != _ENTRY_FIELDS:
            raise ValueError("invalid audit entry shape")
        raw_record = raw_entry["record"]
        if type(raw_record) is not dict or set(raw_record) != _RECORD_FIELDS:
            raise ValueError("invalid audit record shape")
        raw_signals = raw_record["signals"]
        if type(raw_signals) is not list or any(type(value) is not str for value in raw_signals):
            raise ValueError("invalid audit signals")
        try:
            signals = tuple(SecurityAuditSignal(value) for value in raw_signals)
            record = SecurityAuditRecord.create(
                action_id=raw_record["action_id"],
                target_id=raw_record["target_id"],
                allowed=raw_record["allowed"],
                requires_approval=raw_record["requires_approval"],
                signals=signals,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid audit record") from exc

        rebuilt = log.append(record)
        if type(raw_entry["sequence"]) is not int or raw_entry["sequence"] != rebuilt.sequence:
            raise ValueError("audit sequence mismatch")
        if type(raw_entry["previous_digest"]) is not str or raw_entry["previous_digest"] != rebuilt.previous_digest:
            raise ValueError("audit previous digest mismatch")
        if type(raw_entry["digest"]) is not str or raw_entry["digest"] != rebuilt.digest:
            raise ValueError("audit digest mismatch")

    if not log.verify():
        raise ValueError("imported audit log failed verification")
    return log

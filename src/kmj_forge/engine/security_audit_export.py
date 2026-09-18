from __future__ import annotations

import json

from kmj_forge.engine.security_audit_log import SecurityAuditLog


_SCHEMA = "kmj-forge.security-audit.v1"


def export_audit_log(log: SecurityAuditLog) -> str:
    """Return a deterministic, secret-safe snapshot of a verified audit log.

    Export is deliberately read-only and refuses to serialize a chain whose
    integrity check fails. The document contains only fields already admitted
    by the constrained ``SecurityAuditRecord`` boundary.
    """
    if not isinstance(log, SecurityAuditLog):
        raise TypeError("audit export accepts SecurityAuditLog values only")
    if not log.verify():
        raise ValueError("refusing to export an unverified security audit log")

    document = {
        "schema": _SCHEMA,
        "entries": [
            {
                "sequence": entry.sequence,
                "previous_digest": entry.previous_digest,
                "digest": entry.digest,
                "record": {
                    "action_id": entry.record.action_id,
                    "target_id": entry.record.target_id,
                    "allowed": entry.record.allowed,
                    "requires_approval": entry.record.requires_approval,
                    "signals": [signal.value for signal in entry.record.signals],
                },
            }
            for entry in log.entries
        ],
    }
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

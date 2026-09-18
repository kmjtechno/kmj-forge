from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from kmj_forge.engine.security_audit import SecurityAuditRecord


_GENESIS_DIGEST = "0" * 64


@dataclass(frozen=True)
class SecurityAuditEntry:
    """One immutable, tamper-evident security decision entry."""

    sequence: int
    previous_digest: str
    digest: str
    record: SecurityAuditRecord


class SecurityAuditLog:
    """In-memory append-only hash chain for secret-safe security decisions.

    Persistence is deliberately outside this boundary. Only validated
    ``SecurityAuditRecord`` metadata is accepted, preventing arbitrary command
    output, environment data, or credential payloads from entering the chain.
    """

    def __init__(self) -> None:
        self._entries: list[SecurityAuditEntry] = []

    @property
    def entries(self) -> tuple[SecurityAuditEntry, ...]:
        return tuple(self._entries)

    def append(self, record: SecurityAuditRecord) -> SecurityAuditEntry:
        if not isinstance(record, SecurityAuditRecord):
            raise TypeError("audit log accepts SecurityAuditRecord values only")

        sequence = len(self._entries) + 1
        previous_digest = self._entries[-1].digest if self._entries else _GENESIS_DIGEST
        digest = self._digest(sequence, previous_digest, record)
        entry = SecurityAuditEntry(
            sequence=sequence,
            previous_digest=previous_digest,
            digest=digest,
            record=record,
        )
        self._entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous_digest = _GENESIS_DIGEST
        for expected_sequence, entry in enumerate(self._entries, start=1):
            if entry.sequence != expected_sequence:
                return False
            if entry.previous_digest != previous_digest:
                return False
            if entry.digest != self._digest(entry.sequence, entry.previous_digest, entry.record):
                return False
            previous_digest = entry.digest
        return True

    @staticmethod
    def _digest(sequence: int, previous_digest: str, record: SecurityAuditRecord) -> str:
        material = {
            "sequence": sequence,
            "previous_digest": previous_digest,
            "record": {
                "action_id": record.action_id,
                "target_id": record.target_id,
                "allowed": record.allowed,
                "requires_approval": record.requires_approval,
                "signals": [signal.value for signal in record.signals],
            },
        }
        canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

import unittest

from kmj_forge.engine.security_audit import SecurityAuditRecord, SecurityAuditSignal
from kmj_forge.engine.security_audit_log import SecurityAuditLog


class SecurityAuditLogTests(unittest.TestCase):
    def _record(self, action_id="read.repository", target_id="workspace:src"):
        return SecurityAuditRecord.create(
            action_id=action_id,
            target_id=target_id,
            allowed=True,
            requires_approval=False,
            signals=(),
        )

    def test_appends_records_with_monotonic_sequence_and_hash_chain(self):
        log = SecurityAuditLog()
        first = log.append(self._record())
        second = log.append(self._record("read.file", "workspace:README.md"))

        self.assertEqual(first.sequence, 1)
        self.assertEqual(second.sequence, 2)
        self.assertEqual(second.previous_digest, first.digest)
        self.assertTrue(log.verify())

    def test_digest_is_deterministic_for_same_record_and_position(self):
        left = SecurityAuditLog()
        right = SecurityAuditLog()
        left_entry = left.append(self._record())
        right_entry = right.append(self._record())
        self.assertEqual(left_entry.digest, right_entry.digest)

    def test_entries_snapshot_is_immutable_and_does_not_expose_mutation(self):
        log = SecurityAuditLog()
        log.append(self._record())
        snapshot = log.entries
        self.assertIsInstance(snapshot, tuple)
        self.assertEqual(len(snapshot), 1)
        with self.assertRaises(AttributeError):
            snapshot[0].digest = "tampered"

    def test_verify_detects_internal_chain_tampering(self):
        log = SecurityAuditLog()
        log.append(self._record())
        log.append(self._record("read.file", "workspace:README.md"))
        object.__setattr__(log._entries[0], "digest", "0" * 64)
        self.assertFalse(log.verify())

    def test_rejects_non_audit_record(self):
        log = SecurityAuditLog()
        with self.assertRaises(TypeError):
            log.append({"action_id": "read.repository"})

    def test_digest_material_contains_no_secret_payload_surface(self):
        log = SecurityAuditLog()
        entry = log.append(
            SecurityAuditRecord.create(
                action_id="write.local",
                target_id="workspace:config",
                allowed=False,
                requires_approval=True,
                signals=(SecurityAuditSignal.APPROVAL_REQUIRED,),
            )
        )
        self.assertEqual(len(entry.digest), 64)
        self.assertNotIn("config", entry.digest)


if __name__ == "__main__":
    unittest.main()

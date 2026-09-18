import unittest

from kmj_forge.engine.security_audit import SecurityAuditRecord, SecurityAuditSignal


class SecurityAuditRecordTests(unittest.TestCase):
    def test_records_decision_metadata_without_secret_material(self):
        record = SecurityAuditRecord.create(
            action_id="read.repository",
            target_id="workspace:src",
            allowed=True,
            requires_approval=False,
            signals=(),
        )
        self.assertEqual(record.action_id, "read.repository")
        self.assertEqual(record.target_id, "workspace:src")
        self.assertTrue(record.allowed)
        self.assertEqual(record.signals, ())

    def test_rejects_secret_like_metadata(self):
        with self.assertRaises(ValueError):
            SecurityAuditRecord.create(
                action_id="read.repository",
                target_id="token=super-secret-value",
                allowed=False,
                requires_approval=True,
                signals=(SecurityAuditSignal.SECURITY_BLOCKED,),
            )

    def test_rejects_malformed_identifiers(self):
        for action_id, target_id in (("", "workspace:src"), ("read repository", "workspace:src"), ("read.repository", "../etc/passwd")):
            with self.subTest(action_id=action_id, target_id=target_id):
                with self.assertRaises(ValueError):
                    SecurityAuditRecord.create(
                        action_id=action_id,
                        target_id=target_id,
                        allowed=False,
                        requires_approval=False,
                        signals=(),
                    )

    def test_signals_are_canonicalized_and_deduplicated(self):
        record = SecurityAuditRecord.create(
            action_id="write.local",
            target_id="workspace:config",
            allowed=False,
            requires_approval=True,
            signals=(
                SecurityAuditSignal.APPROVAL_REQUIRED,
                SecurityAuditSignal.SECURITY_BLOCKED,
                SecurityAuditSignal.APPROVAL_REQUIRED,
            ),
        )
        self.assertEqual(
            record.signals,
            (SecurityAuditSignal.APPROVAL_REQUIRED, SecurityAuditSignal.SECURITY_BLOCKED),
        )

    def test_inconsistent_decision_fails_closed(self):
        with self.assertRaises(ValueError):
            SecurityAuditRecord.create(
                action_id="write.local",
                target_id="workspace:config",
                allowed=True,
                requires_approval=True,
                signals=(SecurityAuditSignal.APPROVAL_REQUIRED,),
            )


if __name__ == "__main__":
    unittest.main()

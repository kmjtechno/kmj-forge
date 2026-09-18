import json
import unittest

from kmj_forge.engine.security_audit import SecurityAuditRecord, SecurityAuditSignal
from kmj_forge.engine.security_audit_export import export_audit_log
from kmj_forge.engine.security_audit_log import SecurityAuditLog


class SecurityAuditExportTests(unittest.TestCase):
    def _log(self):
        log = SecurityAuditLog()
        log.append(
            SecurityAuditRecord.create(
                action_id="read.repository",
                target_id="workspace:src",
                allowed=True,
                requires_approval=False,
                signals=(),
            )
        )
        log.append(
            SecurityAuditRecord.create(
                action_id="write.local",
                target_id="workspace:config",
                allowed=False,
                requires_approval=True,
                signals=(SecurityAuditSignal.APPROVAL_REQUIRED,),
            )
        )
        return log

    def test_exports_verified_log_as_deterministic_canonical_json(self):
        first = export_audit_log(self._log())
        second = export_audit_log(self._log())
        self.assertEqual(first, second)
        document = json.loads(first)
        self.assertEqual(document["schema"], "kmj-forge.security-audit.v1")
        self.assertEqual(len(document["entries"]), 2)
        self.assertEqual(document["entries"][1]["previous_digest"], document["entries"][0]["digest"])

    def test_export_contains_only_secret_safe_audit_fields(self):
        document = json.loads(export_audit_log(self._log()))
        serialized = json.dumps(document, sort_keys=True)
        self.assertNotIn("command", serialized)
        self.assertNotIn("environment", serialized)
        self.assertNotIn("credential", serialized)
        self.assertEqual(
            set(document["entries"][0]["record"]),
            {"action_id", "target_id", "allowed", "requires_approval", "signals"},
        )

    def test_refuses_unverified_or_tampered_log(self):
        log = self._log()
        object.__setattr__(log._entries[0], "digest", "0" * 64)
        self.assertFalse(log.verify())
        with self.assertRaises(ValueError):
            export_audit_log(log)

    def test_refuses_non_audit_log_values(self):
        with self.assertRaises(TypeError):
            export_audit_log([])


if __name__ == "__main__":
    unittest.main()

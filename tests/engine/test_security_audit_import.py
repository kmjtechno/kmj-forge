import json
import unittest

from kmj_forge.engine.security_audit import SecurityAuditRecord
from kmj_forge.engine.security_audit_export import export_audit_log
from kmj_forge.engine.security_audit_import import import_audit_log
from kmj_forge.engine.security_audit_log import SecurityAuditLog


class SecurityAuditImportTests(unittest.TestCase):
    def _export(self):
        log = SecurityAuditLog()
        log.append(SecurityAuditRecord.create(
            action_id="read.repository",
            target_id="workspace:src",
            allowed=True,
            requires_approval=False,
            signals=(),
        ))
        return export_audit_log(log)

    def test_round_trip_preserves_verified_canonical_export(self):
        exported = self._export()
        restored = import_audit_log(exported)
        self.assertTrue(restored.verify())
        self.assertEqual(export_audit_log(restored), exported)

    def test_refuses_unknown_schema(self):
        document = json.loads(self._export())
        document["schema"] = "kmj-forge.security-audit.v999"
        with self.assertRaises(ValueError):
            import_audit_log(json.dumps(document))

    def test_refuses_digest_tampering(self):
        document = json.loads(self._export())
        document["entries"][0]["digest"] = "0" * 64
        with self.assertRaises(ValueError):
            import_audit_log(json.dumps(document))

    def test_refuses_extra_record_fields(self):
        document = json.loads(self._export())
        document["entries"][0]["record"]["credential"] = "must-not-enter"
        with self.assertRaises(ValueError):
            import_audit_log(json.dumps(document))

    def test_refuses_non_string_input(self):
        with self.assertRaises(TypeError):
            import_audit_log({})


if __name__ == "__main__":
    unittest.main()

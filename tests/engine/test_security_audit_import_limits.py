import json
import unittest

from kmj_forge.engine.security_audit_import import import_audit_log


class SecurityAuditImportLimitTests(unittest.TestCase):
    def test_refuses_oversized_serialized_document(self):
        oversized = " " * (1_048_576 + 1)
        with self.assertRaises(ValueError):
            import_audit_log(oversized)

    def test_refuses_excessive_entry_count_before_rebuilding(self):
        document = {
            "schema": "kmj-forge.security-audit.v1",
            "entries": [None] * 10_001,
        }
        with self.assertRaises(ValueError):
            import_audit_log(json.dumps(document))


if __name__ == "__main__":
    unittest.main()

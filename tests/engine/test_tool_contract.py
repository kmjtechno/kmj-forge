import unittest

from kmj_forge.engine.tool_contract import PermissionClass, ToolContract


class ToolContractTests(unittest.TestCase):
    def test_valid_contract_preserves_required_execution_controls(self):
        contract = ToolContract.create(
            name="read_file",
            permission_class=PermissionClass.READ_ONLY,
            timeout_seconds=30,
            cancellable=True,
            max_retries=2,
            audit_event="tool.read_file",
            error_schema="kmj-forge.tool-error.v1",
            evidence_schema="kmj-forge.tool-evidence.v1",
        )
        self.assertEqual(contract.name, "read_file")
        self.assertEqual(contract.permission_class, PermissionClass.READ_ONLY)
        self.assertEqual(contract.timeout_seconds, 30)
        self.assertEqual(contract.max_retries, 2)

    def test_rejects_non_positive_timeout(self):
        with self.assertRaises(ValueError):
            ToolContract.create(
                name="test",
                permission_class=PermissionClass.READ_ONLY,
                timeout_seconds=0,
                cancellable=True,
                max_retries=0,
                audit_event="tool.test",
                error_schema="error.v1",
                evidence_schema="evidence.v1",
            )

    def test_rejects_negative_or_unbounded_retry_policy(self):
        for retries in (-1, 11):
            with self.subTest(retries=retries), self.assertRaises(ValueError):
                ToolContract.create(
                    name="test",
                    permission_class=PermissionClass.READ_ONLY,
                    timeout_seconds=1,
                    cancellable=True,
                    max_retries=retries,
                    audit_event="tool.test",
                    error_schema="error.v1",
                    evidence_schema="evidence.v1",
                )

    def test_rejects_blank_required_identifiers(self):
        fields = ("name", "audit_event", "error_schema", "evidence_schema")
        base = dict(
            name="test",
            permission_class=PermissionClass.READ_ONLY,
            timeout_seconds=1,
            cancellable=True,
            max_retries=0,
            audit_event="tool.test",
            error_schema="error.v1",
            evidence_schema="evidence.v1",
        )
        for field in fields:
            values = dict(base)
            values[field] = "   "
            with self.subTest(field=field), self.assertRaises(ValueError):
                ToolContract.create(**values)

    def test_rejects_non_boolean_cancellation_flag(self):
        with self.assertRaises(TypeError):
            ToolContract.create(
                name="test",
                permission_class=PermissionClass.READ_ONLY,
                timeout_seconds=1,
                cancellable=1,
                max_retries=0,
                audit_event="tool.test",
                error_schema="error.v1",
                evidence_schema="evidence.v1",
            )


if __name__ == "__main__":
    unittest.main()

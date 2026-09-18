import unittest

from kmj_forge.engine.tool_contract import PermissionClass, ToolContract


BASE = dict(
    name="test",
    permission_class=PermissionClass.READ_ONLY,
    timeout_seconds=1,
    cancellable=True,
    max_retries=0,
    input_schema="kmj-forge.tool-input.v1",
    output_schema="kmj-forge.tool-output.v1",
    audit_event="tool.test",
    error_schema="error.v1",
    evidence_schema="evidence.v1",
)


class ToolContractTests(unittest.TestCase):
    def test_valid_contract_preserves_required_execution_controls(self):
        contract = ToolContract.create(**BASE)
        self.assertEqual(contract.name, "test")
        self.assertEqual(contract.permission_class, PermissionClass.READ_ONLY)
        self.assertEqual(contract.timeout_seconds, 1)
        self.assertEqual(contract.max_retries, 0)
        self.assertEqual(contract.input_schema, "kmj-forge.tool-input.v1")
        self.assertEqual(contract.output_schema, "kmj-forge.tool-output.v1")

    def test_rejects_non_positive_timeout(self):
        values = dict(BASE, timeout_seconds=0)
        with self.assertRaises(ValueError):
            ToolContract.create(**values)

    def test_rejects_negative_or_unbounded_retry_policy(self):
        for retries in (-1, 11):
            values = dict(BASE, max_retries=retries)
            with self.subTest(retries=retries), self.assertRaises(ValueError):
                ToolContract.create(**values)

    def test_rejects_blank_required_identifiers_and_schemas(self):
        fields = (
            "name",
            "input_schema",
            "output_schema",
            "audit_event",
            "error_schema",
            "evidence_schema",
        )
        for field in fields:
            values = dict(BASE)
            values[field] = "   "
            with self.subTest(field=field), self.assertRaises(ValueError):
                ToolContract.create(**values)

    def test_rejects_non_string_typed_schemas(self):
        for field in ("input_schema", "output_schema"):
            values = dict(BASE)
            values[field] = {"type": "object"}
            with self.subTest(field=field), self.assertRaises(ValueError):
                ToolContract.create(**values)

    def test_rejects_non_boolean_cancellation_flag(self):
        values = dict(BASE, cancellable=1)
        with self.assertRaises(TypeError):
            ToolContract.create(**values)


if __name__ == "__main__":
    unittest.main()

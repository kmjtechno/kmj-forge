import unittest

from kmj_forge.engine.tool_contract import PermissionClass, ToolContract
from kmj_forge.engine.tool_registry import ToolRegistry


def contract(
    name: str, permission_class: PermissionClass = PermissionClass.READ_ONLY
) -> ToolContract:
    return ToolContract.create(
        name=name,
        permission_class=permission_class,
        timeout_seconds=1,
        cancellable=True,
        max_retries=0,
        input_schema="kmj-forge.tool-input.v1",
        output_schema="kmj-forge.tool-output.v1",
        audit_event=f"tool.{name}",
        error_schema="error.v1",
        evidence_schema="evidence.v1",
    )


class ToolRegistryTests(unittest.TestCase):
    def test_register_and_resolve_contract(self):
        registry = ToolRegistry()
        expected = contract("read_file")
        registry.register(expected)
        self.assertIs(registry.require("read_file"), expected)

    def test_duplicate_name_is_rejected_fail_closed(self):
        registry = ToolRegistry()
        registry.register(contract("read_file"))
        with self.assertRaises(ValueError):
            registry.register(contract("read_file"))

    def test_unknown_tool_is_rejected_fail_closed(self):
        registry = ToolRegistry()
        with self.assertRaises(KeyError):
            registry.require("missing")

    def test_blank_lookup_is_rejected(self):
        registry = ToolRegistry()
        with self.assertRaises(ValueError):
            registry.require("   ")

    def test_snapshot_is_deterministic_and_immutable(self):
        registry = ToolRegistry()
        registry.register(contract("write_file"))
        registry.register(contract("read_file"))
        snapshot = registry.snapshot()
        self.assertEqual(tuple(snapshot), ("read_file", "write_file"))
        with self.assertRaises(TypeError):
            snapshot["other"] = contract("other")

    def test_require_permission_accepts_exact_permission(self):
        registry = ToolRegistry()
        expected = contract("write_file", PermissionClass.WORKSPACE_WRITE)
        registry.register(expected)
        self.assertIs(
            registry.require_permission("write_file", PermissionClass.WORKSPACE_WRITE),
            expected,
        )

    def test_require_permission_rejects_mismatched_permission_fail_closed(self):
        registry = ToolRegistry()
        registry.register(contract("write_file", PermissionClass.WORKSPACE_WRITE))
        with self.assertRaises(PermissionError):
            registry.require_permission("write_file", PermissionClass.READ_ONLY)

    def test_require_permission_rejects_invalid_expected_permission(self):
        registry = ToolRegistry()
        registry.register(contract("read_file"))
        with self.assertRaises(TypeError):
            registry.require_permission("read_file", "read_only")


if __name__ == "__main__":
    unittest.main()

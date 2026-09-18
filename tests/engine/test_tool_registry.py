import unittest

from kmj_forge.engine.tool_contract import PermissionClass, ToolContract
from kmj_forge.engine.tool_registry import ToolRegistry


def contract(name: str) -> ToolContract:
    return ToolContract.create(
        name=name,
        permission_class=PermissionClass.READ_ONLY,
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


if __name__ == "__main__":
    unittest.main()

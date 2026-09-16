import importlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

from kmj_forge import __version__


def bridge_module():
    spec = importlib.util.find_spec("kmj_forge.desktop_bridge")
    if spec is None:
        raise AssertionError("kmj_forge.desktop_bridge must exist")
    return importlib.import_module("kmj_forge.desktop_bridge")


class DesktopBridgeTests(unittest.TestCase):
    def test_health_uses_versioned_response_envelope(self) -> None:
        bridge = bridge_module()
        response = bridge.handle_request({"protocol_version": "1.0", "operation": "health", "payload": {}})
        self.assertTrue(response["ok"])
        self.assertEqual(response["protocol_version"], "1.0")
        self.assertEqual(response["result"]["forge_version"], __version__)

    def test_protocol_mismatch_and_unknown_operations_are_structured_errors(self) -> None:
        bridge = bridge_module()
        mismatch = bridge.handle_request({"protocol_version": "2.0", "operation": "health", "payload": {}})
        unknown = bridge.handle_request({"protocol_version": "1.0", "operation": "erase_everything", "payload": {}})
        self.assertFalse(mismatch["ok"])
        self.assertEqual(mismatch["error"]["code"], "protocol_mismatch")
        self.assertFalse(unknown["ok"])
        self.assertEqual(unknown["error"]["code"], "unknown_operation")

    def test_inspect_repository_reuses_forge_detection_and_context(self) -> None:
        bridge = bridge_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "app.py").write_text("def validate_token(token):\n    return bool(token)\n", encoding="utf-8")
            (root / "tests" / "test_app.py").write_text("import unittest\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='bridge-fixture'\n", encoding="utf-8")
            response = bridge.handle_request({
                "protocol_version": "1.0",
                "operation": "inspect_repository",
                "payload": {"path": str(root), "objective": "Fix validate_token in app.py", "character_budget": 1000},
            })
            self.assertTrue(response["ok"])
            result = response["result"]
            self.assertIn("python", result["detection"]["languages"])
            self.assertIn("python", result["detection"]["build_systems"])
            self.assertIn("app.py", result["context"]["relevant_files"])
            self.assertLessEqual(result["context"]["total_characters"], 1000)

    def test_run_create_status_and_approval_reuse_persisted_forge_runner(self) -> None:
        bridge = bridge_module()
        with tempfile.TemporaryDirectory() as tmp:
            create = bridge.handle_request({
                "protocol_version": "1.0",
                "operation": "run_create",
                "payload": {"state_dir": tmp, "run_id": "desktop-run", "task_id": "desktop-task", "objective": "Fix tests"},
            })
            self.assertTrue(create["ok"])
            self.assertEqual(create["result"]["state"], "RECEIVE")

            approve = bridge.handle_request({
                "protocol_version": "1.0",
                "operation": "run_approve",
                "payload": {"state_dir": tmp, "run_id": "desktop-run", "action": "terminal"},
            })
            self.assertEqual(approve["result"]["approvals"], ["terminal"])

            status = bridge.handle_request({
                "protocol_version": "1.0",
                "operation": "run_status",
                "payload": {"state_dir": tmp, "run_id": "desktop-run"},
            })
            self.assertEqual(status["result"]["task_id"], "desktop-task")
            self.assertEqual(status["result"]["approvals"], ["terminal"])


if __name__ == "__main__":
    unittest.main()

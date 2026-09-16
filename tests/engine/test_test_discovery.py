import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine.test_discovery import discover_verification_commands


class TestDiscoveryTests(unittest.TestCase):
    def test_discovers_python_unittest_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_app.py").write_text("import unittest\n", encoding="utf-8")
            self.assertEqual(
                discover_verification_commands(root),
                (("python", "-m", "unittest", "discover", "-s", "tests"),),
            )

    def test_prefers_declared_package_test_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"scripts":{"test":"vitest run"}}', encoding="utf-8")
            self.assertEqual(discover_verification_commands(root), (("npm", "test"),))

    def test_discovers_rust_and_go_projects_deterministically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text("[package]\nname='demo'\n", encoding="utf-8")
            (root / "go.mod").write_text("module demo\n", encoding="utf-8")
            self.assertEqual(
                discover_verification_commands(root),
                (("cargo", "test"), ("go", "test", "./...")),
            )

    def test_fails_closed_when_no_test_system_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "verification command"):
                discover_verification_commands(Path(tmp))


if __name__ == "__main__":
    unittest.main()

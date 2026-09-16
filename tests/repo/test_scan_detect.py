import json
import tempfile
import unittest
from pathlib import Path

from kmj_forge.repo import detect_project, scan_repository


class RepositoryScanDetectTests(unittest.TestCase):
    def test_scan_ignores_generated_dirs_and_oversized_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "ignored.py").write_text("ignored", encoding="utf-8")
            (root / "huge.txt").write_text("x" * 1024, encoding="utf-8")

            result = scan_repository(root, max_file_bytes=128)
            paths = {item.path for item in result.files}

            self.assertIn("src/main.py", paths)
            self.assertNotIn("node_modules/ignored.js", paths)
            self.assertNotIn(".git/ignored.py", paths)
            self.assertNotIn("huge.txt", paths)
            self.assertGreaterEqual(result.skipped_files, 3)

    def test_detect_project_reports_languages_build_and_test_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "app.py").write_text("def main(): return 1\n", encoding="utf-8")
            (root / "tests" / "test_app.py").write_text("import unittest\n", encoding="utf-8")
            (root / "web.js").write_text("export const x = 1;\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
            (root / "package.json").write_text(json.dumps({"scripts": {"test": "vitest run"}}), encoding="utf-8")

            detection = detect_project(scan_repository(root))

            self.assertIn("python", detection.languages)
            self.assertIn("javascript", detection.languages)
            self.assertIn("python", detection.build_systems)
            self.assertIn("npm", detection.build_systems)
            self.assertIn("python -m unittest discover -s tests -v", detection.test_commands)
            self.assertIn("npm test", detection.test_commands)


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryStructureTests(unittest.TestCase):
    def test_required_directories_exist(self) -> None:
        required = [
            "docs",
            "core",
            "agents",
            "skills",
            "adapters",
            "schemas",
            "tools",
            "examples",
            "tests",
            "benchmarks",
            ".github/workflows",
            "src/kmj_forge",
        ]
        for path in required:
            self.assertTrue((ROOT / path).is_dir(), path)

    def test_publication_manifest_contains_no_generated_python_bytecode(self) -> None:
        manifest = json.loads(
            (ROOT / "REPOSITORY_MANIFEST.json").read_text(encoding="utf-8")
        )
        generated = [
            path
            for path in manifest["files"]
            if "__pycache__" in Path(path).parts or Path(path).suffix == ".pyc"
        ]
        self.assertEqual(generated, [])

    def test_required_root_files_exist(self) -> None:
        required = [
            "README.md",
            "LICENSE",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "pyproject.toml",
            "VERSION",
        ]
        for path in required:
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()

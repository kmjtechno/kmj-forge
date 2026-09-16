from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import PurePosixPath

from .scan import ScanResult


LANGUAGE_BY_SUFFIX = {
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".kt": "kotlin",
    ".php": "php",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".swift": "swift",
    ".ts": "typescript",
    ".tsx": "typescript",
}


@dataclass(frozen=True, slots=True)
class ProjectDetection:
    languages: tuple[str, ...]
    build_systems: tuple[str, ...]
    test_commands: tuple[str, ...]


def detect_project(scan: ScanResult) -> ProjectDetection:
    paths = {item.path for item in scan.files}
    languages = {
        language
        for item in scan.files
        if (language := LANGUAGE_BY_SUFFIX.get(PurePosixPath(item.path).suffix.lower()))
    }
    build_systems: set[str] = set()
    test_commands: set[str] = set()

    if paths & {"pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"}:
        build_systems.add("python")
    if "package.json" in paths:
        build_systems.add("npm")
    if "Cargo.toml" in paths:
        build_systems.add("cargo")
    if "go.mod" in paths:
        build_systems.add("go")
    if "pom.xml" in paths:
        build_systems.add("maven")
    if paths & {"build.gradle", "build.gradle.kts"}:
        build_systems.add("gradle")

    if "python" in languages and any(path.startswith("tests/") or path.startswith("test_") for path in paths):
        test_commands.add("python -m unittest discover -s tests -v")

    package = next((item for item in scan.files if item.path == "package.json"), None)
    if package is not None:
        try:
            data = json.loads(package.content)
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict) and isinstance(data.get("scripts"), dict) and "test" in data["scripts"]:
            test_commands.add("npm test")

    if "Cargo.toml" in paths:
        test_commands.add("cargo test")
    if "go.mod" in paths:
        test_commands.add("go test ./...")

    return ProjectDetection(
        tuple(sorted(languages)),
        tuple(sorted(build_systems)),
        tuple(sorted(test_commands)),
    )

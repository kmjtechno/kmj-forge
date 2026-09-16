from __future__ import annotations

import json
from pathlib import Path

Command = tuple[str, ...]


def _has_npm_test(root: Path) -> bool:
    package = root / "package.json"
    if not package.is_file():
        return False
    try:
        data = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    scripts = data.get("scripts", {})
    return isinstance(scripts, dict) and isinstance(scripts.get("test"), str) and bool(scripts["test"].strip())


def discover_verification_commands(workspace_root: str | Path) -> tuple[Command, ...]:
    root = Path(workspace_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"workspace root is not a directory: {root}")

    commands: list[Command] = []
    if _has_npm_test(root):
        commands.append(("npm", "test"))
    else:
        tests_dir = root / "tests"
        if tests_dir.is_dir() and any(tests_dir.rglob("test*.py")):
            commands.append(("python", "-m", "unittest", "discover", "-s", "tests"))

    if (root / "Cargo.toml").is_file():
        commands.append(("cargo", "test"))
    if (root / "go.mod").is_file():
        commands.append(("go", "test", "./..."))

    if not commands:
        raise ValueError("no verification command could be discovered")
    return tuple(commands)


__all__ = ["discover_verification_commands"]

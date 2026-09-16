from __future__ import annotations

import subprocess
from pathlib import Path

from kmj_forge.protocol import Task

from .test_discovery import discover_verification_commands
from .verification import VerificationPlan, build_verification_plan


def build_verification_plan_for_workspace(
    task: Task, workspace_root: str | Path
) -> VerificationPlan:
    """Discover workspace verification and bind it to the task contract."""
    commands = discover_verification_commands(workspace_root)
    rendered = tuple(subprocess.list2cmdline(list(command)) for command in commands)
    return build_verification_plan(task, rendered)


__all__ = ["build_verification_plan_for_workspace"]

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine import ForgeRunner
from kmj_forge.engine.runner import UnsafeCommandError, classify_command_risk
from kmj_forge.protocol import Task


class CommandWrapperSafetyTests(unittest.TestCase):
    def test_shell_wrapped_destructive_commands_are_classified(self) -> None:
        cases = (
            ("bash", "-c", "rm -rf ./important"),
            ("sh", "-c", "git reset --hard"),
            ("cmd", "/c", "del /q important.txt"),
            ("powershell", "-Command", "Remove-Item -Recurse -Force important"),
        )
        for command in cases:
            with self.subTest(command=command):
                self.assertEqual(classify_command_risk(command), "destructive")

    def test_shell_wrapped_destructive_command_never_reaches_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runner = ForgeRunner.start(
                Task(task_id="wrapped-command", objective="Reject shell-wrapped destructive commands"),
                state_dir=root / ".kmj-forge",
                run_id="wrapped-command-run",
            )
            runner.approve("terminal")
            with self.assertRaises(UnsafeCommandError):
                runner.run_verification(("bash", "-c", "rm -rf ./important"), cwd=root)


if __name__ == "__main__":
    unittest.main()

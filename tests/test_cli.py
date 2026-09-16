import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from kmj_forge.cli import main


class CliTests(unittest.TestCase):
    def test_version(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().strip(), "KMJ Forge 0.1.0")

    def test_bootstrap_message(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([])
        self.assertEqual(code, 0)
        self.assertIn("KMJ Forge bootstrap is ready.", out.getvalue())

    def test_run_init_and_status_expose_persisted_engine_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["run-init", tmp, "task-cli", "Fix CLI bug", "--run-id", "run-cli"])
            self.assertEqual(code, 0)
            created = json.loads(out.getvalue())
            self.assertEqual(created["run_id"], "run-cli")
            self.assertEqual(created["task_id"], "task-cli")
            self.assertEqual(created["state"], "RECEIVE")
            self.assertTrue((Path(tmp) / "run-cli.json").exists())

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["run-status", tmp, "run-cli"])
            self.assertEqual(code, 0)
            status = json.loads(out.getvalue())
            self.assertEqual(status["run_id"], "run-cli")
            self.assertEqual(status["state"], "RECEIVE")
            self.assertEqual(status["evidence_count"], 0)
            self.assertEqual(status["approvals"], [])

    def test_run_approve_persists_protected_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sink = io.StringIO()
            with redirect_stdout(sink):
                main(["run-init", tmp, "task-cli", "Fix", "--run-id", "run-cli"])
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["run-approve", tmp, "run-cli", "terminal"])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertEqual(result["approvals"], ["terminal"])

            out = io.StringIO()
            with redirect_stdout(out):
                main(["run-status", tmp, "run-cli"])
            self.assertEqual(json.loads(out.getvalue())["approvals"], ["terminal"])


if __name__ == "__main__":
    unittest.main()

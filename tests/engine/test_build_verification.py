import tempfile
import unittest
from pathlib import Path

from kmj_forge.engine.build_verification import build_verification_plan_for_workspace
from kmj_forge.protocol import Task


class BuildVerificationTests(unittest.TestCase):
    def test_discovers_and_binds_workspace_tests_to_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_app.py").write_text("import unittest\n", encoding="utf-8")
            task = Task("t-1", "change app", ("tests pass",))

            plan = build_verification_plan_for_workspace(task, root)

            self.assertEqual(plan.task_id, "t-1")
            self.assertEqual(plan.acceptance_criteria, ("tests pass",))
            self.assertEqual(plan.commands, ("python -m unittest discover -s tests",))

    def test_fails_closed_when_workspace_has_no_verification_system(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "no verification command"):
                build_verification_plan_for_workspace(Task("t-2", "change"), Path(tmp))


if __name__ == "__main__":
    unittest.main()

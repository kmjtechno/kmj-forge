import tempfile
import unittest
from pathlib import Path

from kmj_forge.protocol import Task
from kmj_forge.repo import compile_context, normalize_instruction, scan_repository


class ContextCompilerTests(unittest.TestCase):
    def test_instruction_normalization_preserves_exact_text(self) -> None:
        instruction = "Fix API_URL in src/auth.py after ERROR 401: invalid_token"
        self.assertEqual(normalize_instruction(instruction), instruction)

    def test_relevance_selection_is_deterministic_and_prefers_matching_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "auth.py").write_text("def validate_token(token):\n    return bool(token)\n", encoding="utf-8")
            (root / "test_auth.py").write_text("def test_validate_token():\n    pass\n", encoding="utf-8")
            (root / "unrelated.py").write_text("VALUE = 1\n", encoding="utf-8")
            task = Task(task_id="t1", objective="Fix validate_token in auth.py")
            scan = scan_repository(root)

            first = compile_context(task, scan, character_budget=1000)
            second = compile_context(task, scan, character_budget=1000)

            self.assertEqual(first.relevant_files, second.relevant_files)
            self.assertEqual(first.relevant_files[0], "auth.py")
            self.assertIn("validate_token", first.symbols)

    def test_context_budget_reduces_naive_repository_dump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(12):
                (root / f"module_{index}.py").write_text((f"VALUE_{index} = '{index}'\n" * 80), encoding="utf-8")
            (root / "target.py").write_text("def target_function():\n    return 42\n", encoding="utf-8")
            scan = scan_repository(root)
            naive = sum(len(item.content) for item in scan.files)
            packet = compile_context(Task(task_id="t2", objective="change target_function"), scan, character_budget=700)

            self.assertLessEqual(packet.total_characters, 700)
            self.assertLess(packet.total_characters, naive)
            self.assertIn("target.py", packet.relevant_files)

    def test_packet_carries_permissions_diff_and_diagnostics_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            task = Task(
                task_id="t3",
                objective="Fix run in app.py",
                acceptance_criteria=("tests pass",),
                constraints=("do not rename API",),
            )
            diff = "diff --git a/app.py b/app.py\n@@ -1 +1 @@"
            diagnostic = "app.py:2: NameError: API_TOKEN"
            packet = compile_context(
                task,
                scan_repository(root),
                character_budget=1000,
                permissions=("read", "test"),
                git_diff=diff,
                diagnostics=(diagnostic,),
            )

            self.assertEqual(packet.objective, task.objective)
            self.assertEqual(packet.acceptance_criteria, task.acceptance_criteria)
            self.assertEqual(packet.constraints, task.constraints)
            self.assertEqual(packet.permissions, ("read", "test"))
            self.assertEqual(packet.git_diff, diff)
            self.assertEqual(packet.diagnostics, (diagnostic,))


if __name__ == "__main__":
    unittest.main()

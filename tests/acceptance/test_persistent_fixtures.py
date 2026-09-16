from __future__ import annotations

import unittest
from pathlib import Path

from kmj_forge.protocol import Task
from kmj_forge.repo import compile_context, scan_repository


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "benchmarks" / "fixtures"


class PersistentFixtureAcceptanceTests(unittest.TestCase):
    def test_fixture_context_metrics_are_bounded_and_reproducible(self) -> None:
        cases = {
            "python": ("Change target_value safely", {"python"}, {"python"}),
            "typescript": ("Change targetValue safely", {"typescript"}, {"npm"}),
            "rust": ("Change target_value safely", {"rust"}, {"cargo"}),
            "mixed": ("Change target_value safely", {"python", "typescript", "rust"}, {"python", "npm", "cargo"}),
        }

        for name, (objective, expected_languages, expected_builds) in cases.items():
            with self.subTest(name=name):
                root = FIXTURE_ROOT / name
                self.assertTrue(root.is_dir(), f"missing persistent benchmark fixture: {root}")
                scan = scan_repository(root)
                task = Task(task_id=f"persistent-{name}", objective=objective)
                packet = compile_context(task, scan, character_budget=400)

                self.assertTrue(expected_languages.issubset(set(packet.detection.languages)))
                self.assertTrue(expected_builds.issubset(set(packet.detection.build_systems)))
                self.assertGreater(packet.naive_characters, packet.total_characters)
                self.assertLessEqual(packet.total_characters, 400)
                self.assertLessEqual(packet.total_characters / packet.naive_characters, 0.60)
                self.assertTrue(
                    any("app" in path or "lib.rs" in path for path in packet.relevant_files),
                    f"task-relevant implementation missing from context: {packet.relevant_files}",
                )

                reduction_pct = round(
                    100.0 * (1.0 - (packet.total_characters / packet.naive_characters)),
                    2,
                )
                print(
                    "KMJ_FORGE_CONTEXT_METRIC "
                    f"fixture={name} "
                    f"naive_chars={packet.naive_characters} "
                    f"selected_chars={packet.total_characters} "
                    f"reduction_pct={reduction_pct:.2f} "
                    f"relevant_files={','.join(packet.relevant_files)}"
                )


if __name__ == "__main__":
    unittest.main()

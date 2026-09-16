from __future__ import annotations

import unittest

from kmj_forge.engine.tdd_workflow import TDDPhase, TDDWorkflow


class TDDWorkflowTests(unittest.TestCase):
    def test_requires_observed_failure_before_green(self) -> None:
        workflow = TDDWorkflow("task-1")
        with self.assertRaises(ValueError):
            workflow.record_green("python -m unittest", passed=True)
        workflow.record_red("python -m unittest", passed=False)
        workflow.record_green("python -m unittest", passed=True)
        self.assertEqual(workflow.phase, TDDPhase.GREEN)

    def test_rejects_passing_red_and_failing_green(self) -> None:
        workflow = TDDWorkflow("task-1")
        with self.assertRaises(ValueError):
            workflow.record_red("pytest", passed=True)
        workflow.record_red("pytest", passed=False)
        with self.assertRaises(ValueError):
            workflow.record_green("pytest", passed=False)

    def test_refactor_requires_green_and_preserves_passing_evidence(self) -> None:
        workflow = TDDWorkflow("task-1")
        workflow.record_red("pytest", passed=False)
        workflow.record_green("pytest", passed=True)
        workflow.record_refactor("pytest", passed=True)
        self.assertEqual(workflow.phase, TDDPhase.REFACTOR)
        self.assertTrue(workflow.is_verified)
        self.assertEqual([event.phase for event in workflow.events], [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR])


if __name__ == "__main__":
    unittest.main()

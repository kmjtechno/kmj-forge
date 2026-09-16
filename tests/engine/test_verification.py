import unittest

from kmj_forge.engine.verification import VerificationPlan, build_verification_plan
from kmj_forge.protocol import Task


class VerificationPlanTests(unittest.TestCase):
    def test_plan_requires_tests_for_acceptance_criteria(self):
        task = Task("t1", "fix parser", ("parser accepts valid input",), ())
        plan = build_verification_plan(task, ("python -m unittest discover -s tests -v",))
        self.assertTrue(plan.is_complete)
        self.assertEqual(plan.acceptance_criteria, task.acceptance_criteria)
        self.assertEqual(plan.commands, ("python -m unittest discover -s tests -v",))

    def test_plan_fails_closed_without_verification_command(self):
        task = Task("t2", "fix parser", ("tests pass",), ())
        with self.assertRaisesRegex(ValueError, "verification command"):
            build_verification_plan(task, ())

    def test_round_trip_preserves_verification_contract(self):
        plan = VerificationPlan("t3", ("tests pass",), ("python -m unittest",))
        self.assertEqual(VerificationPlan.from_dict(plan.to_dict()), plan)


if __name__ == "__main__":
    unittest.main()

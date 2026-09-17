import unittest

from kmj_forge.engine.evidence import VerificationRequiredError, require_plan_completion_evidence
from kmj_forge.engine.verification import VerificationPlan
from kmj_forge.protocol import EvidenceRecord


def evidence(evidence_id, task_id, command, status):
    return EvidenceRecord(evidence_id=evidence_id, task_id=task_id, kind="verification",
                          status=status, timestamp="2026-09-17T00:00:00Z", command=command)


class EvidenceRecordTests(unittest.TestCase):
    def setUp(self):
        self.plan = VerificationPlan("task-1", ("works",), ("unit", "regression"))

    def test_requires_evidence_for_every_planned_command(self):
        with self.assertRaisesRegex(VerificationRequiredError, "missing verification evidence: regression"):
            require_plan_completion_evidence(self.plan, (evidence("e1", "task-1", "unit", "PASS"),))

    def test_rejects_wrong_task_and_latest_failed_evidence(self):
        records = (evidence("e1", "other", "unit", "PASS"), evidence("e2", "task-1", "unit", "PASS"),
                   evidence("e3", "task-1", "unit", "FAIL"), evidence("e4", "task-1", "regression", "PASS"))
        with self.assertRaisesRegex(VerificationRequiredError, "verification did not pass: unit"):
            require_plan_completion_evidence(self.plan, records)

    def test_accepts_complete_latest_passing_evidence_in_plan_order(self):
        records = (evidence("e1", "task-1", "regression", "PASS"), evidence("e2", "task-1", "unit", "PASS"))
        verified = require_plan_completion_evidence(self.plan, records)
        self.assertEqual(tuple(item.command for item in verified), self.plan.commands)


if __name__ == "__main__":
    unittest.main()

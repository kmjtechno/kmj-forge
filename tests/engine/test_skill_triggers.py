import unittest

from kmj_forge.engine.skills import SkillDescriptor, SkillRegistry
from kmj_forge.protocol.models import Task


class SkillTriggerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SkillRegistry((
            SkillDescriptor("debug", "Debug failures", ("debug", "test")),
            SkillDescriptor("plan", "Plan work", ("planning",)),
            SkillDescriptor("review", "Review changes", ("review",)),
        ))

    def test_trigger_task_returns_explainable_capability_matches(self) -> None:
        task = Task("t1", "repair parser", requested_capabilities=("test", "debug"))
        triggers = self.registry.trigger_task(task)
        self.assertEqual(tuple(item.skill.skill_id for item in triggers), ("debug",))
        self.assertEqual(triggers[0].matched_capabilities, ("debug", "test"))
        self.assertEqual(triggers[0].reason, "requested capabilities: debug, test")

    def test_trigger_order_is_deterministic_and_empty_request_is_empty(self) -> None:
        task = Task("t2", "plan and review", requested_capabilities=("review", "planning"))
        self.assertEqual(tuple(item.skill.skill_id for item in self.registry.trigger_task(task)), ("plan", "review"))
        self.assertEqual(self.registry.trigger_task(Task("t3", "inspect")), ())


if __name__ == "__main__":
    unittest.main()

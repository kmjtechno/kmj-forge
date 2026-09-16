import unittest

from kmj_forge.engine.skills import SkillDescriptor, SkillRegistry
from kmj_forge.protocol.models import Task


class SkillSpecTests(unittest.TestCase):
    def test_skill_descriptor_round_trip_is_stable(self):
        skill = SkillDescriptor("repo-test", "Run repository tests", ("test", "verify"))
        restored = SkillDescriptor.from_dict(skill.to_dict())
        self.assertEqual(restored, skill)

    def test_registry_snapshot_is_deterministic_and_round_trips(self):
        registry = SkillRegistry((
            SkillDescriptor("z-test", "Test", ("test",)),
            SkillDescriptor("a-read", "Read", ("read",)),
        ))
        payload = registry.to_dict()
        self.assertEqual([item["skill_id"] for item in payload["skills"]], ["a-read", "z-test"])
        restored = SkillRegistry.from_dict(payload)
        task = Task("t", "verify", requested_capabilities=("read", "test"))
        self.assertEqual([s.skill_id for s in restored.resolve_task(task)], ["a-read", "z-test"])


if __name__ == "__main__":
    unittest.main()

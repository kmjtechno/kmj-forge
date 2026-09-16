import unittest

from kmj_forge.engine.skills import (
    SkillDescriptor,
    SkillRegistry,
    SkillResolutionError,
)
from kmj_forge.protocol.models import Task


class SkillRegistryTests(unittest.TestCase):
    def test_task_capabilities_trigger_deterministic_matching_skills(self) -> None:
        registry = SkillRegistry((
            SkillDescriptor("tests", "Run tests", ("test", "verify")),
            SkillDescriptor("code", "Edit source", ("write", "code")),
        ))
        task = Task("t1", "change code safely", requested_capabilities=("code", "verify"))

        resolved = registry.resolve_task(task)

        self.assertEqual(tuple(skill.skill_id for skill in resolved), ("code", "tests"))

    def test_resolution_rejects_uncovered_requested_capability(self) -> None:
        registry = SkillRegistry((SkillDescriptor("tests", "Run tests", ("test",)),))
        task = Task("t2", "deploy", requested_capabilities=("deploy",))

        with self.assertRaisesRegex(SkillResolutionError, "deploy"):
            registry.resolve_task(task)

    def test_registry_rejects_duplicate_ids_and_empty_capabilities(self) -> None:
        with self.assertRaises(ValueError):
            SkillDescriptor("empty", "No capability", ())
        with self.assertRaises(ValueError):
            SkillRegistry((
                SkillDescriptor("same", "One", ("read",)),
                SkillDescriptor("same", "Two", ("write",)),
            ))


if __name__ == "__main__":
    unittest.main()

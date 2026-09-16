from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from kmj_forge.protocol.models import Task


class SkillResolutionError(LookupError):
    pass


@dataclass(frozen=True, slots=True)
class SkillDescriptor:
    skill_id: str
    description: str
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.skill_id.strip() or not self.description.strip():
            raise ValueError("skill_id and description must be non-empty")
        if not self.capabilities or any(not item.strip() for item in self.capabilities):
            raise ValueError("skill capabilities must contain non-empty values")
        if len(self.capabilities) != len(set(self.capabilities)):
            raise ValueError("skill capabilities must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {"skill_id": self.skill_id, "description": self.description,
                "capabilities": list(self.capabilities)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillDescriptor":
        return cls(data["skill_id"], data["description"], tuple(data["capabilities"]))


@dataclass(frozen=True, slots=True)
class SkillTrigger:
    skill: SkillDescriptor
    matched_capabilities: tuple[str, ...]
    reason: str


class SkillRegistry:
    def __init__(self, skills: Iterable[SkillDescriptor] = ()) -> None:
        indexed: dict[str, SkillDescriptor] = {}
        for skill in skills:
            if skill.skill_id in indexed:
                raise ValueError(f"duplicate skill id: {skill.skill_id}")
            indexed[skill.skill_id] = skill
        self._skills = indexed

    def to_dict(self) -> dict[str, Any]:
        return {"skills": [self._skills[key].to_dict() for key in sorted(self._skills)]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillRegistry":
        return cls(SkillDescriptor.from_dict(item) for item in data.get("skills", ()))

    def resolve_task(self, task: Task) -> tuple[SkillDescriptor, ...]:
        requested = set(task.requested_capabilities)
        if not requested:
            return ()
        matched = tuple(sorted(
            (skill for skill in self._skills.values() if requested & set(skill.capabilities)),
            key=lambda skill: skill.skill_id,
        ))
        covered = {cap for skill in matched for cap in skill.capabilities} & requested
        missing = requested - covered
        if missing:
            raise SkillResolutionError(
                f"no registered skill covers requested capabilities: {', '.join(sorted(missing))}"
            )
        return matched

    def trigger_task(self, task: Task) -> tuple[SkillTrigger, ...]:
        requested = set(task.requested_capabilities)
        skills = self.resolve_task(task)
        triggers = []
        for skill in skills:
            matched = tuple(sorted(requested & set(skill.capabilities)))
            triggers.append(SkillTrigger(
                skill=skill,
                matched_capabilities=matched,
                reason=f"requested capabilities: {', '.join(matched)}",
            ))
        return tuple(triggers)


__all__ = [
    "SkillDescriptor",
    "SkillRegistry",
    "SkillResolutionError",
    "SkillTrigger",
]

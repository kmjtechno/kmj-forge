from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "1.0"


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _string_tuple(name: str, value: tuple[str, ...]) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, str) for item in value):
        raise TypeError(f"{name} must be a tuple of strings")


def _require_bool(name: str, value: bool) -> None:
    if type(value) is not bool:
        raise TypeError(f"{name} must be a boolean")


def _require_positive_int(name: str, value: int) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _require_nonnegative_number(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True, slots=True)
class Task:
    task_id: str
    objective: str
    acceptance_criteria: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    requested_capabilities: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("task_id", self.task_id)
        _require_text("objective", self.objective)
        _string_tuple("acceptance_criteria", self.acceptance_criteria)
        _string_tuple("constraints", self.constraints)
        _string_tuple("requested_capabilities", self.requested_capabilities)
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported Task schema_version: {self.schema_version}")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["acceptance_criteria"] = list(self.acceptance_criteria)
        data["constraints"] = list(self.constraints)
        data["requested_capabilities"] = list(self.requested_capabilities)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            task_id=data["task_id"],
            objective=data["objective"],
            acceptance_criteria=tuple(data.get("acceptance_criteria", ())),
            constraints=tuple(data.get("constraints", ())),
            requested_capabilities=tuple(data.get("requested_capabilities", ())),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class ModelCapability:
    provider: str
    model_id: str
    capabilities: tuple[str, ...]
    context_window: int
    input_price_per_million: float
    output_price_per_million: float
    available: bool
    local: bool
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("provider", self.provider)
        _require_text("model_id", self.model_id)
        _string_tuple("capabilities", self.capabilities)
        _require_positive_int("context_window", self.context_window)
        _require_nonnegative_number("input_price_per_million", self.input_price_per_million)
        _require_nonnegative_number("output_price_per_million", self.output_price_per_million)
        _require_bool("available", self.available)
        _require_bool("local", self.local)
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported ModelCapability schema_version: {self.schema_version}")

    @property
    def is_free(self) -> bool:
        return self.input_price_per_million == 0 and self.output_price_per_million == 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = list(self.capabilities)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelCapability":
        return cls(
            provider=data["provider"],
            model_id=data["model_id"],
            capabilities=tuple(data["capabilities"]),
            context_window=data["context_window"],
            input_price_per_million=data["input_price_per_million"],
            output_price_per_million=data["output_price_per_million"],
            available=data["available"],
            local=data["local"],
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    task_id: str
    kind: str
    status: str
    timestamp: str
    command: str | None = None
    environment: dict[str, str] = field(default_factory=dict)
    changed_files: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("evidence_id", self.evidence_id)
        _require_text("task_id", self.task_id)
        _require_text("kind", self.kind)
        _require_text("status", self.status)
        _require_text("timestamp", self.timestamp)
        _string_tuple("changed_files", self.changed_files)
        _string_tuple("artifacts", self.artifacts)
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported EvidenceRecord schema_version: {self.schema_version}")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["changed_files"] = list(self.changed_files)
        data["artifacts"] = list(self.artifacts)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceRecord":
        return cls(
            evidence_id=data["evidence_id"],
            task_id=data["task_id"],
            kind=data["kind"],
            status=data["status"],
            timestamp=data["timestamp"],
            command=data.get("command"),
            environment=dict(data.get("environment", {})),
            changed_files=tuple(data.get("changed_files", ())),
            artifacts=tuple(data.get("artifacts", ())),
            details=dict(data.get("details", {})),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )

"""Validated execution contract shared by KMJ Forge tools."""

from dataclasses import dataclass
from enum import Enum


class PermissionClass(str, Enum):
    READ_ONLY = "read_only"
    WORKSPACE_WRITE = "workspace_write"
    EXTERNAL_WRITE = "external_write"
    PRIVILEGED = "privileged"


@dataclass(frozen=True, slots=True)
class ToolContract:
    name: str
    permission_class: PermissionClass
    timeout_seconds: int
    cancellable: bool
    max_retries: int
    audit_event: str
    error_schema: str
    evidence_schema: str

    @classmethod
    def create(
        cls,
        *,
        name: str,
        permission_class: PermissionClass,
        timeout_seconds: int,
        cancellable: bool,
        max_retries: int,
        audit_event: str,
        error_schema: str,
        evidence_schema: str,
    ) -> "ToolContract":
        identifiers = {
            "name": name,
            "audit_event": audit_event,
            "error_schema": error_schema,
            "evidence_schema": evidence_schema,
        }
        for field, value in identifiers.items():
            if type(value) is not str or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
        if not isinstance(permission_class, PermissionClass):
            raise TypeError("permission_class must be a PermissionClass")
        if type(timeout_seconds) is not int or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")
        if type(cancellable) is not bool:
            raise TypeError("cancellable must be boolean")
        if type(max_retries) is not int or not 0 <= max_retries <= 10:
            raise ValueError("max_retries must be an integer from 0 through 10")

        return cls(
            name=name.strip(),
            permission_class=permission_class,
            timeout_seconds=timeout_seconds,
            cancellable=cancellable,
            max_retries=max_retries,
            audit_event=audit_event.strip(),
            error_schema=error_schema.strip(),
            evidence_schema=evidence_schema.strip(),
        )

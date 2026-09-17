from __future__ import annotations

from dataclasses import dataclass
import re


_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")


@dataclass(frozen=True)
class SecretIsolationPolicy:
    """Fail-closed authorization boundary for named secret capabilities.

    The policy handles identifiers only. It never stores, reads, resolves, logs,
    returns, or injects secret material into a process or tool.
    """

    explicit_approval: bool = False
    allowed_bindings: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.allowed_bindings and not self.explicit_approval:
            raise ValueError("secret allowlist requires explicit approval")
        if len(set(self.allowed_bindings)) != len(self.allowed_bindings):
            raise ValueError("duplicate secret binding")
        for secret_name, consumer in self.allowed_bindings:
            if not self._valid_identifier(secret_name) or not self._valid_identifier(consumer):
                raise ValueError("secret and consumer must use normalized identifiers")

    @staticmethod
    def _valid_identifier(value: str) -> bool:
        return bool(value and value == value.strip() and _IDENTIFIER_RE.fullmatch(value))

    def allows(self, secret_name: str, consumer: str) -> bool:
        if not self.explicit_approval:
            return False
        if not self._valid_identifier(secret_name) or not self._valid_identifier(consumer):
            return False
        return (secret_name, consumer) in self.allowed_bindings

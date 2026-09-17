from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegressionResult:
    command: str
    passed: bool
    test_count: int
    failure_count: int

    def __post_init__(self) -> None:
        if not self.command.strip():
            raise ValueError("command must be non-empty")
        if self.test_count < 0 or self.failure_count < 0 or self.failure_count > self.test_count:
            raise ValueError("invalid regression counts")
        if self.passed and self.failure_count:
            raise ValueError("passing regression evidence cannot contain failures")


class RegressionEngine:
    def verify(self, commands: tuple[str, ...], results: tuple[RegressionResult, ...]) -> tuple[RegressionResult, ...]:
        expected = set(commands)
        observed = {item.command for item in results}
        missing = expected - observed
        if missing:
            raise ValueError("missing regression evidence: " + ", ".join(sorted(missing)))
        unexpected = observed - expected
        if unexpected:
            raise ValueError("unexpected regression evidence: " + ", ".join(sorted(unexpected)))
        if len(observed) != len(results):
            raise ValueError("duplicate regression evidence")
        failures = [item.command for item in results if not item.passed or item.failure_count]
        if failures:
            raise ValueError("regression verification failed: " + ", ".join(sorted(failures)))
        return tuple(sorted(results, key=lambda item: item.command))


__all__ = ["RegressionEngine", "RegressionResult"]

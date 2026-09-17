from __future__ import annotations

from dataclasses import dataclass
import re


_SUSPICIOUS_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?\b",
        r"\bdisregard\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions?|rules?)\b",
        r"\breveal\s+(?:the\s+)?system\s+prompt\b",
        r"\bdisable\s+(?:the\s+)?safety\s+(?:checks?|rules?|controls?)\b",
    )
)


@dataclass(frozen=True)
class PromptInjectionDecision:
    suspicious: bool
    requires_review: bool
    action_authorized: bool = False


@dataclass(frozen=True)
class PromptInjectionPolicy:
    """Fail-closed boundary for treating model-visible content as data, not authority.

    This classifier never grants tool or mutation authority. Suspicious or malformed
    content is surfaced for review; authorization remains the responsibility of a
    separate explicit policy boundary.
    """

    max_content_length: int = 65536

    def __post_init__(self) -> None:
        if self.max_content_length <= 0:
            raise ValueError("max_content_length must be positive")

    def evaluate(self, *, content: str, source_trusted: bool) -> PromptInjectionDecision:
        if not isinstance(content, str) or not content or len(content) > self.max_content_length:
            return PromptInjectionDecision(suspicious=True, requires_review=True)

        suspicious = any(pattern.search(content) for pattern in _SUSPICIOUS_PATTERNS)
        requires_review = suspicious or not source_trusted
        return PromptInjectionDecision(
            suspicious=suspicious,
            requires_review=requires_review,
            action_authorized=False,
        )

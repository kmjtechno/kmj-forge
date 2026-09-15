from __future__ import annotations

from kmj_forge.protocol import ModelCapability

from .policy import RoutingPolicy
from .registry import ModelRegistry


PROFILE_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "fast": (),
    "coding": ("coding",),
    "reasoning": ("reasoning",),
    "long_context": ("long_context",),
    "vision": ("vision",),
    "tool_use": ("tool_use",),
    "planning": ("planning",),
    "debugging": ("debugging",),
    "security": ("security_review",),
}


class NoEligibleModelError(RuntimeError):
    pass


def _requirements(profile: str, extra: tuple[str, ...]) -> frozenset[str]:
    if profile not in PROFILE_CAPABILITIES:
        raise ValueError(f"unknown routing profile: {profile}")
    return frozenset((*PROFILE_CAPABILITIES[profile], *extra))
def _eligible(
    registry: ModelRegistry,
    profile: str,
    policy: RoutingPolicy,
    required_capabilities: tuple[str, ...],
) -> list[ModelCapability]:
    required = _requirements(profile, required_capabilities)
    result: list[ModelCapability] = []
    for candidate in registry.models():
        if not candidate.available:
            continue
        if not registry.is_healthy(candidate):
            continue
        if not policy.allows(candidate):
            continue
        if not required.issubset(candidate.capabilities):
            continue
        result.append(candidate)
    return result


def _rank_key(model: ModelCapability) -> tuple[float, int, int, str, str]:
    total_price = model.input_price_per_million + model.output_price_per_million
    return (
        total_price,
        0 if model.local else 1,
        -model.context_window,
        model.provider,
        model.model_id,
    )
def route_model(
    registry: ModelRegistry,
    profile: str,
    policy: RoutingPolicy,
    *,
    required_capabilities: tuple[str, ...] = (),
) -> ModelCapability:
    candidates = _eligible(registry, profile, policy, required_capabilities)
    if not candidates:
        raise NoEligibleModelError(
            f"no eligible model for profile={profile} mode={policy.mode.value}"
        )
    return min(candidates, key=_rank_key)

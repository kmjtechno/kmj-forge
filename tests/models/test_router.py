import unittest

from kmj_forge.models import (
    ModelRegistry,
    NoEligibleModelError,
    RoutingMode,
    RoutingPolicy,
    route_model,
)
from kmj_forge.protocol import ModelCapability


def model(
    model_id: str,
    *,
    provider: str = "provider",
    capabilities: tuple[str, ...] = ("coding",),
    context_window: int = 32768,
    input_price: float = 0.0,
    output_price: float = 0.0,
    available: bool = True,
    local: bool = False,
) -> ModelCapability:
    return ModelCapability(
        provider=provider,
        model_id=model_id,
        capabilities=capabilities,
        context_window=context_window,
        input_price_per_million=input_price,
        output_price_per_million=output_price,
        available=available,
        local=local,
    )


class ModelRouterTests(unittest.TestCase):
    def test_free_only_never_selects_paid_model(self) -> None:
        registry = ModelRegistry()
        registry.register(model("paid", input_price=0.01, output_price=0.02))
        registry.register(model("free"))

        selected = route_model(registry, "coding", RoutingPolicy(RoutingMode.FREE_ONLY))

        self.assertEqual(selected.model_id, "free")
        self.assertTrue(selected.is_free)

    def test_free_only_blocks_when_only_paid_models_exist(self) -> None:
        registry = ModelRegistry([model("paid", input_price=0.01, output_price=0.02)])

        with self.assertRaisesRegex(NoEligibleModelError, "FREE_ONLY"):
            route_model(registry, "coding", RoutingPolicy(RoutingMode.FREE_ONLY))

    def test_local_only_rejects_cloud_models(self) -> None:
        registry = ModelRegistry([
            model("cloud", local=False),
            model("local", provider="local", local=True),
        ])
        selected = route_model(registry, "coding", RoutingPolicy(RoutingMode.LOCAL_ONLY))
        self.assertTrue(selected.local)

    def test_unavailable_or_incapable_models_are_filtered(self) -> None:
        registry = ModelRegistry([
            model("offline", available=False),
            model("reasoner", capabilities=("reasoning",)),
            model("coder", capabilities=("coding", "tool_use")),
        ])
        selected = route_model(
            registry,
            "coding",
            RoutingPolicy(RoutingMode.FREE_ONLY),
            required_capabilities=("tool_use",),
        )
        self.assertEqual(selected.model_id, "coder")
    def test_ties_are_deterministic_by_provider_and_model_id(self) -> None:
        registry = ModelRegistry([
            model("zeta", provider="z-provider"),
            model("alpha", provider="a-provider"),
        ])
        selected = route_model(registry, "coding", RoutingPolicy(RoutingMode.FREE_ONLY))
        self.assertEqual((selected.provider, selected.model_id), ("a-provider", "alpha"))

    def test_provider_allowlist_and_denylist_are_enforced(self) -> None:
        registry = ModelRegistry([
            model("a", provider="alpha"),
            model("b", provider="beta"),
        ])
        policy = RoutingPolicy(
            RoutingMode.FREE_ONLY,
            allowed_providers=("beta",),
            denied_providers=("alpha",),
        )
        selected = route_model(registry, "coding", policy)
        self.assertEqual(selected.provider, "beta")

    def test_failure_threshold_causes_policy_safe_failover(self) -> None:
        registry = ModelRegistry([model("a"), model("b")])
        registry.record_failure("provider", "a")
        registry.record_failure("provider", "a")
        registry.record_failure("provider", "a")
        selected = route_model(registry, "coding", RoutingPolicy(RoutingMode.FREE_ONLY))
        self.assertEqual(selected.model_id, "b")
    def test_profile_requires_matching_capability(self) -> None:
        registry = ModelRegistry([
            model("coder", capabilities=("coding",)),
            model("planner", capabilities=("planning", "reasoning")),
        ])
        selected = route_model(registry, "planning", RoutingPolicy(RoutingMode.FREE_ONLY))
        self.assertEqual(selected.model_id, "planner")

    def test_free_ties_prefer_local_before_cloud(self) -> None:
        registry = ModelRegistry([
            model("cloud-a", provider="alpha", local=False),
            model("local-z", provider="zeta", local=True),
        ])
        selected = route_model(registry, "coding", RoutingPolicy(RoutingMode.FREE_ONLY))
        self.assertEqual(selected.model_id, "local-z")

    def test_success_restores_model_after_transient_failures(self) -> None:
        registry = ModelRegistry([model("a"), model("b")])
        for _ in range(3):
            registry.record_failure("provider", "a")
        registry.record_success("provider", "a")
        selected = route_model(registry, "coding", RoutingPolicy(RoutingMode.FREE_ONLY))
        self.assertEqual(selected.model_id, "a")
    def test_any_mode_respects_user_price_caps(self) -> None:
        registry = ModelRegistry([
            model("expensive", input_price=2.0, output_price=3.0),
            model("cheap", input_price=0.2, output_price=0.3),
        ])
        policy = RoutingPolicy(
            RoutingMode.ANY,
            max_input_price_per_million=0.5,
            max_output_price_per_million=0.5,
        )
        selected = route_model(registry, "coding", policy)
        self.assertEqual(selected.model_id, "cheap")

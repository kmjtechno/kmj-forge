from __future__ import annotations

import unittest

from kmj_forge.models import ModelRegistry, NoEligibleModelError, RoutingMode, RoutingPolicy, route_model
from kmj_forge.protocol import ModelCapability


class ProviderFailureAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = RoutingPolicy(RoutingMode.FREE_ONLY)

    def test_unavailable_free_provider_does_not_fall_back_to_paid(self) -> None:
        registry = ModelRegistry((
            ModelCapability("free-provider", "free-code", ("coding",), 32_000, 0, 0, False, False),
            ModelCapability("paid-provider", "paid-code", ("coding",), 128_000, 1, 2, True, False),
        ))
        with self.assertRaises(NoEligibleModelError):
            route_model(registry, "coding", self.policy)

    def test_rate_limit_style_failure_threshold_blocks_without_paid_fallback(self) -> None:
        registry = ModelRegistry((
            ModelCapability("free-provider", "free-code", ("coding",), 32_000, 0, 0, True, False),
            ModelCapability("paid-provider", "paid-code", ("coding",), 128_000, 1, 2, True, False),
        ), failure_threshold=1)
        registry.record_failure("free-provider", "free-code")
        self.assertEqual(registry.failure_count("free-provider", "free-code"), 1)
        with self.assertRaises(NoEligibleModelError):
            route_model(registry, "coding", self.policy)

    def test_paid_only_registry_is_blocked_in_free_only_mode(self) -> None:
        registry = ModelRegistry((
            ModelCapability("paid-provider", "paid-code", ("coding",), 128_000, 1, 2, True, False),
        ))
        with self.assertRaises(NoEligibleModelError):
            route_model(registry, "coding", self.policy)


if __name__ == "__main__":
    unittest.main()

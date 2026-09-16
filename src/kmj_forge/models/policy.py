from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kmj_forge.protocol import ModelCapability


class RoutingMode(str, Enum):
    FREE_ONLY = "FREE_ONLY"
    LOCAL_ONLY = "LOCAL_ONLY"
    ANY = "ANY"


@dataclass(frozen=True, slots=True)
class RoutingPolicy:
    mode: RoutingMode
    allowed_providers: tuple[str, ...] = ()
    denied_providers: tuple[str, ...] = ()
    max_input_price_per_million: float | None = None
    max_output_price_per_million: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("max_input_price_per_million", self.max_input_price_per_million),
            ("max_output_price_per_million", self.max_output_price_per_million),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
    def allows(self, model: ModelCapability) -> bool:
        if self.allowed_providers and model.provider not in self.allowed_providers:
            return False
        if model.provider in self.denied_providers:
            return False
        if self.mode is RoutingMode.FREE_ONLY and not model.is_free:
            return False
        if self.mode is RoutingMode.LOCAL_ONLY and not model.local:
            return False
        if (
            self.max_input_price_per_million is not None
            and model.input_price_per_million > self.max_input_price_per_million
        ):
            return False
        if (
            self.max_output_price_per_million is not None
            and model.output_price_per_million > self.max_output_price_per_million
        ):
            return False
        return True

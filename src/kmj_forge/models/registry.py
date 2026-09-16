from __future__ import annotations

from collections.abc import Iterable

from kmj_forge.protocol import ModelCapability


ModelKey = tuple[str, str]


class ModelRegistry:
    def __init__(
        self,
        models: Iterable[ModelCapability] = (),
        *,
        failure_threshold: int = 3,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        self._failure_threshold = failure_threshold
        self._models: dict[ModelKey, ModelCapability] = {}
        self._failures: dict[ModelKey, int] = {}
        for candidate in models:
            self.register(candidate)

    def register(self, model: ModelCapability) -> None:
        self._models[(model.provider, model.model_id)] = model
    def models(self) -> tuple[ModelCapability, ...]:
        return tuple(
            self._models[key]
            for key in sorted(self._models)
        )

    def record_failure(self, provider: str, model_id: str) -> None:
        key = (provider, model_id)
        if key not in self._models:
            raise KeyError(f"unknown model: {provider}/{model_id}")
        self._failures[key] = self._failures.get(key, 0) + 1

    def record_success(self, provider: str, model_id: str) -> None:
        key = (provider, model_id)
        if key not in self._models:
            raise KeyError(f"unknown model: {provider}/{model_id}")
        self._failures[key] = 0

    def is_healthy(self, model: ModelCapability) -> bool:
        key = (model.provider, model.model_id)
        return self._failures.get(key, 0) < self._failure_threshold

    def failure_count(self, provider: str, model_id: str) -> int:
        return self._failures.get((provider, model_id), 0)

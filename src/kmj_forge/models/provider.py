from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, Protocol, runtime_checkable

from kmj_forge.protocol import ModelCapability


@runtime_checkable
class ModelProvider(Protocol):
    def list_models(self) -> Iterable[ModelCapability]: ...

    def generate(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]: ...

    def stream(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> Iterator[dict[str, Any]]: ...
    def tool_call(
        self,
        model_id: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]: ...

    def cancel(self, request_id: str) -> None: ...

    def usage(self, request_id: str) -> dict[str, Any]: ...

    def health_check(self) -> bool: ...

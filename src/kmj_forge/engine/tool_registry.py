"""Fail-closed registry for validated KMJ Forge tool contracts."""

from types import MappingProxyType
from typing import Mapping

from .tool_contract import ToolContract


class ToolRegistry:
    """Register and resolve immutable tool contracts by unique name."""

    def __init__(self) -> None:
        self._contracts: dict[str, ToolContract] = {}

    def register(self, contract: ToolContract) -> None:
        if not isinstance(contract, ToolContract):
            raise TypeError("contract must be a ToolContract")
        if contract.name in self._contracts:
            raise ValueError(f"tool contract already registered: {contract.name}")
        self._contracts[contract.name] = contract

    def require(self, name: str) -> ToolContract:
        if type(name) is not str or not name.strip():
            raise ValueError("tool name must be a non-empty string")
        normalized = name.strip()
        try:
            return self._contracts[normalized]
        except KeyError:
            raise KeyError(f"tool contract is not registered: {normalized}") from None

    def snapshot(self) -> Mapping[str, ToolContract]:
        ordered = {name: self._contracts[name] for name in sorted(self._contracts)}
        return MappingProxyType(ordered)

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import re


_HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$")
_BLOCKED_HOSTS = frozenset({"localhost", "169.254.169.254"})


@dataclass(frozen=True)
class NetworkPolicy:
    """Fail-closed network authorization boundary.

    The policy only decides whether a destination is permitted. It never opens
    sockets, resolves DNS, performs HTTP requests, or changes host networking.
    """

    explicit_approval: bool = False
    allowed_hosts: tuple[str, ...] = ()
    allowed_schemes: tuple[str, ...] = ("https",)
    allowed_ports: tuple[int, ...] = (443,)

    def __post_init__(self) -> None:
        if self.allowed_hosts and not self.explicit_approval:
            raise ValueError("network allowlist requires explicit approval")
        for host in self.allowed_hosts:
            if not self._valid_host(host):
                raise ValueError("allowed host must be a normalized hostname or IP address")
        if any(scheme != scheme.lower() or not scheme.isalpha() for scheme in self.allowed_schemes):
            raise ValueError("network scheme must be lowercase alphabetic text")
        if any(port < 1 or port > 65535 for port in self.allowed_ports):
            raise ValueError("network port must be between 1 and 65535")

    @staticmethod
    def _valid_host(host: str) -> bool:
        if not host or host != host.strip() or "://" in host or "/" in host or "@" in host:
            return False
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return bool(_HOST_RE.fullmatch(host))

    @staticmethod
    def _blocked(host: str) -> bool:
        normalized = host.lower().rstrip(".")
        if normalized in _BLOCKED_HOSTS or normalized.endswith(".localhost"):
            return True
        try:
            address = ipaddress.ip_address(normalized)
        except ValueError:
            return False
        return not address.is_global

    def allows(self, scheme: str, host: str, port: int) -> bool:
        if not self.explicit_approval or not self._valid_host(host):
            return False
        normalized = host.lower().rstrip(".")
        if self._blocked(normalized):
            return False
        approved_hosts = {item.lower().rstrip(".") for item in self.allowed_hosts}
        return (
            normalized in approved_hosts
            and scheme in self.allowed_schemes
            and port in self.allowed_ports
        )

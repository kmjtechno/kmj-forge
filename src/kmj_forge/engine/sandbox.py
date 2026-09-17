from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath


class SandboxMode(str, Enum):
    NONE = "none"
    RESTRICTED = "restricted"
    CONTAINER = "container"
    VM = "vm"
    REMOTE_EPHEMERAL = "remote_ephemeral"


@dataclass(frozen=True)
class SandboxPolicy:
    """Fail-closed policy boundary for Forge execution isolation.

    This object describes permissions only. It never launches processes,
    containers, VMs, network connections, or filesystem mutations.
    """

    mode: SandboxMode = SandboxMode.RESTRICTED
    workspace_root: str = "/workspace"
    explicit_approval: bool = False
    network_allowed: bool = False
    privileged_execution_allowed: bool = False

    def __post_init__(self) -> None:
        root = PurePosixPath(self.workspace_root)
        if not root.is_absolute() or ".." in root.parts:
            raise ValueError("workspace_root must be an absolute normalized path")
        if self.mode is SandboxMode.NONE and not self.explicit_approval:
            raise ValueError("sandbox mode 'none' requires explicit approval")
        if self.privileged_execution_allowed and not self.explicit_approval:
            raise ValueError("privileged execution requires explicit approval")
        if self.network_allowed and not self.explicit_approval:
            raise ValueError("network access requires explicit approval")

    @property
    def host_filesystem_allowed(self) -> bool:
        return self.mode is SandboxMode.NONE and self.explicit_approval

    def allows_path(self, path: str) -> bool:
        candidate = PurePosixPath(path)
        if not candidate.is_absolute() or ".." in candidate.parts:
            return False
        if self.host_filesystem_allowed:
            return True
        root = PurePosixPath(self.workspace_root)
        return candidate == root or root in candidate.parents

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass(frozen=True)
class DeviceEndpoint:
    address: str
    port: int = 830  # NETCONF default (can override)


@dataclass(frozen=True)
class DevicePlatform:
    vendor: str
    os: str
    model: Optional[str] = None


@dataclass(frozen=True)
class DeviceCredentialsRef:
    name: str
    namespace: Optional[str] = None


@dataclass(frozen=True)
class NetworkDeviceSpec:
    """Normalized device spec extracted from the NetworkDevice CR."""
    name: str
    namespace: str
    endpoint: DeviceEndpoint
    platform: DevicePlatform
    transport: str  # gnmi/netconf/rest/cli
    credentials_ref: Optional[DeviceCredentialsRef] = None
    role: Optional[str] = None


@dataclass
class ApplyResult:
    ok: bool
    detail: str = ""
    changed: bool = False
    facts: Optional[Dict[str, Any]] = None


class DeviceAdapter(Protocol):
    """
    Adapter interface: controller talks to this, and adapter talks to devices.
    """

    def validate_intent(self, intent: Dict[str, Any]) -> ApplyResult:
        """Validate intent structure (no device calls needed)."""
        ...

    def apply_intent(self, device: NetworkDeviceSpec, intent: Dict[str, Any], dry_run: bool = False) -> ApplyResult:
        """Apply desired intent to a device (may call the device)."""
        ...

    def read_facts(self, device: NetworkDeviceSpec) -> ApplyResult:
        """Read basic facts/state from a device (reachability/capabilities)."""
        ...

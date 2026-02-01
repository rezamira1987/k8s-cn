from __future__ import annotations

from typing import Any, Dict

from adapters.base import ApplyResult, DeviceAdapter, NetworkDeviceSpec


class DummyAdapter(DeviceAdapter):
    def validate_intent(self, intent: Dict[str, Any]) -> ApplyResult:
        # Very simple validation: intent must be a dict (already), and not empty
        if not intent:
            return ApplyResult(ok=False, detail="intent is empty")
        return ApplyResult(ok=True, detail="intent looks ok (dummy validation)")

    def apply_intent(self, device: NetworkDeviceSpec, intent: Dict[str, Any], dry_run: bool = False) -> ApplyResult:
        action = "DRY-RUN" if dry_run else "APPLY"
        keys = sorted(intent.keys())
        return ApplyResult(
            ok=True,
            changed=not dry_run,
            detail=f"[dummy] {action} intent to {device.namespace}/{device.name} at {device.endpoint.address}:{device.endpoint.port} keys={keys}",
            facts={"vendor": device.platform.vendor, "os": device.platform.os},
        )

    def read_facts(self, device: NetworkDeviceSpec) -> ApplyResult:
        return ApplyResult(
            ok=True,
            changed=False,
            detail=f"[dummy] read_facts from {device.namespace}/{device.name} at {device.endpoint.address}:{device.endpoint.port}",
            facts={"vendor": device.platform.vendor, "os": device.platform.os},
        )

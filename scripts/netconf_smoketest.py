from __future__ import annotations

import os
import sys

from adapters.netconf import NetconfClient, NetconfConnection


def must_getenv(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"Missing env var: {key}", file=sys.stderr)
        sys.exit(2)
    return val


def main() -> int:
    host = os.getenv("NETCONF_HOST", "85.215.60.54")
    port = int(os.getenv("NETCONF_PORT", "830"))
    user = must_getenv("NETCONF_USER")
    pwd = must_getenv("NETCONF_PASS")

    client = NetconfClient(
        NetconfConnection(
            host=host,
            port=port,
            username=user,
            password=pwd,
            hostkey_verify=False,
            timeout=30,
        )
    )

    print(f"Connecting to {host}:{port} ...")
    client.connect()
    print("Connected ✅")

    caps = client.server_capabilities()
    print(f"Server capabilities: {len(caps)} (showing first 5)")
    for c in caps[:5]:
        print(f"  - {c}")

    print("Running get-config (running) ...")
    xml = client.get_running_config()
    print(f"Got reply XML length: {len(xml)} ✅")

    client.close()
    print("Session closed ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

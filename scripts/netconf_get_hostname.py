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

    # Subtree filter: native hostname (Cisco IOS-XE)
    # Note: this is vendor-specific on purpose for a tiny first win.
    filter_xml = """
    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
      <hostname/>
    </native>
    """.strip()

    print(f"Connecting to {host}:{port} ...")
    client.connect()
    print("Connected ✅")

    xml = client.get_config(source="running", filter_xml=filter_xml)
    print(xml)  # print full XML reply for now

    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

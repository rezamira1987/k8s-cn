from __future__ import annotations

import os
import sys
from adapters.netconf import NetconfClient, NetconfConnection

def must_getenv(key: str) -> str:
    v = os.getenv(key)
    if not v:
        print(f"Missing env var: {key}", file=sys.stderr)
        sys.exit(2)
    return v

def main() -> int:
    host = os.getenv("NETCONF_HOST", "85.215.60.54")
    port = int(os.getenv("NETCONF_PORT", "830"))
    user = must_getenv("NETCONF_USER")
    pwd = must_getenv("NETCONF_PASS")

    c = NetconfClient(NetconfConnection(host=host, port=port, username=user, password=pwd))
    c.connect()
    caps = c.server_capabilities()
    c.close()

    def has(x: str) -> bool:
        return any(x in cap for cap in caps)

    print("candidate:", has("capability:candidate"))
    print("confirmed-commit:", has("capability:confirmed-commit"))
    print("validate:", has("capability:validate"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

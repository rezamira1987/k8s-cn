from __future__ import annotations

import os
import sys
from ncclient import manager


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

    print(f"Connecting to {host}:{port} ...")
    with manager.connect(
        host=host,
        port=port,
        username=user,
        password=pwd,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        timeout=30,
    ) as m:
        print("Connected ✅")
        print("Confirming commit ...")
        m.commit()  # confirm the previously confirmed-commit
        print("✅ Commit confirmed (now permanent).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

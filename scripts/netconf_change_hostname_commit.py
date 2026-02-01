from __future__ import annotations

import os
import sys

from lxml import etree
from ncclient import manager

NC_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"
IOSXE_NATIVE_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"


def must_getenv(key: str) -> str:
    v = os.getenv(key)
    if not v:
        print(f"Missing env var: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def build_hostname_config(new_hostname: str) -> etree._Element:
    config_el = etree.Element(f"{{{NC_NS}}}config")
    native_el = etree.SubElement(config_el, f"{{{IOSXE_NATIVE_NS}}}native")
    hostname_el = etree.SubElement(native_el, f"{{{IOSXE_NATIVE_NS}}}hostname")
    hostname_el.text = new_hostname
    return config_el


def main() -> int:
    host = os.getenv("NETCONF_HOST", "85.215.60.54")
    port = int(os.getenv("NETCONF_PORT", "830"))
    user = must_getenv("NETCONF_USER")
    pwd = must_getenv("NETCONF_PASS")
    new_hostname = must_getenv("NEW_HOSTNAME")

    cfg = build_hostname_config(new_hostname)

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

        m.lock("candidate")
        try:
            print("Edit-config (candidate) ...")
            m.edit_config(target="candidate", config=cfg, default_operation="merge")

            print("Validate (candidate) ...")
            m.validate(source="candidate")

            print("Commit (permanent) ...")
            m.commit()

            print("✅ Committed permanently.")
        finally:
            try:
                m.unlock("candidate")
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

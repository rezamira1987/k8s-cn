from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ncclient import manager


@dataclass(frozen=True)
class NetconfConnection:
    host: str
    port: int = 830
    username: str = ""
    password: str = ""
    hostkey_verify: bool = False
    timeout: int = 30


class NetconfClient:
    """
    Minimal NETCONF client:
    - connect
    - get-config (running)
    No edit-config yet.
    """

    def __init__(self, conn: NetconfConnection):
        self.conn = conn
        self._m: Optional[manager.Manager] = None

    def connect(self) -> None:
        self._m = manager.connect(
            host=self.conn.host,
            port=self.conn.port,
            username=self.conn.username,
            password=self.conn.password,
            hostkey_verify=self.conn.hostkey_verify,
            allow_agent=False,
            look_for_keys=False,
            timeout=self.conn.timeout,
        )

    def close(self) -> None:
        if self._m is not None:
            self._m.close_session()
            self._m = None

    def server_capabilities(self) -> list[str]:
        if self._m is None:
            raise RuntimeError("not connected")
        return list(self._m.server_capabilities)

    def get_running_config(self, filter_xml: Optional[str] = None) -> str:
        """
        Returns running config as XML string.
        If filter_xml provided, it must be a valid NETCONF subtree filter XML.
        """
        if self._m is None:
            raise RuntimeError("not connected")

        if filter_xml:
            reply = self._m.get_config(source="running", filter=("subtree", filter_xml))
        else:
            reply = self._m.get_config(source="running")
        return reply.xml

    def get_config(self, source: str = "running", filter_xml: Optional[str] = None) -> str:
        if self._m is None:
            raise RuntimeError("not connected")

        if filter_xml:
            reply = self._m.get_config(source=source, filter=("subtree", filter_xml))
        else:
            reply = self._m.get_config(source=source)
        return reply.xml

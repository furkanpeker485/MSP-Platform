"""Platform istemcisi.

Bağlantıyı her zaman ajan kurar: giden 443. Müşterinin güvenlik duvarında
HR için gelen kural açılmaz.
"""
from __future__ import annotations

import httpx
import structlog

from hragent.config import Config

log = structlog.get_logger(__name__)


class Client:
    def __init__(self, config: Config) -> None:
        self.config = config

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.config.token}"} if self.config.token else {}

    def enroll(self, inventory: dict) -> str:
        """Kayıt: cihaza özel belirteç alınır. Kayıt kodu tek kullanımlıktır."""
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{self.config.platform_url}/agents/enroll",
                json={
                    "enrollment_code": self.config.enrollment_code,
                    "tenant": self.config.tenant,
                    "device_uuid": inventory["uuid"],
                    "hostname": inventory["hostname"],
                    "serial": inventory.get("serial"),
                    "os_family": inventory.get("os_family"),
                },
            )
            resp.raise_for_status()
            return resp.json()["token"]

    def checkin(self, observed: dict, inventory: dict) -> dict:
        """Durum bildirilir, karşılığında yapılacak görevler alınır."""
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{self.config.platform_url}/agents/checkin",
                headers=self._headers(),
                json={"observed": observed, "inventory": inventory},
            )
            resp.raise_for_status()
            return resp.json()

"""SIEM — kayıt kaynakları ve korelasyon.

Ölü bir kaynak sessiz bir kaynak gibi görünür; bu yüzden her kaynak için saniyedeki
olay taban çizgisi kurulur ve sessizlik alarm üretir.
"""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


async def call(op: str, *, tenant: str, **params) -> dict:
    return await {"ensure_source": ensure_source, "ensure_rule": ensure_rule}[op](
        tenant=tenant, **params
    )


async def ensure_source(*, tenant: str, name: str, parser: str, eps_baseline: int = 1, **_) -> dict:
    return await request(
        "POST", f"{settings().siem_url.rstrip('/')}/api/sources",
        token=settings().siem_token,
        json={
            "tenant": tenant,
            "name": name,
            "parser": parser,
            "silence_alert_minutes": 15,
            "eps_baseline": eps_baseline,
        },
    )


async def ensure_rule(*, tenant: str, name: str, mitre: str | None = None, **_) -> dict:
    return await request(
        "POST", f"{settings().siem_url.rstrip('/')}/api/rules",
        token=settings().siem_token,
        json={"tenant": tenant, "name": name, "mitre": mitre},
    )

"""NetBox — envanter ve doğruluk kaynağı.

Her şeyin sağlık kontrolü buna karşı çözümlenir: 'var olanı envanterle karşılaştır'.
Kimlik anahtarı hostname veya ağ kartı kimliği DEĞİL, ajan kimliği + seri numarasıdır —
klonlanmış sanal makineler ikisini de paylaşır.
"""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


def _url(path: str) -> str:
    return f"{settings().netbox_url.rstrip('/')}/api/{path.lstrip('/')}"


async def call(op: str, *, tenant: str, **params) -> dict:
    return await {
        "ensure_tenant": ensure_tenant,
        "ensure_device": ensure_device,
        "decommission": decommission,
        "list_devices": list_devices,
    }[op](tenant=tenant, **params)


async def ensure_tenant(*, tenant: str, **_) -> dict:
    return await request(
        "POST", _url("tenancy/tenants/"),
        token=settings().netbox_token, prefix="Token",
        json={"name": tenant, "slug": tenant},
    )


async def ensure_device(*, tenant: str, uuid: str, serial: str | None = None, **fields) -> dict:
    """Ajan kimliği birincil anahtardır; seri numarası ikincil doğrulamadır."""
    return await request(
        "POST", _url("dcim/devices/"),
        token=settings().netbox_token, prefix="Token",
        json={
            "tenant": {"slug": tenant},
            "custom_fields": {"agent_uuid": uuid},
            "serial": serial or "",
            **fields,
        },
    )


async def list_devices(*, tenant: str, **_) -> dict:
    return await request(
        "GET", _url(f"dcim/devices/?tenant={tenant}&limit=1000"),
        token=settings().netbox_token, prefix="Token",
    )


async def decommission(*, tenant: str, uuid: str, **_) -> dict:
    """Söküm: kayıt silinmez, durumu değişir — envanter geçmişi korunur."""
    return await request(
        "PATCH", _url(f"dcim/devices/?cf_agent_uuid={uuid}"),
        token=settings().netbox_token, prefix="Token",
        json={"status": "decommissioning", "tenant": {"slug": tenant}},
    )

"""Kasa — her hizmetin ilk adımı buraya yazmaktır.

Kiracı ayrışması yol düzeyinde zorunludur: `tenants/<slug>/...`. Bir müşteri için
çalışan iş akışı başka müşterinin yolunu isterse kasa reddeder.
"""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


class CrossTenantAccess(Exception):
    """A kiracısı için çalışan iş, B kiracısının alanını isteyemez."""


def _path(tenant: str, key: str) -> str:
    if key.startswith("tenants/") and not key.startswith(f"tenants/{tenant}/"):
        raise CrossTenantAccess(f"{tenant} → {key}")
    return f"tenants/{tenant}/{key.lstrip('/')}"


async def call(op: str, *, tenant: str, **params) -> dict:
    return await {"store_access": store_access, "has": has, "revoke": revoke}[op](
        tenant=tenant, **params
    )


async def store_access(*, tenant: str, keys: list[str] | None = None, store: str = "", **_) -> dict:
    """Erişim bilgilerini ilgili kasaya yazar.

    `store` hangi kasanın kullanılacağını söyler: `.env`, `ansible-vault`
    veya `n8n-credentials`. Değer platforma hiç uğramaz; yalnız referansı tutulur.
    """
    return await request(
        "POST", f"{settings().vault_addr.rstrip('/')}/v1/secret/data/{_path(tenant, 'access')}",
        token=settings().vault_token, header="X-Vault-Token", prefix="",
        json={"data": {"store": store, "keys": keys or [], "status": "pending-intake"}},
    )


async def has(*, tenant: str, key: str, **_) -> bool:
    try:
        await request(
            "GET", f"{settings().vault_addr.rstrip('/')}/v1/secret/data/{_path(tenant, key)}",
            token=settings().vault_token, header="X-Vault-Token", prefix="",
        )
        return True
    except RuntimeError:
        return False


async def revoke(*, tenant: str, key: str = "", **_) -> dict:
    """Çıkış sürecinin parçası: anahtar iptal edilir ve değiştirilir."""
    return await request(
        "DELETE", f"{settings().vault_addr.rstrip('/')}/v1/secret/metadata/{_path(tenant, key)}",
        token=settings().vault_token, header="X-Vault-Token", prefix="",
    )

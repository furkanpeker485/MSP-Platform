"""Ajan kimliği ve kiracı sınırı.

Kasa, her müşterinin sırlarını tutar. Acme'nin ajanı, Contoso'nun tanımını isteyememelidir;
bu yüzden her istek cihaz kimliğine bağlı bir belirteçle imzalanır ve kiracı sunucuda çözülür.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException

from app.config import settings

TOKEN_TTL = timedelta(hours=12)


SEP = "|"  # ISO zaman damgası iki nokta içerdiği için ayraç olarak ':' kullanılamaz


def issue_agent_token(*, tenant: str, device_uuid: str) -> str:
    """Kayıt sırasında cihaza özel belirteç üretir."""
    if SEP in tenant or SEP in device_uuid:
        raise ValueError(f"kiracı veya cihaz kimliğinde ayraç karakteri: {SEP}")
    issued = datetime.now(timezone.utc).isoformat()
    body = SEP.join((tenant, device_uuid, issued))
    mac = hmac.new(settings().agent_enroll_secret.encode(), body.encode(), hashlib.sha256)
    return SEP.join((body, mac.hexdigest()))


def verify_agent_token(token: str) -> tuple[str, str]:
    """(tenant, device_uuid) döndürür; geçersizse 401."""
    try:
        tenant, device_uuid, issued, mac = token.split(SEP)
    except ValueError:
        raise HTTPException(401, "bozuk belirteç") from None

    body = SEP.join((tenant, device_uuid, issued))
    expected = hmac.new(
        settings().agent_enroll_secret.encode(), body.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(mac, expected):
        raise HTTPException(401, "imza doğrulanamadı")
    if datetime.fromisoformat(issued) + TOKEN_TTL < datetime.now(timezone.utc):
        raise HTTPException(401, "belirteç süresi doldu")
    return tenant, device_uuid


async def agent_identity(authorization: str = Header(default="")) -> tuple[str, str]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "yetki başlığı yok")
    return verify_agent_token(authorization.removeprefix("Bearer ").strip())


def new_enrollment_code() -> str:
    return secrets.token_urlsafe(24)

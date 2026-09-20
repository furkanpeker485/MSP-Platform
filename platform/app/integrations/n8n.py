"""n8n — orkestratör. E şeridindeki takvimli işleri kurar."""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


async def ensure_schedule(*, workflow: str, tenant: str, cron: str) -> dict:
    return await request(
        "POST", f"{settings().awx_url.rstrip('/')}/n8n/api/v1/workflows/{workflow}/activate",
        token=settings().awx_token,
        json={"tenant": tenant, "cron": cron},
    )

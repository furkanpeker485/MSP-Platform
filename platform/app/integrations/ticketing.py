"""Destek kaydı sistemi — F şeridinin arayüzü ve paketlerin şekillendiği yer."""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


async def call(op: str, *, tenant: str, **params) -> dict:
    return await {
        "ensure_tenant": ensure_tenant,
        "ensure_queue": ensure_queue,
        "ensure_sla": ensure_sla,
        "create_work_order": create_work_order,
    }[op](tenant=tenant, **params)


async def ensure_tenant(*, tenant: str, name: str | None = None, **_) -> dict:
    return await request(
        "POST", f"{settings().ticketing_url.rstrip('/')}/entities",
        token=settings().ticketing_token,
        json={"slug": tenant, "name": name or tenant},
    )


async def ensure_queue(*, tenant: str, queue: str, **_) -> dict:
    return await request(
        "POST", f"{settings().ticketing_url.rstrip('/')}/queues",
        token=settings().ticketing_token,
        json={"tenant": tenant, "name": queue},
    )


async def ensure_sla(*, tenant: str, matrix: dict | None = None, **_) -> dict:
    return await request(
        "POST", f"{settings().ticketing_url.rstrip('/')}/sla",
        token=settings().ticketing_token,
        json={"tenant": tenant, "matrix": matrix or {"P1": "4h", "P2": "8h", "P3": "NBD"}},
    )


async def create_work_order(
    *, tenant: str, title: str, queue: str = "saha", sla: str | None = None,
    acceptance: str | None = None, **_
) -> dict:
    """İnsan işi de kayıt altındadır: kabul kriteri olmadan iş emri kapanmaz."""
    return await request(
        "POST", f"{settings().ticketing_url.rstrip('/')}/tickets",
        token=settings().ticketing_token,
        json={
            "tenant": tenant,
            "title": title,
            "queue": queue,
            "sla": sla,
            "acceptance_criteria": acceptance,
            "requires_signoff": True,
        },
    )

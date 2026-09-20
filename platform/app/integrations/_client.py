"""Ortak HTTP istemcisi: yeniden deneme, zaman aşımı ve kimlik başlığı tek yerde."""
from __future__ import annotations

import asyncio
from typing import Any

import httpx
import structlog

log = structlog.get_logger(__name__)

RETRY_STATUS = {429, 502, 503, 504}


async def request(
    method: str,
    url: str,
    *,
    token: str = "",
    header: str = "Authorization",
    prefix: str = "Bearer",
    attempts: int = 3,
    **kwargs: Any,
) -> dict:
    headers = dict(kwargs.pop("headers", {}))
    if token:
        headers[header] = f"{prefix} {token}".strip()

    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.request(method, url, headers=headers, **kwargs)
            if resp.status_code in RETRY_STATUS and attempt < attempts:
                await asyncio.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except httpx.HTTPError as exc:
            last = exc
            if attempt == attempts:
                break
            await asyncio.sleep(2 ** attempt)
    log.error("entegrasyon_hatasi", url=url, error=str(last))
    raise RuntimeError(f"{url}: {last}")

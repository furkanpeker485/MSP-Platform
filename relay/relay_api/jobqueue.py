"""Relay iş kuyruğu.

Platform görevi buraya bırakır; ajan bir sonraki yoklamasında çeker. Ajan hiçbir zaman
aranmaz — yön her zaman içeriden dışarıdır. Kuyruk cihaz kimliğine göre bölümlenir ki
bir cihazın işi başka cihaza gitmesin.
"""
from __future__ import annotations

import json
import os

import redis.asyncio as redis
import structlog

log = structlog.get_logger(__name__)

TTL_SECONDS = 24 * 3600
_client: redis.Redis | None = None


def client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True
        )
    return _client


def _key(tenant: str, device_uuid: str) -> str:
    return f"queue:{tenant}:{device_uuid or 'unassigned'}"


async def push(tenant: str, task: dict) -> dict:
    key = _key(tenant, task.get("device_uuid", ""))
    r = client()
    await r.rpush(key, json.dumps(task, ensure_ascii=False))
    await r.expire(key, TTL_SECONDS)
    depth = await r.llen(key)
    log.info("gorev_kuyruga_alindi", kuyruk=key, derinlik=depth)
    return {"queued": True, "queue": key, "depth": depth}


async def pop_all(tenant: str, device_uuid: str, limit: int = 50) -> list[dict]:
    """Ajan yoklamasında bekleyen görevleri alır. Alınan görev kuyruktan düşer."""
    key = _key(tenant, device_uuid)
    r = client()
    out: list[dict] = []
    for _ in range(limit):
        raw = await r.lpop(key)
        if raw is None:
            break
        out.append(json.loads(raw))
    # cihaza özel kuyruk boşsa, atanmamış havuzdan da al
    if not out and device_uuid:
        shared = _key(tenant, "")
        for _ in range(limit):
            raw = await r.lpop(shared)
            if raw is None:
                break
            out.append(json.loads(raw))
    return out


async def depth(tenant: str, device_uuid: str = "") -> int:
    return int(await client().llen(_key(tenant, device_uuid)))

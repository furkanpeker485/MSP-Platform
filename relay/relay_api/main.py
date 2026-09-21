"""Relay API — ajanların tek muhatabı.

Ajan platformu doğrudan görmez; her şey relay üzerinden geçer. Bu, müşteri ağından
dışarı tek bir çıkış noktası olmasını sağlar.
"""
from __future__ import annotations

import os

import structlog
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

import jobqueue  # stdlib 'queue' ile çakışmaması için bilerek bu ad

log = structlog.get_logger(__name__)
app = FastAPI(title="MSP Site Relay", version="0.1.0")

TENANT = os.environ.get("RELAY_TENANT", "")
RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "")


class Task(BaseModel):
    service_id: str
    task_id: str
    action: str
    params: dict = {}
    device_uuid: str | None = None
    teardown: bool = False


class Checkin(BaseModel):
    device_uuid: str
    observed: dict = {}
    inventory: dict = {}


def _require_platform(authorization: str) -> None:
    if not RELAY_TOKEN or authorization != f"Bearer {RELAY_TOKEN}":
        raise HTTPException(401, "yetkisiz")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "tenant": TENANT, "queue_depth": await jobqueue.depth(TENANT)}


@app.post("/queue")
async def enqueue(task: Task, authorization: str = Header(default="")) -> dict:
    """Platform görev bırakır."""
    _require_platform(authorization)
    return await jobqueue.push(TENANT, task.model_dump())


@app.post("/agents/checkin")
async def checkin(req: Checkin) -> dict:
    """Ajan yoklaması: durumunu bildirir, bekleyen görevlerini alır."""
    tasks = await jobqueue.pop_all(TENANT, req.device_uuid)
    log.info("ajan_yoklamasi", cihaz=req.device_uuid, gorev=len(tasks))
    return {"tasks": tasks, "next_checkin": int(os.environ.get("CHECKIN_SECONDS", "45"))}

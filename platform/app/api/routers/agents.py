"""Ajan uçları. Bağlantıyı her zaman ajan kurar; platform ajanı hiç aramaz."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from pydantic import BaseModel

from app.catalog import load_catalog
from app.config import settings
from app.security import agent_identity, issue_agent_token
from app.models import Lane
from app.services.spec_compiler import compile_spec

router = APIRouter(prefix="/agents", tags=["agents"])
_catalog = load_catalog(settings().catalog_dir)


class EnrollRequest(BaseModel):
    enrollment_code: str
    tenant: str
    device_uuid: str
    hostname: str
    serial: Optional[str] = None
    os_family: Optional[str] = None
    role: str = "workstation"


class ReportRequest(BaseModel):
    observed: dict[str, str] = {}
    inventory: dict = {}


@router.post("/enroll")
async def enroll(req: EnrollRequest) -> dict:
    if not settings().agent_enroll_secret:
        raise HTTPException(503, "kayıt sırrı tanımlı değil")
    token = issue_agent_token(tenant=req.tenant, device_uuid=req.device_uuid)
    return {"token": token, "checkin_seconds": settings().agent_checkin_seconds}


@router.post("/checkin")
async def checkin(req: ReportRequest, identity: tuple = Depends(agent_identity)) -> dict:
    """Ajan durumunu bildirir, karşılığında olması gereken ayarları alır."""
    tenant, device_uuid = identity
    spec = compile_spec(catalog=_catalog, tenant=tenant, entitlements=_entitlements_for(tenant))
    todo = [t for t in spec.by_lane(Lane.A) if req.observed.get(f"{t.service_id}/{t.task_id}") != "ok"]
    return {
        "device": device_uuid,
        "seen_at": datetime.now(timezone.utc).isoformat(),
        "next_checkin": settings().agent_checkin_seconds,
        "tasks": [
            {"service_id": t.service_id, "task_id": t.task_id,
             "action": t.action, "params": t.params}
            for t in todo
        ],
    }


def _entitlements_for(tenant: str) -> list[str]:
    """Gerçek kurulumda veritabanından gelir; burada katalogdaki tümü."""
    return [s.id for s in _catalog]

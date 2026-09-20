"""Katalog uçları. Sitedeki hizmet kimliği ile buradaki kimlik aynıdır."""
from fastapi import APIRouter, HTTPException

from app.catalog import load_catalog
from app.config import settings

router = APIRouter(prefix="/catalog", tags=["catalog"])
_catalog = load_catalog(settings().catalog_dir)


@router.get("")
async def list_services() -> list[dict]:
    return [
        {
            "id": s.id,
            "name": s.name,
            "area": s.area,
            "tier": s.tier,
            "lane": s.lane.value,
            "lanes": [x.value for x in s.lanes],
            "plain": s.plain,
            "automation_grade": s.automation_grade,
            "secret_stores": list(s.secret_stores),
            "requires": list(s.requires),
        }
        for s in _catalog
    ]


@router.get("/{service_id}")
async def get_service(service_id: str) -> dict:
    try:
        s = _catalog.get(service_id)
    except Exception:
        raise HTTPException(404, f"katalogda yok: {service_id}") from None
    return {
        "id": s.id, "name": s.name, "lane": s.lane.value, "executor": s.executor,
        "plain": s.plain, "health_check": s.health_check, "gotcha": s.gotcha,
        "tasks": [
            {"id": t.id, "lane": t.lane.value, "action": t.action, "description": t.description}
            for t in s.tasks
        ],
        "teardown": [{"id": t.id, "action": t.action} for t in s.teardown],
    }

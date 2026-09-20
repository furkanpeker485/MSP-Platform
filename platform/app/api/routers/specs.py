"""Tanım derleme, kuru çalıştırma ve dağıtım."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.catalog import load_catalog
from app.config import settings
from app.services.dispatcher import dispatch
from app.services.spec_compiler import MissingSecret, compile_spec

router = APIRouter(prefix="/specs", tags=["specs"])
_catalog = load_catalog(settings().catalog_dir)


class CompileRequest(BaseModel):
    tenant: str
    entitlements: list[str]
    previous_services: list[str] = []
    device_roles: list[str] = []
    version: int = 1
    dry_run: bool = True


@router.post("/compile")
async def compile_endpoint(req: CompileRequest) -> dict:
    try:
        spec = compile_spec(
            catalog=_catalog,
            tenant=req.tenant,
            entitlements=req.entitlements,
            previous_services=req.previous_services,
            device_roles=set(req.device_roles),
            version=req.version,
        )
    except MissingSecret as exc:
        raise HTTPException(409, str(exc)) from None
    except Exception as exc:
        raise HTTPException(400, str(exc)) from None

    return {
        "spec": spec.to_json(),
        "summary": {
            "services": len(spec.services),
            "tasks": len(spec.tasks),
            "removed": spec.removed,
            "by_lane": {
                lane: len([t for t in spec.tasks if t.lane == lane]) for lane in "ABCDEF"
            },
        },
    }


@router.post("/apply")
async def apply_endpoint(req: CompileRequest) -> dict:
    spec = compile_spec(
        catalog=_catalog, tenant=req.tenant, entitlements=req.entitlements,
        previous_services=req.previous_services, device_roles=set(req.device_roles),
        version=req.version,
    )
    return {"results": await dispatch(spec, dry_run=req.dry_run)}

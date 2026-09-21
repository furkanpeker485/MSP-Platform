"""HR Platformu — giriş noktası."""
from __future__ import annotations

import structlog
from fastapi import FastAPI

from app.api.routers import agents, catalog, health, specs
from app.catalog import load_catalog
from app.config import settings

log = structlog.get_logger(__name__)

app = FastAPI(
    title="MSP-Platform",
    version="0.1.0",
    description="Katalog, hak seti, tanım derleyici ve şerit dağıtıcısı",
)

app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(specs.router)
app.include_router(agents.router)


@app.on_event("startup")
async def startup() -> None:
    cat = load_catalog(settings().catalog_dir)   # tutarsızlık varsa açılışta patlar
    log.info("katalog_yuklendi", hizmet=len(cat))

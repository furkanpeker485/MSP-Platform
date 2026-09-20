"""Sapma uzlaştırması.

Devreye alma ile günlük işletme aynı döngüdür: ilk gün ne koşuyorsa 400. gün de o koşar.
Fark yalnızca şudur — ilk gün her şey eksiktir, sonra yalnız sapanlar uygulanır.
"""
from __future__ import annotations

import structlog

from app.services.dispatcher import dispatch
from app.services.spec_compiler import CompiledSpec, CompiledTask

log = structlog.get_logger(__name__)

# hatalı bir tanımın tek seferde dokunabileceği en fazla cihaz oranı
BLAST_RADIUS = 0.25


class BlastRadiusExceeded(Exception):
    """Bir uygulama tüm sahayı değil, en fazla belirlenen dilimi etkileyebilir."""


def diff(spec: CompiledSpec, observed: dict[str, str]) -> list[CompiledTask]:
    """Arzu edilen durum ile bildirilen durumu karşılaştırır, sapan görevleri döndürür."""
    out = []
    for task in spec.tasks:
        key = f"{task.service_id}/{task.task_id}"
        if observed.get(key) != "ok":
            out.append(task)
    return out


async def reconcile(
    spec: CompiledSpec,
    observed: dict[str, str],
    *,
    device_count: int = 1,
    dry_run: bool = False,
) -> dict:
    drifted = diff(spec, observed)
    if not drifted:
        return {"drifted": 0, "applied": [], "state": "in-sync"}

    if device_count and len(drifted) / max(device_count, 1) > BLAST_RADIUS and not dry_run:
        raise BlastRadiusExceeded(
            f"{len(drifted)} görev {device_count} cihazın %{BLAST_RADIUS:.0%} sınırını aşıyor"
        )

    subset = CompiledSpec(
        tenant=spec.tenant,
        version=spec.version,
        tasks=drifted,
        services=spec.services,
        removed=spec.removed,
    )
    applied = await dispatch(subset, dry_run=dry_run)
    failed = [a for a in applied if a.get("state") == "failed"]
    return {
        "drifted": len(drifted),
        "applied": applied,
        "state": "repaired" if not failed else "partial",
        "rollback_hint": "son sağlam sürüme dön" if failed else None,
    }

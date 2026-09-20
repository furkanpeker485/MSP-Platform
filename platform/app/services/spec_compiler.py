"""Tanım derleyici: hak seti + cihaz rolleri → arzu edilen durum.

Çıktı sürümlüdür ve **çıkarmalıdır**: paket düşünce kaldırılması gereken hizmetler
söküm görevleriyle sıraya girer. Böylece paket düşürme ayrı bir proje olmaktan çıkar.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.catalog import Catalog, CatalogService, Task
from app.models import Lane
from app.services.task_graph import topological_order


class MissingSecret(Exception):
    """Kasaya yazılmamış bir yetkiyle hizmet başlatılamaz."""


@dataclass
class CompiledTask:
    service_id: str
    task_id: str
    lane: str
    action: str
    description: str
    params: dict = field(default_factory=dict)
    teardown: bool = False


@dataclass
class CompiledSpec:
    tenant: str
    version: int
    tasks: list[CompiledTask]
    services: list[str]
    removed: list[str]

    def to_json(self) -> dict:
        return {
            "tenant": self.tenant,
            "version": self.version,
            "services": self.services,
            "removed": self.removed,
            "tasks": [asdict(t) for t in self.tasks],
        }

    def by_lane(self, lane: Lane) -> list[CompiledTask]:
        return [t for t in self.tasks if t.lane == lane.value]


def _expand(svc: CatalogService, device_roles: set[str]) -> list[Task]:
    """Cihaz rolüne göre geçerli olmayan görevleri eler."""
    out = []
    for task in svc.tasks:
        only = task.params.get("only_roles")
        if only and not (set(only) & device_roles):
            continue
        out.append(task)
    return out


def compile_spec(
    *,
    catalog: Catalog,
    tenant: str,
    entitlements: list[str],
    previous_services: list[str] | None = None,
    device_roles: set[str] | None = None,
    version: int = 1,
    vault_has: set[str] | None = None,
) -> CompiledSpec:
    device_roles = device_roles or set()
    previous = set(previous_services or [])
    vault_has = vault_has if vault_has is not None else None

    ordered = topological_order(catalog, entitlements)
    tasks: list[CompiledTask] = []

    for svc in ordered:
        for task in _expand(svc, device_roles):
            if vault_has is not None:
                missing = [s for s in task.requires_secret if s not in vault_has]
                if missing:
                    raise MissingSecret(f"{svc.id}/{task.id}: kasada yok → {missing}")
            tasks.append(
                CompiledTask(
                    service_id=svc.id,
                    task_id=task.id,
                    lane=task.lane.value,
                    action=task.action,
                    description=task.description,
                    params=task.params,
                )
            )

    # çıkarmalı taraf: artık hak edilmeyen hizmetlerin sökümü
    current = {s.id for s in ordered}
    removed = sorted(previous - current)
    for sid in removed:
        for task in catalog.get(sid).teardown:
            tasks.append(
                CompiledTask(
                    service_id=sid,
                    task_id=task.id,
                    lane=task.lane.value,
                    action=task.action,
                    description=task.description,
                    params=task.params,
                    teardown=True,
                )
            )

    return CompiledSpec(
        tenant=tenant,
        version=version,
        tasks=tasks,
        services=[s.id for s in ordered],
        removed=removed,
    )

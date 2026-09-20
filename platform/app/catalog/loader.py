"""Katalog yükleyici.

Tek katalog, iki yüz: pre-sales.hisarresearch.com'daki hizmet kimliği ile buradaki
`id` aynı olmak zorundadır. Farklılaşırsa satılan ile teslim edilen ayrışır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from app.models import Lane

VALID_GRADES = {"FULL", "ASSISTED", "HUMAN"}
VALID_STORES = {".env", "ansible-vault", "n8n-credentials"}


class CatalogError(Exception):
    """Katalog tutarsızlığı — açılışta patlar, çalışma anında değil."""


@dataclass(frozen=True)
class Task:
    id: str
    lane: Lane
    action: str
    description: str
    params: dict = field(default_factory=dict)
    requires_secret: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CatalogService:
    id: str
    name: str
    area: str
    tier: str
    lane: Lane
    lanes: tuple[Lane, ...]
    plain: str
    executor: str
    automation_grade: str
    secret_stores: tuple[str, ...]
    requires: tuple[str, ...]
    tasks: tuple[Task, ...]
    health_check: str
    gotcha: str
    teardown: tuple[Task, ...]

    @property
    def first_task_is_vault(self) -> bool:
        """Her hizmetin ilk adımı erişim bilgilerinin kasaya yazılmasıdır."""
        return bool(self.tasks) and self.tasks[0].action == "vault.store_access"


@dataclass
class Catalog:
    services: dict[str, CatalogService]

    def __iter__(self):
        return iter(self.services.values())

    def __len__(self) -> int:
        return len(self.services)

    def get(self, service_id: str) -> CatalogService:
        try:
            return self.services[service_id]
        except KeyError as exc:
            raise CatalogError(f"katalogda yok: {service_id}") from exc

    def by_lane(self, lane: Lane) -> list[CatalogService]:
        return [s for s in self.services.values() if s.lane is lane]


def _task(raw: dict, where: str) -> Task:
    for key in ("id", "lane", "action"):
        if key not in raw:
            raise CatalogError(f"{where}: görevde '{key}' eksik")
    return Task(
        id=raw["id"],
        lane=Lane(raw["lane"]),
        action=raw["action"],
        description=raw.get("description", ""),
        params=raw.get("params", {}) or {},
        requires_secret=list(raw.get("requires_secret", []) or []),
    )


def load_catalog(directory: str | Path) -> Catalog:
    path = Path(directory)
    if not path.is_dir():
        raise CatalogError(f"katalog klasörü yok: {path}")

    services: dict[str, CatalogService] = {}
    for file in sorted(path.glob("*.yaml")):
        raw = yaml.safe_load(file.read_text(encoding="utf-8"))
        sid = raw.get("id")
        if not sid:
            raise CatalogError(f"{file.name}: 'id' eksik")
        if sid in services:
            raise CatalogError(f"{file.name}: yinelenen kimlik {sid}")
        if raw.get("automation_grade") not in VALID_GRADES:
            raise CatalogError(f"{sid}: geçersiz automation_grade")

        stores = tuple(raw.get("secret_stores", []) or [])
        unknown = set(stores) - VALID_STORES
        if unknown:
            raise CatalogError(f"{sid}: bilinmeyen kasa {unknown}")

        tasks = tuple(_task(t, sid) for t in raw.get("tasks", []))
        service = CatalogService(
            id=sid,
            name=raw["name"],
            area=raw.get("area", ""),
            tier=raw.get("tier", "Proje"),
            lane=Lane(raw["lane"]),
            lanes=tuple(Lane(x) for x in raw.get("lanes", [raw["lane"]])),
            plain=raw.get("plain", ""),
            executor=raw.get("executor", ""),
            automation_grade=raw["automation_grade"],
            secret_stores=stores,
            requires=tuple(raw.get("requires", []) or []),
            tasks=tasks,
            health_check=raw.get("health_check", ""),
            gotcha=raw.get("gotcha", ""),
            teardown=tuple(_task(t, sid) for t in raw.get("teardown", []) or []),
        )
        if not service.first_task_is_vault:
            raise CatalogError(
                f"{sid}: ilk görev 'vault.store_access' olmalı — "
                "kasaya yazılmamış yetkiyle hizmet başlatılmaz"
            )
        services[sid] = service

    # ön koşullar katalogda var mı
    for svc in services.values():
        for dep in svc.requires:
            if dep not in services:
                raise CatalogError(f"{svc.id}: tanımsız ön koşul {dep}")
    return Catalog(services=services)

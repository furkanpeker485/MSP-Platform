"""Görev grafiği: hizmetleri ön koşullarına göre sıralar.

Bir hizmetin görevleri, bağlı olduğu hizmetlerin görevleri bittikten sonra sıraya girer.
Böylece Zabbix host'u, türetildiği NetBox kaydından önce oluşturulamaz.
"""
from __future__ import annotations

from collections import deque

from app.catalog import Catalog, CatalogService


class DependencyCycle(Exception):
    pass


def topological_order(catalog: Catalog, service_ids: list[str]) -> list[CatalogService]:
    """Verilen hizmetleri bağımlılık sırasına dizer (kararlı: alfabetik ikincil sıra)."""
    wanted = set(service_ids)

    # kapanış: ön koşullar hak setinde olmasa bile kurulmalıdır
    queue = deque(wanted)
    while queue:
        sid = queue.popleft()
        for dep in catalog.get(sid).requires:
            if dep not in wanted:
                wanted.add(dep)
                queue.append(dep)

    indegree = {sid: 0 for sid in wanted}
    dependents: dict[str, list[str]] = {sid: [] for sid in wanted}
    for sid in wanted:
        for dep in catalog.get(sid).requires:
            indegree[sid] += 1
            dependents[dep].append(sid)

    ready = sorted([sid for sid, deg in indegree.items() if deg == 0])
    order: list[str] = []
    while ready:
        sid = ready.pop(0)
        order.append(sid)
        for nxt in sorted(dependents[sid]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
                ready.sort()

    if len(order) != len(wanted):
        stuck = sorted(set(wanted) - set(order))
        raise DependencyCycle(f"ön koşul döngüsü: {stuck}")
    return [catalog.get(sid) for sid in order]

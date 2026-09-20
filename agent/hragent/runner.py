"""Görev yürütücü: platformdan gelen eylemi uygun uygulayıcıya bağlar."""
from __future__ import annotations

import structlog

from hragent.apply import ensure_file, ensure_package, ensure_service

log = structlog.get_logger(__name__)


class UnknownAction(Exception):
    pass


def run_task(task: dict, *, dry_run: bool = False) -> dict:
    """Tek bir görevi uygular ve sonucu döndürür. İstisna yutulmaz, yukarı taşınır."""
    action = task.get("action", "")
    params = task.get("params", {}) or {}
    key = f"{task.get('service_id')}/{task.get('task_id')}"

    if action != "agent.converge":
        raise UnknownAction(f"{key}: ajan bu eylemi yürütmez → {action}")

    results = []
    for pkg in params.get("packages", []):
        results.append(ensure_package(pkg["name"], version=pkg.get("version"), dry_run=dry_run))
    for svc in params.get("services", []):
        results.append(ensure_service(svc["name"], state=svc.get("state", "running"),
                                      dry_run=dry_run))
    for f in params.get("files", []):
        results.append(ensure_file(f["path"], f["content"], mode=int(f.get("mode", "644"), 8),
                                   secret=f.get("secret", False), dry_run=dry_run))

    failed = [r for r in results if r["state"] == "failed"]
    return {
        "key": key,
        "state": "failed" if failed else "ok",
        "changed": any(r["changed"] for r in results),
        "details": results,
    }

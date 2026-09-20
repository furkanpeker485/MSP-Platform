"""Servis durumu: çalışıyor mu, açılışta başlıyor mu."""
from __future__ import annotations

import platform
import subprocess

import structlog

log = structlog.get_logger(__name__)


def _running(name: str) -> bool:
    system = platform.system()
    if system == "Windows":
        out = subprocess.run(
            ["sc", "query", name], capture_output=True, text=True, check=False
        ).stdout
        return "RUNNING" in out
    return subprocess.run(
        ["systemctl", "is-active", "--quiet", name], check=False
    ).returncode == 0


def ensure_service(name: str, *, state: str = "running", dry_run: bool = False) -> dict:
    running = _running(name)
    want = state == "running"
    if running == want:
        return {"action": "service", "name": name, "state": "ok", "changed": False}
    if dry_run:
        return {"action": "service", "name": name, "state": f"would-{state}", "changed": False}

    system = platform.system()
    verb = "start" if want else "stop"
    cmd = ["sc", verb, name] if system == "Windows" else ["systemctl", verb, name]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    ok = result.returncode == 0
    if not ok:
        log.error("servis_degistirilemedi", servis=name, hata=result.stderr[:300])
    return {
        "action": "service", "name": name,
        "state": "ok" if ok else "failed", "changed": ok,
    }

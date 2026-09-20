"""Paket kurulumu. Paketler site relay'in önbelleğinden çekilir — geniş alan ağı doymasın."""
from __future__ import annotations

import platform
import subprocess

import structlog

log = structlog.get_logger(__name__)

MANAGERS = {
    "Windows": ["winget", "install", "--silent", "--accept-package-agreements", "--id"],
    "Linux": ["apt-get", "install", "-y"],
    "Darwin": ["brew", "install"],
}


class UnsupportedPlatform(Exception):
    pass


def _installed(name: str) -> bool:
    system = platform.system()
    probe = {
        "Windows": ["winget", "list", "--id", name],
        "Linux": ["dpkg", "-s", name],
        "Darwin": ["brew", "list", name],
    }.get(system)
    if not probe:
        raise UnsupportedPlatform(system)
    return subprocess.run(probe, capture_output=True, check=False).returncode == 0


def ensure_package(name: str, *, version: str | None = None, dry_run: bool = False) -> dict:
    """İstenen paketin kurulu olmasını sağlar. Kurulu ise hiçbir şey yapmaz."""
    if _installed(name):
        return {"action": "package", "name": name, "state": "ok", "changed": False}
    if dry_run:
        return {"action": "package", "name": name, "state": "would-install", "changed": False}

    system = platform.system()
    cmd = MANAGERS.get(system)
    if not cmd:
        raise UnsupportedPlatform(system)
    target = f"{name}={version}" if version and system == "Linux" else name
    result = subprocess.run([*cmd, target], capture_output=True, text=True, check=False)
    ok = result.returncode == 0
    if not ok:
        log.error("paket_kurulamadi", paket=name, kod=result.returncode, hata=result.stderr[:400])
    return {
        "action": "package", "name": name,
        "state": "ok" if ok else "failed",
        "changed": ok, "exit_code": result.returncode,
    }

"""Sır okuma.

Ajanın çalıştırdığı hiçbir script parolayı içinde taşımaz. Değerler `.env` dosyasından
okunur; dosya 0600 izinleriyle durur ve depoya asla girmez.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)

DEFAULT_PATHS = (
    Path("/etc/hragent/.env"),
    Path("C:/ProgramData/HRAgent/.env"),
    Path(".env"),
)


class InsecureSecretFile(Exception):
    """Sır dosyası fazla açık izinlerle duruyorsa okumayı reddederiz."""


def _check_permissions(path: Path) -> None:
    if os.name == "nt":  # Windows'ta izin modeli farklı, ACL ayrıca kontrol edilir
        return
    mode = path.stat().st_mode
    if mode & (stat.S_IRGRP | stat.S_IROTH):
        raise InsecureSecretFile(f"{path}: grup/diğer okuyabiliyor, 0600 olmalı")


def load(path: str | None = None) -> dict:
    """`.env` dosyasını okur. Değerler süreç dışına hiç çıkmaz."""
    candidates = [Path(path)] if path else list(DEFAULT_PATHS)
    for candidate in candidates:
        if not candidate.is_file():
            continue
        _check_permissions(candidate)
        values = {}
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
        log.info("sirlar_yuklendi", kaynak=str(candidate), anahtar_sayisi=len(values))
        return values
    log.warning("sir_dosyasi_bulunamadi", aranan=[str(c) for c in candidates])
    return {}


def get(key: str, default: str = "") -> str:
    """Önce ortam değişkeni, sonra `.env`. Koda gömülü varsayılan parola yoktur."""
    if key in os.environ:
        return os.environ[key]
    return load().get(key, default)

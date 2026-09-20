"""Dosya içeriği ve izinleri. Sır dosyaları daima 0600 yazılır."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

SECRET_MODE = 0o600


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_file(
    path: str, content: str, *, mode: int = 0o644, secret: bool = False, dry_run: bool = False
) -> dict:
    target = Path(path)
    desired = content.encode("utf-8")
    effective_mode = SECRET_MODE if secret else mode

    if target.is_file() and _digest(target.read_bytes()) == _digest(desired):
        if os.name != "nt" and (target.stat().st_mode & 0o777) != effective_mode:
            if not dry_run:
                target.chmod(effective_mode)
            return {"action": "file", "path": path, "state": "ok", "changed": True}
        return {"action": "file", "path": path, "state": "ok", "changed": False}

    if dry_run:
        return {"action": "file", "path": path, "state": "would-write", "changed": False}

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(desired)
    if os.name != "nt":
        target.chmod(effective_mode)
    return {"action": "file", "path": path, "state": "ok", "changed": True}

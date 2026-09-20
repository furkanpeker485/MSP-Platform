"""Donanım ve yazılım envanteri.

Kimlik anahtarı hostname veya ağ kartı kimliği DEĞİLDİR: klonlanmış sanal makineler
ikisini de paylaşır ve iki varlık tek kayda çöker. Anahtar, kalıcı ajan kimliği +
seri numarasıdır.
"""
from __future__ import annotations

import platform
import subprocess
import uuid
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)

UUID_FILE = Path("/etc/hragent/uuid") if platform.system() != "Windows" \
    else Path("C:/ProgramData/HRAgent/uuid")


def device_uuid() -> str:
    """Kalıcı ajan kimliği. Bir kez üretilir, diskte kalır."""
    if UUID_FILE.is_file():
        value = UUID_FILE.read_text(encoding="utf-8").strip()
        if value:
            return value
    value = str(uuid.uuid4())
    try:
        UUID_FILE.parent.mkdir(parents=True, exist_ok=True)
        UUID_FILE.write_text(value, encoding="utf-8")
    except OSError as exc:
        log.warning("kimlik_yazilamadi", error=str(exc))
    return value


def serial_number() -> str:
    """Üretici seri numarası. Boş veya yinelenen olabilir — tek başına anahtar değildir."""
    system = platform.system()
    try:
        if system == "Linux":
            path = Path("/sys/class/dmi/id/product_serial")
            return path.read_text(encoding="utf-8").strip() if path.is_file() else ""
        if system == "Darwin":
            # ioreg çıktısı geçerli UTF-8 olmayabilir: bayt olarak alıp hoşgörülü çözeriz,
            # ayrıca tüm ağaç yerine yalnız platform düğümünü sorarız.
            raw = subprocess.run(
                ["ioreg", "-c", "IOPlatformExpertDevice", "-d", "2"],
                capture_output=True, timeout=10, check=False,
            ).stdout
            out = raw.decode("utf-8", errors="replace")
            for line in out.splitlines():
                if "IOPlatformSerialNumber" in line:
                    parts = line.split('"')
                    return parts[-2] if len(parts) >= 2 else ""
            return ""
        if system == "Windows":
            raw = subprocess.run(
                ["wmic", "bios", "get", "serialnumber"],
                capture_output=True, timeout=10, check=False,
            ).stdout
            out = raw.decode("utf-8", errors="replace").splitlines()
            return out[1].strip() if len(out) > 1 else ""
    except (OSError, subprocess.SubprocessError, IndexError, UnicodeDecodeError) as exc:
        log.warning("seri_no_okunamadi", error=str(exc))
    return ""


def collect() -> dict:
    return {
        "uuid": device_uuid(),
        "serial": serial_number(),
        "hostname": platform.node(),
        "os_family": platform.system(),
        "os_release": platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
    }

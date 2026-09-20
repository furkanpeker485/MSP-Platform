"""Ajan döngüsü.

Devreye alma ile günlük işletme aynı döngüdür: ilk gün her şey eksiktir,
sonraki turlarda yalnız sapanlar uygulanır.
"""
from __future__ import annotations

import argparse
import sys
import time

import structlog

from hragent import inventory as inv
from hragent.client import Client
from hragent.config import Config
from hragent.runner import UnknownAction, run_task

log = structlog.get_logger(__name__)


def one_cycle(client: Client, observed: dict, *, dry_run: bool = False) -> dict:
    facts = inv.collect()
    response = client.checkin(observed, facts)
    tasks = response.get("tasks", [])
    log.info("gorev_alindi", sayi=len(tasks), cihaz=facts["uuid"])

    for task in tasks:
        try:
            result = run_task(task, dry_run=dry_run)
            observed[result["key"]] = result["state"]
        except UnknownAction as exc:
            log.warning("bilinmeyen_eylem", error=str(exc))
        except Exception as exc:  # noqa: BLE001 — tek görev hatası döngüyü düşürmez
            key = f"{task.get('service_id')}/{task.get('task_id')}"
            observed[key] = "failed"
            log.error("gorev_hatasi", gorev=key, error=str(exc))

    return response


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hragent")
    parser.add_argument("--once", action="store_true", help="tek tur koş ve çık")
    parser.add_argument("--dry-run", action="store_true", help="uygulama, yalnız raporla")
    args = parser.parse_args(argv)

    config = Config.load()
    if not config.platform_url:
        log.error("yapilandirma_eksik", eksik="HRAGENT_PLATFORM_URL")
        return 2

    client = Client(config)
    if not config.token and config.enrollment_code:
        client.config.token = client.enroll(inv.collect())
        log.info("kayit_tamam")

    observed: dict = {}
    while True:
        try:
            response = one_cycle(client, observed, dry_run=args.dry_run)
            wait = int(response.get("next_checkin", config.checkin_seconds))
        except Exception as exc:  # noqa: BLE001 — ağ kesintisinde susmayıp beklemeye devam
            log.error("tur_basarisiz", error=str(exc))
            wait = config.checkin_seconds
        if args.once:
            return 0
        time.sleep(wait)


if __name__ == "__main__":
    sys.exit(main())

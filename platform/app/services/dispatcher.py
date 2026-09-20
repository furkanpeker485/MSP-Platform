"""Dağıtıcı: her görevi kendi şeridinin yürütücüsüne yollar.

Şerit → yürütücü eşlemesi tek yerde durur. Yeni bir şerit eklenirse burası genişler,
katalog dosyalarının hiçbiri değişmez.
"""
from __future__ import annotations

import structlog

from app.integrations import awx, netbox, siem, ticketing, vault, zabbix
from app.models import Lane
from app.services.spec_compiler import CompiledSpec, CompiledTask

log = structlog.get_logger(__name__)


class LaneNotImplemented(Exception):
    pass


async def _lane_a(task: CompiledTask, tenant: str) -> dict:
    """Uç cihaz ajanı: görev kuyruğa yazılır, ajan bir sonraki yoklamasında çeker."""
    from app.services import agent_queue

    return await agent_queue.enqueue(tenant=tenant, task=task)


async def _lane_b(task: CompiledTask, tenant: str) -> dict:
    """Ansible: AWX iş şablonu, müşterinin yürütme düğümünde koşar."""
    return await awx.launch_job(
        job_template=task.params.get("job_template", task.action.split(".")[-1]),
        instance_group=f"relay-{tenant}",
        extra_vars={"tenant": tenant, **task.params.get("extra_vars", {})},
    )


async def _lane_c(task: CompiledTask, tenant: str) -> dict:
    """Sağlayıcı arayüzü: ayar müşteride değil, sağlayıcının sisteminde."""
    provider, _, op = task.action.partition(".")
    handler = {
        "netbox": netbox.call,
        "zabbix": zabbix.call,
        "veeam": awx.call_via_relay,   # Veeam API'si müşteri ağında → relay üzerinden
        "cloud": awx.call_via_relay,
    }.get(provider)
    if handler is None:
        raise LaneNotImplemented(f"C şeridinde bilinmeyen sağlayıcı: {provider}")
    return await handler(op, tenant=tenant, **task.params)


async def _lane_d(task: CompiledTask, tenant: str) -> dict:
    """HR platform kurulumu: iş bizim tarafımızda."""
    target, _, op = task.action.partition(".")
    handler = {
        "netbox": netbox.call,
        "zabbix": zabbix.call,
        "siem": siem.call,
        "ticketing": ticketing.call,
        "vault": vault.call,
    }.get(target)
    if handler is None:
        raise LaneNotImplemented(f"D şeridinde bilinmeyen hedef: {target}")
    return await handler(op, tenant=tenant, **task.params)


async def _lane_e(task: CompiledTask, tenant: str) -> dict:
    """Takvimli iş: n8n'de zamanlama kurulur, sonra kendi takviminde koşar."""
    from app.integrations import n8n

    return await n8n.ensure_schedule(
        workflow=task.params["workflow"], tenant=tenant, cron=task.params.get("cron", "0 6 1 * *")
    )


async def _lane_f(task: CompiledTask, tenant: str) -> dict:
    """İnsan iş emri: otomasyon hakkı kurar, teslimi insan yapar."""
    return await ticketing.create_work_order(
        tenant=tenant,
        title=task.description or task.task_id,
        queue=task.params.get("queue", "saha"),
        sla=task.params.get("sla"),
        acceptance=task.params.get("acceptance"),
    )


LANES = {
    Lane.A: _lane_a,
    Lane.B: _lane_b,
    Lane.C: _lane_c,
    Lane.D: _lane_d,
    Lane.E: _lane_e,
    Lane.F: _lane_f,
}


async def dispatch(spec: CompiledSpec, *, dry_run: bool = False) -> list[dict]:
    """Derlenmiş tanımı sırayla yürütür. Sıra zaten görev grafiğinden gelir."""
    results: list[dict] = []
    for task in spec.tasks:
        lane = Lane(task.lane)
        entry = {
            "service": task.service_id,
            "task": task.task_id,
            "lane": task.lane,
            "teardown": task.teardown,
        }
        if dry_run:
            results.append({**entry, "state": "dry-run"})
            continue
        try:
            entry["result"] = await LANES[lane](task, spec.tenant)
            entry["state"] = "done"
        except Exception as exc:  # noqa: BLE001 — tek görev hatası tüm tanımı düşürmez
            log.error("gorev_hatasi", service=task.service_id, task=task.task_id, error=str(exc))
            entry["state"] = "failed"
            entry["error"] = str(exc)
        results.append(entry)
    return results

"""Zabbix — izleme. D şeridinin ana yükü buradadır.

Ajanın kurulması taşımadır; satılan şey host kaydı, şablon bağı ve uyarı kuralıdır.
A şeridi kusursuz çalışıp D şeridi hiç koşmazsa müşteri hiçbir şey satın almamış olur.
"""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


async def _rpc(method: str, params: dict) -> dict:
    return await request(
        "POST", settings().zabbix_url,
        json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1},
        headers={"Authorization": f"Bearer {settings().zabbix_token}"},
    )


async def call(op: str, *, tenant: str, **params) -> dict:
    return await {
        "ensure_host_group": ensure_host_group,
        "ensure_host": ensure_host,
        "link_template": link_template,
        "ensure_action": ensure_action,
    }[op](tenant=tenant, **params)


async def ensure_host_group(*, tenant: str, **_) -> dict:
    return await _rpc("hostgroup.create", {"name": f"tenant/{tenant}"})


async def ensure_host(*, tenant: str, host: str, proxy: str | None = None, **_) -> dict:
    """Host her zaman müşterinin site relay proxy'sine bağlanır — doğrudan değil."""
    return await _rpc(
        "host.create",
        {
            "host": host,
            "groups": [{"name": f"tenant/{tenant}"}],
            "proxy_hostid": proxy or f"relay-{tenant}",
            "tags": [{"tag": "tenant", "value": tenant}],
        },
    )


async def link_template(*, tenant: str, host: str, template: str, **_) -> dict:
    return await _rpc("host.update", {"host": host, "templates": [{"name": template}]})


async def ensure_action(*, tenant: str, name: str, escalation: list | None = None, **_) -> dict:
    return await _rpc(
        "action.create",
        {"name": f"{tenant}/{name}", "operations": escalation or [], "status": 0},
    )

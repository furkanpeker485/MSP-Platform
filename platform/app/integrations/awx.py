"""AWX — B şeridinin yürütücüsü.

Relay, n8n worker'ı DEĞİLDİR. AWX automation mesh'te bir **yürütme düğümüdür**:
`listener_port: null` ve `peers_from_control_nodes: false` ile yapılandırılır, yani
bağlantıyı kendisi dışarı doğru kurar. Müşteri güvenlik duvarında gelen kural açılmaz.
Ayrıntı: docs/architecture.md
"""
from __future__ import annotations

from app.config import settings
from app.integrations._client import request


def _url(path: str) -> str:
    return f"{settings().awx_url.rstrip('/')}/api/v2/{path.lstrip('/')}"


async def launch_job(*, job_template: str, instance_group: str, extra_vars: dict) -> dict:
    """İşi müşterinin yürütme düğümünde koşturur."""
    return await request(
        "POST", _url(f"job_templates/{job_template}/launch/"),
        token=settings().awx_token,
        json={"extra_vars": extra_vars, "instance_group": instance_group},
    )


async def job_status(*, job_id: int) -> dict:
    return await request("GET", _url(f"jobs/{job_id}/"), token=settings().awx_token)


async def call_via_relay(op: str, *, tenant: str, **params) -> dict:
    """Müşteri ağındaki bir arayüze (Veeam, vCenter) relay üzerinden ulaşır."""
    return await launch_job(
        job_template="relay_api_call",
        instance_group=f"relay-{tenant}",
        extra_vars={"operation": op, "tenant": tenant, **params},
    )


async def ensure_execution_node(*, tenant: str, hostname: str) -> dict:
    """Yeni müşteri relay'ini mesh'e kaydeder — dışa doğru eşleşme ile."""
    return await request(
        "POST", _url("instances/"),
        token=settings().awx_token,
        json={
            "hostname": hostname,
            "node_type": "execution",
            "listener_port": None,           # gelen bağlantı dinlemez
            "peers_from_control_nodes": False,  # bağlantıyı düğüm kurar
            "managed_by_policy": False,
        },
    )

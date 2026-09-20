"""A şeridi kuyruğu.

Platform ajanı hiçbir zaman aramaz. Görev, müşterinin site relay'indeki kuyruğa yazılır;
ajan bir sonraki dışa doğru yoklamasında onu çeker. Yön her zaman içeriden dışarıdır.
"""
from __future__ import annotations

import httpx
import structlog

from app.config import settings
from app.services.spec_compiler import CompiledTask

log = structlog.get_logger(__name__)


async def enqueue(*, tenant: str, task: CompiledTask, device_uuid: str | None = None) -> dict:
    """Relay'in iş kuyruğuna görev bırakır."""
    payload = {
        "service_id": task.service_id,
        "task_id": task.task_id,
        "action": task.action,
        "params": task.params,
        "device_uuid": device_uuid,
        "teardown": task.teardown,
    }
    url = f"{settings().awx_url}/relay/{tenant}/queue"  # AWX mesh üzerinden relay'e
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, json=payload, headers=_auth())
        resp.raise_for_status()
        return resp.json()


def _auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings().awx_token}"}

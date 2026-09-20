import pytest

from app.services.drift import BlastRadiusExceeded, diff, reconcile
from app.services.spec_compiler import CompiledSpec, CompiledTask


def _spec(n: int) -> CompiledSpec:
    return CompiledSpec(
        tenant="acme", version=1, services=["x"], removed=[],
        tasks=[CompiledTask("x", f"t{i}", "D", "netbox.ensure_tenant", "") for i in range(n)],
    )


def test_sapmayan_gorev_uygulanmaz():
    spec = _spec(3)
    observed = {f"x/t{i}": "ok" for i in range(3)}
    assert diff(spec, observed) == []


def test_sapan_gorev_yakalanir():
    spec = _spec(3)
    observed = {"x/t0": "ok", "x/t1": "missing", "x/t2": "ok"}
    assert [t.task_id for t in diff(spec, observed)] == ["t1"]


async def test_kuru_calistirma_uygulamaz():
    spec = _spec(2)
    result = await reconcile(spec, {}, device_count=100, dry_run=True)
    assert result["drifted"] == 2
    assert all(a["state"] == "dry-run" for a in result["applied"])


async def test_etki_sinirini_asan_uygulama_reddedilir():
    """Hatalı bir tanım tüm sahayı değil, en fazla belirlenen dilimi etkileyebilir."""
    spec = _spec(50)
    with pytest.raises(BlastRadiusExceeded):
        await reconcile(spec, {}, device_count=10, dry_run=False)

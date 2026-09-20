import pytest

from app.catalog import load_catalog
from app.models import Lane
from app.services.spec_compiler import MissingSecret, compile_spec
from app.services.task_graph import topological_order

CATALOG_DIR = "app/catalog/services"


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(CATALOG_DIR)


def test_on_kosul_once_gelir(catalog):
    order = topological_order(catalog, ["switch-management"])
    ids = [s.id for s in order]
    assert ids[0] == "envanter-yonetim-sistemi"
    assert "switch-management" in ids


def test_hak_setinde_olmayan_on_kosul_da_kurulur(catalog):
    spec = compile_spec(catalog=catalog, tenant="acme", entitlements=["firewall-management"])
    assert "envanter-yonetim-sistemi" in spec.services


def test_paket_dusunce_sokum_gorevi_cikar(catalog):
    """Enterprise'dan Professional'a düşüş: kaldırılan hizmet söküm görevi üretir."""
    spec = compile_spec(
        catalog=catalog,
        tenant="acme",
        entitlements=["envanter-yonetim-sistemi"],
        previous_services=["envanter-yonetim-sistemi", "immutable-backup"],
    )
    assert "immutable-backup" in spec.removed
    teardown = [t for t in spec.tasks if t.teardown]
    assert teardown and all(t.service_id == "immutable-backup" for t in teardown)


def test_ilk_gorev_her_zaman_kasa(catalog):
    spec = compile_spec(catalog=catalog, tenant="acme", entitlements=["active-directory"])
    assert spec.tasks[0].action == "vault.store_access"


def test_kasada_olmayan_sir_derlemeyi_durdurur(catalog):
    svc = catalog.get("switch-management")
    object.__setattr__(svc.tasks[1], "requires_secret", ["snmpv3"])  # noqa: SLF001
    with pytest.raises(MissingSecret):
        compile_spec(
            catalog=catalog, tenant="acme",
            entitlements=["switch-management"], vault_has=set(),
        )


def test_serit_dagilimi_gorevlerde_gorunur(catalog):
    spec = compile_spec(
        catalog=catalog, tenant="acme",
        entitlements=[s.id for s in catalog],
    )
    assert spec.by_lane(Lane.B), "B şeridinde görev yok"
    assert spec.by_lane(Lane.F), "F şeridinde görev yok"
    assert len(spec.services) == 39

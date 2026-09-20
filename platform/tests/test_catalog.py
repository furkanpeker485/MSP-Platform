"""Katalog bütünlüğü. Bu testler tasarımın kurallarını koda bağlar."""
import pytest

from app.catalog import load_catalog
from app.catalog.loader import CatalogError
from app.models import Lane

CATALOG_DIR = "app/catalog/services"


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(CATALOG_DIR)


def test_yayindaki_hizmet_sayisi(catalog):
    assert len(catalog) == 39


def test_her_hizmetin_ilk_adimi_kasadir(catalog):
    """Kasaya yazılmamış bir yetkiyle hiçbir hizmet başlatılmaz."""
    for svc in catalog:
        assert svc.tasks[0].action == "vault.store_access", svc.id


def test_her_hizmetin_sokum_gorevi_var(catalog):
    """Çıkış hattı, giriş hattının aynadaki hâlidir."""
    for svc in catalog:
        assert svc.teardown, f"{svc.id}: söküm görevi yok"
        assert any(t.action == "vault.revoke" for t in svc.teardown), svc.id


def test_serit_dagilimi(catalog):
    counts = {lane: len(catalog.by_lane(lane)) for lane in Lane}
    assert counts[Lane.A] == 2      # yalnız Windows ve Linux Server Yönetimi
    assert counts[Lane.B] == 13
    assert counts[Lane.C] == 10
    assert counts[Lane.D] == 1
    assert counts[Lane.E] == 3
    assert counts[Lane.F] == 10
    assert sum(counts.values()) == 39


def test_envanter_her_seyin_on_kosulu(catalog):
    """Her hizmetin sağlık kontrolü envantere karşı çözümlenir."""
    envanter = catalog.get("envanter-yonetim-sistemi")
    assert envanter.requires == ()
    for svc in catalog:
        if svc.id != envanter.id:
            assert "envanter-yonetim-sistemi" in svc.requires, svc.id


def test_kasa_degerleri_gecerli(catalog):
    for svc in catalog:
        assert svc.secret_stores, svc.id
        for store in svc.secret_stores:
            assert store in {".env", "ansible-vault", "n8n-credentials"}


def test_bozuk_katalog_aciliste_patlar(tmp_path):
    (tmp_path / "kotu.yaml").write_text(
        "id: kotu\nname: Kötü\nlane: A\nautomation_grade: FULL\n"
        "secret_stores: ['.env']\ntasks:\n  - id: x\n    lane: A\n    action: agent.converge\n",
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match="vault.store_access"):
        load_catalog(tmp_path)

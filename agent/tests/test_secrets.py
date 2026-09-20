import os
import stat

import pytest

from hragent import secrets


def test_env_dosyasi_okunur(tmp_path):
    f = tmp_path / ".env"
    f.write_text('A=1\nB="iki"\n# yorum\nBOS\n', encoding="utf-8")
    f.chmod(0o600)
    assert secrets.load(str(f)) == {"A": "1", "B": "iki"}


@pytest.mark.skipif(os.name == "nt", reason="Windows izin modeli farklı")
def test_fazla_acik_izinli_sir_dosyasi_reddedilir(tmp_path):
    """Sır dosyası grup veya diğerlerine okunabiliyorsa okumayı reddederiz."""
    f = tmp_path / ".env"
    f.write_text("A=1\n", encoding="utf-8")
    f.chmod(0o644)
    with pytest.raises(secrets.InsecureSecretFile):
        secrets.load(str(f))


def test_ortam_degiskeni_dosyanin_onunde(tmp_path, monkeypatch):
    monkeypatch.setenv("HRAGENT_TOKEN", "ortamdan")
    assert secrets.get("HRAGENT_TOKEN") == "ortamdan"


def test_kodda_gomulu_varsayilan_parola_yok():
    assert secrets.get("HRAGENT_TOKEN_OLMAYAN") == ""

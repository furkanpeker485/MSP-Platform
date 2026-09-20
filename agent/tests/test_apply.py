import os
from pathlib import Path

import pytest

from hragent.apply.files import ensure_file


def test_dosya_yazilir_ve_ikinci_kez_degismez(tmp_path):
    p = tmp_path / "a" / "b.conf"
    first = ensure_file(str(p), "içerik\n")
    assert first["changed"] is True and p.read_text(encoding="utf-8") == "içerik\n"
    second = ensure_file(str(p), "içerik\n")
    assert second["changed"] is False, "aynı içerik yeniden yazılmamalı"


def test_kuru_calistirma_diske_dokunmaz(tmp_path):
    p = tmp_path / "yok.conf"
    result = ensure_file(str(p), "x", dry_run=True)
    assert result["state"] == "would-write"
    assert not p.exists()


@pytest.mark.skipif(os.name == "nt", reason="Windows izin modeli farklı")
def test_sir_dosyasi_daima_0600(tmp_path):
    p = tmp_path / "gizli.env"
    ensure_file(str(p), "TOKEN=abc", secret=True)
    assert (Path(p).stat().st_mode & 0o777) == 0o600

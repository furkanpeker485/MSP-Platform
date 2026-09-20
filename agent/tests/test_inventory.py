from hragent import inventory


def test_kimlik_kalicidir(tmp_path, monkeypatch):
    """Klonlanmış makineler hostname ve ağ kartı kimliğini paylaşır; anahtar ajan kimliğidir."""
    monkeypatch.setattr(inventory, "UUID_FILE", tmp_path / "uuid")
    first = inventory.device_uuid()
    second = inventory.device_uuid()
    assert first == second and len(first) == 36


def test_envanter_gerekli_alanlari_tasir(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "UUID_FILE", tmp_path / "uuid")
    facts = inventory.collect()
    for key in ("uuid", "hostname", "os_family", "arch"):
        assert facts.get(key), key

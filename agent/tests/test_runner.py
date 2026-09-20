import pytest

from hragent.runner import UnknownAction, run_task


def test_ajan_kendi_seridinde_olmayan_eylemi_reddeder():
    """Ajan yalnız A şeridini yürütür; Ansible işi ona verilmez."""
    with pytest.raises(UnknownAction):
        run_task({"service_id": "switch-management", "task_id": "step-02", "action": "awx.launch"})


def test_bos_gorev_basarili_ve_degisiklik_yok():
    result = run_task(
        {"service_id": "x", "task_id": "t", "action": "agent.converge", "params": {}}
    )
    assert result["state"] == "ok" and result["changed"] is False


def test_dosya_gorevi_uygulanir(tmp_path):
    target = tmp_path / "zabbix_agent2.conf"
    result = run_task(
        {
            "service_id": "server-monitoring", "task_id": "step-01", "action": "agent.converge",
            "params": {"files": [{"path": str(target), "content": "ServerActive=relay\n"}]},
        }
    )
    assert result["state"] == "ok" and result["changed"] is True
    assert target.read_text(encoding="utf-8") == "ServerActive=relay\n"

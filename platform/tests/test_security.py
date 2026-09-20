import pytest
from fastapi import HTTPException

from app.config import settings
from app.integrations.vault import CrossTenantAccess, _path
from app.security import issue_agent_token, verify_agent_token


@pytest.fixture(autouse=True)
def _secret(monkeypatch):
    monkeypatch.setenv("HR_AGENT_ENROLL_SECRET", "test-secret")
    settings.cache_clear()
    yield
    settings.cache_clear()


def test_belirtec_dogrulanir():
    token = issue_agent_token(tenant="acme", device_uuid="dev-1")
    assert verify_agent_token(token) == ("acme", "dev-1")


def test_kurcalanmis_belirtec_reddedilir():
    token = issue_agent_token(tenant="acme", device_uuid="dev-1")
    sahte = token.replace("acme", "contoso", 1)
    with pytest.raises(HTTPException):
        verify_agent_token(sahte)


def test_kiraci_sinirini_asan_kasa_yolu_reddedilir():
    """A kiracısı için çalışan iş, B kiracısının alanını isteyemez."""
    assert _path("acme", "firewall") == "tenants/acme/firewall"
    with pytest.raises(CrossTenantAccess):
        _path("acme", "tenants/contoso/firewall")

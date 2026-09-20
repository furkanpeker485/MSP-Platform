"""Yapılandırma. Tüm sırlar ortam değişkeninden gelir; kodda sabit değer bulunmaz."""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HR_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://hisar:hisar@localhost:5432/hisar"

    netbox_url: str = ""
    netbox_token: str = Field(default="", repr=False)
    zabbix_url: str = ""
    zabbix_token: str = Field(default="", repr=False)
    awx_url: str = ""
    awx_token: str = Field(default="", repr=False)
    siem_url: str = ""
    siem_token: str = Field(default="", repr=False)
    ticketing_url: str = ""
    ticketing_token: str = Field(default="", repr=False)
    vault_addr: str = ""
    vault_token: str = Field(default="", repr=False)

    agent_enroll_secret: str = Field(default="", repr=False)
    agent_checkin_seconds: int = 45
    drift_interval_seconds: int = 900

    catalog_dir: str = "app/catalog/services"


@lru_cache
def settings() -> Settings:
    return Settings()

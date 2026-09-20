from __future__ import annotations

from dataclasses import dataclass

from hragent import secrets


@dataclass
class Config:
    platform_url: str
    token: str
    tenant: str
    enrollment_code: str
    checkin_seconds: int

    @classmethod
    def load(cls) -> "Config":
        env = secrets.load()

        def val(key: str, default: str = "") -> str:
            import os
            return os.environ.get(key) or env.get(key, default)

        return cls(
            platform_url=val("HRAGENT_PLATFORM_URL").rstrip("/"),
            token=val("HRAGENT_TOKEN"),
            tenant=val("HRAGENT_TENANT"),
            enrollment_code=val("HRAGENT_ENROLLMENT_CODE"),
            checkin_seconds=int(val("HRAGENT_CHECKIN_SECONDS", "45")),
        )

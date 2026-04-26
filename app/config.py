"""Runtime configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    allowed_origins: list[str]
    rembg_model: str
    max_upload_bytes: int

    @classmethod
    def from_env(cls) -> "Settings":
        origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
        origins = ["*"] if origins_raw.strip() == "*" else _split_csv(origins_raw)
        return cls(
            allowed_origins=origins,
            rembg_model=os.getenv("REMBG_MODEL", "u2net"),
            max_upload_bytes=int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024,
        )


settings = Settings.from_env()

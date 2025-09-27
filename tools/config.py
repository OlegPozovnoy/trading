# tools/config.py
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    # не тянем зависимость, если её нет — просто пропускаем
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    load_dotenv = None  # type: ignore

def _load_env() -> None:
    """Подхватить my.env или .env из корня проекта, если есть."""
    if load_dotenv is None:
        return
    for name in ("my.env", ".env"):
        p = Path(name)
        if p.exists():
            load_dotenv(p)
            break

_load_env()

def cfg(name: str, default=None, type_=str):
    """Достаём переменную окружения с приведением типа.

    cfg("BATCH_SIZE", 64, int) -> int
    cfg("DRY_RUN", False, bool) -> True/False
    """
    val = os.getenv(name)
    if val is None:
        return default
    if type_ is bool:
        return str(val).strip().lower() in ("1", "true", "yes", "on")
    try:
        return type_(val)
    except Exception:
        return default

@dataclass(frozen=True)
class Settings:
    # AI
    openai_key: Optional[str] = os.getenv("openai_key") or os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Timezone / регионы (на будущее)
    tz: str = os.getenv("TZ", "Europe/Moscow")

    # Примеры на будущее:
    # tinkoff_token: Optional[str] = os.getenv("TINKOFF_TOKEN")
    # postgres_url: Optional[str] = os.getenv("DATABASE_URL")

S = Settings()

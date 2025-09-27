# tools/config.py
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv  # pip install python-dotenv
except Exception:
    load_dotenv = None  # type: ignore

# Для отладки можно посмотреть, откуда загрузили env
_LOADED_ENV_PATH: Optional[str] = None

def _project_root_from_here() -> Path:
    """Ищем корень репозитория (папка с .git), начиная от этого файла вверх."""
    here = Path(__file__).resolve()
    for p in (here.parent, *here.parents):
        if (p / ".git").exists():
            return p
    # Фолбэк: два уровня вверх от tools/config.py -> корень trading/
    return here.parents[1]

def _load_env() -> None:
    """Грузим строго my.env (или .env) из корня проекта. Никаких внешних путей."""
    global _LOADED_ENV_PATH
    if not load_dotenv:
        return
    root = _project_root_from_here()
    for name in ("my.env", ".env"):
        env_path = root / name
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            _LOADED_ENV_PATH = str(env_path)
            break

_load_env()

def cfg(name: str, default=None, type_=str):
    """Чтение переменной окружения с приведением типа."""
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
    # OpenAI
    openai_key: Optional[str] = os.getenv("openai_key") or os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    # Общие
    tz: str = os.getenv("TZ", "Europe/Moscow")

S = Settings()

# (опционально) Функция для быстрой диагностики
def loaded_env_path() -> Optional[str]:
    return _LOADED_ENV_PATH

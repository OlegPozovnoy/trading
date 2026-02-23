# create_tgchannels/pyrogram_errors.py
from __future__ import annotations

from typing import Any, Dict, Optional

def map_pyrogram_error(e: Exception) -> Dict[str, Any]:
    """
    Компактный маппер исключений pyrogram -> human-friendly поля для CSV.
    Работает и без импорта pyrogram (если его нет при стат. анализе).
    """
    name = type(e).__name__
    msg = str(e)

    # Дефолт
    out = {
        "error_code": "UNKNOWN",
        "hint": "Неизвестная ошибка (см. message).",
        "action": "Посмотреть message/traceback, добавить кейс в map_pyrogram_error()",
        "wait_seconds": None,
    }

    # Частые кейсы (по имени класса — так меньше зависимостей)
    if name in {"FloodWait", "FloodWaitError"}:
        # у FloodWait обычно есть атрибут value / x / seconds (зависит от версии)
        wait = None
        for attr in ("value", "x", "seconds", "wait_seconds"):
            if hasattr(e, attr):
                try:
                    wait = int(getattr(e, attr))
                    break
                except Exception:
                    pass
        out.update({
            "error_code": "FLOOD_WAIT",
            "hint": "Telegram ограничил частоту запросов (FloodWait).",
            "action": "Увеличить паузы/лимиты; при повторениях — backoff (см. ниже).",
            "wait_seconds": wait,
        })
        return out

    if name in {"ChannelInvalid", "PeerIdInvalid"}:
        out.update({
            "error_code": "CHANNEL_INVALID",
            "hint": "Неверный channel/peer: tg_id устарел, канал удалён/переехал, либо это не тот тип чата.",
            "action": "Резолв по username (get_chat), обновить tg_id; если не резолвится — пометить невалидным.",
        })
        return out

    if name in {"UsernameInvalid"}:
        out.update({
            "error_code": "USERNAME_INVALID",
            "hint": "Некорректный username (формат/символы).",
            "action": "Проверить username в базе; нормализовать/почистить; пропустить канал.",
        })
        return out

    if name in {"UsernameNotOccupied"}:
        out.update({
            "error_code": "USERNAME_NOT_OCCUPIED",
            "hint": "Username не занят — канал/юзернейм больше не существует.",
            "action": "Пометить как невалидный или найти новый username вручную.",
        })
        return out

    if name in {"ChatWriteForbidden", "ChatAdminRequired", "ChannelPrivate"}:
        out.update({
            "error_code": name.upper(),
            "hint": "Нет прав/канал приватный/нужен доступ.",
            "action": "Добавить аккаунт в канал / получить права / исключить канал из импорта.",
        })
        return out

    if "AUTH_KEY" in msg or name in {"AuthKeyUnregistered", "SessionRevoked"}:
        out.update({
            "error_code": "SESSION_INVALID",
            "hint": "Сессия слетела/отозвана.",
            "action": "Перелогиниться, пересоздать session string / .session файл.",
        })
        return out

    return out

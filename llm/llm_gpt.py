# llm/llm_gpt.py
from __future__ import annotations
from typing import Optional, Dict, Any, List, cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from tools.config import S, cfg
from tools.utils import sync_timed

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """Ленивая инициализация клиента (реиспользуем HTTP-сессию)."""
    global _client
    if _client is None:
        if not S.openai_key:
            raise RuntimeError(
                "OpenAI API key is not configured. "
                "Set openai_key in my.env/.env or export OPENAI_API_KEY."
            )
        # Конструктор в SDK 1.x принимает api_key; timeout опционален.
        # Если твой SDK не поддерживает timeout — просто убери эту строку.
        timeout = cfg("OPENAI_TIMEOUT", 60, int)
        _client = OpenAI(api_key=S.openai_key, timeout=timeout)
    return _client


def _default_messages(text: str, system: Optional[str]) -> List[ChatCompletionMessageParam]:
    """Собираем типизированный список сообщений для Chat Completions."""
    sys_msg: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": system or "You are a helpful assistant.",
    }
    user_msg: ChatCompletionUserMessageParam = {"role": "user", "content": text}
    return [sys_msg, user_msg]


@sync_timed()
def get_gpt_action(
    text: str,
    model: Optional[str] = None,
    *,
    system: Optional[str] = None,
    temperature: float = 0.0,
    messages: Optional[List[ChatCompletionMessageParam]] = None,
    **kwargs: Dict[str, Any],
):
    """
    Быстрый вызов Chat Completions.
    Возвращает resp.choices[0].message (совместимо с существующим кодом).
    """
    client = _get_client()

    # Некоторые типовые заглушки SDK перечисляют допустимые Literal-модели и ворчат на произвольные строки.
    # Для тишины типовой проверки приводим к str через cast.
    _model: str = cast(str, (model or S.openai_model or "gpt-4o-mini"))

    _messages: List[ChatCompletionMessageParam] = (
        messages if messages is not None else _default_messages(text, system)
    )

    resp = client.chat.completions.create(
        model=_model,
        messages=_messages,
        temperature=temperature,
        **kwargs,
    )
    return resp.choices[0].message


@sync_timed()
def get_gpt_text(
    text: str,
    model: Optional[str] = None,
    *,
    system: Optional[str] = None,
    temperature: float = 0.0,
    messages: Optional[List[ChatCompletionMessageParam]] = None,
    **kwargs: Dict[str, Any],
) -> str:
    """То же, но сразу возвращает message.content (str)."""
    msg = get_gpt_action(
        text,
        model=model,
        system=system,
        temperature=temperature,
        messages=messages,
        **kwargs,
    )
    return (msg.content or "") if hasattr(msg, "content") else ""

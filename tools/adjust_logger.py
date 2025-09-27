# tools/adjust_logger.py
from __future__ import annotations
import logging
import sys

_LOG_FORMAT = "%(asctime)s %(levelname).1s %(name)s: %(message)s"
_DATE_FORMAT = "%H:%M:%S"

def configure_logging(level: int = logging.INFO, *, to_stdout: bool = True) -> logging.Logger:
    """
    Минимальный конфиг логов без побочных эффектов при импорте.
    Вызывает один раз на старте приложения/скрипта.
    """
    root = logging.getLogger()
    # Снимаем старые хендлеры (если вдруг уже что-то навешано)
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout if to_stdout else sys.stderr)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    root.addHandler(handler)
    root.setLevel(level)

    # Утихомирим шумные библиотеки
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    return root

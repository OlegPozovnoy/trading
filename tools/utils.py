# tools/utils.py
from __future__ import annotations
import os
import time
import logging
import functools
import random
import inspect
from typing import Callable
import sql.get_table

# ============== Конфиг из окружения (my.env) ==============
def _as_bool(s: str) -> bool:
    return str(s).strip().lower() in ("1", "true", "on", "yes")

FUNC_STATS_ENABLED = _as_bool(os.getenv("FUNC_STATS", "0"))          # 1/true/on => писать метрики
try:
    FUNC_STATS_SAMPLE = float(os.getenv("FUNC_STATS_SAMPLE", "1.0"))  # 0..1 (напр. 0.1 = 10%)
except ValueError:
    FUNC_STATS_SAMPLE = 1.0

# При желании можно логически помечать замеры (уйдёт в имя функции как суффикс)
FUNC_STATS_TAG = os.getenv("FUNC_STATS_TAG", "").strip()
# Имя таблицы (оставил как у тебя)
FUNC_STATS_TABLE = os.getenv("FUNC_STATS_TABLE", "public.func_stats")

log_stats = logging.getLogger("func_stats")


def _sanitize_sql_literal(s: str) -> str:
    """Мини-санитайзер для SQL-литералов (одинарные кавычки дублируем)."""
    return s.replace("'", "''")


def _func_full_name(func: Callable) -> str:
    mod = getattr(func, "__module__", "") or ""
    nm = getattr(func, "__name__", "") or getattr(func, "__qualname__", str(func))
    name = f"{mod}.{nm}" if mod else nm
    if FUNC_STATS_TAG:
        name = f"{name}@{FUNC_STATS_TAG}"
    return name


def _write_func_stat(func: Callable, total_ms: float) -> None:
    """Быстрый UPSERT метрики в Postgres. Ничего не делает, если выключено/не попали в сэмпл."""
    if not FUNC_STATS_ENABLED:
        return
    if FUNC_STATS_SAMPLE < 1.0 and random.random() > FUNC_STATS_SAMPLE:
        return

    name = _sanitize_sql_literal(_func_full_name(func))
    total = float(total_ms)

    # NB: в PostgreSQL '^' — XOR, поэтому используем power(...,2)
    query = f"""
    INSERT INTO {FUNC_STATS_TABLE} (name, num, avg, min, max, stdev, last, last_invoke)
    VALUES ('{name}', 1, {total}, {total}, {total}, 0, {total}, NOW())
    ON CONFLICT (name)
    DO UPDATE SET
      num  = {FUNC_STATS_TABLE}.num + 1,
      avg  = ({FUNC_STATS_TABLE}.avg * {FUNC_STATS_TABLE}.num + {total}) / ({FUNC_STATS_TABLE}.num + 1),
      min  = LEAST({FUNC_STATS_TABLE}.min, {total}),
      max  = GREATEST({FUNC_STATS_TABLE}.max, {total}),
      stdev = sqrt( (({FUNC_STATS_TABLE}.num - 1) * power({FUNC_STATS_TABLE}.stdev, 2)
               + power({total} - {FUNC_STATS_TABLE}.avg, 2)) / {FUNC_STATS_TABLE}.num ),
      last = {total},
      last_invoke = NOW();
    """
    try:
        sql.get_table.exec_query(query)
    except Exception as e:
        # В дебаге показываем причину, но не валим рабочий код
        log_stats.debug("func_stats write failed: %s", e)


# ============== Единый декоратор: timed (авто sync/async) ==============
def timed(name: str | None = None):
    """
    Универсальный таймер для sync/async функций.
    - Лог в DEBUG: 'module.func took X ms'
    - Запись в БД включается через my.env: FUNC_STATS=1 (и опц. FUNC_STATS_SAMPLE)
    """
    def deco(func: Callable):
        log = logging.getLogger(f"{func.__module__}.{getattr(func, '__name__', 'func')}")
        label = name or getattr(func, "__name__", "func")

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                # Берём время только если нужен лог DEBUG или метрики
                if log.isEnabledFor(logging.DEBUG) or FUNC_STATS_ENABLED:
                    t0 = time.perf_counter()
                    try:
                        return await func(*args, **kwargs)
                    finally:
                        dt = (time.perf_counter() - t0) * 1000.0
                        if log.isEnabledFor(logging.DEBUG):
                            log.debug("%s took %.1f ms", label, dt)
                        _write_func_stat(func, dt)
                else:
                    return await func(*args, **kwargs)
            return wrapped
        else:
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                if log.isEnabledFor(logging.DEBUG) or FUNC_STATS_ENABLED:
                    t0 = time.perf_counter()
                    try:
                        return func(*args, **kwargs)
                    finally:
                        dt = (time.perf_counter() - t0) * 1000.0
                        if log.isEnabledFor(logging.DEBUG):
                            log.debug("%s took %.1f ms", label, dt)
                        _write_func_stat(func, dt)
                else:
                    return func(*args, **kwargs)
            return wrapped
    return deco


# ============== Совместимость со старым API ==============
def sync_timed(name: str | None = None):
    return timed(name)

def async_timed(name: str | None = None):
    return timed(name)

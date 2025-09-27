# sql/async_exec.py
from __future__ import annotations

import asyncio

from sql.get_table import engine


async def query_product(pool, query):
    async with pool.acquire() as connection:
        return await connection.execute(query)


async def exec_list(sql_list: list[str]) -> None:
    """
    Выполняет список SQL-строк в ОДНОЙ транзакции.
    Не блокирует event loop — бежит в пуле потоков.
    """
    loop = asyncio.get_running_loop()

    def _run():
        conn = engine.raw_connection()
        try:
            try:
                conn.autocommit = False
            except Exception:
                pass
            cur = conn.cursor()
            try:
                for q in sql_list:
                    if not q:
                        continue
                    cur.execute(q)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()
        finally:
            conn.close()

    await loop.run_in_executor(None, _run)

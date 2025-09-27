# tools/health.py
from __future__ import annotations
import json
from sql.get_table import exec_query

DDL = """
CREATE TABLE IF NOT EXISTS app_health (
  key text PRIMARY KEY,
  ts  timestamptz NOT NULL DEFAULT now(),
  val jsonb NOT NULL DEFAULT '{}'::jsonb
);
"""

def ensure_health_table() -> None:
    exec_query(DDL)

def heartbeat(key: str, **kv) -> None:
    """
    Лёгкий пульс: обновляет таймстемп и (опц.) небольшие поля в JSON.
    Без логов, один upsert.
    """
    payload = json.dumps(kv, ensure_ascii=False)
    exec_query(f"""
        INSERT INTO app_health(key, ts, val)
        VALUES ('{key}', now(), '{payload}'::jsonb)
        ON CONFLICT (key) DO UPDATE
          SET ts = excluded.ts,
              val = app_health.val || excluded.val;
    """)

def status() -> None:
    """
    Короткий вывод «как дела».
    """
    rows = exec_query("""
        with h as (
          select key, ts, extract(epoch from now()-ts) as age
          from app_health
        )
        select key,
               to_char(ts, 'YYYY-MM-DD HH24:MI:SS.US TZ') as last_beat,
               round(age::numeric, 3) as age_sec
        from h
        order by key;
    """).mappings().all()
    if not rows:
        print("health: нет записей (запусти refresh)")
        return
    for r in rows:
        print(f"{r['key']:20s}  last={r['last_beat']}  age={r['age_sec']}s")

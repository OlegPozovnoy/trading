# tools/quotes_daily_export.py
# Дневные цены из df_all_candles_t:
# - берём ПОСЛЕДНЮЮ свечу КАЖДОГО дня ДО/НА 17:00:00 (по умолчанию)
# - включаем выходные (пустые дни) в выдачу
# - сохраняем CSV с колонками: security, class_code, dt, time, close, volume
#
# Запуск (правый клик → Run):
#   без аргументов — последние 10 дней по всем тикерам, cutoff=17:00:00
#   с аргументами:
#     --tickers SBER,GAZP,LKOH
#     --days 30
#     --from 2025-09-01 --to 2025-10-05
#     --cutoff 17:00:00
#
# Требуется: sql.get_table.query_to_df (ваш модуль) и индекс в БД:
#   CREATE INDEX IF NOT EXISTS ix_df_all_candles_t_sec_dt
#   ON public.df_all_candles_t(security, datetime);

from __future__ import annotations

import argparse
import datetime as dt
import os
from typing import Iterable, Optional, Sequence, List, Dict

import pandas as pd
from sql.get_table import query_to_df


# Папка для выгрузок (держите в .gitignore: tools/reports/)
REPORT_DIR = os.path.join("tools", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


# ---------- SQL helpers ----------

def _sql_in_list(items: Sequence[str]) -> str:
    esc = [str(s).replace("'", "''") for s in items]
    return ", ".join(f"'{s}'" for s in esc)


def load_daily_closes(
    tickers: Optional[Iterable[str]] = None,
    date_from: Optional[dt.date] = None,
    date_to: Optional[dt.date] = None,
    time_cutoff: str = "17:00:00",
) -> pd.DataFrame:
    """
    Возвращает по каждой (security, day) ПОСЛЕДНЮЮ свечу дня ДО/НА time_cutoff.
    Колонки: security, class_code, dt(date), time(time), close, volume
    """
    where = ["1=1"]
    if tickers:
        tk = list(tickers)
        where.append(f"security IN ({_sql_in_list(tk)})")
    if date_from:
        where.append(f"datetime::date >= '{date_from.isoformat()}'::date")
    if date_to:
        where.append(f"datetime::date <= '{date_to.isoformat()}'::date")
    if time_cutoff:
        where.append(f"datetime::time <= '{time_cutoff}'::time")

    where_sql = " AND ".join(where)

    query = f"""
    WITH x AS (
      SELECT
        security,
        class_code,
        datetime::date   AS dt,
        datetime::time   AS time,
        close::double precision   AS close,
        volume::double precision  AS volume,
        ROW_NUMBER() OVER (
          PARTITION BY security, datetime::date
          ORDER BY datetime::time DESC
        ) AS rn
      FROM public.df_all_candles_t
      WHERE {where_sql}
    )
    SELECT security, class_code, dt, time, close, volume
    FROM x
    WHERE rn = 1
    ORDER BY security, dt;
    """
    df = query_to_df(query)
    if not df.empty:
        df.columns = [str(c) for c in df.columns]
    return df


# ---------- Постобработка для календаря (включая выходные) ----------

def include_weekends_grid(
    df: pd.DataFrame,
    tickers: Optional[Iterable[str]],
    date_from: dt.date,
    date_to: dt.date,
    time_cutoff: str = "17:00:00",
) -> pd.DataFrame:
    """
    Добавляет в выдачу ВСЕ календарные даты в интервале [date_from, date_to],
    включая выходные (для каждого тикера). Пустые дни будут с NaN в ценах.
    """
    if tickers:
        sec_list = list(dict.fromkeys([str(x) for x in tickers]))
    else:
        sec_list = sorted(df["security"].astype(str).unique().tolist())

    if not sec_list:
        return pd.DataFrame(columns=["security", "class_code", "dt", "time", "close", "volume"])

    rng = pd.date_range(start=date_from, end=date_to, freq="D").date
    idx = pd.MultiIndex.from_product([sec_list, rng], names=["security", "dt"])

    base = df.copy()
    if not base.empty:
        base["security"] = base["security"].astype(str)
        base["dt"] = pd.to_datetime(base["dt"]).dt.date
        base = base.set_index(["security", "dt"])
        base = base.reindex(idx)
    else:
        base = pd.DataFrame(index=idx)

    base = base.reset_index()

    # time для пустых дней ставим равным cutoff
    hh, mm, ss = [int(x) for x in time_cutoff.split(":")]
    cutoff_time = dt.time(hh, mm, ss)
    if "time" not in base.columns:
        base["time"] = cutoff_time
    else:
        base["time"] = base["time"].fillna(cutoff_time)

    # гарантируем порядок/наличие колонок
    for col in ["class_code", "close", "volume"]:
        if col not in base.columns:
            base[col] = pd.Series([None] * len(base))

    base = base[["security", "class_code", "dt", "time", "close", "volume"]]
    return base


# ---------- Утилиты экспорта ----------

def _parse_tickers(arg: Optional[str]) -> Optional[List[str]]:
    if not arg:
        return None
    return [s.strip() for s in arg.split(",") if s.strip()]


def export_csv(
    df_full: pd.DataFrame,
    prefix: str = "daily_closes",
) -> str:
    ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(REPORT_DIR, f"{prefix}_{ts}.csv")
    out = df_full[["security", "class_code", "dt", "time", "close", "volume"]].copy()
    # сериализация: dt как YYYY-MM-DD, time как HH:MM:SS
    out["dt"] = pd.to_datetime(out["dt"]).dt.date.astype(str)
    out["time"] = out["time"].astype(str)
    out.to_csv(csv_path, index=False)
    return csv_path


# ---------- CLI / main ----------

def build_and_export(
    tickers: Optional[List[str]],
    date_from: Optional[dt.date],
    date_to: Optional[dt.date],
    days: int,
    cutoff: str,
) -> Dict[str, int | str]:
    # интервал дат: приоритет у явных --from/--to; иначе последние N календарных дней
    if date_from:
        _date_from = date_from
        _date_to = date_to or dt.date.today()
    else:
        _date_to = date_to or dt.date.today()
        _date_from = _date_to - dt.timedelta(days=days)

    # тянем последнюю свечу каждого дня до/на cutoff
    df = load_daily_closes(
        tickers=tickers,
        date_from=_date_from,
        date_to=_date_to,
        time_cutoff=cutoff,
    )

    # добавляем выходные/пустые дни в интервал
    df_full = include_weekends_grid(
        df=df,
        tickers=tickers,
        date_from=_date_from,
        date_to=_date_to,
        time_cutoff=cutoff,
    )

    path = export_csv(df_full, prefix="daily_closes")
    return {
        "path": path,
        "rows": int(len(df_full)),
        "securities": int(df_full["security"].nunique()) if not df_full.empty else 0,
        "dates": int(pd.to_datetime(df_full["dt"]).dt.date.nunique()) if not df_full.empty else 0,
    }


def main():
    p = argparse.ArgumentParser(description="Экспорт дневных цен (срез на 17:00, выходные включены)")
    p.add_argument("--tickers", type=str, default="", help="Список тикеров через запятую (пусто = все)")
    p.add_argument("--days", type=int, default=10, help="Сколько последних календарных дней (по умолчанию 10)")
    p.add_argument("--from", dest="date_from", type=str, default="", help="Дата от (YYYY-MM-DD), приоритетнее --days")
    p.add_argument("--to", dest="date_to", type=str, default="", help="Дата до (YYYY-MM-DD)")
    p.add_argument("--cutoff", type=str, default="17:00:00", help="Срез дня HH:MM:SS (по умолчанию 17:00:00)")
    args = p.parse_args()

    tickers = _parse_tickers(args.tickers)
    date_from = dt.date.fromisoformat(args.date_from) if args.date_from else None
    date_to = dt.date.fromisoformat(args.date_to) if args.date_to else None

    stats = build_and_export(
        tickers=tickers,
        date_from=date_from,
        date_to=date_to,
        days=args.days,
        cutoff=args.cutoff,
    )

    print(f"Saved CSV: {stats['path']}")
    print(f"Rows: {stats['rows']} | Securities: {stats['securities']} | Dates: {stats['dates']}")


if __name__ == "__main__":
    main()

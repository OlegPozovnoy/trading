# tools/tg_report.py
# Отчёт по Telegram-каналам (только из Mongo): последняя дата поста, "давность", статус import_error.
# Сохраняет ТОЛЬКО CSV в tools/reports/.

from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
from typing import Any, Dict, List, Optional

from pymongo import ASCENDING, DESCENDING

# Mongo-клиент из проекта (db = client.trading)
from nlp import client as mongo_client

log = logging.getLogger("tg_report")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

# Папка для отчётов (в .gitignore добавь строку: tools/reports/)
REPORT_DIR = os.path.join("tools", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


# ---------- Mongo helpers ----------
def ensure_news_indexes() -> None:
    db = mongo_client.trading
    db.news.create_index([("channel_username", ASCENDING), ("date", DESCENDING)], background=True)


def last_news_date(username: str) -> Optional[dt.datetime]:
    if not username:
        return None
    db = mongo_client.trading
    cur = db.news.find({"channel_username": username}).sort("date", DESCENDING).limit(1)
    doc = next(iter(cur), None)
    return doc.get("date") if doc else None


def load_channels(only_active: bool) -> List[Dict[str, Any]]:
    db = mongo_client.trading
    filt = {"is_active": 1} if only_active else {}
    proj = {"username": 1, "tg_id": 1, "title": 1, "is_active": 1, "import_error": 1}
    return list(db.tg_channels.find(filt, proj))


# ---------- Report ----------
def build_snapshot(only_active: bool) -> Dict[str, Any]:
    ensure_news_indexes()
    chans = load_channels(only_active=only_active)

    now = dt.datetime.now(dt.timezone.utc)
    rows: List[Dict[str, Any]] = []

    for ch in chans:
        username = ch.get("username")
        title = ch.get("title")
        tg_id = ch.get("tg_id")
        last = last_news_date(username) if username else None

        age_h = None
        if last:
            if last.tzinfo is None:
                last = last.replace(tzinfo=dt.timezone.utc)
            else:
                last = last.astimezone(dt.timezone.utc)
            age_h = (now - last).total_seconds() / 3600.0

        rows.append({
            "username": username,
            "title": title,
            "tg_id": tg_id,
            "is_active": int(ch.get("is_active", 1) or 0),
            "import_error": ch.get("import_error"),
            "last_news_date": last.isoformat() if last else None,
            "age_hours": round(age_h, 2) if age_h is not None else None,
        })

    summary = {
        "total": len(rows),
        "active": sum(1 for r in rows if r["is_active"] == 1),
        "inactive": sum(1 for r in rows if r["is_active"] == 0),
        "no_access": sum(1 for r in rows if r.get("import_error")),
        "no_posts_24h": sum(
            1 for r in rows
            if (r.get("age_hours") is None or (r.get("age_hours") is not None and r["age_hours"] > 24))
        ),
    }

    return {"generated_at": now.isoformat(), "rows": rows, "summary": summary}


def save_csv(report: Dict[str, Any], prefix: str = "tg_report") -> str:
    """Сохраняет только CSV в tools/reports и возвращает путь."""
    ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(REPORT_DIR, f"{prefix}_{ts}.csv")

    import csv
    cols = [
        "username", "title", "tg_id", "is_active", "import_error",
        "last_news_date", "age_hours"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in report["rows"]:
            w.writerow({k: r.get(k) for k in cols})

    return csv_path


def print_summary(report: Dict[str, Any]) -> None:
    s = report["summary"]
    print(f"Generated at: {report['generated_at']}")
    print(f"Total channels: {s['total']} | active: {s['active']} | inactive: {s['inactive']}")
    print(f"No access(import_error): {s['no_access']} | No posts >24h: {s['no_posts_24h']}")
    print("\nTop stale (by age):")
    stale = sorted(
        [r for r in report["rows"] if r.get("age_hours") is not None],
        key=lambda x: x["age_hours"],
        reverse=True,
    )[:15]
    for r in stale:
        print(f" @{(r['username'] or ''):20s} {r['age_hours']:7.2f}h  last={r['last_news_date']}")


def main():
    p = argparse.ArgumentParser(description="Отчёт по Телеграм-каналам из Mongo (trading.news / trading.tg_channels)")
    p.add_argument("--all", action="store_true", help="Включать неактивные каналы (по умолчанию только is_active=1)")
    args = p.parse_args()

    report = build_snapshot(only_active=not args.all)
    csv_path = save_csv(report, prefix="tg_report")
    print_summary(report)
    print(f"\nSaved CSV: {csv_path}")


if __name__ == "__main__":
    main()

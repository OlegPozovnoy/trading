from __future__ import annotations

import csv
import datetime as dt
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


FIELDS = [
    "ts",
    "session",
    "wait_seconds",
    "source",   # "log" | "exception"
    "message",
]


@dataclass
class FloodWaitCSV:
    out_dir: Path
    session_name: str

    cycle_started_at: Optional[dt.datetime] = None
    rows: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def output_path(self) -> Path:
        return self.out_dir / f"floodwait_{self.session_name}_last.csv"

    def reset_for_cycle(self, cycle_started_at: dt.datetime) -> None:
        self.cycle_started_at = cycle_started_at
        self.rows = []

    def add(self, *, wait_seconds: int, source: str, message: str) -> None:
        now = dt.datetime.now()
        self.rows.append(
            {
                "ts": now.isoformat(sep=" ", timespec="seconds"),
                "session": self.session_name,
                "wait_seconds": int(wait_seconds),
                "source": source,
                "message": message,
            }
        )

    def flush_overwrite(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for r in self.rows:
                w.writerow(r)


class FloodWaitLogHandler(logging.Handler):
    """
    Ловит строки вида:
    WARNING:pyrogram.session.session:[my_account_public] Waiting for 28 seconds before continuing ...
    и кладёт в FloodWaitCSV (в память, без записи на диск).
    """

    _re = re.compile(r"Waiting for\s+(\d+)\s+seconds", re.IGNORECASE)

    def __init__(self, flood_csv: FloodWaitCSV):
        super().__init__(level=logging.WARNING)
        self.flood_csv = flood_csv

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
            m = self._re.search(msg)
            if not m:
                return

            wait_seconds = int(m.group(1))

            # Очень важно: пишем в CSV ТОЛЬКО если это сообщение про НАШУ сессию
            # (pyrogram добавляет [session_name] в message)
            if f"[{self.flood_csv.session_name}]" not in msg:
                return

            self.flood_csv.add(wait_seconds=wait_seconds, source="log", message=msg)
        except Exception:
            # логгер не должен падать
            return

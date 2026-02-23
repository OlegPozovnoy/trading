from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


FIELDS = [
    "ts",
    "session",
    "channel_title",
    "channel_username",
    "tg_id",
    "out_id",
    "tags",
    "error_code",
    "error_type",
    "message",
    "action",
    "wait_seconds",
]


@dataclass
class InvalidChannelsCSV:
    out_dir: Path
    session_name: str

    cycle_started_at: Optional[dt.datetime] = None
    rows: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def output_path(self) -> Path:
        # ОДИН файл “последний прогон”, перезаписываем в конце цикла
        return self.out_dir / f"invalid_channels_{self.session_name}_last.csv"

    def reset_for_cycle(self, cycle_started_at: dt.datetime) -> None:
        self.cycle_started_at = cycle_started_at
        self.rows = []

    def add(
        self,
        channel: Dict[str, Any],
        *,
        error_code: str,
        exc: Exception,
        action: str = "",
        wait_seconds: Optional[int] = None,
    ) -> None:
        now = dt.datetime.now()
        self.rows.append(
            {
                "ts": now.isoformat(sep=" ", timespec="seconds"),
                "session": self.session_name,
                "channel_title": channel.get("title", ""),
                "channel_username": channel.get("username", ""),
                "tg_id": channel.get("tg_id", ""),
                "out_id": channel.get("out_id", ""),
                "tags": ",".join(channel.get("tags", []) or []),
                "error_code": error_code,
                "error_type": type(exc).__name__,
                "message": str(exc),
                "action": action,
                "wait_seconds": wait_seconds if wait_seconds is not None else "",
            }
        )

    def flush_overwrite(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for r in self.rows:
                w.writerow(r)

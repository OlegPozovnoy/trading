# create_tgchannels/channel_status_csv.py
from __future__ import annotations

import csv
import datetime as dt
import logging
import os
import re
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

try:
    from .pyrogram_errors import map_pyrogram_error
except ImportError:
    from create_tgchannels.pyrogram_errors import map_pyrogram_error


def _utcnow_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8", newline="") as f:
        tmp = f.name
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, str(path))


@dataclass
class ChannelStatusRow:
    key: str
    tg_id: str = ""
    username: str = ""
    title: str = ""
    is_private: str = ""
    tags: str = ""  # pipe-separated

    # динамика
    last_status: str = "UNKNOWN"  # OK / ERROR / SKIP / UNKNOWN
    last_error_code: str = ""
    last_error_message: str = ""
    last_hint: str = ""
    last_action: str = ""

    last_session: str = ""
    last_attempt_utc: str = ""
    last_success_utc: str = ""

    attempts: int = 0
    ok: int = 0
    error: int = 0

    last_out_id: str = ""


class ChannelStatusKVCSV:
    """
    In-memory KV store -> CSV snapshot (overwrite).
    Идея: держим состояние всех каналов в dict, обновляем по мере обработки,
    а на диск пишем редко (например, после каждого цикла while/gather).
    """

    HEADER = [
        "key",
        "tg_id",
        "username",
        "title",
        "is_private",
        "tags",
        "last_status",
        "last_error_code",
        "last_error_message",
        "last_hint",
        "last_action",
        "last_session",
        "last_attempt_utc",
        "last_success_utc",
        "attempts",
        "ok",
        "error",
        "last_out_id",
    ]

    def __init__(self, base_dir: Path, filename: str = "channels_status.csv") -> None:
        self.path = Path(base_dir) / filename
        self._rows: Dict[str, ChannelStatusRow] = {}
        self._title_index: Dict[str, str] = {}  # lower(title)->key (best-effort)
        self._username_index: Dict[str, str] = {}  # lower(username)->key
        self._load_if_exists()

    @staticmethod
    def _key_for_channel(ch: Dict[str, Any]) -> str:
        tg_id = ch.get("tg_id")
        if tg_id:
            return f"tg_id:{tg_id}"
        username = (ch.get("username") or "").strip()
        if username:
            return f"username:{username.lower()}"
        title = (ch.get("title") or "").strip()
        return f"title:{title.lower()}"

    def _index_row(self, row: ChannelStatusRow) -> None:
        if row.title:
            self._title_index[row.title.strip().lower()] = row.key
        if row.username:
            self._username_index[row.username.strip().lower()] = row.key

    def _load_if_exists(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    key = (r.get("key") or "").strip()
                    if not key:
                        continue
                    row = ChannelStatusRow(
                        key=key,
                        tg_id=r.get("tg_id", "") or "",
                        username=r.get("username", "") or "",
                        title=r.get("title", "") or "",
                        is_private=r.get("is_private", "") or "",
                        tags=r.get("tags", "") or "",
                        last_status=r.get("last_status", "UNKNOWN") or "UNKNOWN",
                        last_error_code=r.get("last_error_code", "") or "",
                        last_error_message=r.get("last_error_message", "") or "",
                        last_hint=r.get("last_hint", "") or "",
                        last_action=r.get("last_action", "") or "",
                        last_session=r.get("last_session", "") or "",
                        last_attempt_utc=r.get("last_attempt_utc", "") or "",
                        last_success_utc=r.get("last_success_utc", "") or "",
                        attempts=int(r.get("attempts", "0") or 0),
                        ok=int(r.get("ok", "0") or 0),
                        error=int(r.get("error", "0") or 0),
                        last_out_id=r.get("last_out_id", "") or "",
                    )
                    self._rows[key] = row
                    self._index_row(row)
        except Exception:
            logging.getLogger(__name__).exception("Failed to load %s", self.path)

    def ensure_channels(self, channels: Iterable[Dict[str, Any]], is_private: Optional[bool] = None) -> None:
        for ch in channels:
            self.ensure_channel(ch, is_private=is_private)

    def ensure_channel(self, ch: Dict[str, Any], is_private: Optional[bool] = None) -> str:
        key = self._key_for_channel(ch)
        if key not in self._rows:
            tags = ch.get("tags") or []
            if isinstance(tags, list):
                tags_s = "|".join([str(x) for x in tags])
            else:
                tags_s = str(tags)
            row = ChannelStatusRow(
                key=key,
                tg_id=str(ch.get("tg_id") or ""),
                username=str(ch.get("username") or ""),
                title=str(ch.get("title") or ""),
                is_private=str(int(bool(is_private))) if is_private is not None else "",
                tags=tags_s,
                last_out_id=str(ch.get("out_id") or ""),
            )
            self._rows[key] = row
            self._index_row(row)
        else:
            # обновим метаданные, если появились
            row = self._rows[key]
            if ch.get("tg_id"):
                row.tg_id = str(ch.get("tg_id"))
            if ch.get("username"):
                row.username = str(ch.get("username"))
                self._index_row(row)
            if ch.get("title"):
                row.title = str(ch.get("title"))
                self._index_row(row)
            if is_private is not None:
                row.is_private = str(int(bool(is_private)))
            if ch.get("out_id") is not None:
                row.last_out_id = str(ch.get("out_id"))
            tags = ch.get("tags")
            if tags is not None:
                if isinstance(tags, list):
                    row.tags = "|".join([str(x) for x in tags])
                else:
                    row.tags = str(tags)
        return key

    def _get_by_key_or_best_effort(self, ch: Optional[Dict[str, Any]] = None, *, title: str = "", username: str = "") -> ChannelStatusRow:
        if ch is not None:
            key = self.ensure_channel(ch, is_private=None)
            return self._rows[key]

        if username:
            k = self._username_index.get(username.strip().lower())
            if k and k in self._rows:
                return self._rows[k]

        if title:
            k = self._title_index.get(title.strip().lower())
            if k and k in self._rows:
                return self._rows[k]

        # fallback: создаём “виртуальный” ключ
        pseudo = {"title": title or username or "unknown"}
        key = self.ensure_channel(None if pseudo is None else pseudo, is_private=None)  # type: ignore[arg-type]
        return self._rows[key]

    def mark_ok(
        self,
        ch: Dict[str, Any],
        *,
        session_name: str,
        out_id: Optional[Any] = None,
    ) -> None:
        row = self._get_by_key_or_best_effort(ch)
        row.attempts += 1
        row.ok += 1
        row.last_status = "OK"
        row.last_error_code = ""
        row.last_error_message = ""
        row.last_hint = ""
        row.last_action = ""
        row.last_session = session_name
        row.last_attempt_utc = _utcnow_iso()
        row.last_success_utc = row.last_attempt_utc
        if out_id is not None:
            row.last_out_id = str(out_id)

    def mark_error(
        self,
        ch: Optional[Dict[str, Any]] = None,
        *,
        session_name: str,
        exc: Optional[Exception] = None,
        error_code: str = "",
        error_message: str = "",
        title: str = "",
        username: str = "",
        out_id: Optional[Any] = None,
    ) -> None:
        row = self._get_by_key_or_best_effort(ch, title=title, username=username)
        row.attempts += 1
        row.error += 1
        row.last_status = "ERROR"
        row.last_session = session_name
        row.last_attempt_utc = _utcnow_iso()
        if out_id is not None:
            row.last_out_id = str(out_id)

        if exc is not None:
            m = map_pyrogram_error(exc)
            row.last_error_code = m.get("error_code") or type(exc).__name__
            row.last_error_message = str(exc)
            row.last_hint = m.get("hint") or ""
            row.last_action = m.get("action") or ""
        else:
            row.last_error_code = error_code or "ERROR"
            row.last_error_message = error_message or ""
            row.last_hint = ""
            row.last_action = ""

    def flush(self) -> None:
        # snapshot -> overwrite
        rows = list(self._rows.values())

        def _sort_key(r: ChannelStatusRow):
            # private first, then title
            priv = r.is_private
            try:
                priv_i = int(priv) if priv != "" else 9
            except Exception:
                priv_i = 9
            return (priv_i, (r.title or r.username or r.key).lower())

        rows.sort(key=_sort_key)

        out_lines = []
        out_lines.append(",".join(self.HEADER))

        for r in rows:
            d = asdict(r)
            # гарантируем порядок и экранирование
            buf = []
            for col in self.HEADER:
                v = d.get(col, "")
                if v is None:
                    v = ""
                buf.append(v)
            # csv writer для одной строки
            import io
            s = io.StringIO()
            w = csv.writer(s)
            w.writerow(buf)
            out_lines.append(s.getvalue().rstrip("\r\n"))

        _atomic_write_text(self.path, "\n".join(out_lines) + "\n")


class ChannelInvalidLogHandler(logging.Handler):
    """
    Ловит твои WARNING вида:
      [my_account_tgchannels] CHANNEL_INVALID | Шпион РЦБ | Telegram says: [400 CHANNEL_INVALID] ...
    и обновляет status-store в памяти (без записи на диск).
    """

    RX = re.compile(r"^\[(?P<session>[^\]]+)\]\s+CHANNEL_INVALID\s+\|\s+(?P<title>[^|]+?)\s+\|\s+(?P<msg>.+)$")

    def __init__(self, store: ChannelStatusKVCSV) -> None:
        super().__init__(level=logging.WARNING)
        self.store = store

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
            m = self.RX.match(msg.strip())
            if not m:
                return
            session = m.group("session").strip()
            title = m.group("title").strip()
            full = m.group("msg").strip()
            self.store.mark_error(
                None,
                session_name=session,
                error_code="CHANNEL_INVALID",
                error_message=full,
                title=title,
            )
        except Exception:
            # нельзя падать из логгера
            pass

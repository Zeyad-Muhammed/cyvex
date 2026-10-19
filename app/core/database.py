"""SQLite persistence layer.

A single connection is shared across worker threads with a re-entrant lock.
WAL mode keeps reads concurrent while a scan writes progress.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from . import paths

_SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signatures (
    hash     TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'high',
    source   TEXT NOT NULL DEFAULT 'local',
    added    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_history (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_type      TEXT NOT NULL,
    target         TEXT,
    started        TEXT NOT NULL,
    finished       TEXT,
    duration       REAL DEFAULT 0,
    files_scanned  INTEGER DEFAULT 0,
    threats_found  INTEGER DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS detections (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER,
    path      TEXT NOT NULL,
    name      TEXT NOT NULL,
    engine    TEXT NOT NULL,
    severity  TEXT NOT NULL DEFAULT 'high',
    action    TEXT NOT NULL DEFAULT 'detected',
    sha256    TEXT,
    created   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quarantine (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path TEXT NOT NULL,
    store_name    TEXT NOT NULL,
    name          TEXT NOT NULL,
    engine        TEXT,
    severity      TEXT DEFAULT 'high',
    size          INTEGER DEFAULT 0,
    sha256        TEXT,
    created       TEXT NOT NULL,
    restored      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vt_cache (
    hash      TEXT PRIMARY KEY,
    positives INTEGER DEFAULT 0,
    total     INTEGER DEFAULT 0,
    permalink TEXT,
    report    TEXT,
    scanned   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exclusions (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    path    TEXT NOT NULL UNIQUE,
    created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    kind     TEXT NOT NULL,
    message  TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    created  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shield_backups (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path TEXT NOT NULL,
    store_name    TEXT NOT NULL,
    size          INTEGER DEFAULT 0,
    sha256        TEXT,
    created       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_detections_scan ON detections(scan_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON activity(created DESC);
CREATE INDEX IF NOT EXISTS idx_history_started ON scan_history(started DESC);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or paths.db_path()
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA foreign_keys=ON;")
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # -- low level ---------------------------------------------------------
    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self._conn.execute(sql, tuple(params))
            self._conn.commit()
            return cur

    def query(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with self._lock:
            cur = self._conn.execute(sql, tuple(params))
            return cur.fetchall()

    def query_one(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # -- settings ----------------------------------------------------------
    def get_setting(self, key: str, default: Any = None) -> Any:
        row = self.query_one("SELECT value FROM settings WHERE key = ?", (key,))
        if row is None:
            return default
        try:
            return json.loads(row["value"])
        except (ValueError, TypeError):
            return row["value"]

    def set_setting(self, key: str, value: Any) -> None:
        self.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value)),
        )

    def all_settings(self) -> dict[str, Any]:
        return {r["key"]: self.get_setting(r["key"]) for r in self.query("SELECT key FROM settings")}

    # -- activity ----------------------------------------------------------
    def add_activity(self, kind: str, message: str, severity: str = "info") -> dict[str, Any]:
        created = utcnow()
        cur = self.execute(
            "INSERT INTO activity(kind, message, severity, created) VALUES(?,?,?,?)",
            (kind, message, severity, created),
        )
        return {
            "id": cur.lastrowid,
            "kind": kind,
            "message": message,
            "severity": severity,
            "created": created,
        }

    def recent_activity(self, limit: int = 40) -> list[dict[str, Any]]:
        rows = self.query(
            "SELECT * FROM activity ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in rows]

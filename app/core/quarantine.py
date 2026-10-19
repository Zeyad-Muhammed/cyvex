"""Quarantine vault.

Detected files are moved into a vault and stored with an XOR stream cipher and
a small header. This is *obfuscation* (the goal is to prevent the quarantined
sample from being launched or read by other tools), not strong cryptography,
and it is reversible so the user can restore false positives.
"""
from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path
from typing import Any

from . import paths
from .database import Database, utcnow

HEADER = b"NQRN1"
CHUNK = 1024 * 1024


def _keystream(store_name: str) -> bytes:
    return hashlib.sha256(b"NOVU-VAULT-V1" + store_name.encode("utf-8")).digest()


def _xor_stream(data: bytes, key: bytes, offset: int = 0) -> bytes:
    key_len = len(key)
    return bytes(b ^ key[(offset + i) % key_len] for i, b in enumerate(data))


class QuarantineManager:
    def __init__(self, db: Database) -> None:
        self._db = db
        self._dir = paths.quarantine_dir()

    def _store_path(self, store_name: str) -> Path:
        return self._dir / store_name

    def quarantine_file(self, path: str, name: str, engine: str,
                        severity: str, sha256: str | None) -> dict[str, Any]:
        source = Path(path)
        if not source.exists():
            return {"ok": False, "error": "missing"}
        store_name = f"{utcnow().replace(':', '').replace('-', '')}_{secrets.token_hex(8)}.qtn"
        size = 0
        try:
            size = source.stat().st_size
            key = _keystream(store_name)
            with open(source, "rb") as src, open(self._store_path(store_name), "wb") as dst:
                dst.write(HEADER)
                offset = 0
                while True:
                    chunk = src.read(CHUNK)
                    if not chunk:
                        break
                    dst.write(_xor_stream(chunk, key, offset))
                    offset += len(chunk)
            os.remove(source)
        except (OSError, PermissionError) as exc:
            try:
                self._store_path(store_name).unlink(missing_ok=True)
            except OSError:
                pass
            return {"ok": False, "error": str(exc)}

        cur = self._db.execute(
            "INSERT INTO quarantine(original_path, store_name, name, engine, severity, size, sha256, created) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (str(source), store_name, name, engine, severity, size, sha256, utcnow()),
        )
        return {
            "ok": True,
            "id": cur.lastrowid,
            "original_path": str(source),
            "store_name": store_name,
            "name": name,
            "engine": engine,
            "severity": severity,
            "size": size,
            "sha256": sha256,
            "created": utcnow(),
        }

    def list_entries(self) -> list[dict[str, Any]]:
        rows = self._db.query("SELECT * FROM quarantine ORDER BY id DESC")
        return [dict(r) for r in rows]

    def get(self, entry_id: int) -> dict[str, Any] | None:
        row = self._db.query_one("SELECT * FROM quarantine WHERE id = ?", (entry_id,))
        return dict(row) if row else None

    def restore(self, entry_id: int) -> dict[str, Any]:
        entry = self.get(entry_id)
        if not entry:
            return {"ok": False, "error": "not-found"}
        store = self._store_path(entry["store_name"])
        if not store.exists():
            return {"ok": False, "error": "vault-file-missing"}
        target = Path(entry["original_path"])
        try:
            if target.exists():
                target = target.with_suffix(target.suffix + ".restored")
            target.parent.mkdir(parents=True, exist_ok=True)
            key = _keystream(entry["store_name"])
            with open(store, "rb") as src, open(target, "wb") as dst:
                header = src.read(len(HEADER))
                if header != HEADER:
                    return {"ok": False, "error": "corrupt-vault"}
                offset = 0
                while True:
                    chunk = src.read(CHUNK)
                    if not chunk:
                        break
                    dst.write(_xor_stream(chunk, key, offset))
                    offset += len(chunk)
            store.unlink(missing_ok=True)
        except (OSError, PermissionError) as exc:
            return {"ok": False, "error": str(exc)}
        self._db.execute("UPDATE quarantine SET restored = 1 WHERE id = ?", (entry_id,))
        self._db.execute("DELETE FROM quarantine WHERE id = ?", (entry_id,))
        return {"ok": True, "restored_to": str(target)}

    def delete(self, entry_id: int) -> dict[str, Any]:
        entry = self.get(entry_id)
        if not entry:
            return {"ok": False, "error": "not-found"}
        self._store_path(entry["store_name"]).unlink(missing_ok=True)
        self._db.execute("DELETE FROM quarantine WHERE id = ?", (entry_id,))
        return {"ok": True}

    def delete_all(self) -> dict[str, Any]:
        count = 0
        for entry in self.list_entries():
            self._store_path(entry["store_name"]).unlink(missing_ok=True)
            self._db.execute("DELETE FROM quarantine WHERE id = ?", (entry["id"],))
            count += 1
        return {"ok": True, "deleted": count}

    def count(self) -> int:
        row = self._db.query_one("SELECT COUNT(*) AS c FROM quarantine")
        return int(row["c"]) if row else 0

    def total_size(self) -> int:
        row = self._db.query_one("SELECT COALESCE(SUM(size),0) AS s FROM quarantine")
        return int(row["s"]) if row else 0

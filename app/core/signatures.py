"""Signature database and update handling.

Detections from signatures are exact: a file's SHA-256 is looked up in a set
of publicly known malicious hashes. The bundled seed set contains the EICAR
anti-malware test hash (a harmless, official industry test string) so the
engine can be verified end to end without distributing real malware.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from . import paths
from .database import Database, utcnow

# Official EICAR test file - hashing it must produce THREAT_EICAR_SHA256.
EICAR_SHA256 = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
EICAR_MARKER = b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"


class SignatureEngine:
    def __init__(self, db: Database) -> None:
        self._db = db
        self._hashes: dict[str, tuple[str, str]] = {}
        self._seeded = False
        self.reload()

    # -- loading -----------------------------------------------------------
    def reload(self) -> None:
        self._hashes = {
            row["hash"].lower(): (row["name"], row["severity"])
            for row in self._db.query("SELECT hash, name, severity FROM signatures")
        }

    def seed_defaults(self) -> int:
        if self._seeded and self._hashes:
            return 0
        added = 0
        seed_file = paths.seeds_dir() / "default_signatures.json"
        if seed_file.exists():
            try:
                data = json.loads(seed_file.read_text(encoding="utf-8"))
                added += self.add_many(data.get("signatures", []))
            except (OSError, ValueError):
                pass
        # Guarantee the EICAR test signature is present.
        if EICAR_SHA256 not in self._hashes:
            added += self.add_many([{
                "hash": EICAR_SHA256,
                "name": "EICAR-Test-File",
                "severity": "medium",
                "source": "eicar",
            }])
        self._seeded = True
        self.reload()
        return added

    def add_many(self, entries: list[dict[str, Any]]) -> int:
        added = 0
        now = utcnow()
        for entry in entries:
            digest = str(entry.get("hash", "")).strip().lower()
            if len(digest) != 64:
                continue
            cur = self._db.execute(
                "INSERT INTO signatures(hash, name, severity, source, added) "
                "VALUES(?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET "
                "name=excluded.name, severity=excluded.severity",
                (
                    digest,
                    entry.get("name", "Unknown"),
                    entry.get("severity", "high"),
                    entry.get("source", "imported"),
                    entry.get("added", now),
                ),
            )
            added += 1 if cur.rowcount else 0
        self.reload()
        return added

    def update_from_url(self, url: str, timeout: int = 20) -> dict[str, Any]:
        """Download a JSON signature pack and import it."""
        import requests

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI
            return {"ok": False, "error": str(exc), "added": 0}
        entries = payload.get("signatures", payload if isinstance(payload, list) else [])
        added = self.add_many(entries)
        self._db.set_setting("signatures_updated", utcnow())
        return {"ok": True, "added": added}

    # -- lookup ------------------------------------------------------------
    def match_hash(self, digest: str | None) -> tuple[str, str] | None:
        if not digest:
            return None
        return self._hashes.get(digest.lower())

    def match_content(self, head: bytes) -> tuple[str, str] | None:
        if EICAR_MARKER in head:
            return ("EICAR-Test-File", "medium")
        return None

    def count(self) -> int:
        return len(self._hashes)

    def last_updated(self) -> str | None:
        return self._db.get_setting("signatures_updated")

    @staticmethod
    def builtin_hash() -> str:
        return EICAR_SHA256

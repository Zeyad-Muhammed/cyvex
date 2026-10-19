"""Optional VirusTotal v3 hash reputation lookups.

No file is ever uploaded: only the SHA-256 is queried, which keeps local
files private and matches how desktop scanners enrich a verdict with cloud
reputation. Results are cached so the public rate limit (4 requests/minute on
free keys) is respected.
"""
from __future__ import annotations

import json
import time
from typing import Any

import requests

from .database import Database, utcnow

API_URL = "https://www.virustotal.com/api/v3/files/{hash}"
CACHE_TTL_SECONDS = 24 * 60 * 60


class VirusTotalClient:
    def __init__(self, db: Database) -> None:
        self._db = db
        self._session = requests.Session()
        self._last_call = 0.0

    def is_configured(self, api_key: str | None) -> bool:
        return bool(api_key and len(api_key) >= 32)

    def _cached(self, digest: str) -> dict[str, Any] | None:
        row = self._db.query_one("SELECT * FROM vt_cache WHERE hash = ?", (digest,))
        if not row:
            return None
        try:
            from datetime import datetime, timezone

            scanned = datetime.fromisoformat(row["scanned"])
            age = (datetime.now(timezone.utc) - scanned).total_seconds()
        except ValueError:
            age = CACHE_TTL_SECONDS + 1
        if age > CACHE_TTL_SECONDS:
            return None
        report = row["report"]
        payload = {
            "hash": row["hash"],
            "positives": row["positives"],
            "total": row["total"],
            "permalink": row["permalink"],
            "cached": True,
        }
        if report:
            try:
                payload["engines"] = json.loads(report)
            except ValueError:
                pass
        payload["verdict"] = ("malicious" if row["positives"] > 0 else "clean")
        return payload

    def _store(self, digest: str, positives: int, total: int,
               permalink: str, engines: dict[str, str]) -> None:
        self._db.execute(
            "INSERT INTO vt_cache(hash, positives, total, permalink, report, scanned) "
            "VALUES(?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET "
            "positives=excluded.positives, total=excluded.total, "
            "permalink=excluded.permalink, report=excluded.report, scanned=excluded.scanned",
            (digest, positives, total, permalink, json.dumps(engines), utcnow()),
        )

    def check_hash(self, digest: str, api_key: str) -> dict[str, Any]:
        digest = (digest or "").lower()
        if len(digest) != 64:
            return {"ok": False, "error": "invalid-hash"}
        cached = self._cached(digest)
        if cached:
            return {"ok": True, **cached}
        if not self.is_configured(api_key):
            return {"ok": False, "error": "not-configured"}

        wait = 15 - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.time()

        try:
            response = self._session.get(
                API_URL.format(hash=digest),
                headers={"x-apikey": api_key},
                timeout=20,
            )
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}

        if response.status_code == 404:
            self._store(digest, 0, 0, "", {})
            return {"ok": True, "hash": digest, "positives": 0, "total": 0,
                    "permalink": "", "engines": {}, "verdict": "unknown",
                    "cached": False, "note": "not-in-virustotal"}
        if response.status_code == 401:
            return {"ok": False, "error": "invalid-api-key"}
        if response.status_code == 429:
            return {"ok": False, "error": "rate-limit"}
        if response.status_code != 200:
            return {"ok": False, "error": f"http-{response.status_code}"}

        try:
            data = response.json()["data"]["attributes"]
        except (KeyError, ValueError):
            return {"ok": False, "error": "bad-response"}

        stats = data.get("last_analysis_stats", {})
        positives = int(stats.get("malicious", 0)) + int(stats.get("suspicious", 0))
        total = sum(int(v) for v in stats.values() if isinstance(v, int))
        engines: dict[str, str] = {}
        for engine, result in (data.get("last_analysis_results") or {}).items():
            category = result.get("category", "")
            if category in ("malicious", "suspicious"):
                engines[engine] = result.get("result") or category

        permalink = f"https://www.virustotal.com/gui/file/{digest}"
        self._store(digest, positives, total, permalink, engines)
        return {
            "ok": True,
            "hash": digest,
            "positives": positives,
            "total": total,
            "permalink": permalink,
            "engines": engines,
            "verdict": "malicious" if positives else "clean",
            "cached": False,
        }

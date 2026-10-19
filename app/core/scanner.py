"""Scan engine.

Supports quick, full and custom scans with pause/resume/stop, live progress,
signature + heuristic + optional cloud detection, and automatic quarantine.
Runs on a dedicated worker thread so the UI never blocks.
"""
from __future__ import annotations

import os
import threading
import time
import zipfile
from pathlib import Path
from typing import Any

from . import heuristics, paths, winutil
from .database import Database, utcnow
from .events import EventBus
from .hashing import sha256_file
from .quarantine import QuarantineManager
from .settings import Settings
from .signatures import SignatureEngine
from .virustotal import VirusTotalClient

HEAD_BYTES = 64 * 1024
ARCHIVE_EXTENSIONS = {".zip", ".jar"}
SKIP_DIR_NAMES = {
    "$recycle.bin", "system volume information", "windows.old", "recovery",
    "node_modules", ".git", ".venv", "__pycache__",
}
SKIP_DIR_SUBSTRINGS = ("\\windows\\winsxs", "\\windows\\servicing")


class ScanEngine:
    def __init__(self, db: Database, settings: Settings, signatures: SignatureEngine,
                 quarantine: QuarantineManager, virustotal: VirusTotalClient,
                 events: EventBus) -> None:
        self._db = db
        self._settings = settings
        self._signatures = signatures
        self._quarantine = quarantine
        self._vt = virustotal
        self._events = events

        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._pause = threading.Event()
        self._stop = threading.Event()
        self._pause.set()  # set == running, cleared == paused

        self._state: dict[str, Any] = {
            "running": False,
            "scan_id": None,
            "scan_type": None,
            "phase": "idle",
            "status": "idle",
            "files_scanned": 0,
            "total_files": 0,
            "threats_found": 0,
            "current_path": "",
            "started": None,
            "percent": 0.0,
            "paused": False,
        }

    # -- public control ----------------------------------------------------
    def start(self, scan_type: str, targets: list[str] | None = None) -> dict[str, Any]:
        with self._lock:
            if self._state["running"]:
                return {"ok": False, "error": "scan-already-running"}

        resolved = self._resolve_targets(scan_type, targets)
        if not resolved:
            return {"ok": False, "error": "no-targets"}

        cur = self._db.execute(
            "INSERT INTO scan_history(scan_type, target, started, status) VALUES(?,?,?,?)",
            (scan_type, "; ".join(resolved), utcnow(), "running"),
        )
        scan_id = cur.lastrowid

        self._pause.set()
        self._stop.clear()
        with self._lock:
            self._state.update({
                "running": True, "scan_id": scan_id, "scan_type": scan_type,
                "phase": "counting", "status": "running", "files_scanned": 0,
                "total_files": 0, "threats_found": 0, "current_path": "",
                "started": utcnow(), "percent": 0.0, "paused": False,
            })

        self._thread = threading.Thread(
            target=self._run, args=(scan_id, scan_type, resolved), daemon=True, name="novu-scan"
        )
        self._thread.start()
        self._emit_state()
        self._events.emit({"type": "scan:started", "scan_id": scan_id, "scan_type": scan_type})
        self._events.emit({"type": "activity", "kind": "scan",
                           "message": f"Scan started ({scan_type})", "severity": "info"})
        return {"ok": True, "scan_id": scan_id}

    def pause(self) -> dict[str, Any]:
        with self._lock:
            if not self._state["running"]:
                return {"ok": False}
            self._pause.clear()
            self._state["paused"] = True
        self._emit_state()
        return {"ok": True}

    def resume(self) -> dict[str, Any]:
        with self._lock:
            self._pause.set()
            self._state["paused"] = False
        self._emit_state()
        return {"ok": True}

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        self._pause.set()  # release a paused worker so it can observe the stop
        return {"ok": True}

    def is_running(self) -> bool:
        return self._state["running"]

    def scan_single(self, path: str, scan_id: int | None = None) -> bool:
        """Scan one file (used by real-time protection, USB and manual checks)."""
        if not path or not os.path.isfile(path):
            return False
        data_dir = os.path.normcase(str(paths.data_dir()))
        if os.path.normcase(path).startswith(data_dir):
            return False
        if self._is_excluded(path, self._load_exclusions()):
            return False
        max_bytes = int(self._settings.get("scan_max_size_mb", 64)) * 1024 * 1024
        return self._scan_file(path, max_bytes, scan_id)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    # -- internal ----------------------------------------------------------
    def _resolve_targets(self, scan_type: str, targets: list[str] | None) -> list[str]:
        if scan_type == "quick":
            return winutil.quick_scan_targets()
        if scan_type == "full":
            return winutil.fixed_drives()
        if scan_type == "custom":
            return [t for t in (targets or []) if t and Path(t).exists()]
        if scan_type == "removable":
            return winutil.removable_drives()
        return []

    def _run(self, scan_id: int, scan_type: str, targets: list[str]) -> None:
        started = time.time()
        files_scanned = 0
        threats = 0
        status = "completed"
        try:
            total = self._count_files(targets)
            with self._lock:
                self._state["total_files"] = total
                self._state["phase"] = "scanning"
            self._emit_state()

            exclusions = self._load_exclusions()
            max_bytes = int(self._settings.get("scan_max_size_mb", 64)) * 1024 * 1024
            seen: set[str] = set()

            for path in self._iter_files(targets, exclusions):
                if self._stop.is_set():
                    status = "stopped"
                    break
                if not self._pause.wait(timeout=None):
                    break
                if self._stop.is_set():
                    status = "stopped"
                    break

                norm = os.path.normcase(path)
                if norm in seen:
                    continue
                seen.add(norm)

                files_scanned += 1
                with self._lock:
                    self._state["files_scanned"] = files_scanned
                    self._state["current_path"] = path
                    self._state["percent"] = round(min(99.0, files_scanned / total * 100), 1) if total else 0.0

                detected = self._scan_file(path, max_bytes, scan_id)
                if detected:
                    threats += 1
                    with self._lock:
                        self._state["threats_found"] = threats
                if files_scanned % 25 == 0:
                    self._emit_state()

            with self._lock:
                self._state["status"] = status
                self._state["running"] = False
                self._state["percent"] = 100.0 if status == "completed" else self._state["percent"]
        except Exception as exc:  # noqa: BLE001 - report, never crash the thread
            status = "error"
            self._db.add_activity("scan", f"Scan error: {exc}", "error")
            with self._lock:
                self._state["running"] = False
                self._state["status"] = "error"
        finally:
            duration = round(time.time() - started, 2)
            self._db.execute(
                "UPDATE scan_history SET finished=?, duration=?, files_scanned=?, "
                "threats_found=?, status=? WHERE id=?",
                (utcnow(), duration, files_scanned, threats, status, scan_id),
            )
            self._emit_state()
            self._events.emit({
                "type": "scan:finished",
                "scan_id": scan_id,
                "status": status,
                "threats_found": threats,
                "files_scanned": files_scanned,
                "duration": duration,
            })
            self._events.emit({
                "type": "activity", "kind": "scan",
                "message": f"Scan {status}: {files_scanned} files, {threats} threats",
                "severity": "warning" if threats else "success",
            })

    def _scan_file(self, path: str, max_bytes: int, scan_id: int) -> bool:
        try:
            size = os.path.getsize(path)
        except OSError:
            return False

        head = b""
        try:
            with open(path, "rb") as handle:
                head = handle.read(HEAD_BYTES)
        except (OSError, PermissionError):
            return False

        findings: list[dict[str, Any]] = []
        digest: str | None = None

        # 1. signature hash
        if size <= max_bytes:
            digest = sha256_file(path, should_stop=self._stop.is_set)
            if digest:
                match = self._signatures.match_hash(digest)
                if match:
                    findings.append({"name": match[0], "severity": match[1],
                                     "engine": "signature", "detail": "Known malicious hash"})

        # 2. content signature (EICAR)
        content_match = self._signatures.match_content(head)
        if content_match:
            findings.append({"name": content_match[0], "severity": content_match[1],
                             "engine": "signature", "detail": "Known test signature"})

        # 3. heuristics
        for finding in heuristics.analyze(path, head, size):
            findings.append({"name": finding["name"], "severity": finding["severity"],
                             "engine": "heuristic", "detail": finding.get("detail", "")})

        # 4. archive inspection
        ext = Path(path).suffix.lower()
        if self._settings.get("scan_archives", True) and ext in ARCHIVE_EXTENSIONS:
            archive_finding = self._scan_archive(path)
            if archive_finding:
                findings.append(archive_finding)

        # 5. optional cloud enrichment for suspicious files
        if findings and digest and self._settings.get("virustotal_enabled") and \
                not any(f["engine"] == "signature" for f in findings):
            cloud = self._cloud_check(digest)
            if cloud:
                findings.append(cloud)

        if not findings:
            return False

        # keep the most severe finding as the primary detection
        findings.sort(key=lambda f: heuristics.SEVERITY_WEIGHT.get(f["severity"], 0), reverse=True)
        primary = findings[0]
        all_names = ", ".join(sorted({f["name"] for f in findings}))

        action = "detected"
        if self._settings.get("auto_quarantine", True):
            result = self._quarantine.quarantine_file(
                path, all_names, primary["engine"], primary["severity"], digest
            )
            action = "quarantined" if result.get("ok") else "failed"

        self._db.execute(
            "INSERT INTO detections(scan_id, path, name, engine, severity, action, sha256, created) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (scan_id, path, all_names, primary["engine"], primary["severity"],
             action, digest, utcnow()),
        )
        self._db.add_activity(
            "detection",
            f"{'Quarantined' if action == 'quarantined' else 'Detected'} {all_names} in {path}",
            "warning",
        )
        self._events.emit({
            "type": "threat", "path": path, "name": all_names,
            "engine": primary["engine"], "severity": primary["severity"], "action": action,
            "sha256": digest,
        })
        return True

    def _scan_archive(self, path: str) -> dict[str, Any] | None:
        try:
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist()[:2000]:
                    member = info.filename
                    if heuristics.DOUBLE_EXT_RE.search(member):
                        return {"name": "Heur:ArchiveDoubleExtension", "severity": "high",
                                "engine": "heuristic", "detail": f"Archive member '{member}'"}
                    try:
                        with archive.open(info) as handle:
                            chunk = handle.read(HEAD_BYTES)
                        if self._signatures.match_content(chunk):
                            return {"name": "EICAR-Test-File", "severity": "medium",
                                    "engine": "signature", "detail": f"Archive member '{member}'"}
                    except (OSError, RuntimeError):
                        continue
        except (zipfile.BadZipFile, OSError):
            return None
        return None

    def _cloud_check(self, digest: str) -> dict[str, Any] | None:
        budget = int(self._settings.get("virustotal_max_lookups", 10))
        if budget <= 0:
            return None
        api_key = self._settings.get("virustotal_api_key", "")
        result = self._vt.check_hash(digest, api_key)
        if result.get("ok") and result.get("positives", 0) > 0:
            return {"name": f"Cloud:VirusTotal ({result['positives']}/{result.get('total', 0)})",
                    "severity": "high", "engine": "cloud",
                    "detail": result.get("permalink", "")}
        return None

    def _load_exclusions(self) -> list[str]:
        rows = self._db.query("SELECT path FROM exclusions")
        return [os.path.normcase(r["path"].rstrip("\\/")) for r in rows]

    def _should_skip_dir(self, current: str, exclusions: list[str]) -> bool:
        lowered = current.lower()
        if os.path.basename(lowered) in SKIP_DIR_NAMES:
            return True
        if any(sub in lowered for sub in SKIP_DIR_SUBSTRINGS):
            return True
        data_dir = os.path.normcase(str(paths.data_dir()))
        if os.path.normcase(current).startswith(data_dir):
            return True
        for exc in exclusions:
            if os.path.normcase(current).startswith(exc):
                return True
        return False

    def _iter_files(self, targets: list[str], exclusions: list[str]):
        for target in targets:
            if os.path.isfile(target):
                if not self._is_excluded(target, exclusions):
                    yield target
                continue
            for root, dirs, files in os.walk(target, onerror=lambda _e: None):
                if self._stop.is_set():
                    return
                dirs[:] = [d for d in dirs if not self._should_skip_dir(os.path.join(root, d), exclusions)]
                for name in files:
                    full = os.path.join(root, name)
                    if not self._is_excluded(full, exclusions):
                        yield full

    def _is_excluded(self, path: str, exclusions: list[str]) -> bool:
        norm = os.path.normcase(path)
        return any(norm.startswith(exc) for exc in exclusions)

    def _count_files(self, targets: list[str]) -> int:
        exclusions = self._load_exclusions()
        count = 0
        for target in targets:
            if self._stop.is_set():
                break
            if os.path.isfile(target):
                count += 1
                continue
            for root, dirs, files in os.walk(target, onerror=lambda _e: None):
                if self._stop.is_set():
                    return count
                dirs[:] = [d for d in dirs if not self._should_skip_dir(os.path.join(root, d), exclusions)]
                count += len(files)
                with self._lock:
                    self._state["total_files"] = count
                if count % 2000 == 0:
                    self._emit_state()
        return count

    def _emit_state(self) -> None:
        self._events.emit({"type": "scan:progress", **self.snapshot()})

"""Ransomware Shield.

Two defensive layers that work without a kernel driver:

1. Backup: protected folders are snapshotted into a private vault so files can
   be recovered after an attack.
2. Behaviour alert: mass file modification / suspicious ransomware extensions
   trigger an immediate critical alert.
"""
from __future__ import annotations

import json
import os
import shutil
import threading
import time
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import paths
from .database import Database, utcnow
from .events import EventBus

MAX_FILES = 20000
MAX_BYTES = 5 * 1024 * 1024 * 1024
RANSOM_EXTENSIONS = {".locked", ".encrypted", ".crypt", ".crypto", ".enc", ".locky", ".zepto", ".cerber"}
RANSOM_NOTES = {"how_to_decrypt.txt", "readme_decrypt.txt", "decrypt_instructions.txt",
                "readme_for_decrypt.txt", "how_to_restore_files.txt"}
BURST_WINDOW = 10.0
BURST_THRESHOLD = 60


class _BurstHandler(FileSystemEventHandler):
    def __init__(self, on_event) -> None:
        self._on_event = on_event

    def _fire(self, path: str) -> None:
        self._on_event(path)

    def on_created(self, event):
        self._fire(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._fire(event.src_path)

    def on_moved(self, event):
        self._fire(event.dest_path)


class RansomwareShield:
    def __init__(self, db: Database, settings, events: EventBus) -> None:
        self._db = db
        self._settings = settings
        self._events = events
        self._observer: Observer | None = None
        self._lock = threading.RLock()
        self._events_times: list[float] = []
        self._alerted = False
        self._monitor: threading.Thread | None = None
        self._manifest_path = paths.shield_dir() / "manifest.json"

    # -- helpers -----------------------------------------------------------
    def protected_folders(self) -> list[str]:
        folders = self._settings.get("protected_folders", []) or []
        return [f for f in folders if Path(f).exists()]

    def save_protected_folders(self, folders: list[str]) -> list[str]:
        self._settings.set("protected_folders", folders)
        return folders

    @property
    def active(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> bool:
        folders = self.protected_folders()
        if not folders:
            return False
        with self._lock:
            if self.active:
                return True
            observer = Observer()
            handler = _BurstHandler(self._register_event)
            for folder in folders:
                try:
                    observer.schedule(handler, folder, recursive=True)
                except OSError:
                    continue
            observer.daemon = True
            observer.start()
            self._observer = observer
            self._alerted = False
            self._monitor = threading.Thread(target=self._monitor_loop, daemon=True, name="novu-shield")
            self._monitor.start()
        self._events.emit({"type": "protection", "module": "ransomware", "active": True})
        return True

    def stop(self) -> None:
        with self._lock:
            if self._observer:
                try:
                    self._observer.stop()
                    self._observer.join(timeout=3)
                except RuntimeError:
                    pass
                self._observer = None
        self._events.emit({"type": "protection", "module": "ransomware", "active": False})

    def _register_event(self, path: str) -> None:
        now = time.time()
        with self._lock:
            self._events_times.append(now)
            ext = Path(path).suffix.lower()
            name = os.path.basename(path).lower()
            if ext in RANSOM_EXTENSIONS or name in RANSOM_NOTES:
                self._alert(path, f"Suspicious ransomware artefact: {name}")

    def _monitor_loop(self) -> None:
        while self.active:
            time.sleep(2)
            cutoff = time.time() - BURST_WINDOW
            with self._lock:
                self._events_times = [t for t in self._events_times if t >= cutoff]
                if len(self._events_times) >= BURST_THRESHOLD and not self._alerted:
                    self._alert("", f"Mass file changes detected ({len(self._events_times)} in {int(BURST_WINDOW)}s)")

    def _alert(self, path: str, message: str) -> None:
        self._alerted = True
        self._db.add_activity("ransomware", message, "critical")
        self._events.emit({"type": "ransomware:alert", "path": path, "message": message})

    # -- backup ------------------------------------------------------------
    def create_backup(self) -> dict[str, Any]:
        folders = self.protected_folders()
        if not folders:
            return {"ok": False, "error": "no-protected-folders"}
        stamp = utcnow().replace(":", "").replace("-", "")
        root = paths.shield_dir() / f"snapshot_{stamp}"
        root.mkdir(parents=True, exist_ok=True)
        manifest: list[dict[str, Any]] = []
        files = 0
        total = 0
        for folder in folders:
            base = Path(folder)
            for current, _dirs, names in os.walk(folder, onerror=lambda _e: None):
                for name in names:
                    if files >= MAX_FILES or total >= MAX_BYTES:
                        break
                    src = Path(current) / name
                    try:
                        size = src.stat().st_size
                    except OSError:
                        continue
                    if total + size > MAX_BYTES:
                        continue
                    rel = src.relative_to(base)
                    dst = root / base.name / rel
                    try:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                    except (OSError, PermissionError):
                        continue
                    manifest.append({"rel": str(rel), "folder": str(base), "size": size})
                    files += 1
                    total += size
        self._manifest_path.write_text(
            json.dumps({"created": utcnow(), "root": str(root), "files": manifest}),
            encoding="utf-8",
        )
        self._db.add_activity("ransomware", f"Shield backup created ({files} files)", "info")
        return {"ok": True, "files": files, "bytes": total, "created": utcnow()}

    def backup_status(self) -> dict[str, Any]:
        if not self._manifest_path.exists():
            return {"exists": False}
        try:
            data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"exists": False}
        return {"exists": True, "created": data.get("created"),
                "files": len(data.get("files", []))}

    def restore(self) -> dict[str, Any]:
        if not self._manifest_path.exists():
            return {"ok": False, "error": "no-backup"}
        data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        root = Path(data["root"])
        restored = 0
        for item in data.get("files", []):
            src = root / Path(item["folder"]).name / item["rel"]
            dst = Path(item["folder"]) / item["rel"]
            if not src.exists():
                continue
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                restored += 1
            except OSError:
                continue
        self._db.add_activity("ransomware", f"Shield restore completed ({restored} files)", "info")
        return {"ok": True, "restored": restored}

    def status(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "protected_folders": self.protected_folders(),
            "backup": self.backup_status(),
            "alerted": self._alerted,
        }

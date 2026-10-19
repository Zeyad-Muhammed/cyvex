"""Real-time protection.

Watches the user's high-risk folders and scans files the moment they are
created or moved in. A short debounce lets partially-written downloads settle
before they are analysed. Backed by ``watchdog``.
"""
from __future__ import annotations

import os
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import paths
from .events import EventBus


def _watch_folders() -> list[str]:
    home = Path(os.path.expanduser("~"))
    candidates = [
        home / "Downloads",
        home / "Desktop",
        home / "Documents",
        Path(os.environ.get("TEMP", "")),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Temp",
        Path(os.environ.get("APPDATA", "")),
    ]
    return [str(p) for p in candidates if p and p.exists()]


class _Handler(FileSystemEventHandler):
    def __init__(self, callback) -> None:
        self._callback = callback

    def on_created(self, event):  # noqa: D401
        if not event.is_directory:
            self._callback(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._callback(event.dest_path)


class RealtimeProtection:
    def __init__(self, scan_engine, settings, events: EventBus) -> None:
        self._scanner = scan_engine
        self._settings = settings
        self._events = events
        self._observer: Observer | None = None
        self._lock = threading.RLock()
        self._recent: dict[str, float] = {}

    @property
    def active(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

    def start(self) -> bool:
        with self._lock:
            if self.active:
                return True
            folders = _watch_folders()
            if not folders:
                return False
            observer = Observer()
            handler = _Handler(self._on_change)
            for folder in folders:
                try:
                    observer.schedule(handler, folder, recursive=True)
                except OSError:
                    continue
            observer.daemon = True
            observer.start()
            self._observer = observer
        self._events.emit({"type": "protection", "module": "realtime", "active": True})
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
        self._events.emit({"type": "protection", "module": "realtime", "active": False})

    def _on_change(self, path: str) -> None:
        if not self._settings.get("realtime_enabled", True):
            return
        norm = os.path.normcase(path)
        data_dir = os.path.normcase(str(paths.data_dir()))
        if norm.startswith(data_dir):
            return
        now = time.time()
        last = self._recent.get(norm, 0)
        if now - last < 2:
            return
        self._recent[norm] = now
        threading.Thread(target=self._scan_after_delay, args=(path,), daemon=True).start()

    def _scan_after_delay(self, path: str) -> None:
        time.sleep(1.0)
        if not os.path.isfile(path):
            return
        try:
            found = self._scanner.scan_single(path)
        except Exception:  # noqa: BLE001
            return
        if found:
            self._events.emit({
                "type": "activity", "kind": "realtime",
                "message": f"Real-time protection handled a threat in {path}",
                "severity": "warning",
            })

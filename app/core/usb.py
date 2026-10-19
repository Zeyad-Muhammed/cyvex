"""USB / removable-media protection.

Polls for newly attached removable drives and triggers an automatic scan,
the way most desktop suites guard against USB-borne worms.
"""
from __future__ import annotations

import threading
import time

from . import winutil
from .events import EventBus

POLL_SECONDS = 3.0


class USBProtection:
    def __init__(self, scan_engine, settings, events: EventBus) -> None:
        self._scanner = scan_engine
        self._settings = settings
        self._events = events
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._known: set[str] = set()
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def start(self) -> bool:
        if self._active:
            return True
        self._known = set(winutil.removable_drives())
        self._stop.clear()
        self._active = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="novu-usb")
        self._thread.start()
        self._events.emit({"type": "protection", "module": "usb", "active": True})
        return True

    def stop(self) -> None:
        self._active = False
        self._stop.set()
        self._events.emit({"type": "protection", "module": "usb", "active": False})

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                current = set(winutil.removable_drives())
                new_drives = current - self._known
                for drive in new_drives:
                    self._on_attach(drive)
                self._known = current
            except Exception:  # noqa: BLE001
                pass
            self._stop.wait(POLL_SECONDS)

    def _on_attach(self, drive: str) -> None:
        self._events.emit({"type": "usb:attached", "drive": drive})
        self._events.emit({
            "type": "activity", "kind": "usb",
            "message": f"Removable media detected: {drive}", "severity": "info",
        })
        if self._settings.get("scan_removable", True) and not self._scanner.is_running():
            self._scanner.start("custom", [drive])

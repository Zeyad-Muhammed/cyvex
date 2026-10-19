"""Scheduled scans (daily / weekly)."""
from __future__ import annotations

import threading
from datetime import datetime

from .events import EventBus

TICK_SECONDS = 20.0


class Scheduler:
    def __init__(self, scan_engine, settings, events: EventBus) -> None:
        self._scanner = scan_engine
        self._settings = settings
        self._events = events
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._last_key: str | None = None
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def start(self) -> bool:
        if self._active:
            return True
        self._stop.clear()
        self._active = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="novu-scheduler")
        self._thread.start()
        return True

    def stop(self) -> None:
        self._active = False
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._tick()
            except Exception:  # noqa: BLE001
                pass
            self._stop.wait(TICK_SECONDS)

    def _tick(self) -> None:
        if not self._settings.get("scheduled_enabled", False):
            return
        now = datetime.now()
        time_str = str(self._settings.get("schedule_time", "12:00"))
        try:
            hour, minute = (int(x) for x in time_str.split(":"))
        except (ValueError, TypeError):
            return
        if now.hour != hour or now.minute != minute:
            return

        frequency = self._settings.get("schedule_frequency", "daily")
        if frequency == "weekly" and now.weekday() != int(self._settings.get("schedule_day", 0)):
            return

        key = f"{now.date()}-{hour}:{minute}"
        if key == self._last_key:
            return
        self._last_key = key

        if self._scanner.is_running():
            return
        scan_type = self._settings.get("schedule_scan_type", "quick")
        self._scanner.start(scan_type)
        self._events.emit({
            "type": "activity", "kind": "schedule",
            "message": f"Scheduled {scan_type} scan started", "severity": "info",
        })

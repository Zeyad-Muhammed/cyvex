"""Lightweight in-process event bus.

Core modules emit events (progress, detections, protection alerts) and the API
layer forwards them to the web UI via ``window.evaluate_js``. Emitting is
thread-safe and never raises to the caller.
"""
from __future__ import annotations

import threading
from typing import Any, Callable

Listener = Callable[[dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        with self._lock:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def emit(self, event: dict[str, Any]) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                listener(event)
            except Exception:  # noqa: BLE001 - listeners must never break the core
                pass

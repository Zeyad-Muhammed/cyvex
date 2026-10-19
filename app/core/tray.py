"""System tray integration via pystray (best effort, never fatal)."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Callable


class TrayController:
    def __init__(
        self,
        icon_path: Path,
        labels: Callable[[], dict[str, str]],
        on_open: Callable[[], None],
        on_toggle_protection: Callable[[], None],
        on_scan: Callable[[], None],
        on_quit: Callable[[], None],
        is_protection_on: Callable[[], bool],
    ) -> None:
        self._icon_path = icon_path
        self._labels = labels
        self._on_open = on_open
        self._on_toggle = on_toggle_protection
        self._on_scan = on_scan
        self._on_quit = on_quit
        self._is_on = is_protection_on
        self._icon: Any = None
        self._thread: threading.Thread | None = None
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def start(self) -> bool:
        try:
            import pystray
            from PIL import Image
        except Exception:  # noqa: BLE001
            return False

        try:
            image = Image.open(self._icon_path).convert("RGBA")
        except Exception:  # noqa: BLE001
            image = Image.new("RGBA", (64, 64), (37, 99, 235, 255))

        def toggle_label(item: Any) -> str:
            return self._labels()["toggle_off"] if self._is_on() else self._labels()["toggle_on"]

        menu = pystray.Menu(
            pystray.MenuItem(lambda i: self._labels()["open"], lambda i, it: self._on_open(), default=True),
            pystray.MenuItem(toggle_label, lambda i, it: self._on_toggle()),
            pystray.MenuItem(lambda i: self._labels()["scan"], lambda i, it: self._on_scan()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda i: self._labels()["quit"], lambda i, it: self._on_quit()),
        )
        try:
            self._icon = pystray.Icon("CYVEX", image, "CYVEX", menu)
        except Exception:  # noqa: BLE001
            return False

        self._thread = threading.Thread(target=self._run, name="novu-tray", daemon=True)
        self._thread.start()
        self._active = True
        return True

    def _run(self) -> None:
        try:
            self._icon.run()
        except Exception:  # noqa: BLE001
            self._active = False

    def notify(self, title: str, message: str) -> bool:
        if not self._icon:
            return False
        try:
            self._icon.notify(message, title)
            return True
        except Exception:  # noqa: BLE001
            return False

    def stop(self) -> None:
        self._active = False
        if self._icon:
            try:
                self._icon.stop()
            except Exception:  # noqa: BLE001
                pass

"""Application entry point: wires the API to a native webview window."""
from __future__ import annotations

import os
import sys
import threading
import time

import webview

from . import APP_NAME, APP_VERSION
from .api import Api
from .core import log, paths, winutil


def _parse_scan_argument(argv: list[str]) -> str | None:
    for i, arg in enumerate(argv):
        if arg in ("--scan", "-s") and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--scan="):
            return arg.split("=", 1)[1]
    return None


def _watch_pending_scans(api: Api, logger) -> None:  # type: ignore[no-untyped-def]
    while not api._quitting:  # noqa: SLF001
        try:
            pending = winutil.drain_pending_scans()
            if pending:
                logger.info("Running %d forwarded scan request(s)", len(pending))
                api.start_scan("custom", pending)
        except Exception:  # noqa: BLE001
            logger.exception("Pending scan poll failed")
        time.sleep(2)


def main() -> None:
    logger = log.setup()
    log.install_excepthook(logger)
    logger.info("Starting %s %s (frozen=%s)", APP_NAME, APP_VERSION, paths.is_frozen())

    scan_target = _parse_scan_argument(sys.argv[1:])

    if not os.environ.get("CYVEX_NO_SINGLE_INSTANCE"):
        if not winutil.acquire_single_instance():
            logger.info("Another instance is already running; forwarding.")
            if scan_target:
                winutil.enqueue_pending_scan(scan_target)
            if not winutil.focus_existing_window(f"{APP_NAME} {APP_VERSION}"):
                if not scan_target:
                    winutil.message_box(f"{APP_NAME} {APP_VERSION}",
                                        f"{APP_NAME} is already running.")
            return

    api = Api()
    api.initial_scan = scan_target
    index = paths.web_dir() / "index.html"
    frameless = bool(api.settings.get("frameless_window", False))

    window = webview.create_window(
        f"{APP_NAME} {APP_VERSION}",
        url=index.as_uri(),
        js_api=api,
        width=1240,
        height=820,
        min_size=(1024, 680),
        background_color="#0D1117",
        text_select=False,
        frameless=frameless,
        easy_drag=False,
    )
    api.attach_window(window)

    def on_loaded() -> None:
        try:
            api.start_tray()
        except Exception:  # noqa: BLE001
            logger.exception("Tray startup failed")
        try:
            api.bind_drop()
        except Exception:  # noqa: BLE001
            logger.exception("Drop binding failed")
        winutil.set_autostart(bool(api.settings.get("autostart", False)))
        winutil.set_context_menu(bool(api.settings.get("context_menu", False)))
        threading.Thread(target=_watch_pending_scans, args=(api, logger),
                         name="novu-pending", daemon=True).start()

    def on_closing() -> bool:
        if (not api._quitting and api.settings.get("close_to_tray", True)
                and api.tray_available()):  # noqa: SLF001
            try:
                window.hide()
            except Exception:  # noqa: BLE001
                pass
            return False
        try:
            api.shutdown()
        except Exception:  # noqa: BLE001
            logger.exception("Shutdown failed")
        return True

    window.events.loaded += on_loaded
    window.events.closing += on_closing
    webview.start(debug=bool(os.environ.get("CYVEX_DEBUG")))


if __name__ == "__main__":
    main()


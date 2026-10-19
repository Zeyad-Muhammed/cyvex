"""JavaScript <-> Python bridge.

Every public method here is callable from the UI as
``window.pywebview.api.<method>(...)``. Methods return JSON-serialisable
values. Engine events are pushed to the page via ``window.evaluate_js``.
"""
from __future__ import annotations

import csv
import io
import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from . import APP_NAME, APP_VERSION
from .core import log, paths, winutil
from .core.database import Database
from .core.events import EventBus
from .core.hashing import sha256_file
from .core.quarantine import QuarantineManager
from .core.ransomware import RansomwareShield
from .core.realtime import RealtimeProtection
from .core.scanner import ScanEngine
from .core.scheduler import Scheduler
from .core.settings import Settings
from .core.signatures import SignatureEngine
from .core.tray import TrayController
from .core.usb import USBProtection
from .core.virustotal import VirusTotalClient

_TRAY_LABELS = {
    "ar": {"open": "فتح CYVEX", "toggle_on": "تشغيل الحماية", "toggle_off": "إيقاف الحماية",
           "scan": "فحص سريع", "quit": "إنهاء"},
    "en": {"open": "Open CYVEX", "toggle_on": "Enable protection", "toggle_off": "Disable protection",
           "scan": "Quick scan", "quit": "Quit"},
}


class Api:
    def __init__(self) -> None:
        self._window = None
        self._tray: TrayController | None = None
        self._quitting = False
        self.initial_scan: str | None = None
        self._sig_thread: threading.Thread | None = None
        self._sig_stop = threading.Event()
        self.logger = log.get_logger("api")
        self.db = Database()
        self.settings = Settings(self.db)
        self.signatures = SignatureEngine(self.db)
        self.signatures.seed_defaults()
        self.quarantine = QuarantineManager(self.db)
        self.virustotal = VirusTotalClient(self.db)
        self.events = EventBus()
        self.scanner = ScanEngine(
            self.db, self.settings, self.signatures, self.quarantine, self.virustotal, self.events
        )
        self.realtime = RealtimeProtection(self.scanner, self.settings, self.events)
        self.shield = RansomwareShield(self.db, self.settings, self.events)
        self.usb = USBProtection(self.scanner, self.settings, self.events)
        self.scheduler = Scheduler(self.scanner, self.settings, self.events)
        self.events.subscribe(self._forward_event)
        self._apply_protection()
        # pywebview introspects public attributes to expose JS functions and
        # recursively walks any object it finds. Keep internal engines out of
        # that walk (see webview.util.get_functions) to avoid descending into
        # the native window/DB/watchdog graphs.
        for service in (
            self.db, self.settings, self.signatures, self.quarantine,
            self.virustotal, self.events, self.scanner, self.realtime,
            self.shield, self.usb, self.scheduler, self.logger,
        ):
            try:
                service._serializable = False
            except Exception:  # noqa: BLE001
                pass

    def attach_window(self, window: Any) -> None:
        """Bind the native window used for dialogs and event delivery."""
        self._window = window

    # -- desktop integration ----------------------------------------------
    def _tray_labels(self) -> dict[str, str]:
        lang = str(self.settings.get("language", "ar"))
        return _TRAY_LABELS.get(lang, _TRAY_LABELS["en"])

    def start_tray(self) -> bool:
        if not self.settings.get("tray_enabled", True):
            return False
        if self._tray and self._tray.active:
            return True
        self._tray = TrayController(
            icon_path=paths.web_dir() / "icon-256.png",
            labels=self._tray_labels,
            on_open=self.open_main_window,
            on_toggle_protection=self.toggle_protection,
            on_scan=lambda: self.start_scan("quick"),
            on_quit=self.quit_app,
            is_protection_on=lambda: bool(self.settings.get("realtime_enabled", True)),
        )
        ok = self._tray.start()
        if not ok:
            self._tray = None
        return ok

    def _stop_tray(self) -> None:
        if self._tray:
            self._tray.stop()
            self._tray = None

    def tray_available(self) -> bool:
        return bool(self._tray and self._tray.active)

    def open_main_window(self) -> dict[str, Any]:
        if self._window is None:
            return {"ok": False}
        try:
            self._window.show()
            self._window.restore()
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    def hide_main_window(self) -> dict[str, Any]:
        if self._window is None:
            return {"ok": False}
        try:
            self._window.hide()
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    def toggle_protection(self) -> dict[str, Any]:
        new_value = not bool(self.settings.get("realtime_enabled", True))
        self.settings.set("realtime_enabled", new_value)
        if new_value:
            self.realtime.start()
        else:
            self.realtime.stop()
        self._refresh_tray()
        return {"ok": True, "realtime_enabled": new_value}

    def quit_app(self) -> dict[str, Any]:
        self._quitting = True
        self._stop_tray()
        if self._window is not None:
            try:
                self._window.destroy()
            except Exception:  # noqa: BLE001
                pass
        return {"ok": True}

    def _refresh_tray(self) -> None:
        if self._tray and self._tray.active:
            try:
                self._tray._icon.update_menu()  # noqa: SLF001 - pystray has no public refresh
            except Exception:  # noqa: BLE001
                pass

    def get_desktop_integration(self) -> dict[str, Any]:
        return {
            "tray": self.tray_available(),
            "autostart": winutil.autostart_enabled(),
            "context_menu": winutil.context_menu_enabled(),
        }

    def set_autostart(self, enabled: bool) -> dict[str, Any]:
        self.settings.set("autostart", bool(enabled))
        ok = winutil.set_autostart(bool(enabled))
        return {"ok": ok, "autostart": winutil.autostart_enabled()}

    def set_context_menu(self, enabled: bool) -> dict[str, Any]:
        self.settings.set("context_menu", bool(enabled))
        ok = winutil.set_context_menu(bool(enabled))
        return {"ok": ok, "context_menu": winutil.context_menu_enabled()}

    def open_logs_folder(self) -> dict[str, Any]:
        try:
            os.startfile(str(paths.logs_dir()))  # type: ignore[attr-defined]  # noqa: S606
            return {"ok": True}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}

    def get_initial_scan(self) -> dict[str, Any]:
        target = self.initial_scan
        self.initial_scan = None
        return {"target": target}

    # -- event bridge ------------------------------------------------------
    def _forward_event(self, event: dict[str, Any]) -> None:
        payload = json.dumps(event, ensure_ascii=False)
        try:
            if self._window is not None:
                self._window.evaluate_js(f"window.NOVU && window.NOVU.receive({payload})")
        except Exception:  # noqa: BLE001 - window may be closing
            pass
        self._maybe_notify(event)

    def _maybe_notify(self, event: dict[str, Any]) -> None:
        if not self.settings.get("notify", True):
            return
        try:
            kind = event.get("type")
            if kind == "threat":
                title = event.get("name", "Threat detected")
                message = os.path.basename(str(event.get("path", "")))
            elif kind == "scan:finished":
                threats = event.get("threats_found", 0)
                title = "CYVEX"
                message = "Scan completed" if not threats else f"{threats} threats found"
            elif kind == "ransomware:alert":
                title = "Ransomware alert"
                message = str(event.get("message", ""))
            else:
                return
            shown = self._tray.notify(title, message) if self._tray else False
            if not shown:
                winutil.toast(title, message)
        except Exception:  # noqa: BLE001 - notifications are best effort
            pass

    def _apply_protection(self) -> None:
        if self.settings.get("realtime_enabled", True):
            self.realtime.start()
        if self.settings.get("ransomware_enabled", False):
            self.shield.start()
        if self.settings.get("usb_enabled", True):
            self.usb.start()
        self.scheduler.start()
        self._start_signature_updates()

    def _start_signature_updates(self) -> None:
        if self._sig_thread and self._sig_thread.is_alive():
            return
        self._sig_stop.clear()
        self._sig_thread = threading.Thread(
            target=self._signature_update_loop, name="novu-sigupdate", daemon=True
        )
        self._sig_thread.start()

    def _signature_update_loop(self) -> None:
        while not self._sig_stop.wait(6 * 3600):
            if not self.settings.get("signature_auto_update", False):
                continue
            url = str(self.settings.get("signature_update_url", "")).strip()
            if not url:
                continue
            try:
                result = self.signatures.update_from_url(url)
                self.logger.info("Signature auto-update: %s", result)
                if result.get("ok") and result.get("added"):
                    self.events.emit({"type": "activity", "kind": "signatures",
                                      "message": f"Signatures updated (+{result['added']})",
                                      "severity": "success"})
            except Exception:  # noqa: BLE001
                self.logger.exception("Signature auto-update failed")

    # -- bootstrap & dashboard --------------------------------------------
    def bootstrap(self) -> dict[str, Any]:
        return {
            "app": {"name": APP_NAME, "version": APP_VERSION},
            "settings": self.settings.all(include_secrets=False),
            "dashboard": self.get_dashboard(),
            "desktop": self.get_desktop_integration(),
            "initial_scan": self.get_initial_scan(),
        }

    def get_dashboard(self) -> dict[str, Any]:
        last_scan = self.db.query_one("SELECT * FROM scan_history ORDER BY id DESC LIMIT 1")
        last_scan_data = dict(last_scan) if last_scan else None
        totals = self.db.query_one(
            "SELECT COUNT(*) AS scans, COALESCE(SUM(threats_found),0) AS threats FROM scan_history"
        )
        threats_24h = self.db.query_one(
            "SELECT COUNT(*) AS c FROM detections WHERE created >= datetime('now','-1 day')"
        )
        risk = "safe"
        if last_scan_data and last_scan_data["threats_found"]:
            risk = "warning"
        if not self.settings.get("realtime_enabled", True):
            risk = "warning"
        quarantined = self.quarantine.count()
        if quarantined:
            risk = "warning"
        return {
            "risk": risk,
            "last_scan": last_scan_data,
            "totals": {"scans": totals["scans"] if totals else 0,
                       "threats": totals["threats"] if totals else 0,
                       "threats_24h": threats_24h["c"] if threats_24h else 0},
            "quarantine": {"count": quarantined, "size": self.quarantine.total_size()},
            "signatures": {"count": self.signatures.count(),
                           "updated": self.signatures.last_updated()},
            "protection": self.get_protection_status(),
            "scan": self.scanner.snapshot(),
            "activity": self.db.recent_activity(15),
            "system": self.get_system_info(),
        }

    def get_system_info(self) -> dict[str, Any]:
        drives = []
        for drive in winutil.list_drives():
            if drive["type"] in ("fixed", "removable"):
                usage = winutil.drive_usage(drive["root"])
                drives.append({**drive, **usage})
        data_dir = paths.data_dir()
        return {
            "drives": drives,
            "data_dir": str(data_dir),
            "platform": os.name,
            "quick_targets": winutil.quick_scan_targets(),
        }

    def get_protection_status(self) -> dict[str, Any]:
        return {
            "realtime": self.realtime.active,
            "ransomware": self.shield.active,
            "usb": self.usb.active,
            "scheduler": self.scheduler.active,
            "web": self.settings.get("web_protection_enabled", False),
        }

    # -- scanning ----------------------------------------------------------
    def start_scan(self, scan_type: str, targets: list[str] | None = None) -> dict[str, Any]:
        return self.scanner.start(scan_type, targets)

    def scan_control(self, action: str) -> dict[str, Any]:
        if action == "pause":
            return self.scanner.pause()
        if action == "resume":
            return self.scanner.resume()
        if action == "stop":
            return self.scanner.stop()
        return {"ok": False, "error": "unknown-action"}

    def get_scan_status(self) -> dict[str, Any]:
        return self.scanner.snapshot()

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.db.query(
            "SELECT * FROM scan_history ORDER BY id DESC LIMIT ?", (int(limit),)
        )
        return [dict(r) for r in rows]

    def get_detections(self, scan_id: int | None = None, limit: int = 200) -> list[dict[str, Any]]:
        if scan_id:
            rows = self.db.query(
                "SELECT * FROM detections WHERE scan_id = ? ORDER BY id DESC LIMIT ?",
                (int(scan_id), int(limit)),
            )
        else:
            rows = self.db.query(
                "SELECT * FROM detections ORDER BY id DESC LIMIT ?", (int(limit),)
            )
        return [dict(r) for r in rows]

    def get_activity(self, limit: int = 40) -> list[dict[str, Any]]:
        return self.db.recent_activity(int(limit))

    # -- statistics & charts ----------------------------------------------
    def get_stats(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        days = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

        det_rows = self.db.query(
            "SELECT substr(created,1,10) AS d, COUNT(*) AS c FROM detections GROUP BY d"
        )
        scan_rows = self.db.query(
            "SELECT substr(started,1,10) AS d, COUNT(*) AS c FROM scan_history GROUP BY d"
        )
        det_by_day = {r["d"]: r["c"] for r in det_rows}
        scan_by_day = {r["d"]: r["c"] for r in scan_rows}
        timeline = [
            {"day": d, "detections": int(det_by_day.get(d, 0)), "scans": int(scan_by_day.get(d, 0))}
            for d in days
        ]

        severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for r in self.db.query("SELECT severity, COUNT(*) AS c FROM detections GROUP BY severity"):
            if r["severity"] in severity:
                severity[r["severity"]] = int(r["c"])

        engines: dict[str, int] = {}
        for r in self.db.query("SELECT engine, COUNT(*) AS c FROM detections GROUP BY engine"):
            engines[r["engine"] or "unknown"] = int(r["c"])

        totals = self.db.query_one(
            "SELECT COUNT(*) AS scans, COALESCE(SUM(threats_found),0) AS threats FROM scan_history"
        )
        threats_24h = self.db.query_one(
            "SELECT COUNT(*) AS c FROM detections WHERE created >= datetime('now','-1 day')"
        )
        return {
            "timeline": timeline,
            "severity": severity,
            "engines": engines,
            "totals": {
                "scans": int(totals["scans"]) if totals else 0,
                "threats": int(totals["threats"]) if totals else 0,
                "threats_24h": int(threats_24h["c"]) if threats_24h else 0,
                "quarantine": self.quarantine.count(),
            },
        }

    # -- notifications -----------------------------------------------------
    def get_notifications(self, limit: int = 30) -> list[dict[str, Any]]:
        return self.db.recent_activity(int(limit))

    def notify_os(self, title: str, message: str) -> dict[str, Any]:
        return {"ok": winutil.toast(title, message)}

    # -- native window controls (frameless mode) --------------------------
    def window_action(self, action: str) -> dict[str, Any]:
        window = self._window
        if window is None:
            return {"ok": False, "error": "no-window"}
        try:
            if action == "minimize":
                window.minimize()
            elif action == "maximize":
                if getattr(self, "_maximized", False):
                    window.restore()
                    self._maximized = False
                else:
                    window.maximize()
                    self._maximized = True
            elif action == "restore":
                window.restore()
                self._maximized = False
            elif action == "fullscreen":
                window.toggle_fullscreen()
            elif action == "close":
                if (self._tray and self._tray.active
                        and self.settings.get("close_to_tray", True)):
                    window.hide()
                else:
                    self._quitting = True
                    window.destroy()
            else:
                return {"ok": False, "error": "unknown-action"}
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    def window_move(self, x: int, y: int) -> dict[str, Any]:
        if self._window is None:
            return {"ok": False}
        try:
            self._window.move(int(x), int(y))
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    # -- report export -----------------------------------------------------
    def _report_rows(self, scan_id: int | None) -> list[dict[str, Any]]:
        if scan_id:
            rows = self.db.query(
                "SELECT * FROM detections WHERE scan_id = ? ORDER BY id DESC", (int(scan_id),)
            )
        else:
            rows = self.db.query("SELECT * FROM detections ORDER BY id DESC")
        return [dict(r) for r in rows]

    def export_report(self, scan_id: int | None = None, fmt: str = "csv") -> dict[str, Any]:
        import webview

        rows = self._report_rows(scan_id)
        scan = None
        if scan_id:
            scan = self.db.query_one("SELECT * FROM scan_history WHERE id = ?", (int(scan_id),))
            scan = dict(scan) if scan else None
        fmt = (fmt or "csv").lower()
        if fmt not in ("csv", "html", "pdf"):
            fmt = "csv"
        file_types = {
            "csv": ("CSV (*.csv)",),
            "html": ("HTML (*.html)",),
            "pdf": ("PDF (*.pdf)",),
        }[fmt]
        name = f"novu-report-{scan_id or 'all'}.{fmt}"
        try:
            chosen = self._window.create_file_dialog(
                webview.SAVE_DIALOG, save_filename=name, file_types=file_types,
            )
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
        if not chosen:
            return {"ok": False, "error": "cancelled"}
        path = chosen[0] if isinstance(chosen, (list, tuple)) else str(chosen)
        try:
            if fmt == "csv":
                Path(path).write_text(self._report_csv(rows), encoding="utf-8-sig")
            elif fmt == "html":
                Path(path).write_text(self._report_html(rows, scan), encoding="utf-8")
            else:
                result = winutil.html_to_pdf(self._report_html(rows, scan, print_mode=True), path)
                if not result.get("ok"):
                    return {"ok": False, "error": result.get("error", "pdf-failed")}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "path": path, "rows": len(rows)}

    @staticmethod
    def _report_csv(rows: list[dict[str, Any]]) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Date", "Name", "Path", "Engine", "Severity", "Action", "SHA256"])
        for r in rows:
            writer.writerow([
                r.get("created", ""), r.get("name", ""), r.get("path", ""),
                r.get("engine", ""), r.get("severity", ""), r.get("action", ""),
                r.get("sha256") or "",
            ])
        return buf.getvalue()

    @staticmethod
    def _report_html(rows: list[dict[str, Any]], scan: dict[str, Any] | None,
                     print_mode: bool = False) -> str:
        def esc(value: Any) -> str:
            return (str(value if value is not None else "")
                    .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

        head = "<h1>CYVEX — Scan Report</h1>"
        if scan:
            head += (f"<p>Scan #{scan.get('id')} · type {esc(scan.get('scan_type'))} · "
                     f"status {esc(scan.get('status'))} · {esc(scan.get('files_scanned'))} files · "
                     f"{esc(scan.get('threats_found'))} threats · {esc(scan.get('started'))}</p>")
        body = "".join(
            f"<tr><td>{esc(r.get('created'))}</td><td>{esc(r.get('name'))}</td>"
            f"<td class='p'>{esc(r.get('path'))}</td><td>{esc(r.get('engine'))}</td>"
            f"<td>{esc(r.get('severity'))}</td><td>{esc(r.get('sha256') or '')}</td></tr>"
            for r in rows
        ) or "<tr><td colspan='6'>No detections</td></tr>"
        if print_mode:
            style = ("body{font-family:Segoe UI,Arial,sans-serif;background:#fff;color:#111;padding:32px}"
                     "h1{color:#1d4ed8}table{width:100%;border-collapse:collapse;font-size:12px}"
                     "th,td{border-bottom:1px solid #d6dce8;padding:8px;text-align:left}"
                     "th{color:#44506b;text-transform:uppercase;font-size:10px}"
                     "td.p{font-family:Consolas,monospace;font-size:10px;word-break:break-all}")
        else:
            style = ("body{font-family:Segoe UI,Arial,sans-serif;background:#0b1220;color:#e9effb;padding:32px}"
                     "h1{color:#60a5fa}table{width:100%;border-collapse:collapse;font-size:13px}"
                     "th,td{border-bottom:1px solid #1a2740;padding:8px;text-align:left}"
                     "th{color:#93a3c2;text-transform:uppercase;font-size:11px}td.p{font-family:Consolas,monospace}")
        return f"""<!doctype html><html><head><meta charset="utf-8"><title>CYVEX Report</title>
<style>{style}</style>
</head><body>{head}<table><thead><tr><th>Date</th><th>Name</th><th>Path</th>
<th>Engine</th><th>Severity</th><th>SHA256</th></tr></thead><tbody>{body}</tbody></table></body></html>"""

    # -- quarantine --------------------------------------------------------
    def get_quarantine(self) -> list[dict[str, Any]]:
        return self.quarantine.list_entries()

    def quarantine_action(self, entry_id: int, action: str) -> dict[str, Any]:
        if action == "restore":
            return self.quarantine.restore(int(entry_id))
        if action == "delete":
            return self.quarantine.delete(int(entry_id))
        return {"ok": False, "error": "unknown-action"}

    def empty_quarantine(self) -> dict[str, Any]:
        return self.quarantine.delete_all()

    # -- settings ----------------------------------------------------------
    def get_settings(self) -> dict[str, Any]:
        return self.settings.all(include_secrets=False)

    def save_settings(self, values: dict[str, Any]) -> dict[str, Any]:
        safe = dict(values)
        if safe.get("virustotal_api_key") in (None, "", "••••••••"):
            safe.pop("virustotal_api_key", None)
        previous = self.settings.all()
        self.settings.update(safe)
        current = self.settings.all()
        self._react_to_setting_changes(previous, current)
        return current

    def _react_to_setting_changes(self, previous: dict[str, Any], current: dict[str, Any]) -> None:
        if previous.get("realtime_enabled") != current.get("realtime_enabled"):
            if current.get("realtime_enabled"):
                self.realtime.start()
            else:
                self.realtime.stop()
            self._refresh_tray()
        if previous.get("usb_enabled") != current.get("usb_enabled"):
            if current.get("usb_enabled"):
                self.usb.start()
            else:
                self.usb.stop()
        if previous.get("ransomware_enabled") != current.get("ransomware_enabled"):
            if current.get("ransomware_enabled"):
                self.shield.start()
            else:
                self.shield.stop()
        if previous.get("tray_enabled") != current.get("tray_enabled"):
            if current.get("tray_enabled"):
                self.start_tray()
            else:
                self._stop_tray()
        if previous.get("autostart") != current.get("autostart"):
            winutil.set_autostart(bool(current.get("autostart")))
        if previous.get("context_menu") != current.get("context_menu"):
            winutil.set_context_menu(bool(current.get("context_menu")))
        if current.get("language") != previous.get("language"):
            self._refresh_tray()

    # -- exclusions --------------------------------------------------------
    def get_exclusions(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.query("SELECT * FROM exclusions ORDER BY id DESC")]

    def add_exclusion(self, path: str) -> dict[str, Any]:
        if not path:
            return {"ok": False, "error": "empty"}
        from .core.database import utcnow

        self.db.execute(
            "INSERT OR IGNORE INTO exclusions(path, created) VALUES(?,?)", (path, utcnow())
        )
        return {"ok": True}

    def remove_exclusion(self, entry_id: int) -> dict[str, Any]:
        self.db.execute("DELETE FROM exclusions WHERE id = ?", (int(entry_id),))
        return {"ok": True}

    # -- dialogs -----------------------------------------------------------
    def pick_folder(self) -> str | None:
        import webview

        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return None
        return result[0] if isinstance(result, (list, tuple)) else str(result)

    def pick_file(self) -> str | None:
        import webview

        result = self._window.create_file_dialog(webview.OPEN_DIALOG)
        if not result:
            return None
        return result[0] if isinstance(result, (list, tuple)) else str(result)

    # -- virus total -------------------------------------------------------
    def vt_check(self, target: str) -> dict[str, Any]:
        if not self.settings.get("virustotal_enabled", False):
            return {"ok": False, "error": "disabled"}
        api_key = self.settings.get("virustotal_api_key", "")
        if not self.virustotal.is_configured(api_key):
            return {"ok": False, "error": "not-configured"}
        digest = target if len(target) == 64 else sha256_file(target)
        if not digest:
            return {"ok": False, "error": "unreadable"}
        result = self.virustotal.check_hash(digest, api_key)
        result["sha256"] = digest
        return result

    # -- signatures --------------------------------------------------------
    def get_signatures_info(self) -> dict[str, Any]:
        return {"count": self.signatures.count(), "updated": self.signatures.last_updated()}

    def update_signatures(self, url: str | None = None) -> dict[str, Any]:
        if url:
            result = self.signatures.update_from_url(url)
        else:
            # No public endpoint configured: re-seed bundled signatures.
            added = self.signatures.seed_defaults()
            from .core.database import utcnow

            self.db.set_setting("signatures_updated", utcnow())
            result = {"ok": True, "added": added, "note": "bundled"}
        self.events.emit({"type": "activity", "kind": "signatures",
                          "message": "Signature database updated", "severity": "success"})
        return result

    def import_signatures_file(self) -> dict[str, Any]:
        path = self.pick_file()
        if not path:
            return {"ok": False, "error": "cancelled"}
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}
        entries = payload.get("signatures", payload if isinstance(payload, list) else [])
        added = self.signatures.add_many(entries)
        return {"ok": True, "added": added}

    # -- ransomware shield -------------------------------------------------
    def get_shield_status(self) -> dict[str, Any]:
        return self.shield.status()

    def get_protected_folders(self) -> list[str]:
        return self.shield.protected_folders()

    def add_protected_folder(self, path: str) -> dict[str, Any]:
        folders = self.shield.protected_folders()
        if path and path not in folders:
            folders.append(path)
            self.shield.save_protected_folders(folders)
            if self.settings.get("ransomware_enabled", False):
                self.shield.stop()
                self.shield.start()
        return {"ok": True, "folders": folders}

    def remove_protected_folder(self, path: str) -> dict[str, Any]:
        folders = [f for f in self.shield.protected_folders() if f != path]
        self.shield.save_protected_folders(folders)
        if self.settings.get("ransomware_enabled", False):
            self.shield.stop()
            self.shield.start()
        return {"ok": True, "folders": folders}

    def shield_backup(self) -> dict[str, Any]:
        return self.shield.create_backup()

    def shield_restore(self) -> dict[str, Any]:
        return self.shield.restore()

    # -- misc --------------------------------------------------------------
    def open_path(self, path: str) -> dict[str, Any]:
        try:
            os.startfile(path)  # type: ignore[attr-defined]  # noqa: S606
            return {"ok": True}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}

    def complete_first_run(self) -> dict[str, Any]:
        self.settings.set("first_run", False)
        return {"ok": True}

    def on_files_dropped(self, paths: list[str]) -> dict[str, Any]:
        cleaned = [p for p in (paths or []) if p]
        if not cleaned:
            return {"ok": False, "error": "empty"}
        return self.scanner.start("custom", cleaned)

    def bind_drop(self) -> dict[str, Any]:
        """Attach a native DOM drop handler via pywebview (full file paths)."""
        if self._window is None:
            return {"ok": False, "error": "no-window"}
        try:
            from webview.dom import DOMEventHandler

            el = self._window.dom.get_element("#app") or self._window.dom.get_element("body")
            if el is None:
                return {"ok": False, "error": "no-element"}

            def handler(event: dict[str, Any]) -> None:
                try:
                    transfer = event.get("dataTransfer") or {}
                    files = transfer.get("files") or []
                    paths = [f.get("pywebviewFullPath") for f in files
                             if isinstance(f, dict) and f.get("pywebviewFullPath")]
                    self.on_files_dropped(paths)
                except Exception:  # noqa: BLE001
                    self.logger.exception("drop handler failed")

            el.on("drop", DOMEventHandler(handler, prevent_default=True, stop_propagation=True))
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("Drop binding unavailable: %s", exc)
            return {"ok": False, "error": str(exc)}

    def shutdown(self) -> dict[str, Any]:
        self._sig_stop.set()
        self._stop_tray()
        self.realtime.stop()
        self.shield.stop()
        self.usb.stop()
        self.scheduler.stop()
        self.db.close()
        return {"ok": True}

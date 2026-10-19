"""Typed application settings backed by the ``settings`` table."""
from __future__ import annotations

from typing import Any

from . import paths
from .database import Database

DEFAULTS: dict[str, Any] = {
    "theme": "dark",                      # dark | light
    "language": "ar",                     # ar | en
    "first_run": True,
    # appearance
    "accent": "navy",                     # navy | royal | azure | ice
    "reduce_motion": False,
    "high_contrast": False,
    "sidebar_collapsed": False,
    "frameless_window": True,
    # protection modules
    "realtime_enabled": True,
    "ransomware_enabled": False,
    "usb_enabled": True,
    "web_protection_enabled": False,
    # scanning
    "scan_archives": True,
    "scan_max_size_mb": 64,               # files bigger than this skip hashing
    "auto_quarantine": True,
    "scan_removable": True,
    "notify": True,
    # scheduled scans
    "scheduled_enabled": False,
    "schedule_frequency": "daily",        # daily | weekly
    "schedule_time": "12:00",
    "schedule_day": 0,                    # 0=Monday .. 6=Sunday
    # virus total
    "virustotal_enabled": False,
    "virustotal_api_key": "",
    "virustotal_max_lookups": 10,
    # ransomware shield
    "protected_folders": [],
    # desktop integration
    "single_instance": True,
    "tray_enabled": True,
    "close_to_tray": True,
    "autostart": False,
    "context_menu": False,
    # signature updates
    "signature_auto_update": False,
    "signature_update_url": "",
}

_SECRET_KEYS = {"virustotal_api_key"}


def _default_protected_folders() -> list[str]:
    candidates = [
        paths.home() / "Documents",
        paths.home() / "Desktop",
        paths.home() / "Pictures",
    ]
    return [str(p) for p in candidates if p.exists()]


class Settings:
    def __init__(self, db: Database) -> None:
        self._db = db
        if db.get_setting("first_run", None) is None:
            protected = _default_protected_folders()
            self._db.set_setting("protected_folders", protected)

    def get(self, key: str, default: Any = None) -> Any:
        if key in DEFAULTS:
            return self._db.get_setting(key, DEFAULTS[key])
        return self._db.get_setting(key, default)

    def set(self, key: str, value: Any) -> None:
        self._db.set_setting(key, value)

    def all(self, include_secrets: bool = True) -> dict[str, Any]:
        data = dict(DEFAULTS)
        for key in DEFAULTS:
            data[key] = self.get(key)
        if not include_secrets:
            for key in _SECRET_KEYS:
                if data.get(key):
                    data[key] = "••••••••"
        return data

    def update(self, values: dict[str, Any]) -> dict[str, Any]:
        for key, value in values.items():
            if key in DEFAULTS:
                self.set(key, value)
        return self.all()

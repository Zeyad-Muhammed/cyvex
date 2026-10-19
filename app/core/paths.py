"""Filesystem path helpers.

Resolves the application root, both when running from source and when frozen
by PyInstaller. All persistent data is stored next to the executable / project
root so the whole thing stays portable inside a single folder.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def resource_root() -> Path:
    """Directory that holds bundled, read-only resources (web assets, seeds)."""
    if is_frozen():
        # PyInstaller one-folder build extracts to sys._MEIPASS at runtime.
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


def app_root() -> Path:
    """Directory that holds writable runtime data next to the app."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    path = app_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def quarantine_dir() -> Path:
    path = data_dir() / "quarantine"
    path.mkdir(parents=True, exist_ok=True)
    return path


def shield_dir() -> Path:
    """Backups created by the Ransomware Shield."""
    path = data_dir() / "shield"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "novu.db"


def web_dir() -> Path:
    return resource_root() / "app" / "web"


def seeds_dir() -> Path:
    return resource_root() / "app" / "core" / "seeds"


def home() -> Path:
    return Path(os.path.expanduser("~"))

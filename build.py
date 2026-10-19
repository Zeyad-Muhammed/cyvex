"""Build a portable one-folder distribution with PyInstaller.

Usage:
    .venv\\Scripts\\python.exe build.py

Output: dist\\CYVEX\\CYVEX.exe (+ all dependencies and the
``app\\web`` assets). Runtime data is created in a ``data`` folder next to the
executable, so the whole directory can be copied anywhere.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "CYVEX"


def main() -> int:
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", NAME,
        "--icon", str(ROOT / "icon.ico"),
        "--add-data", f"{ROOT / 'icon.ico'}{';' if sys.platform == 'win32' else ':'}.", 
        "--add-data", f"{ROOT / 'app' / 'web'}{';' if sys.platform == 'win32' else ':'}app/web",
        "--add-data", f"{ROOT / 'app' / 'core' / 'seeds'}{';' if sys.platform == 'win32' else ':'}app/core/seeds",
        "--collect-all", "webview",
        "--collect-all", "clr_loader",
        "--collect-all", "pystray",
        "--hidden-import", "pythonnet",
        "--hidden-import", "pystray._win32",
        "--hidden-import", "watchdog.observers.winapi",
        str(ROOT / "run.py"),
    ]
    print("Running:", " ".join(args))
    result = subprocess.run(args, cwd=str(ROOT))
    if result.returncode == 0:
        print(f"\nBuild complete -> {ROOT / 'dist' / NAME}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

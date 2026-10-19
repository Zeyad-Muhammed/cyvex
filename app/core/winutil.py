"""Small Windows helpers (drive enumeration, startup folders).

Every function degrades gracefully on non-Windows platforms so the core stays
testable in isolation.
"""
from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

DRIVE_REMOVABLE = 2
DRIVE_FIXED = 3
DRIVE_REMOTE = 4
DRIVE_CDROM = 5
DRIVE_RAMDISK = 6

_DRIVE_LABELS = {
    DRIVE_REMOVABLE: "removable",
    DRIVE_FIXED: "fixed",
    DRIVE_REMOTE: "network",
    DRIVE_CDROM: "cdrom",
    DRIVE_RAMDISK: "ramdisk",
}


def _drive_type(root: str) -> int:
    try:
        return ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(root))
    except (AttributeError, OSError):
        return 0


def list_drives(kind: int | None = None) -> list[dict[str, str]]:
    """Return drive roots. ``kind`` filters by DRIVE_* constant."""
    drives: list[dict[str, str]] = []
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    except (AttributeError, OSError):
        return drives
    for i in range(26):
        if not (bitmask >> i) & 1:
            continue
        root = f"{chr(65 + i)}:\\"
        dtype = _drive_type(root)
        if kind is not None and dtype != kind:
            continue
        drives.append({"root": root, "type": _DRIVE_LABELS.get(dtype, "unknown")})
    return drives


def fixed_drives() -> list[str]:
    return [d["root"] for d in list_drives(DRIVE_FIXED)]


def removable_drives() -> list[str]:
    return [d["root"] for d in list_drives(DRIVE_REMOVABLE)]


def startup_folders() -> list[str]:
    candidates = [
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
    ]
    return [c for c in candidates if c and Path(c).exists()]


def quick_scan_targets() -> list[str]:
    home = Path(os.path.expanduser("~"))
    candidates = [
        os.environ.get("TEMP", ""),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
        str(home / "Downloads"),
        str(home / "Desktop"),
        str(home / "Documents"),
        *startup_folders(),
    ]
    seen: list[str] = []
    for cand in candidates:
        if cand and Path(cand).exists() and cand not in seen:
            seen.append(cand)
    return seen


def drive_usage(root: str) -> dict[str, int]:
    """Return total/free bytes for a drive root (0/0 on failure)."""
    try:
        import shutil

        usage = shutil.disk_usage(root)
        return {"total": usage.total, "used": usage.used, "free": usage.free}
    except OSError:
        return {"total": 0, "used": 0, "free": 0}


_APP_ID = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe"

_TOAST_PS = (
    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
    "ContentType = WindowsRuntime] | Out-Null;"
    "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType=WindowsRuntime] "
    "| Out-Null;"
    "$t = '<toast><visual><binding template=\"ToastGeneric\"><text>' + $env:CYVEX_TOAST_TITLE + "
    "'</text><text>' + $env:CYVEX_TOAST_MSG + '</text></binding></visual></toast>';"
    "$x = New-Object Windows.Data.Xml.Dom.XmlDocument;"
    "$x.LoadXml($t);"
    "$toast = New-Object Windows.UI.Notifications.ToastNotification $x;"
    "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('"
    + _APP_ID
    + "').Show($toast);"
)


_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_AUTOSTART_NAME = "CYVEX"
_CTX_SHELLS = (
    r"Software\Classes\*\shell\CYVEX",
    r"Software\Classes\Directory\shell\CYVEX",
    r"Software\Classes\Drive\shell\CYVEX",
)


def launch_command() -> str:
    """Command line that starts the app (frozen exe, or pythonw + run.py)."""
    from . import paths

    if paths.is_frozen():
        return f'"{sys.executable}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else Path(sys.executable)
    return f'"{runner}" "{paths.app_root() / "run.py"}"'


def autostart_enabled() -> bool:
    if os.name != "nt":
        return False
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.QueryValueEx(key, _AUTOSTART_NAME)
        return True
    except OSError:
        return False


def set_autostart(enabled: bool) -> bool:
    if os.name != "nt":
        return False
    import winreg

    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, _AUTOSTART_NAME, 0, winreg.REG_SZ, launch_command())
            else:
                try:
                    winreg.DeleteValue(key, _AUTOSTART_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        return False


def context_menu_enabled() -> bool:
    if os.name != "nt":
        return False
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CTX_SHELLS[0]):
            return True
    except OSError:
        return False


def set_context_menu(enabled: bool, label: str = "Scan with CYVEX") -> bool:
    if os.name != "nt":
        return False
    import winreg

    command = f'{launch_command()} --scan "%1"'
    try:
        for shell in _CTX_SHELLS:
            if enabled:
                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, shell, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, None, 0, winreg.REG_SZ, label)
                    try:
                        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, sys.executable)
                    except OSError:
                        pass
                cmd_key = shell + r"\command"
                with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, cmd_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, None, 0, winreg.REG_SZ, command)
            else:
                _delete_tree(winreg.HKEY_CURRENT_USER, shell)
        return True
    except OSError:
        return False


def _delete_tree(root, path: str) -> None:  # type: ignore[no-untyped-def]
    import winreg

    try:
        with winreg.OpenKey(root, path + r"\command") as key:
            winreg.DeleteKey(key, "")
    except OSError:
        pass
    try:
        with winreg.OpenKey(root, path) as key:
            winreg.DeleteKey(key, "")
    except OSError:
        pass


def find_browser() -> str | None:
    """Locate a Chromium browser for headless HTML -> PDF rendering."""
    import shutil

    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""),
                     r"Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if path and Path(path).exists():
            return path
    return shutil.which("msedge") or shutil.which("chrome")


def html_to_pdf(html: str, out_path: str, timeout: int = 60) -> dict[str, Any]:
    """Render an HTML string to a real PDF using a headless Chromium browser."""
    import tempfile

    browser = find_browser()
    if not browser:
        return {"ok": False, "error": "no-browser"}
    tmp_html = Path(tempfile.gettempdir()) / "novu_report.html"
    try:
        tmp_html.write_text(html, encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    args = [
        browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--no-first-run", "--no-default-browser-check",
        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=3000",
        f"--print-to-pdf={out_path}", tmp_html.as_uri(),
    ]
    try:
        result = subprocess.run(
            args, timeout=timeout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=0x08000000 if sys.platform == "win32" else 0,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        try:
            tmp_html.unlink(missing_ok=True)
        except OSError:
            pass
    if result.returncode != 0 or not Path(out_path).exists():
        return {"ok": False, "error": f"render-failed ({result.returncode})"}
    return {"ok": True}


def acquire_single_instance(name: str = "CYVEX_SingleInstance") -> bool:
    """Create a named mutex; return False if another instance already holds it."""
    if os.name != "nt":
        return True
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, name)
    if not handle:
        return True
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        return False
    winutil_state["mutex"] = handle
    return True


winutil_state: dict[str, object] = {}


def message_box(title: str, message: str) -> None:
    if os.name != "nt":
        return
    import ctypes

    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x40)
    except OSError:
        pass


def focus_existing_window(title_prefix: str = "CYVEX") -> bool:
    """Bring an already-running instance's window to the foreground."""
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    found: dict[str, int] = {"hwnd": 0}
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd, _lparam):  # type: ignore[no-untyped-def]
        length = user32.GetWindowTextLengthW(hwnd)
        if length:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if buf.value.startswith(title_prefix):
                found["hwnd"] = hwnd
                return False
        return True

    try:
        user32.EnumWindows(proc(callback), 0)
    except OSError:
        return False
    hwnd = found["hwnd"]
    if not hwnd:
        return False
    try:
        user32.ShowWindow(hwnd, 5)  # SW_SHOW
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
    except OSError:
        return False
    return True


def _pending_file() -> Path:
    from . import paths

    return paths.data_dir() / "pending_scans.txt"


def enqueue_pending_scan(path: str) -> None:
    try:
        with _pending_file().open("a", encoding="utf-8") as handle:
            handle.write(str(path).strip() + "\n")
    except OSError:
        pass


def drain_pending_scans() -> list[str]:
    file = _pending_file()
    try:
        if not file.exists():
            return []
        text = file.read_text(encoding="utf-8")
        file.unlink()
    except OSError:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def toast(title: str, message: str) -> bool:
    """Show a Windows toast notification (best effort, never raises)."""
    if os.name != "nt":
        return False
    env = dict(os.environ)
    env["CYVEX_TOAST_TITLE"] = _xml_escape(str(title or ""))
    env["CYVEX_TOAST_MSG"] = _xml_escape(str(message or ""))
    try:
        import shutil

        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            return False
        creationflags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW
        subprocess.Popen(
            [powershell, "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
             "-Command", _TOAST_PS],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        return True
    except (OSError, ValueError):
        return False

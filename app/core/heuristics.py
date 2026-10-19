"""Heuristic, behaviour-based detection.

Signature lookups only catch files whose exact hash is already known. The
heuristic engine adds *suspicious pattern* detection: risky file types placed
in high-risk locations, double extensions, and script/loader indicators that
are common to droppers, worms and macros. Findings are advisory and are
reported with the rule that triggered them.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

RISKY_EXTENSIONS = {
    ".exe", ".dll", ".scr", ".bat", ".cmd", ".com", ".pif", ".cpl",
    ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh", ".hta", ".ps1", ".psm1",
    ".jar", ".msi", ".lnk", ".reg", ".url", ".iso", ".img",
    ".docm", ".xlsm", ".pptm", ".dotm", ".xlam",
}

SCRIPT_EXTENSIONS = {
    ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh", ".hta", ".ps1", ".psm1", ".bat", ".cmd",
}

DOUBLE_EXT_RE = re.compile(
    r"\.(pdf|doc|docx|xls|xlsx|ppt|pptx|jpg|jpeg|png|gif|bmp|mp3|mp4|avi|mkv|txt|csv|zip|rar|7z|iso)"
    r"\.(exe|scr|com|pif|bat|cmd|vbs|js|jse|wsf|hta|ps1|lnk|msi|jar)$",
    re.IGNORECASE,
)

# (rule name, severity, compiled pattern)
CONTENT_RULES: list[tuple[str, str, re.Pattern[bytes]]] = [
    ("Script:WScript.Shell.Creation", "high",
     re.compile(rb"createobject\s*\(\s*[\"']wscript\.shell", re.IGNORECASE)),
    ("Script:FileSystemObject.Creation", "medium",
     re.compile(rb"createobject\s*\(\s*[\"']scripting\.filesystemobject", re.IGNORECASE)),
    ("Script:Shell.Application.Creation", "medium",
     re.compile(rb"createobject\s*\(\s*[\"']shell\.application", re.IGNORECASE)),
    ("Powershell:EncodedCommand", "high",
     re.compile(rb"powershell(\.exe)?[^\n]{0,40}-(enc|encodedcommand)\b", re.IGNORECASE)),
    ("Downloader:RemotePayload", "high",
     re.compile(rb"(invoke-webrequest|downloadstring|downloadfile|bitsadmin|start-bitstransfer"
                rb"|certutil[^\n]{0,20}-urlcache|winhttp\.winhttprequest)", re.IGNORECASE)),
    ("Execution:CmdDrop", "medium",
     re.compile(rb"cmd(\.exe)?\s*/c\s", re.IGNORECASE)),
    ("Persistence:RunKey", "medium",
     re.compile(rb"currentversion[\\/]?run(once)?", re.IGNORECASE)),
    ("Macro:AutoExec", "high",
     re.compile(rb"(auto_?open|auto_?exec|document_open|workbook_open|auto_?close)", re.IGNORECASE)),
    ("Script:DynamicEval", "low",
     re.compile(rb"\beval\s*\(|fromcharcode\s*\(|unescape\s*\(", re.IGNORECASE)),
    ("Script:Base64Blob", "low",
     re.compile(rb"(frombase64string|atob\s*\(|base64[^\n]{0,10}decode)", re.IGNORECASE)),
    ("Autorun:Autostart", "high",
     re.compile(rb"\[autorun\][^\n]*\n[^\n]*(open|shell\\execute|shellexecute)", re.IGNORECASE)),
]

HIGH_RISK_DIR_MARKERS = (
    "\\temp\\", "\\tmp\\", "\\startup\\", "\\appdata\\local\\temp\\",
    "\\downloads\\", "\\windows\\temp\\", "\\programdata\\",
)

SEVERITY_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _in_risky_location(path: str) -> bool:
    lowered = path.lower()
    return any(marker in lowered for marker in HIGH_RISK_DIR_MARKERS)


def analyze(path: str, head: bytes, size: int = 0) -> list[dict[str, Any]]:
    """Return a list of heuristic findings for a single file."""
    findings: list[dict[str, Any]] = []
    name = os.path.basename(path)
    ext = Path(name).suffix.lower()
    risky_dir = _in_risky_location(path)

    if DOUBLE_EXT_RE.search(name):
        findings.append({
            "name": "Heur:DoubleExtension",
            "severity": "high",
            "detail": "File uses a disguised double extension",
        })

    if name.lower() == "autorun.inf":
        findings.append({
            "name": "Heur:AutorunFile",
            "severity": "high",
            "detail": "autorun.inf present (common USB worm vector)",
        })

    if risky_dir and ext in RISKY_EXTENSIONS:
        findings.append({
            "name": "Heur:RiskyLocation",
            "severity": "low",
            "detail": "Executable/script running from a high-risk folder",
        })

    for rule_name, severity, pattern in CONTENT_RULES:
        if pattern.search(head):
            findings.append({
                "name": f"Heur:{rule_name}",
                "severity": severity,
                "detail": "Suspicious script/loader pattern detected",
            })

    try:
        attrs = os.stat(path).st_file_attributes  # type: ignore[attr-defined]
        if attrs & 0x2 and ext in RISKY_EXTENSIONS and risky_dir:  # FILE_ATTRIBUTE_HIDDEN
            findings.append({
                "name": "Heur:HiddenExecutable",
                "severity": "medium",
                "detail": "Hidden executable in a high-risk folder",
            })
    except (AttributeError, OSError):
        pass

    return findings

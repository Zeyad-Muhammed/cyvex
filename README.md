# CYVEX

A portable **Windows desktop anti-malware scanner**. It combines a signature
(hash) engine, a heuristic/behaviour engine, optional VirusTotal cloud
reputation, a quarantine vault, real-time file monitoring, a ransomware shield
and USB protection behind a modern, Norton-inspired interface — with its own
teal colour system and full **Arabic / English** support.

> **Scope note:** CYVEX is a real, working scanner, but it is not a kernel-level
> anti-virus. It does not install drivers, filter the network stack, or stop
> processes before they run. It detects by file hash, suspicious patterns and
> cloud reputation, isolates threats, and monitors folders. Those limits are by
> design and are stated honestly.

## Features

| Module | What it does |
| --- | --- |
| Quick / Full / Custom scan | Scans high-risk areas, every fixed drive, or folders you pick. |
| Signature engine | Matches SHA-256 against a database of known malicious hashes (EICAR seeded). |
| Heuristic engine | Detects disguised double extensions, risky file types in high-risk folders, and script/loader patterns. |
| Archive scanning | Looks inside ZIP/JAR files for hidden threats. |
| VirusTotal (optional) | Looks up a file's hash against 70+ engines. Only the hash is sent — files never leave the device. |
| Quarantine | Moves threats into an obfuscated vault; restore false positives or delete permanently. |
| Real-time protection | Scans files the instant they land in Downloads, Desktop, Documents or Temp. |
| Ransomware Shield | Snapshots protected folders and raises a critical alert on mass file changes. |
| USB protection | Auto-scans removable drives when they are connected. |
| Scheduled scans | Daily or weekly automatic scans. |
| History & activity | Full scan history with per-scan detections and a live activity feed. |
| Exclusions | Skip trusted paths from all scanning. |
| Report export | Export scan reports as CSV, HTML, or real PDF (via headless Edge/Chrome). |
| System tray | Optional tray icon with quick actions; close-to-tray keeps CYVEX running. |
| Single instance | A second launch focuses the running window and forwards scan requests. |
| Autostart | Optional launch on Windows sign-in. |
| Explorer menu | Optional "Scan with CYVEX" right-click entry for files, folders and drives. |
| Drag & drop | Drop files or folders onto the window to scan them instantly. |
| Signature updates | Manual or scheduled signature-pack updates from a configurable URL. |
| Diagnostics | Rotating logs under `data\logs` with global exception capture. |
| Themes & i18n | Dark/light themes, Arabic and English UI. |

## Requirements

- Windows 10/11 (WebView2 runtime, pre-installed on modern Windows)
- Python 3.11+ (3.12 recommended) for running from source

## Run from source

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

Or simply double-click `run.bat`.

## Build a portable folder

```bat
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe build.py
```

The result is `dist\CYVEX\` — copy that folder anywhere and run
`CYVEX.exe`. A `data\` folder (database, quarantine, backups, logs) is
created next to the executable on first run.

## Testing the engine

The industry-standard **EICAR** test file is supported. Create it with:

```powershell
Set-Content -LiteralPath "$env:TEMP\eicar.com" -NoNewline -Value 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
```

Run a **Custom scan** on `%TEMP%` (or a Quick scan) — CYVEX should detect
`EICAR-Test-File`, quarantine it, and list it in the quarantine view.

## VirusTotal (optional)

1. Get a free API key from https://www.virustotal.com/
2. Settings → VirusTotal → paste the key, enable cloud lookups, save.

Only SHA-256 hashes are queried (free tier: ~4 requests/minute).

## Project layout

```
app/
  main.py            entry point (pywebview window)
  api.py             JS <-> Python bridge (all UI-callable methods)
  core/
    database.py      SQLite persistence
    settings.py      typed settings
    signatures.py    hash signature engine
    heuristics.py    behaviour/pattern rules
    hashing.py       bounded SHA-256
    virustotal.py    cloud reputation (cached, rate-limited)
    quarantine.py    vault (move + obfuscate + restore)
    scanner.py       quick/full/custom engine (pause/resume/stop)
    realtime.py      watchdog-based live scanning
    ransomware.py    backup + behaviour alert
    usb.py           removable-drive watcher
    scheduler.py     daily/weekly scans
    tray.py          system tray icon (pystray)
    log.py           rotating file logging + exception hooks
    winutil.py       Windows drive/startup/tray/context-menu/PDF helpers
  web/               HTML/CSS/JS interface (no external CDNs)
data/                runtime data (created on first run)
```

## Limitations

- No kernel driver / process-termination layer (see scope note above).
- RAR/7z archive internals are not parsed (ZIP/JAR only) without extra native tools.
- VirusTotal free tier limits cloud lookups per minute.
- Ransomware Shield backs up and alerts; it cannot block writes in real time
  without a filesystem minifilter.

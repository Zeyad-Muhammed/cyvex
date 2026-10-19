"""File hashing helpers with bounded, cancellable reads."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable

CHUNK = 1024 * 1024  # 1 MiB


def sha256_file(path: str | Path, max_bytes: int | None = None,
                should_stop: Callable[[], bool] | None = None) -> str | None:
    """Return the SHA-256 hex digest of a file, or ``None`` if unreadable.

    ``max_bytes`` limits how much of a huge file is hashed (partial hash);
    ``should_stop`` allows a running scan to abort a long read promptly.
    """
    digest = hashlib.sha256()
    read = 0
    try:
        with open(path, "rb") as handle:
            while True:
                if should_stop and should_stop():
                    return None
                chunk = handle.read(CHUNK)
                if not chunk:
                    break
                digest.update(chunk)
                read += len(chunk)
                if max_bytes is not None and read >= max_bytes:
                    break
    except (OSError, PermissionError):
        return None
    return digest.hexdigest()

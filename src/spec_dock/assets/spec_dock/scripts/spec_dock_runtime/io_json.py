from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    """Return current local time in ISO-8601 (timezone-aware, seconds precision)."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _today() -> str:
    """Return today's date as `YYYY-MM-DD`."""
    return datetime.now().date().isoformat()


def _load_json(path: Path) -> Any:
    """Read and parse JSON from `path` with user-friendly errors."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {path}: {e}") from e
    except UnicodeDecodeError as e:
        raise RuntimeError(f"Failed to read: {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Failed to read: {path}: {e}") from e


def _write_json(path: Path, data: Any) -> None:
    """Write `data` as pretty-printed JSON into `path` (UTF-8)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _try_make_readonly(path: Path) -> tuple[bool, str | None]:
    """Try to make `path` read-only (best-effort, never raises)."""
    try:
        mode = path.stat().st_mode
        path.chmod(mode & ~0o222)
    except OSError as e:
        return False, str(e)

    if os.name == "posix":
        try:
            if path.stat().st_mode & 0o222:
                return False, "write bit still set after chmod"
        except OSError as e:
            return False, str(e)

    return True, None


def _warn(message: str) -> None:
    """Print a runtime warning using the stable CLI prefix."""
    print(f"spec-dock: (warn) {message}", file=sys.stderr)

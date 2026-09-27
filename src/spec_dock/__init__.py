from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

__all__ = ["__version__"]

try:
    __version__ = Path(__file__).with_name("version.txt").read_text(encoding="utf-8").strip()
except OSError:
    try:
        __version__ = version("spec-dock")
    except PackageNotFoundError:
        __version__ = "0.0.0+unknown"

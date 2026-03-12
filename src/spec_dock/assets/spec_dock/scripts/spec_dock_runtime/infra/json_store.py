from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io_json import _load_json, _write_json


def load_json(path: Path) -> Any:
    return _load_json(path)


def write_json(path: Path, data: Any) -> None:
    _write_json(path, data)

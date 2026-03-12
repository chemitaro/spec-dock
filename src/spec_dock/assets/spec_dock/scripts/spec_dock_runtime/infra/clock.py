from __future__ import annotations

from ..io_json import _now_iso, _today


def now_iso() -> str:
    return _now_iso()


def today() -> str:
    return _today()

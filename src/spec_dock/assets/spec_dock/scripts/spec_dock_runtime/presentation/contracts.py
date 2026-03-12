from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CliText:
    stdout_lines: list[str]
    stderr_lines: list[str]
    warnings: list[str]

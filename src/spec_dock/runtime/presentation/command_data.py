"""Shared typed CLI payloads without a dependency on command dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spec_dock.runtime.presentation.envelope import Diagnostic


@dataclass(frozen=True)
class FamilyData:
    kind: str
    result: dict[str, object]


@dataclass(frozen=True)
class DiagnosticData:
    findings: tuple[Diagnostic, ...] = ()
    unverified: tuple[str, ...] = ()
    kind: str = "diagnostic"


@dataclass(frozen=True)
class ActiveData:
    selection: dict[str, object]
    ancestors: tuple[str, ...]
    kind: str = "active"


@dataclass(frozen=True)
class SyncData:
    observed_at: str
    source: str
    complete: bool
    worktrees: tuple[dict[str, object], ...]
    scopes: tuple[dict[str, object], ...]
    counts: tuple[dict[str, object], ...]
    findings: tuple[Diagnostic, ...] = ()
    kind: str = "sync"

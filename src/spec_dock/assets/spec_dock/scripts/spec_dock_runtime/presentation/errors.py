"""Typed CLI help and usage payloads."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CliMessageData:
    help: str | None


@dataclass(frozen=True)
class VersionData:
    version: str
    engine_digest: str | None


@dataclass(frozen=True)
class CompletionData:
    shell: str
    script: str

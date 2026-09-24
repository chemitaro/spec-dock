"""Verify a pinned external SpecDock engine before the repository shim delegates."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class EnginePin:
    executable: Path
    distribution_root: Path
    distribution_digest: str


@dataclass(frozen=True)
class VerifiedEngine:
    executable: Path
    distribution_root: Path
    distribution_digest: str


def digest_distribution(root: Path) -> str:
    """Hash path, executable bit, and bytes of every file in one fixed bundle."""
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("distribution root must be an absolute, real directory")
    digest = hashlib.sha256()
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("distribution contains a symlink")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ValueError("distribution contains an unsupported entry")
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        metadata = path.stat()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update((metadata.st_mode & 0o111).to_bytes(2, "big"))
        digest.update(metadata.st_size.to_bytes(8, "big"))
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    return digest.hexdigest()


def verify_engine_pin(pin: EnginePin, *, checkout_root: Path) -> VerifiedEngine:
    if not _SHA256.fullmatch(pin.distribution_digest):
        raise ValueError("invalid distribution digest")
    if not pin.executable.is_absolute() or not pin.distribution_root.is_absolute():
        raise ValueError("engine paths must be absolute")
    if pin.executable.is_symlink() or pin.distribution_root.is_symlink():
        raise ValueError("engine path must not be a symlink")
    checkout = checkout_root.resolve(strict=True)
    distribution = pin.distribution_root.resolve(strict=True)
    executable = pin.executable.resolve(strict=True)
    if distribution.is_relative_to(checkout) or executable.is_relative_to(checkout):
        raise ValueError("engine must be outside the checkout")
    if not executable.is_relative_to(distribution) or not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError("engine executable must be an executable file within the fixed distribution")
    if digest_distribution(distribution) != pin.distribution_digest:
        raise ValueError("engine distribution digest mismatch")
    return VerifiedEngine(executable, distribution, pin.distribution_digest)

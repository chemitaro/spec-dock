"""Verify a pinned external SpecDock engine before the repository shim delegates."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

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
    if (
        distribution.is_relative_to(checkout)
        or checkout.is_relative_to(distribution)
        or executable.is_relative_to(checkout)
    ):
        raise ValueError("engine must be outside the checkout")
    if not executable.is_relative_to(distribution) or not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError("engine executable must be an executable file within the fixed distribution")
    if digest_distribution(distribution) != pin.distribution_digest:
        raise ValueError("engine distribution digest mismatch")
    return VerifiedEngine(executable, distribution, pin.distribution_digest)


def git_common_directory(project_root: Path) -> Path:
    """Resolve the shared control directory without importing checkout code."""
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("Git common directory could not be resolved") from error
    if completed.returncode != 0 or not completed.stdout.strip():
        raise ValueError("Git common directory could not be resolved")
    common = Path(completed.stdout.strip())
    if not common.is_absolute() or not common.is_dir():
        raise ValueError("Git common directory is invalid")
    return common.resolve(strict=True)


def read_engine_pin(common_dir: Path, *, checkout_root: Path, require_control_match: bool = True) -> VerifiedEngine:
    """Decode and verify the absolute package location recorded in common control."""
    if not common_dir.is_absolute() or not checkout_root.is_absolute():
        raise ValueError("engine lookup requires absolute paths")
    locator = common_dir / "spec-dock/control/engine.json"
    control = common_dir / "spec-dock/control/control.json"
    if locator.is_symlink() or control.is_symlink():
        raise ValueError("engine control contains a symlink")
    try:
        payload = json.loads(locator.read_text(encoding="utf-8"))
        control_payload = json.loads(control.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("fixed engine control is missing or invalid") from error
    if not isinstance(payload, dict) or set(payload) != {
        "schema_version",
        "executable",
        "distribution_root",
        "distribution_digest",
    }:
        raise ValueError("fixed engine locator has an invalid shape")
    if (
        payload["schema_version"] != 1
        or not isinstance(payload["executable"], str)
        or not isinstance(payload["distribution_root"], str)
        or not isinstance(payload["distribution_digest"], str)
        or not isinstance(control_payload, dict)
        or (require_control_match and control_payload.get("engine_digest") != payload["distribution_digest"])
    ):
        raise ValueError("fixed engine and repository control disagree")
    pin = EnginePin(Path(payload["executable"]), Path(payload["distribution_root"]), payload["distribution_digest"])
    return verify_engine_pin(pin, checkout_root=checkout_root)


def write_engine_pin(common_dir: Path, engine: VerifiedEngine) -> None:
    """Publish one verified locator without replacing another engine identity."""
    if not common_dir.is_absolute() or not _SHA256.fullmatch(engine.distribution_digest):
        raise ValueError("engine locator identity is invalid")
    directory = common_dir / "spec-dock/control"
    for parent in (common_dir / "spec-dock", directory):
        parent.mkdir(mode=0o700, exist_ok=True)
        if parent.is_symlink():
            raise ValueError("engine locator directory is redirected")
    path = directory / "engine.json"
    if path.is_symlink():
        raise ValueError("engine locator is redirected")
    payload = {
        "schema_version": 1,
        "executable": str(engine.executable),
        "distribution_root": str(engine.distribution_root),
        "distribution_digest": engine.distribution_digest,
    }
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("existing engine locator is invalid") from error
        if existing != payload:
            raise ValueError("engine locator already pins another distribution")
        return
    temporary = directory / f".engine-{uuid.uuid4().hex}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write((json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        parent_descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def replace_engine_pin(common_dir: Path, *, prior: VerifiedEngine, next_engine: VerifiedEngine) -> None:
    """Change the locator under the common writer lock after comparing its old identity."""
    if not common_dir.is_absolute() or prior == next_engine:
        raise ValueError("engine handover requires two distinct fixed identities")
    path = common_dir / "spec-dock/control/engine.json"
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError("engine locator is redirected")
    existing = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "schema_version": 1,
        "executable": str(prior.executable),
        "distribution_root": str(prior.distribution_root),
        "distribution_digest": prior.distribution_digest,
    }
    if existing != expected:
        raise ValueError("engine locator changed before handover")
    before = path.stat()
    payload = {
        "schema_version": 1,
        "executable": str(next_engine.executable),
        "distribution_root": str(next_engine.distribution_root),
        "distribution_digest": next_engine.distribution_digest,
    }
    temporary = path.parent / f".engine-{uuid.uuid4().hex}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write((json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        after = path.stat()
        if (after.st_dev, after.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError("engine locator identity changed before handover")
        temporary.replace(path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)

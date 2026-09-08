"""Exact-clean legacy 0.2.3 fixture loading and admission."""

from __future__ import annotations

import base64
from collections.abc import Mapping
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import NoReturn, cast

from spec_dock.provider_lifecycle.candidate import (
    FIXED_DOMAINS,
    CandidateError,
    _entry_stream,
    _safe_relative_symlink,
)
from spec_dock.provider_lifecycle.filesystem import TreeEntry

LEGACY_VERSION = "0.2.3"
LEGACY_SOURCE_COMMIT = "dc638e936e763cc7a6087f258201ed9ed654e7fb"
LEGACY_FIXTURE_PATH = Path(__file__).parent.parent / "assets" / "provider_lifecycle" / "legacy-0.2.3.json"
LEGACY_MAGIC = b"spec-dock-exact-legacy-fixture-v1\0"
_TOP_KEYS = (
    "schema_version",
    "legacy_version",
    "source_repository",
    "source_commit",
    "version_record",
    "domains",
    "aggregate_digest",
)
_VERSION_KEYS = ("path", "kind", "mode", "sha256", "bytes_base64")
_DOMAIN_KEYS = ("kind", "path", "source_path", "tree_digest", "entries")
_DIGEST_CHARS = set("0123456789abcdef")


class LegacyFixtureError(ValueError):
    """The fixture is not the exact closed legacy source."""


def _fail(message: str) -> NoReturn:
    raise LegacyFixtureError(message)


def _directory_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


def _open_absolute_directory_no_follow(path: Path) -> int:
    raw_path = os.fspath(path)
    if not Path(raw_path).is_absolute() or "\x00" in raw_path:
        raise LegacyFixtureError("workspace root must be absolute and NUL-free")
    current_fd = os.open(os.sep, _directory_open_flags())
    try:
        for component in Path(raw_path).parts[1:]:
            if component in {"", ".", ".."}:
                raise LegacyFixtureError("workspace root contains an unsafe component")
            next_fd = os.open(component, _directory_open_flags(), dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _open_child_directory_no_follow(parent_fd: int, components: tuple[str, ...]) -> int:
    current_fd = os.dup(parent_fd)
    try:
        for component in components:
            if component in {"", ".", ".."}:
                raise LegacyFixtureError("workspace path contains an unsafe component")
            next_fd = os.open(component, _directory_open_flags(), dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _exact_keys(value: Mapping[str, object], expected: tuple[str, ...], label: str) -> None:
    if tuple(value.keys()) != expected:
        _fail(f"{label} keys are not exact")


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(character not in _DIGEST_CHARS for character in value):
        _fail(f"{label} is not a lowercase SHA-256 digest")
    return cast("str", value)


def _decode_fixture_bytes(payload: bytes | str) -> Mapping[str, object]:
    raw = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    if not raw.endswith(b"\n") or raw[:-1].find(b"\n") >= 0:
        _fail("legacy fixture must have one terminal LF")
    try:
        text = raw[:-1].decode("utf-8")
    except UnicodeDecodeError as exc:
        _fail(f"legacy fixture is not UTF-8: {exc}")

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                _fail(f"legacy fixture contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=lambda constant: _fail(constant))
    except LegacyFixtureError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        _fail(f"legacy fixture is not valid JSON: {exc}")
    if not isinstance(value, Mapping):
        _fail("legacy fixture must be an object")
    canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"
    if canonical != raw:
        _fail("legacy fixture must be canonical compact JSON")
    return value


def _tree_entries(value: Mapping[str, object]) -> tuple[TreeEntry, ...]:
    raw_entries = value["entries"]
    if not isinstance(raw_entries, list):
        _fail("legacy domain entries must be an array")
    raw_entries = cast("list[object]", raw_entries)
    entries: list[TreeEntry] = []
    previous: bytes | None = None
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, Mapping):
            _fail("legacy domain entry must be an object")
        kind = raw_entry.get("kind")
        if kind == "directory":
            _exact_keys(raw_entry, ("kind", "path"), "legacy directory entry")
            path = raw_entry["path"]
            if not isinstance(path, str) or not path or "\x00" in path or path.startswith("/"):
                _fail("legacy directory path is invalid")
            entry = TreeEntry("directory", path)
        elif kind == "regular":
            _exact_keys(raw_entry, ("kind", "path", "mode", "sha256"), "legacy regular entry")
            path = raw_entry["path"]
            mode = raw_entry["mode"]
            if not isinstance(path, str) or not path or "\x00" in path or path.startswith("/"):
                _fail("legacy regular path is invalid")
            if mode not in {"0644", "0755"}:
                _fail("legacy regular mode is invalid")
            entry = TreeEntry("regular", path, int(mode, 8), _digest(raw_entry["sha256"], "legacy entry sha256"))
        elif kind == "symlink":
            _exact_keys(raw_entry, ("kind", "path", "target"), "legacy symlink entry")
            path = raw_entry["path"]
            target = raw_entry["target"]
            if not isinstance(path, str) or not path or "\x00" in path or path.startswith("/"):
                _fail("legacy symlink path is invalid")
            if not isinstance(target, str):
                _fail("legacy symlink target is invalid")
            try:
                _safe_relative_symlink(target)
            except CandidateError as exc:
                raise LegacyFixtureError(str(exc)) from exc
            entry = TreeEntry("symlink", path, target=target)
        else:
            _fail("legacy entry kind is invalid")
        encoded = entry.path.encode("utf-8")
        if previous is not None and encoded <= previous:
            _fail("legacy entries are not in UTF-8 byte order")
        previous = encoded
        entries.append(entry)
    return tuple(entries)


def _validate_fixture(value: Mapping[str, object]) -> dict[str, object]:
    _exact_keys(value, _TOP_KEYS, "legacy fixture")
    if (
        value["schema_version"] != 1
        or value["legacy_version"] != LEGACY_VERSION
        or value["source_repository"] != "chemitaro/spec-dock"
        or value["source_commit"] != LEGACY_SOURCE_COMMIT
    ):
        _fail("legacy fixture provenance is not exact")
    version_record = value["version_record"]
    if not isinstance(version_record, Mapping):
        _fail("legacy version record must be an object")
    _exact_keys(version_record, _VERSION_KEYS, "legacy version record")
    if (
        version_record["path"] != "spec-dock/spec-dock.version"
        or version_record["kind"] != "regular"
        or version_record["mode"] != "0644"
    ):
        _fail("legacy version record identity is not exact")
    try:
        version_bytes = base64.b64decode(version_record["bytes_base64"], validate=True)
    except (TypeError, ValueError) as exc:
        _fail(f"legacy version record bytes are invalid: {exc}")
    if (
        version_bytes != b"0.2.3\n"
        or _digest(version_record["sha256"], "legacy version record sha256")
        != hashlib.sha256(version_bytes).hexdigest()
    ):
        _fail("legacy version record content is not exact")

    raw_domains = value["domains"]
    if not isinstance(raw_domains, list) or len(raw_domains) != len(FIXED_DOMAINS):
        _fail("legacy fixture must contain six domains")
    raw_domains = cast("list[object]", raw_domains)
    normalized_domains: list[dict[str, object]] = []
    aggregate = bytearray(LEGACY_MAGIC + LEGACY_VERSION.encode() + b"\0")
    for index, raw_domain in enumerate(raw_domains):
        if not isinstance(raw_domain, Mapping):
            _fail("legacy domain must be an object")
        _exact_keys(raw_domain, _DOMAIN_KEYS, "legacy domain")
        expected_kind, expected_path, source_suffix = FIXED_DOMAINS[index]
        expected_source = f"src/spec_dock/assets/{source_suffix}"
        if (raw_domain["kind"], raw_domain["path"], raw_domain["source_path"]) != (
            expected_kind,
            expected_path,
            expected_source,
        ):
            _fail("legacy domain order or source path is not exact")
        entries = _tree_entries(raw_domain)
        stream = _entry_stream(entries)
        tree_digest = _digest(raw_domain["tree_digest"], "legacy tree_digest")
        if tree_digest != hashlib.sha256(stream).hexdigest():
            _fail("legacy tree_digest does not match entries")
        aggregate.extend(b"DOMAIN\0" + expected_kind.encode() + b"\0" + expected_path.encode() + b"\0" + stream)
        normalized_domains.append(dict(raw_domain))
    if _digest(value["aggregate_digest"], "legacy aggregate_digest") != hashlib.sha256(aggregate).hexdigest():
        _fail("legacy aggregate_digest does not match domains")
    result = dict(value)
    result["domains"] = normalized_domains
    return result


def load_legacy_fixture(path: str | os.PathLike[str] | None = None) -> dict[str, object]:
    """Load and strictly validate the shipped exact-clean fixture."""

    fixture_path = LEGACY_FIXTURE_PATH if path is None else Path(path)
    try:
        payload = fixture_path.read_bytes()
    except OSError as exc:
        raise LegacyFixtureError(f"cannot read legacy fixture: {fixture_path}") from exc
    if len(payload) > 1024 * 1024:
        raise LegacyFixtureError("legacy fixture is oversized")
    return _validate_fixture(_decode_fixture_bytes(payload))


def _capture_entries_fd(directory_fd: int, *, exclude_marker: bool) -> tuple[TreeEntry, ...]:
    entries: list[TreeEntry] = []

    def visit(fd: int, prefix: str) -> None:
        names = sorted(os.listdir(fd), key=lambda item: os.fsencode(item))
        for name in names:
            if exclude_marker and not prefix and name == ".spec-dock-provider-slot.json":
                continue
            relative = f"{prefix}/{name}" if prefix else name
            value = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(value.st_mode):
                entries.append(TreeEntry("directory", relative))
                child_fd = os.open(name, _directory_open_flags(), dir_fd=fd)
                try:
                    visit(child_fd, relative)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(value.st_mode):
                mode = stat.S_IMODE(value.st_mode)
                if mode not in {0o644, 0o755}:
                    raise LegacyFixtureError(f"legacy regular mode is invalid: {relative}")
                child_fd = os.open(
                    name,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=fd,
                )
                try:
                    opened = os.fstat(child_fd)
                    if not _same_regular_identity(value, opened):
                        raise LegacyFixtureError(f"legacy file changed while opening: {relative}")
                    digest = hashlib.sha256()
                    while True:
                        chunk = os.read(child_fd, 1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                    after = os.fstat(child_fd)
                    if not _same_regular_identity(opened, after):
                        raise LegacyFixtureError(f"legacy file changed while reading: {relative}")
                finally:
                    os.close(child_fd)
                entries.append(TreeEntry("regular", relative, mode, digest.hexdigest()))
            elif stat.S_ISLNK(value.st_mode):
                target = os.readlink(name, dir_fd=fd)
                try:
                    _safe_relative_symlink(target)
                except CandidateError as exc:
                    raise LegacyFixtureError(str(exc)) from exc
                entries.append(TreeEntry("symlink", relative, target=target))
            else:
                raise LegacyFixtureError(f"legacy entry type is unsupported: {relative}")

    visit(directory_fd, "")
    return tuple(sorted(entries, key=lambda entry: entry.path.encode("utf-8")))


def _same_regular_identity(left: os.stat_result, right: os.stat_result) -> bool:
    return (
        left.st_dev == right.st_dev
        and left.st_ino == right.st_ino
        and left.st_ctime_ns == right.st_ctime_ns
        and left.st_nlink == right.st_nlink
        and left.st_size == right.st_size
        and stat.S_IMODE(left.st_mode) == stat.S_IMODE(right.st_mode)
    )


def _read_record_fd(specdock_fd: int) -> bytes | None:
    try:
        value = os.stat("spec-dock.version", dir_fd=specdock_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1 or stat.S_IMODE(value.st_mode) != 0o644:
        return None
    fd = os.open(
        "spec-dock.version",
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=specdock_fd,
    )
    try:
        opened = os.fstat(fd)
        if not _same_regular_identity(value, opened):
            return None
        data = os.read(fd, 4097)
        if not _same_regular_identity(opened, os.fstat(fd)):
            return None
        return data
    finally:
        os.close(fd)


def classify_exact_legacy_workspace(
    workspace_root: str | os.PathLike[str],
    fixture: Mapping[str, object] | None = None,
) -> str:
    """Return ``legacy-0.2.3`` only for an exact fixed-domain match."""

    try:
        expected = _validate_fixture(dict(fixture)) if fixture is not None else load_legacy_fixture()
        root = Path(workspace_root)
        root_fd = _open_absolute_directory_no_follow(root)
        try:
            specdock_fd = _open_child_directory_no_follow(root_fd, ("spec-dock",))
            try:
                record = _read_record_fd(specdock_fd)
            finally:
                os.close(specdock_fd)
        except OSError:
            os.close(root_fd)
            return "modified-legacy-workspace"
        version_record = expected["version_record"]
        assert isinstance(version_record, Mapping)
        expected_bytes = base64.b64decode(version_record["bytes_base64"], validate=True)
        if record != expected_bytes:
            os.close(root_fd)
            return "modified-legacy-workspace"
        raw_domains = expected["domains"]
        assert isinstance(raw_domains, list)
        aggregate = bytearray(LEGACY_MAGIC + LEGACY_VERSION.encode() + b"\0")
        try:
            for index, raw_domain in enumerate(raw_domains):
                assert isinstance(raw_domain, Mapping)
                kind, public_path, _ = FIXED_DOMAINS[index]
                domain_fd = _open_child_directory_no_follow(root_fd, tuple(public_path.split("/")))
                try:
                    if kind == "slot":
                        try:
                            os.stat(".spec-dock-provider-slot.json", dir_fd=domain_fd, follow_symlinks=False)
                        except FileNotFoundError:
                            pass
                        else:
                            return "modified-legacy-workspace"
                    current_entries = _capture_entries_fd(domain_fd, exclude_marker=kind == "slot")
                finally:
                    os.close(domain_fd)
                fixture_entries = _tree_entries(raw_domain)
                if current_entries != fixture_entries:
                    return "modified-legacy-workspace"
                stream = _entry_stream(current_entries)
                if hashlib.sha256(stream).hexdigest() != raw_domain["tree_digest"]:
                    return "modified-legacy-workspace"
                aggregate.extend(b"DOMAIN\0" + kind.encode() + b"\0" + public_path.encode() + b"\0" + stream)
            if hashlib.sha256(aggregate).hexdigest() != expected["aggregate_digest"]:
                return "modified-legacy-workspace"
            return "legacy-0.2.3"
        finally:
            os.close(root_fd)
    except (OSError, ValueError, TypeError, CandidateError, LegacyFixtureError):
        return "modified-legacy-workspace"


__all__ = [
    "LEGACY_FIXTURE_PATH",
    "LEGACY_SOURCE_COMMIT",
    "LEGACY_VERSION",
    "LegacyFixtureError",
    "classify_exact_legacy_workspace",
    "load_legacy_fixture",
]

"""Bounded, read-only observations of retired records; never execute or repair them."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import os
import re
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.legacy_record_headers import readable_legacy_header
from spec_dock.runtime.infra.json_store import open_guarded_directory

if TYPE_CHECKING:
    from pathlib import Path

MAX_DIAGNOSTIC_BYTES = 1024 * 1024
MAX_LEGACY_OPERATIONS = 4096


@dataclass(frozen=True)
class JsonFileObservation:
    path: Path
    entry_type: str
    classification: str
    size: int | None = None
    payload: dict[str, object] | None = None
    record_kind: str | None = None

    def details(self) -> dict[str, object]:
        schema = self.payload.get("schema_version") if self.payload is not None else None
        return {
            "path": str(self.path),
            "entry_type": self.entry_type,
            "bytes": self.size,
            "classification": self.classification,
            "schema_version": schema if type(schema) is int else None,
            "record_kind": self.record_kind,
        }


def inspect_json_file(path: Path) -> JsonFileObservation:
    """Read a bounded single-link regular JSON object without following redirects."""
    if not path.is_absolute():
        raise ValueError("diagnostic source must be absolute")
    try:
        return _inspect_json_file(path)
    except FileNotFoundError:
        return JsonFileObservation(path, "absent", "absent")
    except ValueError:
        return JsonFileObservation(path, "unavailable", "unsafe_path")
    except OSError:
        return JsonFileObservation(path, "unavailable", "unreadable")


def _inspect_json_file(path: Path) -> JsonFileObservation:
    parent = open_guarded_directory(path.parent)
    try:
        visible = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        entry_type = _entry_type(visible.st_mode)
        if entry_type != "regular" or visible.st_nlink != 1:
            return JsonFileObservation(path, entry_type, "unsafe_file", visible.st_size)
        if visible.st_size > MAX_DIAGNOSTIC_BYTES:
            return JsonFileObservation(path, "regular", "too_large", visible.st_size)
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if _file_key(before) != _file_key(visible):
                return JsonFileObservation(path, "regular", "changed", visible.st_size)
            raw = stream.read(MAX_DIAGNOSTIC_BYTES + 1)
            after = os.fstat(stream.fileno())
        visible_after = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        fresh = open_guarded_directory(path.parent)
        try:
            parent_unchanged = (os.fstat(parent).st_dev, os.fstat(parent).st_ino) == (
                os.fstat(fresh).st_dev,
                os.fstat(fresh).st_ino,
            )
        finally:
            os.close(fresh)
        if (
            not parent_unchanged
            or _file_key(before) != _file_key(after)
            or _file_key(after) != _file_key(visible_after)
        ):
            return JsonFileObservation(path, "regular", "changed", visible.st_size)
        if len(raw) > MAX_DIAGNOSTIC_BYTES:
            return JsonFileObservation(path, "regular", "too_large", len(raw))
        try:
            payload = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        except (ValueError, UnicodeDecodeError, RecursionError):
            return JsonFileObservation(path, "regular", "invalid_json", len(raw))
        if not isinstance(payload, dict):
            return JsonFileObservation(path, "regular", "invalid_object", len(raw))
        return JsonFileObservation(path, "regular", "observed", len(raw), payload)
    finally:
        os.close(parent)


def _entry_type(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    return "special"


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-JSON constant")


def _file_key(value: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_nlink,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def inspect_legacy_files(root: Path, common_dir: Path) -> tuple[JsonFileObservation, ...]:
    control = common_dir / "spec-dock/control"
    files = tuple(
        _classify_legacy(inspect_json_file(path), kind)
        for path, kind in (
            (control / "engine.json", "engine"),
            (control / "control.json", "control"),
            (control / "registry.json", "registry"),
            (root / "spec-dock/.agent/active.json", "active"),
        )
    )
    records: list[JsonFileObservation] = list(files)
    for directory, kind, filename in (
        ("operations", "journal", "journal.json"),
        ("migrations", "migration", "record.json"),
        ("installations", "installation", "group.json"),
        ("finalizations", "finalization", None),
        ("engine-handovers", "handover", None),
    ):
        records.extend(_inspect_records(control / directory, kind, filename, common_dir))
    return tuple(records)


def _classify_legacy(
    observation: JsonFileObservation,
    kind: str,
    common_dir: Path | None = None,
) -> JsonFileObservation:
    classified = _classify_legacy_header(observation, kind, common_dir)
    schema = classified.payload.get("schema_version") if classified.payload is not None else None
    return replace(classified, payload={"schema_version": schema} if type(schema) is int else None)


def _classify_legacy_header(
    observation: JsonFileObservation,
    kind: str,
    common_dir: Path | None = None,
) -> JsonFileObservation:
    observed = replace(observation, record_kind=kind)
    if observed.payload is None:
        return observed
    payload = observed.payload
    if kind == "journal":
        terminal = payload.get("terminal_status")
        effects = payload.get("effects")
        if not readable_legacy_header(payload, kind) or payload.get("operation_id") != observed.path.parent.name:
            return replace(observed, classification="invalid_record")
        assert isinstance(effects, list)
        unresolved = [
            effect for effect in effects if isinstance(effect, dict) and effect.get("status") in ("intent", "unknown")
        ]
        if terminal in ("pending", "unknown") or unresolved:
            plan = payload["effect_plan"]
            assert isinstance(plan, list)
            remote = "remote" in plan or any(effect.get("kind") == "remote" for effect in unresolved)
            return replace(
                observed, classification="remote_effects_unverified" if remote else "operation_effects_unverified"
            )
        return replace(observed, classification="legacy_header_observed")
    if kind in ("migration", "installation", "finalization", "handover"):
        operation_id = observed.path.parent.name if kind in ("migration", "installation") else observed.path.stem
        if (
            not readable_legacy_header(payload, kind)
            or payload.get("operation_id") != operation_id
            or payload.get("common_dir") != str(common_dir)
        ):
            return replace(observed, classification="invalid_record")
        classification = (
            "legacy_header_observed"
            if payload.get("phase") in ("committed", "rolled-back")
            else "transition_effects_unverified"
        )
        return replace(observed, classification=classification)
    expected = {"engine": 1, "control": 3, "registry": 1, "active": 3}[kind]
    if type(payload.get("schema_version")) is not int or payload.get("schema_version") != expected:
        return replace(observed, classification="unknown_schema")
    if not readable_legacy_header(payload, kind):
        return replace(observed, classification="invalid_record")
    return replace(observed, classification="legacy_header_observed")


def _inspect_records(path: Path, kind: str, filename: str | None, common_dir: Path) -> tuple[JsonFileObservation, ...]:
    try:
        return _read_record_directory(path, kind, filename, common_dir)
    except FileNotFoundError:
        return (JsonFileObservation(path, "absent", "absent", record_kind=kind),)
    except ValueError:
        return (JsonFileObservation(path, "unavailable", "unsafe_path", record_kind=kind),)
    except OSError:
        return (JsonFileObservation(path, "unavailable", "unreadable", record_kind=kind),)


def _read_record_directory(
    path: Path,
    kind: str,
    filename: str | None,
    common_dir: Path,
) -> tuple[JsonFileObservation, ...]:
    directory = open_guarded_directory(path)
    try:
        names: list[str] = []
        with os.scandir(directory) as entries:
            for entry in entries:
                if len(names) == MAX_LEGACY_OPERATIONS:
                    return (JsonFileObservation(path, "directory", "too_many_entries", record_kind=kind),)
                names.append(entry.name)
        observations: list[JsonFileObservation] = []
        for name in sorted(names):
            try:
                entry_type = _entry_type(os.stat(name, dir_fd=directory, follow_symlinks=False).st_mode)
            except OSError:
                observations.append(JsonFileObservation(path / name, "unavailable", "unreadable", record_kind=kind))
                continue
            pattern = r"[0-9a-f]{32}" if filename else r"[0-9a-f]{32}\.json"
            if entry_type != ("directory" if filename else "regular") or re.fullmatch(pattern, name) is None:
                observations.append(JsonFileObservation(path / name, entry_type, "unsafe_file", record_kind=kind))
            else:
                journal = inspect_json_file(path / name / filename if filename else path / name)
                if journal.classification == "absent":
                    journal = replace(journal, classification="journal_missing")
                observations.append(_classify_legacy(journal, kind, common_dir))
        fresh = open_guarded_directory(path)
        try:
            if (os.fstat(directory).st_dev, os.fstat(directory).st_ino) != (
                os.fstat(fresh).st_dev,
                os.fstat(fresh).st_ino,
            ):
                observations.append(JsonFileObservation(path, "directory", "changed", record_kind=kind))
        finally:
            os.close(fresh)
        return tuple(observations)
    finally:
        os.close(directory)

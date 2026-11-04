"""The `todos/` place of one catalog: paths, what counts as a record, reading and writing (epic-00547 D-01, D-06).

Records are `todos/<YYYY-MM>/t-xxxx.json`. Readers take no lock: writers replace a whole file, so a reader sees the
old or the new file. Writers run inside `catalog_changes` (the catalog lock shared with sync).
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import secrets
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_sync_rules import is_os_junk
from spec_dock.runtime.domain.todo_record import TodoError, normalize_id, parent_id
from spec_dock.runtime.domain.todo_settings import Layer, parse_layer
from spec_dock.runtime.infra.file_publication import (
    FileSnapshot,
    create_missing_parents,
    publish_file,
    read_regular_file,
)
from spec_dock.runtime.infra.user_config import read_optional

if TYPE_CHECKING:
    from pathlib import Path

TODOS: Final = "todos"
SETTINGS_FILE: Final = "settings.json"
MONTH: Final = re.compile(r"[0-9]{4}-(?:0[1-9]|1[0-2])")
RECORD_NAME: Final = re.compile(r"t-[0-9a-hjkmnp-tv-z]{4}\.json")
CONFLICT_MARK: Final = ".conflict-"


@dataclass(frozen=True)
class Scan:
    records: tuple[Path, ...] = ()
    conflict_copies: tuple[Path, ...] = ()
    unknown: tuple[Path, ...] = ()


@dataclass(frozen=True)
class StoredRecord:
    path: Path
    snapshot: FileSnapshot
    record: dict[str, object]


@dataclass(frozen=True)
class ReadAll:
    records: tuple[StoredRecord, ...] = ()
    invalid: tuple[tuple[Path, str], ...] = ()  # files that are not a JSON object, with the reason
    scan: Scan = Scan()


def encode(record: dict[str, object]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class TodoStore:
    def __init__(self, catalog: Path) -> None:
        self.catalog = catalog
        self.root = catalog / TODOS
        self.settings_path = self.root / SETTINGS_FILE

    def relative(self, path: Path) -> str:
        return path.relative_to(self.catalog).as_posix()

    def record_path(self, todo_id: str, created_at: str) -> Path:
        return self.root / created_at[:7] / f"{todo_id}.json"

    def scan(self) -> Scan:
        """Sort the files under `todos/`; a missing `todos/` is simply empty. OS and temporary files are skipped."""
        if not self.root.is_dir():
            return Scan()
        records: list[Path] = []
        copies: list[Path] = []
        unknown: list[Path] = []
        for entry in sorted(self.root.iterdir()):
            name = entry.name
            if name.startswith(".") or is_os_junk(name) or (name == SETTINGS_FILE and not entry.is_dir()):
                continue
            if not entry.is_dir() or entry.is_symlink() or MONTH.fullmatch(name) is None:
                (copies if CONFLICT_MARK in name else unknown).append(entry)
                continue
            for item in sorted(entry.iterdir()):
                if item.name.startswith(".") or is_os_junk(item.name):
                    continue
                if CONFLICT_MARK in item.name:
                    copies.append(item)
                elif RECORD_NAME.fullmatch(item.name) and not item.is_dir():
                    records.append(item)
                else:
                    unknown.append(item)
        return Scan(tuple(records), tuple(copies), tuple(unknown))

    def read_all(self) -> ReadAll:
        scan = self.scan()
        records: list[StoredRecord] = []
        invalid: list[tuple[Path, str]] = []
        for path in scan.records:
            try:
                snapshot = read_regular_file(path)
                document = json.loads(snapshot.payload.decode("utf-8"))
            except (OSError, ValueError) as error:
                invalid.append((path, f"cannot be read as JSON: {error}"))
                continue
            if not isinstance(document, dict):
                invalid.append((path, "is not a JSON object"))
                continue
            records.append(StoredRecord(path, snapshot, document))
        return ReadAll(tuple(records), tuple(invalid), scan)

    def paths_of(self, todo_id: str) -> list[Path]:
        name = f"{parent_id(normalize_id(todo_id))}.json"
        return [path for path in self.scan().records if path.name == name]

    def find(self, todo_id: str) -> Path:
        """The record file of a task or of a subtask's parent; two months with the same ID stop the command."""
        parent = parent_id(normalize_id(todo_id))
        found = self.paths_of(parent)
        if not found:
            raise TodoError(
                "TODO_NOT_FOUND",
                f"there is no task {parent} in this catalog",
                details={"id": parent},
                next_step="spec-dock todo list --status all",
            )
        if len(found) > 1:
            raise TodoError(
                "TODO_ID_AMBIGUOUS",
                f"{parent} exists in {len(found)} months; give one of them a new ID by hand",
                details={"id": parent, "paths": [self.relative(path) for path in found]},
                next_step="spec-dock todo check",
            )
        return found[0]

    def read_settings(self) -> Layer:
        payload, error = read_optional(self.settings_path)
        return parse_layer("repository", str(self.settings_path), payload, read_error=error)

    def _stage(self, path: Path) -> str:
        return f".{path.name}.{secrets.token_hex(4)}.tmp"

    def write_new(self, path: Path, record: dict[str, object]) -> None:
        create_missing_parents(self.catalog, path, on_created=lambda _directory: None)
        publish_file(path, encode(record), stage_name=self._stage(path), verify=lambda: None)

    def write_replace(self, path: Path, record: dict[str, object], expected: FileSnapshot) -> None:
        publish_file(path, encode(record), stage_name=self._stage(path), verify=lambda: None, expected=expected)

"""The `todos/` place of a catalog: what is a record, reading, finding and writing (iss-00549 D-03)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.todo_record import TodoError, new_record
from spec_dock.runtime.infra.file_publication import read_regular_file
from spec_dock.runtime.infra.todo_store import TodoStore

if TYPE_CHECKING:
    from pathlib import Path


def record(todo_id: str) -> dict[str, object]:
    return new_record(
        todo_id, title="t", by="human", role=None, kind=None, now="2026-11-04T00:00:00Z", due="2026-11-05T00:00:00Z"
    )


def test_scan_sorts_files_into_records_copies_skipped_and_unknown(tmp_path: Path) -> None:
    store = TodoStore(tmp_path)
    assert store.scan().records == () and store.read_all().records == ()
    month = tmp_path / "todos/2026-11"
    month.mkdir(parents=True)
    for name in ("t-7k3m.json", "t-7k3m.conflict-pc-20261104t000000z.json", ".t-7k3m.json.x.tmp", ".DS_Store", "x.txt"):
        (month / name).write_text("{}")
    (tmp_path / "todos/settings.json").write_text("{}")
    (tmp_path / "todos/notes.md").write_text("")
    (tmp_path / "todos/old").mkdir()
    scan = store.scan()
    assert [path.name for path in scan.records] == ["t-7k3m.json"]
    assert [path.name for path in scan.conflict_copies] == ["t-7k3m.conflict-pc-20261104t000000z.json"]
    assert sorted(path.name for path in scan.unknown) == ["notes.md", "old", "x.txt"]


def test_read_all_isolates_broken_files_and_find_resolves_ids(tmp_path: Path) -> None:
    store = TodoStore(tmp_path)
    store.write_new(store.record_path("t-0001", "2026-11-04T00:00:00Z"), record("t-0001"))
    (tmp_path / "todos/2026-11/t-0002.json").write_text("{")
    (tmp_path / "todos/2026-11/t-0003.json").write_text("[]")
    read = store.read_all()
    assert [item.record["id"] for item in read.records] == ["t-0001"]
    assert sorted(path.name for path, _reason in read.invalid) == ["t-0002.json", "t-0003.json"]
    assert store.find("t-0001.2").name == "t-0001.json"
    with pytest.raises(TodoError) as raised:
        store.find("t-0009")
    assert raised.value.code == "TODO_NOT_FOUND"
    (tmp_path / "todos/2026-10").mkdir()
    (tmp_path / "todos/2026-10/t-0001.json").write_text("{}")
    with pytest.raises(TodoError) as raised:
        store.find("t-0001")
    assert raised.value.code == "TODO_ID_AMBIGUOUS" and len(raised.value.details["paths"]) == 2  # type: ignore[arg-type]


def test_write_replace_refuses_a_file_changed_since_it_was_read(tmp_path: Path) -> None:
    store = TodoStore(tmp_path)
    path = store.record_path("t-0001", "2026-11-04T00:00:00Z")
    store.write_new(path, record("t-0001"))
    seen = read_regular_file(path)
    changed = {**record("t-0001"), "title": "u"}
    store.write_replace(path, changed, seen)
    assert json.loads(path.read_text())["title"] == "u"
    with pytest.raises(ValueError):
        store.write_replace(path, record("t-0001"), seen)
    assert [entry.name for entry in path.parent.iterdir()] == ["t-0001.json"]

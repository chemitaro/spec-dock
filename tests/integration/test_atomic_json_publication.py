"""Retained atomic JSON safety, isolated from retired operation-journal fixtures."""

from __future__ import annotations

from multiprocessing import Process, Queue
import os
from pathlib import Path
import time

import pytest

from spec_dock.runtime.infra.json_store import atomic_write_json, reconcile_atomic_json


def test_atomic_json_exchange_failure_keeps_previous_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    original = path.read_bytes()

    def fail_exchange(*args: object, **kwargs: object) -> None:
        raise OSError("injected exchange failure")

    monkeypatch.setattr("spec_dock.runtime.infra.json_store._rename_exchange_at", fail_exchange)
    with pytest.raises(OSError, match="exchange failure"):
        identity = path.stat()
        atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == original


def test_atomic_json_exchange_preserves_racing_destination(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    expected = path.stat()
    competitor = tmp_path / "competitor.json"
    competitor.write_bytes(b'{"competitor":true}\n')

    from spec_dock.runtime.infra import json_store

    real_exchange = json_store._rename_exchange_at
    raced = False

    def race_then_exchange(source_fd: int, source_name: str, target_fd: int, target_name: str) -> None:
        nonlocal raced
        if not raced:
            competitor.replace(path)
            raced = True
        real_exchange(source_fd, source_name, target_fd, target_name)

    monkeypatch.setattr(json_store, "_rename_exchange_at", race_then_exchange)
    with pytest.raises(ValueError, match="identity changed"):
        atomic_write_json(path, {"new": True}, expected_identity=(expected.st_dev, expected.st_ino))
    candidates = [item.read_bytes() for item in tmp_path.rglob("*") if item.is_file()]
    assert b'{"competitor":true}\n' in candidates
    assert path.read_bytes() == b'{"competitor":true}\n'


def test_atomic_json_exchange_error_after_effect_blocks_blind_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    identity = path.stat()
    from spec_dock.runtime.infra import json_store

    real_exchange = json_store._rename_exchange_at

    def effect_then_error(source_fd: int, source_name: str, target_fd: int, target_name: str) -> None:
        real_exchange(source_fd, source_name, target_fd, target_name)
        raise OSError("injected post-effect error")

    monkeypatch.setattr(json_store, "_rename_exchange_at", effect_then_error)
    with pytest.raises(OSError, match="post-effect"):
        atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == b'{"new":true}\n'
    with pytest.raises(RuntimeError, match="recovery is required"):
        atomic_write_json(path, {"newer": True}, expected_identity=(path.stat().st_dev, path.stat().st_ino))


def test_atomic_json_create_only_has_no_second_hardlink(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    atomic_write_json(path, {"created": True})
    assert path.stat().st_nlink == 1
    assert path.read_bytes() == b'{"created":true}\n'


def _exchange_then_hold(path_value: str, ready: Queue[str]) -> None:
    from spec_dock.runtime.infra import json_store

    path = Path(path_value)
    identity = path.stat()
    real_exchange = json_store._rename_exchange_at

    def exchange_then_pause(source_fd: int, source: str, target_fd: int, target: str) -> None:
        real_exchange(source_fd, source, target_fd, target)
        ready.put("exchanged")
        time.sleep(30)

    json_store._rename_exchange_at = exchange_then_pause
    json_store.atomic_write_json(path, {"new": True}, expected_identity=(identity.st_dev, identity.st_ino))


def test_atomic_json_killed_after_exchange_retains_old_and_blocks_retry(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    ready: Queue[str] = Queue()
    child = Process(target=_exchange_then_hold, args=(str(path), ready))
    child.start()
    try:
        assert ready.get(timeout=5) == "exchanged"
    finally:
        child.kill()
        child.join(timeout=5)
    assert path.read_bytes() == b'{"new":true}\n'
    candidates = [item.read_bytes() for item in tmp_path.rglob("*") if item.is_file()]
    assert b'{"original":true}\n' in candidates
    with pytest.raises(RuntimeError, match="recovery is required"):
        atomic_write_json(path, {"newer": True}, expected_identity=(path.stat().st_dev, path.stat().st_ino))
    assert reconcile_atomic_json(path) == ("published",)
    identity = path.stat()
    atomic_write_json(path, {"newer": True}, expected_identity=(identity.st_dev, identity.st_ino))
    assert path.read_bytes() == b'{"newer":true}\n'


def test_atomic_json_refuses_symlink_destination(tmp_path: Path) -> None:
    original = tmp_path / "original.json"
    original.write_text("{}\n", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(original)
    with pytest.raises(ValueError, match="symlink"):
        atomic_write_json(link, {"changed": True})
    assert original.read_text(encoding="utf-8") == "{}\n"


def test_atomic_json_refuses_symlink_ancestor(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    nested = outside / "nested"
    nested.mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        atomic_write_json(alias / "nested" / "data.json", {"changed": True})
    assert not (nested / "data.json").exists()


def test_atomic_json_rejects_hardlinked_target_and_accidental_replace(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    alias = tmp_path / "alias.json"
    path.write_text("{}\n", encoding="utf-8")
    os.link(path, alias)
    identity = path.stat()
    with pytest.raises(ValueError, match="hardlink"):
        atomic_write_json(path, {"changed": True}, expected_identity=(identity.st_dev, identity.st_ino))
    normal = tmp_path / "normal.json"
    normal.write_text("{}\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        atomic_write_json(normal, {"changed": True})
    assert path.read_text(encoding="utf-8") == alias.read_text(encoding="utf-8") == "{}\n"

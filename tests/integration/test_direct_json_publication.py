"""Native one-file publication safety without the retired JSON transaction journal."""

from __future__ import annotations

import json
from multiprocessing import Process, Queue
import os
from pathlib import Path
import stat
import time
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra import direct_json
from spec_dock.runtime.infra.direct_json import MetadataPublicationIncomplete, replace_existing_json
from spec_dock.runtime.infra.file_publication import publish_file

if TYPE_CHECKING:
    from collections.abc import Callable


def _replace(
    path: Path,
    data: dict[str, object],
    *,
    before_replace: Callable[[], object] = lambda: None,
) -> direct_json.PublishedJson:
    original = path.read_bytes()
    identity = path.stat()
    return replace_existing_json(
        path,
        data,
        expected_bytes=original,
        expected_identity=(identity.st_dev, identity.st_ino),
        staging_dir=path.parent / ".agent/staging",
        before_replace=before_replace,
        before_stage=lambda _: None,
    )


def test_metadata_replace_failure_keeps_previous_bytes_without_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    original = path.read_bytes()
    path.chmod(0o640)

    def fail_replace(*args: object, **kwargs: object) -> None:
        raise OSError("injected replacement failure")

    monkeypatch.setattr(direct_json.os, "replace", fail_replace)
    with pytest.raises(MetadataPublicationIncomplete, match="replacement failure") as captured:
        _replace(path, {"new": True})
    assert captured.value.published is None
    assert path.read_bytes() == original
    assert stat.S_IMODE(path.stat().st_mode) == 0o640
    assert len(list((tmp_path / ".agent/staging").glob(".stage-*"))) == 1
    assert not (tmp_path / ".specdock-json-transactions").exists()


def test_metadata_replace_preserves_actor_change_observed_before_replacement(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    competitor = tmp_path / "competitor.json"
    competitor.write_bytes(b'{"competitor":true}\n')

    def actor_change() -> None:
        competitor.replace(path)

    with pytest.raises(ValueError, match="input changed before replacement"):
        _replace(path, {"new": True}, before_replace=actor_change)
    assert path.read_bytes() == b'{"competitor":true}\n'
    assert list((tmp_path / ".agent/staging").iterdir()) == []
    assert not (tmp_path / ".specdock-json-transactions").exists()


def test_metadata_replace_error_after_effect_preserves_visible_bytes_and_reobserves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "state.json"
    path.write_bytes(b'{"original":true}\n')
    native_replace = direct_json.os.replace

    def effect_then_error(
        source: str, target: str, *, src_dir_fd: int | None = None, dst_dir_fd: int | None = None
    ) -> None:
        native_replace(source, target, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd)
        raise OSError("injected post-effect error")

    with monkeypatch.context() as patch:
        patch.setattr(direct_json.os, "replace", effect_then_error)
        with pytest.raises(MetadataPublicationIncomplete, match="post-effect") as captured:
            _replace(path, {"new": True})
    assert captured.value.published is None
    assert json.loads(path.read_bytes()) == {"new": True}
    observed = path.read_bytes()
    assert list((tmp_path / ".agent/staging").iterdir()) == []
    assert not (tmp_path / ".specdock-json-transactions").exists()

    # This is a new explicit operation after observation, not replay of an intent.
    published = _replace(path, {"newer": True})
    assert json.loads(published.payload) == {"newer": True}
    assert path.read_bytes() == published.payload
    assert path.read_bytes() != observed


def test_file_create_only_has_one_link_and_preserves_an_existing_destination(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    payload = b'{"created":true}\n'
    publish_file(path, payload, stage_name=".candidate", verify=lambda: None)
    assert path.stat().st_nlink == 1
    assert path.read_bytes() == payload
    assert not (tmp_path / ".candidate").exists()
    with pytest.raises(ValueError, match="already exists"):
        publish_file(path, b'{"replacement":true}\n', stage_name=".candidate", verify=lambda: None)
    assert path.read_bytes() == payload
    assert not (tmp_path / ".candidate").exists()


def _replace_then_hold(path_value: str, phase: str, ready: Queue[str]) -> None:
    path = Path(path_value)
    native_replace = direct_json.os.replace

    def pause() -> None:
        ready.put(phase)
        time.sleep(30)

    def replace_then_pause(
        src: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dst: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        native_replace(src, dst, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd)
        pause()

    if phase == "after":
        direct_json.os.replace = replace_then_pause
    _replace(path, {"new": True}, before_replace=pause if phase == "before" else lambda: None)


@pytest.mark.parametrize("phase", ["before", "after"])
def test_killed_metadata_replace_preserves_the_visible_boundary_without_journal(tmp_path: Path, phase: str) -> None:
    path = tmp_path / "state.json"
    original = b'{"original":true}\n'
    path.write_bytes(original)
    ready: Queue[str] = Queue()
    child = Process(target=_replace_then_hold, args=(str(path), phase, ready))
    child.start()
    try:
        assert ready.get(timeout=5) == phase
    finally:
        child.kill()
        child.join(timeout=5)
        ready.close()
        ready.join_thread()
    assert child.exitcode is not None and child.exitcode != 0
    stages = tuple((tmp_path / ".agent/staging").glob(".stage-*"))
    if phase == "before":
        assert path.read_bytes() == original
        assert len(stages) == 1
        assert json.loads(stages[0].read_bytes()) == {"new": True}
    else:
        assert json.loads(path.read_bytes()) == {"new": True}
        assert stages == ()
    assert not (tmp_path / ".specdock-json-transactions").exists()
    visible = path.read_bytes()
    retained_stages = {item: item.read_bytes() for item in stages}

    # A reader and a later explicit operation inspect current bytes; no old intent is resumed.
    published = _replace(path, {"explicit_new_operation": True})
    assert json.loads(published.payload) == {"explicit_new_operation": True}
    assert path.read_bytes() == published.payload
    assert path.read_bytes() != visible
    assert {item: item.read_bytes() for item in stages} == retained_stages


def test_metadata_replace_refuses_symlink_destination(tmp_path: Path) -> None:
    original = tmp_path / "original.json"
    original.write_text("{}\n", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(original)
    with pytest.raises(ValueError, match="symlink"):
        _replace(link, {"changed": True})
    assert original.read_text(encoding="utf-8") == "{}\n"


def test_metadata_replace_refuses_symlink_ancestor(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    nested = outside / "nested"
    nested.mkdir(parents=True)
    target = nested / "data.json"
    target.write_text("{}\n", encoding="utf-8")
    alias = tmp_path / "alias"
    alias.symlink_to(outside, target_is_directory=True)
    with pytest.raises(OSError):
        _replace(alias / "nested/data.json", {"changed": True})
    assert target.read_text(encoding="utf-8") == "{}\n"
    assert tuple(nested.iterdir()) == (target,)


def test_metadata_replace_rejects_hardlinked_target(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    alias = tmp_path / "alias.json"
    path.write_text("{}\n", encoding="utf-8")
    os.link(path, alias)
    with pytest.raises(ValueError, match=r"hardlink|single-link"):
        _replace(path, {"changed": True})
    assert path.read_text(encoding="utf-8") == alias.read_text(encoding="utf-8") == "{}\n"
    assert path.stat().st_nlink == 2

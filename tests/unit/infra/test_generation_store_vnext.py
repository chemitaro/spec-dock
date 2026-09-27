"""Published generation pointer remains the authority across staged failures."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.infra import generation_store  # noqa: E402


def test_generation_publish_and_read_immutable_bytes(tmp_path: Path) -> None:
    specdock = tmp_path / "spec-dock"
    specdock.mkdir()
    first = generation_store.publish_generation(
        specdock, files={"index.json": b'{"nodes":[]}'}, source="cache", valid=True, selection_revision=0
    )
    assert generation_store.load_generation(specdock) == first
    second = generation_store.publish_generation(
        specdock,
        files={"index.json": b'{"nodes":[1]}'},
        source="github",
        valid=False,
        selection_revision=1,
        warnings=("github_partial",),
    )
    assert generation_store.load_generation(specdock) == second
    assert (first.path / "index.json").read_bytes() == b'{"nodes":[]}'


def test_failure_before_pointer_retains_previous_generation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specdock = tmp_path / "spec-dock"
    specdock.mkdir()
    first = generation_store.publish_generation(
        specdock, files={"index.json": b"old"}, source="cache", valid=True, selection_revision=0
    )

    def fail_pointer(*_args: object, **_kwargs: object) -> None:
        raise OSError("injected pointer failure")

    monkeypatch.setattr(generation_store, "atomic_write_json", fail_pointer)
    with pytest.raises(OSError, match="injected pointer failure"):
        generation_store.publish_generation(
            specdock, files={"index.json": b"new"}, source="cache", valid=True, selection_revision=0
        )
    assert generation_store.load_generation(specdock) == first


def test_corrupt_pointer_and_redirected_generation_are_rejected(tmp_path: Path) -> None:
    specdock = tmp_path / "spec-dock"
    specdock.mkdir()
    generation_store.publish_generation(
        specdock, files={"index.json": b"old"}, source="cache", valid=True, selection_revision=0
    )
    (specdock / ".agent" / "generation.json").write_text('{"schema_version":1,"generation_id":"../x"}')
    with pytest.raises(ValueError, match="pointer ID"):
        generation_store.load_generation(specdock)

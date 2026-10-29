"""Canonical-mode `artifact create` and `artifact import file` (iss-00432): the catalog, under its lock."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 1234, "葉の作業", parent=2)
    return world


def test_create_publishes_into_the_flat_scope_directory_from_main_and_a_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.run(
        "artifact", "create", "--scope", "iss-1234", "--type", "research", "--title", "Look Around"
    )
    assert code == 0, payload
    artifact = payload["data"]["result"]["artifact"]
    assert artifact["path"].startswith("spec-dock/initiatives/01000-01999/iss-01234/artifacts/")
    assert artifact["path"].endswith("-research-look-around.md") and artifact["scope_id"] == "iss-01234"
    published = world.main / artifact["path"]
    text = published.read_text(encoding="utf-8")
    assert "Look Around" in text and "<SCOPE_ID>" not in text and "<ARTIFACT_ID>" not in text
    (changeset,) = world.changesets()
    assert changeset["paths"] == [artifact["path"].removeprefix("spec-dock/initiatives/")]
    assert world.writes() == []
    source = tmp_path / "evidence.txt"
    source.write_text("measured\n", encoding="utf-8")
    worktree = world.worktree("wt")
    code, payload = world.run("artifact", "import", "file", str(source), "--scope", "iss-01234", checkout=worktree)
    assert code == 0, payload
    imported = payload["data"]["result"]["artifact"]["path"]
    assert imported.startswith("spec-dock/initiatives/01000-01999/iss-01234/artifacts/") and imported.endswith(
        "evidence.txt"
    )
    assert (worktree / imported).read_text(encoding="utf-8") == "measured\n"
    assert (world.catalog / imported.removeprefix("spec-dock/initiatives/")).is_file()
    assert len(world.changesets()) == 2
    code, listed = world.run("artifact", "list", "--scope", "iss-01234")
    assert code == 0 and len(listed["data"]["result"]["items"]) == 2


def test_root_artifacts_stay_in_the_checkout_without_a_changeset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.run("artifact", "create", "--scope", "@root", "--type", "blank", "--title", "Notes")
    assert code == 0, payload
    path = payload["data"]["result"]["artifact"]["path"]
    assert path.startswith("spec-dock/artifacts/") and (world.main / path).is_file()
    assert world.changesets() == []


def test_a_missing_directory_or_a_kind_change_stops_before_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("issue", 7, "no files", parent=2, directory=False)
    code, payload = world.run("artifact", "create", "--scope", "iss-00007", "--type", "blank", "--title", "X")
    assert (code, payload["error"]["code"]) == (4, "LOCAL_TARGET_NOT_FOUND")
    world.edit(lambda fake: setattr(fake.issue(1234), "labels", ["spec-dock:epic"]))
    world.age_probe()
    world.edit(lambda fake: fake.touch(1234))
    code, payload = world.run("artifact", "create", "--scope", "epic-01234", "--type", "blank", "--title", "X")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_KIND_CHANGED")
    assert world.changesets() == []

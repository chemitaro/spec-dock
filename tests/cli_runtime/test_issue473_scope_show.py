"""`scope show --json` returns the assurance level of requirement.cue (iss-00473 AC-01; R-C6 of epic-00425)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.canonical_scopes import CanonicalWorld
from tests.support.cue import cue_executable
from tests.support.cue_scopes import hide_cue, place_sample

if TYPE_CHECKING:
    from pathlib import Path

UNSET = {"level": None, "reason": None, "source": "unset", "problem": None}


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    cue_executable()
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2, documents=())
    world.scope("issue", 4, "Markdown leaf", parent=2)
    place_sample(world.catalog / world.relative("issue", 3), "issue-strict-complete")
    return world


def requirement(world: CanonicalWorld) -> Path:
    return world.catalog / world.relative("issue", 3) / "requirement.cue"


def assurance(world: CanonicalWorld, target: str, *options: str) -> dict[str, object]:
    code, payload = world.run("scope", "show", target, *options)
    assert code == 0, payload
    assert payload["data"]["result"]["scope"]["id"]  # the rest of the result is unchanged
    return payload["data"]["result"]["assurance"]


def test_a_cue_scope_returns_its_level_and_reason(world: CanonicalWorld) -> None:
    assert assurance(world, "iss-3") == {
        "level": "strict",
        "reason": "公開の CLI の契約を変える",
        "source": "cue",
        "problem": None,
    }


def test_markdown_scopes_and_a_missing_directory_are_unset(world: CanonicalWorld) -> None:
    assert assurance(world, "iss-4") == UNSET
    assert assurance(world, "epic-2") == UNSET
    world.scope("issue", 5, parent=2, directory=False)
    world.age_probe()
    assert assurance(world, "iss-5") == UNSET


@pytest.mark.parametrize(
    ("old", "new", "code"),
    [
        ("assurance: {", "assurance: {{", "CUE_INVALID"),
        ("assurance: {", "other: {", "ASSURANCE_UNREADABLE"),
        ('"strict"', '"high"', "ASSURANCE_UNREADABLE"),
        ('reason: "公開の CLI の契約を変える"', 'reason: "  "', "ASSURANCE_UNREADABLE"),
    ],
    ids=["syntax", "no-assurance", "bad-level", "blank-reason"],
)
def test_each_unreadable_level_is_reported_and_show_succeeds(
    world: CanonicalWorld, old: str, new: str, code: str
) -> None:
    path = requirement(world)
    path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
    found = assurance(world, "iss-3")
    assert (found["level"], found["reason"], found["source"]) == (None, None, "unreadable")
    assert found["problem"]["code"] == code  # type: ignore[index]


def test_both_formats_and_a_missing_cue_are_unreadable(world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    assert assurance(world, "iss-3")["problem"] == {"code": "CUE_NOT_FOUND", "message": "cue is not on PATH"}
    assert assurance(world, "iss-4") == UNSET
    (requirement(world).parent / "requirement.md").write_text("# r\n", encoding="utf-8")
    assert assurance(world, "iss-3")["problem"]["code"] == "SCOPE_FORMAT_CONFLICT"  # type: ignore[index]


def test_it_reads_without_reaching_github(world: CanonicalWorld) -> None:
    assurance(world, "iss-3")
    world.age_probe(4000)
    world.edit(lambda fake: fake.inject(status=503, times=50))
    assert assurance(world, "iss-3")["source"] == "cue"
    assert assurance(world, "iss-3", "--offline")["source"] == "cue"

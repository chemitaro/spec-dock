"""Pull request state in the version-2 structure snapshot (iss-00537): the sync reads it, commands never do."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.infra import github_snapshot
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    world.scope("issue", 4, "Base", parent=2)

    def relations(fake: Any) -> None:
        fake.block(3, by=4)
        fake.add_pull_request(40, "chemitaro/iss-00003", checks="FAILURE")

    world.edit(relations)
    return world


def _snapshot_path(world: CanonicalWorld) -> Path:
    return world.state / "spec-dock/github/github.com/example/repo/snapshot.json"


def _pull_queries(world: CanonicalWorld) -> int:
    return sum("pullRequests(" in str(request.payload) for request in world.fake().graphql_requests())


def _step_seven(world: CanonicalWorld) -> None:
    """Step 7 of the periodic sync for this repository, as the resident cycle runs it."""
    from spec_dock.runtime.application.canonical_sync import SyncContext, refresh_structures
    from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry

    entry = RegistryEntry(str(world.catalog), str(world.main), "github.com/example/repo", "git", "2026-10-26T00:00:00Z")
    (result,) = refresh_structures([entry], SyncContext(world.state / "spec-dock"))
    assert result.probe != "failed", result


def _check(world: CanonicalWorld, scope: str) -> dict[str, Any]:
    code, payload = world.run("dependency", "check", scope)
    assert code == 0, payload
    result = dict(payload["data"]["result"])
    result.pop("snapshot", None)
    return result


def test_the_sync_writes_pull_requests_and_commands_never_ask_for_them(world: CanonicalWorld) -> None:
    for argv in (
        ("dependency", "check", "iss-00003"),
        ("scope", "show", "iss-00003"),
        ("dependency", "list", "iss-00003"),
    ):
        code, payload = world.run(*argv)
        assert code == 0, payload
    assert _pull_queries(world) == 0
    assert json.loads(_snapshot_path(world).read_text(encoding="utf-8"))["pull_requests_fetched_at"] is None
    _step_seven(world)
    assert _pull_queries(world) == 1
    stored = json.loads(_snapshot_path(world).read_text(encoding="utf-8"))
    assert stored["version"] == 2 and stored["pull_requests"]["40"]["checks"] == "failure"


def test_dependency_check_is_the_same_on_version_one_and_version_two(world: CanonicalWorld) -> None:
    before = {scope: _check(world, scope) for scope in ("iss-00003", "iss-00004", "epic-00002")}
    path = _snapshot_path(world)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["pull_requests"] = {
        "40": {
            "number": 40,
            "state": "open",
            "is_draft": False,
            "head_ref_name": "chemitaro/iss-00003",
            "mergeable": "conflicting",
            "checks": "failure",
            "created_at": "2026-10-25T00:00:00Z",
            "merged_at": None,
            "closed_at": None,
            "url": "https://github.com/example/repo/pull/40",
        }
    }
    document["pull_requests_fetched_at"] = document["fetched_at"]
    path.write_text(json.dumps(document), encoding="utf-8")
    github_snapshot.clear_memory()
    assert {scope: _check(world, scope) for scope in before} == before
    structure_reads = len(world.fake().graphql_requests())
    version_one = {key: value for key, value in document.items() if not key.startswith("pull_requests")}
    version_one["version"] = 1
    path.write_text(json.dumps(version_one), encoding="utf-8")
    github_snapshot.clear_memory()
    assert {scope: _check(world, scope) for scope in before} == before
    assert len(world.fake().graphql_requests()) == structure_reads  # a version-1 file is read, not refetched
    assert _pull_queries(world) == 0

"""Canonical mode end to end on two clones (iss-00436; Epic AC-02, AC-13, AC-16, AC-18 on injected environments).

Clone A links, creates a Scope with a Japanese title and edits it; its sync pushes. Clone B links, syncs, reads
A's edit, starts work, edits and finishes; the finish waits for B's push before closing the Issue on GitHub.
Both clones push to one temporary bare remote and share one fake GitHub repository. The periodic job is the
recording fake of the injected Linux environment (systemd or the resident loop); its kick runs one sync.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.application import canonical_scopes, canonical_work, canonical_writes
from spec_dock.runtime.infra import github_snapshot, github_structure, runtime_environment
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.canonical_repo import bare_remote, clone, environment, git, isolate_user_state
from tests.support.canonical_scopes import REPOSITORY
from tests.support.canonical_writes import WriteClock, seeded_files
from tests.support.fake_github import FakeGithub, install_fake_gh

if TYPE_CHECKING:
    from tests.support.canonical_sync import FakeScheduler
    from tests.support.fake_github import FakeGhExecutable

ENVIRONMENTS = {
    "systemd": {"systemd_present": True, "systemd_user": True, "linger": True},
    "loop": {"systemd_present": False, "systemd_user": False, "linger": None},
}


class _Clock:
    def __init__(self) -> None:
        self.offset = 0.0

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=self.offset)

    def monotonic(self) -> float:
        return self.offset

    def sleep(self, seconds: float) -> None:
        self.offset += seconds


class Clones:
    def __init__(self, tmp_path: Path, capsys: pytest.CaptureFixture[str], gh: FakeGhExecutable) -> None:
        self.capsys = capsys
        self.gh = gh
        self.remote = bare_remote(tmp_path / "remote.git", files=seeded_files())
        self.a = clone(self.remote, tmp_path / "a")
        self.b = clone(self.remote, tmp_path / "b")

    def run(self, checkout: Path, *argv: str) -> tuple[int, dict[str, Any]]:
        self.capsys.readouterr()
        code = main(["--project", str(checkout), *argv, "--json"])
        return code, json.loads(self.capsys.readouterr().out)

    def ok(self, checkout: Path, *argv: str) -> dict[str, Any]:
        code, payload = self.run(checkout, *argv)
        assert code == 0, (argv, payload)
        return payload

    def specs(self, checkout: Path) -> Path:
        return checkout / "spec-dock/initiatives"

    def fake(self) -> FakeGithub:
        return self.gh.load()

    def full_reads(self) -> int:
        """GraphQL requests: the full structure refresh (the change check is a conditional REST list)."""
        return sum(1 for item in self.fake().requests if item.endpoint == "graphql")


@pytest.mark.parametrize("kind", sorted(ENVIRONMENTS))
def test_link_create_edit_sync_start_and_finish_across_two_clones(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    periodic_jobs: dict[str, FakeScheduler],
    kind: str,
) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    linux = replace(environment(), system="linux", **ENVIRONMENTS[kind])
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: linux)
    github_snapshot.clear_memory()
    monkeypatch.setattr(canonical_writes, "WRITE_CLOCK", WriteClock())
    save_clock = _Clock()
    monkeypatch.setattr(canonical_work, "SAVE_CLOCK", save_clock)
    repository = GithubRepository.parse(REPOSITORY)
    for module in (github_structure, canonical_writes, canonical_scopes):
        monkeypatch.setattr(module, "repository_for_checkout", lambda root, *, timeout: repository)
    clones = Clones(tmp_path, capsys, install_fake_gh(tmp_path, monkeypatch, FakeGithub(REPOSITORY)))
    a, b = clones.a, clones.b

    # A: link (registers the injected periodic job), then create a Scope chain with Japanese titles.
    linked = clones.ok(a, "canonical", "link")
    assert ("ensure", kind) in periodic_jobs[kind].calls, linked
    assert set(periodic_jobs) == {kind}
    init = clones.ok(a, "scope", "create", "initiative", "--backend", "github", "--title", "仕様の集約", "--yes")
    init_id = init["data"]["result"]["scope"]["id"]
    epic_id = clones.ok(
        a, "scope", "create", "epic", "--backend", "github", "--parent", init_id, "--title", "カタログ", "--yes"
    )["data"]["result"]["scope"]["id"]
    issue = clones.ok(
        a, "scope", "create", "issue", "--backend", "github", "--parent", epic_id, "--title", "横断の確かめ", "--yes"
    )
    issue_id = issue["data"]["result"]["scope"]["id"]
    number = int(issue_id.split("-")[1])
    shown = clones.ok(a, "scope", "show", issue_id)
    path = shown["data"]["result"]["scope"]["path"]
    assert path == f"spec-dock/initiatives/00000-00999/{issue_id}"  # flat, bucketed, named by the ID only
    relative = Path(path).relative_to("spec-dock/initiatives")

    # A: edit the Issue's design like any file; the next sync saves and pushes it.
    (clones.specs(a) / relative / "design.md").write_text("# 設計\n\nA が書いた\n", encoding="utf-8")
    synced = clones.ok(a, "canonical", "sync")
    assert synced["data"]["catalogs"][0]["pushed"] is True, synced

    # B: link and sync; A's Scope and edit are readable, and the title comes from GitHub.
    clones.ok(b, "canonical", "link")
    clones.ok(b, "canonical", "sync")
    assert "A が書いた" in (clones.specs(b) / relative / "design.md").read_text(encoding="utf-8")
    reads = clones.full_reads()
    assert reads > 0  # the snapshot was built by a full read before
    shown = clones.ok(b, "scope", "show", issue_id)
    listed = clones.ok(b, "scope", "list")
    assert clones.full_reads() == reads  # AC-16: a fresh snapshot is reused, no full refresh
    assert shown["data"]["result"]["scope"]["title"] == "横断の確かめ"
    assert issue_id in json.dumps(listed["data"], ensure_ascii=False)

    # B: start work on the default branch name <ID>, edit, and finish after the save reached the remote.
    started = clones.ok(b, "work", "start", issue_id, "--base", "origin/main", "--yes")
    assert git(b, "branch", "--show-current") == issue_id, started
    (clones.specs(b) / relative / "plan.md").write_text("# 計画\n\nB が仕上げた\n", encoding="utf-8")

    def kick() -> None:
        code, payload = clones.run(b, "canonical", "sync")
        assert code == 0, payload

    periodic_jobs[kind].on_kick = kick
    periodic_jobs[kind].simulate_run = False
    finished = clones.ok(b, "work", "finish", issue_id, "--yes")
    assert finished["data"]["completed"] is True, finished
    assert periodic_jobs[kind].calls[-1] == ("kick", kind)  # finish asked the job for a cycle now
    pushed = git(clones.remote, "show", f"spec-dock/canonical:{relative.as_posix()}/plan.md")
    assert "B が仕上げた" in pushed
    closed = clones.fake().issue(number)
    assert (closed.state, closed.state_reason) == ("closed", "completed")
    assert clones.ok(b, "active", "show")["data"]["selection"]["status"] == "empty"

    # A: the next sync brings B's edit.
    clones.ok(a, "canonical", "sync")
    assert "B が仕上げた" in (clones.specs(a) / relative / "plan.md").read_text(encoding="utf-8")

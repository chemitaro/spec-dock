"""The Scope detail reading and the screen fields of the dashboard JSON (iss-00531 T-01〜T-05)."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application.contracts import GitWorktreeRecord
from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_scope_details import read_scope_details
from spec_dock.runtime.application.dashboard_site import DashboardSite, SiteRepository
from spec_dock.runtime.application.scope_check import AssuranceReading
from spec_dock.runtime.domain.canonical_structure import ExternalIssue
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.dashboard import NOW, closed, node, pr, prs, snapshot
from tests.support.dashboard_site import register, scope_dir, write_snapshot

if TYPE_CHECKING:
    from spec_dock.runtime.domain.canonical_structure import StructureSnapshot

HOST = "127.0.0.1:47800"
REPO = GithubRepository("o", "r")


def _structure() -> StructureSnapshot:
    """Epic #2 waits for #7 (closed) and #90 (outside); its Issues wait on each other. Epic #10 has a doing
    Issue with a draft PR and two ready Issues, one of which #13 waits for."""
    structure = snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1, blocked_by=(7, 90)),
        node(3, "issue", parent=2, title="Blocked by the Epic"),
        node(4, "issue", parent=2, blocked_by=(3,), title="Waits for #3"),
        node(5, "issue", parent=2, blocked_by=(4,), title="Waits for #4"),
        node(6, "issue", parent=2, in_progress=True, title="Doing with PR"),
        node(10, "epic", parent=1),
        closed(7, "issue", parent=10, title="Closed prerequisite"),
        node(8, "issue", parent=10, in_progress=True, title="Draft PR"),
        node(11, "issue", parent=10, title="Ready alone"),
        node(12, "issue", parent=10, title="Ready and waited for"),
        node(13, "issue", parent=10, blocked_by=(12,), title="Waits for #12"),
        external=(ExternalIssue(90, "Outside <b>issue</b>", "open"),),
    )
    structure = prs(structure, pr(40, "iss-00006", checks="failure"), pr(41, "u/iss-00008", draft=True))
    return replace(structure, repository="github.com/o/r")


class Env:
    def __init__(self, tmp_path: Path, structure: StructureSnapshot | None = None) -> None:
        self.state = tmp_path / "state"
        self.catalog = tmp_path / "r" / "spec-dock" / ".canonical"
        register(self.state, "github.com/o/r", self.catalog)
        write_snapshot(self.state, structure or _structure())
        self.site = DashboardSite(self.state, now=lambda: NOW)
        self.http = DashboardHttp(
            self.site,
            hosts=("127.0.0.1",),
            port=47800,
            embed_hosts=("127.0.0.1",),
            local_url="http://127.0.0.1:47800/",
            version="0.5.1",
            started_at="2026-11-04T11:00:00Z",
            now=lambda: NOW,
        )

    def json(self, path: str) -> tuple[int, Any]:
        response = self.http.handle(Request("GET", path, {}, {"host": HOST}))
        return response.status, json.loads(response.body)


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def _no_assurance(directory: Path | None, *, timeout: float) -> AssuranceReading:
    return AssuranceReading(None, None, "unset")


def _no_worktrees(root: Path, *, timeout: float) -> list[GitWorktreeRecord]:
    return []


# --- Structure: rank and in_progress (T-01) ----------------------------------------------------------------


def test_structure_rank_follows_the_recommended_order(env: Env) -> None:
    status, body = env.json("/api/v1/r/github.com/o/r/structure")
    assert status == 200
    ranked = [item["id"] for item in sorted(body["scopes"], key=lambda item: item["rank"])]
    # needs fix (#6 CI failed), then doing (#8 draft), then ready with the most waiting (#12) first,
    # then blocked (#3, fewest waits); closed last.
    order = [ranked.index(item) for item in ("iss-00006", "iss-00008", "iss-00012", "iss-00011", "iss-00003")]
    assert order == sorted(order)
    assert ranked[-1] == "iss-00007"
    assert sorted(item["rank"] for item in body["scopes"]) == list(range(len(body["scopes"])))
    by_id = {item["id"]: item for item in body["scopes"]}
    assert by_id["iss-00006"]["in_progress"] is True and by_id["iss-00003"]["in_progress"] is False
    assert by_id["iss-00006"]["lane"] == "awaiting_merge" and by_id["iss-00008"]["lane"] == "doing"


# --- Scope JSON: dependencies (T-02) and details (T-05) -----------------------------------------------------


def test_scope_dependencies_split_own_inherited_and_outside(env: Env) -> None:
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/iss-00004")
    assert status == 200
    assert body["scope"]["rank"] >= 0
    waits = body["dependencies"]["waits_for"]
    assert [(item["number"], item["inherited"], item["declared_by"]) for item in waits] == [
        (3, False, "iss-00004"),
        (7, True, "epic-00002"),
        (90, True, "epic-00002"),
    ]
    outside = waits[2]
    assert outside["scope_id"] is None and outside["external"] is True and outside["open"] is True
    assert outside["title"] == "Outside <b>issue</b>"  # escaped by the screen, not here
    assert waits[1]["state"] == "done" and waits[1]["open"] is False
    assert body["dependencies"]["waited_by"] == ["iss-00005"]


def test_scope_document_carries_the_details(env: Env) -> None:
    directory = scope_dir(env.catalog, "iss-00004")
    (directory / "plan.cue").write_text("package spec\n")
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/iss-00004")
    assert status == 200
    details = body["details"]
    assert details["catalog"] == "ok"
    assert {item["key"]: item["exists"] for item in details["documents"]}["plan"] is True


def test_unknown_scope_is_404_without_reading_details(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    import spec_dock.runtime.application.dashboard_http as http

    def boom(*args: object, **kwargs: object) -> dict[str, object]:
        raise AssertionError("details read for an unknown Scope")

    monkeypatch.setattr(http, "read_scope_details", boom)
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/iss-00099")
    assert status == 404 and body["error"]["code"] == "DASHBOARD_SCOPE_UNKNOWN"


def test_reading_details_writes_nothing(env: Env) -> None:
    directory = scope_dir(env.catalog, "iss-00004")
    (directory / "explanation.html").write_text("<p>x</p>")
    before = sorted((path, path.stat().st_mtime_ns) for path in env.catalog.rglob("*"))
    state_before = sorted((path, path.stat().st_mtime_ns) for path in env.state.rglob("*"))
    env.json("/api/v1/r/github.com/o/r/scopes/iss-00004")
    assert sorted((path, path.stat().st_mtime_ns) for path in env.catalog.rglob("*")) == before
    assert sorted((path, path.stat().st_mtime_ns) for path in env.state.rglob("*")) == state_before


# --- Catalog, documents and Artifacts (T-03) ----------------------------------------------------------------


def _site(catalog: Path | None, *, problem: str | None = None) -> SiteRepository:
    return SiteRepository(REPO, catalog, (str(catalog),) if catalog else ("a", "b"), problem)  # type: ignore[arg-type]


def _read(site: SiteRepository, scope_id: str = "iss-00004", **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("assurance_reader", _no_assurance)
    kwargs.setdefault("worktree_lister", _no_worktrees)
    return read_scope_details(site, scope_id, **kwargs)


def test_catalog_states_name_the_next_step(tmp_path: Path) -> None:
    ambiguous = _read(_site(None, problem="ambiguous"))
    assert ambiguous["catalog"] == "ambiguous" and "spec-dock dashboard list" in ambiguous["next_steps"]
    missing = _read(_site(tmp_path / "nowhere"))
    assert missing["catalog"] == "missing" and missing["next_steps"][0] == "spec-dock canonical link"
    catalog = tmp_path / "c"
    catalog.mkdir()
    no_scope = _read(_site(catalog))
    assert no_scope["catalog"] == "scope_missing" and no_scope["documents"] == [] and no_scope["artifacts"] == []
    assert no_scope["worktrees"]["status"] == "ok"  # the catalog exists, so git can still be asked


def test_documents_report_presence_without_following_links(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    directory = scope_dir(catalog, "iss-00004")
    (directory / "requirement.cue").write_text("x")
    (directory / "design.md").write_text("x")  # an older Markdown Scope
    (tmp_path / "elsewhere.cue").write_text("x")
    (directory / "plan.cue").symlink_to(tmp_path / "elsewhere.cue")
    (directory / "explanation.html").write_text("x")
    details = _read(_site(catalog))
    assert details["catalog"] == "ok" and details["next_steps"] == []
    documents = {item["key"]: item for item in details["documents"]}
    assert [item["key"] for item in details["documents"]] == ["requirement", "design", "plan", "explanation", "report"]
    assert documents["requirement"] == {"key": "requirement", "name": "requirement.cue", "exists": True, "href": None}
    assert documents["design"]["name"] == "design.md" and documents["design"]["exists"] is True
    assert documents["plan"]["exists"] is False  # a link is not a regular file
    assert documents["explanation"]["href"] == "/r/github.com/o/r/files/iss-00004/explanation.html"
    assert documents["report"] == {"key": "report", "name": "report.md", "exists": False, "href": None}


def test_artifacts_list_regular_files_with_escaped_links(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    artifacts = scope_dir(catalog, "iss-00004") / "artifacts"
    artifacts.mkdir()
    (artifacts / "b note.md").write_text("hello")
    (artifacts / "a--page.html").write_text("<p>x</p>")
    (artifacts / ".hidden").write_text("x")
    (artifacts / "rules.md").symlink_to(artifacts / "b note.md")
    (artifacts / "dir").mkdir()
    details = _read(_site(catalog))
    names = [item["name"] for item in details["artifacts"]]
    assert names == ["a--page.html", "b note.md"]
    first, second = details["artifacts"]
    assert first["html"] is True and second["html"] is False and second["size"] == 5
    assert second["href"] == "/r/github.com/o/r/files/iss-00004/artifacts/b%20note.md"
    assert second["modified_at"].endswith("Z") and details["artifacts_truncated"] is False


def test_artifacts_stop_at_the_limit(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    artifacts = scope_dir(catalog, "iss-00004") / "artifacts"
    artifacts.mkdir()
    for index in range(5):
        (artifacts / f"f{index}.txt").write_text("x")
    details = _read(_site(catalog), artifact_limit=3)
    assert len(details["artifacts"]) == 3 and details["artifacts_truncated"] is True


# --- Assurance and worktrees (T-04) -------------------------------------------------------------------------


def test_assurance_is_read_only_for_a_cue_scope(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    directory = scope_dir(catalog, "iss-00004")
    calls: list[Path | None] = []

    def reader(path: Path | None, *, timeout: float) -> AssuranceReading:
        calls.append(path)
        assert timeout <= 3.0
        return AssuranceReading("standard", "because", "cue")

    assert _read(_site(catalog), assurance_reader=reader)["assurance"]["source"] == "unset" and calls == []
    (directory / "requirement.cue").write_text("x")
    assurance = _read(_site(catalog), assurance_reader=reader)["assurance"]
    assert assurance == {"level": "standard", "source": "cue", "problem": None} and calls == [directory]


def test_assurance_failures_stay_in_their_field(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    (scope_dir(catalog, "iss-00004") / "requirement.cue").write_text("x")

    def broken(path: Path | None, *, timeout: float) -> AssuranceReading:
        raise subprocess.TimeoutExpired("cue", timeout)

    details = _read(_site(catalog), assurance_reader=broken)
    assert details["assurance"]["source"] == "unreadable" and details["catalog"] == "ok"


def test_worktrees_keep_only_branches_naming_the_scope(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    scope_dir(catalog, "iss-00004")
    seen: list[float] = []

    def lister(root: Path, *, timeout: float) -> list[GitWorktreeRecord]:
        seen.append(timeout)
        assert root == catalog
        return [
            GitWorktreeRecord(Path("/w/main"), "a", "main"),
            GitWorktreeRecord(Path("/w/iss-00004"), "b", "chemitaro/iss-00004"),
            GitWorktreeRecord(Path("/w/iss-00004-x"), "c", "iss-00004-extra"),
            GitWorktreeRecord(Path("/w/iss-00041"), "d", "iss-00041"),
            GitWorktreeRecord(Path("/w/detached"), "e", None, detached=True),
        ]

    worktrees = _read(_site(catalog), worktree_lister=lister)["worktrees"]
    assert worktrees == {
        "status": "ok",
        "items": [
            {"path": "/w/iss-00004", "branch": "chemitaro/iss-00004"},
            {"path": "/w/iss-00004-x", "branch": "iss-00004-extra"},
        ],
    }
    assert seen and seen[0] <= 3.0


def test_worktree_failures_stay_in_their_field(tmp_path: Path) -> None:
    catalog = tmp_path / "c"
    scope_dir(catalog, "iss-00004")

    def failing(root: Path, *, timeout: float) -> list[GitWorktreeRecord]:
        raise GitProcessError(("git",), b"fatal", 128)

    details = _read(_site(catalog), worktree_lister=failing)
    assert details["worktrees"] == {"status": "unreadable", "items": []} and details["catalog"] == "ok"
    assert _read(_site(None, problem="ambiguous"))["worktrees"]["status"] == "unreadable"


def test_real_git_worktree_listing(tmp_path: Path) -> None:
    main = tmp_path / "main"
    subprocess.run(["git", "init", "-q", "-b", "main", str(main)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(main),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@e",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "x",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-q", "-b", "u/iss-00004", str(tmp_path / "wt")], check=True
    )
    catalog = main / "spec-dock" / ".canonical"
    scope_dir(catalog, "iss-00004")
    details: dict[str, Any] = read_scope_details(_site(catalog), "iss-00004", assurance_reader=_no_assurance)
    assert details["worktrees"]["status"] == "ok"
    assert [item["branch"] for item in details["worktrees"]["items"]] == ["u/iss-00004"]


def test_open_child_stages_leave_closed_children_out(env: Env) -> None:
    status, body = env.json("/api/v1/r/github.com/o/r/scopes/epic-00010")
    assert status == 200
    # #13 waits for #12 (open), so it is stage 2; the closed #7 is in no open stage.
    stages = body["open_child_stages"]["stages"]
    assert stages[0] and "iss-00013" in stages[1]
    assert all("iss-00007" not in stage for stage in stages)
    assert any("iss-00007" in stage for stage in body["child_stages"]["stages"])

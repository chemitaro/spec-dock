"""migrate.py register, verify and undo against the fake GitHub (AC-435-06, 07, 08, 17, AC-456-01, 02)."""

from __future__ import annotations

import itertools
import json
from typing import TYPE_CHECKING

from tests.support.migration_repo import build_legacy, snapshot

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

    from tests.support.fake_github import FakeGithub
    from tests.support.migration_repo import Legacy


def _model(fake: FakeGithub) -> dict:
    """The GitHub state register may change: labels, bodies, parents, dependencies, states."""
    return {
        "labels": sorted(fake.labels),
        "issues": {
            number: (
                issue.title,
                issue.body,
                issue.state,
                sorted(issue.labels),
                issue.parent,
                sorted(map(tuple, issue.blocked_by)),
            )
            for (_, number), issue in sorted(fake.issues.items())
        },
    }


def test_register_adds_structure_maps_local_scopes_and_verify_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    before = snapshot(legacy)
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    after = snapshot(legacy)
    assert after["refs"] == before["refs"] and after["status"] == before["status"]  # repository files unchanged
    fake = legacy.github
    assert set(fake.labels) >= {"spec-dock:initiative", "spec-dock:epic", "spec-dock:issue"}
    assert fake.labels["spec-dock:epic"]["color"] == "1d76db"
    created = fake.issue(40)
    assert created.title == "Architecture" and created.labels == ["spec-dock:initiative"]
    assert created.body == ""
    assert fake.issue(31).labels == [] and fake.issue(31).state == "closed"  # the unrelated Issue stays untouched
    assert fake.issue(3).body == "Gamma body."  # register never writes a body
    assert not [r for r in fake.writes() if r.method == "PATCH"]
    creation = next(r for r in fake.writes() if r.endpoint == "repos/example/repo/issues")
    assert creation.payload == {"title": "Architecture", "labels": ["spec-dock:initiative"]}
    assert fake.issue(3).parent == ["example/repo", 2]
    assert fake.issue(5).parent == ["example/repo", 39]
    assert fake.issue(3).blocked_by == [["example/repo", 4]]
    assert fake.issue(39).labels == ["spec-dock:initiative"]
    idmap = json.loads((legacy.records / "idmap.json").read_text())["entries"]
    assert idmap == {
        "init-local-00002": {"id": "init-00039", "number": 39, "how": "existing"},
        "init-local-00003": {"id": "init-00040", "number": 40, "how": "created"},
    }
    issue_ids = {issue.id for issue in fake.issues.values()}
    for request in fake.writes():
        payload = request.payload
        assert isinstance(payload, dict)
        if request.endpoint.endswith("/sub_issues"):
            assert payload["sub_issue_id"] in issue_ids  # the Issue id, never its number
            assert payload["replace_parent"] is False
        if request.endpoint.endswith("/blocked_by"):
            assert payload["issue_id"] == fake.issue_id(4)
    code, result = legacy.run("verify")
    assert code == 0, result
    assert result["data"]["mismatches"] == []
    writes = len(fake.writes())
    code, result = legacy.run("register", apply=True)
    assert code == 0 and len(fake.writes()) == writes  # nothing left to send


def test_an_interrupted_register_resumes_without_duplicates_and_undo_restores_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    fake.add_issue(60, title="Labelled before", labels=["spec-dock:issue"])
    fake.issues.pop(("example/repo", 60))  # keep the pre-existing label definition only
    original = _model(fake)
    fake.inject(status=502, method="POST", endpoint="repos/example/repo/issues/2/labels", times=1)
    code, result = legacy.run("register", apply=True)
    assert code == 3 and result["status"] == "stopped"
    assert any("register --apply again" in step for step in result["next_steps"])
    first = [(r.method, r.endpoint, json.dumps(r.payload, sort_keys=True)) for r in fake.writes() if r.status < 400]
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    second = [(r.method, r.endpoint, json.dumps(r.payload, sort_keys=True)) for r in fake.writes() if r.status < 400]
    resent = second[len(first) :]
    assert not set(resent) & set(first)
    assert len([r for r in second if r[1] == "repos/example/repo/issues" and r[0] == "POST"]) == 1
    assert legacy.run("verify")[0] == 0
    created_number = json.loads((legacy.records / "idmap.json").read_text())["entries"]["init-local-00003"]["number"]
    code, result = legacy.run("undo", apply=True)
    assert code == 0, result
    restored = _model(fake)
    assert restored["labels"] == original["labels"]  # register-created label definitions are gone, the old one stays
    created = restored["issues"].pop(created_number)
    assert created[2] == "closed" and created[3] == []
    assert fake.issue(created_number).state_reason == "not_planned"
    assert restored["issues"] == original["issues"]
    idmap = json.loads((legacy.records / "idmap.json").read_text())["entries"]
    assert "init-local-00003" not in idmap
    writes = len(fake.writes())
    assert legacy.run("undo", apply=True)[0] == 0
    assert len(fake.writes()) == writes


def test_a_lost_create_answer_is_recovered_without_a_second_issue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    fake.inject(status=502, method="POST", endpoint="repos/example/repo/issues", apply=True)
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    creations = [r for r in fake.writes() if r.method == "POST" and r.endpoint == "repos/example/repo/issues"]
    assert len(creations) == 1
    assert legacy.run("verify")[0] == 0


def test_register_paces_writes_and_waits_out_a_rate_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    fake.inject(
        status=403,
        headers={"retry-after": "30"},
        body={"message": "secondary rate limit"},
        method="POST",
        endpoint="repos/example/repo/issues/1/labels",
    )
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    writes = list(fake.writes())
    times = [r.at for r in writes]
    assert all(later - earlier >= 1.0 for earlier, later in itertools.pairwise(times))
    limited = [index for index, r in enumerate(writes) if r.status == 403]
    assert len(limited) == 1
    retried = writes[limited[0] + 1]
    assert (retried.method, retried.endpoint) == (writes[limited[0]].method, writes[limited[0]].endpoint)
    assert retried.at - writes[limited[0]].at >= 30


def test_the_minute_and_hour_ceilings_hold_for_long_runs() -> None:
    from tests.support.fake_github import FakeClock, FakeGithub
    from tests.support.migration_repo import migrate_module

    module = migrate_module()
    clock = FakeClock()
    fake = FakeGithub("example/repo", clock=clock)
    fake.add_issue(1, title="One")
    gh = module.Github("example", "repo", runner=fake, clock=clock)
    for index in range(620):
        gh.write("POST", "repos/example/repo/issues/1/labels", {"labels": [f"l{index}"]})
    times = [r.at for r in fake.writes()]
    assert all(b - a >= 1.0 for a, b in itertools.pairwise(times))
    for start, moment in enumerate(times):
        assert sum(1 for t in times[start:] if t - moment < 60) <= 80
        assert sum(1 for t in times[start:] if t - moment < 3600) <= 500


def test_register_skips_conflicting_github_structure_and_verify_reports_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    fake.issue(4).labels = ["spec-dock:epic"]
    fake.issue(4).body = "<!-- spec-dock:slug=other -->\n"  # an old marker is only text now
    fake.add_issue(70, title="Elsewhere")
    fake.set_parent(3, 70)
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    codes = {item["code"] for item in result["anomalies"]}
    assert {"KIND_LABEL_CONFLICT", "PARENT_CONFLICT"} <= codes
    assert "SLUG_MARKER_CONFLICT" not in codes
    assert fake.issue(4).labels == ["spec-dock:epic"]
    assert fake.issue(4).body == "<!-- spec-dock:slug=other -->\n"
    assert fake.issue(3).parent == ["example/repo", 70]
    code, result = legacy.run("verify")
    assert code == 1 and result["status"] == "problems"
    joined = "\n".join(result["data"]["mismatches"])
    assert "iss-00004" in joined and "iss-00003" in joined


def test_blocking_anomalies_stop_register_before_any_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tests.support.migration_repo import ISSUE3, meta

    legacy = build_legacy(tmp_path, monkeypatch)
    legacy.commit_to_origin(
        {f"{ISSUE3}/.meta.json": meta("issue", "iss-00003", "Gamma", "gamma", 4, parent="epic-00002")}, "dup"
    )
    code, result = legacy.run("register", apply=True)
    assert code == 2
    assert legacy.github.writes() == []
    assert {"ID_NUMBER_MISMATCH", "DUPLICATE_NUMBER"} <= {item["code"] for item in result["anomalies"]}


def _creation_intent(legacy: Legacy, at: str = "2026-10-26T00:00:00Z") -> None:
    """undo.jsonl as left by a register stopped right after it sent the Issue creation."""
    legacy.records.mkdir(parents=True, exist_ok=True)
    intent = {
        "seq": 1,
        "at": at,
        "phase": "intent",
        "op": "issue.create",
        "local_id": "init-local-00003",
        "title": "Architecture",
        "label": "spec-dock:initiative",
    }
    (legacy.records / "undo.jsonl").write_text(json.dumps(intent) + "\n")


def _issue_creations(fake: FakeGithub) -> list:
    return [r for r in fake.writes() if r.method == "POST" and r.endpoint == "repos/example/repo/issues"]


def test_undo_finds_an_issue_whose_creation_was_never_recorded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    _creation_intent(legacy)
    orphan = legacy.github.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    code, result = legacy.run("undo", apply=True)
    assert code == 0, result
    assert orphan.state == "closed" and orphan.state_reason == "not_planned" and orphan.labels == []


def test_a_register_stopped_after_the_creation_picks_that_issue_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    _creation_intent(legacy, at="2026-10-26T00:03:00Z")  # the local clock ran three minutes ahead of GitHub
    orphan = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    assert _issue_creations(fake) == []
    idmap = json.loads((legacy.records / "idmap.json").read_text())["entries"]
    assert idmap["init-local-00003"] == {"id": f"init-{orphan.number:05d}", "number": orphan.number, "how": "created"}
    assert legacy.run("verify")[0] == 0


def test_two_matching_issues_stop_register_with_their_numbers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    _creation_intent(legacy)
    first = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    second = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    code, result = legacy.run("register", apply=True)
    assert code in (2, 3) and result["status"] in ("refused", "stopped")
    assert f"#{first.number}" in result["error"] and f"#{second.number}" in result["error"]
    assert any("register --apply" in step for step in result["next_steps"])
    assert _issue_creations(fake) == []
    code, result = legacy.run("undo", apply=True)
    assert code in (2, 3) and f"#{first.number}" in result["error"]
    assert first.state == "open" and second.state == "open"


def test_issues_by_someone_else_or_from_before_the_intent_are_not_picked_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, timezone

    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    _creation_intent(legacy, at="2026-10-26T00:10:00Z")
    stranger = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"], author="someone-else")
    older = fake.add_issue(
        title="Architecture",
        labels=["spec-dock:initiative"],
        created_at=datetime(2026, 10, 26, 0, 4, 59, tzinfo=timezone.utc),  # beyond the five-minute allowance
    )
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    assert len(_issue_creations(fake)) == 1
    number = json.loads((legacy.records / "idmap.json").read_text())["entries"]["init-local-00003"]["number"]
    assert number not in (stranger.number, older.number)


def test_a_label_someone_else_created_meanwhile_is_never_deleted_by_undo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    fake.inject(
        status=422,
        body={"message": "Validation Failed", "errors": [{"code": "already_exists"}]},
        method="POST",
        endpoint="repos/example/repo/labels",
        apply=True,
    )
    assert legacy.run("register", apply=True)[0] == 0
    first = next(r for r in fake.writes() if r.endpoint == "repos/example/repo/labels")
    assert first.status == 422
    assert legacy.run("undo", apply=True)[0] == 0
    assert set(fake.labels) == {first.payload["name"]}  # type: ignore[index]


def test_graphql_rate_limits_are_waited_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    legacy.github.inject(
        status=200, body={"errors": [{"type": "RATE_LIMITED", "message": "rate limited"}]}, endpoint="graphql"
    )
    code, _ = legacy.run("plan")
    assert code == 0
    assert 60.0 in legacy.clock.sleeps


def test_undo_does_not_count_an_issue_already_recorded_for_another_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    recorded = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    orphan = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    legacy.records.mkdir(parents=True, exist_ok=True)
    base = {"op": "issue.create", "title": "Architecture", "label": "spec-dock:initiative"}
    lines = [
        {"seq": 1, "at": "2026-10-26T00:00:00Z", "phase": "intent", "local_id": "init-local-00007", **base},
        {
            "seq": 2,
            "at": "2026-10-26T00:00:00Z",
            "phase": "done",
            "ref": 1,
            "local_id": "init-local-00007",
            "number": recorded.number,
            "database_id": recorded.id,
            **base,
        },
        {"seq": 3, "at": "2026-10-26T00:00:00Z", "phase": "intent", "local_id": "init-local-00008", **base},
    ]
    (legacy.records / "undo.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))
    code, result = legacy.run("undo", apply=True)
    assert code == 0, result
    assert orphan.state == "closed" and recorded.state == "closed"  # each closed once, by its own record


def test_a_creation_recorded_before_the_id_map_was_saved_is_used_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    fake = legacy.github
    created = fake.add_issue(title="Architecture", labels=["spec-dock:initiative"])
    legacy.records.mkdir(parents=True, exist_ok=True)
    base = {
        "op": "issue.create",
        "local_id": "init-local-00003",
        "title": "Architecture",
        "label": "spec-dock:initiative",
    }
    lines = [
        {"seq": 1, "at": "2026-10-26T00:00:00Z", "phase": "intent", **base},
        {
            "seq": 2,
            "at": "2026-10-26T00:00:00Z",
            "phase": "done",
            "ref": 1,
            "number": created.number,
            "database_id": created.id,
            **base,
        },
    ]
    (legacy.records / "undo.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    assert _issue_creations(fake) == []
    idmap = json.loads((legacy.records / "idmap.json").read_text())["entries"]
    assert idmap["init-local-00003"]["number"] == created.number
    assert legacy.run("verify")[0] == 0


def test_undo_without_a_work_record_stops_before_reading_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """iss-00436 (I-8 ST-1): a wrong or missing --state-dir must not look like "nothing to undo"."""
    legacy = build_legacy(tmp_path, monkeypatch)
    for apply in (False, True):
        code, result = legacy.run("undo", apply=apply)
        assert (code, result["status"]) == (2, "refused"), result
        assert "undo.jsonl" in result["error"]
        assert any("--state-dir" in step for step in result["next_steps"])
    assert legacy.github.writes() == []
    assert not (legacy.records / "undo.jsonl").exists()


def test_register_after_undo_creates_a_new_issue_instead_of_the_undone_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """iss-00436 (I-15 gate 2 P3): the closed, unlabelled Issue undo left behind is never reused."""
    legacy = build_legacy(tmp_path, monkeypatch)
    assert legacy.run("register", apply=True)[0] == 0
    undone = json.loads((legacy.records / "idmap.json").read_text())["entries"]["init-local-00003"]["number"]
    assert legacy.run("undo", apply=True)[0] == 0
    legacy.clock.advance(600)
    code, result = legacy.run("register", apply=True)
    assert code == 0, result
    entry = json.loads((legacy.records / "idmap.json").read_text())["entries"]["init-local-00003"]
    assert entry["how"] == "created" and entry["number"] != undone
    assert len(_issue_creations(legacy.github)) == 2
    assert legacy.github.issue(entry["number"]).labels == ["spec-dock:initiative"]
    assert legacy.github.issue(undone).state == "closed"
    assert legacy.run("verify")[0] == 0

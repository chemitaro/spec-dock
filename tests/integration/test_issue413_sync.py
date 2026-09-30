"""Sync displays current Scope lifecycle and all worktree selections without persistence."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_local_sync_is_readonly_and_includes_unselected_scopes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    before[record] = record.read_bytes()
    before[root / "spec-dock/workspace.json"] = (root / "spec-dock/workspace.json").read_bytes()
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    data = result["data"]
    assert data["kind"] == "sync"
    assert data["source"] == "local"
    assert data["complete"] is True
    assert data["scopes"] == [
        {"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "unknown"},
        {"scope_id": "epic-00002", "github_ref": "gh:example/repo#2", "lifecycle": "unknown"},
    ]
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": True},
        {"scope_id": "epic-00002", "direct_selected_count": 0, "descendant_selected_count": 0, "complete": True},
    ]
    assert len(data["worktrees"]) == 1
    assert data["worktrees"][0]["process_state"] == "not_observed"
    assert data["worktrees"][0]["selection"]["scope_id"] == "init-00001"
    assert data["worktrees"][0]["lifecycle"] == "unknown"
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (root / ".git/spec-dock").exists()
    assert set(record.parent.iterdir()) == {record}


@pytest.mark.parametrize("source", [["--source", "cache"], ["--source=cache"]])
def test_sync_rejects_retired_cache_source_before_resolving_the_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], source: list[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "workspace", "sync", *source, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert "local" in result["error"]["message"]
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_sync_offline_mode_refuses_requested_github_observation_before_a_get(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--offline", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert not log.exists()
    assert not (root / "spec-dock/.agent").exists()
    assert main(["--project", str(root), "workspace", "sync", "--offline", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["complete"] is True
    assert not log.exists()


def test_sync_text_displays_each_worktree_lifecycle_and_selection_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    select_fixture(root)
    github_fixture(tmp_path, monkeypatch, {"1": "completed"})
    assert main(["--project", str(root), "workspace", "sync", "--source", "github"]) == 0
    output = capsys.readouterr()
    assert output.err == ""
    assert "source=github complete=true" in output.out
    assert str(root) in output.out
    assert "selection=selected" in output.out
    assert "process_state=not_observed" in output.out
    assert "scope_id=init-00001 github_ref=gh:example/repo#1 lifecycle=completed" in output.out
    assert "direct_selected_count=1 descendant_selected_count=0 complete=true" in output.out


def test_conflicting_github_linkages_keep_each_observed_ref_and_lifecycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    select_fixture(root)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    metadata = linked / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(metadata.read_bytes())
    payload["github"]["repo_owner"] = "other"
    metadata.write_text(json.dumps(payload))
    record = select_fixture(linked)
    payload = json.loads(record.read_bytes())
    payload["github_ref"] = "gh:other/repo#1"
    record.write_text(json.dumps(payload))
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    executable = tmp_path / "gh-bin/gh"
    code = (
        executable
        .read_text()
        .replace(
            "assert endpoint==f'repos/example/repo/issues/{number}'",
            "repository='/'.join(endpoint.split('/')[1:3]); assert repository in ('example/repo','other/repo')",
        )
        .replace(
            "'repository_url':'https://api.github.com/repos/example/repo'",
            "'repository_url':f'https://api.github.com/repos/{repository}'",
        )
        .replace(
            "f'https://github.com/example/repo/issues/{number}'",
            "f'https://github.com/{repository}/issues/{number}'",
        )
        .replace(
            "state=states[str(number)]",
            "state='completed' if repository=='other/repo' else states[str(number)]",
        )
        .replace("{'method':method,", "{'endpoint':endpoint,'method':method,")
    )
    executable.write_text(code)
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 7
    data = json.loads(capsys.readouterr().out)["data"]
    assert data["scopes"] == [
        {"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "open"},
        {"scope_id": "init-00001", "github_ref": "gh:other/repo#1", "lifecycle": "completed"},
    ]
    rows = {row["path"]: row for row in data["worktrees"]}
    assert rows[str(root)]["lifecycle"] == "open"
    assert rows[str(linked)]["lifecycle"] == "completed"
    assert any(item["code"] == "SCOPE_IDENTITY_CONFLICT" for item in data["findings"])
    assert [json.loads(line)["endpoint"] for line in log.read_text().splitlines()] == [
        "repos/example/repo/issues/1",
        "repos/other/repo/issues/1",
    ]
    assert record.read_bytes() == before


def test_same_github_ref_under_different_scope_ids_is_an_identity_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    scope = linked / "spec-dock/initiatives/init-00001-fixture"
    renamed = scope.with_name("init-local-00001-fixture")
    scope.rename(renamed)
    payload = json.loads((renamed / ".meta.json").read_bytes())
    payload["id"] = "init-local-00001"
    (renamed / ".meta.json").write_text(json.dumps(payload))
    record = select_fixture(linked, scope_id="init-local-00001")
    before = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert data["scopes"] == [
        {"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "open"},
        {"scope_id": "init-local-00001", "github_ref": "gh:example/repo#1", "lifecycle": "open"},
    ]
    assert any(item["code"] == "SCOPE_IDENTITY_CONFLICT" for item in data["findings"])
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 0, "descendant_selected_count": 0, "complete": False},
        {"scope_id": "init-local-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": False},
    ]
    assert len(log.read_text().splitlines()) == 1
    assert record.read_bytes() == before


def test_existing_duplicate_selections_are_displayed_without_automatic_clear(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    record = select_fixture(root)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    duplicate = select_fixture(linked)
    before = {record: record.read_bytes(), duplicate: duplicate.read_bytes()}
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 2, "descendant_selected_count": 0, "complete": False}
    ]
    assert len(data["worktrees"]) == 2
    assert all(row["selection"]["status"] == "selected" for row in data["worktrees"])
    assert any(item["code"] == "SELECTION_DUPLICATE" for item in data["findings"])
    assert all(path.read_bytes() == value for path, value in before.items())


def test_github_sync_cannot_report_a_complete_observation_for_unknown_remote_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    github_fixture(tmp_path, monkeypatch, {"1": "unknown"})
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["effects"] == []
    assert result["data"]["complete"] is False
    assert result["data"]["scopes"][0]["lifecycle"] == "unknown"
    assert result["data"]["worktrees"][0]["lifecycle"] == "unknown"
    assert result["data"]["findings"][0]["code"] == "GITHUB_STATE_UNKNOWN"
    assert record.read_bytes() == before


def test_unreadable_worktree_record_keeps_known_counts_incomplete_and_preserves_bytes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    record = select_fixture(root)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    broken = select_fixture(linked)
    broken.write_bytes(b"not valid JSON")
    before = {record: record.read_bytes(), broken: broken.read_bytes()}

    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": False}
    ]
    rows = {row["path"]: row for row in data["worktrees"]}
    assert rows[str(root)]["selection"]["status"] == "selected"
    assert rows[str(linked)]["selection"]["status"] == "invalid"
    assert rows[str(linked)]["findings"]
    assert any(item["details"].get("path") == str(linked) for item in data["findings"])
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (root / ".git/spec-dock").exists()
    assert set(record.parent.iterdir()) == {record}


@pytest.mark.parametrize("source", ["local", "github"])
def test_stale_selection_keeps_its_known_scope_and_direct_count_without_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], source: str
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    record = select_fixture(linked)
    before = record.read_bytes()
    for worktree in (root, linked):
        shutil.rmtree(worktree / "spec-dock/initiatives/init-00001-fixture")
    log = github_fixture(tmp_path, monkeypatch, {"1": "completed"})
    assert main(["--project", str(root), "workspace", "sync", "--source", source, "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    data = result["data"]
    assert data["complete"] is False
    assert data["scopes"] == [
        {
            "scope_id": "init-00001",
            "github_ref": "gh:example/repo#1",
            "lifecycle": "completed" if source == "github" else "unknown",
        }
    ]
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": False}
    ]
    row = next(row for row in data["worktrees"] if row["path"] == str(linked))
    assert row["selection"]["status"] == "stale"
    assert row["selection"]["scope_id"] == "init-00001"
    assert row["lifecycle"] == ("completed" if source == "github" else "unknown")
    assert record.read_bytes() == before
    if source == "github":
        assert len(log.read_text().splitlines()) == 1
    else:
        assert not log.exists()


def test_github_sync_separates_lifecycle_from_selection_without_a_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    before[record] = record.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "completed", "2": "open"})

    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]
    assert result["effects"] == []
    assert data["complete"] is True
    assert data["scopes"] == [
        {"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "completed"},
        {"scope_id": "epic-00002", "github_ref": "gh:example/repo#2", "lifecycle": "open"},
    ]
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": True},
        {"scope_id": "epic-00002", "direct_selected_count": 0, "descendant_selected_count": 0, "complete": True},
    ]
    assert data["worktrees"][0]["lifecycle"] == "completed"
    assert data["worktrees"][0]["selection"]["status"] == "selected"
    assert [(item["method"], item["number"]) for item in map(json.loads, log.read_text().splitlines())] == [
        ("GET", 1),
        ("GET", 2),
    ]
    assert all(path.read_bytes() == value for path, value in before.items())
    assert set(record.parent.iterdir()) == {record}
    assert not (root / "spec-dock/.agent/github-status-cache.json").exists()

    log.unlink()
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 0
    local = json.loads(capsys.readouterr().out)["data"]
    assert [row["lifecycle"] for row in local["scopes"]] == ["unknown", "unknown"]
    assert local["worktrees"][0]["lifecycle"] == "unknown"
    assert not log.exists()


def test_sync_includes_another_worktrees_target_chain_without_reading_its_unrelated_tree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "main")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    epic = add_scope(linked, "epic-00002", "epic", "init-00001", linked / "spec-dock/initiatives/init-00001-fixture")
    add_scope(linked, "iss-00003", "issue", "epic-00002", epic)
    unrelated = linked / "spec-dock/initiatives/init-00099-other"
    unrelated.mkdir()
    (unrelated / ".meta.json").write_bytes(b"unrelated invalid metadata must not be read")
    record = select_fixture(linked, scope_id="iss-00003", number=3)
    before = record.read_bytes()

    assert main(["--project", str(linked), "scope", "list", "--json"]) == 3
    capsys.readouterr()

    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]
    assert result["effects"] == []
    assert data["complete"] is True
    assert [row["scope_id"] for row in data["scopes"]] == ["init-00001", "epic-00002", "iss-00003"]
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 0, "descendant_selected_count": 1, "complete": True},
        {"scope_id": "epic-00002", "direct_selected_count": 0, "descendant_selected_count": 1, "complete": True},
        {"scope_id": "iss-00003", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": True},
    ]
    rows = {row["path"]: row for row in data["worktrees"]}
    assert set(rows) == {str(root), str(linked)}
    assert rows[str(root)]["selection"]["status"] == "empty"
    assert rows[str(linked)]["selection"]["scope_id"] == "iss-00003"
    assert rows[str(linked)]["selection"]["branch_changed"] is True
    assert rows[str(linked)]["selection"]["current_branch"] is None
    assert rows[str(linked)]["process_state"] == "not_observed"
    assert record.read_bytes() == before


def test_unavailable_github_observation_is_partial_without_effects_or_cached_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    cache = root / "spec-dock/.agent/github-status-cache.json"
    cache.write_text('{"items":{"epic-00002":{"state":"completed"}}}\n')
    before = {record: record.read_bytes(), cache: cache.read_bytes()}
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})

    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["effects"] == []
    assert result["error"]["code"] == "SYNC_INCOMPLETE"
    data = result["data"]
    assert data["complete"] is False
    assert data["scopes"] == [
        {"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "open"},
        {"scope_id": "epic-00002", "github_ref": "gh:example/repo#2", "lifecycle": "unknown"},
    ]
    assert any(item["details"].get("github_ref") == "gh:example/repo#2" for item in data["findings"])
    assert [(item["method"], item["number"]) for item in map(json.loads, log.read_text().splitlines())] == [
        ("GET", 1),
        ("GET", 2),
    ]
    assert all(path.read_bytes() == value for path, value in before.items())


def test_conflicting_parent_chains_are_reported_without_collapsing_worktree_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "main")
    first = root / "spec-dock/initiatives/init-00001-fixture"
    other = root / "spec-dock/initiatives/init-00005-other"
    other.mkdir()
    payload = json.loads((first / ".meta.json").read_bytes())
    payload.update(id="init-00005", slug="other", github=dict(payload["github"], issue_number=5))
    (other / ".meta.json").write_text(json.dumps(payload))
    epic = add_scope(root, "epic-00002", "epic", "init-00001", first)
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    subprocess.run(["git", "-C", str(root), "add", "--", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture hierarchy",
        ],
        check=True,
        capture_output=True,
    )
    main_record = select_fixture(root, scope_id="iss-00003", number=3)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    changed_epic = linked / other.relative_to(root) / "epics" / epic.name
    changed_epic.parent.mkdir()
    (linked / epic.relative_to(root)).rename(changed_epic)
    changed = json.loads((changed_epic / ".meta.json").read_bytes())
    changed.update(parent_id="init-00005", initiative_id="init-00005")
    (changed_epic / ".meta.json").write_text(json.dumps(changed))
    issue = add_scope(linked, "iss-00004", "issue", "epic-00002", changed_epic)
    changed = json.loads((issue / ".meta.json").read_bytes())
    changed["initiative_id"] = "init-00005"
    (issue / ".meta.json").write_text(json.dumps(changed))
    linked_record = select_fixture(linked, scope_id="iss-00004", number=4)
    before = {main_record: main_record.read_bytes(), linked_record: linked_record.read_bytes()}

    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    data = json.loads(capsys.readouterr().out)["data"]
    assert data["complete"] is False
    assert any(item["code"] == "SCOPE_ANCESTRY_CONFLICT" for item in data["findings"])
    counts = {row["scope_id"]: row for row in data["counts"]}
    assert counts["init-00001"]["descendant_selected_count"] == 1
    assert counts["init-00005"]["descendant_selected_count"] == 1
    assert counts["epic-00002"]["descendant_selected_count"] == 2
    assert all(row["complete"] is False for row in counts.values())
    assert len(data["worktrees"]) == 2
    assert all(row["selection"]["status"] == "selected" for row in data["worktrees"])
    assert all(path.read_bytes() == value for path, value in before.items())


@pytest.mark.parametrize("allow_invalid", [False, True])
def test_sync_unknown_schema_is_a_readonly_diagnostic_failure_even_with_allow_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], allow_invalid: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(metadata.read_bytes())
    payload["schema_version"] = 999
    metadata.write_text(json.dumps(payload))
    before = metadata.read_bytes()
    options = ["--allow-invalid"] if allow_invalid else []
    assert main(["--project", str(root), "workspace", "sync", *options, "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert result["effects"] == []
    assert result["error"]["code"] == "SYNC_INPUT_INVALID"
    assert metadata.read_bytes() == before
    assert not (root / "spec-dock/.agent").exists()


def test_multiple_worktrees_share_parent_counts_and_live_refs_once_with_schema_valid_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from copy import deepcopy
    from pathlib import Path

    from tests.cli_runtime.test_issue413_contract import add_scope

    root = committed_workspace(tmp_path / "main")
    epic = add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    for number in (3, 4, 6):
        add_scope(root, f"iss-{number:05d}", "issue", "epic-00002", epic)
    subprocess.run(["git", "-C", str(root), "add", "--", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture hierarchy",
        ],
        check=True,
        capture_output=True,
    )
    records = [select_fixture(root, scope_id="epic-00002", number=2)]
    for number in (3, 4):
        linked = tmp_path / f"linked-{number}"
        subprocess.run(
            ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
            check=True,
            capture_output=True,
        )
        records.append(select_fixture(linked, scope_id=f"iss-{number:05d}", number=number))
    before = {record: record.read_bytes() for record in records}
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "completed", "4": "open", "6": "open"})
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]
    assert len(data["worktrees"]) == 3
    assert all(row["process_state"] == "not_observed" for row in data["worktrees"])
    counts = {row["scope_id"]: row for row in data["counts"]}
    assert counts["epic-00002"] == {
        "scope_id": "epic-00002",
        "direct_selected_count": 1,
        "descendant_selected_count": 2,
        "complete": True,
    }
    assert counts["init-00001"]["descendant_selected_count"] == 3
    assert counts["iss-00003"]["direct_selected_count"] == 1
    assert counts["iss-00006"]["direct_selected_count"] == 0
    states = {row["scope_id"]: row["lifecycle"] for row in data["scopes"]}
    assert states["iss-00003"] == "completed" and states["iss-00006"] == "open"
    assert [(row["method"], row["number"]) for row in map(json.loads, log.read_text().splitlines())] == [
        ("GET", 1),
        ("GET", 2),
        ("GET", 3),
        ("GET", 4),
        ("GET", 6),
    ]
    assert all(path.read_bytes() == value for path, value in before.items())
    schema = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "docs/issue-plans/iss-00413-external-cli-state/artifacts/cli-schema.json"
        ).read_bytes()
    )
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    validator.validate(result)
    missing = deepcopy(result)
    del missing["data"]["scopes"]
    with pytest.raises(ValidationError):
        validator.validate(missing)
    invalid = deepcopy(result)
    invalid["data"]["scopes"][0]["lifecycle"] = "running"
    with pytest.raises(ValidationError):
        validator.validate(invalid)


def test_existing_local_lifecycle_disagreement_does_not_adopt_one_worktrees_value(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    before = {}
    for worktree, state in ((root, "completed"), (linked, "open")):
        metadata = worktree / "spec-dock/initiatives/init-00001-fixture/.meta.json"
        payload = json.loads(metadata.read_bytes())
        payload.update(
            backend="local",
            github=None,
            lifecycle={"state": state, "revision": 1, "updated_at": "2026-09-30T00:00:00Z"},
        )
        metadata.write_text(json.dumps(payload))
        record = select_fixture(worktree)
        payload = json.loads(record.read_bytes())
        payload["github_ref"] = None
        record.write_text(json.dumps(payload))
        before[metadata], before[record] = metadata.read_bytes(), record.read_bytes()
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    data = json.loads(capsys.readouterr().out)["data"]
    assert data["scopes"] == [{"scope_id": "init-00001", "github_ref": None, "lifecycle": "unknown"}]
    assert all(row["lifecycle"] == "unknown" for row in data["worktrees"])
    assert any(row["code"] == "LOCAL_LIFECYCLE_CONFLICT" for row in data["findings"])
    assert all(path.read_bytes() == value for path, value in before.items())


def test_sync_preserves_native_git_error_when_one_worktree_cannot_be_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import os
    import shutil
    import sys

    root = committed_workspace(tmp_path / "main")
    select_fixture(root)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    real_git = shutil.which("git")
    assert real_git is not None
    bin_dir = tmp_path / "git-bin"
    bin_dir.mkdir()
    executable = bin_dir / "git"
    original_error = "fatal: fixture read refused\nsecond original line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport os,sys\n"
        f"if sys.argv[1:4]==['-C',{str(linked)!r},'rev-parse']:\n"
        f" sys.stderr.write({original_error!r}); sys.exit(73)\n"
        f"os.execv({real_git!r},['git',*sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    output = capsys.readouterr()
    assert output.err == ""
    result = json.loads(output.out)
    assert result["status"] == "partial" and result["effects"] == []
    assert result["error"]["details"]["git"]["stderr"] == original_error
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert main(["--project", str(root), "workspace", "sync"]) == 7
    assert original_error in capsys.readouterr().err


def test_sync_help_describes_readonly_observations_without_generations(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "workspace", "sync"]) == 0
    text = capsys.readouterr().out
    assert "local" in text and "github" in text
    assert "worktrees" in text and "scopes" in text and "counts" in text
    assert "complete" in text and "not_observed" in text
    assert "specdock.cli/v2" in text
    assert "generation" not in text.lower()
    assert "None; this command only reads" in text

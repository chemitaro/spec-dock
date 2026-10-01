"""Dependency operations use current metadata and explicit live observations."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_contract import add_scope
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def dependency_workspace(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = committed_workspace(tmp_path / "consumer")
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    source = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    child = add_scope(root, "iss-00003", "issue", "epic-00002", source)
    add_scope(root, "epic-00004", "epic", "init-00001", initiative)
    return root, source / ".meta.json", child / ".meta.json"


def two_dependency_trees(tmp_path: Path) -> tuple[Path, tuple[Path, Path, Path], tuple[Path, Path, Path]]:
    """Construct two existing GitHub-backed fixture trees with unique issue numbers."""
    root = committed_workspace(tmp_path / "consumer")
    left_init = root / "spec-dock/initiatives/init-00001-fixture"
    left_epic = add_scope(root, "epic-00002", "epic", "init-00001", left_init)
    left_issue = add_scope(root, "iss-00003", "issue", "epic-00002", left_epic)
    right_init = root / "spec-dock/initiatives/init-00004-fixture"
    right_init.mkdir()
    template = json.loads((left_init / ".meta.json").read_bytes())
    (right_init / ".meta.json").write_text(
        json.dumps({**template, "id": "init-00004", "github": {**template["github"], "issue_number": 4}})
    )
    right_epic = add_scope(root, "epic-00005", "epic", "init-00004", right_init)
    right_issue = add_scope(root, "iss-00006", "issue", "epic-00005", right_epic)
    for scope in (right_epic, right_issue):
        metadata = scope / ".meta.json"
        payload = json.loads(metadata.read_bytes())
        metadata.write_text(json.dumps({**payload, "initiative_id": "init-00004"}))
    return (
        root,
        (left_init / ".meta.json", left_epic / ".meta.json", left_issue / ".meta.json"),
        (right_init / ".meta.json", right_epic / ".meta.json", right_issue / ".meta.json"),
    )


def test_dependency_list_derives_inherited_edges_from_current_metadata_without_control(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["epic-00004"]
    source.write_text(json.dumps(payload))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (*root.glob("spec-dock/**/.meta.json"), record)}
    assert main(["--project", str(root), "dependency", "list", "@current", "--view", "effective", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["effects"] == []
    assert result["data"] == {
        "kind": "dependency",
        "result": {
            "scope_id": "iss-00003",
            "declared": [],
            "effective": ["epic-00004"],
            "ready": None,
            "blockers": [],
            "changed": False,
        },
    }
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent/staging").exists()


def test_offline_live_dependency_check_refuses_before_any_github_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, child = dependency_workspace(tmp_path)
    before = {path: path.read_bytes() for path in (source, child)}
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open"})
    assert (
        main(["--project", str(root), "dependency", "check", "iss-00003", "--source", "github", "--offline", "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and not log.exists()
    assert all(path.read_bytes() == exact for path, exact in before.items())


@pytest.mark.parametrize("stored_state", ["closed", "malformed"])
def test_dependency_check_defaults_to_unknown_github_state_and_never_reads_retired_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], stored_state: str
) -> None:
    root, _source, child = dependency_workspace(tmp_path)
    payload = json.loads(child.read_bytes())
    payload["depends_on"] = ["epic-00004"]
    child.write_text(json.dumps(payload))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    cache = root / "spec-dock/.agent/github-status-cache.json"
    cache.write_text('{"items":{"iss-00003":{"state":"open"},"epic-00004":{"state":"completed"}}}')
    retired_indexes = [cache.parent / name for name in ("index-all.json", "index.json")]
    for index in retired_indexes:
        index.write_bytes(
            json.dumps({
                "nodes": {
                    "epic-00004": {
                        "type": "epic",
                        "github": {"state": "CLOSED", "updated_at": "2026-06-05T00:00:00Z"},
                        "private": "private old cache sentinel",
                    },
                },
            }).encode()
            if stored_state == "closed"
            else b"{private malformed cache sentinel"
        )
    before = {
        path: path.read_bytes() for path in (*root.glob("spec-dock/**/.meta.json"), record, cache, *retired_indexes)
    }
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open", "4": "completed"})
    assert main(["--project", str(root), "dependency", "check", "@current", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert data["scope_id"] == "iss-00003" and data["ready"] is False and data["changed"] is False
    assert data["declared"] == ["epic-00004"] and data["effective"] == ["epic-00004"]
    assert {item["details"]["scope_id"] for item in data["blockers"]} == {
        "iss-00003",
        "epic-00002",
        "init-00001",
        "epic-00004",
    }
    assert all(item["details"]["observed_state"] == "unknown" for item in data["blockers"])
    assert result["effects"] == [] and output.err == "" and not log.exists()
    assert "private old cache sentinel" not in output.out and "private malformed cache sentinel" not in output.out
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("target", ["epic-00002", "iss-00003"])
def test_dependency_list_merges_each_ancestor_once_and_preserves_all_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], target: str
) -> None:
    root, left, right = two_dependency_trees(tmp_path)
    sibling = add_scope(root, "iss-00007", "issue", "epic-00005", right[1].parent) / ".meta.json"
    payload = json.loads(sibling.read_bytes())
    payload["initiative_id"] = "init-00004"
    sibling.write_text(json.dumps(payload))
    for path, dependencies in zip(left, (["iss-00006"], ["iss-00006", "iss-00007"], ["iss-00007"]), strict=True):
        payload = json.loads(path.read_bytes())
        payload["depends_on"] = dependencies
        path.write_text(json.dumps(payload))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (*left, *right, sibling, record)}
    log = github_fixture(tmp_path, monkeypatch, {})
    assert main(["--project", str(root), "dependency", "list", target, "--view", "effective", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["scope_id"] == target and data["ready"] is None and data["changed"] is False
    assert data["effective"] == (["iss-00006", "iss-00007"] if target == "epic-00002" else ["iss-00007", "iss-00006"])
    assert data["declared"] == (["iss-00006", "iss-00007"] if target == "epic-00002" else ["iss-00007"])
    assert result["effects"] == [] and not log.exists()
    assert all(path.read_bytes() == payload for path, payload in before.items())
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("kind", ["initiative", "epic"])
@pytest.mark.parametrize("backend", ["github", "local"])
@pytest.mark.parametrize("state", ["open", "completed"])
@pytest.mark.parametrize("populated", [False, True])
def test_high_level_prerequisite_uses_its_own_observed_lifecycle_without_completing_from_children(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    backend: str,
    state: str,
    populated: bool,
) -> None:
    root, left, right = two_dependency_trees(tmp_path)
    if not populated:
        shutil.rmtree(right[1 if kind == "initiative" else 2].parent)
    metadata_paths = tuple(path for path in (*left, *right) if path.exists())
    prerequisite = "init-00004" if kind == "initiative" else "epic-00005"
    number = 4 if kind == "initiative" else 5
    for path in metadata_paths:
        payload = json.loads(path.read_bytes())
        if path == left[2]:
            payload["depends_on"] = [prerequisite]
        if backend == "local":
            payload.update(
                backend="local",
                github=None,
                lifecycle={
                    "state": state if payload["id"] == prerequisite else "open",
                    "revision": 7,
                    "updated_at": "2026-09-29T00:00:00Z",
                },
            )
        path.write_text(json.dumps(payload))
    before = {path: path.read_bytes() for path in metadata_paths}
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open", str(number): state})
    assert (
        main([
            "--project",
            str(root),
            "dependency",
            "check",
            "iss-00003",
            "--source",
            backend,
            *(["--offline"] if backend == "local" else []),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["ready"] is (state == "completed") and data["effective"] == [prerequisite]
    assert data["changed"] is False and result["effects"] == []
    assert [item["details"]["scope_id"] for item in data["blockers"]] == ([prerequisite] if state == "open" else [])
    if backend == "github":
        requests = [json.loads(line) for line in log.read_text().splitlines()]
        assert len(requests) == 4 and {item["number"] for item in requests} == {1, 2, 3, number}
        assert all(item["method"] == "GET" for item in requests)
    else:
        assert not log.exists()
    assert all(path.read_bytes() == payload for path, payload in before.items())
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_dependency_check_refuses_an_empty_container_cycle_before_any_remote_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _source, _child = dependency_workspace(tmp_path)
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    other = add_scope(root, "epic-00005", "epic", "init-00001", initiative)
    empty = initiative / "epics/epic-00004-fixture"
    for owner, dependency in ((empty, "epic-00005"), (other, "epic-00004")):
        metadata = owner / ".meta.json"
        payload = json.loads(metadata.read_bytes())
        payload["depends_on"] = [dependency]
        metadata.write_text(json.dumps(payload))
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    log = github_fixture(tmp_path, monkeypatch, {})
    assert main(["--project", str(root), "dependency", "check", "epic-00004", "--source", "github", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert "cycle" in result["error"]["message"] and not log.exists()
    assert all(path.read_bytes() == payload for path, payload in before.items())
    assert not (root / ".git/spec-dock").exists()


def test_live_dependency_check_fetches_only_the_target_chain_and_effective_prerequisites(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["epic-00004"]
    source.write_text(json.dumps(payload))
    add_scope(root, "epic-00005", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (*root.glob("spec-dock/**/.meta.json"), record)}
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open", "4": "completed"})
    assert main(["--project", str(root), "dependency", "check", "@current", "--source", "github", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["ready"] is True and result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["declared"] == [] and result["data"]["result"]["effective"] == ["epic-00004"]
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    assert {row["number"] for row in requests} == {1, 2, 3, 4}
    assert len(requests) == 4 and all(row["method"] == "GET" for row in requests)
    assert result["effects"] == [] and result["warnings"] == []
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent/staging").exists()


def test_unavailable_prerequisite_remains_unknown_with_explicit_remote_diagnostic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _source, child = dependency_workspace(tmp_path)
    payload = json.loads(child.read_bytes())
    payload["depends_on"] = ["epic-00004"]
    child.write_text(json.dumps(payload))
    before = child.read_bytes()
    log = github_fixture(tmp_path, monkeypatch, {"1": "open", "2": "open", "3": "open", "4": "completed"})
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace(
            "state=states[str(number)]\n",
            "state=states[str(number)]\nif number==4:\n print('HTTP/2.0 503 Unavailable\\n\\n{}'); sys.exit(1)\n",
        )
    )
    assert main(["--project", str(root), "dependency", "check", "iss-00003", "--source", "github", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GITHUB_REMOTE_UNAVAILABLE" and result["effects"] == []
    data = result["data"]["result"]
    assert data["ready"] is False and data["changed"] is False
    assert [(item["details"]["scope_id"], item["details"]["observed_state"]) for item in data["blockers"]] == [
        ("epic-00004", "unknown")
    ]
    assert all(row["method"] == "GET" for row in map(json.loads, log.read_text().splitlines()))
    assert child.read_bytes() == before and not (root / "spec-dock/.agent").exists()


def test_dependency_add_updates_only_the_source_metadata_and_preserves_optional_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    original = json.loads(source.read_bytes())
    original["optional"] = {"nested": ["日本語", {"keep": True}]}
    source.write_text(json.dumps(original))
    source.chmod(0o640)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (*root.glob("spec-dock/**/.meta.json"), record)}
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main(["--project", str(root), "dependency", "add", "--from", "@epic", "--to", "gh:example/repo#4", "--json"])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"] == {
        "scope_id": "epic-00002",
        "declared": ["epic-00004"],
        "effective": ["epic-00004"],
        "ready": None,
        "blockers": [],
        "changed": True,
    }
    assert result["effects"] == [{"kind": "dependency-edge", "status": "succeeded", "target": "epic-00002->epic-00004"}]
    updated = json.loads(source.read_bytes())
    assert updated == {**original, "depends_on": ["epic-00004"], "revision": original["revision"] + 1}
    assert source.stat().st_mode & 0o777 == 0o640
    assert all(path.read_bytes() == exact for path, exact in before.items() if path != source)
    assert not log.exists() and not (root / ".git/spec-dock").exists()
    assert main(["--project", str(root), "dependency", "list", "iss-00003", "--view", "effective", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["effective"] == ["epic-00004"]


@pytest.mark.parametrize("source_index", [0, 1, 2])
@pytest.mark.parametrize("target_index", [0, 1, 2])
def test_dependency_all_kind_pairs_preserve_metadata_mode_other_scopes_and_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    source_index: int,
    target_index: int,
) -> None:
    root, left, right = two_dependency_trees(tmp_path)
    source, target = left[source_index], right[target_index]
    payload = json.loads(source.read_bytes())
    payload["optional"] = {"nested": ["日本語", {"keep": True}]}
    source.write_text(json.dumps(payload))
    source.chmod(0o640)
    target_id = json.loads(target.read_bytes())["id"]
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (*left, *right, record)}
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main(["--project", str(root), "dependency", "add", "--from", payload["id"], "--to", target_id, "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["changed"] is True
    assert json.loads(source.read_bytes()) == {
        **payload,
        "depends_on": [target_id],
        "revision": payload["revision"] + 1,
    }
    assert source.stat().st_mode & 0o777 == 0o640
    assert all(path.read_bytes() == exact for path, exact in before.items() if path != source)
    assert not log.exists() and not (root / ".git/spec-dock").exists()


def test_dependency_duplicate_add_is_unchanged_and_preserves_every_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, source, _child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    log = github_fixture(tmp_path, monkeypatch, {})
    arguments = ["--project", str(root), "dependency", "add", "--from", "epic-00002", "--to", "epic-00004", "--json"]
    assert main(arguments) == 0
    capsys.readouterr()
    before = tree_digest(root)
    source_before, record_before = source.read_bytes(), record.read_bytes()
    assert main(arguments) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "unchanged" and result["data"]["result"]["changed"] is False
    assert result["effects"] == [{"kind": "dependency-edge", "status": "unchanged", "target": "epic-00002->epic-00004"}]
    assert source.read_bytes() == source_before and record.read_bytes() == record_before
    assert tree_digest(root) == before and output.err == "" and not log.exists()
    assert not (root / ".git/spec-dock").exists()


def test_dependency_add_dry_run_plans_edges_without_creating_stage_or_changing_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, child = dependency_workspace(tmp_path)
    before = {path: path.read_bytes() for path in (source, child)}
    assert (
        main([
            "--project",
            str(root),
            "dependency",
            "add",
            "--from",
            "epic-00002",
            "--to",
            "epic-00004",
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert result["status"] == "planned" and data["can_apply"] is True and data["blockers"] == []
    assert data["declared"] == ["epic-00004"] and data["effective"] == ["epic-00004"] and data["changed"] is False
    assert result["effects"] == [{"kind": "dependency-edge", "status": "planned", "target": "epic-00002->epic-00004"}]
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_dependency_remove_and_missing_ok_keep_absence_distinct_from_a_changed_edge(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    common = ["--project", str(root), "dependency"]
    options = ["--from", "epic-00002", "--to", "epic-00004", "--json"]
    assert main([*common, "add", *options]) == 0
    capsys.readouterr()
    assert main([*common, "remove", *options]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["changed"] is True and result["data"]["result"]["declared"] == []
    assert result["data"]["result"]["effective"] == []
    assert result["effects"] == [{"kind": "dependency-edge", "status": "succeeded", "target": "epic-00002->epic-00004"}]
    before = source.read_bytes()
    assert json.loads(before)["revision"] == 2
    assert main([*common, "remove", *options]) == 4
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert source.read_bytes() == before
    assert main([*common, "remove", *options, "--missing-ok"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "unchanged" and result["data"]["result"]["changed"] is False
    assert result["effects"] == [{"kind": "dependency-edge", "status": "unchanged", "target": "epic-00002->epic-00004"}]
    assert source.read_bytes() == before and not (root / ".git/spec-dock").exists()


def test_confirmed_dependency_replacement_keeps_its_effect_after_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    previous = (source.stat().st_dev, source.stat().st_ino)
    real_close = os.close
    failed = False

    def close(descriptor: int) -> None:
        nonlocal failed
        observed = os.fstat(descriptor)
        current = source.stat()
        identity = observed.st_dev, observed.st_ino
        should_fail = not failed and identity == (current.st_dev, current.st_ino) and identity != previous
        real_close(descriptor)
        if should_fail:
            failed = True
            raise OSError("fixture: confirmed dependency replacement cleanup failed")

    monkeypatch.setattr(os, "close", close)
    assert (
        main(["--project", str(root), "dependency", "add", "--from", "epic-00002", "--to", "epic-00004", "--json"]) == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert failed and result["status"] == "partial"
    assert result["data"]["result"]["changed"] is True and result["data"]["result"]["declared"] == ["epic-00004"]
    assert result["effects"] == [{"kind": "dependency-edge", "status": "succeeded", "target": "epic-00002->epic-00004"}]
    assert json.loads(source.read_bytes())["depends_on"] == ["epic-00004"]
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


@pytest.mark.parametrize("options", [["--source", "cache"], ["--source=cache"], ["--allow-stale"]])
def test_retired_dependency_readiness_inputs_are_rejected_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], options: list[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "dependency", "check", "iss-00003", *options, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "epic-00002"]])
def test_dependency_mutation_target_guards_refuse_before_metadata_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: list[str]
) -> None:
    root, source, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (source, child, record)}
    assert (
        main(["--project", str(root), "dependency", "add", "--from", "@epic", "--to", "epic-00004", *guard, "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / "spec-dock/.agent/staging").exists()


def test_dependency_publication_preserves_an_actor_edit_detected_before_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, child = dependency_workspace(tmp_path)
    original = json.loads(source.read_bytes())
    child_before = child.read_bytes()
    actor = {**original, "revision": original["revision"] + 1, "optional": {"actor": "preserve"}}
    real_fsync = os.fsync
    edited = False

    def fsync(descriptor: int) -> None:
        nonlocal edited
        if not edited and stat.S_ISREG(os.fstat(descriptor).st_mode):
            edited = True
            source.write_text(json.dumps(actor))
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert (
        main(["--project", str(root), "dependency", "add", "--from", "epic-00002", "--to", "epic-00004", "--json"]) == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert edited and result["status"] == "failed" and result["data"]["result"]["changed"] is False
    assert result["effects"] == [
        {"kind": "dependency-edge", "status": "not_attempted", "target": "epic-00002->epic-00004"}
    ]
    assert json.loads(source.read_bytes()) == actor and child.read_bytes() == child_before
    assert not list((root / "spec-dock/.agent/staging").iterdir())


@pytest.mark.parametrize("action", ["list", "check", "add", "remove"])
def test_dependency_leaf_help_describes_control_free_v2_operations(
    capsys: pytest.CaptureFixture[str], action: str
) -> None:
    assert main(["help", "dependency", action]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output
    assert "--source cache" not in output and "--resume" not in output and "journal" not in output
    if action == "check":
        assert "local" in output and "github" in output


@pytest.mark.parametrize("view", ["declared", "effective", None])
def test_dependency_text_view_distinguishes_declared_from_inherited_edges(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], view: str | None
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["epic-00004"]
    source.write_text(json.dumps(payload))
    options = ["--view", view] if view else []
    assert main(["--project", str(root), "dependency", "list", "iss-00003", *options]) == 0
    output = capsys.readouterr()
    assert output.err == "" and "scope_id=iss-00003" in output.out
    if view == "declared":
        assert "declared=[]" in output.out and "effective=" not in output.out and "epic-00004" not in output.out
    elif view == "effective":
        assert 'effective=["epic-00004"]' in output.out and "declared=" not in output.out
    else:
        assert "declared=[]" in output.out and 'effective=["epic-00004"]' in output.out


@pytest.mark.parametrize(
    "command", [["scope", "list"], ["dependency", "list", "iss-00003"], ["dependency", "check", "iss-00003"]]
)
def test_readonly_previews_preserve_readiness_and_leave_all_inputs_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], command: list[str]
) -> None:
    root, _source, _child = dependency_workspace(tmp_path)
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    assert main(["--project", str(root), *command, "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned" and result["data"]["result"]["can_apply"] is True
    assert result["effects"] == []
    if command[1] == "check":
        assert result["data"]["result"]["ready"] is False
        assert len(result["data"]["result"]["blockers"]) == 3
    else:
        assert result["data"]["result"]["blockers"] == []
    assert all(path.read_bytes() == payload for path, payload in before.items())
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize(
    "edge",
    [
        ("epic-00002", "epic-00002"),
        ("iss-00003", "epic-00002"),
        ("epic-00002", "iss-00003"),
        ("epic-00002", "epic-00004"),
    ],
)
def test_dependency_add_rejects_self_ancestry_and_inherited_wait_cycles_before_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edge: tuple[str, str]
) -> None:
    root, _source, _child = dependency_workspace(tmp_path)
    if edge == ("epic-00002", "epic-00004"):
        other = add_scope(
            root,
            "iss-00005",
            "issue",
            "epic-00004",
            root / "spec-dock/initiatives/init-00001-fixture/epics/epic-00004-fixture",
        )
        payload = json.loads((other / ".meta.json").read_bytes())
        payload["depends_on"] = ["iss-00003"]
        (other / ".meta.json").write_text(json.dumps(payload))
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    assert main(["--project", str(root), "dependency", "add", "--from", edge[0], "--to", edge[1], "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert all(path.read_bytes() == payload for path, payload in before.items())
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize(
    "first,second",
    [
        (("init-00001", "epic-00005"), ("epic-00005", "iss-00003")),
        (("iss-00003", "epic-00005"), ("epic-00005", "init-00001")),
    ],
)
def test_dependency_rejects_cross_tree_inheritance_and_parent_completion_cycles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    first: tuple[str, str],
    second: tuple[str, str],
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, _left, _right = two_dependency_trees(tmp_path)
    arguments = ["--project", str(root), "dependency", "add"]
    log = github_fixture(tmp_path, monkeypatch, {})
    assert main([*arguments, "--from", first[0], "--to", first[1], "--json"]) == 0
    capsys.readouterr()
    before = tree_digest(root)
    assert main([*arguments, "--from", second[0], "--to", second[1], "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert "cycle" in result["error"]["message"] and result["effects"] == []
    assert tree_digest(root) == before and not log.exists()
    assert not (root / ".git/spec-dock").exists()


def test_uncertain_dependency_replace_retains_unknown_effect_and_never_rolls_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, child = dependency_workspace(tmp_path)
    child_before = child.read_bytes()
    real_replace = os.replace
    attempts: list[str] = []

    def replace(source_path: str, destination_path: str, **kwargs: int) -> None:
        attempts.append(destination_path)
        real_replace(source_path, destination_path, **kwargs)
        raise OSError("fixture: replacement result unavailable")

    monkeypatch.setattr(os, "replace", replace)
    assert (
        main(["--project", str(root), "dependency", "add", "--from", "epic-00002", "--to", "epic-00004", "--json"]) == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert attempts == [".meta.json"] and result["status"] == "partial"
    assert result["effects"] == [{"kind": "dependency-edge", "status": "unknown", "target": "epic-00002->epic-00004"}]
    assert result["data"]["result"]["changed"] is False and result["data"]["result"]["declared"] == []
    assert result["data"]["result"]["metadata_observation"] == "before-operation"
    assert json.loads(source.read_bytes())["depends_on"] == ["epic-00004"] and child.read_bytes() == child_before
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory flock boundary")
def test_dependency_mutation_proceeds_while_start_exclusion_is_held(tmp_path: Path) -> None:
    import fcntl

    root, source, _child = dependency_workspace(tmp_path)
    descriptor = os.open(root / ".git", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(root),
                "dependency",
                "add",
                "--from",
                "epic-00002",
                "--to",
                "epic-00004",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == "" and json.loads(result.stdout)["data"]["result"]["changed"] is True
        assert json.loads(source.read_bytes())["depends_on"] == ["epic-00004"]
        assert not (root / ".git/spec-dock").exists()
    finally:
        os.close(descriptor)


def test_dependency_text_check_displays_readiness_and_unknown_authority_blockers(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _source, _child = dependency_workspace(tmp_path)
    assert main(["--project", str(root), "dependency", "check", "iss-00003"]) == 0
    output = capsys.readouterr()
    assert output.err == "" and "ready=false" in output.out and "scope_id=iss-00003" in output.out
    assert "iss-00003 requires open; observed unknown" in output.out
    assert "epic-00002 requires open; observed unknown" in output.out
    assert "init-00001 requires open; observed unknown" in output.out


def test_dependency_dry_run_refuses_unignored_staging_without_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, child = dependency_workspace(tmp_path)
    (root / "spec-dock/.gitignore").write_bytes(b"")
    before = {path: path.read_bytes() for path in (source, child)}
    assert (
        main([
            "--project",
            str(root),
            "dependency",
            "add",
            "--from",
            "epic-00002",
            "--to",
            "epic-00004",
            "--dry-run",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and "ignored" in result["error"]["message"]
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_dependency_local_check_preserves_genuine_existing_local_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, source, _child = dependency_workspace(tmp_path)
    for path in root.glob("spec-dock/**/.meta.json"):
        payload = json.loads(path.read_bytes())
        payload.update(
            backend="local",
            github=None,
            lifecycle={
                "state": "completed" if payload["id"] == "epic-00004" else "open",
                "revision": 7,
                "updated_at": "2026-09-29T00:00:00Z",
            },
        )
        if path == source:
            payload["depends_on"] = ["epic-00004"]
        path.write_text(json.dumps(payload))
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    log = github_fixture(tmp_path, monkeypatch, {})
    assert main(["--project", str(root), "dependency", "check", "iss-00003", "--offline", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["ready"] is True and result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["effective"] == ["epic-00004"] and result["effects"] == []
    assert not log.exists() and all(path.read_bytes() == exact for path, exact in before.items())


@pytest.mark.parametrize("target,ready", [("init-00001", True), ("iss-00003", False)])
def test_readiness_ignores_child_dependencies_and_completed_children_do_not_complete_the_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    target: str,
    ready: bool,
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, left, right = two_dependency_trees(tmp_path)
    for path in (*left, *right):
        payload = json.loads(path.read_bytes())
        payload.update(
            backend="local",
            github=None,
            lifecycle={
                "state": "completed" if path in right[1:] else "open",
                "revision": 7,
                "updated_at": "2026-09-29T00:00:00Z",
            },
        )
        if path == left[2]:
            payload["depends_on"] = ["init-00004"]
        path.write_text(json.dumps(payload))
    before = tree_digest(root)
    log = github_fixture(tmp_path, monkeypatch, {})
    assert main(["--project", str(root), "dependency", "check", target, "--offline", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["ready"] is ready and result["effects"] == []
    if ready:
        assert data["effective"] == [] and data["blockers"] == []
    else:
        assert data["effective"] == ["init-00004"]
        assert [item["details"] for item in data["blockers"]] == [
            {
                "scope_id": "init-00004",
                "required_state": "completed",
                "observed_state": "open",
                "source": "local",
                "stale": False,
            }
        ]
    assert tree_digest(root) == before and not log.exists()
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()

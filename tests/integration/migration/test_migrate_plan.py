"""migrate.py plan, target resolution and the read-only default (AC-435-01, 08, 16, 18)."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tests.support.canonical_repo import add_worktree, git
from tests.support.migration_repo import ISSUE3, build_legacy, meta, snapshot, write_files

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _codes(result: dict) -> list[str]:
    return [item["code"] for item in result["anomalies"]]


def test_plan_lists_local_scopes_with_their_replacement_and_no_blocking_anomaly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    code, result = legacy.run("plan")
    assert code == 0, result
    assert result["status"] == "ok" and result["default_branch"] == "main"
    assert result["repository"] == "github.com/example/repo"
    assert result["data"]["scopes"]["total"] == 7
    local = result["data"]["local_scopes"]
    assert local["init-local-00002"] == {"how": "existing", "number": 39, "id": "init-00039"}
    assert local["init-local-00003"] == {"how": "created", "number": None, "id": None}
    messages = {item["scope"]: item["message"] for item in result["anomalies"] if item["code"] == "LOCAL_SCOPE"}
    assert "init-00039" in messages["init-local-00002"]
    assert "create a new initiative Issue titled 'Architecture'" in messages["init-local-00003"]
    assert "'Old Thing'" in messages["init-local-00003"]
    assert not [item for item in result["anomalies"] if item["blocking"]]
    registration = result["data"]["registration"]
    assert registration["by_operation"] == {
        "label.create": 3,
        "issue.create": 1,
        "issue.label": 6,
        "sub_issue": 4,
        "blocked_by": 1,
    }
    assert legacy.github.writes() == []


def test_plan_reports_number_mismatches_and_title_differences_as_anomalies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    legacy.github.issue(4).title = "Delta renamed on GitHub"
    legacy.commit_to_origin(
        {f"{ISSUE3}/.meta.json": meta("issue", "iss-00003", "Gamma", "gamma", 33, parent="epic-00002")}, "mismatch"
    )
    code, result = legacy.run("plan")
    assert code == 1
    assert result["status"] == "problems"
    by_code = {item["code"]: item for item in result["anomalies"]}
    assert by_code["ID_NUMBER_MISMATCH"]["blocking"] is True
    assert "#33" in by_code["ID_NUMBER_MISMATCH"]["message"]
    assert by_code["TITLE_MISMATCH"]["blocking"] is False
    assert "Delta renamed on GitHub" in by_code["TITLE_MISMATCH"]["message"]


def test_plan_finds_kind_rule_cycle_missing_references_and_closed_parents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    legacy.github.issue(2).state = "closed"
    legacy.commit_to_origin(
        {
            f"{ISSUE3}/.meta.json": meta(
                "issue", "iss-00003", "Gamma", "gamma", 3, parent="init-00001", depends_on=("iss-00004", "iss-00099")
            ),
            "spec-dock/initiatives/init-00001-alpha/epics/epic-00002-beta/issues/iss-00004-delta/.meta.json": meta(
                "issue", "iss-00004", "Delta", "delta", 4, parent="epic-00002", depends_on=("iss-00003",)
            ),
        },
        "broken",
    )
    code, result = legacy.run("plan")
    assert code == 1
    codes = _codes(result)
    assert {"KIND_RULE", "DEPENDENCY_MISSING", "DEPENDENCY_CYCLE", "CLOSED_PARENT_OPEN_CHILD"} <= set(codes)


def test_plan_shows_ci_lines_worktrees_local_files_and_a_head_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    changed = add_worktree(legacy.main, tmp_path / "feature", "feature")
    write_files(changed, {f"{ISSUE3}/plan.md": b"# edited\n", f"{ISSUE3}/notes.md": b"new\n"})
    git(changed, "add", "--", f"{ISSUE3}/plan.md")
    git(changed, "commit", "-qm", "spec edit")
    write_files(changed, {f"{ISSUE3}/plan.md": b"# edited twice\n"})
    clean = add_worktree(legacy.main, tmp_path / "clean", "clean")
    gone = add_worktree(legacy.main, tmp_path / "gone", "gone")
    subprocess.run(["rm", "-rf", str(gone)], check=True)
    write_files(legacy.main, {f"{ISSUE3}/.workbench/note.md": b"ignored\n", f"{ISSUE3}/draft.md": b"untracked\n"})
    git(legacy.main, "commit", "-q", "--allow-empty", "-m", "local only")
    before = snapshot(legacy)
    code, result = legacy.run("plan")
    assert code == 0, result
    assert snapshot(legacy) == before
    steps = result["data"]["ci_steps"]
    assert [(s["path"], s["line"]) for s in steps] == [(".github/workflows/ci.yml", 8), (".github/workflows/ci.yml", 9)]
    worktrees = {item["path"]: item for item in result["data"]["worktrees"]}
    assert worktrees[str(changed)]["spec_changes"]["committed"] == [f"{ISSUE3}/plan.md"]
    assert sorted(worktrees[str(changed)]["spec_changes"]["uncommitted"]) == [f"{ISSUE3}/notes.md", f"{ISSUE3}/plan.md"]
    assert worktrees[str(clean)]["spec_changes"] == {"committed": [], "uncommitted": []}
    assert worktrees[str(gone)].get("missing") is True
    assert result["data"]["main_local_files"] == 2
    assert any("HEAD" in warning for warning in result["warnings"])


def test_every_subcommand_reaches_its_plan_and_writes_nothing_without_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    feature = add_worktree(legacy.main, tmp_path / "feature", "feature")
    write_files(feature, {f"{ISSUE3}/plan.md": b"# edited\n"})
    write_files(legacy.main, {f"{ISSUE3}/.workbench/note.md": b"ignored\n"})

    def dry(command: str, *args: str, expected: int = 0) -> dict:
        before = (
            snapshot(legacy),
            git(feature, "status", "--porcelain", "--ignored"),
            git(feature, "rev-parse", "HEAD"),
        )
        code, result = legacy.run(command, *args)
        assert code == expected, (command, result)
        after = (
            snapshot(legacy),
            git(feature, "status", "--porcelain", "--ignored"),
            git(feature, "rev-parse", "HEAD"),
        )
        assert after == before, command
        return result

    dry("plan")
    dry("verify", expected=1)
    assert dry("register")["data"]["operations"]
    assert legacy.run("register", apply=True)[0] == 0
    writes = len(legacy.github.writes())
    assert any(line.startswith("would undo") for line in dry("undo")["messages"])
    assert dry("build-canonical")["data"]["canonical_commit"]
    assert legacy.run("build-canonical", apply=True)[0] == 0
    assert dry("cut")["data"]["commit"]
    assert legacy.run("cut", apply=True)[0] == 0
    git(legacy.main, "fetch", "-q", "origin")
    git(legacy.main, "merge", "-q", "--ff-only", "origin/spec-dock/migrate-to-canonical")
    git(legacy.main, "push", "-q", "origin", "HEAD:main")
    git(legacy.main, "fetch", "-q", "origin")
    moves = dry("move-local", str(legacy.main))["data"]
    assert moves["create_catalog"] is True and moves["moves"]
    adopt = dry("adopt-worktree", str(feature))["data"]
    assert adopt["canonical_commit"] and f"{ISSUE3}/plan.md" in adopt["delete"]
    assert dry("export-legacy")["data"]["scopes"] == 7
    assert len(legacy.github.writes()) == writes


def test_a_missing_origin_head_stops_with_the_set_head_step(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    git(legacy.main, "remote", "set-head", "origin", "--delete")
    code, result = legacy.run("plan")
    assert code == 2 and result["status"] == "refused"
    assert any("remote set-head origin --auto" in step for step in result["next_steps"])


def test_repo_is_required_off_github_and_must_match_a_github_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.support.migration_repo import migrate_module

    legacy = build_legacy(tmp_path, monkeypatch)
    import io
    import json

    stream = io.StringIO()
    code = migrate_module().main(["plan", "--project", str(legacy.main), "--json"], runner=legacy.github, stdout=stream)
    assert code == 2 and "--repo" in json.loads(stream.getvalue())["next_steps"][0]
    git(legacy.main, "remote", "set-url", "origin", "https://github.com/example/repo.git")
    stream = io.StringIO()
    code = migrate_module().main(
        ["plan", "--project", str(legacy.main), "--repo", "other/repo", "--json"], runner=legacy.github, stdout=stream
    )
    assert code == 2 and "differs from origin" in json.loads(stream.getvalue())["error"]


def test_a_linked_worktree_is_not_accepted_as_the_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    linked = add_worktree(legacy.main, tmp_path / "linked", "linked")
    code, result = legacy.run("plan", project=linked)
    assert code == 2 and "main checkout" in result["error"]


def test_writing_commands_stop_when_the_local_default_branch_is_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    legacy.commit_to_origin({"README.md": b"later\n"}, "later")
    git(legacy.main, "update-ref", "refs/remotes/origin/main", "HEAD")
    before = snapshot(legacy)
    for command in ("register", "build-canonical", "cut"):
        code, result = legacy.run(command, apply=True)
        assert code == 2, (command, result)
        assert any("fetch origin" in step for step in result["next_steps"])
    assert snapshot(legacy) == before
    code, result = legacy.run("plan")
    assert any("fetch origin" in warning for warning in result["warnings"])


def test_the_script_runs_standalone_with_gh_on_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import json
    import sys

    from tests.support.fake_github import install_fake_gh
    from tests.support.migration_repo import SCRIPT

    legacy = build_legacy(tmp_path, monkeypatch)
    install_fake_gh(tmp_path, monkeypatch, legacy.github)
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            str(SCRIPT),
            "plan",
            "--project",
            str(legacy.main),
            "--repo",
            "example/repo",
            "--state-dir",
            str(legacy.state),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["data"]["scopes"]["total"] == 7
    text = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "plan", "--project", str(legacy.main), "--repo", "example/repo"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )
    assert text.returncode == 0 and "migrate.py plan: ok" in text.stdout and "LOCAL_SCOPE" in text.stdout


def test_the_readme_covers_preparation_rehearsal_cutover_rollback_and_scopeless_repositories() -> None:
    from tests.support.migration_repo import SCRIPT

    readme = (SCRIPT.parent / "README.md").read_text(encoding="utf-8")
    for heading in ("## 準備", "## 予行演習", "## 本番", "## 戻し方", "## Scope のないリポジトリ"):
        assert heading in readme
    for command in (
        "plan",
        "register",
        "verify",
        "undo",
        "build-canonical",
        "cut",
        "move-local",
        "adopt-worktree",
        "export-legacy",
    ):
        assert f"`{command}" in readme
    assert "idmap.json" in readme and "--no-schedule" in readme
    for text in ("## 平らにする写し", "<区切り>/<ID>/", "unrewritable", "data.history", "untitled", "SCOPE_KIND_CHANGED"):
        assert text in readme
    assert "slug の印" not in readme and "spec-dock:slug" not in readme
    assert (SCRIPT.parent / ".gitignore").read_text() == "/.state/\n"

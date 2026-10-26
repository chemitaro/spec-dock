"""spec-dock canonical check judges one committed code tree, whatever the working tree declares (AC-434-01..05)."""

from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock import __version__
from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_check import code_repository, commit, git, stage_gitlink, use_assets_with_ignore_rules

if TYPE_CHECKING:
    from pathlib import Path


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, Any]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_a_clean_code_tree_passes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 0, result
    assert result["command"] == "canonical check" and result["status"] == "succeeded"
    assert result["effects"] == [] and result["error"] is None and result["warnings"] == []
    data = result["data"]
    assert data["kind"] == "canonical-check"
    assert data["result"]["valid"] is True and data["result"]["failures"] == []
    assert data["result"]["revision"] == "HEAD" and len(data["result"]["commit"]) == 40
    assert data["result"]["package_version"] == __version__


def _problem(root: Path, problem: str) -> None:
    """Commit one way a code tree can break the default-branch rules."""
    if problem == "spec-file":
        (root / "spec-dock/initiatives/init-00001-plan").mkdir(parents=True)
        (root / "spec-dock/initiatives/init-00001-plan/requirement.md").write_text("spec\n", encoding="utf-8")
    elif problem == "spec-link":
        (root / "spec-dock/initiatives").symlink_to(".canonical")
        git(root, "add", "--force", "--", "spec-dock/initiatives")
    elif problem in ("spec-gitlink", "catalog-gitlink"):
        stage_gitlink(root, "spec-dock/initiatives" if problem == "spec-gitlink" else "spec-dock/.canonical")
        commit(root, problem, stage=False)
        return
    elif problem == "catalog-file":
        (root / "spec-dock/.canonical").mkdir()
        (root / "spec-dock/.canonical/README.md").write_text("catalog\n", encoding="utf-8")
        git(root, "add", "--force", "--", "spec-dock/.canonical/README.md")
    elif problem == "scope-metadata":
        (root / "spec-dock/artifacts").mkdir()
        (root / "spec-dock/artifacts/.meta.json").write_text("{}\n", encoding="utf-8")
    elif problem == "schema-3":
        (root / "spec-dock/workspace.json").write_text(
            json.dumps({"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}), encoding="utf-8"
        )
    elif problem == "asset-modified":
        (root / "spec-dock/docs/README.md").write_text("edited\n", encoding="utf-8")
    elif problem == "asset-deleted":
        (root / "spec-dock/docs/README.md").unlink()
    elif problem == "asset-symlink":
        (root / "spec-dock/docs/README.md").unlink()
        (root / "spec-dock/docs/README.md").symlink_to("guide.md")
    elif problem == "ignore-rules":
        gitignore = root / "spec-dock/.gitignore"
        kept = [line for line in gitignore.read_text(encoding="utf-8").splitlines() if line != "/initiatives"]
        gitignore.write_text("\n".join(kept) + "\n", encoding="utf-8")
    commit(root, problem)


@pytest.mark.parametrize(
    ("problem", "expected"),
    [
        ("spec-file", [("SPEC_PATH_TRACKED", "spec-dock/initiatives/init-00001-plan/requirement.md")]),
        ("spec-link", [("SPEC_PATH_TRACKED", "spec-dock/initiatives")]),
        ("spec-gitlink", [("SPEC_PATH_TRACKED", "spec-dock/initiatives")]),
        ("catalog-file", [("CATALOG_PATH_TRACKED", "spec-dock/.canonical/README.md")]),
        ("catalog-gitlink", [("CATALOG_PATH_TRACKED", "spec-dock/.canonical")]),
        ("scope-metadata", [("SCOPE_METADATA_TRACKED", "spec-dock/artifacts/.meta.json")]),
        ("schema-3", [("WORKSPACE_NOT_MIGRATED", "spec-dock/workspace.json")]),
        ("asset-modified", [("STATIC_ASSET_INVALID", "spec-dock/docs/README.md")]),
        ("asset-deleted", [("STATIC_ASSET_INVALID", "spec-dock/docs/README.md")]),
        ("asset-symlink", [("STATIC_ASSET_INVALID", "spec-dock/docs/README.md")]),
        (
            "ignore-rules",
            [("STATIC_ASSET_INVALID", "spec-dock/.gitignore"), ("IGNORE_RULES_MISSING", "spec-dock/.gitignore")],
        ),
    ],
)
def test_each_default_branch_problem_fails_with_its_path_and_next_step(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    problem: str,
    expected: list[tuple[str, str]],
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    _problem(root, problem)
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 7, result
    assert result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    assert result["error"]["details"]["failure_count"] == len(expected)
    failures = result["data"]["result"]["failures"]
    assert [(item["code"], item["details"]["path"]) for item in failures] == expected
    assert all(item["details"]["next_step"] for item in failures)
    assert result["recovery"]["instructions"] == list(dict.fromkeys(item["details"]["next_step"] for item in failures))
    assert result["data"]["result"]["valid"] is False


def test_a_schema_three_commit_lists_every_problem_instead_of_stopping(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    for problem in ("spec-file", "catalog-file", "scope-metadata", "schema-3", "asset-modified"):
        _problem(root, problem)
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 7 and result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    assert [item["code"] for item in result["data"]["result"]["failures"]] == [
        "SPEC_PATH_TRACKED",
        "CATALOG_PATH_TRACKED",
        "SCOPE_METADATA_TRACKED",
        "WORKSPACE_NOT_MIGRATED",
        "STATIC_ASSET_INVALID",
    ]


@pytest.mark.parametrize("working_declaration", ["schema-3", "schema-4", "absent", "corrupt"])
def test_the_working_tree_declaration_never_decides_the_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    working_declaration: str,
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    declaration = root / "spec-dock/workspace.json"
    if working_declaration == "schema-3":
        declaration.write_text('{"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}')
    elif working_declaration == "absent":
        declaration.unlink()
    elif working_declaration == "corrupt":
        declaration.write_text("{broken")

    def no_context(*args: object, **kwargs: object) -> object:
        raise AssertionError("canonical check must not resolve the workspace context")

    monkeypatch.setattr("spec_dock.runtime.application.project_context.resolve_context", no_context)
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 0 and result["data"]["result"]["valid"] is True, result


def test_it_runs_without_network_tokens_or_state_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    _problem(root, "spec-file")
    state = tmp_path / "state"
    only_git = tmp_path / "bin"
    only_git.mkdir()
    (only_git / "git").symlink_to(shutil.which("git") or "/usr/bin/git")
    monkeypatch.setenv("PATH", str(only_git))
    for name in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    assert shutil.which("gh") is None
    before = tree_digest(root)
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 7 and result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    assert tree_digest(root) == before and not state.exists()


def test_a_different_running_version_warns_and_keeps_the_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    monkeypatch.setattr("spec_dock.runtime.application.canonical_check.__version__", "9.9.9")
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 0 and result["status"] == "succeeded"
    (warning,) = result["warnings"]
    assert warning["code"] == "SPEC_DOCK_VERSION_MISMATCH"
    assert warning["details"]["expected"] == "9.9.9"
    assert warning["details"]["actual"] == (root / "spec-dock/system/spec-dock-version").read_text().strip()


def test_commit_selects_the_tree_to_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    clean = git(root, "rev-parse", "HEAD").strip()
    _problem(root, "spec-file")
    assert _run(capsys, "--project", str(root), "canonical", "check")[0] == 7
    code, result = _run(capsys, "--project", str(root), "canonical", "check", "--commit", clean[:12])
    assert code == 0 and result["data"]["result"]["commit"] == clean
    assert result["data"]["result"]["revision"] == clean[:12]


@pytest.mark.parametrize("case", ["unknown-commit", "not-a-commit", "no-commit-yet"])
def test_a_missing_commit_stops_before_checking_with_a_next_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    if case in ("unknown-commit", "not-a-commit"):
        root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
        argv = ["--commit", "no-such-branch" if case == "unknown-commit" else "HEAD^{tree}"]
    else:
        root = tmp_path / "empty"
        root.mkdir()
        git(root, "init", "-q", "-b", "main")
        argv = []
    code, result = _run(capsys, "--project", str(root), "canonical", "check", *argv)
    assert code == 3 and result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "PRECONDITION_FAILED"
    assert "--commit" in result["recovery"]["instructions"][0]


def test_expectation_guards_cannot_be_checked_against_a_commit_tree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    for guard in ("--expect-current", "--expect-backend"):
        value = "iss-00001" if guard == "--expect-current" else "github"
        code, result = _run(capsys, "--project", str(root), "canonical", "check", guard, value)
        assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED"
        assert "without --expect-current and --expect-backend" in result["recovery"]["instructions"][0]


def test_text_output_lists_each_failure_with_its_path_and_next_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    _problem(root, "spec-file")
    assert main(["--project", str(root), "canonical", "check"]) == 7
    output = capsys.readouterr()
    head = git(root, "rev-parse", "HEAD").strip()
    assert output.out.splitlines()[:3] == [
        "spec-dock: failed (canonical check)",
        f"commit={head} valid=false failures=1",
        'failure [SPEC_PATH_TRACKED] path="spec-dock/initiatives/init-00001-plan/requirement.md" '
        'next_step="Remove the spec paths from this branch with git rm -r --cached -- spec-dock/initiatives, '
        'then commit; specs belong on the spec-dock/canonical branch."',
    ]
    assert "error [CANONICAL_CHECK_FAILED]" in output.err
    assert "recovery: Remove the spec paths from this branch" in output.err


def test_a_legacy_schema_three_repository_reports_its_specs_and_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_work_start import committed_workspace

    root = committed_workspace((tmp_path / "legacy").resolve())
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    assert code == 7 and result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    codes = {item["code"] for item in result["data"]["result"]["failures"]}
    assert {"SPEC_PATH_TRACKED", "WORKSPACE_NOT_MIGRATED"} <= codes


def test_text_output_shows_the_next_step_of_a_version_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    monkeypatch.setattr("spec_dock.runtime.application.canonical_check.__version__", "9.9.9")
    assert main(["--project", str(root), "canonical", "check"]) == 0
    output = capsys.readouterr()
    assert (
        'warning [SPEC_DOCK_VERSION_MISMATCH] path="spec-dock/system/spec-dock-version" '
        'next_step="Run the SpecDock version named by spec-dock/system/spec-dock-version, '
        'or run spec-dock installation update and commit to record this version."'
    ) in output.out.splitlines()
    assert "warning [SPEC_DOCK_VERSION_MISMATCH]" in output.err


def test_dry_run_follows_the_read_only_planning_rule_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = code_repository(tmp_path / "repo", use_assets_with_ignore_rules(monkeypatch))
    before = tree_digest(root)
    code, result = _run(capsys, "--project", str(root), "canonical", "check", "--dry-run")
    assert code == 0 and result["status"] == "planned" and result["effects"] == []
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["valid"] is True
    assert tree_digest(root) == before
    _problem(root, "spec-file")
    before = tree_digest(root)
    code, result = _run(capsys, "--project", str(root), "canonical", "check", "--dry-run")
    assert code == 7 and result["status"] == "failed" and result["data"]["result"]["can_apply"] is False
    assert tree_digest(root) == before


def test_the_shipped_package_fails_only_for_the_ignore_rules_until_its_gitignore_carries_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.application.canonical_check import SPEC_DOCK_GITIGNORE, SPEC_DOCK_IGNORE_LINES
    from spec_dock.runtime.infra.static_assets import package_static_assets

    assets = package_static_assets()
    shipped = next(asset for asset in assets if asset.path == SPEC_DOCK_GITIGNORE).payload.decode().splitlines()
    root = code_repository(tmp_path / "repo", assets)
    code, result = _run(capsys, "--project", str(root), "canonical", "check")
    if all(line in shipped for line in SPEC_DOCK_IGNORE_LINES):
        assert code == 0, result
    else:
        assert code == 7
        assert [item["code"] for item in result["data"]["result"]["failures"]] == ["IGNORE_RULES_MISSING"]


def test_the_shipped_assets_pass_without_overlaying_the_ignore_rules(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    from spec_dock.runtime.infra.static_assets import package_static_assets
    from tests.support.canonical_check import assets_with_ignore_rules, gitignore_with_ignore_rules

    shipped = package_static_assets()
    gitignore = next(asset for asset in shipped if asset.path == "spec-dock/.gitignore")
    assert gitignore_with_ignore_rules(gitignore.payload) == gitignore.payload
    assert assets_with_ignore_rules() == shipped
    root = code_repository(tmp_path / "repo", shipped)
    code = main(["--project", str(root), "canonical", "check", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert "IGNORE_RULES_MISSING" not in [item["code"] for item in result["data"]["result"]["failures"]]
    assert code == 0, result

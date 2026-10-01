"""Public contracts for the external CLI without repository control (Issue #413)."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest


def test_scope_read_help_explains_current_metadata_and_unobserved_github_state(
    capsys: pytest.CaptureFixture[str],
) -> None:
    for leaf in ("list", "show"):
        assert main(["scope", leaf, "--help"]) == 0
        help_text = capsys.readouterr().out
        assert "unknown" in help_text and "Current metadata" in help_text
        assert "cached state" not in help_text and "specdock.cli/v2" in help_text


def make_workspace(root: Path) -> Path:
    """Build a GitHub-backed schema-3 test fixture, never real dogfood metadata."""
    root.mkdir()
    subprocess.run(["git", "init", "--initial-branch=main", "-q", str(root)], check=True, capture_output=True)
    workspace = root / "spec-dock"
    scope = workspace / "initiatives/init-00001-fixture"
    scope.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        '{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n', encoding="utf-8"
    )
    (workspace / ".gitignore").write_text(".agent/\n.workbench/\n", encoding="utf-8")
    (scope / ".meta.json").write_text(
        json.dumps({
            "schema_version": 3,
            "id": "init-00001",
            "type": "initiative",
            "title": "Fixture",
            "slug": "fixture",
            "parent_id": None,
            "initiative_id": None,
            "epic_id": None,
            "backend": "github",
            "github": {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"},
            "lifecycle": None,
            "revision": 0,
            "depends_on": [],
            "created_at": "2026-09-30T00:00:00Z",
            "updated_at": "2026-09-30T00:00:00Z",
        })
        + "\n",
        encoding="utf-8",
    )
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (scope / filename).write_text("# Fixture\n", encoding="utf-8")
    return root


def test_independent_scope_read_does_not_require_control(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()

    exit_code = main(["--project", str(root), "scope", "show", "init-00001", "--json"])

    output = capsys.readouterr()
    assert exit_code == 0, output.out + output.err
    result = json.loads(output.out)
    assert result["data"]["result"]["scope"]["id"] == "init-00001"
    assert result["data"]["result"]["scope"]["status"]["state"] == "unknown"
    assert result["effects"] == []
    assert not output.err
    assert metadata.read_bytes() == before
    assert not (root / ".git/spec-dock").exists()


def test_scope_read_dry_run_exposes_a_valid_preview_without_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()
    assert main(["--project", str(root), "scope", "show", "init-00001", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert metadata.read_bytes() == before and result["effects"] == []
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_scope_text_read_displays_the_target_authority_and_path_without_changing_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    assert main(["--project", str(root), "scope", "show", "init-00001"]) == 0
    output = capsys.readouterr()
    for value in ("init-00001", "Fixture", "github", "unknown", "spec-dock/initiatives/init-00001-fixture"):
        assert value in output.out, output.out
    assert output.err == "" and tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_active_text_read_displays_empty_or_selected_direct_and_current_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = make_workspace(tmp_path / "consumer")
    for selected in (False, True):
        if selected:
            select_fixture(root)
        before = tree_digest(root)
        assert main(["--project", str(root), "active", "show"]) == 0
        output = capsys.readouterr()
        assert ("selected" if selected else "empty") in output.out
        if selected:
            assert "init-00001" in output.out and "gh:example/repo#1" in output.out
        assert "main" in output.out and output.err == ""
        assert tree_digest(root) == before and not (root / ".git/spec-dock").exists()


def test_every_public_leaf_help_describes_the_v2_envelope_without_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.cli.catalog import LEAF_PATHS

    assert len(LEAF_PATHS) == 44
    for leaf in LEAF_PATHS:
        assert main(["--project", str(tmp_path / "missing"), "help", *leaf.split(), "--json"]) == 0
        output = capsys.readouterr()
        result = json.loads(output.out)
        assert result["schema_version"] == "specdock.cli/v2" and result["effects"] == [] and output.err == ""
        help_text = result["data"]["text"]
        assert "specdock.cli/v2" in help_text and "specdock.cli/v1" not in help_text, leaf
    assert list(tmp_path.iterdir()) == []


def test_project_root_with_crlf_is_not_normalized(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_workspace(tmp_path / "consumer\r\nname")
    assert main(["--project", str(root), "scope", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["id"] == "init-00001"


def test_scope_state_filter_does_not_adopt_retired_status_cache(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    agent = root / "spec-dock/.agent"
    agent.mkdir()
    cache = agent / "github-status-cache.json"
    cache.write_text(
        json.dumps({
            "schema_version": 1,
            "items": {
                "init-00001": {
                    "github_ref": "gh:example/repo#1",
                    "state": "completed",
                    "observed_at": "2026-09-29T00:00:00Z",
                }
            },
        })
    )
    before = cache.read_bytes()
    assert main(["--project", str(root), "scope", "list", "--state", "completed", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["items"] == []
    assert result["data"]["result"]["unknown_filtered_count"] == 1
    assert cache.read_bytes() == before
    assert not output.err


def test_old_writer_workspace_is_readable_without_control(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_workspace(tmp_path / "consumer")
    declaration = root / "spec-dock/workspace.json"
    declaration.write_text('{"schema_version":3,"writer_protocol":"specdock.writer/v1"}\n')
    before = declaration.read_bytes()
    assert main(["--project", str(root), "scope", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "succeeded"
    assert declaration.read_bytes() == before


def test_active_show_empty_is_read_only_and_does_not_create_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    assert main(["--project", str(root), "active", "show", "--json"]) == 0
    output = capsys.readouterr()
    data = json.loads(output.out)["data"]
    assert data["kind"] == "active"
    assert data["selection"]["status"] == "empty"
    assert data["selection"]["scope_id"] is None
    assert data["ancestors"] == []
    assert not (root / "spec-dock/.agent").exists()
    assert not (root / ".git/spec-dock").exists()


def test_dynamic_scope_uses_direct_record_and_keeps_it_stale_when_scope_disappears(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.application.project_context import resolve_context
    from spec_dock.runtime.domain.work_target import WorkTarget
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    root = make_workspace(tmp_path / "consumer")
    context = resolve_context(str(root), root)
    with WorkTargetStore(root) as store:
        handle = store.publish(
            WorkTarget(
                "specdock.work-target/v1",
                "init-00001",
                "gh:example/repo#1",
                "selected-branch",
                "2026-09-30T00:00:00Z",
                context.clone_identity,
                context.worktree_identity,
            )
        )
        path = store.path / handle.basename
        before = path.read_bytes()
        assert main(["--project", str(root), "scope", "show", "@current", "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["data"]["result"]["scope"]["id"] == "init-00001"
        metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
        metadata.unlink()
        # Missing metadata is an incomplete tree, never an empty selection.
        assert main(["--project", str(root), "scope", "show", "@current", "--json"]) != 0
        capsys.readouterr()
        assert path.read_bytes() == before


def add_scope(root: Path, scope_id: str, kind: str, parent_id: str, parent: Path) -> Path:
    metadata = json.loads((root / "spec-dock/initiatives/init-00001-fixture/.meta.json").read_bytes())
    path = parent / ("epics" if kind == "epic" else "issues") / f"{scope_id}-fixture"
    path.mkdir(parents=True)
    (path / ".meta.json").write_text(
        json.dumps(
            dict(
                metadata,
                id=scope_id,
                type=kind,
                parent_id=parent_id,
                initiative_id="init-00001",
                epic_id=parent_id if kind == "issue" else None,
                github=dict(metadata["github"], issue_number=int(scope_id.split("-")[-1])),
            )
        )
    )
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (path / filename).write_text("# Fixture\n", encoding="utf-8")
    return path

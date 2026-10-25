"""Schema-4 workspaces enter canonical mode; commands without a canonical handler stop without writing."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.cli.catalog import LEAF_PATHS
from spec_dock.runtime.commands.canonical_dispatch import CANONICAL_HANDLERS, REPOSITORY_INDEPENDENT_HANDLERS
from spec_dock.runtime.infra.tree_backup import tree_digest

if TYPE_CHECKING:
    from pathlib import Path

NEW = "specdock.worktree-writer/v1"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def canonical_workspace(root: Path, declaration: object | None = None) -> Path:
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "--local", "maintenance.auto", "false")
    (root / "spec-dock").mkdir()
    payload = {"schema_version": 4, "writer_protocol": NEW} if declaration is None else declaration
    (root / "spec-dock/workspace.json").write_text(json.dumps(payload), encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    return root


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, Any]:
    code = main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def _leaf_arguments(root: Path, outside: Path) -> dict[str, list[str]]:
    source = str(outside / "evidence.txt")
    other = str(outside / "other-worktree")
    return {
        "scope create initiative": ["--backend", "github", "--title", "Plan", "--yes"],
        "scope create epic": ["--backend", "github", "--parent", "init-00001", "--title", "Core", "--yes"],
        "scope create issue": ["--backend", "github", "--parent", "epic-00002", "--title", "Leaf", "--yes"],
        "scope import github initiative": ["gh:example/repo#1", "--title", "Plan", "--yes"],
        "scope import github epic": ["gh:example/repo#2", "--parent", "init-00001", "--title", "Core", "--yes"],
        "scope import github issue": ["gh:example/repo#3", "--parent", "epic-00002", "--title", "Leaf", "--yes"],
        "scope list": [],
        "scope show": ["init-00001"],
        "scope edit": ["init-00001", "--title", "Renamed", "--yes"],
        "scope close": ["init-00001", "--yes"],
        "scope reopen": ["init-00001", "--yes"],
        "scope delete": ["init-00001", "--yes"],
        "active show": [],
        "active set": ["init-00001", "--yes"],
        "active clear": ["--all", "--yes"],
        "work start": ["init-00001", "--base", "HEAD", "--yes"],
        "work finish": ["init-00001", "--yes"],
        "branch show": ["init-00001"],
        "branch create": ["init-00001", "--base", "HEAD", "--yes"],
        "branch switch": ["init-00001", "--yes"],
        "dependency list": ["init-00001"],
        "dependency check": ["init-00001"],
        "dependency add": ["--from", "iss-00003", "--to", "iss-00004", "--yes"],
        "dependency remove": ["--from", "iss-00003", "--to", "iss-00004", "--yes"],
        "artifact create": ["--scope", "init-00001", "--type", "blank", "--title", "Note", "--yes"],
        "artifact import file": [source, "--scope", "init-00001", "--yes"],
        "artifact list": ["--scope", "init-00001"],
        "artifact show": ["20261026t000000z-note", "--scope", "init-00001"],
        "worktree create": ["feature", "--base", "HEAD", "--root", str(outside), "--yes"],
        "worktree list": [],
        "worktree show": [str(root)],
        "worktree remove": [other, "--yes"],
        "worktree bootstrap": [other, "--yes"],
        "workbench copy": ["--scope", "init-00001", "--to-worktree", other, "--yes"],
        "workspace sync": [],
        "workspace validate": [],
        "workspace doctor": [],
    }


def test_every_command_without_a_canonical_handler_stops_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = canonical_workspace(tmp_path / "consumer")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "evidence.txt").write_text("evidence\n", encoding="utf-8")
    arguments = _leaf_arguments(root, outside)
    excluded = {"help", "completion", "workspace migrate"} | {
        leaf for leaf in LEAF_PATHS if leaf.startswith("installation ")
    }
    assert set(arguments) == set(LEAF_PATHS) - excluded
    variants = [(leaf, extra) for leaf, extra in arguments.items()]
    variants += [("workspace validate", ["--ci"]), ("workspace doctor", ["--raw"])]
    before = tree_digest(root), tree_digest(outside)
    for leaf, extra in variants:
        if leaf in CANONICAL_HANDLERS or leaf in REPOSITORY_INDEPENDENT_HANDLERS:
            continue
        code, result = _run(capsys, "--project", str(root), *leaf.split(), *extra)
        assert code == 3, (leaf, result)
        assert result["status"] == "failed" and result["effects"] == []
        assert result["error"]["code"] == "CANONICAL_NOT_IMPLEMENTED", (leaf, result)
        assert "SpecDock 0.3.0" in result["recovery"]["instructions"][0]
        assert (tree_digest(root), tree_digest(outside)) == before, leaf


def test_text_output_shows_the_next_step(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = canonical_workspace(tmp_path / "consumer")
    assert main(["--project", str(root), "scope", "list"]) == 3
    stderr = capsys.readouterr().err
    assert "error [CANONICAL_NOT_IMPLEMENTED]" in stderr and "recovery: Wait for SpecDock 0.3.0" in stderr


@pytest.mark.parametrize(
    "declaration",
    [
        {"schema_version": 5, "writer_protocol": NEW},
        {"schema_version": True, "writer_protocol": NEW},
        {"schema_version": "4", "writer_protocol": NEW},
        {"schema_version": 4, "writer_protocol": "specdock.unknown/v9"},
    ],
)
def test_unknown_declarations_still_fail_the_precondition(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], declaration: dict[str, object]
) -> None:
    root = canonical_workspace(tmp_path / "consumer", declaration)
    code, result = _run(capsys, "--project", str(root), "scope", "list")
    assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED"


@pytest.mark.parametrize(
    "flags", [["--dry-run"], ["--backup-dir", "{backup}", "--confirm-old-writers-stopped", "--yes"]]
)
def test_workspace_migrate_is_not_applicable_and_keeps_the_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], flags: list[str]
) -> None:
    root = canonical_workspace(tmp_path / "consumer")
    declaration = (root / "spec-dock/workspace.json").read_bytes()
    before = tree_digest(root)
    argv = [str(tmp_path / "backup") if flag == "{backup}" else flag for flag in flags]
    code, result = _run(
        capsys,
        "--project",
        str(root),
        "workspace",
        "migrate",
        "--to-schema",
        "3",
        "--to-writer-protocol",
        NEW,
        *argv,
    )
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_APPLICABLE"
    assert result["recovery"]["instructions"]
    assert (root / "spec-dock/workspace.json").read_bytes() == declaration and tree_digest(root) == before
    assert not (tmp_path / "backup").exists()


def _uninitialized(root: Path) -> Path:
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    return root


@pytest.mark.parametrize("flags", [["--dry-run"], ["--yes"]])
def test_installation_init_declares_schema_four_and_names_the_next_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], flags: list[str]
) -> None:
    target = _uninitialized(tmp_path / "fresh")
    code, result = _run(capsys, "installation", "init", str(target), *flags)
    assert code == 0
    warnings = result["warnings"]
    assert [item["code"] for item in warnings] == ["CANONICAL_NOT_LINKED"]
    assert warnings[0]["details"]["next_step"] == "spec-dock canonical link"
    if flags == ["--yes"]:
        assert json.loads((target / "spec-dock/workspace.json").read_bytes()) == {
            "schema_version": 4,
            "writer_protocol": NEW,
        }


def test_installation_show_update_and_uninstall_accept_schema_four(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from pathlib import Path

    target = _uninitialized(tmp_path / "fresh")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    code, shown = _run(capsys, "installation", "show", "--target", str(target))
    data = shown["data"]["result"]
    assert code == 0 and data["workspace"]["schema_version"] == 4
    assert all(asset["classification"] == "current" for asset in data["assets"])
    code, planned = _run(capsys, "installation", "update", "--target", str(target), "--dry-run")
    assert code == 0 and planned["status"] == "planned"
    legacy_shim = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-shim.txt").read_bytes()
    (target / "spec-dock/scripts/spec-dock").write_bytes(legacy_shim)
    code, updated = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "update"), "--yes"
    )
    assert code == 0 and updated["data"]["result"]["changed_paths"] == ["spec-dock/scripts/spec-dock"]
    declaration = (target / "spec-dock/workspace.json").read_bytes()
    code, removed = _run(
        capsys, "installation", "uninstall", "--target", str(target), "--backup-dir", str(tmp_path / "remove"), "--yes"
    )
    assert code == 0 and "spec-dock/scripts/spec-dock" in removed["data"]["result"]["retired_paths"]
    assert (target / "spec-dock/workspace.json").read_bytes() == declaration


def test_schema_four_with_the_old_writer_protocol_cannot_update(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _uninitialized(tmp_path / "fresh")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    (target / "spec-dock/workspace.json").write_text(
        json.dumps({"schema_version": 4, "writer_protocol": "specdock.writer/v1"}), encoding="utf-8"
    )
    code, result = _run(capsys, "installation", "update", "--target", str(target), "--dry-run")
    assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED"


@pytest.mark.parametrize(
    "command",
    [["installation", "show"], ["installation", "update", "--dry-run"], ["installation", "uninstall", "--dry-run"]],
)
def test_expect_current_on_a_schema_four_installation_is_not_implemented(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], command: list[str]
) -> None:
    target = _uninitialized(tmp_path / "fresh")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    before = tree_digest(target)
    code, result = _run(capsys, *command, "--target", str(target), "--expect-current", "init-00001")
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_IMPLEMENTED"
    assert tree_digest(target) == before


def test_schema_three_installation_show_reports_the_old_declaration_as_known_old(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _uninitialized(tmp_path / "fresh")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    (target / "spec-dock/workspace.json").write_text(
        '{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n', encoding="utf-8"
    )
    code, shown = _run(capsys, "installation", "show", "--target", str(target))
    data = shown["data"]["result"]
    classes = {asset["path"]: asset["classification"] for asset in data["assets"]}
    assert code == 0 and data["workspace"]["schema_version"] == 3
    assert classes.pop("spec-dock/workspace.json") == "known-old"
    assert set(classes.values()) == {"current"}

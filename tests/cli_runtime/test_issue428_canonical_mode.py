"""Schema-4 workspaces enter canonical mode; commands without a canonical handler stop without writing."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
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


def test_text_output_shows_the_next_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # iss-00436 removed CANONICAL_NOT_IMPLEMENTED; a canonical refusal still renders its next step as text.
    root = canonical_workspace(tmp_path / "consumer")
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "migrate",
            "--to-schema",
            "3",
            "--to-writer-protocol",
            "specdock.worktree-writer/v1",
            "--dry-run",
        ])
        == 3
    )
    stderr = capsys.readouterr().err
    assert "error [CANONICAL_NOT_APPLICABLE]" in stderr and "recovery: " in stderr


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
def test_expect_current_on_a_schema_four_installation_is_checked_before_any_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], command: list[str]
) -> None:
    target = _uninitialized(tmp_path / "fresh")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    before = tree_digest(target)
    code, result = _run(capsys, *command, "--target", str(target), "--expect-current", "init-00001")
    # iss-00431 checks the expectation against the structure snapshot; this target has no GitHub origin.
    assert code == 5 and result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "GIT_FAILED"
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

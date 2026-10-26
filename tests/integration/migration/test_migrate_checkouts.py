"""migrate.py move-local, adopt-worktree and export-legacy on real checkouts (AC-435-03, 04, 10, 11, 12)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main as spec_dock_main
from spec_dock.runtime.infra import runtime_environment
from tests.support.canonical_repo import add_worktree, clone, environment, git
from tests.support.migration_repo import (
    EPIC,
    INIT,
    ISSUE3,
    ISSUE4,
    LOCAL2,
    Legacy,
    build_legacy,
    legacy_specs,
    refs,
    write_files,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

CUT = "spec-dock/migrate-to-canonical"


def _migrated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **options: Any) -> Legacy:
    legacy = build_legacy(tmp_path, monkeypatch, **options)
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: environment())
    for command in ("register", "build-canonical", "cut"):
        code, result = legacy.run(command, apply=True)
        assert code == 0, (command, result)
    return legacy


def _merge_cut(legacy: Legacy) -> None:
    """The human PR merge: origin's default branch takes the cut branch."""
    git(legacy.main, "fetch", "-q", "origin")
    git(legacy.main, "merge", "-q", "--ff-only", f"origin/{CUT}")
    git(legacy.main, "push", "-q", "origin", f"HEAD:{legacy.default_branch}")
    git(legacy.main, "fetch", "-q", "origin")


def _link(capsys: pytest.CaptureFixture[str], checkout: Path) -> tuple[int, dict[str, Any]]:
    capsys.readouterr()
    code = spec_dock_main(["--project", str(checkout), "canonical", "link", "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_move_local_moves_ignored_and_untracked_files_into_a_new_catalog_that_link_accepts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    legacy = _migrated(tmp_path, monkeypatch)
    write_files(
        legacy.main,
        {
            f"{ISSUE3}/.workbench/note.md": b"ignored note\n",
            f"{ISSUE3}/draft.md": b"untracked draft\n",
            f"{LOCAL2}/extra.md": b"local extra\n",
        },
    )
    _merge_cut(legacy)
    write_files(legacy.main, {f"{ISSUE3}/plan.md": b"# my local plan\n"})  # collides with canonical's plan.md
    code, result = legacy.run("move-local", str(legacy.main), "--pc-name", "Test.PC.local", apply=True)
    assert code == 0, result
    catalog = legacy.main / "spec-dock/.canonical"
    gamma = catalog / ISSUE3.removeprefix("spec-dock/initiatives/")
    assert (gamma / ".workbench/note.md").read_bytes() == b"ignored note\n"
    assert (gamma / "draft.md").read_bytes() == b"untracked draft\n"
    assert (gamma / "plan.md").read_bytes() == b"# Gamma plan\n"
    assert (gamma / "plan.local-test.md").read_bytes() == b"# my local plan\n"
    assert (catalog / "init-00039-proto/extra.md").read_bytes() == b"local extra\n"
    assert not (legacy.main / "spec-dock/initiatives").exists()
    worktrees = git(legacy.main, "worktree", "list", "--porcelain")
    assert f"worktree {catalog}" in worktrees and "locked spec-dock canonical catalog" in worktrees
    assert git(catalog, "rev-parse", "--abbrev-ref", "@{upstream}") == "origin/spec-dock/canonical"
    code, linked = _link(capsys, legacy.main)
    assert code == 0, linked
    assert linked["status"] == "succeeded"
    assert ("catalog.create", "succeeded") not in [(e["kind"], e["status"]) for e in linked["effects"]]
    assert (legacy.main / "spec-dock/initiatives").is_symlink()
    assert (legacy.main / "spec-dock/initiatives" / ISSUE3.removeprefix("spec-dock/initiatives/") / "draft.md").exists()


def test_move_local_refuses_tracked_specs_and_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = _migrated(tmp_path, monkeypatch)
    code, result = legacy.run("move-local", str(legacy.main), apply=True)
    assert code == 2 and "tracked files" in result["error"]
    _merge_cut(legacy)
    write_files(legacy.main, {f"{ISSUE4}/.meta.json": b"{}\n"})
    code, result = legacy.run("move-local", str(legacy.main), apply=True)
    assert code == 2 and ".meta.json" in result["error"]
    assert not (legacy.main / "spec-dock/.canonical").exists()


def _feature(legacy: Legacy, tmp_path: Path) -> Path:
    """A pre-migration branch with committed and uncommitted spec changes, created before the cut merge."""
    feature = add_worktree(legacy.main, tmp_path / "feature", "feature")
    write_files(feature, {f"{ISSUE3}/plan.md": b"# Gamma plan on the branch\n"})
    git(feature, "commit", "-qam", "branch spec edit")
    write_files(
        feature,
        {
            f"{ISSUE4}/requirement.md": b"# Delta uncommitted\n",
            f"{EPIC}/notes.md": b"new untracked spec\n",
            f"{ISSUE3}/.workbench/scratch.md": b"ignored scratch\n",
            f"{ISSUE4}/.meta.json": legacy_specs()[f"{ISSUE4}/.meta.json"].replace(b'"Delta"', b'"Delta v2"'),
        },
    )
    return feature


def test_adopt_worktree_moves_branch_specs_into_canonical_and_the_branch_merges_without_specs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = _migrated(tmp_path, monkeypatch)
    feature = _feature(legacy, tmp_path)
    _merge_cut(legacy)
    code, preview = legacy.run("adopt-worktree", str(feature))
    assert code == 0, preview
    assert f"{ISSUE4}/requirement.md" in preview["data"]["delete"] and preview["data"]["mismatched"] == []
    assert "iss-00004: title 'Delta' -> 'Delta v2'" in preview["data"]["structure_differences"]
    code, result = legacy.run("adopt-worktree", str(feature), apply=True)
    assert code == 0, result
    gamma = ISSUE3.removeprefix("spec-dock/initiatives/")
    delta = ISSUE4.removeprefix("spec-dock/initiatives/")
    beta = EPIC.removeprefix("spec-dock/initiatives/")

    def canonical(path: str) -> bytes:
        import subprocess

        return subprocess.run(
            ["git", "-C", str(legacy.remote), "cat-file", "blob", f"spec-dock/canonical:{path}"],
            check=True,
            capture_output=True,
        ).stdout

    assert canonical(f"{gamma}/plan.md") == b"# Gamma plan on the branch\n"
    assert canonical(f"{delta}/requirement.md") == b"# Delta uncommitted\n"
    assert canonical(f"{beta}/notes.md") == b"new untracked spec\n"
    assert "Delta v2" not in git(legacy.remote, "ls-tree", "-r", "--name-only", "spec-dock/canonical")
    assert git(feature, "ls-tree", "-r", "--name-only", "HEAD", "--", "spec-dock/initiatives") == ""
    assert (feature / ISSUE3 / ".workbench/scratch.md").exists()  # ignored files wait for move-local
    assert not (feature / ISSUE3 / "plan.md").exists()
    git(feature, "merge", "-q", "--no-edit", f"origin/{legacy.default_branch}")
    git(legacy.main, "merge", "-q", "--no-edit", "feature")
    assert git(legacy.main, "ls-tree", "-r", "--name-only", "HEAD", "--", "spec-dock/initiatives") == ""
    record = json.loads((legacy.records / "adopt/feature.json").read_text())
    assert "iss-00004: title 'Delta' -> 'Delta v2'" in record["structure_differences"]


def test_both_sides_changing_one_file_keeps_canonical_and_stops_before_removing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = _migrated(tmp_path, monkeypatch)
    feature = _feature(legacy, tmp_path)
    _merge_cut(legacy)
    other = clone(legacy.remote, tmp_path / "canonical-editor", "--branch", "spec-dock/canonical")
    write_files(other, {f"{ISSUE3.removeprefix('spec-dock/initiatives/')}/plan.md": b"# canonical side\n"})
    git(other, "commit", "-qam", "canonical edit")
    git(other, "push", "-q", "origin", "HEAD:spec-dock/canonical")
    code, preview = legacy.run("adopt-worktree", str(feature), "--pc-name", "box")
    assert code == 0 and preview["data"]["mismatched"] == [f"{ISSUE3}/plan.md"]
    status = git(feature, "status", "--porcelain")
    code, result = legacy.run("adopt-worktree", str(feature), "--pc-name", "box", apply=True)
    assert code == 3 and result["status"] == "stopped"
    gamma = ISSUE3.removeprefix("spec-dock/initiatives/")
    tree = git(legacy.remote, "ls-tree", "-r", "--name-only", "spec-dock/canonical", "--", gamma)
    copies = [line for line in tree.splitlines() if ".conflict-box-" in line]
    assert len(copies) == 1 and copies[0].endswith(".md")
    assert git(feature, "status", "--porcelain") == status  # nothing removed, nothing committed
    pushed = refs(legacy.remote)["refs/heads/spec-dock/canonical"]
    code, _again = legacy.run("adopt-worktree", str(feature), "--pc-name", "box", apply=True)
    assert code == 3 and refs(legacy.remote)["refs/heads/spec-dock/canonical"] == pushed  # already adopted: no push


def test_an_unchanged_worktree_only_drops_the_spec_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = _migrated(tmp_path, monkeypatch)
    plain = add_worktree(legacy.main, tmp_path / "plain", "plain")
    _merge_cut(legacy)
    before = refs(legacy.remote)
    code, result = legacy.run("adopt-worktree", str(plain), apply=True)
    assert code == 0, result
    assert refs(legacy.remote) == before
    assert not (plain / "spec-dock/initiatives").exists()
    git(plain, "merge", "-q", "--no-edit", f"origin/{legacy.default_branch}")
    assert git(plain, "ls-tree", "-r", "--name-only", "HEAD", "--", "spec-dock/initiatives") == ""


def test_export_legacy_rebuilds_schema_three_metadata_that_legacy_commands_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    legacy = _migrated(tmp_path, monkeypatch)
    _merge_cut(legacy)
    legacy.github.issue(4).title = "デルタ（日本語の題名）"
    writes = len(legacy.github.writes())
    main_refs = refs(legacy.main)
    code, result = legacy.run("export-legacy", apply=True)
    assert code == 0, result
    assert len(legacy.github.writes()) == writes and refs(legacy.main) == main_refs
    checkout = clone(legacy.remote, tmp_path / "exported", "--branch", "spec-dock/export-legacy")
    original = legacy_specs()
    renamed = {"init-local-00002": "init-00039", "init-local-00003": "init-00040"}
    for path, payload in original.items():
        if not path.endswith(".meta.json"):
            continue
        target = path
        for old, new in renamed.items():
            target = target.replace(f"{old}-", f"{new}-")
        produced = (checkout / target).read_bytes()
        if path == f"{ISSUE4}/.meta.json":
            before, after = json.loads(payload), json.loads(produced)
            assert after.pop("title") == "デルタ（日本語の題名）" and before.pop("title") == "Delta"
            assert after.pop("revision") == before.pop("revision") + 1
            assert after == before
            assert produced.startswith(b"{\n  ")  # the original indented style
        elif any(old in path for old in renamed) or "epic-00005" in path:
            before, after = json.loads(payload), json.loads(produced)
            for item in (before, after):
                item.pop("revision")
                for key in ("id", "parent_id", "initiative_id"):
                    if isinstance(item.get(key), str):
                        item[key] = renamed.get(item[key], item[key])
            if path.startswith("spec-dock/initiatives/init-local-00003"):
                before["github"]["issue_number"] = 40
            assert after == before
        else:
            assert produced == payload, path
    assert (checkout / "spec-dock/workspace.json").read_bytes() == (
        legacy.root / "seed/spec-dock/workspace.json"
    ).read_bytes()
    assert not (checkout / ".github/workflows/spec-dock-check.yml").exists()
    assert (checkout / INIT / "requirement.md").read_bytes() == b"# Alpha\n"
    capsys.readouterr()
    assert spec_dock_main(["--project", str(checkout), "workspace", "validate", "--json"]) == 0, capsys.readouterr().out
    capsys.readouterr()
    assert spec_dock_main(["--project", str(checkout), "scope", "show", "iss-00004", "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert "デルタ" in json.dumps(shown, ensure_ascii=False)

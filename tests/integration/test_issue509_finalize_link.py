"""The Grill finalizer passes through the version-4 `spec-dock/initiatives` catalog link only (iss-00509)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from tests.integration.test_issue413_assets import uninitialized_worktree

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py"
HELPER = ROOT / "src/spec_dock/assets/install_root" / SKILL
PREVIOUS = ROOT / "tests/fixtures/issue509/finalize-artifact-0.5.0.txt"
RELATIVE = "spec-dock/initiatives/00000-00999/iss-00003/artifacts/20261102-research.md"
SCAFFOLD = b"---\nid: a\n---\n\n# Title\n\n## Placeholder\n"
BODY = "## Question\n\n- 確認する。\n".encode()


def _helper(*argv: str, cwd: Path, body: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(HELPER), *argv], cwd=cwd, input=body, capture_output=True, check=False, timeout=10
    )


def _layout(tmp_path: Path, relative: str = RELATIVE) -> tuple[Path, Path, Path]:
    """A worktree whose `spec-dock/initiatives` links to a catalog in another checkout, like a linked worktree."""
    main_checkout = tmp_path / "main"
    catalog = main_checkout / "spec-dock/.canonical"
    artifact = catalog / Path(relative).relative_to("spec-dock/initiatives")
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(SCAFFOLD)
    (main_checkout / ".git/worktrees/worktree").mkdir(parents=True)
    repo = tmp_path / "worktree"
    (repo / "spec-dock").mkdir(parents=True)
    (repo / ".git").write_text(f"gitdir: {main_checkout}/.git/worktrees/worktree\n", encoding="utf-8")
    (repo / "spec-dock/initiatives").symlink_to(catalog)
    return repo, catalog, artifact


def _finalize(repo: Path, relative: str = RELATIVE) -> subprocess.CompletedProcess[bytes]:
    identity = _helper("identity", "--repo-root", str(repo), "--artifact", relative, cwd=repo)
    if identity.returncode != 0:
        return identity
    info = json.loads(identity.stdout)
    return _helper(
        "finalize",
        "--repo-root",
        str(repo),
        "--artifact",
        relative,
        "--expected-device",
        str(info["device"]),
        "--expected-inode",
        str(info["inode"]),
        "--expected-ctime-ns",
        str(info["ctime_ns"]),
        cwd=repo,
        body=BODY,
    )


def test_artifact_through_the_catalog_link_is_finalized(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    result = _finalize(repo)
    assert result.returncode == 0, result.stderr
    assert artifact.read_bytes() == SCAFFOLD[: SCAFFOLD.index(b"\n## ") + 1] + BODY


def test_a_relative_catalog_link_is_finalized(tmp_path: Path) -> None:
    repo, catalog, artifact = _layout(tmp_path)
    link = repo / "spec-dock/initiatives"
    link.unlink()
    link.symlink_to(Path("../../main/spec-dock/.canonical"))
    assert link.resolve() == catalog.resolve()
    assert _finalize(repo).returncode == 0
    assert artifact.read_bytes().endswith(BODY)


def _assert_refused(repo: Path, protected: list[Path], relative: str = RELATIVE) -> None:
    before = {path: path.read_bytes() for path in protected}
    result = _finalize(repo, relative)
    assert result.returncode == 1
    assert b"error:" in result.stderr
    assert {path: path.read_bytes() for path in protected} == before


def test_a_link_to_another_directory_is_refused(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    other = tmp_path / "other/artifacts-root"
    moved = other / "00000-00999/iss-00003/artifacts"
    moved.mkdir(parents=True)
    (moved / artifact.name).write_bytes(SCAFFOLD)
    link = repo / "spec-dock/initiatives"
    link.unlink()
    link.symlink_to(other)
    _assert_refused(repo, [moved / artifact.name])


def test_a_link_to_a_catalog_named_directory_outside_spec_dock_is_refused(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    other = tmp_path / "elsewhere/.canonical"
    moved = other / "00000-00999/iss-00003/artifacts"
    moved.mkdir(parents=True)
    (moved / artifact.name).write_bytes(SCAFFOLD)
    link = repo / "spec-dock/initiatives"
    link.unlink()
    link.symlink_to(other)
    _assert_refused(repo, [moved / artifact.name])


def test_another_clones_catalog_is_refused(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    other = tmp_path / "other-clone/spec-dock/.canonical"
    moved = other / "00000-00999/iss-00003/artifacts"
    moved.mkdir(parents=True)
    (moved / artifact.name).write_bytes(SCAFFOLD)
    link = repo / "spec-dock/initiatives"
    link.unlink()
    link.symlink_to(other)
    _assert_refused(repo, [moved / artifact.name])


def test_a_worktree_without_git_metadata_refuses_the_link(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    (repo / ".git").unlink()
    _assert_refused(repo, [artifact])


def test_the_main_checkout_itself_may_use_a_link_to_its_own_catalog(tmp_path: Path) -> None:
    _, catalog, artifact = _layout(tmp_path)
    main_checkout = catalog.parent.parent
    (main_checkout / "spec-dock/initiatives").symlink_to(catalog)
    assert _finalize(main_checkout).returncode == 0
    assert artifact.read_bytes().endswith(BODY)


def test_a_catalog_that_is_itself_a_link_is_refused(tmp_path: Path) -> None:
    repo, catalog, artifact = _layout(tmp_path)
    real = tmp_path / "real"
    catalog.rename(real)
    catalog.symlink_to(real)
    _assert_refused(repo, [real / "00000-00999/iss-00003/artifacts" / artifact.name])


def test_a_link_below_the_catalog_is_refused(tmp_path: Path) -> None:
    repo, catalog, artifact = _layout(tmp_path)
    real = catalog / "00000-00999/iss-00003"
    real.rename(catalog / "00000-00999/real-scope")
    (catalog / "00000-00999/iss-00003").symlink_to(catalog / "00000-00999/real-scope")
    _assert_refused(repo, [catalog / "00000-00999/real-scope/artifacts" / artifact.name])


def test_a_link_in_place_of_spec_dock_is_refused(tmp_path: Path) -> None:
    repo, catalog, artifact = _layout(tmp_path)
    (repo / "spec-dock/initiatives").unlink()
    (repo / "spec-dock").rmdir()
    (repo / "spec-dock").symlink_to(tmp_path / "main/spec-dock")
    (tmp_path / "main/spec-dock/initiatives").symlink_to(catalog)
    _assert_refused(repo, [artifact])


def test_an_artifact_that_is_a_link_is_refused(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    target = artifact.with_name("target.md")
    artifact.rename(target)
    artifact.symlink_to(target)
    _assert_refused(repo, [target])


def test_the_catalog_link_is_not_accepted_for_other_roots(tmp_path: Path) -> None:
    repo, _, artifact = _layout(tmp_path)
    (repo / "docs").symlink_to(artifact.parent.parent.parent.parent)
    _assert_refused(repo, [artifact], "docs/00000-00999/iss-00003/artifacts/" + artifact.name)


def test_an_ordinary_directory_still_works(tmp_path: Path) -> None:
    repo = tmp_path / "plain"
    artifact = repo / RELATIVE
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(SCAFFOLD)
    assert _finalize(repo).returncode == 0
    assert artifact.read_bytes().endswith(BODY)


def _entry() -> dict[str, Any]:
    files = json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text("utf-8"))["files"]
    return next(item for item in files if item["path"] == SKILL)


def test_the_inventory_accepts_the_0_5_0_bytes_and_the_dogfood_copy_matches() -> None:
    entry = _entry()
    assert entry["sha256"] == hashlib.sha256(HELPER.read_bytes()).hexdigest()
    assert hashlib.sha256(PREVIOUS.read_bytes()).hexdigest() in entry["known_old_sha256"]
    assert PREVIOUS.read_bytes() != HELPER.read_bytes()
    assert (ROOT / SKILL).read_bytes() == HELPER.read_bytes()


def test_installation_update_upgrades_a_0_5_0_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    (target / SKILL).write_bytes(PREVIOUS.read_bytes())
    backup = tmp_path / "backup"
    code = main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"])
    applied = json.loads(capsys.readouterr().out)
    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    assert applied["data"]["result"]["changed_paths"] == [SKILL]
    assert (target / SKILL).read_bytes() == HELPER.read_bytes()
    assert (backup / "static" / SKILL).read_bytes() == PREVIOUS.read_bytes()

"""The three ignore lines hide only a symlinked spec-dock/initiatives and the catalog (iss-00429, AC-429-04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.canonical_layout import EXCLUDE_LINES, GITIGNORE_LINES
from spec_dock.runtime.infra.canonical_files import append_exclude
from tests.support.canonical_repo import SHIPPED_GITIGNORE, configure, git

if TYPE_CHECKING:
    from pathlib import Path


def _repository(root: Path, *, shipped_gitignore: bool) -> Path:
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    configure(root)
    (root / "spec-dock").mkdir()
    (root / "spec-dock/workspace.json").write_text('{"schema_version":3}\n', encoding="utf-8")
    if shipped_gitignore:
        (root / "spec-dock/.gitignore").write_bytes(SHIPPED_GITIGNORE.read_bytes())
    else:
        append_exclude(root / ".git", EXCLUDE_LINES)
    return root


def test_the_shipped_gitignore_carries_the_three_lines_in_spec_dock_form() -> None:
    lines = SHIPPED_GITIGNORE.read_text(encoding="utf-8").splitlines()
    assert all(line in lines for line in GITIGNORE_LINES)


@pytest.mark.parametrize("shipped_gitignore", [True, False], ids=["gitignore", "info-exclude"])
def test_a_real_initiatives_directory_keeps_new_spec_files_visible(tmp_path: Path, shipped_gitignore: bool) -> None:
    root = _repository(tmp_path / "legacy", shipped_gitignore=shipped_gitignore)
    spec = root / "spec-dock/initiatives/init-00001-plan/plan.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("plan\n", encoding="utf-8")
    status = git(root, "status", "--porcelain", "--untracked-files=all")
    assert "?? spec-dock/initiatives/init-00001-plan/plan.md" in status.splitlines()
    git(root, "add", "-A")
    assert "spec-dock/initiatives/init-00001-plan/plan.md" in git(root, "ls-files").splitlines()


@pytest.mark.parametrize("shipped_gitignore", [True, False], ids=["gitignore", "info-exclude"])
def test_a_symlinked_initiatives_and_the_catalog_are_ignored(tmp_path: Path, shipped_gitignore: bool) -> None:
    root = _repository(tmp_path / "canonical", shipped_gitignore=shipped_gitignore)
    (root / "spec-dock/.canonical/init-00001-plan").mkdir(parents=True)
    (root / "spec-dock/.canonical/init-00001-plan/plan.md").write_text("plan\n", encoding="utf-8")
    (root / "spec-dock/initiatives").symlink_to(".canonical")
    status = git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert not any(line.endswith(("spec-dock/initiatives", ".canonical/init-00001-plan/plan.md")) for line in status)
    ignored = git(root, "status", "--porcelain", "--ignored", "--untracked-files=all").splitlines()
    assert "!! spec-dock/initiatives" in ignored
    git(root, "add", "-A")
    tracked = git(root, "ls-files").splitlines()
    assert not any(path.startswith(("spec-dock/initiatives", "spec-dock/.canonical")) for path in tracked)

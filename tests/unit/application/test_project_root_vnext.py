"""Project context is fixed before target lookup or effects."""

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.resolve_target import resolve_project_root  # noqa: E402


def test_implicit_project_uses_nearest_git_root_from_child(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    child = root / "src" / "nested"
    child.mkdir(parents=True)
    assert resolve_project_root(child, git_root=lambda _: root) == root


def test_explicit_project_must_name_root_and_match_shim(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    child = root / "src"
    child.mkdir(parents=True)
    assert resolve_project_root(child, explicit_project=root, shim_root=root, git_root=lambda _: root) == root
    with pytest.raises(ValueError, match="root"):
        resolve_project_root(child, explicit_project=child, git_root=lambda _: root)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    with pytest.raises(ValueError, match="shim"):
        resolve_project_root(child, explicit_project=foreign, shim_root=root, git_root=lambda _: foreign)


def test_non_git_project_is_rejected_for_scope_operations(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Git"):
        resolve_project_root(tmp_path, git_root=lambda _: None)

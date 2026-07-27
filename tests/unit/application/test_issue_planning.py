from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.issue_planning import resolve_existing_issue_target  # noqa: E402
from spec_dock_runtime.domain.issue_planning_contracts import ReviewedPlanningIdentity  # noqa: E402
from spec_dock_runtime.infra.contracts import StoredMetaRecord  # noqa: E402


def _record(path: Path, *, node_id: str = "iss-00003", kind: str = "issue") -> StoredMetaRecord:
    return StoredMetaRecord(
        kind=kind,
        id=node_id,
        title="Issue",
        slug="issue",
        path=path.as_posix(),
        parent_id="epic-00002",
        initiative_id="init-00001",
        epic_id="epic-00002",
        github_issue_number=3,
        meta_path=(path / ".meta.json").as_posix(),
    )


def _issue_tree(repo_root: Path) -> Path:
    issue_dir = (
        repo_root
        / "spec-dock"
        / "initiatives"
        / "init-one"
        / "epics"
        / "epic-one"
        / "issues"
        / "iss-one"
    )
    issue_dir.mkdir(parents=True)
    for filename in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / filename).write_text(filename, encoding="utf-8")
    return issue_dir


def test_resolve_existing_issue_returns_parents_and_exact_three_paths(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    result = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)
    assert result.issue_id == "iss-00003"
    assert result.parent_epic_id == "epic-00002"
    assert result.parent_initiative_id == "init-00001"
    assert tuple(Path(path).name for path in result.canonical_issue_paths) == (
        "design.md",
        "plan.md",
        "requirement.md",
    )


def test_git_bound_identity_accepts_exact_resolver_tuple(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)
    identity = ReviewedPlanningIdentity(
        mode="git-bound",
        issue_id=target.issue_id,
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        canonical_target_paths=target.canonical_issue_paths,
        expected_canonical_target_paths=target.canonical_issue_paths,
    )
    identity.validate_canonical_target_paths(target.canonical_issue_paths)


@pytest.mark.parametrize("target", ["iss-99999", "init-00001", "epic-00002", "build payment flow"])
def test_resolve_existing_issue_rejects_unknown_parent_and_seed_targets(tmp_path: Path, target: str) -> None:
    issue_dir = _issue_tree(tmp_path)
    records = [
        _record(issue_dir),
        _record(issue_dir.parent.parent.parent, node_id="epic-00002", kind="epic"),
        _record(issue_dir.parent.parent.parent.parent.parent, node_id="init-00001", kind="initiative"),
    ]
    with pytest.raises(ValueError, match="existing Issue"):
        resolve_existing_issue_target(target, records, tmp_path)


def test_resolve_existing_issue_rejects_non_issue_record_with_issue_shaped_id(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    with pytest.raises(ValueError, match="existing Issue required"):
        resolve_existing_issue_target(
            "iss-00003",
            [_record(issue_dir, kind="epic")],
            tmp_path,
        )


def test_resolve_existing_issue_rejects_outside_and_dotdot_paths(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    for filename in ("requirement.md", "design.md", "plan.md"):
        (outside / filename).write_text(filename, encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        resolve_existing_issue_target("iss-00003", [_record(outside)], tmp_path)

    _issue_tree(tmp_path)
    dotdot_path = Path("spec-dock/initiatives/init-one/../init-one/epics/epic-one/issues/iss-one")
    with pytest.raises(ValueError, match=r"safe|dot|canonical"):
        resolve_existing_issue_target("iss-00003", [_record(dotdot_path)], tmp_path)


def test_resolve_existing_issue_rejects_symlinked_issue_or_document(tmp_path: Path) -> None:
    real_issue = _issue_tree(tmp_path)
    linked_issue = real_issue.parent / "iss-linked"
    linked_issue.symlink_to(real_issue, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        resolve_existing_issue_target("iss-00003", [_record(linked_issue)], tmp_path)

    (real_issue / "plan.md").unlink()
    (real_issue / "plan.md").symlink_to(real_issue / "design.md")
    with pytest.raises(ValueError, match="incomplete"):
        resolve_existing_issue_target("iss-00003", [_record(real_issue)], tmp_path)


def test_resolve_existing_issue_rejects_missing_canonical_document(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    (issue_dir / "plan.md").unlink()
    with pytest.raises(ValueError, match="incomplete"):
        resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)

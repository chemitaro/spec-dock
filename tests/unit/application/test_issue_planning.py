from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.issue_planning import resolve_existing_issue_target  # noqa: E402
from spec_dock_runtime.domain.authoring_pack.preflight_contract import (  # noqa: E402
    FetchSummary,
    FreshnessEvidence,
    PreflightResult,
    RepositorySnapshot,
)
from spec_dock_runtime.domain.authoring_pack.source_manifest import (  # noqa: E402
    build_source_manifest,
    empty_source_manifest,
)
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


@pytest.mark.parametrize(
    "blockers",
    [
        ("dirty_tracked",),
        ("staged_changes",),
        ("untracked_files",),
        ("detached_head",),
        ("remote_branch_missing",),
        ("origin_fetch_failed",),
        ("ahead_of_remote",),
        ("behind_remote",),
        ("diverged_from_remote",),
        ("concurrent_repo_change",),
    ],
)
def test_transport_short_circuits_backend_for_git_preflight_failures(
    tmp_path: Path,
    blockers: tuple[str, ...],
) -> None:
    issue_dir = _issue_tree(tmp_path)
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    run = module.run_issue_planning_transport
    result = run(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(blockers=blockers),
        repo_slug_resolver=lambda root: "owner/repo",
        prompt_synthesizer=lambda **kwargs: object(),
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("blocked", "git_preflight_blocked")
    assert result.details == blockers
    assert backend_calls == []


def test_transport_rejects_wrong_upstream_branch_before_backend(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    run = module.run_issue_planning_transport
    result = run(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(upstream="origin/other"),
        repo_slug_resolver=lambda root: "owner/repo",
        prompt_synthesizer=lambda **kwargs: object(),
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("blocked", "upstream_branch_mismatch")
    assert backend_calls == []


def test_transport_rejects_non_github_origin_without_leaking_error(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    run = module.run_issue_planning_transport
    private_url = "/Users/alice/private/repository"

    def reject_slug(root: Path) -> str:
        raise RuntimeError(f"origin is not GitHub: {private_url}")

    result = run(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(),
        repo_slug_resolver=reject_slug,
        prompt_synthesizer=lambda **kwargs: object(),
        backend_invoker=lambda **kwargs: pytest.fail("backend must not run"),
    )
    assert (result.status, result.reason) == ("blocked", "github_upstream_required")
    assert private_url not in repr(result)
    assert private_url not in str(result.to_dict())


def test_preflight_failure_redacts_unsafe_blocker_path_and_secret(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    private_value = "/Users/alice/private/token=abc123secret"
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(
            blockers=(f"unsafe_source_path:absolute-outside-repo:{private_value}",)
        ),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("backend must not run"),
    )
    assert result.details == ("unsafe_source_path",)
    assert private_value not in repr(result)
    assert private_value not in str(result.to_dict())


def test_transport_rejects_source_mutation_after_preflight_before_backend(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    source_paths = tuple(
        sorted(
            (
                (issue_dir / "design.md").relative_to(tmp_path).as_posix(),
                (issue_dir / "plan.md").relative_to(tmp_path).as_posix(),
                (issue_dir / "requirement.md").relative_to(tmp_path).as_posix(),
            ),
            key=lambda value: value.encode("utf-8"),
        )
    )
    manifest = build_source_manifest(tmp_path, source_paths)
    backend_calls: list[object] = []

    def mutate_then_synthesize(**kwargs):
        (issue_dir / "plan.md").write_text("mutated after preflight", encoding="utf-8")
        from spec_dock_runtime.application.issue_planning_prompt import (
            synthesize_issue_planning_prompt,
        )

        return synthesize_issue_planning_prompt(**kwargs)

    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(source_manifest=manifest),
        repo_slug_resolver=lambda root: "owner/repo",
        prompt_synthesizer=mutate_then_synthesize,
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("blocked", "git_preflight_blocked")
    assert result.details == ("source_snapshot_mismatch",)
    assert backend_calls == []


def test_transport_sensitive_git_identity_rejection_does_not_leak_source_evidence(
    tmp_path: Path,
) -> None:
    issue_dir = _issue_tree(tmp_path)
    secret_branch = "token=abc123secret"
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(
            branch=secret_branch,
            upstream=f"origin/{secret_branch}",
        ),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("rejected", "sensitive_input_rejected")
    assert result.source_evidence is None
    assert result.details == ()
    assert backend_calls == []
    assert secret_branch not in repr(result)
    assert secret_branch not in str(result.to_dict())


def _preflight(
    *,
    blockers: tuple[str, ...] = (),
    branch: str = "feature/issue",
    upstream: str = "origin/feature/issue",
    source_manifest=None,
) -> PreflightResult:
    manifest = source_manifest or empty_source_manifest()
    repository = RepositorySnapshot(
        normalized_origin="github.com/owner/repo",
        branch=branch,
        local_head="a" * 40,
        upstream=upstream,
        effective_ref=branch,
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        worktree_state=blockers,
        source_manifest=manifest,
        snapshot_id="b" * 64,
    )
    return PreflightResult(
        status="blocked" if blockers else "pass",
        evidence_mode="github-synced",
        sync_state="blocked" if blockers else "synced",
        github_sync="failed" if blockers else "verified",
        requested_ref=branch,
        effective_ref=branch,
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest=manifest,
        source_hash_mismatch_checked=False,
        blockers=blockers,
        fetch=FetchSummary(status="failed" if "origin_fetch_failed" in blockers else "success"),
        freshness=FreshnessEvidence(
            snapshot_id="b" * 64,
            final_guard_snapshot_id="b" * 64,
            concurrent_change_check="changed" if "concurrent_repo_change" in blockers else "stable",
            remote_head_disposition="fetched_remote_tracking_ref",
        ),
        repository=repository,
    )

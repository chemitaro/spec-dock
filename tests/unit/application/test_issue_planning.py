from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

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
from spec_dock_runtime.infra.contracts import (  # noqa: E402
    DirectDependencyResolution,
    StoredMetaRecord,
)


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


def _planning_document(filename: str, *, issue_id: str = "iss-00003") -> bytes:
    kind = {
        "requirement.md": "要件定義書（Issue）",
        "design.md": "設計書（Issue）",
        "plan.md": "実装計画書（Issue）",
    }[filename]
    dependency = {
        "requirement.md": "",
        "design.md": '依存: ["requirement.md"]\n',
        "plan.md": '依存: ["requirement.md", "design.md"]\n',
    }[filename]
    return (
        "---\n"
        f"種別: {kind}\n"
        f'ID: "{issue_id}"\n'
        'タイトル: "Issue"\n'
        '状態: "approved"\n'
        '作成者: "Author"\n'
        '最終更新: "2026-07-27"\n'
        f"{dependency}"
        '親: ["epic-00002", "init-00001"]\n'
        "---\n\n"
        f"# {issue_id} Issue\n\n"
        "## Section\n\n"
        "Substantive content.\n"
    ).encode()


def _planning_tree(repo_root: Path) -> Path:
    issue_dir = _issue_tree(repo_root)
    for filename in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / filename).write_bytes(_planning_document(filename))
    return issue_dir


def _planner_payload() -> bytes:
    chunks: list[bytes] = []
    filenames = ("requirement.md", "design.md", "plan.md")
    for index, filename in enumerate(filenames):
        chunks.extend(
            (
                f"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={filename}>>>\n".encode(),
                _planning_document(filename),
                f"<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={filename}>>>".encode()
                + (b"\n" if index < len(filenames) - 1 else b""),
            )
        )
    return b"".join(chunks)


def _successful_transport(payload: bytes | None = None):
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningInvocationResult", "PlanningSourceEvidence"],
    )
    value = payload or _planner_payload()
    evidence = contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash="c" * 64,
        snapshot_id="b" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    return contracts.PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=evidence,
        response_bytes=len(value),
        response_sha256=hashlib.sha256(value).hexdigest(),
        transient_payload=value,
    )


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


def test_current_front_matter_inconsistency_short_circuits_backend(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    (issue_dir / "plan.md").write_bytes(_planning_document("plan.md", issue_id="iss-99999"))
    output = tmp_path / "output"
    output.mkdir()
    backend_calls: list[object] = []
    result = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    ).run_issue_planning_create(
        request=__import__(
            "spec_dock_runtime.application.issue_planning",
            fromlist=["PlanningCreateRequest"],
        ).PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("rejected", "planning_context_rejected")
    assert backend_calls == []


def test_create_maps_s02_nonpass_without_candidate_work(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningInvocationResult"],
    )
    publisher_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: contracts.PlanningInvocationResult(
            status="blocked",
            reason="backend_timeout",
        ),
        publisher=lambda **kwargs: publisher_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("blocked", "backend_timeout")
    assert publisher_calls == []


def test_create_rejects_transient_payload_digest_mismatch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    transport = _successful_transport()
    object.__setattr__(transport, "response_sha256", "d" * 64)
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: transport,
    )
    assert (result.status, result.reason) == ("rejected", "planner_response_rejected")
    assert list(output.iterdir()) == []


def test_create_returns_ok_candidate_created_only_after_atomic_publication(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(),
        clock=lambda: datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc).isoformat(),
    )
    assert (result.status, result.reason) == ("ok", "candidate_created")
    identity = result.output["candidate_identity"]
    final = output / identity["logical_filename"]
    assert final.is_file()
    assert hashlib.sha256(final.read_bytes()).hexdigest() == identity["zip_sha256"]


def test_create_success_output_has_only_safe_keys(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert set(result.output) == {"candidate_identity", "zip_byte_count"}
    assert str(output) not in str(result.to_dict())
    assert _planner_payload().decode() not in str(result.to_dict())


def test_unsupported_atomic_publication_leaves_final_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    infra = __import__(
        "spec_dock_runtime.infra.issue_planning_candidate",
        fromlist=["atomic_publish_no_replace"],
    )

    def unsupported(source: Path, destination: Path) -> None:
        raise NotImplementedError

    monkeypatch.setattr(infra, "atomic_publish_no_replace", unsupported)
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("blocked", "candidate_publication_failed")
    assert list(output.iterdir()) == []


def test_atomic_publication_collision_preserves_existing_candidate_bytes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    arguments = {
        "request": module.PlanningCreateRequest("iss-00003", output),
        "records": [_record(issue_dir)],
        "repo_root": repo,
        "repo_slug_resolver": lambda root: "owner/repo",
        "backend_invoker": lambda **kwargs: None,
        "transport_runner": lambda **kwargs: _successful_transport(),
        "clock": lambda: "2026-07-28T12:00:00+00:00",
    }
    first = module.run_issue_planning_create(**arguments)
    candidate = output / first.output["candidate_identity"]["logical_filename"]
    before = candidate.read_bytes()
    second = module.run_issue_planning_create(**arguments)
    assert (second.status, second.reason) == ("rejected", "output_collision")
    assert candidate.read_bytes() == before
    assert len(list(output.iterdir())) == 1


def test_create_uses_one_dependency_snapshot_for_transport_and_source_baseline(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    loader_calls: list[str] = []
    transport_dependencies: list[str] = []

    def changing_loader(issue_id: str) -> list[DirectDependencyResolution]:
        loader_calls.append(issue_id)
        resolved = "iss-00001" if len(loader_calls) == 1 else "iss-00002"
        return [DirectDependencyResolution(raw_ref=resolved, resolved_node_id=resolved)]

    def transport_runner(**kwargs):
        dependencies = kwargs["dependency_loader"]("iss-00003")
        transport_dependencies.extend(item.resolved_node_id for item in dependencies)
        return _successful_transport()

    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        dependency_loader=changing_loader,
        transport_runner=transport_runner,
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    candidate = output / result.output["candidate_identity"]["logical_filename"]
    internal_root = result.output["candidate_identity"]["internal_root"]
    with zipfile.ZipFile(candidate) as archive:
        baseline = json.loads(archive.read(f"{internal_root}/SOURCE-BASELINE.json"))
    assert loader_calls == ["iss-00003"]
    assert baseline["dependency_ids"] == transport_dependencies == ["iss-00001"]


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

from pathlib import Path
import subprocess
import sys

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application import issue_planning  # noqa: E402
from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (  # noqa: E402
    run_github_sync_preflight,
)
from spec_dock_runtime.domain.authoring_pack.preflight_contract import (  # noqa: E402
    FetchSummary,
    FreshnessEvidence,
    GitProcessOutcome,
    PreflightResult,
    RepositorySnapshot,
)
from spec_dock_runtime.domain.authoring_pack.source_manifest import (  # noqa: E402
    build_source_manifest,
    empty_source_manifest,
)
from spec_dock_runtime.infra.contracts import DirectDependencyResolution, StoredMetaRecord  # noqa: E402
from spec_dock_runtime.infra.issue_planning_chatgpt import (  # noqa: E402
    resolve_issue_planning_github_repository,
)


def test_synced_source_to_transport_tracer_preserves_identity_and_is_not_lifecycle_success(
    tmp_path: Path,
) -> None:
    issue_dir = tmp_path / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    for name in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / name).write_text(name, encoding="utf-8")
    record = StoredMetaRecord(
        kind="issue",
        id="iss-00003",
        title="Issue",
        slug="issue",
        path=issue_dir.as_posix(),
        parent_id="epic-00002",
        initiative_id="init-00001",
        epic_id="epic-00002",
        github_issue_number=3,
        meta_path=(issue_dir / ".meta.json").as_posix(),
    )
    invoked: list[object] = []
    run = issue_planning.run_issue_planning_transport
    result = run(
        issue="iss-00003",
        records=[record],
        repo_root=tmp_path,
        role="planner",
        dependency_loader=lambda issue_id: [
            DirectDependencyResolution(raw_ref="iss-00001", resolved_node_id="iss-00001")
        ],
        preflight_runner=lambda request: _preflight(
            source_manifest=build_source_manifest(tmp_path, request.source_paths)
        ),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: invoked.append(kwargs) or _transport_result(),
    )
    assert len(invoked) == 1
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.source_evidence.repository == "owner/repo"
    assert result.source_evidence.local_head == "a" * 40
    assert result.reason not in {
        "candidate_created",
        "candidate_revised",
        "review_completed",
        "adoption_published",
    }


def test_real_preflight_clean_synced_github_branch_invokes_backend_once(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "checkout", "-b", "feature/issue")
    issue_dir = tmp_path / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    for name in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / name).write_text(name, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture")
    head = _git(tmp_path, "rev-parse", "HEAD")
    _git(tmp_path, "remote", "add", "origin", "git@github.com:owner/repo.git")
    _git(tmp_path, "update-ref", "refs/remotes/origin/feature/issue", head)
    _git(tmp_path, "branch", "--set-upstream-to", "origin/feature/issue")
    record = StoredMetaRecord(
        kind="issue",
        id="iss-00003",
        title="Issue",
        slug="issue",
        path=issue_dir.as_posix(),
        parent_id="epic-00002",
        initiative_id="init-00001",
        epic_id="epic-00002",
        github_issue_number=3,
        meta_path=(issue_dir / ".meta.json").as_posix(),
    )
    backend_calls: list[object] = []
    result = issue_planning.run_issue_planning_transport(
        issue="iss-00003",
        records=[record],
        repo_root=tmp_path,
        role="planner",
        repo_slug_resolver=resolve_issue_planning_github_repository,
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs)
        or _transport_result(source_evidence=kwargs["source_evidence"]),
        preflight_runner=lambda request: run_github_sync_preflight(
            request,
            fetch_executor=lambda fetch_request: GitProcessOutcome(
                return_code=0,
                termination="exited",
                stdout=b"",
                stderr=b"",
                duration_ms=1,
            ),
        ),
    )
    assert len(backend_calls) == 1
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.source_evidence.local_head == head
    assert result.source_evidence.remote_head == head


def _preflight(*, source_manifest=None) -> PreflightResult:
    manifest = source_manifest or empty_source_manifest()
    repository = RepositorySnapshot(
        normalized_origin="github.com/owner/repo",
        branch="feature/issue",
        local_head="a" * 40,
        upstream="origin/feature/issue",
        effective_ref="feature/issue",
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        worktree_state=(),
        source_manifest=manifest,
        snapshot_id="b" * 64,
    )
    return PreflightResult(
        status="pass",
        evidence_mode="github-synced",
        sync_state="synced",
        github_sync="verified",
        requested_ref="feature/issue",
        effective_ref="feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest=manifest,
        source_hash_mismatch_checked=False,
        fetch=FetchSummary(status="success"),
        freshness=FreshnessEvidence(
            snapshot_id="b" * 64,
            final_guard_snapshot_id="b" * 64,
            concurrent_change_check="stable",
            remote_head_disposition="fetched_remote_tracking_ref",
        ),
        repository=repository,
    )


def _transport_result(*, source_evidence=None):
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningInvocationResult"],
    )
    evidence = source_evidence or contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash=empty_source_manifest().source_manifest_hash,
        snapshot_id="b" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    return contracts.PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=evidence,
        response_bytes=4,
        response_sha256="c" * 64,
        transient_payload=b"body",
    )


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

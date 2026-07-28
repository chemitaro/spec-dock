import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

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
    classify_transport_frame,
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


def test_fake_transport_to_candidate_preserves_source_and_payload_binding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    output = tmp_path / "output"
    output.mkdir()
    record = _record(issue_dir)
    payload = _planner_payload(documents)
    result = issue_planning.run_issue_planning_create(
        request=issue_planning.PlanningCreateRequest("iss-00003", output),
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _transport_result(payload=payload),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "candidate_created")
    candidate = output / result.output["candidate_identity"]["logical_filename"]
    with zipfile.ZipFile(candidate) as archive:
        root = result.output["candidate_identity"]["internal_root"]
        baseline = json.loads(archive.read(f"{root}/SOURCE-BASELINE.json"))
    assert baseline["source_repository"] == "owner/repo"
    assert baseline["source_head"] == "a" * 40
    assert baseline["planner_payload_sha256"] == hashlib.sha256(payload).hexdigest()


def test_fake_backend_partial_or_fourth_document_leaves_final_zero(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    output = tmp_path / "output"
    output.mkdir()
    payload = _planner_payload(documents) + b"fourth document"
    result = issue_planning.run_issue_planning_create(
        request=issue_planning.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _transport_result(payload=payload),
    )
    assert (result.status, result.reason) == ("rejected", "planner_response_rejected")
    assert list(output.iterdir()) == []


def test_real_outer_frame_extraction_feeds_exact_inner_candidate_grammar(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    output = tmp_path / "output"
    output.mkdir()
    payload = _planner_payload(documents)
    evidence = _transport_result(payload=payload).source_evidence
    outer = (
        b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
        + b"a" * 40
        + b">>>\n"
        + payload
        + b"\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n"
    )
    transport = classify_transport_frame(
        outer,
        role="planner",
        source_head="a" * 40,
        source_evidence=evidence,
    )
    assert transport.transient_payload == payload
    result = issue_planning.run_issue_planning_create(
        request=issue_planning.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: transport,
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "candidate_created")


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


def _transport_result(*, source_evidence=None, payload: bytes = b"body"):
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
        response_bytes=len(payload),
        response_sha256=hashlib.sha256(payload).hexdigest(),
        transient_payload=payload,
    )


def _record(issue_dir: Path) -> StoredMetaRecord:
    return StoredMetaRecord(
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


def _planning_document(filename: str) -> bytes:
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
        'ID: "iss-00003"\n'
        'タイトル: "Issue"\n'
        '状態: "approved"\n'
        '作成者: "Author"\n'
        '最終更新: "2026-07-27"\n'
        f"{dependency}"
        '親: ["epic-00002", "init-00001"]\n'
        "---\n\n"
        "# iss-00003 Issue\n\n"
        "## Section\n\n"
        "Substantive content.\n"
    ).encode()


def _planner_payload(documents: dict[str, bytes]) -> bytes:
    names = ("requirement.md", "design.md", "plan.md")
    return b"".join(
        f"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={name}>>>\n".encode()
        + documents[name]
        + f"<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={name}>>>".encode()
        + (b"\n" if index < len(names) - 1 else b"")
        for index, name in enumerate(names)
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

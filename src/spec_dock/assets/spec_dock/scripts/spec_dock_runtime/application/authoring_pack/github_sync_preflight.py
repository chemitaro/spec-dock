from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable, Literal

from spec_dock_runtime.domain.authoring_pack.preflight_contract import GitVisibleRef, PreflightResult
from spec_dock_runtime.domain.authoring_pack.source_manifest import (
    build_source_manifest,
    expected_hash_from_manifest,
)


EvidenceMode = Literal["github-synced", "local-context"]


@dataclass(frozen=True)
class GitHubSyncPreflightRequest:
    repo_root: Path | None = None
    evidence_mode: EvidenceMode = "github-synced"
    ref: str | None = None
    allow_default_branch_fallback: bool = False
    source_paths: tuple[str, ...] = ()
    expected_source_manifest: Path | None = None
    expected_source_hash: str | None = None
    provided_context_paths: tuple[str, ...] = ()
    diff_summary: str | None = None
    unsynced_reason: str | None = None


RemoteObserver = Callable[[Path, str | None, bool], GitVisibleRef]


def run_github_sync_preflight(
    request: GitHubSyncPreflightRequest,
    *,
    remote_observer: RemoteObserver | None = None,
) -> PreflightResult:
    repo_root = _resolve_repo_root(request.repo_root)
    manifest_paths = request.source_paths
    if request.evidence_mode == "local-context" and not manifest_paths:
        manifest_paths = request.provided_context_paths
    source_manifest = build_source_manifest(repo_root, manifest_paths)

    expected_source_hash = _resolve_expected_hash(request)
    if request.evidence_mode == "local-context":
        return _local_context_result(request, source_manifest, expected_source_hash)

    blockers: list[str] = []
    remediation: list[str] = []
    blockers.extend(_worktree_blockers(repo_root))
    branch = _git_stdout(repo_root, "rev-parse", "--abbrev-ref", "HEAD", check=False)
    current_branch = None if branch in (None, "", "HEAD") else branch
    local_head = _git_stdout(repo_root, "rev-parse", "HEAD", check=False)
    requested_ref = request.ref or current_branch

    if current_branch is None:
        blockers.append("detached_head")
        remediation.append("checkout a named branch before GitHub-synced authoring preflight")

    if _git_stdout(repo_root, "remote", "get-url", "origin", check=False) is None:
        blockers.append("origin_missing")
        remediation.append("configure origin before GitHub-synced authoring preflight")

    upstream = _git_stdout(repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    if upstream is None:
        blockers.append("remote_branch_missing")
        remediation.append("set an origin upstream branch or use explicit local-context evidence")
    elif not upstream.startswith("origin/"):
        blockers.append("origin_mismatch")
        remediation.append("track an origin branch before repo-aware GitHub authoring")

    observer = remote_observer or _observe_origin_ref
    visible = observer(repo_root, requested_ref, request.allow_default_branch_fallback)
    blockers.extend(visible.blockers)
    remediation.extend(visible.remediation)

    if visible.state != "resolved":
        blockers.append(visible.state)

    status = "blocked" if blockers else "pass"
    sync_state = "blocked" if blockers else "synced"
    github_sync = "failed" if blockers else "verified"
    if not blockers and local_head != visible.remote_head:
        ahead, behind = _ahead_behind(repo_root, visible.effective_ref)
        if ahead > 0 and behind > 0:
            blockers.append("diverged_from_remote")
            remediation.append("reconcile diverged local and origin branches")
            status = "blocked"
            sync_state = "blocked"
        elif ahead > 0:
            blockers.append("ahead_of_remote")
            remediation.append("push local commits before GitHub-synced authoring")
            status = "blocked"
            sync_state = "blocked"
        elif behind > 0:
            blockers.append("behind_remote")
            remediation.append("pull or rebase onto origin before GitHub-synced authoring")
            status = "stale"
            sync_state = "stale"
        else:
            blockers.append("head_mismatch")
            remediation.append("make local HEAD match the remote-visible branch")
            status = "blocked"
            sync_state = "blocked"
        github_sync = "failed"

    checked = expected_source_hash is not None
    if expected_source_hash is not None and expected_source_hash != source_manifest.source_manifest_hash:
        blockers.append("source_hash_mismatch")
        remediation.append("refresh the source manifest baseline before using this evidence")
        status = "stale"
        sync_state = "stale"
        github_sync = "failed"

    return PreflightResult(
        status=status,
        evidence_mode="github-synced",
        sync_state=sync_state,
        github_sync=github_sync,
        requested_ref=requested_ref,
        effective_ref=visible.effective_ref,
        local_head=local_head,
        remote_head=visible.remote_head,
        source_manifest=source_manifest,
        source_hash_mismatch_checked=checked,
        blockers=tuple(dict.fromkeys(blockers)),
        remediation=tuple(dict.fromkeys(remediation)),
        expected_source_hash=expected_source_hash,
        current_source_hash=source_manifest.source_manifest_hash,
    )


def _local_context_result(
    request: GitHubSyncPreflightRequest,
    source_manifest,
    expected_source_hash: str | None,
) -> PreflightResult:
    blockers: list[str] = []
    remediation: list[str] = []
    if not request.unsynced_reason:
        blockers.append("missing_unsynced_reason")
        remediation.append("provide --unsynced-reason for local-context evidence")
    if not request.provided_context_paths and not request.diff_summary:
        blockers.append("missing_context_provenance")
        remediation.append("provide --provided-context-path or --diff-summary for local-context evidence")
    status = "blocked" if blockers else "pass"
    if expected_source_hash is not None and expected_source_hash != source_manifest.source_manifest_hash:
        blockers.append("source_hash_mismatch")
        remediation.append("refresh the source manifest baseline before using this evidence")
        status = "blocked" if status == "blocked" else "stale"
    return PreflightResult(
        status=status,
        evidence_mode="local-context",
        sync_state="local_context",
        github_sync="not_verified",
        requested_ref=request.ref,
        effective_ref=None,
        local_head=None,
        remote_head=None,
        source_manifest=source_manifest,
        source_hash_mismatch_checked=expected_source_hash is not None,
        blockers=tuple(blockers),
        remediation=tuple(remediation),
        expected_source_hash=expected_source_hash,
        provided_context_paths=request.provided_context_paths,
        diff_summary=request.diff_summary,
        unsynced_reason=request.unsynced_reason,
        current_source_hash=source_manifest.source_manifest_hash,
    )


def _resolve_repo_root(repo_root: Path | None) -> Path:
    if repo_root is not None:
        return repo_root.resolve()
    discovered = _git_stdout(Path.cwd(), "rev-parse", "--show-toplevel", check=False)
    if discovered is None:
        raise RuntimeError("not inside a git repository; provide --repo-root")
    return Path(discovered).resolve()


def _resolve_expected_hash(request: GitHubSyncPreflightRequest) -> str | None:
    manifest_hash = None
    if request.expected_source_manifest is not None:
        manifest_hash = expected_hash_from_manifest(request.expected_source_manifest)
    if manifest_hash and request.expected_source_hash and manifest_hash != request.expected_source_hash:
        raise ValueError("expected source manifest hash and --expected-source-hash disagree")
    return request.expected_source_hash or manifest_hash


def _worktree_blockers(repo_root: Path) -> tuple[str, ...]:
    status = _git_status_porcelain(repo_root)
    if status is None:
        return ("git_status_unavailable",)
    blockers: list[str] = []
    for line in status.splitlines():
        if line.startswith("??"):
            blockers.append("untracked_files")
            continue
        index_state = line[0]
        worktree_state = line[1]
        if index_state != " ":
            blockers.append("staged_changes")
        if worktree_state != " ":
            blockers.append("dirty_tracked")
    return tuple(dict.fromkeys(blockers))


def _git_status_porcelain(repo_root: Path) -> str | None:
    p = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        return None
    return (p.stdout or "").rstrip("\n")


def _observe_origin_ref(repo_root: Path, requested_ref: str | None, allow_fallback: bool) -> GitVisibleRef:
    if not requested_ref:
        return GitVisibleRef(
            state="branch_missing",
            requested_ref=requested_ref,
            effective_ref=None,
            remote_head=None,
            blockers=("remote_branch_missing",),
            remediation=("checkout a branch or pass --ref",),
        )
    remote_head = _git_stdout(repo_root, "rev-parse", "--verify", f"refs/remotes/origin/{requested_ref}", check=False)
    if remote_head is not None:
        return GitVisibleRef("resolved", requested_ref, requested_ref, remote_head)
    if not allow_fallback:
        return GitVisibleRef(
            state="branch_missing",
            requested_ref=requested_ref,
            effective_ref=None,
            remote_head=None,
            blockers=("remote_branch_missing",),
            remediation=("pass --allow-default-branch-fallback only when default branch evidence is intended",),
        )
    default_ref = _git_stdout(repo_root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False)
    if default_ref is None or not default_ref.startswith("origin/"):
        return GitVisibleRef(
            state="default_branch_unknown",
            requested_ref=requested_ref,
            effective_ref=None,
            remote_head=None,
            blockers=("default_branch_unknown",),
            remediation=("fetch origin HEAD or pass an explicit existing --ref",),
        )
    effective_ref = default_ref.removeprefix("origin/")
    fallback_head = _git_stdout(repo_root, "rev-parse", "--verify", f"refs/remotes/origin/{effective_ref}", check=False)
    if fallback_head is None:
        return GitVisibleRef(
            state="branch_missing",
            requested_ref=requested_ref,
            effective_ref=effective_ref,
            remote_head=None,
            blockers=("remote_branch_missing",),
            remediation=("fetch the fallback branch before authoring preflight",),
        )
    return GitVisibleRef("resolved", requested_ref, effective_ref, fallback_head)


def _ahead_behind(repo_root: Path, effective_ref: str | None) -> tuple[int, int]:
    if not effective_ref:
        return (0, 0)
    output = _git_stdout(repo_root, "rev-list", "--left-right", "--count", f"HEAD...refs/remotes/origin/{effective_ref}", check=False)
    if output is None:
        return (0, 0)
    left, right = output.split()
    return (int(left), int(right))


def _git_stdout(repo_root: Path, *args: str, check: bool) -> str | None:
    p = subprocess.run(["git", *args], cwd=str(repo_root), capture_output=True, text=True, check=False)
    if p.returncode != 0:
        if check:
            raise RuntimeError(f"git failed: {' '.join(args)}\n{(p.stderr or '').strip()}")
        return None
    return (p.stdout or "").strip()

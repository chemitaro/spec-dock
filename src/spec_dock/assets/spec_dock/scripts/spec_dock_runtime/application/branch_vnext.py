"""Create, inspect, and switch exact canonical Scope branch bindings."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import subprocess
from typing import TYPE_CHECKING

from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_result,
)
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.branch_binding import BranchBinding
from spec_dock_runtime.domain.lifecycle import decode_scope_metadata
from spec_dock_runtime.infra.active_store import load_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.git_cli import sanitized_git_environment, worktree_list
from spec_dock_runtime.infra.json_store import read_guarded_json
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.registry_store import RegistryStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.operation import OperationRecord


def _git(repo_root: Path, *arguments: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=sanitized_git_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("Git operation could not be observed") from error


def _resolve_commit(repo_root: Path, reference: str) -> str:
    if not reference or reference.startswith("-"):
        raise ValueError("branch base must be an explicit Git reference")
    result = _git(repo_root, "rev-parse", "--verify", "--end-of-options", f"{reference}^{{commit}}")
    sha = result.stdout.strip()
    if result.returncode != 0 or len(sha) not in (40, 64) or any(char not in "0123456789abcdef" for char in sha):
        raise ValueError("branch base does not resolve to a commit")
    return sha


def _branch_exists(repo_root: Path, name: str) -> bool:
    result = _git(repo_root, "show-ref", "--verify", "--quiet", f"refs/heads/{name}")
    if result.returncode not in (0, 1):
        raise RuntimeError("Git branch inventory could not be read")
    return result.returncode == 0


def _validate_name(repo_root: Path, name: str) -> None:
    if not name or not name.isascii() or name.startswith("-"):
        raise ValueError("canonical branch name is invalid")
    if _git(repo_root, "check-ref-format", "--branch", name).returncode != 0:
        raise ValueError("canonical branch name is invalid")


def _verify_scope_at_commit(repo_root: Path, views: tuple[ScopeView, ...], scope_id: str, sha: str) -> None:
    by_id = {view.id: view for view in views}
    current = by_id[scope_id]
    while True:
        relative = current.path.relative_to(repo_root).as_posix()
        result = _git(repo_root, "show", f"{sha}:{relative}/.meta.json")
        if result.returncode != 0:
            raise ValueError("base commit is missing Scope metadata")
        try:
            raw = json.loads(result.stdout)
            if not isinstance(raw, dict):
                raise ValueError("base metadata is not an object")
            metadata = decode_scope_metadata(raw)
        except (ValueError, json.JSONDecodeError) as error:
            raise ValueError("base commit has invalid Scope metadata") from error
        if (
            metadata.raw.get("id") != current.id
            or metadata.raw.get("type") != current.kind
            or metadata.raw.get("parent_id") != current.parent_id
        ):
            raise ValueError("base commit Scope graph differs from the current snapshot")
        if current.parent_id is None:
            return
        current = by_id[current.parent_id]


def _binding_for_scope(store: RegistryStore, scope_id: str) -> BranchBinding:
    matches = [binding for binding in store.load()[0].branches if binding.scope_id == scope_id]
    if len(matches) != 1:
        raise LookupError("canonical branch binding is missing")
    return matches[0]


def _branch_fingerprint(scope_id: str, name: str, sha: str) -> str:
    payload = json.dumps((scope_id, name, sha), separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


def show_scope_branch(repo_root: Path, common_dir: Path, scope_id: str) -> BranchBinding:
    binding = _binding_for_scope(RegistryStore(common_dir), scope_id)
    if not _branch_exists(repo_root, binding.name):
        raise ValueError("CANONICAL_BRANCH_MISSING")
    return binding


def resolve_branch_scope(repo_root: Path, worktree_id: str, target: str) -> str:
    """Resolve an ID, GitHub reference, or active selector from one workspace snapshot."""
    specdock_dir = repo_root / "spec-dock"
    views = load_scope_views(specdock_dir)
    selection, _ = load_selection_v3(specdock_dir, worktree_id=worktree_id)
    return show_scope(views, target, selection=selection).id


def preview_scope_branch_switch(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope_id: str,
) -> BranchBinding:
    """Check the exact checkout candidate without taking a writer lock or invoking Git switch."""
    admit_writer(
        load_control(common_dir),
        common_dir=common_dir,
        worktree_id=worktree_id,
        engine_digest=engine_digest,
        expected_epoch=expected_epoch,
    )
    binding = show_scope_branch(repo_root, common_dir, scope_id)
    status = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise ValueError("branch switch requires a clean working tree")
    for worktree in worktree_list(repo_root):
        if worktree.branch == binding.name and worktree.path.resolve(strict=True) != repo_root.resolve(strict=True):
            raise ValueError("canonical branch is checked out in another worktree")
    tip = _resolve_commit(repo_root, f"refs/heads/{binding.name}")
    views = load_scope_views(repo_root / "spec-dock")
    show_scope(views, scope_id)
    _verify_scope_at_commit(repo_root, views, scope_id, tip)
    return binding


def scope_from_current_branch(repo_root: Path, common_dir: Path) -> str:
    """Resolve an exact recorded branch name; never infer an ID from its text."""
    current = _git(repo_root, "branch", "--show-current")
    if current.returncode != 0:
        raise RuntimeError("current Git branch could not be read")
    name = current.stdout.strip()
    if not name:
        raise LookupError("canonical branch is unavailable on detached HEAD")
    matches = [binding for binding in RegistryStore(common_dir).load()[0].branches if binding.name == name]
    if len(matches) != 1:
        raise LookupError("canonical branch binding is missing or ambiguous")
    if not _branch_exists(repo_root, name):
        raise ValueError("CANONICAL_BRANCH_MISSING")
    return matches[0].scope_id


def _finish_failed_git_effect(journal: JournalStore, intent: OperationRecord, *, name: str, repo_root: Path) -> None:
    if _branch_exists(repo_root, name):
        uncertain = record_effect_result(intent, effect_id="git-branch", status="unknown")
        journal.update(uncertain, expected_sequence=intent.sequence)
        raise RuntimeError("branch creation outcome is unknown; inspect the pending operation")
    failed = record_effect_result(intent, effect_id="git-branch", status="failed")
    journal.update(failed, expected_sequence=intent.sequence)
    terminal = replace(failed, phase="complete", terminal_status="failed", sequence=failed.sequence + 1)
    journal.update(terminal, expected_sequence=failed.sequence)
    raise RuntimeError("Git branch creation failed without creating a ref")


def _plan_scope_branch_create(
    repo_root: Path, common_dir: Path, scope_id: str, base: str, name: str | None
) -> tuple[BranchBinding, int, int]:
    views = load_scope_views(repo_root / "spec-dock")
    scope = show_scope(views, scope_id)
    loaded = read_guarded_json(scope.path / ".meta.json")
    if loaded is None or not isinstance(loaded[0], dict):
        raise ValueError("Scope metadata is missing")
    metadata = decode_scope_metadata(loaded[0])
    slug = metadata.raw.get("slug")
    if not isinstance(slug, str) or not slug or metadata.revision != scope.revision:
        raise ValueError("Scope metadata changed before branch creation")
    branch_name = name if name is not None else f"{scope.id}-{slug}"
    _validate_name(repo_root, branch_name)
    state, _identity = RegistryStore(common_dir).load()
    if any(binding.scope_id == scope.id or binding.name == branch_name for binding in state.branches):
        raise ValueError("Scope or branch is already bound")
    if _branch_exists(repo_root, branch_name):
        raise ValueError("BRANCH_ADOPTION_REQUIRED")
    sha = _resolve_commit(repo_root, base)
    _verify_scope_at_commit(repo_root, views, scope.id, sha)
    return BranchBinding(scope.id, branch_name, sha), scope.revision, state.revision


def preview_scope_branch_create(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope_id: str,
    base: str,
    name: str | None,
) -> BranchBinding:
    """Preview a fixed branch create without reserving a ref or journal."""
    admit_writer(
        load_control(common_dir),
        common_dir=common_dir,
        worktree_id=worktree_id,
        engine_digest=engine_digest,
        expected_epoch=expected_epoch,
    )
    binding, _scope_revision, _registry_revision = _plan_scope_branch_create(
        repo_root, common_dir, scope_id, base, name
    )
    return binding


@dataclass(frozen=True)
class BranchCreateReceipt:
    binding: BranchBinding
    operation_id: str


def create_scope_branch_with_receipt(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope_id: str,
    base: str,
    name: str | None,
    lock_timeout: float = 0.0,
) -> BranchCreateReceipt:
    """Create a new branch at a fixed commit, then durably bind it without checkout."""
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        registry = RegistryStore(common_dir)
        binding, scope_revision, registry_revision = _plan_scope_branch_create(
            repo_root, common_dir, scope_id, base, name
        )
        branch_name = binding.name
        sha = binding.initial_sha
        assert control is not None
        journal = JournalStore(common_dir)
        operation = prepare_operation(
            command="branch.create",
            effect_plan=("git-branch", "registry-bind"),
            fixed_targets={"scope": scope_id, "branch": branch_name, "base_sha": sha},
            request_fingerprint=_branch_fingerprint(scope_id, branch_name, sha),
            before_revisions={"registry": registry_revision, "metadata": scope_revision},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        journal.create(operation)
        intent = record_effect_intent(operation, effect_id="git-branch", kind="git", target=branch_name)
        journal.update(intent, expected_sequence=operation.sequence)
        created = _git(repo_root, "branch", branch_name, sha)
        if created.returncode != 0:
            _finish_failed_git_effect(journal, intent, name=branch_name, repo_root=repo_root)
        advanced = record_effect_result(intent, effect_id="git-branch", status="succeeded")
        journal.update(advanced, expected_sequence=intent.sequence)
        registry_intent = record_effect_intent(advanced, effect_id="registry-bind", kind="local", target=scope_id)
        journal.update(registry_intent, expected_sequence=advanced.sequence)
        registry.bind_locked(binding)
        bound = record_effect_result(registry_intent, effect_id="registry-bind", status="succeeded")
        journal.update(bound, expected_sequence=registry_intent.sequence)
        terminal = replace(bound, phase="complete", terminal_status="succeeded", sequence=bound.sequence + 1)
        journal.update(terminal, expected_sequence=bound.sequence)
        return BranchCreateReceipt(binding, operation.operation_id)


def create_scope_branch(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope_id: str,
    base: str,
    name: str | None,
    lock_timeout: float = 0.0,
) -> BranchBinding:
    """Create and return the canonical binding for application callers."""
    return create_scope_branch_with_receipt(
        repo_root=repo_root,
        common_dir=common_dir,
        worktree_id=worktree_id,
        engine_digest=engine_digest,
        expected_epoch=expected_epoch,
        scope_id=scope_id,
        base=base,
        name=name,
        lock_timeout=lock_timeout,
    ).binding


def resume_scope_branch_create(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    operation_id: str,
    expected_scope_id: str | None = None,
    lock_timeout: float = 0.0,
) -> BranchBinding:
    """Complete the recorded binding only after observing its exact fixed Git ref."""
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        if operation.terminal_status == "succeeded":
            targets = dict(operation.fixed_targets)
            if (
                operation.command != "branch.create"
                or set(targets) != {"scope", "branch", "base_sha"}
                or (expected_scope_id is not None and targets["scope"] != expected_scope_id)
                or operation.request_fingerprint
                != _branch_fingerprint(targets["scope"], targets["branch"], targets["base_sha"])
                or operation.engine_digest != engine_digest
                or operation.writer_epoch != expected_epoch
            ):
                raise ValueError("completed branch operation differs from the recorded request")
            binding = BranchBinding(targets["scope"], targets["branch"], targets["base_sha"])
            if show_scope_branch(repo_root, common_dir, binding.scope_id) != binding:
                raise ValueError("completed branch binding changed")
            return binding
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        targets = dict(operation.fixed_targets)
        if (
            operation.command != "branch.create"
            or operation.effect_plan != ("git-branch", "registry-bind")
            or set(targets) != {"scope", "branch", "base_sha"}
            or (expected_scope_id is not None and targets["scope"] != expected_scope_id)
            or operation.engine_digest != engine_digest
            or operation.writer_epoch != expected_epoch
            or operation.terminal_status != "pending"
        ):
            raise ValueError("branch create recovery operation differs from the recorded request")
        scope_id, name, sha = targets["scope"], targets["branch"], targets["base_sha"]
        if operation.request_fingerprint != _branch_fingerprint(scope_id, name, sha):
            raise ValueError("branch create recovery fingerprint differs from fixed targets")
        binding = BranchBinding(scope_id, name, sha)
        _validate_name(repo_root, name)
        views = load_scope_views(repo_root / "spec-dock")
        show_scope(views, scope_id)
        _verify_scope_at_commit(repo_root, views, scope_id, sha)
        effects = operation.effects
        if effects and (effects[0].id != "git-branch" or effects[0].target != name):
            raise ValueError("recorded Git effect is invalid")
        exists = _branch_exists(repo_root, name)
        if exists and _resolve_commit(repo_root, f"refs/heads/{name}") != sha:
            raise ValueError("recorded branch ref changed; recovery needs inspection")
        if not effects:
            if exists:
                raise ValueError("unrecorded branch ref cannot be adopted during recovery")
            next_record = record_effect_intent(operation, effect_id="git-branch", kind="git", target=name)
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if not exists:
            if operation.effects[0].status != "intent":
                raise ValueError("recorded branch ref disappeared; recovery needs inspection")
            created = _git(repo_root, "branch", name, sha)
            if created.returncode != 0:
                _finish_failed_git_effect(journal, operation, name=name, repo_root=repo_root)
            if not _branch_exists(repo_root, name) or _resolve_commit(repo_root, f"refs/heads/{name}") != sha:
                raise RuntimeError("branch creation result is inconsistent; inspect the pending operation")
        if operation.effects[0].status == "intent":
            operation = record_effect_result(operation, effect_id="git-branch", status="succeeded")
            journal.update(operation, expected_sequence=operation.sequence - 1)
        elif operation.effects[0].status != "succeeded":
            raise ValueError("recorded Git effect cannot be resumed")
        if len(operation.effects) == 1:
            next_record = record_effect_intent(operation, effect_id="registry-bind", kind="local", target=scope_id)
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if len(operation.effects) != 2 or operation.effects[1].id != "registry-bind":
            raise ValueError("recorded registry effect is invalid")
        state, _identity = RegistryStore(common_dir).load()
        before_revision = dict(operation.before_revisions).get("registry")
        if before_revision is None:
            raise ValueError("recorded registry revision is missing")
        matches = [item for item in state.branches if item.scope_id == scope_id or item.name == name]
        if matches:
            if matches != [binding] or state.revision != before_revision + 1:
                raise ValueError("recorded binding conflicts with the current registry")
        elif state.revision == before_revision:
            RegistryStore(common_dir).bind_locked(binding)
        else:
            raise ValueError("registry revision changed during branch recovery")
        if operation.effects[1].status == "intent":
            next_record = record_effect_result(operation, effect_id="registry-bind", status="succeeded")
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        elif operation.effects[1].status != "succeeded":
            raise ValueError("recorded registry effect cannot be resumed")
        terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
        journal.update(terminal, expected_sequence=operation.sequence)
        return binding


def switch_scope_branch(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    scope_id: str,
    lock_timeout: float = 0.0,
) -> BranchBinding:
    """Switch only to the recorded branch after verifying the target snapshot and ownership."""
    with WriterLock(common_dir, timeout=lock_timeout):
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        binding = show_scope_branch(repo_root, common_dir, scope_id)
        status = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
        if status.returncode != 0 or status.stdout.strip():
            raise ValueError("branch switch requires a clean working tree")
        for worktree in worktree_list(repo_root):
            if worktree.branch == binding.name and worktree.path.resolve(strict=True) != repo_root.resolve(strict=True):
                raise ValueError("canonical branch is checked out in another worktree")
        tip = _resolve_commit(repo_root, f"refs/heads/{binding.name}")
        views = load_scope_views(repo_root / "spec-dock")
        show_scope(views, scope_id)
        _verify_scope_at_commit(repo_root, views, scope_id, tip)
        switched = _git(repo_root, "switch", "--no-guess", binding.name, timeout=60.0)
        if switched.returncode != 0:
            raise RuntimeError("Git branch switch failed; inspect current HEAD before retrying")
        actual_branch = _git(repo_root, "branch", "--show-current")
        actual_sha = _resolve_commit(repo_root, "HEAD")
        if actual_branch.stdout.strip() != binding.name or actual_sha != tip:
            raise RuntimeError("Git branch changed during switch; inspect current HEAD")
        after_status = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
        if after_status.returncode != 0 or after_status.stdout.strip():
            raise RuntimeError("checkout changed the working tree; inspect current HEAD and hook effects")
        after_views = load_scope_views(repo_root / "spec-dock")
        show_scope(after_views, scope_id)
        _verify_scope_at_commit(repo_root, after_views, scope_id, actual_sha)
        return binding

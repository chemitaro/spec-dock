"""Canonical-mode failure codes and their next step, defined once for every canonical command."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_layout import GITIGNORE_LINES, GITIGNORE_PATH
from spec_dock.runtime.infra.github_structure import (
    GITHUB_ACCESS_DENIED,
    GITHUB_CREATE_IDENTITY_UNKNOWN,
    GITHUB_EFFECT_UNKNOWN,
    GITHUB_RATE_LIMITED,
    GITHUB_REQUEST_REJECTED,
    GITHUB_RESPONSE_INVALID,
    GITHUB_UNAVAILABLE,
)
from spec_dock.runtime.infra.static_assets import classify_static_digest
from spec_dock.runtime.presentation.command_data import DiagnosticData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from spec_dock.runtime.infra.github_structure import GithubStructureError
    from spec_dock.runtime.infra.static_assets import StaticAsset

CANONICAL_NOT_IMPLEMENTED: Final = "CANONICAL_NOT_IMPLEMENTED"
CANONICAL_NOT_MIGRATED: Final = "CANONICAL_NOT_MIGRATED"
CANONICAL_NOT_APPLICABLE: Final = "CANONICAL_NOT_APPLICABLE"
CANONICAL_NOT_LINKED: Final = "CANONICAL_NOT_LINKED"
CANONICAL_CHECK_FAILED: Final = "CANONICAL_CHECK_FAILED"
# Catalog and link (iss-00429).
CANONICAL_UNSUPPORTED_LAYOUT: Final = "CANONICAL_UNSUPPORTED_LAYOUT"
CANONICAL_GIT_TOO_OLD: Final = "CANONICAL_GIT_TOO_OLD"
CANONICAL_FOREIGN_CHECKOUT: Final = "CANONICAL_FOREIGN_CHECKOUT"
CANONICAL_PATH_OCCUPIED: Final = "CANONICAL_PATH_OCCUPIED"
CANONICAL_LINK_OCCUPIED: Final = "CANONICAL_LINK_OCCUPIED"
CANONICAL_SANDBOX_DENIED: Final = "CANONICAL_SANDBOX_DENIED"
CANONICAL_LOCK_BUSY: Final = "CANONICAL_LOCK_BUSY"
CANONICAL_FORMAT_UNSUPPORTED: Final = "CANONICAL_FORMAT_UNSUPPORTED"
START_LOCK_BUSY: Final = "START_LOCK_BUSY"
OS_ACCESS_DENIED: Final = "OS_ACCESS_DENIED"
# Warnings (no exit code of their own).
CANONICAL_TOOL_SETTING_MISSING: Final = "CANONICAL_TOOL_SETTING_MISSING"
CANONICAL_TOOL_SETTING_UNKNOWN: Final = "CANONICAL_TOOL_SETTING_UNKNOWN"
CANONICAL_IGNORE_RULES_MISSING: Final = "CANONICAL_IGNORE_RULES_MISSING"
CANONICAL_MAIN_MOVED: Final = "CANONICAL_MAIN_MOVED"
CANONICAL_REMOTE_MISSING: Final = "CANONICAL_REMOTE_MISSING"
CANONICAL_MAIN_NOT_MIGRATED: Final = "CANONICAL_MAIN_NOT_MIGRATED"
CANONICAL_CHECKOUT_NOT_MIGRATED: Final = "CANONICAL_CHECKOUT_NOT_MIGRATED"
CANONICAL_INSIDE_CATALOG: Final = "CANONICAL_INSIDE_CATALOG"
CANONICAL_BASE_HAS_SPECS: Final = "CANONICAL_BASE_HAS_SPECS"
CANONICAL_CATALOG_PROTECTED: Final = "CANONICAL_CATALOG_PROTECTED"
CANONICAL_WORKBENCH_SHARED: Final = "CANONICAL_WORKBENCH_SHARED"
# Periodic sync (iss-00430). Warnings unless noted.
CANONICAL_SYNC_NOT_SCHEDULED: Final = "CANONICAL_SYNC_NOT_SCHEDULED"
CANONICAL_SYNC_NOT_CONFIRMED: Final = "CANONICAL_SYNC_NOT_CONFIRMED"
CANONICAL_PUSH_AUTH_FAILED: Final = "CANONICAL_PUSH_AUTH_FAILED"
CANONICAL_LINGER_DISABLED: Final = "CANONICAL_LINGER_DISABLED"
CANONICAL_RUNNER_RESTART: Final = "CANONICAL_RUNNER_RESTART"
CANONICAL_RUNNER_STOPPED: Final = "CANONICAL_RUNNER_STOPPED"
CANONICAL_UNPUSHED_STALE: Final = "CANONICAL_UNPUSHED_STALE"
CANONICAL_SYNC_BLOCKED: Final = "CANONICAL_SYNC_BLOCKED"
CANONICAL_SYNC_FAILED: Final = "CANONICAL_SYNC_FAILED"
CANONICAL_STATE_UNREADABLE: Final = "CANONICAL_STATE_UNREADABLE"
CANONICAL_GIT_IN_PROGRESS: Final = "CANONICAL_GIT_IN_PROGRESS"
CANONICAL_PAUSED: Final = "CANONICAL_PAUSED"  # exit 3 for a resume with the wrong option
CANONICAL_SAVE_HELD: Final = "CANONICAL_SAVE_HELD"
CANONICAL_SAVE_UNCONFIRMED: Final = "CANONICAL_SAVE_UNCONFIRMED"  # work finish (iss-00432): 6 after a changeset, else 3
SAVE_UNCONFIRMED_NEXT_STEP: Final = (
    "Run spec-dock canonical status to see why the save was not confirmed, then run spec-dock work finish again."
)
CANONICAL_UNSAVED_CHANGES: Final = "CANONICAL_UNSAVED_CHANGES"  # exit 3
CANONICAL_IGNORED_FILES_PRESENT: Final = "CANONICAL_IGNORED_FILES_PRESENT"  # exit 3
CANONICAL_SCHEDULER_FAILED: Final = "CANONICAL_SCHEDULER_FAILED"  # partial, exit 6
CANONICAL_NOT_HELD: Final = "CANONICAL_NOT_HELD"  # exit 3
CANONICAL_NOT_RESTORABLE: Final = "CANONICAL_NOT_RESTORABLE"  # exit 3
CANONICAL_PATH_NOT_FOUND: Final = "CANONICAL_PATH_NOT_FOUND"  # exit 3
CANONICAL_REGISTRY_UNREADABLE: Final = "CANONICAL_REGISTRY_UNREADABLE"  # exit 3
CANONICAL_STATE_ROOT_MISMATCH: Final = "CANONICAL_STATE_ROOT_MISMATCH"  # exit 3 for link; a warning in status
CANONICAL_DASHBOARD_OCCUPIED: Final = "CANONICAL_DASHBOARD_OCCUPIED"  # state.json dashboard.error; a status warning
CANONICAL_DASHBOARD_FAILED: Final = "CANONICAL_DASHBOARD_FAILED"  # state.json dashboard.error; a status warning

NOT_IMPLEMENTED_RECOVERY: Final = (
    "Wait for SpecDock 0.3.0, which completes canonical mode for this command; "
    "this repository declares workspace schema 4."
)
NOT_MIGRATED_RECOVERY: Final = (
    "This repository is not migrated (workspace schema 3); follow scripts/migrate-to-canonical/README.md "
    "in SpecDock 0.3.0 to migrate it."
)
CANONICAL_NOT_LINKED_RECOVERY: Final = "spec-dock canonical link"
MIGRATE_NOT_APPLICABLE_RECOVERY: Final = (
    "No writer-protocol migration applies to a schema-4 workspace; nothing needs to be done."
)
UNSUPPORTED_LAYOUT_RECOVERY: Final = (
    "Use a clone whose main checkout holds the .git directory; bare and separate-git-dir layouts are not supported."
)
GIT_TOO_OLD_RECOVERY: Final = "Install Git 2.38 or later, then run spec-dock canonical link again."
FOREIGN_CHECKOUT_RECOVERY: Final = (
    "Saving and syncing run on the host; in this container only read and write the spec files, "
    "or clone the repository inside the container and run spec-dock canonical link."
)
SANDBOX_DENIED_RECOVERY: Final = "Run the same command outside the sandbox (in a normal terminal)."
LOCK_BUSY_RECOVERY: Final = "Wait a moment, then run the same command again."
FORMAT_UNSUPPORTED_RECOVERY: Final = "Update SpecDock; this catalog uses a canonical format it cannot write."
FORMAT_MISSING_RECOVERY: Final = (
    "Check that the root of the spec-dock/canonical branch has a valid .spec-dock-canonical.json; "
    "SpecDock writes only a catalog that declares format 1."
)
PERMISSION_DENIED_RECOVERY: Final = (
    "Check the permissions of the listed paths; inside a sandbox, run the same command in a normal terminal."
)
INSIDE_CATALOG_RECOVERY: Final = "Run the command from the checkout root, or add --project <checkout>."
MAIN_NOT_MIGRATED_NEXT_STEP: Final = (
    "Check out a migrated commit (workspace schema 4) in the main checkout, then run spec-dock canonical link there."
)
CHECKOUT_NOT_MIGRATED_NEXT_STEP: Final = (
    "Base the worktree on a commit that declares workspace schema 4, then run spec-dock canonical link in it."
)
BASE_HAS_SPECS_RECOVERY: Final = "Use a commit made after the switch to canonical storage as the base."
CATALOG_PROTECTED_RECOVERY: Final = "To detach this clone's catalog, run spec-dock canonical remove."
WORKBENCH_SHARED_RECOVERY: Final = (
    "Nothing to do: every worktree of this clone sees the same catalog, including each Scope's .workbench."
)
CHECK_INSTEAD_RECOVERY: Final = "Run spec-dock canonical check to check a commit in CI."
START_LOCK_BUSY_RECOVERY: Final = "Wait a moment, then run spec-dock canonical link again."
LINK_AGAIN_RECOVERY: Final = "Run spec-dock canonical link again; it continues from the current state."
LINK_NETWORK_RECOVERY: Final = (
    "Check the network connection and the Git credentials for origin (for GitHub over HTTPS, gh auth setup-git), "
    "then run spec-dock canonical link again."
)
GIT_IDENTITY_RECOVERY: Final = (
    "Set the Git identity (git config user.name and user.email), then run spec-dock canonical link again."
)
IGNORE_RULES_UPDATE_NEXT_STEP: Final = (
    "Run spec-dock installation update --target <checkout> --backup-dir <new external directory> --yes "
    f"and commit {GITIGNORE_PATH}; the shipped file carries the canonical ignore rules."
)
IGNORE_RULES_MERGE_NEXT_STEP: Final = (
    f"Merge the shipped {GITIGNORE_PATH} into this modified copy so it ends with these lines in this order, "
    f"then commit: {', '.join(GITIGNORE_LINES)}."
)
MAIN_MOVED_NEXT_STEP: Final = (
    "Git may also have reconnected the linked worktrees; run spec-dock canonical link in each linked worktree "
    "(for a worktree that also moved, first run git worktree repair <path> in the main checkout)."
)
REMOTE_MISSING_NEXT_STEP: Final = (
    "Check whether the GitHub branch spec-dock/canonical was deleted; if it was, sync stops; "
    "follow spec-dock canonical status."
)
SYNC_NOT_SCHEDULED_NEXT_STEP: Final = (
    "Run spec-dock canonical link (without --no-schedule) to register this catalog for periodic sync."
)
PRIVACY_NEXT_STEP: Final = (
    "In System Settings > Privacy & Security, allow Full Disk Access (or Removable Volumes) for the listed "
    "programs (the spec-dock Python and git), then check spec-dock canonical status."
)
DASHBOARD_OCCUPIED_NEXT_STEP: Final = "Move the listed paths away; the next sync writes the dashboard there."
DASHBOARD_FAILED_NEXT_STEP: Final = "Check the snapshot and sync items of spec-dock canonical status."
DASHBOARD_MISSING_NEXT_STEP: Final = (
    "The next periodic sync writes the dashboard; check the sync item of spec-dock canonical status."
)
SYNC_LOG_NEXT_STEP: Final = "Check <state root>/canonical-sync.log, then spec-dock canonical status."
PUSH_AUTH_HTTPS_NEXT_STEP: Final = "Run gh auth setup-git so the periodic job can push over HTTPS."
PUSH_AUTH_SSH_NEXT_STEP: Final = (
    "The periodic job may not get an SSH agent; switch origin to https and use gh authentication (gh auth setup-git)."
)
LINGER_NEXT_STEP: Final = (
    "Run loginctl enable-linger {user} (it may need administrator rights) so sync keeps running after logout."
)
UNPUSHED_STALE_NEXT_STEP: Final = (
    "Check the network and gh auth status, then look at the sync item of spec-dock canonical status."
)
SYNC_BLOCKED_NEXT_STEP: Final = (
    "Finish editing the listed files; they are saved within 5 minutes and then merged. "
    "A held file needs the next step of changes.holds."
)
STATE_UNREADABLE_NEXT_STEP: Final = "Inspect and move the listed file aside, then run spec-dock canonical link."
GIT_IN_PROGRESS_NEXT_STEP: Final = (
    "Finish the unfinished Git operation in the catalog (for example git -C <catalog> merge --abort). "
    "For index.lock: if no git process works in the catalog, delete that file."
)
PAUSED_NEXT_STEP: Final = (
    "Read the pause reason in spec-dock canonical status, follow 'When sync stops' in the SpecDock docs, then run "
    "spec-dock canonical resume --adopt-remote (remote_rewritten, merge_failed) or --push-local (remote_deleted)."
)
SAVE_HELD_NEXT_STEPS: Final[Mapping[str, str]] = {
    "mass_delete": "If the deletions are intended, run spec-dock canonical accept --deletions; "
    "if not, run spec-dock canonical restore.",
    "secret": "Remove the secret from the file (the hold lifts by itself), or run spec-dock canonical accept <path> "
    "for a false positive.",
    "too_large": "Make the file 10 MiB or smaller, or run spec-dock canonical accept <path>.",
}
ADOPT_HELD_NEXT_STEP: Final = (
    "The listed files came back from local commits that GitHub dropped; fix or remove them in the catalog "
    "(or run spec-dock canonical accept <path>). Deletions (mass_delete) of files GitHub still has are "
    "applied only after spec-dock canonical accept --deletions. Then run spec-dock canonical resume --adopt-remote "
    "again."
)
RUNTIME_INCOMING_NEXT_STEP: Final = (
    "GitHub's spec-dock/canonical carries .runtime/, which SpecDock never syncs: in a separate clone with "
    "spec-dock/canonical checked out (not in the catalog), run git rm -r --cached .runtime, commit and push, then run "
    "spec-dock canonical resume --adopt-remote."
)
UNSAVED_CHANGES_RECOVERY: Final = "Check spec-dock canonical status and wait until everything is saved and pushed."
IGNORED_FILES_RECOVERY: Final = "Move the listed files out of the catalog, then run the same command again."
SCHEDULER_FAILED_RECOVERY: Final = "Check the reported output, then run spec-dock canonical link again."
NOT_HELD_RECOVERY: Final = "Name paths listed in changes.holds of spec-dock canonical status."
NOT_RESTORABLE_RECOVERY: Final = (
    "HEAD has no version of this file; fix or delete it yourself, or run spec-dock canonical accept <path> to save it."
)
PATH_NOT_FOUND_RECOVERY: Final = "Name an existing file inside the catalog (relative to spec-dock/initiatives)."
REGISTRY_UNREADABLE_RECOVERY: Final = "Inspect and move the listed registry aside, then run spec-dock canonical link."
STATE_ROOT_MISMATCH_NEXT_STEP: Final = (
    "Run the command with the state root the installed job uses (set XDG_STATE_HOME as when it was linked), "
    "or run spec-dock canonical remove for the catalogs registered there first."
)
SCOPE_KIND_CHANGED_RECOVERY: Final = (
    "Restore the GitHub kind label. If the new kind is intended, create the Scope again with that kind "
    "(spec-dock scope create), move the old directory's contents into the new <ID>/, then run "
    "spec-dock scope delete <current ID>."
)
STATUS_RECOVERY: Final = "spec-dock canonical status"
_FAILURE_EXIT_CODES: Final = frozenset({1, 2, 3, 4, 5, 7})

_GITHUB_RECOVERY: Final[Mapping[str, str]] = {
    GITHUB_UNAVAILABLE: "Check the network connection and run gh auth status, then run the same command.",
    GITHUB_ACCESS_DENIED: "Check the target Issue and gh auth status before a new explicit operation.",
    GITHUB_REQUEST_REJECTED: "Check the target Issue and gh auth status before a new explicit operation.",
    GITHUB_RESPONSE_INVALID: "Check the target Issue and gh auth status before a new explicit operation.",
    GITHUB_EFFECT_UNKNOWN: "Inspect the GitHub Issue before a new explicit operation; the write may have applied.",
    GITHUB_CREATE_IDENTITY_UNKNOWN: (
        "Find the GitHub Issue that may have been created, then finish it with spec-dock scope import github."
    ),
}
GITHUB_UNAVAILABLE_RECOVERY: Final = _GITHUB_RECOVERY[GITHUB_UNAVAILABLE]


class CanonicalCommandError(Exception):
    """A canonical command stopped before writing; dispatch renders it with its next step."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        exit_code: int = 3,
        recovery: tuple[str, ...] = (),
        details: dict[str, object] | None = None,
    ) -> None:
        if exit_code not in _FAILURE_EXIT_CODES:
            raise ValueError("a canonical failure before writing exits with 1, 2, 3, 4, 5 or 7")
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.recovery = recovery
        self.details = details or {}
        super().__init__(f"{code}: {message}")

    def result(self, command: str) -> OperationResult[DiagnosticData]:
        return canonical_failure(command, self.code, self.message, self.exit_code, self.recovery, self.details)


def canonical_failure(
    command: str,
    code: str,
    message: str,
    exit_code: int,
    recovery: tuple[str, ...],
    details: dict[str, object] | None = None,
) -> OperationResult[DiagnosticData]:
    return OperationResult(
        command,
        "failed",
        DiagnosticData(),
        exit_code,
        error=Diagnostic(code, message, details or {}),
        recovery=RecoveryInstructions(recovery) if recovery else None,
    )


def canonical_not_implemented(command: str) -> OperationResult[DiagnosticData]:
    return canonical_failure(
        command,
        CANONICAL_NOT_IMPLEMENTED,
        f"{command} has no canonical-mode implementation in this SpecDock build",
        3,
        (NOT_IMPLEMENTED_RECOVERY,),
    )


def canonical_not_migrated(command: str) -> OperationResult[DiagnosticData]:
    return canonical_failure(
        command,
        CANONICAL_NOT_MIGRATED,
        f"{command} needs a migrated repository; this workspace declares schema 3",
        3,
        (NOT_MIGRATED_RECOVERY,),
    )


def github_error_result(command: str, error: GithubStructureError) -> OperationResult[object]:
    """Render an uncaught GitHub failure; an uncertain write becomes partial with an unknown effect."""
    if error.code == GITHUB_RATE_LIMITED:
        recovery = (
            f"Run the same command after {error.retry_at}." if error.retry_at else "Wait, then run the same command."
        )
    else:
        recovery = _GITHUB_RECOVERY.get(error.code, _GITHUB_RECOVERY[GITHUB_UNAVAILABLE])
    details: dict[str, object] = {"status": error.status, "endpoint": error.endpoint}
    if error.retry_at is not None:
        details["retry_at"] = error.retry_at
    diagnostic = Diagnostic(error.code, error.message, details)
    if error.uncertain:
        return OperationResult(
            command,
            "partial",
            DiagnosticData(),
            6,
            effects=(Effect("github.write", "unknown", error.endpoint),),
            error=diagnostic,
            recovery=RecoveryInstructions((recovery,)),
        )
    return OperationResult(
        command, "failed", DiagnosticData(), 5, error=diagnostic, recovery=RecoveryInstructions((recovery,))
    )


def ignore_rules_next_step(assets: Sequence[StaticAsset], payload: bytes | None) -> str:
    """installation update replaces a missing or shipped (current or older) file; it never overwrites a modified one."""
    asset = next((item for item in assets if item.path == GITIGNORE_PATH), None)
    digest = None if payload is None else hashlib.sha256(payload).hexdigest()
    if asset is not None and classify_static_digest(asset, digest) in ("missing", "current", "known-old"):
        return IGNORE_RULES_UPDATE_NEXT_STEP
    return IGNORE_RULES_MERGE_NEXT_STEP

"""Canonical-mode failure codes and their next step, defined once for every canonical command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from spec_dock.runtime.infra.github_structure import (
    GITHUB_ACCESS_DENIED,
    GITHUB_CREATE_IDENTITY_UNKNOWN,
    GITHUB_EFFECT_UNKNOWN,
    GITHUB_RATE_LIMITED,
    GITHUB_REQUEST_REJECTED,
    GITHUB_RESPONSE_INVALID,
    GITHUB_UNAVAILABLE,
)
from spec_dock.runtime.presentation.command_data import DiagnosticData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock.runtime.infra.github_structure import GithubStructureError

CANONICAL_NOT_IMPLEMENTED: Final = "CANONICAL_NOT_IMPLEMENTED"
CANONICAL_NOT_MIGRATED: Final = "CANONICAL_NOT_MIGRATED"
CANONICAL_NOT_APPLICABLE: Final = "CANONICAL_NOT_APPLICABLE"
CANONICAL_NOT_LINKED: Final = "CANONICAL_NOT_LINKED"
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
START_LOCK_BUSY_RECOVERY: Final = "Wait a moment, then run spec-dock canonical link again."
LINK_AGAIN_RECOVERY: Final = "Run spec-dock canonical link again; it continues from the current state."
LINK_NETWORK_RECOVERY: Final = (
    "Check the network connection and the Git credentials for origin (for GitHub over HTTPS, gh auth setup-git), "
    "then run spec-dock canonical link again."
)
GIT_IDENTITY_RECOVERY: Final = (
    "Set the Git identity (git config user.name and user.email), then run spec-dock canonical link again."
)
INSTALLATION_UPDATE_RECOVERY: Final = "spec-dock installation update"
MAIN_MOVED_NEXT_STEP: Final = (
    "Git may also have reconnected the linked worktrees; run spec-dock canonical link in each linked worktree "
    "(for a worktree that also moved, first run git worktree repair <path> in the main checkout)."
)
REMOTE_MISSING_NEXT_STEP: Final = (
    "Check whether the GitHub branch spec-dock/canonical was deleted; if it was, sync stops; "
    "follow spec-dock canonical status."
)
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

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
CANONICAL_CHECK_FAILED: Final = "CANONICAL_CHECK_FAILED"

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

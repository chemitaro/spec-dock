"""Check that one commit of the code tree holds no specs and keeps intact SpecDock files (Epic design ch. 8)."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import TYPE_CHECKING, Final

from spec_dock import __version__
from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_CHECK_FAILED,
    NOT_MIGRATED_RECOVERY,
    CanonicalCommandError,
)
from spec_dock.runtime.application.project_context import (
    CANONICAL_WORKSPACE_SCHEMA,
    LEGACY_WORKSPACE_SCHEMA,
    NEW_WRITER_PROTOCOL,
    OLD_WRITER_PROTOCOL,
    resolve_git_context,
    workspace_mode,
)
from spec_dock.runtime.infra.commit_tree import list_commit_tree, read_blob, resolve_commit
from spec_dock.runtime.infra.static_assets import classify_static_digest, package_static_assets
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable, Mapping, Sequence
    from pathlib import Path

    from spec_dock.runtime.infra.commit_tree import TreeEntry
    from spec_dock.runtime.infra.static_assets import StaticAsset

# Contract C7: later Issues (the migration script's cut) copy these values and compare them in tests.
CI_VERSION_FILE: Final = "spec-dock/system/spec-dock-version"
WORKFLOW_SAMPLE: Final = "spec-dock/docs/ci/spec-dock-check.yml"
WORKFLOW_DESTINATION: Final = ".github/workflows/spec-dock-check.yml"
WORKFLOW_BRANCH_LINE: Final = "branches: [main]"

WORKSPACE_DECLARATION: Final = "spec-dock/workspace.json"
SPEC_DOCK_GITIGNORE: Final = "spec-dock/.gitignore"
# Epic design.md chapter 3 "無視の設定", relative to spec-dock/. This is contract C3, owned by I-2; whichever of
# I-2 and I-7 merges later replaces this copy with I-2's constant.
SPEC_DOCK_IGNORE_LINES: Final = ("/.canonical/", "/initiatives", "!/initiatives/")
SPEC_ROOT: Final = "spec-dock/initiatives"
CATALOG_ROOT: Final = "spec-dock/.canonical"
SPEC_PATH_TRACKED: Final = "SPEC_PATH_TRACKED"
CATALOG_PATH_TRACKED: Final = "CATALOG_PATH_TRACKED"
SCOPE_METADATA_TRACKED: Final = "SCOPE_METADATA_TRACKED"
WORKSPACE_NOT_MIGRATED: Final = "WORKSPACE_NOT_MIGRATED"
WORKSPACE_DECLARATION_INVALID: Final = "WORKSPACE_DECLARATION_INVALID"
STATIC_ASSET_INVALID: Final = "STATIC_ASSET_INVALID"
IGNORE_RULES_MISSING: Final = "IGNORE_RULES_MISSING"
SPEC_DOCK_VERSION_MISMATCH: Final = "SPEC_DOCK_VERSION_MISMATCH"
_SPEC_PATH_NEXT_STEP: Final = (
    "Remove the spec paths from this branch with git rm -r --cached -- spec-dock/initiatives, then commit; "
    "specs belong on the spec-dock/canonical branch."
)
_CATALOG_PATH_NEXT_STEP: Final = (
    "Remove the catalog paths from this branch with git rm -r --cached -- spec-dock/.canonical, then commit; "
    "spec-dock canonical link restores the ignore rules."
)
_DECLARATION_NEXT_STEP: Final = (
    f'Commit {WORKSPACE_DECLARATION} as {{"schema_version": {CANONICAL_WORKSPACE_SCHEMA}, '
    f'"writer_protocol": "{NEW_WRITER_PROTOCOL}"}}.'
)
_NEWER_SCHEMA_NEXT_STEP: Final = (
    f"Install the SpecDock version named by {CI_VERSION_FILE}; "
    f"this SpecDock knows workspace schema {LEGACY_WORKSPACE_SCHEMA} and {CANONICAL_WORKSPACE_SCHEMA}."
)
_STATIC_ASSET_NEXT_STEP: Final = (
    "Run spec-dock installation update --target <checkout> --backup-dir <new external directory> --yes "
    "and commit the static files; a modified file needs a manual merge."
)
_IGNORE_RULES_NEXT_STEP: Final = (
    f"Add these lines to {SPEC_DOCK_GITIGNORE} in this order, then commit: {', '.join(SPEC_DOCK_IGNORE_LINES)}."
)
_VERSION_NEXT_STEP: Final = (
    f"Run the SpecDock version named by {CI_VERSION_FILE}, "
    "or run spec-dock installation update and commit to record this version."
)
_SCOPE_METADATA_NEXT_STEP: Final = (
    "Remove the tracked .meta.json files from this branch with git rm --cached, then commit; "
    "canonical mode keeps Scope structure in GitHub Issues."
)


@dataclass(frozen=True)
class CheckOutcome:
    failures: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]
    version_file: str | None


def check_canonical_commit(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object]:
    """canonical check: judge the committed tree only; the working tree's declaration and mode are never read."""
    if namespace.expect_current is not None or namespace.expect_backend is not None:
        raise CanonicalCommandError(
            "PRECONDITION_FAILED",
            "canonical check reads a commit tree and cannot verify --expect-current or --expect-backend",
            recovery=(
                "Run spec-dock canonical check without --expect-current and --expect-backend; "
                "it reads a commit tree, not a selection.",
            ),
        )
    git = resolve_git_context(namespace.project, cwd, timeout=namespace.timeout)
    commit = resolve_commit(git.root, namespace.commit, timeout=namespace.timeout)
    if commit is None:
        raise CanonicalCommandError(
            "PRECONDITION_FAILED",
            f"canonical check needs an existing commit: {namespace.commit}",
            recovery=(
                "Pass an existing commit with --commit REV, or commit first; canonical check reads a commit tree.",
            ),
        )
    entries = list_commit_tree(git.root, commit, timeout=namespace.timeout)
    outcome = evaluate_commit_tree(
        entries,
        lambda entry: read_blob(git.root, entry.object_id, timeout=namespace.timeout),
        assets=package_static_assets(),
        running_version=__version__,
    )
    data = FamilyData(
        "canonical-check",
        {
            "commit": commit,
            "revision": namespace.commit,
            "valid": not outcome.failures,
            "failures": outcome.failures,
            "entry_count": len(entries),
            "package_version": __version__,
            "version_file": outcome.version_file,
        },
    )
    if not outcome.failures:
        return OperationResult(namespace.command_path, "succeeded", data, 0, warnings=outcome.warnings)
    next_steps = tuple(dict.fromkeys(str(failure.details["next_step"]) for failure in outcome.failures))
    return OperationResult(
        namespace.command_path,
        "failed",
        data,
        7,
        warnings=outcome.warnings,
        error=Diagnostic(
            CANONICAL_CHECK_FAILED,
            f"{len(outcome.failures)} problems in commit {commit[:12]}; each failure names its path and next step",
            {"failure_count": len(outcome.failures), "commit": commit},
        ),
        recovery=RecoveryInstructions(next_steps),
    )


def evaluate_commit_tree(
    entries: Sequence[TreeEntry],
    read: Callable[[TreeEntry], bytes],
    *,
    assets: Sequence[StaticAsset],
    running_version: str,
) -> CheckOutcome:
    """Apply the six rules to a listed commit tree; read is called only for the blobs a rule needs."""
    by_path = {entry.path: entry for entry in entries}
    failures = [*_path_failures(entries)]
    declaration = _declaration_failure(by_path.get(WORKSPACE_DECLARATION), read)
    if declaration is not None:
        failures.append(declaration)
    failures.extend(_asset_failures(assets, by_path, read))
    ignore = _ignore_rules_failure(by_path.get(SPEC_DOCK_GITIGNORE), read)
    if ignore is not None:
        failures.append(ignore)
    version_entry = by_path.get(CI_VERSION_FILE)
    if version_entry is None or version_entry.kind != "regular":
        return CheckOutcome(tuple(failures), (), None)  # rule 5 reports the missing version file
    try:
        version_file: str | None = read(version_entry).decode("utf-8").strip()
    except UnicodeDecodeError:
        version_file = None
    warnings: tuple[Diagnostic, ...] = ()
    if version_file != running_version:
        warnings = (
            Diagnostic(
                SPEC_DOCK_VERSION_MISMATCH,
                "the committed SpecDock version differs from the running SpecDock",
                {
                    "path": CI_VERSION_FILE,
                    "expected": running_version,
                    "actual": version_file,
                    "next_step": _VERSION_NEXT_STEP,
                },
            ),
        )
    return CheckOutcome(tuple(failures), warnings, version_file)


def _path_failures(entries: Sequence[TreeEntry]) -> tuple[Diagnostic, ...]:
    """Rules 1-3: each tracked path is reported once, by the first rule it breaks, in rule then tree order."""
    rules = (
        (SPEC_PATH_TRACKED, "a spec path is tracked on this branch", _SPEC_PATH_NEXT_STEP),
        (CATALOG_PATH_TRACKED, "a catalog path is tracked on this branch", _CATALOG_PATH_NEXT_STEP),
        (SCOPE_METADATA_TRACKED, "Scope metadata is tracked on this branch", _SCOPE_METADATA_NEXT_STEP),
    )
    found: list[list[Diagnostic]] = [[] for _rule in rules]
    for entry in entries:
        if _within(entry.path, SPEC_ROOT):
            index = 0
        elif _within(entry.path, CATALOG_ROOT):
            index = 1
        elif entry.path.startswith("spec-dock/") and entry.path.rsplit("/", 1)[-1] == ".meta.json":
            index = 2
        else:
            continue
        code, message, next_step = rules[index]
        found[index].append(_failure(code, entry.path, message, next_step, entry=entry.kind))
    return tuple(failure for group in found for failure in group)


def _declaration_failure(entry: TreeEntry | None, read: Callable[[TreeEntry], bytes]) -> Diagnostic | None:
    """Rule 4: schema 4 with a writer protocol the declaration reader knows; schema 3 is one failure."""
    if entry is None:
        return _invalid_declaration("missing", "the workspace declaration is not committed")
    if entry.kind != "regular":
        return _invalid_declaration("not-regular", "the workspace declaration is not a regular file")
    try:
        declaration = json.loads(read(entry).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        declaration = None
    if not isinstance(declaration, dict):
        return _invalid_declaration("invalid-json", "the workspace declaration is not a JSON object")
    version = declaration.get("schema_version")
    try:
        mode = workspace_mode(declaration)
    except ValueError:
        newer = type(version) is int and version > CANONICAL_WORKSPACE_SCHEMA
        return _invalid_declaration(
            "unknown-schema",
            "the workspace declaration has an unknown schema_version",
            _NEWER_SCHEMA_NEXT_STEP if newer else _DECLARATION_NEXT_STEP,
        )
    if mode == "legacy":
        return _failure(
            WORKSPACE_NOT_MIGRATED,
            WORKSPACE_DECLARATION,
            "this commit declares workspace schema 3; the repository is not migrated to canonical storage",
            NOT_MIGRATED_RECOVERY,
            schema_version=version,
        )
    if declaration.get("writer_protocol") not in (NEW_WRITER_PROTOCOL, OLD_WRITER_PROTOCOL):
        return _invalid_declaration(
            "unknown-writer-protocol", "the workspace declaration has an unknown writer_protocol"
        )
    return None


def _invalid_declaration(reason: str, message: str, next_step: str = _DECLARATION_NEXT_STEP) -> Diagnostic:
    return _failure(WORKSPACE_DECLARATION_INVALID, WORKSPACE_DECLARATION, message, next_step, reason=reason)


def _asset_failures(
    assets: Sequence[StaticAsset], by_path: Mapping[str, TreeEntry], read: Callable[[TreeEntry], bytes]
) -> tuple[Diagnostic, ...]:
    """Rule 5: package-owned static files match this package or a known older one (installation show's rule)."""
    failures: list[Diagnostic] = []
    for asset in assets:
        if asset.init_only:
            continue  # the declaration is user-owned after init; rule 4 judges it
        entry = by_path.get(asset.path)
        if entry is None:
            classification = classify_static_digest(asset, None)
        elif entry.kind != "regular":
            classification = "unsafe"
        else:
            classification = classify_static_digest(asset, hashlib.sha256(read(entry)).hexdigest())
        if classification not in ("current", "known-old"):
            failures.append(
                _failure(
                    STATIC_ASSET_INVALID,
                    asset.path,
                    f"a SpecDock static file is {classification}",
                    _STATIC_ASSET_NEXT_STEP,
                    classification=classification,
                )
            )
    return tuple(failures)


def _ignore_rules_failure(entry: TreeEntry | None, read: Callable[[TreeEntry], bytes]) -> Diagnostic | None:
    """Rule 5: the three ignore lines exist and the negation follows the link rule (Git's last match wins)."""
    if entry is None or entry.kind != "regular":
        return None  # the static-asset rule already reports this path
    lines = [line.rstrip() for line in read(entry).decode("utf-8", errors="replace").split("\n")]
    missing = [line for line in SPEC_DOCK_IGNORE_LINES if line not in lines]
    link, negation = SPEC_DOCK_IGNORE_LINES[1:]
    misordered = not missing and _last_index(lines, negation) < _last_index(lines, link)
    if not missing and not misordered:
        return None
    return _failure(
        IGNORE_RULES_MISSING,
        SPEC_DOCK_GITIGNORE,
        "the canonical ignore rules are missing or out of order",
        _IGNORE_RULES_NEXT_STEP,
        missing_lines=missing,
        misordered=misordered,
    )


def _last_index(lines: Sequence[str], value: str) -> int:
    return len(lines) - 1 - lines[::-1].index(value)


def _within(path: str, root: str) -> bool:
    return path == root or path.startswith(f"{root}/")


def _failure(code: str, path: str, message: str, next_step: str, **details: object) -> Diagnostic:
    return Diagnostic(code, message, {"path": path, "next_step": next_step, **details})

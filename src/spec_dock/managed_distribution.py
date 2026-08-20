"""Distribution catalog, identity validation, and safe distribution plans.

The module owns the provider physical catalog and the shared S20/S25/S30
distribution boundary.  Plan construction remains read-only; the S30 apply
seam mutates only a validated target through descriptor-relative, no-follow
operations and fails closed when an identity changes.
"""

from __future__ import annotations

from contextlib import suppress
import ctypes
from dataclasses import dataclass, field, replace
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import stat
import sys
import time
from typing import TYPE_CHECKING, Any, Literal, NoReturn

if TYPE_CHECKING:
    from collections.abc import Callable


class DistributionManifestError(ValueError):
    """Raised when the provider-private distribution manifest is unsafe."""


class DistributionPlanError(ValueError):
    """Raised when a read-only assessment cannot issue mutation authority."""


class DistributionApplyError(RuntimeError):
    """Raised when a distribution plan cannot be applied safely."""

    def __init__(
        self,
        message: str,
        *,
        phase: str | None = None,
        applied_paths: tuple[str, ...] = (),
        pending_paths: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.phase = phase
        self.applied_paths = applied_paths
        self.pending_paths = pending_paths


class DistributionAdmissionError(RuntimeError):
    """Raised when a consumer cannot safely enter a distribution operation."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class DistributionIdentity:
    """The immutable identity of one provider or historical file."""

    kind: str
    sha256: str | None = None
    mode: int | None = None
    target: str | None = None


@dataclass(frozen=True)
class DistributionSourceSnapshot:
    """Stable identity of a provider regular file captured with its bytes."""

    device: int
    inode: int
    ctime_ns: int
    mtime_ns: int
    size: int
    mode: int


@dataclass(frozen=True)
class DistributionAsset:
    """One file in the physical Current provider catalog."""

    path: str
    identity: DistributionIdentity
    source_path: str | None = None
    source_snapshot: DistributionSourceSnapshot | None = None
    generated_content: bytes | None = None
    refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None


DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]
DistributionActionName = Literal["create", "adopt", "upgrade", "prune", "preserve", "block"]
DistributionProvenance = Literal["missing", "current", "historical", "unknown"]


@dataclass(frozen=True)
class DistributionAction:
    """One read-only classification result for a consumer path."""

    path: str
    operation: DistributionOperation
    action: DistributionActionName
    provenance: DistributionProvenance
    reason: str
    blocked: bool = False

    @property
    def classification(self) -> DistributionActionName:
        """Design vocabulary alias for the action kind."""

        return self.action

    @property
    def blocking(self) -> bool:
        """Design vocabulary alias for a preserve-and-block result."""

        return self.blocked

    @property
    def operator_action(self) -> str:
        """Sanitized next step for a human or a later apply phase."""

        if not self.blocked:
            return "no mutation required"
        if self.reason in {"unknown-current-collision", "obsolete-identity-unknown"}:
            return "inspect ownership and resolve the collision before retrying"
        if self.reason == "hard-link-mutation-unsafe":
            return "remove the unexpected hard link before retrying"
        return "inspect the path type and resolve the collision before retrying"

    def diagnostic(self) -> dict[str, object]:
        """Return only repository-relative, non-content diagnostic fields."""

        return {
            "operation": self.operation,
            "path": self.path,
            "classification": self.classification,
            "provenance": self.provenance,
            "reason": self.reason,
            "blocking": self.blocking,
            "operator_action": self.operator_action,
        }


@dataclass(frozen=True)
class DistributionManifest:
    """Validated historical-only manifest sections."""

    schema_version: int
    recognized_workspace_versions: tuple[dict[str, Any], ...]
    historical_current_identities: tuple[dict[str, Any], ...]
    trusted_consumer_manifests: tuple[dict[str, Any], ...]
    obsolete_exact_files: tuple[dict[str, Any], ...]
    historical_shortcuts: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class PathIdentitySnapshot:
    """No-follow identity of one repository-relative filesystem component."""

    relative_path: str
    exists: bool
    device: int | None = None
    inode: int | None = None
    ctime_ns: int | None = None
    file_type: str | None = None
    link_count: int | None = None
    identity: DistributionIdentity | None = None


@dataclass(frozen=True)
class DistributionTargetSnapshot:
    """Root, parent, and exact-target identities captured during preflight."""

    root: PathIdentitySnapshot
    parents: tuple[PathIdentitySnapshot, ...]
    target: PathIdentitySnapshot


@dataclass(frozen=True)
class DistributionPlan:
    """Read-only S20/S25 plan surface consumed by the S30 apply seam."""

    current_assets: tuple[DistributionAsset, ...]
    actions: tuple[DistributionAction, ...]
    manifest: DistributionManifest
    scaffold_root: Path | None = None
    install_root: Path | None = None
    manifest_path: Path | None = None
    target_root: Path | None = None
    operation: DistributionOperation = "fresh"
    target_snapshots: tuple[tuple[str, DistributionTargetSnapshot], ...] = ()
    scaffold_assets: tuple[DistributionAsset, ...] = ()

    @property
    def scaffold_paths(self) -> frozenset[str]:
        """Return target paths owned by the provider scaffold portion."""

        return frozenset(asset.path for asset in self.scaffold_assets)

    @property
    def blocked(self) -> bool:
        """Whether any classified action requires preserve-and-block."""

        return any(action.blocked for action in self.actions)


RecognizedDistributionIntent = Literal["update", "init-force"]


@dataclass(frozen=True)
class WorkspaceAssessment:
    """Read-only recognized-workspace observation without mutation authority."""

    intent: RecognizedDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]
    blockers: tuple[DistributionAction, ...]


@dataclass(frozen=True)
class ExecutableMutationPlan:
    """A blocker-free recognized plan bound to one root and contract."""

    intent: RecognizedDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    plan_digest: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]


JournalCheckpoint = Literal["pending", "published", "verified"]
JournalStatus = Literal["prepared", "executing", "verifying", "completed"]


@dataclass(frozen=True)
class OperationJournalAction:
    path: str
    action: DistributionActionName
    provenance: DistributionProvenance
    reason: str
    precondition: dict[str, object]
    postcondition: dict[str, object]
    checkpoint: JournalCheckpoint = "pending"


@dataclass(frozen=True)
class OperationJournal:
    schema_version: int
    protocol_version: int
    operation_id: str
    root_identity: DistributionRootIdentity
    workspace_identity: PathIdentitySnapshot
    intent: RecognizedDistributionIntent
    authority: str
    package_version: str
    contract_identity: str
    plan_digest: str
    created_at_ns: int
    status: JournalStatus
    actions: tuple[OperationJournalAction, ...]
    staging_leases: tuple[DistributionStageOwnership, ...] = ()
    created_parent_bindings: tuple[PathIdentitySnapshot, ...] = ()
    source_snapshot: PathIdentitySnapshot | None = field(default=None, compare=False, repr=False)
    source_sha256: str | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class DistributionProcessResult:
    status: Literal["completed", "blocked", "recovery_required"]
    intent: RecognizedDistributionIntent
    actions: tuple[DistributionAction, ...]
    plan_digest: str | None = None
    reason: str | None = None
    applied_paths: tuple[str, ...] = ()
    pending_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class DistributionResult:
    """Result of a completed, identity-checked distribution apply."""

    status: Literal["complete"]
    actions: tuple[DistributionAction, ...]


@dataclass(frozen=True)
class DistributionRootIdentity:
    """Stable identity used to bind a retry marker to one repository root."""

    device: int
    inode: int


@dataclass(frozen=True)
class DistributionStageOwnership:
    """Recorded identity of one private staging entry created by an apply."""

    path: str
    stage_name: str
    device: int
    inode: int
    ctime_ns: int
    file_type: Literal["regular", "symlink"]


@dataclass(frozen=True)
class DistributionRetryMarker:
    """Validated init/update retry marker without absolute paths or secrets."""

    operation: Literal["fresh", "update", "init-force"]
    package_version: str
    target_root: DistributionRootIdentity
    last_completed_phase: str
    purpose: Literal["distribution-rerun", "recognized-journal-forward-only"]
    stage_ownership: tuple[DistributionStageOwnership, ...] = ()
    operation_id: str | None = None
    contract_identity: str | None = None
    plan_digest: str | None = None
    source_snapshot: PathIdentitySnapshot | None = field(default=None, compare=False, repr=False)
    source_sha256: str | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class DistributionAdmission:
    """Read-only result of operation admission."""

    operation: DistributionOperation
    status: Literal["fresh", "existing", "recognized", "retry", "uninstall-retry"]
    package_version: str
    target_version: str | None = None
    marker: DistributionRetryMarker | None = None
    version_identity: DistributionIdentity | None = None

    def diagnostic(self) -> dict[str, object]:
        """Return stable, repository-relative admission evidence."""

        return {
            "operation": self.operation,
            "status": self.status,
            "package_version": self.package_version,
            "target_version": self.target_version,
            "retry": self.marker is not None,
        }


_SCHEMA_VERSION = 1
_MANIFEST_FIELDS = frozenset({
    "schema_version",
    "recognized_workspace_versions",
    "historical_current_identities",
    "trusted_consumer_manifests",
    "obsolete_exact_files",
    "historical_shortcuts",
})
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_GLOB_CHARS = frozenset("*?[]{}")


def _fail(message: str) -> NoReturn:
    raise DistributionManifestError(message)


def _exact_relative_path(value: Any, *, field_name: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        _fail(f"{field_name} must be a non-empty repository-relative path")
    if "\\" in value or "\x00" in value or value.startswith("/") or _DRIVE_RE.match(value):
        _fail(f"{field_name} must be a POSIX repository-relative path")
    if value.endswith("/") or any(char in _GLOB_CHARS for char in value):
        _fail(f"{field_name} must identify one exact file")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        _fail(f"{field_name} must not contain empty, '.', or '..' path components")
    normalized = PurePosixPath(value)
    if normalized.as_posix() != value:
        _fail(f"{field_name} is not normalized")
    return normalized


def _sha256(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        _fail(f"{field_name} must be lowercase hexadecimal SHA-256")
    return value


def _source(value: Any, *, field_name: str) -> dict[str, Any]:
    """Validate trace evidence without exposing it in runtime diagnostics."""

    if not isinstance(value, dict) or not value:
        _fail(f"{field_name} must contain historical trace evidence")
    kind = value.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        _fail(f"{field_name}.kind must be non-empty")
    if "path" in value:
        _exact_relative_path(value["path"], field_name=f"{field_name}.path")
    for key in ("ref", "artifact"):
        if key in value and (not isinstance(value[key], str) or not value[key].strip()):
            _fail(f"{field_name}.{key} must be non-empty when present")
    return dict(value)


def _identity_record(value: Any, *, field_name: str, require_source: bool = True) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{field_name} must be an object")
    allowed = {"path", "kind", "sha256", "mode", "target", "source"}
    unknown = set(value) - allowed
    if unknown:
        _fail(f"{field_name} contains unsupported fields: {', '.join(sorted(unknown))}")
    path = _exact_relative_path(value.get("path"), field_name=f"{field_name}.path")
    kind = value.get("kind")
    if kind == "regular":
        digest = _sha256(value.get("sha256"), field_name=f"{field_name}.sha256")
        if "target" in value:
            _fail(f"{field_name}.target is only valid for symlinks")
        result: dict[str, Any] = {"path": path.as_posix(), "kind": kind, "sha256": digest}
        if "mode" in value:
            mode = value["mode"]
            if isinstance(mode, bool) or not isinstance(mode, int) or not 0 <= mode <= 0o777:
                _fail(f"{field_name}.mode must be an integer between 0 and 0o777")
            result["mode"] = mode
    elif kind == "symlink":
        target = value.get("target")
        if not isinstance(target, str) or not target or "\\" in target or target.startswith("/"):
            _fail(f"{field_name}.target must be a normalized relative link target")
        target_path = _exact_relative_path(target, field_name=f"{field_name}.target")
        if "sha256" in value:
            _fail(f"{field_name}.sha256 is not valid for symlinks")
        result = {"path": path.as_posix(), "kind": kind, "target": target_path.as_posix()}
    else:
        _fail(f"{field_name}.kind must be 'regular' or 'symlink'")
    if require_source:
        result["source"] = _source(value.get("source"), field_name=f"{field_name}.source")
    elif "source" in value:
        result["source"] = _source(value["source"], field_name=f"{field_name}.source")
    return result


def _section_list(raw: dict[str, Any], name: str) -> list[Any]:
    value = raw.get(name)
    if not isinstance(value, list):
        _fail(f"manifest.{name} must be an array")
    return value


def _validate_manifest(raw: Any) -> DistributionManifest:
    if not isinstance(raw, dict):
        _fail("manifest top-level value must be an object")
    if set(raw) != _MANIFEST_FIELDS:
        missing = sorted(_MANIFEST_FIELDS - set(raw))
        extra = sorted(set(raw) - _MANIFEST_FIELDS)
        detail = []
        if missing:
            detail.append(f"missing={','.join(missing)}")
        if extra:
            detail.append(f"unsupported={','.join(extra)}")
        _fail("manifest schema fields are invalid (" + "; ".join(detail) + ")")
    if raw["schema_version"] != _SCHEMA_VERSION:
        _fail(f"unsupported manifest schema_version: {raw['schema_version']!r}")

    recognized: list[dict[str, Any]] = []
    for index, item in enumerate(_section_list(raw, "recognized_workspace_versions")):
        if not isinstance(item, dict) or set(item) != {"version", "anchors"}:
            _fail(f"recognized_workspace_versions[{index}] has invalid shape")
        version = item.get("version")
        if (
            not isinstance(version, str)
            or re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version) is None
        ):
            _fail(f"recognized_workspace_versions[{index}].version must be canonical MAJOR.MINOR.PATCH")
        anchors_raw = item.get("anchors")
        if not isinstance(anchors_raw, list) or not anchors_raw:
            _fail(f"recognized_workspace_versions[{index}].anchors must be non-empty")
        anchors = tuple(
            _identity_record(anchor, field_name=f"recognized_workspace_versions[{index}].anchors[{j}]")
            for j, anchor in enumerate(anchors_raw)
        )
        recognized.append({"version": version, "anchors": anchors})

    historical_current = [
        _identity_record(item, field_name=f"historical_current_identities[{index}]")
        for index, item in enumerate(_section_list(raw, "historical_current_identities"))
    ]

    trusted: list[dict[str, Any]] = []
    for index, item in enumerate(_section_list(raw, "trusted_consumer_manifests")):
        if not isinstance(item, dict) or set(item) != {"path", "kind", "sha256", "source", "claims"}:
            _fail(f"trusted_consumer_manifests[{index}] has invalid shape")
        manifest_identity = _identity_record(
            {key: item[key] for key in ("path", "kind", "sha256", "source")},
            field_name=f"trusted_consumer_manifests[{index}]",
        )
        claims_raw = item.get("claims")
        if not isinstance(claims_raw, list):
            _fail(f"trusted_consumer_manifests[{index}].claims must be an array")
        claims = tuple(
            _identity_record(claim, field_name=f"trusted_consumer_manifests[{index}].claims[{j}]")
            for j, claim in enumerate(claims_raw)
        )
        manifest_identity["claims"] = claims
        trusted.append(manifest_identity)

    obsolete: list[dict[str, Any]] = []
    for index, item in enumerate(_section_list(raw, "obsolete_exact_files")):
        if not isinstance(item, dict) or set(item) != {"path", "surface", "identities", "on_unknown"}:
            _fail(f"obsolete_exact_files[{index}] has invalid shape")
        path = _exact_relative_path(item.get("path"), field_name=f"obsolete_exact_files[{index}].path")
        surface = item.get("surface")
        if not isinstance(surface, str) or not surface.strip():
            _fail(f"obsolete_exact_files[{index}].surface must be non-empty")
        identities_raw = item.get("identities")
        if not isinstance(identities_raw, list):
            _fail(f"obsolete_exact_files[{index}].identities must be an array")
        identities = tuple(
            _identity_record(identity, field_name=f"obsolete_exact_files[{index}].identities[{j}]")
            for j, identity in enumerate(identities_raw)
        )
        if any(identity["path"] != path.as_posix() for identity in identities):
            _fail(f"obsolete_exact_files[{index}] identity path must match record path")
        if item.get("on_unknown") != "preserve-and-block":
            _fail(f"obsolete_exact_files[{index}].on_unknown must be preserve-and-block")
        obsolete.append({
            "path": path.as_posix(),
            "surface": surface,
            "identities": identities,
            "on_unknown": "preserve-and-block",
        })

    shortcuts: list[dict[str, Any]] = []
    for index, item in enumerate(_section_list(raw, "historical_shortcuts")):
        if not isinstance(item, dict) or set(item) != {"path", "kind", "target", "source"}:
            _fail(f"historical_shortcuts[{index}] has invalid shape")
        if item.get("kind") != "symlink":
            _fail(f"historical_shortcuts[{index}].kind must be symlink")
        path = _exact_relative_path(item.get("path"), field_name=f"historical_shortcuts[{index}].path")
        target = _exact_relative_path(item.get("target"), field_name=f"historical_shortcuts[{index}].target")
        shortcuts.append({
            "path": path.as_posix(),
            "kind": "symlink",
            "target": target.as_posix(),
            "source": _source(item.get("source"), field_name=f"historical_shortcuts[{index}].source"),
        })

    return DistributionManifest(
        schema_version=_SCHEMA_VERSION,
        recognized_workspace_versions=tuple(recognized),
        historical_current_identities=tuple(historical_current),
        trusted_consumer_manifests=tuple(trusted),
        obsolete_exact_files=tuple(obsolete),
        historical_shortcuts=tuple(shortcuts),
    )


def _path_overlaps(left: str, right: str) -> bool:
    left_parts = PurePosixPath(left).parts
    right_parts = PurePosixPath(right).parts
    return left_parts[: len(right_parts)] == right_parts or right_parts[: len(left_parts)] == left_parts


def _assert_no_manifest_overlap(
    current_paths: set[str],
    manifest: DistributionManifest,
    *,
    protected_paths: set[str] | frozenset[str] = frozenset(),
) -> None:
    for current_path in current_paths:
        if any(_path_overlaps(current_path, protected_path) for protected_path in protected_paths):
            _fail(f"physical Current path overlaps protected workspace surface: {current_path}")

    seen_historical: set[tuple[str, str, str | None, str | None]] = set()
    for item in manifest.historical_current_identities:
        signature = (item["path"], item["kind"], item.get("sha256"), item.get("target"))
        if signature in seen_historical:
            _fail(f"duplicate historical identity: {item['path']}")
        seen_historical.add(signature)

    records: list[tuple[str, str, bool, bool]] = []
    for version_index, version in enumerate(manifest.recognized_workspace_versions):
        for anchor_index, anchor in enumerate(version["anchors"]):
            records.append((
                anchor["path"],
                f"recognized_workspace_versions[{version_index}].anchors[{anchor_index}]",
                False,
                True,
            ))
    for item in manifest.historical_current_identities:
        # A historical identity is intentionally allowed to describe the same
        # target path as a newly shipped Current asset.  It is the evidence
        # used to classify an existing consumer file for upgrade/prune.
        records.append((item["path"], "historical_current_identities", True, False))
    for item in manifest.obsolete_exact_files:
        records.append((item["path"], "obsolete_exact_files", False, False))
    for manifest_index, item in enumerate(manifest.trusted_consumer_manifests):
        records.append((item["path"], f"trusted_consumer_manifests[{manifest_index}]", False, False))
        for claim_index, claim in enumerate(item["claims"]):
            records.append((
                claim["path"],
                f"trusted_consumer_manifests[{manifest_index}].claims[{claim_index}]",
                True,
                False,
            ))
    for item in manifest.historical_shortcuts:
        # The canonical shortcut is a Current identity even though it is
        # synthesized rather than shipped as a regular file.  Historical
        # shortcut records may therefore share that exact path as evidence;
        # ancestor/descendant overlap remains invalid.
        records.append((item["path"], "historical_shortcuts", True, False))

    for index, (path, section, allows_current_overlap, allows_protected_overlap) in enumerate(records):
        if allows_current_overlap:
            current_overlap = any(
                _path_overlaps(path, current_path) and path != current_path for current_path in current_paths
            )
        else:
            current_overlap = any(_path_overlaps(path, current_path) for current_path in current_paths)
        if current_overlap:
            _fail(f"manifest path overlaps physical Current catalog: {path}")
        if not allows_protected_overlap and any(
            _path_overlaps(path, protected_path) for protected_path in protected_paths
        ):
            _fail(f"manifest path overlaps protected workspace surface: {path}")
        for other_path, other_section, _, _ in records[:index]:
            if section == "historical_current_identities" and other_section == section and path == other_path:
                # Multiple releases may legitimately have different bytes at
                # one reusable Current path; exact duplicates were rejected
                # above by identity signature.
                continue
            # A trusted claim is supplemental evidence for an obsolete exact
            # record at the same path, not a second mutable path declaration.
            trusted_claim = ".claims[" in section and other_section == "obsolete_exact_files"
            obsolete_claim = ".claims[" in other_section and section == "obsolete_exact_files"
            historical_trusted = ".claims[" in section and other_section == "historical_current_identities"
            trusted_historical = ".claims[" in other_section and section == "historical_current_identities"
            if (trusted_claim or obsolete_claim or historical_trusted or trusted_historical) and path == other_path:
                continue
            if _path_overlaps(path, other_path):
                _fail(f"manifest paths overlap: {section}:{path} and {other_section}:{other_path}")


def _load_manifest(path: Path) -> DistributionManifest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DistributionManifestError(f"unable to load distribution manifest: {path.name}") from exc
    return _validate_manifest(raw)


_CANONICAL_VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\n$")
_DISTRIBUTION_RETRY_MARKER_REL = Path("spec-dock/.distribution-retry.json")
_UNINSTALL_RETRY_MARKER_REL = Path("spec-dock/.uninstall-retry.json")
_DISTRIBUTION_JOURNAL_REL = Path("spec-dock/.distribution-journal.json")
_DISTRIBUTION_JOURNAL_SCHEMA_VERSION = 1
_DISTRIBUTION_JOURNAL_PROTOCOL_VERSION = 1
_DISTRIBUTION_RETRY_SCHEMA_VERSION = 1
_DISTRIBUTION_RETRY_PURPOSE: Literal["distribution-rerun"] = "distribution-rerun"
_DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION = 2
_DISTRIBUTION_JOURNAL_GUARD_PURPOSE: Literal["recognized-journal-forward-only"] = "recognized-journal-forward-only"
_DISTRIBUTION_RETRY_PHASES = frozenset({
    "preflight-complete",
    "managed-scaffold-refreshed",
    "current-external-materialized",
    "obsolete-pruned",
    "post-verified",
    "version-written",
})
_UNINSTALL_RETRY_MARKER_PAYLOAD = {
    "schema_version": 1,
    "managed_by": "spec-dock",
    "purpose": "uninstall-rerun",
}
_VERSION_ANCHOR_PATHS = frozenset({"spec-dock/scripts/spec-dock", "spec-dock/.gitignore"})
_SCAFFOLD_MANAGED_ROOTS = ("docs", "templates", "scripts", "system")
_PROTECTED_WORKSPACE_ROOTS = frozenset({
    *(f"spec-dock/{name}" for name in _SCAFFOLD_MANAGED_ROOTS),
    "spec-dock/initiatives",
    "spec-dock/active",
    "spec-dock/.agent",
    "spec-dock/.workbench",
    "spec-dock/.gitignore",
    "spec-dock/spec-dock.version",
    "spec-dock/.distribution-retry.json",
    "spec-dock/.distribution-journal.json",
    "spec-dock/.uninstall-retry.json",
})


def _protected_workspace_paths(scaffold_assets: tuple[DistributionAsset, ...]) -> frozenset[str]:
    """Return all provider-owned and user-preserve workspace boundaries."""

    return _PROTECTED_WORKSPACE_ROOTS | frozenset(asset.path for asset in scaffold_assets)


def _admission_block(reason: str, detail: str) -> NoReturn:
    raise DistributionAdmissionError(f"distribution admission blocked ({reason}): {detail}", reason=reason)


def _parse_canonical_version(value: str, *, source: str) -> tuple[int, int, int]:
    """Parse the deliberately narrow version grammar used by workspace markers."""

    try:
        match = _CANONICAL_VERSION_RE.fullmatch(value)
    except (OverflowError, ValueError):
        match = None
    if match is None:
        _admission_block("invalid-version", f"{source} is not canonical MAJOR.MINOR.PATCH")
    assert match is not None
    try:
        return tuple(int(component) for component in match.groups())  # type: ignore[return-value]
    except (OverflowError, ValueError):
        _admission_block("invalid-version", f"{source} contains an invalid numeric component")


def _parse_package_version(value: str, *, source: str) -> tuple[int, int, int]:
    if "\n" in value or "\r" in value:
        _admission_block("invalid-version", f"{source} must not contain a line break")
    return _parse_canonical_version(value + "\n", source=source)


def _read_no_follow_regular_evidence(
    path: Path,
    *,
    label: str,
    allow_missing: bool = False,
) -> tuple[bytes, os.stat_result] | None:
    """Read one link-count-one regular file and retain its held identity."""

    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        _admission_block("platform-unsupported", "no-follow regular-file admission is unavailable")
    if path.is_symlink():
        if label == "uninstall retry marker":
            _admission_block("invalid-file", "symlinked SpecDock uninstall retry marker")
        _admission_block("invalid-file", f"{label} is symlinked")
    flags = os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        if allow_missing:
            return None
        _admission_block("missing", f"{label} is missing")
    except OSError:
        _admission_block("invalid-file", f"{label} cannot be opened without following links")
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            _admission_block("invalid-file", f"{label} must be a regular file")
        if before.st_nlink != 1:
            _admission_block("hard-link", f"{label} must have link count 1")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        content = b"".join(chunks)
        after = os.fstat(fd)
        if (
            before.st_dev,
            before.st_ino,
            before.st_ctime_ns,
            before.st_mode,
            before.st_nlink,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_ctime_ns,
            after.st_mode,
            after.st_nlink,
        ):
            _admission_block("invalid-file", f"{label} changed while it was read")
        return content, after
    except OSError:
        _admission_block("read-error", f"{label} cannot be read safely")
    finally:
        os.close(fd)


def _read_no_follow_regular(path: Path, *, label: str, allow_missing: bool = False) -> bytes | None:
    """Read one link-count-one regular file without following a symlink."""

    evidence = _read_no_follow_regular_evidence(path, label=label, allow_missing=allow_missing)
    return evidence[0] if evidence is not None else None


def _path_present_no_follow(path: Path) -> bool:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return False
    except OSError:
        _admission_block("marker-invalid", f"cannot inspect {path.name}")
    return True


def _root_identity_for_admission(target_root: Path) -> DistributionRootIdentity:
    try:
        info = os.lstat(target_root)
    except OSError:
        _admission_block("target-root-invalid", "target root cannot be inspected safely")
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        _admission_block("target-root-invalid", "target root must be a real directory")
    return DistributionRootIdentity(device=info.st_dev, inode=info.st_ino)


def _is_preserved_specs_workspace(target_root: Path) -> bool:
    """Recognize only the exact boundary left by a successful keep-specs uninstall."""

    specdock_path = target_root / "spec-dock"
    try:
        specdock_info = os.lstat(specdock_path)
    except FileNotFoundError:
        return False
    except OSError:
        _admission_block("workspace-invalid", "managed workspace cannot be inspected safely")
    if stat.S_ISLNK(specdock_info.st_mode) or not stat.S_ISDIR(specdock_info.st_mode):
        return False
    try:
        children = list(os.scandir(specdock_path))
    except OSError:
        _admission_block("workspace-invalid", "managed workspace cannot be inspected safely")
    if {entry.name for entry in children} != {"initiatives"}:
        return False
    initiatives = children[0]
    try:
        initiatives_info = initiatives.stat(follow_symlinks=False)
    except OSError:
        _admission_block("workspace-invalid", "preserved spec history cannot be inspected safely")
    if initiatives.name != "initiatives" or not stat.S_ISDIR(initiatives_info.st_mode):
        return False
    pending = [initiatives.path]
    while pending:
        current = pending.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            _admission_block("workspace-invalid", "preserved spec history cannot be inspected safely")
        for entry in entries:
            try:
                entry_info = entry.stat(follow_symlinks=False)
            except OSError:
                _admission_block("workspace-invalid", "preserved spec history cannot be inspected safely")
            if stat.S_ISLNK(entry_info.st_mode):
                return False
            if stat.S_ISDIR(entry_info.st_mode):
                pending.append(entry.path)
                continue
            if not stat.S_ISREG(entry_info.st_mode):
                return False
    return True


def _assert_real_parent_chain(target_root: Path, relative_path: str, *, label: str) -> bool:
    current = target_root
    for component in PurePosixPath(relative_path).parts[:-1]:
        current = current / component
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            return False
        except OSError:
            _admission_block("invalid-file", f"{label} parent cannot be inspected")
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            _admission_block("invalid-file", f"{label} parent must be a real directory")
    return True


def _read_distribution_retry_marker(target_root: Path) -> DistributionRetryMarker | None:
    path = target_root / _DISTRIBUTION_RETRY_MARKER_REL
    if not _path_present_no_follow(path):
        return None
    evidence = _read_no_follow_regular_evidence(path, label="distribution retry marker")
    assert evidence is not None
    raw_bytes, source_info = evidence
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _admission_block("marker-invalid", "distribution retry marker is not valid UTF-8 JSON")
    if not isinstance(raw, dict):
        _admission_block("marker-invalid", "distribution retry marker must be an object")
    base_fields = {
        "schema_version",
        "operation",
        "package_version",
        "target_root",
        "last_completed_phase",
        "purpose",
    }
    schema_version = raw.get("schema_version")
    purpose = raw.get("purpose")
    supported_guard = (
        schema_version == _DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION and purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE
    )
    supported_legacy = schema_version == _DISTRIBUTION_RETRY_SCHEMA_VERSION and purpose == _DISTRIBUTION_RETRY_PURPOSE
    expected_fields = (
        base_fields | {"operation_id", "contract_identity", "plan_digest"} if supported_guard else base_fields
    )
    raw_fields = set(raw)
    if raw_fields != expected_fields and raw_fields != expected_fields | {"stage_ownership"}:
        _admission_block("marker-invalid", "distribution retry marker fields are invalid")
    if not supported_guard and not supported_legacy:
        _admission_block("marker-invalid", "distribution retry marker schema is unsupported")
    operation = raw.get("operation")
    if operation not in {"fresh", "update", "init-force"}:
        _admission_block("marker-invalid", "distribution retry marker operation is unsupported")
    package_version = raw.get("package_version")
    if not isinstance(package_version, str):
        _admission_block("marker-invalid", "distribution retry marker package_version is invalid")
    _parse_package_version(package_version, source="distribution retry marker package_version")
    root = raw.get("target_root")
    if not isinstance(root, dict) or set(root) != {"device", "inode"}:
        _admission_block("marker-invalid", "distribution retry marker target_root identity is invalid")
    device = root.get("device")
    inode = root.get("inode")
    if (
        isinstance(device, bool)
        or not isinstance(device, int)
        or device <= 0
        or isinstance(inode, bool)
        or not isinstance(inode, int)
        or inode <= 0
    ):
        _admission_block("marker-invalid", "distribution retry marker target_root identity is invalid")
    phase = raw.get("last_completed_phase")
    if not isinstance(phase, str) or phase not in _DISTRIBUTION_RETRY_PHASES:
        _admission_block("marker-invalid", "distribution retry marker phase is invalid")
    operation_id = raw.get("operation_id") if supported_guard else None
    contract_identity = raw.get("contract_identity") if supported_guard else None
    plan_digest = raw.get("plan_digest") if supported_guard else None
    if supported_guard and (
        not isinstance(operation_id, str)
        or not operation_id
        or not isinstance(contract_identity, str)
        or not contract_identity
        or not isinstance(plan_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", plan_digest)
    ):
        _admission_block("marker-invalid", "distribution retry marker plan binding is invalid")
    stage_ownership: list[DistributionStageOwnership] = []
    raw_stage_ownership = raw.get("stage_ownership", [])
    if not isinstance(raw_stage_ownership, list):
        _admission_block("marker-invalid", "distribution retry marker stage ownership is invalid")
    for item in raw_stage_ownership:
        if not isinstance(item, dict) or set(item) != {
            "path",
            "stage_name",
            "device",
            "inode",
            "ctime_ns",
            "file_type",
        }:
            _admission_block("marker-invalid", "distribution retry marker stage ownership is invalid")
        stage_path = item.get("path")
        stage_name = item.get("stage_name")
        file_type = item.get("file_type")
        if (
            not isinstance(stage_path, str)
            or not stage_path
            or PurePosixPath(stage_path).is_absolute()
            or ".." in PurePosixPath(stage_path).parts
            or PurePosixPath(stage_path).as_posix() != stage_path
            or not isinstance(stage_name, str)
            or not stage_name
            or PurePosixPath(stage_name).name != stage_name
            or not isinstance(file_type, str)
            or file_type not in {"regular", "symlink"}
        ):
            _admission_block("marker-invalid", "distribution retry marker stage ownership is invalid")
        stage_device = item.get("device")
        stage_inode = item.get("inode")
        stage_ctime_ns = item.get("ctime_ns")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in (stage_device, stage_inode, stage_ctime_ns)
        ):
            _admission_block("marker-invalid", "distribution retry marker stage ownership is invalid")
        assert isinstance(stage_device, int)
        assert isinstance(stage_inode, int)
        assert isinstance(stage_ctime_ns, int)
        assert file_type in {"regular", "symlink"}
        stage_file_type: Literal["regular", "symlink"] = "regular" if file_type == "regular" else "symlink"
        stage_ownership.append(
            DistributionStageOwnership(
                path=stage_path,
                stage_name=stage_name,
                device=stage_device,
                inode=stage_inode,
                ctime_ns=stage_ctime_ns,
                file_type=stage_file_type,
            )
        )
    return DistributionRetryMarker(
        operation=operation,
        package_version=package_version,
        target_root=DistributionRootIdentity(device=device, inode=inode),
        last_completed_phase=phase,
        purpose=(_DISTRIBUTION_JOURNAL_GUARD_PURPOSE if supported_guard else _DISTRIBUTION_RETRY_PURPOSE),
        stage_ownership=tuple(stage_ownership),
        operation_id=operation_id,
        contract_identity=contract_identity,
        plan_digest=plan_digest,
        source_snapshot=_snapshot_from_stat(_DISTRIBUTION_RETRY_MARKER_REL.as_posix(), source_info),
        source_sha256=hashlib.sha256(raw_bytes).hexdigest(),
    )


def _read_uninstall_retry_marker_for_admission(target_root: Path) -> bool:
    path = target_root / _UNINSTALL_RETRY_MARKER_REL
    if not _path_present_no_follow(path):
        return False
    raw_bytes = _read_no_follow_regular(path, label="uninstall retry marker")
    assert raw_bytes is not None
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _admission_block("marker-invalid", "uninstall retry marker is not valid UTF-8 JSON")
    if raw != _UNINSTALL_RETRY_MARKER_PAYLOAD:
        _admission_block("marker-invalid", "uninstall retry marker schema is invalid")
    return True


def _anchor_identity_matches(target_root: Path, anchor: dict[str, Any]) -> bool:
    path_text = anchor.get("path")
    if path_text not in _VERSION_ANCHOR_PATHS or anchor.get("kind") != "regular":
        return False
    expected_digest = anchor.get("sha256")
    if not isinstance(expected_digest, str):
        return False
    if not _assert_real_parent_chain(target_root, path_text, label=f"version anchor {path_text}"):
        return False
    actual = _read_no_follow_regular(target_root / path_text, label=f"version anchor {path_text}", allow_missing=True)
    if actual is None:
        return False
    return hashlib.sha256(actual).hexdigest() == expected_digest


def _recognized_version_entry(manifest: DistributionManifest, version: str) -> dict[str, Any]:
    matches = [item for item in manifest.recognized_workspace_versions if item.get("version") == version]
    if len(matches) != 1:
        _admission_block("unknown-version", f"workspace version {version!r} is not an exact recognized entry")
    entry = matches[0]
    anchors = entry.get("anchors")
    if not isinstance(anchors, tuple):
        _admission_block("anchor-mismatch", f"workspace version {version!r} has invalid anchors")
    by_path = {anchor.get("path"): anchor for anchor in anchors if isinstance(anchor, dict)}
    if set(_VERSION_ANCHOR_PATHS) - set(by_path):
        _admission_block("anchor-mismatch", f"workspace version {version!r} is missing required anchors")
    return entry


def _validate_workspace_version(
    target_root: Path,
    *,
    manifest: DistributionManifest,
    package_version: str,
) -> tuple[str, tuple[int, int, int], DistributionIdentity]:
    version_path = target_root / "spec-dock" / "spec-dock.version"
    raw_bytes = _read_no_follow_regular(version_path, label="spec-dock/spec-dock.version", allow_missing=True)
    if raw_bytes is None:
        _admission_block("missing-version", "spec-dock/spec-dock.version is missing")
    try:
        version_text = raw_bytes.decode("ascii")
    except UnicodeDecodeError:
        _admission_block("invalid-version", "spec-dock/spec-dock.version must be ASCII")
    target_tuple = _parse_canonical_version(version_text, source="spec-dock/spec-dock.version")
    try:
        version_info = os.lstat(version_path)
    except OSError:
        _admission_block("invalid-file", "spec-dock/spec-dock.version changed during admission")
    if not stat.S_ISREG(version_info.st_mode) or version_info.st_nlink != 1:
        _admission_block("invalid-file", "spec-dock/spec-dock.version changed during admission")
    version_identity = DistributionIdentity(
        kind="regular",
        sha256=hashlib.sha256(raw_bytes).hexdigest(),
        mode=stat.S_IMODE(version_info.st_mode),
    )
    entry = _recognized_version_entry(manifest, version_text[:-1])
    anchors = entry["anchors"]
    for path_text in _VERSION_ANCHOR_PATHS:
        anchor = next((item for item in anchors if item.get("path") == path_text), None)
        if anchor is None or not _anchor_identity_matches(target_root, anchor):
            _admission_block("anchor-mismatch", f"version anchor does not match: {path_text}")
    package_tuple = _parse_package_version(package_version, source="executing package version")
    if target_tuple > package_tuple:
        _admission_block(
            "downgrade-blocked", f"target version {version_text[:-1]} is newer than package {package_version}"
        )
    return version_text[:-1], target_tuple, version_identity


def admit_distribution_operation(
    target_root: Path,
    *,
    operation: DistributionOperation,
    package_version: str,
    manifest_path: Path,
) -> DistributionAdmission:
    """Admit an installer operation without mutating the consumer tree.

    This is intentionally separate from distribution planning and apply.  It
    validates the package version, workspace marker, version-specific anchors,
    and operation-specific retry markers before any caller performs a write.
    """

    if operation not in _OPERATIONS:
        _admission_block("operation-invalid", f"unsupported operation: {operation!r}")
    _parse_package_version(package_version, source="executing package version")
    target_root = Path(target_root)
    root_identity = _root_identity_for_admission(target_root)
    try:
        manifest = _load_manifest(Path(manifest_path))
    except DistributionManifestError as exc:
        _admission_block("manifest-invalid", str(exc))

    specdock_path = target_root / "spec-dock"
    try:
        specdock_info = os.lstat(specdock_path)
    except FileNotFoundError:
        specdock_info = None
    except OSError:
        _admission_block("workspace-invalid", "managed workspace cannot be inspected safely")
    if (
        specdock_info is not None
        and not stat.S_ISLNK(specdock_info.st_mode)
        and not stat.S_ISDIR(specdock_info.st_mode)
    ):
        _admission_block("workspace-invalid", "spec-dock must be a real directory")
    if specdock_info is not None and stat.S_ISLNK(specdock_info.st_mode):
        _admission_block("workspace-invalid", "spec-dock is a symlink; a real directory is required")

    distribution_marker_present = _path_present_no_follow(target_root / _DISTRIBUTION_RETRY_MARKER_REL)
    journal_present = _path_present_no_follow(target_root / _DISTRIBUTION_JOURNAL_REL)
    uninstall_marker_present = _path_present_no_follow(target_root / _UNINSTALL_RETRY_MARKER_REL)
    if uninstall_marker_present and (distribution_marker_present or journal_present):
        _admission_block("dual-marker", "distribution recovery states cannot coexist")

    if journal_present:
        if operation not in {"update", "init-force"}:
            _admission_block("distribution-retry-present", "recover distribution before this operation")
        distribution_marker = _read_distribution_retry_marker(target_root)
        if distribution_marker is None or (
            distribution_marker.purpose != _DISTRIBUTION_JOURNAL_GUARD_PURPOSE
            or distribution_marker.source_snapshot is None
            or distribution_marker.source_sha256 is None
            or distribution_marker.operation != operation
            or distribution_marker.target_root != root_identity
            or distribution_marker.last_completed_phase != "preflight-complete"
            or distribution_marker.stage_ownership
            or not _journal_package_is_compatible(distribution_marker.package_version, package_version)
        ):
            _admission_block("dual-marker", "distribution recovery states cannot coexist")
        return DistributionAdmission(
            operation=operation,
            status="retry",
            package_version=package_version,
            marker=distribution_marker,
        )

    distribution_marker = _read_distribution_retry_marker(target_root)
    uninstall_marker = _read_uninstall_retry_marker_for_admission(target_root)
    if distribution_marker is not None:
        if operation == "uninstall":
            _admission_block("distribution-retry-present", "recover distribution before uninstall")
        if distribution_marker.operation != operation:
            _admission_block("marker-operation-mismatch", "retry marker belongs to another operation")
        if not _journal_package_is_compatible(distribution_marker.package_version, package_version):
            _admission_block("marker-package-mismatch", "retry marker belongs to another package version")
        if distribution_marker.target_root != root_identity:
            _admission_block("cross-root-replay", "retry marker belongs to another repository root")
        return DistributionAdmission(
            operation=operation,
            status="retry",
            package_version=package_version,
            marker=distribution_marker,
        )
    if uninstall_marker:
        if operation != "uninstall":
            _admission_block("uninstall-retry-present", "recover uninstall before init or update")
        return DistributionAdmission(
            operation=operation,
            status="uninstall-retry",
            package_version=package_version,
        )

    # A successful uninstall may intentionally leave an empty workspace
    # boundary after the retry marker is finalized.  Treat that exact empty
    # directory as a fresh admission so the documented `init` recovery path
    # can recreate the managed scaffold without requiring `--force`.
    if specdock_info is not None:
        try:
            empty_workspace_boundary = not any(specdock_path.iterdir())
        except OSError:
            _admission_block("workspace-invalid", "managed workspace cannot be inspected safely")
        if empty_workspace_boundary and operation in {"fresh", "init-force"}:
            return DistributionAdmission(operation=operation, status="fresh", package_version=package_version)
        if operation in {"fresh", "init-force"} and _is_preserved_specs_workspace(target_root):
            return DistributionAdmission(operation=operation, status="fresh", package_version=package_version)

    if specdock_info is None:
        if operation in {"fresh", "init-force"}:
            return DistributionAdmission(operation=operation, status="fresh", package_version=package_version)
        if operation == "update":
            _admission_block(
                "workspace-missing",
                "'spec-dock' not found. Run 'spec-dock init' first.",
            )
        _admission_block("workspace-missing", "target is not a managed SpecDock repo")
    if operation == "fresh":
        return DistributionAdmission(operation=operation, status="existing", package_version=package_version)
    target_version, _target_tuple, version_identity = _validate_workspace_version(
        target_root,
        manifest=manifest,
        package_version=package_version,
    )
    return DistributionAdmission(
        operation=operation,
        status="recognized",
        package_version=package_version,
        target_version=target_version,
        version_identity=version_identity,
    )


def _current_assets(install_root: Path) -> tuple[DistributionAsset, ...]:
    if not install_root.is_dir() or install_root.is_symlink():
        raise DistributionManifestError("physical install-root must be a directory")
    assets: list[DistributionAsset] = []
    for candidate in sorted(install_root.rglob("*"), key=lambda item: item.relative_to(install_root).as_posix()):
        if not candidate.is_file() or candidate.is_symlink():
            continue
        relative_candidate = candidate.relative_to(install_root)
        if "__pycache__" in relative_candidate.parts or relative_candidate.suffix in {".pyc", ".pyo"}:
            continue
        relative = _exact_relative_path(relative_candidate.as_posix(), field_name="Current path")
        try:
            content, source_snapshot = _source_asset_bytes(candidate)
            digest = hashlib.sha256(content).hexdigest()
        except (OSError, DistributionApplyError) as exc:
            raise DistributionManifestError(f"unable to read Current asset: {relative.as_posix()}") from exc
        assets.append(
            DistributionAsset(
                path=relative.as_posix(),
                identity=DistributionIdentity(
                    kind="regular",
                    sha256=digest,
                    mode=source_snapshot.mode,
                ),
                source_snapshot=source_snapshot,
            )
        )
    return tuple(assets)


def _scaffold_assets(scaffold_root: Path, *, operation: DistributionOperation) -> tuple[DistributionAsset, ...]:
    """Build the managed scaffold portion of the shared distribution catalog."""

    def is_pruned_by_scaffold_refresh(relative: Path) -> bool:
        parts = relative.parts
        if parts[0] == "scripts" and parts[-1].startswith("spec-dock-close") and parts[-1].endswith(".sh"):
            return True
        if parts[0] != "templates":
            return False
        if len(parts) == 2 and parts[1] in {"requirement.md", "design.md", "plan.md", "report.md"}:
            return True
        if len(parts) >= 2 and parts[1] in {"current", "completed"}:
            return True
        if (
            len(parts) >= 3
            and parts[1] in {"initiative", "epic", "issue"}
            and (parts[2] == "deps.json" or parts[2] in {"adrs", "artifacts", "current", "completed"})
        ):
            return True
        preserved_readmes = {
            PurePosixPath("templates/README.md"),
            PurePosixPath("templates/root/.workbench/README.md"),
            PurePosixPath("templates/initiative/.workbench/README.md"),
            PurePosixPath("templates/epic/.workbench/README.md"),
            PurePosixPath("templates/issue/.workbench/README.md"),
        }
        return parts[-1] == "README.md" and relative not in preserved_readmes

    if not scaffold_root.is_dir() or scaffold_root.is_symlink():
        raise DistributionManifestError("Missing asset directory: spec_dock")
    if not (scaffold_root / ".gitignore").is_file() or (scaffold_root / ".gitignore").is_symlink():
        raise DistributionManifestError("Missing asset file: spec_dock/.gitignore")
    source_entries: list[tuple[str, Path]] = [(".gitignore", scaffold_root / ".gitignore")]
    for root_name in _SCAFFOLD_MANAGED_ROOTS:
        source_root = scaffold_root / root_name
        if not source_root.is_dir() or source_root.is_symlink():
            raise DistributionManifestError(f"Invalid asset directory: spec_dock/{root_name}")
        for candidate in sorted(source_root.rglob("*"), key=lambda item: item.relative_to(scaffold_root).as_posix()):
            relative = candidate.relative_to(scaffold_root)
            if "__pycache__" in relative.parts or relative.suffix in {".pyc", ".pyo"}:
                continue
            if is_pruned_by_scaffold_refresh(relative):
                continue
            if candidate.is_file() and not candidate.is_symlink():
                source_entries.append((relative.as_posix(), candidate))
    runtime_script = scaffold_root / "scripts" / "spec-dock"
    try:
        runtime_info = os.lstat(runtime_script)
    except OSError as exc:
        raise DistributionManifestError("Missing asset file: spec_dock/scripts/spec-dock") from exc
    if (
        stat.S_ISLNK(runtime_info.st_mode)
        or not stat.S_ISREG(runtime_info.st_mode)
        or runtime_info.st_nlink != 1
        or stat.S_IMODE(runtime_info.st_mode) & 0o111 == 0
    ):
        raise DistributionManifestError("Invalid asset file: spec_dock/scripts/spec-dock")
    seed_readme = scaffold_root / "templates" / "root" / ".workbench" / "README.md"
    if not seed_readme.is_file() or seed_readme.is_symlink():
        raise DistributionManifestError("Missing asset file: spec_dock/templates/root/.workbench/README.md")
    if operation == "fresh" and seed_readme.is_file() and not seed_readme.is_symlink():
        source_entries.append((".workbench/README.md", seed_readme))

    assets: list[DistributionAsset] = []
    for source_path, candidate in sorted(source_entries):
        try:
            content, source_snapshot = _source_asset_bytes(candidate)
            digest = hashlib.sha256(content).hexdigest()
        except (OSError, DistributionApplyError) as exc:
            raise DistributionManifestError(f"unable to read scaffold asset: {source_path}") from exc
        mode = source_snapshot.mode
        if source_path == "scripts/spec-dock":
            mode |= 0o111
        if source_path.startswith("system/active-none/"):
            mode &= ~0o222
        target_path = f"spec-dock/{source_path}"
        assets.append(
            DistributionAsset(
                path=target_path,
                source_path=source_path,
                identity=DistributionIdentity(
                    kind="regular",
                    sha256=digest,
                    mode=mode,
                ),
                source_snapshot=source_snapshot,
            )
        )
    return tuple(assets)


_OPERATIONS = frozenset({"fresh", "update", "init-force", "uninstall"})
_CURRENT_SHORTCUTS = {
    "spec": DistributionIdentity(kind="symlink", target="spec-dock/scripts/spec-dock"),
}


@dataclass(frozen=True)
class _TargetObservation:
    state: str
    identity: DistributionIdentity | None = None
    link_count: int | None = None
    snapshot: DistributionTargetSnapshot | None = None


def _identity_matches(
    actual: DistributionIdentity,
    record: dict[str, Any],
    *,
    include_mode: bool = True,
) -> bool:
    if actual.kind != record.get("kind"):
        return False
    if actual.kind == "regular":
        if actual.sha256 != record.get("sha256"):
            return False
        expected_mode = record.get("mode")
        return not include_mode or expected_mode is None or actual.mode == expected_mode
    return actual.target == record.get("target")


def _normalized_link_target(value: str) -> str | None:
    if not value or "\\" in value or value.startswith("/") or _DRIVE_RE.match(value):
        return None
    try:
        return _exact_relative_path(value, field_name="target link").as_posix()
    except DistributionManifestError:
        return None


def _generated_link_target_is_within_root(path: str, target: str) -> bool:
    if not target or "\\" in target or target.startswith("/") or _DRIVE_RE.match(target):
        return False
    parts: list[str] = list(PurePosixPath(path).parent.parts)
    for component in PurePosixPath(target).parts:
        if component in {"", "."}:
            continue
        if component == "..":
            if not parts:
                return False
            parts.pop()
            continue
        parts.append(component)
    return bool(parts)


def _normalized_link_target_for_path(path: str, target: str) -> str | None:
    normalized = _normalized_link_target(target)
    if normalized is not None:
        return normalized
    return target if _generated_link_target_is_within_root(path, target) else None


def _file_type(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    return "special"


def _missing_snapshot(relative_path: str) -> PathIdentitySnapshot:
    return PathIdentitySnapshot(relative_path=relative_path, exists=False)


def _snapshot_from_stat(
    relative_path: str,
    info: os.stat_result,
    *,
    identity: DistributionIdentity | None = None,
) -> PathIdentitySnapshot:
    return PathIdentitySnapshot(
        relative_path=relative_path,
        exists=True,
        device=info.st_dev,
        inode=info.st_ino,
        ctime_ns=info.st_ctime_ns,
        file_type=_file_type(info.st_mode),
        link_count=info.st_nlink,
        identity=identity,
    )


def _target_snapshot(
    root: PathIdentitySnapshot,
    parents: list[PathIdentitySnapshot],
    target: PathIdentitySnapshot,
) -> DistributionTargetSnapshot:
    return DistributionTargetSnapshot(root=root, parents=tuple(parents), target=target)


def _same_observed_node(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and before.st_ctime_ns == after.st_ctime_ns
        and stat.S_IFMT(before.st_mode) == stat.S_IFMT(after.st_mode)
    )


def _digest_open_file(fd: int) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            return digest.hexdigest()
        digest.update(chunk)


def _observe_target(target_root: Path, relative_path: str) -> _TargetObservation:
    """Inspect one target through held directory descriptors without following links."""

    try:
        root_stat = os.lstat(target_root)
    except FileNotFoundError:
        return _TargetObservation(
            "missing",
            snapshot=_target_snapshot(
                _missing_snapshot("."),
                [],
                _missing_snapshot(relative_path),
            ),
        )
    except OSError:
        return _TargetObservation("root-error")
    root_snapshot = _snapshot_from_stat(".", root_stat)
    if stat.S_ISLNK(root_stat.st_mode):
        return _TargetObservation(
            "root-symlink",
            snapshot=_target_snapshot(root_snapshot, [], _missing_snapshot(relative_path)),
        )
    if not stat.S_ISDIR(root_stat.st_mode):
        return _TargetObservation(
            "root-non-directory",
            snapshot=_target_snapshot(root_snapshot, [], _missing_snapshot(relative_path)),
        )

    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        parent_fd = os.open(target_root, directory_flags)
        opened_root = os.fstat(parent_fd)
    except OSError:
        return _TargetObservation(
            "root-error",
            snapshot=_target_snapshot(root_snapshot, [], _missing_snapshot(relative_path)),
        )
    if not _same_observed_node(root_stat, opened_root):
        os.close(parent_fd)
        return _TargetObservation(
            "root-error",
            snapshot=_target_snapshot(root_snapshot, [], _missing_snapshot(relative_path)),
        )

    parts = PurePosixPath(relative_path).parts
    parents: list[PathIdentitySnapshot] = []
    parent_parts: list[str] = []
    missing_parent = False
    try:
        for component in parts[:-1]:
            parent_parts.append(component)
            parent_relative = "/".join(parent_parts)
            if missing_parent:
                parents.append(_missing_snapshot(parent_relative))
                continue
            try:
                component_stat = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                parents.append(_missing_snapshot(parent_relative))
                missing_parent = True
                continue
            except OSError:
                return _TargetObservation(
                    "parent-error",
                    snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
                )
            component_snapshot = _snapshot_from_stat(parent_relative, component_stat)
            parents.append(component_snapshot)
            if stat.S_ISLNK(component_stat.st_mode):
                return _TargetObservation(
                    "symlink-container",
                    snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
                )
            if not stat.S_ISDIR(component_stat.st_mode):
                return _TargetObservation(
                    "non-directory-container",
                    snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
                )
            try:
                next_fd = os.open(component, directory_flags, dir_fd=parent_fd)
                opened_component = os.fstat(next_fd)
            except OSError:
                return _TargetObservation(
                    "parent-error",
                    snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
                )
            if not _same_observed_node(component_stat, opened_component):
                os.close(next_fd)
                return _TargetObservation(
                    "parent-error",
                    snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
                )
            os.close(parent_fd)
            parent_fd = next_fd

        if missing_parent:
            return _TargetObservation(
                "missing",
                snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
            )

        exact_name = parts[-1]
        try:
            exact_stat = os.stat(exact_name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return _TargetObservation(
                "missing",
                snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
            )
        except OSError:
            return _TargetObservation(
                "target-error",
                snapshot=_target_snapshot(root_snapshot, parents, _missing_snapshot(relative_path)),
            )

        if stat.S_ISLNK(exact_stat.st_mode):
            try:
                link_target = _normalized_link_target_for_path(
                    relative_path,
                    str(os.readlink(exact_name, dir_fd=parent_fd)),
                )
                after_link = os.stat(exact_name, dir_fd=parent_fd, follow_symlinks=False)
            except OSError:
                link_target = None
                after_link = exact_stat
            if not _same_observed_node(exact_stat, after_link):
                return _TargetObservation(
                    "target-error",
                    snapshot=_target_snapshot(root_snapshot, parents, _snapshot_from_stat(relative_path, exact_stat)),
                )
            identity = DistributionIdentity(kind="symlink", target=link_target)
            return _TargetObservation(
                "symlink",
                identity,
                exact_stat.st_nlink,
                _target_snapshot(
                    root_snapshot,
                    parents,
                    _snapshot_from_stat(relative_path, exact_stat, identity=identity),
                ),
            )
        if stat.S_ISREG(exact_stat.st_mode):
            file_fd: int | None = None
            try:
                file_fd = os.open(exact_name, file_flags, dir_fd=parent_fd)
                opened_file = os.fstat(file_fd)
                if not _same_observed_node(exact_stat, opened_file) or not stat.S_ISREG(opened_file.st_mode):
                    raise OSError(errno.ESTALE, "managed target identity changed")
                digest = _digest_open_file(file_fd)
                after_read = os.fstat(file_fd)
                if not _same_observed_node(opened_file, after_read):
                    raise OSError(errno.ESTALE, "managed target identity changed")
            except OSError:
                return _TargetObservation(
                    "target-error",
                    snapshot=_target_snapshot(root_snapshot, parents, _snapshot_from_stat(relative_path, exact_stat)),
                )
            finally:
                if file_fd is not None:
                    os.close(file_fd)
            identity = DistributionIdentity(
                kind="regular",
                sha256=digest,
                mode=stat.S_IMODE(opened_file.st_mode),
            )
            return _TargetObservation(
                "regular",
                identity,
                opened_file.st_nlink,
                _target_snapshot(
                    root_snapshot,
                    parents,
                    _snapshot_from_stat(relative_path, opened_file, identity=identity),
                ),
            )
        if stat.S_ISDIR(exact_stat.st_mode):
            return _TargetObservation(
                "directory",
                link_count=exact_stat.st_nlink,
                snapshot=_target_snapshot(root_snapshot, parents, _snapshot_from_stat(relative_path, exact_stat)),
            )
        return _TargetObservation(
            "special",
            link_count=exact_stat.st_nlink,
            snapshot=_target_snapshot(root_snapshot, parents, _snapshot_from_stat(relative_path, exact_stat)),
        )
    finally:
        os.close(parent_fd)


def _historical_records(manifest: DistributionManifest) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = list(manifest.historical_current_identities)
    for version in manifest.recognized_workspace_versions:
        records.extend(version["anchors"])
        version_bytes = f"{version['version']}\n".encode()
        records.append({
            "path": "spec-dock/spec-dock.version",
            "kind": "regular",
            "sha256": hashlib.sha256(version_bytes).hexdigest(),
        })
    for item in manifest.obsolete_exact_files:
        records.extend(item["identities"])
    records.extend(manifest.historical_shortcuts)
    return tuple(records)


def _trusted_manifest_matches(
    target_root: Path,
    path: str,
    actual: DistributionIdentity,
    manifest: DistributionManifest,
) -> bool:
    for trusted in manifest.trusted_consumer_manifests:
        manifest_observation = _observe_target(target_root, trusted["path"])
        manifest_identity = manifest_observation.identity
        if manifest_identity is None or not _identity_matches(manifest_identity, trusted, include_mode=False):
            continue
        for claim in trusted["claims"]:
            if claim["path"] == path and _identity_matches(actual, claim, include_mode=False):
                return True
    return False


def _historical_provenance(
    target_root: Path,
    path: str,
    actual: DistributionIdentity,
    manifest: DistributionManifest,
) -> str | None:
    for record in _historical_records(manifest):
        if record["path"] == path and _identity_matches(actual, record, include_mode=False):
            return "direct"
    if _trusted_manifest_matches(target_root, path, actual, manifest):
        return "trusted-manifest"
    return None


def _target_identity_specs(
    current_assets: tuple[DistributionAsset, ...],
    scaffold_assets: tuple[DistributionAsset, ...] = (),
) -> dict[str, DistributionIdentity]:
    # Historical shortcut records are evidence only.  They must never create
    # a new Fresh target; the shipped canonical shortcut is the sole Current
    # shortcut and is represented by the synthetic rule above.
    return {
        **_CURRENT_SHORTCUTS,
        **{asset.path: asset.identity for asset in current_assets},
        **{asset.path: asset.identity for asset in scaffold_assets},
    }


def _blocked_action(
    path: str,
    operation: DistributionOperation,
    reason: str,
    *,
    provenance: DistributionProvenance = "unknown",
    action: DistributionActionName = "block",
) -> DistributionAction:
    return DistributionAction(path, operation, action, provenance, reason, blocked=True)


def _classify_current_target(
    *,
    target_root: Path,
    path: str,
    expected: DistributionIdentity,
    operation: DistributionOperation,
    manifest: DistributionManifest,
    generated_path: bool = False,
    refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None,
    observation: _TargetObservation | None = None,
) -> DistributionAction:
    if observation is None:
        observation = _observe_target(target_root, path)
    if observation.state == "missing":
        if operation == "uninstall":
            return DistributionAction(path, operation, "prune", "missing", "already-absent")
        return DistributionAction(path, operation, "create", "missing", "target-missing")
    if observation.state == "directory":
        return _blocked_action(path, operation, "exact-path-directory")
    if observation.state == "symlink-container":
        return _blocked_action(path, operation, "symlink-container")
    if observation.state == "non-directory-container":
        return _blocked_action(path, operation, "non-directory-container")
    if observation.state in {
        "root-symlink",
        "root-non-directory",
        "root-error",
        "parent-error",
        "target-error",
        "special",
    }:
        return _blocked_action(path, operation, "unsafe-target-path")

    actual = observation.identity
    if actual is None:
        return _blocked_action(path, operation, "unsafe-target-path")
    generated_refresh_allowed = generated_path and (
        refreshable_existing_identities is None or actual in refreshable_existing_identities
    )
    if actual.kind != expected.kind:
        if (
            generated_refresh_allowed
            and operation in {"update", "init-force"}
            and {actual.kind, expected.kind} <= {"regular", "symlink"}
        ):
            if observation.link_count is not None and observation.link_count > 1:
                return _blocked_action(path, operation, "hard-link-mutation-unsafe", provenance="current")
            return DistributionAction(path, operation, "upgrade", "current", "generated-state-refresh")
        return _blocked_action(path, operation, "exact-path-symlink" if actual.kind == "symlink" else "exact-path-type")
    if actual.kind == "symlink" and actual.target != expected.target:
        if generated_refresh_allowed and operation in {"update", "init-force"}:
            if observation.link_count is not None and observation.link_count > 1:
                return _blocked_action(path, operation, "hard-link-mutation-unsafe", provenance="current")
            return DistributionAction(path, operation, "upgrade", "current", "generated-state-refresh")
        provenance = _historical_provenance(target_root, path, actual, manifest)
        if provenance is not None and operation in {"update", "init-force"}:
            if observation.link_count is not None and observation.link_count > 1:
                return _blocked_action(
                    path,
                    operation,
                    "hard-link-mutation-unsafe",
                    provenance="historical",
                )
            return DistributionAction(path, operation, "upgrade", "historical", "direct-historical-identity-match")
        if provenance is not None and operation == "uninstall":
            if observation.link_count is not None and observation.link_count > 1:
                return _blocked_action(
                    path,
                    operation,
                    "hard-link-mutation-unsafe",
                    provenance="historical",
                )
            return DistributionAction(path, operation, "prune", "historical", "historical-identity-match")
        if provenance is not None:
            return _blocked_action(
                path,
                operation,
                "historical-identity-fresh-preserve",
                provenance="historical",
                action="preserve",
            )
        return _blocked_action(path, operation, "unknown-current-collision", action="preserve")
    if actual.kind == "regular" and actual.sha256 != expected.sha256:
        if generated_refresh_allowed and operation in {"update", "init-force"}:
            if observation.link_count is not None and observation.link_count > 1:
                return _blocked_action(path, operation, "hard-link-mutation-unsafe", provenance="current")
            return DistributionAction(path, operation, "upgrade", "current", "generated-state-refresh")
        provenance = _historical_provenance(target_root, path, actual, manifest)
        if provenance is None:
            return _blocked_action(path, operation, "unknown-current-collision", action="preserve")
        if observation.link_count is not None and observation.link_count > 1:
            return _blocked_action(
                path,
                operation,
                "hard-link-mutation-unsafe",
                provenance="historical",
            )
        if operation == "uninstall":
            return DistributionAction(path, operation, "prune", "historical", "historical-identity-match")
        if operation in {"update", "init-force"}:
            reason = (
                "trusted-manifest-identity-match"
                if provenance == "trusted-manifest"
                else "direct-historical-identity-match"
            )
            return DistributionAction(path, operation, "upgrade", "historical", reason)
        return _blocked_action(
            path,
            operation,
            "historical-identity-fresh-preserve",
            provenance="historical",
            action="preserve",
        )

    if (
        actual.kind == "regular"
        and actual.sha256 == expected.sha256
        and expected.mode is not None
        and actual.mode != expected.mode
    ):
        if operation in {"fresh", "uninstall"}:
            return _blocked_action(
                path,
                operation,
                "current-mode-mismatch",
                provenance="current",
                action="preserve",
            )
        if operation in {"update", "init-force"} and observation.link_count is not None and observation.link_count > 1:
            return _blocked_action(
                path,
                operation,
                "hard-link-mutation-unsafe",
                provenance="current",
            )
        if operation in {"update", "init-force"}:
            return DistributionAction(path, operation, "upgrade", "current", "current-mode-mismatch")

    if (
        actual.kind == "symlink"
        and observation.link_count is not None
        and observation.link_count > 1
        and operation == "uninstall"
    ):
        return _blocked_action(
            path,
            operation,
            "hard-link-mutation-unsafe",
            provenance="current",
        )

    if (
        actual.kind == "regular"
        and observation.link_count is not None
        and observation.link_count > 1
        and operation in {"update", "init-force", "uninstall"}
    ):
        return _blocked_action(
            path,
            operation,
            "hard-link-mutation-unsafe",
            provenance="current",
        )

    if operation == "uninstall":
        return DistributionAction(path, operation, "prune", "current", "current-identity-match")
    return DistributionAction(path, operation, "adopt", "current", "current-identity-match")


def _classify_obsolete_target(
    *,
    target_root: Path,
    item: dict[str, Any],
    operation: DistributionOperation,
    manifest: DistributionManifest,
    observation: _TargetObservation | None = None,
) -> DistributionAction | None:
    path = item["path"]
    if observation is None:
        observation = _observe_target(target_root, path)
    if observation.state == "missing":
        return None
    if observation.state == "directory":
        return _blocked_action(path, operation, "exact-path-directory")
    if observation.state == "symlink-container":
        return _blocked_action(path, operation, "symlink-container")
    if observation.state != "regular" and observation.state != "symlink":
        return _blocked_action(path, operation, "unsafe-target-path")
    actual = observation.identity
    if actual is None:
        return _blocked_action(path, operation, "unsafe-target-path")
    direct = any(_identity_matches(actual, identity, include_mode=False) for identity in item["identities"])
    trusted = _trusted_manifest_matches(target_root, path, actual, manifest)
    if not direct and not trusted:
        return _blocked_action(path, operation, "obsolete-identity-unknown", action="preserve")
    if actual.kind == "regular" and observation.link_count is not None and observation.link_count > 1:
        return _blocked_action(path, operation, "hard-link-mutation-unsafe", provenance="historical")
    if actual.kind == "symlink" and observation.link_count is not None and observation.link_count > 1:
        return _blocked_action(path, operation, "hard-link-mutation-unsafe", provenance="historical")
    reason = "trusted-manifest-identity-match" if trusted and not direct else "direct-obsolete-identity-match"
    return DistributionAction(path, operation, "prune", "historical", reason)


def _classify_target(
    *,
    target_root: Path,
    current_assets: tuple[DistributionAsset, ...],
    operation: DistributionOperation,
    manifest: DistributionManifest,
    scaffold_assets: tuple[DistributionAsset, ...] = (),
) -> tuple[tuple[DistributionAction, ...], tuple[tuple[str, DistributionTargetSnapshot], ...]]:
    specs = _target_identity_specs(current_assets, scaffold_assets)
    generated_assets = {asset.path: asset for asset in scaffold_assets if asset.source_path is None}
    actions: list[DistributionAction] = []
    observations: dict[str, _TargetObservation] = {}
    for path, expected in sorted(specs.items()):
        observation = _observe_target(target_root, path)
        observations[path] = observation
        actions.append(
            _classify_current_target(
                target_root=target_root,
                path=path,
                expected=expected,
                operation=operation,
                manifest=manifest,
                generated_path=path in generated_assets,
                refreshable_existing_identities=(
                    generated_assets[path].refreshable_existing_identities if path in generated_assets else None
                ),
                observation=observation,
            )
        )
    if operation in {"update", "init-force", "uninstall"}:
        current_paths = set(specs)
        for item in manifest.obsolete_exact_files:
            if item["path"] in current_paths:
                continue
            observation = _observe_target(target_root, item["path"])
            observations[item["path"]] = observation
            action = _classify_obsolete_target(
                target_root=target_root,
                item=item,
                operation=operation,
                manifest=manifest,
                observation=observation,
            )
            if action is not None:
                actions.append(action)
    snapshots: list[tuple[str, DistributionTargetSnapshot]] = []
    for path in sorted(observations):
        snapshot = observations[path].snapshot
        if snapshot is not None:
            snapshots.append((path, snapshot))
    return tuple(actions), tuple(snapshots)


def build_distribution_plan(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path | None = None,
    target_root: Path | None = None,
    operation: DistributionOperation = "fresh",
    generated_assets: tuple[DistributionAsset, ...] = (),
) -> DistributionPlan:
    """Build a read-only Current/historical distribution plan.

    ``install_root`` is the provider physical source.  It is never modified;
    ``scaffold_root`` is retained only as context for later steps.  When
    ``target_root`` is supplied, S25 classifies exact consumer paths without
    writing them.  The target tree is never used as a source catalog.
    """

    install_root = Path(install_root)
    manifest_path = Path(manifest_path)
    if operation not in _OPERATIONS:
        raise DistributionManifestError(f"unsupported distribution operation: {operation!r}")
    current_assets = _current_assets(install_root)
    scaffold_assets = (
        _scaffold_assets(Path(scaffold_root), operation=operation)
        if scaffold_root is not None and operation != "uninstall"
        else ()
    )
    normalized_generated_assets: list[DistributionAsset] = []
    occupied_paths = {asset.path for asset in (*current_assets, *scaffold_assets)} | set(_CURRENT_SHORTCUTS)
    for asset in generated_assets:
        try:
            normalized_path = _exact_relative_path(asset.path, field_name="generated asset path").as_posix()
        except DistributionManifestError as exc:
            raise DistributionPlanError("generated asset path is not repository-relative") from exc
        if normalized_path != asset.path or normalized_path in occupied_paths:
            raise DistributionPlanError("generated asset path is duplicated or not canonical")
        if asset.source_path is not None or asset.source_snapshot is not None:
            raise DistributionPlanError("generated asset cannot reference a provider source path")
        if asset.identity.kind == "regular":
            if (
                asset.generated_content is None
                or asset.identity.sha256 != hashlib.sha256(asset.generated_content).hexdigest()
            ):
                raise DistributionPlanError("generated regular asset identity does not match its content")
        elif asset.identity.kind == "symlink":
            if asset.generated_content is not None or not _generated_link_target_is_within_root(
                normalized_path, asset.identity.target or ""
            ):
                raise DistributionPlanError("generated symlink asset has an invalid target")
        else:
            raise DistributionPlanError("generated asset kind is unsupported")
        occupied_paths.add(normalized_path)
        normalized_generated_assets.append(asset)
    scaffold_assets = (*scaffold_assets, *normalized_generated_assets)
    manifest = _load_manifest(manifest_path)
    _assert_no_manifest_overlap(
        {asset.path for asset in current_assets} | set(_CURRENT_SHORTCUTS),
        manifest,
        protected_paths=_protected_workspace_paths(scaffold_assets),
    )
    actions: tuple[DistributionAction, ...] = ()
    target_snapshots: tuple[tuple[str, DistributionTargetSnapshot], ...] = ()
    if target_root is not None:
        actions, target_snapshots = _classify_target(
            target_root=Path(target_root),
            current_assets=current_assets,
            operation=operation,
            manifest=manifest,
            scaffold_assets=scaffold_assets,
        )
    return DistributionPlan(
        current_assets=current_assets,
        actions=actions,
        manifest=manifest,
        scaffold_root=Path(scaffold_root) if scaffold_root is not None else None,
        install_root=install_root,
        manifest_path=manifest_path,
        target_root=Path(target_root) if target_root is not None else None,
        operation=operation,
        target_snapshots=target_snapshots,
        scaffold_assets=scaffold_assets,
    )


def _distribution_identity_payload(identity: DistributionIdentity | None) -> dict[str, object] | None:
    if identity is None:
        return None
    return {
        "kind": identity.kind,
        "sha256": identity.sha256,
        "mode": identity.mode,
        "target": identity.target,
    }


def _contract_identity(plan: DistributionPlan) -> str:
    assets = sorted((*plan.current_assets, *plan.scaffold_assets), key=lambda asset: asset.path)
    payload = {
        "schema_version": plan.manifest.schema_version,
        "assets": [
            {
                "path": asset.path,
                "identity": _distribution_identity_payload(asset.identity),
            }
            for asset in assets
        ],
        "recognized_workspace_versions": plan.manifest.recognized_workspace_versions,
        "historical_current_identities": plan.manifest.historical_current_identities,
        "trusted_consumer_manifests": plan.manifest.trusted_consumer_manifests,
        "obsolete_exact_files": plan.manifest.obsolete_exact_files,
        "historical_shortcuts": plan.manifest.historical_shortcuts,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _root_identity_for_assessment(target_root: Path) -> DistributionRootIdentity:
    try:
        info = os.lstat(target_root)
    except OSError as exc:
        raise DistributionPlanError("recognized target root cannot be inspected safely") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise DistributionPlanError("recognized target root is not a real directory")
    return DistributionRootIdentity(device=info.st_dev, inode=info.st_ino)


def build_workspace_assessment(
    install_root: Path,
    *,
    manifest_path: Path,
    target_root: Path,
    intent: RecognizedDistributionIntent,
    scaffold_root: Path | None = None,
    generated_assets: tuple[DistributionAsset, ...] = (),
) -> WorkspaceAssessment:
    """Assess one recognized operation without creating execution authority."""

    if intent not in {"update", "init-force"}:
        raise DistributionPlanError(f"unsupported recognized intent: {intent!r}")
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        operation=intent,
        generated_assets=generated_assets,
    )
    blockers = tuple(action for action in plan.actions if action.blocked)
    return WorkspaceAssessment(
        intent=intent,
        root_identity=_root_identity_for_assessment(target_root),
        contract_identity=_contract_identity(plan),
        distribution_plan=plan,
        actions=plan.actions,
        blockers=blockers,
    )


def _action_precondition_payload(plan: DistributionPlan, action: DistributionAction) -> dict[str, object]:
    snapshots = dict(plan.target_snapshots)
    snapshot = snapshots.get(action.path)
    if snapshot is None:
        raise DistributionPlanError(f"assessment is missing a precondition for '{action.path}'")
    target = snapshot.target
    return {
        "root": _path_snapshot_condition(snapshot.root),
        "parents": [_path_snapshot_condition(parent) for parent in snapshot.parents],
        "exists": target.exists,
        "device": target.device,
        "inode": target.inode,
        "ctime_ns": target.ctime_ns,
        "file_type": target.file_type,
        "link_count": target.link_count,
        "identity": _distribution_identity_payload(target.identity),
    }


def _action_postcondition_payload(plan: DistributionPlan, action: DistributionAction) -> dict[str, object]:
    snapshot = dict(plan.target_snapshots).get(action.path)
    if snapshot is None:
        raise DistributionPlanError(f"assessment is missing a postcondition for '{action.path}'")
    boundary = {
        "root": _path_snapshot_condition(snapshot.root),
        "parents": [_path_snapshot_condition(parent) for parent in snapshot.parents],
    }
    expected = _expected_target_identity(plan, action.path)
    if action.action == "prune":
        return {**boundary, "exists": False, "identity": None}
    if expected is None:
        expected = snapshot.target.identity
    expected_type = expected.kind if expected is not None else snapshot.target.file_type
    return {
        **boundary,
        "exists": True,
        "file_type": expected_type,
        "link_count": 1,
        "identity": _distribution_identity_payload(expected),
    }


def _path_snapshot_condition(snapshot: PathIdentitySnapshot) -> dict[str, object]:
    return {
        "relative_path": snapshot.relative_path,
        "exists": snapshot.exists,
        "device": snapshot.device,
        "inode": snapshot.inode,
        "ctime_ns": snapshot.ctime_ns,
        "file_type": snapshot.file_type,
        "link_count": snapshot.link_count,
    }


def _plan_digest_condition(condition: dict[str, object]) -> dict[str, object]:
    """Exclude directory ctime noise that recovery metadata itself changes."""

    normalized = dict(condition)
    root = normalized.get("root")
    if isinstance(root, dict):
        normalized["root"] = {key: value for key, value in root.items() if key != "ctime_ns"}
    parents = normalized.get("parents")
    if isinstance(parents, list):
        normalized["parents"] = [
            {key: value for key, value in parent.items() if key != "ctime_ns"} if isinstance(parent, dict) else parent
            for parent in parents
        ]
    return normalized


def _mutation_plan_digest(assessment: WorkspaceAssessment) -> str:
    plan = assessment.distribution_plan
    ordered_actions = sorted(assessment.actions, key=lambda action: (action.path, action.action, action.reason))
    payload = {
        "schema_version": 1,
        "intent": assessment.intent,
        "root_binding": {
            "device": assessment.root_identity.device,
            "inode": assessment.root_identity.inode,
        },
        "contract_identity": assessment.contract_identity,
        "actions": [
            {
                "path": action.path,
                "action": action.action,
                "provenance": action.provenance,
                "reason": action.reason,
                "precondition": _plan_digest_condition(_action_precondition_payload(plan, action)),
                "postcondition": _plan_digest_condition(_action_postcondition_payload(plan, action)),
            }
            for action in ordered_actions
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_executable_mutation_plan(assessment: WorkspaceAssessment) -> ExecutableMutationPlan:
    """Issue mutation authority only for a complete blocker-free assessment."""

    plan = assessment.distribution_plan
    if plan.operation != assessment.intent:
        raise DistributionPlanError("workspace assessment intent does not match its distribution plan")
    if assessment.contract_identity != _contract_identity(plan):
        raise DistributionPlanError("workspace assessment contract identity does not match its distribution plan")
    if assessment.actions != plan.actions:
        raise DistributionPlanError("workspace assessment actions do not match its distribution plan")
    expected_blockers = tuple(action for action in plan.actions if action.blocked)
    if assessment.blockers != expected_blockers:
        raise DistributionPlanError("workspace assessment blockers do not match its distribution plan")
    if assessment.blockers:
        raise DistributionPlanError("workspace assessment contains blocker dispositions")
    if not assessment.actions:
        raise DistributionPlanError("workspace assessment contains no managed actions")
    actions_by_path = {action.path: action for action in assessment.actions}
    snapshots = dict(plan.target_snapshots)
    if len(actions_by_path) != len(assessment.actions) or len(snapshots) != len(plan.target_snapshots):
        raise DistributionPlanError("workspace assessment contains duplicate managed paths")
    if not set(actions_by_path).issubset(snapshots):
        raise DistributionPlanError("workspace assessment is missing snapshots for managed actions")
    current_specs = _target_identity_specs(plan.current_assets, plan.scaffold_assets)
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files} - set(current_specs)
    for action in assessment.actions:
        try:
            _exact_relative_path(action.path, field_name="workspace assessment action path")
        except DistributionManifestError as exc:
            raise DistributionPlanError("workspace assessment contains an unsafe managed path") from exc
        if action.operation != assessment.intent:
            raise DistributionPlanError("workspace assessment action intent mismatch")
        if action.action == "prune":
            if action.path not in obsolete_paths:
                raise DistributionPlanError("workspace assessment prune is outside obsolete authority")
        elif action.path not in current_specs:
            raise DistributionPlanError("workspace assessment action is outside current authority")
        snapshot = snapshots[action.path]
        if (
            not snapshot.root.exists
            or snapshot.root.file_type != "directory"
            or (snapshot.root.device, snapshot.root.inode)
            != (assessment.root_identity.device, assessment.root_identity.inode)
        ):
            raise DistributionPlanError("workspace assessment root snapshot does not match its root binding")
        _action_precondition_payload(plan, action)
        _action_postcondition_payload(plan, action)
    return ExecutableMutationPlan(
        intent=assessment.intent,
        root_identity=assessment.root_identity,
        contract_identity=assessment.contract_identity,
        plan_digest=_mutation_plan_digest(assessment),
        distribution_plan=assessment.distribution_plan,
        actions=assessment.actions,
    )


def _staging_leases_payload(journal: OperationJournal) -> list[dict[str, object]]:
    return [
        {
            "path": lease.path,
            "stage_name": lease.stage_name,
            "device": lease.device,
            "inode": lease.inode,
            "ctime_ns": lease.ctime_ns,
            "file_type": lease.file_type,
        }
        for lease in journal.staging_leases
    ]


def _staging_leases_digest(
    *,
    operation_id: str,
    leases: list[dict[str, object]],
) -> str:
    payload = {
        "operation_id": operation_id,
        "staging_leases": leases,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _created_parent_bindings_payload(journal: OperationJournal) -> list[dict[str, object]]:
    return [_path_snapshot_condition(binding) for binding in journal.created_parent_bindings]


def _created_parent_bindings_digest(
    *,
    operation_id: str,
    bindings: list[dict[str, object]],
) -> str:
    encoded = json.dumps(
        {"operation_id": operation_id, "created_parent_bindings": bindings},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _journal_payload(journal: OperationJournal) -> dict[str, object]:
    leases = _staging_leases_payload(journal)
    created_parent_bindings = _created_parent_bindings_payload(journal)
    return {
        "schema_version": journal.schema_version,
        "protocol_version": journal.protocol_version,
        "operation_id": journal.operation_id,
        "root_binding": {
            "device": journal.root_identity.device,
            "inode": journal.root_identity.inode,
        },
        "workspace_binding": _path_snapshot_condition(journal.workspace_identity),
        "intent": journal.intent,
        "authority": journal.authority,
        "package_version": journal.package_version,
        "contract_identity": journal.contract_identity,
        "plan_digest": journal.plan_digest,
        "created_at_ns": journal.created_at_ns,
        "status": journal.status,
        "actions": [
            {
                "path": action.path,
                "action": action.action,
                "provenance": action.provenance,
                "reason": action.reason,
                "precondition": action.precondition,
                "postcondition": action.postcondition,
                "checkpoint": action.checkpoint,
            }
            for action in journal.actions
        ],
        "staging_leases": leases,
        "staging_leases_digest": _staging_leases_digest(
            operation_id=journal.operation_id,
            leases=leases,
        ),
        "created_parent_bindings": created_parent_bindings,
        "created_parent_bindings_digest": _created_parent_bindings_digest(
            operation_id=journal.operation_id,
            bindings=created_parent_bindings,
        ),
    }


def _journal_bytes(journal: OperationJournal) -> bytes:
    return (json.dumps(_journal_payload(journal), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _parse_operation_journal(raw: bytes) -> OperationJournal:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DistributionApplyError("journal-protocol-incompatible") from exc
    if not isinstance(payload, dict):
        raise DistributionApplyError("journal-protocol-incompatible")
    expected_fields = {
        "schema_version",
        "protocol_version",
        "operation_id",
        "root_binding",
        "workspace_binding",
        "intent",
        "authority",
        "package_version",
        "contract_identity",
        "plan_digest",
        "created_at_ns",
        "status",
        "actions",
        "staging_leases",
        "staging_leases_digest",
        "created_parent_bindings",
        "created_parent_bindings_digest",
    }
    if set(payload) != expected_fields:
        raise DistributionApplyError("journal-protocol-incompatible")
    root = payload["root_binding"]
    workspace = payload["workspace_binding"]
    actions = payload["actions"]
    if (
        payload["schema_version"] != _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
        or payload["protocol_version"] != _DISTRIBUTION_JOURNAL_PROTOCOL_VERSION
        or not isinstance(root, dict)
        or set(root) != {"device", "inode"}
        or not all(isinstance(root[field], int) for field in ("device", "inode"))
        or not isinstance(workspace, dict)
        or set(workspace) != {"relative_path", "exists", "device", "inode", "ctime_ns", "file_type", "link_count"}
        or workspace.get("relative_path") != "spec-dock"
        or workspace.get("exists") is not True
        or workspace.get("file_type") != "directory"
        or any(
            isinstance(workspace.get(field), bool) or not isinstance(workspace.get(field), int)
            for field in ("device", "inode", "ctime_ns", "link_count")
        )
        or payload["intent"] not in {"update", "init-force"}
        or not isinstance(payload["authority"], str)
        or not isinstance(payload["package_version"], str)
        or not isinstance(payload["operation_id"], str)
        or not isinstance(payload["contract_identity"], str)
        or not isinstance(payload["plan_digest"], str)
        or not isinstance(payload["created_at_ns"], int)
        or payload["status"] not in {"prepared", "executing", "verifying", "completed"}
        or not isinstance(actions, list)
    ):
        raise DistributionApplyError("journal-protocol-incompatible")
    parsed_actions: list[OperationJournalAction] = []
    for item in actions:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "action", "provenance", "reason", "precondition", "postcondition", "checkpoint"}
            or not isinstance(item["path"], str)
            or item["action"] not in {"create", "adopt", "upgrade", "prune", "preserve", "block"}
            or item["provenance"] not in {"missing", "current", "historical", "unknown"}
            or not isinstance(item["reason"], str)
            or not isinstance(item["precondition"], dict)
            or not isinstance(item["postcondition"], dict)
            or item["checkpoint"] not in {"pending", "published", "verified"}
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        parsed_actions.append(
            OperationJournalAction(
                path=item["path"],
                action=item["action"],
                provenance=item["provenance"],
                reason=item["reason"],
                precondition=item["precondition"],
                postcondition=item["postcondition"],
                checkpoint=item["checkpoint"],
            )
        )
    raw_leases = payload["staging_leases"]
    if (
        not isinstance(raw_leases, list)
        or not isinstance(payload["staging_leases_digest"], str)
        or payload["staging_leases_digest"]
        != _staging_leases_digest(
            operation_id=payload["operation_id"],
            leases=raw_leases,
        )
    ):
        raise DistributionApplyError("journal-protocol-incompatible")
    leases: list[DistributionStageOwnership] = []
    for item in raw_leases:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "stage_name", "device", "inode", "ctime_ns", "file_type"}
            or not isinstance(item["path"], str)
            or not isinstance(item["stage_name"], str)
            or PurePosixPath(item["stage_name"]).name != item["stage_name"]
            or any(not isinstance(item[field], int) for field in ("device", "inode", "ctime_ns"))
            or not (
                all(item[field] == 0 for field in ("device", "inode", "ctime_ns"))
                or all(item[field] > 0 for field in ("device", "inode", "ctime_ns"))
            )
            or item["file_type"] not in {"regular", "symlink"}
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        leases.append(
            DistributionStageOwnership(
                path=item["path"],
                stage_name=item["stage_name"],
                device=item["device"],
                inode=item["inode"],
                ctime_ns=item["ctime_ns"],
                file_type=item["file_type"],
            )
        )
    raw_bindings = payload["created_parent_bindings"]
    if (
        not isinstance(raw_bindings, list)
        or not isinstance(payload["created_parent_bindings_digest"], str)
        or payload["created_parent_bindings_digest"]
        != _created_parent_bindings_digest(
            operation_id=payload["operation_id"],
            bindings=raw_bindings,
        )
    ):
        raise DistributionApplyError("journal-protocol-incompatible")
    created_parent_bindings: list[PathIdentitySnapshot] = []
    for item in raw_bindings:
        if (
            not isinstance(item, dict)
            or set(item) != {"relative_path", "exists", "device", "inode", "ctime_ns", "file_type", "link_count"}
            or not isinstance(item["relative_path"], str)
            or not isinstance(item["exists"], bool)
            or (
                item["exists"] is True
                and (
                    any(not isinstance(item[field], int) for field in ("device", "inode", "ctime_ns", "link_count"))
                    or item["file_type"] != "directory"
                )
            )
            or (
                item["exists"] is False
                and any(item[field] is not None for field in ("device", "inode", "ctime_ns", "file_type", "link_count"))
            )
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        created_parent_bindings.append(
            PathIdentitySnapshot(
                relative_path=item["relative_path"],
                exists=item["exists"],
                device=item["device"],
                inode=item["inode"],
                ctime_ns=item["ctime_ns"],
                file_type=item["file_type"],
                link_count=item["link_count"],
            )
        )
    if len({item.relative_path for item in created_parent_bindings}) != len(created_parent_bindings):
        raise DistributionApplyError("journal-protocol-incompatible")
    checkpoints = {action.checkpoint for action in parsed_actions}
    if (
        (payload["status"] == "prepared" and (checkpoints - {"pending"} or leases))
        or (payload["status"] == "executing" and "verified" in checkpoints)
        or (
            payload["status"] in {"verifying", "completed"}
            and (
                checkpoints != {"verified"} or leases or any(not binding.exists for binding in created_parent_bindings)
            )
        )
    ):
        raise DistributionApplyError("journal-protocol-incompatible")
    return OperationJournal(
        schema_version=payload["schema_version"],
        protocol_version=payload["protocol_version"],
        operation_id=payload["operation_id"],
        root_identity=DistributionRootIdentity(device=root["device"], inode=root["inode"]),
        workspace_identity=PathIdentitySnapshot(
            relative_path="spec-dock",
            exists=True,
            device=workspace["device"],
            inode=workspace["inode"],
            ctime_ns=workspace["ctime_ns"],
            file_type="directory",
            link_count=workspace["link_count"],
        ),
        intent=payload["intent"],
        authority=payload["authority"],
        package_version=payload["package_version"],
        contract_identity=payload["contract_identity"],
        plan_digest=payload["plan_digest"],
        created_at_ns=payload["created_at_ns"],
        status=payload["status"],
        actions=tuple(parsed_actions),
        staging_leases=tuple(leases),
        created_parent_bindings=tuple(created_parent_bindings),
    )


def _journal_package_is_compatible(journal_version: str, executing_version: str) -> bool:
    """Allow the same journal protocol to move forward, never backward."""

    try:
        journal_tuple = _parse_package_version(journal_version, source="journal package version")
        executing_tuple = _parse_package_version(executing_version, source="executing package version")
    except DistributionAdmissionError:
        return False
    return executing_tuple >= journal_tuple


class OperationJournalStore:
    """Descriptor-bound durable storage for one recognized operation journal."""

    def __init__(self, target_root: Path, *, identity_path: Path | None = None) -> None:
        self.target_root = Path(target_root)
        self.identity_path = Path(identity_path) if identity_path is not None else self.target_root
        self.path = self.target_root / _DISTRIBUTION_JOURNAL_REL
        self._forward_guard: DistributionRetryMarker | None = None

    @staticmethod
    def _workspace_condition(journal: OperationJournal) -> dict[str, object]:
        return _path_snapshot_condition(journal.workspace_identity)

    def _open_parent(
        self,
        expected_root: DistributionRootIdentity,
        expected_workspace: dict[str, object] | None = None,
    ) -> tuple[int, int]:
        flags = _distribution_directory_flags()
        try:
            root_fd = os.open(self.target_root, flags)
        except OSError as exc:
            raise DistributionApplyError("journal-root-mismatch") from exc
        try:
            opened = os.fstat(root_fd)
            visible = os.lstat(self.identity_path)
            if (
                stat.S_ISLNK(visible.st_mode)
                or not stat.S_ISDIR(visible.st_mode)
                or (opened.st_dev, opened.st_ino) != (expected_root.device, expected_root.inode)
                or (visible.st_dev, visible.st_ino) != (expected_root.device, expected_root.inode)
            ):
                raise DistributionApplyError("journal-root-mismatch")
            parent_fd = os.open("spec-dock", flags, dir_fd=root_fd)
            if expected_workspace is not None:
                parent = os.fstat(parent_fd)
                if (
                    expected_workspace.get("exists") is not True
                    or expected_workspace.get("file_type") != "directory"
                    or (parent.st_dev, parent.st_ino)
                    != (
                        expected_workspace.get("device"),
                        expected_workspace.get("inode"),
                    )
                ):
                    raise DistributionApplyError("journal-parent-mismatch")
        except Exception:
            os.close(root_fd)
            raise
        return root_fd, parent_fd

    @staticmethod
    def _same_marker_evidence(
        current: DistributionRetryMarker,
        expected: DistributionRetryMarker,
    ) -> bool:
        return (
            current == expected
            and current.purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE
            and current.source_snapshot is not None
            and current.source_snapshot == expected.source_snapshot
            and current.source_sha256 is not None
            and current.source_sha256 == expected.source_sha256
        )

    def _assert_current_forward_guard(self, marker: DistributionRetryMarker) -> None:
        try:
            current = _read_distribution_retry_marker(self.target_root)
        except DistributionAdmissionError as exc:
            raise DistributionApplyError("dual-recovery-state") from exc
        if current is None or not self._same_marker_evidence(current, marker):
            raise DistributionApplyError("dual-recovery-state")

    @staticmethod
    def _assert_bound_regular_entry(
        parent_fd: int,
        name: str,
        held_fd: int,
        expected_snapshot: PathIdentitySnapshot,
        expected_sha256: str,
        *,
        identity_error: str,
    ) -> os.stat_result:
        try:
            visible_before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            held_before = os.fstat(held_fd)
            raw = _read_fd_bytes(held_fd)
            held_after = os.fstat(held_fd)
            visible_after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except OSError as exc:
            raise DistributionApplyError(identity_error) from exc
        if (
            not stat.S_ISREG(held_before.st_mode)
            or held_before.st_nlink != 1
            or not _same_stat_identity(held_before, expected_snapshot)
            or _stat_identity_tuple(visible_before) != _stat_identity_tuple(held_before)
            or _stat_identity_tuple(held_after) != _stat_identity_tuple(held_before)
            or _stat_identity_tuple(visible_after) != _stat_identity_tuple(held_before)
            or hashlib.sha256(raw).hexdigest() != expected_sha256
        ):
            raise DistributionApplyError(identity_error)
        return held_after

    def _open_bound_forward_guard(self, parent_fd: int) -> int | None:
        marker = self._forward_guard
        if marker is None:
            return None
        expected_snapshot = marker.source_snapshot
        expected_sha256 = marker.source_sha256
        if expected_snapshot is None or expected_sha256 is None:
            raise DistributionApplyError("dual-recovery-state")
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if not isinstance(nofollow, int):
            raise DistributionApplyError("platform lacks required no-follow file support")
        try:
            guard_fd = os.open(
                _DISTRIBUTION_RETRY_MARKER_REL.name,
                os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent_fd,
            )
        except OSError as exc:
            raise DistributionApplyError("dual-recovery-state") from exc
        try:
            self._assert_bound_regular_entry(
                parent_fd,
                _DISTRIBUTION_RETRY_MARKER_REL.name,
                guard_fd,
                expected_snapshot,
                expected_sha256,
                identity_error="dual-recovery-state",
            )
        except Exception:
            os.close(guard_fd)
            raise
        return guard_fd

    def _assert_bound_forward_guard(self, parent_fd: int, guard_fd: int | None) -> None:
        if guard_fd is None:
            return
        assert self._forward_guard is not None
        assert self._forward_guard.source_snapshot is not None
        assert self._forward_guard.source_sha256 is not None
        self._assert_bound_regular_entry(
            parent_fd,
            _DISTRIBUTION_RETRY_MARKER_REL.name,
            guard_fd,
            self._forward_guard.source_snapshot,
            self._forward_guard.source_sha256,
            identity_error="dual-recovery-state",
        )

    def bind_forward_guard(self, marker: DistributionRetryMarker) -> None:
        self._assert_current_forward_guard(marker)
        self._forward_guard = marker

    def _assert_guard_anchors_journal(self, journal: OperationJournal) -> None:
        guard = self._forward_guard
        if guard is None:
            raise DistributionApplyError("dual-recovery-state")
        if guard.operation_id != journal.operation_id:
            raise DistributionApplyError("journal-plan-mismatch")
        if guard.contract_identity != journal.contract_identity:
            raise DistributionApplyError("journal-contract-mismatch")
        if guard.plan_digest != journal.plan_digest:
            raise DistributionApplyError("journal-plan-mismatch")

    def _write(
        self,
        journal: OperationJournal,
        *,
        predecessor: OperationJournal | None = None,
        require_absent: bool = False,
    ) -> OperationJournal:
        content = _journal_bytes(journal)
        predecessor_content = _journal_bytes(predecessor) if predecessor is not None else None
        root_fd, parent_fd = self._open_parent(
            journal.root_identity,
            self._workspace_condition(journal),
        )
        destination = _DISTRIBUTION_JOURNAL_REL.name
        stage = f".distribution-journal-{secrets.token_hex(16)}.stage"
        stage_info: os.stat_result | None = None
        stage_fd: int | None = None
        destination_fd: int | None = None
        guard_fd: int | None = None
        published_new = False
        swapped_out: os.stat_result | None = None
        try:
            guard_fd = self._open_bound_forward_guard(parent_fd)
            try:
                destination_info = os.stat(destination, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                destination_info = None
            if require_absent and destination_info is not None:
                raise DistributionApplyError("dual-recovery-state")
            if predecessor is not None and destination_info is None:
                raise DistributionApplyError("journal-precondition-mismatch")
            if destination_info is not None and (
                not stat.S_ISREG(destination_info.st_mode) or destination_info.st_nlink != 1
            ):
                raise DistributionApplyError("journal-protocol-incompatible")
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise DistributionApplyError("platform lacks required no-follow file support")
            if predecessor is not None:
                assert destination_info is not None
                expected_snapshot = predecessor.source_snapshot
                expected_sha256 = predecessor.source_sha256
                if expected_snapshot is None or expected_sha256 is None:
                    raise DistributionApplyError("journal-precondition-mismatch")
                try:
                    destination_fd = os.open(
                        destination,
                        os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                        dir_fd=parent_fd,
                    )
                except OSError as exc:
                    raise DistributionApplyError("journal-precondition-mismatch") from exc
                if (
                    not _same_stat_identity(destination_info, expected_snapshot)
                    or _stat_identity_tuple(os.fstat(destination_fd)) != _stat_identity_tuple(destination_info)
                    or (predecessor_bytes := _read_fd_bytes(destination_fd)) != predecessor_content
                    or hashlib.sha256(predecessor_bytes).hexdigest() != expected_sha256
                    or _stat_identity_tuple(os.fstat(destination_fd)) != _stat_identity_tuple(destination_info)
                ):
                    raise DistributionApplyError("journal-precondition-mismatch")
            try:
                stage_fd = os.open(
                    stage,
                    os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                    0o600,
                    dir_fd=parent_fd,
                )
            except OSError as exc:
                raise DistributionApplyError("journal publish failed") from exc
            _write_fd_bytes(stage_fd, content)
            os.fchmod(stage_fd, 0o600)
            stage_info = os.fstat(stage_fd)
            visible_stage = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
            if _stat_identity_tuple(visible_stage) != _stat_identity_tuple(stage_info) or not _held_fd_has_exact_bytes(
                stage_fd, content
            ):
                raise DistributionApplyError("journal-precondition-mismatch")
            self._assert_bound_forward_guard(parent_fd, guard_fd)
            if destination_info is None:
                _rename_distribution_no_replace(parent_fd, stage, parent_fd, destination)
                published_new = True
                published = os.stat(destination, dir_fd=parent_fd, follow_symlinks=False)
                if _stat_identity_tuple(published) != _stat_identity_tuple(
                    os.fstat(stage_fd)
                ) or not _held_fd_has_exact_bytes(stage_fd, content):
                    raise DistributionApplyError("journal-precondition-mismatch")
            else:
                assert destination_fd is not None
                swapped_out = _swap_regular_distribution_target_if_bound(
                    parent_fd,
                    stage,
                    destination,
                    target_fd=destination_fd,
                    staging_fd=stage_fd,
                    expected_target=destination_info,
                    identity_message="journal-precondition-mismatch",
                )
                published_new = True
                if not _held_fd_has_exact_bytes(stage_fd, content):
                    try:
                        _rename_distribution_swap(parent_fd, stage, parent_fd, destination)
                        os.fsync(parent_fd)
                    except OSError as exc:
                        raise DistributionApplyError("journal-precondition-mismatch") from exc
                    raise DistributionApplyError("journal-precondition-mismatch")
            os.fsync(parent_fd)
            self._assert_bound_forward_guard(parent_fd, guard_fd)
            published_info = os.fstat(stage_fd)
            successor_snapshot = _snapshot_from_stat(
                _DISTRIBUTION_JOURNAL_REL.as_posix(),
                published_info,
            )
            self._assert_bound_regular_entry(
                parent_fd,
                destination,
                stage_fd,
                successor_snapshot,
                hashlib.sha256(content).hexdigest(),
                identity_error="journal-precondition-mismatch",
            )
            visible = os.lstat(self.identity_path)
            if (visible.st_dev, visible.st_ino) != (
                journal.root_identity.device,
                journal.root_identity.inode,
            ):
                raise DistributionApplyError("journal-root-mismatch")
            if swapped_out is not None:
                _remove_distribution_stage_if_owned(
                    parent_fd,
                    stage,
                    swapped_out,
                    strict=True,
                )
            return replace(
                journal,
                source_snapshot=successor_snapshot,
                source_sha256=hashlib.sha256(content).hexdigest(),
            )
        except Exception:
            if published_new and stage_fd is not None and stage_info is not None:
                try:
                    if swapped_out is None:
                        _remove_distribution_target_if_bound(
                            parent_fd,
                            destination,
                            os.fstat(stage_fd),
                            held_fd=stage_fd,
                            identity_message="journal-precondition-mismatch",
                        )
                    elif destination_fd is not None:
                        visible_destination = os.stat(destination, dir_fd=parent_fd, follow_symlinks=False)
                        visible_stage = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
                        if _stat_identity_tuple(visible_destination) == _stat_identity_tuple(
                            os.fstat(stage_fd)
                        ) and _stat_identity_tuple(visible_stage) == _stat_identity_tuple(os.fstat(destination_fd)):
                            _rename_distribution_swap(parent_fd, stage, parent_fd, destination)
                            os.fsync(parent_fd)
                except (DistributionApplyError, OSError):
                    pass
            if stage_info is not None:
                _remove_distribution_stage_if_owned(parent_fd, stage, stage_info)
            raise
        finally:
            if guard_fd is not None:
                os.close(guard_fd)
            if destination_fd is not None:
                os.close(destination_fd)
            if stage_fd is not None:
                os.close(stage_fd)
            os.close(parent_fd)
            os.close(root_fd)

    def _read(self, expected_root: DistributionRootIdentity) -> OperationJournal:
        root_fd, parent_fd = self._open_parent(expected_root)
        try:
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise DistributionApplyError("platform lacks required no-follow file support")
            try:
                info = os.stat(_DISTRIBUTION_JOURNAL_REL.name, dir_fd=parent_fd, follow_symlinks=False)
                fd = os.open(
                    _DISTRIBUTION_JOURNAL_REL.name,
                    os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=parent_fd,
                )
            except FileNotFoundError as exc:
                raise DistributionApplyError("operation journal is missing") from exc
            except OSError as exc:
                raise DistributionApplyError("journal-protocol-incompatible") from exc
            try:
                opened = os.fstat(fd)
                if (
                    not stat.S_ISREG(info.st_mode)
                    or info.st_nlink != 1
                    or (opened.st_dev, opened.st_ino, opened.st_ctime_ns, opened.st_nlink)
                    != (info.st_dev, info.st_ino, info.st_ctime_ns, info.st_nlink)
                ):
                    raise DistributionApplyError("journal-protocol-incompatible")
                raw = _read_fd_bytes(fd)
                if len(raw) > 16 * 1024 * 1024:
                    raise DistributionApplyError("journal-protocol-incompatible")
                after_read = os.fstat(fd)
                if _stat_identity_tuple(after_read) != _stat_identity_tuple(opened):
                    raise DistributionApplyError("journal-protocol-incompatible")
            finally:
                os.close(fd)
            journal = replace(
                _parse_operation_journal(raw),
                source_snapshot=_snapshot_from_stat(_DISTRIBUTION_JOURNAL_REL.as_posix(), after_read),
                source_sha256=hashlib.sha256(raw).hexdigest(),
            )
            if journal.root_identity != expected_root:
                raise DistributionApplyError("journal-root-mismatch")
            parent = os.fstat(parent_fd)
            expected_workspace = self._workspace_condition(journal)
            if (
                expected_workspace.get("exists") is not True
                or expected_workspace.get("file_type") != "directory"
                or (parent.st_dev, parent.st_ino)
                != (
                    expected_workspace.get("device"),
                    expected_workspace.get("inode"),
                )
            ):
                raise DistributionApplyError("journal-parent-mismatch")
            return journal
        finally:
            os.close(parent_fd)
            os.close(root_fd)

    def prepare(self, plan: ExecutableMutationPlan, *, package_version: str) -> OperationJournal:
        created_at_ns = time.time_ns()
        guard = self._forward_guard
        if guard is None:
            try:
                existing_guard = _read_distribution_retry_marker(self.target_root)
            except DistributionAdmissionError as exc:
                raise DistributionApplyError("dual-recovery-state") from exc
            if existing_guard is not None:
                guard = existing_guard
            else:
                guard = self.prepare_legacy_guard(plan, package_version=package_version)
            self.bind_forward_guard(guard)
        if (
            guard.operation_id is None
            or guard.contract_identity != plan.contract_identity
            or guard.plan_digest != plan.plan_digest
        ):
            raise DistributionApplyError("dual-recovery-state")
        operation_id = guard.operation_id
        try:
            workspace_info = os.lstat(self.target_root / "spec-dock")
        except OSError as exc:
            raise DistributionApplyError("journal-parent-mismatch") from exc
        if stat.S_ISLNK(workspace_info.st_mode) or not stat.S_ISDIR(workspace_info.st_mode):
            raise DistributionApplyError("journal-parent-mismatch")
        journal = OperationJournal(
            schema_version=_DISTRIBUTION_JOURNAL_SCHEMA_VERSION,
            protocol_version=_DISTRIBUTION_JOURNAL_PROTOCOL_VERSION,
            operation_id=operation_id,
            root_identity=plan.root_identity,
            workspace_identity=_snapshot_from_stat("spec-dock", workspace_info),
            intent=plan.intent,
            authority="recognized-workspace-reconciliation",
            package_version=package_version,
            contract_identity=plan.contract_identity,
            plan_digest=plan.plan_digest,
            created_at_ns=created_at_ns,
            status="prepared",
            actions=tuple(
                OperationJournalAction(
                    path=action.path,
                    action=action.action,
                    provenance=action.provenance,
                    reason=action.reason,
                    precondition=_action_precondition_payload(plan.distribution_plan, action),
                    postcondition=_action_postcondition_payload(plan.distribution_plan, action),
                )
                for action in sorted(plan.actions, key=lambda item: (item.path, item.action, item.reason))
            ),
            created_parent_bindings=tuple(
                _missing_snapshot(path)
                for path in sorted({
                    parent.relative_path
                    for action in plan.actions
                    for parent in dict(plan.distribution_plan.target_snapshots)[action.path].parents
                    if not parent.exists
                })
            ),
        )
        return self._write(journal, require_absent=True)

    def prepare_legacy_guard(
        self,
        plan: ExecutableMutationPlan,
        *,
        package_version: str,
        replace_marker: DistributionRetryMarker | None = None,
    ) -> DistributionRetryMarker:
        """Publish an old-installer-visible guard before the new journal exists."""

        created_at_ns = time.time_ns()
        operation_id = hashlib.sha256(
            f"{plan.plan_digest}:{created_at_ns}:{secrets.token_hex(16)}".encode()
        ).hexdigest()
        marker = DistributionRetryMarker(
            operation=plan.intent,
            package_version=package_version,
            target_root=plan.root_identity,
            last_completed_phase="preflight-complete",
            purpose=_DISTRIBUTION_JOURNAL_GUARD_PURPOSE,
            operation_id=operation_id,
            contract_identity=plan.contract_identity,
            plan_digest=plan.plan_digest,
        )
        payload: dict[str, object] = {
            "schema_version": _DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {
                "device": marker.target_root.device,
                "inode": marker.target_root.inode,
            },
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
            "operation_id": marker.operation_id,
            "contract_identity": marker.contract_identity,
            "plan_digest": marker.plan_digest,
        }
        content = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        try:
            workspace_info = os.lstat(self.target_root / "spec-dock")
        except OSError as exc:
            raise DistributionApplyError("journal-parent-mismatch") from exc
        if stat.S_ISLNK(workspace_info.st_mode) or not stat.S_ISDIR(workspace_info.st_mode):
            raise DistributionApplyError("journal-parent-mismatch")
        workspace_condition = _path_snapshot_condition(_snapshot_from_stat("spec-dock", workspace_info))
        root_fd, parent_fd = self._open_parent(plan.root_identity, workspace_condition)
        destination = _DISTRIBUTION_RETRY_MARKER_REL.name
        stage = f".distribution-retry-{secrets.token_hex(16)}.stage"
        stage_info: os.stat_result | None = None
        swapped_out: os.stat_result | None = None
        held_fd: int | None = None
        stage_fd: int | None = None
        try:
            try:
                destination_info = os.stat(destination, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                destination_info = None
            if replace_marker is None and destination_info is not None:
                raise DistributionApplyError("dual-recovery-state")
            if replace_marker is not None:
                expected = replace_marker.source_snapshot
                expected_sha256 = replace_marker.source_sha256
                if expected is None or expected_sha256 is None or destination_info is None:
                    current = _read_distribution_retry_marker(self.target_root)
                    if current != replace_marker or current is None:
                        raise DistributionApplyError("legacy-marker-unconvertible")
                    expected = current.source_snapshot
                    expected_sha256 = current.source_sha256
                assert expected is not None
                assert expected_sha256 is not None
                if (
                    not expected.exists
                    or expected.file_type != "regular"
                    or expected.link_count != 1
                    or destination_info is None
                    or (
                        destination_info.st_dev,
                        destination_info.st_ino,
                        destination_info.st_ctime_ns,
                        _file_type(destination_info.st_mode),
                        destination_info.st_nlink,
                    )
                    != (
                        expected.device,
                        expected.inode,
                        expected.ctime_ns,
                        expected.file_type,
                        expected.link_count,
                    )
                ):
                    raise DistributionApplyError("legacy-marker-unconvertible")
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise DistributionApplyError("platform lacks required no-follow file support")
            if replace_marker is not None:
                try:
                    held_fd = os.open(
                        destination,
                        os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                        dir_fd=parent_fd,
                    )
                except OSError as exc:
                    raise DistributionApplyError("legacy-marker-unconvertible") from exc
                held_before = os.fstat(held_fd)
                assert destination_info is not None
                if (
                    held_before.st_dev,
                    held_before.st_ino,
                    held_before.st_ctime_ns,
                    held_before.st_mode,
                    held_before.st_nlink,
                ) != (
                    destination_info.st_dev,
                    destination_info.st_ino,
                    destination_info.st_ctime_ns,
                    destination_info.st_mode,
                    destination_info.st_nlink,
                ):
                    raise DistributionApplyError("legacy-marker-unconvertible")
                chunks: list[bytes] = []
                while True:
                    chunk = os.read(held_fd, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                held_after = os.fstat(held_fd)
                if (
                    held_before.st_dev,
                    held_before.st_ino,
                    held_before.st_ctime_ns,
                    held_before.st_mode,
                    held_before.st_nlink,
                ) != (
                    held_after.st_dev,
                    held_after.st_ino,
                    held_after.st_ctime_ns,
                    held_after.st_mode,
                    held_after.st_nlink,
                ) or hashlib.sha256(b"".join(chunks)).hexdigest() != expected_sha256:
                    raise DistributionApplyError("legacy-marker-unconvertible")
            stage_fd = os.open(
                stage,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                0o600,
                dir_fd=parent_fd,
            )
            _write_fd_bytes(stage_fd, content)
            os.fchmod(stage_fd, 0o600)
            stage_info = os.fstat(stage_fd)
            visible_stage = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
            if _stat_identity_tuple(visible_stage) != _stat_identity_tuple(stage_info) or not _held_fd_has_exact_bytes(
                stage_fd, content
            ):
                raise DistributionApplyError("legacy-marker-unconvertible")
            if replace_marker is None:
                _rename_distribution_no_replace(parent_fd, stage, parent_fd, destination)
                published = os.stat(destination, dir_fd=parent_fd, follow_symlinks=False)
                if _stat_identity_tuple(published) != _stat_identity_tuple(
                    os.fstat(stage_fd)
                ) or not _held_fd_has_exact_bytes(stage_fd, content):
                    raise DistributionApplyError("legacy-marker-unconvertible")
            else:
                assert destination_info is not None
                assert held_fd is not None
                swapped_out = _swap_regular_distribution_target_if_bound(
                    parent_fd,
                    stage,
                    destination,
                    target_fd=held_fd,
                    staging_fd=stage_fd,
                    expected_target=destination_info,
                    identity_message="legacy-marker-unconvertible",
                )
                if not _held_fd_has_exact_bytes(stage_fd, content):
                    try:
                        _rename_distribution_swap(parent_fd, stage, parent_fd, destination)
                        os.fsync(parent_fd)
                    except OSError as exc:
                        raise DistributionApplyError("legacy-marker-unconvertible") from exc
                    raise DistributionApplyError("legacy-marker-unconvertible")
            os.fsync(parent_fd)
            published_info = os.fstat(stage_fd)
            successor_snapshot = _snapshot_from_stat(
                _DISTRIBUTION_RETRY_MARKER_REL.as_posix(),
                published_info,
            )
            self._assert_bound_regular_entry(
                parent_fd,
                destination,
                stage_fd,
                successor_snapshot,
                hashlib.sha256(content).hexdigest(),
                identity_error="legacy-marker-unconvertible",
            )
            if swapped_out is not None:
                _remove_distribution_stage_if_owned(
                    parent_fd,
                    stage,
                    swapped_out,
                    strict=True,
                )
                os.fsync(parent_fd)
            return replace(
                marker,
                source_snapshot=successor_snapshot,
                source_sha256=hashlib.sha256(content).hexdigest(),
            )
        except Exception:
            if stage_info is not None:
                _remove_distribution_stage_if_owned(parent_fd, stage, stage_info)
            raise
        finally:
            if stage_fd is not None:
                os.close(stage_fd)
            if held_fd is not None:
                os.close(held_fd)
            os.close(parent_fd)
            os.close(root_fd)

    def resume(self, plan: ExecutableMutationPlan, *, package_version: str) -> OperationJournal:
        journal = self._read(plan.root_identity)
        self._assert_guard_anchors_journal(journal)
        if journal.root_identity != plan.root_identity:
            raise DistributionApplyError("journal-root-mismatch")
        if journal.intent != plan.intent:
            raise DistributionApplyError("journal-intent-mismatch")
        if journal.authority != "recognized-workspace-reconciliation":
            raise DistributionApplyError("journal-authority-mismatch")
        if journal.protocol_version != _DISTRIBUTION_JOURNAL_PROTOCOL_VERSION or not _journal_package_is_compatible(
            journal.package_version,
            package_version,
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        if journal.contract_identity != plan.contract_identity:
            raise DistributionApplyError("journal-contract-mismatch")
        if journal.plan_digest != plan.plan_digest:
            raise DistributionApplyError("journal-plan-mismatch")
        return journal

    def load_for_assessment(
        self,
        assessment: WorkspaceAssessment,
        *,
        package_version: str,
        require_guard: bool = True,
    ) -> OperationJournal:
        journal = self._read(assessment.root_identity)
        if require_guard:
            self._assert_guard_anchors_journal(journal)
        elif journal.status != "completed":
            raise DistributionApplyError("dual-recovery-state")
        if journal.root_identity != assessment.root_identity:
            raise DistributionApplyError("journal-root-mismatch")
        if journal.intent != assessment.intent:
            raise DistributionApplyError("journal-intent-mismatch")
        if journal.authority != "recognized-workspace-reconciliation":
            raise DistributionApplyError("journal-authority-mismatch")
        if journal.protocol_version != _DISTRIBUTION_JOURNAL_PROTOCOL_VERSION or not _journal_package_is_compatible(
            journal.package_version,
            package_version,
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        if journal.contract_identity != assessment.contract_identity:
            raise DistributionApplyError("journal-contract-mismatch")
        return journal

    def write(
        self,
        journal: OperationJournal,
        *,
        predecessor: OperationJournal | None = None,
    ) -> OperationJournal:
        if predecessor is None:
            predecessor = self._read(journal.root_identity)
        return self._write(journal, predecessor=predecessor)

    def mark_executing(self, journal: OperationJournal) -> OperationJournal:
        if journal.status not in {"prepared", "executing"}:
            raise DistributionApplyError("journal-precondition-mismatch")
        return self.write(replace(journal, status="executing"), predecessor=journal)

    def checkpoint_published(
        self,
        journal: OperationJournal,
        completed_paths: tuple[str, ...],
    ) -> OperationJournal:
        completed = set(completed_paths)
        active = journal
        records = {record.path: record for record in journal.actions}
        rebound_leases: list[DistributionStageOwnership] = []
        rebound = False
        for lease in active.staging_leases:
            if lease.path not in completed:
                rebound_leases.append(lease)
                continue
            try:
                parent_chain = _open_distribution_parent_chain(
                    self.target_root,
                    lease.path,
                    create_missing=False,
                )
            except DistributionApplyError as exc:
                raise DistributionApplyError("managed staging cleanup failed") from exc
            try:
                try:
                    stage_info = os.stat(lease.stage_name, dir_fd=parent_chain[-1], follow_symlinks=False)
                except FileNotFoundError:
                    if lease.device == lease.inode == lease.ctime_ns == 0:
                        raise DistributionApplyError("managed staging cleanup failed") from None
                    record = records.get(lease.path)
                    if record is None:
                        raise DistributionApplyError("managed staging cleanup failed") from None
                    target_name = PurePosixPath(lease.path).name
                    try:
                        target_info = os.stat(target_name, dir_fd=parent_chain[-1], follow_symlinks=False)
                    except FileNotFoundError as exc:
                        if record.action == "prune" and record.postcondition.get("exists") is False:
                            continue
                        raise DistributionApplyError("managed staging cleanup failed") from exc
                    target_identity = _distribution_stage_identity(parent_chain[-1], target_name, lease.path)
                    if (
                        target_info.st_dev != lease.device
                        or target_info.st_ino != lease.inode
                        or _file_type(target_info.st_mode) != lease.file_type
                        or target_info.st_nlink != 1
                        or record.postcondition.get("identity") != _distribution_identity_payload(target_identity)
                    ):
                        raise DistributionApplyError("managed staging cleanup failed") from None
                    rebound_leases.append(lease)
                    continue
                if lease.device == lease.inode == lease.ctime_ns == 0:
                    record = records.get(lease.path)
                    candidate = _distribution_stage_identity(
                        parent_chain[-1],
                        lease.stage_name,
                        lease.path,
                    )
                    if (
                        record is None
                        or record.action != "prune"
                        or stage_info.st_dev != record.precondition.get("device")
                        or stage_info.st_ino != record.precondition.get("inode")
                        or _file_type(stage_info.st_mode) != record.precondition.get("file_type")
                        or stage_info.st_nlink != record.precondition.get("link_count") == 1
                        or record.precondition.get("identity") != _distribution_identity_payload(candidate)
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    rebound_leases.append(_distribution_stage_ownership(lease.path, lease.stage_name, stage_info))
                    rebound = True
                    continue
                if (
                    stage_info.st_dev == lease.device
                    and stage_info.st_ino == lease.inode
                    and stage_info.st_ctime_ns == lease.ctime_ns
                    and _file_type(stage_info.st_mode) == lease.file_type
                    and stage_info.st_nlink == 1
                ):
                    rebound_leases.append(lease)
                    continue
                record = records.get(lease.path)
                if record is None or record.action != "upgrade":
                    raise DistributionApplyError("managed staging cleanup failed")
                target_name = PurePosixPath(lease.path).name
                target_info = os.stat(target_name, dir_fd=parent_chain[-1], follow_symlinks=False)
                target_identity = _distribution_stage_identity(parent_chain[-1], target_name, lease.path)
                stage_identity = _distribution_stage_identity(parent_chain[-1], lease.stage_name, lease.path)
                pre = record.precondition
                post = record.postcondition
                canonical_is_published_lease = (
                    target_info.st_dev == lease.device
                    and target_info.st_ino == lease.inode
                    and _file_type(target_info.st_mode) == lease.file_type
                    and target_info.st_nlink == 1
                    and post.get("identity") == _distribution_identity_payload(target_identity)
                )
                stage_is_displaced_predecessor = (
                    stage_info.st_dev == pre.get("device")
                    and stage_info.st_ino == pre.get("inode")
                    and _file_type(stage_info.st_mode) == pre.get("file_type")
                    and stage_info.st_nlink == pre.get("link_count") == 1
                    and pre.get("identity") == _distribution_identity_payload(stage_identity)
                )
                if not canonical_is_published_lease or not stage_is_displaced_predecessor:
                    raise DistributionApplyError("managed staging cleanup failed")
                rebound_leases.append(_distribution_stage_ownership(lease.path, lease.stage_name, stage_info))
                rebound = True
            finally:
                _close_distribution_parent_chain(parent_chain)
        if rebound:
            active = self.write(
                replace(active, staging_leases=tuple(rebound_leases)),
                predecessor=active,
            )
        for lease in active.staging_leases:
            if lease.path not in completed:
                continue
            try:
                parent_chain = _open_distribution_parent_chain(
                    self.target_root,
                    lease.path,
                    create_missing=False,
                )
            except DistributionApplyError as exc:
                raise DistributionApplyError("managed staging cleanup failed") from exc
            try:
                try:
                    stage_info = os.stat(lease.stage_name, dir_fd=parent_chain[-1], follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if (
                    stage_info.st_dev != lease.device
                    or stage_info.st_ino != lease.inode
                    or stage_info.st_ctime_ns != lease.ctime_ns
                    or _file_type(stage_info.st_mode) != lease.file_type
                    or stage_info.st_nlink != 1
                ):
                    raise DistributionApplyError("managed staging cleanup failed")
                _remove_distribution_stage_if_owned(
                    parent_chain[-1],
                    lease.stage_name,
                    stage_info,
                    strict=True,
                )
            finally:
                _close_distribution_parent_chain(parent_chain)
        actions = tuple(
            replace(action, checkpoint="published")
            if action.path in completed and action.checkpoint == "pending"
            else action
            for action in active.actions
        )
        staging_leases = tuple(lease for lease in active.staging_leases if lease.path not in completed)
        return self.write(
            replace(
                active,
                status="executing",
                actions=actions,
                staging_leases=staging_leases,
            ),
            predecessor=active,
        )

    def record_staging_lease(
        self,
        journal: OperationJournal,
        lease: DistributionStageOwnership,
    ) -> OperationJournal:
        # One action owns at most one live private-stage transition.  A new
        # attempt is recorded only after stale-stage cleanup, so it supersedes
        # any earlier lease for the same canonical path.
        retained = tuple(item for item in journal.staging_leases if item.path != lease.path)
        return self.write(replace(journal, staging_leases=(*retained, lease)), predecessor=journal)

    def record_created_parent_bindings(
        self,
        journal: OperationJournal,
        bindings: tuple[PathIdentitySnapshot, ...],
    ) -> OperationJournal:
        existing = {binding.relative_path: binding for binding in journal.created_parent_bindings}
        for binding in bindings:
            current = existing.get(binding.relative_path)
            if current is not None and current.exists and not _same_structure_identity(current, binding):
                raise DistributionApplyError("journal-precondition-mismatch")
            existing[binding.relative_path] = binding
        ordered = tuple(existing[path] for path in sorted(existing))
        return self.write(replace(journal, created_parent_bindings=ordered), predecessor=journal)

    def mark_verified(self, journal: OperationJournal) -> OperationJournal:
        if (
            journal.staging_leases
            or any(action.checkpoint == "pending" for action in journal.actions)
            or any(not binding.exists for binding in journal.created_parent_bindings)
        ):
            raise DistributionApplyError("journal-precondition-mismatch")
        actions = tuple(replace(action, checkpoint="verified") for action in journal.actions)
        return self.write(replace(journal, status="verifying", actions=actions), predecessor=journal)

    def mark_completed(self, journal: OperationJournal) -> OperationJournal:
        if journal.staging_leases or any(action.checkpoint != "verified" for action in journal.actions):
            raise DistributionApplyError("journal-precondition-mismatch")
        return self.write(replace(journal, status="completed"), predecessor=journal)

    def remove_completed(self, journal: OperationJournal, *, guard_already_removed: bool = False) -> None:
        if (
            journal.status != "completed"
            or journal.staging_leases
            or any(action.checkpoint != "verified" for action in journal.actions)
        ):
            raise DistributionApplyError("journal-precondition-mismatch")
        self._remove_exact(
            journal,
            failure_reason="journal finalization failed",
            require_guard=not guard_already_removed,
        )

    def discard_prepared(self, journal: OperationJournal) -> None:
        """Roll back a journal that has not acquired leases or mutation progress."""

        if (
            journal.status != "prepared"
            or journal.staging_leases
            or any(action.checkpoint != "pending" for action in journal.actions)
        ):
            raise DistributionApplyError("journal-precondition-mismatch")
        self._remove_exact(journal, failure_reason="journal rollback failed")

    def _remove_exact(
        self,
        journal: OperationJournal,
        *,
        failure_reason: str,
        require_guard: bool = True,
    ) -> None:
        root_fd, parent_fd = self._open_parent(journal.root_identity)
        guard_fd: int | None = None
        try:
            if require_guard:
                guard_fd = self._open_bound_forward_guard(parent_fd)
            name = _DISTRIBUTION_JOURNAL_REL.name
            try:
                info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                return
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise DistributionApplyError("journal-protocol-incompatible")
            expected_snapshot = journal.source_snapshot
            expected_sha256 = journal.source_sha256
            if expected_snapshot is None or expected_sha256 is None or not _same_stat_identity(info, expected_snapshot):
                raise DistributionApplyError("journal-precondition-mismatch")
            self._quarantine_and_remove(
                parent_fd,
                name,
                info,
                expected_snapshot=expected_snapshot,
                expected_sha256=expected_sha256,
                pre_delete_check=(
                    (lambda: self._assert_bound_forward_guard(parent_fd, guard_fd)) if require_guard else None
                ),
                identity_error="journal-precondition-mismatch",
                failure_reason=failure_reason,
            )
        finally:
            if guard_fd is not None:
                os.close(guard_fd)
            os.close(parent_fd)
            os.close(root_fd)

    def _quarantine_and_remove(
        self,
        parent_fd: int,
        name: str,
        expected: os.stat_result,
        *,
        expected_snapshot: PathIdentitySnapshot,
        expected_sha256: str,
        pre_delete_check: Callable[[], None] | None = None,
        identity_error: str,
        failure_reason: str,
    ) -> None:
        """Move a bound regular file aside before deleting its exact identity."""

        identity_token = hashlib.sha256(
            f"{expected.st_dev}:{expected.st_ino}:{expected.st_ctime_ns}".encode()
        ).hexdigest()[:16]
        token = f"{identity_token}-{secrets.token_hex(16)}"
        quarantine = f".{name}.{token}.remove"
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if not isinstance(nofollow, int):
            raise DistributionApplyError("platform lacks required no-follow file support")
        try:
            held_fd = os.open(
                name,
                os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent_fd,
            )
        except OSError as exc:
            raise DistributionApplyError(identity_error) from exc
        try:
            try:
                held_before = os.fstat(held_fd)
                if (
                    held_before.st_dev,
                    held_before.st_ino,
                    held_before.st_ctime_ns,
                    held_before.st_mode,
                    held_before.st_nlink,
                ) != (
                    expected.st_dev,
                    expected.st_ino,
                    expected.st_ctime_ns,
                    expected.st_mode,
                    expected.st_nlink,
                ) or not _same_stat_identity(held_before, expected_snapshot):
                    raise DistributionApplyError(identity_error)
                raw = _read_fd_bytes(held_fd)
                if hashlib.sha256(raw).hexdigest() != expected_sha256 or _stat_identity_tuple(
                    os.fstat(held_fd)
                ) != _stat_identity_tuple(held_before):
                    raise DistributionApplyError(identity_error)
                _rename_distribution_no_replace(parent_fd, name, parent_fd, quarantine)
            except OSError as exc:
                raise DistributionApplyError(failure_reason) from exc
            try:
                moved = os.stat(quarantine, dir_fd=parent_fd, follow_symlinks=False)
                held_after = os.fstat(held_fd)
            except OSError as exc:
                raise DistributionApplyError(failure_reason) from exc
            moved_identity = (
                moved.st_dev,
                moved.st_ino,
                moved.st_ctime_ns,
                moved.st_mode,
                moved.st_nlink,
            )
            held_identity = (
                held_after.st_dev,
                held_after.st_ino,
                held_after.st_ctime_ns,
                held_after.st_mode,
                held_after.st_nlink,
            )
            if moved_identity != held_identity:
                self._restore_quarantined_entry(
                    parent_fd,
                    name,
                    quarantine,
                    held_fd,
                    identity_error=identity_error,
                    failure_reason=failure_reason,
                    require_held_identity=False,
                )
                raise DistributionApplyError(identity_error)
            try:
                # Persist the name transition before the destructive step.  A
                # later cleanup failure can then restore the still-linked exact
                # inode instead of losing the canonical recovery authority.
                os.fsync(parent_fd)
                if pre_delete_check is not None:
                    pre_delete_check()
                _remove_distribution_stage_if_owned(parent_fd, quarantine, moved, strict=True)
            except (DistributionApplyError, OSError) as exc:
                self._restore_quarantined_entry(
                    parent_fd,
                    name,
                    quarantine,
                    held_fd,
                    identity_error=identity_error,
                    failure_reason=failure_reason,
                    require_held_identity=True,
                )
                raise DistributionApplyError(failure_reason) from exc
        finally:
            os.close(held_fd)

    @staticmethod
    def _restore_quarantined_entry(
        parent_fd: int,
        name: str,
        quarantine: str,
        held_fd: int,
        *,
        identity_error: str,
        failure_reason: str,
        require_held_identity: bool,
    ) -> None:
        """Restore the held recovery entry after a post-rename failure."""

        try:
            quarantined = os.stat(quarantine, dir_fd=parent_fd, follow_symlinks=False)
            held = os.fstat(held_fd)
        except OSError as exc:
            raise DistributionApplyError(failure_reason) from exc
        if require_held_identity and (
            quarantined.st_dev,
            quarantined.st_ino,
            quarantined.st_ctime_ns,
            quarantined.st_mode,
            quarantined.st_nlink,
        ) != (
            held.st_dev,
            held.st_ino,
            held.st_ctime_ns,
            held.st_mode,
            held.st_nlink,
        ):
            raise DistributionApplyError(identity_error)
        try:
            _rename_distribution_no_replace(parent_fd, quarantine, parent_fd, name)
            os.fsync(parent_fd)
        except OSError as exc:
            raise DistributionApplyError(failure_reason) from exc

    def remove_legacy_marker(self, marker: DistributionRetryMarker) -> None:
        if marker.target_root != _root_identity_for_assessment(self.target_root):
            raise DistributionApplyError("journal-root-mismatch")
        if marker.purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE:
            self._assert_current_forward_guard(marker)
        else:
            current = _read_distribution_retry_marker(self.target_root)
            if current != marker:
                raise DistributionApplyError("legacy-marker-unconvertible")
        root_fd, parent_fd = self._open_parent(marker.target_root)
        try:
            name = _DISTRIBUTION_RETRY_MARKER_REL.name
            try:
                info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except OSError as exc:
                raise DistributionApplyError("legacy-marker-unconvertible") from exc
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise DistributionApplyError("legacy-marker-unconvertible")
            expected_snapshot = marker.source_snapshot
            expected_sha256 = marker.source_sha256
            if expected_snapshot is None or expected_sha256 is None or not _same_stat_identity(info, expected_snapshot):
                raise DistributionApplyError("legacy-marker-unconvertible")
            self._quarantine_and_remove(
                parent_fd,
                name,
                info,
                expected_snapshot=expected_snapshot,
                expected_sha256=expected_sha256,
                identity_error="legacy-marker-unconvertible",
                failure_reason="legacy-marker-unconvertible",
            )
        finally:
            os.close(parent_fd)
            os.close(root_fd)


def _generated_regular_asset(
    path: str,
    content: bytes,
    *,
    mode: int,
    refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None,
) -> DistributionAsset:
    return DistributionAsset(
        path=path,
        identity=DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=mode,
        ),
        generated_content=content,
        refreshable_existing_identities=refreshable_existing_identities,
    )


def _journal_digest(journal: OperationJournal) -> str:
    payload = {
        "schema_version": 1,
        "intent": journal.intent,
        "root_binding": {
            "device": journal.root_identity.device,
            "inode": journal.root_identity.inode,
        },
        "contract_identity": journal.contract_identity,
        "actions": [
            {
                "path": action.path,
                "action": action.action,
                "provenance": action.provenance,
                "reason": action.reason,
                "precondition": _plan_digest_condition(action.precondition),
                "postcondition": _plan_digest_condition(action.postcondition),
            }
            for action in journal.actions
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _snapshot_matches_condition(
    snapshot: DistributionTargetSnapshot,
    condition: dict[str, object],
    created_parent_bindings: tuple[PathIdentitySnapshot, ...] = (),
) -> bool:
    root_condition = condition.get("root")
    if not isinstance(root_condition, dict) or not _path_snapshot_matches_condition(snapshot.root, root_condition):
        return False
    parent_conditions = condition.get("parents")
    if not isinstance(parent_conditions, list):
        return False
    actual_parents = {parent.relative_path: parent for parent in snapshot.parents}
    bound_parents = {parent.relative_path: parent for parent in created_parent_bindings}
    for parent_condition in parent_conditions:
        if not isinstance(parent_condition, dict):
            return False
        relative_path = parent_condition.get("relative_path")
        if not isinstance(relative_path, str):
            return False
        actual_parent = actual_parents.get(relative_path)
        if actual_parent is None or not _path_snapshot_matches_condition(actual_parent, parent_condition):
            bound_parent = bound_parents.get(relative_path)
            if (
                parent_condition.get("exists") is not False
                or actual_parent is None
                or bound_parent is None
                or not bound_parent.exists
                or actual_parent.file_type != "directory"
                or not _same_structure_identity(actual_parent, bound_parent)
            ):
                return False
    target = snapshot.target
    if condition.get("exists") != target.exists:
        return False
    if "device" in condition and condition.get("device") != target.device:
        return False
    if "inode" in condition and condition.get("inode") != target.inode:
        return False
    if "ctime_ns" in condition and condition.get("ctime_ns") != target.ctime_ns:
        return False
    if "file_type" in condition and condition.get("file_type") != target.file_type:
        return False
    if "link_count" in condition and condition.get("link_count") != target.link_count:
        return False
    return condition.get("identity") == _distribution_identity_payload(target.identity)


def _path_snapshot_matches_condition(snapshot: PathIdentitySnapshot, condition: dict[str, object]) -> bool:
    return all(
        condition.get(field) == getattr(snapshot, field)
        for field in ("relative_path", "exists", "device", "inode", "file_type")
    )


def _condition_has_complete_parent_chain(
    snapshot: DistributionTargetSnapshot,
    condition: dict[str, object],
) -> bool:
    parent_conditions = condition.get("parents")
    if not isinstance(parent_conditions, list):
        return False
    relative_paths = tuple(
        parent.get("relative_path") if isinstance(parent, dict) else None for parent in parent_conditions
    )
    return relative_paths == tuple(parent.relative_path for parent in snapshot.parents)


def _condition_has_complete_target_identity(condition: dict[str, object]) -> bool:
    required_fields = {
        "root",
        "parents",
        "exists",
        "device",
        "inode",
        "ctime_ns",
        "file_type",
        "link_count",
        "identity",
    }
    if set(condition) != required_fields or not isinstance(condition["exists"], bool):
        return False
    if condition["exists"] is False:
        return all(
            condition[field] is None for field in ("device", "inode", "ctime_ns", "file_type", "link_count", "identity")
        )
    return (
        all(
            isinstance(condition[field], int) and not isinstance(condition[field], bool)
            for field in ("device", "inode", "ctime_ns", "link_count")
        )
        and isinstance(condition["file_type"], str)
        and isinstance(condition["identity"], dict)
    )


def _assert_journal_action_contract(assessment: WorkspaceAssessment, journal: OperationJournal) -> None:
    plan = assessment.distribution_plan
    if plan.target_root is None:
        raise DistributionApplyError("journal-plan-mismatch")
    current_actions = {action.path: action for action in assessment.actions}
    records = {record.path: record for record in journal.actions}
    completed_missing_obsolete = {
        record.path
        for record in journal.actions
        if record.action == "prune" and record.checkpoint != "pending" and record.path not in current_actions
    }
    if len(records) != len(journal.actions) or set(records) - completed_missing_obsolete != set(current_actions):
        raise DistributionApplyError("journal-plan-mismatch")
    lease_keys = {(lease.path, lease.stage_name) for lease in journal.staging_leases}
    if len(lease_keys) != len(journal.staging_leases):
        raise DistributionApplyError("journal-plan-mismatch")
    allowed_created_parents: set[str] = set()
    for record in journal.actions:
        if not _condition_has_complete_target_identity(record.precondition):
            raise DistributionApplyError("journal-plan-mismatch")
        parents = record.precondition.get("parents")
        if not isinstance(parents, list):
            raise DistributionApplyError("journal-plan-mismatch")
        allowed_created_parents.update(
            parent["relative_path"]
            for parent in parents
            if isinstance(parent, dict)
            and parent.get("exists") is False
            and isinstance(parent.get("relative_path"), str)
        )
    if any(binding.relative_path not in allowed_created_parents for binding in journal.created_parent_bindings):
        raise DistributionApplyError("journal-plan-mismatch")
    actual_parents = {
        parent.relative_path: parent for snapshot in dict(plan.target_snapshots).values() for parent in snapshot.parents
    }
    if any(
        binding.exists
        and (
            (actual := actual_parents.get(binding.relative_path)) is None
            or not _same_structure_identity(actual, binding)
        )
        for binding in journal.created_parent_bindings
    ):
        raise DistributionApplyError("journal-precondition-mismatch")
    for lease in journal.staging_leases:
        if lease.path not in records:
            raise DistributionApplyError("journal-plan-mismatch")
        expected = _expected_target_identity(plan, lease.path)
        known_identities = tuple(
            identity for identity in (expected, *_historical_stage_identities(plan, lease.path)) if identity is not None
        )
        if not any(
            _matches_distribution_stage_name(lease.stage_name, lease.path, identity) for identity in known_identities
        ):
            raise DistributionApplyError("journal-plan-mismatch")
    current_specs = _target_identity_specs(plan.current_assets, plan.scaffold_assets)
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files} - set(current_specs)
    for record in journal.actions:
        if record.action == "prune":
            if record.path not in obsolete_paths or record.postcondition.get("exists") is not False:
                raise DistributionApplyError("journal-plan-mismatch")
        else:
            expected_identity = current_specs.get(record.path)
            if expected_identity is None or record.action not in {"create", "adopt", "upgrade", "preserve"}:
                raise DistributionApplyError("journal-plan-mismatch")
            if (
                record.postcondition.get("exists") is not True
                or record.postcondition.get("file_type") != expected_identity.kind
                or record.postcondition.get("link_count") != 1
                or record.postcondition.get("identity") != _distribution_identity_payload(expected_identity)
            ):
                raise DistributionApplyError("journal-plan-mismatch")
        snapshot = dict(plan.target_snapshots).get(record.path)
        if snapshot is None and record.path in completed_missing_obsolete:
            snapshot = _observe_target(plan.target_root, record.path).snapshot
        if (
            snapshot is None
            or not _condition_has_complete_parent_chain(snapshot, record.precondition)
            or not _condition_has_complete_parent_chain(snapshot, record.postcondition)
        ):
            raise DistributionApplyError("journal-plan-mismatch")
        if record.checkpoint == "pending":
            current = current_actions[record.path]
            if (record.action, record.provenance, record.reason) != (
                current.action,
                current.provenance,
                current.reason,
            ):
                raise DistributionApplyError("journal-plan-mismatch")
            if not _snapshot_matches_condition(
                snapshot,
                record.precondition,
                journal.created_parent_bindings,
            ):
                raise DistributionApplyError("journal-plan-mismatch")


def _resume_executable_plan(
    assessment: WorkspaceAssessment,
    journal: OperationJournal,
) -> ExecutableMutationPlan:
    if _journal_digest(journal) != journal.plan_digest:
        raise DistributionApplyError("journal-plan-mismatch")
    _assert_journal_action_contract(assessment, journal)
    plan = assessment.distribution_plan
    if plan.target_root is None:
        raise DistributionApplyError("journal-plan-mismatch")
    snapshots = dict(plan.target_snapshots)
    original_actions: list[DistributionAction] = []
    pending_actions: list[DistributionAction] = []
    for record in journal.actions:
        snapshot = snapshots.get(record.path)
        if snapshot is None and record.action == "prune" and record.checkpoint != "pending":
            snapshot = _observe_target(plan.target_root, record.path).snapshot
        if snapshot is None:
            raise DistributionApplyError("journal-precondition-mismatch")
        expected = record.precondition if record.checkpoint == "pending" else record.postcondition
        if not _snapshot_matches_condition(snapshot, expected, journal.created_parent_bindings):
            raise DistributionApplyError("journal-precondition-mismatch")
        action = DistributionAction(
            path=record.path,
            operation=journal.intent,
            action=record.action,
            provenance=record.provenance,
            reason=record.reason,
        )
        original_actions.append(action)
        if record.checkpoint == "pending":
            pending_actions.append(action)
    pending_plan = replace(assessment.distribution_plan, actions=tuple(pending_actions))
    return ExecutableMutationPlan(
        intent=journal.intent,
        root_identity=journal.root_identity,
        contract_identity=journal.contract_identity,
        plan_digest=journal.plan_digest,
        distribution_plan=pending_plan,
        actions=tuple(original_actions),
    )


def _reconcile_pending_journal_actions(
    assessment: WorkspaceAssessment,
    journal: OperationJournal,
) -> OperationJournal:
    """Advance crash-ambiguous pending records only from exact observation."""

    snapshots = dict(assessment.distribution_plan.target_snapshots)
    reconciled: list[OperationJournalAction] = []
    changed = False
    for record in journal.actions:
        if record.checkpoint != "pending":
            reconciled.append(record)
            continue
        snapshot = snapshots.get(record.path)
        if snapshot is None:
            raise DistributionApplyError("journal-precondition-mismatch")
        matches_pre = _snapshot_matches_condition(snapshot, record.precondition, journal.created_parent_bindings)
        matches_post = _snapshot_matches_condition(snapshot, record.postcondition, journal.created_parent_bindings)
        if matches_post and (not matches_pre or record.action in {"adopt", "preserve"}):
            reconciled.append(replace(record, checkpoint="published"))
            changed = True
            continue
        if matches_pre and not matches_post:
            reconciled.append(record)
            continue
        raise DistributionApplyError("journal-precondition-mismatch")
    if not changed:
        return journal
    return replace(journal, status="executing", actions=tuple(reconciled))


def _reconcile_created_parent_bindings(
    store: OperationJournalStore,
    assessment: WorkspaceAssessment,
    journal: OperationJournal,
) -> OperationJournal:
    """Bind an empty parent created immediately before an abrupt stop."""

    actual_parents = {
        parent.relative_path: parent
        for snapshot in dict(assessment.distribution_plan.target_snapshots).values()
        for parent in snapshot.parents
    }
    bindings = {binding.relative_path: binding for binding in journal.created_parent_bindings}
    changed = False
    for relative_path, binding in tuple(bindings.items()):
        if binding.exists:
            continue
        actual = actual_parents.get(relative_path)
        if actual is None or not actual.exists:
            continue
        if actual.file_type != "directory":
            raise DistributionApplyError("journal-precondition-mismatch")
        parent_path = store.target_root / PurePosixPath(relative_path)
        try:
            if any(parent_path.iterdir()):
                raise DistributionApplyError("journal-precondition-mismatch")
        except OSError as exc:
            raise DistributionApplyError("journal-precondition-mismatch") from exc
        if any(
            action.checkpoint != "pending"
            for action in journal.actions
            if action.path == relative_path or action.path.startswith(f"{relative_path}/")
        ):
            raise DistributionApplyError("journal-precondition-mismatch")
        bindings[relative_path] = actual
        changed = True
    if not changed:
        return journal
    return store.write(
        replace(
            journal,
            created_parent_bindings=tuple(bindings[path] for path in sorted(bindings)),
        ),
        predecessor=journal,
    )


def _journal_version_precondition_identity(journal: OperationJournal) -> DistributionIdentity | None:
    for action in journal.actions:
        if action.path != "spec-dock/spec-dock.version":
            continue
        identity = action.precondition.get("identity")
        if (
            isinstance(identity, dict)
            and identity.get("kind") == "regular"
            and isinstance(identity.get("sha256"), str)
            and (identity.get("mode") is None or isinstance(identity.get("mode"), int))
        ):
            return DistributionIdentity(
                kind="regular",
                sha256=identity["sha256"],
                mode=identity.get("mode"),
            )
    return None


def _validated_legacy_stage_leases(
    plan: ExecutableMutationPlan,
    marker: DistributionRetryMarker,
    target_root: Path,
) -> tuple[DistributionStageOwnership, ...]:
    """Bind exact legacy private stages to the reconstructed current plan."""

    if not marker.stage_ownership:
        return ()
    actions = {action.path: action for action in plan.actions}
    snapshots = _plan_snapshot_map(plan.distribution_plan)
    seen: set[tuple[str, str]] = set()
    validated: list[DistributionStageOwnership] = []
    for lease in marker.stage_ownership:
        key = (lease.path, lease.stage_name)
        action = actions.get(lease.path)
        snapshot = snapshots.get(lease.path)
        expected = _expected_target_identity(plan.distribution_plan, lease.path)
        historical = _historical_stage_identities(plan.distribution_plan, lease.path)
        if (
            key in seen
            or action is None
            or action.action not in {"create", "upgrade", "prune"}
            or snapshot is None
            or expected is None
            or not any(
                _matches_distribution_stage_name(lease.stage_name, lease.path, identity)
                for identity in (expected, *historical)
            )
        ):
            raise DistributionApplyError("legacy-marker-unconvertible")
        seen.add(key)
        try:
            parent_chain = _open_distribution_parent_chain(
                target_root,
                lease.path,
                create_missing=False,
                expected_snapshot=snapshot,
            )
        except DistributionApplyError as exc:
            raise DistributionApplyError("legacy-marker-unconvertible") from exc
        try:
            try:
                current = os.stat(lease.stage_name, dir_fd=parent_chain[-1], follow_symlinks=False)
            except OSError as exc:
                raise DistributionApplyError("legacy-marker-unconvertible") from exc
            if (
                current.st_dev != lease.device
                or current.st_ino != lease.inode
                or current.st_ctime_ns != lease.ctime_ns
                or _file_type(current.st_mode) != lease.file_type
                or current.st_nlink != 1
            ):
                raise DistributionApplyError("legacy-marker-unconvertible")
        finally:
            _close_distribution_parent_chain(parent_chain)
        validated.append(lease)
    return tuple(validated)


def execute_recognized_distribution(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    intent: RecognizedDistributionIntent,
    package_version: str,
    legacy_marker: DistributionRetryMarker | None = None,
    generated_assets: tuple[DistributionAsset, ...] = (),
    version_refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None,
    root_identity_path: Path | None = None,
) -> DistributionProcessResult:
    """Execute one recognized update/init-force through the journaled service."""

    store = OperationJournalStore(target_root, identity_path=root_identity_path)
    journal_present = _path_present_no_follow(store.path)
    legacy_present = _path_present_no_follow(target_root / _DISTRIBUTION_RETRY_MARKER_REL)
    journal_seed: OperationJournal | None = None
    guard_marker = legacy_marker
    marker_read_error: DistributionAdmissionError | None = None
    operation_package_version = package_version
    version_refresh_identities = version_refreshable_existing_identities
    terminal_journal_without_guard = False
    if not journal_present and legacy_present and guard_marker is None:
        try:
            guard_marker = _read_distribution_retry_marker(target_root)
        except DistributionAdmissionError as exc:
            marker_read_error = exc
    if not journal_present and guard_marker is not None and guard_marker.purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE:
        operation_package_version = guard_marker.package_version
    if journal_present:
        try:
            journal_seed = store._read(_root_identity_for_assessment(target_root))
            if guard_marker is None:
                try:
                    guard_marker = _read_distribution_retry_marker(target_root)
                except DistributionAdmissionError as exc:
                    raise DistributionApplyError("dual-recovery-state") from exc
            terminal_journal_without_guard = journal_seed.status == "completed" and guard_marker is None
            if not terminal_journal_without_guard and (
                guard_marker is None
                or guard_marker.purpose != _DISTRIBUTION_JOURNAL_GUARD_PURPOSE
                or guard_marker.operation != journal_seed.intent
                or guard_marker.package_version != journal_seed.package_version
                or guard_marker.target_root != journal_seed.root_identity
                or guard_marker.last_completed_phase != "preflight-complete"
                or guard_marker.stage_ownership
            ):
                raise DistributionApplyError("dual-recovery-state")
            if guard_marker is not None:
                store.bind_forward_guard(guard_marker)
                store._assert_guard_anchors_journal(journal_seed)
            operation_package_version = journal_seed.package_version
            journal_version_identity = _journal_version_precondition_identity(journal_seed)
            if journal_version_identity is not None:
                version_refresh_identities = (journal_version_identity,)
        except DistributionApplyError as exc:
            return DistributionProcessResult(
                status="recovery_required",
                intent=intent,
                actions=(),
                reason=str(exc),
            )
    version_asset = _generated_regular_asset(
        "spec-dock/spec-dock.version",
        f"{operation_package_version}\n".encode(),
        mode=0o644,
        refreshable_existing_identities=version_refresh_identities,
    )
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent=intent,
        generated_assets=(version_asset, *generated_assets),
    )
    if marker_read_error is not None:
        return DistributionProcessResult(
            status="recovery_required",
            intent=intent,
            actions=assessment.actions,
            reason="legacy-marker-unconvertible",
        )
    if not journal_present and not legacy_present and assessment.blockers:
        reasons = ", ".join(f"{action.path}: {action.reason}" for action in assessment.blockers)
        return DistributionProcessResult(
            status="blocked",
            intent=intent,
            actions=assessment.actions,
            reason=reasons,
        )
    if (
        not journal_present
        and not legacy_present
        and all(action.action in {"adopt", "preserve"} for action in assessment.actions)
    ):
        return DistributionProcessResult(
            status="completed",
            intent=intent,
            actions=assessment.actions,
            plan_digest=_mutation_plan_digest(assessment),
        )
    plan_digest: str | None = None
    journal: OperationJournal | None = None
    try:
        if legacy_present and guard_marker is None:
            guard_marker = _read_distribution_retry_marker(target_root)
        if (
            journal_present
            and legacy_present
            and (
                journal_seed is None
                or guard_marker is None
                or guard_marker.operation != journal_seed.intent
                or guard_marker.package_version != journal_seed.package_version
                or guard_marker.target_root != journal_seed.root_identity
                or guard_marker.last_completed_phase != "preflight-complete"
                or guard_marker.stage_ownership
            )
        ):
            raise DistributionApplyError("dual-recovery-state")
        if legacy_present:
            if not journal_present:
                executable = build_executable_mutation_plan(assessment)
                plan_digest = executable.plan_digest
                if (
                    guard_marker is None
                    or guard_marker.operation != intent
                    or not _journal_package_is_compatible(guard_marker.package_version, package_version)
                    or guard_marker.target_root != executable.root_identity
                    or guard_marker.last_completed_phase != "preflight-complete"
                ):
                    raise DistributionApplyError("legacy-marker-unconvertible")
                if guard_marker.purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE:
                    if (
                        guard_marker.stage_ownership
                        or guard_marker.operation_id is None
                        or guard_marker.contract_identity != executable.contract_identity
                        or guard_marker.plan_digest != executable.plan_digest
                    ):
                        raise DistributionApplyError("forward-guard-plan-mismatch")
                    store.bind_forward_guard(guard_marker)
                    journal = store.prepare(executable, package_version=guard_marker.package_version)
                else:
                    legacy_stage_leases = _validated_legacy_stage_leases(executable, guard_marker, target_root)
                    guard_marker = store.prepare_legacy_guard(
                        executable,
                        package_version=package_version,
                        replace_marker=guard_marker,
                    )
                    store.bind_forward_guard(guard_marker)
                    journal = store.prepare(executable, package_version=package_version)
                    if legacy_stage_leases:
                        journal = store.write(
                            replace(journal, staging_leases=legacy_stage_leases),
                            predecessor=journal,
                        )
            else:
                assert journal_seed is not None
                journal = store.load_for_assessment(
                    assessment,
                    package_version=package_version,
                    require_guard=not terminal_journal_without_guard,
                )
        elif journal_present:
            journal = store.load_for_assessment(
                assessment,
                package_version=package_version,
                require_guard=not terminal_journal_without_guard,
            )
        if journal_present:
            assert journal is not None
            journal = _reconcile_created_parent_bindings(store, assessment, journal)
            if journal.status == "completed":
                executable = _resume_executable_plan(assessment, journal)
                if assessment.blockers or any(
                    action.action not in {"adopt", "preserve"} for action in assessment.actions
                ):
                    raise DistributionApplyError("distribution postcondition failed")
                if guard_marker is not None:
                    store.remove_legacy_marker(guard_marker)
                store.remove_completed(journal, guard_already_removed=True)
                if journal.package_version != package_version:
                    return execute_recognized_distribution(
                        install_root,
                        manifest_path=manifest_path,
                        scaffold_root=scaffold_root,
                        target_root=target_root,
                        intent=intent,
                        package_version=package_version,
                        generated_assets=generated_assets,
                        version_refreshable_existing_identities=(version_asset.identity,),
                        root_identity_path=root_identity_path,
                    )
                return DistributionProcessResult(
                    status="completed",
                    intent=intent,
                    actions=assessment.actions,
                    plan_digest=journal.plan_digest,
                )
            if journal.status == "verifying":
                executable = _resume_executable_plan(assessment, journal)
                if assessment.blockers or any(
                    action.action not in {"adopt", "preserve"} for action in assessment.actions
                ):
                    raise DistributionApplyError("distribution postcondition failed")
                journal = store.mark_completed(journal)
                if guard_marker is not None:
                    store.remove_legacy_marker(guard_marker)
                store.remove_completed(journal, guard_already_removed=True)
                if journal.package_version != package_version:
                    return execute_recognized_distribution(
                        install_root,
                        manifest_path=manifest_path,
                        scaffold_root=scaffold_root,
                        target_root=target_root,
                        intent=intent,
                        package_version=package_version,
                        generated_assets=generated_assets,
                        version_refreshable_existing_identities=(version_asset.identity,),
                        root_identity_path=root_identity_path,
                    )
                return DistributionProcessResult(
                    status="completed",
                    intent=intent,
                    actions=assessment.actions,
                    plan_digest=journal.plan_digest,
                )
            reconciled = _reconcile_pending_journal_actions(assessment, journal)
            if reconciled != journal:
                journal = store.write(reconciled)
            published_paths = tuple(action.path for action in journal.actions if action.checkpoint == "published")
            if any(lease.path in published_paths for lease in journal.staging_leases):
                journal = store.checkpoint_published(journal, published_paths)
            executable = _resume_executable_plan(assessment, journal)
        elif journal is None:
            executable = build_executable_mutation_plan(assessment)
            guard_marker = store.prepare_legacy_guard(executable, package_version=package_version)
            store.bind_forward_guard(guard_marker)
            journal = store.prepare(executable, package_version=package_version)
        plan_digest = executable.plan_digest
        journal = store.mark_executing(journal)
        active_journal = journal
        refreshed_assessment = build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent=intent,
            generated_assets=(version_asset, *generated_assets),
        )
        refreshed_executable = _resume_executable_plan(refreshed_assessment, journal)

        recorded_completed: tuple[str, ...] = ()

        def record_staging_lease(lease: DistributionStageOwnership) -> None:
            nonlocal active_journal, journal
            active_journal = store.record_staging_lease(active_journal, lease)
            journal = active_journal

        def record_created_parents(bindings: tuple[PathIdentitySnapshot, ...]) -> None:
            nonlocal active_journal, journal
            active_journal = store.record_created_parent_bindings(active_journal, bindings)
            journal = active_journal

        def record_progress(
            _phase: str,
            completed: tuple[str, ...],
            _pending: tuple[str, ...],
            _phase_complete: bool,
        ) -> None:
            nonlocal active_journal, journal, recorded_completed
            if completed == recorded_completed:
                return
            active_journal = store.checkpoint_published(active_journal, completed)
            journal = active_journal
            recorded_completed = completed

        apply_distribution_plan(
            refreshed_executable.distribution_plan,
            allow_stale_stage_cleanup=bool(active_journal.staging_leases),
            stage_ownership=active_journal.staging_leases,
            stage_ownership_recorder=record_staging_lease,
            created_parent_bindings=active_journal.created_parent_bindings,
            created_parent_recorder=record_created_parents,
            write_ahead_stage_reservations=True,
            progress_recorder=record_progress,
        )
        post = build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent=intent,
            generated_assets=(version_asset, *generated_assets),
        )
        if post.blockers or any(action.action not in {"adopt", "preserve"} for action in post.actions):
            raise DistributionApplyError("distribution postcondition failed")
        active_journal = store.mark_verified(active_journal)
        active_journal = store.mark_completed(active_journal)
        if guard_marker is not None:
            store.remove_legacy_marker(guard_marker)
        store.remove_completed(active_journal, guard_already_removed=True)
        journal = active_journal
    except Exception as exc:
        if not isinstance(exc, DistributionApplyError):
            reason = "generated-state-reconciliation-failed"
        else:
            reason = str(exc)
            sensitive_paths = tuple(
                str(path) for path in (install_root, scaffold_root, target_root) if path.is_absolute()
            )
            if (
                any(path in reason for path in sensitive_paths)
                or "credential=" in reason.lower()
                or re.search(r"(?:^|[\s=])/", reason) is not None
            ):
                reason = "distribution-apply-failed"
        return DistributionProcessResult(
            status="recovery_required",
            intent=intent,
            actions=assessment.actions,
            plan_digest=plan_digest,
            reason=reason,
            applied_paths=(
                tuple(action.path for action in journal.actions if action.checkpoint != "pending")
                if journal is not None
                else ()
            ),
            pending_paths=(
                tuple(action.path for action in journal.actions if action.checkpoint == "pending")
                if journal is not None
                else ()
            ),
        )
    if operation_package_version != package_version:
        return execute_recognized_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent=intent,
            package_version=package_version,
            generated_assets=generated_assets,
            version_refreshable_existing_identities=(version_asset.identity,),
            root_identity_path=root_identity_path,
        )
    return DistributionProcessResult(
        status="completed",
        intent=intent,
        actions=assessment.actions,
        plan_digest=executable.plan_digest,
    )


def _distribution_directory_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if not isinstance(nofollow, int) or not isinstance(directory, int):
        raise DistributionApplyError("platform lacks required no-follow directory support")
    return os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0)


def _open_distribution_parent_chain(
    target_root: Path,
    target_rel: str,
    *,
    create_missing: bool = False,
    expected_snapshot: DistributionTargetSnapshot | None = None,
    created_parent_bindings: dict[str, PathIdentitySnapshot] | None = None,
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None = None,
) -> tuple[int, ...]:
    flags = _distribution_directory_flags()
    fds: list[int] = []
    created_missing = False
    try:
        fds.append(os.open(target_root, flags))
        if expected_snapshot is not None:
            _assert_distribution_chain_bound(
                tuple(fds),
                expected_snapshot,
                target_rel,
                exact=not created_missing,
            )
        parts = PurePosixPath(target_rel).parts
        for component_index, component in enumerate(parts[:-1]):
            created_component = False
            component_relative = "/".join(parts[: component_index + 1])
            expected_parent = None
            if expected_snapshot is not None:
                expected_parent = next(
                    (parent for parent in expected_snapshot.parents if parent.relative_path == component_relative),
                    None,
                )
            try:
                next_fd = os.open(component, flags, dir_fd=fds[-1])
                if expected_parent is not None and not expected_parent.exists:
                    bound_parent = (
                        created_parent_bindings.get(component_relative) if created_parent_bindings is not None else None
                    )
                    if (
                        bound_parent is None
                        or not bound_parent.exists
                        or not _same_stat_structure(os.fstat(next_fd), bound_parent)
                    ):
                        os.close(next_fd)
                        raise DistributionApplyError(f"managed target parent appeared during apply for '{target_rel}'")
            except FileNotFoundError:
                if not create_missing:
                    raise DistributionApplyError(f"managed target parent is missing for '{target_rel}'") from None
                if expected_snapshot is not None:
                    _assert_distribution_chain_bound(
                        tuple(fds),
                        expected_snapshot,
                        target_rel,
                        exact=not created_missing,
                    )
                _assert_visible_distribution_chain_bound(target_root, target_rel, tuple(fds))
                try:
                    os.mkdir(component, dir_fd=fds[-1])
                except FileExistsError:
                    if expected_parent is not None and not expected_parent.exists:
                        raise DistributionApplyError(
                            f"managed target parent appeared during apply for '{target_rel}'"
                        ) from None
                else:
                    os.fsync(fds[-1])
                    created_missing = True
                    created_component = True
                next_fd = os.open(component, flags, dir_fd=fds[-1])
            except OSError as exc:
                raise DistributionApplyError(f"managed target parent is unsafe for '{target_rel}'") from exc
            fds.append(next_fd)
            _assert_visible_distribution_chain_bound(target_root, target_rel, tuple(fds))
            if created_component and created_parent_bindings is not None:
                created_parent_bindings[component_relative] = _snapshot_from_stat(
                    component_relative,
                    os.fstat(next_fd),
                )
                if created_parent_recorder is not None:
                    created_parent_recorder(
                        tuple(created_parent_bindings[path] for path in sorted(created_parent_bindings))
                    )
            if expected_snapshot is not None:
                _assert_distribution_chain_bound(
                    tuple(fds),
                    expected_snapshot,
                    target_rel,
                    exact=not created_missing,
                )
        return tuple(fds)
    except DistributionApplyError:
        for fd in reversed(fds):
            os.close(fd)
        raise
    except OSError as exc:
        for fd in reversed(fds):
            os.close(fd)
        raise DistributionApplyError("managed target root cannot be opened safely") from exc


def _close_distribution_parent_chain(fds: tuple[int, ...]) -> None:
    for fd in reversed(fds):
        os.close(fd)


def _same_stat_identity(left: os.stat_result, right: PathIdentitySnapshot) -> bool:
    return (
        right.exists
        and left.st_dev == right.device
        and left.st_ino == right.inode
        and left.st_ctime_ns == right.ctime_ns
        and _file_type(left.st_mode) == right.file_type
        and left.st_nlink == right.link_count
    )


def _same_stat_structure(left: os.stat_result, right: PathIdentitySnapshot) -> bool:
    return (
        right.exists
        and left.st_dev == right.device
        and left.st_ino == right.inode
        and _file_type(left.st_mode) == right.file_type
    )


def _assert_distribution_chain_bound(
    fds: tuple[int, ...],
    snapshot: DistributionTargetSnapshot,
    target_rel: str,
    *,
    exact: bool = False,
) -> None:
    if not snapshot.root.exists:
        raise DistributionApplyError(f"managed target identity changed for '{target_rel}'")
    root_matches = (
        _same_stat_identity(os.fstat(fds[0]), snapshot.root)
        if exact
        else _same_stat_structure(os.fstat(fds[0]), snapshot.root)
    )
    if not root_matches:
        raise DistributionApplyError(f"managed target identity changed for '{target_rel}'")
    for fd, expected in zip(fds[1:], snapshot.parents, strict=False):
        if not expected.exists:
            continue
        parent_matches = (
            _same_stat_identity(os.fstat(fd), expected) if exact else _same_stat_structure(os.fstat(fd), expected)
        )
        if not parent_matches:
            raise DistributionApplyError(f"managed target identity changed for '{target_rel}'")


def _assert_visible_distribution_chain_bound(
    target_root: Path,
    target_rel: str,
    fds: tuple[int, ...],
) -> None:
    parts = PurePosixPath(target_rel).parts
    for index, fd in enumerate(fds):
        visible = target_root.joinpath(*parts[:index]) if index else target_root
        try:
            visible_stat = os.lstat(visible)
            held_stat = os.fstat(fd)
        except OSError as exc:
            raise DistributionApplyError(f"managed target identity changed for '{target_rel}'") from exc
        if (
            visible_stat.st_dev != held_stat.st_dev
            or visible_stat.st_ino != held_stat.st_ino
            or _file_type(visible_stat.st_mode) != _file_type(held_stat.st_mode)
        ):
            raise DistributionApplyError(f"managed target identity changed for '{target_rel}'")


def _assert_regular_fd_safe(
    fd: int,
    snapshot: PathIdentitySnapshot,
    path: str,
    *,
    exact: bool,
) -> None:
    actual = os.fstat(fd)
    matches = _same_stat_identity(actual, snapshot) if exact else _same_stat_structure(actual, snapshot)
    if not matches or actual.st_nlink != 1:
        raise DistributionApplyError(f"managed target identity changed for '{path}'")


def _read_fd_bytes(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(fd, 1024 * 64)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _held_fd_has_exact_bytes(fd: int, expected: bytes) -> bool:
    before = os.fstat(fd)
    content = _read_fd_bytes(fd)
    after = os.fstat(fd)
    return _stat_identity_tuple(before) == _stat_identity_tuple(after) and content == expected


def _source_snapshot(info: os.stat_result) -> DistributionSourceSnapshot:
    return DistributionSourceSnapshot(
        device=info.st_dev,
        inode=info.st_ino,
        ctime_ns=info.st_ctime_ns,
        mtime_ns=info.st_mtime_ns,
        size=info.st_size,
        mode=stat.S_IMODE(info.st_mode),
    )


def _source_asset_bytes(source_path: Path) -> tuple[bytes, DistributionSourceSnapshot]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        raise DistributionApplyError("platform lacks required no-follow file support")
    try:
        source_stat = os.lstat(source_path)
        if not stat.S_ISREG(source_stat.st_mode):
            raise DistributionApplyError("provider Current asset is not a regular file")
        fd = os.open(source_path, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0))
    except DistributionApplyError:
        raise
    except OSError as exc:
        raise DistributionApplyError("provider Current asset cannot be read safely") from exc
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise DistributionApplyError("provider Current asset changed type")
        if _source_snapshot(source_stat) != _source_snapshot(opened):
            raise DistributionApplyError("provider Current asset identity changed before read")
        content = _read_fd_bytes(fd)
        after_read = os.fstat(fd)
        snapshot = _source_snapshot(after_read)
        if snapshot != _source_snapshot(opened):
            raise DistributionApplyError("provider Current asset identity changed during read")
        return content, snapshot
    finally:
        os.close(fd)


def _write_fd_bytes(
    fd: int,
    content: bytes,
    *,
    before_mutation: Callable[[], None] | None = None,
) -> None:
    if before_mutation is not None:
        before_mutation()
    os.ftruncate(fd, 0)
    os.lseek(fd, 0, os.SEEK_SET)
    view = memoryview(content)
    offset = 0
    while offset < len(view):
        if before_mutation is not None:
            before_mutation()
        written = os.write(fd, view[offset:])
        if written <= 0:
            raise DistributionApplyError("managed target write made no progress")
        offset += written
    os.fsync(fd)


def _resolve_distribution_no_replace_rename() -> tuple[Any, int]:
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux"):
        rename = getattr(library, "renameat2", None)
        flag = 0x00000001  # RENAME_NOREPLACE
    elif sys.platform == "darwin":
        rename = getattr(library, "renameatx_np", None)
        flag = 0x00000004  # RENAME_EXCL
    else:
        raise DistributionApplyError("platform lacks required no-replace rename support")
    if rename is None:
        raise DistributionApplyError("platform lacks required no-replace rename support")
    rename.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    rename.restype = ctypes.c_int
    return rename, flag


def _rename_distribution_no_replace(
    source_parent_fd: int,
    source_name: str,
    destination_parent_fd: int,
    destination_name: str,
) -> None:
    rename, flag = _resolve_distribution_no_replace_rename()
    result = rename(
        source_parent_fd,
        os.fsencode(source_name),
        destination_parent_fd,
        os.fsencode(destination_name),
        flag,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number in (errno.EEXIST, errno.ENOTEMPTY):
        raise FileExistsError(error_number, os.strerror(error_number), destination_name)
    raise OSError(error_number, os.strerror(error_number), destination_name)


def _resolve_distribution_swap_rename() -> tuple[Any, int]:
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux"):
        rename = getattr(library, "renameat2", None)
        flag = 0x00000002  # RENAME_EXCHANGE
    elif sys.platform == "darwin":
        rename = getattr(library, "renameatx_np", None)
        flag = 0x00000002  # RENAME_SWAP
    else:
        raise DistributionApplyError("platform lacks required atomic replace support")
    if rename is None:
        raise DistributionApplyError("platform lacks required atomic replace support")
    rename.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    rename.restype = ctypes.c_int
    return rename, flag


def _rename_distribution_swap(
    source_parent_fd: int,
    source_name: str,
    destination_parent_fd: int,
    destination_name: str,
) -> None:
    rename, flag = _resolve_distribution_swap_rename()
    result = rename(
        source_parent_fd,
        os.fsencode(source_name),
        destination_parent_fd,
        os.fsencode(destination_name),
        flag,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    raise OSError(error_number, os.strerror(error_number), destination_name)


def _stat_identity_tuple(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_ctime_ns, info.st_mode, info.st_nlink)


def _stat_structure_tuple(info: os.stat_result) -> tuple[int, int, str, int]:
    return (info.st_dev, info.st_ino, _file_type(info.st_mode), info.st_nlink)


def _restore_distribution_quarantine(
    parent_fd: int,
    quarantine_name: str,
    target_name: str,
    *,
    failure_message: str,
) -> None:
    try:
        _rename_distribution_no_replace(parent_fd, quarantine_name, parent_fd, target_name)
        os.fsync(parent_fd)
    except OSError as exc:
        raise DistributionApplyError(failure_message) from exc


def _remove_distribution_target_if_bound(
    parent_fd: int,
    target_name: str,
    expected: os.stat_result,
    *,
    held_fd: int | None = None,
    identity_message: str,
    transition_path: str | None = None,
    transition_name: str | None = None,
    transition_recorder: Callable[[DistributionStageOwnership], None] | None = None,
) -> None:
    """Delete only the inode bound before the pathname mutation.

    A nonce quarantine turns a concurrent replacement into a reversible move:
    the moved entry is compared with the held descriptor (or the exact
    no-follow symlink identity) before any unlink is attempted.
    """

    expected_identity = _stat_identity_tuple(expected)
    if held_fd is not None and _stat_identity_tuple(os.fstat(held_fd)) != expected_identity:
        raise DistributionApplyError(identity_message)
    quarantine_name = transition_name or f".{target_name}.{secrets.token_hex(16)}.remove"
    if transition_recorder is not None:
        if transition_path is None:
            raise DistributionApplyError(identity_message)
        file_type = _file_type(expected.st_mode)
        if file_type not in {"regular", "symlink"}:
            raise DistributionApplyError(identity_message)
        transition_recorder(
            _reserved_distribution_stage_ownership(
                transition_path,
                quarantine_name,
                "regular" if file_type == "regular" else "symlink",
            )
        )
    try:
        _rename_distribution_no_replace(parent_fd, target_name, parent_fd, quarantine_name)
    except OSError as exc:
        raise DistributionApplyError(identity_message) from exc
    try:
        moved = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
        bound_identity = _stat_identity_tuple(os.fstat(held_fd)) if held_fd is not None else expected_identity
        if _stat_identity_tuple(moved) != bound_identity:
            _restore_distribution_quarantine(
                parent_fd,
                quarantine_name,
                target_name,
                failure_message=identity_message,
            )
            raise DistributionApplyError(identity_message)
        os.fsync(parent_fd)
        if transition_recorder is not None:
            assert transition_path is not None
            transition_recorder(_distribution_stage_ownership(transition_path, quarantine_name, moved))
        try:
            _remove_distribution_stage_if_owned(parent_fd, quarantine_name, moved, strict=True)
        except DistributionApplyError as exc:
            _restore_distribution_quarantine(
                parent_fd,
                quarantine_name,
                target_name,
                failure_message=identity_message,
            )
            raise DistributionApplyError(identity_message) from exc
    except Exception:
        raise


def _swap_regular_distribution_target_if_bound(
    parent_fd: int,
    staging_name: str,
    target_name: str,
    *,
    target_fd: int,
    staging_fd: int,
    expected_target: os.stat_result,
    identity_message: str,
) -> os.stat_result:
    """Exchange two held regular files and roll back a raced pathname."""

    if _stat_identity_tuple(os.fstat(target_fd)) != _stat_identity_tuple(expected_target):
        raise DistributionApplyError(identity_message)
    visible_target = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
    visible_stage = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
    if _stat_identity_tuple(visible_target) != _stat_identity_tuple(expected_target) or _stat_identity_tuple(
        visible_stage
    ) != _stat_identity_tuple(os.fstat(staging_fd)):
        raise DistributionApplyError(identity_message)
    _rename_distribution_swap(parent_fd, staging_name, parent_fd, target_name)
    os.fsync(parent_fd)
    moved_target = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
    published = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
    if _stat_identity_tuple(moved_target) != _stat_identity_tuple(os.fstat(target_fd)) or _stat_identity_tuple(
        published
    ) != _stat_identity_tuple(os.fstat(staging_fd)):
        if _stat_identity_tuple(published) == _stat_identity_tuple(os.fstat(staging_fd)):
            # The canonical predecessor changed before the exchange: the
            # exact successor is canonical and the unknown entry is at stage.
            # Re-check that pair and exchange it back so the unknown entry
            # returns to its original canonical name.
            rollback_target = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
            rollback_stage = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            if _stat_identity_tuple(rollback_target) != _stat_identity_tuple(published) or _stat_identity_tuple(
                rollback_stage
            ) != _stat_identity_tuple(moved_target):
                raise DistributionApplyError(identity_message)
            _rename_distribution_swap(parent_fd, staging_name, parent_fd, target_name)
            os.fsync(parent_fd)
            restored_target = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
            restored_stage = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            if _stat_identity_tuple(restored_target) != _stat_identity_tuple(moved_target) or _stat_identity_tuple(
                restored_stage
            ) != _stat_identity_tuple(published):
                raise DistributionApplyError(identity_message)
        # The exchange already happened.  An unknown canonical entry may have
        # been published after it, so exchanging again would move or delete a
        # third-party entry.  Preserve both names for journaled recovery.
        raise DistributionApplyError(identity_message)
    return moved_target


def _swap_symlink_distribution_target_if_bound(
    parent_fd: int,
    staging_name: str,
    target_name: str,
    *,
    expected_target: PathIdentitySnapshot,
    staging_stat: os.stat_result,
    identity_message: str,
) -> os.stat_result:
    """Exchange symlinks and restore both names when a pathname raced."""

    def read_exact_symlink(name: str) -> tuple[os.stat_result, str]:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISLNK(before.st_mode) or before.st_nlink != 1:
            raise DistributionApplyError(identity_message)
        try:
            link_target = _normalized_link_target_for_path(
                expected_target.relative_path,
                os.readlink(name, dir_fd=parent_fd),
            )
        except OSError as exc:
            raise DistributionApplyError(identity_message) from exc
        after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if _stat_identity_tuple(after) != _stat_identity_tuple(before):
            raise DistributionApplyError(identity_message)
        if link_target is None:
            raise DistributionApplyError(identity_message)
        return after, link_target

    expected_predecessor_target = (
        expected_target.identity.target
        if expected_target.identity is not None and expected_target.identity.kind == "symlink"
        else None
    )
    if expected_predecessor_target is None:
        raise DistributionApplyError(identity_message)

    visible_target, visible_target_link = read_exact_symlink(target_name)
    visible_stage, visible_stage_link = read_exact_symlink(staging_name)
    staged_target = visible_stage_link
    if (
        not _same_stat_identity(visible_target, expected_target)
        or visible_target_link != expected_predecessor_target
        or _stat_identity_tuple(visible_stage) != _stat_identity_tuple(staging_stat)
        or visible_stage_link != staged_target
    ):
        raise DistributionApplyError(identity_message)
    _rename_distribution_swap(parent_fd, staging_name, parent_fd, target_name)
    os.fsync(parent_fd)
    moved_target, moved_target_link = read_exact_symlink(staging_name)
    published, published_link = read_exact_symlink(target_name)
    if (
        not _same_stat_structure(moved_target, expected_target)
        or moved_target.st_nlink != expected_target.link_count
        or moved_target_link != expected_predecessor_target
        or _stat_structure_tuple(published) != _stat_structure_tuple(staging_stat)
        or published_link != staged_target
    ):
        published_is_exact_successor = (
            _stat_structure_tuple(published) == _stat_structure_tuple(staging_stat) and published_link == staged_target
        )
        if published_is_exact_successor:
            rollback_target, rollback_target_link = read_exact_symlink(target_name)
            rollback_stage, rollback_stage_link = read_exact_symlink(staging_name)
            if (
                _stat_identity_tuple(rollback_target) != _stat_identity_tuple(published)
                or rollback_target_link != published_link
                or _stat_identity_tuple(rollback_stage) != _stat_identity_tuple(moved_target)
                or rollback_stage_link != moved_target_link
            ):
                raise DistributionApplyError(identity_message)
            _rename_distribution_swap(parent_fd, staging_name, parent_fd, target_name)
            os.fsync(parent_fd)
            restored_target, restored_target_link = read_exact_symlink(target_name)
            restored_stage, restored_stage_link = read_exact_symlink(staging_name)
            if (
                _stat_identity_tuple(restored_target) != _stat_identity_tuple(moved_target)
                or restored_target_link != moved_target_link
                or _stat_identity_tuple(restored_stage) != _stat_identity_tuple(published)
                or restored_stage_link != published_link
            ):
                raise DistributionApplyError(identity_message)
        # Never roll an unknown post-exchange canonical entry through the
        # private stage name.  The journal owns recovery; both entries remain.
        raise DistributionApplyError(identity_message)
    return moved_target


def _remove_distribution_stage_if_owned(
    parent_fd: int,
    stage_name: str,
    created: os.stat_result,
    *,
    strict: bool = False,
) -> None:
    try:
        current = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        if strict:
            raise DistributionApplyError("managed staging cleanup failed") from exc
        return
    owned = (
        current.st_dev == created.st_dev
        and current.st_ino == created.st_ino
        and current.st_ctime_ns == created.st_ctime_ns
        and _file_type(current.st_mode) == _file_type(created.st_mode)
        and current.st_nlink == created.st_nlink == 1
    )
    if not owned:
        if strict:
            raise DistributionApplyError("managed staging identity changed")
        return
    try:
        os.unlink(stage_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    except FileNotFoundError:
        return
    except OSError as exc:
        if strict:
            raise DistributionApplyError("managed staging cleanup failed") from exc


def _distribution_stage_identity(parent_fd: int, stage_name: str, path: str) -> DistributionIdentity | None:
    """Read a private stage identity without following its final path."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        raise DistributionApplyError("platform lacks required no-follow file support")
    try:
        info = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise DistributionApplyError("managed staging artifact cannot be inspected safely") from exc
    if info.st_nlink != 1:
        return None
    kind = _file_type(info.st_mode)
    if kind == "regular":
        try:
            fd = os.open(stage_name, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd)
        except OSError as exc:
            raise DistributionApplyError("managed staging artifact cannot be opened safely") from exc
        try:
            opened = os.fstat(fd)
            if (
                opened.st_dev != info.st_dev
                or opened.st_ino != info.st_ino
                or opened.st_ctime_ns != info.st_ctime_ns
                or opened.st_nlink != 1
                or not stat.S_ISREG(opened.st_mode)
            ):
                raise DistributionApplyError("managed staging identity changed")
            return DistributionIdentity(
                kind="regular",
                sha256=hashlib.sha256(_read_fd_bytes(fd)).hexdigest(),
                mode=stat.S_IMODE(opened.st_mode),
            )
        finally:
            os.close(fd)
    if kind == "symlink":
        try:
            target = os.readlink(stage_name, dir_fd=parent_fd)
        except OSError as exc:
            raise DistributionApplyError("managed staging symlink cannot be read safely") from exc
        normalized = _normalized_link_target_for_path(path, target)
        if normalized is None:
            raise DistributionApplyError("managed staging symlink target is unsafe")
        return DistributionIdentity(kind="symlink", target=normalized)
    return None


def _distribution_stage_ownership(
    path: str,
    stage_name: str,
    info: os.stat_result,
) -> DistributionStageOwnership:
    kind = _file_type(info.st_mode)
    if kind not in {"regular", "symlink"} or info.st_nlink != 1:
        raise DistributionApplyError("managed staging artifact is not safe to record")
    file_type: Literal["regular", "symlink"] = "regular" if kind == "regular" else "symlink"
    return DistributionStageOwnership(
        path=path,
        stage_name=stage_name,
        device=info.st_dev,
        inode=info.st_ino,
        ctime_ns=info.st_ctime_ns,
        file_type=file_type,
    )


def _reserved_distribution_stage_ownership(
    path: str,
    stage_name: str,
    file_type: Literal["regular", "symlink"],
) -> DistributionStageOwnership:
    """Persist a private stage name before its namespace entry is created."""

    return DistributionStageOwnership(
        path=path,
        stage_name=stage_name,
        device=0,
        inode=0,
        ctime_ns=0,
        file_type=file_type,
    )


def _distribution_stage_name(path: str, identity: DistributionIdentity) -> str:
    """Return the stable prefix for private stages owned by one planned target."""
    if identity.kind == "regular":
        identity_key = f"regular:{identity.sha256}"
        prefix = ".spec-dock-file-"
    else:
        identity_key = f"symlink:{identity.target}"
        prefix = ".spec-dock-symlink-"
    digest = hashlib.sha256(f"{path}\0{identity_key}".encode()).hexdigest()[:24]
    return f"{prefix}{digest}"


def _new_distribution_stage_name(path: str, identity: DistributionIdentity) -> str:
    """Return an attempt-unique stage name so an unleased crash cannot reserve the next attempt."""

    return f"{_distribution_stage_name(path, identity)}-{secrets.token_hex(16)}"


def _matches_distribution_stage_name(name: str, path: str, identity: DistributionIdentity) -> bool:
    prefix = _distribution_stage_name(path, identity)
    return name == prefix or name.startswith(f"{prefix}-")


def _historical_stage_identities(plan: DistributionPlan, path: str) -> tuple[DistributionIdentity, ...]:
    identities: list[DistributionIdentity] = []
    for record in _historical_records(plan.manifest):
        if record["path"] != path:
            continue
        if record["kind"] == "regular":
            identities.append(
                DistributionIdentity(
                    kind="regular",
                    sha256=record["sha256"],
                    mode=record.get("mode"),
                )
            )
        else:
            identities.append(DistributionIdentity(kind="symlink", target=record["target"]))
    return tuple(identities)


def _cleanup_stale_distribution_stages(
    plan: DistributionPlan,
    target_root: Path,
    action: DistributionAction,
    snapshot: DistributionTargetSnapshot,
    stage_ownership: tuple[DistributionStageOwnership, ...],
) -> None:
    """Retry cleanup of private stages recorded by an earlier failed apply."""
    if action.action not in {"create", "adopt", "upgrade", "prune"}:
        return
    expected = _expected_target_identity(plan, action.path)
    historical = _historical_stage_identities(plan, action.path)
    if expected is None and not historical:
        return
    try:
        parent_chain = _open_distribution_parent_chain(
            target_root,
            action.path,
            create_missing=False,
            expected_snapshot=snapshot,
        )
    except DistributionApplyError as exc:
        if "parent is missing" in str(exc):
            return
        raise
    try:
        parent_fd = parent_chain[-1]
        try:
            names = os.listdir(parent_fd)  # noqa: PTH208 - descriptor-relative scan is required for no-follow safety
        except OSError as exc:
            raise DistributionApplyError("managed staging directory cannot be listed safely") from exc
        known_identities = tuple(item for item in (expected, *historical) if item is not None)
        mismatch_detected = False
        cleaned = False
        for owned in stage_ownership:
            if owned.path != action.path or owned.stage_name not in names:
                continue
            if not any(
                _matches_distribution_stage_name(owned.stage_name, action.path, identity)
                for identity in known_identities
            ):
                continue
            try:
                current = os.stat(owned.stage_name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise DistributionApplyError("managed staging artifact cannot be inspected safely") from exc
            if owned.device == owned.inode == owned.ctime_ns == 0:
                if _file_type(current.st_mode) != owned.file_type or current.st_nlink != 1:
                    mismatch_detected = True
                    continue
                _remove_distribution_stage_if_owned(
                    parent_fd,
                    owned.stage_name,
                    current,
                    strict=True,
                )
                cleaned = True
                continue
            if (
                current.st_dev != owned.device
                or current.st_ino != owned.inode
                or current.st_ctime_ns != owned.ctime_ns
                or _file_type(current.st_mode) != owned.file_type
                or current.st_nlink != 1
            ):
                mismatch_detected = True
                continue
            candidate = _distribution_stage_identity(parent_fd, owned.stage_name, owned.path)
            if candidate is None:
                mismatch_detected = True
                continue
            # The retry marker's exact no-follow device/inode/ctime identity
            # proves ownership of this private stage.  Its payload may be
            # partial after a failed write, so requiring a known package
            # digest here would strand the same-package retry.  Content and
            # ownership checks still apply to ordinary target mutations.
            try:
                os.unlink(owned.stage_name, dir_fd=parent_fd)
                os.fsync(parent_fd)
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise DistributionApplyError("managed staging cleanup failed") from exc
            cleaned = True
        if mismatch_detected and not cleaned:
            raise DistributionApplyError("managed staging identity changed")
    finally:
        _close_distribution_parent_chain(parent_chain)


def _expected_target_identity(plan: DistributionPlan, path: str) -> DistributionIdentity | None:
    return _target_identity_specs(plan.current_assets, plan.scaffold_assets).get(path)


def _asset_for_target(plan: DistributionPlan, path: str) -> DistributionAsset | None:
    for asset in (*plan.current_assets, *plan.scaffold_assets):
        target_path = asset.path
        if target_path == path:
            return asset
    return None


def _plan_snapshot_map(plan: DistributionPlan) -> dict[str, DistributionTargetSnapshot]:
    return dict(plan.target_snapshots)


def _assert_plan_target_snapshot(
    target_root: Path,
    path: str,
    expected: DistributionTargetSnapshot,
) -> _TargetObservation:
    observation = _observe_target(target_root, path)
    if observation.snapshot != expected:
        raise DistributionApplyError(f"managed target identity changed for '{path}'")
    return observation


def _same_structure_identity(actual: PathIdentitySnapshot, expected: PathIdentitySnapshot) -> bool:
    if not expected.exists or not actual.exists:
        return actual.exists == expected.exists
    return (
        actual.device == expected.device and actual.inode == expected.inode and actual.file_type == expected.file_type
    )


def _assert_pending_snapshot_stable(
    actual: DistributionTargetSnapshot,
    expected: DistributionTargetSnapshot,
    path: str,
    created_parent_bindings: dict[str, PathIdentitySnapshot],
) -> None:
    if not _same_structure_identity(actual.root, expected.root):
        raise DistributionApplyError(f"managed target identity changed for '{path}'")
    actual_parents = {parent.relative_path: parent for parent in actual.parents}
    for expected_parent in expected.parents:
        actual_parent = actual_parents.get(
            expected_parent.relative_path, _missing_snapshot(expected_parent.relative_path)
        )
        if expected_parent.exists:
            if not _same_structure_identity(actual_parent, expected_parent):
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
        elif actual_parent.exists:
            bound_parent = created_parent_bindings.get(expected_parent.relative_path)
            if bound_parent is None or not bound_parent.exists:
                # A parent that was absent during preflight may only become
                # acceptable after this operation creates and binds it through
                # `_bind_created_parent_identities`.  Accepting an unbound
                # inode here would turn a user- or concurrently-created
                # directory into an operation-owned parent after preflight.
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
            if actual_parent.file_type != "directory" or not _same_structure_identity(actual_parent, bound_parent):
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
    if actual.target != expected.target:
        raise DistributionApplyError(f"managed target identity changed for '{path}'")


def _bind_created_parent_identities(
    target_rel: str,
    snapshot: DistributionTargetSnapshot,
    parent_chain: tuple[int, ...],
    created_parent_bindings: dict[str, PathIdentitySnapshot],
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None = None,
) -> None:
    changed = False
    for index, expected_parent in enumerate(snapshot.parents, start=1):
        bound_parent = created_parent_bindings.get(expected_parent.relative_path)
        if index >= len(parent_chain) or (expected_parent.exists and (bound_parent is None or bound_parent.exists)):
            continue
        current = _snapshot_from_stat(
            expected_parent.relative_path,
            os.fstat(parent_chain[index]),
        )
        if bound_parent is None or not bound_parent.exists:
            created_parent_bindings[expected_parent.relative_path] = current
            changed = True
        elif not _same_structure_identity(current, bound_parent):
            raise DistributionApplyError(f"managed target identity changed for '{target_rel}'")
    if changed and created_parent_recorder is not None:
        created_parent_recorder(tuple(created_parent_bindings[path] for path in sorted(created_parent_bindings)))


def _apply_regular_action(
    *,
    target_root: Path,
    action: DistributionAction,
    snapshot: DistributionTargetSnapshot,
    expected: DistributionIdentity,
    source_bytes: bytes | None,
    source_mode: int | None,
    created_parent_bindings: dict[str, PathIdentitySnapshot],
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None,
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None,
    write_ahead_stage_reservations: bool,
) -> None:
    path = action.path
    if action.action == "prune" and not snapshot.target.exists:
        return
    parent_chain = _open_distribution_parent_chain(
        target_root,
        path,
        create_missing=action.action == "create",
        expected_snapshot=snapshot,
        created_parent_bindings=created_parent_bindings,
        created_parent_recorder=created_parent_recorder,
    )
    try:
        _assert_distribution_chain_bound(parent_chain, snapshot, path)
        _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
        _bind_created_parent_identities(
            path,
            snapshot,
            parent_chain,
            created_parent_bindings,
            created_parent_recorder,
        )
        parent_fd = parent_chain[-1]
        target_name = PurePosixPath(path).name
        try:
            target_stat = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
            target_exists = True
        except FileNotFoundError:
            target_stat = None
            target_exists = False

        if action.action == "create":
            if target_exists:
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
            if expected.kind != "regular" or source_bytes is None or source_mode is None:
                raise DistributionApplyError(f"unsupported managed create action for '{path}'")
            _resolve_distribution_no_replace_rename()
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise DistributionApplyError("platform lacks required no-follow file support")
            staging_name = _new_distribution_stage_name(path, expected)
            if write_ahead_stage_reservations and stage_ownership_recorder is not None:
                stage_ownership_recorder(_reserved_distribution_stage_ownership(path, staging_name, "regular"))
            fd = os.open(
                staging_name,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                source_mode,
                dir_fd=parent_fd,
            )
            created = os.fstat(fd)
            stage_identity = created
            try:
                if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
                    raise DistributionApplyError(f"managed target is unsafe for '{path}'")
                if stage_ownership_recorder is not None and not write_ahead_stage_reservations:
                    stage_ownership_recorder(_distribution_stage_ownership(path, staging_name, created))
                mutation_phase = "pre"

                def check_before_write() -> None:
                    nonlocal mutation_phase
                    _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                    current = os.fstat(fd)
                    if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
                        raise DistributionApplyError(f"managed target identity changed for '{path}'")
                    mutation_phase = "post"

                _write_fd_bytes(fd, source_bytes, before_mutation=check_before_write)
                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                if os.fstat(fd).st_nlink != 1:
                    raise DistributionApplyError(f"managed target identity changed for '{path}'")
                os.fchmod(fd, source_mode)
                verified = os.fstat(fd)
                if (
                    verified.st_nlink != 1
                    or stat.S_IMODE(verified.st_mode) != source_mode
                    or hashlib.sha256(_read_fd_bytes(fd)).hexdigest() != expected.sha256
                ):
                    raise DistributionApplyError(f"managed target verification failed for '{path}'")
                stage_identity = verified
                if write_ahead_stage_reservations and stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(path, staging_name, verified))
                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                _rename_distribution_no_replace(parent_fd, staging_name, parent_fd, target_name)
                os.fsync(parent_fd)
            finally:
                with suppress(OSError):
                    stage_identity = os.fstat(fd)
                try:
                    # A failed write may mutate the stage before raising.  The
                    # creation-time stat is then stale (ctime changes), so
                    # refresh and publish the no-follow identity before
                    # attempting ownership-checked cleanup.  The refreshed
                    # marker lets the next same-package retry identify a
                    # partial stage even when cleanup fails here.
                    if stage_ownership_recorder is not None and not write_ahead_stage_reservations:
                        stage_ownership_recorder(_distribution_stage_ownership(path, staging_name, stage_identity))
                finally:
                    try:
                        os.close(fd)
                    finally:
                        _remove_distribution_stage_if_owned(
                            parent_fd,
                            staging_name,
                            stage_identity,
                            strict=True,
                        )
            published_fd = os.open(target_name, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd)
            try:
                published = os.fstat(published_fd)
                if (
                    published.st_nlink != 1
                    or stat.S_IMODE(published.st_mode) != source_mode
                    or hashlib.sha256(_read_fd_bytes(published_fd)).hexdigest() != expected.sha256
                ):
                    raise DistributionApplyError(f"managed target verification failed for '{path}'")
            finally:
                os.close(published_fd)
            return

        if not target_exists or target_stat is None:
            if action.action == "prune":
                return
            raise DistributionApplyError(f"managed target identity changed for '{path}'")

        if expected.kind != "regular":
            raise DistributionApplyError(f"unsupported regular managed action for '{path}'")
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if not isinstance(nofollow, int):
            raise DistributionApplyError("platform lacks required no-follow file support")
        flags = os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0)
        fd = os.open(target_name, flags, dir_fd=parent_fd)
        try:
            opened = os.fstat(fd)
            if not _same_stat_identity(opened, snapshot.target) or opened.st_nlink != 1:
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
            if action.action == "prune":
                target_identity = snapshot.target.identity
                if target_identity is None or target_identity.kind != "regular":
                    raise DistributionApplyError(f"managed target identity changed for '{path}'")
                if hashlib.sha256(_read_fd_bytes(fd)).hexdigest() != target_identity.sha256:
                    raise DistributionApplyError(f"managed target identity changed for '{path}'")
                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                _assert_regular_fd_safe(fd, snapshot.target, path, exact=True)
                _remove_distribution_target_if_bound(
                    parent_fd,
                    target_name,
                    opened,
                    held_fd=fd,
                    identity_message=f"managed target identity changed for '{path}'",
                    transition_path=path,
                    transition_name=_new_distribution_stage_name(path, target_identity),
                    transition_recorder=(stage_ownership_recorder if write_ahead_stage_reservations else None),
                )
                return
            if action.action != "upgrade":
                raise DistributionApplyError(f"unsupported regular action for '{path}'")
            if source_bytes is None or source_mode is None:
                raise DistributionApplyError(f"missing provider bytes for '{path}'")
            _assert_regular_fd_safe(fd, snapshot.target, path, exact=True)
            target_identity = snapshot.target.identity
            if target_identity is None or target_identity.kind != "regular":
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
            if hashlib.sha256(_read_fd_bytes(fd)).hexdigest() != target_identity.sha256:
                raise DistributionApplyError(f"managed target identity changed for '{path}'")

            _resolve_distribution_swap_rename()
            staging_name = _new_distribution_stage_name(path, expected)
            if write_ahead_stage_reservations and stage_ownership_recorder is not None:
                stage_ownership_recorder(_reserved_distribution_stage_ownership(path, staging_name, "regular"))
            staging_fd = os.open(
                staging_name,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                source_mode,
                dir_fd=parent_fd,
            )
            staging_stat = os.fstat(staging_fd)
            stage_identity = staging_stat
            swapped = False
            try:
                if not stat.S_ISREG(staging_stat.st_mode) or staging_stat.st_nlink != 1:
                    raise DistributionApplyError(f"managed target staging failed for '{path}'")
                if stage_ownership_recorder is not None and not write_ahead_stage_reservations:
                    stage_ownership_recorder(_distribution_stage_ownership(path, staging_name, staging_stat))

                def check_before_stage_write() -> None:
                    _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                    current = os.fstat(staging_fd)
                    if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
                        raise DistributionApplyError(f"managed target staging failed for '{path}'")

                _write_fd_bytes(staging_fd, source_bytes, before_mutation=check_before_stage_write)
                os.fchmod(staging_fd, source_mode)
                staged = os.fstat(staging_fd)
                if (
                    staged.st_nlink != 1
                    or stat.S_IMODE(staged.st_mode) != source_mode
                    or hashlib.sha256(_read_fd_bytes(staging_fd)).hexdigest() != expected.sha256
                ):
                    raise DistributionApplyError(f"managed target staging verification failed for '{path}'")
                stage_identity = staged
                if write_ahead_stage_reservations and stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(path, staging_name, staged))

                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                _assert_regular_fd_safe(fd, snapshot.target, path, exact=True)
                if hashlib.sha256(_read_fd_bytes(fd)).hexdigest() != target_identity.sha256:
                    raise DistributionApplyError(f"managed target identity changed for '{path}'")
                _swap_regular_distribution_target_if_bound(
                    parent_fd,
                    staging_name,
                    target_name,
                    target_fd=fd,
                    staging_fd=staging_fd,
                    expected_target=opened,
                    identity_message=f"managed target identity changed for '{path}'",
                )
                swapped = True

                published_fd = os.open(
                    target_name, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd
                )
                try:
                    published = os.fstat(published_fd)
                    if (
                        published.st_nlink != 1
                        or stat.S_IMODE(published.st_mode) != source_mode
                        or hashlib.sha256(_read_fd_bytes(published_fd)).hexdigest() != expected.sha256
                    ):
                        raise DistributionApplyError(f"managed target verification failed for '{path}'")
                finally:
                    os.close(published_fd)
            finally:
                if not swapped:
                    # A failed write may mutate the stage before raising.  The
                    # creation-time stat is then stale (ctime changes), so
                    # refresh and publish the no-follow identity before
                    # attempting ownership-checked cleanup.
                    visible_stage_matches = False
                    with suppress(OSError):
                        stage_identity = os.fstat(staging_fd)
                        visible_stage = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                        visible_stage_matches = _stat_identity_tuple(visible_stage) == _stat_identity_tuple(
                            stage_identity
                        )
                    if not visible_stage_matches:
                        os.close(staging_fd)
                        raise DistributionApplyError(f"managed target identity changed for '{path}'")
                    try:
                        if stage_ownership_recorder is not None and not write_ahead_stage_reservations:
                            stage_ownership_recorder(_distribution_stage_ownership(path, staging_name, stage_identity))
                    finally:
                        try:
                            os.close(staging_fd)
                        finally:
                            _remove_distribution_stage_if_owned(
                                parent_fd,
                                staging_name,
                                stage_identity,
                                strict=True,
                            )
                else:
                    published_successor = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                    os.close(staging_fd)
                    try:
                        old_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                        old_fd = os.open(
                            staging_name,
                            os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                            dir_fd=parent_fd,
                        )
                        try:
                            old_digest = hashlib.sha256(_read_fd_bytes(old_fd)).hexdigest()
                        finally:
                            os.close(old_fd)
                        if (
                            _same_stat_structure(old_stat, snapshot.target)
                            and old_stat.st_nlink == 1
                            and old_digest == target_identity.sha256
                        ):
                            if stage_ownership_recorder is not None:
                                # Persist the exact canonical successor before
                                # removing the displaced predecessor.  Retry
                                # can then prove both sides of an interrupted
                                # publish/cleanup transition and rebind the
                                # stage lease when needed.
                                try:
                                    stage_ownership_recorder(
                                        _distribution_stage_ownership(
                                            path,
                                            staging_name,
                                            published_successor if write_ahead_stage_reservations else old_stat,
                                        )
                                    )
                                except Exception as record_error:
                                    # The swap has already published the new
                                    # target, so the stage pathname now owns
                                    # the former target inode.  A transient
                                    # marker-write failure must not strand the
                                    # pre-swap identity: retry the recorder
                                    # once before falling back to cleanup.
                                    with suppress(Exception):
                                        stage_ownership_recorder(
                                            _distribution_stage_ownership(
                                                path,
                                                staging_name,
                                                published_successor if write_ahead_stage_reservations else old_stat,
                                            )
                                        )
                                    try:
                                        _remove_distribution_stage_if_owned(
                                            parent_fd,
                                            staging_name,
                                            old_stat,
                                            strict=True,
                                        )
                                    except DistributionApplyError as cleanup_error:
                                        try:
                                            _remove_distribution_stage_if_owned(
                                                parent_fd,
                                                staging_name,
                                                old_stat,
                                                strict=True,
                                            )
                                        except DistributionApplyError as retry_cleanup_error:
                                            raise retry_cleanup_error from record_error
                                        raise cleanup_error from record_error
                                    raise
                            _remove_distribution_stage_if_owned(
                                parent_fd,
                                staging_name,
                                old_stat,
                                strict=True,
                            )
                        else:
                            raise DistributionApplyError("managed staging identity changed")
                    except FileNotFoundError:
                        pass
        finally:
            os.close(fd)
    except FileNotFoundError as exc:
        raise DistributionApplyError(f"managed target identity changed for '{path}'") from exc
    except OSError as exc:
        raise DistributionApplyError(f"managed target apply failed for '{path}'") from exc
    finally:
        _close_distribution_parent_chain(parent_chain)


def _apply_symlink_action(
    *,
    target_root: Path,
    action: DistributionAction,
    snapshot: DistributionTargetSnapshot,
    expected: DistributionIdentity,
    created_parent_bindings: dict[str, PathIdentitySnapshot],
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None,
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None,
    write_ahead_stage_reservations: bool,
) -> None:
    if expected.target is None:
        raise DistributionApplyError(f"managed symlink identity has no target for '{action.path}'")
    expected_target = expected.target
    if action.action == "prune" and not snapshot.target.exists:
        return
    parent_chain = _open_distribution_parent_chain(
        target_root,
        action.path,
        create_missing=action.action == "create",
        expected_snapshot=snapshot,
        created_parent_bindings=created_parent_bindings,
        created_parent_recorder=created_parent_recorder,
    )
    try:
        _assert_distribution_chain_bound(parent_chain, snapshot, action.path)
        _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
        _bind_created_parent_identities(
            action.path,
            snapshot,
            parent_chain,
            created_parent_bindings,
            created_parent_recorder,
        )
        parent_fd = parent_chain[-1]
        target_name = PurePosixPath(action.path).name
        try:
            current_stat = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
            target_exists = True
        except FileNotFoundError:
            current_stat = None
            current_target = None
            target_exists = False
        except OSError as exc:
            raise DistributionApplyError(f"managed target is unsafe for '{action.path}'") from exc
        else:
            assert current_stat is not None
            if stat.S_ISLNK(current_stat.st_mode):
                try:
                    current_target = _normalized_link_target_for_path(
                        action.path,
                        os.readlink(target_name, dir_fd=parent_fd),
                    )
                except OSError as exc:
                    raise DistributionApplyError(f"managed target is unsafe for '{action.path}'") from exc
            else:
                current_target = None

        if action.action == "create":
            if target_exists:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            _resolve_distribution_no_replace_rename()
            staging_name = _new_distribution_stage_name(action.path, expected)
            if write_ahead_stage_reservations and stage_ownership_recorder is not None:
                stage_ownership_recorder(_reserved_distribution_stage_ownership(action.path, staging_name, "symlink"))
            os.symlink(expected_target, staging_name, dir_fd=parent_fd)
            staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            published = False
            try:
                staged_target = _normalized_link_target_for_path(
                    action.path, os.readlink(staging_name, dir_fd=parent_fd)
                )
                if staged_target != expected_target or staging_stat.st_nlink != 1:
                    raise DistributionApplyError(f"managed target staging failed for '{action.path}'")
                if stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(action.path, staging_name, staging_stat))
                _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
                _rename_distribution_no_replace(parent_fd, staging_name, parent_fd, target_name)
                os.fsync(parent_fd)
                published = True
            finally:
                if not published:
                    # A recorder failure or publish failure may leave the
                    # symlink stage behind.  Refresh its no-follow identity
                    # before retrying the marker record and use strict,
                    # ownership-checked cleanup so a transient unlink error
                    # remains recoverable by the next same-package retry.
                    with suppress(OSError):
                        staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                    try:
                        if stage_ownership_recorder is not None:
                            stage_ownership_recorder(
                                _distribution_stage_ownership(action.path, staging_name, staging_stat)
                            )
                    finally:
                        _remove_distribution_stage_if_owned(
                            parent_fd,
                            staging_name,
                            staging_stat,
                            strict=True,
                        )
            created_target = _normalized_link_target_for_path(action.path, os.readlink(target_name, dir_fd=parent_fd))
            if created_target != expected_target:
                raise DistributionApplyError(f"managed target verification failed for '{action.path}'")
            return
        if action.action == "prune":
            if not target_exists:
                return
            if snapshot.target.identity is None or current_target != snapshot.target.identity.target:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            latest_stat = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
            if not _same_stat_identity(latest_stat, snapshot.target) or latest_stat.st_nlink != 1:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
            latest_target = _normalized_link_target_for_path(action.path, os.readlink(target_name, dir_fd=parent_fd))
            if latest_target != snapshot.target.identity.target:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            _remove_distribution_target_if_bound(
                parent_fd,
                target_name,
                latest_stat,
                identity_message=f"managed target identity changed for '{action.path}'",
                transition_path=action.path,
                transition_name=_new_distribution_stage_name(action.path, snapshot.target.identity),
                transition_recorder=(stage_ownership_recorder if write_ahead_stage_reservations else None),
            )
            return
        if action.action == "upgrade":
            if not target_exists or snapshot.target.identity is None:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            if snapshot.target.identity.kind == "symlink" and current_target != snapshot.target.identity.target:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            _resolve_distribution_swap_rename()
            staging_name = _new_distribution_stage_name(action.path, expected)
            if write_ahead_stage_reservations and stage_ownership_recorder is not None:
                stage_ownership_recorder(_reserved_distribution_stage_ownership(action.path, staging_name, "symlink"))
            os.symlink(expected_target, staging_name, dir_fd=parent_fd)
            staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            cleanup_stage_stat = staging_stat
            swapped = False
            try:
                staged_target = _normalized_link_target_for_path(
                    action.path, os.readlink(staging_name, dir_fd=parent_fd)
                )
                if staged_target != expected_target:
                    raise DistributionApplyError(f"managed target staging failed for '{action.path}'")
                if stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(action.path, staging_name, staging_stat))
                latest_stat = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                if not _same_stat_identity(latest_stat, snapshot.target) or latest_stat.st_nlink != 1:
                    raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                if snapshot.target.identity.kind == "symlink":
                    latest_target = _normalized_link_target_for_path(
                        action.path, os.readlink(target_name, dir_fd=parent_fd)
                    )
                    if latest_target != snapshot.target.identity.target:
                        raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
                _swap_symlink_distribution_target_if_bound(
                    parent_fd,
                    staging_name,
                    target_name,
                    expected_target=snapshot.target,
                    staging_stat=staging_stat,
                    identity_message=f"managed target identity changed for '{action.path}'",
                )
                swapped = True
                published_target = _normalized_link_target_for_path(
                    action.path, os.readlink(target_name, dir_fd=parent_fd)
                )
                if published_target != expected_target:
                    raise DistributionApplyError(f"managed target verification failed for '{action.path}'")
            finally:
                if not swapped:
                    # Do not refresh an ambiguous post-exchange pathname into
                    # operation ownership.  Cleanup is authorized only when
                    # the original staged symlink identity and target remain
                    # bound to the staging name.
                    stage_is_original = False
                    try:
                        visible_stage = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                        visible_target = _normalized_link_target_for_path(
                            action.path,
                            os.readlink(staging_name, dir_fd=parent_fd),
                        )
                        visible_stage_after = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                        stage_is_original = (
                            _stat_structure_tuple(visible_stage) == _stat_structure_tuple(cleanup_stage_stat)
                            and _stat_identity_tuple(visible_stage_after) == _stat_identity_tuple(visible_stage)
                            and visible_target == expected_target
                        )
                    except (FileNotFoundError, OSError, DistributionApplyError):
                        stage_is_original = False
                    if not stage_is_original:
                        raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                    cleanup_stage_stat = visible_stage
                    try:
                        if stage_ownership_recorder is not None:
                            stage_ownership_recorder(
                                _distribution_stage_ownership(action.path, staging_name, cleanup_stage_stat)
                            )
                    finally:
                        _remove_distribution_stage_if_owned(
                            parent_fd,
                            staging_name,
                            cleanup_stage_stat,
                            strict=True,
                        )
                else:
                    published_successor = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                    try:
                        old_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                        old_target = (
                            _normalized_link_target_for_path(action.path, os.readlink(staging_name, dir_fd=parent_fd))
                            if stat.S_ISLNK(old_stat.st_mode)
                            else None
                        )
                        if (
                            snapshot.target.identity is not None
                            and old_target == snapshot.target.identity.target
                            and _same_stat_structure(old_stat, snapshot.target)
                            and old_stat.st_nlink == 1
                        ):
                            if stage_ownership_recorder is not None:
                                # Bind the exact canonical successor before
                                # removing the displaced predecessor.  Retry
                                # can validate both namespace roles.
                                try:
                                    stage_ownership_recorder(
                                        _distribution_stage_ownership(
                                            action.path,
                                            staging_name,
                                            published_successor if write_ahead_stage_reservations else old_stat,
                                        )
                                    )
                                except Exception as record_error:
                                    # The swap already published the new
                                    # target.  Retry the marker record once,
                                    # then fall back to strict cleanup; if
                                    # cleanup also fails, retry it once so
                                    # either durable ownership or removal is
                                    # established before returning partial
                                    # failure.
                                    with suppress(Exception):
                                        stage_ownership_recorder(
                                            _distribution_stage_ownership(
                                                action.path,
                                                staging_name,
                                                published_successor if write_ahead_stage_reservations else old_stat,
                                            )
                                        )
                                    try:
                                        _remove_distribution_stage_if_owned(
                                            parent_fd,
                                            staging_name,
                                            old_stat,
                                            strict=True,
                                        )
                                    except DistributionApplyError as cleanup_error:
                                        try:
                                            _remove_distribution_stage_if_owned(
                                                parent_fd,
                                                staging_name,
                                                old_stat,
                                                strict=True,
                                            )
                                        except DistributionApplyError as retry_cleanup_error:
                                            raise retry_cleanup_error from record_error
                                        raise cleanup_error from record_error
                                    raise
                            _remove_distribution_stage_if_owned(
                                parent_fd,
                                staging_name,
                                old_stat,
                                strict=True,
                            )
                    except FileNotFoundError:
                        pass
            return
        raise DistributionApplyError(f"unsupported symlink action for '{action.path}'")
    except FileNotFoundError as exc:
        raise DistributionApplyError(f"managed target identity changed for '{action.path}'") from exc
    except OSError as exc:
        raise DistributionApplyError(f"managed target apply failed for '{action.path}'") from exc
    finally:
        _close_distribution_parent_chain(parent_chain)


def _apply_distribution_action(
    plan: DistributionPlan,
    target_root: Path,
    action: DistributionAction,
    snapshot: DistributionTargetSnapshot,
    created_parent_bindings: dict[str, PathIdentitySnapshot],
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None = None,
    write_ahead_stage_reservations: bool = False,
) -> None:
    if action.action in {"adopt", "preserve"}:
        return
    expected = _expected_target_identity(plan, action.path)
    if expected is None and action.action != "prune":
        raise DistributionApplyError(f"managed action has no Current identity for '{action.path}'")
    if action.action == "create" and expected is not None:
        _resolve_distribution_no_replace_rename()
    elif action.action == "upgrade" and expected is not None:
        _resolve_distribution_swap_rename()

    source_bytes: bytes | None = None
    source_mode: int | None = None
    if action.action in {"create", "upgrade"}:
        if expected is None or expected.kind != "regular":
            source_bytes = None
        else:
            asset = _asset_for_target(plan, action.path)
            if asset is None:
                raise DistributionApplyError(f"distribution plan has no provider source for '{action.path}'")
            if asset.generated_content is not None:
                source_bytes = asset.generated_content
                observed_source_snapshot = None
            else:
                source_root = plan.scaffold_root if asset.source_path is not None else plan.install_root
                if source_root is None:
                    raise DistributionApplyError("distribution plan has no provider source root")
                source_rel = asset.source_path or asset.path
                source_bytes, observed_source_snapshot = _source_asset_bytes(source_root / source_rel)
                if asset.source_snapshot is None or observed_source_snapshot != asset.source_snapshot:
                    raise DistributionApplyError(f"provider Current asset identity changed for '{action.path}'")
            if expected.sha256 is None or hashlib.sha256(source_bytes).hexdigest() != expected.sha256:
                raise DistributionApplyError(f"provider Current asset content changed for '{action.path}'")
            if expected.mode is None:
                raise DistributionApplyError(f"provider Current asset mode changed for '{action.path}'")
            # Bind the mutation to the mode captured in the read-only plan;
            # never publish a mode observed after plan construction.
            source_mode = expected.mode

    target_kind = snapshot.target.file_type
    if expected is not None and expected.kind == "symlink":
        if expected.target is None:
            raise DistributionApplyError(f"managed action has no symlink target for '{action.path}'")
        _apply_symlink_action(
            target_root=target_root,
            action=action,
            snapshot=snapshot,
            expected=expected,
            created_parent_bindings=created_parent_bindings,
            stage_ownership_recorder=stage_ownership_recorder,
            created_parent_recorder=created_parent_recorder,
            write_ahead_stage_reservations=write_ahead_stage_reservations,
        )
        return
    if expected is None and target_kind == "symlink":
        historical_identity = snapshot.target.identity
        if historical_identity is None or historical_identity.kind != "symlink":
            raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
        if historical_identity.target is None:
            raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
        _apply_symlink_action(
            target_root=target_root,
            action=action,
            snapshot=snapshot,
            expected=historical_identity,
            created_parent_bindings=created_parent_bindings,
            stage_ownership_recorder=stage_ownership_recorder,
            created_parent_recorder=created_parent_recorder,
            write_ahead_stage_reservations=write_ahead_stage_reservations,
        )
        return
    if expected is None and target_kind != "regular":
        raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
    _apply_regular_action(
        target_root=target_root,
        action=action,
        snapshot=snapshot,
        expected=expected if expected is not None else snapshot.target.identity,  # type: ignore[arg-type]
        source_bytes=source_bytes,
        source_mode=source_mode,
        created_parent_bindings=created_parent_bindings,
        stage_ownership_recorder=stage_ownership_recorder,
        created_parent_recorder=created_parent_recorder,
        write_ahead_stage_reservations=write_ahead_stage_reservations,
    )


def apply_distribution_plan(
    plan: DistributionPlan,
    *,
    allow_stale_stage_cleanup: bool = False,
    allow_blocked_scaffold_paths: bool = False,
    stage_ownership: tuple[DistributionStageOwnership, ...] = (),
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    created_parent_bindings: tuple[PathIdentitySnapshot, ...] = (),
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None = None,
    write_ahead_stage_reservations: bool = False,
    scaffold_applier: Callable[[], None] | None = None,
    progress_recorder: Callable[[str, tuple[str, ...], tuple[str, ...], bool], None] | None = None,
) -> DistributionResult:
    """Apply a validated plan with no-follow identity checks at every action.

    This S30 seam intentionally does not perform CLI admission, version-marker
    handling, retry persistence, or recursive cleanup.  Stale private-stage
    cleanup is opt-in for a validated same-package retry and only removes
    stage entries whose no-follow identity was recorded immediately after
    creation by that retry marker; ordinary runs leave unknown stage-like
    siblings untouched.  Any preflight or identity mismatch raises before the
    corresponding action writes or removes a target path.
    """

    target_root = plan.target_root
    if target_root is None or plan.install_root is None:
        raise DistributionApplyError("distribution plan is missing target or provider roots")
    permitted_scaffold_paths = (
        plan.scaffold_paths if scaffold_applier is not None and allow_blocked_scaffold_paths else frozenset()
    )
    blocked_actions = [
        action for action in plan.actions if action.blocked and action.path not in permitted_scaffold_paths
    ]
    if blocked_actions:
        raise DistributionApplyError("distribution plan is blocked")
    try:
        root_stat = os.lstat(target_root)
    except OSError as exc:
        raise DistributionApplyError("managed target root cannot be opened safely") from exc
    if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode):
        raise DistributionApplyError("managed target root is not a real directory")

    snapshots = _plan_snapshot_map(plan)
    created_parent_bindings_by_path = {binding.relative_path: binding for binding in created_parent_bindings}
    scaffold_paths = plan.scaffold_paths if scaffold_applier is not None else frozenset()
    for action in plan.actions:
        snapshot = snapshots.get(action.path)
        if snapshot is None:
            raise DistributionApplyError("distribution plan is missing a target identity snapshot")
        _assert_plan_target_snapshot(target_root, action.path, snapshot)

    applied_paths: list[str] = []
    pending_paths = [action.path for action in plan.actions]

    if scaffold_applier is not None and scaffold_paths:
        if progress_recorder is not None:
            progress_recorder("managed-scaffold-refresh", tuple(applied_paths), tuple(pending_paths), False)
        try:
            scaffold_applier()
            for action in plan.actions:
                if action.path not in scaffold_paths:
                    continue
                refreshed = _observe_target(target_root, action.path)
                if refreshed.snapshot is None:
                    raise DistributionApplyError(f"managed scaffold post-apply path is missing for '{action.path}'")
                expected = _expected_target_identity(plan, action.path)
                if expected is None or refreshed.identity != expected:
                    raise DistributionApplyError(f"managed scaffold post-apply verification failed for '{action.path}'")
                snapshots[action.path] = refreshed.snapshot
                applied_paths.append(action.path)
                pending_paths.remove(action.path)
            for action in plan.actions:
                if action.path in scaffold_paths:
                    continue
                refreshed = _observe_target(target_root, action.path)
                if refreshed.snapshot is None:
                    raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                scaffold_owned_obsolete = (
                    action.action == "prune"
                    and any(action.path.startswith(f"spec-dock/{root}/") for root in _SCAFFOLD_MANAGED_ROOTS)
                    and refreshed.state == "missing"
                )
                if not scaffold_owned_obsolete:
                    _assert_pending_snapshot_stable(
                        refreshed.snapshot,
                        snapshots[action.path],
                        action.path,
                        created_parent_bindings_by_path,
                    )
                snapshots[action.path] = refreshed.snapshot
        except Exception as exc:
            if isinstance(exc, DistributionApplyError) and exc.phase is not None:
                raise
            raise DistributionApplyError(
                str(exc),
                phase="managed-scaffold-refresh",
                applied_paths=tuple(applied_paths),
                pending_paths=tuple(pending_paths),
            ) from exc
        if progress_recorder is not None:
            progress_recorder("managed-scaffold-refresh", tuple(applied_paths), tuple(pending_paths), True)

    current_paths = {asset.path for asset in plan.current_assets} | set(_CURRENT_SHORTCUTS)
    external_actions = tuple(action for action in plan.actions if action.path not in scaffold_paths)
    action_groups = (
        ("current-external-materialize", tuple(action for action in external_actions if action.path in current_paths)),
        ("obsolete-prune", tuple(action for action in external_actions if action.path not in current_paths)),
    )
    actions_to_apply = tuple(action for _, actions in action_groups for action in actions)
    action_index = {id(action): index for index, action in enumerate(actions_to_apply)}
    for phase, actions in action_groups:
        if not actions:
            if progress_recorder is not None:
                progress_recorder(phase, tuple(applied_paths), tuple(pending_paths), True)
            continue
        if progress_recorder is not None:
            progress_recorder(phase, tuple(applied_paths), tuple(pending_paths), False)
        for action in actions:
            index = action_index[id(action)]
            try:
                snapshot = snapshots[action.path]
                if allow_stale_stage_cleanup:
                    _cleanup_stale_distribution_stages(plan, target_root, action, snapshot, stage_ownership)
                # Removing a known stale stage mutates the parent directory ctime.  The
                # target itself must remain unchanged, but every later action needs the
                # refreshed parent snapshot before it can be applied or adopted.
                refreshed = _observe_target(target_root, action.path)
                if refreshed.snapshot is None:
                    raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                _assert_pending_snapshot_stable(
                    refreshed.snapshot,
                    snapshot,
                    action.path,
                    created_parent_bindings_by_path,
                )
                snapshot = refreshed.snapshot
                snapshots[action.path] = snapshot
                for pending in actions_to_apply[index + 1 :]:
                    pending_snapshot = snapshots[pending.path]
                    pending_observation = _observe_target(target_root, pending.path)
                    if pending_observation.snapshot is None:
                        raise DistributionApplyError(f"managed target identity changed for '{pending.path}'")
                    _assert_pending_snapshot_stable(
                        pending_observation.snapshot,
                        pending_snapshot,
                        pending.path,
                        created_parent_bindings_by_path,
                    )
                    snapshots[pending.path] = pending_observation.snapshot
                if action.action not in {"adopt", "preserve"}:
                    if stage_ownership_recorder is None and created_parent_recorder is None:
                        _apply_distribution_action(
                            plan,
                            target_root,
                            action,
                            snapshot,
                            created_parent_bindings_by_path,
                        )
                    elif stage_ownership_recorder is None:
                        _apply_distribution_action(
                            plan,
                            target_root,
                            action,
                            snapshot,
                            created_parent_bindings_by_path,
                            created_parent_recorder=created_parent_recorder,
                        )
                    else:
                        _apply_distribution_action(
                            plan,
                            target_root,
                            action,
                            snapshot,
                            created_parent_bindings_by_path,
                            stage_ownership_recorder,
                            created_parent_recorder,
                            write_ahead_stage_reservations,
                        )
                applied_paths.append(action.path)
                pending_paths.remove(action.path)
                if progress_recorder is not None:
                    progress_recorder(phase, tuple(applied_paths), tuple(pending_paths), False)
                for pending in actions_to_apply[index + 1 :]:
                    pending_snapshot = snapshots[pending.path]
                    pending_observation = _observe_target(target_root, pending.path)
                    if pending_observation.snapshot is None:
                        raise DistributionApplyError(f"managed target identity changed for '{pending.path}'")
                    _assert_pending_snapshot_stable(
                        pending_observation.snapshot,
                        pending_snapshot,
                        pending.path,
                        created_parent_bindings_by_path,
                    )
                    snapshots[pending.path] = pending_observation.snapshot
            except Exception as exc:
                if isinstance(exc, DistributionApplyError) and exc.phase is not None:
                    raise
                raise DistributionApplyError(
                    str(exc),
                    phase=phase,
                    applied_paths=tuple(applied_paths),
                    pending_paths=tuple(pending_paths),
                ) from exc
        if progress_recorder is not None:
            progress_recorder(phase, tuple(applied_paths), tuple(pending_paths), True)

    return DistributionResult(status="complete", actions=plan.actions)


__all__ = [
    "DistributionAction",
    "DistributionActionName",
    "DistributionApplyError",
    "DistributionAsset",
    "DistributionIdentity",
    "DistributionManifest",
    "DistributionManifestError",
    "DistributionOperation",
    "DistributionPlan",
    "DistributionPlanError",
    "DistributionProcessResult",
    "DistributionProvenance",
    "DistributionResult",
    "DistributionSourceSnapshot",
    "DistributionStageOwnership",
    "DistributionTargetSnapshot",
    "ExecutableMutationPlan",
    "OperationJournal",
    "OperationJournalAction",
    "OperationJournalStore",
    "PathIdentitySnapshot",
    "RecognizedDistributionIntent",
    "WorkspaceAssessment",
    "apply_distribution_plan",
    "build_distribution_plan",
    "build_executable_mutation_plan",
    "build_workspace_assessment",
    "execute_recognized_distribution",
]

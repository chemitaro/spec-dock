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
from typing import TYPE_CHECKING, Any, Literal, NoReturn, cast

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


@dataclass(frozen=True)
class DistributionDirectoryRequirement:
    """One real directory that must exist before managed file actions run."""

    path: str


DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]
JournaledDistributionIntent = Literal["fresh", "update", "init-force"]
DistributionActionName = Literal[
    "create",
    "adopt",
    "upgrade",
    "prune",
    "preserve",
    "block",
    "ensure-directory",
]
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
    required_directories: tuple[DistributionDirectoryRequirement, ...] = ()

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

    intent: JournaledDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]
    blockers: tuple[DistributionAction, ...]


@dataclass(frozen=True)
class ExecutableMutationPlan:
    """A blocker-free recognized plan bound to one root and contract."""

    intent: JournaledDistributionIntent
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
    intent: JournaledDistributionIntent
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
    intent: JournaledDistributionIntent
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
    role: Literal[
        "stage",
        "predecessor-quarantine",
        "backup-reserved",
        "backup-dual",
        "backup-only-reserved",
        "backup-only",
        "gc-reserved",
        "gc-exact",
    ] = "stage"
    gc_predecessor_name: str | None = None
    gc_ordinal: int | None = None


@dataclass(frozen=True)
class DistributionRetryMarker:
    """Validated init/update retry marker without absolute paths or secrets."""

    operation: Literal["fresh", "update", "init-force"]
    package_version: str
    target_root: DistributionRootIdentity
    last_completed_phase: str
    purpose: Literal[
        "distribution-rerun",
        "recognized-journal-forward-only",
        "fresh-journal-forward-only",
    ]
    stage_ownership: tuple[DistributionStageOwnership, ...] = ()
    operation_id: str | None = None
    contract_identity: str | None = None
    plan_digest: str | None = None
    journal_digest: str | None = None
    journal_predecessor_digest: str | None = None
    journal_created_at_ns: int | None = None
    source_snapshot: PathIdentitySnapshot | None = field(default=None, compare=False, repr=False)
    source_sha256: str | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class DistributionAdmission:
    """Read-only result of operation admission."""

    operation: DistributionOperation
    intent: JournaledDistributionIntent | None
    status: Literal["fresh", "existing", "recognized", "retry", "uninstall-retry"]
    package_version: str
    target_version: str | None = None
    marker: DistributionRetryMarker | None = None
    version_identity: DistributionIdentity | None = None

    def diagnostic(self) -> dict[str, object]:
        """Return stable, repository-relative admission evidence."""

        return {
            "operation": self.operation,
            "intent": self.intent,
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
# Fresh journals reuse the existing schema-1 field shape.  The schema-2
# discriminator belongs to the forward guard, not to the journal payload.
_DISTRIBUTION_FRESH_JOURNAL_SCHEMA_VERSION = _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
_DISTRIBUTION_LEGACY_JOURNAL_PROTOCOL_VERSION = 1
_DISTRIBUTION_JOURNAL_PROTOCOL_VERSION = 2
_DISTRIBUTION_SUPPORTED_JOURNAL_PROTOCOL_VERSIONS = frozenset({
    _DISTRIBUTION_LEGACY_JOURNAL_PROTOCOL_VERSION,
    _DISTRIBUTION_JOURNAL_PROTOCOL_VERSION,
})
_DISTRIBUTION_RETRY_SCHEMA_VERSION = 1
_DISTRIBUTION_RETRY_PURPOSE: Literal["distribution-rerun"] = "distribution-rerun"
_DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION = 2
_DISTRIBUTION_JOURNAL_GUARD_PURPOSE: Literal["recognized-journal-forward-only"] = "recognized-journal-forward-only"
_DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE: Literal["fresh-journal-forward-only"] = "fresh-journal-forward-only"
_DISTRIBUTION_JOURNAL_AUTHORITIES = {
    "recognized-journal-forward-only": "recognized-workspace-reconciliation",
    "fresh-journal-forward-only": "fresh-distribution-provisioning",
}
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
    supported_guard = schema_version == _DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION and purpose in {
        _DISTRIBUTION_JOURNAL_GUARD_PURPOSE,
        _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE,
    }
    supported_legacy = schema_version == _DISTRIBUTION_RETRY_SCHEMA_VERSION and purpose == _DISTRIBUTION_RETRY_PURPOSE
    expected_fields = (
        base_fields | {"operation_id", "contract_identity", "plan_digest"} if supported_guard else base_fields
    )
    anchor_fields = {"journal_digest", "journal_predecessor_digest"}
    created_at_anchor_field = {"journal_created_at_ns"}
    raw_fields = set(raw)
    allowed_field_sets = {
        frozenset(expected_fields),
        frozenset(expected_fields | {"stage_ownership"}),
    }
    if supported_guard:
        legacy_anchor_sets = {fields | anchor_fields for fields in tuple(allowed_field_sets)}
        allowed_field_sets.update(legacy_anchor_sets)
        allowed_field_sets.update({fields | created_at_anchor_field for fields in legacy_anchor_sets})
    if frozenset(raw_fields) not in allowed_field_sets:
        _admission_block("marker-invalid", "distribution retry marker fields are invalid")
    if not supported_guard and not supported_legacy:
        _admission_block("marker-invalid", "distribution retry marker schema is unsupported")
    operation = raw.get("operation")
    if operation not in {"fresh", "update", "init-force"}:
        _admission_block("marker-invalid", "distribution retry marker operation is unsupported")
    if supported_guard and (
        (purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE and operation not in {"update", "init-force"})
        or (purpose == _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE and operation != "fresh")
    ):
        _admission_block("marker-invalid", "distribution retry marker purpose and operation do not match")
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
    journal_digest = raw.get("journal_digest") if supported_guard else None
    journal_predecessor_digest = raw.get("journal_predecessor_digest") if supported_guard else None
    journal_created_at_ns = raw.get("journal_created_at_ns") if supported_guard else None
    if supported_guard and (
        not isinstance(operation_id, str)
        or not operation_id
        or not isinstance(contract_identity, str)
        or not contract_identity
        or not isinstance(plan_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", plan_digest)
    ):
        _admission_block("marker-invalid", "distribution retry marker plan binding is invalid")
    if (
        supported_guard
        and raw_fields & anchor_fields
        and (
            not isinstance(journal_digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", journal_digest)
            or (
                journal_created_at_ns is not None
                and (
                    isinstance(journal_created_at_ns, bool)
                    or not isinstance(journal_created_at_ns, int)
                    or journal_created_at_ns <= 0
                )
            )
            or (
                journal_predecessor_digest is not None
                and (
                    not isinstance(journal_predecessor_digest, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", journal_predecessor_digest)
                )
            )
        )
    ):
        _admission_block("marker-invalid", "distribution retry marker journal anchor is invalid")
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
    guard_purpose = (
        cast(
            "Literal['recognized-journal-forward-only', 'fresh-journal-forward-only']",
            purpose,
        )
        if supported_guard
        else _DISTRIBUTION_RETRY_PURPOSE
    )
    return DistributionRetryMarker(
        operation=operation,
        package_version=package_version,
        target_root=DistributionRootIdentity(device=device, inode=inode),
        last_completed_phase=phase,
        purpose=guard_purpose,
        stage_ownership=tuple(stage_ownership),
        operation_id=operation_id,
        contract_identity=contract_identity,
        plan_digest=plan_digest,
        journal_digest=journal_digest,
        journal_predecessor_digest=journal_predecessor_digest,
        journal_created_at_ns=journal_created_at_ns,
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


def _journal_authority_for_intent(intent: JournaledDistributionIntent) -> str:
    return "fresh-distribution-provisioning" if intent == "fresh" else "recognized-workspace-reconciliation"


def _journal_guard_purpose_for_intent(
    intent: JournaledDistributionIntent,
) -> Literal["recognized-journal-forward-only", "fresh-journal-forward-only"]:
    return _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE if intent == "fresh" else _DISTRIBUTION_JOURNAL_GUARD_PURPOSE


def _journal_intent_for_guard_purpose(
    purpose: str,
) -> JournaledDistributionIntent:
    if purpose == _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE:
        return "fresh"
    if purpose == _DISTRIBUTION_JOURNAL_GUARD_PURPOSE:
        return "update"
    raise DistributionPlanError("unsupported journal guard purpose")


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
        if operation == "uninstall":
            _admission_block("distribution-retry-present", "recover distribution before this operation")
        distribution_marker = _read_distribution_retry_marker(target_root)
        if distribution_marker is None:
            try:
                terminal_journal = OperationJournalStore(target_root)._read(root_identity)
            except DistributionApplyError:
                _admission_block("dual-marker", "distribution recovery states cannot coexist")
            if (
                terminal_journal.status != "completed"
                or terminal_journal.intent not in {"fresh", "update", "init-force"}
                or terminal_journal.authority != _journal_authority_for_intent(terminal_journal.intent)
                or terminal_journal.protocol_version not in _DISTRIBUTION_SUPPORTED_JOURNAL_PROTOCOL_VERSIONS
                or not _journal_package_is_compatible(terminal_journal.package_version, package_version)
                or terminal_journal.staging_leases
                or any(action.checkpoint != "verified" for action in terminal_journal.actions)
            ):
                _admission_block("dual-marker", "distribution recovery states cannot coexist")
            if terminal_journal.intent != "fresh" and terminal_journal.intent != operation:
                _admission_block("marker-operation-mismatch", "journal belongs to another operation")
            return DistributionAdmission(
                operation=operation,
                intent=terminal_journal.intent,
                status="retry",
                package_version=package_version,
            )
        if distribution_marker is None:
            _admission_block("dual-marker", "distribution recovery states cannot coexist")
        marker_intent = (
            "fresh"
            if (
                distribution_marker.purpose == _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE
                or distribution_marker.operation == "fresh"
            )
            else operation
        )
        marker_operation_valid = (
            distribution_marker.operation == "fresh"
            if marker_intent == "fresh"
            else distribution_marker.operation == operation
        )
        if distribution_marker is None or (
            distribution_marker.purpose
            not in {
                _DISTRIBUTION_JOURNAL_GUARD_PURPOSE,
                _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE,
            }
            or distribution_marker.source_snapshot is None
            or distribution_marker.source_sha256 is None
            or not marker_operation_valid
            or distribution_marker.target_root != root_identity
            or distribution_marker.last_completed_phase != "preflight-complete"
            or not _journal_package_is_compatible(distribution_marker.package_version, package_version)
        ):
            _admission_block("dual-marker", "distribution recovery states cannot coexist")
        return DistributionAdmission(
            operation=operation,
            intent=marker_intent,
            status="retry",
            package_version=package_version,
            marker=distribution_marker,
        )

    distribution_marker = _read_distribution_retry_marker(target_root)
    uninstall_marker = _read_uninstall_retry_marker_for_admission(target_root)
    if distribution_marker is not None:
        if operation == "uninstall":
            _admission_block("distribution-retry-present", "recover distribution before uninstall")
        marker_intent = (
            "fresh"
            if (
                distribution_marker.purpose == _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE
                or distribution_marker.operation == "fresh"
            )
            else operation
        )
        marker_operation_valid = (
            distribution_marker.operation == "fresh"
            if marker_intent == "fresh"
            else distribution_marker.operation == operation
        )
        if not marker_operation_valid:
            _admission_block("marker-operation-mismatch", "retry marker belongs to another operation")
        if not _journal_package_is_compatible(distribution_marker.package_version, package_version):
            _admission_block("marker-package-mismatch", "retry marker belongs to another package version")
        if distribution_marker.target_root != root_identity:
            _admission_block("cross-root-replay", "retry marker belongs to another repository root")
        return DistributionAdmission(
            operation=operation,
            intent=marker_intent,
            status="retry",
            package_version=package_version,
            marker=distribution_marker,
        )
    if uninstall_marker:
        if operation != "uninstall":
            _admission_block("uninstall-retry-present", "recover uninstall before init or update")
        return DistributionAdmission(
            operation=operation,
            intent=None,
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
        if empty_workspace_boundary and operation in {"fresh", "init-force", "update"}:
            return DistributionAdmission(
                operation=operation, intent="fresh", status="fresh", package_version=package_version
            )
        if operation in {"fresh", "init-force", "update"} and _is_preserved_specs_workspace(target_root):
            return DistributionAdmission(
                operation=operation, intent="fresh", status="fresh", package_version=package_version
            )

    if specdock_info is None:
        if operation in {"fresh", "init-force", "update"}:
            return DistributionAdmission(
                operation=operation, intent="fresh", status="fresh", package_version=package_version
            )
        if operation == "update":
            _admission_block(
                "workspace-missing",
                "'spec-dock' not found. Run 'spec-dock init' first.",
            )
        _admission_block("workspace-missing", "target is not a managed SpecDock repo")
    if operation == "fresh":
        return DistributionAdmission(
            operation=operation, intent="fresh", status="existing", package_version=package_version
        )
    target_version, _target_tuple, version_identity = _validate_workspace_version(
        target_root,
        manifest=manifest,
        package_version=package_version,
    )
    recognized_intent: JournaledDistributionIntent | None = None
    if operation in {"update", "init-force"}:
        recognized_intent = cast("JournaledDistributionIntent", operation)
    return DistributionAdmission(
        operation=operation,
        intent=recognized_intent,
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
        # The fresh root workbench seed is published at the workspace root,
        # while its provider source remains under the root template.  Keep the
        # two paths explicit so the journaled apply phase can read the same
        # no-follow source that preflight inspected.
        target_path = (
            "spec-dock/.workbench/README.md" if source_path == ".workbench/README.md" else f"spec-dock/{source_path}"
        )
        provider_source_path = (
            "templates/root/.workbench/README.md" if source_path == ".workbench/README.md" else source_path
        )
        assets.append(
            DistributionAsset(
                path=target_path,
                source_path=provider_source_path,
                identity=DistributionIdentity(
                    kind="regular",
                    sha256=digest,
                    mode=mode,
                ),
                source_snapshot=source_snapshot,
            )
        )
    return tuple(assets)


def _fresh_required_directory_paths(
    assets: tuple[DistributionAsset, ...],
) -> tuple[DistributionDirectoryRequirement, ...]:
    # These workspace boundaries are part of the fresh contract even when the
    # current provider catalog has no child asset under them.  They are the
    # preserved-specs and runtime-state roots that the installer has always
    # provisioned and that later commands address directly.
    required: set[str] = {
        "spec-dock",
        "spec-dock/initiatives",
        "spec-dock/.agent",
    }
    for asset in assets:
        parts = PurePosixPath(asset.path).parts[:-1]
        required.update("/".join(parts[:index]) for index in range(1, len(parts) + 1))
    return tuple(
        DistributionDirectoryRequirement(path)
        for path in sorted(required, key=lambda path: (len(PurePosixPath(path).parts), path))
    )


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
        and operation in {"fresh", "uninstall"}
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
        and operation in {"fresh", "update", "init-force", "uninstall"}
        and not (operation == "fresh" and path == "spec-dock/.workbench/README.md")
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


def _classify_required_directory(
    *,
    target_root: Path,
    path: str,
    operation: DistributionOperation,
    observation: _TargetObservation | None = None,
) -> DistributionAction:
    if observation is None:
        observation = _observe_target(target_root, path)
    if observation.state == "missing":
        return DistributionAction(
            path,
            operation,
            "ensure-directory",
            "missing",
            "required-directory-missing",
        )
    if observation.state == "directory":
        return DistributionAction(path, operation, "adopt", "current", "required-directory-present")
    reason = {
        "symlink-container": "required-directory-symlink",
        "special": "required-directory-unsafe",
    }.get(observation.state, "required-directory-file")
    return _blocked_action(path, operation, reason, action="preserve")


def _classify_target(
    *,
    target_root: Path,
    current_assets: tuple[DistributionAsset, ...],
    operation: DistributionOperation,
    manifest: DistributionManifest,
    scaffold_assets: tuple[DistributionAsset, ...] = (),
    required_directories: tuple[DistributionDirectoryRequirement, ...] = (),
) -> tuple[tuple[DistributionAction, ...], tuple[tuple[str, DistributionTargetSnapshot], ...]]:
    specs = _target_identity_specs(current_assets, scaffold_assets)
    generated_assets = {asset.path: asset for asset in scaffold_assets if asset.source_path is None}
    actions: list[DistributionAction] = []
    observations: dict[str, _TargetObservation] = {}
    for requirement in required_directories:
        path = requirement.path
        observation = _observe_target(target_root, path)
        observations[path] = observation
        actions.append(
            _classify_required_directory(
                target_root=target_root,
                path=path,
                operation=operation,
                observation=observation,
            )
        )
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
    required_directories = (
        _fresh_required_directory_paths((*current_assets, *scaffold_assets)) if operation == "fresh" else ()
    )
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
            required_directories=required_directories,
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
        required_directories=required_directories,
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
        "required_directories": [item.path for item in plan.required_directories],
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
    intent: JournaledDistributionIntent,
    scaffold_root: Path | None = None,
    generated_assets: tuple[DistributionAsset, ...] = (),
) -> WorkspaceAssessment:
    """Assess one journaled operation without creating execution authority."""

    if intent not in {"fresh", "update", "init-force"}:
        raise DistributionPlanError(f"unsupported journaled intent: {intent!r}")
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


def _required_directory_identity(plan: DistributionPlan, path: str) -> DistributionIdentity | None:
    if any(item.path == path for item in plan.required_directories):
        return DistributionIdentity(kind="directory")
    return None


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
    if expected_type == "directory":
        if action.action == "adopt" and snapshot.target.exists and snapshot.target.file_type == "directory":
            return {
                **boundary,
                "exists": True,
                # An adopted directory is not mutated by the action, but
                # publishing children below it may change ctime/link-count.
                # Keep the captured device/inode as the exact recovery
                # identity while treating those metadata fields as wildcards.
                "device": snapshot.target.device,
                "inode": snapshot.target.inode,
                "ctime_ns": 0,
                "file_type": "directory",
                "link_count": 0,
                "identity": _distribution_identity_payload(expected),
            }
        return {
            **boundary,
            "exists": True,
            # Directory metadata changes when child entries are published.  The
            # directory identity itself is the stable postcondition; zeroed
            # structural fields intentionally make the condition metadata-free.
            "device": 0,
            "inode": 0,
            "ctime_ns": 0,
            "file_type": "directory",
            "link_count": 0,
            "identity": _distribution_identity_payload(expected),
        }
    if action.action == "adopt" and snapshot.target.exists and snapshot.target.file_type != "directory":
        if (
            snapshot.target.device is None
            or snapshot.target.inode is None
            or snapshot.target.ctime_ns is None
            or snapshot.target.link_count is None
        ):
            raise DistributionPlanError(f"assessment is missing structural identity for '{action.path}'")
        return {
            **boundary,
            "exists": True,
            # Adoption does not mutate a non-directory target.  Preserve the
            # observed node identity and link topology so an interrupted
            # checkpoint cannot resume against an external replacement.
            "device": snapshot.target.device,
            "inode": snapshot.target.inode,
            "ctime_ns": snapshot.target.ctime_ns,
            "file_type": snapshot.target.file_type,
            "link_count": snapshot.target.link_count,
            "identity": _distribution_identity_payload(expected),
        }
    return {
        **boundary,
        "exists": True,
        "file_type": expected_type,
        "link_count": 1,
        "identity": _distribution_identity_payload(expected),
    }


def _legacy_action_postcondition_payload(
    plan: DistributionPlan,
    action: DistributionAction,
    *,
    fixed_link_count: bool = False,
) -> dict[str, object]:
    """Reconstruct the schema-1/protocol-1 adopt condition shape.

    The journal protocol remains version 1 even though current adopt
    postconditions now retain structural identity.  Older journals therefore
    legitimately omit device/inode/ctime for an existing non-directory adopt.
    Keep the old wire shape available for plan-digest compatibility checks.
    """

    payload = _action_postcondition_payload(plan, action)
    if action.action != "adopt" or payload.get("file_type") == "directory":
        return payload
    if fixed_link_count:
        payload = {**payload, "link_count": 1}
    return {key: value for key, value in payload.items() if key not in {"device", "inode", "ctime_ns"}}


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
    if normalized.get("file_type") == "directory":
        normalized.pop("ctime_ns", None)
        normalized.pop("link_count", None)
    root = normalized.get("root")
    if isinstance(root, dict):
        normalized["root"] = {key: value for key, value in root.items() if key not in {"ctime_ns", "link_count"}}
    parents = normalized.get("parents")
    if isinstance(parents, list):
        normalized["parents"] = [
            {key: value for key, value in parent.items() if key not in {"ctime_ns", "link_count"}}
            if isinstance(parent, dict)
            else parent
            for parent in parents
        ]
    return normalized


def _distribution_plan_digest(
    *,
    intent: JournaledDistributionIntent,
    root_identity: DistributionRootIdentity,
    contract_identity: str,
    plan: DistributionPlan,
    actions: tuple[DistributionAction, ...],
    legacy_adopt_postconditions: bool = False,
    legacy_adopt_fixed_link_count: bool = False,
) -> str:
    ordered_actions = sorted(actions, key=lambda action: (action.path, action.action, action.reason))
    payload: dict[str, object] = {
        "schema_version": (
            _DISTRIBUTION_FRESH_JOURNAL_SCHEMA_VERSION if intent == "fresh" else _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
        ),
        "intent": intent,
        "root_binding": {
            "device": root_identity.device,
            "inode": root_identity.inode,
        },
        "contract_identity": contract_identity,
        "actions": [
            {
                "path": action.path,
                "action": action.action,
                "provenance": action.provenance,
                "reason": action.reason,
                "precondition": _plan_digest_condition(_action_precondition_payload(plan, action)),
                "postcondition": _plan_digest_condition(
                    _legacy_action_postcondition_payload(
                        plan,
                        action,
                        fixed_link_count=legacy_adopt_fixed_link_count,
                    )
                    if legacy_adopt_postconditions
                    else _action_postcondition_payload(plan, action)
                ),
            }
            for action in ordered_actions
        ],
    }
    if intent == "fresh":
        payload["required_directories"] = sorted(item.path for item in plan.required_directories)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mutation_plan_digest(
    assessment: WorkspaceAssessment,
    *,
    legacy_adopt_postconditions: bool = False,
    legacy_adopt_fixed_link_count: bool = False,
) -> str:
    return _distribution_plan_digest(
        intent=assessment.intent,
        root_identity=assessment.root_identity,
        contract_identity=assessment.contract_identity,
        plan=assessment.distribution_plan,
        actions=assessment.actions,
        legacy_adopt_postconditions=legacy_adopt_postconditions,
        legacy_adopt_fixed_link_count=legacy_adopt_fixed_link_count,
    )


def _executable_plan_digest(
    plan: ExecutableMutationPlan,
    *,
    legacy_adopt_postconditions: bool = False,
    legacy_adopt_fixed_link_count: bool = False,
) -> str:
    return _distribution_plan_digest(
        intent=plan.intent,
        root_identity=plan.root_identity,
        contract_identity=plan.contract_identity,
        plan=plan.distribution_plan,
        actions=plan.actions,
        legacy_adopt_postconditions=legacy_adopt_postconditions,
        legacy_adopt_fixed_link_count=legacy_adopt_fixed_link_count,
    )


def _mutation_plan_digest_candidates(assessment: WorkspaceAssessment) -> frozenset[str]:
    return frozenset({
        _mutation_plan_digest(assessment),
        _mutation_plan_digest(assessment, legacy_adopt_postconditions=True),
        _mutation_plan_digest(
            assessment,
            legacy_adopt_postconditions=True,
            legacy_adopt_fixed_link_count=True,
        ),
    })


def _executable_plan_digest_candidates(plan: ExecutableMutationPlan) -> frozenset[str]:
    return frozenset({
        plan.plan_digest,
        _executable_plan_digest(plan, legacy_adopt_postconditions=True),
        _executable_plan_digest(
            plan,
            legacy_adopt_postconditions=True,
            legacy_adopt_fixed_link_count=True,
        ),
    })


def _plan_digest_matches(plan: ExecutableMutationPlan, stored_digest: str | None) -> bool:
    return stored_digest in _executable_plan_digest_candidates(plan)


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
    current_specs = {
        **_target_identity_specs(plan.current_assets, plan.scaffold_assets),
        **{item.path: DistributionIdentity(kind="directory") for item in plan.required_directories},
    }
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files} - set(current_specs)
    for action in assessment.actions:
        try:
            _exact_relative_path(action.path, field_name="workspace assessment action path")
        except DistributionManifestError as exc:
            raise DistributionPlanError("workspace assessment contains an unsafe managed path") from exc
        if action.operation != assessment.intent:
            raise DistributionPlanError("workspace assessment action intent mismatch")
        if action.action == "ensure-directory":
            if not any(item.path == action.path for item in plan.required_directories):
                raise DistributionPlanError("workspace assessment ensure-directory is outside directory authority")
        elif action.action == "prune":
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
            **({"role": lease.role} if lease.role != "stage" else {}),
            **(
                {
                    "gc_predecessor_name": lease.gc_predecessor_name,
                    "gc_ordinal": lease.gc_ordinal,
                }
                if lease.gc_predecessor_name is not None
                else {}
            ),
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
            for action in sorted(journal.actions, key=lambda item: (item.path, item.action, item.reason))
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
    journal_schema_supported = payload["schema_version"] == _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
    journal_intent_supported = payload.get("intent") in {"fresh", "update", "init-force"}
    journal_authority_supported = isinstance(payload.get("authority"), str)
    schema_intent_supported = payload["schema_version"] == _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
    if (
        not journal_schema_supported
        or not schema_intent_supported
        or not journal_intent_supported
        or not journal_authority_supported
        or payload["protocol_version"] not in _DISTRIBUTION_SUPPORTED_JOURNAL_PROTOCOL_VERSIONS
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
            or item["action"] not in {"create", "adopt", "upgrade", "prune", "preserve", "block", "ensure-directory"}
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
        lease_fields = {"path", "stage_name", "device", "inode", "ctime_ns", "file_type"}
        transition_fields = {"gc_predecessor_name", "gc_ordinal"}
        item_fields = frozenset(item) if isinstance(item, dict) else frozenset()
        has_transition = item_fields == frozenset(lease_fields | {"role"} | transition_fields)
        if (
            not isinstance(item, dict)
            or item_fields
            not in {
                frozenset(lease_fields),
                frozenset(lease_fields | {"role"}),
                frozenset(lease_fields | {"role"} | transition_fields),
            }
            or not isinstance(item["path"], str)
            or not isinstance(item["stage_name"], str)
            or PurePosixPath(item["stage_name"]).name != item["stage_name"]
            or any(not isinstance(item[field], int) for field in ("device", "inode", "ctime_ns"))
            or not (
                all(item[field] == 0 for field in ("device", "inode", "ctime_ns"))
                or all(item[field] > 0 for field in ("device", "inode", "ctime_ns"))
            )
            or item["file_type"] not in {"regular", "symlink"}
            or item.get("role", "stage")
            not in {
                "stage",
                "predecessor-quarantine",
                "backup-reserved",
                "backup-dual",
                "backup-only-reserved",
                "backup-only",
                "gc-reserved",
                "gc-exact",
            }
            or (
                has_transition
                and (
                    item.get("role") not in {"gc-reserved", "gc-exact", "backup-only"}
                    or not isinstance(item["gc_predecessor_name"], str)
                    or PurePosixPath(item["gc_predecessor_name"]).name != item["gc_predecessor_name"]
                    or item["gc_predecessor_name"] == item["stage_name"]
                    or not isinstance(item["gc_ordinal"], int)
                    or isinstance(item["gc_ordinal"], bool)
                    or item["gc_ordinal"] not in {1, 2, 3}
                )
            )
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
                role=item.get(
                    "role",
                    "predecessor-quarantine" if item["stage_name"].endswith(".remove") else "stage",
                ),
                gc_predecessor_name=(item["gc_predecessor_name"] if has_transition else None),
                gc_ordinal=(item["gc_ordinal"] if has_transition else None),
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
    prepared_leases_are_guard_inheritable = all(
        lease.role == "stage" and lease.device > 0 and lease.inode > 0 and lease.ctime_ns > 0 for lease in leases
    )
    if (
        (payload["status"] == "prepared" and (checkpoints - {"pending"} or not prepared_leases_are_guard_inheritable))
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

    def __init__(
        self,
        target_root: Path,
        *,
        identity_path: Path | None = None,
        expected_workspace_identity: tuple[int, int] | None = None,
        workspace_closed_set_validator: Callable[[tuple[str, ...]], None] | None = None,
    ) -> None:
        self.target_root = Path(target_root)
        self.identity_path = Path(identity_path) if identity_path is not None else self.target_root
        self.path = self.target_root / _DISTRIBUTION_JOURNAL_REL
        self.expected_workspace_identity = expected_workspace_identity
        self.workspace_closed_set_validator = workspace_closed_set_validator
        self.require_journal_absent = False
        self._forward_guard: DistributionRetryMarker | None = None

    def _validate_workspace_closed_set(self, extra_entries: tuple[str, ...] = ()) -> None:
        if self.require_journal_absent and _path_present_no_follow(self.path):
            raise DistributionApplyError("dual-recovery-state")
        if self.workspace_closed_set_validator is not None:
            self.workspace_closed_set_validator(extra_entries)

    @staticmethod
    def _workspace_condition(journal: OperationJournal) -> dict[str, object]:
        return _path_snapshot_condition(journal.workspace_identity)

    def _open_parent(
        self,
        expected_root: DistributionRootIdentity,
        expected_workspace: dict[str, object] | None = None,
    ) -> tuple[int, int]:
        if expected_workspace is None and self.expected_workspace_identity is not None:
            expected_workspace = {
                "exists": True,
                "file_type": "directory",
                "device": self.expected_workspace_identity[0],
                "inode": self.expected_workspace_identity[1],
            }
        flags = _distribution_directory_flags()
        parent_fd: int | None = None
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
            self._validate_workspace_closed_set()
        except Exception:
            if parent_fd is not None:
                os.close(parent_fd)
            os.close(root_fd)
            raise
        assert parent_fd is not None
        return root_fd, parent_fd

    @staticmethod
    def _same_marker_evidence(
        current: DistributionRetryMarker,
        expected: DistributionRetryMarker,
    ) -> bool:
        return (
            current == expected
            and current.purpose
            in {
                _DISTRIBUTION_JOURNAL_GUARD_PURPOSE,
                _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE,
            }
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
        if guard.journal_digest is not None and journal.source_sha256 not in {
            guard.journal_digest,
            guard.journal_predecessor_digest,
        }:
            raise DistributionApplyError("journal-precondition-mismatch")

    def _anchor_digestless_initial_journal(
        self,
        journal: OperationJournal,
        plan: ExecutableMutationPlan,
    ) -> None:
        guard = self._forward_guard
        if guard is None or guard.journal_digest is not None:
            return
        expected_staging_leases: tuple[DistributionStageOwnership, ...] = ()
        if journal.staging_leases:
            expected_staging_leases = _validated_legacy_stage_leases(
                plan,
                guard,
                self.target_root,
                allow_operation_created_parents=True,
            )
        if (
            journal.status != "prepared"
            or journal.staging_leases != expected_staging_leases
            or any(action.checkpoint != "pending" for action in journal.actions)
            or journal.source_sha256 is None
            or _journal_digest(journal) not in _executable_plan_digest_candidates(plan)
        ):
            raise DistributionApplyError("journal-precondition-mismatch")
        expected_initial = self._initial_journal(
            plan,
            package_version=journal.package_version,
            operation_id=journal.operation_id,
            created_at_ns=journal.created_at_ns,
        )
        if journal.created_parent_bindings != expected_initial.created_parent_bindings:
            raise DistributionApplyError("journal-precondition-mismatch")
        expected_actions = {
            action.path: (
                action.action,
                action.provenance,
                action.reason,
                _action_precondition_payload(plan.distribution_plan, action),
                _action_postcondition_payload(plan.distribution_plan, action),
                _legacy_action_postcondition_payload(plan.distribution_plan, action),
                _legacy_action_postcondition_payload(
                    plan.distribution_plan,
                    action,
                    fixed_link_count=True,
                ),
            )
            for action in plan.actions
        }
        if len(expected_actions) != len(journal.actions):
            raise DistributionApplyError("journal-precondition-mismatch")
        for record in journal.actions:
            expected = expected_actions.get(record.path)
            if expected is None or (record.action, record.provenance, record.reason) != expected[:3]:
                raise DistributionApplyError("journal-precondition-mismatch")
            expected_conditions = [expected[3]]
            if record.action == "adopt" and record.postcondition.get("file_type") != "directory":
                expected_conditions.extend((expected[4], expected[5], expected[6]))
            else:
                expected_conditions.append(expected[4])
            for index, recorded_condition in enumerate((record.precondition, record.postcondition)):
                candidates = expected_conditions if index == 1 else [expected[3]]
                normalized_candidates = [
                    OperationJournalStore._normalize_initial_action_condition(candidate) for candidate in candidates
                ]
                if recorded_condition not in candidates and recorded_condition not in normalized_candidates:
                    raise DistributionApplyError("journal-precondition-mismatch")
        anchored = self.prepare_legacy_guard(
            None,
            package_version=guard.package_version,
            replace_marker=guard,
            stage_ownership=expected_staging_leases,
            journal_digest=journal.source_sha256,
            journal_predecessor_digest=None,
            journal_created_at_ns=journal.created_at_ns,
        )
        self.bind_forward_guard(anchored)

    def _write(
        self,
        journal: OperationJournal,
        *,
        predecessor: OperationJournal | None = None,
        require_absent: bool = False,
    ) -> OperationJournal:
        content = _journal_bytes(journal)
        predecessor_content = _journal_bytes(predecessor) if predecessor is not None else None
        if predecessor is not None and self._forward_guard is not None:
            assert predecessor_content is not None
            predecessor_digest = predecessor.source_sha256 or hashlib.sha256(predecessor_content).hexdigest()
            anchored_guard = self.prepare_legacy_guard(
                None,
                package_version=self._forward_guard.package_version,
                replace_marker=self._forward_guard,
                stage_ownership=self._forward_guard.stage_ownership,
                journal_digest=hashlib.sha256(content).hexdigest(),
                journal_predecessor_digest=predecessor_digest,
            )
            self.bind_forward_guard(anchored_guard)
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
                    or hashlib.sha256(_read_fd_bytes(destination_fd)).hexdigest() != expected_sha256
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
            self._validate_workspace_closed_set((stage,))
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
            else:
                # A write failure can occur before stage_info is captured.  The
                # O_EXCL-created stage is still owned by this operation and
                # must not strand a markerless fresh workspace.
                with suppress(OSError, DistributionApplyError):
                    orphan_info = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
                    _remove_distribution_stage_if_owned(parent_fd, stage, orphan_info)
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

    @staticmethod
    def _normalize_initial_action_condition(condition: dict[str, object]) -> dict[str, object]:
        parents = condition.get("parents")
        if not isinstance(parents, list):
            return condition
        normalized_parents = [
            {
                **parent,
                **(
                    {"ctime_ns": 0, "link_count": 0}
                    if isinstance(parent, dict) and parent.get("relative_path") == "spec-dock"
                    else {}
                ),
            }
            for parent in parents
        ]
        return {**condition, "parents": normalized_parents}

    def _initial_journal(
        self,
        plan: ExecutableMutationPlan,
        *,
        package_version: str,
        operation_id: str,
        created_at_ns: int,
    ) -> OperationJournal:
        try:
            workspace_info = os.lstat(self.target_root / "spec-dock")
        except OSError as exc:
            raise DistributionApplyError("journal-parent-mismatch") from exc
        if stat.S_ISLNK(workspace_info.st_mode) or not stat.S_ISDIR(workspace_info.st_mode):
            raise DistributionApplyError("journal-parent-mismatch")
        if (
            self.expected_workspace_identity is not None
            and (
                workspace_info.st_dev,
                workspace_info.st_ino,
            )
            != self.expected_workspace_identity
        ):
            raise DistributionApplyError("journal-parent-mismatch")
        return OperationJournal(
            schema_version=(
                _DISTRIBUTION_FRESH_JOURNAL_SCHEMA_VERSION
                if plan.intent == "fresh"
                else _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
            ),
            protocol_version=_DISTRIBUTION_JOURNAL_PROTOCOL_VERSION,
            operation_id=operation_id,
            root_identity=plan.root_identity,
            workspace_identity=replace(
                _snapshot_from_stat("spec-dock", workspace_info),
                # Guard and journal publication intentionally mutate this
                # directory's ctime.  The authority boundary is its held
                # dev/inode/type binding, so keep the serialized initial
                # journal reconstructable across a guard-only crash.
                ctime_ns=0,
                link_count=0,
            ),
            intent=plan.intent,
            authority=_journal_authority_for_intent(plan.intent),
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
                    precondition=self._normalize_initial_action_condition(
                        _action_precondition_payload(plan.distribution_plan, action)
                    ),
                    postcondition=self._normalize_initial_action_condition(
                        _action_postcondition_payload(plan.distribution_plan, action)
                    ),
                )
                for action in sorted(plan.actions, key=lambda item: (item.path, item.action, item.reason))
            ),
            created_parent_bindings=tuple(
                _missing_snapshot(path)
                for path in sorted({
                    *{
                        parent.relative_path
                        for action in plan.actions
                        for parent in dict(plan.distribution_plan.target_snapshots)[action.path].parents
                        if not parent.exists
                    },
                    *{
                        action.path
                        for action in plan.actions
                        if action.action == "ensure-directory"
                        and not dict(plan.distribution_plan.target_snapshots)[action.path].target.exists
                    },
                })
            ),
            staging_leases=(),
        )

    def prepare(self, plan: ExecutableMutationPlan, *, package_version: str) -> OperationJournal:
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
        legacy_plan_digests = _executable_plan_digest_candidates(plan)
        if (
            guard.operation_id is None
            or guard.contract_identity != plan.contract_identity
            or guard.plan_digest not in legacy_plan_digests
        ):
            raise DistributionApplyError("dual-recovery-state")
        if guard.plan_digest != plan.plan_digest:
            guard = self.prepare_legacy_guard(
                None,
                package_version=guard.package_version,
                replace_marker=guard,
                plan_digest_override=plan.plan_digest,
                stage_ownership=guard.stage_ownership,
            )
            self.bind_forward_guard(guard)
        operation_id = guard.operation_id
        if operation_id is None:
            raise DistributionApplyError("dual-recovery-state")
        created_at_ns = guard.journal_created_at_ns or time.time_ns()
        journal = replace(
            self._initial_journal(
                plan,
                package_version=package_version,
                operation_id=operation_id,
                created_at_ns=created_at_ns,
            ),
            staging_leases=guard.stage_ownership,
        )
        initial_digest = hashlib.sha256(_journal_bytes(journal)).hexdigest()
        if guard.journal_digest is None:
            guard = self.prepare_legacy_guard(
                None,
                package_version=guard.package_version,
                replace_marker=guard,
                stage_ownership=guard.stage_ownership,
                journal_digest=initial_digest,
                journal_predecessor_digest=None,
                journal_created_at_ns=created_at_ns,
            )
            self.bind_forward_guard(guard)
        elif guard.journal_digest != initial_digest:
            raise DistributionApplyError("journal-precondition-mismatch")
        return self._write(journal, require_absent=True)

    def prepare_legacy_guard(
        self,
        plan: ExecutableMutationPlan | None,
        *,
        package_version: str,
        replace_marker: DistributionRetryMarker | None = None,
        plan_digest_override: str | None = None,
        stage_ownership: tuple[DistributionStageOwnership, ...] = (),
        journal_digest: str | None = None,
        journal_predecessor_digest: str | None = None,
        journal_created_at_ns: int | None = None,
    ) -> DistributionRetryMarker:
        """Publish an old-installer-visible guard before the new journal exists."""

        created_at_ns = time.time_ns()
        if plan is None:
            if replace_marker is None or replace_marker.operation_id is None:
                raise DistributionApplyError("dual-recovery-state")
            operation = replace_marker.operation
            target_root = replace_marker.target_root
            operation_id = replace_marker.operation_id
            contract_identity = replace_marker.contract_identity
            plan_digest = plan_digest_override or replace_marker.plan_digest
        else:
            operation = plan.intent
            target_root = plan.root_identity
            operation_id = hashlib.sha256(
                f"{plan.plan_digest}:{created_at_ns}:{secrets.token_hex(16)}".encode()
            ).hexdigest()
            contract_identity = plan.contract_identity
            plan_digest = plan.plan_digest
            if journal_digest is None:
                initial = replace(
                    self._initial_journal(
                        plan,
                        package_version=package_version,
                        operation_id=operation_id,
                        created_at_ns=created_at_ns,
                    ),
                    staging_leases=stage_ownership,
                )
                journal_digest = hashlib.sha256(_journal_bytes(initial)).hexdigest()
                journal_created_at_ns = created_at_ns
        marker = DistributionRetryMarker(
            operation=operation,
            package_version=package_version,
            target_root=target_root,
            last_completed_phase="preflight-complete",
            purpose=_journal_guard_purpose_for_intent(operation),
            operation_id=operation_id,
            contract_identity=contract_identity,
            plan_digest=plan_digest,
            stage_ownership=stage_ownership,
            journal_digest=journal_digest,
            journal_predecessor_digest=journal_predecessor_digest,
            journal_created_at_ns=(
                None
                if plan_digest_override is not None and journal_digest is None
                else journal_created_at_ns
                if journal_created_at_ns is not None
                else (replace_marker.journal_created_at_ns if replace_marker is not None else None)
            ),
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
            "stage_ownership": [
                {
                    "path": lease.path,
                    "stage_name": lease.stage_name,
                    "device": lease.device,
                    "inode": lease.inode,
                    "ctime_ns": lease.ctime_ns,
                    "file_type": lease.file_type,
                }
                for lease in stage_ownership
            ],
            "operation_id": marker.operation_id,
            "contract_identity": marker.contract_identity,
            "plan_digest": marker.plan_digest,
        }
        if marker.journal_digest is not None:
            payload["journal_digest"] = marker.journal_digest
            payload["journal_predecessor_digest"] = marker.journal_predecessor_digest
            payload["journal_created_at_ns"] = marker.journal_created_at_ns
        content = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        try:
            workspace_info = os.lstat(self.target_root / "spec-dock")
        except OSError as exc:
            raise DistributionApplyError("journal-parent-mismatch") from exc
        if stat.S_ISLNK(workspace_info.st_mode) or not stat.S_ISDIR(workspace_info.st_mode):
            raise DistributionApplyError("journal-parent-mismatch")
        workspace_condition = _path_snapshot_condition(_snapshot_from_stat("spec-dock", workspace_info))
        if self.expected_workspace_identity is not None:
            workspace_condition.update({
                "device": self.expected_workspace_identity[0],
                "inode": self.expected_workspace_identity[1],
            })
        root_fd, parent_fd = self._open_parent(marker.target_root, workspace_condition)
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
            self._validate_workspace_closed_set((stage,))
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
            else:
                # Preserve the original write error while removing a stage
                # whose metadata was not captured before the failure.
                with suppress(OSError, DistributionApplyError):
                    orphan_info = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
                    _remove_distribution_stage_if_owned(parent_fd, stage, orphan_info)
            raise
        finally:
            if stage_fd is not None:
                os.close(stage_fd)
            if held_fd is not None:
                os.close(held_fd)
            os.close(parent_fd)
            os.close(root_fd)

    def restore_marker_bytes(self, marker: DistributionRetryMarker, content: bytes) -> None:
        """Restore a legacy marker after a conversion lost its journal race."""

        expected = marker.source_snapshot
        expected_sha256 = marker.source_sha256
        if expected is None or expected_sha256 is None:
            raise DistributionApplyError("legacy-marker-unconvertible")
        root_fd, parent_fd = self._open_parent(marker.target_root)
        stage = f".distribution-retry-{secrets.token_hex(16)}.restore"
        stage_info: os.stat_result | None = None
        stage_fd: int | None = None
        held_fd: int | None = None
        swapped_out: os.stat_result | None = None
        try:
            try:
                destination_info = os.stat(
                    _DISTRIBUTION_RETRY_MARKER_REL.name,
                    dir_fd=parent_fd,
                    follow_symlinks=False,
                )
            except OSError as exc:
                raise DistributionApplyError("legacy-marker-unconvertible") from exc
            if (
                not stat.S_ISREG(destination_info.st_mode)
                or destination_info.st_nlink != 1
                or destination_info.st_dev != expected.device
                or destination_info.st_ino != expected.inode
                or destination_info.st_ctime_ns != expected.ctime_ns
                or _file_type(destination_info.st_mode) != expected.file_type
                or destination_info.st_nlink != expected.link_count
            ):
                raise DistributionApplyError("legacy-marker-unconvertible")
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise DistributionApplyError("platform lacks required no-follow file support")
            held_fd = os.open(
                _DISTRIBUTION_RETRY_MARKER_REL.name,
                os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent_fd,
            )
            if _stat_identity_tuple(os.fstat(held_fd)) != _stat_identity_tuple(destination_info):
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
            self._validate_workspace_closed_set((stage,))
            swapped_out = _swap_regular_distribution_target_if_bound(
                parent_fd,
                stage,
                _DISTRIBUTION_RETRY_MARKER_REL.name,
                target_fd=held_fd,
                staging_fd=stage_fd,
                expected_target=destination_info,
                identity_message="legacy-marker-unconvertible",
            )
            os.fsync(parent_fd)
            published = os.fstat(stage_fd)
            successor_snapshot = _snapshot_from_stat(
                _DISTRIBUTION_RETRY_MARKER_REL.as_posix(),
                published,
            )
            self._assert_bound_regular_entry(
                parent_fd,
                _DISTRIBUTION_RETRY_MARKER_REL.name,
                stage_fd,
                successor_snapshot,
                hashlib.sha256(content).hexdigest(),
                identity_error="legacy-marker-unconvertible",
            )
            _remove_distribution_stage_if_owned(parent_fd, stage, swapped_out, strict=True)
            os.fsync(parent_fd)
        except Exception:
            if stage_info is not None and swapped_out is None:
                with suppress(OSError, DistributionApplyError):
                    _remove_distribution_stage_if_owned(parent_fd, stage, stage_info, strict=True)
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
        _assert_gc_transition_graph(journal)
        current_guard = _read_distribution_retry_marker(self.target_root)
        if current_guard is None or current_guard.purpose != _journal_guard_purpose_for_intent(plan.intent):
            raise DistributionApplyError("dual-recovery-state")
        self.bind_forward_guard(current_guard)
        if journal.root_identity != plan.root_identity:
            raise DistributionApplyError("journal-root-mismatch")
        if journal.intent != plan.intent:
            raise DistributionApplyError("journal-intent-mismatch")
        if journal.authority != _journal_authority_for_intent(plan.intent):
            raise DistributionApplyError("journal-authority-mismatch")
        if (
            journal.protocol_version not in _DISTRIBUTION_SUPPORTED_JOURNAL_PROTOCOL_VERSIONS
            or not _journal_package_is_compatible(
                journal.package_version,
                package_version,
            )
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        if journal.contract_identity != plan.contract_identity:
            raise DistributionApplyError("journal-contract-mismatch")
        if not _plan_digest_matches(plan, journal.plan_digest):
            raise DistributionApplyError("journal-plan-mismatch")
        if journal.status == "prepared" and journal.staging_leases:
            validated_guard_leases = _validated_legacy_stage_leases(
                plan,
                current_guard,
                self.target_root,
                allow_operation_created_parents=True,
            )
            if journal.staging_leases != validated_guard_leases:
                raise DistributionApplyError("journal-precondition-mismatch")
        self._anchor_digestless_initial_journal(journal, plan)
        self._assert_guard_anchors_journal(journal)
        journal = self._migrate_legacy_protocol_journal(journal, plan.distribution_plan)
        journal = self._resume_displaced_quarantine_cleanup(
            journal,
            {action.path for action in journal.actions if action.checkpoint != "pending"},
        )
        return journal

    def load_for_assessment(
        self,
        assessment: WorkspaceAssessment,
        *,
        package_version: str,
        require_guard: bool = True,
    ) -> OperationJournal:
        journal = self._read(assessment.root_identity)
        _assert_gc_transition_graph(journal)
        if require_guard:
            current_guard = _read_distribution_retry_marker(self.target_root)
            if current_guard is None or current_guard.purpose != _journal_guard_purpose_for_intent(assessment.intent):
                raise DistributionApplyError("dual-recovery-state")
            self.bind_forward_guard(current_guard)
        elif journal.status != "completed":
            raise DistributionApplyError("dual-recovery-state")
        if journal.root_identity != assessment.root_identity:
            raise DistributionApplyError("journal-root-mismatch")
        if journal.intent != assessment.intent:
            raise DistributionApplyError("journal-intent-mismatch")
        if journal.authority != _journal_authority_for_intent(assessment.intent):
            raise DistributionApplyError("journal-authority-mismatch")
        if (
            journal.protocol_version not in _DISTRIBUTION_SUPPORTED_JOURNAL_PROTOCOL_VERSIONS
            or not _journal_package_is_compatible(
                journal.package_version,
                package_version,
            )
        ):
            raise DistributionApplyError("journal-protocol-incompatible")
        if journal.contract_identity != assessment.contract_identity:
            raise DistributionApplyError("journal-contract-mismatch")
        if require_guard:
            if self._forward_guard is not None and self._forward_guard.journal_digest is None:
                self._anchor_digestless_initial_journal(
                    journal,
                    _resume_executable_plan(assessment, journal),
                )
            self._assert_guard_anchors_journal(journal)
            journal = self._migrate_legacy_protocol_journal(journal, assessment.distribution_plan)
            journal = self._resume_displaced_quarantine_cleanup(
                journal,
                {action.path for action in journal.actions if action.checkpoint != "pending"},
            )
        return journal

    def _migrate_legacy_protocol_journal(
        self,
        journal: OperationJournal,
        plan: DistributionPlan,
    ) -> OperationJournal:
        """Promote protocol-1 successor records before current validation.

        Protocol 1 did not persist the structural identity of a published
        regular/symlink successor.  Such a record is compatible only when its
        semantic postcondition still matches the current target; the current
        observation is then write-ahead as the protocol-2 exact binding before
        any further resume or cleanup transition.
        """

        if journal.protocol_version != _DISTRIBUTION_LEGACY_JOURNAL_PROTOCOL_VERSION:
            return journal
        snapshots = dict(plan.target_snapshots)
        migrated_actions: list[OperationJournalAction] = []
        for record in journal.actions:
            if not _is_legacy_successor_postcondition(record):
                migrated_actions.append(record)
                continue
            snapshot = snapshots.get(record.path)
            if snapshot is None or not _snapshot_matches_condition(
                snapshot,
                record.postcondition,
                journal.created_parent_bindings,
            ):
                raise DistributionApplyError("journal-precondition-mismatch")
            target = snapshot.target
            if (
                not target.exists
                or target.file_type == "directory"
                or any(value is None for value in (target.device, target.inode, target.ctime_ns, target.link_count))
            ):
                raise DistributionApplyError("journal-protocol-incompatible")
            migrated_actions.append(
                replace(
                    record,
                    postcondition={
                        **record.postcondition,
                        "device": target.device,
                        "inode": target.inode,
                        "ctime_ns": target.ctime_ns,
                        "link_count": target.link_count,
                    },
                )
            )
        migrated = replace(
            journal,
            protocol_version=_DISTRIBUTION_JOURNAL_PROTOCOL_VERSION,
            actions=tuple(migrated_actions),
        )
        return self.write(migrated, predecessor=journal)

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
        persisted = self._read(journal.root_identity)
        self._assert_guard_anchors_journal(persisted)
        if (
            persisted.operation_id != journal.operation_id
            or persisted.contract_identity != journal.contract_identity
            or persisted.plan_digest != journal.plan_digest
        ):
            raise DistributionApplyError("journal-precondition-mismatch")
        active = self._resume_displaced_quarantine_cleanup(persisted, completed)
        records = {record.path: record for record in journal.actions}
        cleanup_transitions: dict[
            str,
            tuple[DistributionStageOwnership, dict[str, object], dict[str, object]],
        ] = {}
        updated_leases = {lease.path: lease for lease in active.staging_leases}
        leases_changed = False
        for lease in active.staging_leases:
            if lease.path not in completed or lease.role != "stage":
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
                        if record.action == "prune" and _journal_postcondition(record).get("exists") is False:
                            continue
                        raise DistributionApplyError("managed staging cleanup failed") from exc
                    target_identity = _distribution_stage_identity(parent_chain[-1], target_name, lease.path)
                    if (
                        record.action == "adopt"
                        and target_info.st_nlink == 1
                        and _journal_postcondition(record).get("identity")
                        == _distribution_identity_payload(target_identity)
                    ):
                        continue
                    if (
                        target_info.st_dev != lease.device
                        or target_info.st_ino != lease.inode
                        or _file_type(target_info.st_mode) != lease.file_type
                        or target_info.st_nlink != 1
                        or _journal_postcondition(record).get("identity")
                        != _distribution_identity_payload(target_identity)
                    ):
                        raise DistributionApplyError("managed staging cleanup failed") from None
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
                    updated_leases[lease.path] = _distribution_stage_ownership(
                        lease.path,
                        lease.stage_name,
                        stage_info,
                    )
                    leases_changed = True
                    continue
                if (
                    stage_info.st_dev == lease.device
                    and stage_info.st_ino == lease.inode
                    and stage_info.st_ctime_ns == lease.ctime_ns
                    and _file_type(stage_info.st_mode) == lease.file_type
                    and stage_info.st_nlink == 1
                ):
                    continue
                record = records.get(lease.path)
                if record is None or record.action != "upgrade":
                    raise DistributionApplyError("managed staging cleanup failed")
                target_name = PurePosixPath(lease.path).name
                target_info = os.stat(target_name, dir_fd=parent_chain[-1], follow_symlinks=False)
                target_identity = _distribution_stage_identity(parent_chain[-1], target_name, lease.path)
                stage_identity = _distribution_stage_identity(parent_chain[-1], lease.stage_name, lease.path)
                pre = record.precondition
                post = _journal_postcondition(record)
                canonical_is_published_lease = (
                    target_info.st_dev == lease.device
                    and target_info.st_ino == lease.inode
                    and target_info.st_ctime_ns == lease.ctime_ns
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
                cleanup_transitions[lease.path] = (lease, pre, post)
            finally:
                _close_distribution_parent_chain(parent_chain)
        if leases_changed:
            active = self.write(
                replace(
                    active,
                    staging_leases=tuple(updated_leases[lease.path] for lease in active.staging_leases),
                ),
                predecessor=active,
            )
        successor_actions: dict[str, OperationJournalAction] = {}
        for lease in active.staging_leases:
            if lease.path not in completed or lease.role != "stage":
                continue
            record = next((item for item in active.actions if item.path == lease.path), None)
            if record is None or record.action not in {"create", "upgrade"}:
                continue
            if record.postcondition.get("file_type") == "directory":
                continue
            parent_chain = _open_distribution_parent_chain(
                self.target_root,
                lease.path,
                create_missing=False,
            )
            try:
                successor_postcondition = self._capture_exact_canonical_successor(
                    parent_chain[-1],
                    PurePosixPath(lease.path).name,
                    lease.path,
                    lease,
                    record.postcondition,
                )
            finally:
                _close_distribution_parent_chain(parent_chain)
            successor_actions[lease.path] = replace(record, postcondition=successor_postcondition)
        if successor_actions:
            active = self.write(
                replace(
                    active,
                    actions=tuple(successor_actions.get(record.path, record) for record in active.actions),
                ),
                predecessor=active,
            )
        for lease in active.staging_leases:
            if lease.path not in completed or lease.role != "stage":
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
                if lease.path not in cleanup_transitions and (
                    stage_info.st_dev != lease.device
                    or stage_info.st_ino != lease.inode
                    or stage_info.st_ctime_ns != lease.ctime_ns
                    or _file_type(stage_info.st_mode) != lease.file_type
                    or stage_info.st_nlink != 1
                ):
                    raise DistributionApplyError("managed staging cleanup failed")

                def record_cleanup_transition(updated: DistributionStageOwnership) -> None:
                    nonlocal active
                    active = self.record_staging_lease(active, updated)

                _remove_distribution_stage_if_owned(
                    parent_chain[-1],
                    lease.stage_name,
                    stage_info,
                    strict=True,
                    transition_path=lease.path if lease.path in cleanup_transitions else None,
                    canonical_name=(PurePosixPath(lease.path).name if lease.path in cleanup_transitions else None),
                    canonical_ownership=(
                        cleanup_transitions[lease.path][0] if lease.path in cleanup_transitions else None
                    ),
                    canonical_condition=(
                        cleanup_transitions[lease.path][2] if lease.path in cleanup_transitions else None
                    ),
                    stage_condition=(cleanup_transitions[lease.path][1] if lease.path in cleanup_transitions else None),
                    transition_recorder=(record_cleanup_transition if lease.path in cleanup_transitions else None),
                )
            finally:
                _close_distribution_parent_chain(parent_chain)
        actions = tuple(
            replace(action, checkpoint="published")
            if action.path in completed and action.checkpoint == "pending"
            else action
            for action in active.actions
        )
        published = self.write(
            replace(
                active,
                status="executing",
                actions=actions,
            ),
            predecessor=active,
        )
        published_records = {record.path: record for record in published.actions}
        for lease in published.staging_leases:
            if lease.path not in completed or lease.role != "backup-only":
                continue
            parent_chain = _open_distribution_parent_chain(
                self.target_root,
                lease.path,
                create_missing=False,
            )
            try:
                parent_fd = parent_chain[-1]
                backup_name = lease.stage_name
                backup = _stat_optional_no_follow(parent_fd, backup_name)
                if backup is None:
                    continue
                if (
                    backup.st_dev != lease.device
                    or backup.st_ino != lease.inode
                    or backup.st_ctime_ns != lease.ctime_ns
                    or _file_type(backup.st_mode) != lease.file_type
                    or backup.st_nlink != 1
                ):
                    raise DistributionApplyError("managed staging cleanup failed")
                record = published_records.get(lease.path)
                if record is None:
                    raise DistributionApplyError("managed staging cleanup failed")
                target_name = PurePosixPath(lease.path).name
                if record.action == "prune":

                    def validate_prune_backup_gc(
                        bound_parent_fd: int = parent_fd,
                        bound_target_name: str = target_name,
                    ) -> None:
                        if _stat_optional_no_follow(bound_parent_fd, bound_target_name) is not None:
                            raise DistributionApplyError("managed staging cleanup failed")

                    validate_backup_gc: Callable[[], None] = validate_prune_backup_gc
                else:
                    successors = tuple(
                        item for item in published.staging_leases if item.path == lease.path and item.role == "stage"
                    )
                    if len(successors) != 1:
                        raise DistributionApplyError("managed staging cleanup failed")
                    bound_postcondition = _journal_postcondition(record)
                    self._assert_exact_canonical_successor(
                        parent_fd,
                        target_name,
                        lease.path,
                        successors[0],
                        bound_postcondition,
                    )

                    def validate_successor_backup_gc(
                        bound_parent_fd: int = parent_fd,
                        bound_target_name: str = target_name,
                        bound_path: str = lease.path,
                        bound_successor: DistributionStageOwnership = successors[0],
                        bound_postcondition: dict[str, object] = bound_postcondition,
                    ) -> None:
                        self._assert_exact_canonical_successor(
                            bound_parent_fd,
                            bound_target_name,
                            bound_path,
                            bound_successor,
                            bound_postcondition,
                        )

                    validate_backup_gc = validate_successor_backup_gc

                def record_backup_gc(updated: DistributionStageOwnership) -> None:
                    nonlocal published
                    published = self.record_staging_lease(published, updated)

                _remove_distribution_stage_if_owned(
                    parent_fd,
                    backup_name,
                    backup,
                    strict=True,
                    mutation_validator=validate_backup_gc,
                    gc_path=lease.path,
                    gc_recorder=record_backup_gc,
                )
            finally:
                _close_distribution_parent_chain(parent_chain)
        staging_leases = tuple(lease for lease in published.staging_leases if lease.path not in completed)
        return self.write(
            replace(published, staging_leases=staging_leases),
            predecessor=published,
        )

    @staticmethod
    def _capture_exact_canonical_successor(
        parent_fd: int,
        target_name: str,
        path: str,
        successor: DistributionStageOwnership,
        postcondition: dict[str, object],
    ) -> dict[str, object]:
        canonical = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
        canonical_identity = _distribution_stage_identity(parent_fd, target_name, path)
        if (
            canonical.st_dev != successor.device
            or canonical.st_ino != successor.inode
            or _file_type(canonical.st_mode) != successor.file_type
            or canonical.st_nlink != 1
            or postcondition.get("identity") != _distribution_identity_payload(canonical_identity)
        ):
            raise DistributionApplyError("managed staging cleanup failed")
        return {
            **postcondition,
            "device": canonical.st_dev,
            "inode": canonical.st_ino,
            "ctime_ns": canonical.st_ctime_ns,
            "link_count": canonical.st_nlink,
        }

    @staticmethod
    def _assert_exact_canonical_successor(
        parent_fd: int,
        target_name: str,
        path: str,
        successor: DistributionStageOwnership,
        postcondition: dict[str, object],
    ) -> None:
        OperationJournalStore._capture_exact_canonical_successor(
            parent_fd,
            target_name,
            path,
            successor,
            postcondition,
        )

    def _resume_displaced_quarantine_cleanup(
        self,
        journal: OperationJournal,
        completed: set[str],
    ) -> OperationJournal:
        """Finish a write-ahead predecessor quarantine without losing its successor lease."""

        active = self._resume_gc_cleanup(journal)
        active = self._promote_roleless_backup_leases(active)
        records = {record.path: record for record in active.actions}
        quarantine_leases = tuple(
            lease
            for lease in active.staging_leases
            if lease.role == "predecessor-quarantine"
            and (
                lease.path in completed
                or (
                    (record := records.get(lease.path)) is not None
                    and record.checkpoint == "pending"
                    and record.action in {"create", "adopt"}
                )
            )
        )
        if not quarantine_leases:
            return active
        if len({lease.path for lease in quarantine_leases}) != len(quarantine_leases):
            raise DistributionApplyError("managed staging cleanup failed")

        for quarantine_lease in quarantine_leases:
            record = records.get(quarantine_lease.path)
            original_stage_name = quarantine_lease.stage_name.rsplit(".", 2)[0]
            successors = tuple(
                lease
                for lease in active.staging_leases
                if lease.path == quarantine_lease.path
                and lease.role == "stage"
                and (record is None or record.action == "upgrade" or lease.stage_name != original_stage_name)
                and lease.stage_name != _distribution_quarantine_backup_name(quarantine_lease.stage_name)
            )
            backup_leases = tuple(
                lease
                for lease in active.staging_leases
                if lease.path == quarantine_lease.path
                and lease.role in {"backup-reserved", "backup-dual", "backup-only-reserved", "backup-only"}
            )
            if (
                record is None
                or record.action not in {"create", "adopt", "upgrade", "prune"}
                or (record.action == "upgrade" and len(successors) != 1)
                or (record.action != "upgrade" and successors)
            ):
                raise DistributionApplyError("managed staging cleanup failed")
            successor = successors[0] if successors else None
            if successor is not None and not quarantine_lease.stage_name.startswith(f"{successor.stage_name}."):
                raise DistributionApplyError("managed staging cleanup failed")
            try:
                parent_chain = _open_distribution_parent_chain(
                    self.target_root,
                    quarantine_lease.path,
                    create_missing=False,
                )
            except DistributionApplyError as exc:
                raise DistributionApplyError("managed staging cleanup failed") from exc
            try:
                parent_fd = parent_chain[-1]
                target_name = PurePosixPath(quarantine_lease.path).name

                def validate_canonical_authority(
                    bound_record: OperationJournalAction = record,
                    bound_successor: DistributionStageOwnership | None = successor,
                    bound_parent_fd: int = parent_fd,
                    bound_target_name: str = target_name,
                    bound_path: str = quarantine_lease.path,
                ) -> None:
                    if bound_record.action == "upgrade":
                        assert bound_successor is not None
                        self._assert_exact_canonical_successor(
                            bound_parent_fd,
                            bound_target_name,
                            bound_path,
                            bound_successor,
                            _journal_postcondition(bound_record),
                        )
                    elif bound_record.action == "prune":
                        if _stat_optional_no_follow(bound_parent_fd, bound_target_name) is not None:
                            raise DistributionApplyError("managed staging cleanup failed")
                    elif not _entry_matches_journal_condition(
                        bound_parent_fd,
                        bound_target_name,
                        bound_path,
                        bound_record.precondition,
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")

                validate_canonical_authority()
                bound_postcondition = _journal_postcondition(record)
                if successor is not None:
                    self._assert_exact_canonical_successor(
                        parent_fd,
                        target_name,
                        quarantine_lease.path,
                        successor,
                        bound_postcondition,
                    )

                quarantine_info = _stat_optional_no_follow(parent_fd, quarantine_lease.stage_name)
                original_info = _stat_optional_no_follow(parent_fd, original_stage_name)
                backup_name = _distribution_quarantine_backup_name(quarantine_lease.stage_name)
                backup_info = _stat_optional_no_follow(parent_fd, backup_name)

                def record_transition(lease: DistributionStageOwnership) -> None:
                    nonlocal active
                    active = self.record_staging_lease(active, lease)

                if backup_info is not None:
                    if original_info is not None:
                        raise DistributionApplyError("managed staging cleanup failed")
                    if quarantine_info is None:
                        exact_backup = tuple(lease for lease in backup_leases if lease.role == "backup-only")
                        if not exact_backup:
                            reserved_backup = tuple(
                                lease for lease in backup_leases if lease.role == "backup-only-reserved"
                            )
                            dual_backup_leases = tuple(lease for lease in backup_leases if lease.role == "backup-dual")
                            if (
                                len(reserved_backup) != 1
                                or len(dual_backup_leases) != 1
                                or backup_info.st_dev != dual_backup_leases[0].device
                                or backup_info.st_ino != dual_backup_leases[0].inode
                                or _file_type(backup_info.st_mode) != dual_backup_leases[0].file_type
                                or backup_info.st_nlink != 1
                            ):
                                raise DistributionApplyError("managed staging cleanup failed")
                            record_transition(
                                _distribution_stage_ownership(
                                    quarantine_lease.path,
                                    backup_name,
                                    backup_info,
                                    role="backup-only",
                                )
                            )
                            exact_backup = tuple(
                                lease
                                for lease in active.staging_leases
                                if lease.path == quarantine_lease.path and lease.role == "backup-only"
                            )
                        if (
                            len(exact_backup) != 1
                            or backup_info.st_dev != exact_backup[0].device
                            or backup_info.st_ino != exact_backup[0].inode
                            or backup_info.st_ctime_ns != exact_backup[0].ctime_ns
                            or _file_type(backup_info.st_mode) != exact_backup[0].file_type
                            or backup_info.st_nlink != 1
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                    else:
                        exact_dual = tuple(lease for lease in backup_leases if lease.role == "backup-dual")
                        if not exact_dual:
                            reserved_backup = tuple(lease for lease in backup_leases if lease.role == "backup-reserved")
                            quarantine_identity = _distribution_stage_identity(
                                parent_fd,
                                quarantine_lease.stage_name,
                                quarantine_lease.path,
                                allow_backup_link=True,
                            )
                            if (
                                len(reserved_backup) != 1
                                or quarantine_info.st_dev != backup_info.st_dev
                                or quarantine_info.st_ino != backup_info.st_ino
                                or quarantine_info.st_dev != quarantine_lease.device
                                or quarantine_info.st_ino != quarantine_lease.inode
                                or quarantine_info.st_nlink != backup_info.st_nlink
                                or quarantine_info.st_nlink != 2
                                or _file_type(quarantine_info.st_mode) != quarantine_lease.file_type
                                or record.precondition.get("identity")
                                != _distribution_identity_payload(quarantine_identity)
                            ):
                                raise DistributionApplyError("managed staging cleanup failed")
                            record_transition(
                                _distribution_stage_ownership(
                                    quarantine_lease.path,
                                    backup_name,
                                    backup_info,
                                    role="backup-dual",
                                )
                            )
                            exact_dual = tuple(
                                lease
                                for lease in active.staging_leases
                                if lease.path == quarantine_lease.path and lease.role == "backup-dual"
                            )
                        if (
                            len(exact_dual) != 1
                            or quarantine_info.st_dev != backup_info.st_dev
                            or quarantine_info.st_ino != backup_info.st_ino
                            or backup_info.st_dev != exact_dual[0].device
                            or backup_info.st_ino != exact_dual[0].inode
                            or backup_info.st_ctime_ns != exact_dual[0].ctime_ns
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                    backup_leases = tuple(
                        lease
                        for lease in active.staging_leases
                        if lease.path == quarantine_lease.path
                        and lease.role in {"backup-reserved", "backup-dual", "backup-only-reserved", "backup-only"}
                    )
                if quarantine_info is not None and original_info is not None:
                    raise DistributionApplyError("managed staging cleanup failed")

                reserved = quarantine_lease.device == quarantine_lease.inode == quarantine_lease.ctime_ns == 0
                if original_info is not None:
                    if record.action in {"create", "adopt"}:
                        source_leases = tuple(
                            lease
                            for lease in active.staging_leases
                            if lease.path == quarantine_lease.path
                            and lease.role == "stage"
                            and lease.stage_name == original_stage_name
                        )
                        if (
                            len(source_leases) == 1
                            and source_leases[0].device == source_leases[0].inode == source_leases[0].ctime_ns == 0
                            and _file_type(original_info.st_mode) == source_leases[0].file_type
                            and original_info.st_nlink == 1
                        ):
                            record_transition(
                                _distribution_stage_ownership(
                                    quarantine_lease.path,
                                    original_stage_name,
                                    original_info,
                                )
                            )
                            source_leases = tuple(
                                lease
                                for lease in active.staging_leases
                                if lease.path == quarantine_lease.path
                                and lease.role == "stage"
                                and lease.stage_name == original_stage_name
                            )
                        if (
                            len(source_leases) != 1
                            or original_info.st_dev != source_leases[0].device
                            or original_info.st_ino != source_leases[0].inode
                            or original_info.st_ctime_ns != source_leases[0].ctime_ns
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                        _remove_distribution_target_if_bound(
                            parent_fd,
                            original_stage_name,
                            original_info,
                            identity_message="managed staging cleanup failed",
                            transition_path=quarantine_lease.path,
                            transition_name=quarantine_lease.stage_name,
                            transition_recorder=record_transition,
                            canonical_validator=validate_canonical_authority,
                        )
                    else:
                        assert successor is not None
                        _remove_distribution_stage_if_owned(
                            parent_fd,
                            original_stage_name,
                            original_info,
                            strict=True,
                            transition_path=quarantine_lease.path,
                            canonical_name=target_name,
                            canonical_ownership=successor,
                            canonical_condition=_journal_postcondition(record),
                            stage_condition=record.precondition,
                            transition_name=quarantine_lease.stage_name,
                            transition_recorder=record_transition,
                        )
                elif quarantine_info is not None:
                    dual_backup = next(
                        (lease for lease in backup_leases if lease.role == "backup-dual"),
                        None,
                    )
                    quarantine_authority = dual_backup if backup_info is not None else quarantine_lease
                    quarantine_identity = _distribution_stage_identity(
                        parent_fd,
                        quarantine_lease.stage_name,
                        quarantine_lease.path,
                        allow_backup_link=backup_info is not None,
                    )
                    stale_source = next(
                        (
                            lease
                            for lease in active.staging_leases
                            if lease.path == quarantine_lease.path
                            and lease.role == "stage"
                            and lease.stage_name == original_stage_name
                        ),
                        None,
                    )
                    if record.action in {"create", "adopt"}:
                        payload_is_owned = stale_source is not None and (
                            stale_source.device == stale_source.inode == stale_source.ctime_ns == 0
                            or (
                                quarantine_info.st_dev == stale_source.device
                                and quarantine_info.st_ino == stale_source.inode
                            )
                        )
                    else:
                        payload_is_owned = record.precondition.get("identity") == _distribution_identity_payload(
                            quarantine_identity
                        )
                    if (
                        _file_type(quarantine_info.st_mode) != quarantine_lease.file_type
                        or quarantine_info.st_nlink not in ({1, 2} if backup_info is not None else {1})
                        or not payload_is_owned
                        or (
                            not reserved
                            and (
                                quarantine_authority is None
                                or quarantine_info.st_dev != quarantine_authority.device
                                or quarantine_info.st_ino != quarantine_authority.inode
                                or quarantine_info.st_ctime_ns != quarantine_authority.ctime_ns
                            )
                        )
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    if reserved:
                        record_transition(
                            _distribution_stage_ownership(
                                quarantine_lease.path,
                                quarantine_lease.stage_name,
                                quarantine_info,
                                role="predecessor-quarantine",
                            )
                        )
                    validate_canonical_authority()

                    def validate_canonical_for_unlink(
                        bound_parent_fd: int = parent_fd,
                        bound_target_name: str = target_name,
                        bound_path: str = quarantine_lease.path,
                        bound_successor: DistributionStageOwnership | None = successor,
                        bound_postcondition: dict[str, object] = bound_postcondition,
                        bound_action: str = record.action,
                    ) -> None:
                        if bound_action in {"create", "adopt", "prune"}:
                            validate_canonical_authority()
                        else:
                            assert bound_successor is not None
                            self._assert_exact_canonical_successor(
                                bound_parent_fd,
                                bound_target_name,
                                bound_path,
                                bound_successor,
                                bound_postcondition,
                            )

                    _unlink_distribution_quarantine_with_backup(
                        parent_fd,
                        quarantine_lease.stage_name,
                        original_stage_name,
                        quarantine_info,
                        canonical_validator=validate_canonical_for_unlink,
                        mutation_validator=None,
                        allow_existing_backup=True,
                        backup_recorder=record_transition,
                        transition_path=quarantine_lease.path,
                    )
                elif reserved:
                    raise DistributionApplyError("managed staging cleanup failed")
            finally:
                _close_distribution_parent_chain(parent_chain)

            retained_backup = next(
                (
                    lease
                    for lease in active.staging_leases
                    if lease.path == quarantine_lease.path and lease.role == "backup-only"
                ),
                None,
            )
            if retained_backup is None:
                raise DistributionApplyError("managed staging cleanup failed")
            parent_chain = _open_distribution_parent_chain(
                self.target_root,
                quarantine_lease.path,
                create_missing=False,
            )
            try:
                parent_fd = parent_chain[-1]
                validate_canonical_authority()
                backup_name = retained_backup.stage_name
                backup = _stat_optional_no_follow(parent_fd, backup_name)
                if backup is not None:
                    if (
                        backup.st_dev != retained_backup.device
                        or backup.st_ino != retained_backup.inode
                        or backup.st_ctime_ns != retained_backup.ctime_ns
                        or _file_type(backup.st_mode) != retained_backup.file_type
                        or backup.st_nlink != 1
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")

                    def validate_backup_gc() -> None:
                        validate_canonical_authority()

                    _remove_distribution_stage_if_owned(
                        parent_fd,
                        backup_name,
                        backup,
                        strict=True,
                        mutation_validator=validate_backup_gc,
                        gc_path=quarantine_lease.path,
                        gc_recorder=record_transition,
                    )
            finally:
                _close_distribution_parent_chain(parent_chain)

            retained = tuple(
                lease
                for lease in active.staging_leases
                if not (
                    lease.path == quarantine_lease.path
                    and (
                        lease.role
                        in {
                            "predecessor-quarantine",
                            "backup-reserved",
                            "backup-dual",
                            "backup-only-reserved",
                            "backup-only",
                            "gc-reserved",
                            "gc-exact",
                        }
                        or (
                            record.action in {"create", "adopt"}
                            and lease.role == "stage"
                            and lease.stage_name == original_stage_name
                        )
                    )
                )
            )
            active = self.write(replace(active, staging_leases=retained), predecessor=active)
        return active

    def _resume_gc_cleanup(self, journal: OperationJournal) -> OperationJournal:
        """Finish journal-owned private-name GC before any target action resumes."""

        _assert_gc_transition_graph(journal)
        active = journal
        records = {record.path: record for record in active.actions}
        gc_leases = _ordered_gc_transition_leases(active)
        for stale_gc_lease in gc_leases:
            current_gc = tuple(
                lease
                for lease in active.staging_leases
                if lease.path == stale_gc_lease.path
                and lease.stage_name == stale_gc_lease.stage_name
                and lease.role in {"gc-reserved", "gc-exact"}
            )
            if not current_gc:
                continue
            if len(current_gc) != 1:
                raise DistributionApplyError("managed staging cleanup failed")
            gc_lease = current_gc[0]
            record = records.get(gc_lease.path)
            if record is None:
                raise DistributionApplyError("managed staging cleanup failed")
            original_name = gc_lease.gc_predecessor_name or gc_lease.stage_name.rsplit(".", 2)[0]
            sources = tuple(
                lease
                for lease in active.staging_leases
                if lease.path == gc_lease.path and lease.stage_name == original_name
            )
            source_candidates = tuple(lease for lease in sources if lease.role == "stage") or sources
            if not source_candidates and gc_lease.role == "gc-exact" and gc_lease.gc_predecessor_name is not None:
                source_candidates = (gc_lease,)
            backup_sources = _explicit_gc_backup_sources(active, gc_lease)
            if len(backup_sources) > 1:
                raise DistributionApplyError("managed staging cleanup failed")
            backup_source = backup_sources[0] if backup_sources else None
            if (
                not source_candidates
                and gc_lease.gc_ordinal == 2
                and gc_lease.gc_predecessor_name is not None
                and backup_source is not None
            ):
                source_candidates = (backup_source,)
            if len(source_candidates) != 1:
                raise DistributionApplyError("managed staging cleanup failed")
            source = source_candidates[0]
            parallel_predecessor_name = (
                backup_source.stage_name
                if backup_source is not None
                else next(
                    (
                        _distribution_quarantine_backup_name(lease.stage_name)
                        for lease in active.staging_leases
                        if lease.path == gc_lease.path and lease.role == "predecessor-quarantine"
                    ),
                    None,
                )
            )
            successor_gc = next(
                (
                    lease
                    for lease in active.staging_leases
                    if lease.path == gc_lease.path
                    and lease.stage_name != gc_lease.stage_name
                    and lease.role in {"gc-reserved", "gc-exact"}
                    and lease.gc_predecessor_name == gc_lease.stage_name
                    and lease.gc_ordinal is not None
                    and gc_lease.gc_ordinal is not None
                    and lease.gc_ordinal == gc_lease.gc_ordinal + 1
                ),
                None,
            )
            parallel_gc = next(
                (
                    lease
                    for lease in active.staging_leases
                    if lease.path == gc_lease.path
                    and lease.stage_name != gc_lease.stage_name
                    and lease.role in {"gc-reserved", "gc-exact", "backup-only"}
                    and gc_lease.gc_ordinal == 2
                    and lease.gc_ordinal == 3
                    and parallel_predecessor_name is not None
                    and lease.gc_predecessor_name == parallel_predecessor_name
                ),
                None,
            )
            transition_continues = successor_gc is not None or parallel_gc is not None
            parent_chain = _open_distribution_parent_chain(
                self.target_root,
                gc_lease.path,
                create_missing=False,
            )
            try:
                parent_fd = parent_chain[-1]
                target_name = PurePosixPath(gc_lease.path).name

                def validate_gc_authority(
                    bound_record: OperationJournalAction = record,
                    bound_parent_fd: int = parent_fd,
                    bound_target_name: str = target_name,
                    bound_path: str = gc_lease.path,
                ) -> None:
                    _assert_created_parent_bindings_closed_set(self.target_root, active)  # noqa: B023
                    if bound_record.checkpoint == "pending" and bound_record.action in {"create", "adopt"}:
                        condition = bound_record.precondition
                    else:
                        condition = _journal_postcondition(bound_record)
                    if not _entry_matches_journal_condition(
                        bound_parent_fd,
                        bound_target_name,
                        bound_path,
                        condition,
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")

                original = _stat_optional_no_follow(parent_fd, original_name)
                quarantined = _stat_optional_no_follow(parent_fd, gc_lease.stage_name)
                successor_info = (
                    _stat_optional_no_follow(parent_fd, successor_gc.stage_name) if successor_gc is not None else None
                )
                parallel_info = (
                    _stat_optional_no_follow(parent_fd, parallel_gc.stage_name) if parallel_gc is not None else None
                )
                backup_info = (
                    _stat_optional_no_follow(parent_fd, backup_source.stage_name) if backup_source is not None else None
                )

                def record_gc(updated: DistributionStageOwnership) -> None:
                    nonlocal active
                    active = self.record_staging_lease(active, updated)

                if quarantined is None and (successor_info is not None or parallel_info is not None):
                    continuation_info = successor_info or parallel_info
                    assert continuation_info is not None
                    if (
                        continuation_info.st_dev != gc_lease.device
                        or continuation_info.st_ino != gc_lease.inode
                        or _file_type(continuation_info.st_mode) != gc_lease.file_type
                        or continuation_info.st_nlink not in {1, 2}
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    if (
                        parallel_gc is not None
                        and parallel_info is not None
                        and parallel_gc.role == "gc-exact"
                        and parallel_gc.gc_ordinal == 3
                        and parallel_info.st_nlink == 1
                    ):
                        record_gc(
                            _distribution_stage_ownership(
                                gc_lease.path,
                                parallel_gc.stage_name,
                                parallel_info,
                                role="backup-only",
                                gc_predecessor_name=parallel_gc.gc_predecessor_name,
                                gc_ordinal=parallel_gc.gc_ordinal,
                            )
                        )
                elif quarantined is None and original is not None:
                    if gc_lease.gc_ordinal == 3 and gc_lease.gc_predecessor_name is not None:
                        if (
                            original.st_dev != source.device
                            or original.st_ino != source.inode
                            or _file_type(original.st_mode) != source.file_type
                            or original.st_nlink not in {1, 2}
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                        validate_gc_authority()
                        _rename_distribution_no_replace(
                            parent_fd,
                            original_name,
                            parent_fd,
                            gc_lease.stage_name,
                        )
                        os.fsync(parent_fd)
                        promoted = os.stat(gc_lease.stage_name, dir_fd=parent_fd, follow_symlinks=False)
                        if (
                            promoted.st_dev != source.device
                            or promoted.st_ino != source.inode
                            or _file_type(promoted.st_mode) != source.file_type
                            or promoted.st_nlink not in {1, 2}
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                        record_gc(
                            _distribution_stage_ownership(
                                gc_lease.path,
                                gc_lease.stage_name,
                                promoted,
                                role="gc-exact",
                                gc_predecessor_name=gc_lease.gc_predecessor_name,
                                gc_ordinal=gc_lease.gc_ordinal,
                            )
                        )
                        return self._resume_gc_cleanup(active)
                    if (
                        original.st_dev != source.device
                        or original.st_ino != source.inode
                        or (gc_lease.role != "gc-reserved" and original.st_ctime_ns != source.ctime_ns)
                        or _file_type(original.st_mode) != source.file_type
                        or original.st_nlink != 1
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    _remove_distribution_stage_if_owned(
                        parent_fd,
                        original_name,
                        original,
                        strict=True,
                        mutation_validator=validate_gc_authority,
                        gc_path=gc_lease.path,
                        gc_recorder=record_gc,
                        gc_name=gc_lease.stage_name,
                        gc_ordinal=gc_lease.gc_ordinal or 1,
                        gc_predecessor_name=original_name,
                    )
                    quarantined = None
                elif quarantined is not None:
                    if gc_lease.role == "gc-reserved":
                        if (
                            quarantined.st_dev != source.device
                            or quarantined.st_ino != source.inode
                            or _file_type(quarantined.st_mode) != source.file_type
                            or quarantined.st_nlink not in {1, 2}
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                        record_gc(
                            DistributionStageOwnership(
                                path=gc_lease.path,
                                stage_name=gc_lease.stage_name,
                                device=quarantined.st_dev,
                                inode=quarantined.st_ino,
                                ctime_ns=quarantined.st_ctime_ns,
                                file_type=("regular" if stat.S_ISREG(quarantined.st_mode) else "symlink"),
                                role="gc-exact",
                                gc_predecessor_name=gc_lease.gc_predecessor_name,
                                gc_ordinal=gc_lease.gc_ordinal,
                            )
                        )
                        gc_lease = next(
                            lease
                            for lease in active.staging_leases
                            if lease.path == gc_lease.path
                            and lease.stage_name == gc_lease.stage_name
                            and lease.role == "gc-exact"
                        )
                    exact_backup_authority = (
                        backup_source is not None
                        and backup_info is not None
                        and backup_info.st_dev == quarantined.st_dev == gc_lease.device
                        and backup_info.st_ino == quarantined.st_ino == gc_lease.inode
                        and _file_type(backup_info.st_mode) == _file_type(quarantined.st_mode) == gc_lease.file_type
                        and backup_info.st_nlink == quarantined.st_nlink == 2
                        and (
                            backup_source.role == "backup-reserved"
                            or (
                                gc_lease.gc_ordinal == 2
                                and gc_lease.gc_predecessor_name is not None
                                and (
                                    parallel_gc is None
                                    or (
                                        parallel_gc.gc_ordinal == 3
                                        and parallel_gc.gc_predecessor_name == backup_source.stage_name
                                    )
                                )
                            )
                            or (
                                backup_info.st_dev == backup_source.device
                                and backup_info.st_ino == backup_source.inode
                                and backup_info.st_ctime_ns == backup_source.ctime_ns
                                and _file_type(backup_info.st_mode) == backup_source.file_type
                            )
                        )
                    )
                    exact_peer_authority = (
                        parallel_gc is not None
                        and parallel_info is not None
                        and original is None
                        and parallel_info.st_dev == quarantined.st_dev == gc_lease.device
                        and parallel_info.st_ino == quarantined.st_ino == gc_lease.inode
                        and _file_type(parallel_info.st_mode) == _file_type(quarantined.st_mode) == gc_lease.file_type
                        and quarantined.st_nlink == 2
                    )
                    exact_terminal_authority = (
                        gc_lease.gc_ordinal == 3
                        and gc_lease.gc_predecessor_name is not None
                        and original is None
                        and quarantined.st_nlink == 1
                        and backup_source is not None
                        and backup_source.role == "backup-dual"
                        and backup_source.device == quarantined.st_dev == gc_lease.device
                        and backup_source.inode == quarantined.st_ino == gc_lease.inode
                        and backup_source.file_type == _file_type(quarantined.st_mode) == gc_lease.file_type
                        and not any(
                            lease.path == gc_lease.path
                            and lease.role in {"gc-reserved", "gc-exact"}
                            and lease.gc_ordinal is not None
                            and lease.gc_ordinal < 3
                            for lease in active.staging_leases
                        )
                    )
                    transition_continues = transition_continues or exact_peer_authority
                    if (
                        quarantined.st_dev != gc_lease.device
                        or quarantined.st_ino != gc_lease.inode
                        or (
                            quarantined.st_ctime_ns != gc_lease.ctime_ns
                            and not exact_backup_authority
                            and not exact_peer_authority
                            and not exact_terminal_authority
                        )
                        or _file_type(quarantined.st_mode) != gc_lease.file_type
                        or quarantined.st_nlink not in {1, 2}
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    if (
                        quarantined.st_nlink == 2
                        and not exact_peer_authority
                        and not exact_backup_authority
                        and (
                            original is None
                            or original.st_dev != quarantined.st_dev
                            or original.st_ino != quarantined.st_ino
                            or original.st_nlink != 2
                        )
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    validate_gc_authority()
                    verified = os.stat(gc_lease.stage_name, dir_fd=parent_fd, follow_symlinks=False)
                    if _stat_identity_tuple(verified) != _stat_identity_tuple(quarantined):
                        raise DistributionApplyError("managed staging cleanup failed")
                    os.unlink(gc_lease.stage_name, dir_fd=parent_fd)
                    os.fsync(parent_fd)
                    retained_peer_name = (
                        parallel_gc.stage_name if exact_peer_authority and parallel_gc is not None else None
                    )
                    retained_backup_name = (
                        backup_source.stage_name
                        if exact_backup_authority
                        and backup_source is not None
                        and successor_gc is None
                        and parallel_gc is None
                        else None
                    )
                    if (
                        (original is not None and successor_gc is not None)
                        or retained_peer_name is not None
                        or retained_backup_name is not None
                    ):
                        retained_source_name = retained_peer_name or retained_backup_name or original_name
                        retained_source = os.stat(retained_source_name, dir_fd=parent_fd, follow_symlinks=False)
                        if original is not None and successor_gc is not None:
                            record_gc(
                                replace(
                                    successor_gc,
                                    gc_predecessor_name=original_name,
                                    gc_ordinal=3,
                                )
                            )
                        record_gc(
                            _distribution_stage_ownership(
                                gc_lease.path,
                                retained_source_name,
                                retained_source,
                                role="backup-only",
                                gc_predecessor_name=(
                                    (
                                        parallel_gc.gc_predecessor_name
                                        if retained_peer_name is not None and parallel_gc is not None
                                        else gc_lease.stage_name
                                    )
                                    if retained_peer_name is not None or retained_backup_name is not None
                                    else None
                                ),
                                gc_ordinal=(
                                    (
                                        parallel_gc.gc_ordinal
                                        if retained_peer_name is not None and parallel_gc is not None
                                        else 3
                                    )
                                    if retained_peer_name is not None or retained_backup_name is not None
                                    else None
                                ),
                            )
                        )
                        transition_continues = True
                    validate_gc_authority()
                    if original is not None and successor_gc is None:
                        retained_source = os.stat(original_name, dir_fd=parent_fd, follow_symlinks=False)
                        if (
                            retained_source.st_dev != quarantined.st_dev
                            or retained_source.st_ino != quarantined.st_ino
                            or retained_source.st_nlink != 1
                        ):
                            raise DistributionApplyError("managed staging cleanup failed")
                        os.unlink(original_name, dir_fd=parent_fd)
                        os.fsync(parent_fd)
            finally:
                _close_distribution_parent_chain(parent_chain)
            completed_quarantines = {
                lease.stage_name
                for lease in active.staging_leases
                if lease.path == gc_lease.path
                and lease.role == "predecessor-quarantine"
                and _distribution_quarantine_backup_name(lease.stage_name) == original_name
            }
            if not transition_continues and source.role == "backup-only" and len(completed_quarantines) != 1:
                raise DistributionApplyError("managed staging cleanup failed")
            retained = tuple(
                lease
                for lease in active.staging_leases
                if not (
                    lease.path == gc_lease.path
                    and (
                        (
                            not transition_continues
                            and lease.role
                            in {
                                "gc-reserved",
                                "gc-exact",
                                "backup-reserved",
                                "backup-dual",
                                "backup-only-reserved",
                                "backup-only",
                            }
                        )
                        or (
                            transition_continues
                            and lease.stage_name == gc_lease.stage_name
                            and lease.role in {"gc-reserved", "gc-exact"}
                        )
                        or lease.stage_name == gc_lease.stage_name
                        or (not transition_continues and lease.stage_name == original_name)
                        or (not transition_continues and lease.stage_name in completed_quarantines)
                    )
                )
            )
            active = self.write(replace(active, staging_leases=retained), predecessor=active)
        return active

    def _promote_roleless_backup_leases(self, journal: OperationJournal) -> OperationJournal:
        """Upgrade prior roleless backup records only from their exact namespace state."""

        active = journal
        records = {record.path: record for record in active.actions}
        quarantine_leases = tuple(lease for lease in active.staging_leases if lease.role == "predecessor-quarantine")
        for quarantine in quarantine_leases:
            backup_name = _distribution_quarantine_backup_name(quarantine.stage_name)
            roleless = tuple(
                lease
                for lease in active.staging_leases
                if lease.path == quarantine.path and lease.role == "stage" and lease.stage_name == backup_name
            )
            explicit_backups = tuple(
                lease
                for lease in active.staging_leases
                if lease.path == quarantine.path
                and lease.stage_name == backup_name
                and lease.role in {"backup-reserved", "backup-dual", "backup-only-reserved", "backup-only"}
            )
            if explicit_backups:
                continue
            if len(roleless) > 1:
                raise DistributionApplyError("managed staging cleanup failed")
            # 55796 serialized the recovery inode only once under the
            # roleless ``.remove`` name.  Its derived backup pathname was not
            # separately journaled, so the parser exposes only the inferred
            # predecessor role.  Later role-aware recovery may promote that
            # exact inode only after proving the derived backup namespace.
            legacy = roleless[0] if roleless else quarantine
            record = records.get(quarantine.path)
            if record is None or record.action not in {"upgrade", "prune"}:
                if not roleless:
                    continue
                raise DistributionApplyError("managed staging cleanup failed")
            parent_chain = _open_distribution_parent_chain(
                self.target_root,
                quarantine.path,
                create_missing=False,
            )
            try:
                parent_fd = parent_chain[-1]
                backup = _stat_optional_no_follow(parent_fd, backup_name)
                visible_quarantine = _stat_optional_no_follow(parent_fd, quarantine.stage_name)
                if backup is None and not roleless:
                    continue
                if (
                    backup is None
                    or backup.st_dev != legacy.device
                    or backup.st_ino != legacy.inode
                    or (backup.st_ctime_ns != legacy.ctime_ns and bool(roleless))
                    or _file_type(backup.st_mode) != legacy.file_type
                ):
                    raise DistributionApplyError("managed staging cleanup failed")
                backup_identity = _distribution_stage_identity(
                    parent_fd,
                    backup_name,
                    quarantine.path,
                    allow_backup_link=visible_quarantine is not None,
                )
                if record.precondition.get("identity") != _distribution_identity_payload(backup_identity):
                    raise DistributionApplyError("managed staging cleanup failed")
                if visible_quarantine is None:
                    if backup.st_nlink != 1:
                        raise DistributionApplyError("managed staging cleanup failed")
                    role: Literal["backup-dual", "backup-only"] = "backup-only"
                else:
                    if (
                        backup.st_nlink != 2
                        or visible_quarantine.st_dev != backup.st_dev
                        or visible_quarantine.st_ino != backup.st_ino
                        or visible_quarantine.st_nlink != 2
                    ):
                        raise DistributionApplyError("managed staging cleanup failed")
                    role = "backup-dual"
                promoted = DistributionStageOwnership(
                    path=quarantine.path,
                    stage_name=backup_name,
                    device=backup.st_dev,
                    inode=backup.st_ino,
                    ctime_ns=backup.st_ctime_ns,
                    file_type=quarantine.file_type,
                    role=role,
                )
            finally:
                _close_distribution_parent_chain(parent_chain)
            retained = tuple(item for item in active.staging_leases if not roleless or item is not legacy)
            active = self.write(
                replace(active, staging_leases=(*retained, promoted)),
                predecessor=active,
            )
        return active

    def record_staging_lease(
        self,
        journal: OperationJournal,
        lease: DistributionStageOwnership,
    ) -> OperationJournal:
        backup_roles = {
            "backup-reserved",
            "backup-dual",
            "backup-only-reserved",
            "backup-only",
        }
        gc_roles = {"gc-reserved", "gc-exact"}
        if lease.role == "predecessor-quarantine":
            retained = tuple(
                item
                for item in journal.staging_leases
                if not (item.path == lease.path and item.role == "predecessor-quarantine")
            )
        elif lease.role in backup_roles:
            retained = tuple(
                item
                for item in journal.staging_leases
                if not (
                    item.path == lease.path
                    and (
                        (
                            item.role in backup_roles
                            and (
                                lease.role in {"backup-only", "backup-reserved", "backup-dual"}
                                or item.role == lease.role
                            )
                        )
                        or (
                            lease.role == "backup-only"
                            and item.role in gc_roles
                            and item.stage_name == lease.stage_name
                        )
                    )
                )
            )
        elif lease.role in gc_roles:
            retained = tuple(
                item
                for item in journal.staging_leases
                if not (item.path == lease.path and item.stage_name == lease.stage_name and item.role in gc_roles)
            )
        else:
            retained = tuple(item for item in journal.staging_leases if item.path != lease.path or item.role != "stage")
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
        self._assert_published_successor_postconditions(journal)
        actions = tuple(replace(action, checkpoint="verified") for action in journal.actions)
        return self.write(replace(journal, status="verifying", actions=actions), predecessor=journal)

    def mark_completed(self, journal: OperationJournal) -> OperationJournal:
        if journal.staging_leases or any(action.checkpoint != "verified" for action in journal.actions):
            raise DistributionApplyError("journal-precondition-mismatch")
        self._assert_published_successor_postconditions(journal)
        return self.write(replace(journal, status="completed"), predecessor=journal)

    def _assert_published_successor_postconditions(self, journal: OperationJournal) -> None:
        for record in journal.actions:
            if record.action not in {"create", "upgrade"} or record.checkpoint == "pending":
                continue
            condition = _journal_postcondition(record)
            if any(field not in condition for field in ("device", "inode", "ctime_ns", "link_count")):
                raise DistributionApplyError("journal-protocol-incompatible")
            parent_chain = _open_distribution_parent_chain(
                self.target_root,
                record.path,
                create_missing=False,
            )
            try:
                if not _entry_matches_journal_condition(
                    parent_chain[-1],
                    PurePosixPath(record.path).name,
                    record.path,
                    condition,
                ):
                    raise DistributionApplyError("journal-precondition-mismatch")
            finally:
                _close_distribution_parent_chain(parent_chain)

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
        root_fd, parent_fd = self._open_parent(journal.root_identity, self._workspace_condition(journal))
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
        if marker.purpose in {
            _DISTRIBUTION_JOURNAL_GUARD_PURPOSE,
            _DISTRIBUTION_FRESH_JOURNAL_GUARD_PURPOSE,
        }:
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
    payload: dict[str, object] = {
        "schema_version": (
            _DISTRIBUTION_FRESH_JOURNAL_SCHEMA_VERSION
            if journal.intent == "fresh"
            else _DISTRIBUTION_JOURNAL_SCHEMA_VERSION
        ),
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
                "postcondition": _plan_digest_condition(_journal_digest_postcondition(action)),
            }
            for action in journal.actions
        ],
    }
    if journal.intent == "fresh":
        required_directories: list[str] = []
        for action in journal.actions:
            identity = action.postcondition.get("identity")
            if (
                action.postcondition.get("file_type") == "directory"
                and isinstance(identity, dict)
                and identity.get("kind") == "directory"
            ):
                required_directories.append(action.path)
        payload["required_directories"] = required_directories
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _journal_digest_postcondition(action: OperationJournalAction) -> dict[str, object]:
    """Exclude runtime successor identity from the canonical plan digest."""

    condition = action.postcondition
    if action.action not in {"create", "upgrade"} or condition.get("file_type") == "directory":
        return condition
    return {key: value for key, value in condition.items() if key not in {"device", "inode", "ctime_ns"}}


def _is_legacy_adopt_postcondition(record: OperationJournalAction) -> bool:
    condition = record.postcondition
    return (
        record.action == "adopt"
        and condition.get("exists") is True
        and condition.get("file_type") != "directory"
        and not {"device", "inode", "ctime_ns"}.intersection(condition)
        and set(condition) == {"root", "parents", "exists", "file_type", "link_count", "identity"}
        and all(field in record.precondition for field in ("device", "inode", "ctime_ns", "link_count"))
    )


def _is_legacy_successor_postcondition(record: OperationJournalAction) -> bool:
    condition = record.postcondition
    return (
        record.checkpoint != "pending"
        and record.action in {"create", "upgrade"}
        and condition.get("exists") is True
        and condition.get("file_type") in {"regular", "symlink"}
        and not {"device", "inode", "ctime_ns"}.intersection(condition)
        and set(condition) == {"root", "parents", "exists", "file_type", "link_count", "identity"}
        and condition.get("link_count") == 1
    )


def _journal_postcondition(record: OperationJournalAction) -> dict[str, object]:
    """Return a validated postcondition view across protocol-1 revisions.

    Protocol 1 journals written before Issue 369's structural-identity
    strengthening contain a non-directory ``adopt`` postcondition without
    device/inode/ctime.  The precondition was already required to capture the
    complete structural identity, so derive all structural fields from that
    immutable witness.  This covers both the original fixed-link-count
    serializer and the intermediate symlink serializer without weakening
    replacement detection.  Malformed or partially expanded shapes are
    returned unchanged and remain fail-closed in the normal contract validator.
    """

    condition = record.postcondition
    if not _is_legacy_adopt_postcondition(record):
        return condition
    precondition = record.precondition
    required = ("device", "inode", "ctime_ns", "link_count")
    if any(field not in precondition for field in required):
        return condition
    return {
        **condition,
        "device": precondition["device"],
        "inode": precondition["inode"],
        "ctime_ns": precondition["ctime_ns"],
        "link_count": precondition["link_count"],
    }


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
    directory_metadata_wildcard = condition.get("file_type") == "directory" and condition.get("identity") is None
    directory_wildcard = (
        condition.get("file_type") == "directory"
        and condition.get("identity")
        == {
            "kind": "directory",
            "sha256": None,
            "mode": None,
            "target": None,
        }
        and condition.get("device") == 0
        and condition.get("inode") == 0
    )
    identity_condition = condition.get("identity")
    directory_identity_wildcard = (
        condition.get("file_type") == "directory"
        and isinstance(identity_condition, dict)
        and identity_condition.get("kind") == "directory"
        and not directory_wildcard
    )
    if "device" in condition and condition.get("device") not in ({0} if directory_wildcard else {target.device}):
        return False
    if "inode" in condition and condition.get("inode") not in ({0} if directory_wildcard else {target.inode}):
        return False
    if (
        "ctime_ns" in condition
        and not directory_metadata_wildcard
        and not directory_identity_wildcard
        and condition.get("ctime_ns") not in ({0} if directory_wildcard else {target.ctime_ns})
    ):
        return False
    if "file_type" in condition and condition.get("file_type") != target.file_type:
        return False
    if "link_count" in condition and not directory_metadata_wildcard and not directory_identity_wildcard:
        expected_link_count = condition.get("link_count")
        workbench_seed_hard_link = (
            target.relative_path == "spec-dock/.workbench/README.md"
            and target.file_type == "regular"
            and condition.get("file_type") == "regular"
            and condition.get("identity") == _distribution_identity_payload(target.identity)
            and expected_link_count == 1
            and isinstance(target.link_count, int)
            and target.link_count >= 1
        )
        if not workbench_seed_hard_link and expected_link_count not in (
            {0} if directory_wildcard else {target.link_count}
        ):
            return False
    if directory_wildcard:
        bound_target = bound_parents.get(target.relative_path)
        if bound_target is not None:
            return (
                target.file_type == "directory"
                and target.exists
                and bound_target.exists
                and _same_structure_identity(target, bound_target)
            )
        # The fresh workspace is bound separately by OperationJournalStore's
        # root/workspace identity checks; it is the only directory postcondition
        # that intentionally has no created-parent record.
        return target.relative_path == "spec-dock" and target.file_type == "directory" and target.exists
    if directory_identity_wildcard:
        return target.file_type == "directory" and target.exists
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
    if condition["file_type"] == "directory" and condition["identity"] is None:
        return all(
            isinstance(condition[field], int) and not isinstance(condition[field], bool)
            for field in ("device", "inode", "ctime_ns", "link_count")
        )
    return (
        all(
            isinstance(condition[field], int) and not isinstance(condition[field], bool)
            for field in ("device", "inode", "ctime_ns", "link_count")
        )
        and isinstance(condition["file_type"], str)
        and isinstance(condition["identity"], dict)
    )


def _explicit_gc_backup_sources(
    journal: OperationJournal,
    gc_lease: DistributionStageOwnership,
) -> tuple[DistributionStageOwnership, ...]:
    predecessor_name = gc_lease.gc_predecessor_name
    if predecessor_name is None:
        return ()
    return tuple(
        lease
        for lease in journal.staging_leases
        if lease.path == gc_lease.path
        and lease.role in {"backup-reserved", "backup-dual"}
        and (
            lease.stage_name == predecessor_name
            or lease.stage_name == _distribution_quarantine_backup_name(predecessor_name)
            or (predecessor_name.startswith(f"{lease.stage_name}.") and predecessor_name.endswith(".gc"))
        )
    )


def _ordered_gc_transition_leases(journal: OperationJournal) -> tuple[DistributionStageOwnership, ...]:
    return tuple(
        sorted(
            (lease for lease in journal.staging_leases if lease.role in {"gc-reserved", "gc-exact"}),
            key=lambda lease: (
                lease.path,
                lease.gc_ordinal if lease.gc_ordinal is not None else 0,
                0 if lease.role == "gc-exact" else 1,
                lease.stage_name,
            ),
        )
    )


def _gc_transition_companion_is_explicit(
    journal: OperationJournal,
    left: DistributionStageOwnership,
    right: DistributionStageOwnership,
) -> bool:
    if left.path != right.path or left.stage_name == right.stage_name:
        return False
    if (
        left.gc_ordinal is not None
        and right.gc_ordinal is not None
        and left.role in {"gc-reserved", "gc-exact", "backup-only"}
        and right.role in {"gc-reserved", "gc-exact", "backup-only"}
    ):
        if right.gc_predecessor_name == left.stage_name and right.gc_ordinal == left.gc_ordinal + 1:
            return True
        if left.gc_predecessor_name == right.stage_name and left.gc_ordinal == right.gc_ordinal + 1:
            return True
        ordinal_two, ordinal_three = (left, right) if left.gc_ordinal == 2 else (right, left)
        if ordinal_two.gc_ordinal == 2 and ordinal_three.gc_ordinal == 3:
            return any(
                backup.path == left.path
                and backup.stage_name == ordinal_three.gc_predecessor_name
                and backup.role in {"backup-reserved", "backup-dual", "backup-only-reserved", "backup-only"}
                and backup.device == ordinal_two.device
                and backup.inode == ordinal_two.inode
                and backup.file_type == ordinal_two.file_type
                for backup in journal.staging_leases
            )
    gc_lease, backup = (left, right) if left.gc_ordinal is not None else (right, left)
    if (
        gc_lease.gc_ordinal in {1, 3}
        and gc_lease.gc_predecessor_name == backup.stage_name
        and backup.role in {"backup-reserved", "backup-dual", "backup-only-reserved", "backup-only"}
    ):
        return True
    if gc_lease.gc_ordinal != 2 or backup.role not in {
        "backup-reserved",
        "backup-dual",
        "backup-only-reserved",
        "backup-only",
    }:
        return False
    if (
        gc_lease.gc_predecessor_name is not None
        and gc_lease.gc_predecessor_name.startswith(f"{backup.stage_name}.")
        and gc_lease.gc_predecessor_name.endswith(".gc")
        and gc_lease.device == backup.device
        and gc_lease.inode == backup.inode
        and gc_lease.file_type == backup.file_type
    ):
        return True
    return any(
        predecessor.path == gc_lease.path
        and predecessor.stage_name == gc_lease.gc_predecessor_name
        and predecessor.role in {"gc-reserved", "gc-exact"}
        and predecessor.gc_ordinal == 1
        and predecessor.gc_predecessor_name == backup.stage_name
        and predecessor.device == gc_lease.device == backup.device
        and predecessor.inode == gc_lease.inode == backup.inode
        and predecessor.file_type == gc_lease.file_type == backup.file_type
        for predecessor in journal.staging_leases
    )


def _assert_gc_transition_graph(journal: OperationJournal) -> None:
    """Reject malformed GC authority graphs before inspecting or mutating names."""

    if any(
        len(_explicit_gc_backup_sources(journal, lease)) > 1
        for lease in journal.staging_leases
        if lease.role in {"gc-reserved", "gc-exact"}
    ):
        raise DistributionApplyError("journal-plan-mismatch")
    leases_by_name: dict[str, list[DistributionStageOwnership]] = {}
    for lease in journal.staging_leases:
        leases_by_name.setdefault(lease.stage_name, []).append(lease)

    transition_ordinals: set[tuple[str, int]] = set()
    outgoing_edges: dict[tuple[str, str], list[int]] = {}
    for lease in journal.staging_leases:
        has_predecessor = lease.gc_predecessor_name is not None
        if has_predecessor != (lease.gc_ordinal is not None):
            raise DistributionApplyError("journal-plan-mismatch")
        if not has_predecessor:
            continue
        predecessor_name = lease.gc_predecessor_name
        ordinal = lease.gc_ordinal
        assert predecessor_name is not None
        assert ordinal is not None
        if (
            lease.role not in {"gc-reserved", "gc-exact", "backup-only"}
            or lease.stage_name == PurePosixPath(lease.path).name
            or PurePosixPath(predecessor_name).name != predecessor_name
            or predecessor_name == lease.stage_name
            or predecessor_name == PurePosixPath(lease.path).name
            or ordinal not in {1, 2, 3}
            or (lease.path, ordinal) in transition_ordinals
        ):
            raise DistributionApplyError("journal-plan-mismatch")
        transition_ordinals.add((lease.path, ordinal))
        outgoing_edges.setdefault((lease.path, predecessor_name), []).append(ordinal)

        named_predecessors = leases_by_name.get(predecessor_name, [])
        if any(candidate.path != lease.path for candidate in named_predecessors):
            raise DistributionApplyError("journal-plan-mismatch")
        same_path_predecessors = tuple(candidate for candidate in named_predecessors if candidate.path == lease.path)
        if len(same_path_predecessors) > 1:
            raise DistributionApplyError("journal-plan-mismatch")
        if same_path_predecessors:
            predecessor = same_path_predecessors[0]
            if (
                lease.device > 0
                and predecessor.device > 0
                and (
                    lease.device != predecessor.device
                    or lease.inode != predecessor.inode
                    or lease.file_type != predecessor.file_type
                )
            ):
                raise DistributionApplyError("journal-plan-mismatch")
            if predecessor.gc_ordinal is not None:
                if predecessor.role not in {"gc-reserved", "gc-exact"} or ordinal != predecessor.gc_ordinal + 1:
                    raise DistributionApplyError("journal-plan-mismatch")
            elif ordinal == 1:
                if predecessor.role not in {
                    "stage",
                    "predecessor-quarantine",
                    "backup-reserved",
                    "backup-dual",
                    "backup-only-reserved",
                    "backup-only",
                }:
                    raise DistributionApplyError("journal-plan-mismatch")
            elif ordinal == 3:
                if predecessor.role not in {
                    "backup-reserved",
                    "backup-dual",
                    "backup-only-reserved",
                    "backup-only",
                }:
                    raise DistributionApplyError("journal-plan-mismatch")
            else:
                raise DistributionApplyError("journal-plan-mismatch")
            continue

        backup_predecessors = tuple(
            candidate
            for candidate in journal.staging_leases
            if candidate.path == lease.path
            and candidate.role in {"backup-reserved", "backup-dual"}
            and (
                candidate.stage_name == _distribution_quarantine_backup_name(predecessor_name)
                or (
                    predecessor_name.startswith(f"{candidate.stage_name}.")
                    and predecessor_name.endswith(".gc")
                    and lease.device > 0
                    and candidate.device == lease.device
                    and candidate.inode == lease.inode
                    and candidate.file_type == lease.file_type
                )
            )
        )
        derived_missing_backup = any(
            candidate.path == lease.path
            and candidate.role == "predecessor-quarantine"
            and _distribution_quarantine_backup_name(candidate.stage_name) == predecessor_name
            for candidate in journal.staging_leases
        )
        if not ((ordinal == 2 and len(backup_predecessors) == 1) or (ordinal in {1, 3} and derived_missing_backup)):
            raise DistributionApplyError("journal-plan-mismatch")
    for (path, predecessor_name), ordinals in outgoing_edges.items():
        if len(ordinals) == 1:
            continue
        graph_predecessor = next(
            (lease for lease in journal.staging_leases if lease.path == path and lease.stage_name == predecessor_name),
            None,
        )
        derived_missing_backup = any(
            lease.path == path
            and lease.role == "predecessor-quarantine"
            and _distribution_quarantine_backup_name(lease.stage_name) == predecessor_name
            for lease in journal.staging_leases
        )
        if sorted(ordinals) != [1, 3] or not (
            (graph_predecessor is not None and graph_predecessor.role in {"backup-reserved", "backup-dual"})
            or derived_missing_backup
        ):
            raise DistributionApplyError("journal-plan-mismatch")
    for path in {lease.path for lease in journal.staging_leases}:
        ordinal_two = next(
            (
                lease
                for lease in journal.staging_leases
                if lease.path == path and lease.gc_ordinal == 2 and lease.role in {"gc-reserved", "gc-exact"}
            ),
            None,
        )
        ordinal_three = next(
            (
                lease
                for lease in journal.staging_leases
                if lease.path == path
                and lease.gc_ordinal == 3
                and lease.role in {"gc-reserved", "gc-exact", "backup-only"}
            ),
            None,
        )
        if ordinal_two is None or ordinal_three is None or ordinal_three.gc_predecessor_name is None:
            continue
        retained_predecessor = next(
            (
                lease
                for lease in journal.staging_leases
                if lease.path == path
                and lease.stage_name == ordinal_three.gc_predecessor_name
                and lease.role in {"backup-reserved", "backup-dual", "backup-only-reserved", "backup-only"}
            ),
            None,
        )
        if (
            retained_predecessor is not None
            and ordinal_two.device > 0
            and retained_predecessor.device > 0
            and (
                ordinal_two.device != retained_predecessor.device
                or ordinal_two.inode != retained_predecessor.inode
                or ordinal_two.file_type != retained_predecessor.file_type
            )
        ):
            raise DistributionApplyError("journal-plan-mismatch")


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
    _assert_gc_transition_graph(journal)
    allowed_created_parents: set[str] = set()
    for record in journal.actions:
        if not _condition_has_complete_target_identity(record.precondition):
            raise DistributionApplyError("journal-plan-mismatch")
        # A required-directory action owns the directory it creates.  The
        # kernel records that target as a created-parent binding so a retry
        # can revalidate its exact inode; permit that binding even though the
        # directory itself is not listed in its parent chain.
        if record.action == "ensure-directory" and record.precondition.get("exists") is False:
            allowed_created_parents.add(record.path)
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
    for binding in journal.created_parent_bindings:
        if not binding.exists:
            continue
        actual = actual_parents.get(binding.relative_path)
        if actual is None:
            # A standalone required-directory action has no child asset
            # whose parent chain would expose the directory.  Its target
            # snapshot is the authoritative structure identity instead.
            directory_snapshot = dict(plan.target_snapshots).get(binding.relative_path)
            actual = directory_snapshot.target if directory_snapshot is not None else None
        if actual is None or not _same_structure_identity(actual, binding):
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
    current_specs = {
        **_target_identity_specs(plan.current_assets, plan.scaffold_assets),
        **{item.path: DistributionIdentity(kind="directory") for item in plan.required_directories},
    }
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files} - set(current_specs)
    for record in journal.actions:
        postcondition = _journal_postcondition(record)
        expected_identity: DistributionIdentity | None = None
        if record.action == "prune":
            if record.path not in obsolete_paths or postcondition.get("exists") is not False:
                raise DistributionApplyError("journal-plan-mismatch")
        elif record.action == "ensure-directory":
            if not any(item.path == record.path for item in plan.required_directories):
                raise DistributionApplyError("journal-plan-mismatch")
            expected_identity = DistributionIdentity(kind="directory")
        else:
            expected_identity = current_specs.get(record.path)
            if expected_identity is None or record.action not in {"create", "adopt", "upgrade", "preserve"}:
                raise DistributionApplyError("journal-plan-mismatch")
        target_snapshot = dict(plan.target_snapshots).get(record.path)
        if record.action == "ensure-directory":
            assert expected_identity is not None
            if (
                postcondition.get("exists") is not True
                or postcondition.get("file_type") != "directory"
                or postcondition.get("identity") != _distribution_identity_payload(expected_identity)
            ):
                raise DistributionApplyError("journal-plan-mismatch")
        elif (
            record.action != "prune"
            and expected_identity is not None
            and expected_identity.kind != "directory"
            and (
                postcondition.get("exists") is not True
                or postcondition.get("file_type") != expected_identity.kind
                or (
                    record.action == "adopt"
                    and (
                        target_snapshot is None
                        or any(
                            postcondition.get(field) != getattr(target_snapshot.target, field)
                            for field in ("device", "inode", "ctime_ns")
                        )
                    )
                )
                or (
                    record.action in {"create", "upgrade"}
                    and record.checkpoint != "pending"
                    and (
                        target_snapshot is None
                        or any(
                            postcondition.get(field) != getattr(target_snapshot.target, field)
                            for field in ("device", "inode", "ctime_ns", "link_count")
                        )
                    )
                )
                or (
                    postcondition.get("link_count")
                    != (
                        target_snapshot.target.link_count
                        if record.action == "adopt" and target_snapshot is not None
                        else 1
                    )
                )
                or postcondition.get("identity") != _distribution_identity_payload(expected_identity)
            )
        ):
            raise DistributionApplyError("journal-plan-mismatch")
        snapshot = dict(plan.target_snapshots).get(record.path)
        if snapshot is None and record.path in completed_missing_obsolete:
            snapshot = _observe_target(plan.target_root, record.path).snapshot
        if (
            snapshot is None
            or not _condition_has_complete_parent_chain(snapshot, record.precondition)
            or not _condition_has_complete_parent_chain(snapshot, postcondition)
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
    if _journal_digest(journal) not in {journal.plan_digest, *_mutation_plan_digest_candidates(assessment)}:
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
        expected = record.precondition if record.checkpoint == "pending" else _journal_postcondition(record)
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
        matches_post = _snapshot_matches_condition(
            snapshot,
            _journal_postcondition(record),
            journal.created_parent_bindings,
        )
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
    """Bind a safely recoverable parent that appeared before an abrupt stop.

    A user may have published an exact provider asset into a missing parent
    between attempts.  Such a parent is adoptable only when every existing
    child is already represented by a journal action's exact postcondition;
    unknown children remain a fail-closed journal mismatch.
    """

    _assert_created_parent_bindings_closed_set(store.target_root, journal)

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
        if actual is None:
            directory_snapshot = dict(assessment.distribution_plan.target_snapshots).get(relative_path)
            actual = directory_snapshot.target if directory_snapshot is not None else None
        if actual is None or not actual.exists:
            continue
        if actual.file_type != "directory":
            raise DistributionApplyError("journal-precondition-mismatch")
        parent_path = store.target_root / PurePosixPath(relative_path)
        try:
            children = tuple(parent_path.iterdir())
        except OSError as exc:
            raise DistributionApplyError("journal-precondition-mismatch") from exc
        tentative_bindings = (
            *(item for path, item in bindings.items() if path != relative_path),
            actual,
        )
        snapshots = dict(assessment.distribution_plan.target_snapshots)
        records = {record.path: record for record in journal.actions}
        for child in children:
            child_path = f"{relative_path}/{child.name}"
            record = records.get(child_path)
            snapshot = snapshots.get(child_path)
            if (
                record is None
                or snapshot is None
                or not _snapshot_matches_condition(
                    snapshot,
                    _journal_postcondition(record),
                    tentative_bindings,
                )
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


def _entry_matches_journal_condition(
    parent_fd: int,
    name: str,
    path: str,
    condition: dict[str, object],
) -> bool:
    try:
        info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        identity = _distribution_stage_identity(
            parent_fd,
            name,
            path,
            allow_backup_link=path == "spec-dock/.workbench/README.md",
        )
    except FileNotFoundError:
        return condition.get("exists") is False
    except (OSError, DistributionApplyError):
        return False
    for field_name, actual in (
        ("device", info.st_dev),
        ("inode", info.st_ino),
        ("ctime_ns", info.st_ctime_ns),
        ("file_type", _file_type(info.st_mode)),
        ("link_count", info.st_nlink),
    ):
        workbench_seed_hard_link = (
            path == "spec-dock/.workbench/README.md"
            and field_name == "link_count"
            and condition.get("file_type") == "regular"
            and condition.get("link_count") == 1
            and isinstance(actual, int)
            and actual >= 1
        )
        if (
            field_name in condition
            and not (
                condition[field_name] == 0
                and field_name in {"device", "inode", "ctime_ns", "link_count"}
                and condition.get("file_type") == "directory"
            )
            and not workbench_seed_hard_link
            and condition[field_name] != actual
        ):
            return False
    condition_identity = condition.get("identity")
    if (
        condition.get("exists") is True
        and condition.get("file_type") == "directory"
        and isinstance(condition_identity, dict)
        and condition_identity.get("kind") == "directory"
    ):
        return _file_type(info.st_mode) == "directory"
    return condition.get("exists") is True and condition.get("identity") == _distribution_identity_payload(identity)


def _entry_matches_staging_lease(
    parent_fd: int,
    name: str,
    lease: DistributionStageOwnership,
    *,
    require_ctime: bool = True,
) -> bool:
    try:
        info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except (FileNotFoundError, OSError):
        return False
    return (
        lease.device > 0
        and info.st_dev == lease.device
        and info.st_ino == lease.inode
        and (not require_ctime or info.st_ctime_ns == lease.ctime_ns)
        and _file_type(info.st_mode) == lease.file_type
        and info.st_nlink == 1
    )


def _assert_workspace_closed_set_tree(workspace: Path, allowed: frozenset[str]) -> None:
    def walk(current: Path, relative: str) -> None:
        try:
            entries = tuple(os.scandir(current))
        except OSError as exc:
            raise DistributionApplyError("journal-parent-mismatch") from exc
        for entry in entries:
            child = f"{relative}/{entry.name}" if relative else entry.name
            has_allowed_descendant = any(path.startswith(f"{child}/") for path in allowed)
            if child not in allowed and not has_allowed_descendant:
                raise DistributionApplyError("journal-parent-mismatch")
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise DistributionApplyError("journal-parent-mismatch") from exc
            if has_allowed_descendant:
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                    raise DistributionApplyError("journal-parent-mismatch")
                walk(Path(entry.path), child)

    walk(workspace, "")


def _assert_created_workspace_closed_set(
    target_root: Path,
    expected_identity: tuple[int, int] | None,
    journal: OperationJournal | None,
    allowed_workspace_entries: frozenset[str] | None = None,
) -> None:
    """Re-prove a fresh bootstrap directory and reject unknown root children."""

    if expected_identity is None:
        return
    workspace = target_root / "spec-dock"
    try:
        info = os.lstat(workspace)
    except OSError as exc:
        raise DistributionApplyError("journal-parent-mismatch") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino) != expected_identity:
        raise DistributionApplyError("journal-parent-mismatch")
    if allowed_workspace_entries is not None and journal is None:
        _assert_workspace_closed_set_tree(workspace, allowed_workspace_entries)
        return
    workspace_fd: int | None = None
    try:
        workspace_fd = os.open(workspace, _distribution_directory_flags())
        opened = os.fstat(workspace_fd)
        if (opened.st_dev, opened.st_ino) != expected_identity:
            raise DistributionApplyError("journal-parent-mismatch")
        with os.scandir(workspace_fd) as entries:
            names = {entry.name for entry in entries}
    except OSError as exc:
        raise DistributionApplyError("journal-parent-mismatch") from exc
    finally:
        if workspace_fd is not None:
            with suppress(OSError):
                os.close(workspace_fd)
    allowed = set()
    if _path_present_no_follow(workspace / _DISTRIBUTION_RETRY_MARKER_REL.name):
        allowed.add(_DISTRIBUTION_RETRY_MARKER_REL.name)
    if journal is not None:
        allowed.add(_DISTRIBUTION_JOURNAL_REL.name)
        for path in (
            *(action.path for action in journal.actions),
            *(binding.relative_path for binding in journal.created_parent_bindings),
            *(lease.path for lease in journal.staging_leases),
        ):
            parts = PurePosixPath(path).parts
            if len(parts) > 1 and parts[0] == "spec-dock":
                allowed.add(parts[1])
        for lease in journal.staging_leases:
            parts = PurePosixPath(lease.path).parts
            if len(parts) == 2 and parts[0] == "spec-dock":
                allowed.add(lease.stage_name)
    if names - allowed:
        raise DistributionApplyError("journal-parent-mismatch")


def _assert_fresh_guard_only_closed_set(
    target_root: Path,
    plan: ExecutableMutationPlan,
    marker: DistributionRetryMarker,
    extra_entries: tuple[str, ...] = (),
) -> tuple[tuple[int, int], frozenset[str]]:
    """Re-prove a fresh workspace before converting a guard-only retry.

    A guard-only retry has no journal from which the bootstrap witness can be
    restored.  The guard plan still binds the current workspace identity via
    its action preconditions, so reject any child that is not an exact prefix
    of a planned path or an operation-owned recovery entry before publishing a
    journal.
    """

    workspace = target_root / "spec-dock"
    try:
        workspace_info = os.lstat(workspace)
    except OSError as exc:
        raise DistributionApplyError("journal-parent-mismatch") from exc
    if stat.S_ISLNK(workspace_info.st_mode) or not stat.S_ISDIR(workspace_info.st_mode):
        raise DistributionApplyError("journal-parent-mismatch")

    workspace_identities: set[tuple[int, int]] = set()
    for _, snapshot in plan.distribution_plan.target_snapshots:
        for parent in snapshot.parents:
            if parent.relative_path == "spec-dock" and parent.exists:
                if parent.file_type != "directory" or parent.device is None or parent.inode is None:
                    raise DistributionApplyError("journal-parent-mismatch")
                workspace_identities.add((parent.device, parent.inode))
        target = snapshot.target
        if target.relative_path == "spec-dock" and target.exists:
            if target.file_type != "directory" or target.device is None or target.inode is None:
                raise DistributionApplyError("journal-parent-mismatch")
            workspace_identities.add((target.device, target.inode))
    if len(workspace_identities) != 1 or (workspace_info.st_dev, workspace_info.st_ino) not in workspace_identities:
        raise DistributionApplyError("journal-parent-mismatch")

    allowed: set[str] = {
        _DISTRIBUTION_RETRY_MARKER_REL.name,
        _DISTRIBUTION_JOURNAL_REL.name,
    }

    def add_path(relative_path: str) -> None:
        parts = PurePosixPath(relative_path).parts
        if not parts or parts[0] != "spec-dock":
            return
        for index in range(1, len(parts) + 1):
            allowed.add(PurePosixPath(*parts[1:index]).as_posix())

    for action in plan.actions:
        add_path(action.path)
    for lease in marker.stage_ownership:
        add_path(lease.path)
        lease_parts = PurePosixPath(lease.path).parts
        if len(lease_parts) >= 2 and lease_parts[0] == "spec-dock":
            lease_parent = PurePosixPath(*lease_parts[1:-1])
            allowed.add((lease_parent / lease.stage_name).as_posix() if lease_parent.parts else lease.stage_name)
    for extra in extra_entries:
        relative = PurePosixPath(extra)
        if relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 1:
            raise DistributionApplyError("journal-parent-mismatch")
        allowed.add(relative.as_posix())

    _assert_workspace_closed_set_tree(workspace, frozenset(allowed))
    return (workspace_info.st_dev, workspace_info.st_ino), frozenset(allowed)


def _assert_created_parent_bindings_closed_set(
    target_root: Path,
    journal: OperationJournal,
) -> None:
    """Treat recovered parent bindings as hints and re-prove their contents."""

    originally_missing: set[str] = set()
    for action in journal.actions:
        parents = action.precondition.get("parents")
        if not isinstance(parents, list):
            raise DistributionApplyError("journal-precondition-mismatch")
        if action.action == "ensure-directory" and action.precondition.get("exists") is False:
            originally_missing.add(action.path)
        originally_missing.update(
            parent["relative_path"]
            for parent in parents
            if isinstance(parent, dict)
            and parent.get("exists") is False
            and isinstance(parent.get("relative_path"), str)
        )
    bindings = {binding.relative_path: binding for binding in journal.created_parent_bindings}
    for relative_path, binding in bindings.items():
        if relative_path not in originally_missing or not binding.exists:
            continue
        try:
            parent_chain = _open_distribution_parent_chain(
                target_root,
                f"{relative_path}/.closed-set-probe",
                create_missing=False,
            )
        except DistributionApplyError as exc:
            raise DistributionApplyError("journal-precondition-mismatch") from exc
        try:
            _assert_created_parent_binding_fd_closed_set(
                parent_chain[-1],
                relative_path,
                binding,
                journal,
            )
        finally:
            _close_distribution_parent_chain(parent_chain)


def _assert_created_parent_binding_fd_closed_set(
    parent_fd: int,
    relative_path: str,
    binding: PathIdentitySnapshot,
    journal: OperationJournal,
) -> None:
    """Re-prove one created parent using the descriptor held by the mutator."""

    bindings = {item.relative_path: item for item in journal.created_parent_bindings}
    records = {record.path: record for record in journal.actions}
    before = os.fstat(parent_fd)
    if not _same_stat_structure(before, binding):
        raise DistributionApplyError("journal-precondition-mismatch")
    try:
        names = os.listdir(parent_fd)
    except OSError as exc:
        raise DistributionApplyError("journal-precondition-mismatch") from exc
    for name in names:
        child_path = f"{relative_path}/{name}"
        child_binding = bindings.get(child_path)
        if child_binding is not None and child_binding.exists:
            try:
                child_info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except OSError as exc:
                raise DistributionApplyError("journal-precondition-mismatch") from exc
            if child_info.st_nlink < 1 or not _same_stat_structure(child_info, child_binding):
                raise DistributionApplyError("journal-precondition-mismatch")
            continue
        record = records.get(child_path)
        if record is not None:
            canonical_is_exact_lease = any(
                lease.path == child_path
                and lease.role == "stage"
                and _entry_matches_staging_lease(
                    parent_fd,
                    name,
                    lease,
                    require_ctime=False,
                )
                for lease in journal.staging_leases
            )
            if (record.checkpoint != "pending" or canonical_is_exact_lease) and _entry_matches_journal_condition(
                parent_fd, name, child_path, _journal_postcondition(record)
            ):
                continue
        matched_stage = False
        for lease in journal.staging_leases:
            if PurePosixPath(lease.path).parent.as_posix() != relative_path:
                continue
            if lease.stage_name != name:
                continue
            if lease.device == lease.inode == lease.ctime_ns == 0:
                try:
                    reserved_info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                except OSError as exc:
                    raise DistributionApplyError("journal-precondition-mismatch") from exc
                companion: DistributionStageOwnership | None = None
                allowed_links = {1}
                requires_companion = False
                if lease.role == "gc-reserved":
                    companion = next(
                        (
                            item
                            for item in journal.staging_leases
                            if item.path == lease.path
                            and item.stage_name == lease.gc_predecessor_name
                            and item.device > 0
                            and (
                                (lease.gc_ordinal == 1 and item.role in {"stage", "backup-dual", "backup-only"})
                                or (lease.gc_ordinal == 2 and item.role == "gc-exact" and item.gc_ordinal == 1)
                                or (
                                    lease.gc_ordinal == 3
                                    and item.role in {"backup-reserved", "backup-dual", "backup-only"}
                                )
                            )
                        ),
                        None,
                    )
                    requires_companion = True
                    allowed_links = (
                        {2}
                        if lease.gc_ordinal in {2, 3}
                        or (companion is not None and companion.role in {"backup-dual", "backup-only"})
                        else {1}
                    )
                elif lease.role in {"backup-reserved", "backup-only-reserved"}:
                    companion = next(
                        (
                            item
                            for item in journal.staging_leases
                            if item.path == lease.path
                            and item.device > 0
                            and (
                                (
                                    item.role == "predecessor-quarantine"
                                    and _distribution_quarantine_backup_name(item.stage_name) == lease.stage_name
                                )
                                or (
                                    lease.role == "backup-reserved"
                                    and item.role == "gc-exact"
                                    and item.gc_predecessor_name == lease.stage_name
                                )
                            )
                        ),
                        None,
                    )
                    requires_companion = True
                    allowed_links = {1, 2} if lease.role == "backup-only-reserved" else {2}
                if (
                    _file_type(reserved_info.st_mode) == lease.file_type
                    and reserved_info.st_nlink in allowed_links
                    and not (requires_companion and companion is None)
                    and (
                        companion is None
                        or (reserved_info.st_dev == companion.device and reserved_info.st_ino == companion.inode)
                    )
                ):
                    matched_stage = True
                    break
            try:
                exact_info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except OSError as exc:
                raise DistributionApplyError("journal-precondition-mismatch") from exc
            if lease.role == "predecessor-quarantine":
                dual_backup = next(
                    (item for item in journal.staging_leases if item.path == lease.path and item.role == "backup-dual"),
                    None,
                )
                if (
                    dual_backup is not None
                    and exact_info.st_dev == dual_backup.device
                    and exact_info.st_ino == dual_backup.inode
                    and exact_info.st_ctime_ns == dual_backup.ctime_ns
                    and _file_type(exact_info.st_mode) == dual_backup.file_type
                    and exact_info.st_nlink == 2
                ):
                    matched_stage = True
                    break
            gc_companion = next(
                (
                    item
                    for item in journal.staging_leases
                    if item.path == lease.path
                    and item.stage_name != lease.stage_name
                    and item.device > 0
                    and _gc_transition_companion_is_explicit(journal, lease, item)
                ),
                None,
            )
            if lease.role == "backup-dual" and exact_info.st_nlink == 2:
                for candidate in journal.staging_leases:
                    if (
                        candidate.path != lease.path
                        or candidate.role != "gc-exact"
                        or candidate.device != lease.device
                        or candidate.inode != lease.inode
                        or not _gc_transition_companion_is_explicit(journal, lease, candidate)
                    ):
                        continue
                    try:
                        candidate_info = os.stat(
                            candidate.stage_name,
                            dir_fd=parent_fd,
                            follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        continue
                    except OSError as exc:
                        raise DistributionApplyError("journal-precondition-mismatch") from exc
                    if (
                        candidate_info.st_dev == exact_info.st_dev == lease.device
                        and candidate_info.st_ino == exact_info.st_ino == lease.inode
                        and _file_type(candidate_info.st_mode) == _file_type(exact_info.st_mode) == lease.file_type
                        and candidate_info.st_nlink == 2
                    ):
                        matched_stage = True
                        break
                if matched_stage:
                    break
            if (
                lease.role == "backup-dual"
                and exact_info.st_dev == lease.device
                and exact_info.st_ino == lease.inode
                and _file_type(exact_info.st_mode) == lease.file_type
                and exact_info.st_nlink == 1
                and any(
                    candidate.path == lease.path
                    and candidate.role in {"gc-reserved", "gc-exact"}
                    and candidate.gc_ordinal == 3
                    and candidate.gc_predecessor_name == lease.stage_name
                    for candidate in journal.staging_leases
                )
                and all(
                    candidate.role == "gc-exact"
                    and candidate.device == lease.device
                    and candidate.inode == lease.inode
                    and candidate.file_type == lease.file_type
                    and _stat_optional_no_follow(parent_fd, candidate.stage_name) is None
                    for candidate in journal.staging_leases
                    if candidate.path == lease.path
                    and candidate.role in {"gc-reserved", "gc-exact"}
                    and candidate.gc_ordinal in {1, 2}
                )
            ):
                matched_stage = True
                break
            if (
                lease.role == "gc-exact"
                and exact_info.st_dev == lease.device
                and exact_info.st_ino == lease.inode
                and exact_info.st_ctime_ns == lease.ctime_ns
                and _file_type(exact_info.st_mode) == lease.file_type
                and exact_info.st_nlink == 1
            ):
                matched_stage = True
                break
            if (
                lease.role == "gc-exact"
                and lease.gc_ordinal == 3
                and exact_info.st_dev == lease.device
                and exact_info.st_ino == lease.inode
                and _file_type(exact_info.st_mode) == lease.file_type
                and exact_info.st_nlink == 1
            ):
                completed_predecessor = next(
                    (
                        candidate
                        for candidate in journal.staging_leases
                        if candidate.path == lease.path
                        and candidate.role == "gc-exact"
                        and candidate.gc_ordinal == 2
                        and candidate.device == lease.device
                        and candidate.inode == lease.inode
                        and candidate.file_type == lease.file_type
                    ),
                    None,
                )
                if (
                    completed_predecessor is not None
                    and _stat_optional_no_follow(parent_fd, completed_predecessor.stage_name) is None
                ):
                    matched_stage = True
                    break
            if lease.role == "gc-exact" and lease.gc_ordinal == 2 and exact_info.st_nlink == 2:
                graph_successor = next(
                    (
                        candidate
                        for candidate in journal.staging_leases
                        if candidate.path == lease.path
                        and candidate.role == "gc-reserved"
                        and candidate.gc_ordinal == 3
                        and any(
                            backup.path == lease.path
                            and backup.stage_name == candidate.gc_predecessor_name
                            and backup.role in {"backup-reserved", "backup-dual"}
                            and backup.device == lease.device
                            and backup.inode == lease.inode
                            and backup.file_type == lease.file_type
                            for backup in journal.staging_leases
                        )
                    ),
                    None,
                )
                if graph_successor is not None:
                    try:
                        graph_info = os.stat(
                            graph_successor.stage_name,
                            dir_fd=parent_fd,
                            follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        graph_info = None
                    except OSError as exc:
                        raise DistributionApplyError("journal-precondition-mismatch") from exc
                    if (
                        graph_info is not None
                        and graph_info.st_dev == exact_info.st_dev == lease.device
                        and graph_info.st_ino == exact_info.st_ino == lease.inode
                        and _file_type(graph_info.st_mode) == _file_type(exact_info.st_mode) == lease.file_type
                        and graph_info.st_nlink == 2
                    ):
                        matched_stage = True
                        break
            if lease.role == "gc-exact" and exact_info.st_nlink == 2:
                for candidate in journal.staging_leases:
                    if (
                        candidate.path != lease.path
                        or candidate.stage_name == lease.stage_name
                        or candidate.device != lease.device
                        or candidate.inode != lease.inode
                        or not _gc_transition_companion_is_explicit(journal, lease, candidate)
                    ):
                        continue
                    try:
                        candidate_info = os.stat(
                            candidate.stage_name,
                            dir_fd=parent_fd,
                            follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        continue
                    except OSError as exc:
                        raise DistributionApplyError("journal-precondition-mismatch") from exc
                    if (
                        candidate_info.st_dev == exact_info.st_dev == lease.device
                        and candidate_info.st_ino == exact_info.st_ino == lease.inode
                        and _file_type(candidate_info.st_mode) == _file_type(exact_info.st_mode) == lease.file_type
                        and candidate_info.st_nlink == 2
                    ):
                        matched_stage = True
                        break
                if matched_stage:
                    break
            if gc_companion is not None:
                try:
                    companion_info = os.stat(
                        gc_companion.stage_name,
                        dir_fd=parent_fd,
                        follow_symlinks=False,
                    )
                except FileNotFoundError:
                    if (
                        lease.role != "gc-exact"
                        and exact_info.st_dev == gc_companion.device
                        and exact_info.st_ino == gc_companion.inode
                        and _file_type(exact_info.st_mode) == gc_companion.file_type
                        and exact_info.st_nlink == 1
                    ):
                        matched_stage = True
                        break
                    gc_companion = None
                except OSError as exc:
                    raise DistributionApplyError("journal-precondition-mismatch") from exc
                if gc_companion is not None:
                    exact_gc = lease if lease.role == "gc-exact" else gc_companion
                    if (
                        exact_info.st_nlink == 2
                        and exact_info.st_dev == companion_info.st_dev == exact_gc.device
                        and exact_info.st_ino == companion_info.st_ino == exact_gc.inode
                        and companion_info.st_ctime_ns == exact_gc.ctime_ns
                        and _file_type(exact_info.st_mode) == _file_type(companion_info.st_mode) == exact_gc.file_type
                        and companion_info.st_nlink == 2
                    ):
                        matched_stage = True
                        break
            expected_links = 2 if lease.role == "backup-dual" else 1
            if (
                lease.device > 0
                and exact_info.st_dev == lease.device
                and exact_info.st_ino == lease.inode
                and exact_info.st_ctime_ns == lease.ctime_ns
                and _file_type(exact_info.st_mode) == lease.file_type
                and exact_info.st_nlink == expected_links
            ):
                matched_stage = True
                break
            record = records.get(lease.path)
            canonical_name = PurePosixPath(lease.path).name
            if (
                record is not None
                and record.action == "upgrade"
                and _entry_matches_staging_lease(
                    parent_fd,
                    canonical_name,
                    lease,
                    require_ctime=False,
                )
                and _entry_matches_journal_condition(parent_fd, name, lease.path, record.precondition)
            ):
                matched_stage = True
                break
        if not matched_stage:
            raise DistributionApplyError("journal-precondition-mismatch")
    after = os.fstat(parent_fd)
    if _stat_identity_tuple(after) != _stat_identity_tuple(before):
        raise DistributionApplyError("journal-precondition-mismatch")


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
    *,
    allow_operation_created_parents: bool = False,
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
            or action.action not in {"create", "adopt", "upgrade", "prune"}
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
                expected_snapshot=None if allow_operation_created_parents else snapshot,
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


def _execute_distribution_reconciliation(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    intent: JournaledDistributionIntent,
    package_version: str,
    legacy_marker: DistributionRetryMarker | None = None,
    generated_assets: tuple[DistributionAsset, ...] = (),
    version_refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None,
    root_identity_path: Path | None = None,
    created_workspace_identity: tuple[int, int] | None = None,
    preserved_state_validator: Callable[[], None] | None = None,
) -> DistributionProcessResult:
    """Execute one journaled distribution intent through the shared service."""

    preserved_validation_active = True
    journal: OperationJournal | None = None
    boundary_workspace_identity = created_workspace_identity
    boundary_workspace_closed_set: frozenset[str] | None = None
    guard_only_plan: ExecutableMutationPlan | None = None
    guard_only_marker: DistributionRetryMarker | None = None
    boundary_journal: OperationJournal | None = None

    def revalidate_guard_only_workspace(extra_entries: tuple[str, ...] = ()) -> None:
        if guard_only_plan is None or guard_only_marker is None:
            return
        _assert_fresh_guard_only_closed_set(
            target_root,
            guard_only_plan,
            guard_only_marker,
            extra_entries,
        )

    def validate_preserved_state() -> None:
        _assert_created_workspace_closed_set(
            target_root,
            boundary_workspace_identity,
            journal or boundary_journal,
            boundary_workspace_closed_set if journal is None else None,
        )
        if preserved_validation_active and preserved_state_validator is not None:
            preserved_state_validator()

    def validate_first_target_mutation() -> Callable[[], None] | None:
        validate_preserved_state()

        def commit() -> None:
            nonlocal preserved_validation_active
            preserved_validation_active = False

        return commit

    store = OperationJournalStore(
        target_root,
        identity_path=root_identity_path,
        expected_workspace_identity=created_workspace_identity,
        workspace_closed_set_validator=revalidate_guard_only_workspace,
    )
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
    if (
        not journal_present
        and guard_marker is not None
        and guard_marker.purpose == _journal_guard_purpose_for_intent(intent)
    ):
        operation_package_version = guard_marker.package_version
    if journal_present:
        try:
            journal_seed = store._read(_root_identity_for_assessment(target_root))
            _assert_gc_transition_graph(journal_seed)
            if intent == "fresh":
                workspace_device = journal_seed.workspace_identity.device
                workspace_inode = journal_seed.workspace_identity.inode
                if not isinstance(workspace_device, int) or not isinstance(workspace_inode, int):
                    raise DistributionApplyError("journal-protocol-incompatible")
                boundary_workspace_identity = (workspace_device, workspace_inode)
                boundary_journal = journal_seed
            if guard_marker is None:
                try:
                    guard_marker = _read_distribution_retry_marker(target_root)
                except DistributionAdmissionError as exc:
                    raise DistributionApplyError("dual-recovery-state") from exc
            terminal_journal_without_guard = journal_seed.status == "completed" and guard_marker is None
            if not terminal_journal_without_guard and (
                guard_marker is None
                or guard_marker.purpose != _journal_guard_purpose_for_intent(intent)
                or guard_marker.operation != journal_seed.intent
                or guard_marker.package_version != journal_seed.package_version
                or guard_marker.target_root != journal_seed.root_identity
                or guard_marker.last_completed_phase != "preflight-complete"
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
    try:
        validate_preserved_state()
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
    journal = None
    legacy_marker_bytes: bytes | None = None
    legacy_marker_replaced = False
    restore_legacy_marker_on_failure = False
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
            )
        ):
            raise DistributionApplyError("dual-recovery-state")
        if legacy_present:
            if not journal_present:
                executable = build_executable_mutation_plan(assessment)
                plan_digest = executable.plan_digest
                legacy_fresh_conversion = (
                    guard_marker is not None
                    and guard_marker.purpose == _DISTRIBUTION_RETRY_PURPOSE
                    and guard_marker.operation == "fresh"
                    and intent == "fresh"
                )
                if intent == "fresh" and created_workspace_identity is None:
                    assert guard_marker is not None
                    (
                        boundary_workspace_identity,
                        boundary_workspace_closed_set,
                    ) = _assert_fresh_guard_only_closed_set(target_root, executable, guard_marker)
                    store.expected_workspace_identity = boundary_workspace_identity
                    guard_only_plan = executable
                    guard_only_marker = guard_marker
                package_compatible = guard_marker is not None and (
                    guard_marker.package_version == package_version
                    if legacy_fresh_conversion
                    else _journal_package_is_compatible(guard_marker.package_version, package_version)
                )
                if (
                    guard_marker is None
                    or guard_marker.operation != intent
                    or not package_compatible
                    or guard_marker.target_root != executable.root_identity
                    or (guard_marker.last_completed_phase != "preflight-complete" and not legacy_fresh_conversion)
                ):
                    raise DistributionApplyError("legacy-marker-unconvertible")
                if guard_marker.purpose == _journal_guard_purpose_for_intent(intent):
                    if (
                        guard_marker.operation_id is None
                        or guard_marker.contract_identity != executable.contract_identity
                        or not _plan_digest_matches(executable, guard_marker.plan_digest)
                    ):
                        raise DistributionApplyError("forward-guard-plan-mismatch")
                    _validated_legacy_stage_leases(executable, guard_marker, target_root)
                    store.bind_forward_guard(guard_marker)
                    validate_preserved_state()
                    journal = store.prepare(executable, package_version=guard_marker.package_version)
                    store.workspace_closed_set_validator = None
                    guard_only_plan = None
                    guard_only_marker = None
                else:
                    legacy_stage_leases = _validated_legacy_stage_leases(executable, guard_marker, target_root)
                    store.require_journal_absent = legacy_fresh_conversion
                    restore_legacy_marker_on_failure = legacy_fresh_conversion
                    store._validate_workspace_closed_set()
                    validate_preserved_state()
                    legacy_marker_bytes = _read_no_follow_regular(
                        target_root / _DISTRIBUTION_RETRY_MARKER_REL,
                        label="distribution retry marker",
                    )
                    guard_marker = store.prepare_legacy_guard(
                        executable,
                        package_version=package_version,
                        replace_marker=guard_marker,
                        stage_ownership=legacy_stage_leases,
                    )
                    legacy_marker_replaced = True
                    guard_only_marker = guard_marker
                    store.bind_forward_guard(guard_marker)
                    validate_preserved_state()
                    journal = store.prepare(executable, package_version=package_version)
                    legacy_marker_replaced = False
                    store.require_journal_absent = False
                    store.workspace_closed_set_validator = None
                    guard_only_plan = None
                    guard_only_marker = None
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
            validate_preserved_state()
            journal = _reconcile_created_parent_bindings(store, assessment, journal)
            if journal.status == "completed":
                executable = _resume_executable_plan(assessment, journal)
                if assessment.blockers or any(
                    action.action not in {"adopt", "preserve"} for action in assessment.actions
                ):
                    raise DistributionApplyError("distribution postcondition failed")
                if guard_marker is not None:
                    validate_preserved_state()
                    store.remove_legacy_marker(store._forward_guard or guard_marker)
                validate_preserved_state()
                store.remove_completed(journal, guard_already_removed=True)
                if journal.package_version != package_version and intent != "fresh":
                    return _execute_distribution_reconciliation(
                        install_root,
                        manifest_path=manifest_path,
                        scaffold_root=scaffold_root,
                        target_root=target_root,
                        intent=intent,
                        package_version=package_version,
                        generated_assets=generated_assets,
                        version_refreshable_existing_identities=(version_asset.identity,),
                        root_identity_path=root_identity_path,
                        created_workspace_identity=created_workspace_identity,
                        preserved_state_validator=(preserved_state_validator if preserved_validation_active else None),
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
                validate_preserved_state()
                journal = store.mark_completed(journal)
                if guard_marker is not None:
                    validate_preserved_state()
                    store.remove_legacy_marker(store._forward_guard or guard_marker)
                validate_preserved_state()
                store.remove_completed(journal, guard_already_removed=True)
                if journal.package_version != package_version and intent != "fresh":
                    return _execute_distribution_reconciliation(
                        install_root,
                        manifest_path=manifest_path,
                        scaffold_root=scaffold_root,
                        target_root=target_root,
                        intent=intent,
                        package_version=package_version,
                        generated_assets=generated_assets,
                        version_refreshable_existing_identities=(version_asset.identity,),
                        root_identity_path=root_identity_path,
                        created_workspace_identity=created_workspace_identity,
                        preserved_state_validator=(preserved_state_validator if preserved_validation_active else None),
                    )
                return DistributionProcessResult(
                    status="completed",
                    intent=intent,
                    actions=assessment.actions,
                    plan_digest=journal.plan_digest,
                )
            reconciled = _reconcile_pending_journal_actions(assessment, journal)
            if reconciled != journal:
                validate_preserved_state()
                journal = store.write(reconciled)
            published_paths = tuple(action.path for action in journal.actions if action.checkpoint == "published")
            if any(lease.path in published_paths for lease in journal.staging_leases):
                validate_preserved_state()
                journal = store.checkpoint_published(journal, published_paths)
            executable = _resume_executable_plan(assessment, journal)
        elif journal is None:
            executable = build_executable_mutation_plan(assessment)
            validate_preserved_state()
            guard_marker = store.prepare_legacy_guard(executable, package_version=package_version)
            store.bind_forward_guard(guard_marker)
            validate_preserved_state()
            journal = store.prepare(executable, package_version=package_version)
        plan_digest = executable.plan_digest
        validate_preserved_state()
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
            validate_preserved_state()
            active_journal = store.record_staging_lease(active_journal, lease)
            journal = active_journal

        def remove_staging_leases(path: str, stage_names: tuple[str, ...]) -> None:
            nonlocal active_journal, journal
            validate_preserved_state()
            completes_gc = any(
                lease.path == path and lease.stage_name in stage_names and lease.role == "backup-only"
                for lease in active_journal.staging_leases
            )
            retained = tuple(
                lease
                for lease in active_journal.staging_leases
                if not (
                    lease.path == path
                    and (
                        lease.stage_name in stage_names or (completes_gc and lease.role in {"gc-reserved", "gc-exact"})
                    )
                )
            )
            active_journal = store.write(
                replace(active_journal, staging_leases=retained),
                predecessor=active_journal,
            )
            journal = active_journal

        def record_created_parents(bindings: tuple[PathIdentitySnapshot, ...]) -> None:
            nonlocal active_journal, journal
            validate_preserved_state()
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
            validate_preserved_state()
            active_journal = store.checkpoint_published(active_journal, completed)
            journal = active_journal
            recorded_completed = completed

        def validate_mutation_boundary() -> None:
            validate_preserved_state()
            _assert_created_parent_bindings_closed_set(target_root, active_journal)

        def validate_held_parent_boundary(path: str, parent_chain: tuple[int, ...]) -> None:
            validate_preserved_state()
            record = next((item for item in active_journal.actions if item.path == path), None)
            if record is None:
                raise DistributionApplyError("journal-precondition-mismatch")
            parents = record.precondition.get("parents")
            if not isinstance(parents, list):
                raise DistributionApplyError("journal-precondition-mismatch")
            bindings = {item.relative_path: item for item in active_journal.created_parent_bindings}
            for index, parent in enumerate(parents, start=1):
                if not isinstance(parent, dict) or not isinstance(parent.get("relative_path"), str):
                    raise DistributionApplyError("journal-precondition-mismatch")
                binding = bindings.get(parent["relative_path"])
                if binding is None or not binding.exists:
                    continue
                if index >= len(parent_chain):
                    raise DistributionApplyError("journal-precondition-mismatch")
                _assert_created_parent_binding_fd_closed_set(
                    parent_chain[index],
                    binding.relative_path,
                    binding,
                    active_journal,
                )

        apply_distribution_plan(
            refreshed_executable.distribution_plan,
            allow_stale_stage_cleanup=bool(active_journal.staging_leases),
            stage_ownership=active_journal.staging_leases,
            stage_ownership_recorder=record_staging_lease,
            stage_ownership_remover=remove_staging_leases,
            created_parent_bindings=active_journal.created_parent_bindings,
            created_parent_recorder=record_created_parents,
            write_ahead_stage_reservations=True,
            progress_recorder=record_progress,
            before_mutation=validate_mutation_boundary,
            held_parent_validator=validate_held_parent_boundary,
            first_target_mutation_validator=validate_first_target_mutation,
        )
        # No later callback may reinterpret service-owned output as an
        # externally appeared preserved path.  Mutation paths deactivate at
        # their first namespace write; an all-adopt/preserve plan reaches this
        # boundary without a target mutation and is deactivated here.
        preserved_validation_active = False
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
        validate_preserved_state()
        _resume_executable_plan(post, active_journal)
        active_journal = store.mark_verified(active_journal)
        validate_preserved_state()
        active_journal = store.mark_completed(active_journal)
        if guard_marker is not None:
            validate_preserved_state()
            store.remove_legacy_marker(store._forward_guard or guard_marker)
        validate_preserved_state()
        store.remove_completed(active_journal, guard_already_removed=True)
        journal = active_journal
    except Exception as caught:
        failure: Exception = caught
        if (
            restore_legacy_marker_on_failure
            and legacy_marker_replaced
            and legacy_marker_bytes is not None
            and journal is None
        ):
            try:
                store.require_journal_absent = False
                current_guard = store._forward_guard or guard_marker
                if current_guard is None:
                    raise DistributionApplyError("dual-recovery-state")
                store.restore_marker_bytes(current_guard, legacy_marker_bytes)
                legacy_marker_replaced = False
            except Exception:
                failure = DistributionApplyError("dual-recovery-state")
        if not isinstance(failure, DistributionApplyError):
            reason = "generated-state-reconciliation-failed"
        else:
            reason = str(failure)
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
    if operation_package_version != package_version and intent != "fresh":
        return _execute_distribution_reconciliation(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent=intent,
            package_version=package_version,
            generated_assets=generated_assets,
            version_refreshable_existing_identities=(version_asset.identity,),
            root_identity_path=root_identity_path,
            created_workspace_identity=created_workspace_identity,
            preserved_state_validator=(preserved_state_validator if preserved_validation_active else None),
        )
    return DistributionProcessResult(
        status="completed",
        intent=intent,
        actions=assessment.actions,
        plan_digest=executable.plan_digest,
    )


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
    preserved_state_validator: Callable[[], None] | None = None,
) -> DistributionProcessResult:
    """Execute a recognized update or init-force through the shared service."""

    return _execute_distribution_reconciliation(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent=intent,
        package_version=package_version,
        legacy_marker=legacy_marker,
        generated_assets=generated_assets,
        version_refreshable_existing_identities=version_refreshable_existing_identities,
        root_identity_path=root_identity_path,
        preserved_state_validator=preserved_state_validator,
    )


def execute_fresh_distribution(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    package_version: str,
    legacy_marker: DistributionRetryMarker | None = None,
    generated_assets: tuple[DistributionAsset, ...] = (),
    root_identity_path: Path | None = None,
    created_workspace_identity: tuple[int, int] | None = None,
) -> DistributionProcessResult:
    """Execute a fresh operation through the shared journaled reconciliation core."""

    return _execute_distribution_reconciliation(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="fresh",
        package_version=package_version,
        legacy_marker=legacy_marker,
        generated_assets=generated_assets,
        root_identity_path=root_identity_path,
        created_workspace_identity=created_workspace_identity,
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
    first_target_mutation_validator: Callable[[], Callable[[], None] | None] | None = None,
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
                commit_first_mutation = (
                    first_target_mutation_validator() if first_target_mutation_validator is not None else None
                )
                try:
                    os.mkdir(component, dir_fd=fds[-1])
                except FileExistsError:
                    if expected_parent is not None and not expected_parent.exists:
                        raise DistributionApplyError(
                            f"managed target parent appeared during apply for '{target_rel}'"
                        ) from None
                else:
                    if commit_first_mutation is not None:
                        commit_first_mutation()
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


def _stat_optional_no_follow(parent_fd: int, name: str) -> os.stat_result | None:
    try:
        return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise DistributionApplyError("managed staging cleanup failed") from exc


def _distribution_quarantine_backup_name(quarantine_name: str) -> str:
    return f".spec-dock-backup-{hashlib.sha256(quarantine_name.encode()).hexdigest()[:32]}"


def _unlink_distribution_quarantine_with_backup(
    parent_fd: int,
    quarantine_name: str,
    stage_name: str,
    expected: os.stat_result,
    *,
    canonical_validator: Callable[[], None],
    mutation_validator: Callable[[], None] | None,
    allow_existing_backup: bool = False,
    backup_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    transition_path: str | None = None,
) -> None:
    """Unlink one exact quarantine while retaining a restorable hardlink."""

    backup_name = _distribution_quarantine_backup_name(quarantine_name)
    if mutation_validator is not None:
        mutation_validator()
    try:
        existing_backup = _stat_optional_no_follow(parent_fd, backup_name)
        if existing_backup is not None and not allow_existing_backup:
            raise DistributionApplyError("managed staging cleanup failed")
        if existing_backup is None:
            if backup_recorder is not None:
                if transition_path is None:
                    raise DistributionApplyError("managed staging cleanup failed")
                backup_recorder(
                    _reserved_distribution_stage_ownership(
                        transition_path,
                        backup_name,
                        "regular" if stat.S_ISREG(expected.st_mode) else "symlink",
                        role="backup-reserved",
                    )
                )
            os.link(
                quarantine_name,
                backup_name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            os.fsync(parent_fd)
        backup = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
        visible = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            visible.st_dev != backup.st_dev
            or visible.st_ino != backup.st_ino
            or _file_type(visible.st_mode) != _file_type(backup.st_mode)
            or backup.st_nlink < 2
            or visible.st_nlink < 2
            or visible.st_dev != expected.st_dev
            or visible.st_ino != expected.st_ino
        ):
            raise DistributionApplyError("managed staging cleanup failed")
        if backup_recorder is not None:
            if transition_path is None:
                raise DistributionApplyError("managed staging cleanup failed")
            backup_recorder(
                DistributionStageOwnership(
                    path=transition_path,
                    stage_name=backup_name,
                    device=visible.st_dev,
                    inode=visible.st_ino,
                    ctime_ns=visible.st_ctime_ns,
                    file_type="regular" if stat.S_ISREG(visible.st_mode) else "symlink",
                    role="backup-dual",
                )
            )
        canonical_validator()
        # A second no-follow observation closes an interposition after the
        # first final stat.  The backup remains an independent exact reference.
        final_visible = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
        final_backup = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            final_visible.st_dev != final_backup.st_dev
            or final_visible.st_ino != final_backup.st_ino
            or _file_type(final_visible.st_mode) != _file_type(final_backup.st_mode)
            or final_visible.st_nlink < 2
            or final_backup.st_nlink < 2
        ):
            with suppress(OSError):
                _rename_distribution_no_replace(parent_fd, backup_name, parent_fd, stage_name)
                os.fsync(parent_fd)
            raise DistributionApplyError("managed staging cleanup failed")
        if mutation_validator is not None:
            mutation_validator()
        if backup_recorder is not None:
            assert transition_path is not None
            backup_recorder(
                _reserved_distribution_stage_ownership(
                    transition_path,
                    backup_name,
                    "regular" if stat.S_ISREG(expected.st_mode) else "symlink",
                    role="backup-only-reserved",
                )
            )
        os.unlink(quarantine_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
        try:
            canonical_validator()
        except DistributionApplyError:
            with suppress(OSError):
                os.link(
                    backup_name,
                    quarantine_name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                    follow_symlinks=False,
                )
                os.fsync(parent_fd)
            raise
        final_backup = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
        if final_backup.st_dev != backup.st_dev or final_backup.st_ino != backup.st_ino:
            raise DistributionApplyError("managed staging cleanup failed")
        if backup_recorder is not None:
            if transition_path is None:
                raise DistributionApplyError("managed staging cleanup failed")
            backup_recorder(
                _distribution_stage_ownership(
                    transition_path,
                    backup_name,
                    final_backup,
                    role="backup-only",
                )
            )
            return
        os.unlink(backup_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    except (OSError, DistributionApplyError) as exc:
        with suppress(OSError):
            visible = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
            retained = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
            if visible.st_dev == retained.st_dev and visible.st_ino == retained.st_ino:
                os.unlink(backup_name, dir_fd=parent_fd)
                os.fsync(parent_fd)
        raise DistributionApplyError("managed staging cleanup failed") from exc


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
    mutation_validator: Callable[[], None] | None = None,
    canonical_validator: Callable[[], None] | None = None,
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
                role="predecessor-quarantine",
            )
        )
    if mutation_validator is not None:
        mutation_validator()
    try:
        _rename_distribution_no_replace(parent_fd, target_name, parent_fd, quarantine_name)
    except OSError as exc:
        raise DistributionApplyError(identity_message) from exc
    try:
        moved = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
        moved_matches_bound = (
            _stat_identity_tuple(moved) == _stat_identity_tuple(os.fstat(held_fd))
            if held_fd is not None
            else (
                moved.st_dev == expected.st_dev
                and moved.st_ino == expected.st_ino
                and moved.st_mode == expected.st_mode
                and moved.st_nlink == expected.st_nlink
            )
        )
        if not moved_matches_bound:
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
            transition_recorder(
                _distribution_stage_ownership(
                    transition_path,
                    quarantine_name,
                    moved,
                    role="predecessor-quarantine",
                )
            )
        if mutation_validator is not None:
            mutation_validator()
        try:
            if transition_recorder is None:
                _remove_distribution_stage_if_owned(parent_fd, quarantine_name, moved, strict=True)
            else:

                def assert_pruned_canonical_absent() -> None:
                    if canonical_validator is not None:
                        canonical_validator()
                    elif _stat_optional_no_follow(parent_fd, target_name) is not None:
                        raise DistributionApplyError(identity_message)

                _unlink_distribution_quarantine_with_backup(
                    parent_fd,
                    quarantine_name,
                    target_name,
                    moved,
                    canonical_validator=assert_pruned_canonical_absent,
                    mutation_validator=mutation_validator,
                    backup_recorder=transition_recorder,
                    transition_path=transition_path,
                )
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
    transition_path: str | None = None,
    canonical_name: str | None = None,
    canonical_ownership: DistributionStageOwnership | None = None,
    canonical_condition: dict[str, object] | None = None,
    stage_condition: dict[str, object] | None = None,
    recovery_stage_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    transition_name: str | None = None,
    transition_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    mutation_validator: Callable[[], None] | None = None,
    gc_path: str | None = None,
    gc_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    gc_name: str | None = None,
    gc_ordinal: int = 1,
    gc_predecessor_name: str | None = None,
) -> str | None:
    try:
        current = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError as exc:
        if strict:
            raise DistributionApplyError("managed staging cleanup failed") from exc
        return None
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
        return None
    if gc_recorder is not None and gc_path is None:
        raise DistributionApplyError("managed staging cleanup failed")
    transition_args = (
        transition_path,
        canonical_name,
        canonical_ownership,
        canonical_condition,
        stage_condition,
    )
    if any(item is not None for item in transition_args):
        if any(item is None for item in transition_args):
            raise DistributionApplyError("managed staging cleanup failed")
        assert transition_path is not None
        assert canonical_name is not None
        assert canonical_ownership is not None
        assert canonical_condition is not None
        assert stage_condition is not None
        try:
            canonical = os.stat(canonical_name, dir_fd=parent_fd, follow_symlinks=False)
            canonical_identity = _distribution_stage_identity(parent_fd, canonical_name, transition_path)
            stage_identity = _distribution_stage_identity(parent_fd, stage_name, transition_path)
        except (FileNotFoundError, OSError, DistributionApplyError) as exc:
            raise DistributionApplyError("managed staging cleanup failed") from exc
        canonical_owned = (
            canonical.st_dev == canonical_ownership.device
            and canonical.st_ino == canonical_ownership.inode
            and canonical.st_ctime_ns == canonical_ownership.ctime_ns
            and _file_type(canonical.st_mode) == canonical_ownership.file_type
            and canonical.st_nlink == 1
            and canonical_condition.get("identity") == _distribution_identity_payload(canonical_identity)
        )
        stage_owned = stage_condition.get("identity") == _distribution_identity_payload(stage_identity)
        stage_owned = stage_owned and all(
            stage_condition.get(field_name) == actual
            for field_name, actual in (
                ("device", current.st_dev),
                ("inode", current.st_ino),
                ("file_type", _file_type(current.st_mode)),
                ("link_count", current.st_nlink),
            )
        )
        if not canonical_owned or not stage_owned:
            raise DistributionApplyError("managed staging cleanup failed")
        quarantine_name = transition_name or f"{stage_name}.{secrets.token_hex(16)}.remove"
        held_fd: int | None = None
        original_link: str | None = None
        try:
            if stat.S_ISREG(current.st_mode):
                nofollow = getattr(os, "O_NOFOLLOW", None)
                if not isinstance(nofollow, int):
                    raise DistributionApplyError("platform lacks required no-follow file support")
                held_fd = os.open(
                    stage_name,
                    os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=parent_fd,
                )
                if _stat_identity_tuple(os.fstat(held_fd)) != _stat_identity_tuple(current):
                    raise DistributionApplyError("managed staging cleanup failed")
            elif stat.S_ISLNK(current.st_mode):
                original_link = os.readlink(stage_name, dir_fd=parent_fd)
                if _stat_identity_tuple(
                    os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                ) != _stat_identity_tuple(current):
                    raise DistributionApplyError("managed staging cleanup failed")
            else:
                raise DistributionApplyError("managed staging cleanup failed")
            if transition_recorder is not None:
                transition_recorder(
                    _reserved_distribution_stage_ownership(
                        transition_path,
                        quarantine_name,
                        "regular" if stat.S_ISREG(current.st_mode) else "symlink",
                        role="predecessor-quarantine",
                    )
                )
            if mutation_validator is not None:
                mutation_validator()
            _rename_distribution_no_replace(parent_fd, stage_name, parent_fd, quarantine_name)
            os.fsync(parent_fd)
            moved = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
            if held_fd is not None:
                if _stat_identity_tuple(moved) != _stat_identity_tuple(os.fstat(held_fd)):
                    raise DistributionApplyError("managed staging cleanup failed")
            elif (
                original_link is None
                or os.readlink(quarantine_name, dir_fd=parent_fd) != original_link
                or _stat_identity_tuple(os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False))
                != _stat_identity_tuple(moved)
            ):
                raise DistributionApplyError("managed staging cleanup failed")
            moved_identity = _distribution_stage_identity(parent_fd, quarantine_name, transition_path)
            if stage_condition.get("identity") != _distribution_identity_payload(moved_identity):
                raise DistributionApplyError("managed staging cleanup failed")
            if transition_recorder is not None:
                transition_recorder(
                    _distribution_stage_ownership(
                        transition_path,
                        quarantine_name,
                        moved,
                        role="predecessor-quarantine",
                    )
                )
            if mutation_validator is not None:
                mutation_validator()

            def assert_canonical_successor() -> None:
                canonical = os.stat(canonical_name, dir_fd=parent_fd, follow_symlinks=False)
                canonical_identity = _distribution_stage_identity(parent_fd, canonical_name, transition_path)
                if (
                    canonical.st_dev != canonical_ownership.device
                    or canonical.st_ino != canonical_ownership.inode
                    or canonical.st_ctime_ns != canonical_ownership.ctime_ns
                    or _file_type(canonical.st_mode) != canonical_ownership.file_type
                    or canonical.st_nlink != 1
                    or canonical_condition.get("identity") != _distribution_identity_payload(canonical_identity)
                ):
                    raise DistributionApplyError("managed staging cleanup failed")

            assert_canonical_successor()
            _unlink_distribution_quarantine_with_backup(
                parent_fd,
                quarantine_name,
                stage_name,
                moved,
                canonical_validator=assert_canonical_successor,
                mutation_validator=mutation_validator,
                backup_recorder=transition_recorder,
                transition_path=transition_path,
            )
            return None
        except (DistributionApplyError, OSError) as exc:
            with suppress(DistributionApplyError):
                _restore_distribution_quarantine(
                    parent_fd,
                    quarantine_name,
                    stage_name,
                    failure_message="managed staging cleanup failed",
                )
            if transition_recorder is not None:
                with suppress(Exception):
                    transition_recorder(
                        _reserved_distribution_stage_ownership(
                            transition_path,
                            quarantine_name,
                            "regular" if stat.S_ISREG(current.st_mode) else "symlink",
                            role="predecessor-quarantine",
                        )
                    )
            if recovery_stage_recorder is not None:
                with suppress(Exception):
                    restored = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                    restored_identity = _distribution_stage_identity(parent_fd, stage_name, transition_path)
                    if stage_condition.get("identity") == _distribution_identity_payload(restored_identity):
                        recovery_stage_recorder(_distribution_stage_ownership(transition_path, stage_name, restored))
            raise DistributionApplyError("managed staging cleanup failed") from exc
        finally:
            if held_fd is not None:
                os.close(held_fd)
    try:
        quarantine_name = gc_name or f"{stage_name}.{secrets.token_hex(16)}.gc"
        delete_name: str | None = None
        retained_gc_name: str | None = None
        gc_held_fd: int | None = None
        gc_original_link: str | None = None
        if stat.S_ISREG(current.st_mode):
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise DistributionApplyError("platform lacks required no-follow file support")
            gc_held_fd = os.open(
                stage_name,
                os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent_fd,
            )
            if _stat_identity_tuple(os.fstat(gc_held_fd)) != _stat_identity_tuple(current):
                raise DistributionApplyError("managed staging identity changed")
        elif stat.S_ISLNK(current.st_mode):
            gc_original_link = os.readlink(stage_name, dir_fd=parent_fd)
            if _stat_identity_tuple(
                os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
            ) != _stat_identity_tuple(current):
                raise DistributionApplyError("managed staging identity changed")
        else:
            raise DistributionApplyError("managed staging identity changed")
        try:
            if gc_recorder is not None:
                if gc_path is None:
                    raise DistributionApplyError("managed staging cleanup failed")
                gc_recorder(
                    _reserved_distribution_stage_ownership(
                        gc_path,
                        quarantine_name,
                        "regular" if stat.S_ISREG(current.st_mode) else "symlink",
                        role="gc-reserved",
                        gc_predecessor_name=gc_predecessor_name or stage_name,
                        gc_ordinal=gc_ordinal,
                    )
                )
            if mutation_validator is not None:
                mutation_validator()
            _rename_distribution_no_replace(parent_fd, stage_name, parent_fd, quarantine_name)
            os.fsync(parent_fd)
            moved = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
            moved_is_exact = (
                _stat_identity_tuple(moved) == _stat_identity_tuple(os.fstat(gc_held_fd))
                if gc_held_fd is not None
                else (
                    gc_original_link is not None
                    and moved.st_dev == current.st_dev
                    and moved.st_ino == current.st_ino
                    and moved.st_mode == current.st_mode
                    and moved.st_nlink == current.st_nlink
                    and os.readlink(quarantine_name, dir_fd=parent_fd) == gc_original_link
                )
            )
            if not moved_is_exact:
                _restore_distribution_quarantine(
                    parent_fd,
                    quarantine_name,
                    stage_name,
                    failure_message="managed staging cleanup failed",
                )
                raise DistributionApplyError("managed staging identity changed")
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    _distribution_stage_ownership(
                        gc_path,
                        quarantine_name,
                        moved,
                        role="gc-exact",
                        gc_predecessor_name=gc_predecessor_name or stage_name,
                        gc_ordinal=gc_ordinal,
                    )
                )
                try:
                    if mutation_validator is not None:
                        mutation_validator()
                except DistributionApplyError:
                    _restore_distribution_quarantine(
                        parent_fd,
                        quarantine_name,
                        stage_name,
                        failure_message="managed staging cleanup failed",
                    )
                    raise
            # Keep an independent exact link until the moved deletion
            # candidate has been revalidated.  A replacement of the first
            # quarantine name is then moved, inspected, and restored instead
            # of being unlinked as if it were operation-owned.
            retained_name = stage_name
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    _reserved_distribution_stage_ownership(
                        gc_path,
                        retained_name,
                        "regular" if stat.S_ISREG(moved.st_mode) else "symlink",
                        role="backup-reserved",
                    )
                )
            os.link(
                quarantine_name,
                retained_name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            os.fsync(parent_fd)
            verified = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
            if (
                verified.st_dev != moved.st_dev
                or verified.st_ino != moved.st_ino
                or verified.st_mode != moved.st_mode
                or verified.st_nlink != 2
                or (stat.S_ISLNK(moved.st_mode) and os.readlink(quarantine_name, dir_fd=parent_fd) != gc_original_link)
            ):
                raise DistributionApplyError("managed staging identity changed")
            if gc_recorder is not None:
                assert gc_path is not None
                retained = os.stat(retained_name, dir_fd=parent_fd, follow_symlinks=False)
                gc_recorder(
                    _distribution_stage_ownership(
                        gc_path,
                        retained_name,
                        retained,
                        role="backup-dual",
                    )
                )
                gc_recorder(
                    DistributionStageOwnership(
                        path=gc_path,
                        stage_name=quarantine_name,
                        device=verified.st_dev,
                        inode=verified.st_ino,
                        ctime_ns=verified.st_ctime_ns,
                        file_type="regular" if stat.S_ISREG(verified.st_mode) else "symlink",
                        role="gc-exact",
                        gc_predecessor_name=gc_predecessor_name or stage_name,
                        gc_ordinal=gc_ordinal,
                    )
                )
            delete_name = f"{stage_name}.{secrets.token_hex(16)}.gc"
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    _reserved_distribution_stage_ownership(
                        gc_path,
                        delete_name,
                        "regular" if stat.S_ISREG(moved.st_mode) else "symlink",
                        role="gc-reserved",
                        gc_predecessor_name=quarantine_name,
                        gc_ordinal=2,
                    )
                )
            _rename_distribution_no_replace(parent_fd, quarantine_name, parent_fd, delete_name)
            os.fsync(parent_fd)
            deleting = os.stat(delete_name, dir_fd=parent_fd, follow_symlinks=False)
            retained = os.stat(retained_name, dir_fd=parent_fd, follow_symlinks=False)
            if (
                deleting.st_dev != retained.st_dev
                or deleting.st_ino != retained.st_ino
                or _file_type(deleting.st_mode) != _file_type(retained.st_mode)
                or deleting.st_nlink != retained.st_nlink
                or deleting.st_nlink != 2
                or (stat.S_ISLNK(deleting.st_mode) and os.readlink(delete_name, dir_fd=parent_fd) != gc_original_link)
            ):
                _restore_distribution_quarantine(
                    parent_fd,
                    delete_name,
                    quarantine_name,
                    failure_message="managed staging cleanup failed",
                )
                raise DistributionApplyError("managed staging identity changed")
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    DistributionStageOwnership(
                        path=gc_path,
                        stage_name=delete_name,
                        device=deleting.st_dev,
                        inode=deleting.st_ino,
                        ctime_ns=deleting.st_ctime_ns,
                        file_type="regular" if stat.S_ISREG(deleting.st_mode) else "symlink",
                        role="gc-exact",
                        gc_predecessor_name=quarantine_name,
                        gc_ordinal=2,
                    )
                )
            try:
                if mutation_validator is not None:
                    mutation_validator()
            except DistributionApplyError:
                raise
            retained_gc_name = f"{stage_name}.{secrets.token_hex(16)}.gc"
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    _reserved_distribution_stage_ownership(
                        gc_path,
                        retained_gc_name,
                        "regular" if stat.S_ISREG(retained.st_mode) else "symlink",
                        role="gc-reserved",
                        gc_predecessor_name=retained_name,
                        gc_ordinal=3,
                    )
                )
            _rename_distribution_no_replace(
                parent_fd,
                retained_name,
                parent_fd,
                retained_gc_name,
            )
            os.fsync(parent_fd)
            retained_gc = os.stat(retained_gc_name, dir_fd=parent_fd, follow_symlinks=False)
            deleting = os.stat(delete_name, dir_fd=parent_fd, follow_symlinks=False)
            if (
                retained_gc.st_dev != deleting.st_dev
                or retained_gc.st_ino != deleting.st_ino
                or _file_type(retained_gc.st_mode) != _file_type(deleting.st_mode)
                or retained_gc.st_nlink != deleting.st_nlink
                or retained_gc.st_nlink != 2
                or (
                    stat.S_ISLNK(retained_gc.st_mode)
                    and os.readlink(retained_gc_name, dir_fd=parent_fd) != gc_original_link
                )
            ):
                _restore_distribution_quarantine(
                    parent_fd,
                    retained_gc_name,
                    retained_name,
                    failure_message="managed staging cleanup failed",
                )
                raise DistributionApplyError("managed staging identity changed")
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    DistributionStageOwnership(
                        path=gc_path,
                        stage_name=retained_gc_name,
                        device=retained_gc.st_dev,
                        inode=retained_gc.st_ino,
                        ctime_ns=retained_gc.st_ctime_ns,
                        file_type="regular" if stat.S_ISREG(retained_gc.st_mode) else "symlink",
                        role="gc-exact",
                        gc_predecessor_name=retained_name,
                        gc_ordinal=3,
                    )
                )
            if mutation_validator is not None:
                mutation_validator()
            os.unlink(delete_name, dir_fd=parent_fd)
            os.fsync(parent_fd)
            retained = os.stat(retained_gc_name, dir_fd=parent_fd, follow_symlinks=False)
            if (
                retained.st_dev != moved.st_dev
                or retained.st_ino != moved.st_ino
                or _file_type(retained.st_mode) != _file_type(moved.st_mode)
                or retained.st_nlink != 1
                or (
                    stat.S_ISLNK(retained.st_mode)
                    and os.readlink(retained_gc_name, dir_fd=parent_fd) != gc_original_link
                )
            ):
                raise DistributionApplyError("managed staging identity changed")
            if gc_recorder is not None:
                assert gc_path is not None
                gc_recorder(
                    _distribution_stage_ownership(
                        gc_path,
                        retained_gc_name,
                        retained,
                        role="backup-only",
                        gc_predecessor_name=retained_name,
                        gc_ordinal=3,
                    )
                )
            if mutation_validator is not None and gc_recorder is not None:
                mutation_validator()
            os.unlink(retained_gc_name, dir_fd=parent_fd)
            os.fsync(parent_fd)
            return retained_gc_name
        except Exception:
            if retained_gc_name is not None:
                with suppress(OSError, DistributionApplyError):
                    if (
                        _stat_optional_no_follow(parent_fd, retained_gc_name) is not None
                        and _stat_optional_no_follow(parent_fd, retained_name) is None
                    ):
                        _restore_distribution_quarantine(
                            parent_fd,
                            retained_gc_name,
                            retained_name,
                            failure_message="managed staging cleanup failed",
                        )
            if delete_name is not None:
                with suppress(OSError, DistributionApplyError):
                    deleting = os.stat(delete_name, dir_fd=parent_fd, follow_symlinks=False)
                    retained = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                    if (
                        deleting.st_dev == retained.st_dev
                        and deleting.st_ino == retained.st_ino
                        and _file_type(deleting.st_mode) == _file_type(retained.st_mode)
                        and deleting.st_nlink == retained.st_nlink == 2
                    ):
                        os.unlink(delete_name, dir_fd=parent_fd)
                        os.fsync(parent_fd)
                        restored = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                        if recovery_stage_recorder is not None and gc_path is not None:
                            recovery_stage_recorder(_distribution_stage_ownership(gc_path, stage_name, restored))
            with suppress(OSError, DistributionApplyError):
                retained = os.stat(quarantine_name, dir_fd=parent_fd, follow_symlinks=False)
                retained_is_exact = (
                    _stat_identity_tuple(retained) == _stat_identity_tuple(os.fstat(gc_held_fd))
                    if gc_held_fd is not None
                    else (
                        gc_original_link is not None
                        and retained.st_dev == current.st_dev
                        and retained.st_ino == current.st_ino
                        and retained.st_mode == current.st_mode
                        and retained.st_nlink == current.st_nlink
                        and os.readlink(quarantine_name, dir_fd=parent_fd) == gc_original_link
                    )
                )
                if retained_is_exact and _stat_optional_no_follow(parent_fd, stage_name) is None:
                    _restore_distribution_quarantine(
                        parent_fd,
                        quarantine_name,
                        stage_name,
                        failure_message="managed staging cleanup failed",
                    )
                    if recovery_stage_recorder is not None and gc_path is not None:
                        restored = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                        recovery_stage_recorder(_distribution_stage_ownership(gc_path, stage_name, restored))
            raise
        finally:
            if gc_held_fd is not None:
                os.close(gc_held_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        if strict:
            raise DistributionApplyError("managed staging cleanup failed") from exc
        return None


def _distribution_stage_identity(
    parent_fd: int,
    stage_name: str,
    path: str,
    *,
    allow_backup_link: bool = False,
) -> DistributionIdentity | None:
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
    if info.st_nlink not in ({1, 2} if allow_backup_link else {1}):
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
                or opened.st_nlink != info.st_nlink
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
    *,
    role: Literal[
        "stage",
        "predecessor-quarantine",
        "backup-reserved",
        "backup-dual",
        "backup-only-reserved",
        "backup-only",
        "gc-reserved",
        "gc-exact",
    ] = "stage",
    gc_predecessor_name: str | None = None,
    gc_ordinal: int | None = None,
) -> DistributionStageOwnership:
    kind = _file_type(info.st_mode)
    expected_links = 2 if role == "backup-dual" else 1
    if kind not in {"regular", "symlink"} or info.st_nlink != expected_links:
        raise DistributionApplyError("managed staging artifact is not safe to record")
    file_type: Literal["regular", "symlink"] = "regular" if kind == "regular" else "symlink"
    return DistributionStageOwnership(
        path=path,
        stage_name=stage_name,
        device=info.st_dev,
        inode=info.st_ino,
        ctime_ns=info.st_ctime_ns,
        file_type=file_type,
        role=role,
        gc_predecessor_name=gc_predecessor_name,
        gc_ordinal=gc_ordinal,
    )


def _reserved_distribution_stage_ownership(
    path: str,
    stage_name: str,
    file_type: Literal["regular", "symlink"],
    *,
    role: Literal[
        "stage",
        "predecessor-quarantine",
        "backup-reserved",
        "backup-dual",
        "backup-only-reserved",
        "backup-only",
        "gc-reserved",
        "gc-exact",
    ] = "stage",
    gc_predecessor_name: str | None = None,
    gc_ordinal: int | None = None,
) -> DistributionStageOwnership:
    """Persist a private stage name before its namespace entry is created."""

    return DistributionStageOwnership(
        path=path,
        stage_name=stage_name,
        device=0,
        inode=0,
        ctime_ns=0,
        file_type=file_type,
        role=role,
        gc_predecessor_name=gc_predecessor_name,
        gc_ordinal=gc_ordinal,
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
    mutation_validator: Callable[[tuple[int, ...]], None] | None = None,
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    stage_ownership_remover: Callable[[str, tuple[str, ...]], None] | None = None,
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

        def validate_cleanup_namespace() -> None:
            if mutation_validator is not None:
                mutation_validator(parent_chain)

        validate_cleanup_namespace()
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
            if owned.role != "stage":
                continue
            if owned.device == owned.inode == owned.ctime_ns == 0:
                if _file_type(current.st_mode) != owned.file_type or current.st_nlink != 1:
                    mismatch_detected = True
                    continue
            elif (
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
            if stage_ownership_recorder is None or stage_ownership_remover is None:
                _remove_distribution_stage_if_owned(
                    parent_fd,
                    owned.stage_name,
                    current,
                    strict=True,
                    mutation_validator=validate_cleanup_namespace,
                )
                cleaned = True
                continue
            quarantine_name = f"{owned.stage_name}.{secrets.token_hex(16)}.remove"
            held_fd: int | None = None
            try:
                if stat.S_ISREG(current.st_mode):
                    nofollow = getattr(os, "O_NOFOLLOW", None)
                    if not isinstance(nofollow, int):
                        raise DistributionApplyError("platform lacks required no-follow file support")
                    held_fd = os.open(
                        owned.stage_name,
                        os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                        dir_fd=parent_fd,
                    )
                _remove_distribution_target_if_bound(
                    parent_fd,
                    owned.stage_name,
                    current,
                    held_fd=held_fd,
                    identity_message="managed staging cleanup failed",
                    transition_path=owned.path,
                    transition_name=quarantine_name,
                    transition_recorder=stage_ownership_recorder,
                    mutation_validator=validate_cleanup_namespace,
                )
            finally:
                if held_fd is not None:
                    os.close(held_fd)
            backup_name = _distribution_quarantine_backup_name(quarantine_name)
            backup = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
            validate_cleanup_namespace()
            gc_name = _remove_distribution_stage_if_owned(
                parent_fd,
                backup_name,
                backup,
                strict=True,
                mutation_validator=validate_cleanup_namespace,
                gc_path=owned.path,
                gc_recorder=stage_ownership_recorder,
            )
            stage_ownership_remover(
                owned.path,
                tuple(name for name in (owned.stage_name, quarantine_name, backup_name, gc_name) if name is not None),
            )
            cleaned = True
        if mismatch_detected and not cleaned:
            raise DistributionApplyError("managed staging identity changed")
    finally:
        _close_distribution_parent_chain(parent_chain)


def _expected_target_identity(plan: DistributionPlan, path: str) -> DistributionIdentity | None:
    identity = _target_identity_specs(plan.current_assets, plan.scaffold_assets).get(path)
    return identity if identity is not None else _required_directory_identity(plan, path)


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
    if observation.snapshot is None:
        raise DistributionApplyError(f"managed target identity changed for '{path}'")
    try:
        _assert_pending_snapshot_stable(
            observation.snapshot,
            expected,
            path,
            {},
        )
    except DistributionApplyError:
        raise DistributionApplyError(f"managed target identity changed for '{path}'") from None
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
    target_matches = (
        _same_structure_identity(actual.target, expected.target)
        if expected.target.file_type == "directory"
        else actual.target == expected.target
    )
    if not target_matches:
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
    before_mutation: Callable[[], None] | None,
    held_parent_validator: Callable[[str, tuple[int, ...]], None] | None,
    first_target_mutation_validator: Callable[[], Callable[[], None] | None] | None,
) -> None:
    path = action.path
    if action.action == "prune" and not snapshot.target.exists:
        return
    if first_target_mutation_validator is None:
        parent_chain = _open_distribution_parent_chain(
            target_root,
            path,
            create_missing=action.action == "create",
            expected_snapshot=snapshot,
            created_parent_bindings=created_parent_bindings,
            created_parent_recorder=created_parent_recorder,
        )
    else:
        parent_chain = _open_distribution_parent_chain(
            target_root,
            path,
            create_missing=action.action == "create",
            expected_snapshot=snapshot,
            created_parent_bindings=created_parent_bindings,
            created_parent_recorder=created_parent_recorder,
            first_target_mutation_validator=first_target_mutation_validator,
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

        def validate_held_namespace() -> None:
            if before_mutation is not None:
                before_mutation()
            if held_parent_validator is not None:
                held_parent_validator(path, parent_chain)

        validate_held_namespace()
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
                validate_held_namespace()
            validate_held_namespace()
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            fd = os.open(
                staging_name,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                source_mode,
                dir_fd=parent_fd,
            )
            if commit_first_mutation is not None:
                commit_first_mutation()
            created = os.fstat(fd)
            validate_held_namespace()
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
                    validate_held_namespace()
                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                validate_held_namespace()
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
                            mutation_validator=validate_held_namespace,
                            gc_path=path,
                            gc_recorder=stage_ownership_recorder,
                            recovery_stage_recorder=stage_ownership_recorder,
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
                commit_first_mutation = (
                    first_target_mutation_validator() if first_target_mutation_validator is not None else None
                )
                validate_held_namespace()
                _remove_distribution_target_if_bound(
                    parent_fd,
                    target_name,
                    opened,
                    held_fd=fd,
                    identity_message=f"managed target identity changed for '{path}'",
                    transition_path=path,
                    transition_name=_new_distribution_stage_name(path, target_identity),
                    transition_recorder=(stage_ownership_recorder if write_ahead_stage_reservations else None),
                    mutation_validator=validate_held_namespace,
                )
                if commit_first_mutation is not None:
                    commit_first_mutation()
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
                validate_held_namespace()
            validate_held_namespace()
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            staging_fd = os.open(
                staging_name,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                source_mode,
                dir_fd=parent_fd,
            )
            if commit_first_mutation is not None:
                commit_first_mutation()
            staging_stat = os.fstat(staging_fd)
            validate_held_namespace()
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
                    validate_held_namespace()

                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                _assert_regular_fd_safe(fd, snapshot.target, path, exact=True)
                if hashlib.sha256(_read_fd_bytes(fd)).hexdigest() != target_identity.sha256:
                    raise DistributionApplyError(f"managed target identity changed for '{path}'")
                validate_held_namespace()
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
                staged_successor = os.fstat(staging_fd)

                published_fd = os.open(
                    target_name, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd
                )
                try:
                    published = os.fstat(published_fd)
                    if (
                        _stat_identity_tuple(published) != _stat_identity_tuple(staged_successor)
                        or published.st_nlink != 1
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
                                mutation_validator=validate_held_namespace,
                                gc_path=path,
                                gc_recorder=stage_ownership_recorder,
                                recovery_stage_recorder=stage_ownership_recorder,
                            )
                else:
                    published_successor = staged_successor
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
                            successor_ownership = _distribution_stage_ownership(
                                path,
                                staging_name,
                                published_successor,
                            )
                            successor_condition: dict[str, object] = {
                                "identity": _distribution_identity_payload(expected)
                            }
                            predecessor_condition: dict[str, object] = {
                                "device": snapshot.target.device,
                                "inode": snapshot.target.inode,
                                "file_type": snapshot.target.file_type,
                                "link_count": snapshot.target.link_count,
                                "identity": _distribution_identity_payload(snapshot.target.identity),
                            }
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
                                            transition_path=path,
                                            canonical_name=target_name,
                                            canonical_ownership=successor_ownership,
                                            canonical_condition=successor_condition,
                                            stage_condition=predecessor_condition,
                                            recovery_stage_recorder=(
                                                stage_ownership_recorder if not write_ahead_stage_reservations else None
                                            ),
                                            transition_recorder=(
                                                stage_ownership_recorder if write_ahead_stage_reservations else None
                                            ),
                                            mutation_validator=validate_held_namespace,
                                        )
                                    except DistributionApplyError as cleanup_error:
                                        # Quarantine restoration changes ctime.  Do not
                                        # reacquire predecessor authority from a fresh
                                        # stat and retry in-place; the recovery recorder
                                        # above persisted the new exact lease for the
                                        # next normal recovery pass.
                                        raise cleanup_error from record_error
                                    raise
                            current_successor = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                            if _stat_identity_tuple(current_successor) != _stat_identity_tuple(published_successor):
                                raise DistributionApplyError(f"managed target identity changed for '{path}'")
                            _remove_distribution_stage_if_owned(
                                parent_fd,
                                staging_name,
                                old_stat,
                                strict=True,
                                transition_path=path,
                                canonical_name=target_name,
                                canonical_ownership=successor_ownership,
                                canonical_condition=successor_condition,
                                stage_condition=predecessor_condition,
                                recovery_stage_recorder=(
                                    stage_ownership_recorder if not write_ahead_stage_reservations else None
                                ),
                                transition_recorder=(
                                    stage_ownership_recorder if write_ahead_stage_reservations else None
                                ),
                                mutation_validator=validate_held_namespace,
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
    before_mutation: Callable[[], None] | None,
    held_parent_validator: Callable[[str, tuple[int, ...]], None] | None,
    first_target_mutation_validator: Callable[[], Callable[[], None] | None] | None,
) -> None:
    if expected.target is None:
        raise DistributionApplyError(f"managed symlink identity has no target for '{action.path}'")
    expected_target = expected.target
    if action.action == "prune" and not snapshot.target.exists:
        return
    if first_target_mutation_validator is None:
        parent_chain = _open_distribution_parent_chain(
            target_root,
            action.path,
            create_missing=action.action == "create",
            expected_snapshot=snapshot,
            created_parent_bindings=created_parent_bindings,
            created_parent_recorder=created_parent_recorder,
        )
    else:
        parent_chain = _open_distribution_parent_chain(
            target_root,
            action.path,
            create_missing=action.action == "create",
            expected_snapshot=snapshot,
            created_parent_bindings=created_parent_bindings,
            created_parent_recorder=created_parent_recorder,
            first_target_mutation_validator=first_target_mutation_validator,
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

        def validate_held_namespace() -> None:
            if before_mutation is not None:
                before_mutation()
            if held_parent_validator is not None:
                held_parent_validator(action.path, parent_chain)

        validate_held_namespace()
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
                validate_held_namespace()
            validate_held_namespace()
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            os.symlink(expected_target, staging_name, dir_fd=parent_fd)
            if commit_first_mutation is not None:
                commit_first_mutation()
            staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            validate_held_namespace()
            published = False
            try:
                staged_target = _normalized_link_target_for_path(
                    action.path, os.readlink(staging_name, dir_fd=parent_fd)
                )
                if staged_target != expected_target or staging_stat.st_nlink != 1:
                    raise DistributionApplyError(f"managed target staging failed for '{action.path}'")
                if stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(action.path, staging_name, staging_stat))
                    validate_held_namespace()
                _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
                validate_held_namespace()
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
                            mutation_validator=validate_held_namespace,
                            gc_path=action.path,
                            gc_recorder=stage_ownership_recorder,
                            recovery_stage_recorder=stage_ownership_recorder,
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
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            validate_held_namespace()
            _remove_distribution_target_if_bound(
                parent_fd,
                target_name,
                latest_stat,
                identity_message=f"managed target identity changed for '{action.path}'",
                transition_path=action.path,
                transition_name=_new_distribution_stage_name(action.path, snapshot.target.identity),
                transition_recorder=(stage_ownership_recorder if write_ahead_stage_reservations else None),
                mutation_validator=validate_held_namespace,
            )
            if commit_first_mutation is not None:
                commit_first_mutation()
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
                validate_held_namespace()
            validate_held_namespace()
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            os.symlink(expected_target, staging_name, dir_fd=parent_fd)
            if commit_first_mutation is not None:
                commit_first_mutation()
            staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            validate_held_namespace()
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
                    validate_held_namespace()
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
                validate_held_namespace()
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
                            mutation_validator=validate_held_namespace,
                            gc_path=action.path,
                            gc_recorder=stage_ownership_recorder,
                            recovery_stage_recorder=stage_ownership_recorder,
                        )
                else:
                    current_successor = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                    current_target = _normalized_link_target_for_path(
                        action.path,
                        os.readlink(target_name, dir_fd=parent_fd),
                    )
                    if (
                        _stat_structure_tuple(current_successor) != _stat_structure_tuple(staging_stat)
                        or current_target != expected_target
                    ):
                        raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                    published_successor = current_successor
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
                            successor_ownership = _distribution_stage_ownership(
                                action.path,
                                staging_name,
                                published_successor,
                            )
                            successor_condition: dict[str, object] = {
                                "identity": _distribution_identity_payload(expected)
                            }
                            predecessor_condition: dict[str, object] = {
                                "device": snapshot.target.device,
                                "inode": snapshot.target.inode,
                                "file_type": snapshot.target.file_type,
                                "link_count": snapshot.target.link_count,
                                "identity": _distribution_identity_payload(snapshot.target.identity),
                            }
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
                                    # then fall back to strict cleanup.
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
                                            transition_path=action.path,
                                            canonical_name=target_name,
                                            canonical_ownership=successor_ownership,
                                            canonical_condition=successor_condition,
                                            stage_condition=predecessor_condition,
                                            recovery_stage_recorder=(
                                                stage_ownership_recorder if not write_ahead_stage_reservations else None
                                            ),
                                            transition_recorder=(
                                                stage_ownership_recorder if write_ahead_stage_reservations else None
                                            ),
                                            mutation_validator=validate_held_namespace,
                                        )
                                    except DistributionApplyError as cleanup_error:
                                        # Restoration changes ctime; only a
                                        # persisted exact recovery lease may
                                        # authorize the next cleanup attempt.
                                        raise cleanup_error from record_error
                                    raise
                            current_successor = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                            if _stat_identity_tuple(current_successor) != _stat_identity_tuple(published_successor):
                                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                            _remove_distribution_stage_if_owned(
                                parent_fd,
                                staging_name,
                                old_stat,
                                strict=True,
                                transition_path=action.path,
                                canonical_name=target_name,
                                canonical_ownership=successor_ownership,
                                canonical_condition=successor_condition,
                                stage_condition=predecessor_condition,
                                recovery_stage_recorder=(
                                    stage_ownership_recorder if not write_ahead_stage_reservations else None
                                ),
                                transition_recorder=(
                                    stage_ownership_recorder if write_ahead_stage_reservations else None
                                ),
                                mutation_validator=validate_held_namespace,
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
    before_mutation: Callable[[], None] | None = None,
    held_parent_validator: Callable[[str, tuple[int, ...]], None] | None = None,
    first_target_mutation_validator: Callable[[], Callable[[], None] | None] | None = None,
) -> None:
    if action.action in {"adopt", "preserve"}:
        return
    if action.action == "ensure-directory":
        parent_chain = _open_distribution_parent_chain(
            target_root,
            action.path,
            create_missing=False,
            expected_snapshot=snapshot,
            created_parent_bindings=created_parent_bindings,
        )
        try:
            if before_mutation is not None:
                before_mutation()
            if held_parent_validator is not None:
                held_parent_validator(action.path, parent_chain)
            parent_fd = parent_chain[-1]
            name = PurePosixPath(action.path).name
            try:
                existing = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                existing = None
            if existing is not None:
                if not stat.S_ISDIR(existing.st_mode) or stat.S_ISLNK(existing.st_mode):
                    raise DistributionApplyError(f"required directory appeared unsafely for '{action.path}'")
                binding = _snapshot_from_stat(action.path, existing)
                previous = created_parent_bindings.get(action.path)
                if previous is None or not _same_stat_structure(existing, previous):
                    raise DistributionApplyError(f"required directory appeared during apply for '{action.path}'")
                return
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            os.mkdir(name, dir_fd=parent_fd)
            if commit_first_mutation is not None:
                commit_first_mutation()
            os.fsync(parent_fd)
            created = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if not stat.S_ISDIR(created.st_mode) or stat.S_ISLNK(created.st_mode) or created.st_nlink < 1:
                raise DistributionApplyError(f"required directory verification failed for '{action.path}'")
            binding = _snapshot_from_stat(action.path, created)
            created_parent_bindings[action.path] = binding
            if created_parent_recorder is not None:
                created_parent_recorder(
                    tuple(created_parent_bindings[path] for path in sorted(created_parent_bindings))
                )
        except FileExistsError as exc:
            raise DistributionApplyError(f"required directory appeared during apply for '{action.path}'") from exc
        except OSError as exc:
            raise DistributionApplyError(f"required directory apply failed for '{action.path}'") from exc
        finally:
            _close_distribution_parent_chain(parent_chain)
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
            before_mutation=before_mutation,
            held_parent_validator=held_parent_validator,
            first_target_mutation_validator=first_target_mutation_validator,
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
            before_mutation=before_mutation,
            held_parent_validator=held_parent_validator,
            first_target_mutation_validator=first_target_mutation_validator,
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
        before_mutation=before_mutation,
        held_parent_validator=held_parent_validator,
        first_target_mutation_validator=first_target_mutation_validator,
    )


def apply_distribution_plan(
    plan: DistributionPlan,
    *,
    allow_stale_stage_cleanup: bool = False,
    allow_blocked_scaffold_paths: bool = False,
    stage_ownership: tuple[DistributionStageOwnership, ...] = (),
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    stage_ownership_remover: Callable[[str, tuple[str, ...]], None] | None = None,
    created_parent_bindings: tuple[PathIdentitySnapshot, ...] = (),
    created_parent_recorder: Callable[[tuple[PathIdentitySnapshot, ...]], None] | None = None,
    write_ahead_stage_reservations: bool = False,
    scaffold_applier: Callable[[], None] | None = None,
    progress_recorder: Callable[[str, tuple[str, ...], tuple[str, ...], bool], None] | None = None,
    before_mutation: Callable[[], None] | None = None,
    held_parent_validator: Callable[[str, tuple[int, ...]], None] | None = None,
    first_target_mutation_validator: Callable[[], Callable[[], None] | None] | None = None,
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
            if before_mutation is not None:
                before_mutation()
            commit_first_mutation = (
                first_target_mutation_validator() if first_target_mutation_validator is not None else None
            )
            scaffold_applier()
            if commit_first_mutation is not None:
                commit_first_mutation()
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
    required_directory_paths = {item.path for item in plan.required_directories}
    external_actions = tuple(action for action in plan.actions if action.path not in scaffold_paths)
    directory_actions = tuple(action for action in external_actions if action.path in required_directory_paths)
    action_groups = (
        ("ensure-directory", directory_actions),
        ("current-external-materialize", tuple(action for action in external_actions if action.path in current_paths)),
        (
            "obsolete-prune",
            tuple(
                action
                for action in external_actions
                if action.path not in current_paths
                and action.path not in required_directory_paths
                and action.action != "ensure-directory"
            ),
        ),
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
                if before_mutation is not None:
                    before_mutation()
                if allow_stale_stage_cleanup:

                    def validate_stale_cleanup(
                        parent_chain: tuple[int, ...],
                        path: str = action.path,
                    ) -> None:
                        if before_mutation is not None:
                            before_mutation()
                        if held_parent_validator is not None:
                            held_parent_validator(path, parent_chain)

                    _cleanup_stale_distribution_stages(
                        plan,
                        target_root,
                        action,
                        snapshot,
                        stage_ownership,
                        mutation_validator=validate_stale_cleanup,
                        stage_ownership_recorder=stage_ownership_recorder,
                        stage_ownership_remover=stage_ownership_remover,
                    )
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
                    if before_mutation is not None:
                        before_mutation()
                    if stage_ownership_recorder is None and created_parent_recorder is None:
                        if before_mutation is None:
                            _apply_distribution_action(
                                plan,
                                target_root,
                                action,
                                snapshot,
                                created_parent_bindings_by_path,
                            )
                        else:
                            _apply_distribution_action(
                                plan,
                                target_root,
                                action,
                                snapshot,
                                created_parent_bindings_by_path,
                                before_mutation=before_mutation,
                                held_parent_validator=held_parent_validator,
                                first_target_mutation_validator=first_target_mutation_validator,
                            )
                    elif stage_ownership_recorder is None:
                        if before_mutation is None:
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
                                created_parent_recorder=created_parent_recorder,
                                before_mutation=before_mutation,
                                held_parent_validator=held_parent_validator,
                                first_target_mutation_validator=first_target_mutation_validator,
                            )
                    elif before_mutation is None:
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
                            before_mutation,
                            held_parent_validator,
                            first_target_mutation_validator,
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
    "DistributionDirectoryRequirement",
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
    "JournaledDistributionIntent",
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
    "execute_fresh_distribution",
    "execute_recognized_distribution",
]

"""Distribution catalog, identity validation, and safe distribution plans.

The module owns the provider physical catalog and the shared S20/S25/S30
distribution boundary.  Plan construction remains read-only; the S30 apply
seam mutates only a validated target through descriptor-relative, no-follow
operations and fails closed when an identity changes.
"""

from __future__ import annotations

from contextlib import suppress
import ctypes
from dataclasses import dataclass
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import TYPE_CHECKING, Any, Literal, NoReturn

if TYPE_CHECKING:
    from collections.abc import Callable


class DistributionManifestError(ValueError):
    """Raised when the provider-private distribution manifest is unsafe."""


class DistributionApplyError(RuntimeError):
    """Raised when a distribution plan cannot be applied safely."""


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
class DistributionAsset:
    """One file in the physical Current provider catalog."""

    path: str
    identity: DistributionIdentity
    source_path: str | None = None


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
    purpose: Literal["distribution-rerun"]
    stage_ownership: tuple[DistributionStageOwnership, ...] = ()


@dataclass(frozen=True)
class DistributionAdmission:
    """Read-only result of operation admission."""

    operation: DistributionOperation
    status: Literal["fresh", "existing", "recognized", "retry", "uninstall-retry"]
    package_version: str
    target_version: str | None = None
    marker: DistributionRetryMarker | None = None

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
_DISTRIBUTION_RETRY_SCHEMA_VERSION = 1
_DISTRIBUTION_RETRY_PURPOSE: Literal["distribution-rerun"] = "distribution-rerun"
_DISTRIBUTION_RETRY_PHASES = frozenset({
    "preflight-complete",
    "distribution-applied",
    "scaffold-refreshed",
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


def _read_no_follow_regular(path: Path, *, label: str, allow_missing: bool = False) -> bytes | None:
    """Read one link-count-one regular file without following a symlink."""

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
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            _admission_block("invalid-file", f"{label} must be a regular file")
        if info.st_nlink != 1:
            _admission_block("hard-link", f"{label} must have link count 1")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    except OSError:
        _admission_block("read-error", f"{label} cannot be read safely")
    finally:
        os.close(fd)


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
    if initiatives.name != "initiatives" or initiatives.is_symlink() or not initiatives.is_dir(follow_symlinks=False):
        return False
    pending = [initiatives.path]
    while pending:
        current = pending.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            _admission_block("workspace-invalid", "preserved spec history cannot be inspected safely")
        for entry in entries:
            if entry.is_symlink():
                return False
            if entry.is_dir(follow_symlinks=False):
                pending.append(entry.path)
                continue
            if not entry.is_file(follow_symlinks=False):
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
    raw_bytes = _read_no_follow_regular(path, label="distribution retry marker")
    assert raw_bytes is not None
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _admission_block("marker-invalid", "distribution retry marker is not valid UTF-8 JSON")
    if not isinstance(raw, dict):
        _admission_block("marker-invalid", "distribution retry marker must be an object")
    expected_fields = {
        "schema_version",
        "operation",
        "package_version",
        "target_root",
        "last_completed_phase",
        "purpose",
    }
    raw_fields = set(raw)
    if raw_fields != expected_fields and raw_fields != expected_fields | {"stage_ownership"}:
        _admission_block("marker-invalid", "distribution retry marker fields are invalid")
    if raw.get("schema_version") != _DISTRIBUTION_RETRY_SCHEMA_VERSION:
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
    if raw.get("purpose") != _DISTRIBUTION_RETRY_PURPOSE:
        _admission_block("marker-invalid", "distribution retry marker purpose is unsupported")
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
        purpose=_DISTRIBUTION_RETRY_PURPOSE,
        stage_ownership=tuple(stage_ownership),
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
) -> tuple[str, tuple[int, int, int]]:
    version_path = target_root / "spec-dock" / "spec-dock.version"
    raw_bytes = _read_no_follow_regular(version_path, label="spec-dock/spec-dock.version", allow_missing=True)
    if raw_bytes is None:
        _admission_block("missing-version", "spec-dock/spec-dock.version is missing")
    try:
        version_text = raw_bytes.decode("ascii")
    except UnicodeDecodeError:
        _admission_block("invalid-version", "spec-dock/spec-dock.version must be ASCII")
    target_tuple = _parse_canonical_version(version_text, source="spec-dock/spec-dock.version")
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
    return version_text[:-1], target_tuple


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

    distribution_marker_present = _path_present_no_follow(target_root / _DISTRIBUTION_RETRY_MARKER_REL)
    uninstall_marker_present = _path_present_no_follow(target_root / _UNINSTALL_RETRY_MARKER_REL)
    if distribution_marker_present and uninstall_marker_present:
        _admission_block("dual-marker", "distribution and uninstall retry markers cannot coexist")

    distribution_marker = _read_distribution_retry_marker(target_root)
    uninstall_marker = _read_uninstall_retry_marker_for_admission(target_root)
    if distribution_marker is not None:
        if operation == "uninstall":
            _admission_block("distribution-retry-present", "recover distribution before uninstall")
        if distribution_marker.operation != operation:
            _admission_block("marker-operation-mismatch", "retry marker belongs to another operation")
        if distribution_marker.package_version != package_version:
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
    target_version, _target_tuple = _validate_workspace_version(
        target_root,
        manifest=manifest,
        package_version=package_version,
    )
    return DistributionAdmission(
        operation=operation,
        status="recognized",
        package_version=package_version,
        target_version=target_version,
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
            file_stat = candidate.stat()
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except OSError as exc:
            raise DistributionManifestError(f"unable to read Current asset: {relative.as_posix()}") from exc
        assets.append(
            DistributionAsset(
                path=relative.as_posix(),
                identity=DistributionIdentity(
                    kind="regular",
                    sha256=digest,
                    mode=stat.S_IMODE(file_stat.st_mode),
                ),
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
        return ()
    if not (scaffold_root / ".gitignore").is_file() or (scaffold_root / ".gitignore").is_symlink():
        return ()
    source_entries: list[tuple[str, Path]] = [(".gitignore", scaffold_root / ".gitignore")]
    for root_name in _SCAFFOLD_MANAGED_ROOTS:
        source_root = scaffold_root / root_name
        if not source_root.is_dir() or source_root.is_symlink():
            return ()
        for candidate in sorted(source_root.rglob("*"), key=lambda item: item.relative_to(scaffold_root).as_posix()):
            relative = candidate.relative_to(scaffold_root)
            if "__pycache__" in relative.parts or relative.suffix in {".pyc", ".pyo"}:
                continue
            if is_pruned_by_scaffold_refresh(relative):
                continue
            if candidate.is_file() and not candidate.is_symlink():
                source_entries.append((relative.as_posix(), candidate))
    seed_readme = scaffold_root / "templates" / "root" / ".workbench" / "README.md"
    if operation == "fresh" and seed_readme.is_file() and not seed_readme.is_symlink():
        source_entries.append((".workbench/README.md", seed_readme))

    assets: list[DistributionAsset] = []
    for source_path, candidate in sorted(source_entries):
        try:
            info = candidate.stat()
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except OSError as exc:
            raise DistributionManifestError(f"unable to read scaffold asset: {source_path}") from exc
        mode = stat.S_IMODE(info.st_mode)
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
                link_target = _normalized_link_target(str(os.readlink(exact_name, dir_fd=parent_fd)))
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
    if actual.kind != expected.kind:
        return _blocked_action(path, operation, "exact-path-symlink" if actual.kind == "symlink" else "exact-path-type")
    if actual.kind == "symlink" and actual.target != expected.target:
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
        if operation == "fresh":
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
        and operation == "uninstall"
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
                    created_missing = True
                next_fd = os.open(component, flags, dir_fd=fds[-1])
            except OSError as exc:
                raise DistributionApplyError(f"managed target parent is unsafe for '{target_rel}'") from exc
            fds.append(next_fd)
            _assert_visible_distribution_chain_bound(target_root, target_rel, tuple(fds))
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


def _source_asset_bytes(source_path: Path) -> tuple[bytes, int]:
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
        actual = os.fstat(fd)
        if not stat.S_ISREG(actual.st_mode):
            raise DistributionApplyError("provider Current asset changed type")
        return _read_fd_bytes(fd), stat.S_IMODE(actual.st_mode)
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
    except FileNotFoundError:
        return
    except OSError as exc:
        if strict:
            raise DistributionApplyError("managed staging cleanup failed") from exc


def _distribution_stage_identity(parent_fd: int, stage_name: str) -> DistributionIdentity | None:
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
        normalized = _normalized_link_target(target)
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


def _distribution_stage_name(path: str, identity: DistributionIdentity) -> str:
    """Return the stable private stage name owned by one planned target."""
    if identity.kind == "regular":
        identity_key = f"regular:{identity.sha256}"
        prefix = ".spec-dock-file-"
    else:
        identity_key = f"symlink:{identity.target}"
        prefix = ".spec-dock-symlink-"
    digest = hashlib.sha256(f"{path}\0{identity_key}".encode()).hexdigest()[:24]
    return f"{prefix}{digest}"


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
                owned.stage_name == _distribution_stage_name(action.path, identity) for identity in known_identities
            ):
                continue
            try:
                current = os.stat(owned.stage_name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise DistributionApplyError("managed staging artifact cannot be inspected safely") from exc
            if (
                current.st_dev != owned.device
                or current.st_ino != owned.inode
                or current.st_ctime_ns != owned.ctime_ns
                or _file_type(current.st_mode) != owned.file_type
                or current.st_nlink != 1
            ):
                mismatch_detected = True
                continue
            candidate = _distribution_stage_identity(parent_fd, owned.stage_name)
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
            if bound_parent is None:
                # A parent that was absent during preflight may only become
                # acceptable after this operation creates and binds it through
                # `_bind_created_parent_identities`.  Accepting an unbound
                # inode here would turn a user- or concurrently-created
                # directory into an operation-owned parent after preflight.
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
            if not _same_structure_identity(actual_parent, bound_parent):
                raise DistributionApplyError(f"managed target identity changed for '{path}'")
    if actual.target != expected.target:
        raise DistributionApplyError(f"managed target identity changed for '{path}'")


def _bind_created_parent_identities(
    target_rel: str,
    snapshot: DistributionTargetSnapshot,
    parent_chain: tuple[int, ...],
    created_parent_bindings: dict[str, PathIdentitySnapshot],
) -> None:
    for index, expected_parent in enumerate(snapshot.parents, start=1):
        if expected_parent.exists or index >= len(parent_chain):
            continue
        current = _snapshot_from_stat(
            expected_parent.relative_path,
            os.fstat(parent_chain[index]),
        )
        bound_parent = created_parent_bindings.get(expected_parent.relative_path)
        if bound_parent is None:
            created_parent_bindings[expected_parent.relative_path] = current
        elif not _same_structure_identity(current, bound_parent):
            raise DistributionApplyError(f"managed target identity changed for '{target_rel}'")


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
) -> None:
    path = action.path
    if action.action == "prune" and not snapshot.target.exists:
        return
    parent_chain = _open_distribution_parent_chain(
        target_root,
        path,
        create_missing=action.action == "create",
        expected_snapshot=snapshot,
    )
    try:
        _assert_distribution_chain_bound(parent_chain, snapshot, path)
        _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
        _bind_created_parent_identities(path, snapshot, parent_chain, created_parent_bindings)
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
            staging_name = _distribution_stage_name(path, expected)
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
                if stage_ownership_recorder is not None:
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
                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                _rename_distribution_no_replace(parent_fd, staging_name, parent_fd, target_name)
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
                    if stage_ownership_recorder is not None:
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
                os.unlink(target_name, dir_fd=parent_fd)
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
            staging_name = _distribution_stage_name(path, expected)
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
                if stage_ownership_recorder is not None:
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

                _assert_visible_distribution_chain_bound(target_root, path, parent_chain)
                _assert_regular_fd_safe(fd, snapshot.target, path, exact=True)
                if hashlib.sha256(_read_fd_bytes(fd)).hexdigest() != target_identity.sha256:
                    raise DistributionApplyError(f"managed target identity changed for '{path}'")
                _rename_distribution_swap(parent_fd, staging_name, parent_fd, target_name)
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
                    with suppress(OSError):
                        stage_identity = os.fstat(staging_fd)
                    try:
                        if stage_ownership_recorder is not None:
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
                                # The swap rebinds the stage pathname to the
                                # former target.  Persist that new identity
                                # before cleanup so a failed unlink can be
                                # recovered by the next retry.  If marker
                                # publication itself fails, remove the old
                                # target immediately so the stale pre-swap
                                # marker cannot hide a managed payload.
                                try:
                                    stage_ownership_recorder(
                                        _distribution_stage_ownership(path, staging_name, old_stat)
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
                                            _distribution_stage_ownership(path, staging_name, old_stat)
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
    )
    try:
        _assert_distribution_chain_bound(parent_chain, snapshot, action.path)
        _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
        _bind_created_parent_identities(action.path, snapshot, parent_chain, created_parent_bindings)
        parent_fd = parent_chain[-1]
        target_name = PurePosixPath(action.path).name
        try:
            current_target = os.readlink(target_name, dir_fd=parent_fd)
            target_exists = True
        except FileNotFoundError:
            current_target = None
            target_exists = False
        except OSError as exc:
            raise DistributionApplyError(f"managed target is unsafe for '{action.path}'") from exc

        if action.action == "create":
            if target_exists:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            _resolve_distribution_no_replace_rename()
            staging_name = _distribution_stage_name(action.path, expected)
            os.symlink(expected_target, staging_name, dir_fd=parent_fd)
            staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            published = False
            try:
                staged_target = _normalized_link_target(os.readlink(staging_name, dir_fd=parent_fd))
                if staged_target != expected_target or staging_stat.st_nlink != 1:
                    raise DistributionApplyError(f"managed target staging failed for '{action.path}'")
                if stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(action.path, staging_name, staging_stat))
                _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
                _rename_distribution_no_replace(parent_fd, staging_name, parent_fd, target_name)
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
            created_target = _normalized_link_target(os.readlink(target_name, dir_fd=parent_fd))
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
            latest_target = _normalized_link_target(os.readlink(target_name, dir_fd=parent_fd))
            if latest_target != snapshot.target.identity.target:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            os.unlink(target_name, dir_fd=parent_fd)
            return
        if action.action == "upgrade":
            if not target_exists or snapshot.target.identity is None:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            if current_target != snapshot.target.identity.target:
                raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
            _resolve_distribution_swap_rename()
            staging_name = _distribution_stage_name(action.path, expected)
            os.symlink(expected_target, staging_name, dir_fd=parent_fd)
            staging_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
            swapped = False
            try:
                staged_target = _normalized_link_target(os.readlink(staging_name, dir_fd=parent_fd))
                if staged_target != expected_target:
                    raise DistributionApplyError(f"managed target staging failed for '{action.path}'")
                if stage_ownership_recorder is not None:
                    stage_ownership_recorder(_distribution_stage_ownership(action.path, staging_name, staging_stat))
                latest_stat = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
                if not _same_stat_identity(latest_stat, snapshot.target) or latest_stat.st_nlink != 1:
                    raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                latest_target = _normalized_link_target(os.readlink(target_name, dir_fd=parent_fd))
                if latest_target != snapshot.target.identity.target:
                    raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
                _assert_visible_distribution_chain_bound(target_root, action.path, parent_chain)
                _rename_distribution_swap(parent_fd, staging_name, parent_fd, target_name)
                swapped = True
                published_target = _normalized_link_target(os.readlink(target_name, dir_fd=parent_fd))
                if published_target != expected_target:
                    raise DistributionApplyError(f"managed target verification failed for '{action.path}'")
            finally:
                if not swapped:
                    # Match regular-file staging semantics: retry the
                    # ownership record after a pre-swap failure, then clean
                    # only the refreshed no-follow identity strictly.
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
                else:
                    try:
                        old_target = _normalized_link_target(os.readlink(staging_name, dir_fd=parent_fd))
                        old_stat = os.stat(staging_name, dir_fd=parent_fd, follow_symlinks=False)
                        if (
                            snapshot.target.identity is not None
                            and old_target == snapshot.target.identity.target
                            and _same_stat_structure(old_stat, snapshot.target)
                            and old_stat.st_nlink == 1
                        ):
                            if stage_ownership_recorder is not None:
                                # After the atomic swap, the stage pathname
                                # owns the former target.  Record that inode
                                # before unlink so a failed cleanup remains
                                # safely retryable.
                                try:
                                    stage_ownership_recorder(
                                        _distribution_stage_ownership(action.path, staging_name, old_stat)
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
                                            _distribution_stage_ownership(action.path, staging_name, old_stat)
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
            source_root = plan.scaffold_root if asset.source_path is not None else plan.install_root
            if source_root is None:
                raise DistributionApplyError("distribution plan has no provider source root")
            source_rel = asset.source_path or asset.path
            source_bytes, observed_source_mode = _source_asset_bytes(source_root / source_rel)
            if expected.mode is None or observed_source_mode != expected.mode:
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
    )


def apply_distribution_plan(
    plan: DistributionPlan,
    *,
    allow_stale_stage_cleanup: bool = False,
    allow_blocked_scaffold_paths: bool = False,
    stage_ownership: tuple[DistributionStageOwnership, ...] = (),
    stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    scaffold_applier: Callable[[], None] | None = None,
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
    created_parent_bindings: dict[str, PathIdentitySnapshot] = {}
    scaffold_paths = plan.scaffold_paths if scaffold_applier is not None else frozenset()
    for action in plan.actions:
        snapshot = snapshots.get(action.path)
        if snapshot is None:
            raise DistributionApplyError("distribution plan is missing a target identity snapshot")
        _assert_plan_target_snapshot(target_root, action.path, snapshot)

    actions_to_apply = tuple(action for action in plan.actions if action.path not in scaffold_paths)
    for index, action in enumerate(actions_to_apply):
        snapshot = snapshots[action.path]
        _assert_plan_target_snapshot(target_root, action.path, snapshot)
        if allow_stale_stage_cleanup:
            _cleanup_stale_distribution_stages(plan, target_root, action, snapshot, stage_ownership)
        # Removing a known stale stage mutates the parent directory ctime.  The
        # target itself must remain unchanged, but every later action needs the
        # refreshed parent snapshot before it can be applied or adopted.
        refreshed = _observe_target(target_root, action.path)
        if refreshed.snapshot is None:
            raise DistributionApplyError(f"managed target identity changed for '{action.path}'")
        _assert_pending_snapshot_stable(refreshed.snapshot, snapshot, action.path, created_parent_bindings)
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
                created_parent_bindings,
            )
            snapshots[pending.path] = pending_observation.snapshot
        if action.action in {"adopt", "preserve"}:
            continue
        if stage_ownership_recorder is None:
            _apply_distribution_action(plan, target_root, action, snapshot, created_parent_bindings)
        else:
            _apply_distribution_action(
                plan,
                target_root,
                action,
                snapshot,
                created_parent_bindings,
                stage_ownership_recorder,
            )
        for pending in actions_to_apply[index + 1 :]:
            pending_snapshot = snapshots[pending.path]
            pending_observation = _observe_target(target_root, pending.path)
            if pending_observation.snapshot is None:
                raise DistributionApplyError(f"managed target identity changed for '{pending.path}'")
            _assert_pending_snapshot_stable(
                pending_observation.snapshot,
                pending_snapshot,
                pending.path,
                created_parent_bindings,
            )
            snapshots[pending.path] = pending_observation.snapshot

    if scaffold_applier is not None and scaffold_paths:
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
    "DistributionProvenance",
    "DistributionResult",
    "DistributionStageOwnership",
    "DistributionTargetSnapshot",
    "PathIdentitySnapshot",
    "apply_distribution_plan",
    "build_distribution_plan",
]

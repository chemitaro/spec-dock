"""Distribution catalog, historical identity validation, and read-only plans.

The module owns the provider physical catalog and the shared S20/S25
classification boundary.  It never mutates a consumer tree.  Later Issue 360
steps may consume the returned plan, but apply, prune, and CLI orchestration
remain outside this module for now.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Literal


class DistributionManifestError(ValueError):
    """Raised when the provider-private distribution manifest is unsafe."""


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
class DistributionPlan:
    """Read-only S20/S25 plan surface for later apply steps."""

    current_assets: tuple[DistributionAsset, ...]
    actions: tuple[DistributionAction, ...]
    manifest: DistributionManifest
    scaffold_root: Path | None = None

    @property
    def blocked(self) -> bool:
        """Whether any classified action requires preserve-and-block."""

        return any(action.blocked for action in self.actions)


_SCHEMA_VERSION = 1
_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "recognized_workspace_versions",
        "historical_current_identities",
        "trusted_consumer_manifests",
        "obsolete_exact_files",
        "historical_shortcuts",
    }
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_GLOB_CHARS = frozenset("*?[]{}")


def _fail(message: str) -> None:
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
    allowed = {"path", "kind", "sha256", "target", "source"}
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
        if not isinstance(version, str) or not version.strip():
            _fail(f"recognized_workspace_versions[{index}].version must be non-empty")
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
        obsolete.append(
            {
                "path": path.as_posix(),
                "surface": surface,
                "identities": identities,
                "on_unknown": "preserve-and-block",
            }
        )

    shortcuts: list[dict[str, Any]] = []
    for index, item in enumerate(_section_list(raw, "historical_shortcuts")):
        if not isinstance(item, dict) or set(item) != {"path", "kind", "target", "source"}:
            _fail(f"historical_shortcuts[{index}] has invalid shape")
        if item.get("kind") != "symlink":
            _fail(f"historical_shortcuts[{index}].kind must be symlink")
        path = _exact_relative_path(item.get("path"), field_name=f"historical_shortcuts[{index}].path")
        target = _exact_relative_path(item.get("target"), field_name=f"historical_shortcuts[{index}].target")
        shortcuts.append(
            {
                "path": path.as_posix(),
                "kind": "symlink",
                "target": target.as_posix(),
                "source": _source(item.get("source"), field_name=f"historical_shortcuts[{index}].source"),
            }
        )

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
) -> None:
    seen_historical: set[tuple[str, str, str | None, str | None]] = set()
    for item in manifest.historical_current_identities:
        signature = (item["path"], item["kind"], item.get("sha256"), item.get("target"))
        if signature in seen_historical:
            _fail(f"duplicate historical identity: {item['path']}")
        seen_historical.add(signature)

    records: list[tuple[str, str, bool]] = []
    for version_index, version in enumerate(manifest.recognized_workspace_versions):
        for anchor_index, anchor in enumerate(version["anchors"]):
            records.append(
                (
                    anchor["path"],
                    f"recognized_workspace_versions[{version_index}].anchors[{anchor_index}]",
                    False,
                )
            )
    for item in manifest.historical_current_identities:
        # A historical identity is intentionally allowed to describe the same
        # target path as a newly shipped Current asset.  It is the evidence
        # used to classify an existing consumer file for upgrade/prune.
        records.append((item["path"], "historical_current_identities", True))
    for item in manifest.obsolete_exact_files:
        records.append((item["path"], "obsolete_exact_files", False))
    for manifest_index, item in enumerate(manifest.trusted_consumer_manifests):
        records.append((item["path"], f"trusted_consumer_manifests[{manifest_index}]", False))
        for claim_index, claim in enumerate(item["claims"]):
            records.append(
                (
                    claim["path"],
                    f"trusted_consumer_manifests[{manifest_index}].claims[{claim_index}]",
                    True,
                )
            )
    for item in manifest.historical_shortcuts:
        # The canonical shortcut is a Current identity even though it is
        # synthesized rather than shipped as a regular file.  Historical
        # shortcut records may therefore share that exact path as evidence;
        # ancestor/descendant overlap remains invalid.
        records.append((item["path"], "historical_shortcuts", True))

    for index, (path, section, allows_current_overlap) in enumerate(records):
        if allows_current_overlap:
            current_overlap = any(
                _path_overlaps(path, current_path) and path != current_path
                for current_path in current_paths
            )
        else:
            current_overlap = any(_path_overlaps(path, current_path) for current_path in current_paths)
        if current_overlap:
            _fail(f"manifest path overlaps physical Current catalog: {path}")
        for other_path, other_section, _ in records[:index]:
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


def _current_assets(install_root: Path) -> tuple[DistributionAsset, ...]:
    if not install_root.is_dir() or install_root.is_symlink():
        raise DistributionManifestError("physical install-root must be a directory")
    assets: list[DistributionAsset] = []
    for candidate in sorted(install_root.rglob("*"), key=lambda item: item.relative_to(install_root).as_posix()):
        if not candidate.is_file() or candidate.is_symlink():
            continue
        relative = _exact_relative_path(candidate.relative_to(install_root).as_posix(), field_name="Current path")
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


_OPERATIONS = frozenset({"fresh", "update", "init-force", "uninstall"})
_CURRENT_SHORTCUTS = {
    "spec": DistributionIdentity(kind="symlink", target="spec-dock/scripts/spec-dock"),
}


@dataclass(frozen=True)
class _TargetObservation:
    state: str
    identity: DistributionIdentity | None = None
    link_count: int | None = None


def _identity_matches(actual: DistributionIdentity, record: dict[str, Any]) -> bool:
    if actual.kind != record.get("kind"):
        return False
    if actual.kind == "regular":
        return actual.sha256 == record.get("sha256")
    return actual.target == record.get("target")


def _normalized_link_target(value: str) -> str | None:
    if not value or "\\" in value or value.startswith("/") or _DRIVE_RE.match(value):
        return None
    try:
        return _exact_relative_path(value, field_name="target link").as_posix()
    except DistributionManifestError:
        return None


def _observe_target(target_root: Path, relative_path: str) -> _TargetObservation:
    """Inspect one target path without following a symlink component."""

    current = target_root
    try:
        root_stat = os.lstat(current)
    except FileNotFoundError:
        return _TargetObservation("missing")
    except OSError:
        return _TargetObservation("root-error")
    if stat.S_ISLNK(root_stat.st_mode):
        return _TargetObservation("root-symlink")
    if not stat.S_ISDIR(root_stat.st_mode):
        return _TargetObservation("root-non-directory")

    parts = PurePosixPath(relative_path).parts
    for component in parts[:-1]:
        current = current / component
        try:
            component_stat = os.lstat(current)
        except FileNotFoundError:
            return _TargetObservation("missing")
        except OSError:
            return _TargetObservation("parent-error")
        if stat.S_ISLNK(component_stat.st_mode):
            return _TargetObservation("symlink-container")
        if not stat.S_ISDIR(component_stat.st_mode):
            return _TargetObservation("non-directory-container")

    exact = current / parts[-1]
    try:
        exact_stat = os.lstat(exact)
    except FileNotFoundError:
        return _TargetObservation("missing")
    except OSError:
        return _TargetObservation("target-error")

    if stat.S_ISLNK(exact_stat.st_mode):
        try:
            link_target = _normalized_link_target(os.readlink(exact))
        except OSError:
            link_target = None
        return _TargetObservation(
            "symlink",
            DistributionIdentity(kind="symlink", target=link_target),
            exact_stat.st_nlink,
        )
    if stat.S_ISREG(exact_stat.st_mode):
        try:
            digest = hashlib.sha256(exact.read_bytes()).hexdigest()
        except OSError:
            return _TargetObservation("target-error")
        return _TargetObservation(
            "regular",
            DistributionIdentity(
                kind="regular",
                sha256=digest,
                mode=stat.S_IMODE(exact_stat.st_mode),
            ),
            exact_stat.st_nlink,
        )
    if stat.S_ISDIR(exact_stat.st_mode):
        return _TargetObservation("directory", link_count=exact_stat.st_nlink)
    return _TargetObservation("special", link_count=exact_stat.st_nlink)


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
        if manifest_identity is None or not _identity_matches(manifest_identity, trusted):
            continue
        for claim in trusted["claims"]:
            if claim["path"] == path and _identity_matches(actual, claim):
                return True
    return False


def _historical_provenance(
    target_root: Path,
    path: str,
    actual: DistributionIdentity,
    manifest: DistributionManifest,
) -> str | None:
    for record in _historical_records(manifest):
        if record["path"] == path and _identity_matches(actual, record):
            return "direct"
    if _trusted_manifest_matches(target_root, path, actual, manifest):
        return "trusted-manifest"
    return None


def _target_identity_specs(
    current_assets: tuple[DistributionAsset, ...],
) -> dict[str, DistributionIdentity]:
    # Historical shortcut records are evidence only.  They must never create
    # a new Fresh target; the shipped canonical shortcut is the sole Current
    # shortcut and is represented by the synthetic rule above.
    return {
        **_CURRENT_SHORTCUTS,
        **{asset.path: asset.identity for asset in current_assets},
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
) -> DistributionAction:
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
    if observation.state in {"root-symlink", "root-non-directory", "root-error", "parent-error", "target-error", "special"}:
        return _blocked_action(path, operation, "unsafe-target-path")

    actual = observation.identity
    if actual is None:
        return _blocked_action(path, operation, "unsafe-target-path")
    if actual.kind != expected.kind:
        return _blocked_action(path, operation, "exact-path-symlink" if actual.kind == "symlink" else "exact-path-type")
    if actual.kind == "symlink" and actual.target != expected.target:
        provenance = _historical_provenance(target_root, path, actual, manifest)
        if provenance is not None and operation in {"update", "init-force"}:
            return DistributionAction(path, operation, "upgrade", "historical", "direct-historical-identity-match")
        if provenance is not None and operation == "uninstall":
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
            reason = "trusted-manifest-identity-match" if provenance == "trusted-manifest" else "direct-historical-identity-match"
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
) -> DistributionAction | None:
    path = item["path"]
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
    direct = any(_identity_matches(actual, identity) for identity in item["identities"])
    trusted = _trusted_manifest_matches(target_root, path, actual, manifest)
    if not direct and not trusted:
        return _blocked_action(path, operation, "obsolete-identity-unknown", action="preserve")
    if actual.kind == "regular" and observation.link_count is not None and observation.link_count > 1:
        return _blocked_action(path, operation, "hard-link-mutation-unsafe", provenance="historical")
    reason = "trusted-manifest-identity-match" if trusted and not direct else "direct-obsolete-identity-match"
    return DistributionAction(path, operation, "prune", "historical", reason)


def _classify_target(
    *,
    target_root: Path,
    current_assets: tuple[DistributionAsset, ...],
    operation: DistributionOperation,
    manifest: DistributionManifest,
) -> tuple[DistributionAction, ...]:
    specs = _target_identity_specs(current_assets)
    actions = [
        _classify_current_target(
            target_root=target_root,
            path=path,
            expected=expected,
            operation=operation,
            manifest=manifest,
        )
        for path, expected in sorted(specs.items())
    ]
    if operation in {"update", "init-force", "uninstall"}:
        current_paths = set(specs)
        for item in manifest.obsolete_exact_files:
            if item["path"] in current_paths:
                continue
            action = _classify_obsolete_target(
                target_root=target_root,
                item=item,
                operation=operation,
                manifest=manifest,
            )
            if action is not None:
                actions.append(action)
    return tuple(actions)


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
    manifest = _load_manifest(manifest_path)
    _assert_no_manifest_overlap(
        {asset.path for asset in current_assets} | set(_CURRENT_SHORTCUTS),
        manifest,
    )
    actions: tuple[DistributionAction, ...] = ()
    if target_root is not None:
        actions = _classify_target(
            target_root=Path(target_root),
            current_assets=current_assets,
            operation=operation,
            manifest=manifest,
        )
    return DistributionPlan(
        current_assets=current_assets,
        actions=actions,
        manifest=manifest,
        scaffold_root=Path(scaffold_root) if scaffold_root is not None else None,
    )


__all__ = [
    "DistributionAsset",
    "DistributionAction",
    "DistributionActionName",
    "DistributionIdentity",
    "DistributionManifest",
    "DistributionManifestError",
    "DistributionOperation",
    "DistributionPlan",
    "DistributionProvenance",
    "build_distribution_plan",
]

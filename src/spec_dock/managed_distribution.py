"""Read-only distribution catalog and historical manifest validation.

This module is intentionally limited to the S20 boundary.  It derives the
Current catalog from the provider's physical install-root and validates the
provider-private historical manifest.  Consumer classification and any
filesystem mutation belong to later Issue 360 steps.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any


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
    """Read-only S20 plan surface for later classifier/apply steps."""

    current_assets: tuple[DistributionAsset, ...]
    actions: tuple[Any, ...]
    manifest: DistributionManifest
    scaffold_root: Path | None = None


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
    records: list[tuple[str, str]] = []
    for version_index, version in enumerate(manifest.recognized_workspace_versions):
        for anchor_index, anchor in enumerate(version["anchors"]):
            records.append(
                (
                    anchor["path"],
                    f"recognized_workspace_versions[{version_index}].anchors[{anchor_index}]",
                )
            )
    for item in manifest.historical_current_identities:
        records.append((item["path"], "historical_current_identities"))
    for item in manifest.obsolete_exact_files:
        records.append((item["path"], "obsolete_exact_files"))
    for manifest_index, item in enumerate(manifest.trusted_consumer_manifests):
        records.append((item["path"], f"trusted_consumer_manifests[{manifest_index}]"))
        for claim_index, claim in enumerate(item["claims"]):
            records.append(
                (
                    claim["path"],
                    f"trusted_consumer_manifests[{manifest_index}].claims[{claim_index}]",
                )
            )
    for item in manifest.historical_shortcuts:
        records.append((item["path"], "historical_shortcuts"))

    for index, (path, section) in enumerate(records):
        if any(_path_overlaps(path, current_path) for current_path in current_paths):
            _fail(f"manifest path overlaps physical Current catalog: {path}")
        for other_path, other_section in records[:index]:
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


def build_distribution_plan(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path | None = None,
) -> DistributionPlan:
    """Build a read-only Current/historical distribution plan.

    ``install_root`` is the provider physical source.  It is never modified;
    ``scaffold_root`` is retained only as context for later steps and is not
    scanned or rewritten here.
    """

    install_root = Path(install_root)
    manifest_path = Path(manifest_path)
    current_assets = _current_assets(install_root)
    manifest = _load_manifest(manifest_path)
    _assert_no_manifest_overlap({asset.path for asset in current_assets}, manifest)
    return DistributionPlan(
        current_assets=current_assets,
        actions=(),
        manifest=manifest,
        scaffold_root=Path(scaffold_root) if scaffold_root is not None else None,
    )


__all__ = [
    "DistributionAsset",
    "DistributionIdentity",
    "DistributionManifest",
    "DistributionManifestError",
    "DistributionPlan",
    "build_distribution_plan",
]

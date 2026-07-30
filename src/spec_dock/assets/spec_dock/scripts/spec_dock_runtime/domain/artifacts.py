from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

DIRECT_ARTIFACT_TYPES = (
    "blank",
    "research",
    "interview",
    "disc",
    "decision-candidate",
    "pr-repair-batch",
    "adr",
)
ROUTING_ONLY_ARTIFACT_TYPES = ("draft-requirement", "draft-design", "draft-plan")
SUPPORTED_ARTIFACT_TYPES = (*DIRECT_ARTIFACT_TYPES, *ROUTING_ONLY_ARTIFACT_TYPES)
UNSUPPORTED_ARTIFACT_TYPES = ("scratch", "note")

_ARTIFACT_TIMESTAMP_INTENT_RE = re.compile(r"^[0-9]{8}[tT][0-9].*$")
_ARTIFACT_DOC_TYPE_PATTERN = "|".join(
    re.escape(doc_type) for doc_type in sorted(SUPPORTED_ARTIFACT_TYPES, key=len, reverse=True)
)
_TYPED_ARTIFACT_FILENAME_RE = re.compile(
    r"^(?P<ts>[0-9]{8}t[0-9]{6}z)(?:-(?P<nn>0[1-9]|[1-9][0-9]))?"
    rf"-(?P<artifact_type>{_ARTIFACT_DOC_TYPE_PATTERN})-"
    r"(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
_BLANK_ARTIFACT_FILENAME_RE = re.compile(
    r"^(?P<ts>[0-9]{8}t[0-9]{6}z)(?:-(?P<nn>0[1-9]|[1-9][0-9]))?"
    r"-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
_GRANDFATHERED_LEGACY_ARTIFACT_FILENAME_RE = re.compile(r"^[0-9]{3}-(?:adr|disc|note)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


@dataclass(frozen=True)
class ArtifactFilename:
    timestamp: str
    suffix: int | None
    artifact_type: str
    slug: str
    artifact_id: str


@dataclass(frozen=True)
class GenericImportedArtifactFilename:
    timestamp: str
    suffix: int | None
    original_basename: str
    artifact_id: str


_GENERIC_IMPORTED_ARTIFACT_FILENAME_RE = re.compile(
    r"^(?P<ts>[0-9]{8}t[0-9]{6}z)(?:-(?P<nn>0[1-9]|[1-9][0-9]))?--(?P<basename>.+)$"
)


def normalize_generic_artifact_basename(name: str) -> str:
    if name in ("", ".", "..") or "\x00" in name or "/" in name or "\\" in name:
        raise RuntimeError("Invalid generic artifact basename")
    return name


def format_generic_imported_artifact_filename(
    *,
    timestamp: str,
    original_basename: str,
    suffix: int | None = None,
) -> str:
    normalized = normalize_generic_artifact_basename(original_basename)
    prefix = timestamp if suffix is None else f"{timestamp}-{suffix:02d}"
    filename = f"{prefix}--{normalized}"
    if parse_generic_imported_artifact_filename(filename) is None:
        raise RuntimeError("Invalid generic artifact identity")
    return filename


def parse_generic_imported_artifact_filename(name: str) -> GenericImportedArtifactFilename | None:
    if name == "rules.md":
        return None
    matched = _GENERIC_IMPORTED_ARTIFACT_FILENAME_RE.fullmatch(name)
    if matched is None:
        return None
    original_basename = str(matched.group("basename"))
    try:
        normalize_generic_artifact_basename(original_basename)
    except RuntimeError:
        return None
    timestamp = str(matched.group("ts"))
    suffix_raw = matched.group("nn")
    suffix = int(suffix_raw) if suffix_raw is not None else None
    return GenericImportedArtifactFilename(
        timestamp=timestamp,
        suffix=suffix,
        original_basename=original_basename,
        artifact_id=name,
    )


def is_supported_artifact_type(artifact_type: str) -> bool:
    return artifact_type in SUPPORTED_ARTIFACT_TYPES


def is_direct_artifact_type(artifact_type: str) -> bool:
    return artifact_type in DIRECT_ARTIFACT_TYPES


def is_routing_only_artifact_type(artifact_type: str) -> bool:
    return artifact_type in ROUTING_ONLY_ARTIFACT_TYPES


def is_ambiguous_blank_artifact_slug(slug: str) -> bool:
    return any(
        slug == artifact_type or slug.startswith(f"{artifact_type}-") for artifact_type in SUPPORTED_ARTIFACT_TYPES
    )


def is_grandfathered_legacy_artifact_filename(name: str) -> bool:
    return _GRANDFATHERED_LEGACY_ARTIFACT_FILENAME_RE.fullmatch(name) is not None


def parse_artifact_filename(name: str) -> ArtifactFilename | None:
    if name == "rules.md":
        return None
    matched = _TYPED_ARTIFACT_FILENAME_RE.fullmatch(name)
    if matched is not None:
        timestamp = str(matched.group("ts"))
        suffix_raw = matched.group("nn")
        suffix = int(suffix_raw) if suffix_raw is not None else None
        artifact_type = str(matched.group("artifact_type"))
        slug = str(matched.group("slug"))
        if artifact_type == "blank":
            return None
        artifact_id = f"{timestamp}-{artifact_type}" if suffix is None else f"{timestamp}-{suffix:02d}-{artifact_type}"
        return ArtifactFilename(
            timestamp=timestamp,
            suffix=suffix,
            artifact_type=artifact_type,
            slug=slug,
            artifact_id=artifact_id,
        )
    matched = _BLANK_ARTIFACT_FILENAME_RE.fullmatch(name)
    if matched is None:
        return None
    timestamp = str(matched.group("ts"))
    suffix_raw = matched.group("nn")
    suffix = int(suffix_raw) if suffix_raw is not None else None
    slug = str(matched.group("slug"))
    parts = slug.split("-")
    if re.fullmatch(r"[0-9]{2}", parts[0]) is not None:
        return None
    for end in range(len(parts), 0, -1):
        if "-".join(parts[:end]) in SUPPORTED_ARTIFACT_TYPES:
            return None
    artifact_id = timestamp if suffix is None else f"{timestamp}-{suffix:02d}"
    return ArtifactFilename(
        timestamp=timestamp,
        suffix=suffix,
        artifact_type="blank",
        slug=slug,
        artifact_id=artifact_id,
    )


def artifact_id_from_path(path: Path) -> str:
    parsed = parse_artifact_filename(path.name)
    if parsed is None:
        raise RuntimeError(f"Invalid artifact filename: {path.name}")
    return parsed.artifact_id


def is_malformed_artifact_candidate(path: Path) -> bool:
    if path.name == "rules.md":
        return False
    if path.suffix != ".md":
        return False
    if is_grandfathered_legacy_artifact_filename(path.name):
        return False
    if parse_generic_imported_artifact_filename(path.name) is not None:
        return False
    if parse_artifact_filename(path.name) is not None:
        return False
    stem = path.stem
    lowered = stem.lower()
    parts = lowered.split("-")
    if _ARTIFACT_TIMESTAMP_INTENT_RE.fullmatch(stem) is not None:
        return True
    for artifact_type in (*SUPPORTED_ARTIFACT_TYPES, *UNSUPPORTED_ARTIFACT_TYPES):
        if (
            lowered == artifact_type
            or lowered.startswith(f"{artifact_type}-")
            or lowered.startswith(f"{artifact_type}_")
        ):
            return True
        for start in (1, 2):
            if len(parts) <= start:
                continue
            for end in range(len(parts), start, -1):
                if "-".join(parts[start:end]) == artifact_type:
                    return True
    return False


def scan_artifact_duplicate_state(artifacts_dir: Path) -> tuple[str | None, set[str]]:
    refs: list[ArtifactFilename] = []
    if artifacts_dir.is_symlink():
        return f"Unsafe artifact directory under {artifacts_dir}: artifacts directory must not be a symlink", set()
    if os.path.lexists(artifacts_dir) and not artifacts_dir.is_dir():
        return f"Unsafe artifact directory under {artifacts_dir}: artifacts path is not a directory", set()
    if artifacts_dir.exists():
        for path in sorted(artifacts_dir.glob("*.md"), key=lambda p: p.as_posix()):
            if path.name == "rules.md":
                continue
            if path.is_symlink():
                return f"Unsafe artifact file under {artifacts_dir}: {path.name} is a symlink", set()
            if is_malformed_artifact_candidate(path):
                return f"Malformed artifact filename under {artifacts_dir}: {path.name}", set()
            parsed = parse_artifact_filename(path.name)
            if parsed is not None:
                refs.append(parsed)
    by_standard_slot: dict[str, list[str]] = {}
    by_suffix_slot: dict[tuple[str, int], list[str]] = {}
    artifact_ids: set[str] = set()
    for parsed in refs:
        if parsed.artifact_id in artifact_ids:
            return f"Duplicate artifact id detected under {artifacts_dir}: id={parsed.artifact_id}", artifact_ids
        artifact_ids.add(parsed.artifact_id)
        if parsed.suffix is None:
            by_standard_slot.setdefault(parsed.timestamp, []).append(parsed.artifact_id)
        else:
            by_suffix_slot.setdefault((parsed.timestamp, parsed.suffix), []).append(parsed.artifact_id)
    for timestamp, ids in sorted(by_standard_slot.items()):
        if len(ids) > 1:
            return f"Duplicate artifact timestamp slot detected under {artifacts_dir}: slot={timestamp}", artifact_ids
    for (timestamp, suffix), ids in sorted(by_suffix_slot.items()):
        if len(ids) > 1:
            return (
                f"Duplicate artifact timestamp suffix detected under {artifacts_dir}: slot={timestamp}-{suffix:02d}",
                artifact_ids,
            )
    return None, artifact_ids


def allocate_artifact_filename_for_timestamp(
    artifacts_dir: Path,
    *,
    timestamp: str,
    artifact_type: str,
    slug: str,
) -> tuple[Path, str]:
    refs: list[ArtifactFilename] = []
    if artifacts_dir.exists():
        for path in sorted(artifacts_dir.glob("*.md"), key=lambda p: p.as_posix()):
            parsed = parse_artifact_filename(path.name)
            if parsed is not None:
                refs.append(parsed)
    matching = [parsed for parsed in refs if parsed.timestamp == timestamp]
    if not matching:
        return _format_artifact_identity(
            artifacts_dir, timestamp=timestamp, suffix=None, artifact_type=artifact_type, slug=slug
        )
    used_suffixes = {parsed.suffix for parsed in matching if parsed.suffix is not None}
    for suffix in range(1, 100):
        if suffix not in used_suffixes:
            return _format_artifact_identity(
                artifacts_dir,
                timestamp=timestamp,
                suffix=suffix,
                artifact_type=artifact_type,
                slug=slug,
            )
    raise RuntimeError(
        "Artifact timestamp suffix exhaustion: "
        f"timestamp={timestamp} under {artifacts_dir}. "
        "Suffix allocation is limited to 01..99 within a single-second artifact family."
    )


def _format_artifact_identity(
    artifacts_dir: Path,
    *,
    timestamp: str,
    suffix: int | None,
    artifact_type: str,
    slug: str,
) -> tuple[Path, str]:
    if artifact_type == "blank":
        stem_prefix = timestamp if suffix is None else f"{timestamp}-{suffix:02d}"
    else:
        stem_prefix = f"{timestamp}-{artifact_type}" if suffix is None else f"{timestamp}-{suffix:02d}-{artifact_type}"
    return artifacts_dir / f"{stem_prefix}-{slug}.md", stem_prefix

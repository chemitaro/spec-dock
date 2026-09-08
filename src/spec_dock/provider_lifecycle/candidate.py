"""Fixed provider candidate inventory and canonical digesting."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import posixpath
import stat
from typing import TYPE_CHECKING

from spec_dock.provider_lifecycle.contracts import CandidateDomain, CandidateIdentity, SkillSlotMarker
from spec_dock.provider_lifecycle.filesystem import TreeEntry
from spec_dock.provider_lifecycle.wire import parse_slot_marker, serialize_slot_marker

if TYPE_CHECKING:
    from collections.abc import Sequence

CANDIDATE_VERSION = "0.2.4"
CANDIDATE_MAGIC = b"spec-dock-fixed-provider-candidate-v1\0"
SLOT_MARKER_NAME = ".spec-dock-provider-slot.json"
FIXED_DOMAINS = (
    ("root", "spec-dock/docs", "spec_dock/docs"),
    ("root", "spec-dock/templates", "spec_dock/templates"),
    ("root", "spec-dock/system", "spec_dock/system"),
    ("root", "spec-dock/scripts", "spec_dock/scripts"),
    ("slot", ".agents/skills/spec-dock", "install_root/.agents/skills/spec-dock"),
    (
        "slot",
        ".agents/skills/spec-dock-grill-with-docs",
        "install_root/.agents/skills/spec-dock-grill-with-docs",
    ),
)
_SLOT_NAMES = ("slot-spec-dock", "slot-spec-dock-grill-with-docs")


class CandidateError(ValueError):
    """The fixed candidate contains an unsupported or unsafe object."""


@dataclass(frozen=True, slots=True)
class _CapturedDomain:
    kind: str
    path: str
    source_path: str
    entries: tuple[TreeEntry, ...]
    tree_digest: str

    @property
    def identity(self) -> CandidateDomain:
        return CandidateDomain(self.kind, self.path, self.tree_digest, len(self.entries))


def _bytes_path(value: str, label: str) -> bytes:
    if "\x00" in value:
        raise CandidateError(f"{label} contains NUL")
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CandidateError(f"{label} is not UTF-8") from exc


def _safe_relative_symlink(target: str) -> None:
    if not target or target.startswith("/") or "\x00" in target or "\\" in target:
        raise CandidateError("symlink target must be a relative POSIX path")
    depth = 0
    for part in target.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            depth -= 1
            if depth < 0:
                raise CandidateError("symlink target lexically escapes its domain")
        else:
            depth += 1


def _regular_digest(path: str | os.PathLike[str], expected: os.stat_result) -> str:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(fd)
        if (
            opened.st_dev != expected.st_dev
            or opened.st_ino != expected.st_ino
            or opened.st_ctime_ns != expected.st_ctime_ns
            or opened.st_nlink != expected.st_nlink
            or stat.S_IMODE(opened.st_mode) != stat.S_IMODE(expected.st_mode)
        ):
            raise CandidateError("candidate file changed while opening")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        closed = os.fstat(fd)
        if (
            closed.st_dev != opened.st_dev
            or closed.st_ino != opened.st_ino
            or closed.st_ctime_ns != opened.st_ctime_ns
            or closed.st_size != opened.st_size
        ):
            raise CandidateError("candidate file changed while reading")
        return digest.hexdigest()
    finally:
        os.close(fd)


def _capture_entries(root: Path, *, exclude_marker: bool) -> tuple[TreeEntry, ...]:
    entries: list[TreeEntry] = []

    def visit(directory: Path, prefix: str) -> None:
        try:
            with os.scandir(directory) as iterator:
                children = sorted(iterator, key=lambda item: os.fsencode(item.name))
        except OSError as exc:
            raise CandidateError(f"cannot read candidate directory {directory}") from exc
        for child in children:
            relative = posixpath.join(prefix, child.name) if prefix else child.name
            if exclude_marker and not prefix and child.name == SLOT_MARKER_NAME:
                continue
            value = child.stat(follow_symlinks=False)
            kind = (
                "directory"
                if stat.S_ISDIR(value.st_mode)
                else "regular"
                if stat.S_ISREG(value.st_mode)
                else "symlink"
                if stat.S_ISLNK(value.st_mode)
                else "special"
            )
            if kind == "directory":
                entries.append(TreeEntry(kind, relative))
                visit(Path(child.path), relative)
            elif kind == "regular":
                mode = stat.S_IMODE(value.st_mode)
                if mode not in {0o644, 0o755}:
                    raise CandidateError(f"candidate regular mode is not 0644/0755: {relative}")
                entries.append(TreeEntry(kind, relative, mode, _regular_digest(child.path, value)))
            elif kind == "symlink":
                target = Path(child.path).readlink().as_posix()
                _safe_relative_symlink(target)
                entries.append(TreeEntry(kind, relative, target=target))
            else:
                raise CandidateError(f"candidate has unsupported entry: {relative}")

    visit(root, "")
    return tuple(sorted(entries, key=lambda entry: entry.path.encode("utf-8")))


def _entry_stream(entries: Sequence[TreeEntry]) -> bytes:
    stream = bytearray()
    for entry in entries:
        path = _bytes_path(entry.path, "candidate path")
        if entry.kind == "directory":
            stream.extend(b"D\0" + path + b"\0")
        elif entry.kind == "regular":
            if entry.mode not in {0o644, 0o755} or entry.sha256 is None:
                raise CandidateError("regular candidate entry is incomplete")
            stream.extend(b"F\0" + path + b"\0" + f"{entry.mode:04o}".encode() + b"\0" + entry.sha256.encode() + b"\0")
        elif entry.kind == "symlink":
            if entry.target is None:
                raise CandidateError("symlink candidate entry is incomplete")
            _safe_relative_symlink(entry.target)
            stream.extend(b"L\0" + path + b"\0" + _bytes_path(entry.target, "symlink target") + b"\0")
        else:
            raise CandidateError("unsupported candidate entry kind")
    return bytes(stream)


def _capture_domain(kind: str, public_path: str, source_path: Path) -> _CapturedDomain:
    try:
        value = source_path.stat(follow_symlinks=False)
    except OSError as exc:
        raise CandidateError(f"missing candidate domain: {source_path}") from exc
    if not stat.S_ISDIR(value.st_mode):
        raise CandidateError(f"candidate domain is not a directory: {public_path}")
    entries = _capture_entries(source_path, exclude_marker=kind == "slot")
    return _CapturedDomain(
        kind, public_path, source_path.as_posix(), entries, hashlib.sha256(_entry_stream(entries)).hexdigest()
    )


def _assets_root(source_root: Path | None) -> Path:
    if source_root is None:
        return Path(__file__).parent.parent / "assets"
    if _is_directory(source_root / "spec_dock") and _is_directory(source_root / "install_root"):
        return source_root
    if _is_directory(source_root / "assets" / "spec_dock") and _is_directory(source_root / "assets" / "install_root"):
        return source_root / "assets"
    raise CandidateError("source root does not contain the packaged asset roots")


def _is_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(os.lstat(path).st_mode)
    except FileNotFoundError:
        return False


def _captured_candidate(source_root: Path | None = None) -> tuple[_CapturedDomain, ...]:
    assets = _assets_root(source_root)
    captured: list[_CapturedDomain] = []
    for kind, public_path, source_suffix in FIXED_DOMAINS:
        captured.append(_capture_domain(kind, public_path, assets / source_suffix))
    return tuple(captured)


def _aggregate_digest(domains: Sequence[_CapturedDomain]) -> str:
    stream = bytearray(CANDIDATE_MAGIC + CANDIDATE_VERSION.encode("utf-8") + b"\0")
    for domain in domains:
        stream.extend(b"DOMAIN\0" + domain.kind.encode("utf-8") + b"\0" + domain.path.encode("utf-8") + b"\0")
        stream.extend(_entry_stream(domain.entries))
    return hashlib.sha256(stream).hexdigest()


def capture_packaged_candidate(source_root: str | os.PathLike[str] | None = None) -> CandidateIdentity:
    """Capture the six packaged domains in the fixed source order."""

    domains = _captured_candidate(None if source_root is None else Path(source_root))
    return CandidateIdentity(
        1, CANDIDATE_VERSION, _aggregate_digest(domains), tuple(domain.identity for domain in domains)
    )


def compute_candidate_digest(candidate: CandidateIdentity | Sequence[_CapturedDomain] | str | os.PathLike[str]) -> str:
    """Return the canonical aggregate digest for a candidate capture."""

    if isinstance(candidate, CandidateIdentity):
        return candidate.aggregate_digest
    if isinstance(candidate, (str, os.PathLike)):
        return _aggregate_digest(_captured_candidate(Path(candidate)))
    domains = tuple(candidate)
    return _aggregate_digest(domains)


def _staged_domain_path(staged_root: Path, index: int, domain: CandidateDomain) -> Path:
    public_path = Path(*domain.path.split("/"))
    if _is_directory(staged_root / public_path):
        return staged_root / public_path
    return staged_root / _SLOT_NAMES[index - 4] if index >= 4 else staged_root / domain.path.rsplit("/", 1)[-1]


def validate_staged_candidate(staged_root: str | os.PathLike[str], expected: CandidateIdentity) -> bool:
    """Validate a stage's six registered domains and both slot markers."""

    if (
        not isinstance(expected, CandidateIdentity)
        or expected.schema_version != 1
        or expected.version != CANDIDATE_VERSION
    ):
        raise CandidateError("expected candidate identity is invalid")
    if len(expected.domains) != len(FIXED_DOMAINS):
        raise CandidateError("expected candidate does not contain six domains")
    root = Path(staged_root)
    for index, identity in enumerate(expected.domains):
        if not isinstance(identity, CandidateDomain):
            raise CandidateError("candidate domain identity is invalid")
        expected_kind, expected_path, _ = FIXED_DOMAINS[index]
        if (identity.kind, identity.path) != (expected_kind, expected_path):
            raise CandidateError("candidate domain order or path mismatch")
        current_path = _staged_domain_path(root, index, identity)
        current = _capture_domain(identity.kind, identity.path, current_path)
        if current.identity != identity:
            raise CandidateError(f"staged candidate digest mismatch at {identity.path}")
        if identity.kind == "slot":
            marker_path = current_path / SLOT_MARKER_NAME
            try:
                marker = parse_slot_marker(marker_path.read_bytes())
            except (OSError, ValueError) as exc:
                raise CandidateError(f"slot marker is invalid at {identity.path}") from exc
            if (
                marker.slot != identity.path
                or marker.version != CANDIDATE_VERSION
                or marker.candidate_digest != expected.aggregate_digest
            ):
                raise CandidateError(f"slot marker does not bind to candidate at {identity.path}")
    if compute_candidate_digest(expected) != expected.aggregate_digest:
        raise CandidateError("expected candidate aggregate digest is inconsistent")
    return True


def slot_markers(candidate: CandidateIdentity) -> tuple[SkillSlotMarker, SkillSlotMarker]:
    """Build the two public marker values for a captured candidate."""

    return tuple(
        SkillSlotMarker(1, path, CANDIDATE_VERSION, candidate.aggregate_digest)
        for path in (FIXED_DOMAINS[4][1], FIXED_DOMAINS[5][1])
    )  # type: ignore[return-value]


def marker_bytes(candidate: CandidateIdentity, slot: str) -> bytes:
    """Return canonical marker bytes for one exact slot path."""

    return serialize_slot_marker(SkillSlotMarker(1, slot, CANDIDATE_VERSION, candidate.aggregate_digest))


__all__ = [
    "CANDIDATE_MAGIC",
    "CANDIDATE_VERSION",
    "FIXED_DOMAINS",
    "SLOT_MARKER_NAME",
    "CandidateError",
    "capture_packaged_candidate",
    "compute_candidate_digest",
    "marker_bytes",
    "slot_markers",
    "validate_staged_candidate",
]

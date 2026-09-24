"""Resolve only the fixed SpecDock supply source and inspect pinned archives."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from io import BytesIO
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
from typing import TYPE_CHECKING
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 uses the declared tomli dependency.
    import tomli as tomllib

if TYPE_CHECKING:
    from collections.abc import Iterable

SOURCE_REPOSITORY = "chemitaro/spec-dock"
SOURCE_URL = f"https://github.com/{SOURCE_REPOSITORY}.git"
_SHA = re.compile(r"[0-9a-f]{40}\Z")
_VERSION = re.compile(r"v?[0-9]+(?:\.[0-9]+){2}(?:[a-zA-Z0-9._-]*)\Z")
_REQUIRED_DIRECTORIES = (
    "src/spec_dock/assets/spec_dock/docs",
    "src/spec_dock/assets/spec_dock/templates",
    "src/spec_dock/assets/spec_dock/system",
    "src/spec_dock/assets/spec_dock/scripts",
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock",
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs",
)
_REQUIRED_FILES = (
    "pyproject.toml",
    "src/spec_dock/assets/spec_dock/.gitignore",
    "src/spec_dock/assets/spec_dock/workspace.json",
)
_MAX_ARCHIVE_SIZE = 200 * 1024 * 1024
_MAX_FILE_SIZE = 50 * 1024 * 1024


@dataclass(frozen=True)
class PinnedSource:
    repository: str
    commit: str
    version: str | None


@dataclass(frozen=True)
class PackagedSource:
    repository: str
    commit: None
    version: str


@dataclass(frozen=True)
class VerifiedBundle:
    source: PinnedSource | PackagedSource
    root: Path
    digest: str
    tooling_paths: tuple[str, ...]


def resolve_source(*, version: str | None, commit: str | None, ls_remote_tags: str = "") -> PinnedSource:
    """Freeze one explicit version or full commit before any archive is fetched."""
    if (version is None) == (commit is None):
        raise ValueError("specify exactly one version or commit")
    if commit is not None:
        if _SHA.fullmatch(commit) is None:
            raise ValueError("commit must be a complete lowercase SHA-1")
        return PinnedSource(SOURCE_REPOSITORY, commit, None)
    assert version is not None
    if _VERSION.fullmatch(version) is None:
        raise ValueError("version format is invalid")
    candidate_tags = {version, version.removeprefix("v") if version.startswith("v") else f"v{version}"}
    tags: dict[str, dict[str, str]] = {}
    for line in ls_remote_tags.splitlines():
        sha, separator, ref = line.partition("\t")
        if not separator or _SHA.fullmatch(sha) is None or not ref.startswith("refs/tags/"):
            raise ValueError("tag resolution response is invalid")
        tag_name = ref.removeprefix("refs/tags/")
        peeled = tag_name.endswith("^{}")
        tag_name = tag_name[:-3] if peeled else tag_name
        if tag_name in candidate_tags:
            key = "peeled" if peeled else "direct"
            previous = tags.setdefault(tag_name, {}).get(key)
            if previous is not None and previous != sha:
                raise ValueError("tag resolution is inconsistent")
            tags[tag_name][key] = sha
    if len(tags) != 1:
        raise ValueError("version must resolve to exactly one fixed-source tag")
    references = next(iter(tags.values()))
    pinned = references.get("peeled") or references.get("direct")
    if pinned is None:
        raise ValueError("tag has no commit identity")
    return PinnedSource(SOURCE_REPOSITORY, pinned, version)


def resolve_fixed_source(*, version: str | None, commit: str | None, timeout: float = 30.0) -> PinnedSource:
    """Query tags once from the sole trusted source and retain only the returned SHA."""
    if commit is not None or version is None:
        return resolve_source(version=version, commit=commit)
    if timeout <= 0:
        raise ValueError("source resolution timeout must be positive")
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_CONFIG_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    try:
        with tempfile.TemporaryDirectory(prefix="specdock-source-") as directory:
            completed = subprocess.run(
                ["git", "ls-remote", "--tags", SOURCE_URL],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                env=environment,
            )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("fixed source tag resolution failed") from error
    if completed.returncode != 0:
        raise ValueError("fixed source tag resolution failed")
    return resolve_source(version=version, commit=None, ls_remote_tags=completed.stdout)


def fixed_archive_url(source: PinnedSource) -> str:
    if source.repository != SOURCE_REPOSITORY or _SHA.fullmatch(source.commit) is None:
        raise ValueError("archive source is not the fixed SpecDock repository")
    return f"https://api.github.com/repos/{SOURCE_REPOSITORY}/tarball/{source.commit}"


def download_pinned_archive(source: PinnedSource, *, timeout: float = 60.0) -> bytes:
    """Fetch only the frozen commit archive; never execute received bytes."""
    if timeout <= 0:
        raise ValueError("archive download timeout must be positive")
    request = Request(fixed_archive_url(source), headers={"User-Agent": "spec-dock-installer"})
    try:
        with urlopen(request, timeout=timeout) as response:
            final_url = urlsplit(response.geturl())
            expected_api_path = f"/repos/{SOURCE_REPOSITORY}/tarball/{source.commit}"
            allowed_destination = (final_url.hostname == "api.github.com" and final_url.path == expected_api_path) or (
                final_url.hostname == "codeload.github.com"
                and final_url.path.startswith(f"/{SOURCE_REPOSITORY}/")
                and final_url.path.rsplit("/", 1)[-1] == source.commit
            )
            if final_url.scheme != "https" or not allowed_destination:
                raise ValueError("archive redirected outside the fixed GitHub hosts")
            archive = response.read(_MAX_ARCHIVE_SIZE + 1)
    except (OSError, URLError) as error:
        raise ValueError("fixed archive download failed") from error
    if len(archive) > _MAX_ARCHIVE_SIZE:
        raise ValueError("archive exceeds size limit")
    return archive


def assert_disjoint_source_target(source: Path, target: Path) -> None:
    source_path = source.resolve(strict=True)
    target_path = target.resolve(strict=False)
    if source_path == target_path or source_path.is_relative_to(target_path) or target_path.is_relative_to(source_path):
        raise ValueError("distribution source and installation target overlap")


def _members(archive: bytes) -> tuple[tuple[str, tarfile.TarInfo, bytes], ...]:
    if len(archive) > _MAX_ARCHIVE_SIZE:
        raise ValueError("archive exceeds size limit")
    with tarfile.open(fileobj=BytesIO(archive), mode="r:gz") as stream:
        members = stream.getmembers()
        entries: list[tuple[str, tarfile.TarInfo, bytes]] = []
        prefix: str | None = None
        names: set[str] = set()
        spellings: dict[str, str] = {}
        kinds: dict[str, str] = {}
        total = 0
        for member in members:
            name = member.name
            normalized = name[:-1] if member.isdir() and name.endswith("/") else name
            path = PurePosixPath(normalized)
            parts = path.parts
            if (
                not parts
                or name.startswith("/")
                or "\\" in name
                or "\x00" in name
                or any(part in ("", ".", "..") for part in normalized.split("/"))
            ):
                raise ValueError("archive member path is unsafe")
            if prefix is None:
                prefix = parts[0]
            if parts[0] != prefix:
                raise ValueError("archive has multiple roots")
            if not member.isdir() and not member.isfile():
                raise ValueError("archive contains a link or special file")
            if member.mode & ~0o777 or member.mode & 0o022:
                raise ValueError("archive permissions are unsafe")
            if len(parts) == 1:
                continue
            relative = PurePosixPath(*parts[1:]).as_posix()
            for depth in range(1, len(parts)):
                component = PurePosixPath(*parts[1 : depth + 1]).as_posix()
                folded_component = component.casefold()
                earlier = spellings.setdefault(folded_component, component)
                if earlier != component:
                    raise ValueError("archive path capitalization collides")
                kind = "file" if depth == len(parts) - 1 and member.isfile() else "directory"
                existing_kind = kinds.setdefault(folded_component, kind)
                if existing_kind != kind:
                    raise ValueError("archive path type collides")
            folded = relative.casefold()
            if member.isfile():
                if folded in names or member.size > _MAX_FILE_SIZE:
                    raise ValueError("archive member is duplicated or too large")
                names.add(folded)
                total += member.size
                if total > _MAX_ARCHIVE_SIZE:
                    raise ValueError("archive expanded size limit exceeded")
                stream_file = stream.extractfile(member)
                if stream_file is None:
                    raise ValueError("archive file cannot be read")
                content = stream_file.read(_MAX_FILE_SIZE + 1)
                if len(content) != member.size:
                    raise ValueError("archive file length differs")
                entries.append((relative, member, content))
        return tuple(entries)


def _tooling_inventory(root: Path) -> tuple[str, ...]:
    for path in _REQUIRED_DIRECTORIES:
        if not (root / path).is_dir():
            raise ValueError(f"fixed distribution lacks managed directory: {path}")
    for path in _REQUIRED_FILES:
        if not (root / path).is_file():
            raise ValueError(f"fixed distribution lacks packaged file: {path}")
    paths: list[str] = list(_REQUIRED_FILES)
    for directory in _REQUIRED_DIRECTORIES:
        paths.extend(path.relative_to(root).as_posix() for path in (root / directory).rglob("*") if path.is_file())
    return tuple(sorted(paths))


def _preflight_tooling_entries(entries: tuple[tuple[str, tarfile.TarInfo, bytes], ...], *, version: str | None) -> None:
    by_name = {name: content for name, _member, content in entries}
    for path in _REQUIRED_FILES:
        if path not in by_name:
            raise ValueError(f"fixed distribution lacks packaged file: {path}")
    for directory in _REQUIRED_DIRECTORIES:
        if not any(name.startswith(f"{directory}/") for name in by_name):
            raise ValueError(f"fixed distribution lacks managed directory: {directory}")
    try:
        project = tomllib.loads(by_name["pyproject.toml"].decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError("archive project identity is invalid") from error
    metadata = project.get("project")
    if not isinstance(metadata, dict) or metadata.get("name") != "spec-dock":
        raise ValueError("archive project identity is not SpecDock")
    if version is not None and metadata.get("version") != version.removeprefix("v"):
        raise ValueError("archive package version differs from pinned tag")


def _digest_paths(root: Path, paths: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for name in paths:
        path = root / name
        data = path.read_bytes()
        mode = path.stat().st_mode & 0o777
        digest.update(name.encode() + b"\0" + mode.to_bytes(2, "big") + hashlib.sha256(data).digest() + b"\0")
    return digest.hexdigest()


def verify_bundle_integrity(bundle: VerifiedBundle) -> None:
    """Recheck the immutable input just before installer staging."""
    if isinstance(bundle.source, PinnedSource):
        fixed_archive_url(bundle.source)
    elif bundle.source.repository != SOURCE_REPOSITORY or _VERSION.fullmatch(bundle.source.version) is None:
        raise ValueError("packaged bundle source identity is invalid")
    root = bundle.root
    if not root.is_dir() or root.is_symlink():
        raise ValueError("verified bundle root is unavailable")
    paths: list[str] = []
    for path in root.rglob("*"):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            raise ValueError("verified bundle contains an unsafe entry")
        if path.is_file():
            paths.append(path.relative_to(root).as_posix())
    if _digest_paths(root, sorted(paths)) != bundle.digest or _tooling_inventory(root) != bundle.tooling_paths:
        raise ValueError("verified bundle content changed after archive validation")


def packaged_bundle(*, assets_root: Path, destination: Path, version: str) -> VerifiedBundle:
    """Normalize the executing package's assets into a verified inert bundle."""
    if _VERSION.fullmatch(version) is None or not assets_root.is_absolute() or not assets_root.is_dir():
        raise ValueError("installed package source is invalid")
    if not destination.is_absolute() or destination.exists() or destination.is_symlink():
        raise ValueError("package bundle destination must be a new absolute directory")
    for path in assets_root.rglob("*"):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            raise ValueError("installed package has an unsafe asset")
    normalized = destination / "src/spec_dock/assets"
    normalized.parent.mkdir(parents=True)
    shutil.copytree(
        assets_root,
        normalized,
        symlinks=False,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    (destination / "pyproject.toml").write_text(
        f'[project]\nname = "spec-dock"\nversion = "{version.removeprefix("v")}"\n', encoding="utf-8"
    )
    paths = tuple(sorted(path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()))
    bundle = VerifiedBundle(
        PackagedSource(SOURCE_REPOSITORY, None, version),
        destination,
        _digest_paths(destination, paths),
        _tooling_inventory(destination),
    )
    verify_bundle_integrity(bundle)
    return bundle


def verify_pinned_archive(source: PinnedSource, archive: bytes, destination: Path) -> VerifiedBundle:
    """Extract inert regular files only into a new directory, then hash all inputs."""
    fixed_archive_url(source)
    entries = _members(archive)
    _preflight_tooling_entries(entries, version=source.version)
    if (
        not destination.is_absolute()
        or ".." in destination.parts
        or any(parent.is_symlink() for parent in destination.parents)
    ):
        raise ValueError("archive destination path is unsafe")
    if destination.exists() or destination.is_symlink():
        raise ValueError("archive destination must be new")
    destination.mkdir(mode=0o700, parents=True)
    for name, member, content in entries:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
        path.chmod(0o755 if member.mode & 0o111 else 0o644)
    tooling_paths = _tooling_inventory(destination)
    all_paths = tuple(sorted(name for name, _member, _content in entries))
    return VerifiedBundle(source, destination, _digest_paths(destination, all_paths), tooling_paths)

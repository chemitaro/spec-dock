"""Replace fixed tooling directories; consumer data is outside this boundary."""

from __future__ import annotations

from pathlib import Path
import shutil

ASSETS = Path(__file__).parent / "assets"
ROOTS = ("docs", "templates", "system", "scripts")
SKILLS = ("spec-dock", "spec-dock-grill-with-docs")
TOOL_DIRECTORIES = tuple(f"spec-dock/{name}" for name in ROOTS) + tuple(f".agents/skills/{name}" for name in SKILLS)
VERSION_FILE = "spec-dock/spec-dock.version"


def _check_target(target: Path) -> None:
    """Reject redirecting parents before deleting any managed directory."""
    for relative in (*TOOL_DIRECTORIES, VERSION_FILE):
        path = target
        for part in Path(relative).parts:
            path = path / part
            if path.is_symlink():
                raise ValueError(f"Refusing symbolic link in installation target: {path}")
            if path.exists() and not path.is_dir() and path != target / VERSION_FILE:
                raise ValueError(f"Expected installation directory: {path}")
        if relative == VERSION_FILE and path.exists() and not path.is_file():
            raise ValueError(f"Expected version file: {path}")


def _sources(assets: Path) -> tuple[Path, ...]:
    return tuple(assets / "spec_dock" / name for name in ROOTS) + tuple(
        assets / "install_root/.agents/skills" / name for name in SKILLS
    )


def _copy(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))


def install(target: Path, *, version: str, fresh: bool, assets: Path = ASSETS) -> None:
    """Prepare all paths, replace the directories, then record the version.

    Updates are deliberately non-transactional. Stop repository commands while
    updating; after an I/O failure rerun the external installer from the start.
    """
    _check_target(target)
    sources = _sources(assets)
    for source in sources:
        if not source.is_dir():
            raise ValueError(f"Missing packaged directory: {source}")
        for relative in TOOL_DIRECTORIES:
            destination = (target / relative).resolve()
            if source.resolve().is_relative_to(destination) or destination.is_relative_to(source.resolve()):
                raise ValueError("Installation target overlaps the distribution source")
    target.mkdir(parents=True, exist_ok=True)
    if fresh:
        _copy(assets / "spec_dock", target / "spec-dock")
    for relative, source in zip(TOOL_DIRECTORIES, sources, strict=True):
        if fresh and relative.startswith("spec-dock/"):
            continue
        destination = target / relative
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _copy(source, destination)
    version_path = target / VERSION_FILE
    version_path.unlink(missing_ok=True)
    version_path.write_text(version + "\n", encoding="utf-8")


def uninstall(target: Path, *, apply: bool) -> None:
    """Remove only fixed tooling paths. A missing installation is harmless."""
    _check_target(target)
    if not apply:
        return
    for relative in TOOL_DIRECTORIES:
        path = target / relative
        if path.exists():
            shutil.rmtree(path)
    (target / VERSION_FILE).unlink(missing_ok=True)

"""Replace fixed tooling directories; consumer data is outside this boundary."""

from __future__ import annotations

from pathlib import Path
import shutil

ASSETS = Path(__file__).parent / "assets"
ROOTS = ("docs", "templates", "system", "scripts")
SKILLS = ("spec-dock", "spec-dock-grill-with-docs")
TOOL_DIRECTORIES = tuple(f"spec-dock/{name}" for name in ROOTS) + tuple(f".agents/skills/{name}" for name in SKILLS)
VERSION_FILE = "spec-dock/spec-dock.version"
IGNORE_FILE = "spec-dock/.gitignore"
LEGACY_WORKBENCH_IGNORE = (
    b"# spec-dock runtime (generated)\n"
    b"# v2 generated state for agents (SSOT + derived views)\n"
    b".agent/\n"
    b"# legacy v2 name (kept ignored for safe upgrades)\n"
    b".work/\n"
    b"# local disposable work areas (reserved exact directory name at any scope)\n"
    b".workbench/\n"
    b"active/\n"
    b"/adrs/\n"
    b"tree-all.puml\n"
    b"tree.puml\n"
    b"deps-issues.puml\n"
    b"deps-raw.puml\n"
    b"dashboard.md\n"
)


def _check_target(target: Path) -> None:
    """Reject redirecting parents before deleting any managed directory."""
    for relative in (*TOOL_DIRECTORIES, VERSION_FILE, IGNORE_FILE):
        path = target
        for part in Path(relative).parts:
            path = path / part
            if path.is_symlink():
                raise ValueError(f"Refusing symbolic link in installation target: {path}")
            if path.exists() and not path.is_dir() and path not in (target / VERSION_FILE, target / IGNORE_FILE):
                raise ValueError(f"Expected installation directory: {path}")
        if relative in (VERSION_FILE, IGNORE_FILE) and path.exists() and not path.is_file():
            raise ValueError(f"Expected installation file: {path}")


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
    if fresh:
        source = (assets / "spec_dock").resolve()
        destination = (target / "spec-dock").resolve()
        if source.is_relative_to(destination) or destination.is_relative_to(source):
            raise ValueError("Installation target overlaps the distribution source")
    if not (assets / "spec_dock/.gitignore").is_file():
        raise ValueError("Missing packaged file: spec-dock/.gitignore")
    target.mkdir(parents=True, exist_ok=True)
    if fresh:
        _copy(assets / "spec_dock", target / "spec-dock")
        root_workbench = target / "spec-dock/.workbench"
        root_workbench.mkdir()
        shutil.copyfile(
            assets / "spec_dock/templates/root/.workbench/README.md",
            root_workbench / "README.md",
        )
    for relative, source in zip(TOOL_DIRECTORIES, sources, strict=True):
        if fresh and relative.startswith("spec-dock/"):
            continue
        destination = target / relative
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _copy(source, destination)
    ignore_path = target / IGNORE_FILE
    if ignore_path.exists() and ignore_path.read_bytes() == LEGACY_WORKBENCH_IGNORE:
        ignore_path.unlink()
    if not ignore_path.exists():
        shutil.copyfile(assets / "spec_dock/.gitignore", ignore_path)
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

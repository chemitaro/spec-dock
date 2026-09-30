"""Static resources shipped by the installed package."""

from importlib.resources import files
from pathlib import Path

ASSETS = Path(str(files("spec_dock").joinpath("assets")))
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

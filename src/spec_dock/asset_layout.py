"""Static resources shipped by the installed package."""

from importlib.resources import files
from pathlib import Path

ASSETS = Path(str(files("spec_dock").joinpath("assets")))
ROOTS = ("docs", "templates", "system", "scripts")
SKILLS = ("spec-dock", "spec-dock-grill-with-docs")
SKILL_ROOTS = (".agents/skills",)
TOOL_DIRECTORIES = tuple(f"spec-dock/{name}" for name in ROOTS) + tuple(
    f"{root}/{name}" for root in SKILL_ROOTS for name in SKILLS
)
VERSION_FILE = "spec-dock/spec-dock.version"
IGNORE_FILE = "spec-dock/.gitignore"

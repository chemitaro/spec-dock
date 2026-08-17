import json
import os
from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

_STALE_BUILD_OUTPUT_PATTERNS = (
    "spec_dock/assets/spec_dock/scripts/spec-dock-close*.sh",
    "spec_dock/assets/github/workflows/spec-dock-close.yml",
    "spec_dock/assets/spec_dock/templates/**/current/**",
    "spec_dock/assets/spec_dock/templates/**/completed/**",
    "spec_dock/assets/spec_dock/templates/adr.md",
    "spec_dock/assets/spec_dock/templates/**/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
    "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
    "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
    "spec_dock/assets/spec_dock/templates/design.md",
    "spec_dock/assets/spec_dock/templates/plan.md",
    "spec_dock/assets/spec_dock/templates/report.md",
    "spec_dock/assets/spec_dock/templates/requirement.md",
)

_DISTRIBUTABLE_TEMPLATE_README_PATHS = (
    "README.md",
    "root/.workbench/README.md",
    "initiative/.workbench/README.md",
    "epic/.workbench/README.md",
    "issue/.workbench/README.md",
)
_BUILD_TEMPLATE_ROOT = Path("spec_dock/assets/spec_dock/templates")
_SOURCE_TEMPLATE_ROOT = Path("src/spec_dock/assets/spec_dock/templates")
_BUILD_ASSET_ROOT = Path("spec_dock/assets")
_SOURCE_ASSET_ROOT = Path("src/spec_dock/assets")

_GENERATED_PYTHON_CACHE_PATTERNS = (
    "spec_dock/**/__pycache__",
    "spec_dock/**/__pycache__/**",
    "spec_dock/**/*.pyc",
    "spec_dock/**/*.pyo",
)

_SEEDED_STALE_OUTPUT_FIXTURE_PATHS = (
    "spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md",
    "spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md",
    "spec_dock/assets/spec_dock/scripts/authoring-pack/README.md",
    "spec_dock/assets/spec_dock/scripts/spec-dock-close-smoke.sh",
    "spec_dock/assets/github/workflows/spec-dock-close.yml",
    "spec_dock/assets/spec_dock/templates/initiative/current/stale.md",
    "spec_dock/assets/spec_dock/templates/initiative/completed/stale.md",
    "spec_dock/assets/spec_dock/templates/adr.md",
    "spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
    "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
    "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
    "spec_dock/assets/spec_dock/templates/issue/legacy/README.md",
    "spec_dock/assets/spec_dock/templates/design.md",
    "spec_dock/assets/spec_dock/templates/plan.md",
    "spec_dock/assets/spec_dock/templates/report.md",
    "spec_dock/assets/spec_dock/templates/requirement.md",
)
_SEED_STALE_BUILD_OUTPUTS_ENV_VAR = "SPEC_DOCK_BUILD_PY_SEED_STALE_FIXTURES"
_PRE_PRUNE_SNAPSHOT_ENV_VAR = "SPEC_DOCK_BUILD_PY_PRE_PRUNE_SNAPSHOT"


def _is_generated_python_cache_path(path: str) -> bool:
    candidate = Path(path)
    return "__pycache__" in candidate.parts or candidate.suffix in {".pyc", ".pyo"}


def _is_distributable_template_readme_source(path: str) -> bool:
    candidate = Path(path)
    if candidate.name != "README.md":
        return True
    try:
        template_relative = candidate.relative_to(_SOURCE_TEMPLATE_ROOT).as_posix()
    except ValueError:
        return True
    return template_relative in _DISTRIBUTABLE_TEMPLATE_README_PATHS


def _prune_stale_build_outputs(build_lib: Path) -> None:
    stale_paths = {
        path
        for pattern in (*_GENERATED_PYTHON_CACHE_PATTERNS, *_STALE_BUILD_OUTPUT_PATTERNS)
        for path in build_lib.glob(pattern)
    }
    template_root = build_lib / _BUILD_TEMPLATE_ROOT
    stale_paths.update(
        path
        for path in template_root.rglob("README.md")
        if path.relative_to(template_root).as_posix() not in _DISTRIBUTABLE_TEMPLATE_README_PATHS
    )
    build_asset_root = build_lib / _BUILD_ASSET_ROOT
    stale_paths.update(
        path
        for path in build_asset_root.rglob("*")
        if not (_SOURCE_ASSET_ROOT / path.relative_to(build_asset_root)).exists()
    )
    for stale_path in sorted(stale_paths, key=lambda path: len(path.parts), reverse=True):
        if stale_path.is_dir():
            shutil.rmtree(stale_path, ignore_errors=True)
        elif stale_path.exists():
            stale_path.unlink()


def _seed_stale_build_outputs(build_lib: Path) -> None:
    for fixture_relative_path in _SEEDED_STALE_OUTPUT_FIXTURE_PATHS:
        fixture_path = build_lib / fixture_relative_path
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text("stale wrapper-era artifact fixture\n", encoding="utf-8")


def _write_pre_prune_snapshot(build_lib: Path) -> None:
    snapshot_target = os.environ.get(_PRE_PRUNE_SNAPSHOT_ENV_VAR)
    if not snapshot_target:
        return

    snapshot_path = Path(snapshot_target)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    present_before_prune = [
        fixture_relative_path
        for fixture_relative_path in _SEEDED_STALE_OUTPUT_FIXTURE_PATHS
        if (build_lib / fixture_relative_path).is_file()
    ]
    template_root = build_lib / _BUILD_TEMPLATE_ROOT
    template_readmes_before_prune = sorted(
        path.relative_to(template_root).as_posix() for path in template_root.rglob("README.md") if path.is_file()
    )
    snapshot_payload = {
        "expected_seeded_stale_fixture_paths": list(_SEEDED_STALE_OUTPUT_FIXTURE_PATHS),
        "present_before_prune": present_before_prune,
        "template_readmes_before_prune": template_readmes_before_prune,
    }
    snapshot_path.write_text(
        json.dumps(snapshot_payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


class build_py(_build_py):
    def run(self) -> None:
        build_lib = Path(self.build_lib)
        super().run()
        if os.environ.get(_SEED_STALE_BUILD_OUTPUTS_ENV_VAR) == "1":
            _seed_stale_build_outputs(build_lib)
        _write_pre_prune_snapshot(build_lib)
        _prune_stale_build_outputs(build_lib)


class sdist(_sdist):
    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        distributable_files = [
            path
            for path in files
            if not _is_generated_python_cache_path(path) and _is_distributable_template_readme_source(path)
        ]
        super().make_release_tree(base_dir, distributable_files)


setup(cmdclass={"build_py": build_py, "sdist": sdist})

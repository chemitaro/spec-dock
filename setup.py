import json
import os
from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

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
    "spec_dock/assets/spec_dock/templates/*/**/README.md",
    "spec_dock/assets/spec_dock/templates/design.md",
    "spec_dock/assets/spec_dock/templates/plan.md",
    "spec_dock/assets/spec_dock/templates/report.md",
    "spec_dock/assets/spec_dock/templates/requirement.md",
)

_SEEDED_STALE_OUTPUT_FIXTURE_PATHS = (
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


def _prune_stale_build_outputs(build_lib: Path) -> None:
    stale_paths = {path for pattern in _STALE_BUILD_OUTPUT_PATTERNS for path in build_lib.glob(pattern)}
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
    snapshot_payload = {
        "expected_seeded_stale_fixture_paths": list(_SEEDED_STALE_OUTPUT_FIXTURE_PATHS),
        "present_before_prune": present_before_prune,
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


setup(cmdclass={"build_py": build_py})

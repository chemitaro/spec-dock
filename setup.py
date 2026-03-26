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


def _prune_stale_build_outputs(build_lib: Path) -> None:
    stale_paths = {
        path
        for pattern in _STALE_BUILD_OUTPUT_PATTERNS
        for path in build_lib.glob(pattern)
    }
    for stale_path in sorted(stale_paths, key=lambda path: len(path.parts), reverse=True):
        if stale_path.is_dir():
            shutil.rmtree(stale_path, ignore_errors=True)
        elif stale_path.exists():
            stale_path.unlink()


class build_py(_build_py):
    def run(self) -> None:
        super().run()
        _prune_stale_build_outputs(Path(self.build_lib))


setup(cmdclass={"build_py": build_py})

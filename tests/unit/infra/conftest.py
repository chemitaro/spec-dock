"""Avoid repeating provider installation used only as an infra-test precondition."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

import pytest

_SETUP_ONLY_PREFIXES = (
    "test_checked_in_dogfooding_",
    "test_recognized_reconciliation_",
    "test_uninstall_",
    "test_update_",
)


def _clone_tree_contents(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    command = (
        ["cp", "-cR", f"{source}/.", str(target)]
        if sys.platform == "darwin"
        else ["cp", "--reflink=auto", "-a", f"{source}/.", str(target)]
    )
    try:
        subprocess.run(command, check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        shutil.copytree(source, target, symlinks=True, dirs_exist_ok=True)


@pytest.fixture(scope="session")
def _infra_init_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    module = pytest.importorskip("tests.unit.infra.test_init_update")
    template = tmp_path_factory.mktemp("spec-dock-infra-init-template")
    assert module.main(["init", str(template)]) == 0
    return template


@pytest.fixture(autouse=True)  # noqa: RUF076
def _reuse_infra_init_result(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    _infra_init_template: Path,
) -> None:
    module_name = request.node.nodeid.split("::", 1)[0][:-3].replace("/", ".")
    if module_name != "tests.unit.infra.test_init_update":
        return
    if not request.node.originalname.startswith(_SETUP_ONLY_PREFIXES):
        return

    real_main = request.module.main

    def cached_main(args: list[str]) -> int:
        if len(args) != 2 or args[0] != "init":
            return real_main(args)
        target = Path(args[1])
        if not target.is_dir() or any(target.iterdir()):
            return real_main(args)
        _clone_tree_contents(_infra_init_template, target)
        return 0

    monkeypatch.setattr(request.module, "main", cached_main)

"""Avoid repeating provider installation for dogfooding parity tests."""

from __future__ import annotations

from pathlib import Path
import shutil

import pytest


@pytest.fixture(scope="session")
def _dogfooding_init_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    module = pytest.importorskip("tests.unit.infra.test_init_update")
    template = tmp_path_factory.mktemp("spec-dock-dogfooding-init-template")
    assert module.main(["init", str(template)]) == 0
    return template


@pytest.fixture
def _reuse_dogfooding_init_result(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    _dogfooding_init_template: Path,
) -> None:
    if request.module.__name__ != "tests.unit.infra.test_init_update":
        return
    if "checked_in_dogfooding" not in request.node.originalname:
        return

    real_main = request.module.main

    def cached_main(args: list[str]) -> int:
        if len(args) != 2 or args[0] != "init":
            return real_main(args)
        target = Path(args[1])
        if not target.is_dir() or any(target.iterdir()):
            return real_main(args)
        shutil.copytree(_dogfooding_init_template, target, symlinks=True, dirs_exist_ok=True)
        return 0

    monkeypatch.setattr(request.module, "main", cached_main)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        module_name = item.nodeid.split("::", 1)[0][:-3].replace("/", ".")
        if module_name != "tests.unit.infra.test_init_update":
            continue
        if "checked_in_dogfooding" in item.nodeid:
            item.add_marker(pytest.mark.usefixtures("_reuse_dogfooding_init_result"))

"""Shared setup optimisations for the CLI runtime regression lane.

The runtime tests exercise commands after a freshly provisioned workspace in
many cases.  Re-running the complete provider distribution for every such
case makes the full lane measure provisioning repeatedly instead of the
behaviour under test.  Modules that do not test the init implementation opt
into a session-built, immutable init result below.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tests.cli_runtime import harness

# Keep tests that deliberately monkeypatch or assert the distribution cutover
# on the real init path.  The listed modules exercise runtime commands against
# an already-provisioned workspace and do not assert the init implementation.
_TEMPLATE_MODULES = frozenset({
    "tests.cli_runtime.test_active",
    "tests.cli_runtime.test_artifact_import_file",
    "tests.cli_runtime.test_artifact_import_s04",
    "tests.cli_runtime.test_close",
    "tests.cli_runtime.test_delete",
    "tests.cli_runtime.test_deps",
    "tests.cli_runtime.test_doctor",
    "tests.cli_runtime.test_import",
    "tests.cli_runtime.test_issue_lifecycle",
    "tests.cli_runtime.test_new",
    "tests.cli_runtime.test_storage_core_cli",
    "tests.cli_runtime.test_sync",
    "tests.cli_runtime.test_uninstall",
    "tests.cli_runtime.test_update",
    "tests.cli_runtime.test_validate",
    "tests.cli_runtime.test_workbench",
    "tests.cli_runtime.test_worktree",
    "tests.cli_runtime.test_wrappers",
})
_DISTRIBUTION_CUTOVER_MODULE = "tests.cli_runtime.test_distribution_cutover"
_DISTRIBUTION_SETUP_OPERATIONS = ("update", "uninstall", "recognized")


def _can_reuse_fresh_init_result(module_name: str, test_name: str) -> bool:
    """Return whether plain init is only a precondition for this test."""

    if module_name in _TEMPLATE_MODULES:
        return True
    if module_name != _DISTRIBUTION_CUTOVER_MODULE:
        return False
    return (
        any(operation in test_name for operation in _DISTRIBUTION_SETUP_OPERATIONS)
        and "fresh" not in test_name
        and "reinit" not in test_name
    )


def _clone_tree_contents(source: Path, target: Path) -> None:
    """Clone a setup tree with copy-on-write when the host supports it."""

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
def _fresh_init_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build one real init result for the cacheable runtime test modules."""

    template = tmp_path_factory.mktemp("spec-dock-init-template")
    assert harness.main(["init", str(template)]) == 0
    return template


# Dynamic usefixtures markers are added after fixture closure construction;
# autouse plus the nodeid allow-list is required for deterministic activation.
@pytest.fixture(autouse=True)  # noqa: RUF076
def _reuse_fresh_init_result(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    _fresh_init_template: Path,
) -> None:
    """Copy the real init result only for tests that use it as a precondition.

    A test that passes any init option, targets a non-empty directory, or is
    outside the allow-list continues to execute the real provider init path.
    This preserves tests for source capture, security races, and cutover
    semantics while removing repeated setup from command-behaviour tests.
    """

    module_name = request.node.nodeid.split("::", 1)[0][:-3].replace("/", ".")
    if not _can_reuse_fresh_init_result(module_name, request.node.originalname):
        return

    real_main = request.module.main

    def cached_main(args: list[str]) -> int:
        if len(args) != 2 or args[0] != "init":
            return real_main(args)
        target = Path(args[1])
        if not target.is_dir() or any(target.iterdir()):
            return real_main(args)
        _clone_tree_contents(_fresh_init_template, target)
        return 0

    monkeypatch.setattr(request.module, "main", cached_main)

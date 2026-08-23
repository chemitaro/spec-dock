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
    "tests.cli_runtime.test_storage_core_cli",
    "tests.cli_runtime.test_sync",
    "tests.cli_runtime.test_uninstall",
    "tests.cli_runtime.test_update",
    "tests.cli_runtime.test_validate",
    "tests.cli_runtime.test_workbench",
    "tests.cli_runtime.test_worktree",
    "tests.cli_runtime.test_wrappers",
})


def _remove_tree_entry(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _copy_tree_replace_symlinks(source: Path, target: Path) -> None:
    """Copy a setup tree without following or colliding with target symlinks."""

    target.mkdir(parents=True, exist_ok=True)
    for source_entry in source.iterdir():
        target_entry = target / source_entry.name
        if source_entry.is_symlink():
            if target_entry.exists() or target_entry.is_symlink():
                _remove_tree_entry(target_entry)
            target_entry.symlink_to(source_entry.readlink())
        elif source_entry.is_dir():
            if target_entry.is_symlink() or target_entry.is_file():
                _remove_tree_entry(target_entry)
            _copy_tree_replace_symlinks(source_entry, target_entry)
        else:
            if target_entry.exists() or target_entry.is_symlink():
                _remove_tree_entry(target_entry)
            shutil.copy2(source_entry, target_entry)


@pytest.fixture(scope="session")
def _fresh_init_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build one real init result for the cacheable runtime test modules."""

    template = tmp_path_factory.mktemp("spec-dock-init-template")
    assert harness.main(["init", str(template)]) == 0
    return template


@pytest.fixture(scope="session")
def _linked_hierarchy_templates(
    _fresh_init_template: Path,
) -> dict[tuple[object, ...], Path]:
    """Hold materialized ``new initiative/epic/issue`` setup templates."""

    return {}


@pytest.fixture
def _reuse_fresh_init_result(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
    _fresh_init_template: Path,
    _linked_hierarchy_templates: dict[tuple[object, ...], Path],
) -> None:
    """Copy the real init result only for tests that use it as a precondition.

    A test that passes any init option, targets a non-empty directory, or is
    outside the allow-list continues to execute the real provider init path.
    This preserves tests for source capture, security races, and cutover
    semantics while removing repeated setup from command-behaviour tests.
    """

    module_name = request.module.__name__
    if module_name not in _TEMPLATE_MODULES:
        return

    real_main = request.module.main
    fresh_targets: set[Path] = set()

    def cached_main(args: list[str]) -> int:
        if len(args) != 2 or args[0] != "init":
            return real_main(args)
        target = Path(args[1])
        if not target.is_dir() or any(target.iterdir()):
            return real_main(args)
        shutil.copytree(_fresh_init_template, target, symlinks=True, dirs_exist_ok=True)
        fresh_targets.add(target.resolve())
        return 0

    monkeypatch.setattr(request.module, "main", cached_main)

    instance = request.instance
    if instance is None or not hasattr(instance, "_create_same_repo_linked_hierarchy"):
        return
    real_create = instance._create_same_repo_linked_hierarchy

    def cached_create(target: Path, *args: object, **kwargs: object) -> None:
        initiatives = target / "spec-dock" / "initiatives"
        if (
            target.is_symlink()
            or target.resolve() not in fresh_targets
            or (target / ".git").exists()
            or not initiatives.is_dir()
            or any(initiatives.iterdir())
        ):
            real_create(target, *args, **kwargs)
            return

        key = (type(instance), args, tuple(sorted(kwargs.items(), key=lambda item: item[0])))
        template = _linked_hierarchy_templates.get(key)
        if template is None:
            template = tmp_path_factory.mktemp("spec-dock-linked-hierarchy")
            shutil.copytree(_fresh_init_template, template, symlinks=True, dirs_exist_ok=True)
            real_create(template, *args, **kwargs)
            _linked_hierarchy_templates[key] = template
        _copy_tree_replace_symlinks(template, target)
        fresh_targets.discard(target.resolve())

    monkeypatch.setattr(instance, "_create_same_repo_linked_hierarchy", cached_create)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        module_name = item.nodeid.split("::", 1)[0][:-3].replace("/", ".")
        if module_name in _TEMPLATE_MODULES:
            item.add_marker(pytest.mark.usefixtures("_reuse_fresh_init_result"))

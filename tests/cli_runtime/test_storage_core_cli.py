from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main

RETAINED_REGISTRY_KEYS = {
    "active_clear",
    "active_set",
    "active_show",
    "artifact_import_file",
    "close",
    "delete",
    "deps_add",
    "deps_check",
    "deps_remove",
    "doctor",
    "import_epic",
    "import_initiative",
    "import_issue",
    "issue_finish",
    "issue_start",
    "new_artifact",
    "new_epic",
    "new_initiative",
    "new_issue",
    "sync",
    "uninstall",
    "update",
    "validate",
    "workbench_copy",
    "worktree_create",
    "worktree_list",
    "worktree_remove",
    "worktree_show",
}

RETAINED_LEAF_HELP = (
    ("new", "initiative", "--help"),
    ("new", "epic", "--help"),
    ("new", "issue", "--help"),
    ("new", "artifact", "--help"),
    ("artifact", "import", "file", "--help"),
    ("active", "set", "--help"),
    ("active", "show", "--help"),
    ("active", "clear", "--help"),
    ("issue", "start", "--help"),
    ("issue", "finish", "--help"),
    ("deps", "check", "--help"),
    ("deps", "add", "--help"),
    ("deps", "remove", "--help"),
    ("import", "initiative", "--help"),
    ("import", "epic", "--help"),
    ("import", "issue", "--help"),
    ("worktree", "create", "--help"),
    ("worktree", "list", "--help"),
    ("worktree", "show", "--help"),
    ("worktree", "remove", "--help"),
    ("workbench", "copy", "--help"),
    ("delete", "--help"),
    ("close", "--help"),
    ("update", "--help"),
    ("uninstall", "--help"),
    ("sync", "--help"),
    ("validate", "--help"),
    ("doctor", "--help"),
)


def _tree_snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative] = ("symlink", str(path.readlink()))
        elif path.is_file():
            snapshot[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_dir():
            snapshot[relative] = ("directory", "")
    return snapshot


class TestStorageCoreCli(CliRuntimeHarness):
    def test_root_help_registry_and_leaf_help_match_storage_core_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            root_help = self._run_runtime_capture(target, ["--help"])
            assert root_help.returncode == 0
            choices_match = re.search(r"\{([^}]+)\}", root_help.stdout)
            assert choices_match is not None
            assert set(choices_match.group(1).split(",")) == {
                "active",
                "artifact",
                "close",
                "delete",
                "deps",
                "doctor",
                "import",
                "issue",
                "new",
                "sync",
                "uninstall",
                "update",
                "validate",
                "workbench",
                "worktree",
            }

            for args in RETAINED_LEAF_HELP:
                result = self._run_runtime_capture(target, list(args))
                assert result.returncode == 0, (args, result.stdout, result.stderr)

            runtime_dir = target / "spec-dock" / "scripts"
            registry_result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import sys; "
                        "sys.dont_write_bytecode = True; "
                        "sys.path.insert(0, sys.argv[1]); "
                        "from spec_dock_runtime.cli.registry import build_registry; "
                        "print('\\n'.join(sorted(build_registry().items)))"
                    ),
                    str(runtime_dir),
                ],
                cwd=target,
                capture_output=True,
                text=True,
            )
            assert registry_result.returncode == 0, registry_result.stderr
            assert set(registry_result.stdout.splitlines()) == RETAINED_REGISTRY_KEYS

    def test_active_set_exposes_only_target_selectors_and_invalid_target_is_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            active_help = self._run_runtime_capture(target, ["active", "set", "--help"])
            assert active_help.returncode == 0
            for selector in ("target", "--id", "--github-issue"):
                assert selector in active_help.stdout

            for selector_args in (
                ["iss-00003"],
                ["--id", "iss-00003"],
                ["--github-issue", "3"],
            ):
                self._run_runtime(target, ["active", "clear"])
                selected = self._run_runtime_capture(target, ["active", "set", *selector_args])
                assert selected.returncode == 0, (selector_args, selected.stdout, selected.stderr)

            baseline = _tree_snapshot(target / "spec-dock")
            invalid = self._run_runtime_capture(target, ["active", "set", "missing-node"])
            assert invalid.returncode != 0
            assert "invalid target" in invalid.stderr.lower()
            assert _tree_snapshot(target / "spec-dock") == baseline

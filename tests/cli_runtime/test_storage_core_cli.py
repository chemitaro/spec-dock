from __future__ import annotations

import hashlib
import os
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

REMOVED_HELP_ROUTES = (
    ("assurance", "--help"),
    ("authoring", "--help"),
    ("guidance", "--help"),
    ("workflow", "--help"),
    ("delegated-authoring", "--help"),
    ("artifact", "import", "chatgpt-output", "--help"),
)

REMOVED_RUNTIME_MODULES = (
    "application.assurance",
    "application.delegated_authoring",
    "application.import_artifact",
    "application.issue_planning",
    "application.issue_planning_prompt",
    "application.authoring_pack",
    "chatgpt_app",
    "application.workflow",
    "commands.assurance",
    "commands.authoring",
    "commands.delegated_authoring",
    "commands.issue_planning",
    "commands.workflow",
    "domain.artifact_composer",
    "domain.assurance",
    "domain.authority",
    "domain.delegated_authoring",
    "domain.authoring_pack",
    "domain.issue_planning_candidate",
    "domain.issue_planning_contracts",
    "domain.runbook",
    "domain.workflow_state",
    "infra.artifact_store",
    "infra.assurance_store",
    "infra.issue_planning_apply",
    "infra.issue_planning_candidate",
    "infra.issue_planning_chatgpt",
    "infra.issue_planning_oracle_artifact",
    "infra.issue_planning_review",
    "infra.runbook_store",
    "infra.authoring_pack",
    "presentation.assurance_text",
    "presentation.issue_planning",
    "presentation.authoring_pack",
    "presentation.workflow",
)

RETAINED_RUNTIME_MODULES = (
    "app",
    "application.contracts",
    "application.create_artifact_doc",
    "application.create_node",
    "application.import_file_artifact",
    "application.ports",
    "application.sync_state",
    "application.validate_tree",
    "cli.bootstrap",
    "cli.dispatch",
    "cli.parser",
    "cli.registry",
    "commands.artifact_import",
    "domain.active",
    "domain.artifacts",
    "domain.deps",
    "domain.validation",
    "infra.binary_artifact_publisher",
    "infra.template_scaffolder",
    "presentation.contracts",
)

REMOVED_APPLICATION_CONTRACT_SYMBOLS = (
    "ArtifactImportError",
    "ArtifactImportRequest",
    "ArtifactImportResult",
    "AssuranceOperation",
    "AssuranceResult",
    "AssuranceResultStatus",
    "AssuranceTargetView",
    "ClassifyAssuranceRequest",
    "ComposeArtifactSelection",
    "ComposeArtifactView",
    "ComposeAssuranceRequest",
    "CreateDiscussionDocRequest",
    "CreateDiscussionDocResult",
    "RunbookProjectionResult",
    "ShowAssuranceRequest",
    "VerifyAssuranceRequest",
    "WorkflowNextRequest",
    "WorkflowResult",
    "WorkflowStatusRequest",
)

REMOVED_USE_CASE_FIELDS = (
    "classify_assurance",
    "compose_assurance",
    "import_artifact",
    "repo_root",
    "show_assurance",
    "specdock_dir",
    "verify_assurance",
    "workflow_next",
    "workflow_status",
    "planning_apply",
    "planning_create",
    "planning_review",
    "planning_revise",
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


def _runtime_python_manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.py"), key=lambda item: item.as_posix())
    }


class TestStorageCoreCli(CliRuntimeHarness):
    @staticmethod
    def _assert_removed_runtime_is_absent_retained_runtime_imports_and_projection_matches() -> None:
        repo_root = Path(__file__).resolve().parents[2]
        provider_scripts = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        dogfood_scripts = repo_root / "spec-dock" / "scripts"
        provider_runtime = provider_scripts / "spec_dock_runtime"
        dogfood_runtime = dogfood_scripts / "spec_dock_runtime"

        for runtime_root in (provider_runtime, dogfood_runtime):
            for module in REMOVED_RUNTIME_MODULES:
                assert not runtime_root.joinpath(*module.split(".")).with_suffix(".py").exists(), module

        smoke_script = "\n".join((
            "from dataclasses import fields",
            "from importlib import import_module",
            "from importlib.util import find_spec",
            "import sys",
            "sys.dont_write_bytecode = True",
            f"removed = {REMOVED_RUNTIME_MODULES!r}",
            f"retained = {RETAINED_RUNTIME_MODULES!r}",
            f"removed_contracts = {REMOVED_APPLICATION_CONTRACT_SYMBOLS!r}",
            f"removed_use_cases = {REMOVED_USE_CASE_FIELDS!r}",
            "for module in retained:",
            "    import_module('spec_dock_runtime.' + module)",
            "for module in removed:",
            "    assert find_spec('spec_dock_runtime.' + module) is None, module",
            "contracts = import_module('spec_dock_runtime.application.contracts')",
            "create_node = import_module('spec_dock_runtime.application.create_node')",
            "discussion_docs = import_module('spec_dock_runtime.domain.discussion_docs')",
            "ports = import_module('spec_dock_runtime.application.ports')",
            "for symbol in removed_contracts:",
            "    assert not hasattr(contracts, symbol), symbol",
            "assert not hasattr(create_node, 'create_discussion_doc')",
            "assert not hasattr(create_node, 'plan_discussion_doc')",
            "assert not hasattr(discussion_docs, 'CREATABLE_DISCUSSION_DOC_TYPES')",
            "assert not hasattr(discussion_docs, 'is_creatable_discussion_doc_type')",
            "use_case_fields = {field.name for field in fields(contracts.UseCases)}",
            "assert not use_case_fields.intersection(removed_use_cases)",
            "port_fields = {field.name for field in fields(ports.Ports)}",
            "assert {'explicit_file_source_guard', 'explicit_file_artifact_publisher'} <= port_fields",
            "assert hasattr(ports, 'ExplicitFileSourceGuard')",
            "assert hasattr(ports, 'ExplicitFileArtifactPublisher')",
        ))
        for scripts_root in (provider_scripts, dogfood_scripts):
            result = subprocess.run(
                [sys.executable, "-c", smoke_script],
                cwd=repo_root,
                env={**os.environ, "PYTHONPATH": str(scripts_root), "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, (scripts_root, result.stdout, result.stderr)

        assert _runtime_python_manifest(provider_runtime) == _runtime_python_manifest(dogfood_runtime)

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

    def test_removed_routes_are_parser_errors_without_tree_or_state_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            baseline = _tree_snapshot(target / "spec-dock")

            for args in REMOVED_HELP_ROUTES:
                result = self._run_runtime_capture(target, list(args))
                assert result.returncode != 0, (args, result.stdout, result.stderr)
                assert "invalid choice" in result.stderr
                assert _tree_snapshot(target / "spec-dock") == baseline

    def test_active_set_exposes_only_target_selectors_and_invalid_target_is_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            active_help = self._run_runtime_capture(target, ["active", "set", "--help"])
            assert active_help.returncode == 0
            for selector in ("target", "--id", "--github-issue"):
                assert selector in active_help.stdout
            exposed_options = set(re.findall(r"(?<!\w)-{1,2}[a-z][a-z-]*", active_help.stdout))
            assert exposed_options.isdisjoint({
                "--checkout",
                "--no-checkout",
                "--github",
                "--no-github",
                "--gh-limit",
                "--force",
                "-f",
            })

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


def test_storage_core_runtime_deletion_contract() -> None:
    TestStorageCoreCli._assert_removed_runtime_is_absent_retained_runtime_imports_and_projection_matches()

import ast
import unittest
from pathlib import Path


class TestCliTestTreeSplitS12(unittest.TestCase):
    def test_test_module_inventory_exists(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        expected = [
            repo_root / "tests" / "test_init_update.py",
            repo_root / "tests" / "cli_runtime" / "harness.py",
            repo_root / "tests" / "cli_runtime" / "test_wrappers.py",
            repo_root / "tests" / "cli_runtime" / "test_new.py",
            repo_root / "tests" / "cli_runtime" / "test_active.py",
            repo_root / "tests" / "cli_runtime" / "test_sync.py",
            repo_root / "tests" / "cli_runtime" / "test_deps.py",
            repo_root / "tests" / "cli_runtime" / "test_import.py",
            repo_root / "tests" / "cli_runtime" / "test_validate.py",
            repo_root / "tests" / "cli_runtime" / "test_runtime_validate_s02.py",
            repo_root / "tests" / "cli_runtime" / "test_runtime_deps_s04.py",
            repo_root / "tests" / "cli_runtime" / "test_runtime_active_s05.py",
            repo_root / "tests" / "cli_runtime" / "test_runtime_new_s08.py",
            repo_root / "tests" / "cli_runtime" / "test_runtime_new_doc_s09.py",
            repo_root / "tests" / "domain_runtime" / "test_runtime_domain_s01.py",
            repo_root / "tests" / "domain_runtime" / "test_runtime_domain_s03.py",
            repo_root / "tests" / "presentation_runtime" / "test_runtime_sync_s07.py",
        ]
        for path in expected:
            self.assertTrue(path.is_file(), f"missing test module: {path}")

    def test_regular_package_discovery_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        package_inits = [
            repo_root / "tests" / "__init__.py",
            repo_root / "tests" / "cli_runtime" / "__init__.py",
            repo_root / "tests" / "domain_runtime" / "__init__.py",
            repo_root / "tests" / "presentation_runtime" / "__init__.py",
        ]
        for path in package_inits:
            self.assertTrue(path.is_file(), f"missing package init: {path}")
        for path in (repo_root / "tests").rglob("test_*.py"):
            text = path.read_text(encoding="utf-8")
            module = ast.parse(text)
            has_load_tests = any(
                isinstance(node, ast.FunctionDef) and node.name == "load_tests" for node in module.body
            )
            self.assertFalse(has_load_tests, f"load_tests must not be used: {path}")

    def test_command_grouping_contains_critical_inventory(self) -> None:
        from tests.cli_runtime import (
            test_active,
            test_deps,
            test_import,
            test_new,
            test_runtime_active_s05,
            test_runtime_active_s06,
            test_runtime_deps_s04,
            test_runtime_import_s10,
            test_runtime_new_doc_s09,
            test_runtime_new_s08,
            test_runtime_shell_s11,
            test_runtime_validate_s02,
            test_sync,
            test_validate,
        )
        from tests.presentation_runtime import test_runtime_sync_s07

        groups = {
            test_active.TestCliActive: ["test_active_set_force_overrides_deps_guard"],
            test_deps.TestCliDeps: ["test_deps_check_json_stdout_only"],
            test_import.TestCliImport: ["test_import_initiative_creates_node_and_runs_sync_without_updating_active"],
            test_new.TestCliNew: ["test_new_doc_adr_increments_id_within_scope_discussions"],
            test_sync.TestCliSync: ["test_sync_emits_deps_issues_json_and_puml_todo_only"],
            test_validate.TestCliValidate: ["test_validate_detects_broken_parent_id"],
            test_runtime_shell_s11.RuntimeShellS11Tests: ["test_staged_delegation_path_regression"],
            test_runtime_active_s05.TestRuntimeActiveS05: [
                "test_show_active_reads_agent_manifest_into_active_view_result"
            ],
            test_runtime_active_s06.TestRuntimeActiveS06: ["test_set_active_patch_failure_rolls_back"],
            test_runtime_deps_s04.TestRuntimeDepsS04: ["test_check_deps_use_case_and_cycle_fail_fast"],
            test_runtime_import_s10.TestRuntimeImportS10: [
                "test_import_then_sync_artifact_path_name_content_regression"
            ],
            test_runtime_new_s08.TestRuntimeNewS08: ["test_planning_regression_create_plan_contains_all_candidates"],
            test_runtime_new_doc_s09.TestRuntimeNewDocS09: ["test_generated_path_name_content_regression"],
            test_runtime_validate_s02.TestRuntimeValidateS02: [
                "test_validate_tree_use_case_returns_result_with_checked_node_count"
            ],
            test_runtime_sync_s07.TestRuntimeSyncS07: ["test_sync_use_case_writes_artifacts_and_paths"],
        }
        for test_class, required_methods in groups.items():
            available = set(dir(test_class))
            for method_name in required_methods:
                self.assertIn(method_name, available)

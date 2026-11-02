"""Pure domain ID helpers."""

import ast
from pathlib import Path

from spec_dock.runtime.domain import ids as domain_ids


class TestRuntimeDomainS01:
    def test_domain_ids_parse_format_helpers(self) -> None:
        assert domain_ids.format_id("epic", 7) == "epic-00007"
        assert domain_ids.parse_id("EPIC-local-00007") == ("epic", True, 7)

    def test_domain_ids_deps_sort_key_helper(self) -> None:
        node_ids = ["iss-local-00002", "iss-00010", "iss-local-00001", "iss-00002"]
        assert sorted(node_ids, key=domain_ids.deps_node_sort_key) == [
            "iss-00002",
            "iss-00010",
            "iss-local-00001",
            "iss-local-00002",
        ]

    def test_domain_modules_have_no_shell_io_imports(self) -> None:
        module_paths = [domain_ids.__file__]
        forbidden_import_roots = {
            "argparse",
            "json",
            "os",
            "shutil",
            "subprocess",
            "sys",
        }

        for module_path in module_paths:
            source = Path(module_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported_roots: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_roots.add(alias.name.split(".", 1)[0])
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported_roots.add(node.module.split(".", 1)[0])

            assert imported_roots.isdisjoint(forbidden_import_roots), (
                f"forbidden import detected in {module_path}: {sorted(imported_roots & forbidden_import_roots)}"
            )

from pathlib import Path


class TestUnitDiscoverySmoke:
    def test_unit_package_markers_exist(self) -> None:
        tests_root = Path(__file__).resolve().parents[1]

        for relative_path in (
            "unit",
            "unit/application",
            "unit/cli",
            "unit/commands",
            "unit/domain",
            "unit/infra",
            "unit/presentation",
        ):
            marker = tests_root / relative_path / "__init__.py"
            assert marker.is_file(), f"missing package marker: {relative_path}"

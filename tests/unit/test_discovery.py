from pathlib import Path
import unittest


class UnitDiscoverySmokeTest(unittest.TestCase):
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
            with self.subTest(path=relative_path):
                self.assertTrue(marker.is_file())


if __name__ == "__main__":
    unittest.main()

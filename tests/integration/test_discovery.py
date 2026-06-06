from pathlib import Path
import unittest


class IntegrationDiscoverySmokeTest(unittest.TestCase):
    def test_integration_package_markers_exist(self) -> None:
        tests_root = Path(__file__).resolve().parents[1]

        for relative_path in (
            "integration",
            "integration/git_remote",
            "integration/github",
        ):
            marker = tests_root / relative_path / "__init__.py"
            with self.subTest(path=relative_path):
                self.assertTrue(marker.is_file())


if __name__ == "__main__":
    unittest.main()

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "relative_path",
    (
        "integration",
        "integration/git_remote",
        "integration/github",
    ),
)
class TestIntegrationDiscoverySmoke:
    def test_integration_package_markers_exist(self, relative_path: str) -> None:
        tests_root = Path(__file__).resolve().parents[1]
        marker = tests_root / relative_path / "__init__.py"
        assert marker.is_file(), f"missing package marker for path={relative_path}"

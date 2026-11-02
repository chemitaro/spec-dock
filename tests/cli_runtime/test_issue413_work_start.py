"""Legacy schema-3 Start fixtures kept for other modules (iss-00440).

Its tests moved to tests/cli_runtime/test_issue440_g1_work_start.py and test_issue440_g1_cli_parsing.py.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tests.cli_runtime.test_issue413_contract import make_workspace

if TYPE_CHECKING:
    from pathlib import Path


# TODO(iss-00440): remove after all groups migrate
def committed_workspace(root: Path) -> Path:
    make_workspace(root)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    return root


# TODO(iss-00440): remove after all groups migrate
def open_issue(root: Path, repository: str, number: int) -> object:
    # The record type left with the legacy REST gateway in 0.5.0; importing it here keeps this module collectable.
    from spec_dock.runtime.infra.contracts import GithubIssueRecord  # type: ignore[import-not-found]

    return GithubIssueRecord(
        number,
        repository,
        "Fixture",
        "open",
        "open",
        None,
        "2026-09-30T00:00:00Z",
        f"https://github.com/{repository}/issues/{number}",
    )

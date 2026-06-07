import json
import os
import pytest
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.domain.models import SpecGraph, SpecNode
from spec_dock_runtime.domain.status import resolve_issue_statuses
from spec_dock_runtime.infra.github_cli import issue_index, issue_index_raw


class TestFakeGhHarness(CliRuntimeHarness):
    def setup_method(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

    def _issue_node(self, issue_id: str, number: int) -> SpecNode:
        return SpecNode(
            kind="issue",
            id=issue_id,
            title=issue_id,
            slug=issue_id,
            path=Path(issue_id),
            meta_path=Path(issue_id) / ".meta.json",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=number,
            github_repo_owner="example",
            github_repo_name="repo",
        )

    def test_default_fake_gh_issue_list_returns_small_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / ".bin"
            bin_dir.mkdir()
            self._make_default_gh_issue_list_stub(bin_dir)

            p = subprocess.run(
                [
                    str(bin_dir / "gh"),
                    "issue",
                    "list",
                    "--state",
                    "all",
                    "--limit",
                    "10000",
                    "--json",
                    "number,state,title,labels,updatedAt,url",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        issues = json.loads(p.stdout)
        assert len(issues) <= 3
        assert len(issues) != 10000

    def test_issue_index_raw_captures_large_limit_argv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / ".bin"
            bin_dir.mkdir()
            log_path = root / ".gh.log"
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[{"number": 1, "state": "OPEN", "title": "One", "labels": [], "updatedAt": "t"}],
                log_path=log_path,
            )

            with pytest.MonkeyPatch.context() as monkeypatch:
                monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
                issue_index_raw(root, limit=10000)

            argv = log_path.read_text(encoding="utf-8").split()

        assert "--limit" in argv
        assert argv[argv.index("--limit") + 1] == "10000"

    def test_large_issue_number_uses_minimal_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / ".bin"
            bin_dir.mkdir()
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {
                        "number": 10000,
                        "state": "OPEN",
                        "title": "Large issue number",
                        "labels": [],
                        "updatedAt": "2026-05-13T00:00:00Z",
                    }
                ],
            )

            with pytest.MonkeyPatch.context() as monkeypatch:
                monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
                snapshots = issue_index(root, limit=10000)

        assert len(snapshots) == 1
        assert snapshots[0].issue_number == 10000

    def test_state_variations_use_minimal_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / ".bin"
            bin_dir.mkdir()
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Open", "labels": [], "updatedAt": "t"},
                    {"number": 102, "state": "CLOSED", "title": "Closed", "labels": [], "updatedAt": "t"},
                    {"number": 103, "state": "UNKNOWN", "title": "Unknown", "labels": [], "updatedAt": "t"},
                ],
            )

            with pytest.MonkeyPatch.context() as monkeypatch:
                monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
                snapshots = issue_index(root, limit=10000)

        assert len(snapshots) == 3
        assert [snapshot.issue_number for snapshot in snapshots] == [101, 102, 103]

        graph = SpecGraph(
            nodes_by_id={
                "iss-00101": self._issue_node("iss-00101", 101),
                "iss-00102": self._issue_node("iss-00102", 102),
                "iss-00103": self._issue_node("iss-00103", 103),
                "iss-00104": self._issue_node("iss-00104", 104),
            }
        )
        statuses = resolve_issue_statuses(
            graph,
            github_enabled=True,
            issue_snapshots=snapshots,
            cached_issue_status_by_id={},
            current_repo_slug="example/repo",
        )

        assert statuses["iss-00101"].effective_status == "open"
        assert statuses["iss-00102"].effective_status == "done"
        assert statuses["iss-00103"].source == "github"
        assert statuses["iss-00103"].effective_status == "open"
        assert statuses["iss-00104"].source == "unknown"
        assert statuses["iss-00104"].effective_status == "unknown"

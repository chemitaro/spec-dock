"""Import CLI binds a fixed GitHub Issue and recovers local scaffold writes."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli import vnext_runtime  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue, _ready_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_scope_import_cli_previews_and_creates_without_post(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    prefix = ("scope", "import", "github", "initiative", "gh:example/repo#47", "--title", "Local plan")
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert gateway.calls == 0
    imported = _run(repo, *prefix)
    assert imported.exit_code == 0
    payload = json.loads(imported.stdout)
    assert payload["data"]["scope_id"] == "init-00047"
    assert gateway.calls == 0


def test_scope_import_cli_resumes_after_local_collision(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    destination = repo / "spec-dock/initiatives/init-00047-plan"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("occupied\n", encoding="utf-8")
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    prefix = ("scope", "import", "github", "initiative", "gh:example/repo#47", "--title", "Plan")
    first = _run(repo, *prefix)
    assert first.exit_code == 6
    operation = JournalStore(cast("Path", common["common_dir"])).pending()[0]
    destination.unlink()
    resumed = _run(repo, *prefix, "--resume", operation.operation_id)
    assert resumed.exit_code == 0
    assert json.loads(resumed.stdout)["operation_id"] == operation.operation_id
    assert gateway.calls == 0


def test_scope_import_cli_requires_source_reference(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    result = _run(repo, "scope", "import", "github", "initiative", "--title", "Plan")
    assert result.exit_code == 2

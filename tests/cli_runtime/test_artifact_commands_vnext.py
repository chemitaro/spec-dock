"""Artifact mutation leaves expose catalog identities without leaking source data."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.cli import vnext_runtime  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_artifact_list_show_cli_return_only_catalog_metadata(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    catalog = repo / "spec-dock" / "artifacts"
    catalog.mkdir(exist_ok=True)
    (catalog / "20260925t000000z--source.bin").write_bytes(b"secret payload")
    listed = _run(repo, "artifact", "list", "--scope", "@root")
    assert listed.exit_code == 0
    payload = json.loads(listed.stdout)
    assert payload["data"]["scope_id"] == "root"
    artifact_id = payload["data"]["items"][0]["artifact_id"]
    assert "secret payload" not in listed.stdout
    shown = _run(repo, "artifact", "show", artifact_id, "--scope", "@root")
    assert shown.exit_code == 0
    assert json.loads(shown.stdout)["data"]["artifact_id"] == artifact_id
    assert "secret payload" not in shown.stdout


def test_artifact_create_cli_previews_then_publishes_under_local_scope(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    initiative = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    prefix = ("artifact", "create", "--scope", initiative.id, "--type", "research", "--title", "Evidence")
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["data"]["scope_id"] == initiative.id
    assert not tuple((initiative.path / "artifacts").glob("*research*"))
    created = _run(repo, *prefix)
    assert created.exit_code == 0
    payload = json.loads(created.stdout)
    assert payload["data"]["creation_type"] == "research"
    assert payload["data"]["scope_id"] == initiative.id
    invalid = _run(repo, "artifact", "create", "--scope", "@root", "--type", "research", "--title", "Wrong")
    assert invalid.exit_code == 3


def test_artifact_post_publication_io_failure_reports_unknown_local_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    initiative = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    original = vnext_runtime.run_artifact_change

    def publish_then_fail(*args: object, **kwargs: object) -> None:
        original(*args, **kwargs)
        raise OSError("injected after Artifact publication")

    monkeypatch.setattr(vnext_runtime, "run_artifact_change", publish_then_fail)
    failed = _run(repo, "artifact", "create", "--scope", initiative.id, "--type", "research", "--title", "Evidence")
    payload = json.loads(failed.stdout)
    assert failed.exit_code == 6
    assert payload["status"] == "partial"
    assert payload["target"]["id"] == initiative.id
    assert payload["effects"] == [{"kind": "artifact-create", "status": "unknown", "target": initiative.id}]
    assert payload["recovery"]["can_resume"] is False
    assert payload["recovery"]["can_rollback"] is False
    assert tuple((initiative.path / "artifacts").glob("*research*"))


def test_artifact_import_cli_keeps_external_file_private(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    source = tmp_path / "private-source.bin"
    source.write_bytes(b"secret payload")
    prefix = ("artifact", "import", "file", str(source), "--scope", "@root")
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    assert str(source) not in preview.stdout
    imported = _run(repo, *prefix)
    assert imported.exit_code == 0
    payload = json.loads(imported.stdout)
    assert payload["data"]["scope_id"] == "root"
    assert str(source) not in imported.stdout
    assert "secret payload" not in imported.stdout
    assert source.read_bytes() == b"secret payload"

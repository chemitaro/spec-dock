"""Dependency queries expose declared edges and readiness through the vNext CLI."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.dependency_vnext import mutate_scope_dependency  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_dependency_vnext import _two_trees  # noqa: E402


def test_dependency_list_and_check_cli_use_same_scope_graph(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    repo = cast("Path", common["repo_root"])
    mutate_scope_dependency(
        from_target=left[1].id,
        to_target=right[0].id,
        action="add",
        **{key: value for key, value in common.items() if key != "updated_at"},
    )
    listed = run_vnext(
        ["dependency", "list", left[2].id, "--view", "effective", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert listed.exit_code == 0
    edges = json.loads(listed.stdout)["data"]["edges"]
    assert [(edge["target_id"], edge["declared_by"]) for edge in edges] == [(right[0].id, left[1].id)]
    checked = run_vnext(
        ["dependency", "check", left[2].id, "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert checked.exit_code == 0
    assert json.loads(checked.stdout)["data"]["ready"] is False


def test_dependency_change_cli_previews_and_applies_one_edge(tmp_path: Path) -> None:
    common, left, right = _two_trees(tmp_path)
    repo = cast("Path", common["repo_root"])
    metadata = left[1].path / ".meta.json"
    original = metadata.read_bytes()
    command = ["dependency", "add", "--from", left[1].id, "--to", right[0].id, "--json"]
    preview = run_vnext([*command, "--dry-run"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert metadata.read_bytes() == original

    added = run_vnext(command, invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert added.exit_code == 0
    payload = json.loads(added.stdout)
    assert payload["data"] == {"from_id": left[1].id, "to_id": right[0].id, "revision": 1, "changed": True}
    assert json.loads(metadata.read_text())["depends_on"] == [right[0].id]

    duplicate = run_vnext(command, invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert json.loads(duplicate.stdout)["status"] == "unchanged"
    remove = ["dependency", "remove", "--from", left[1].id, "--to", right[0].id, "--json"]
    removed = run_vnext(remove, invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert removed.exit_code == 0
    assert json.loads(removed.stdout)["status"] == "succeeded"
    assert json.loads(metadata.read_text())["depends_on"] == []
    missing = run_vnext(remove, invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")
    assert missing.exit_code == 4
    missing_ok = run_vnext(
        [*remove, "--missing-ok"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4"
    )
    assert json.loads(missing_ok.stdout)["status"] == "unchanged"

"""Scope list/show are stable, cache-aware, and read-only."""

from __future__ import annotations

import json
from pathlib import Path
import stat
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.application.edit_scope import edit_scope_title  # noqa: E402
from spec_dock_runtime.application.scope_query import list_scopes, load_scope_views, show_scope  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_scope_query_filters_local_and_cached_github_without_network_or_write(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    local = create_local_scope(kind="initiative", title="Local", parent=None, ancestors=(), **common)
    repo = cast("Path", common["repo_root"])
    specdock_dir = repo / "spec-dock"
    before_meta = (local.path / ".meta.json").read_bytes()
    views = load_scope_views(specdock_dir)
    result = list_scopes(views, kind="initiative")
    assert [item.id for item in result.items] == [local.id]
    assert result.items[0].status.state == "open"
    assert result.items[0].status.source == "local"
    assert list_scopes(views, kind="issue").items == ()
    assert show_scope(views, local.id).id == local.id
    selection = SelectionState("main", 0, local.id, None, None, local.id)
    assert show_scope(views, "@current", selection=selection).id == local.id
    assert (local.path / ".meta.json").read_bytes() == before_meta


def test_scope_query_keeps_github_status_source_and_stale_flag(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    specdock_dir = repo / "spec-dock"
    from spec_dock_runtime.application.import_github_scope import import_github_scope
    from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue

    imported = import_github_scope(
        kind="initiative",
        github_ref="gh:example/repo#47",
        repo_hint=None,
        title="Imported",
        parent_id=None,
        slug=None,
        gateway=FakeGateway(_issue()),
        **common,
    )
    cache_path = specdock_dir / ".agent" / "github-status-cache.json"
    atomic_write_json(
        cache_path,
        {
            "schema_version": 1,
            "items": {
                imported.id: {
                    "github_ref": imported.github_ref,
                    "state": "completed",
                    "observed_at": "2026-09-25T00:00:00Z",
                }
            },
        },
    )
    views = load_scope_views(specdock_dir)
    item = show_scope(views, imported.id)
    assert item.status.state == "completed"
    assert item.status.source == "cache"
    assert item.status.stale
    assert [scope.id for scope in list_scopes(views, state="completed").items] == [imported.id]


def test_scope_title_edit_preserves_slug_backend_and_read_only_mode(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    local = create_local_scope(kind="initiative", title="Original", parent=None, ancestors=(), **common)
    meta_path = local.path / ".meta.json"
    before = json.loads(meta_path.read_text(encoding="utf-8"))
    before["custom_note"] = {"owner": "test", "priority": 4}
    loaded = read_guarded_json(meta_path)
    assert loaded is not None
    atomic_write_json(meta_path, before, expected_identity=loaded[1])
    before_mode = stat.S_IMODE(meta_path.stat().st_mode)
    document_bytes = {path.name: path.read_bytes() for path in local.path.glob("*.md")}
    result = edit_scope_title(
        target_id=local.id, title="Revised", **{key: value for key, value in common.items() if key != "updated_at"}
    )
    after = json.loads(meta_path.read_text(encoding="utf-8"))
    assert result.changed
    assert after["title"] == "Revised"
    assert after["revision"] == before["revision"] + 1
    assert {key: value for key, value in after.items() if key not in ("title", "revision")} == {
        key: value for key, value in before.items() if key not in ("title", "revision")
    }
    assert stat.S_IMODE(meta_path.stat().st_mode) == before_mode
    assert {path.name: path.read_bytes() for path in local.path.glob("*.md")} == document_bytes
    same = edit_scope_title(
        target_id=local.id, title="Revised", **{key: value for key, value in common.items() if key != "updated_at"}
    )
    assert not same.changed
    assert json.loads(meta_path.read_text(encoding="utf-8")) == after

"""The Markdown and PlantUML dashboard is gone (iss-00533, epic-00427 R-23 and D-10).

The periodic sync writes none of the five files, `canonical status` has no `dashboard` item, `canonical remove`
leaves the five files alone, and an old `dashboard` field of state.json is ignored.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.infra.canonical_state import catalog_state_dir, read_catalog_state
from tests.support.canonical_sync import SyncPair

if TYPE_CHECKING:
    from tests.support.fake_github import FakeGithub

ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD = ROOT / "src/spec_dock/assets/spec_dock"
FIVE = ("dashboard.md", "tree.puml", "tree-all.puml", "deps-issues.puml", "deps-raw.puml")
STATUS_ITEMS = {
    "catalog",
    "link",
    "exclude",
    "access",
    "tools",
    "sync",
    "changes",
    "format",
    "git",
    "snapshot",
    "structure",
    "kind",
}


def _fake_structure(monkeypatch: pytest.MonkeyPatch) -> FakeGithub:
    from spec_dock.runtime.application import canonical_sync
    from spec_dock.runtime.infra.github_snapshot import clear_memory
    from spec_dock.runtime.infra.github_structure import GithubApi
    from tests.support.fake_github import FakeGithub

    fake = FakeGithub("example/repo")
    initiative = fake.scope("initiative", title="仕様の正本")
    epic = fake.scope("epic", title="ダッシュボード", parent=initiative.number)
    fake.scope("issue", title="着手できる", parent=epic.number)
    clear_memory()
    monkeypatch.setattr(canonical_sync, "repository_of", lambda *_a, **_k: "github.com/example/repo")
    monkeypatch.setattr(canonical_sync, "github_api_for", lambda cwd: GithubApi(runner=fake, clock=fake.clock))
    return fake


@pytest.fixture
def pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> SyncPair:
    return SyncPair.create(tmp_path, monkeypatch, capsys)


def _directory(checkout: Path) -> Path:
    return checkout / "spec-dock"


def _plant_old_files(checkout: Path) -> dict[str, tuple[int, str]]:
    """The five files as a previous version left them; returns their mtime and text."""
    for name in FIVE:
        (_directory(checkout) / name).write_text(f"old {name}\n", encoding="utf-8")
    return _stamps(checkout)


def _stamps(checkout: Path) -> dict[str, tuple[int, str]]:
    return {
        name: ((_directory(checkout) / name).stat().st_mtime_ns, (_directory(checkout) / name).read_text("utf-8"))
        for name in FIVE
        if (_directory(checkout) / name).is_file()
    }


def _state_file(pair: SyncPair, checkout: Path) -> Path:
    return catalog_state_dir(pair.state_root, os.path.realpath(pair.catalog(checkout))) / "state.json"


def _put_old_dashboard_field(pair: SyncPair, checkout: Path, value: object) -> None:
    path = _state_file(pair, checkout)
    payload = json.loads(path.read_text("utf-8"))
    payload["dashboard"] = value
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_a_cycle_writes_none_of_the_five_files_and_reports_zero(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    """T-01 (R-01)."""
    _fake_structure(monkeypatch)
    for _ in range(2):
        code, result = pair.sync(pair.a)
        assert code == 0, result
        (repository,) = result["data"]["repositories"]
        assert repository["dashboards_written"] == 0 and repository["probe"] in ("changed", "unchanged")
        pair.advance(61)
    assert _stamps(pair.a) == {}
    assert (pair.state_root / "github/github.com/example/repo/snapshot.json").is_file()


def test_a_cycle_leaves_the_files_a_previous_version_wrote(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    """T-02 (R-01, F-02)."""
    _fake_structure(monkeypatch)
    before = _plant_old_files(pair.a)
    code, result = pair.sync(pair.a)
    assert code == 0, result
    assert _stamps(pair.a) == before


def test_status_has_no_dashboard_item_even_with_an_old_recorded_error(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T-03 (R-02)."""
    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    error = {"code": "CANONICAL_DASHBOARD_OCCUPIED", "message": "occupied", "paths": ["/x"]}
    _put_old_dashboard_field(pair, pair.a, {"input_hash": "0" * 64, "written_at": None, "error": error})
    code, result = pair.run(pair.a, "canonical", "status")
    assert code == 0, result
    assert set(result["data"]) == STATUS_ITEMS
    assert not [item for item in result["warnings"] if item["code"].startswith("CANONICAL_DASHBOARD")]


def test_remove_neither_plans_nor_deletes_the_five_files(pair: SyncPair, monkeypatch: pytest.MonkeyPatch) -> None:
    """T-04 (R-03, F-02)."""
    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    before = _plant_old_files(pair.a)
    code, result = pair.run(pair.a, "canonical", "remove")
    assert code == 0 and result["status"] == "planned", result
    assert not [item for item in result["effects"] if "dashboard" in item["kind"]]
    code, result = pair.run(pair.a, "canonical", "remove", "--yes")
    assert code == 0, result
    assert not [item for item in result["effects"] if "dashboard" in item["kind"]]
    assert _stamps(pair.a) == before


@pytest.mark.parametrize("value", ["broken", ["not", "an", "object"], {"input_hash": "0" * 64}])
def test_an_old_dashboard_field_is_ignored_and_dropped(
    pair: SyncPair, monkeypatch: pytest.MonkeyPatch, value: object
) -> None:
    """T-05 (F-01)."""
    _fake_structure(monkeypatch)
    pair.sync(pair.a)
    _put_old_dashboard_field(pair, pair.a, value)
    catalog = os.path.realpath(pair.catalog(pair.a))
    assert read_catalog_state(pair.state_root, catalog) is not None
    pair.advance(61)
    code, result = pair.sync(pair.a)
    assert code == 0, result
    assert "dashboard" not in json.loads(_state_file(pair, pair.a).read_text("utf-8"))


@pytest.mark.parametrize(
    "module",
    [
        "spec_dock.runtime.application.canonical_dashboard",
        "spec_dock.runtime.domain.canonical_dashboard",
        "spec_dock.runtime.presentation.markdown",
        "spec_dock.runtime.presentation.puml",
    ],
)
def test_the_generation_modules_are_gone(module: str) -> None:
    """T-06 (R-04)."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module)


def test_no_generation_name_is_left_in_the_runtime_or_the_shipped_ignore() -> None:
    """T-06 (R-04). Shipped documents are checked by T-07; #534 names the five files in migration.md."""
    names = ("_refresh_dashboards", "CANONICAL_DASHBOARD_", "dashboard_item", "canonical.dashboard.remove", *FIVE)
    pattern = re.compile("|".join(re.escape(name) for name in names))
    sources = [*(ROOT / "src/spec_dock/runtime").rglob("*.py"), ROOT / "src/spec_dock/asset_layout.py"]
    sources.append(SCAFFOLD / ".gitignore")
    found = [
        f"{path.relative_to(ROOT)}:{number}"
        for path in sources
        for number, line in enumerate(path.read_text("utf-8").splitlines(), 1)
        if pattern.search(line)
    ]
    assert found == []


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_the_shipped_assets_documents_and_help_match_the_removal() -> None:
    """T-07 (R-05)."""
    from spec_dock.runtime.cli.catalog import HELP_SPECS

    def leaf_help_text(leaf: str) -> str:
        return " ".join(str(value) for value in vars(HELP_SPECS[leaf]).values())

    inventory = json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text("utf-8"))
    rows = {row["path"]: row for row in inventory["files"]}
    for relative in (".gitignore", "docs/canonical.md"):
        provider = SCAFFOLD / relative
        row = rows[f"spec-dock/{relative}"]
        assert row["sha256"] == _sha(provider), relative
        assert (ROOT / "spec-dock" / relative).read_bytes() == provider.read_bytes(), relative
    canonical = (SCAFFOLD / "docs/canonical.md").read_text("utf-8")
    for word in (*FIVE, "CANONICAL_DASHBOARD", "`dashboard`"):
        assert word not in canonical, word
    for leaf in ("canonical status", "canonical sync", "canonical remove"):
        text = leaf_help_text(leaf)
        assert "dashboard files" not in text and "five dashboard" not in text, leaf
    assert ", dashboard," not in leaf_help_text("canonical status")
    assert "dashboards_written (always 0" in leaf_help_text("canonical sync")


# The 0.5.x provider assets (the inventory rows before iss-00533); `known_old_sha256` must recognize them.
PREVIOUS_SHA = {
    ".gitignore": "c9323d364063c4fd8db1b724a2994d0310976208dd5c1a236294f81f9ece9bcb",
    "docs/canonical.md": "5af6ae7a2fd4e9bac3269f2184fcf7013591f5cba616c0ef44302e8c361a0751",
}


@pytest.mark.parametrize("relative", [".gitignore", "docs/canonical.md"])
def test_the_previous_asset_is_a_known_old_version(relative: str) -> None:
    """T-07 (R-05): `installation update` recognizes 0.5.x's file and replaces it."""
    inventory: Any = json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text("utf-8"))
    (row,) = [row for row in inventory["files"] if row["path"] == f"spec-dock/{relative}"]
    assert PREVIOUS_SHA[relative] in row["known_old_sha256"]

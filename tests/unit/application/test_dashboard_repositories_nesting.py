"""The repository list returns each repository's nesting without paths (iss-00613 T-06)."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application import dashboard_site
from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request
from spec_dock.runtime.application.dashboard_nesting import Nesting
from spec_dock.runtime.application.dashboard_site import DashboardSite
from spec_dock.runtime.domain.canonical_sync_state import RegistryEntry, SyncRegistry
from spec_dock.runtime.infra.canonical_registry import read_registry, write_registry_locked
from spec_dock.runtime.infra.dashboard_store import hide_repository, show_repository
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.canonical_repo import isolate_user_state
from tests.support.dashboard import NOW

if TYPE_CHECKING:
    from pathlib import Path

HOST = "127.0.0.1:47800"
FIELDS = ["repository", "host", "owner", "name", "path", "api", "problem"]

CO, HL, TK = "github.com/o/company-os", "github.com/o/housing-lifecycle", "github.com/o/taikyohiyou_project"
ID, GM, TC, YB = (
    "github.com/o/input-devices",
    "github.com/o/generic-mona",
    "github.com/o/tenting-cradle",
    "github.com/o/yubisaki",
)
SD, OW, DUP, IN = "github.com/o/spec-dock", "github.com/o/orca-web", "github.com/o/dup", "github.com/o/inner"
UN_CHILD = "github.com/o/under-unknown"


def add_row(state: Path, repository: str | None, checkout: Path) -> Path:
    """Register a catalog whose main checkout is `checkout` (the shared helper registers the catalog's parent)."""
    catalog = checkout / "spec-dock" / ".canonical"
    catalog.mkdir(parents=True, exist_ok=True)
    try:
        current = read_registry(state)
    except Exception:
        current = SyncRegistry(None, ())
    entry = RegistryEntry(str(catalog), str(checkout), repository, str(checkout / ".git"), "2026-11-01T00:00:00Z")
    write_registry_locked(state, current.with_entry(entry))
    return catalog


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.tmp = tmp_path
        self.state = tmp_path / "state"
        ws = tmp_path / "ws"
        co = ws / "company-os"
        self.rows = {
            CO: co,
            HL: co / "businesses" / "housing-lifecycle",
            TK: co / "businesses" / "housing-lifecycle" / "products" / "taikyohiyou_project",
            ID: co / "businesses" / "input-devices",
            GM: co / "businesses" / "input-devices" / "products" / "generic-mona",
            TC: co / "businesses" / "input-devices" / "products" / "tenting-cradle",
            YB: co / "businesses" / "input-devices" / "products" / "yubisaki",
            SD: ws / "tools" / "spec-dock",
            OW: ws / "tools" / "orca-web",
            IN: co / "businesses" / "dup-a" / "products" / "inner",
            UN_CHILD: co / "services" / "unknown" / "groups" / "child",
        }
        self.catalogs = [add_row(self.state, key, checkout) for key, checkout in self.rows.items()]
        # Two clones of one repository (ambiguous) and a row whose repository is unknown.
        self.catalogs.append(add_row(self.state, DUP, co / "businesses" / "dup-a"))
        self.catalogs.append(add_row(self.state, DUP, ws / "elsewhere" / "dup-b"))
        self.catalogs.append(add_row(self.state, None, co / "services" / "unknown"))
        self.site = DashboardSite(self.state, now=lambda: NOW, user_config=tmp_path / "home" / "config.json")
        self.http = DashboardHttp(
            self.site,
            hosts=("127.0.0.1",),
            port=47800,
            embed_hosts=("127.0.0.1",),
            local_url="http://127.0.0.1:47800/",
            version="0.9.4",
            started_at="2026-11-04T11:00:00Z",
            now=lambda: NOW,
        )

    def raw(self) -> str:
        response = self.http.handle(Request("GET", "/api/v1/repositories", {}, {"host": HOST}))
        assert response.status == 200
        return response.body.decode() if isinstance(response.body, bytes) else str(response.body)

    def body(self) -> dict[str, Any]:
        loaded: dict[str, Any] = json.loads(self.raw())
        return loaded

    def nesting(self) -> dict[str, tuple[str | None, list[str]]]:
        return {item["repository"]: (item["parent"], item["tier"]) for item in self.body()["repositories"]}


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    isolate_user_state(monkeypatch, tmp_path)
    return Env(tmp_path)


def test_the_list_adds_parent_and_tier_after_the_current_fields(env: Env) -> None:
    hide_repository(env.state, GithubRepository("o", "housing-lifecycle"), now=NOW)
    body = env.body()
    assert body["schema"] == "specdock.dashboard/v1"
    items = body["repositories"]
    keys = [item["repository"] for item in items]
    assert keys == sorted({*env.rows, DUP} - {HL})  # the order (by key) is the current one; the hidden one is out
    for item in items:
        assert list(item) == [*FIELDS, "parent", "tier"]
        host, owner, name = item["repository"].split("/")
        assert [item[field] for field in FIELDS] == [
            item["repository"],
            host,
            owner,
            name,
            f"/r/{item['repository']}/",
            f"/api/v1/r/{item['repository']}/",
            "ambiguous" if item["repository"] == DUP else None,
        ]
        assert item["parent"] is None or item["parent"] in keys
    assert body["unknown_count"] == 1
    assert env.nesting() == {
        CO: (None, []),
        SD: (None, []),
        OW: (None, []),
        DUP: (None, []),  # two clones: at the top (F-02)
        TK: (CO, ["プロダクト"]),  # inside the hidden one: the outer shown ancestor, no hidden names (F-03)
        ID: (CO, ["事業"]),
        GM: (ID, ["プロダクト"]),
        TC: (ID, ["プロダクト"]),
        YB: (ID, ["プロダクト"]),
        IN: (CO, ["プロダクト"]),  # inside a clone: counted from the clone's checkout
        UN_CHILD: (CO, ["groups"]),  # inside an unknown row: counted from that row
    }


def test_the_response_carries_no_path(env: Env) -> None:
    hide_repository(env.state, GithubRepository("o", "housing-lifecycle"), now=NOW)
    raw = env.raw()
    needles = {str(env.tmp), os.path.realpath(env.tmp), "/ws/", "company-os/businesses", ".canonical"}
    for checkout in env.rows.values():
        needles.update({str(checkout), os.path.realpath(checkout)})
    needles.update(str(catalog) for catalog in env.catalogs)
    for entry in env.site.registry_entries():
        needles.update({entry.catalog, entry.main_checkout, entry.git})
    for needle in needles:
        assert needle not in raw, needle
        assert json.dumps(needle)[1:-1] not in raw, needle


def test_changing_the_marks_changes_the_nesting_on_the_next_request(env: Env) -> None:
    assert env.nesting()[TK] == (HL, ["プロダクト"])
    assert env.nesting()[HL] == (CO, ["事業"])
    hide_repository(env.state, GithubRepository("o", "housing-lifecycle"), now=NOW)
    assert env.nesting()[TK] == (CO, ["プロダクト"])
    hide_repository(env.state, GithubRepository("o", "company-os"), now=NOW)
    nesting = env.nesting()
    assert nesting[TK] == (None, []) and nesting[ID] == (None, []) and nesting[GM] == (ID, ["プロダクト"])
    show_repository(env.state, GithubRepository("o", "housing-lifecycle"))
    show_repository(env.state, GithubRepository("o", "company-os"))
    assert env.nesting()[TK] == (HL, ["プロダクト"])


def test_a_repository_hidden_by_its_settings_parents_nothing(env: Env) -> None:
    catalog = env.rows[ID] / "spec-dock" / ".canonical"
    (catalog / "dashboard.json").write_text(json.dumps({"schema": "specdock.dashboard-settings/v1", "visible": False}))
    nesting = env.nesting()
    assert ID not in nesting
    assert nesting[GM] == (CO, ["プロダクト"])


def test_the_site_pairs_each_listed_repository_with_its_nesting(env: Env) -> None:
    pairs = env.site.nested_repositories()
    assert [site.key for site, _nesting in pairs] == [site.key for site in env.site.repositories()]
    assert {site.key: nesting for site, nesting in pairs}[TK] == Nesting(HL, ("プロダクト",))


def test_paths_are_resolved_once_per_listing_read(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    real = os.path.realpath

    def counting(path: Any, *args: Any, **kwargs: Any) -> str:
        calls.append(str(path))
        return real(path, *args, **kwargs)

    monkeypatch.setattr(dashboard_site.os.path, "realpath", counting)
    env.body()
    first = len(calls)
    assert first > 0
    env.body()
    env.site.nested_repositories()
    assert len(calls) == first


def test_a_main_checkout_that_is_not_absolute_is_at_the_top(env: Env) -> None:
    current = read_registry(env.state)
    entries = tuple(
        RegistryEntry(entry.catalog, "", entry.repository, entry.git, entry.registered_at)
        if entry.repository == ID
        else entry
        for entry in current.catalogs
    )
    write_registry_locked(env.state, SyncRegistry(current.scheduler, entries))
    nesting = env.nesting()
    assert nesting[ID] == (None, [])
    assert nesting[GM] == (CO, ["事業", "input-devices", "プロダクト"])

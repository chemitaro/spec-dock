"""orca-web settings and HTTP integration (iss-00591 T-02, T-03)."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from spec_dock.runtime.application.dashboard_http import DashboardHttp, Request, Response
from spec_dock.runtime.application.dashboard_site import DashboardSite
from tests.support.dashboard import NOW
from tests.support.dashboard_site import register, sample, scope_dir, write_snapshot

REPOSITORY = "github.com/o/r"


def write_config(path: Path, section: object, *, raw: bytes | None = None) -> None:
    before = path.stat().st_mtime_ns if path.exists() else 0
    path.write_bytes(
        raw if raw is not None else json.dumps({"schema": "specdock.config/v1", "orca_web": section}).encode()
    )
    stamp = max(before + 1_000_000, path.stat().st_mtime_ns)
    os.utime(path, ns=(stamp, stamp))


def environment(tmp_path: Path) -> tuple[DashboardSite, Path, Path]:
    state, catalog, config = tmp_path / "state", tmp_path / "main" / "catalog", tmp_path / "config.json"
    register(state, REPOSITORY, catalog)
    write_snapshot(state, sample())
    return DashboardSite(state, now=lambda: NOW, user_config=config), config, catalog


def http_for(site: DashboardSite) -> DashboardHttp:
    return DashboardHttp(
        site,
        hosts=("127.0.0.1", "localhost", "192.0.2.10"),
        port=47800,
        embed_hosts=("127.0.0.1",),
        local_url="http://127.0.0.1:47800/",
        version="0.5.1",
        started_at="2026-11-04T11:00:00Z",
        now=lambda: NOW,
    )


def get(http: DashboardHttp, path: str, host: str = "127.0.0.1:47800", *, embed: bool = False) -> Response:
    return http.handle(Request("GET", path, {"embed": ["1"]} if embed else {}, {"host": host}))


def test_settings_reload_without_changing_visibility_or_duplicating_problems(tmp_path: Path) -> None:
    site, config, _catalog = environment(tmp_path)
    assert site.orca_web().enabled and site.orca_web().port == 8791
    shown = [item.key for item in site.repositories()]
    visibility = site.visibility(REPOSITORY).to_json()
    write_config(config, {"enabled": False, "port": 9001})
    assert not site.orca_web().enabled and site.orca_web().port == 9001
    write_config(config, {"port": 0})
    assert not site.orca_web().enabled
    (problem,) = site.config_problems()
    assert (problem.layer, problem.path) == ("user", str(config))
    assert "orca_web.port" in problem.reason
    assert [item.key for item in site.repositories()] == shown == [REPOSITORY]
    assert site.visibility(REPOSITORY).to_json() == visibility
    write_config(config, {}, raw=b"{broken")
    assert not site.orca_web().enabled
    (problem,) = site.config_problems()
    assert "not JSON" in problem.reason and "orca_web" not in problem.reason
    write_config(config, {"port": 9001})
    assert site.orca_web().enabled and site.orca_web().port == 9001
    assert site.config_problems() == ()


def test_http_origin_and_shell_policy_follow_admitted_host_and_live_settings(tmp_path: Path) -> None:
    from spec_dock.runtime.application.dashboard_http import _SHELL_CSP
    from spec_dock.runtime.infra.dashboard_store import hide_repository
    from spec_dock.runtime.infra.github_structure import GithubRepository

    site, config, catalog = environment(tmp_path)
    http = http_for(site)

    def listing(host: str = "127.0.0.1:47800") -> Any:
        return json.loads(get(http, "/api/v1/repositories", host).body)

    assert listing()["server"]["orca_web"] == {
        "enabled": True,
        "origin": "http://127.0.0.1:8791",
        "port": 8791,
        "problem": None,
    }
    baseline = {item.strip().split()[0]: item.strip() for item in _SHELL_CSP.split(";")}
    for host in ("127.0.0.1", "192.0.2.10", "LOCALHOST"):
        origin = f"http://{host.lower()}:8791"
        assert listing(f"{host}:47800")["server"]["orca_web"]["origin"] == origin
        for path in ("/", "/todos", f"/r/{REPOSITORY}/", f"/r/{REPOSITORY}/board"):
            for embed in (False, True):
                response = get(http, path, f"{host}:47800", embed=embed)
                assert response.status == 200
                csp = response.header("content-security-policy")
                assert csp is not None
                directives = {item.strip().split()[0]: item.strip() for item in csp.split(";")}
                for key, value in baseline.items():
                    assert directives[key] == value + (
                        f" {origin}" if key in {"script-src", "style-src", "connect-src", "frame-src"} else ""
                    )
                assert directives["frame-ancestors"] == (
                    "frame-ancestors " + http.embed_ancestors if embed else "frame-ancestors 'self'"
                )
    material = scope_dir(catalog, "iss-00002") / "explanation.html"
    material.write_text("<p>material</p>")
    material_path = f"/r/{REPOSITORY}/files/iss-00002/explanation.html"
    assert get(http, material_path).status == 200
    original_material_csp = get(http, material_path).header("content-security-policy")
    original_json_csp = get(http, "/api/v1/repositories").header("content-security-policy")
    write_config(config, {"port": 9001})
    assert listing()["server"]["orca_web"]["origin"] == "http://127.0.0.1:9001"
    assert "http://127.0.0.1:9001" in (get(http, "/").header("content-security-policy") or "")
    write_config(config, {"enabled": False})
    assert listing()["server"]["orca_web"] == {"enabled": False, "origin": None, "port": 8791, "problem": None}
    assert get(http, "/").header("content-security-policy") == _SHELL_CSP + "; frame-ancestors 'self'"
    assert get(http, material_path).header("content-security-policy") == original_material_csp
    assert get(http, "/api/v1/repositories").header("content-security-policy") == original_json_csp
    write_config(config, {"port": 47800})
    invalid = listing()["server"]["orca_web"]
    assert invalid["enabled"] is False and invalid["origin"] is None and "own port" in invalid["problem"]
    assert site.config_problems() == ()
    assert get(http, "/", "evil.example:47800").status == 421
    write_config(config, {})
    hide_repository(site.state_root, GithubRepository("o", "r"), now=NOW)
    hidden = get(http, f"/r/{REPOSITORY}/")
    assert hidden.status == 404 and "http://127.0.0.1:8791" in (hidden.header("content-security-policy") or "")


def test_shell_creates_one_shared_reader_and_serves_its_modules(tmp_path: Path) -> None:
    site, _config, _catalog = environment(tmp_path)
    http = http_for(site)
    for name in ("orca.js", "orca_match.js"):
        response = get(http, f"/assets/core/{name}")
        assert response.status == 200
        assert response.header("content-type") == "text/javascript; charset=utf-8"
    response = get(http, "/assets/app.js")
    assert response.status == 200
    source = response.body.decode()
    assert 'import { createOrca } from "./core/orca.js";' in source
    assert source.count("createOrca(") == 1
    boot = source.split("async function boot()", 1)[1]
    assert "state.orca = createOrca(state.server?.orca_web ?? null);" in boot
    assert boot.index("state.orca = createOrca(") > boot.index("state.server = listing.server ?? null;")
    check_server = source.split("async function checkServer()", 1)[1].split("async function boot()", 1)[0]
    assert "createOrca" not in check_server and "state.orca =" not in check_server
    # iss-00593 D-06: render() draws with viewCtx(), the same ctx that ctx.current() builds again.
    assert "module.render(root, viewCtx());" in source
    render = source.split("function viewCtx() {", 1)[1].split("\n}\n", 1)[0]
    assert "orca: state.orca," in render

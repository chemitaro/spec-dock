"""Routing and responses of the dashboard server (iss-00529 D-04〜D-07; Epic D-03, D-09, D-15, D-18).

`DashboardHttp.handle(Request) -> Response` has no socket, so every route and header is tested directly. The
server only reads: GitHub, the catalog, the repository and the registry are never written. The one write is a
"seen" record, accepted only from the dashboard's own pages (exact Origin, a fixed header, JSON).

Isolation of HTML materials (Epic D-09, #527 P-3/P-4): every response under `/r/…/files/` carries
`sandbox allow-scripts allow-popups` without `allow-same-origin` and the embedding `frame-ancestors`, so a
material runs in an opaque origin and cannot read the screens or the API. Only `/ds/` and `/vendor/` (no data)
carry `Access-Control-Allow-Origin: *`; the API never carries CORS headers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
import stat
from typing import TYPE_CHECKING, Final
from urllib.parse import unquote

from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.domain.dashboard_model import seen_scopes
from spec_dock.runtime.infra.dashboard_assets import (
    AssetFile,
    content_type,
    design_system_asset,
    screen_asset,
    vendor_asset,
)
from spec_dock.runtime.infra.dashboard_store import append_seen, find_seen
from spec_dock.runtime.presentation.dashboard_api import API_SCHEMA, scope_document, structure_document
from spec_dock.runtime.presentation.dashboard_summary import summary_document

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from pathlib import Path

    from spec_dock.runtime.application.dashboard_site import DashboardSite, RepositoryView, SiteRepository

SEEN_HEADER: Final = "x-specdock-dashboard"
SCREENS: Final = frozenset({"graph", "board", "timeline"})
_SNAPSHOT_ERRORS: Final = {
    "missing": ("DASHBOARD_SNAPSHOT_MISSING", "spec-dock canonical link", "spec-dock canonical status"),
    "unreadable": ("DASHBOARD_SNAPSHOT_UNREADABLE", "spec-dock canonical status"),
    "unsupported": ("DASHBOARD_SNAPSHOT_UNSUPPORTED", "spec-dock --version"),
}
_SHELL_CSP: Final = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    " connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'"
)


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: Mapping[str, Sequence[str]] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)  # lower-case names
    body: bytes = b""

    def header(self, name: str) -> str | None:
        return self.headers.get(name.lower())

    def param(self, name: str) -> str | None:
        values = self.query.get(name)
        return values[0] if values else None


@dataclass
class Response:
    status: int
    headers: list[tuple[str, str]]
    body: bytes = b""

    def header(self, name: str) -> str | None:
        return next((value for key, value in self.headers if key.lower() == name.lower()), None)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DashboardHttp:
    def __init__(
        self,
        site: DashboardSite,
        *,
        hosts: Sequence[str],
        port: int,
        embed_hosts: Sequence[str],
        local_url: str | None,
        version: str,
        started_at: str,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.site = site
        self.hosts = tuple(hosts)
        self.port = port
        self.embed_hosts = tuple(embed_hosts)
        self.local_url = local_url
        self.version = version
        self.started_at = started_at
        self.now = now

    # --- Headers -----------------------------------------------------------------------------------------------

    @property
    def embed_ancestors(self) -> str:
        return " ".join(("'self'", *(f"http://{host}:*" for host in self.embed_hosts)))

    def origins(self) -> frozenset[str]:
        return frozenset(f"http://{host}:{self.port}" for host in self.hosts)

    def _base(self, content: str, *, cache: str = "no-store") -> list[tuple[str, str]]:
        return [
            ("Content-Type", content),
            ("X-Content-Type-Options", "nosniff"),
            ("Cache-Control", cache),
            ("Referrer-Policy", "no-referrer"),
        ]

    def _json(self, status: int, payload: object) -> Response:
        headers = self._base("application/json; charset=utf-8")
        headers.append(("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"))
        return Response(status, headers, json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _error(self, status: int, code: str, message: str, *next_steps: str) -> Response:
        return self._json(
            status, {"schema": API_SCHEMA, "error": {"code": code, "message": message, "next_steps": list(next_steps)}}
        )

    def _html(self, status: int, body: bytes, *, embed: bool) -> Response:
        headers = self._base("text/html; charset=utf-8")
        ancestors = self.embed_ancestors if embed else "'self'"
        headers.append(("Content-Security-Policy", f"{_SHELL_CSP}; frame-ancestors {ancestors}"))
        return Response(status, headers, body)

    def _static(self, asset: AssetFile | None, *, cors: bool) -> Response:
        if asset is None:
            return self._plain(404, "not found")
        headers = self._base(asset.content_type, cache="no-cache")
        if cors:
            headers.append(("Access-Control-Allow-Origin", "*"))
        return Response(200, headers, asset.body)

    def _plain(self, status: int, text: str) -> Response:
        return Response(status, self._base("text/plain; charset=utf-8"), text.encode("utf-8"))

    def _material(self, status: int, body: bytes, content: str) -> Response:
        headers = self._base(content)
        headers.append((
            "Content-Security-Policy",
            f"sandbox allow-scripts allow-popups; frame-ancestors {self.embed_ancestors}",
        ))
        return Response(status, headers, body)

    # --- Entry -------------------------------------------------------------------------------------------------

    def handle(self, request: Request) -> Response:
        if not self._host_allowed(request.header("host")):
            return self._plain(421, "misdirected request: this host name is not served")
        if request.method not in ("GET", "HEAD", "POST"):
            response = self._plain(405, "method not allowed")
            response.headers.append(("Allow", "GET, HEAD, POST"))
            return response
        parts = _segments(request.path)
        if parts is None:
            return self._plain(400, "bad path")
        if request.method == "POST":
            if len(parts) == 7 and parts[:3] == ["api", "v1", "r"] and parts[6] == "seen":
                return self._seen(request, parts[3], parts[4], parts[5])
            response = self._plain(405, "method not allowed")
            response.headers.append(("Allow", "GET, HEAD"))
            return response
        return self._get(request, parts)

    def _host_allowed(self, value: str | None) -> bool:
        if not value:
            return False
        name, separator, port = value.strip().lower().rpartition(":")
        return bool(separator) and port == str(self.port) and name in self.hosts

    def _get(self, request: Request, parts: list[str]) -> Response:
        embed = request.param("embed") == "1"
        trimmed = parts[:-1] if parts and parts[-1] == "" else parts
        if not trimmed:
            return self._shell(embed)
        head, rest = trimmed[0], trimmed[1:]
        if head == "assets":
            return self._static(screen_asset(rest), cors=False)
        if head == "ds":
            return self._static(design_system_asset(rest), cors=True)
        if head == "vendor":
            return self._static(vendor_asset(rest), cors=True)
        if head == "api" and rest[:1] == ["v1"]:
            return self._api(request, rest[1:])
        if head == "r" and len(rest) >= 3:
            if rest[2] == "design-system" and len(rest) > 3:
                asset = design_system_asset(rest[3:])
                if asset is not None:
                    return self._static(asset, cors=True)
            return self._repository_page(rest[0], rest[1], rest[2], rest[3:], embed)
        return self._plain(404, "not found")

    # --- Screens -----------------------------------------------------------------------------------------------

    def _shell(self, embed: bool) -> Response:
        asset = screen_asset(["index.html"])
        if asset is None:
            return self._plain(500, "the dashboard screens are missing from this installation")
        return self._html(200, asset.body, embed=embed)

    def _repository_page(self, host: str, owner: str, name: str, rest: list[str], embed: bool) -> Response:
        found, site = self.site.lookup(host, owner, name)
        is_files = rest[:1] == ["files"]
        if found == "unknown" or site is None:
            return (
                self._material(404, b"not found", "text/plain; charset=utf-8")
                if is_files
                else self._plain(404, "this repository is not registered on this PC")
            )
        if found == "hidden":
            page = _hidden_page(site.repository.slug)
            if is_files:
                return self._material(404, page, "text/html; charset=utf-8")
            return self._html(404, page, embed=embed)
        if is_files:
            return self._file(site, rest[1:])
        if not rest or (len(rest) == 1 and rest[0] in SCREENS) or (len(rest) == 2 and rest[0] == "scopes"):
            return self._shell(embed)
        return self._plain(404, "not found")

    def _file(self, site: SiteRepository, rest: list[str]) -> Response:
        if site.catalog is None:
            payload = json.dumps(
                {
                    "code": "DASHBOARD_REPOSITORY_AMBIGUOUS",
                    "message": "two clones of this repository are registered; the catalog cannot be chosen",
                    "catalogs": list(site.catalogs),
                    "next_steps": ["spec-dock dashboard list", "spec-dock canonical remove"],
                },
                ensure_ascii=False,
            ).encode("utf-8")
            return self._material(409, payload, "application/json; charset=utf-8")
        if len(rest) < 2:
            return self._material(404, b"not found", "text/plain; charset=utf-8")
        try:
            relative = scope_relative(rest[0])
        except ValueError:
            return self._material(404, b"not found", "text/plain; charset=utf-8")
        body = _read_regular(site.catalog, [*relative.parts, *rest[1:]])
        if body is None:
            return self._material(404, b"not found", "text/plain; charset=utf-8")
        return self._material(200, body, content_type(rest[-1]))

    # --- API ---------------------------------------------------------------------------------------------------

    def _api(self, request: Request, parts: list[str]) -> Response:
        if parts == ["repositories"]:
            return self._json(200, self._repositories())
        if len(parts) >= 5 and parts[0] == "r":
            found, site = self.site.lookup(parts[1], parts[2], parts[3])
            if found == "unknown" or site is None:
                return self._error(404, "DASHBOARD_REPOSITORY_UNKNOWN", "this repository is not registered on this PC")
            if found == "hidden":
                return self._error(
                    404,
                    "DASHBOARD_REPOSITORY_HIDDEN",
                    "this repository is hidden from the dashboard",
                    f"spec-dock dashboard show {site.repository.slug}",
                )
            try:
                return self._repository_api(request, site, parts[4:])
            except Exception as error:  # one repository's failure stays in its own response (R-03, F-12)
                return self._error(500, "DASHBOARD_REPOSITORY_FAILED", f"{type(error).__name__}: {error}")
        return self._error(404, "DASHBOARD_NOT_FOUND", "no such API")

    def _repositories(self) -> dict[str, object]:
        items = []
        for site in self.site.repositories():
            repository = site.repository
            items.append({
                "repository": site.key,
                "host": repository.host,
                "owner": repository.owner,
                "name": repository.name,
                "path": f"/r/{site.key}/",
                "api": f"/api/v1/r/{site.key}/",
                "problem": site.problem,
            })
        return {
            "schema": API_SCHEMA,
            "repositories": items,
            "unknown_count": self.site.unknown_count(),
            "server": {"version": self.version, "started_at": self.started_at, "embed_hosts": list(self.embed_hosts)},
        }

    def _repository_api(self, request: Request, site: SiteRepository, op: list[str]) -> Response:
        view = self.site.view(site)
        if op == ["revision"]:
            return self._json(200, {"schema": API_SCHEMA, "repository": site.key, "revision": view.revision})
        if op == ["structure"]:
            latest = find_seen(self.site.state_root, site.repository, None)
            wanted = request.param("baseline")
            baseline = (find_seen(self.site.state_root, site.repository, wanted) if wanted else None) or latest
            return self._json(200, structure_document(view, now=self.now(), baseline=baseline, latest=latest))
        if op == ["summary"]:
            return self._summary(view)
        if len(op) == 2 and op[0] == "scopes":
            wanted = request.param("baseline")
            baseline = (find_seen(self.site.state_root, site.repository, wanted) if wanted else None) or find_seen(
                self.site.state_root, site.repository, None
            )
            document = scope_document(view, op[1], baseline=baseline)
            if document is None:
                return self._error(404, "DASHBOARD_SCOPE_UNKNOWN", f"{op[1]} is not in this repository's structure")
            return self._json(200, document)
        return self._error(404, "DASHBOARD_NOT_FOUND", "no such API")

    def _summary(self, view: RepositoryView) -> Response:
        if view.status != "ok" or view.model is None:
            code, *steps = _SNAPSHOT_ERRORS[view.status if view.status != "ok" else "missing"]
            return self._error(
                503, code, f"the structure snapshot of {view.repository.repository.slug} is {view.status}", *steps
            )
        return self._json(200, summary_document(view.model, hidden=False, server=self.local_url))

    # --- Seen (D-07) -------------------------------------------------------------------------------------------

    def _seen(self, request: Request, host: str, owner: str, name: str) -> Response:
        content = (request.header("content-type") or "").split(";", 1)[0].strip().lower()
        if (
            request.header("origin") not in self.origins()
            or request.header(SEEN_HEADER) != "1"
            or content != "application/json"
        ):
            return self._plain(403, "forbidden: only the dashboard's own pages may record what was seen")
        found, site = self.site.lookup(host, owner, name)
        if found != "visible" or site is None:
            return self._error(404, "DASHBOARD_REPOSITORY_UNKNOWN", "this repository is not served")
        view = self.site.view(site)
        if view.model is None:
            return self._error(409, "DASHBOARD_NOTHING_TO_RECORD", "there is no structure to record as seen")
        record = append_seen(self.site.state_root, site.repository, seen_scopes(view.model), now=self.now())
        return self._json(200, {"schema": API_SCHEMA, "seen_id": record.seen_id, "seen_at": record.seen_at})


def _segments(raw: str) -> list[str] | None:
    """Decoded path segments; None for anything that could leave its directory."""
    if not raw.startswith("/"):
        return None
    pieces = raw[1:].split("/")
    found: list[str] = []
    for index, piece in enumerate(pieces):
        try:
            value = unquote(piece, errors="strict") if "%" in piece else piece
        except UnicodeDecodeError:
            return None
        last = index == len(pieces) - 1
        if value == "" and last:
            found.append("")
            continue
        if value in ("", ".", "..") or any(mark in value for mark in ("/", "\\", "\x00")):
            return None
        found.append(value)
    return found


def _read_regular(root: Path, parts: Sequence[str]) -> bytes | None:
    """Read a regular file below `root` without following any link and without directories."""
    current = root
    try:
        if not stat.S_ISDIR(os.lstat(current).st_mode):
            return None
        for index, part in enumerate(parts):
            current = current / part
            mode = os.lstat(current).st_mode
            if stat.S_ISLNK(mode):
                return None
            last = index == len(parts) - 1
            if last and not stat.S_ISREG(mode):
                return None
            if not last and not stat.S_ISDIR(mode):
                return None
        descriptor = os.open(current, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    except (OSError, ValueError):
        return None
    with os.fdopen(descriptor, "rb") as stream:
        return stream.read()


def _hidden_page(slug: str) -> bytes:
    return (
        '<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>表示を止めたリポジトリ</title></head>'
        "<body><h1>このリポジトリの表示は止めてあります</h1>"
        f"<p>表示に戻すには、次のコマンドを実行します。</p><pre>spec-dock dashboard show {slug}</pre></body></html>"
    ).encode()

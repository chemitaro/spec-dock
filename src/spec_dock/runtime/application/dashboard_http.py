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
import html
import json
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING, Final
from urllib.parse import unquote

from spec_dock.runtime.application.dashboard_documents import (
    ScopeDocuments,
    document_details,
    failure_page,
    is_cue_scope,
    markdown_page,
)
from spec_dock.runtime.application.dashboard_progress import (
    PlanProgressCache,
    issues_in_progress,
    read_plan_progress,
)
from spec_dock.runtime.application.dashboard_scope_details import (
    StructureFactsCache,
    read_scope_details,
    read_structure_facts,
    scope_facts,
)
from spec_dock.runtime.application.dashboard_todos import CatalogUnreadable, TodoFilterInvalid, parse_status
from spec_dock.runtime.application.todo_aggregate import registry_summary_todos
from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.domain.dashboard_model import seen_scopes
from spec_dock.runtime.domain.dashboard_visibility import REPOSITORY_FILE
from spec_dock.runtime.domain.orca_web import OrcaWebOrigin, orca_web_origin
from spec_dock.runtime.domain.todo_record import TodoError
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

    from spec_dock.runtime.application.dashboard_site import DashboardSite, RepositoryView, SiteRepository
    from spec_dock.runtime.domain.dashboard_model import ScopeModel

SEEN_HEADER: Final = "x-specdock-dashboard"
SCREENS: Final = frozenset({"graph", "board", "timeline", "todos"})
_SNAPSHOT_ERRORS: Final = {
    "missing": ("DASHBOARD_SNAPSHOT_MISSING", "spec-dock canonical link", "spec-dock canonical status"),
    "unreadable": ("DASHBOARD_SNAPSHOT_UNREADABLE", "spec-dock canonical status"),
    "unsupported": ("DASHBOARD_SNAPSHOT_UNSUPPORTED", "spec-dock --version"),
}
_SHELL_CSP: Final = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    " connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'"
)


def shell_csp(origin: str | None) -> str:
    """Extend only the shell's four integration directives."""
    if origin is None:
        return _SHELL_CSP
    allowed = {"script-src", "style-src", "connect-src", "frame-src"}
    return ";".join(
        part + (f" {origin}" if part.strip().split()[0] in allowed else "") for part in _SHELL_CSP.split(";")
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
        self.installed_version = version  # the server's loop sets the upgraded version (iss-00530 R-05)
        self.started_at = started_at
        self.now = now
        self.facts = StructureFactsCache()  # iss-00544 D-02: assurance levels remembered across requests
        self.progress = PlanProgressCache()  # iss-00574 D-07: plan counts remembered across requests
        self.documents = ScopeDocuments()  # iss-00535 D-01: drawings remembered by their files' times

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

    def _html(self, status: int, body: bytes, *, embed: bool, orca_origin: str | None = None) -> Response:
        headers = self._base("text/html; charset=utf-8")
        ancestors = self.embed_ancestors if embed else "'self'"
        headers.append(("Content-Security-Policy", f"{shell_csp(orca_origin)}; frame-ancestors {ancestors}"))
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
            return self._shell(request, embed)
        head, rest = trimmed[0], trimmed[1:]
        if head == "assets":
            return self._static(screen_asset(rest), cors=False)
        if head == "favicon.ico" and not rest:
            return self._static(screen_asset(["favicon.svg"]), cors=False)  # the mark, so no 404 (iss-00572)
        if head == "ds":
            return self._static(design_system_asset(rest), cors=True)
        if head == "vendor":
            return self._static(vendor_asset(rest), cors=True)
        if head == "api" and rest[:1] == ["v1"]:
            return self._api(request, rest[1:])
        if head == "todos" and not rest:
            return self._shell(request, embed)  # every repository's human tasks (iss-00554 D-04)
        if head == "r" and len(rest) >= 3:
            if rest[2] == "design-system" and len(rest) > 3:
                asset = design_system_asset(rest[3:])
                if asset is not None:
                    return self._static(asset, cors=True)
            return self._repository_page(request, rest[0], rest[1], rest[2], rest[3:], embed)
        return self._plain(404, "not found")

    # --- Screens -----------------------------------------------------------------------------------------------

    def _orca(self, request: Request) -> OrcaWebOrigin:
        host = (request.header("host") or "").strip().lower().rpartition(":")[0]
        return orca_web_origin(self.site.orca_web(), host, self.port)

    def _shell(self, request: Request, embed: bool) -> Response:
        asset = screen_asset(["index.html"])
        if asset is None:
            return self._plain(500, "the dashboard screens are missing from this installation")
        return self._html(200, asset.body, embed=embed, orca_origin=self._orca(request)["origin"])

    def _repository_page(
        self, request: Request, host: str, owner: str, name: str, rest: list[str], embed: bool
    ) -> Response:
        found, site = self.site.lookup(host, owner, name)
        is_files = rest[:1] == ["files"]
        if found == "unknown" or site is None:
            return (
                self._material(404, b"not found", "text/plain; charset=utf-8")
                if is_files
                else self._plain(404, "this repository is not registered on this PC")
            )
        if found == "hidden":
            page = _hidden_page(self._hidden_steps(site))
            if is_files:
                return self._material(404, page, "text/html; charset=utf-8")
            return self._html(404, page, embed=embed, orca_origin=self._orca(request)["origin"])
        if is_files:
            return self._file(site, rest[1:])
        if len(rest) >= 3 and rest[0] == "scopes" and rest[2] == "doc":
            return self._document(site, rest[1], rest[3:])
        if not rest or (len(rest) == 1 and rest[0] in SCREENS) or (len(rest) == 2 and rest[0] in ("scopes", "todos")):
            return self._shell(request, embed)
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

    # --- Documents (iss-00535 D-02) ------------------------------------------------------------------------------

    def _scope_place(self, site: SiteRepository, scope_id: str) -> tuple[Path, Path, ScopeModel] | Response:
        """The Scope directory, the repository root for the CUE types and the Scope's model, or a refusal."""
        refused = self._material(404, b"not found", "text/plain; charset=utf-8")
        if site.catalog is None:
            return self._file(site, [])  # the same 409 as materials
        view = self.site.view(site)
        model = view.model.scopes.get(scope_id) if view.model is not None else None
        if model is None:
            return refused
        try:
            directory = site.catalog / Path(*scope_relative(scope_id).parts)
        except ValueError:
            return refused
        if not _is_directory(directory):
            return refused
        return directory, site.checkout or site.catalog, model

    def _document(self, site: SiteRepository, scope_id: str, parts: list[str]) -> Response:
        place = self._scope_place(site, scope_id)
        if isinstance(place, Response):
            return place
        directory, root, model = place
        if parts:
            page = markdown_page(directory, parts, scope_id=scope_id, title=model.title)
            if page is None:
                return self._material(404, b"not found", "text/plain; charset=utf-8")
            return self._material(200, page.encode("utf-8"), "text/html; charset=utf-8")
        if not is_cue_scope(directory):
            return self._material(404, b"not found", "text/plain; charset=utf-8")
        drawn = self.documents.drawn(
            scope_id=scope_id, kind=model.kind, title=model.title, directory=directory, repository_root=root
        )
        if drawn.html is None:
            page = failure_page(scope_id, model.title, drawn.check)
            return self._material(503, page.encode("utf-8"), "text/html; charset=utf-8")
        return self._material(200, drawn.html.encode("utf-8"), "text/html; charset=utf-8")

    def _document_details(
        self, site: SiteRepository, model: ScopeModel, details: dict[str, object]
    ) -> dict[str, object]:
        directory: Path | None = None
        if site.catalog is not None:
            try:
                directory = site.catalog / Path(*scope_relative(model.id).parts)
            except ValueError:
                directory = None
        return document_details(
            details,
            self.documents,
            base=f"/r/{site.key}/scopes/{model.id}/doc",
            scope_id=model.id,
            kind=model.kind,
            title=model.title,
            directory=directory,
            repository_root=site.checkout or site.catalog or Path(),
        )

    # --- API ---------------------------------------------------------------------------------------------------

    def _api(self, request: Request, parts: list[str]) -> Response:
        if parts == ["repositories"]:
            return self._json(200, self._repositories(request))
        if parts == ["todos"]:
            return self._todo_list(request, None)
        if parts == ["todos", "revision"]:
            sites = self.site.repositories()
            revision = self.site.todos.revision(sites, self.site.listing_signature())
            return self._json(200, {"schema": API_SCHEMA, "revision": revision})
        if len(parts) >= 5 and parts[0] == "r":
            found, site = self.site.lookup(parts[1], parts[2], parts[3])
            if found == "unknown" or site is None:
                return self._error(404, "DASHBOARD_REPOSITORY_UNKNOWN", "this repository is not registered on this PC")
            if found == "hidden":
                return self._error(
                    404,
                    "DASHBOARD_REPOSITORY_HIDDEN",
                    "this repository is hidden from the dashboard",
                    *self._hidden_steps(site),
                )
            try:
                return self._repository_api(request, site, parts[4:])
            except Exception as error:  # one repository's failure stays in its own response (R-03, F-12)
                return self._error(500, "DASHBOARD_REPOSITORY_FAILED", f"{type(error).__name__}: {error}")
        return self._error(404, "DASHBOARD_NOT_FOUND", "no such API")

    def _hidden_steps(self, site: SiteRepository) -> tuple[str, ...]:
        """What shows the repository again: `dashboard show` for the mark, the settings file for the settings."""
        visibility = self.site.visibility(site.key)
        steps: list[str] = []
        if visibility.mark:
            steps.append(f"spec-dock dashboard show {site.repository.slug}")
        if not visibility.config.visible:
            steps.append("spec-dock dashboard list")
            source = visibility.config.source
            if source == "invalid":
                paths = [problem.path for problem in visibility.config.problems]
            elif source == "user":
                paths = [str(self.site.user_config)]
            else:
                paths = [str(Path(catalog) / REPOSITORY_FILE) for catalog in site.catalogs]
            steps.extend(f"edit {path}" for path in paths)
        return tuple(steps)

    def _repositories(self, request: Request) -> dict[str, object]:
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
            "marks_unreadable": self.site.marks_unreadable(),
            "server": {
                "orca_web": self._orca(request),
                "version": self.version,
                "started_at": self.started_at,
                "embed_hosts": list(self.embed_hosts),
                "installed_version": self.installed_version,
                "restart_required": self.installed_version != self.version,
            },
        }

    def _repository_api(self, request: Request, site: SiteRepository, op: list[str]) -> Response:
        view = self.site.view(site)
        if op == ["revision"]:
            return self._json(200, {"schema": API_SCHEMA, "repository": site.key, "revision": view.revision})
        if op == ["structure"]:
            latest = find_seen(self.site.state_root, site.repository, None)
            wanted = request.param("baseline")
            baseline = (find_seen(self.site.state_root, site.repository, wanted) if wanted else None) or latest
            ids = sorted(view.model.scopes) if view.model is not None else []
            readings = read_structure_facts(site, ids, self.facts)  # iss-00544 D-02
            todos = self.site.todos.annotations(site, view.model)  # iss-00554 D-03
            progress = read_plan_progress(site, issues_in_progress(view.model), self.progress)  # iss-00574 D-07
            document = structure_document(
                view,
                now=self.now(),
                baseline=baseline,
                latest=latest,
                readings=readings,
                todos=todos,
                progress=progress,
            )
            return self._json(200, document)
        if op == ["summary"]:
            return self._summary(view)
        if op == ["todos"]:
            return self._todo_list(request, site)
        if len(op) == 2 and op[0] == "todos":
            return self._todo_one(site, op[1])
        if len(op) == 2 and op[0] == "scopes":
            wanted = request.param("baseline")
            baseline = (find_seen(self.site.state_root, site.repository, wanted) if wanted else None) or find_seen(
                self.site.state_root, site.repository, None
            )
            known = view.model is not None and op[1] in view.model.scopes
            details = read_scope_details(site, op[1]) if known else None  # iss-00531 D-04
            if details is not None and view.model is not None:
                details = self._document_details(site, view.model.scopes[op[1]], details)  # iss-00535 D-02
            one = {op[1]: scope_facts(details)} if details is not None else None
            scope_todos = self.site.todos.annotations(site, view.model) if known else None
            doing = [op[1]] if op[1] in issues_in_progress(view.model) else []
            one_progress = read_plan_progress(site, doing, self.progress, prune=False) if doing else None
            scope_json = scope_document(
                view,
                op[1],
                baseline=baseline,
                details=details,
                readings=one,
                todos=scope_todos,
                now=self.now(),
                progress=one_progress,
            )
            if scope_json is None:
                return self._error(404, "DASHBOARD_SCOPE_UNKNOWN", f"{op[1]} is not in this repository's structure")
            return self._json(200, scope_json)
        return self._error(404, "DASHBOARD_NOT_FOUND", "no such API")

    def _summary(self, view: RepositoryView) -> Response:
        if view.status != "ok" or view.model is None:
            code, *steps = _SNAPSHOT_ERRORS[view.status if view.status != "ok" else "missing"]
            return self._error(
                503, code, f"the structure snapshot of {view.repository.repository.slug} is {view.status}", *steps
            )
        todos = registry_summary_todos(self.site.state_root, view.repository.repository, now=self.now())
        return self._json(200, summary_document(view.model, hidden=False, server=self.local_url, todos=todos))

    # --- Human tasks (iss-00554 D-04) ---------------------------------------------------------------------------

    def _todo_list(self, request: Request, site: SiteRepository | None) -> Response:
        try:
            status = parse_status(request.param("status"))
        except TodoFilterInvalid as error:
            return self._error(
                400,
                "DASHBOARD_TODO_FILTER_INVALID",
                f"status {error} is not one of open, snoozed, done, cancelled, all",
            )
        todos = self.site.todos
        if site is None:
            return self._json(200, todos.list_document(self.site.repositories(), status))
        return self._json(200, todos.repository_document(site, status))

    def _todo_one(self, site: SiteRepository, raw_id: str) -> Response:
        try:
            return self._json(200, self.site.todos.one(site, raw_id))
        except CatalogUnreadable as error:
            step = str(error.problem.get("next_step") or "spec-dock canonical status")
            return self._error(503, str(error.problem.get("code") or "TODO_REPOSITORY_UNREADABLE"), str(error), step)
        except TodoError as error:
            steps = [error.next_step] if error.next_step else []
            status = 404 if error.code in ("TODO_NOT_FOUND", "TODO_INVALID") else 409
            return self._error(status, error.code, error.message, *steps)

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


def _is_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(os.lstat(path).st_mode)
    except OSError:
        return False


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


def _hidden_page(steps: tuple[str, ...]) -> bytes:
    lines = "\n".join(html.escape(step) for step in steps)
    return (
        '<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>表示を止めたリポジトリ</title></head>'
        "<body><h1>このリポジトリの表示は止めてあります</h1>"
        "<p>表示に戻すには、次の手順を行います（edit は、その設定のファイルの visible を直すことです）。</p>"
        f"<pre>{lines}</pre></body></html>"
    ).encode()

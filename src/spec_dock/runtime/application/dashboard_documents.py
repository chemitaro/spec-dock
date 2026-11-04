"""The documents of a Scope as the dashboard shows them (iss-00535 D-01; Epic D-11, R-19, R-25, R-26, F-10).

A CUE Scope is drawn by the drawing entry of contract K5 (`render_scope`) with the server's own design system
(`/ds/`) and diagram parts (`/vendor/`), so nothing comes from the internet. The drawn page, its check report
and the plan progress are remembered per Scope in memory, keyed by the time and size of every file the drawing
reads; the 5-second refresh therefore runs `cue` only after a file changed. A tool failure (no `cue`, a time
out) is never remembered, so the next request tries again (F-01).

Markdown documents (a Markdown Scope's requirement, design and plan, any Scope's report and ADRs) are wrapped
in the thin page of `wrap_page`. Only fixed names are read, never through a link. Nothing is written.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
import re
import stat
import threading
from typing import TYPE_CHECKING, Final
from urllib.parse import quote

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.scope_check import REPOSITORY_TYPES
from spec_dock.runtime.application.scope_render import ScopeRenderSource, render_scope
from spec_dock.runtime.presentation.spec_page import page_title, wrap_page

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path

    from spec_dock.runtime.application.scope_check import ScopeCheckReport
    from spec_dock.runtime.application.scope_render import RenderedScope
    from spec_dock.runtime.presentation.envelope import Diagnostic

DESIGN_SYSTEM_BASE: Final = "/ds/"
VENDOR_BASE: Final = "/vendor/"
TIMEOUT: Final = 10.0
ADR_LIMIT: Final = 100
DRAWN_FILES: Final = (
    "requirement.cue",
    "design.cue",
    "plan.cue",
    "explanation.html",
    "requirement.md",
)  # .md: a format conflict
MARKDOWN_DOCUMENTS: Final = ("requirement.md", "design.md", "plan.md", "report.md")
ADR_FOLDERS: Final = ("artifacts", "discussions")
_ADR: Final = re.compile(r"(?:^|-)adr-.*\.md\Z", re.IGNORECASE)
_TOOL_STEP: Final = "cue v0.17.1 以上を PATH に入れる（cue version で確かめる）"

_Signature = tuple[tuple[object, ...] | None, ...]


def _regular(path: Path) -> os.stat_result | None:
    try:
        info = os.lstat(path)
    except OSError:
        return None
    return info if stat.S_ISREG(info.st_mode) else None


def _is_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(os.lstat(path).st_mode)
    except OSError:
        return False


def is_cue_scope(directory: Path) -> bool:
    return _regular(directory / "requirement.cue") is not None


def _signature(directory: Path, repository_root: Path) -> _Signature:
    """Time and size of every file the drawing reads: the Scope's files and the repository's types."""
    parts: list[tuple[str, int, int] | None] = []
    for name in DRAWN_FILES:
        info = _regular(directory / name)
        parts.append(None if info is None else (name, info.st_mtime_ns, info.st_size))
    types = repository_root / REPOSITORY_TYPES
    try:
        names = sorted(item.name for item in os.scandir(types) if item.name.endswith(".cue"))
    except OSError:
        names = []
    for name in names:
        info = _regular(types / name)
        parts.append(None if info is None else (f"types/{name}", info.st_mtime_ns, info.st_size))
    return tuple(parts)


# --- Plan progress (R-04, Epic R-26) --------------------------------------------------------------------------


def plan_progress(evaluation: Mapping[str, object] | None) -> dict[str, object] | None:
    """Counts of the plan's steps by status; `total` leaves dropped steps out. None without steps."""
    steps = evaluation.get("steps") if evaluation is not None else None
    if not isinstance(steps, dict) or not steps:
        return None
    counts = {"done": 0, "doing": 0, "todo": 0, "dropped": 0}
    doing: list[dict[str, str]] = []
    for key in sorted(steps):
        value = steps[key]
        status = value.get("status", "todo") if isinstance(value, dict) else "todo"
        status = status if status in counts else "todo"
        counts[status] += 1
        if status == "doing" and isinstance(value, dict):
            title = value.get("title")
            doing.append({"id": key, "title": title if isinstance(title, str) else ""})
    total = counts["done"] + counts["doing"] + counts["todo"]
    return {"total": total, **counts, "doing_steps": doing}


# --- The CUE drawing and its check (R-01, R-02, F-01) ---------------------------------------------------------


@dataclass(frozen=True)
class DrawnScope:
    """One drawing: `html` is None when the tool failed (`failure` holds the code, the text and the next step)."""

    html: str | None
    check: dict[str, object]
    progress: dict[str, object] | None


def _diagnostic(item: Diagnostic) -> dict[str, object]:
    file = item.details.get("file") if isinstance(item.details, dict) else None
    return {"code": item.code, "message": item.message, "file": file if isinstance(file, str) else None}


def _check(report: ScopeCheckReport, complete: bool, scope_id: str) -> dict[str, object]:
    errors = [_diagnostic(item) for item in report.errors]
    warnings = [_diagnostic(item) for item in report.warnings]
    return {
        "status": "ok" if not errors else "invalid",
        "complete": complete,
        "errors": errors,
        "warnings": warnings,
        "next_steps": [f"spec-dock scope check {scope_id}"] if errors else [],
    }


def _failed(scope_id: str, code: str, message: str, step: str | None) -> DrawnScope:
    steps = [step] if step else []
    if code.startswith("CUE_NOT_FOUND") or code == "CUE_VERSION_UNSUPPORTED":
        steps = [_TOOL_STEP]
    steps.append(f"spec-dock scope check {scope_id}")
    check = {"status": "failed", "complete": False, "code": code, "message": message, "errors": [], "warnings": []}
    check["next_steps"] = steps
    return DrawnScope(None, check, None)


@dataclass
class ScopeDocuments:
    """The drawings remembered so far, per (catalog, Scope); lives as long as the server and is never written."""

    timeout: float = TIMEOUT
    render: Callable[..., RenderedScope] = render_scope
    _drawn: dict[tuple[str, str], tuple[_Signature, DrawnScope]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def drawn(
        self, *, scope_id: str, kind: str, title: str | None, directory: Path, repository_root: Path
    ) -> DrawnScope:
        key = (str(directory), scope_id)
        # The kind (passed to `cue`) and the title (on the page) come from the structure, so they key it too.
        signature = (("scope", kind, title), *_signature(directory, repository_root))
        with self._lock:
            remembered = self._drawn.get(key)
        if remembered is not None and remembered[0] == signature:
            return remembered[1]
        source = ScopeRenderSource(scope_id, kind, title, directory, repository_root, shown=scope_id)
        try:
            rendered = self.render(
                source, design_system_base=DESIGN_SYSTEM_BASE, vendor_base=VENDOR_BASE, timeout=self.timeout
            )
        except CanonicalCommandError as error:
            step = error.details.get("next_step") if isinstance(error.details, dict) else None
            return _failed(scope_id, error.code, error.message, step if isinstance(step, str) else None)
        except Exception as error:  # a broken drawing never takes the detail screen down (F-01)
            return _failed(scope_id, "DASHBOARD_RENDER_FAILED", f"{type(error).__name__}: {error}", None)
        drawn = DrawnScope(
            rendered.html,
            _check(rendered.report, rendered.complete, scope_id),
            plan_progress(rendered.report.evaluation) if rendered.complete else None,
        )
        with self._lock:
            self._drawn[key] = (signature, drawn)
        return drawn


def failure_page(scope_id: str, title: str | None, check: Mapping[str, object]) -> str:
    """The thin page shown in the document frame when the drawing failed (F-01)."""
    steps = check.get("next_steps")
    lines = [
        "---",
        f"title: {page_title(scope_id, title)} の文書を描けませんでした",
        "category: CUE の仕様",
        "---",
        "",
        f"`{check.get('code')}`：{check.get('message')}",
        "",
        "次の1手：",
        "",
        *(f"- `{step}`" for step in (steps if isinstance(steps, list) else [])),
    ]
    markdown = "\n".join(str(line).replace("\n", " ") for line in lines) + "\n"
    return wrap_page(
        markdown,
        title=page_title(scope_id, title),
        design_system_base=DESIGN_SYSTEM_BASE,
        vendor_base=VENDOR_BASE,
    )


# --- Markdown documents (R-03, Epic R-25) ---------------------------------------------------------------------


def adr_documents(directory: Path, limit: int = ADR_LIMIT) -> list[str]:
    """`artifacts/<name>` and `discussions/<name>` of the regular `.md` files named as ADRs, by name."""
    found: list[str] = []
    for folder in ADR_FOLDERS:
        if not _is_directory(directory / folder):
            continue
        try:
            names = sorted(item.name for item in os.scandir(directory / folder))
        except OSError:
            continue
        for name in names:
            if _ADR.search(name) and not name.startswith(".") and _regular(directory / folder / name) is not None:
                found.append(f"{folder}/{name}")
                if len(found) == limit:
                    return found
    return found


def allowed_markdown(parts: list[str]) -> bool:
    if len(parts) == 1:
        return parts[0] in MARKDOWN_DOCUMENTS
    return len(parts) == 2 and parts[0] in ADR_FOLDERS and bool(_ADR.search(parts[1])) and not parts[1].startswith(".")


def _read_text(directory: Path, parts: list[str]) -> str | None:
    """A regular UTF-8 file below the Scope directory, without following any link."""
    current = directory
    try:
        for index, part in enumerate(parts):
            current = current / part
            mode = os.lstat(current).st_mode
            last = index == len(parts) - 1
            if stat.S_ISLNK(mode) or (last and not stat.S_ISREG(mode)) or (not last and not stat.S_ISDIR(mode)):
                return None
        descriptor = os.open(current, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
        with os.fdopen(descriptor, "rb") as stream:
            return stream.read().decode("utf-8", errors="replace")
    except (OSError, ValueError):
        return None


_CATEGORIES: Final = {
    "requirement.md": "Markdown の要件",
    "design.md": "Markdown の設計",
    "plan.md": "Markdown の計画",
    "report.md": "報告",
}
_FRONT_MATTER: Final = re.compile(r"\A---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|\Z)")


def _with_front_matter(text: str, *, title: str, lead: str, category: str) -> str:
    """The design system reads only ASCII keys, so a document gets its own title and category; the document's
    own front matter (often Japanese keys) stays readable as a YAML block at the top of the body."""
    found = _FRONT_MATTER.match(text)
    body = text[found.end() :] if found else text
    kept = f"```yaml\n{found.group(1).replace('```', '` ` `')}\n```\n\n" if found else ""
    one_line = lambda value: value.replace("\n", " ").replace('"', "'")  # noqa: E731
    front = f'---\ntitle: "{one_line(title)}"\nlead: "{one_line(lead)}"\ncategory: "{one_line(category)}"\n---\n\n'
    return front + kept + body


def markdown_page(directory: Path, parts: list[str], *, scope_id: str, title: str | None) -> str | None:
    """The thin page around one allowed Markdown document, or None (not allowed, missing, a link)."""
    if not allowed_markdown(parts):
        return None
    text = _read_text(directory, parts)
    if text is None:
        return None
    shown = "/".join(parts)
    heading = f"{page_title(scope_id, title)} · {shown}"
    return wrap_page(
        _with_front_matter(
            text, title=page_title(scope_id, title), lead=shown, category=_CATEGORIES.get(parts[0], "ADR")
        ),
        title=heading,
        design_system_base=DESIGN_SYSTEM_BASE,
        vendor_base=VENDOR_BASE,
    )


# --- The Scope API's document fields (iss-00535 D-02) ---------------------------------------------------------


def document_details(
    details: dict[str, object],
    documents: ScopeDocuments,
    *,
    base: str,
    scope_id: str,
    kind: str,
    title: str | None,
    directory: Path | None,
    repository_root: Path,
) -> dict[str, object]:
    """`details` with `spec`, `check`, `progress`, `adrs` and each document's `view` (the path the frame shows).

    `base` is `/r/<host>/<owner>/<name>/scopes/<ID>/doc`. Without a readable Scope directory the fields are
    empty; the catalog problem is already in `details`.
    """
    readable = directory is not None and details.get("catalog") == "ok"
    cue = readable and directory is not None and is_cue_scope(directory)
    drawn = (
        documents.drawn(scope_id=scope_id, kind=kind, title=title, directory=directory, repository_root=repository_root)
        if cue and directory is not None
        else None
    )
    shown: list[dict[str, object]] = []
    listed = details.get("documents")
    for item in listed if isinstance(listed, list) else []:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        view: str | None = None
        if item.get("exists") and item.get("key") != "explanation":
            if isinstance(name, str) and name.endswith(".cue"):
                view = base
            elif isinstance(name, str) and name in MARKDOWN_DOCUMENTS:
                view = f"{base}/{quote(name, safe='')}"
        shown.append({**item, "view": view})
    adrs = adr_documents(directory) if readable and directory is not None else []
    return {
        **details,
        "documents": shown,
        "spec": base if cue else None,
        "check": drawn.check if drawn is not None else None,
        "progress": drawn.progress if drawn is not None else None,
        "adrs": [
            {
                "name": path.split("/", 1)[1],
                "path": path,
                "view": f"{base}/" + "/".join(quote(part, safe="") for part in path.split("/")),
            }
            for path in adrs
        ],
    }

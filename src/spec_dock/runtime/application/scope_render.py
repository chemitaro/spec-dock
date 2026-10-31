"""Draw one CUE Scope as HTML (iss-00476; the drawing entry of contract K5, epic-00425 R-F1).

Entry for hosts such as the dashboard server (epic-00427)::

    from spec_dock.runtime.application.scope_render import ScopeRenderSource, render_scope_html

    html = render_scope_html(
        ScopeRenderSource(scope_id="iss-00476", kind="issue", title="Render CUE Specs As HTML",
                          directory=<the Scope directory>, repository_root=<the checkout root>),
        design_system_base="/design-system/",  # URL head that serves ds.css and ds.js (spec-dock/design-system/)
        vendor_base="/vendor/",                # URL head of the bundled diagram parts, or None for the CDN
    )

The Scope is evaluated once by I-2's check (contract K1; `cue` v0.17.1 or later on PATH, no network), and the
evaluation is laid out by `presentation.spec_page` in the thin explanation shape. Nothing is written.

Stops with CanonicalCommandError: SCOPE_NOT_CUE (exit 7) for a Markdown Scope, and the codes of `scope check`
(CUE_NOT_FOUND, CUE_VERSION_UNSUPPORTED, CUE_SCHEMA_UNSUPPORTED exit 3; CUE_TIMEOUT, CUE_FAILED exit 5).
A Scope whose evaluation fails (shape errors, both formats) gives a page of its check results only
(`RenderedScope.complete` is False); connection findings are shown at the top of a complete page.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.scope_check import SPEC_FINDINGS, check_scope_documents
from spec_dock.runtime.presentation.spec_page import page_title, spec_markdown, wrap_page

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.application.scope_check import ScopeCheckReport
    from spec_dock.runtime.presentation.envelope import Diagnostic

SCOPE_NOT_CUE: Final = "SCOPE_NOT_CUE"
SCOPE_RENDER_INCOMPLETE: Final = "SCOPE_RENDER_INCOMPLETE"
DESIGN_SYSTEM_MISSING: Final = "DESIGN_SYSTEM_MISSING"
_NOT_CUE_STEP: Final = (
    "Read requirement.md, design.md and plan.md directly; scope render draws only CUE Scopes (requirement.cue)."
)


@dataclass(frozen=True)
class ScopeRenderSource:
    """One Scope to draw. `kind` comes from GitHub, the structure authority (passed to `cue` as -t kind)."""

    scope_id: str
    kind: str
    title: str | None
    directory: Path
    repository_root: Path
    shown: str | None = None  # how errors name the Scope directory; default: relative to repository_root


@dataclass(frozen=True)
class RenderedScope:
    html: str
    report: ScopeCheckReport
    complete: bool  # the evaluation passed and the whole body was drawn
    errors: tuple[Diagnostic, ...]  # errors shown on the page (not findings, not the explanation check)


def render_scope(
    source: ScopeRenderSource, *, design_system_base: str, vendor_base: str | None, timeout: float = 30.0
) -> RenderedScope:
    """Evaluate and draw one Scope; see the module docstring for the stops."""
    report = check_scope_documents(
        source.directory,
        kind=source.kind,
        shown=source.shown or _shown(source),
        repository_root=source.repository_root,
        timeout=timeout,
    )
    if report.format == "markdown":
        raise CanonicalCommandError(
            SCOPE_NOT_CUE,
            f"{source.scope_id} is a Markdown Scope; scope render draws only CUE Scopes",
            exit_code=7,
            recovery=(_NOT_CUE_STEP,),
            details={"scope_id": source.scope_id, "next_step": _NOT_CUE_STEP},
        )
    errors = tuple(
        error for error in report.errors if error.code != SPEC_FINDINGS and not error.code.startswith("EXPLANATION_")
    )
    evaluation = report.evaluation
    # The level is read from requirement.cue alone, as scope show and scope check read it (K3, R-C2).
    reading = report.assurance
    assurance = {"level": reading.level, "reason": reading.reason} if reading.source == "cue" else None
    title = page_title(source.scope_id, source.title)
    markdown = spec_markdown(
        scope_id=source.scope_id, title=source.title, evaluation=evaluation, assurance=assurance, errors=errors
    )
    page = wrap_page(markdown, title=title, design_system_base=design_system_base, vendor_base=vendor_base)
    return RenderedScope(page, report, evaluation is not None, errors)


def render_scope_html(
    source: ScopeRenderSource, *, design_system_base: str, vendor_base: str | None, timeout: float = 30.0
) -> str:
    """The HTML of one CUE Scope (the documented entry of contract K5); see the module docstring."""
    return render_scope(source, design_system_base=design_system_base, vendor_base=vendor_base, timeout=timeout).html


def _shown(source: ScopeRenderSource) -> str:
    try:
        return source.directory.relative_to(source.repository_root).as_posix()
    except ValueError:
        return os.fspath(source.directory)

"""The drawing entry of contract K5 (iss-00476): render_scope_html over I-2's evaluation, with the real `cue`."""

from __future__ import annotations

import re
import socket
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.scope_render import ScopeRenderSource, render_scope, render_scope_html
from spec_dock.runtime.domain.explanation_shape import inspect_explanation
from tests.support.cue import cue_executable
from tests.support.cue_scopes import hide_cue, install_fake_cue, place_sample

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.usefixtures("real_cue")


@pytest.fixture
def real_cue() -> None:
    cue_executable()


@pytest.fixture
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("the renderer must not use the network")

    monkeypatch.setattr(socket.socket, "connect", refuse)


def source(tmp_path: Path, sample: str, kind: str = "issue") -> ScopeRenderSource:
    repository = tmp_path / "repo"
    scope = place_sample(repository / "spec-dock/initiatives/00000-00999/iss-00003", sample)
    return ScopeRenderSource("iss-00003", kind, "書き出し <b>", scope, repository)


@pytest.mark.usefixtures("no_network")
def test_an_issue_is_drawn_in_the_thin_shape(tmp_path: Path) -> None:
    page = render_scope_html(
        source(tmp_path, "issue-strict-complete"), design_system_base="../../../design-system/", vendor_base=None
    )
    shape = inspect_explanation(page)
    assert shape.problems == () and not shape.skeleton
    assert "ds-vendor-base" not in page
    assert "<title>iss-00003 書き出し &lt;b&gt;</title>" in page
    for anchor in ("R-01", "F-01", "D-01", "S-01", "T-01"):
        assert f'<h3 id="{anchor}">' in page
    assert "誤りと指摘はありません。" in page


@pytest.mark.usefixtures("no_network")
def test_an_epic_is_drawn_with_its_slices_and_the_vendor_base(tmp_path: Path) -> None:
    rendered = render_scope(
        source(tmp_path, "epic-standard-uncovered", "epic"), design_system_base="/ds/", vendor_base="/vendor/"
    )
    assert rendered.complete
    assert '<meta name="ds-vendor-base" content="/vendor/">' in rendered.html
    assert '<h3 id="slice-iss-00011">' in rendered.html
    assert '<link rel="stylesheet" href="/ds/ds.css">' in rendered.html


def test_the_same_scope_draws_the_same_html(tmp_path: Path) -> None:
    scope = source(tmp_path, "issue-standard-gaps")
    first = render_scope_html(scope, design_system_base="/ds/", vendor_base=None)
    assert first == render_scope_html(scope, design_system_base="/ds/", vendor_base=None)


def test_findings_are_shown_first_and_the_explanation_check_is_left_out(tmp_path: Path) -> None:
    scope = source(tmp_path, "issue-standard-gaps")
    (scope.directory / "explanation.html").unlink()
    rendered = render_scope(scope, design_system_base="/ds/", vendor_base=None)
    assert rendered.complete and rendered.report.errors
    assert rendered.errors == ()  # findings are drawn from the evaluation; the explanation is not this page's
    results = rendered.html[rendered.html.index("## 検査の結果") : rendered.html.index("## 保証レベル")]
    assert "requirement\\-without\\-design" in results and "EXPLANATION" not in rendered.html


def test_a_shape_error_gives_a_page_of_check_results_only(tmp_path: Path) -> None:
    scope = source(tmp_path, "issue-light-minimal")
    requirement = scope.directory / "requirement.cue"
    requirement.write_text(requirement.read_text(encoding="utf-8") + '\nrequirements: "R-09": {}\n', encoding="utf-8")
    rendered = render_scope(scope, design_system_base="/ds/", vendor_base=None)
    assert not rendered.complete
    assert [error.code for error in rendered.errors] and {e.code for e in rendered.errors} == {"CUE_INVALID"}
    assert re.findall(r"^## (.+)$", rendered.html, re.MULTILINE) == ["検査の結果"]


def test_a_scope_with_both_formats_gives_a_page_of_check_results_only(tmp_path: Path) -> None:
    scope = source(tmp_path, "issue-light-minimal")
    (scope.directory / "requirement.md").write_text("# r\n", encoding="utf-8")
    rendered = render_scope(scope, design_system_base="/ds/", vendor_base=None)
    assert not rendered.complete and [error.code for error in rendered.errors] == ["SCOPE_FORMAT_CONFLICT"]


def test_a_markdown_scope_stops_without_cue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    directory = tmp_path / "repo/scope"
    directory.mkdir(parents=True)
    (directory / "requirement.md").write_text("# r\n", encoding="utf-8")
    with pytest.raises(CanonicalCommandError) as raised:
        render_scope_html(
            ScopeRenderSource("iss-00003", "issue", None, directory, tmp_path / "repo"),
            design_system_base="/ds/",
            vendor_base=None,
        )
    assert (raised.value.code, raised.value.exit_code) == ("SCOPE_NOT_CUE", 7)


@pytest.mark.parametrize(
    ("setup", "code", "exit_code"),
    [
        ("hide", "CUE_NOT_FOUND", 3),
        ("old", "CUE_VERSION_UNSUPPORTED", 3),
    ],
)
def test_a_cue_problem_stops_with_the_scope_check_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, setup: str, code: str, exit_code: int
) -> None:
    scope = source(tmp_path, "issue-light-minimal")
    if setup == "hide":
        hide_cue(monkeypatch)
    else:
        install_fake_cue(tmp_path, monkeypatch, version="cue version v0.16.0")
    with pytest.raises(CanonicalCommandError) as raised:
        render_scope_html(scope, design_system_base="/ds/", vendor_base=None)
    assert (raised.value.code, raised.value.exit_code) == (code, exit_code)


def test_the_level_is_read_from_requirement_cue_alone(tmp_path: Path) -> None:
    scope = source(tmp_path, "issue-light-minimal")
    requirement = scope.directory / "requirement.cue"
    text = requirement.read_text(encoding="utf-8")
    start = text.index("assurance:")
    end = text.index("}", start) + 1
    requirement.write_text(text[:start] + text[end:], encoding="utf-8")
    plan = scope.directory / "plan.cue"
    plan.write_text(plan.read_text(encoding="utf-8") + "\n" + text[start:end] + "\n", encoding="utf-8")
    rendered = render_scope(scope, design_system_base="/ds/", vendor_base=None)
    assert rendered.complete
    assert "ASSURANCE\\_UNREADABLE" in rendered.html
    assert "status: 保証レベル 未確定" in rendered.html and "読めません" in rendered.html


class TestEmbeddedDesignSystem:
    """iss-00489 R-05/F-01: the design system can be carried inside the page; the default keeps the links."""

    @staticmethod
    def design_system() -> Path:
        from tests.support.cue_scopes import SKELETON

        return SKELETON.parent

    @pytest.mark.usefixtures("no_network")
    def test_the_default_is_the_page_it_was(self, tmp_path: Path) -> None:
        scope = source(tmp_path, "issue-strict-complete")
        linked = render_scope_html(scope, design_system_base="/ds/", vendor_base=None)
        assert render_scope_html(scope, design_system_base="/ds/", vendor_base=None, embed_design_system=None) == linked
        assert '<link rel="stylesheet" href="/ds/ds.css">' in linked and '<script src="/ds/ds.js">' in linked

    @pytest.mark.usefixtures("no_network")
    def test_an_embedded_page_carries_the_three_files_and_no_path(self, tmp_path: Path) -> None:
        import base64

        ds = self.design_system()
        page = render_scope_html(
            source(tmp_path, "issue-strict-complete"),
            design_system_base="file:///nowhere/",
            vendor_base=None,
            embed_design_system=ds,
        )
        assert "file:" not in page and "ds.css" not in page and "ds.js" not in page
        assert f"<style>\n{(ds / 'ds.css').read_text(encoding='utf-8')}" in page
        scripts = re.findall(r'<script src="data:text/javascript;base64,([A-Za-z0-9+/=]+)"></script>', page)
        decoded = [base64.b64decode(item) for item in scripts]
        # marked comes first, so ds.js finds window.marked and never asks for vendor/marked.umd.js.
        assert decoded == [(ds / "vendor/marked.umd.js").read_bytes(), (ds / "ds.js").read_bytes()]
        assert page.index('id="ds-source"') < page.index("data:text/javascript")
        assert '<h3 id="R-01">' in page and "<title>iss-00003 書き出し &lt;b&gt;</title>" in page

    def test_a_missing_design_system_stops_without_a_page(self, tmp_path: Path) -> None:
        with pytest.raises(CanonicalCommandError) as raised:
            render_scope_html(
                source(tmp_path, "issue-strict-complete"),
                design_system_base="/ds/",
                vendor_base=None,
                embed_design_system=tmp_path / "absent",
            )
        assert (raised.value.code, raised.value.exit_code) == ("DESIGN_SYSTEM_MISSING", 3)
        assert "installation update" in " ".join(raised.value.recovery)

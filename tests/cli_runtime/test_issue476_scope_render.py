"""`spec-dock scope render <ID>` on a canonical catalog (iss-00476; the drawing entry of K5, epic-00425)."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.domain.explanation_shape import inspect_explanation
from tests.support.canonical_scopes import CanonicalWorld
from tests.support.cue import cue_executable
from tests.support.cue_scopes import hide_cue, place_sample

if TYPE_CHECKING:
    from pathlib import Path

SHOWN = "spec-dock/initiatives/00000-00999/iss-00003"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    cue_executable()
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf <export>", parent=2, documents=())
    world.scope("issue", 4, "Markdown leaf", parent=2)
    place_sample(world.catalog / world.relative("issue", 3), "issue-strict-complete")
    return world


def files_of(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink() and ".git" not in path.relative_to(root).parts
    }


def text_run(world: CanonicalWorld, *argv: str) -> tuple[int, str, str]:
    world.capsys.readouterr()
    code = main(["--project", str(world.main), *argv])
    captured = world.capsys.readouterr()
    return code, captured.out, captured.err


def design_system(world: CanonicalWorld) -> Path:
    return world.main / "spec-dock" / "design-system"


def give_design_system(world: CanonicalWorld) -> None:
    from tests.support.cue_scopes import SKELETON

    target = design_system(world)
    if not target.exists():
        shutil.copytree(SKELETON.parent, target)


def test_the_html_alone_goes_to_standard_output_without_writing(world: CanonicalWorld) -> None:
    give_design_system(world)
    before = (files_of(world.catalog.resolve()), files_of(world.main))
    code, out, err = text_run(world, "scope", "render", "iss-3")
    assert code == 0, err
    assert out.startswith("<!doctype html>\n") and out.endswith("</html>\n")
    assert "spec-dock:" not in out.splitlines()[0]
    base = design_system(world).resolve().as_uri() + "/"
    assert f'<link rel="stylesheet" href="{base}ds.css">' in out and f'<script src="{base}ds.js">' in out
    assert "ds-vendor-base" not in out
    assert "<title>iss-00003 Leaf &lt;export&gt;</title>" in out
    assert '<h3 id="R-01">' in out and "誤りと指摘はありません。" in out
    assert inspect_explanation(out.replace(base, "../../../design-system/")).problems == ()
    assert err == ""
    assert (files_of(world.catalog.resolve()), files_of(world.main)) == before


def test_json_carries_the_same_html(world: CanonicalWorld) -> None:
    give_design_system(world)
    _, out, _ = text_run(world, "scope", "render", "iss-3")
    code, payload = world.run("scope", "render", "iss-00003")
    assert (code, payload["command"], payload["status"], payload["error"]) == (0, "scope render", "succeeded", None)
    result = payload["data"]["result"]
    assert payload["data"]["kind"] == "scope-render"
    assert (result["scope_id"], result["kind"], result["path"], result["format"]) == (
        "iss-00003",
        "issue",
        SHOWN,
        "cue",
    )
    assert (result["complete"], result["valid"], result["errors"], result["vendor_base"]) == (True, True, [], None)
    assert result["html"] == out


def test_an_evaluation_failure_succeeds_with_the_check_results_and_a_warning(world: CanonicalWorld) -> None:
    give_design_system(world)
    plan = world.catalog / world.relative("issue", 3) / "plan.cue"
    plan.write_text(plan.read_text(encoding="utf-8").replace('status: "doing"', 'status: "nope"'), encoding="utf-8")
    code, out, err = text_run(world, "scope", "render", "iss-3")
    assert code == 0
    assert "warning [SCOPE_RENDER_INCOMPLETE]" in err and "spec-dock scope check iss-00003" in err
    assert "CUE\\_INVALID" in out and "## 要件" not in out
    code, payload = world.run("scope", "render", "iss-3")
    result = payload["data"]["result"]
    assert (result["complete"], result["valid"]) == (False, False)
    assert {item["code"] for item in result["errors"]} == {"CUE_INVALID"}


def test_findings_render_with_success(world: CanonicalWorld) -> None:
    give_design_system(world)
    design = world.catalog / world.relative("issue", 3) / "design.cue"
    design.write_text(design.read_text(encoding="utf-8").replace('satisfies: ["F-01"]', 'satisfies: ["R-09"]'), "utf-8")
    code, payload = world.run("scope", "render", "iss-3")
    result = payload["data"]["result"]
    assert (code, result["complete"], result["valid"], result["errors"]) == (0, True, False, [])
    assert "### unknown\\-reference" in result["html"] and "R\\-09（ない番号）" in result["html"]


def test_a_markdown_scope_stops_with_scope_not_cue(world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    code, out, err = text_run(world, "scope", "render", "iss-4")
    assert code == 7
    assert "<!doctype" not in out and "error [SCOPE_NOT_CUE]" in err


def test_a_missing_cue_stops_like_scope_check(world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    hide_cue(monkeypatch)
    code, payload = world.run("scope", "render", "iss-3")
    assert (code, payload["error"]["code"]) == (3, "CUE_NOT_FOUND")


def test_a_checkout_without_the_design_system_warns(world: CanonicalWorld) -> None:
    if design_system(world).exists():
        shutil.rmtree(design_system(world))
    code, out, err = text_run(world, "scope", "render", "iss-3")
    assert code == 0 and out.startswith("<!doctype html>")
    assert "warning [DESIGN_SYSTEM_MISSING]" in err
    assert "spec-dock installation update" in err


def test_inline_embeds_the_design_system_and_reports_no_base(world: CanonicalWorld) -> None:
    """iss-00489 R-05: the page needs no file outside itself; the default stays the file: link."""
    give_design_system(world)
    code, out, err = text_run(world, "scope", "render", "iss-3", "--design-system", "inline")
    assert code == 0, err
    assert "file:" not in out and "ds.css" not in out and "<style>\n" in out
    assert out.count('<script src="data:text/javascript;base64,') == 2
    assert '<h3 id="R-01">' in out
    code, payload = world.run("scope", "render", "iss-3", "--design-system", "inline")
    result = payload["data"]["result"]
    assert (code, result["design_system"], result["design_system_base"], result["html"]) == (0, "inline", None, out)
    code, payload = world.run("scope", "render", "iss-3")
    result = payload["data"]["result"]
    assert (result["design_system"], result["design_system_base"]) == (
        "file",
        design_system(world).resolve().as_uri() + "/",
    )


def test_inline_without_the_design_system_stops_without_a_page(world: CanonicalWorld) -> None:
    """iss-00489 F-01: nothing half-drawn; the next step is installation update."""
    if design_system(world).exists():
        shutil.rmtree(design_system(world))
    code, out, err = text_run(world, "scope", "render", "iss-3", "--design-system", "inline")
    assert code == 3 and "<!doctype" not in out and "<html" not in out
    assert "error [DESIGN_SYSTEM_MISSING]" in err and "spec-dock installation update" in err


def test_an_unknown_design_system_mode_is_a_usage_error(world: CanonicalWorld) -> None:
    code, out, _ = text_run(world, "scope", "render", "iss-3", "--design-system", "relative")
    assert code != 0 and "<!doctype" not in out

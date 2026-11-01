"""The CUE authoring guides, skill and release documents agree with the type and runtime they describe (iss-00477)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import pytest

from spec_dock.runtime.application import (
    canonical_errors,
    canonical_scope_check,
    canonical_scope_create,
    scope_check,
    scope_render,
)
from spec_dock.runtime.application.scope_check import check_scope_documents
from spec_dock.runtime.domain.explanation_shape import DESIGN_SYSTEM_CSS, DESIGN_SYSTEM_JS, SKELETON_MARKER
from spec_dock.runtime.infra import cue_tool
from tests.support.cue import cue_executable
from tests.support.cue_scopes import written_explanation

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src/spec_dock/assets"
SCAFFOLD = ASSETS / "spec_dock"
DOCS = SCAFFOLD / "docs"
AUTHORING = DOCS / "authoring"
CUE_GUIDE = AUTHORING / "cue.md"
EXPLANATION_GUIDE = AUTHORING / "explanation.md"
SKILL = ASSETS / "install_root/.agents/skills/spec-dock/SKILL.md"
RULES = ROOT / "src/spec_dock/cue/v1/rules.cue"
VERSION = "0.4.1"
STAGES = {0: "light から", 1: "standard から", 2: "strict から", 3: "critical"}
EVERY_STAGE = "どの段階でも"
# The bytes of every static asset this Issue rewrites, as of d53b24d64 (0.3.0 assets). A consumer holding them
# must be able to `installation update` (F-08); CI's shallow clone cannot read the history, so they are fixed here.
PREVIOUS_SHA256 = {
    ".agents/skills/spec-dock/SKILL.md": "66f2cdf90516",
    "spec-dock/docs/authoring/historical.md": "0074ff1c57c3",
    "spec-dock/docs/authoring/issue-plan.md": "4b4d6ac04307",
    "spec-dock/docs/authoring/overview.md": "8438f0cf9901",
    "spec-dock/docs/authoring/scope-layering.md": "0be56200566b",
    "spec-dock/docs/canonical.md": "ac31d512666e",
    "spec-dock/docs/migration.md": "1b17e1b38284",
    "spec-dock/system/spec-dock-version": "d915cc95d6ca",
    "spec-dock/templates/README.md": "3ec4263314f2",
}
# The bytes of cue.md as iss-00477 first shipped it (7f3cf7d3c); iss-00487 rewrote it.
CUE_GUIDE_FIRST_SHA256 = "c674b205dce51b30766e60dd1302aedf8672e2facefda4aaa47f37d7499ec88e"
# The bytes of cue.md as iss-00487 shipped it (155d144d8); iss-00489 rewrote it again.
CUE_GUIDE_ISS487_SHA256 = "a4593015a9dc78bff46204436f02ba0ecc49cf3e13de5d9b33cd28e958451d28"
CUE_MODULES = (canonical_scope_create, scope_check, canonical_scope_check, scope_render, cue_tool)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.index(heading + "\n")
    end = text.find("\n## ", start + len(heading))
    return text[start : end if end >= 0 else len(text)]


def _table(text: str) -> dict[str, list[str]]:
    """Each backticked code in a table row's first cell, with that row's cells."""
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or set(cells[0]) <= {"-", ":"}:
            continue
        for code in re.findall(r"`([A-Za-z][A-Za-z0-9_-]+)`", cells[0]):
            rows[code] = cells
    return rows


def _rule_stages() -> dict[str, int | None]:
    """Each rule of the v1 type with the lowest level that reports it (None: any level, when execution is used)."""
    text = _read(RULES)
    body = text[text.index("\nfindings: {") :]
    stages: dict[str, int | None] = {}
    condition: int | None = 0
    for line in body.splitlines():
        guard = re.match(r"^\tif (.+) \{$", line)
        if guard:
            stage = re.fullmatch(r"_rank >= (\d)", guard.group(1))
            condition = int(stage.group(1)) if stage else None
            continue
        if line == "\t}":
            condition = 0
            continue
        rule = re.match(r'^\t{1,2}"([a-z-]+)": ', line)
        if rule:
            stages[rule.group(1)] = condition
    return stages


def _public_codes(module: object) -> set[str]:
    return {name for name, value in vars(module).items() if isinstance(value, str) and name == value and name.isupper()}


def test_the_cue_guide_lists_every_rule_at_the_stage_the_type_reports_it() -> None:
    stages = _rule_stages()
    assert len(stages) == 8, stages
    rows = _table(_section(_read(CUE_GUIDE), "## つながりの規則"))
    assert set(rows) == set(stages)
    for rule, stage in stages.items():
        assert rows[rule][-1].startswith(EVERY_STAGE if stage is None else STAGES[stage]), (rule, rows[rule])


def test_every_public_code_of_the_cue_parts_has_a_documented_next_step() -> None:
    documented = {
        **_table(_section(_read(DOCS / "canonical.md"), "## エラーと次の1手")),
        **_table(_section(_read(CUE_GUIDE), "## 検査と表示")),
    }
    codes = set().union(*(_public_codes(module) for module in CUE_MODULES))
    assert {"ASSURANCE_REQUIRED", "ASSURANCE_NOT_WRITTEN", "CUE_INVALID", "EXPLANATION_SKELETON"} <= codes
    missing = sorted(code for code in codes if code not in documented)
    assert missing == []
    assert [code for code in codes if not documented[code][-1]] == []


def test_the_cue_guide_code_table_matches_the_codes_the_check_returns() -> None:
    rows = _table(_section(_read(CUE_GUIDE), "## 検査と表示"))
    codes = _public_codes(scope_check) | _public_codes(canonical_scope_check)
    assert set(rows) == codes
    assert [code for code, cells in rows.items() if not cells[-1]] == []
    for code, (exit_code, _step) in scope_check._TOOL_STEPS.items():
        assert rows[code][1].startswith(f"止まる（{exit_code}）"), (code, rows[code])


def test_the_cue_guide_says_leaf_help_lists_the_common_options() -> None:
    section = _section(_read(CUE_GUIDE), "## 検査と表示")
    assert "一覧には出ません" not in section
    assert "葉の `--help`" in section and "common options" in section


def test_the_canonical_table_binds_the_assurance_rows() -> None:
    rows = _table(_section(_read(DOCS / "canonical.md"), "## エラーと次の1手"))
    required = rows["ASSURANCE_REQUIRED"]
    assert required[1].startswith("2") and "--assurance <値>" in required[2] and "--assurance-reason" in required[2]
    assert rows["ASSURANCE_NOT_WRITTEN"][1].startswith("警告") and "requirement.cue" in rows["ASSURANCE_NOT_WRITTEN"][2]
    outdated = rows["SCOPE_TEMPLATES_OUTDATED"]
    assert outdated[1].startswith("3") and "spec-dock installation update" in outdated[2]


def test_the_canonical_table_names_the_partial_finish_after_a_reopen() -> None:
    row = _table(_section(_read(DOCS / "canonical.md"), "## エラーと次の1手"))["SCOPE_CHECK_FAILED"]
    assert "6（partial" in row[1] and "開き直" in row[1]


def test_the_kind_change_recovery_recreates_a_cue_scope_without_a_format_conflict() -> None:
    row = _table(_section(_read(DOCS / "canonical.md"), "## エラーと次の1手"))["SCOPE_KIND_CHANGED"][-1]
    recovery = canonical_errors.SCOPE_KIND_CHANGED_RECOVERY
    for text in (row, recovery):
        assert "SCOPE_FORMAT_CONFLICT" in text and "--assurance" in text and "scope delete" in text
    assert "spec-dock scope delete <current ID>" in recovery and "requirement.cue" in recovery


def test_the_cue_guide_sample_passes_scope_check(tmp_path: Path) -> None:
    cue_executable()
    blocks = re.findall(r"```cue\n// (requirement|design|plan)\.cue\n(.*?)```", _read(CUE_GUIDE), re.DOTALL)
    assert [name for name, _ in blocks] == ["requirement", "design", "plan"]
    scope = tmp_path / "iss-00001"
    scope.mkdir()
    for name, body in blocks:
        (scope / f"{name}.cue").write_text(body, encoding="utf-8")
    (scope / "explanation.html").write_text(written_explanation(), encoding="utf-8")
    (scope / "report.md").write_text("# Result Summary\n", encoding="utf-8")
    report = check_scope_documents(scope, kind="issue", shown="iss-00001", repository_root=tmp_path, timeout=60.0)
    assert report.checked and report.errors == () and report.warnings == ()
    assert report.assurance.level == "standard"
    assert report.findings is not None and all(items == [] for items in report.findings.values())


def test_the_explanation_guide_states_the_shape_the_check_reads() -> None:
    guide = _read(EXPLANATION_GUIDE)
    for token in (SKELETON_MARKER, DESIGN_SYSTEM_CSS, DESIGN_SYSTEM_JS, 'id="ds-source"', "`title`", "ds-vendor-base"):
        assert token in guide, token
    rows = _table(_section(guide, "## 検査"))
    assert rows["EXPLANATION_MISSING"][1:] == ["誤り", "警告"]
    assert rows["EXPLANATION_SKELETON"][1:] == ["誤り", "警告"]
    assert rows["EXPLANATION_INVALID"][1:] == ["誤り", "誤り"]


@pytest.mark.parametrize("name", ["overview.md", "issue-plan.md", "scope-layering.md"])
def test_the_existing_guides_point_cue_scopes_to_the_assurance_level(name: str) -> None:
    text = _read(AUTHORING / name)
    section = _section(text, "## 保証レベル（CUE の Scope）") if name != "overview.md" else text
    assert "保証レベル" in section and "(cue.md)" in section and "Markdown の Scope" in section
    assert "requirement.cue" in section


@pytest.mark.parametrize("name", ["issue-plan.md", "scope-layering.md"])
def test_the_layer_guides_link_both_cue_guides_like_the_overview(name: str) -> None:
    section = _section(_read(AUTHORING / name), "## 保証レベル（CUE の Scope）")
    assert "(cue.md)" in section and "(explanation.md)" in section
    assert (ROOT / "spec-dock/docs/authoring" / name).read_bytes() == (AUTHORING / name).read_bytes()


def test_the_overview_links_both_new_guides_and_keeps_the_planning_level_for_markdown() -> None:
    overview = _read(AUTHORING / "overview.md")
    section = _section(overview, "## CUE の Scope と保証レベル")
    assert "(cue.md)" in section and "(explanation.md)" in section
    assert "## Planning Level" in overview and "Markdown の Scope" in _section(overview, "## Planning Level")


def test_historical_separates_the_old_assurance_from_the_assurance_level() -> None:
    text = _read(AUTHORING / "historical.md")
    assert "`.assurance.json`" in text and "保証レベル" in text and "(cue.md)" in text


def test_the_template_catalog_names_the_cue_set_and_its_arguments() -> None:
    text = _read(SCAFFOLD / "templates/README.md")
    section = _section(text, "## CUE の Scope の雛形")
    for kind in ("initiative", "epic", "issue"):
        assert f"`cue/{kind}/{{requirement.cue,design.cue,plan.cue,explanation.html,report.md}}`" in section
    for token in ("{{ASSURANCE_LEVEL}}", "{{ASSURANCE_REASON}}", "--assurance", "--assurance-reason"):
        assert token in section, token
    assert "SCOPE_TEMPLATES_OUTDATED" in section and "canonical モード" in section
    assert "../docs/authoring/cue.md" in section and "../docs/authoring/explanation.md" in section


def test_the_skill_carries_the_cue_section_for_canonical_mode() -> None:
    skill = _read(SKILL)
    section = _section(skill, "## CUE の Scope と説明資料")
    for token in (
        "--assurance",
        "--assurance-reason",
        "scope check",
        "scope render",
        "work finish",
        "plan.cue",
        "spec-dock/docs/authoring/cue.md",
        "spec-dock/docs/authoring/explanation.md",
        "canonical モード",
        "CANONICAL_NOT_MIGRATED",
    ):
        assert token in section, token
    assert (ROOT / ".agents/skills/spec-dock/SKILL.md").read_bytes() == SKILL.read_bytes()


def test_the_version_is_0_4_1_everywhere() -> None:
    project = re.search(r'^\[project\]\nname = "spec-dock"\nversion = "([^"]+)"', _read(ROOT / "pyproject.toml"), re.M)
    assert project is not None and project.group(1) == VERSION
    locked = re.search(r'\[\[package\]\]\nname = "spec-dock"\nversion = "([^"]+)"', _read(ROOT / "uv.lock"))
    assert locked is not None and locked.group(1) == VERSION
    for root in (SCAFFOLD, ROOT / "spec-dock"):
        assert _read(root / "system/spec-dock-version") == f"{VERSION}\n"


def test_the_release_notes_list_the_contract_changes_for_canonical_mode() -> None:
    section = _section(_read(DOCS / "migration.md"), "## 0.4.0 への更新")
    for token in (
        "spec-dock scope check",
        "spec-dock scope render",
        "--assurance",
        "--assurance-reason",
        "v0.17.1",
        "installation update",
        "canonical モード",
        "CANONICAL_NOT_MIGRATED",
        "authoring/cue.md",
    ):
        assert token in section, token
    readme = _read(ROOT / "README.md")
    assert "全55コマンド" in readme and "全53コマンド" not in readme
    assert "src/spec_dock/assets/spec_dock/docs/migration.md" in _section(readme, "## CUE の仕様（0.4.0）")
    cue_section = _section(readme, "## CUE の仕様（0.4.0）")
    assert "`cue`" in cue_section and "canonical モード" in cue_section


def test_the_inventory_ships_the_new_guides_and_accepts_the_previous_bytes() -> None:
    inventory = json.loads(_read(ASSETS / "static-inventory.json"))
    entries = {entry["path"]: entry for entry in inventory["files"]}
    for name in ("cue.md", "explanation.md"):
        entry = entries[f"spec-dock/docs/authoring/{name}"]
        data = (AUTHORING / name).read_bytes()
        # iss-00487 and iss-00489 rewrote cue.md after it first shipped; those earlier bytes are its known old versions.
        known_old = [CUE_GUIDE_ISS487_SHA256, CUE_GUIDE_FIRST_SHA256] if name == "cue.md" else []
        assert entry["sha256"] == hashlib.sha256(data).hexdigest() and entry["known_old_sha256"] == known_old
        assert (ROOT / "spec-dock/docs/authoring" / name).read_bytes() == data
    for path, previous in PREVIOUS_SHA256.items():
        entry = entries[path]
        assert any(old.startswith(previous) for old in entry["known_old_sha256"]), path
        assert not entry["sha256"].startswith(previous), path

"""The flattening copy of migrate.py: layout, path mapping and relative-link rewriting (AC-456-03, 04, 07)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re

import pytest

from spec_dock.cli import main as spec_dock_main
from tests.support.canonical_repo import add_worktree, clone, git
from tests.support.migration_repo import (
    EPIC as LEGACY_EPIC,
    INIT as LEGACY_INIT,
    ISSUE3,
    ISSUE4,
    LINKED_EXTRA,
    Legacy,
    Symlink,
    build_legacy,
    flat_path,
    linked_specs,
    merge_cut,
    meta,
    migrate_module,
    migrated,
    refs,
    snapshot,
    write_files,
)

SPEC = "spec-dock/initiatives"
INIT = "init-00001-alpha"
EPIC = f"{INIT}/epics/epic-00002-beta"
ISSUE = f"{EPIC}/issues/iss-00003-gamma"


def _metas(**extra: bytes) -> dict[str, bytes]:
    metas = {
        INIT: meta("initiative", "init-00001", "Alpha", "alpha", 1),
        EPIC: meta("epic", "epic-00002", "Beta", "beta", 2, parent="init-00001"),
        ISSUE: meta("issue", "iss-00003", "Gamma", "gamma", 3, parent="epic-00002"),
    }
    metas.update(extra)
    return metas


def test_scope_directories_follow_their_place_not_their_name() -> None:
    module = migrate_module()
    metas = _metas(**{
        f"{ISSUE}/discussions/iss-00009-not-a-scope": meta("issue", "iss-00009", "X", "x", 9),
        "init-local-00002-proto": meta("initiative", "init-local-00002", "Proto", "proto", 39),
        "init-local-00003-arch": meta("initiative", "init-local-00003", "Arch", "arch", 31),
    })
    layout = module.nested_layout(metas, {"init-local-00002": {"id": "init-00039", "number": 39, "how": "existing"}})
    assert layout.places == {
        INIT: "00000-00999/init-00001",
        EPIC: "00000-00999/epic-00002",
        ISSUE: "00000-00999/iss-00003",
        "init-local-00002-proto": "00000-00999/init-00039",
    }
    assert {item["code"] for item in layout.unmapped.values()} == {"FLATTEN_SCOPE_UNMAPPED"}
    assert set(layout.unmapped) == {"init-local-00003-arch"}


def test_ids_come_from_type_id_and_number_and_duplicates_are_unmapped() -> None:
    module = migrate_module()
    broken = {
        "init-00004-mismatch": meta("initiative", "init-00004", "M", "m", 5),
        "init-00006-wrong-kind": meta("epic", "init-00006", "W", "w", 6),
        "init-00007-bad-json": b"{",
        "init-01000-a": meta("initiative", "init-01000", "A", "a", 1000),
        "init-01000-b": meta("initiative", "init-01000", "B", "b", 1000),
        "init-100454-big": json.dumps({
            "type": "initiative",
            "id": "init-100454",
            "github": {"issue_number": 100454},
        }).encode(),
    }
    layout = module.nested_layout(broken, {})
    assert layout.places == {"init-100454-big": "100000-100999/init-100454"}
    codes = {path: item["code"] for path, item in layout.unmapped.items()}
    assert codes == {
        "init-00004-mismatch": "FLATTEN_SCOPE_UNMAPPED",
        "init-00006-wrong-kind": "FLATTEN_SCOPE_UNMAPPED",
        "init-00007-bad-json": "FLATTEN_SCOPE_UNMAPPED",
        "init-01000-a": "FLATTEN_DUPLICATE_ID",
        "init-01000-b": "FLATTEN_DUPLICATE_ID",
    }


def test_plan_places_scopes_to_be_created_at_a_pending_place() -> None:
    module = migrate_module()
    metas = {"init-local-00003-arch": meta("initiative", "init-local-00003", "Arch", "arch", 31)}
    layout = module.nested_layout(metas, {"init-local-00003": {"relative": "pending/init-local-00003"}})
    assert layout.places == {"init-local-00003-arch": "pending/init-local-00003"}
    assert layout.pending == {"init-local-00003-arch": "init-local-00003"}
    assert layout.unmapped == {}


def test_files_map_to_their_deepest_scope_and_child_layer_files_are_dropped_or_refused() -> None:
    module = migrate_module()
    flat = module.FlatMap(module.nested_layout(_metas(), {}))
    assert flat.file(f"{ISSUE}/artifacts/a.md") == "00000-00999/iss-00003/artifacts/a.md"
    assert (
        flat.file(f"{ISSUE}/discussions/iss-00009-x/notes.md")
        == "00000-00999/iss-00003/discussions/iss-00009-x/notes.md"
    )
    assert flat.file(f"{EPIC}/design.md") == "00000-00999/epic-00002/design.md"
    assert flat.file(f"{ISSUE}/.meta.json") == module.DROPPED
    assert flat.file(f"{EPIC}/issues/rules.md") == module.DROPPED
    assert flat.file(f"{INIT}/epics/rules.md") == module.DROPPED
    assert flat.file(f"{INIT}/epics/new-epic/requirement.md")["code"] == "FLATTEN_NESTED_FILE"
    assert flat.file(f"{EPIC}/issues/README.md")["code"] == "FLATTEN_NESTED_FILE"
    assert flat.file("README.md")["code"] == "FLATTEN_OUTSIDE_SCOPE"
    assert flat.place(f"{EPIC}/issues") == "00000-00999/epic-00002"
    assert flat.place(INIT) == "00000-00999/init-00001"
    assert flat.place("") == ""
    assert flat.place(f"{INIT}/epics/new-epic") is None


def _rewrite(module, payload: bytes, old: str, new: str, *, kind: str = "markdown", places=None, symlinks=None):
    flat = module.FlatMap(module.nested_layout(_metas(), {}))
    target = module.link_target(flat, symlinks or {})
    return module.rewrite_links(payload, kind=kind, old=f"{SPEC}/{old}", new=f"{SPEC}/{new}", target=target)


def test_markdown_links_follow_the_new_depth_and_keep_suffixes() -> None:
    module = migrate_module()
    text = (
        "詳細: [Guide](../../../../../../docs/authoring/design.md)\n"
        "[parent](../../requirement.md#goal) [own](requirement.md) [art](artifacts/a.md)\n"
        "[issues](../) [repo](../../../../../../../docs/x/README.md)\n"
        "[web](https://example.com/a) [anchor](#here) [abs](/etc/hosts)\n"
        '![img](<../../artifacts/p.png> "title")\n'
        "[ref]: ../../design.md\n"
    )
    payload, links = _rewrite(module, text.encode(), f"{ISSUE}/design.md", "00000-00999/iss-00003/design.md")
    assert payload.decode() == (
        "詳細: [Guide](../../../docs/authoring/design.md)\n"
        "[parent](../epic-00002/requirement.md#goal) [own](requirement.md) [art](artifacts/a.md)\n"
        "[issues](../epic-00002/) [repo](../../../../docs/x/README.md)\n"
        "[web](https://example.com/a) [anchor](#here) [abs](/etc/hosts)\n"
        '![img](<../epic-00002/artifacts/p.png> "title")\n'
        "[ref]: ../epic-00002/design.md\n"
    )
    assert sum(1 for link in links if link.rewritten) == 6


def test_links_inside_code_are_left_alone() -> None:
    module = migrate_module()
    text = (
        "```text\n[a](../../requirement.md)\n```\n"
        "~~~\n[b](../../requirement.md)\n~~~\n"
        "`[c](../../requirement.md)` and ``[d](../../x.md) ` `` then [e](../../requirement.md)\n"
    )
    payload, _ = _rewrite(module, text.encode(), f"{ISSUE}/plan.md", "00000-00999/iss-00003/plan.md")
    assert payload.decode() == text.replace("[e](../../requirement.md)", "[e](../epic-00002/requirement.md)")


def test_symlinks_and_links_to_dropped_rules_point_at_the_final_target() -> None:
    module = migrate_module()
    symlinks = {f"{EPIC}/issues/rules.md": b"../../../../../docs/rules/epic/issues.md"}
    payload, links = _rewrite(
        module,
        b"../../../../../../../docs/rules/issue/artifacts.md",
        f"{ISSUE}/artifacts/rules.md",
        "00000-00999/iss-00003/artifacts/rules.md",
        kind="symlink",
    )
    assert payload == b"../../../../docs/rules/issue/artifacts.md"
    assert links[0].after == "spec-dock/docs/rules/issue/artifacts.md"
    payload, _ = _rewrite(
        module,
        b"[rules](../rules.md)",
        f"{EPIC}/design.md",
        "00000-00999/epic-00002/design.md",
        symlinks=symlinks,
    )
    assert payload == b"[rules](../rules.md)"  # the Initiative's epics/rules.md has no known final target: kept
    payload, links = _rewrite(
        module, b"[rules](issues/rules.md)", f"{EPIC}/design.md", "00000-00999/epic-00002/design.md", symlinks=symlinks
    )
    assert payload == b"[rules](../../../docs/rules/epic/issues.md)"


def test_html_href_and_src_are_rewritten_too() -> None:
    module = migrate_module()
    text = '<a href="../../../requirement.md">x</a><img src=\'../../../artifacts/i.png\'><a href="#top">t</a>'
    payload, _ = _rewrite(
        module,
        text.encode(),
        f"{ISSUE}/artifacts/20261029t000001z--guide.html",
        "00000-00999/iss-00003/artifacts/20261029t000001z--guide.html",
        kind="html",
    )
    assert payload.decode() == (
        "<a href=\"../../epic-00002/requirement.md\">x</a><img src='../../epic-00002/artifacts/i.png'>"
        '<a href="#top">t</a>'
    )


def test_unmappable_targets_stay_and_the_report_separates_new_and_old_breakage() -> None:
    module = migrate_module()
    payload, links = _rewrite(
        module,
        b"[gone](../../../../epics/new-epic/x.md) [old](missing.md) [ok](../../design.md)",
        f"{ISSUE}/plan.md",
        "00000-00999/iss-00003/plan.md",
    )
    assert payload == b"[gone](../../../../epics/new-epic/x.md) [old](missing.md) [ok](../epic-00002/design.md)"
    before = module.PathSet([
        f"{SPEC}/{INIT}/epics/new-epic/x.md",
        f"{SPEC}/{EPIC}/design.md",
    ])
    after = module.PathSet([f"{SPEC}/00000-00999/epic-00002/design.md"])
    report = module.link_report(links, before, after)
    assert report.rewritten == 1
    assert [item["text"] for item in report.unrewritable] == ["../../../../epics/new-epic/x.md"]
    assert [item["text"] for item in report.broken_before] == ["missing.md"]


def test_nest_map_reverses_the_flat_places() -> None:
    module = migrate_module()
    nest = module.NestMap({"init-00001": INIT, "epic-00002": EPIC, "iss-00003": ISSUE})
    assert nest.file("00000-00999/iss-00003/plan.md") == f"{ISSUE}/plan.md"
    assert nest.place("00000-00999/epic-00002") == EPIC
    assert nest.place("00000-00999") is None
    assert nest.file("01000-01999/iss-00003/plan.md")["code"] == "CATALOG_PATH_OUTSIDE_SCOPE"
    target = module.link_target(nest, {})
    payload, _ = module.rewrite_links(
        b"[p](../epic-00002/requirement.md) [g](../../../docs/authoring/plan.md)",
        kind="markdown",
        old=f"{SPEC}/00000-00999/iss-00003/plan.md",
        new=f"{SPEC}/{ISSUE}/plan.md",
        target=target,
    )
    assert payload == b"[p](../../requirement.md) [g](../../../../../../docs/authoring/plan.md)"


@pytest.mark.parametrize("kind", ["markdown", "html"])
def test_undecodable_documents_are_copied_unchanged(kind: str) -> None:
    module = migrate_module()
    payload, links = _rewrite(module, b"\xff[x](../../a.md)", f"{ISSUE}/a.md", "00000-00999/iss-00003/a.md", kind=kind)
    assert payload == b"\xff[x](../../a.md)" and links == []


# --- end to end on a repository with links (AC-456-04, 05 in small, 06, 07, 11) --------------------------------

_MD_LINK = re.compile(r"\]\(\s*<?([^)\s>]+)")
_HTML_LINK = re.compile(r"""(?:href|src)=["']([^"']+)""")


def _opened_links(root: Path) -> dict[str, list[str]]:
    """Independent check: every relative link under root, opened as the checkout shows it. Returns broken ones."""
    broken: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            if not path.exists():  # the operating system follows the link from its real place
                broken.setdefault(relative, []).append(str(path.readlink()))
            continue
        if not path.is_file() or path.suffix not in (".md", ".html"):
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for value in (_MD_LINK if path.suffix == ".md" else _HTML_LINK).findall(text):
            if re.match(r"^[a-z]+:", value) or value.startswith(("#", "/")):
                continue
            candidate = Path(os.path.normpath(path.parent / value.split("#")[0]))
            if not candidate.exists():
                broken.setdefault(relative, []).append(value)
    return broken


def _linked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> Legacy:
    legacy = migrated(tmp_path, monkeypatch, specs=linked_specs(), extra=LINKED_EXTRA)
    merge_cut(legacy)
    code, result = legacy.run("move-local", str(legacy.main), apply=True)
    assert code == 0, result
    capsys.readouterr()
    assert spec_dock_main(["--project", str(legacy.main), "canonical", "link", "--no-schedule", "--json"]) == 0
    capsys.readouterr()
    return legacy


def test_every_link_of_a_linked_tree_opens_through_the_flat_catalog(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "before").mkdir()
    (tmp_path / "after").mkdir()
    before = build_legacy(tmp_path / "before", monkeypatch, specs=linked_specs(), extra=LINKED_EXTRA)
    assert _opened_links(before.main / SPEC) == {}  # the fixture's links all open before the migration
    capsys.readouterr()
    assert spec_dock_main(["--project", str(before.main), "workspace", "validate", "--json"]) == 0, capsys.readouterr()
    legacy = _linked(tmp_path / "after", monkeypatch, capsys)
    build = next(item for item in legacy.outputs if item["command"] == "build-canonical")
    assert build["data"]["flatten"]["links"]["unrewritable"] == []
    assert build["data"]["flatten"]["links"]["rewritten"] >= 20
    catalog = legacy.main / SPEC
    assert catalog.is_symlink()
    assert _opened_links(catalog) == {}
    design = (catalog / flat_path(ISSUE3) / "design.md").read_text(encoding="utf-8")
    assert "詳細: [Design Guide](../../../docs/authoring/design.md)" in design
    assert "[Epic requirement](../epic-00002/requirement.md#scope)" in design
    assert "[siblings](../epic-00002/)" in design
    assert "[Delta](../iss-00004/requirement.md)" in design
    assert "[Proto epic](../epic-00005/design.md)" in design
    assert "[Repository guide](../../../../docs/guide.md)" in design
    assert "[Own plan](plan.md)" in design
    assert "```text\n[example](../../requirement.md)\n```" in design  # code is not a link
    note = (catalog / flat_path(LEGACY_EPIC) / "artifacts/20261029t000000z--note.md").read_text(encoding="utf-8")
    assert (
        note
        == "[issues](..) [rules](../../../../docs/rules/epic/issues.md) [initiative](../../init-00001/requirement.md)\n"
    )
    guide = (catalog / flat_path(ISSUE3) / "artifacts/20261029t000001z--guide.html").read_text(encoding="utf-8")
    assert guide.startswith("<a href=\"../../epic-00002/requirement.md\">Epic</a> <img src='../plan.md'>")
    assert (
        str((catalog / flat_path(ISSUE3) / "artifacts/rules.md").readlink())
        == "../../../../docs/rules/issue/artifacts.md"
    )
    assert (
        not (catalog / flat_path(LEGACY_INIT) / "epics").exists()
        and not (catalog / flat_path(LEGACY_EPIC) / "issues").exists()
    )
    assert (
        catalog / flat_path(ISSUE3) / "discussions/iss-00099-topic/notes.md"
    ).read_bytes() == b"[plan](../../plan.md)\n"


def test_unrewritable_links_are_listed_by_plan_and_build_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specs = linked_specs()
    specs[f"{ISSUE4}/plan.md"] = b"[metadata](.meta.json) [broken](nowhere.md)\n"
    legacy = build_legacy(tmp_path, monkeypatch, specs=specs, extra=LINKED_EXTRA)
    code, result = legacy.run("plan")
    assert code == 0, result
    links = result["data"]["flatten"]["links"]
    assert [(item["file"], item["text"]) for item in links["unrewritable"]] == [
        (f"{SPEC}/{flat_path(ISSUE4)}/plan.md", ".meta.json")
    ]
    assert [item["text"] for item in links["broken_before"]] == ["nowhere.md"]
    assert any(".meta.json" in warning for warning in result["warnings"])
    assert legacy.run("register", apply=True)[0] == 0
    code, result = legacy.run("build-canonical")
    assert code == 0 and result["data"]["flatten"]["links"]["unrewritable"][0]["text"] == ".meta.json"


def test_plan_before_register_places_local_scopes_by_the_plan_and_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch, specs=linked_specs(), extra=LINKED_EXTRA)
    objects = git(legacy.main, "count-objects", "-v")
    before = snapshot(legacy)
    code, result = legacy.run("plan")
    assert code == 0, result
    assert result["data"]["flatten"]["problems"] == []
    assert result["data"]["flatten"]["pending"] == {"init-local-00003-architecture": "init-local-00003"}
    assert result["data"]["flatten"]["links"]["unrewritable"] == []
    assert snapshot(legacy) == before
    assert git(legacy.main, "count-objects", "-v") == objects


def test_move_local_rewrites_moved_links_and_refuses_files_without_a_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = migrated(tmp_path, monkeypatch, specs=linked_specs(), extra=LINKED_EXTRA)
    merge_cut(legacy)
    write_files(legacy.main, {f"{LEGACY_INIT}/epics/loose.md": b"stray\n"})
    code, result = legacy.run("move-local", str(legacy.main), apply=True)
    assert code == 2 and "no place" in result["error"]
    assert not (legacy.main / "spec-dock/.canonical").exists()
    (legacy.main / LEGACY_INIT / "epics/loose.md").unlink()
    write_files(
        legacy.main,
        {
            f"{ISSUE3}/.workbench/note.md": b"[epic](../../../requirement.md)\n",
            f"{ISSUE3}/.workbench/epic-link": Symlink("../../../design.md"),
        },
    )
    code, result = legacy.run("move-local", str(legacy.main), apply=True)
    assert code == 0, result
    moved = legacy.main / "spec-dock/.canonical" / flat_path(ISSUE3) / ".workbench"
    assert (moved / "note.md").read_bytes() == b"[epic](../../epic-00002/requirement.md)\n"
    assert str((moved / "epic-link").readlink()) == "../../epic-00002/design.md"


def test_adopt_worktree_removes_files_whose_links_were_rewritten_and_refuses_unflattenable_specs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = migrated(tmp_path, monkeypatch, specs=linked_specs(), extra=LINKED_EXTRA)
    feature = add_worktree(legacy.main, tmp_path / "feature", "feature")
    write_files(feature, {f"{ISSUE3}/plan.md": b"[epic](../../requirement.md) edited\n"})
    stray = add_worktree(legacy.main, tmp_path / "stray", "stray")
    write_files(stray, {f"{LEGACY_EPIC}/issues/loose.md": b"stray\n"})
    merge_cut(legacy)
    before = refs(legacy.remote)
    code, result = legacy.run("adopt-worktree", str(stray), apply=True)
    assert code == 2 and "cannot be flattened" in result["error"]
    assert refs(legacy.remote) == before and (stray / LEGACY_EPIC / "issues/loose.md").exists()
    code, result = legacy.run("adopt-worktree", str(feature), apply=True)
    assert code == 0, result
    assert result["data"]["mismatched"] == []
    assert f"{ISSUE3}/design.md" in result["data"]["delete"]  # its links were rewritten, still equal after the copy
    plan = git(legacy.remote, "show", f"spec-dock/canonical:{flat_path(ISSUE3)}/plan.md")
    assert plan == "[epic](../epic-00002/requirement.md) edited"
    assert not (feature / ISSUE3 / "design.md").exists()


def test_export_legacy_nests_back_with_the_original_links_and_new_scope_slugs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    legacy = _linked(tmp_path, monkeypatch, capsys)
    fake = legacy.github
    catalog = legacy.main / SPEC
    japanese = fake.scope("issue", title="日本語の題名", parent=2)
    english = fake.scope("issue", title="Add Refresh Token", parent=2)
    for issue in (japanese, english):
        folder = catalog / migrate_module().scope_relative(f"iss-{issue.number:05d}")
        write_files(
            folder, {name: f"# {name}\n".encode() for name in ("requirement.md", "design.md", "plan.md", "report.md")}
        )
        write_files(folder, {"artifacts/rules.md": Symlink("../../../../docs/rules/issue/artifacts.md")})
    git(catalog, "add", "-A")
    git(catalog, "commit", "-qm", "new scopes")
    git(catalog, "push", "-q", "origin", "HEAD:spec-dock/canonical")
    code, result = legacy.run("export-legacy", apply=True)
    assert code == 0, result
    assert result["data"]["links"]["unrewritable"] == []
    checkout = clone(legacy.remote, tmp_path / "exported", "--branch", "spec-dock/export-legacy")
    new_japanese = f"{LEGACY_EPIC}/issues/iss-{japanese.number:05d}-untitled"
    new_english = f"{LEGACY_EPIC}/issues/iss-{english.number:05d}-add-refresh-token"
    assert (checkout / new_japanese / ".meta.json").exists() and (checkout / new_english / ".meta.json").exists()
    assert json.loads((checkout / new_japanese / ".meta.json").read_text())["title"] == "日本語の題名"
    original = linked_specs()
    for path, payload in original.items():
        if path.endswith(".meta.json") or "init-local-" in path:
            continue
        exported = checkout / path
        if isinstance(payload, Symlink):
            assert str((exported).readlink()) == str(payload), path
        elif (
            path == f"{LEGACY_EPIC}/artifacts/20261029t000000z--note.md"
        ):  # epics/ and rules.md targets return as their equivalents
            assert (
                exported.read_bytes()
                == b"[issues](..) [rules](../../../../../docs/rules/epic/issues.md) [initiative](../../../requirement.md)\n"
            )
        elif path == f"{ISSUE3}/design.md":  # the issues/ directory comes back as its Epic directory
            expected = payload.replace(b"[siblings](../)", b"[siblings](../../)")
            assert exported.read_bytes() == expected.replace(b"init-local-00002-proto", b"init-00039-proto")
        else:
            assert exported.read_bytes() == payload, path
    assert (
        checkout / new_english / "artifacts/rules.md"
    ).readlink().as_posix() == "../../../../../../../docs/rules/issue/artifacts.md"
    assert str((checkout / LEGACY_EPIC / "issues/rules.md").readlink()) == "../../../../../docs/rules/epic/issues.md"
    assert _opened_links(checkout / SPEC) == {}
    capsys.readouterr()
    assert spec_dock_main(["--project", str(checkout), "workspace", "validate", "--json"]) == 0, capsys.readouterr().out


@pytest.mark.parametrize("problem", ["parentless-epic", "directory-without-issue", "kind-changed"])
def test_export_legacy_stops_before_writing_when_the_catalog_cannot_nest_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], problem: str
) -> None:
    legacy = _linked(tmp_path, monkeypatch, capsys)
    fake = legacy.github
    catalog = legacy.main / SPEC
    expected = {
        "parentless-epic": "PARENT_MISSING",
        "directory-without-issue": "SCOPE_ISSUE_MISSING",
        "kind-changed": "SCOPE_KIND_CHANGED",
    }[problem]
    if problem == "parentless-epic":
        fake.set_parent(2, None)
    elif problem == "directory-without-issue":
        write_files(catalog, {"00000-00999/iss-00777/requirement.md": b"# orphan\n"})
        git(catalog, "add", "-A")
        git(catalog, "commit", "-qm", "orphan")
        git(catalog, "push", "-q", "origin", "HEAD:spec-dock/canonical")
    else:
        fake.issue(4).labels = ["spec-dock:epic"]
    before = refs(legacy.remote)
    for apply in (False, True):
        code, result = legacy.run("export-legacy", apply=apply)
        assert code == 2, result
        assert expected in {item["code"] for item in result["anomalies"]}
    assert refs(legacy.remote) == before


def test_a_lone_backtick_does_not_hide_links_in_later_paragraphs() -> None:
    module = migrate_module()
    text = "Press the ` key.\n\n[epic](../../requirement.md) and `code`\n"
    payload, links = _rewrite(module, text.encode(), f"{ISSUE}/plan.md", "00000-00999/iss-00003/plan.md")
    assert payload.decode() == "Press the ` key.\n\n[epic](../epic-00002/requirement.md) and `code`\n"
    assert [link.text for link in links] == ["../../requirement.md"]

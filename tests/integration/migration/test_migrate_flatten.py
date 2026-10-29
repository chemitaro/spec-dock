"""The flattening copy of migrate.py: layout, path mapping and relative-link rewriting (AC-456-03, 04, 07)."""

from __future__ import annotations

import json

import pytest

from tests.support.migration_repo import meta, migrate_module

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
        "init-100454-big": json.dumps({"type": "initiative", "id": "init-100454", "github": {"issue_number": 100454}}).encode(),
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
    assert flat.file(f"{ISSUE}/discussions/iss-00009-x/notes.md") == "00000-00999/iss-00003/discussions/iss-00009-x/notes.md"
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
        "![img](<../../artifacts/p.png> \"title\")\n"
        "[ref]: ../../design.md\n"
    )
    payload, links = _rewrite(module, text.encode(), f"{ISSUE}/design.md", "00000-00999/iss-00003/design.md")
    assert payload.decode() == (
        "詳細: [Guide](../../../docs/authoring/design.md)\n"
        "[parent](../epic-00002/requirement.md#goal) [own](requirement.md) [art](artifacts/a.md)\n"
        "[issues](../epic-00002/) [repo](../../../../docs/x/README.md)\n"
        "[web](https://example.com/a) [anchor](#here) [abs](/etc/hosts)\n"
        "![img](<../epic-00002/artifacts/p.png> \"title\")\n"
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
        module, text.encode(), f"{ISSUE}/artifacts/guide.html", "00000-00999/iss-00003/artifacts/guide.html", kind="html"
    )
    assert payload.decode() == (
        '<a href="../../epic-00002/requirement.md">x</a><img src=\'../../epic-00002/artifacts/i.png\'>'
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

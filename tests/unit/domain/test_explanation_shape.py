"""The thin explanation shape of contract K5 (epic-00425): what `scope check` accepts in explanation.html."""

from __future__ import annotations

from pathlib import Path

import pytest

from spec_dock.runtime.domain.explanation_shape import SKELETON_MARKER, inspect_explanation

SKELETON = (
    Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/design-system/explanation-skeleton.html"
)


def skeleton() -> str:
    return SKELETON.read_text(encoding="utf-8")


def written() -> str:
    """The skeleton after its author removed the marker line."""
    return skeleton().replace(SKELETON_MARKER + "\n", "")


def test_the_shipped_skeleton_has_the_shape_and_is_still_a_skeleton() -> None:
    shape = inspect_explanation(skeleton())
    assert (shape.skeleton, shape.problems) == (True, ())


def test_removing_the_marker_leaves_a_written_explanation() -> None:
    shape = inspect_explanation(written())
    assert (shape.skeleton, shape.problems) == (False, ())


@pytest.mark.parametrize(
    ("change", "fragment"),
    [
        (
            lambda text: text.replace('<script type="text/markdown" id="ds-source">', "<div>", 1).replace(
                "</script>\n<script src", "</div>\n<script src", 1
            ),
            "ds-source",
        ),
        (
            lambda text: text.replace(
                "</head>", '<script type="text/markdown" id="ds-source">\n---\ntitle: b\n---\n</script></head>'
            ),
            "ds-source",
        ),
        (lambda text: text.replace("title: この Scope", "name: この Scope", 1), "title"),
        (lambda text: text.replace("title: この Scope の説明資料（題名を書き換えます）", "title:   ", 1), "title"),
        (lambda text: text.replace("\n---\ntitle:", "\ntitle:", 1), "title"),
        (lambda text: text.replace('<link rel="stylesheet" href="../../../design-system/ds.css">', ""), "ds.css"),
        (lambda text: text.replace("../../../design-system/ds.css", "ds.css"), "ds.css"),
        (lambda text: text.replace('<script src="../../../design-system/ds.js"></script>', ""), "ds.js"),
    ],
    ids=["no-source", "two-sources", "no-title-key", "blank-title", "no-front-matter", "no-css", "other-css", "no-js"],
)
def test_each_broken_shape_is_a_problem(change: object, fragment: str) -> None:
    text = change(written())  # type: ignore[operator]
    assert text != written()
    shape = inspect_explanation(text)
    assert shape.problems, text
    assert any(fragment in problem for problem in shape.problems), shape.problems


def test_attribute_order_and_extra_attributes_do_not_matter() -> None:
    text = (
        written()
        .replace(
            '<script type="text/markdown" id="ds-source">', '<script id="ds-source" data-x="1" type="text/markdown">'
        )
        .replace(
            '<link rel="stylesheet" href="../../../design-system/ds.css">',
            '<link href="../../../design-system/ds.css" rel="preload stylesheet">',
        )
    )
    assert inspect_explanation(text).problems == ()


def test_a_marker_outside_the_markdown_does_not_make_a_skeleton() -> None:
    text = written().replace("<body></body>", f"<body>{SKELETON_MARKER}</body>")
    assert inspect_explanation(text).skeleton is False


def test_without_a_markdown_block_the_marker_anywhere_still_counts() -> None:
    text = skeleton().replace('id="ds-source"', 'id="other"')
    shape = inspect_explanation(text)
    assert shape.skeleton is True and shape.problems

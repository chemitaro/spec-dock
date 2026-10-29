"""Pure rules for Scope directories written in canonical mode."""

from __future__ import annotations

from spec_dock.runtime.domain.canonical_scaffold import strip_structure_front_matter


def test_title_and_parent_lines_leave_the_front_matter_only() -> None:
    text = (
        "---\n"
        '種別: 要件定義書（Issue）\n'
        'ID: "iss-00012"\n'
        'タイトル: "Leaf"\n'
        '状態: "draft"\n'
        '親: ["epic-00002", "init-00001"]\n'
        "---\n"
        "\n"
        "# iss-00012 Leaf — 要件定義\n"
        "親: body lines stay\n"
        "タイトル: also in the body\n"
    )
    assert strip_structure_front_matter(text) == (
        "---\n"
        '種別: 要件定義書（Issue）\n'
        'ID: "iss-00012"\n'
        '状態: "draft"\n'
        "---\n"
        "\n"
        "# iss-00012 Leaf — 要件定義\n"
        "親: body lines stay\n"
        "タイトル: also in the body\n"
    )


def test_text_without_a_closed_front_matter_is_unchanged() -> None:
    for text in ("# Title\nタイトル: x\n", "---\nタイトル: x\n", "", "--- \nタイトル: x\n---\n"):
        assert strip_structure_front_matter(text) == text


def test_crlf_front_matter_is_handled_line_by_line() -> None:
    assert strip_structure_front_matter('---\r\nID: "a"\r\nタイトル: "b"\r\n---\r\nbody\r\n') == (
        '---\r\nID: "a"\r\n---\r\nbody\r\n'
    )

"""The page of one CUE Scope (iss-00476): fixed order, links both ways, status counts, escaping, thin HTML shape."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
from typing import Any

from spec_dock.runtime.domain.explanation_shape import inspect_explanation
from spec_dock.runtime.presentation.envelope import Diagnostic
from spec_dock.runtime.presentation.spec_page import number_key, plain, spec_markdown, wrap_page

SAMPLES = Path(__file__).resolve().parents[2] / "fixtures/cue/v1/samples"


def evaluation(sample: str) -> dict[str, Any]:
    return json.loads((SAMPLES / sample / "expected.json").read_text(encoding="utf-8"))["export"]


def markdown(value: dict[str, Any] | None, *, errors: tuple[Diagnostic, ...] = (), title: str | None = "題名") -> str:
    assurance = value.get("assurance") if value else None
    return spec_markdown(scope_id="iss-00003", title=title, evaluation=value, assurance=assurance, errors=errors)


def source_of(page: str) -> str:
    match = re.search(r'<script type="text/markdown" id="ds-source">\n(.*?)\n</script>', page, re.DOTALL)
    assert match is not None
    return match.group(1)


def reorder(value: object) -> object:
    if isinstance(value, dict):
        return {key: reorder(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [reorder(item) for item in value]
    return value


def test_sections_come_in_the_fixed_order() -> None:
    text = markdown(evaluation("issue-strict-complete"))
    headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
    assert headings == ["検査の結果", "保証レベル", "要件", "失敗・境界条件", "設計", "計画"]
    order = [text.index(f'id="{key}"') for key in ("R-01", "F-01", "D-01", "D-02", "S-01", "S-02", "S-03", "T-01")]
    assert order == sorted(order)
    assert text.startswith("---\ntitle: iss-00003 題名\n")
    assert "status: 保証レベル strict" in text


def test_the_same_evaluation_in_another_key_order_gives_the_same_markdown() -> None:
    value = evaluation("issue-strict-complete")
    assert markdown(value) == markdown(copy.deepcopy(value)) == markdown(reorder(value))  # type: ignore[arg-type]


def test_numbers_sort_by_their_value() -> None:
    assert sorted(["R-100", "R-99", "R-02", "R-10"], key=number_key) == ["R-02", "R-10", "R-99", "R-100"]
    value = evaluation("issue-light-minimal")
    value["requirements"] = {key: {"title": key} for key in ("R-100", "R-99", "R-02")}
    text = markdown(value)
    assert text.index('id="R-02"') < text.index('id="R-99"') < text.index('id="R-100"')


def test_requirements_link_to_what_satisfies_them_and_back() -> None:
    text = markdown(evaluation("issue-strict-complete"))
    requirement = text[text.index('id="R-01"') : text.index("## 失敗・境界条件")]
    for line in ("- 設計：[D\\-01](#D-01)", "- 手順：[S\\-01](#S-01)", "- テスト：[T\\-01](#T-01)"):
        assert line in requirement
    design = text[text.index('id="D-01"') : text.index('id="D-02"')]
    assert "- 満たすもの：[R\\-01](#R-01)" in design
    assert "- 先にする手順：[S\\-01](#S-01)" in text


def test_a_missing_number_is_not_a_link() -> None:
    text = markdown(evaluation("issue-standard-gaps"))
    assert "R\\-03（ない番号）" in text
    assert "](#R-03)" not in text


def test_an_epic_links_requirements_to_its_slices() -> None:
    text = markdown(evaluation("epic-standard-uncovered"))
    assert '<h3 id="slice-iss-00011">iss-00011</h3>' in text
    assert "- 切り分け：[iss\\-00011](#slice-iss-00011)" in text
    assert "- 先にする切り分け：[iss\\-00011](#slice-iss-00011)" in text
    assert "- 手順：" not in text and "進み具合" not in text


def test_findings_and_errors_come_first_with_their_hints() -> None:
    error = Diagnostic(
        "CUE_INVALID",
        'requirements."R-01".title: incomplete',
        {"file": "x/requirement.cue", "line": 3, "field": 'requirements."R-01".title', "hint": "Write it"},
    )
    text = markdown(evaluation("issue-standard-gaps"), errors=(error,))
    results = text[text.index("## 検査の結果") : text.index("## 保証レベル")]
    assert "**CUE\\_INVALID**" in results and "直し方：Write it" in results
    assert "### requirement\\-without\\-design" in results
    assert "- [R\\-02](#R-02)：R\\-02 を満たす設計がありません" in results
    assert "直し方：design\\.cue の design" in results
    assert "### requirement\\-without\\-step" not in results  # an empty rule is not shown
    assert "誤りと指摘はありません。" in markdown(evaluation("issue-strict-complete"))


def test_without_an_evaluation_only_the_check_results_are_shown() -> None:
    error = Diagnostic("SCOPE_FORMAT_CONFLICT", "both", {"file": "x"})
    text = markdown(None, errors=(error,))
    assert re.findall(r"^## (.+)$", text, re.MULTILINE) == ["検査の結果"]
    assert "status: 保証レベル 未確定" in text and "本文は描いていません" in text


def test_steps_show_their_status_and_the_counts() -> None:
    text = markdown(evaluation("issue-strict-complete"))
    assert "| まだ | 0 |\n| 作業中 | 1 |\n| 済み | 1 |\n| 取り下げ | 1 |\n| 全体 | 3 |" in text
    step = text[text.index('id="S-02"') : text.index('id="S-03"')]
    assert "- 状態：作業中" in step


def test_text_fields_stay_markdown_and_other_values_are_escaped() -> None:
    value = evaluation("issue-light-minimal")
    value["purpose"] = "**太字** と `code` と <i>斜体</i>"
    value["requirements"] = {"R-01": {"title": "<b>&|*_ 題名", "text": "- 項目\n- 項目2"}}
    value["steps"] = {"S-01": {"title": "手順", "realizes": ["R-01"], "status": "todo", "session": "a|b<c>"}}
    value["extra"] = {"note": "<x>"}
    text = markdown(value)
    assert "**太字** と `code` と <i>斜体</i>" in text
    assert '<h3 id="R-01">R-01 &lt;b&gt;&amp;|*_ 題名</h3>' in text
    assert "- 項目\n- 項目2" in text
    assert "- セッション：a\\|b\\<c\\>" in text
    assert '"note": "\\u003cx>"' in text  # other fields are JSON, with < written as <


def test_nothing_can_end_the_script_block() -> None:
    value = evaluation("issue-light-minimal")
    value["purpose"] = "</script><script>alert(1)</script> <!-- <script> --> </SCRIPT >"
    value["requirements"] = {"R-01": {"title": "</script>", "text": "```\n</script>"}}
    value["extra"] = "</script><!--"
    page = wrap_page(markdown(value, title="</script> <!--"), title="t", design_system_base="ds/", vendor_base=None)
    source = source_of(page)
    assert not re.search(r"</script", source, re.IGNORECASE) and "<!--" not in source
    assert page.count("</script>") == 2  # the Markdown block and ds.js
    assert "```\n<\\/script>\n```" in source  # a fence left open is closed


def test_plain_escapes_every_ascii_mark_on_one_line() -> None:
    assert plain("a\nb  # [x](y) <z> & `q`") == "a b  \\# \\[x\\]\\(y\\) \\<z\\> \\& \\`q\\`"


def test_the_page_has_the_thin_explanation_shape() -> None:
    page = wrap_page(
        markdown(evaluation("issue-strict-complete")),
        title="iss-00003 題名",
        design_system_base="../../../design-system/",
        vendor_base=None,
    )
    shape = inspect_explanation(page)
    assert shape.problems == () and not shape.skeleton
    assert "ds-vendor-base" not in page
    assert page.count('id="ds-source"') == 1


def test_bases_join_and_vendor_meta() -> None:
    page = wrap_page(
        "---\ntitle: t\n---\n", title='a"<b>', design_system_base="/design-system", vendor_base='/vendor/"x'
    )
    assert '<link rel="stylesheet" href="/design-system/ds.css">' in page
    assert '<script src="/design-system/ds.js"></script>' in page
    assert '<meta name="ds-vendor-base" content="/vendor/&quot;x">' in page
    assert "<title>a&quot;&lt;b&gt;</title>" in page
    assert '<link rel="stylesheet" href="ds.css">' in wrap_page("", title="t", design_system_base="", vendor_base=None)


def test_the_front_matter_title_uses_full_width_marks_and_the_body_shows_the_exact_title() -> None:
    text = markdown(evaluation("issue-light-minimal"), title='"<img src=x onerror=alert(1)> *a* _b_ [c] `d` \\ & ~ |"')
    front = text.split("\n---\n", 1)[0]
    title = front.splitlines()[1]
    assert title == 'title: iss-00003 "＜img src=x onerror=alert(1)＞ ＊a＊ ＿b＿ ［c］ ｀d｀ ＼ ＆ ～ ｜'
    assert not set(title[len("title: ") :]) & set("<>&*_`[]\\~|")
    assert '題名：iss\\-00003 \\"\\<img src\\=x onerror\\=alert\\(1\\)\\>' in text


def test_a_comment_alone_is_kept_and_broken_only_beside_a_script_tag() -> None:
    value = evaluation("issue-light-minimal")
    value["purpose"] = "`<!-- 印 -->` を消す"
    assert "`<!-- 印 -->` を消す" in markdown(value)
    value["background"] = "<script>x</script>"
    text = markdown(value)
    assert "<!--" not in text and "`<!\\-- 印 -->`" in text


def test_an_id_that_is_not_a_number_is_plain_text() -> None:
    value = evaluation("issue-light-minimal")
    value["findings"] = {
        "rollback-missing": [{"id": "rollback", "message": "m"}],
        "x": [{"id": "Q-07", "message": "m"}],
    }
    text = markdown(value)
    assert "- rollback：m" in text and "Q\\-07（ない番号）" in text

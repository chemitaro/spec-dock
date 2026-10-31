"""The page of one CUE Scope (iss-00476; contract K5 of epic-00425): evaluation JSON -> Markdown -> thin HTML.

Pure functions: no `cue`, no files. `spec_markdown` lays the K1 evaluation out in a fixed order (check results,
assurance, requirements, failures, design, plan, other fields) and links every number both ways; `wrap_page`
puts the Markdown into the same thin HTML as an explanation (I-4), which `ds.js` draws in the browser.

Escaping: text fields (`#Text`) are Markdown and stay Markdown. Every other value is shown as text: backslash
escapes in Markdown, entity escapes inside the raw HTML headings. Nothing may end the `<script>` that holds
the Markdown: `</script` becomes `<\\/script` (ds.js turns it back) and `<!--` becomes `<!\\--`.
"""

from __future__ import annotations

import html
import json
import re
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence

    from spec_dock.runtime.presentation.envelope import Diagnostic

STATUS_LABELS: Final = {"todo": "まだ", "doing": "作業中", "done": "済み", "dropped": "取り下げ"}

_REQUIREMENT_SECTIONS: Final = (
    ("purpose", "目的"),
    ("background", "背景"),
    ("includes", "含めるもの"),
    ("excludes", "含めないもの"),
    ("constraints", "制約"),
    ("decisions", "決めたこと"),
    ("questions", "未解決のこと"),
)
_DESIGN_SECTIONS: Final = (
    ("goals", "設計の目標"),
    ("current", "今"),
    ("target", "目指す形"),
    ("compatibility", "互換性"),
    ("risks", "リスク"),
)
_PLAN_HEAD: Final = (("goal", "目標"),)
_PLAN_TAIL: Final = (("verification", "検証"), ("rollback", "戻し方"), ("exit", "終える条件"))
_NUMBERED: Final = ("requirements", "failures", "design", "steps", "tests", "slices")
_KNOWN_TOP: Final = frozenset(
    {"schema", "kind", "assurance", "findings", "execution", *_NUMBERED}
    | {key for key, _ in (*_REQUIREMENT_SECTIONS, *_DESIGN_SECTIONS, *_PLAN_HEAD, *_PLAN_TAIL)}
)
_KNOWN_FIELDS: Final = {
    "requirements": ("title", "text", "acceptance"),
    "failures": ("title", "text", "impact", "recovery"),
    "design": ("title", "text", "satisfies"),
    "steps": ("title", "text", "realizes", "status", "after", "session"),
    "tests": ("title", "text", "verifies"),
    "slices": ("covers", "text", "after", "session"),
    "sessions": ("task", "model", "effort", "rationale"),
    "reviews": ("role", "after", "model", "effort"),
}

_PUNCTUATION = re.compile(r"([!-/:-@\[-`{-~])")
_FULLWIDTH: Final = str.maketrans("\\`*_[]<>&~|", "＼｀＊＿［］＜＞＆～｜")
_NUMBER = re.compile(r"^([A-Za-z]+)-([0-9]+)$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_SCRIPT_END = re.compile(r"</(script)", re.IGNORECASE)
_SCRIPT_OPEN = re.compile(r"<script[\s/>]", re.IGNORECASE)


def plain(value: object) -> str:
    """A non-text value as Markdown text: one line, every ASCII punctuation mark backslash-escaped."""
    return _PUNCTUATION.sub(r"\\\1", _one_line(value))


def _one_line(value: object) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return " ".join(part.strip() for part in text.splitlines() if part.strip())


def _heading_text(value: object) -> str:
    return html.escape(_one_line(value), quote=True)


def _front_value(value: object) -> str:
    """A front matter value: one line, no edge quotes, Markdown and HTML marks as look-alike full-width marks.

    ds.js reads `title` both as inline Markdown (the cover, raw HTML passes) and as text (the bar, the footer,
    document.title); full-width marks look the same either way and never become an element or emphasis.
    """
    return _one_line(value).strip("\"'").translate(_FULLWIDTH)


def number_key(key: str) -> tuple[str, int, str]:
    """`R-100` after `R-99`: the prefix, the number as a number, then the key itself."""
    match = _NUMBER.match(key)
    if match is None:
        return (key, -1, key)
    return (match.group(1), int(match.group(2)), key)


def _numbered(items: object) -> list[tuple[str, Mapping[str, object]]]:
    if not isinstance(items, dict):
        return []
    return [(key, items[key]) for key in sorted(items, key=number_key) if isinstance(items[key], dict)]


def _text_block(value: object) -> str:
    """A text field as a Markdown block; a fence left open is closed so it cannot swallow the page."""
    if not isinstance(value, str):
        return plain(value)
    lines = value.strip("\n").splitlines()
    fence: str | None = None
    for line in lines:
        match = _FENCE.match(line)
        if match is None:
            continue
        mark = match.group(1)
        if fence is None:
            fence = mark
        elif mark[0] == fence[0] and len(mark) >= len(fence) and not match.group(2).strip():
            fence = None
    if fence is not None:
        lines.append(fence)
    return "\n".join(line.rstrip() for line in lines)


def _list_item(value: object, bullet: str = "- ") -> str:
    """One list item; the continuation lines of a text field are indented under the bullet."""
    block = _text_block(value).splitlines() or [""]
    indent = " " * len(bullet)
    return "\n".join([bullet + block[0], *[(indent + line) if line else "" for line in block[1:]]])


def _indent(block: str, prefix: str) -> str:
    return "\n".join((prefix + line) if line else "" for line in block.splitlines())


def _code_block(value: object) -> str:
    """Other fields as JSON in a fence longer than any backtick run inside; `<` is written as \\u003c."""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).replace("<", "\\u003c")
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}json\n{text}\n{fence}"


class _Links:
    """Which numbers exist, and who refers to each requirement and failure condition."""

    def __init__(self, evaluation: Mapping[str, object]) -> None:
        self.issue = evaluation.get("kind", "issue") == "issue"
        self.anchors: dict[str, str] = {}
        for field in ("requirements", "failures", "design", "steps", "tests"):
            for key, _ in _numbered(evaluation.get(field)):
                self.anchors[key] = key
        for key, _ in _numbered(evaluation.get("slices")):
            self.anchors[key] = f"slice-{key}"
        self.back: dict[str, dict[str, list[str]]] = {}
        for field, link in (
            ("design", "satisfies"),
            ("steps", "realizes"),
            ("tests", "verifies"),
            ("slices", "covers"),
        ):
            for key, item in _numbered(evaluation.get(field)):
                for target in _strings(item.get(link)):
                    if not isinstance(target, str):
                        continue
                    self.back.setdefault(target, {}).setdefault(field, []).append(key)

    def link(self, key: object) -> str:
        if isinstance(key, str) and key in self.anchors:
            return f"[{plain(key)}](#{self.anchors[key]})"
        if isinstance(key, str) and _NUMBER.match(key):
            return f"{plain(key)}（ない番号）"
        return plain(key)

    def links(self, keys: Iterable[object]) -> str:
        return "、".join(self.link(key) for key in keys) or "なし"


def _strings(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _heading(anchor: str, label: str, title: object | None) -> str:
    shown = _heading_text(label) if title is None else f"{_heading_text(label)} {_heading_text(title)}"
    return f'<h3 id="{html.escape(anchor, quote=True)}">{shown}</h3>'


def _extra(item: Mapping[str, object], known: Sequence[str]) -> list[str]:
    rest = {key: item[key] for key in sorted(item) if key not in known}
    return ["その他の項目：", _code_block(rest)] if rest else []


def _sections(evaluation: Mapping[str, object], pairs: Sequence[tuple[str, str]]) -> list[str]:
    out: list[str] = []
    for key, label in pairs:
        if key not in evaluation:
            continue
        value = evaluation[key]
        out.append(f"### {label}")
        if isinstance(value, list):
            out.append("\n".join(_list_item(item) for item in value) or "なし")
        else:
            out.append(_text_block(value))
    return out


def _labelled(label: str, value: str) -> str:
    return f"- {label}：{value}"


def _check_results(errors: Sequence[Diagnostic], evaluation: Mapping[str, object] | None, links: _Links) -> list[str]:
    out = ["## 検査の結果"]
    for error in errors:
        details = error.details
        place = " ".join(
            f"{name} {plain(details[name])}" for name in ("file", "line", "field") if details.get(name) is not None
        )
        line = f"- **{plain(error.code)}**{('（' + place + '）') if place else ''}：{plain(error.message)}"
        if details.get("hint"):
            line += f"\\\n  直し方：{plain(details['hint'])}"
        out.append(line)
    findings = evaluation.get("findings") if evaluation is not None else None
    any_finding = False
    if isinstance(findings, dict):
        for rule in sorted(findings):
            items = [item for item in _strings(findings[rule]) if isinstance(item, dict)]
            if not items:
                continue
            any_finding = True
            out.append(f"### {plain(rule)}")
            rows = []
            for item in items:
                row = f"- {links.link(item.get('id'))}：{plain(item.get('message', ''))}"
                if item.get("hint"):
                    row += f"\\\n  直し方：{plain(item['hint'])}"
                rows.append(row)
            out.append("\n".join(rows))
    if not errors and not any_finding:
        out.append("誤りと指摘はありません。")
    return out


def _assurance(assurance: Mapping[str, object] | None) -> list[str]:
    out = ["## 保証レベル"]
    if not assurance or not isinstance(assurance.get("level"), str):
        out.append("読めません（検査の結果を見てください）。")
        return out
    out.append(f"**{plain(assurance['level'])}**")
    if assurance.get("reason") is not None:
        out.append(_text_block(assurance["reason"]))
    return out


def _requirements(evaluation: Mapping[str, object], links: _Links) -> list[str]:
    out = ["## 要件", *_sections(evaluation, _REQUIREMENT_SECTIONS)]
    for key, item in _numbered(evaluation.get("requirements")):
        out += _target(key, item, "requirements", links)
    out.append("## 失敗・境界条件")
    failures = _numbered(evaluation.get("failures"))
    if not failures:
        out.append("なし")
    for key, item in failures:
        out += _target(key, item, "failures", links)
    return out


def _target(key: str, item: Mapping[str, object], field: str, links: _Links) -> list[str]:
    out = [_heading(key, key, item.get("title", ""))]
    if "text" in item:
        out.append(_text_block(item["text"]))
    if field == "requirements" and "acceptance" in item:
        out.append(
            "受け入れ：\n\n" + ("\n".join(_list_item(value) for value in _strings(item["acceptance"])) or "なし")
        )
    if field == "failures":
        for name, label in (("impact", "影響"), ("recovery", "回復")):
            if name in item:
                out.append(f"{label}：\n\n" + _text_block(item[name]))
    back = links.back.get(key, {})
    sources: tuple[tuple[str, str], ...] = (("design", "設計"), ("steps", "手順"), ("tests", "テスト"))
    if not links.issue:
        sources = (("design", "設計"), ("slices", "切り分け"))
    rows = [_labelled(label, links.links(back.get(source, []))) for source, label in sources]
    out.append("つながり：\n\n" + "\n".join(rows))
    out += _extra(item, _KNOWN_FIELDS[field])
    return out


def _design(evaluation: Mapping[str, object], links: _Links) -> list[str]:
    out = ["## 設計", *_sections(evaluation, _DESIGN_SECTIONS)]
    for key, item in _numbered(evaluation.get("design")):
        out.append(_heading(key, key, item.get("title", "")))
        if "text" in item:
            out.append(_text_block(item["text"]))
        out.append(_labelled("満たすもの", links.links(_strings(item.get("satisfies")))))
        out += _extra(item, _KNOWN_FIELDS["design"])
    return out


def _plan(evaluation: Mapping[str, object], links: _Links) -> list[str]:
    out = ["## 計画", *_sections(evaluation, _PLAN_HEAD)]
    steps = _numbered(evaluation.get("steps"))
    if steps:
        counts = dict.fromkeys(STATUS_LABELS, 0)
        for _, item in steps:
            status = item.get("status", "todo")
            if status in counts:
                counts[status] += 1
        out.append("### 進み具合")
        table = ["| 状態 | 数 |", "|---|---|"]
        table += [f"| {label} | {counts[status]} |" for status, label in STATUS_LABELS.items()]
        table.append(f"| 全体 | {len(steps)} |")
        out.append("\n".join(table))
    for key, item in steps:
        out.append(_heading(key, key, item.get("title", "")))
        status = item.get("status", "todo")
        rows = [_labelled("状態", plain(STATUS_LABELS.get(str(status), status)))]
        rows.append(_labelled("満たすもの", links.links(_strings(item.get("realizes")))))
        if "after" in item:
            rows.append(_labelled("先にする手順", links.links(_strings(item["after"]))))
        if "session" in item:
            rows.append(_labelled("セッション", plain(item["session"])))
        out.append("\n".join(rows))
        if "text" in item:
            out.append(_text_block(item["text"]))
        out += _extra(item, _KNOWN_FIELDS["steps"])
    for key, item in _numbered(evaluation.get("tests")):
        out.append(_heading(key, key, item.get("title", "")))
        out.append(_labelled("確かめるもの", links.links(_strings(item.get("verifies")))))
        if "text" in item:
            out.append(_text_block(item["text"]))
        out += _extra(item, _KNOWN_FIELDS["tests"])
    for key, item in _numbered(evaluation.get("slices")):
        out.append(_heading(f"slice-{key}", key, None))
        rows = [_labelled("任せる要件", links.links(_strings(item.get("covers"))))]
        if "after" in item:
            rows.append(_labelled("先にする切り分け", links.links(_strings(item["after"]))))
        if "session" in item:
            rows.append(_labelled("セッション", plain(item["session"])))
        out.append("\n".join(rows))
        if "text" in item:
            out.append(_text_block(item["text"]))
        out += _extra(item, _KNOWN_FIELDS["slices"])
    out += _sections(evaluation, _PLAN_TAIL)
    out += _execution(evaluation.get("execution"), evaluation, links)
    return out


def _execution(execution: object, evaluation: Mapping[str, object], links: _Links) -> list[str]:
    if not isinstance(execution, dict):
        return []
    out = ["### 実行の割り当て"]
    users: dict[str, list[str]] = {}
    for field in ("steps", "slices"):
        for key, item in _numbered(evaluation.get(field)):
            if isinstance(item.get("session"), str):
                users.setdefault(str(item["session"]), []).append(key)
    sessions = execution.get("sessions")
    if isinstance(sessions, dict):
        for name in sorted(sessions):
            session = sessions[name] if isinstance(sessions[name], dict) else {}
            rows = [f"- セッション **{plain(name)}**"]
            for field, label in (("model", "モデル"), ("effort", "推論")):
                if field in session:
                    rows.append(f"  - {label}：{plain(session[field])}")
            rows.append(f"  - 使う手順：{links.links(users.get(name, []))}")
            for field, label in (("task", "作業"), ("rationale", "根拠")):
                if field in session:
                    rows.append(f"  - {label}：\n\n" + _indent(_text_block(session[field]), "    "))
            out.append("\n".join(rows))
            out += _extra(session, _KNOWN_FIELDS["sessions"])
    reviews = execution.get("reviews")
    if isinstance(reviews, dict):
        for name in sorted(reviews):
            review = reviews[name] if isinstance(reviews[name], dict) else {}
            rows = [f"- レビュー **{plain(name)}**"]
            if "role" in review:
                rows.append(f"  - 役割：{plain(review['role'])}")
            if "after" in review:
                rows.append(f"  - 後にする手順：{links.link(review['after'])}")
            for field, label in (("model", "モデル"), ("effort", "推論")):
                if field in review:
                    rows.append(f"  - {label}：{plain(review[field])}")
            out.append("\n".join(rows))
            out += _extra(review, _KNOWN_FIELDS["reviews"])
    return out


def _others(evaluation: Mapping[str, object]) -> list[str]:
    rest: dict[str, object] = {key: evaluation[key] for key in sorted(evaluation) if key not in _KNOWN_TOP}
    for parent, known in (("assurance", ("level", "reason")), ("execution", ("sessions", "reviews"))):
        value = evaluation.get(parent)
        if isinstance(value, dict):
            rest.update({f"{parent}.{key}": value[key] for key in sorted(value) if key not in known})
    return ["## その他の項目", _code_block(rest)] if rest else []


def spec_markdown(
    *,
    scope_id: str,
    title: str | None,
    evaluation: Mapping[str, object] | None,
    assurance: Mapping[str, object] | None,
    errors: Sequence[Diagnostic],
) -> str:
    """The Markdown of one Scope in the fixed order; without an evaluation only the check results are shown."""
    level = assurance.get("level") if assurance else None
    schema = evaluation.get("schema") if evaluation is not None else None
    front = [
        "---",
        f"title: {_front_value(page_title(scope_id, title))}",
        f"lead: {_front_value('CUE の要件・設計・計画（' + (schema if isinstance(schema, str) else '型の版は未確定') + '）から描いたページです。')}",
        "category: CUE の仕様",
        f"status: {_front_value('保証レベル ' + (level if isinstance(level, str) else '未確定'))}",
        "---",
    ]
    links = _Links(evaluation or {})
    blocks = [f"題名：{plain(page_title(scope_id, title))}", *_check_results(errors, evaluation, links)]
    if evaluation is not None:
        blocks += _assurance(assurance)
        blocks += _requirements(evaluation, links)
        blocks += _design(evaluation, links)
        blocks += _plan(evaluation, links)
        blocks += _others(evaluation)
    else:
        blocks.append("評価が通らないので、本文は描いていません。上の誤りを直してから、もう一度描いてください。")
    return _script_safe("\n".join(front) + "\n\n" + "\n\n".join(blocks) + "\n")


def _script_safe(markdown: str) -> str:
    """`</script` never appears; `<!--` is broken only when a `<script` open tag could follow it (double escape)."""
    safe = _SCRIPT_END.sub(r"<\\/\1", markdown)
    if "<!--" in safe and _SCRIPT_OPEN.search(safe):
        safe = safe.replace("<!--", "<!\\--")
    return safe


def page_title(scope_id: str, title: str | None) -> str:
    shown = _one_line(title) if title else ""
    return f"{scope_id} {shown}" if shown else scope_id


def _join(base: str, name: str) -> str:
    return f"{base}{name}" if not base or base.endswith("/") else f"{base}/{name}"


def wrap_page(markdown: str, *, title: str, design_system_base: str, vendor_base: str | None) -> str:
    """The thin explanation shape of contract K5 around `markdown` (already script-safe)."""
    attribute: Callable[[str], str] = lambda value: html.escape(value, quote=True)  # noqa: E731
    head = [
        "<!doctype html>",
        '<html lang="ja">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        '<meta name="color-scheme" content="light dark">',
    ]
    if vendor_base is not None:
        head.append(f'<meta name="ds-vendor-base" content="{attribute(vendor_base)}">')
    head += [
        f"<title>{html.escape(_one_line(title))}</title>",
        f'<link rel="stylesheet" href="{attribute(_join(design_system_base, "ds.css"))}">',
        '<script type="text/markdown" id="ds-source">',
        _script_safe(markdown).rstrip("\n"),
        "</script>",
        f'<script src="{attribute(_join(design_system_base, "ds.js"))}"></script>',
        "</head>",
        "<body></body>",
        "</html>",
    ]
    return "\n".join(head) + "\n"

"""The human-task screens and marks (iss-00554 T-09, T-10).

The static checks always run. The JavaScript checks run the pure helpers (`views/todos/logic.js`), the shell's
marks (`core/ui.js`), the routes (`core/route.js`) and the shared card under node; on CI node is required.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

ASSETS = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "dashboard"
VIEWS = ASSETS / "views"
NODE = shutil.which("node")


# --- T-10: static checks -----------------------------------------------------------------------------------------


def test_the_screen_is_a_slot_and_the_shell_knows_its_routes() -> None:
    source = (VIEWS / "todos.js").read_text()
    assert "export default {" in source and 'id: "todos"' in source
    assert '"/assets/views/_shared/parts.css"' in source and '"/assets/views/todos.css"' in source
    assert "todos" in (VIEWS / "index.js").read_text()
    assert '["todos", "人のタスク", "person"]' in (ASSETS / "core" / "topbar.js").read_text()


def test_the_task_screens_only_read() -> None:
    for path in (VIEWS / "todos.js", VIEWS / "todos" / "logic.js", ASSETS / "core" / "api.js"):
        text = path.read_text()
        assert not re.search(r"https?://(?!x\")", text.replace("^https?:\\/\\/", "")), path
        assert "<button" not in text or path.name == "api.js", path  # no buttons: nothing to complete or snooze
    api = (ASSETS / "core" / "api.js").read_text()
    tail = api[api.index("// The human tasks") :]
    assert "method:" not in tail  # GET only
    screen = (VIEWS / "todos.js").read_text()
    for word in ("todo done", "todo snooze", "todo add", "navigator.clipboard", "<form", "method:"):
        assert word not in screen, word


def test_user_text_is_escaped_in_the_task_screen() -> None:
    raw = re.compile(r"\$\{(?:[a-z]+\.)+(title|text|note|body|key|reason|reply_to|message|role|by|tags?|id|record)\}")
    for name in ("todos.js",):
        for number, line in enumerate((VIEWS / name).read_text().splitlines(), 1):
            assert not raw.search(line), f"{name}:{number}: {line.strip()}"


def test_the_task_styles_stay_inside_the_screen() -> None:
    text = (VIEWS / "todos.css").read_text()
    selectors = [line for line in text.splitlines() if line and not line.startswith((" ", "}", "/*", "@"))]
    assert selectors and all(line.startswith('[data-view="todos"]') for line in selectors), selectors


# --- T-09: JavaScript checks under node --------------------------------------------------------------------------


def _node() -> str:
    if NODE is None:
        if os.environ.get("CI"):
            pytest.fail("node is required on CI for the human-task screen checks (iss-00554)")
        pytest.skip("node is not installed")
    return NODE


def _run(script: str, tmp_path: Path) -> dict:
    imports = {
        "logic": VIEWS / "todos" / "logic.js",
        "ui": ASSETS / "core" / "ui.js",
        "route": ASSETS / "core" / "route.js",
        "parts": VIEWS / "_shared" / "parts.js",
    }
    runner = tmp_path / "check.mjs"
    runner.write_text(
        "globalThis.location = new URL('http://127.0.0.1:47800/');\n"
        + "".join(f"const {name} = await import({json.dumps(path.as_uri())});\n" for name, path in imports.items())
        + "const out = {};\n"
        + textwrap.dedent(script)
        + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([_node(), str(runner)], capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


ITEMS = """
const item = (id, repository, derived, todo = {}) => ({repository, derived, todo: {id, status: "open", kind: "todo", tags: [], ...todo}});
const items = [
  item("t-0001", "github.com/o/r", {overdue: true, effective_status: "open"}, {tags: ["a"]}),
  item("t-0002", "github.com/o/s", {due_soon: true, effective_status: "open"}, {kind: "decide"}),
  item("t-0003", "github.com/o/s", {blocking: true, effective_status: "open"}),
  item("t-0004", "github.com/o/r", {effective_status: "open"}, {tags: ["a", "b"]}),
  item("t-0005", "github.com/o/r", {effective_status: "snoozed"}, {status: "snoozed"}),
  item("t-0006", "github.com/o/r", {effective_status: "done"}, {status: "done"}),
];
"""


def test_groups_filters_and_words(tmp_path: Path) -> None:
    out = _run(
        ITEMS
        + """
        out.groups = logic.groupItems(items).map((group) => [group.key, group.items.map((i) => i.todo.id)]);
        const params = new URLSearchParams("repo=github.com/o/r&tag=a&kind=bogus&closed=1");
        out.options = logic.todoOptions(params);
        out.filtered = logic.applyFilters(items, out.options).map((i) => i.todo.id);
        out.kind = logic.applyFilters(items, {repo: "", tag: "", kind: "decide"}).map((i) => i.todo.id);
        out.tags = logic.tagsOf(items);
        out.kinds = logic.kindsOf(items);
        const now = Date.parse("2026-11-04T12:00:00Z");
        out.overdue = logic.dueWords("2026-11-04T09:00:00Z", {overdue: true}, now);
        out.soon = logic.dueWords("2026-11-04T14:30:00Z", {}, now).tone;
        out.later = logic.dueWords("2026-11-20T00:00:00Z", {}, now).tone;
        out.none = logic.dueWords(null).text;
        out.param = logic.withParam("/todos?embed=1&repo=x", "repo", null);
        out.param2 = logic.withParam("/todos?embed=1", "closed", true);
        out.name = [logic.repoName("github.com/o/r"), logic.repoName("example.com/o/r")];
        """,
        tmp_path,
    )
    assert out["groups"] == [
        ["overdue", ["t-0001"]],
        ["soon", ["t-0002"]],
        ["blocking", ["t-0003"]],
        ["later", ["t-0004"]],
        ["snoozed", ["t-0005"]],
        ["closed", ["t-0006"]],
    ]
    assert out["options"] == {"repo": "github.com/o/r", "tag": "a", "kind": "", "closed": True}
    assert out["filtered"] == ["t-0001", "t-0004"] and out["kind"] == ["t-0002"]
    assert out["tags"] == ["a", "b"] and out["kinds"] == ["decide", "todo"]
    assert out["overdue"] == {"text": "期限切れ（3時間超過）", "tone": "danger"}
    assert out["soon"] == "warning" and out["later"] == "" and out["none"] == "期限なし"
    assert out["param"] == "/todos?embed=1" and out["param2"] == "/todos?embed=1&closed=1"
    assert out["name"] == ["o/r", "example.com/o/r"]


def test_safe_markdown_never_passes_html_or_script_links(tmp_path: Path) -> None:
    out = _run(
        """
        out.html = logic.safeMarkdown('# 見出し\\n<script>alert(1)</script> **太字** `<i>`\\n\\n- [x](javascript:alert(1))\\n- [ok](https://example.com/a?b=1&c=2)\\n1. one\\n\\n```\\n<img src=x onerror=alert(1)>\\n```\\n<img src=x onerror=alert(1)>');
        """,
        tmp_path,
    )
    html = out["html"]
    assert "<script" not in html and "<img" not in html and "javascript:" not in html.replace("(javascript:", "")
    assert '<a href="javascript' not in html
    assert "&lt;script&gt;" in html and "<strong>太字</strong>" in html and "<code>&lt;i&gt;</code>" in html
    assert '<a href="https://example.com/a?b=1&amp;c=2" target="_blank" rel="noopener noreferrer">ok</a>' in html
    assert "<ol><li>one</li></ol>" in html and "<pre><code>&lt;img src=x onerror=alert(1)&gt;</code></pre>" in html


def test_history_words_cover_every_record_action(tmp_path: Path) -> None:
    source = (ASSETS.parents[1] / "runtime" / "domain" / "todo_record.py").read_text()
    block = source[source.index("ACTIONS: Final = (") : source.index("UPDATABLE")]
    actions = re.findall(r'"([a-z_]+)"', block)
    out = _run("out.words = logic.ACTION_WORDS;", tmp_path)
    assert actions and sorted(out["words"]) == sorted(actions)


def test_routes_and_paths(tmp_path: Path) -> None:
    out = _run(
        """
        const r = (path) => { const x = route.parseRoute("http://127.0.0.1:47800" + path); return [x.view, x.repository, x.todo]; };
        out.all = r("/todos?repo=a");
        out.repo = r("/r/github.com/o/r/todos");
        out.one = r("/r/github.com/o/r/todos/t-0001");
        out.overview = r("/");
        out.graph = r("/r/github.com/o/r/");
        out.paths = [route.todosPath(null), route.todosPath("github.com/o/r"), route.todoPath("github.com/o/r", "t-0001")];
        """,
        tmp_path,
    )
    assert out["all"] == ["todos", None, None]
    assert out["repo"] == ["todos", "github.com/o/r", None]
    assert out["one"] == ["todos", "github.com/o/r", "t-0001"]
    assert out["overview"] == ["overview", None, None] and out["graph"] == ["graph", "github.com/o/r", None]
    assert out["paths"] == ["/todos", "/r/github.com/o/r/todos", "/r/github.com/o/r/todos/t-0001"]


def test_human_marks_on_issues_parents_and_cards(tmp_path: Path) -> None:
    out = _run(
        """
        const issue = {id: "iss-00003", number: 3, kind: "issue", state: "blocked", path: "/r/github.com/o/r/scopes/iss-00003", title: "<b>x</b>", reason: {text: ""}, todos: {blocking: 2, blocking_with_descendants: 2, related: 1}};
        const epic = {...issue, id: "epic-00001", kind: "epic", children: [], todos: {blocking: 0, blocking_with_descendants: 3, related: 0}};
        const none = {...issue, id: "iss-00004", todos: {blocking: 0, blocking_with_descendants: 0, related: 4}};
        out.issue = ui.humanCount(issue);
        out.epic = ui.humanCount(epic);
        out.markIssue = ui.humanMark(2);
        out.markEpic = ui.humanMark(3, {descendants: true});
        out.markNone = ui.humanMark(0);
        const ctx = {href: (p) => p};
        out.card = parts.card(issue, ctx);
        out.cardEpic = parts.card(epic, ctx);
        out.cardNone = parts.card(none, ctx);
        out.missing = ui.humanCount({kind: "issue"});
        """,
        tmp_path,
    )
    assert out["issue"] == {"count": 2, "descendants": False}
    assert out["epic"] == {"count": 3, "descendants": True}
    assert "人 2" in out["markIssue"] and 'aria-label="人のタスク 2件が止めている"' in out["markIssue"]
    assert "<small>配下も</small>" in out["markEpic"] and "（配下を含む）" in out["markEpic"]
    assert out["markNone"] == ""
    assert 'class="sd-hm"' in out["card"] and "人 2" in out["card"] and "&lt;b&gt;" in out["card"]
    assert "人 3" in out["cardEpic"] and "配下も" in out["cardEpic"]
    assert "sd-hm" not in out["cardNone"]
    assert out["missing"] == {"count": 0, "descendants": False}

"""The shipped CLI reference explains the agents tab (iss-00593 T-08, D-08)."""

from __future__ import annotations

import hashlib
import ipaddress
import json
from pathlib import Path
import re

ASSETS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets"
REFERENCE = ASSETS / "spec_dock/docs/reference_cli.md"
CODES = (
    "orca-loading",
    "orca-unreachable",
    "orca-shape",
    "orca-orca-unreachable",
    "orca-orca-starting",
    "orca-config",
    "orca-embed",
    "orca-agent-gone",
    "orca-agent-choose",
    "orca-agent-drift",
)


def _section() -> str:
    text = REFERENCE.read_text(encoding="utf-8")
    start = text.index("\n## orca-web との連携\n")
    end = text.index("\n## ", start + 1)
    return text[start:end]


def test_the_reference_explains_the_agents_tab() -> None:
    section = _section()
    assert "### エージェントのタブ" in section and "（キー`agents`）" in section
    assert "**出す条件**" in section and "(1)" in section and "(4)" in section
    assert "問い合わせの`agent`" in section and "`agent=gone:<id>`" in section
    assert "`sendEnabled`（既定は止まっている）" in section
    for path in ("/api/token", "/api/send/", "/api/open", "/api/settings"):
        assert f"`{path}`" in section, path
    assert "`allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox`" in section
    assert "orca-web の iss-00037 で、埋め込みの中の同じ iframe への移りはなくなった" in section
    rows = {
        m.group(1): m.group(2) for m in re.finditer(r"^\| `(orca-[a-z-]+)` \| ([^|]+) \| ([^|]+) \|$", section, re.M)
    }
    assert sorted(rows) == sorted(CODES)
    for code in CODES:
        assert rows[code].strip(), code


def test_the_reference_names_no_real_address_or_personal_path() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    tailnet = ipaddress.ip_network("100.64.0.0/10")
    for found in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
        try:
            address = ipaddress.ip_address(found)
        except ValueError:
            continue
        assert address not in tailnet, found
    for prefix in ("/Users/", "/home/", "/Volumes/"):
        assert prefix not in text, prefix


def test_the_inventory_carries_the_new_reference() -> None:
    entries = {e["path"]: e for e in json.loads((ASSETS / "static-inventory.json").read_text())["files"]}
    entry = entries["spec-dock/docs/reference_cli.md"]
    assert entry["sha256"] == hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    assert len(entry["known_old_sha256"]) == len(set(entry["known_old_sha256"]))


def test_the_reference_explains_the_choice_fixes_of_issue_602() -> None:
    """iss-00602 T-06 (D-06): the choice kept from the memory, the panel's foot links, modified presses, shape."""
    section = _section()
    agents = section[section.index("### エージェントのタブ") :]
    assert "その Scope で最後に開いた相手を開いたときも、その相手を問い合わせ（横の欄では欄の中）に書く" in agents
    assert "帯の今の相手を押しても枠は読み込み直されません" in agents
    assert "横の欄の足の「詳しい画面」と「新しいタブで開く」は、欄の今の選びを、なければ同じ Scope の覚え" in agents
    assert "欄がどのタブを見ていても" in agents
    assert "どちらも、その相手がいなくなったと画面が知っていれば`gone:<id>`として持つ" in agents
    assert "その相手が戻った後に新しいタブで開いても開きません" in agents
    assert "修飾キー（Ctrl・Cmd・Shift・Alt）つきの押しで新しいタブに開くときは、元の画面の覚えを変えません" in agents
    shape = next(line for line in agents.splitlines() if line.startswith("| `orca-shape` |"))
    assert "worktree の`agents`が並びでないときも、形の違う1件に数える" in shape


def test_the_inventory_accepts_the_reference_of_the_last_release() -> None:
    entries = {e["path"]: e for e in json.loads((ASSETS / "static-inventory.json").read_text())["files"]}
    entry = entries["spec-dock/docs/reference_cli.md"]
    released = "6b8066f2ad598b16f243307be2073f424ace27167b718de770ba804d44c5c4a8"  # v0.9.3
    assert released in entry["known_old_sha256"] and entry["sha256"] != released

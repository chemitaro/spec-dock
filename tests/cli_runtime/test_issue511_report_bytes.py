"""iss-00511: the report.md that `scope create` writes is byte for byte what 0.4.2 wrote.

The fixtures were rebuilt from `git show v0.4.2:src/spec_dock/assets/spec_dock/templates/cue/<kind>/report.md`: 0.4.2
dropped the front-matter `タイトル:` and `親:` lines while writing, 0.5.0 left them out of the template instead, and the
placeholders were replaced with the values below. The date line is `<TODAY>` here.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

from tests.support.canonical_writes import WriteWorld

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/issue511"
REASON = "公開の CLI の契約を変えるため"


@pytest.mark.parametrize(("kind", "prefix"), [("initiative", "init"), ("epic", "epic"), ("issue", "iss")])
def test_the_created_report_keeps_the_0_4_2_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str, prefix: str
) -> None:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    parent = {"initiative": (), "epic": ("--parent", "init-00001"), "issue": ("--parent", "epic-00002")}[kind]
    code, payload = world.write(
        "scope", "create", kind, "--backend", "github", *parent, "--title", "新しい作業",
        "--assurance", "strict", "--assurance-reason", REASON,
    )  # fmt: skip
    assert code == 0, payload
    created = (world.catalog / "00000-00999" / f"{prefix}-00003" / "report.md").read_text(encoding="utf-8")
    dated = re.sub(r'(最終更新: ")\d{4}-\d{2}-\d{2}(")', r"\1<TODAY>\2", created)
    assert dated.encode("utf-8") == (FIXTURES / f"report-0.4.2-{kind}.md").read_bytes()

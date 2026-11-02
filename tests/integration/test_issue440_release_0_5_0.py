"""SpecDock 0.5.0: the version, its migration notes, and the upgrade path from the 0.4.2 assets (iss-00440).

`tests/fixtures/issue440/inventory-0.4.2.json` is the static inventory 0.4.2 shipped (path, source, sha256, mode);
`tests/fixtures/issue440/v0.4.2/` holds the 0.4.2 bytes of every asset 0.5.0 changed or retired, one file per path
(`/` written as `__`, `.txt` appended so no fixture acts as a real `.gitignore`).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.static_assets import (
    RETIRED_LEGACY_SCAFFOLD_PATHS,
    package_retired_assets,
    package_static_assets,
)
from tests.integration.test_issue413_assets import uninitialized_worktree

if TYPE_CHECKING:
    from collections.abc import Iterator

ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD = ROOT / "src/spec_dock/assets/spec_dock"
FIXTURES = ROOT / "tests/fixtures/issue440"
INVENTORY_0_4_2: dict[str, dict[str, Any]] = json.loads((FIXTURES / "inventory-0.4.2.json").read_text("utf-8"))
NOT_MIGRATED_NEXT_STEP = (
    "This repository is not migrated (workspace schema 3); reinstall SpecDock 0.4.2 and follow "
    "scripts/migrate-to-canonical/README.md at the v0.4.2 tag to migrate it."
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _previous_bytes() -> Iterator[tuple[str, bytes]]:
    for fixture in sorted((FIXTURES / "v0.4.2").iterdir()):
        yield fixture.name.removesuffix(".txt").replace("__", "/"), fixture.read_bytes()


PREVIOUS = dict(_previous_bytes())
CURRENT = {asset.path: asset for asset in package_static_assets()}
RETIRED = {asset.path: asset for asset in package_retired_assets()}


def test_the_migration_notes_describe_0_5_0_and_the_dogfood_copy_matches() -> None:
    text = (SCAFFOLD / "docs/migration.md").read_text("utf-8")
    headings = re.findall(r"^## (.+)$", text, re.M)
    assert headings.index("0.5.0 への更新") == headings.index("0.4.2 への更新") + 1
    assert "schema3の旧writerから移行" not in headings
    [section] = re.findall(r"^## 0\.5\.0 への更新\n(.*?)(?=^## )", text, re.M | re.S)
    for token in (
        "CANONICAL_NOT_MIGRATED",
        "0.4.2",
        "v0.4.2",
        "workspace migrate",
        "workbench copy",
        "workspace validate --ci",
        "--source local",
        "--slug",
        "CANONICAL_NOT_APPLICABLE",
        "CANONICAL_WORKBENCH_SHARED",
        "spec-dock/templates/{initiative,epic,issue}/",
        "epics.md",
        "issues.md",
        "タイトル:",
        "CLAUDE_SKILL_LINK_MISSING",
        "!**/.workbench/",
        "git add spec-dock/templates",
        "installation update",
    ):
        assert token in section, token
    [moving] = re.findall(r"^## canonical モードへの移行\n(.*?)(?=^## )", text, re.M | re.S)
    assert "v0.4.2" in moving and "読み替え" in moving and "0.3.0 に上げ" not in moving
    for relative in ("docs/migration.md", "docs/canonical.md", "docs/reference_cli.md", "system/spec-dock-version"):
        assert (ROOT / "spec-dock" / relative).read_bytes() == (SCAFFOLD / relative).read_bytes(), relative


def test_the_not_migrated_next_step_names_0_4_2_everywhere() -> None:
    from spec_dock.runtime.application.canonical_errors import NOT_MIGRATED_RECOVERY

    assert NOT_MIGRATED_RECOVERY == NOT_MIGRATED_NEXT_STEP
    canonical = (SCAFFOLD / "docs/canonical.md").read_text("utf-8")
    [row] = [line for line in canonical.splitlines() if line.startswith("| `CANONICAL_NOT_MIGRATED` |")]
    assert "SpecDock 0.4.2" in row and "`v0.4.2`" in row and "0.3.0 を入れ直" not in row


def test_every_0_4_2_asset_is_current_known_old_or_retired() -> None:
    """Every byte 0.4.2 shipped is recognized by 0.5.0, so `installation update` never stops on it."""
    for path, shipped in INVENTORY_0_4_2.items():
        if path in CURRENT:
            asset = CURRENT[path]
            assert shipped["sha256"] == asset.sha256 or shipped["sha256"] in asset.known_old_sha256, path
        else:
            assert path in RETIRED, path
            assert shipped["sha256"] in RETIRED[path].known_old_sha256, path
    for path, payload in PREVIOUS.items():
        assert _sha(payload) == INVENTORY_0_4_2[path]["sha256"], path


def test_the_retired_assets_are_exactly_the_legacy_scaffold() -> None:
    removed = set(INVENTORY_0_4_2) - set(CURRENT)
    assert removed == set(RETIRED_LEGACY_SCAFFOLD_PATHS)
    assert len(removed) == 17
    for kind in ("initiative", "epic", "issue"):
        assert not (SCAFFOLD / "templates" / kind).exists()
        assert not (ROOT / "spec-dock/templates" / kind).exists()
    for name in ("rules/initiative/epics.md", "rules/epic/issues.md"):
        assert not (SCAFFOLD / "docs" / name).exists() and not (ROOT / "spec-dock/docs" / name).exists()


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_the_cue_report_template_carries_no_title_or_parent(kind: str) -> None:
    report = (SCAFFOLD / "templates/cue" / kind / "report.md").read_text("utf-8")
    front = report.split("---\n")[1]
    assert "タイトル:" not in front and "親:" not in front
    assert "](../../../docs/authoring/report.md)" in report


@pytest.mark.parametrize(
    "path", ["spec-dock/templates/cue/issue/report.md", "spec-dock/templates/issue/notes.md", "spec-dock/docs/x.md"]
)
def test_retired_entries_outside_the_named_paths_stay_refused(
    path: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resources = tmp_path / "assets"
    resources.mkdir()
    (resources / "static-inventory.json").write_text(
        json.dumps({
            "schema_version": "specdock.static-inventory/v1",
            "files": [],
            "retired": [{"path": path, "known_old_sha256": ["0" * 64]}],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr("spec_dock.runtime.infra.static_assets.files", lambda _package: tmp_path)
    with pytest.raises(ValueError, match="unsafe target"):
        package_retired_assets()


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_installation_update_upgrades_a_0_4_2_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    for relative, payload in PREVIOUS.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    changed = sorted(path for path in PREVIOUS if path in CURRENT)
    retired = sorted(path for path in PREVIOUS if path not in CURRENT)
    backup = tmp_path / "backup"
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes"
    )
    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    assert sorted(applied["data"]["result"]["changed_paths"]) == changed
    assert sorted(applied["data"]["result"]["retired_paths"]) == retired
    for relative in changed:
        assert (target / relative).read_bytes() == CURRENT[relative].payload, relative
    for relative in retired:
        assert not (target / relative).exists(), relative
    for relative, payload in PREVIOUS.items():
        assert (backup / "static" / relative).read_bytes() == payload, relative
    code, shown = _run(capsys, "installation", "show", "--target", str(target))
    assert code == 0
    assert {item["classification"] for item in shown["data"]["result"]["assets"]} == {"current"}


def test_installation_update_keeps_a_modified_retired_template_for_a_manual_merge(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    edited = target / "spec-dock/templates/issue/plan.md"
    edited.parent.mkdir(parents=True)
    edited.write_bytes(PREVIOUS["spec-dock/templates/issue/plan.md"] + b"\nlocal note\n")
    code, result = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(tmp_path / "b"), "--yes"
    )
    assert (code, result["error"]["code"]) == (3, "PRECONDITION_FAILED")
    assert "spec-dock/templates/issue/plan.md" in result["error"]["message"]
    assert result["effects"] == [] and edited.read_bytes().endswith(b"local note\n")

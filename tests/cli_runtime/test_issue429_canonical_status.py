"""`spec-dock canonical status`, the sandbox write check and the tool-setting lines (iss-00429)."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra import runtime_environment
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import (
    add_worktree,
    bare_remote,
    clone,
    environment,
    git,
    isolate_user_state,
)

if TYPE_CHECKING:
    from pathlib import Path

ITEMS = {
    "catalog",
    "link",
    "exclude",
    "access",
    "tools",
    "sync",
    "changes",
    "format",
    "git",
    "snapshot",
    "dashboard",
    "structure",
}
pytestmark = pytest.mark.usefixtures("isolated")
needs_permissions = pytest.mark.skipif(os.geteuid() == 0, reason="root ignores directory permissions")


@pytest.fixture
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    home = isolate_user_state(monkeypatch, tmp_path)
    inject(monkeypatch)
    return home


def inject(monkeypatch: pytest.MonkeyPatch, **options: Any) -> None:
    monkeypatch.setattr(
        runtime_environment, "detect_runtime_environment", lambda *args, **kwargs: environment(**options)
    )


def run(capsys: pytest.CaptureFixture[str], checkout: Path, *argv: str) -> tuple[int, dict[str, Any]]:
    code = main(["--project", str(checkout), *argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


@pytest.fixture
def remote(tmp_path: Path) -> Path:
    return bare_remote(tmp_path / "remote.git")


@pytest.fixture
def linked_clone(capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path) -> tuple[Path, Path]:
    main_checkout = clone(remote, tmp_path / "main")
    assert run(capsys, main_checkout, "canonical", "link")[0] == 0
    linked = add_worktree(main_checkout, tmp_path / "linked", "feature")
    assert run(capsys, linked, "canonical", "link")[0] == 0
    return main_checkout, linked


def test_status_of_a_linked_clone_reports_every_item_and_no_problems(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path]
) -> None:
    main_checkout, _linked = linked_clone
    code, result = run(capsys, main_checkout, "canonical", "status")
    assert code == 0 and result["status"] == "succeeded" and result["warnings"] == []
    data = result["data"]
    assert set(data) == ITEMS | {"kind"} and data["kind"] == "canonical-status"
    for item in ("catalog", "link", "exclude", "access", "tools", "format", "git", "changes"):
        assert data[item]["status"] == "ok", (item, data[item])
    # iss-00438: no GitHub repository, so no dashboard is drawn for this clone.
    assert data["dashboard"]["status"] == "not_applicable" and data["dashboard"]["next_step"] is None
    # iss-00430: the (fake) periodic job ran once after link; origin is a bare path, so no snapshot applies.
    assert data["sync"]["status"] == "ok" and data["sync"]["registered"] is True
    assert data["snapshot"]["status"] == "unknown" and data["snapshot"]["repository"] is None
    # iss-00431: structure reads GitHub only with --structure.
    assert data["structure"] == {"status": "not_checked", "next_step": None}
    assert data["catalog"]["locked"] and data["catalog"]["branch"] == "spec-dock/canonical"
    assert data["format"]["version"] == 1 and data["git"]["supported"]
    assert data["changes"]["unsaved"] == 0 and data["changes"]["unpushed"] == 0


def test_status_writes_nothing_anywhere(
    capsys: pytest.CaptureFixture[str], remote: Path, linked_clone: tuple[Path, Path], tmp_path: Path
) -> None:
    main_checkout, linked = linked_clone
    (main_checkout / "spec-dock/.canonical/init-00001-plan").mkdir()
    (main_checkout / "spec-dock/.canonical/init-00001-plan/plan.md").write_text("draft\n", encoding="utf-8")
    state = tmp_path / "state"  # canonical link (iss-00430 steps 6-7) wrote the registry and the baseline here
    before = tree_digest(main_checkout), tree_digest(linked), tree_digest(remote), tree_digest(state)
    for checkout in (main_checkout, linked):
        code, result = run(capsys, checkout, "canonical", "status")
        assert code == 0 and result["data"]["changes"]["unsaved"] == 1
    assert (tree_digest(main_checkout), tree_digest(linked), tree_digest(remote), tree_digest(state)) == before


def test_status_names_the_problem_and_the_next_step_for_an_unlinked_clone(
    capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path
) -> None:
    fresh = clone(remote, tmp_path / "fresh")
    code, result = run(capsys, fresh, "canonical", "status")
    assert code == 0 and result["status"] == "succeeded"
    data = result["data"]
    assert data["catalog"]["state"] == "absent" and data["catalog"]["next_step"] == "spec-dock canonical link"
    assert data["link"]["status"] == "problem" and data["exclude"]["status"] == "problem"
    codes = {item["code"] for item in result["warnings"]}
    assert codes == {"CANONICAL_NOT_LINKED", "CANONICAL_IGNORE_RULES_MISSING", "CANONICAL_SYNC_NOT_SCHEDULED"}
    assert all(item["details"]["next_step"] for item in result["warnings"])


def test_status_reports_conflict_copies_and_unpushed_commits(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path]
) -> None:
    main_checkout, _linked = linked_clone
    catalog = main_checkout / "spec-dock/.canonical"
    (catalog / "plan.conflict-mac-20261025T120000Z.md").write_text("theirs\n", encoding="utf-8")
    git(catalog, "add", "-A")
    git(catalog, "commit", "-qm", "local")
    _code, result = run(capsys, main_checkout, "canonical", "status")
    changes = result["data"]["changes"]
    assert changes["conflict_files"] == ["plan.conflict-mac-20261025T120000Z.md"] and changes["unpushed"] == 1
    assert changes["oldest_unpushed_at"] and "Merge" in changes["next_step"]


def test_a_missing_gitignore_rule_points_to_installation_update(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    remote = bare_remote(tmp_path / "plain.git", gitignore=False)
    checkout = clone(remote, tmp_path / "plain")
    code, result = run(capsys, checkout, "canonical", "link")
    assert code == 0
    (warning,) = [item for item in result["warnings"] if item["code"] == "CANONICAL_IGNORE_RULES_MISSING"]
    assert "spec-dock installation update" in warning["details"]["next_step"]
    code, status = run(capsys, checkout, "canonical", "status")
    assert status["data"]["exclude"]["gitignore"]["missing"] == ["/.canonical/", "/initiatives", "!/initiatives/"]
    assert status["data"]["exclude"]["info_exclude"]["missing"] == []
    assert "spec-dock installation update" in status["data"]["exclude"]["next_step"]


def test_a_modified_gitignore_without_the_rules_points_to_a_manual_merge(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    # installation update does not overwrite a modified file, so the same next step as canonical check is shown.
    remote = bare_remote(tmp_path / "modified.git", gitignore=False, files={"spec-dock/.gitignore": b"*.log\n"})
    checkout = clone(remote, tmp_path / "modified")
    code, result = run(capsys, checkout, "canonical", "link")
    assert code == 0
    (warning,) = [item for item in result["warnings"] if item["code"] == "CANONICAL_IGNORE_RULES_MISSING"]
    assert "Merge the shipped spec-dock/.gitignore" in warning["details"]["next_step"]
    code, status = run(capsys, checkout, "canonical", "status")
    assert "Merge the shipped spec-dock/.gitignore" in status["data"]["exclude"]["next_step"]


def test_the_text_output_shows_each_next_step(capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path) -> None:
    fresh = clone(remote, tmp_path / "fresh")
    assert main(["--project", str(fresh), "canonical", "status"]) == 0
    output = capsys.readouterr()
    assert "spec-dock: succeeded (canonical status)" in output.out
    assert "warning [CANONICAL_NOT_LINKED]" in output.err and "next: spec-dock canonical link" in output.err


@needs_permissions
def test_in_a_codex_sandbox_status_shows_the_exact_writable_roots_line(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    main_checkout, linked = linked_clone
    catalog = main_checkout / "spec-dock/.canonical"
    monkeypatch.setenv("CODEX_SANDBOX", "seatbelt")
    inject(monkeypatch)
    catalog.chmod(0o555)
    try:
        code, result = run(capsys, linked, "canonical", "status")
    finally:
        catalog.chmod(0o755)
    assert code == 0
    codex = result["data"]["tools"]["codex"]
    line = f'writable_roots = ["{catalog}"]'
    assert codex["sandbox"] and codex["writable"] is False and codex["line"] == line
    (warning,) = [item for item in result["warnings"] if item["details"].get("tool") == "codex"]
    assert warning["code"] == "CANONICAL_TOOL_SETTING_MISSING" and line in warning["message"]
    assert warning["details"]["section"] == "[sandbox_workspace_write]"
    assert result["data"]["access"]["writable"] is False
    # Every problem item has its warning (design ch. 10); the access one points at the tools line.
    (access,) = [item for item in result["warnings"] if item["details"].get("item") == "access"]
    assert access["code"] == "OS_ACCESS_DENIED" and "tools item" in access["details"]["next_step"]


@needs_permissions
def test_a_sandbox_that_cannot_write_git_stops_catalog_creation_but_allows_linking_only(
    capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fresh = clone(remote, tmp_path / "fresh")
    common = fresh / ".git"
    before = tree_digest(fresh)
    common.chmod(0o555)
    try:
        code, plain = run(capsys, fresh, "canonical", "link")
        monkeypatch.setenv("CODEX_SANDBOX", "seatbelt")
        inject(monkeypatch)
        _code, result = run(capsys, fresh, "canonical", "link")
    finally:
        common.chmod(0o755)
        monkeypatch.delenv("CODEX_SANDBOX")
        inject(monkeypatch)
    assert code == 3 and plain["error"]["code"] == "CANONICAL_SANDBOX_DENIED" and plain["effects"] == []
    assert "Check the permissions" in plain["recovery"]["instructions"][0]
    assert result["error"]["code"] == "CANONICAL_SANDBOX_DENIED" and result["effects"] == []
    assert str(common) in result["error"]["details"]["paths"]
    assert "outside the sandbox" in result["recovery"]["instructions"][0]
    assert tree_digest(fresh) == before

    assert run(capsys, fresh, "canonical", "link")[0] == 0
    linked = add_worktree(fresh, tmp_path / "linked", "feature")
    monkeypatch.setenv("CODEX_SANDBOX", "seatbelt")
    inject(monkeypatch)
    for protected in (common, fresh / "spec-dock"):
        protected.chmod(0o555)
    try:
        code, result = run(capsys, linked, "canonical", "link")
    finally:
        for protected in (common, fresh / "spec-dock"):
            protected.chmod(0o755)
    assert code == 0, result
    assert [(item["kind"], item["status"]) for item in result["effects"] if item["status"] != "unchanged"] == [
        ("canonical.link", "succeeded")
    ]


def test_claude_code_settings_without_the_catalog_get_the_exact_line(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], isolated: Path
) -> None:
    main_checkout, linked = linked_clone
    catalog = main_checkout / "spec-dock/.canonical"
    line = '{ "permissions": { "additionalDirectories": ["' + str(catalog) + '"] } }'
    _code, result = run(capsys, linked, "canonical", "status")
    claude = result["data"]["tools"]["claude_code"]
    assert claude["needed"] and claude["configured"] is False and claude["line"] == line
    (warning,) = [item for item in result["warnings"] if item["details"].get("tool") == "claude_code"]
    assert warning["code"] == "CANONICAL_TOOL_SETTING_MISSING" and line in warning["message"]
    _code, result = run(capsys, linked, "canonical", "link")
    assert any(item["code"] == "CANONICAL_TOOL_SETTING_MISSING" for item in result["warnings"])
    _code, result = run(capsys, main_checkout, "canonical", "status")
    assert result["data"]["tools"]["claude_code"]["needed"] is False and result["warnings"] == []


@pytest.mark.parametrize("where", ["user", "local"])
def test_claude_code_settings_listing_the_catalog_or_a_parent_are_enough(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], isolated: Path, where: str
) -> None:
    main_checkout, linked = linked_clone
    if where == "user":
        settings = isolated / ".claude/settings.json"
        entry = str(main_checkout)
    else:
        settings = linked / ".claude/settings.local.json"
        entry = str(main_checkout / "spec-dock/.canonical")
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps({"permissions": {"additionalDirectories": [entry]}}), encoding="utf-8")
    before = settings.read_bytes()
    _code, result = run(capsys, linked, "canonical", "status")
    assert result["data"]["tools"]["claude_code"]["configured"] is True and result["warnings"] == []
    assert settings.read_bytes() == before


def test_unreadable_claude_code_settings_cannot_be_judged(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], isolated: Path
) -> None:
    _main, linked = linked_clone
    settings = isolated / ".claude/settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text("{ not json", encoding="utf-8")
    _code, result = run(capsys, linked, "canonical", "status")
    assert result["data"]["tools"]["claude_code"]["configured"] is None
    assert [item["code"] for item in result["warnings"]] == ["CANONICAL_TOOL_SETTING_UNKNOWN"]


def test_a_newer_canonical_format_is_reported(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path]
) -> None:
    main_checkout, _linked = linked_clone
    (main_checkout / "spec-dock/.canonical/.spec-dock-canonical.json").write_text('{"format": 2}\n', encoding="utf-8")
    code, result = run(capsys, main_checkout, "canonical", "status")
    assert result["data"]["format"] == {
        "status": "problem",
        "next_step": result["data"]["format"]["next_step"],
        "version": 2,
        "supported_max": 1,
        "writable": False,
    }
    assert [item["code"] for item in result["warnings"]] == ["CANONICAL_FORMAT_UNSUPPORTED"]
    code, linked_result = run(capsys, main_checkout, "canonical", "link")
    assert code == 0 and [item["code"] for item in linked_result["warnings"]] == ["CANONICAL_FORMAT_UNSUPPORTED"]


def test_a_missing_canonical_format_file_is_reported_by_status_and_link(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path]
) -> None:
    main_checkout, _linked = linked_clone
    (main_checkout / "spec-dock/.canonical/.spec-dock-canonical.json").unlink()
    code, result = run(capsys, main_checkout, "canonical", "status")
    assert code == 0 and result["data"]["format"]["status"] == "problem"
    assert result["data"]["format"]["version"] is None and result["data"]["format"]["writable"] is False
    assert [item["code"] for item in result["warnings"]] == ["CANONICAL_FORMAT_UNSUPPORTED"]
    code, linked_result = run(capsys, main_checkout, "canonical", "link")
    assert code == 0 and [item["code"] for item in linked_result["warnings"]] == ["CANONICAL_FORMAT_UNSUPPORTED"]
    assert linked_result["warnings"][0]["details"]["next_step"] == result["warnings"][0]["details"]["next_step"]


def test_an_old_git_is_reported_without_failing(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    main_checkout, _linked = linked_clone
    inject(monkeypatch, git_version=(2, 37, 0))
    code, result = run(capsys, main_checkout, "canonical", "status")
    assert code == 0 and result["data"]["git"]["status"] == "problem"
    assert [item["code"] for item in result["warnings"]] == ["CANONICAL_GIT_TOO_OLD"]
    assert result["data"]["catalog"]["status"] == "unknown"


def test_a_bare_layout_cannot_report_status(capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path) -> None:
    git(remote, "worktree", "add", "-q", str(tmp_path / "tree"), "main")
    code, result = run(capsys, (tmp_path / "tree").resolve(), "canonical", "status")
    assert code == 3 and result["error"]["code"] == "CANONICAL_UNSUPPORTED_LAYOUT"


@needs_permissions
def test_the_write_check_comes_before_any_network_call(
    capsys: pytest.CaptureFixture[str], remote: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra import canonical_git

    fresh = clone(remote, tmp_path / "fresh")

    def offline(*args: object, **kwargs: object) -> str:
        raise AssertionError("ls-remote must not run before the write check")

    monkeypatch.setattr(canonical_git, "remote_canonical", offline)
    monkeypatch.setenv("CODEX_SANDBOX", "seatbelt")
    inject(monkeypatch)
    (fresh / ".git").chmod(0o555)
    try:
        code, result = run(capsys, fresh, "canonical", "link")
    finally:
        (fresh / ".git").chmod(0o755)
    assert code == 3 and result["error"]["code"] == "CANONICAL_SANDBOX_DENIED"


@needs_permissions
def test_a_denied_main_spec_dock_is_an_access_problem_not_a_crash(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path]
) -> None:
    main_checkout, linked = linked_clone
    (main_checkout / "spec-dock").chmod(0o000)
    try:
        code, result = run(capsys, linked, "canonical", "status")
    finally:
        (main_checkout / "spec-dock").chmod(0o755)
    assert code == 0 and result["status"] == "succeeded", result
    assert result["data"]["access"]["status"] == "problem"
    assert "OS_ACCESS_DENIED" in [item["code"] for item in result["warnings"]]


def test_a_registration_through_an_alias_matches_by_identity(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], tmp_path: Path
) -> None:
    from spec_dock.runtime.infra import canonical_git

    main_checkout, _linked = linked_clone
    alias = tmp_path / "alias"
    alias.symlink_to(main_checkout, target_is_directory=True)
    admin = canonical_git.read_gitdir(main_checkout / "spec-dock/.canonical")
    assert admin is not None
    (admin / "gitdir").write_text(str(alias / "spec-dock/.canonical/.git") + "\n", encoding="utf-8")
    _code, result = run(capsys, main_checkout, "canonical", "status")
    assert result["data"]["catalog"]["status"] == "ok" and result["data"]["catalog"]["registration_matches"] is True

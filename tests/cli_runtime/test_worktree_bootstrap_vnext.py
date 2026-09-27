"""Bootstrap runs only as an explicit, bounded operation on a registered target."""

from __future__ import annotations

from pathlib import Path
import sys
import threading
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.worktree_bootstrap_vnext import bootstrap_worktree  # noqa: E402
from spec_dock_runtime.application.worktree_vnext import create_worktree  # noqa: E402
from spec_dock_runtime.cli.admission import admit_writer  # noqa: E402
from spec_dock_runtime.cli.options import parse_vnext  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control  # noqa: E402
from spec_dock_runtime.infra.json_store import read_guarded_json  # noqa: E402
from tests.cli_runtime.test_worktree_create_vnext import _committed_repo  # noqa: E402


def _created(tmp_path: Path):
    common = _committed_repo(tmp_path)
    source = cast("Path", common["repo_root"])
    result = create_worktree(base="HEAD", name="planning", root=tmp_path / "worktrees", **common)
    arguments = {
        "repo_root": source,
        "common_dir": source / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 2,
        "reference": "planning",
    }
    return source, result, arguments


def test_dry_run_and_offline_never_evaluate_make(tmp_path: Path) -> None:
    _source, created, arguments = _created(tmp_path)
    (created.path / "Makefile").write_text("init: $(shell touch trap-ran)\n\ttrue\n", encoding="utf-8")
    planned = bootstrap_worktree(dry_run=True, **arguments)
    assert not planned.started and planned.status == "planned"
    assert not (created.path / "bootstrap-ran").exists()
    assert not (created.path / "trap-ran").exists()
    with pytest.raises(ValueError, match="offline"):
        bootstrap_worktree(offline=True, **arguments)
    assert not (created.path / "bootstrap-ran").exists()
    assert not (created.path / "trap-ran").exists()


def test_explicit_bootstrap_runs_make_and_keeps_diagnostic_record(tmp_path: Path) -> None:
    source, created, arguments = _created(tmp_path)
    result = bootstrap_worktree(timeout=10, **arguments)
    assert result.started and result.status == "succeeded" and result.exit_code == 0
    assert (created.path / "bootstrap-ran").exists()
    record = read_guarded_json(source / ".git" / "spec-dock" / "control" / "bootstrap" / f"{created.id}.json")
    assert record is not None and record[0]["status"] == "succeeded"


def test_timeout_is_partial_and_does_not_block_unrelated_writers(tmp_path: Path) -> None:
    source, created, arguments = _created(tmp_path)
    (created.path / "Makefile").write_text("init:\n\tsleep 10\n", encoding="utf-8")
    result = bootstrap_worktree(timeout=0.1, **arguments)
    assert result.started and result.status == "partial" and result.timed_out
    record = read_guarded_json(source / ".git" / "spec-dock" / "control" / "bootstrap" / f"{created.id}.json")
    assert record is not None and record[0]["status"] == "partial"
    admit_writer(
        load_control(source / ".git"),
        common_dir=source / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=2,
    )


def test_partial_bootstrap_requires_explicit_target_recovery_without_rerunning_make(tmp_path: Path) -> None:
    source, created, arguments = _created(tmp_path)
    makefile = created.path / "Makefile"
    makefile.write_text("init:\n\tsleep 10\n", encoding="utf-8")
    first = bootstrap_worktree(timeout=0.1, **arguments)
    assert first.status == "partial"
    with pytest.raises(ValueError, match="unresolved"):
        bootstrap_worktree(timeout=0.1, **arguments)
    makefile.write_text("init:\n\ttouch retried\n", encoding="utf-8")
    recovered = bootstrap_worktree(recover=True, **arguments)
    assert recovered.status == "reconciled" and not recovered.started
    assert not (created.path / "retried").exists()
    record = read_guarded_json(source / ".git/spec-dock/control/bootstrap" / f"{created.id}.json")
    assert record is not None and record[0]["status"] == "reconciled"
    second = bootstrap_worktree(timeout=10, **arguments)
    assert second.status == "succeeded"
    assert (created.path / "retried").exists()


def test_bootstrap_recovery_cannot_acknowledge_a_live_attempt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from spec_dock_runtime.application import worktree_bootstrap_vnext as module

    _source, _created_worktree, arguments = _created(tmp_path)
    entered = threading.Event()
    release = threading.Event()

    def slow_make(_path: Path, *, timeout: float) -> tuple[bool, int, bool, str]:
        entered.set()
        assert release.wait(5)
        return True, 0, False, ""

    monkeypatch.setattr(module, "_run_make", slow_make)
    failures: list[Exception] = []

    def run_first() -> None:
        try:
            bootstrap_worktree(**arguments)
        except Exception as error:
            failures.append(error)

    worker = threading.Thread(target=run_first)
    worker.start()
    try:
        assert entered.wait(5)
        with pytest.raises(BlockingIOError):
            bootstrap_worktree(recover=True, **arguments)
    finally:
        release.set()
        worker.join(timeout=5)
    assert not failures


def test_bootstrap_cli_recovery_is_explicit() -> None:
    parsed = parse_vnext(["worktree", "bootstrap", "wt:wt1", "--recover", "--yes"])
    assert parsed.command_path == "worktree bootstrap"
    assert parsed.recover and parsed.yes


def test_missing_target_fails_before_make_or_record(tmp_path: Path) -> None:
    source, _created_worktree, arguments = _created(tmp_path)
    with pytest.raises(LookupError):
        bootstrap_worktree(**{**arguments, "reference": "missing"})
    assert not (source / ".git" / "spec-dock" / "control" / "bootstrap" / "missing.json").exists()


def test_output_capture_is_bounded_and_redacts_obvious_credentials(tmp_path: Path) -> None:
    _source, created, arguments = _created(tmp_path)
    (created.path / "Makefile").write_text(
        'init:\n\tpython -c \'print("TOKEN=sekret ") ; print("x" * 100000)\'\n',
        encoding="utf-8",
    )
    outcome = bootstrap_worktree(timeout=10, **arguments)
    assert outcome.status == "succeeded"
    assert "sekret" not in outcome.diagnostic
    assert len(outcome.diagnostic) < 5000
    assert outcome.diagnostic == "make init finished; output omitted"


def test_bootstrap_never_exposes_arbitrary_hook_output(tmp_path: Path) -> None:
    _source, created, arguments = _created(tmp_path)
    secret = "unlabelled-secret-value-409"
    (created.path / "Makefile").write_text(
        f"init:\n\t@printf '{secret}\\n'\n",
        encoding="utf-8",
    )
    outcome = bootstrap_worktree(timeout=10, **arguments)
    assert outcome.status == "succeeded"
    assert secret not in outcome.diagnostic
    assert outcome.diagnostic == "make init finished; output omitted"

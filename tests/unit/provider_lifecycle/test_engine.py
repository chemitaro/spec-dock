from __future__ import annotations

from io import BytesIO
from pathlib import Path
import subprocess
import tarfile

import pytest

from spec_dock.provider_lifecycle.candidate import FIXED_DOMAINS
from spec_dock.provider_lifecycle.contracts import LifecycleMode, LifecycleRequest, Operation
from spec_dock.provider_lifecycle.engine import FAULT_POINTS, ProviderLifecycleEngine
from spec_dock.provider_lifecycle.legacy_fixture import LEGACY_SOURCE_COMMIT
from spec_dock.provider_lifecycle.private_state import PrivateStateError, PrivateStateForeignError
from spec_dock.provider_lifecycle.wire import parse_installation_record, serialize_public_result


def _materialize_legacy_workspace(root: Path) -> None:
    repository = Path(__file__).parents[3]
    sources = [f"src/spec_dock/assets/{suffix}" for _kind, _public, suffix in FIXED_DOMAINS]
    archive = subprocess.run(
        ["git", "archive", "--format=tar", LEGACY_SOURCE_COMMIT, "--", *sources, "spec-dock/spec-dock.version"],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as stream:
        for member in stream:
            if member.name == "spec-dock/spec-dock.version":
                destination = root / member.name
            else:
                domain = next(
                    (
                        item
                        for item in FIXED_DOMAINS
                        if member.name == f"src/spec_dock/assets/{item[2]}"
                        or member.name.startswith(f"src/spec_dock/assets/{item[2]}/")
                    ),
                    None,
                )
                if domain is None:
                    continue
                destination = root / domain[1] / member.name[len(f"src/spec_dock/assets/{domain[2]}") :].lstrip("/")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.issym():
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(member.linkname)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = stream.extractfile(member)
                assert source is not None
                destination.write_bytes(source.read())
                destination.chmod(0o755 if member.mode & 0o111 else 0o644)


def _request(
    root: Path,
    operation: Operation,
    *,
    mode: LifecycleMode = "apply",
    specs_mode: str | None = None,
) -> LifecycleRequest:
    return LifecycleRequest(
        str(root.resolve()),
        mode,
        mode == "apply",
        specs_mode=specs_mode,
        operation=operation,
        seed_policy="create-if-absent" if operation == "install" else "preserve-only",
    )


def _workspace_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    snapshot: dict[str, tuple[object, ...]] = {}
    for path in (root, *root.rglob("*")):
        relative = "." if path == root else path.relative_to(root).as_posix()
        value = path.lstat()
        if path.is_symlink():
            snapshot[relative] = ("symlink", path.readlink().as_posix())
        elif path.is_file():
            snapshot[relative] = ("file", value.st_mode & 0o777, path.read_bytes())
        else:
            snapshot[relative] = ("directory", value.st_mode & 0o777)
    return snapshot


def test_t06_all_fixed_fault_boundaries_converge_to_wire_continuations(tmp_path: Path) -> None:
    for index, point in enumerate(sorted(FAULT_POINTS)):
        workspace = (tmp_path / f"fault-{index}-{point}").resolve()
        workspace.mkdir()
        request = _request(workspace, "install")

        first = ProviderLifecycleEngine(fault_injector=point).execute(request, force=True)
        serialize_public_result(first)
        assert first.status in {"blocked", "partial_failure", "completed", "completed_with_warnings"}

        retry = first
        for _attempt in range(4):
            if retry.status == "completed":
                break
            if retry.continuation["next_action"] == "retry-cleanup":
                command = retry.continuation["next_command"]
                assert isinstance(command, str)
                token = command.split("--provider-cleanup-token ", 1)[1].split(" -- ", 1)[0]
                retry = ProviderLifecycleEngine().execute(request, force=True, cleanup_token=token)
            else:
                if retry.continuation["next_action"] != "none":
                    assert retry.continuation["next_action"] == "run-request"
                retry = ProviderLifecycleEngine().execute(request, force=True)
            serialize_public_result(retry)
        assert retry.status == "completed"
        assert retry.code in {"install-completed", "update-completed", "terminal-cleanup-completed"}


def test_t07_legacy_migration_uninstall_and_old_package_mutation_zero(tmp_path: Path) -> None:
    workspace = (tmp_path / "legacy").resolve()
    workspace.mkdir()
    _materialize_legacy_workspace(workspace)
    protected = workspace / "spec-dock" / "initiatives" / "protected.txt"
    protected.parent.mkdir(parents=True)
    protected.write_bytes(b"consumer-owned\n")
    before_protected = (protected.read_bytes(), protected.lstat().st_ino)

    migrated = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert migrated.status == "completed"
    assert migrated.code == "legacy-migration-completed"
    assert (protected.read_bytes(), protected.lstat().st_ino) == before_protected
    record = parse_installation_record((workspace / "spec-dock/spec-dock.version").read_bytes())
    assert record.state == "ready"
    assert record.version == "0.2.4"

    uninstalled = ProviderLifecycleEngine().execute(
        _request(workspace, "uninstall", specs_mode="keep"),
    )
    assert uninstalled.status == "completed"
    assert uninstalled.code == "uninstall-completed"
    assert parse_installation_record((workspace / "spec-dock/spec-dock.version").read_bytes()).state == (
        "tooling-absent-preserved-data"
    )
    assert not (workspace / "spec-dock/docs").exists()
    assert not (workspace / ".agents/skills/spec-dock").exists()
    assert (protected.read_bytes(), protected.lstat().st_ino) == before_protected

    before_rejected_purge = _workspace_snapshot(workspace)
    rejected = ProviderLifecycleEngine().execute(
        _request(workspace, "uninstall", specs_mode="remove"),
    )
    assert rejected.status == "error"
    assert rejected.code == "spec-history-purge-removed"
    assert _workspace_snapshot(workspace) == before_rejected_purge


@pytest.mark.parametrize(
    ("failure", "expected_code"),
    [
        (PrivateStateForeignError("foreign private authority"), "stage-owner-mismatch"),
        (PrivateStateError("private authority I/O"), "lifecycle-preparation-failed"),
    ],
)
def test_t04_initial_private_authority_preserves_foreign_vs_io_wire_codes(
    monkeypatch, tmp_path: Path, failure: PrivateStateError, expected_code: str
) -> None:
    modes: tuple[LifecycleMode, ...] = ("apply", "dry-run")
    for index, mode in enumerate(modes):
        workspace = (tmp_path / f"authority-{expected_code}-{index}").resolve()
        workspace.mkdir()
        engine = ProviderLifecycleEngine()

        def fail_stores(*_args, **_kwargs):
            raise failure

        monkeypatch.setattr(engine, "_stores", fail_stores)
        before = _workspace_snapshot(workspace)
        result = engine.execute(_request(workspace, "install", mode=mode), force=True)

        serialize_public_result(result)
        assert result.status == "blocked"
        assert result.code == expected_code
        assert result.operation is None
        assert result.candidate_digest is None
        assert result.seed_policy is None
        assert result.mutation_started is False
        assert result.continuation["next_action"] == "none"
        assert _workspace_snapshot(workspace) == before


def test_t04_foreign_stage_owner_is_stage_owner_mismatch_in_candidate_staging(monkeypatch, tmp_path: Path) -> None:
    workspace = (tmp_path / "stage-owner").resolve()
    workspace.mkdir()
    engine = ProviderLifecycleEngine()

    def fail_prepare_stage(*_args, **_kwargs):
        raise PrivateStateForeignError("foreign stage owner")

    monkeypatch.setattr(engine, "_prepare_stage", fail_prepare_stage)
    result = engine.execute(_request(workspace, "install"), force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "stage-owner-mismatch"
    assert result.operation == "install"
    assert result.candidate_digest is not None
    assert result.seed_policy == "create-if-absent"
    assert result.phase == "candidate-staging"
    assert result.last_completed_phase == "preflight"
    assert result.mutation_started is False
    assert result.actions == ()

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.authoring_pack import github_sync_preflight
        from spec_dock_runtime.domain.authoring_pack import source_manifest
    finally:
        sys.path.pop(0)
    return source_manifest, github_sync_preflight


def test_tc_s04_001_003_default_authoring_manifest_does_not_discover_generic_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_manifest, _preflight = _runtime_modules()
    default_source = tmp_path / source_manifest.DEFAULT_SOURCE_PATHS[0]
    default_source.parent.mkdir(parents=True, exist_ok=True)
    default_source.write_text("provider source\n", encoding="utf-8")
    generic = (
        tmp_path
        / "spec-dock"
        / "initiatives"
        / "init-00001"
        / "artifacts"
        / "20260730t010203z--accepted-adr-looking.md"
    )
    generic.parent.mkdir(parents=True, exist_ok=True)
    generic.write_bytes(b"\xff\xfeauthority: accepted\nmirror_eligible: true\n")
    original_open = Path.open

    def guarded_open(path: Path, *args, **kwargs):
        if path == generic:
            raise AssertionError("default authoring discovery must not open generic artifacts")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)

    manifest = source_manifest.build_source_manifest(tmp_path, ())

    assert default_source.relative_to(tmp_path).as_posix() in manifest.source_hashes
    assert generic.relative_to(tmp_path).as_posix() not in manifest.source_hashes


@pytest.mark.parametrize(
    "source_path",
    (
        ".workbench",
        ".workbench/report.md",
        "spec-dock/.workbench",
        "spec-dock/initiatives/init-00001/.workbench/report.md",
    ),
)
def test_source_path_blockers_reject_exact_workbench_component_before_filesystem_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_path: str,
) -> None:
    source_manifest, _preflight = _runtime_modules()
    candidate = tmp_path / source_path
    original_stat = Path.stat
    original_lstat = Path.lstat

    def guarded_stat(path: Path, *args, **kwargs):
        if path == candidate:
            raise AssertionError("workbench source was accessed")
        return original_stat(path, *args, **kwargs)

    def guarded_lstat(path: Path, *args, **kwargs):
        if path == candidate:
            raise AssertionError("workbench source was accessed")
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", guarded_stat)
    monkeypatch.setattr(Path, "lstat", guarded_lstat)

    blockers = source_manifest.source_path_blockers(tmp_path, (source_path,))

    assert blockers == (f"unsafe_source_path:workbench:{source_path}",)


@pytest.mark.parametrize(
    "source_path",
    (
        ".workbench",
        ".workbench/report.md",
        "spec-dock/.workbench",
        "spec-dock/initiatives/init-00001/.workbench/report.md",
    ),
)
def test_build_source_manifest_skips_explicit_workbench_source_before_filesystem_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_path: str,
) -> None:
    source_manifest, _preflight = _runtime_modules()
    candidate = tmp_path / source_path
    original_stat = Path.stat
    original_lstat = Path.lstat

    def guarded_stat(path: Path, *args, **kwargs):
        if path == candidate:
            raise AssertionError("workbench source was accessed")
        return original_stat(path, *args, **kwargs)

    def guarded_lstat(path: Path, *args, **kwargs):
        if path == candidate:
            raise AssertionError("workbench source was accessed")
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", guarded_stat)
    monkeypatch.setattr(Path, "lstat", guarded_lstat)

    manifest = source_manifest.build_source_manifest(tmp_path, (source_path,))

    assert manifest.source_paths == ()
    assert manifest.source_hashes == {}
    assert manifest.source_manifest_hash == hashlib.sha256(b"{}").hexdigest()


def test_build_source_manifest_prunes_workbench_from_parent_walk_before_descendant_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_manifest, _preflight = _runtime_modules()
    package = tmp_path / "package"
    package.mkdir()
    (package / "safe.py").write_bytes(b"safe\n")
    near_name = package / ".workbench-notes"
    near_name.mkdir()
    (near_name / "kept.py").write_bytes(b"kept\n")

    def guarded_walk(path: Path):
        assert Path(path) == package
        child_dirnames = [".workbench", ".workbench-notes"]
        yield package, child_dirnames, ["safe.py"]
        if ".workbench" in child_dirnames:
            raise AssertionError("walk attempted to enter .workbench")
        yield near_name, [], ["kept.py"]

    monkeypatch.setattr(source_manifest, "walk", guarded_walk)

    manifest = source_manifest.build_source_manifest(tmp_path, ("package",))

    assert manifest.source_paths == ("package",)
    assert set(manifest.source_hashes) == {"package/safe.py", "package/.workbench-notes/kept.py"}


def test_source_path_blockers_prune_workbench_from_parent_walk_before_descendant_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_manifest, _preflight = _runtime_modules()
    package = tmp_path / "package"
    package.mkdir()
    near_name = package / ".workbench-notes"
    near_name.mkdir()

    def guarded_walk(path: Path):
        assert Path(path) == package
        child_dirnames = [".workbench", ".workbench-notes"]
        yield package, child_dirnames, []
        if ".workbench" in child_dirnames:
            raise AssertionError("walk attempted to enter .workbench")
        yield near_name, [], []

    monkeypatch.setattr(source_manifest, "walk", guarded_walk)

    blockers = source_manifest.source_path_blockers(tmp_path, ("package",))

    assert blockers == ()


def test_source_manifest_preserves_near_workbench_names(tmp_path: Path) -> None:
    source_manifest, _preflight = _runtime_modules()
    near_name = tmp_path / ".workbench-notes"
    near_name.mkdir()
    (near_name / "report.md").write_bytes(b"report\n")

    blockers = source_manifest.source_path_blockers(tmp_path, (".workbench-notes",))
    manifest = source_manifest.build_source_manifest(tmp_path, (".workbench-notes",))

    assert blockers == ()
    assert manifest.source_paths == (".workbench-notes",)
    assert set(manifest.source_hashes) == {".workbench-notes/report.md"}


def test_source_manifest_allows_absolute_in_repo_source_when_only_repo_ancestor_is_workbench(tmp_path: Path) -> None:
    source_manifest, _preflight = _runtime_modules()
    repo_root = tmp_path / ".workbench" / "repo"
    source = repo_root / "package"
    source.mkdir(parents=True)
    (source / "safe.py").write_bytes(b"safe\n")

    blockers = source_manifest.source_path_blockers(repo_root, (str(source),))
    manifest = source_manifest.build_source_manifest(repo_root, (str(source),))

    assert blockers == ()
    assert manifest.source_paths == ("package",)
    assert set(manifest.source_hashes) == {"package/safe.py"}


def test_source_manifest_rejects_absolute_workbench_source_relative_to_repo(tmp_path: Path) -> None:
    source_manifest, _preflight = _runtime_modules()
    source = tmp_path / ".workbench" / "report.md"
    source.parent.mkdir()
    source.write_bytes(b"scratch\n")

    blockers = source_manifest.source_path_blockers(tmp_path, (str(source),))
    manifest = source_manifest.build_source_manifest(tmp_path, (str(source),))

    assert blockers == (f"unsafe_source_path:workbench:{source}",)
    assert manifest.source_paths == ()
    assert manifest.source_hashes == {}


def test_source_manifest_rejects_absolute_source_through_workbench_intermediate_symlink(tmp_path: Path) -> None:
    source_manifest, _preflight = _runtime_modules()
    safe_dir = tmp_path / "safe"
    safe_dir.mkdir()
    (safe_dir / "report.md").write_bytes(b"safe\n")
    workbench_link = tmp_path / ".workbench" / "link"
    workbench_link.parent.mkdir()
    workbench_link.symlink_to(safe_dir, target_is_directory=True)
    source = workbench_link / "report.md"

    blockers = source_manifest.source_path_blockers(tmp_path, (str(source),))
    manifest = source_manifest.build_source_manifest(tmp_path, (str(source),))

    assert blockers == (f"unsafe_source_path:workbench:{source}",)
    assert manifest.source_paths == ()
    assert manifest.source_hashes == {}


def test_source_manifest_keeps_absolute_outside_blocker_for_workbench_ancestor(tmp_path: Path) -> None:
    source_manifest, _preflight = _runtime_modules()
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside_source = tmp_path / ".workbench" / "outside" / "report.md"
    outside_source.parent.mkdir(parents=True)
    outside_source.write_bytes(b"outside\n")

    blockers = source_manifest.source_path_blockers(repo_root, (str(outside_source),))

    assert blockers == (f"unsafe_source_path:absolute-outside-repo:{outside_source}",)


def test_preflight_stops_before_manifest_and_remote_observer_for_workbench_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _source_manifest, preflight = _runtime_modules()
    workbench_source = tmp_path / ".workbench" / "report.md"
    workbench_source.parent.mkdir()
    workbench_source.write_text("super-secret-body\n", encoding="utf-8")

    def fail_manifest(*_args, **_kwargs):
        raise AssertionError("manifest construction must not start")

    def fail_observer(*_args, **_kwargs):
        raise AssertionError("remote observation must not start")

    monkeypatch.setattr(preflight, "build_source_manifest", fail_manifest)

    result = preflight.run_github_sync_preflight(
        preflight.GitHubSyncPreflightRequest(
            repo_root=tmp_path,
            source_paths=(".workbench/report.md",),
        ),
        remote_observer=fail_observer,
    )

    assert result.status == "blocked"
    assert result.github_sync == "failed"
    assert result.source_manifest.source_paths == ()
    assert result.source_manifest.source_hashes == {}
    assert result.blockers == ("unsafe_source_path:workbench:.workbench/report.md",)
    assert "report" not in " ".join(result.remediation)
    assert "super-secret-body" not in repr(result.to_dict())

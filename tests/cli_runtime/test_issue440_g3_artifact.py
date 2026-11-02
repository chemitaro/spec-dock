"""Artifact create/import/list/show in canonical mode preserve evidence without common control (iss-00440).

Replaces tests/cli_runtime/test_issue413_artifact.py, which ran on the retired schema-3 dependency workspace. A
Scope's Artifacts live in its flat catalog directory `<catalog>/<bucket>/<ID>/artifacts/` (shown through the
`spec-dock/initiatives` link); `@root` Artifacts stay in the checkout's `spec-dock/artifacts/`.

Canonical Scope publication reports an attempted publication that failed as `effects: [artifact failed]` where
the legacy publication reported no effects.
"""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_writes import WriteWorld
from tests.support.legacy_contracts_g3 import cli, make_world, select

SCOPE = "iss-00003"
SHOWN = "spec-dock/initiatives/00000-00999/iss-00003"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = make_world(tmp_path, monkeypatch, capsys, write=True)
    world.scope("epic", 2, "Fixture", parent=1)
    world.scope("issue", 3, "Fixture", parent=2)
    assert isinstance(world, WriteWorld)
    return world


def _artifact(capsys: pytest.CaptureFixture[str], root: Path, *argv: str) -> tuple[int, dict]:
    return cli(capsys, "--project", str(root), "artifact", *argv, "--json")


def _create(capsys: pytest.CaptureFixture[str], root: Path, *options: str, scope: str = SCOPE) -> tuple[int, dict]:
    return _artifact(capsys, root, "create", "--scope", scope, "--type", "research", "--title", "Evidence", *options)


def _fixed_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-10-01T00:00:00+00:00")


def _failed_attempt(result: dict, name: str) -> list[dict[str, str]]:
    """Canonical Scope publication reports the attempted Artifact as failed (legacy: no effects)."""
    assert result["status"] == "failed"
    return [{"kind": "artifact", "status": "failed", "target": f"{SHOWN}/artifacts/{name}"}]


@pytest.mark.parametrize("kind", ["blank", "research", "interview", "disc", "decision-candidate", "adr"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_root_create_supports_all_templates_and_preview_without_unrelated_scope_metadata(
    world: WriteWorld, capsys: pytest.CaptureFixture[str], kind: str, dry_run: bool
) -> None:
    root = world.main
    flags = ["--dry-run"] if dry_run else []
    code, result = _artifact(
        capsys,
        root,
        "create",
        "--scope",
        "@root",
        "--type",
        kind,
        "--title",
        "Root evidence",
        "--slug",
        "root-evidence",
        *flags,
    )
    assert code == 0, result
    artifact = result["data"]["result"]["artifact"]
    path = root / artifact["path"]
    assert artifact["scope_id"] == "root" and path.parent == root / "spec-dock/artifacts"
    assert result["data"]["result"]["changed"] is not dry_run
    assert path.exists() is not dry_run
    if dry_run:
        assert result["status"] == "planned" and not path.parent.exists()
        assert all(effect["status"] == "planned" for effect in result["effects"])
    else:
        text = path.read_text()
        assert "Root evidence" in text and artifact["id"] in text and "<SCOPE_ID>" not in text
        code, listed = _artifact(capsys, root, "list", "--scope", "@root")
        assert code == 0 and listed["data"]["result"]["items"] == [artifact]
    assert world.changesets() == [] and world.writes() == []
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_root_create_renders_legacy_scope_placeholders_without_inventing_a_scope_or_github_issue(
    world: WriteWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    (root / "spec-dock/templates/artifacts/research.md").write_text(
        "<SCOPE_ID>|<INIT_ID>|<INIT_TITLE>|<EPIC_ID>|<EPIC_TITLE>|<ISS_ID>|<ISS_TITLE>|"
        "<FEATURE_ID>|<FEATURE_NAME>|<GITHUB_ISSUE_NUMBER_OR_URL>|<ISSUE_NUMBER_OR_URL>\n<RESEARCH_TITLE>\n"
    )
    code, result = _artifact(
        capsys, root, "create", "--scope", "@root", "--type", "research", "--title", "Root artifact"
    )
    assert code == 0, result
    artifact = result["data"]["result"]["artifact"]
    assert (root / artifact["path"]).read_text() == "root||||||||||\nRoot artifact\n"


@pytest.mark.parametrize("failure", ["missing", "denied", "io", "invalid"])
def test_import_source_errors_keep_the_public_exit_class_and_hide_the_source_path(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], failure: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    source = tmp_path / "private-source.bin"
    if failure != "missing":
        source.write_bytes(b"private source bytes")
        native_open = os.open

        def open_file(path, flags, mode=0o777, **kwargs):
            if path == "private-source.bin" and "dir_fd" in kwargs:
                if failure == "invalid":
                    raise ValueError(f"private-parent body hash count sentinel: {source}")
                raise OSError(errno.EACCES if failure == "denied" else errno.EIO, "fixture source failed", str(source))
            return native_open(path, flags, mode, **kwargs)

        monkeypatch.setattr(os, "open", open_file)
    assert main(["--project", str(root), "artifact", "import", "file", str(source), "--scope", SCOPE, "--json"]) == (
        4 if failure == "missing" else 3 if failure == "invalid" else 5
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and str(source) not in output.out and "private source bytes" not in output.out
    assert "private-parent" not in output.out and "body hash count sentinel" not in output.out
    assert result["status"] == "failed" and result["effects"] == [] and not (owner / "artifacts").exists()
    assert world.changesets() == []
    if failure != "missing":
        assert source.read_bytes() == b"private source bytes"


@pytest.mark.parametrize("target", ["iss-00004", "iss-00999"])
def test_import_resolves_the_exact_owner_before_opening_the_source(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], target: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    source = tmp_path / "private-source.bin"
    source.write_bytes(b"private source bytes")
    native_open = os.open

    def refuse_source_open(path, flags, mode=0o777, **kwargs):
        if path == source.name and "dir_fd" in kwargs:
            pytest.fail("An invalid owner must fail before the explicit source is opened")
        return native_open(path, flags, mode, **kwargs)

    with monkeypatch.context() as patched:
        patched.setattr(os, "open", refuse_source_open)
        assert (
            main(["--project", str(root), "artifact", "import", "file", str(source), "--scope", target, "--json"]) == 4
        )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["error"]["code"] == "SCOPE_NOT_FOUND" and result["effects"] == []
    assert str(source) not in output.out and "private source bytes" not in output.out
    assert source.read_bytes() == b"private source bytes" and not (owner / "artifacts").exists()
    assert world.changesets() == []


@pytest.mark.parametrize("operation", ["create", "import"])
def test_artifact_shared_slot_exhaustion_preserves_all_evidence_without_a_candidate(
    world: WriteWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    operation: str,
) -> None:
    root, owner = world.main, world.find(SCOPE)
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-07-30T01:02:03+00:00")
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    timestamp = "20260730t010203z"
    (artifacts / f"{timestamp}-adr-existing.md").write_bytes(b"standard")
    for suffix in range(1, 100):
        name = f"{timestamp}-{suffix:02d}-existing.md" if suffix % 2 else f"{timestamp}-{suffix:02d}--existing.bin"
        (artifacts / name).write_bytes(str(suffix).encode())
    before = {path.name: path.read_bytes() for path in artifacts.iterdir()}
    documents = {path.name: path.read_bytes() for path in owner.glob("*.md")}
    source = tmp_path / "private-source.bin"
    source.write_bytes(b"private source bytes")
    arguments = (
        ["create", "--type", "research", "--title", "Evidence", "--slug", "evidence"]
        if operation == "create"
        else ["import", "file", str(source)]
    )
    assert main(["--project", str(root), "artifact", *arguments, "--scope", SCOPE, "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "LOCAL_IO_FAILED" and "Artifact timestamp suffix exhaustion" in output.out
    assert str(source) not in output.out and "private source bytes" not in output.out
    assert {path.name: path.read_bytes() for path in artifacts.iterdir()} == before
    assert {path.name: path.read_bytes() for path in owner.glob("*.md")} == documents
    assert source.read_bytes() == b"private source bytes" and world.changesets() == []
    assert not (root / ".git/spec-dock").exists()


def test_root_artifact_catalog_reads_only_identity_without_control_or_body(
    world: WriteWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    catalog = root / "spec-dock/artifacts"
    catalog.mkdir()
    document = catalog / "20261001t000000z--private.bin"
    document.write_bytes(b"private content must not appear in stdout")
    before = document.read_bytes()
    code, listed = _artifact(capsys, root, "list", "--scope", "@root")
    assert code == 0, listed
    view = {
        "id": document.name,
        "scope_id": "root",
        "path": document.relative_to(root).as_posix(),
        "type": "generic-file",
    }
    assert listed["data"] == {"kind": "artifact-list", "result": {"scope_id": "root", "items": [view]}}
    assert listed["effects"] == []
    assert main(["--project", str(root), "artifact", "show", document.name, "--scope", "@root", "--json"]) == 0
    shown = capsys.readouterr().out
    assert json.loads(shown)["data"] == {"kind": "artifact", "result": {"artifact": view, "changed": False}}
    assert "private content" not in shown and document.read_bytes() == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_scope_artifact_catalog_preserves_typed_historical_unknown_and_generic_evidence_without_opening_bodies(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = world.main, world.find(SCOPE)
    catalog = owner / "artifacts"
    catalog.mkdir()
    cases = [
        ("001-note-old.md", "001-note", "historical-note"),
        ("20260925t000000z-research-study.md", "20260925t000000z-research", "research"),
        ("20260925t000001z-newtype-study.md", "20260925t000001z", "untyped-markdown"),
        ("20260925t000002z--source.bin", "20260925t000002z--source.bin", "generic-file"),
    ]
    for name, _artifact_id, _kind in cases:
        (catalog / name).write_bytes(b"private evidence body\x00\xff")
    before = tree_digest(root), tree_digest(owner)
    native_open = os.open

    def refuse_evidence_body(path, flags, mode=0o777, **kwargs):
        if os.fsdecode(path).rsplit(os.sep, 1)[-1] in {row[0] for row in cases}:
            pytest.fail("Artifact list/show must not open evidence bodies")
        return native_open(path, flags, mode, **kwargs)

    with monkeypatch.context() as patched:
        patched.setattr(os, "open", refuse_evidence_body)
        assert main(["--project", str(root), "artifact", "list", "--scope", SCOPE, "--json"]) == 0
        output = capsys.readouterr()
        result = json.loads(output.out)
        expected = [
            {"id": artifact_id, "scope_id": SCOPE, "path": f"{SHOWN}/artifacts/{name}", "type": kind}
            for name, artifact_id, kind in cases
        ]
        assert result["data"]["result"]["items"] == expected and result["effects"] == []
        assert "private evidence body" not in output.out + output.err
        assert main(["--project", str(root), "artifact", "show", "001-note", "--scope", SCOPE, "--json"]) == 0
        output = capsys.readouterr()
        assert json.loads(output.out)["data"]["result"]["artifact"] == expected[0]
        assert "private evidence body" not in output.out + output.err
    assert (tree_digest(root), tree_digest(owner)) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("scope", ["@root", SCOPE])
def test_duplicate_artifact_timestamp_slots_refuse_catalog_reads_without_changes(
    world: WriteWorld, capsys: pytest.CaptureFixture[str], scope: str
) -> None:
    root = world.main
    owner = root / "spec-dock" if scope == "@root" else world.find(SCOPE)
    catalog = owner / "artifacts"
    catalog.mkdir()
    first = catalog / "20260925t000000z--first.bin"
    first.write_bytes(b"first evidence")
    (catalog / "20260925t000000z--second.bin").write_bytes(b"second evidence")
    before = tree_digest(root), tree_digest(catalog)
    for command in (["list"], ["show", first.name]):
        code, result = _artifact(capsys, root, *command, "--scope", scope)
        assert code == 3, result
        assert result["error"]["message"] == "ARTIFACT_CATALOG_INVALID" and result["effects"] == []
    assert (tree_digest(root), tree_digest(catalog)) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_create_artifact_preserves_six_type_template_and_existing_scope_files(
    world: WriteWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = world.main, world.find(SCOPE)
    documents = {path.name: path.read_bytes() for path in owner.iterdir()}
    assert world.run("scope", "show", SCOPE)[0] == 0  # --offline reads the structure this read stored
    code, result = _artifact(
        capsys,
        root,
        "create",
        "--scope",
        SCOPE,
        "--type",
        "research",
        "--title",
        "調査資料",
        "--slug",
        "evidence",
        "--offline",
    )
    assert code == 0, result
    artifact = result["data"]["result"]["artifact"]
    path = root / artifact["path"]
    assert artifact["scope_id"] == SCOPE and artifact["type"] == "research"
    assert path.parent.resolve() == owner / "artifacts" and path.name.endswith("-research-evidence.md")
    text = path.read_text()
    assert artifact["id"] in text and "調査資料" in text and f'親: ["{SCOPE}"]' in text
    assert result["data"]["result"]["changed"] is True
    assert result["effects"] == [{"kind": "artifact", "status": "succeeded", "target": artifact["path"]}]
    assert {path.name: path.read_bytes() for path in owner.iterdir() if path.name != "artifacts"} == documents
    assert world.writes() == [] and not (root / ".git/spec-dock").exists()


def test_import_one_opaque_file_to_root_preserves_bytes_name_source_and_privacy(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    source = tmp_path / "Private 資料.PNG"
    payload = b"\x00\xffprivate binary content"
    source.write_bytes(payload)
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "import",
            "file",
            str(source),
            "--scope",
            "@root",
            "--offline",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr().out
    result = json.loads(output)
    artifact = result["data"]["result"]["artifact"]
    destination = root / artifact["path"]
    assert artifact["scope_id"] == "root" and artifact["type"] == "generic-file"
    assert destination.parent == root / "spec-dock/artifacts" and destination.name.endswith("--Private 資料.PNG")
    assert artifact["id"] == destination.name and destination.read_bytes() == payload and source.read_bytes() == payload
    assert str(source) not in output and "private binary content" not in output
    assert result["effects"] == [
        {"kind": "artifact", "status": "succeeded", "target": destination.relative_to(root).as_posix()}
    ]
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("kind", ["blank", "research", "interview", "disc", "decision-candidate", "adr"])
def test_all_creation_templates_and_owner_local_timestamp_slots_are_preserved(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    monkeypatch.setenv("USER", "Fixture author")
    _fixed_clock(monkeypatch)
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    existing = artifacts / "20261001t000000z--evidence.bin"
    existing.write_bytes(b"existing evidence")
    code, result = _artifact(
        capsys, root, "create", "--scope", SCOPE, "--type", kind, "--title", "資料", "--slug", "proof"
    )
    assert code == 0, result
    artifact = result["data"]["result"]["artifact"]
    path = root / artifact["path"]
    assert path.name.startswith("20261001t000000z-01-") and artifact["id"] in path.read_text()
    assert "<SCOPE_ID>" not in path.read_text() and "<YOUR_NAME>" not in path.read_text()
    assert '作成者: "Fixture author"' in path.read_text()
    assert ('authority: "draft"' if kind == "adr" else f'template: "{kind}"') in path.read_text()
    assert existing.read_bytes() == b"existing evidence"
    assert not list(artifacts.glob(".publish-*")) and not (root / ".git/spec-dock").exists()


def test_parallel_different_slug_candidates_in_one_timestamp_slot_are_conflicts_without_overwrite(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A canonical Scope Artifact is published under the catalog lock, so a nested in-process create would wait
    # for that lock instead of racing; the unlocked `@root` publication keeps the same naming race.
    root = world.main
    _fixed_clock(monkeypatch)
    artifacts = root / "spec-dock/artifacts"
    artifacts.mkdir()
    real_open = os.open
    second: list[int] = []
    prefix = ["--project", str(root), "artifact", "create", "--scope", "@root", "--type", "research", "--title", "資料"]

    def open_file(path, flags, mode=0o777, **kwargs):
        descriptor = real_open(path, flags, mode, **kwargs)
        if isinstance(path, str) and path.startswith(".publish-") and flags & os.O_CREAT and not second:
            second.append(-1)
            second[0] = main([*prefix, "--slug", "second", "--json"])
        return descriptor

    monkeypatch.setattr(os, "open", open_file)
    assert main([*prefix, "--slug", "first", "--json"]) == 0
    results = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert second == [3] and results[0]["effects"] == [] and results[0]["data"]["result"]["artifact"] is None
    assert results[1]["data"]["result"]["changed"] is True
    assert [path.name for path in artifacts.iterdir()] == ["20261001t000000z-research-first.md"]


@pytest.mark.parametrize("operation", ["create", "import"])
def test_artifact_dry_run_plans_an_identity_without_directory_stage_or_source_change(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], operation: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    source = tmp_path / "source.bin"
    source.write_bytes(b"opaque evidence")
    command = (
        ["create", "--type", "interview", "--title", "Interview", "--slug", "interview-evidence"]
        if operation == "create"
        else ["import", "file", str(source)]
    )
    before = tree_digest(owner)
    code, result = _artifact(capsys, root, *command, "--scope", SCOPE, "--dry-run")
    assert code == 0, result
    data = result["data"]["result"]
    assert (
        result["status"] == "planned"
        and data["can_apply"] is True
        and data["blockers"] == []
        and data["changed"] is False
    )
    assert data["artifact"]["scope_id"] == SCOPE and result["effects"][0]["status"] == "planned"
    assert not (owner / "artifacts").exists() and source.read_bytes() == b"opaque evidence"
    assert not (root / "spec-dock/.agent").exists() and tree_digest(owner) == before
    assert world.changesets() == [] and world.writes() == []


@pytest.mark.skipif(os.name != "posix", reason="native executable Git diagnostics")
def test_artifact_post_publication_git_failure_retains_confirmed_file_and_original_diagnostic(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Only the `@root` publication observes Git again after publishing; a canonical Scope publication does not.
    root = world.main
    _fixed_clock(monkeypatch)
    destination = root / "spec-dock/artifacts/20261001t000000z-research-evidence.md"
    native_git = shutil.which("git")
    assert native_git is not None
    bin_dir = tmp_path / "git-bin"
    bin_dir.mkdir()
    executable = bin_dir / "git"
    diagnostic = "fixture: original post-publication Git error\nsecond line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport os, sys\nif sys.argv[-2:] == ['rev-parse', '--show-toplevel'] and os.path.exists({str(destination)!r}):\n sys.stderr.write({diagnostic!r}); sys.exit(73)\nos.execv({native_git!r}, [{native_git!r}, *sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    code, result = _create(capsys, root, "--slug", "evidence", scope="@root")
    assert code == 6, result
    assert destination.exists() and result["status"] == "partial"
    assert result["data"]["result"]["changed"] is True
    assert result["effects"] == [
        {"kind": "artifact", "status": "succeeded", "target": destination.relative_to(root).as_posix()}
    ]
    assert result["error"]["code"] == "GIT_FAILED" and result["error"]["details"]["git"]["stderr"] == diagnostic
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert result["recovery"]["can_rollback"] is False and result["recovery"]["can_resume"] is False


def test_replaced_stage_is_preserved_and_is_never_published_as_the_artifact(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = world.main, world.find(SCOPE)
    _fixed_clock(monkeypatch)
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    stage = artifacts / ".publish-20261001t000000z.tmp"
    real_fsync = os.fsync
    changed = False

    def fsync(descriptor: int) -> None:
        nonlocal changed
        if stage.exists() and not changed:
            changed = True
            stage.rename(artifacts / "held-original.tmp")
            stage.write_bytes(b"actor stage that must never become the Artifact")
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    code, result = _create(capsys, root, "--slug", "evidence")
    assert code == 3, result
    assert changed and result["effects"] == _failed_attempt(result, "20261001t000000z-research-evidence.md")
    assert stage.read_bytes() == b"actor stage that must never become the Artifact"
    assert not (artifacts / "20261001t000000z-research-evidence.md").exists()


@pytest.mark.parametrize("replacement", ["owner", "artifacts"])
def test_artifact_publication_refuses_a_replaced_directory_and_preserves_actor_files(
    world: WriteWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    replacement: str,
) -> None:
    root, owner = world.main, world.find(SCOPE)
    _fixed_clock(monkeypatch)
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    preserved = {"rules.md": b"actor rules must survive", "existing.bin": b"opaque evidence\x00\xff"}
    for name, payload in preserved.items():
        (artifacts / name).write_bytes(payload)
    directory = owner if replacement == "owner" else artifacts
    held = tmp_path / "held-directory"
    stage = artifacts / ".publish-20261001t000000z.tmp"
    native_fsync = os.fsync
    changed = False

    def replace_directory(descriptor: int) -> None:
        nonlocal changed
        if stage.exists() and not changed:
            changed = True
            directory.rename(held)
            shutil.copytree(held, directory, ignore=shutil.ignore_patterns(".publish-*"))
            (directory / "actor-only.bin").write_bytes(b"replacement actor bytes")
        native_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", replace_directory)
    code, result = _create(capsys, root, "--slug", "evidence")
    assert code == 3, result
    assert changed and result["data"]["result"]["artifact"] is None
    assert result["effects"] == _failed_attempt(result, "20261001t000000z-research-evidence.md")
    assert (directory / "actor-only.bin").read_bytes() == b"replacement actor bytes"
    held_artifacts = held / "artifacts" if replacement == "owner" else held
    for name, payload in preserved.items():
        assert (artifacts / name).read_bytes() == payload and (held_artifacts / name).read_bytes() == payload
    assert not list(artifacts.glob("*research-evidence.md")) and not list(held_artifacts.glob("*research-evidence.md"))
    assert not list(artifacts.glob(".publish-*")) and not list(held_artifacts.glob(".publish-*"))
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("operation", ["create", "import"])
def test_artifact_dynamic_owner_and_guard_capture_one_direct_selection_without_changing_it(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], operation: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    record = select(world, SCOPE, 3)
    before = record.read_bytes()
    source = tmp_path / "evidence.bin"
    source.write_bytes(b"evidence")
    command = (
        ["create", "--type", "interview", "--title", "Interview", "--slug", "evidence"]
        if operation == "create"
        else ["import", "file", str(source)]
    )
    code, result = _artifact(
        capsys, root, *command, "--scope", "@epic", "--expect-current", SCOPE, "--expect-backend", "github"
    )
    assert code == 0, result
    assert result["data"]["result"]["artifact"]["scope_id"] == "epic-00002" and record.read_bytes() == before
    assert not (owner / "artifacts").exists() and (world.find("epic-00002") / "artifacts").is_dir()


@pytest.mark.parametrize("source_kind", ["symlink", "hardlink", "directory", "fifo"])
def test_import_rejects_non_single_regular_sources_without_writes_or_source_disclosure(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], source_kind: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    real = tmp_path / "private.bin"
    real.write_bytes(b"private evidence")
    source = tmp_path / "bad-source.bin"
    if source_kind == "symlink":
        source.symlink_to(real)
    elif source_kind == "hardlink":
        os.link(real, source)
    elif source_kind == "directory":
        source.mkdir()
    elif hasattr(os, "mkfifo"):
        os.mkfifo(source)
    else:
        pytest.skip("native FIFO unavailable")
    assert main(["--project", str(root), "artifact", "import", "file", str(source), "--scope", SCOPE, "--json"]) == 3
    output = capsys.readouterr().out
    assert str(source) not in output and "private evidence" not in output and json.loads(output)["effects"] == []
    assert not (owner / "artifacts").exists() and real.read_bytes() == b"private evidence"
    assert world.changesets() == []


@pytest.mark.parametrize("dry_run", [False, True])
def test_redirected_artifact_directory_is_refused_without_external_changes(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, owner = world.main, world.find(SCOPE)
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "marker.bin"
    marker.write_bytes(b"preserve")
    (owner / "artifacts").symlink_to(outside, target_is_directory=True)
    options = ["--dry-run"] if dry_run else []
    code, result = _create(capsys, root, "--slug", "proof", *options)
    assert code in (3, 5), result
    assert result["effects"] == [] and list(outside.iterdir()) == [marker] and marker.read_bytes() == b"preserve"
    assert world.changesets() == []


def test_unknown_link_outcome_preserves_artifact_and_candidate_without_automatic_retry(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = world.main, world.find(SCOPE)
    (owner / "artifacts").mkdir()
    real_link = os.link
    attempted: list[str] = []

    def link(source, destination, **kwargs):
        attempted.append(destination)
        real_link(source, destination, **kwargs)
        raise OSError("fixture: publication reply unavailable")

    monkeypatch.setattr(os, "link", link)
    code, result = _create(capsys, root, "--slug", "evidence")
    assert code == 6, result
    assert len(attempted) == 1 and result["effects"][0]["status"] == "unknown"
    assert result["data"]["result"] == {"artifact": None, "changed": False}
    files = list((owner / "artifacts").iterdir())
    assert len(files) == 2 and files[0].read_bytes() == files[1].read_bytes()
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_confirmed_artifact_survives_descriptor_cleanup_failure(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = world.main, world.find(SCOPE)
    (owner / "artifacts").mkdir()
    real_close = os.close
    real_open = os.open
    failed = False
    held: list[int] = []

    def open_file(path, flags, mode=0o777, **kwargs):
        descriptor = real_open(path, flags, mode, **kwargs)
        if isinstance(path, str) and path.startswith(".publish-") and flags & os.O_CREAT:
            held.append(descriptor)
        return descriptor

    def close(descriptor):
        nonlocal failed
        opened = os.fstat(descriptor)
        published = list((owner / "artifacts").glob("*research-evidence.md"))
        actual = published[0].stat() if published else None
        completed = (
            descriptor in held
            and actual is not None
            and stat.S_ISREG(opened.st_mode)
            and (opened.st_dev, opened.st_ino) == (actual.st_dev, actual.st_ino)
            and not list((owner / "artifacts").glob(".publish-*"))
        )
        real_close(descriptor)
        if completed and not failed:
            failed = True
            raise OSError("fixture: confirmed publication close failed")

    monkeypatch.setattr(os, "open", open_file)
    monkeypatch.setattr(os, "close", close)
    code, result = _create(capsys, root, "--slug", "evidence")
    assert code == 6, result
    assert failed and result["data"]["result"]["changed"] is True
    published = list((owner / "artifacts").glob("*research-evidence.md"))
    assert result["effects"][0]["status"] == "succeeded" and published
    # the confirmed publication is recorded for saving
    (changeset,) = world.changesets()
    assert changeset["paths"] == [published[0].relative_to(world.catalog).as_posix()]


@pytest.mark.skipif(os.name != "posix", reason="native POSIX common-directory exclusion")
def test_artifact_creation_does_not_wait_on_another_process_start_lock(world: WriteWorld) -> None:
    import fcntl

    root, owner = world.main, world.find(SCOPE)
    descriptor = os.open(root / ".git", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(root),
                "artifact",
                "create",
                "--scope",
                SCOPE,
                "--type",
                "research",
                "--title",
                "Evidence",
                "--slug",
                "evidence",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == "" and json.loads(result.stdout)["data"]["result"]["changed"] is True
        assert list((owner / "artifacts").glob("*research-evidence.md")) and not (root / ".git/spec-dock").exists()
    finally:
        os.close(descriptor)


def test_root_artifact_import_and_catalog_do_not_require_unrelated_scope_metadata(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    # neither GitHub nor the catalog is reachable: `@root` Artifacts depend on no Scope input
    (root / "spec-dock/initiatives").unlink()
    path = [entry for entry in os.environ["PATH"].split(os.pathsep) if entry != str(world.gh.bin_dir)]
    monkeypatch.setenv("PATH", os.pathsep.join(path))
    assert shutil.which("gh") is None or Path(shutil.which("gh") or "").parent != world.gh.bin_dir
    source = tmp_path / "evidence.bin"
    source.write_bytes(b"evidence")
    code, imported = _artifact(capsys, root, "import", "file", str(source), "--scope", "@root")
    assert code == 0, imported
    created = imported["data"]["result"]["artifact"]
    code, listed = _artifact(capsys, root, "list", "--scope", "@root")
    assert code == 0 and listed["data"]["result"]["items"] == [created]


def test_custom_artifact_template_keeps_existing_scope_and_github_replacement_tokens(
    world: WriteWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    template = root / "spec-dock/templates/artifacts/research.md"
    template.write_text(
        "<ARTIFACT_ID> <ARTIFACT_TITLE> <ISS_ID> <ISS_TITLE> <FEATURE_ID> <FEATURE_NAME> <EPIC_ID> <INIT_ID> <ISSUE_NUMBER_OR_URL> <GITHUB_ISSUE_NUMBER_OR_URL>\n"
    )
    code, result = _create(capsys, root, "--slug", "proof")
    assert code == 0, result
    artifact = result["data"]["result"]["artifact"]
    text = (root / artifact["path"]).read_text()
    assert text == f"{artifact['id']} Evidence iss-00003 Fixture iss-00003 Fixture epic-00002 init-00001 #3 #3\n"


def test_uncertain_artifact_directory_creation_reports_partial_and_preserves_it_without_publication(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `@root` keeps this contract; the canonical Scope publication matches it (iss-00507, the next test).
    root = world.main
    owner = root / "spec-dock"
    real_mkdir = os.mkdir
    attempted = False

    def mkdir(path, mode=0o777, **kwargs):
        nonlocal attempted
        real_mkdir(path, mode, **kwargs)
        if path == "artifacts" and not attempted:
            attempted = True
            raise OSError("fixture: directory creation reply unavailable")

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, result = _create(capsys, root, "--slug", "proof", scope="@root")
    assert code == 6, result
    assert attempted and (owner / "artifacts").is_dir() and list((owner / "artifacts").iterdir()) == []
    assert result["effects"][0] == {
        "kind": "artifact.directory",
        "status": "unknown",
        "target": (owner / "artifacts").relative_to(root).as_posix(),
    }
    assert result["effects"][1]["status"] == "not_attempted"


def test_uncertain_scope_artifact_directory_creation_reports_partial_and_preserves_it_without_publication(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # iss-00507 R-02: the canonical Scope publication reports a created `artifacts/` like `@root` does
    root, owner = world.main, world.find(SCOPE)
    assert not (owner / "artifacts").exists()
    real_mkdir = os.mkdir
    attempted: list[bool] = []

    def mkdir(path, mode=0o777, **kwargs):
        real_mkdir(path, mode, **kwargs)
        if path == "artifacts" and not attempted:
            attempted.append(True)
            raise OSError("fixture: directory creation reply unavailable")

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, result = _create(capsys, root, "--slug", "proof")
    assert attempted and (code, result["status"]) == (6, "partial"), result
    assert result["error"]["code"] == "ARTIFACT_PUBLICATION_INCOMPLETE" and result["recovery"] is not None
    assert (owner / "artifacts").is_dir() and list((owner / "artifacts").iterdir()) == []
    assert result["effects"][0] == {"kind": "artifact.directory", "status": "unknown", "target": f"{SHOWN}/artifacts"}
    assert result["effects"][1]["kind"] == "artifact" and result["effects"][1]["status"] == "not_attempted"
    assert len(result["effects"]) == 2
    assert result["data"]["result"] == {"artifact": None, "changed": False}
    assert world.changesets() == []


def test_failure_after_creating_the_scope_artifact_directory_reports_it_succeeded(
    world: WriteWorld, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # iss-00507 R-02: the directory was confirmed created; the following publication failed before any link
    root, owner = world.main, world.find(SCOPE)
    real_open = os.open
    failed: list[bool] = []

    def open_file(path, flags, mode=0o777, **kwargs):
        if isinstance(path, str) and path.startswith(".publish-") and flags & os.O_CREAT and not failed:
            failed.append(True)
            raise OSError("fixture: stage creation failed")
        return real_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", open_file)
    code, result = _create(capsys, root, "--slug", "proof")
    assert failed and (code, result["status"]) == (6, "partial"), result
    assert result["error"]["code"] == "ARTIFACT_PUBLICATION_INCOMPLETE"
    assert (owner / "artifacts").is_dir() and list((owner / "artifacts").iterdir()) == []
    assert result["effects"][0] == {"kind": "artifact.directory", "status": "succeeded", "target": f"{SHOWN}/artifacts"}
    assert result["effects"][1:] == [{"kind": "artifact", "status": "failed", "target": result["effects"][1]["target"]}]
    assert result["data"]["result"] == {"artifact": None, "changed": False}


def test_artifact_catalog_never_discloses_a_directory_swapped_to_an_external_alias(
    world: WriteWorld, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = world.main, world.find(SCOPE)
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    (artifacts / "20261001t000000z-research-owned.md").write_text("owned")
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "20261001t000001z--private-name.bin"
    secret.write_bytes(b"private external evidence")
    real_scandir = os.scandir
    calls = 0
    held = artifacts.stat()

    def scandir(path):
        nonlocal calls
        matches = path == artifacts
        if isinstance(path, int):
            opened = os.fstat(path)
            matches = (opened.st_dev, opened.st_ino) == (held.st_dev, held.st_ino)
        if matches:
            calls += 1
            if calls == 2:
                artifacts.rename(owner / "moved-artifacts")
                artifacts.symlink_to(outside, target_is_directory=True)
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", scandir)
    # canonical mode stops with LOCAL_IO_FAILED (exit 5) where the legacy reader reported exit 3
    assert main(["--project", str(root), "artifact", "list", "--scope", SCOPE, "--json"]) in (3, 5)
    output = capsys.readouterr().out
    assert json.loads(output)["status"] == "failed"
    assert "private-name.bin" not in output and "private external evidence" not in output
    assert json.loads(output)["effects"] == [] and secret.read_bytes() == b"private external evidence"


def test_artifact_help_describes_v2_file_publication_and_rejects_retired_recovery_before_context(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["artifact", "create", "--help"]) == 0
    help_text = capsys.readouterr().out
    assert "artifact:{id,scope_id,path,type}" in help_text and "shared counter" in help_text
    assert "specdock.cli/v2" in help_text and "journal" not in help_text
    code, result = cli(
        capsys,
        "--project",
        str(tmp_path / "missing"),
        "artifact",
        "create",
        "--scope",
        SCOPE,
        "--type",
        "research",
        "--title",
        "Evidence",
        "--resume",
        "old-operation",
        "--json",
    )
    assert code == 2
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == [] and list(tmp_path.iterdir()) == []


# --- added by iss-00440 (spec): an invalid Artifact --slug writes nothing ---


@pytest.mark.parametrize("scope", [SCOPE, "@root"])
def test_invalid_artifact_slug_stops_without_github_or_catalog_writes(
    world: WriteWorld, capsys: pytest.CaptureFixture[str], scope: str
) -> None:
    root, owner = world.main, world.find(SCOPE)
    before = tree_digest(root), tree_digest(world.catalog.resolve())
    code, result = _create(capsys, root, "--slug", "Add_Token", scope=scope)
    # the slug validator's RuntimeError reaches the dispatcher as a local failure (today's result)
    assert (code, result["status"], result["error"]["code"]) == (5, "failed", "LOCAL_IO_FAILED"), result
    assert "--slug is invalid" in result["error"]["message"] and result["effects"] == []
    assert world.writes() == [] and world.changesets() == []
    assert not (owner / "artifacts").exists() and not (root / "spec-dock/artifacts").exists()
    assert (tree_digest(root), tree_digest(world.catalog.resolve())) == before

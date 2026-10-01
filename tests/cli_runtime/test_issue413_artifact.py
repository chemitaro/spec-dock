"""Ordinary Artifact operations preserve evidence without common control."""

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
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_dependency import dependency_workspace
from tests.cli_runtime.test_issue413_finish import github_fixture


def artifact_workspace(tmp_path: Path) -> tuple[Path, Path]:
    root, _parent, child = dependency_workspace(tmp_path)
    assets = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock"
    shutil.copytree(assets / "templates/artifacts", root / "spec-dock/templates/artifacts")
    return root, child.parent


@pytest.mark.parametrize("kind", ["blank", "research", "interview", "disc", "decision-candidate", "adr"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_root_create_supports_all_templates_and_preview_without_unrelated_scope_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], kind: str, dry_run: bool
) -> None:
    root, owner = artifact_workspace(tmp_path)
    (owner / ".meta.json").write_bytes(b"unrelated invalid metadata")
    flags = ["--dry-run"] if dry_run else []
    assert (
        main([
            "--project",
            str(root),
            "artifact",
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
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
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
        assert main(["--project", str(root), "artifact", "list", "--scope", "@root", "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["data"]["result"]["items"] == [artifact]
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_root_create_renders_legacy_scope_placeholders_without_inventing_a_scope_or_github_issue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _owner = artifact_workspace(tmp_path)
    (root / "spec-dock/templates/artifacts/research.md").write_text(
        "<SCOPE_ID>|<INIT_ID>|<INIT_TITLE>|<EPIC_ID>|<EPIC_TITLE>|<ISS_ID>|<ISS_TITLE>|"
        "<FEATURE_ID>|<FEATURE_NAME>|<GITHUB_ISSUE_NUMBER_OR_URL>|<ISSUE_NUMBER_OR_URL>\n<RESEARCH_TITLE>\n"
    )
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "@root",
            "--type",
            "research",
            "--title",
            "Root artifact",
            "--json",
        ])
        == 0
    )
    artifact = json.loads(capsys.readouterr().out)["data"]["result"]["artifact"]
    assert (root / artifact["path"]).read_text() == "root||||||||||\nRoot artifact\n"


@pytest.mark.parametrize("failure", ["missing", "denied", "io", "invalid"])
def test_import_source_errors_keep_the_public_exit_class_and_hide_the_source_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], failure: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
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
    assert main([
        "--project",
        str(root),
        "artifact",
        "import",
        "file",
        str(source),
        "--scope",
        "iss-00003",
        "--json",
    ]) == (4 if failure == "missing" else 3 if failure == "invalid" else 5)
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and str(source) not in output.out and "private source bytes" not in output.out
    assert "private-parent" not in output.out and "body hash count sentinel" not in output.out
    assert result["status"] == "failed" and result["effects"] == [] and not (owner / "artifacts").exists()
    if failure != "missing":
        assert source.read_bytes() == b"private source bytes"


@pytest.mark.parametrize("target", ["iss-00001", "iss-00999"])
def test_import_resolves_the_exact_owner_before_opening_the_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], target: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
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


@pytest.mark.parametrize("operation", ["create", "import"])
def test_artifact_shared_slot_exhaustion_preserves_all_evidence_without_a_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], operation: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-07-30T01:02:03+00:00")
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    timestamp = "20260730t010203z"
    (artifacts / f"{timestamp}-adr-existing.md").write_bytes(b"standard")
    for suffix in range(1, 100):
        name = f"{timestamp}-{suffix:02d}-existing.md" if suffix % 2 else f"{timestamp}-{suffix:02d}--existing.bin"
        (artifacts / name).write_bytes(str(suffix).encode())
    before = {path.name: path.read_bytes() for path in artifacts.iterdir()}
    metadata = (owner / ".meta.json").read_bytes()
    source = tmp_path / "private-source.bin"
    source.write_bytes(b"private source bytes")
    arguments = (
        ["create", "--type", "research", "--title", "Evidence", "--slug", "evidence"]
        if operation == "create"
        else ["import", "file", str(source)]
    )
    assert main(["--project", str(root), "artifact", *arguments, "--scope", "iss-00003", "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["status"] == "failed" and result["effects"] == []
    assert result["error"]["code"] == "LOCAL_IO_FAILED" and "Artifact timestamp suffix exhaustion" in output.out
    assert str(source) not in output.out and "private source bytes" not in output.out
    assert {path.name: path.read_bytes() for path in artifacts.iterdir()} == before
    assert (owner / ".meta.json").read_bytes() == metadata and source.read_bytes() == b"private source bytes"
    assert not (root / ".git/spec-dock").exists()


def test_root_artifact_catalog_reads_only_identity_without_control_or_body(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, _child = dependency_workspace(tmp_path)
    catalog = root / "spec-dock/artifacts"
    catalog.mkdir()
    document = catalog / "20261001t000000z--private.bin"
    document.write_bytes(b"private content must not appear in stdout")
    before = document.read_bytes()
    assert main(["--project", str(root), "artifact", "list", "--scope", "@root", "--json"]) == 0
    listed = json.loads(capsys.readouterr().out)
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, owner = artifact_workspace(tmp_path)
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
    before = tree_digest(root)
    native_open = os.open

    def refuse_evidence_body(path, flags, mode=0o777, **kwargs):
        if os.fsdecode(path).rsplit(os.sep, 1)[-1] in {row[0] for row in cases}:
            pytest.fail("Artifact list/show must not open evidence bodies")
        return native_open(path, flags, mode, **kwargs)

    with monkeypatch.context() as patched:
        patched.setattr(os, "open", refuse_evidence_body)
        assert main(["--project", str(root), "artifact", "list", "--scope", "iss-00003", "--json"]) == 0
        output = capsys.readouterr()
        result = json.loads(output.out)
        expected = [
            {
                "id": artifact_id,
                "scope_id": "iss-00003",
                "path": (catalog / name).relative_to(root).as_posix(),
                "type": kind,
            }
            for name, artifact_id, kind in cases
        ]
        assert result["data"]["result"]["items"] == expected and result["effects"] == []
        assert "private evidence body" not in output.out + output.err
        assert main(["--project", str(root), "artifact", "show", "001-note", "--scope", "iss-00003", "--json"]) == 0
        output = capsys.readouterr()
        assert json.loads(output.out)["data"]["result"]["artifact"] == expected[0]
        assert "private evidence body" not in output.out + output.err
    assert tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("scope", ["@root", "iss-00003"])
def test_duplicate_artifact_timestamp_slots_refuse_catalog_reads_without_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], scope: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, issue = artifact_workspace(tmp_path)
    owner = root / "spec-dock" if scope == "@root" else issue
    catalog = owner / "artifacts"
    catalog.mkdir()
    first = catalog / "20260925t000000z--first.bin"
    first.write_bytes(b"first evidence")
    (catalog / "20260925t000000z--second.bin").write_bytes(b"second evidence")
    before = tree_digest(root)
    for command in (["list"], ["show", first.name]):
        assert main(["--project", str(root), "artifact", *command, "--scope", scope, "--json"]) == 3
        result = json.loads(capsys.readouterr().out)
        assert result["error"]["message"] == "ARTIFACT_CATALOG_INVALID" and result["effects"] == []
    assert tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_create_artifact_preserves_six_type_template_and_existing_scope_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    metadata = owner / ".meta.json"
    before = metadata.read_bytes()
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "調査資料",
            "--slug",
            "evidence",
            "--offline",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    artifact = result["data"]["result"]["artifact"]
    path = root / artifact["path"]
    assert artifact["scope_id"] == "iss-00003" and artifact["type"] == "research"
    assert path.parent == owner / "artifacts" and path.name.endswith("-research-evidence.md")
    assert (
        artifact["id"] in path.read_text()
        and "調査資料" in path.read_text()
        and '親: ["iss-00003"]' in path.read_text()
    )
    assert result["data"]["result"]["changed"] is True
    assert result["effects"] == [
        {"kind": "artifact", "status": "succeeded", "target": path.relative_to(root).as_posix()}
    ]
    assert metadata.read_bytes() == before and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("kind", ["blank", "research", "interview", "disc", "decision-candidate", "adr"])
def test_existing_local_initiative_accepts_all_artifact_types_and_preserves_metadata_and_documents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    root, _issue = artifact_workspace(tmp_path)
    owner = root / "spec-dock/initiatives/init-00001-fixture"
    metadata = owner / ".meta.json"
    payload = json.loads(metadata.read_bytes())
    payload.update(
        backend="local",
        github=None,
        lifecycle={"state": "open", "revision": 7, "updated_at": "2026-09-29T00:00:00Z"},
        optional={"private": "existing local metadata must survive"},
    )
    metadata.write_text(json.dumps(payload))
    metadata.chmod(0o640)
    document = owner / "requirement.md"
    document.write_bytes(b"existing local specification\n")
    before = {path: path.read_bytes() for path in (*root.glob("spec-dock/**/.meta.json"), document)}
    refs_before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "init-00001",
            "--type",
            kind,
            "--title",
            "Existing local evidence",
            "--slug",
            "evidence",
            "--expect-backend",
            "local",
            "--offline",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr()
    artifact = json.loads(output.out)["data"]["result"]["artifact"]
    destination = root / artifact["path"]
    assert destination.parent == owner / "artifacts"
    assert artifact["scope_id"] == "init-00001" and artifact["type"] == (
        "untyped-markdown" if kind == "blank" else kind
    )
    assert set(artifact) == {"id", "scope_id", "path", "type"}
    assert main(["--project", str(root), "artifact", "show", artifact["id"], "--scope", "init-00001", "--json"]) == 0
    shown = capsys.readouterr()
    assert json.loads(shown.out)["data"]["result"]["artifact"] == artifact
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert metadata.stat().st_mode & 0o777 == 0o640
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == refs_before
    assert not log.exists() and "existing local metadata must survive" not in output.out + shown.out
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_import_one_opaque_file_to_root_preserves_bytes_name_source_and_privacy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _owner = artifact_workspace(tmp_path)
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
    monkeypatch.setenv("USER", "Fixture author")
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-10-01T00:00:00+00:00")
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    existing = artifacts / "20261001t000000z--evidence.bin"
    existing.write_bytes(b"existing evidence")
    prefix = [
        "--project",
        str(root),
        "artifact",
        "create",
        "--scope",
        "iss-00003",
        "--type",
        kind,
        "--title",
        "資料",
        "--slug",
        "proof",
        "--json",
    ]
    assert main(prefix) == 0
    result = json.loads(capsys.readouterr().out)
    artifact = result["data"]["result"]["artifact"]
    path = root / artifact["path"]
    assert path.name.startswith("20261001t000000z-01-") and artifact["id"] in path.read_text()
    assert "<SCOPE_ID>" not in path.read_text() and "<YOUR_NAME>" not in path.read_text()
    assert '作成者: "Fixture author"' in path.read_text()
    assert ('authority: "draft"' if kind == "adr" else f'template: "{kind}"') in path.read_text()
    assert existing.read_bytes() == b"existing evidence"
    assert not list(artifacts.glob(".publish-*")) and not (root / ".git/spec-dock").exists()


def test_parallel_different_slug_candidates_in_one_timestamp_slot_are_conflicts_without_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-10-01T00:00:00+00:00")
    artifacts = owner / "artifacts"
    artifacts.mkdir()
    real_open = os.open
    second: list[int] = []
    prefix = [
        "--project",
        str(root),
        "artifact",
        "create",
        "--scope",
        "iss-00003",
        "--type",
        "research",
        "--title",
        "資料",
    ]

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
    tmp_path: Path, capsys: pytest.CaptureFixture[str], operation: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"opaque evidence")
    command = (
        ["create", "--type", "interview", "--title", "Interview", "--slug", "interview-evidence"]
        if operation == "create"
        else ["import", "file", str(source)]
    )
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    assert main(["--project", str(root), "artifact", *command, "--scope", "iss-00003", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert (
        result["status"] == "planned"
        and data["can_apply"] is True
        and data["blockers"] == []
        and data["changed"] is False
    )
    assert data["artifact"]["scope_id"] == "iss-00003" and result["effects"][0]["status"] == "planned"
    assert not (owner / "artifacts").exists() and source.read_bytes() == b"opaque evidence"
    assert not (root / "spec-dock/.agent").exists() and all(
        path.read_bytes() == exact for path, exact in before.items()
    )


@pytest.mark.skipif(os.name != "posix", reason="native executable Git diagnostics")
def test_artifact_post_publication_git_failure_retains_confirmed_file_and_original_diagnostic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-10-01T00:00:00+00:00")
    destination = owner / "artifacts/20261001t000000z-research-evidence.md"
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
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "evidence",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert destination.exists() and result["status"] == "partial"
    assert result["data"]["result"]["changed"] is True
    assert result["effects"] == [
        {"kind": "artifact", "status": "succeeded", "target": destination.relative_to(root).as_posix()}
    ]
    assert result["error"]["code"] == "GIT_FAILED" and result["error"]["details"]["git"]["stderr"] == diagnostic
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert result["recovery"]["can_rollback"] is False and result["recovery"]["can_resume"] is False


def test_replaced_stage_is_preserved_and_is_never_published_as_the_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-10-01T00:00:00+00:00")
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
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "evidence",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert changed and result["effects"] == []
    assert stage.read_bytes() == b"actor stage that must never become the Artifact"
    assert not (artifacts / "20261001t000000z-research-evidence.md").exists()


@pytest.mark.parametrize("replacement", ["owner", "artifacts"])
def test_artifact_publication_refuses_a_replaced_directory_and_preserves_actor_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], replacement: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
    monkeypatch.setattr("spec_dock.runtime.infra.clock.now_iso", lambda: "2026-10-01T00:00:00+00:00")
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
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "evidence",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert changed and result["effects"] == [] and result["data"]["result"]["artifact"] is None
    assert (directory / "actor-only.bin").read_bytes() == b"replacement actor bytes"
    held_artifacts = held / "artifacts" if replacement == "owner" else held
    for name, payload in preserved.items():
        assert (artifacts / name).read_bytes() == payload and (held_artifacts / name).read_bytes() == payload
    assert not list(artifacts.glob("*research-evidence.md")) and not list(held_artifacts.glob("*research-evidence.md"))
    assert not list(artifacts.glob(".publish-*")) and not list(held_artifacts.glob(".publish-*"))
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("operation", ["create", "import"])
def test_artifact_dynamic_owner_and_guard_capture_one_direct_selection_without_changing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], operation: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    source = tmp_path / "evidence.bin"
    source.write_bytes(b"evidence")
    command = (
        ["create", "--type", "interview", "--title", "Interview", "--slug", "evidence"]
        if operation == "create"
        else ["import", "file", str(source)]
    )
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            *command,
            "--scope",
            "@epic",
            "--expect-current",
            "iss-00003",
            "--expect-backend",
            "github",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["artifact"]["scope_id"] == "epic-00002" and record.read_bytes() == before
    assert not (owner / "artifacts").exists()


@pytest.mark.parametrize("source_kind", ["symlink", "hardlink", "directory", "fifo"])
def test_import_rejects_non_single_regular_sources_without_writes_or_source_disclosure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], source_kind: str
) -> None:
    root, owner = artifact_workspace(tmp_path)
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
    assert (
        main(["--project", str(root), "artifact", "import", "file", str(source), "--scope", "iss-00003", "--json"]) == 3
    )
    output = capsys.readouterr().out
    assert str(source) not in output and "private evidence" not in output and json.loads(output)["effects"] == []
    assert not (owner / "artifacts").exists() and real.read_bytes() == b"private evidence"


@pytest.mark.parametrize("dry_run", [False, True])
def test_redirected_artifact_directory_is_refused_without_external_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, owner = artifact_workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "marker.bin"
    marker.write_bytes(b"preserve")
    (owner / "artifacts").symlink_to(outside, target_is_directory=True)
    options = ["--dry-run"] if dry_run else []
    assert main([
        "--project",
        str(root),
        "artifact",
        "create",
        "--scope",
        "iss-00003",
        "--type",
        "research",
        "--title",
        "Evidence",
        "--slug",
        "proof",
        *options,
        "--json",
    ]) in (3, 5)
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and list(outside.iterdir()) == [marker] and marker.read_bytes() == b"preserve"


def test_unknown_link_outcome_preserves_artifact_and_candidate_without_automatic_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    (owner / "artifacts").mkdir()
    real_link = os.link
    attempted: list[str] = []

    def link(source, destination, **kwargs):
        attempted.append(destination)
        real_link(source, destination, **kwargs)
        raise OSError("fixture: publication reply unavailable")

    monkeypatch.setattr(os, "link", link)
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "evidence",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert len(attempted) == 1 and result["effects"][0]["status"] == "unknown"
    assert result["data"]["result"] == {"artifact": None, "changed": False}
    files = list((owner / "artifacts").iterdir())
    assert len(files) == 2 and files[0].read_bytes() == files[1].read_bytes()
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_confirmed_artifact_survives_descriptor_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
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
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "evidence",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert failed and result["data"]["result"]["changed"] is True
    assert result["effects"][0]["status"] == "succeeded" and list((owner / "artifacts").glob("*research-evidence.md"))


@pytest.mark.skipif(os.name != "posix", reason="native POSIX common-directory exclusion")
def test_artifact_creation_does_not_wait_on_another_process_start_lock(tmp_path: Path) -> None:
    import fcntl

    root, owner = artifact_workspace(tmp_path)
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
                "iss-00003",
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
            timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == "" and json.loads(result.stdout)["data"]["result"]["changed"] is True
        assert list((owner / "artifacts").glob("*research-evidence.md")) and not (root / ".git/spec-dock").exists()
    finally:
        os.close(descriptor)


def test_root_artifact_import_and_catalog_do_not_require_unrelated_scope_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    (owner / ".meta.json").write_bytes(b"{invalid unrelated metadata}")
    source = tmp_path / "evidence.bin"
    source.write_bytes(b"evidence")
    assert main(["--project", str(root), "artifact", "import", "file", str(source), "--scope", "@root", "--json"]) == 0
    created = json.loads(capsys.readouterr().out)["data"]["result"]["artifact"]
    assert main(["--project", str(root), "artifact", "list", "--scope", "@root", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["items"] == [created]


def test_custom_artifact_template_keeps_existing_scope_and_github_replacement_tokens(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _owner = artifact_workspace(tmp_path)
    template = root / "spec-dock/templates/artifacts/research.md"
    template.write_text(
        "<ARTIFACT_ID> <ARTIFACT_TITLE> <ISS_ID> <ISS_TITLE> <FEATURE_ID> <FEATURE_NAME> <EPIC_ID> <INIT_ID> <ISSUE_NUMBER_OR_URL> <GITHUB_ISSUE_NUMBER_OR_URL>\n"
    )
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "proof",
            "--json",
        ])
        == 0
    )
    artifact = json.loads(capsys.readouterr().out)["data"]["result"]["artifact"]
    text = (root / artifact["path"]).read_text()
    assert text == f"{artifact['id']} Evidence iss-00003 Fixture iss-00003 Fixture epic-00002 init-00001 #3 #3\n"


def test_uncertain_artifact_directory_creation_reports_partial_and_preserves_it_without_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
    original = (owner / ".meta.json").read_bytes()
    real_mkdir = os.mkdir
    attempted = False

    def mkdir(path, mode=0o777, **kwargs):
        nonlocal attempted
        real_mkdir(path, mode, **kwargs)
        if path == "artifacts" and not attempted:
            attempted = True
            raise OSError("fixture: directory creation reply unavailable")

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--slug",
            "proof",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert attempted and (owner / "artifacts").is_dir() and list((owner / "artifacts").iterdir()) == []
    assert result["effects"][0] == {
        "kind": "artifact.directory",
        "status": "unknown",
        "target": (owner / "artifacts").relative_to(root).as_posix(),
    }
    assert result["effects"][1]["status"] == "not_attempted" and (owner / ".meta.json").read_bytes() == original


def test_artifact_catalog_never_discloses_a_directory_swapped_to_an_external_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, owner = artifact_workspace(tmp_path)
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
    assert main(["--project", str(root), "artifact", "list", "--scope", "iss-00003", "--json"]) == 3
    output = capsys.readouterr().out
    assert "private-name.bin" not in output and "private external evidence" not in output
    assert json.loads(output)["effects"] == [] and secret.read_bytes() == b"private external evidence"


def test_artifact_help_describes_v2_file_publication_and_rejects_retired_recovery_before_context(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["artifact", "create", "--help"]) == 0
    help_text = capsys.readouterr().out
    assert "artifact:{id,scope_id,path,type}" in help_text and "shared counter" in help_text
    assert "specdock.cli/v2" in help_text and "journal" not in help_text
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "artifact",
            "create",
            "--scope",
            "iss-00003",
            "--type",
            "research",
            "--title",
            "Evidence",
            "--resume",
            "old-operation",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == [] and list(tmp_path.iterdir()) == []

import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.infra import issue_planning_oracle_artifact as artifact_reader  # noqa: E402


def test_artifact_reader_registry_is_exact_version_bound() -> None:
    reader = artifact_reader.artifact_reader_for_version("0.16.1")
    assert reader.version == "0.16.1"
    assert reader.read_session_status is artifact_reader.read_session_status
    assert reader.snapshot_authoring_zip is artifact_reader.snapshot_authoring_zip
    assert reader.snapshot_review_json is artifact_reader.snapshot_review_json
    assert reader.has_exact_repository_access_failure is artifact_reader.has_exact_repository_access_failure
    assert reader.review_output_characterized is True

    reader_0170 = artifact_reader.artifact_reader_for_version("0.17.0")
    assert reader_0170.version == "0.17.0"
    assert reader_0170.read_session_status is artifact_reader.read_session_status_0170
    assert reader_0170.snapshot_authoring_zip is artifact_reader.snapshot_authoring_zip_0170
    assert reader_0170.snapshot_review_json is artifact_reader.snapshot_review_json_0170
    assert reader_0170.has_exact_repository_access_failure is artifact_reader.has_exact_repository_access_failure_0170
    assert reader_0170.review_output_characterized is False

    for version in ("0.16.0", "0.16.2", "0.17.1", "0.18.0"):
        with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
            artifact_reader.artifact_reader_for_version(version)


def test_0170_reader_accepts_core_schema_and_ignores_transfer_origin(tmp_path: Path) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "oracle-017-attachment-characterization.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(
            "oracle-017-attachment-characterization/payload.txt",
            "attachment-characterization-ok\n",
        )
    entry = _artifact("file", zip_path)
    entry["transfer"] = {"status": "not-needed", "path": "/outside.zip"}
    entry["origin"] = {"mode": "local", "sha256": "0" * 64}
    _write_metadata(session, [entry])

    reader = artifact_reader.artifact_reader_for_version("0.17.0")
    snapshot = reader.snapshot_authoring_zip(
        session,
        session_id=session.name,
        oracle_version="0.17.0",
        staging_dir=tmp_path / "staging",
    )
    assert snapshot.observed_transport_filename == "oracle-017-attachment-characterization.zip"
    assert snapshot.size_bytes == zip_path.stat().st_size
    assert snapshot.sha256 == hashlib.sha256(zip_path.read_bytes()).hexdigest()


@pytest.mark.parametrize("unknown_first", [False, True])
@pytest.mark.parametrize("kind", ["transcript", "repository-failure", "missing"])
def test_0170_authoring_zip_rejects_mixed_uncharacterized_inventory(
    monkeypatch,
    tmp_path: Path,
    unknown_first: bool,
    kind: str,
) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "oracle-017-attachment-characterization.zip"
    _write_zip(zip_path)
    unknown_path = session / "artifacts" / "uncharacterized.md"
    unknown_path.write_bytes(b"uncharacterized\n")
    unknown_entry = _artifact(kind if kind != "missing" else "file", unknown_path)
    if kind == "missing":
        unknown_entry.pop("kind")
    zip_entry = _artifact("file", zip_path)
    entries = [unknown_entry, zip_entry] if unknown_first else [zip_entry, unknown_entry]
    _write_metadata(session, entries)

    delegated: list[object] = []
    original = artifact_reader._snapshot_authoring_zip_from_metadata

    def spy(*args, **kwargs):
        delegated.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(artifact_reader, "_snapshot_authoring_zip_from_metadata", spy)
    staging_dir = tmp_path / "staging"
    reader = artifact_reader.artifact_reader_for_version("0.17.0")

    with pytest.raises(artifact_reader.OracleArtifactError) as error:
        reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.17.0",
            staging_dir=staging_dir,
        )

    assert error.value.code == "oracle_artifact_rejected"
    assert delegated == []
    assert not staging_dir.exists()


@pytest.mark.parametrize("defect", ["path", "sizeBytes", "sha256", "validation"])
def test_0170_extra_fields_cannot_override_core_defect(tmp_path: Path, defect: str) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "oracle-017-attachment-characterization.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(
            "oracle-017-attachment-characterization/payload.txt",
            "attachment-characterization-ok\n",
        )
    entry = _artifact("file", zip_path)
    core_value = entry[defect]
    if defect == "path":
        entry[defect] = str(session / "outside.zip")
    elif defect == "sizeBytes":
        assert isinstance(core_value, int)
        entry[defect] = core_value + 1
    elif defect == "sha256":
        entry[defect] = "0" * 64
    else:
        entry[defect] = {"type": "zip", "ok": False}
    entry["transfer"] = {
        "path": str(zip_path),
        "sizeBytes": zip_path.stat().st_size,
        "sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        "validation": {"type": "zip", "ok": True},
    }
    entry["origin"] = dict(entry["transfer"])
    _write_metadata(session, [entry])

    reader = artifact_reader.artifact_reader_for_version("0.17.0")
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.17.0",
            staging_dir=tmp_path / "staging",
        )


def test_version_bound_readers_reject_cross_version_calls(tmp_path: Path) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    _write_metadata(session, [_artifact("file", zip_path)])

    reader_0161 = artifact_reader.artifact_reader_for_version("0.16.1")
    reader_0170 = artifact_reader.artifact_reader_for_version("0.17.0")
    for reader, version in ((reader_0161, "0.17.0"), (reader_0170, "0.16.1")):
        with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
            reader.snapshot_authoring_zip(
                session,
                session_id=session.name,
                oracle_version=version,
                staging_dir=tmp_path / f"staging-{version}",
            )


@pytest.mark.parametrize("status", [None, 123, "", "running"])
def test_0170_reader_rejects_invalid_status(tmp_path: Path, status: object) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    _write_metadata(session, [_artifact("file", zip_path)])
    metadata_path = session / "meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = status
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    reader = artifact_reader.artifact_reader_for_version("0.17.0")
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.17.0",
            staging_dir=tmp_path / "staging",
        )


def test_0170_reader_rejects_uncharacterized_0161_review_transcript(tmp_path: Path) -> None:
    session = _session(tmp_path)
    transcript = session / "artifacts" / "transcript.md"
    transcript.write_bytes(b"# Transcript\n## Answer\n{\"verdict\":\"pass\"}\n")
    _write_metadata(session, [_artifact("transcript", transcript)])

    reader = artifact_reader.artifact_reader_for_version("0.17.0")
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        reader.snapshot_review_json(
            session,
            session_id=session.name,
            oracle_version="0.17.0",
            staging_dir=tmp_path / "staging",
        )


def test_0170_reader_rejects_uncharacterized_0161_repository_sentinel(tmp_path: Path) -> None:
    session = _session(tmp_path)
    transcript = session / "artifacts" / "transcript.md"
    transcript.write_bytes(b"# Transcript\n## Answer\nrepository access failed\n")
    _write_metadata(session, [_artifact("transcript", transcript)])

    reader = artifact_reader.artifact_reader_for_version("0.17.0")
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        reader.has_exact_repository_access_failure(
            session,
            session_id=session.name,
            oracle_version="0.17.0",
            staging_dir=tmp_path / "staging",
        )


@pytest.mark.parametrize("kind", ["transcript", "repository-failure", "missing"])
def test_0170_reader_rejects_uncharacterized_artifact_kind(tmp_path: Path, kind: str) -> None:
    session = _session(tmp_path)
    artifact_path = session / "artifacts" / "unknown.bin"
    artifact_path.write_bytes(b"uncharacterized\n")
    entry = _artifact("file", artifact_path)
    if kind == "transcript":
        entry = _artifact("transcript", artifact_path)
    elif kind == "repository-failure":
        entry["kind"] = "repository-failure"
    else:
        entry.pop("kind")
    _write_metadata(session, [entry])

    reader = artifact_reader.artifact_reader_for_version("0.17.0")
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        reader.has_exact_repository_access_failure(
            session,
            session_id=session.name,
            oracle_version="0.17.0",
            staging_dir=tmp_path / "staging",
        )


def test_snapshots_exact_oracle_zip_and_review_json(tmp_path: Path) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "iss-00003-issue-planning-documents (2).zip"
    _write_zip(zip_path)
    _write_metadata(session, [_artifact("file", zip_path)])

    snapshot = artifact_reader.snapshot_authoring_zip(
        session,
        session_id=session.name,
        oracle_version="0.16.1",
        staging_dir=tmp_path / "staging-zip",
    )
    assert snapshot.expected_logical_filename == "iss-00003-issue-planning-documents.zip"
    assert snapshot.observed_transport_filename.endswith(" (2).zip")
    assert snapshot.internal_root == "iss-00003-issue-planning-documents"

    transcript = session / "artifacts" / "transcript.md"
    transcript.write_bytes(b'# Oracle Browser Transcript\n## Prompt\nprivate\n## Answer\n{"verdict":"pass"}\n')
    _write_metadata(session, [_artifact("transcript", transcript)])
    review = artifact_reader.snapshot_review_json(
        session,
        session_id=session.name,
        oracle_version="0.16.1",
        staging_dir=tmp_path / "staging-json",
    )
    assert review.json_bytes == b'{"verdict":"pass"}'
    assert "private" not in repr(review)


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        (b"repository access failed", True),
        (b"repository access failed: using main instead", False),
        (b"prefix repository access failed", False),
    ],
)
def test_exact_repository_access_failure_detection(
    tmp_path: Path,
    answer: bytes,
    expected: bool,
) -> None:
    session = _session(tmp_path)
    transcript = session / "artifacts" / "transcript.md"
    transcript.write_bytes(b"# Oracle Browser Transcript\n## Prompt\nprivate\n## Answer\n" + answer + b"\n")
    _write_metadata(session, [_artifact("transcript", transcript)])

    assert (
        artifact_reader.has_exact_repository_access_failure(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )
        is expected
    )


def test_repository_access_failure_with_zip_is_contradictory(tmp_path: Path) -> None:
    session = _session(tmp_path)
    transcript = session / "artifacts" / "transcript.md"
    transcript.write_bytes(b"# Oracle Browser Transcript\n## Prompt\nprivate\n## Answer\nrepository access failed\n")
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    _write_metadata(
        session,
        [_artifact("transcript", transcript), _artifact("file", zip_path)],
    )

    with pytest.raises(
        artifact_reader.OracleArtifactError,
        match="oracle_artifact_rejected",
    ):
        artifact_reader.has_exact_repository_access_failure(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )


@pytest.mark.parametrize("count", [0, 2])
def test_zip_inventory_requires_exactly_one_match(tmp_path: Path, count: int) -> None:
    session = _session(tmp_path)
    artifacts = []
    for index in range(count):
        path = session / "artifacts" / f"candidate-{index}.zip"
        _write_zip(path)
        artifacts.append(_artifact("file", path))
    _write_metadata(session, artifacts)

    expected = "oracle_artifact_missing" if count == 0 else "oracle_artifact_ambiguous"
    with pytest.raises(artifact_reader.OracleArtifactError, match=expected):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )


@pytest.mark.parametrize(
    "failure",
    ["wrong-session", "unsupported-version", "unsupported-mode", "size", "sha"],
)
def test_metadata_identity_and_integrity_fail_closed(tmp_path: Path, failure: str) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    entry = _artifact("file", zip_path)
    if failure == "size":
        size_bytes = entry["sizeBytes"]
        assert isinstance(size_bytes, int)
        entry["sizeBytes"] = size_bytes + 1
    elif failure == "sha":
        entry["sha256"] = "0" * 64
    _write_metadata(session, [entry])
    if failure == "unsupported-mode":
        metadata_path = session / "meta.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["mode"] = "api"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    session_id = "other-session" if failure == "wrong-session" else session.name
    version = "0.16.2" if failure == "unsupported-version" else "0.16.1"
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session_id,
            oracle_version=version,
            staging_dir=tmp_path / "staging",
        )


def test_metadata_oversized_integer_is_rejected_at_json_boundary(tmp_path: Path) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    entry = _artifact("file", zip_path)
    metadata = (
        '{"id":'
        + json.dumps(session.name)
        + ',"status":"completed","mode":"browser","oversized":'
        + ("9" * 5000)
        + ',"artifacts":'
        + json.dumps([entry], separators=(",", ":"))
        + "}"
    )
    (session / "meta.json").write_text(metadata, encoding="utf-8")

    with pytest.raises(artifact_reader.OracleArtifactError) as error:
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )

    assert error.value.code == "oracle_artifact_rejected"


@pytest.mark.parametrize("failure", ["source-mutation", "staging-rehash"])
def test_snapshot_rejects_mutation_or_staging_rehash(
    monkeypatch,
    tmp_path: Path,
    failure: str,
) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    _write_metadata(session, [_artifact("file", zip_path)])

    if failure == "source-mutation":
        original_read_fd = artifact_reader._read_fd_bounded

        def mutate_after_read(descriptor: int, limit: int) -> bytes:
            payload = original_read_fd(descriptor, limit)
            if limit == artifact_reader.MAX_ARTIFACT_BYTES:
                current = zip_path.stat().st_mtime_ns
                os.utime(zip_path, ns=(current + 1, current + 1))
            return payload

        monkeypatch.setattr(artifact_reader, "_read_fd_bounded", mutate_after_read)
    else:
        original_read_file = artifact_reader._read_bounded_regular_file

        def corrupt_staging(path: Path, limit: int) -> bytes:
            payload = original_read_file(path, limit)
            return b"corrupt" if path.name == "oracle-artifact.snapshot" else payload

        monkeypatch.setattr(artifact_reader, "_read_bounded_regular_file", corrupt_staging)

    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )


def test_descriptor_rooted_open_rejects_artifact_parent_swap(
    monkeypatch,
    tmp_path: Path,
) -> None:
    session = _session(tmp_path)
    safe = session / "artifacts" / "candidate.zip"
    _write_zip(safe)
    safe_bytes = safe.read_bytes()
    _write_metadata(session, [_artifact("file", safe)])
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_file = outside / "candidate.zip"
    outside_file.write_bytes(safe_bytes)
    original = session / "artifacts-original"
    swapped = False

    def swap_parent(_parent_fd: int, leaf_name: str) -> None:
        nonlocal swapped
        if leaf_name != "candidate.zip" or swapped:
            return
        (session / "artifacts").rename(original)
        (session / "artifacts").symlink_to(outside, target_is_directory=True)
        swapped = True

    monkeypatch.setattr(artifact_reader, "_before_leaf_open", swap_parent, raising=False)
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected") as error:
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )
    assert swapped is True
    assert str(outside) not in str(error.value)
    assert safe_bytes not in repr(error.value).encode()


def test_descriptor_rooted_open_rejects_session_root_swap_for_metadata(
    monkeypatch,
    tmp_path: Path,
) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    _write_metadata(session, [_artifact("file", zip_path)])
    replacement = tmp_path / "replacement-session"
    replacement.mkdir()
    (replacement / "meta.json").write_bytes((session / "meta.json").read_bytes())
    original = session.with_name(f"{session.name}-original")
    swapped = False

    def swap_root(_parent_fd: int, leaf_name: str) -> None:
        nonlocal swapped
        if leaf_name != "meta.json" or swapped:
            return
        session.rename(original)
        session.symlink_to(replacement, target_is_directory=True)
        swapped = True

    monkeypatch.setattr(artifact_reader, "_before_leaf_open", swap_root)
    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )
    assert swapped is True


def test_descriptor_rooted_open_fails_closed_without_openat_support(
    monkeypatch,
    tmp_path: Path,
) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    _write_zip(zip_path)
    _write_metadata(session, [_artifact("file", zip_path)])
    monkeypatch.setattr(artifact_reader.os, "supports_dir_fd", frozenset())

    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )


@pytest.mark.parametrize(
    "overflow",
    ["entry-count", "entry-size", "total-size", "compression-ratio"],
)
def test_zip_central_directory_bounds_reject_before_entry_read(
    monkeypatch,
    tmp_path: Path,
    overflow: str,
) -> None:
    session = _session(tmp_path)
    zip_path = session / "artifacts" / "candidate.zip"
    compression = zipfile.ZIP_DEFLATED if overflow == "compression-ratio" else zipfile.ZIP_STORED
    with zipfile.ZipFile(zip_path, "w", compression=compression) as archive:
        if overflow == "entry-count":
            for index in range(2049):
                archive.writestr(f"candidate/{index}.md", "")
        elif overflow == "entry-size":
            archive.writestr("candidate/large.md", b"")
        else:
            if overflow == "total-size":
                for index in range(5):
                    archive.writestr(f"candidate/{index}.md", b"")
            else:
                archive.writestr("candidate/high-ratio.md", b"x" * 1024 * 1024)
    if overflow == "entry-size":
        _patch_central_sizes(zip_path, [16 * 1024 * 1024 + 1])
    elif overflow == "total-size":
        _patch_central_sizes(zip_path, [16 * 1024 * 1024] * 5)
    _write_metadata(session, [_artifact("file", zip_path)])
    monkeypatch.setattr(
        zipfile.ZipFile,
        "testzip",
        lambda *_args, **_kwargs: pytest.fail("testzip must not run"),
    )
    monkeypatch.setattr(
        zipfile.ZipExtFile,
        "read",
        lambda *_args, **_kwargs: pytest.fail("entry bytes must not be read"),
    )

    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )


def _patch_central_sizes(path: Path, sizes: list[int]) -> None:
    payload = bytearray(path.read_bytes())
    positions: list[int] = []
    start = 0
    while True:
        position = payload.find(b"PK\x01\x02", start)
        if position < 0:
            break
        positions.append(position)
        start = position + 4
    assert len(positions) == len(sizes)
    for position, size in zip(positions, sizes, strict=True):
        payload[position + 20 : position + 24] = size.to_bytes(4, "little")
        payload[position + 24 : position + 28] = size.to_bytes(4, "little")
    path.write_bytes(payload)


@pytest.mark.parametrize(
    "unsafe_kind",
    ["outside", "relative-escape", "parent-symlink", "file-symlink", "directory", "fifo"],
)
def test_artifact_path_must_be_contained_regular_and_symlink_free(
    tmp_path: Path,
    unsafe_kind: str,
) -> None:
    session = _session(tmp_path)
    safe = session / "artifacts" / "candidate.zip"
    _write_zip(safe)
    target = safe
    if unsafe_kind == "outside":
        target = tmp_path / "outside.zip"
        _write_zip(target)
    elif unsafe_kind == "relative-escape":
        target = Path("../outside.zip")
        _write_zip(session.parent / "outside.zip")
    elif unsafe_kind == "parent-symlink":
        real = session / "real"
        real.mkdir()
        target = real / "candidate.zip"
        _write_zip(target)
        alias = session / "alias"
        alias.symlink_to(real, target_is_directory=True)
        target = alias / "candidate.zip"
    elif unsafe_kind == "file-symlink":
        real = session / "artifacts" / "real.zip"
        _write_zip(real)
        safe.unlink()
        safe.symlink_to(real)
    elif unsafe_kind == "directory":
        safe.unlink()
        safe.mkdir()
    elif unsafe_kind == "fifo":
        safe.unlink()
        os.mkfifo(safe)
    _write_metadata(
        session,
        [
            {
                "kind": "file",
                "path": str(target),
                "sizeBytes": 1,
                "sha256": "0" * 64,
                "validation": {"type": "zip", "ok": True},
            }
        ],
    )

    with pytest.raises(artifact_reader.OracleArtifactError, match="oracle_artifact_rejected"):
        artifact_reader.snapshot_authoring_zip(
            session,
            session_id=session.name,
            oracle_version="0.16.1",
            staging_dir=tmp_path / "staging",
        )


def _session(tmp_path: Path) -> Path:
    session = tmp_path / "oracle-home" / "sessions" / "specdock-issue-abc123"
    (session / "artifacts").mkdir(parents=True)
    return session


def _write_zip(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("iss-00003-issue-planning-documents/requirement.md", "body\n")


def _artifact(kind: str, path: Path) -> dict[str, object]:
    contents = path.read_bytes()
    return {
        "kind": kind,
        "path": str(path),
        "sizeBytes": len(contents),
        "sha256": hashlib.sha256(contents).hexdigest(),
        "validation": {"type": "zip" if kind == "file" else "generic", "ok": True},
    }


def _write_metadata(session: Path, artifacts: list[dict[str, object]]) -> None:
    (session / "meta.json").write_text(
        json.dumps({
            "id": session.name,
            "status": "completed",
            "mode": "browser",
            "artifacts": artifacts,
        }),
        encoding="utf-8",
    )

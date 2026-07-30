import os
from pathlib import Path
import sys

import pytest


def _artifacts_module():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import artifacts
    finally:
        sys.path.pop(0)
    return artifacts


def test_generic_parser_round_trips_without_changing_typed_blank_grammar() -> None:
    artifacts = _artifacts_module()
    standard = "20260730t010203z--Report FINAL.PDF"
    suffixed = "20260730t010203z-07--opaque.md"

    parsed_standard = artifacts.parse_generic_imported_artifact_filename(standard)
    parsed_suffixed = artifacts.parse_generic_imported_artifact_filename(suffixed)

    assert parsed_standard is not None
    assert parsed_standard.artifact_id == standard
    assert parsed_standard.suffix is None
    assert parsed_suffixed is not None
    assert parsed_suffixed.artifact_id == suffixed
    assert parsed_suffixed.suffix == 7
    assert artifacts.parse_artifact_filename(standard) is None
    assert artifacts.parse_artifact_filename(suffixed) is None
    assert artifacts.parse_artifact_filename("20260730t010203z-adr-decision.md").artifact_type == "adr"
    assert artifacts.parse_artifact_filename("20260730t010203z-notes.md").artifact_type == "blank"
    for malformed in (
        "20260730t010203z-00--bad.bin",
        "20260730t010203z-100--bad.bin",
        "20260730t010203z--",
        "20260730t010203z--.",
    ):
        assert artifacts.parse_generic_imported_artifact_filename(malformed) is None


@pytest.mark.parametrize(
    "basename",
    (
        "Report FINAL.PDF",
        "archive.tar.gz",
        "README",
        ".env",
        "結合\u0301-資料.txt",
        "絵文字-😀.ZIP",
        "Case.txt",
        "case.txt",
        r"posix\backslash.bin",
    ),
)
def test_safe_generic_basename_is_preserved_exactly(basename: str) -> None:
    artifacts = _artifacts_module()

    assert (
        artifacts.normalize_generic_artifact_basename(
            basename,
            name_max_bytes=255,
            max_prefix_bytes=len(b"20260730t010203z-99--"),
        )
        == basename
    )


def test_undecodable_generic_basename_is_rejected_as_domain_error() -> None:
    artifacts = _artifacts_module()
    undecodable = os.fsdecode(b"invalid-\xff.bin")

    with pytest.raises(RuntimeError, match="Invalid generic artifact basename"):
        artifacts.normalize_generic_artifact_basename(
            undecodable,
            name_max_bytes=255,
            max_prefix_bytes=len(b"20260730t010203z-99--"),
        )


def test_unsafe_and_overlong_basename_is_deterministic_utf8_and_name_max_safe() -> None:
    artifacts = _artifacts_module()
    timestamp = "20260730t010203z"
    prefix_bytes = len(f"{timestamp}-99--".encode())
    original = ("報告" * 80) + ".archive.tar.gz"

    first = artifacts.normalize_generic_artifact_basename(
        original,
        name_max_bytes=96,
        max_prefix_bytes=prefix_bytes,
    )
    second = artifacts.normalize_generic_artifact_basename(
        original,
        name_max_bytes=96,
        max_prefix_bytes=prefix_bytes,
    )
    filename = artifacts.format_generic_imported_artifact_filename(
        timestamp=timestamp,
        original_basename=original,
        suffix=99,
        name_max_bytes=96,
    )

    assert first == second
    assert first.endswith(".archive.tar.gz")
    assert len(filename.encode("utf-8")) <= 96
    first.encode("utf-8").decode("utf-8")
    assert (
        artifacts.normalize_generic_artifact_basename(
            "unsafe\x01name. ",
            name_max_bytes=255,
            max_prefix_bytes=prefix_bytes,
        )
        == "unsafe_name__"
    )


def test_overlong_basename_preserves_longest_extension_chain_that_fits_with_stem() -> None:
    artifacts = _artifacts_module()

    assert (
        artifacts.normalize_generic_artifact_basename(
            "stem.long.mid.gz",
            name_max_bytes=12,
            max_prefix_bytes=0,
        )
        == "stem.mid.gz"
    )


def test_shared_slot_ledger_scans_direct_child_names_across_all_families(tmp_path) -> None:
    artifacts = _artifacts_module()
    timestamp = "20260730t010203z"
    (tmp_path / f"{timestamp}-adr-decision.md").write_text("typed body", encoding="utf-8")
    (tmp_path / f"{timestamp}-01-notes.md").write_text("blank body", encoding="utf-8")
    (tmp_path / f"{timestamp}-02--opaque.bin").write_bytes(b"\xff")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / f"{timestamp}-03--ignored.bin").write_bytes(b"nested")

    error, ledger = artifacts.scan_artifact_slot_ledger(tmp_path)
    destination, artifact_id = artifacts.allocate_generic_imported_artifact_filename_for_timestamp(
        tmp_path,
        timestamp=timestamp,
        original_basename="Report FINAL.PDF",
        name_max_bytes=255,
    )

    assert error is None
    assert ledger.used_slots == frozenset({
        artifacts.ArtifactSlot(timestamp, None),
        artifacts.ArtifactSlot(timestamp, 1),
        artifacts.ArtifactSlot(timestamp, 2),
    })
    assert destination.name == f"{timestamp}-03--Report FINAL.PDF"
    assert artifact_id == destination.name


def test_shared_slot_exhaustion_is_bounded_without_mutation(tmp_path) -> None:
    artifacts = _artifacts_module()
    timestamp = "20260730t010203z"
    standard = tmp_path / f"{timestamp}-adr-existing.md"
    standard.write_bytes(b"standard")
    for suffix in range(1, 100):
        if suffix % 2:
            name = f"{timestamp}-{suffix:02d}-existing.md"
        else:
            name = f"{timestamp}-{suffix:02d}--existing.bin"
        (tmp_path / name).write_bytes(str(suffix).encode())
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}

    with pytest.raises(RuntimeError, match="Artifact timestamp suffix exhaustion"):
        artifacts.allocate_generic_imported_artifact_filename_for_timestamp(
            tmp_path,
            timestamp=timestamp,
            original_basename="new.bin",
            name_max_bytes=255,
        )

    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before

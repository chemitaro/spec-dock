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


def test_current_creatable_artifact_catalog_is_exact() -> None:
    artifacts = _artifacts_module()
    current_types = (
        "blank",
        "research",
        "interview",
        "disc",
        "decision-candidate",
        "adr",
    )
    assert current_types == artifacts.CURRENT_CREATABLE_ARTIFACT_TYPES
    assert all(artifacts.can_create_artifact_type(value) for value in current_types)
    assert not any(
        artifacts.can_create_artifact_type(value)
        for value in (
            "analysis",
            "pr-repair-batch",
            "draft-requirement",
            "draft-design",
            "draft-plan",
            "scratch",
            "note",
            "unknown",
        )
    )


@pytest.mark.parametrize(
    ("filename", "expected_type"),
    (
        ("20260810t010101z-pr-repair-batch-review-fix.md", "pr-repair-batch"),
        ("20260810t010102z-draft-requirement-requirement.md", "draft-requirement"),
        ("20260810t010103z-draft-design-design.md", "draft-design"),
        ("20260810t010104z-draft-plan-plan.md", "draft-plan"),
        ("20260810t010105z-scratch-capture.md", "scratch"),
        ("20260810t010106z-note-handoff.md", "note"),
    ),
)
def test_existing_timestamp_typed_historical_catalog_is_recognized_without_becoming_creatable(
    tmp_path: Path,
    filename: str,
    expected_type: str,
) -> None:
    artifacts = _artifacts_module()
    path = tmp_path / filename

    parsed = artifacts.parse_existing_artifact_filename(filename)

    assert parsed is not None
    assert parsed.artifact_type == expected_type
    assert artifacts.parse_artifact_filename(filename) == parsed
    assert artifacts.is_malformed_artifact_candidate(path) is False
    assert artifacts.can_create_artifact_type(expected_type) is False


@pytest.mark.parametrize(
    ("filename", "expected_type"),
    (
        ("001-adr-token-rotation.md", "adr"),
        ("002-disc-api-options.md", "disc"),
        ("003-note-kickoff-memo.md", "note"),
    ),
)
def test_existing_sequential_historical_catalog_is_explicitly_recognized(
    tmp_path: Path,
    filename: str,
    expected_type: str,
) -> None:
    artifacts = _artifacts_module()
    path = tmp_path / filename

    parsed = artifacts.parse_existing_artifact_filename(filename)

    assert parsed is not None
    assert parsed.artifact_type == expected_type
    assert parsed.sequence == filename[:3]
    assert artifacts.is_malformed_artifact_candidate(path) is False


@pytest.mark.parametrize(
    "filename",
    (
        "20260810t010107z--Report FINAL.PDF",
        "20260810t010107z-07--opaque.md",
    ),
)
def test_existing_generic_import_catalog_is_recognized_as_opaque_identity(tmp_path: Path, filename: str) -> None:
    artifacts = _artifacts_module()

    parsed = artifacts.parse_existing_artifact_filename(filename)

    assert parsed is not None
    assert parsed.artifact_id == filename
    assert artifacts.is_malformed_artifact_candidate(tmp_path / filename) is False


@pytest.mark.parametrize(
    "filename",
    (
        "20260810T010101z-adr-upper-t.md",
        "20260810t010101Z-adr-upper-z.md",
        "20260810t010101-adr-missing-z.md",
        "20260810t010101z_analysis-bad-separator.md",
        "20260810t010101z-.md",
        "20260810t01010z-adr-short-time.md",
        "20261340t256199z-adr-impossible-time.md",
        "20260810t010101z-00-note-bad-slot.md",
        "20260810t010101z-100-note-bad-slot.md",
        "001-scratch-not-in-sequential-catalog.md",
    ),
)
def test_existing_catalog_rejects_timestamp_intent_and_sequential_controls(tmp_path: Path, filename: str) -> None:
    artifacts = _artifacts_module()

    assert artifacts.parse_existing_artifact_filename(filename) is None
    assert artifacts.is_malformed_artifact_candidate(tmp_path / filename) is True


@pytest.mark.parametrize(
    "filename",
    (
        "20260811t091549z-analysis-operational-state-eventstore-readmodel-boundary.md",
        "20260811t095606z-analysis-event-sourcing-synchronous-current-state-projection.md",
        "20260811t113200z-analysis-existing-projection-uow-reuse.md",
        "20260811t113201z-report-validation-result.md",
        "20260811t113202z-review-final-gate.md",
        "20260811t113203z-external-document.md",
    ),
)
def test_existing_timestamp_markdown_with_unknown_type_like_label_is_accepted_as_untyped(
    tmp_path: Path,
    filename: str,
) -> None:
    artifacts = _artifacts_module()

    parsed = artifacts.parse_existing_artifact_filename(filename)

    assert parsed is not None
    # Stored untyped Markdown retains the historical "blank" representation;
    # this does not make its leading label part of the creation type catalog.
    assert parsed.artifact_type == "blank"
    assert artifacts.is_malformed_artifact_candidate(tmp_path / filename) is False


def test_historical_tokens_are_not_misclassified_as_blank_slugs() -> None:
    artifacts = _artifacts_module()

    for historical_type in (
        "pr-repair-batch",
        "draft-requirement",
        "draft-design",
        "draft-plan",
        "scratch",
        "note",
    ):
        filename = f"20260810t010101z-{historical_type}-evidence.md"
        parsed = artifacts.parse_artifact_filename(filename)
        assert parsed is not None
        assert parsed.artifact_type == historical_type


def test_sequential_historical_duplicate_id_remains_actionable(tmp_path: Path) -> None:
    artifacts = _artifacts_module()
    (tmp_path / "001-adr-first.md").write_bytes(b"first")
    (tmp_path / "001-adr-second.md").write_bytes(b"second")

    error, ledger = artifacts.scan_artifact_slot_ledger(tmp_path)

    assert error is not None
    assert "Duplicate artifact id detected" in error
    assert "id=001-adr" in error
    assert ledger.used_slots == frozenset()
    assert ledger.artifact_ids == frozenset()


def test_out_of_band_non_markdown_attachment_is_distinct_from_generic_import_and_managed_malformed_candidate(
    tmp_path: Path,
) -> None:
    artifacts = _artifacts_module()
    attachment = "20260810t010101z-disc-export.html"
    generic = "20260810t010102z--export.html"
    untyped = "20260810t010103z-analysis-managed.md"

    assert artifacts.parse_existing_artifact_filename(attachment) is None
    assert artifacts.is_malformed_artifact_candidate(tmp_path / attachment) is False
    generic_parsed = artifacts.parse_existing_artifact_filename(generic)
    assert generic_parsed is not None
    assert generic_parsed.artifact_id == generic
    untyped_parsed = artifacts.parse_existing_artifact_filename(untyped)
    assert untyped_parsed is not None
    assert untyped_parsed.artifact_type == "blank"
    assert artifacts.is_malformed_artifact_candidate(tmp_path / untyped) is False


@pytest.mark.parametrize(
    "filename",
    (
        "20260230t120000z--capture.html",
        "20260810t010101z-00--capture.bin",
        "20260810t010101z-100--capture.json",
        "20260810t010101z--",
        "20260810t010101z--unsafe\nname.html",
        "20260810t010101z--unsafe\u200bname.html",
    ),
)
def test_invalid_generic_import_intent_is_malformed_independent_of_extension(
    tmp_path: Path,
    filename: str,
) -> None:
    artifacts = _artifacts_module()

    assert artifacts.parse_existing_artifact_filename(filename) is None
    assert artifacts.is_malformed_artifact_candidate(tmp_path / filename) is True


def test_generic_intent_does_not_expand_to_single_hyphen_non_markdown_or_directory(tmp_path: Path) -> None:
    artifacts = _artifacts_module()
    attachment = tmp_path / "20260810t010101z-disc-export.html"
    authoring_pack = tmp_path / "20260810t010102z-chatgpt-final-authoring-pack"
    authoring_pack.mkdir()

    assert artifacts.is_malformed_artifact_candidate(attachment) is False
    assert artifacts.is_malformed_artifact_candidate(authoring_pack) is False


def test_invalid_generic_import_intent_with_representable_path_separator_is_malformed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifacts = _artifacts_module()
    filename = r"20260810t010101z--unsafe\name.html"
    monkeypatch.setattr(artifacts.os, "sep", "\\")

    assert artifacts.parse_existing_artifact_filename(filename) is None
    assert artifacts.is_malformed_artifact_candidate(tmp_path / filename) is True


def test_generic_parser_rejects_surrogate_escaped_basename_as_malformed(tmp_path: Path) -> None:
    artifacts = _artifacts_module()
    filename = "20260810t010101z--invalid-\udcff.bin"
    valid_unicode = "20260810t010102z--絵文字-😀.ZIP"

    assert artifacts.parse_generic_imported_artifact_filename(filename) is None
    assert artifacts.parse_existing_artifact_filename(filename) is None
    assert artifacts.is_malformed_artifact_candidate(tmp_path / filename) is True
    assert artifacts.parse_generic_imported_artifact_filename(valid_unicode) is not None


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

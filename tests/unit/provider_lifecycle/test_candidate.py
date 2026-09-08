from __future__ import annotations

from pathlib import Path
import shutil
from typing import cast

import pytest

from spec_dock.provider_lifecycle.candidate import (
    CANDIDATE_VERSION,
    FIXED_DOMAINS,
    CandidateError,
    capture_packaged_candidate,
    marker_bytes,
    validate_staged_candidate,
)
from spec_dock.provider_lifecycle.contracts import InstallationRecord
from spec_dock.provider_lifecycle.legacy_fixture import LEGACY_SOURCE_COMMIT, load_legacy_fixture
from spec_dock.provider_lifecycle.wire import parse_installation_record, serialize_installation_record


def _copy_assets_to_stage(stage: Path) -> None:
    assets = Path(__file__).parents[3] / "src" / "spec_dock" / "assets"
    for index, (_kind, public_path, source_suffix) in enumerate(FIXED_DOMAINS):
        source = assets / source_suffix
        target = stage / (
            public_path.rsplit("/", 1)[-1]
            if index < 4
            else ("slot-spec-dock" if index == 4 else "slot-spec-dock-grill-with-docs")
        )
        shutil.copytree(source, target, symlinks=True)


def test_t02_candidate_record_marker_and_legacy_fixture_are_closed_and_deterministic() -> None:
    first = capture_packaged_candidate()
    second = capture_packaged_candidate()
    assert first == second
    assert [domain.path for domain in first.domains] == [domain[1] for domain in FIXED_DOMAINS]

    record = InstallationRecord(
        1,
        "incomplete",
        "install",
        CANDIDATE_VERSION,
        first.aggregate_digest,
        "create-if-absent",
        {"spec-dock": CANDIDATE_VERSION, "spec-dock-grill-with-docs": CANDIDATE_VERSION},
    )
    record_bytes = serialize_installation_record(record)
    assert parse_installation_record(record_bytes) == record
    assert record_bytes.count(b"\n") == 1

    marker = marker_bytes(first, FIXED_DOMAINS[4][1])
    assert marker.count(b"\n") == 1

    fixture = load_legacy_fixture()
    assert fixture["legacy_version"] == "0.2.3"
    assert fixture["source_commit"] == LEGACY_SOURCE_COMMIT
    domains = cast("list[dict[str, object]]", fixture["domains"])
    assert [domain["path"] for domain in domains] == [domain[1] for domain in FIXED_DOMAINS]
    assert isinstance(fixture["aggregate_digest"], str)


def test_t02_packaged_candidate_is_six_domains_in_fixed_order_and_is_repeatable() -> None:
    first = capture_packaged_candidate()
    second = capture_packaged_candidate()
    assert first == second
    assert first.schema_version == 1
    assert first.version == CANDIDATE_VERSION
    assert [domain.path for domain in first.domains] == [domain[1] for domain in FIXED_DOMAINS]
    assert all(domain.entry_count >= 0 for domain in first.domains)


def test_t02_stage_digest_and_markers_bind_to_the_candidate(tmp_path: Path) -> None:
    candidate = capture_packaged_candidate()
    stage = tmp_path / "stage"
    stage.mkdir()
    _copy_assets_to_stage(stage)
    for index, (_kind, public_path, _source) in enumerate(FIXED_DOMAINS[4:], start=4):
        name = "slot-spec-dock" if index == 4 else "slot-spec-dock-grill-with-docs"
        (stage / name / ".spec-dock-provider-slot.json").write_bytes(marker_bytes(candidate, public_path))
        (stage / name / ".spec-dock-provider-slot.json").chmod(0o644)
    assert validate_staged_candidate(stage, candidate)

    (stage / "docs" / "new.txt").write_text("foreign\n", encoding="utf-8")
    (stage / "docs" / "new.txt").chmod(0o644)
    with pytest.raises(CandidateError):
        validate_staged_candidate(stage, candidate)


def test_t02_unsafe_candidate_entries_fail_closed(tmp_path: Path) -> None:
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "bad").symlink_to("../../outside")
    source_root = tmp_path / "assets"
    (source_root / "spec_dock").mkdir(parents=True)
    (source_root / "install_root").mkdir()
    for _kind, _public, suffix in FIXED_DOMAINS:
        target = source_root / suffix
        target.mkdir(parents=True, exist_ok=True)
        if suffix == "spec_dock/docs":
            shutil.copy2(domain / "bad", target / "bad", follow_symlinks=False)
    with pytest.raises(CandidateError):
        capture_packaged_candidate(source_root)

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import shutil
import sys
import zipfile

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def _infra():
    return __import__(
        "spec_dock_runtime.infra.issue_planning_candidate",
        fromlist=["build_deterministic_zip"],
    )


def _files() -> dict[str, bytes]:
    return {
        "CHECKSUMS.sha256": b"checksums\n",
        "MANIFEST.json": b"{}\n",
        "PLACEHOLDER-ORACLE-MAP.json": b"{}\n",
        "SOURCE-BASELINE.json": b"{}\n",
        "design.md": b"design\n",
        "plan.md": b"plan\n",
        "requirement.md": b"requirement\n",
    }


def test_zip_bytes_are_reproducible_for_fixed_inputs_and_timestamp(tmp_path: Path) -> None:
    instant = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    _infra().build_deterministic_zip(first, "candidate", _files(), instant)
    _infra().build_deterministic_zip(second, "candidate", _files(), instant)
    assert first.read_bytes() == second.read_bytes()


def test_zip_entry_order_permissions_timestamp_comments_and_extra_fields_are_fixed(
    tmp_path: Path,
) -> None:
    path = tmp_path / "candidate.zip"
    _infra().build_deterministic_zip(
        path,
        "candidate",
        _files(),
        datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
    )
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        assert [info.filename for info in infos] == sorted(
            [f"candidate/{name}" for name in _files()],
            key=lambda value: value.encode(),
        )
        assert archive.comment == b""
        assert all(info.external_attr >> 16 == 0o100644 for info in infos)
        assert all(info.extra == b"" and info.comment == b"" for info in infos)


@pytest.mark.parametrize("kind", ["missing", "inside", "ancestor", "symlink"])
def test_output_guard_requires_existing_external_non_symlink_directory(
    tmp_path: Path,
    kind: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    output = tmp_path / "output"
    if kind == "inside":
        output = repo / "output"
        output.mkdir()
    elif kind == "ancestor":
        output = tmp_path
    elif kind == "symlink":
        target = tmp_path / "target"
        target.mkdir()
        output.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="output"):
        _infra().validate_candidate_output_directory(output, repo)


def test_atomic_publication_collision_preserves_existing_bytes(tmp_path: Path) -> None:
    source = tmp_path / "staged.zip"
    source.write_bytes(b"new")
    destination = tmp_path / "candidate.zip"
    destination.write_bytes(b"existing")
    before = hashlib.sha256(destination.read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        _infra().atomic_publish_no_replace(source, destination)
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == before


def _valid_candidate(
    tmp_path: Path,
    *,
    body: str = "Substantive content.",
) -> tuple[Path, Path, object]:
    domain = __import__(
        "spec_dock_runtime.domain.issue_planning_candidate",
        fromlist=["build_candidate_material"],
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningContext"],
    )
    documents = {
        name: (
            "---\n"
            f"種別: {kind}\n"
            'ID: "iss-00003"\n'
            'タイトル: "Issue"\n'
            '状態: "approved"\n'
            '作成者: "Author"\n'
            '最終更新: "2026-07-28"\n'
            + (
                '依存: ["requirement.md"]\n'
                if name == "design.md"
                else '依存: ["requirement.md", "design.md"]\n'
                if name == "plan.md"
                else ""
            )
            + '親: ["epic-00002", "init-00001"]\n'
            "---\n\n"
            f"# iss-00003 Issue\n\n## Section\n\n{body}\n"
        ).encode()
        for name, kind in (
            ("requirement.md", "要件定義書（Issue）"),
            ("design.md", "設計書（Issue）"),
            ("plan.md", "実装計画書（Issue）"),
        )
    }
    payload = domain.render_planner_payload(documents)
    context = contracts.PlanningContext(
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        parent_epic_id="epic-00002",
        parent_initiative_id="init-00001",
        dependency_summary=(),
        canonical_issue_paths=(
            "spec-dock/initiatives/i/epics/e/issues/x/design.md",
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md",
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md",
        ),
        relevant_source_paths=(),
        operator_context=(),
    )
    source = contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash="b" * 64,
        snapshot_id="c" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    material = domain.build_candidate_material(
        planner_documents=documents,
        baseline=domain.parse_current_front_matter_baseline(documents),
        context=context,
        source_evidence=source,
        planner_payload=payload,
        operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
    )
    repo = tmp_path / "repo"
    output = tmp_path / "output"
    repo.mkdir()
    output.mkdir()
    published = _infra().build_and_publish_candidate(
        output_guard=_infra().validate_candidate_output_directory(output, repo),
        repo_root=repo,
        material=material,
    )
    return repo, output / published.identity.logical_filename, published.identity


@pytest.mark.parametrize("renamed", ["candidate-copy.zip", "candidate (0).zip", "candidate.zip.bak"])
def test_load_verified_candidate_rejects_fuzzy_and_unauthorized_rename(
    tmp_path: Path,
    renamed: str,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    target = candidate.with_name(renamed)
    candidate.rename(target)
    with pytest.raises(ValueError):
        _infra().load_verified_issue_candidate(target, repo)


def test_load_verified_candidate_accepts_closed_alias_and_rejects_repack_and_root_mismatch(
    tmp_path: Path,
) -> None:
    repo, candidate, identity = _valid_candidate(tmp_path)
    alias = candidate.with_name(f"{candidate.stem} (2).zip")
    shutil.copyfile(candidate, alias)
    loaded = _infra().load_verified_issue_candidate(alias, repo)
    assert loaded.identity.logical_filename == identity.logical_filename
    assert loaded.identity.observed_transport_filename == alias.name

    repacked = candidate.with_name(identity.logical_filename)
    candidate.unlink()
    with zipfile.ZipFile(alias) as source, zipfile.ZipFile(repacked, "w") as destination:
        for name in source.namelist():
            destination.writestr(name, source.read(name))
    with pytest.raises(ValueError):
        _infra().load_verified_issue_candidate(repacked, repo)

    root_mismatch = candidate.with_name(f"{candidate.stem} (3).zip")
    with zipfile.ZipFile(alias) as source, zipfile.ZipFile(root_mismatch, "w") as destination:
        for name in source.namelist():
            relative = name.split("/", 1)[1]
            destination.writestr(f"wrong-root/{relative}", source.read(name))
    with pytest.raises(ValueError):
        _infra().load_verified_issue_candidate(root_mismatch, repo)


def test_load_verified_candidate_uses_validated_bytes_when_path_is_swapped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    repo, candidate, _ = _valid_candidate(first_root)
    _, other_candidate, _ = _valid_candidate(second_root, body="Different valid content.")
    first_bytes = candidate.read_bytes()
    other_bytes = other_candidate.read_bytes()
    assert first_bytes != other_bytes
    infra = _infra()
    original_review = infra.review_pack_input

    def swap_after_validation(path: Path, *, profile):
        result = original_review(path, profile=profile)
        candidate.write_bytes(other_bytes)
        return result

    monkeypatch.setattr(infra, "review_pack_input", swap_after_validation)
    loaded = infra.load_verified_issue_candidate(candidate, repo)
    assert loaded.zip_bytes == first_bytes
    assert loaded.identity.zip_sha256 == hashlib.sha256(first_bytes).hexdigest()


def test_load_verified_candidate_never_returns_transient_sensitive_malformed_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    original_candidate_bytes = candidate.read_bytes()
    transient_bytes = b"token=abc123secret; not a ZIP"
    infra = _infra()
    original_review = infra.review_pack_input
    original_read_bytes = Path.read_bytes
    restore_on_read = [False]

    def swap_after_validation(path: Path, *, profile):
        result = original_review(path, profile=profile)
        candidate.write_bytes(transient_bytes)
        restore_on_read[0] = True
        return result

    def transient_read(path: Path) -> bytes:
        data = original_read_bytes(path)
        if path == candidate and restore_on_read[0]:
            candidate.write_bytes(original_candidate_bytes)
            restore_on_read[0] = False
        return data

    monkeypatch.setattr(infra, "review_pack_input", swap_after_validation)
    monkeypatch.setattr(Path, "read_bytes", transient_read)
    try:
        loaded = infra.load_verified_issue_candidate(candidate, repo)
    finally:
        candidate.write_bytes(original_candidate_bytes)
    assert loaded.zip_bytes == original_candidate_bytes
    assert b"abc123secret" not in loaded.zip_bytes


def test_load_verified_candidate_fifo_swap_is_nonblocking_and_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    infra = _infra()
    original_open = infra.os.open
    swapped = [False]

    def swap_before_open(path, flags, *args, **kwargs):
        if (
            (Path(path) == candidate or (path == candidate.name and kwargs.get("dir_fd") is not None))
            and not swapped[0]
        ):
            swapped[0] = True
            candidate.unlink()
            os.mkfifo(candidate)
            assert flags & infra.os.O_NONBLOCK
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(infra.os, "open", swap_before_open)
    with pytest.raises(ValueError):
        infra.load_verified_issue_candidate(candidate, repo)
    assert swapped == [True]


def test_load_verified_candidate_parent_swap_never_redirects_into_repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_root = tmp_path / "external"
    repo_root = tmp_path / "repo-side"
    external_root.mkdir()
    repo_root.mkdir()
    repo, candidate, _ = _valid_candidate(external_root)
    _, repo_candidate, _ = _valid_candidate(repo_root, body="Repository secret data.")
    original_bytes = candidate.read_bytes()
    redirected_bytes = repo_candidate.read_bytes()
    assert original_bytes != redirected_bytes
    redirected = repo / candidate.name
    shutil.copyfile(repo_candidate, redirected)
    parent = candidate.parent
    backup = tmp_path / "external-parent-backup"
    infra = _infra()
    original_open = infra.os.open
    swapped = [False]

    def swap_parent() -> None:
        if swapped[0]:
            return
        swapped[0] = True
        parent.rename(backup)
        parent.symlink_to(repo, target_is_directory=True)

    def swap_during_open(path, flags, *args, **kwargs):
        if Path(path) == candidate and not swapped[0]:
            swap_parent()
            return original_open(path, flags, *args, **kwargs)
        if path == parent.name and flags & getattr(os, "O_DIRECTORY", 0) and not swapped[0]:
            descriptor = original_open(path, flags, *args, **kwargs)
            swap_parent()
            return descriptor
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(infra.os, "open", swap_during_open)
    loaded = infra.load_verified_issue_candidate(candidate, repo)
    assert loaded.zip_bytes == original_bytes
    assert redirected_bytes not in loaded.zip_bytes
    assert swapped == [True]

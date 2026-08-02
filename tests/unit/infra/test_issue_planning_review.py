from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def test_review_evidence_directory_publishes_atomically_no_replace(tmp_path: Path) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    repo = tmp_path / "repo"
    output.mkdir()
    repo.mkdir()
    published = review.publish_planning_review_evidence(
        output_dir=output,
        repo_root=repo,
        reviewed_identity_sha256="a" * 64,
        review_result_bytes=b'{"verdict":"pass"}',
        summary_bytes=b"# Planning Review\n",
        operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
        publication_guard=lambda: True,
    )
    assert (output / published.review_result_file).read_bytes() == b'{"verdict":"pass"}'
    assert (output / published.review_summary_file).read_bytes() == b"# Planning Review\n"
    with pytest.raises(FileExistsError):
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b"changed",
            summary_bytes=b"changed",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=lambda: True,
        )
    assert (output / published.review_result_file).read_bytes() == b'{"verdict":"pass"}'


def test_review_publication_rejects_staging_directory_name_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    repo = tmp_path / "repo"
    output.mkdir()
    repo.mkdir()
    replaced: list[Path] = []
    original_publish = review._atomic_publish_no_replace_at

    def replace_staging(parent, staged, destination, *, expected_files):
        displaced_name = f"{staged.name}.owned"
        os.rename(staged.name, displaced_name, src_dir_fd=parent, dst_dir_fd=parent)
        replacement = output / staged.name
        replacement.mkdir()
        (replacement / "attacker-controlled").write_bytes(b"must remain")
        replaced.append(replacement)
        original_publish(parent, staged, destination, expected_files=expected_files)

    monkeypatch.setattr(review, "_atomic_publish_no_replace_at", replace_staging)
    with pytest.raises(ValueError, match=r"identity|staging|publication"):
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b'{"verdict":"pass"}',
            summary_bytes=b"# Planning Review\n",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=lambda: True,
        )

    assert replaced
    assert (replaced[0] / "attacker-controlled").read_bytes() == b"must remain"
    assert (output / f"{replaced[0].name}.owned" / "planning-review-result.json").is_file()
    assert not any(path.name.startswith("review-") for path in output.iterdir())


@pytest.mark.parametrize("guard_mode", ["false", "exception"])
@pytest.mark.parametrize("destructive_operation", ["unlink", "rmdir"])
def test_review_cleanup_without_conditional_remove_preserves_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    guard_mode: str,
    destructive_operation: str,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    repo = tmp_path / "repo"
    sentinel = output / "sentinel.txt"
    output.mkdir()
    repo.mkdir()
    sentinel.write_bytes(b"keep")

    def forbidden_destructive_operation(*args: object, **kwargs: object) -> None:
        del args, kwargs
        pytest.fail(f"cleanup attempted unsafe {destructive_operation}")

    monkeypatch.setattr(review.os, destructive_operation, forbidden_destructive_operation)

    def publication_guard() -> bool:
        if guard_mode == "exception":
            raise RuntimeError("guard detail must not escape")
        return False

    with pytest.raises(OSError) as error:
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b'{"verdict":"pass"}',
            summary_bytes=b"# Planning Review\n",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=publication_guard,
        )

    assert not isinstance(error.value, review.ReviewSourceStale)
    assert sentinel.read_bytes() == b"keep"
    published = next(path for path in output.iterdir() if path.name.startswith("review-"))
    assert (published / "planning-review-result.json").read_bytes() == b'{"verdict":"pass"}'
    assert (published / "planning-review-summary.md").read_bytes() == b"# Planning Review\n"


def test_review_publication_rejects_staging_child_replacement_without_deleting_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    repo = tmp_path / "repo"
    output.mkdir()
    repo.mkdir()
    original_verify = review._verify_review_directory_contents
    calls = [0]

    def replace_child_after_capture(directory, expected_files):
        original_verify(directory, expected_files)
        calls[0] += 1
        if calls[0] == 1:
            os.rename(
                "planning-review-result.json",
                "planning-review-result.json.owned",
                src_dir_fd=directory.descriptor,
                dst_dir_fd=directory.descriptor,
            )
            descriptor = os.open(
                "planning-review-result.json",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=directory.descriptor,
            )
            try:
                os.write(descriptor, b"attacker-controlled")
            finally:
                os.close(descriptor)

    monkeypatch.setattr(review, "_verify_review_directory_contents", replace_child_after_capture)
    with pytest.raises(ValueError, match=r"identity|contents|publication"):
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b'{"verdict":"pass"}',
            summary_bytes=b"# Planning Review\n",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=lambda: True,
        )

    staging = next(path for path in output.iterdir() if path.name.startswith(".spec-dock-planning-review-"))
    assert (staging / "planning-review-result.json").read_bytes() == b"attacker-controlled"
    assert (staging / "planning-review-result.json.owned").is_file()


@pytest.mark.parametrize("swap_kind", ["symlink", "replacement"])
def test_review_publication_rejects_output_directory_identity_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    swap_kind: str,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    backup = tmp_path / "original-output"
    repo = tmp_path / "repo"
    output.mkdir()
    repo.mkdir()
    original_write = review._write_exact_at
    writes = [0]

    def swap_after_staging(directory_descriptor: int, name: str, data: bytes) -> None:
        original_write(directory_descriptor, name, data)
        writes[0] += 1
        if writes[0] != 2:
            return
        output.rename(backup)
        if swap_kind == "symlink":
            output.symlink_to(repo, target_is_directory=True)
        else:
            output.mkdir()

    monkeypatch.setattr(review, "_write_exact_at", swap_after_staging)
    with pytest.raises(ValueError, match=r"identity|output"):
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b'{"verdict":"pass"}',
            summary_bytes=b"# Planning Review\n",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=lambda: True,
        )
    assert list(repo.iterdir()) == []
    if output.is_dir() and not output.is_symlink():
        assert list(output.iterdir()) == []


def test_review_publication_never_stages_through_swapped_output_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    backup = tmp_path / "original-output"
    repo = tmp_path / "repo"
    output.mkdir()
    repo.mkdir()
    original_revalidate = review._revalidate_output_guard
    original_write = review._write_exact_at
    revalidations = [0]
    repo_write_observed = [False]

    def swap_after_initial_revalidation(guard: object, repo_root: Path) -> None:
        original_revalidate(guard, repo_root)
        revalidations[0] += 1
        if revalidations[0] == 1:
            output.rename(backup)
            output.symlink_to(repo, target_is_directory=True)

    def observe_write(directory_descriptor: int, name: str, data: bytes) -> None:
        repo_write_observed[0] |= bool(list(repo.iterdir()))
        original_write(directory_descriptor, name, data)
        repo_write_observed[0] |= bool(list(repo.iterdir()))

    monkeypatch.setattr(review, "_revalidate_output_guard", swap_after_initial_revalidation)
    monkeypatch.setattr(review, "_write_exact_at", observe_write)
    with pytest.raises(ValueError, match=r"identity|output"):
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b'{"verdict":"pass"}',
            summary_bytes=b"# Planning Review\n",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=lambda: True,
        )
    assert repo_write_observed == [False]
    assert list(repo.iterdir()) == []
    staging = next(path for path in backup.iterdir() if path.name.startswith(".spec-dock-planning-review-"))
    assert (staging / "planning-review-result.json").is_file()


def test_review_publication_never_renames_through_swapped_output_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["publish_planning_review_evidence"],
    )
    output = tmp_path / "output"
    backup = tmp_path / "original-output"
    repo = tmp_path / "repo"
    output.mkdir()
    repo.mkdir()
    original_revalidate = review._revalidate_output_guard
    revalidations = [0]
    repo_baseline: list[tuple[str, bytes]] = []

    def swap_after_final_revalidation(guard: object, repo_root: Path) -> None:
        original_revalidate(guard, repo_root)
        revalidations[0] += 1
        if revalidations[0] != 2:
            return
        temporary_name = next(
            child.name for child in output.iterdir() if child.name.startswith(".spec-dock-planning-review-")
        )
        output.rename(backup)
        output.symlink_to(repo, target_is_directory=True)
        malicious_source = repo / temporary_name
        malicious_source.mkdir()
        (malicious_source / "attacker-controlled").write_bytes(b"not review evidence")
        repo_baseline.extend(
            (str(path.relative_to(repo)), path.read_bytes()) for path in repo.rglob("*") if path.is_file()
        )

    monkeypatch.setattr(review, "_revalidate_output_guard", swap_after_final_revalidation)
    with pytest.raises(OSError, match=r"publication failed"):
        review.publish_planning_review_evidence(
            output_dir=output,
            repo_root=repo,
            reviewed_identity_sha256="a" * 64,
            review_result_bytes=b'{"verdict":"pass"}',
            summary_bytes=b"# Planning Review\n",
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            publication_guard=lambda: True,
        )
    assert [
        (str(path.relative_to(repo)), path.read_bytes()) for path in repo.rglob("*") if path.is_file()
    ] == repo_baseline
    assert any(path.name.startswith(".spec-dock-planning-review-") for path in repo.iterdir())
    staging = next(path for path in backup.iterdir() if path.name.startswith("review-"))
    assert staging.is_dir()
    assert (staging / "planning-review-result.json").is_file()


@pytest.mark.parametrize("swap_kind", ["fifo", "symlink"])
def test_external_review_result_transient_swap_is_nonblocking_and_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    swap_kind: str,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["read_external_review_result"],
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    result_path = tmp_path / "review.json"
    content = b'{"verdict":"pass"}'
    result_path.write_bytes(content)
    original_open = review.os.open
    swapped = [False]

    def swap_before_open(path, flags, *args, **kwargs):
        if (
            Path(path) == result_path or (path == result_path.name and kwargs.get("dir_fd") is not None)
        ) and not swapped[0]:
            swapped[0] = True
            result_path.unlink()
            if swap_kind == "fifo":
                os.mkfifo(result_path)
                assert flags & review.os.O_NONBLOCK
            else:
                result_path.symlink_to(repo)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(review.os, "open", swap_before_open)
    with pytest.raises((FileNotFoundError, ValueError)):
        review.read_external_review_result(
            result_path,
            repo_root=repo,
            expected_sha256=hashlib.sha256(content).hexdigest(),
        )
    assert swapped == [True]


def test_external_review_result_rejects_oversize_without_pathname_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["read_external_review_result"],
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    result_path = tmp_path / "review.json"
    result_path.write_bytes(b"x" * (review.MAX_REVIEW_RESULT_BYTES + 1))
    original_read_bytes = Path.read_bytes
    pathname_reads = [0]
    descriptor_read_requests: list[int] = []
    original_os_read = review.os.read

    def observe_pathname_read(path: Path) -> bytes:
        if path == result_path:
            pathname_reads[0] += 1
        return original_read_bytes(path)

    def observe_descriptor_read(descriptor: int, count: int) -> bytes:
        descriptor_read_requests.append(count)
        return original_os_read(descriptor, count)

    monkeypatch.setattr(Path, "read_bytes", observe_pathname_read)
    monkeypatch.setattr(review.os, "read", observe_descriptor_read)
    with pytest.raises(ValueError, match="bounded"):
        review.read_external_review_result(
            result_path,
            repo_root=repo,
            expected_sha256="a" * 64,
        )
    assert pathname_reads == [0]
    assert sum(descriptor_read_requests) <= review.MAX_REVIEW_RESULT_BYTES + 1


def test_external_review_result_parent_swap_never_redirects_into_repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    review = __import__(
        "spec_dock_runtime.infra.issue_planning_review",
        fromlist=["read_external_review_result"],
    )
    repo = tmp_path / "repo"
    external = tmp_path / "external"
    repo.mkdir()
    external.mkdir()
    result_path = external / "review.json"
    original_bytes = b'{"verdict":"pass"}'
    redirected_bytes = b'{"token":"abc123secret"}'
    result_path.write_bytes(original_bytes)
    (repo / result_path.name).write_bytes(redirected_bytes)
    backup = tmp_path / "external-backup"
    original_open = review.os.open
    original_read_bytes = Path.read_bytes
    swapped = [False]

    def swap_parent() -> None:
        if swapped[0]:
            return
        swapped[0] = True
        external.rename(backup)
        external.symlink_to(repo, target_is_directory=True)

    def swap_during_open(path, flags, *args, **kwargs):
        if Path(path) == result_path and not swapped[0]:
            swap_parent()
            return original_open(path, flags, *args, **kwargs)
        if path == external.name and flags & getattr(os, "O_DIRECTORY", 0) and not swapped[0]:
            descriptor = original_open(path, flags, *args, **kwargs)
            swap_parent()
            return descriptor
        return original_open(path, flags, *args, **kwargs)

    def swap_during_pathname_read(path: Path) -> bytes:
        if path == result_path:
            swap_parent()
        return original_read_bytes(path)

    monkeypatch.setattr(review.os, "open", swap_during_open)
    monkeypatch.setattr(Path, "read_bytes", swap_during_pathname_read)
    with pytest.raises(ValueError):
        review.read_external_review_result(
            result_path,
            repo_root=repo,
            expected_sha256=hashlib.sha256(redirected_bytes).hexdigest(),
        )
    assert swapped == [True]

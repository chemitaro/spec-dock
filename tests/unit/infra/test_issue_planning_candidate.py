from datetime import datetime, timezone
import hashlib
from pathlib import Path
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

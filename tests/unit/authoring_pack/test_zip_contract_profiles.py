from dataclasses import replace
from pathlib import Path
import stat
import sys
import unicodedata
import zipfile

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def _zip_contract():
    return __import__(
        "spec_dock_runtime.domain.authoring_pack.zip_contract",
        fromlist=["issue_candidate_v1_profile", "review_pack_input"],
    )


COMPANION_PATH = (
    "artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"
)
CANDIDATE_INVENTORY = (
    "CHECKSUMS.sha256",
    "MANIFEST.json",
    "PLACEHOLDER-ORACLE-MAP.json",
    "SOURCE-BASELINE.json",
    COMPANION_PATH,
    "design.md",
    "plan.md",
    "requirement.md",
)
AUTHORING_INVENTORY = (
    COMPANION_PATH,
    "design.md",
    "plan.md",
    "requirement.md",
)


def _zip(path: Path, root: str = "candidate", *, names: tuple[str, ...] | None = None) -> None:
    inventory = names or CANDIDATE_INVENTORY
    with zipfile.ZipFile(path, "w") as archive:
        for name in inventory:
            info = zipfile.ZipInfo(f"{root}/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, "{}\n" if name.endswith(".json") else "text\n")


def test_issue_candidate_profile_accepts_exact_generated_zip(tmp_path: Path) -> None:
    path = tmp_path / "candidate.zip"
    _zip(path)
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    assert module.review_pack_input(path, profile=profile).status == "pass"


def test_s10_issue_authoring_profile_accepts_exact_four_file_zip(tmp_path: Path) -> None:
    path = tmp_path / "authoring.zip"
    _zip(path, "authoring", names=AUTHORING_INVENTORY)
    module = _zip_contract()
    profile = module.issue_authoring_v1_profile(
        expected_root="authoring",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert result.status == "pass"
    assert tuple(sorted(result.reviewed_files)) == tuple(sorted(AUTHORING_INVENTORY))


@pytest.mark.parametrize(
    ("names", "finding"),
    [
        ((COMPANION_PATH, "design.md", "requirement.md"), "inventory_mismatch"),
        ((*AUTHORING_INVENTORY, "notes.md"), "inventory_mismatch"),
        ((*AUTHORING_INVENTORY, "architecture.md"), "inventory_mismatch"),
        ((COMPANION_PATH,), "inventory_mismatch"),
    ],
)
def test_s10_issue_authoring_profile_rejects_missing_extra_fourth_spec_and_partial_inventory(
    tmp_path: Path,
    names: tuple[str, ...],
    finding: str,
) -> None:
    path = tmp_path / "authoring.zip"
    _zip(path, "authoring", names=names)
    module = _zip_contract()
    profile = module.issue_authoring_v1_profile(
        expected_root="authoring",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert result.status == "rejected"
    assert finding in result.findings


def test_s10_issue_authoring_profile_rejects_directory_entry(tmp_path: Path) -> None:
    path = tmp_path / "authoring.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for name in AUTHORING_INVENTORY:
            info = zipfile.ZipInfo(f"authoring/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, "text\n")
        archive.writestr("authoring/extra/", b"")
    module = _zip_contract()
    profile = module.issue_authoring_v1_profile(
        expected_root="authoring",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert result.status == "rejected"
    assert "directory_entry" in result.findings


def test_issue_candidate_profile_accepts_transcript_marker_mentions_without_turn_pairs(
    tmp_path: Path,
) -> None:
    path = tmp_path / "candidate.zip"
    required = CANDIDATE_INVENTORY
    marker_content = {
        "design.md": "# Raw transcript vocabulary\n\nThe term raw transcript names an evidence class.\n",
        "plan.md": "- ChatGPT transcript、credential、private absolute pathを保存しない。\n",
        "requirement.md": "The runtime must not persist a browser transcript.\n",
    }
    with zipfile.ZipFile(path, "w") as archive:
        for name in required:
            info = zipfile.ZipInfo(f"candidate/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(
                info,
                marker_content.get(name, "{}\n"),
            )
    validator_calls: list[tuple[tuple[str, ...], str]] = []

    def validate(files, root):
        validator_calls.append((tuple(sorted(files)), root))
        return ()

    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=validate,
    )
    result = module.review_pack_input(path, profile=profile)

    assert result.status == "pass"
    assert tuple(sorted(result.reviewed_files)) == tuple(sorted(required))
    assert validator_calls == [(tuple(sorted(required)), "candidate")]


def test_issue_candidate_profile_rejects_structured_transcript_payload(tmp_path: Path) -> None:
    path = tmp_path / "candidate.zip"
    transcript = "# Oracle Browser Transcript\n## Prompt\nprivate requirement body\n## Answer\nprivate response body\n"
    required = CANDIDATE_INVENTORY
    with zipfile.ZipFile(path, "w") as archive:
        for name in required:
            info = zipfile.ZipInfo(f"candidate/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, transcript if name == "design.md" else "{}\n")
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)

    assert result.status == "rejected"
    assert "raw_transcript" in result.findings
    assert "private requirement body" not in repr(result.findings)
    assert str(tmp_path) not in repr(result.findings)


def test_issue_candidate_profile_rejects_tree_input(tmp_path: Path) -> None:
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    assert module.review_pack_input(tmp_path, profile=profile).findings == ("zip_input_required",)


@pytest.mark.parametrize(
    ("root", "names", "finding"),
    [
        ("wrong", None, "wrong_root"),
        ("candidate", ("../design.md",), "unsafe_path"),
        ("candidate", ("design.md",), "inventory_mismatch"),
        ("candidate", ("nested.zip",), "nested_archive"),
    ],
)
def test_issue_candidate_profile_rejects_unsafe_archive_class(
    tmp_path: Path,
    root: str,
    names: tuple[str, ...] | None,
    finding: str,
) -> None:
    path = tmp_path / "candidate.zip"
    _zip(path, root, names=names)
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert result.status == "rejected"
    assert finding in result.findings


def test_generic_review_pack_input_default_characterization_is_unchanged(tmp_path: Path) -> None:
    result = _zip_contract().review_pack_input(tmp_path)
    assert result.input_kind == "tree"
    assert result.fallback is True
    assert "wrong_root" in result.findings


@pytest.mark.parametrize(
    ("mode", "finding"),
    [
        ("directory", "directory_entry"),
        ("duplicate", "duplicate_entry"),
        ("casefold", "casefold_collision"),
        ("unicode", "unicode_nfc_collision"),
        ("symlink", "symlink_entry"),
        ("special", "special_entry"),
        ("executable", "executable_entry"),
        ("binary", "binary_payload"),
    ],
)
def test_issue_candidate_profile_rejects_entry_type_collision_and_binary_classes(
    tmp_path: Path,
    mode: str,
    finding: str,
) -> None:
    path = tmp_path / "candidate.zip"
    required = CANDIDATE_INVENTORY
    with zipfile.ZipFile(path, "w") as archive:
        for name in required:
            info = zipfile.ZipInfo(f"candidate/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            content = b"{}\n" if name.endswith(".json") else b"text\n"
            if mode == "symlink" and name == "design.md":
                info.external_attr = (stat.S_IFLNK | 0o644) << 16
            elif mode == "special" and name == "design.md":
                info.external_attr = (stat.S_IFIFO | 0o644) << 16
            elif mode == "executable" and name == "design.md":
                info.external_attr = (stat.S_IFREG | 0o755) << 16
            elif mode == "binary" and name == "design.md":
                content = b"\xff"
            archive.writestr(info, content)
        if mode == "directory":
            archive.writestr("candidate/extra/", b"")
        elif mode == "duplicate":
            with pytest.warns(UserWarning, match="Duplicate name"):
                info = zipfile.ZipInfo("candidate/design.md")
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, b"duplicate")
        elif mode == "casefold":
            archive.writestr("candidate/DESIGN.md", b"collision")
        elif mode == "unicode":
            composed = "candidate/r\u00e9sum\u00e9.md"
            decomposed = unicodedata.normalize("NFD", composed)
            archive.writestr(composed, b"one")
            archive.writestr(decomposed, b"two")
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert result.status == "rejected"
    assert finding in result.findings


def test_issue_candidate_profile_enforces_resource_limits(tmp_path: Path) -> None:
    path = tmp_path / "candidate.zip"
    _zip(path)
    module = _zip_contract()
    profile = replace(
        module.issue_candidate_v1_profile(
            expected_root="candidate",
            expected_companion_path=COMPANION_PATH,
            cross_file_validator=lambda files, root: (),
        ),
        max_entry_bytes=1,
        max_total_bytes=1,
        max_file_count=1,
    )
    findings = module.review_pack_input(path, profile=profile).findings
    assert "file_count_limit" in findings
    assert "entry_size_limit" in findings
    assert "total_size_limit" in findings


def test_issue_candidate_profile_findings_do_not_echo_sensitive_values_or_absolute_paths(
    tmp_path: Path,
) -> None:
    path = tmp_path / "candidate.zip"
    secret = "token=abc123secret"
    with zipfile.ZipFile(path, "w") as archive:
        for name in CANDIDATE_INVENTORY:
            info = zipfile.ZipInfo(f"candidate/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, secret if name == "design.md" else "{}\n")
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert "secret_like_payload" in result.findings
    assert secret not in repr(result.findings)
    assert str(tmp_path) not in repr(result.findings)


@pytest.mark.parametrize(
    ("mode", "finding"),
    [
        ("encrypted", "encrypted_entry"),
        ("crc", "unreadable_payload"),
        ("ratio", "entry_compression_ratio_limit"),
    ],
)
def test_issue_candidate_profile_rejects_encryption_crc_and_compression_ratio(
    tmp_path: Path,
    mode: str,
    finding: str,
) -> None:
    path = tmp_path / "candidate.zip"
    required = CANDIDATE_INVENTORY
    compression = zipfile.ZIP_DEFLATED if mode == "ratio" else zipfile.ZIP_STORED
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        for name in required:
            info = zipfile.ZipInfo(f"candidate/{name}")
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = compression
            content = b"A" * 10_000 if mode == "ratio" and name == "design.md" else f"{name}\n".encode()
            archive.writestr(info, content)
    if mode == "encrypted":
        _set_encrypted_flag(path, "candidate/design.md")
    elif mode == "crc":
        _corrupt_stored_entry(path, "candidate/design.md")
    module = _zip_contract()
    profile = module.issue_candidate_v1_profile(
        expected_root="candidate",
        expected_companion_path=COMPANION_PATH,
        cross_file_validator=lambda files, root: (),
    )
    result = module.review_pack_input(path, profile=profile)
    assert result.status == "rejected"
    assert finding in result.findings


def _set_encrypted_flag(path: Path, target: str) -> None:
    data = bytearray(path.read_bytes())
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo(target)
        local_offset = info.header_offset
    local_flags = int.from_bytes(data[local_offset + 6 : local_offset + 8], "little") | 0x1
    data[local_offset + 6 : local_offset + 8] = local_flags.to_bytes(2, "little")
    cursor = 0
    while True:
        cursor = data.find(b"PK\x01\x02", cursor)
        if cursor < 0:
            raise AssertionError("central directory entry not found")
        name_length = int.from_bytes(data[cursor + 28 : cursor + 30], "little")
        extra_length = int.from_bytes(data[cursor + 30 : cursor + 32], "little")
        comment_length = int.from_bytes(data[cursor + 32 : cursor + 34], "little")
        name = bytes(data[cursor + 46 : cursor + 46 + name_length]).decode()
        if name == target:
            flags = int.from_bytes(data[cursor + 8 : cursor + 10], "little") | 0x1
            data[cursor + 8 : cursor + 10] = flags.to_bytes(2, "little")
            break
        cursor += 46 + name_length + extra_length + comment_length
    path.write_bytes(data)


def _corrupt_stored_entry(path: Path, target: str) -> None:
    data = bytearray(path.read_bytes())
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo(target)
        offset = info.header_offset
    name_length = int.from_bytes(data[offset + 26 : offset + 28], "little")
    extra_length = int.from_bytes(data[offset + 28 : offset + 30], "little")
    payload_offset = offset + 30 + name_length + extra_length
    data[payload_offset] ^= 0x01
    path.write_bytes(data)

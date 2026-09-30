"""Fixed Git commit IDs accept only complete SHA-1 or SHA-256 output."""

import pytest


@pytest.mark.parametrize("output", [b"a" * 39 + b"\n", b"a" * 41 + b"\n", b"a" * 40 + b"\nextra\n", b"g" * 64 + b"\n"])
def test_incomplete_or_non_hex_commit_output_is_rejected(output: bytes) -> None:
    from spec_dock.runtime.domain.git_ref import parse_commit_oid

    with pytest.raises(ValueError, match="commit OID"):
        parse_commit_oid(output)


@pytest.mark.parametrize("output", [b"a" * 40 + b"\n", b"1" * 64 + b"\n"])
def test_full_sha1_and_sha256_commit_output_is_admitted(output: bytes) -> None:
    from spec_dock.runtime.domain.git_ref import parse_commit_oid

    assert parse_commit_oid(output) == output[:-1].decode("ascii")

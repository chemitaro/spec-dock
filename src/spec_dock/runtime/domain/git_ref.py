"""Values admitted from Git's resolved commit output."""

import re


def parse_commit_oid(output: bytes) -> str:
    value = output.removesuffix(b"\n")
    if re.fullmatch(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})", value) is None:
        raise ValueError("Git commit OID must be a full SHA-1 or SHA-256 ID")
    return value.decode("ascii")

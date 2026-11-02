from __future__ import annotations

import re
import unicodedata

DEFAULT_ID_WIDTH = 5

ID_RE = re.compile(r"^(?P<prefix>init|epic|iss|adr)(?:-(?P<local>local))?-(?P<num>[0-9]+)$")
NUM_RE = re.compile(r"^[0-9]+$")
# An explicit `artifact create --slug` (Artifact naming; R-J7) is kebab-case only.
INPUT_SLUG_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Canonical-mode Scope IDs (Epic design ch. 2): five digits zero-padded, longer numbers never start with 0.
CANONICAL_ID_RE = re.compile(r"^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$")


def validate_input_slug_kebab(value: str, *, field: str = "--slug") -> str:
    """Validate CLI input slug for new/import commands (kebab-case only)."""
    slug = value.strip()
    if not slug:
        raise RuntimeError(f"{field} is required")
    if INPUT_SLUG_KEBAB_RE.fullmatch(slug):
        return slug
    raise RuntimeError(
        f"{field} is invalid: {value!r}\n"
        f"expected regex: {INPUT_SLUG_KEBAB_RE.pattern}\n"
        "OK examples: 'add-refresh-token', 'jwt-auth-2'\n"
        "NG examples: 'Add-token', 'add_token', 'add..token', '日本語'"
    )


def slugify(title: str) -> str:
    """Conservative Unicode-aware slugifier for filenames."""
    s = unicodedata.normalize("NFKC", title).strip().lower()
    s = re.sub(r"\s+", "-", s)

    out: list[str] = []
    for ch in s:
        if ch.isalnum() or ch in ("-", "_", "."):
            out.append(ch)
        else:
            out.append("-")

    slug = "".join(out)
    slug = re.sub(r"-{2,}", "-", slug).strip("-._")
    return slug or "item"


def parse_id(value: str) -> tuple[str, bool, int]:
    """Parse a node id (`<prefix>-<num>` or `<prefix>-local-<num>`)."""
    m = ID_RE.fullmatch(value.strip().lower())
    if not m:
        raise RuntimeError(f"Invalid id format: {value!r} (expected: <prefix>-NNNN or <prefix>-local-NNNN)")
    prefix = m.group("prefix")
    is_local = m.group("local") == "local"
    num = int(m.group("num"))
    return prefix, is_local, num


def format_id(prefix: str, num: int, *, width: int = DEFAULT_ID_WIDTH, local: bool = False) -> str:
    """Format an id with zero-padding."""
    if local:
        return f"{prefix}-local-{num:0{width}d}"
    return f"{prefix}-{num:0{width}d}"


def deps_node_sort_key(node_id: str) -> tuple[int, int, str]:
    """Deterministic sort key for dependency-related outputs."""
    _, is_local, num = parse_id(node_id)
    return (1 if is_local else 0, num, node_id)

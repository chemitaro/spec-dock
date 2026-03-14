from __future__ import annotations

import re

from ..application.contracts import TargetRef

_num_re = re.compile(r"^[0-9]+$")
_gh_issue_url_re = re.compile(r"/issues/(?P<num>[0-9]+)\b")
_node_id_re = re.compile(r"^(?P<prefix>init|epic|iss)(?:-(?P<local>local))?-(?P<num>[0-9]+)$")
_id_in_text_re = re.compile(r"(?<![a-z0-9])(?P<id>(?:init|epic|iss)(?:-local)?-[0-9]+)(?![a-z0-9])")


def parse_github_issue_target(target: str) -> int:
    raw = target.strip()
    if not raw:
        raise RuntimeError("target is required")

    match = _gh_issue_url_re.search(raw)
    if match:
        return int(match.group("num"))

    if raw.startswith("#") and _num_re.fullmatch(raw[1:]):
        return int(raw[1:])

    if _num_re.fullmatch(raw):
        return int(raw)

    raise RuntimeError(
        "Invalid target. Use a GitHub issue number (e.g. 123 / #123 / URL like .../issues/123)."
    )


def parse_active_like_target(target: str) -> tuple[TargetRef, str]:
    raw = target.strip()
    if not raw:
        raise RuntimeError("target is required")

    match = _gh_issue_url_re.search(raw)
    if match:
        issue_number = int(match.group("num"))
        return (TargetRef(kind="github_issue", node_id=None, github_issue_number=issue_number), f"github#{issue_number}")

    if raw.startswith("#") and _num_re.fullmatch(raw[1:]):
        issue_number = int(raw[1:])
        return (TargetRef(kind="github_issue", node_id=None, github_issue_number=issue_number), f"github#{issue_number}")

    if _num_re.fullmatch(raw):
        issue_number = int(raw)
        return (TargetRef(kind="github_issue", node_id=None, github_issue_number=issue_number), f"github#{issue_number}")

    lowered = raw.lower()
    matches = [item.group("id") for item in _id_in_text_re.finditer(lowered)]
    unique = sorted(set(matches))
    if len(unique) == 1:
        _assert_valid_node_id(unique[0])
        return (TargetRef(kind="node_id", node_id=unique[0], github_issue_number=None), unique[0])

    if len(unique) > 1:
        by_prefix: dict[str, list[str]] = {"iss": [], "epic": [], "init": []}
        for item in unique:
            for prefix in ("iss", "epic", "init"):
                if item.startswith(prefix + "-"):
                    by_prefix[prefix].append(item)
                    break

        for prefix in ("iss", "epic", "init"):
            values = by_prefix[prefix]
            if len(values) == 1:
                _assert_valid_node_id(values[0])
                return (TargetRef(kind="node_id", node_id=values[0], github_issue_number=None), values[0])
            if len(values) > 1:
                raise RuntimeError(f"Ambiguous target: multiple {prefix} ids found: {', '.join(sorted(values))}")

        raise RuntimeError(f"Ambiguous target: multiple ids found: {', '.join(unique)}")

    raise RuntimeError(
        "Invalid target. Use a GitHub issue number (e.g. 123 / #123 / URL) or a node id (e.g. iss-00123)."
    )


def _assert_valid_node_id(value: str) -> None:
    if _node_id_re.fullmatch(value) is None:
        raise RuntimeError(f"Invalid node id: {value}")


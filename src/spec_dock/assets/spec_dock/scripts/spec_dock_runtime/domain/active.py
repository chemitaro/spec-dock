from __future__ import annotations

from .models import BranchDecision, SpecNode


def resolve_branch_decision(node: SpecNode, *, candidate_is_valid: bool = True) -> BranchDecision:
    candidate = f"{node.id}-{node.slug}"
    fallback = node.id
    warnings: list[str] = []

    if not candidate.isascii():
        warnings.append("id-slug is non-ascii; fallback to id")
        return BranchDecision(desired=fallback, candidates=(candidate, fallback), warnings=tuple(warnings))

    if not candidate_is_valid:
        warnings.append("id-slug is invalid ref; fallback to id")
        return BranchDecision(desired=fallback, candidates=(candidate, fallback), warnings=tuple(warnings))

    return BranchDecision(desired=candidate, candidates=(candidate, fallback), warnings=tuple(warnings))

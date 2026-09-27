"""Strict vNext selector syntax and snapshot resolution."""

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.domain.selectors import (  # noqa: E402
    ActiveScopeSelector,
    ArtifactRootSelector,
    GithubScopeSelector,
    ScopeIdSelector,
    WorktreeIdSelector,
    WorktreePathSelector,
    parse_artifact_selector,
    parse_github_ref,
    parse_scope_selector,
    parse_worktree_selector,
)


def test_full_scope_id_normalizes_case_and_existing_width() -> None:
    assert parse_scope_selector("  ISS-409  ") == ScopeIdSelector("iss-00409", "issue")
    assert parse_scope_selector("epic-local-7") == ScopeIdSelector("epic-local-00007", "epic")


def test_explicit_current_and_github_refs_have_distinct_types() -> None:
    assert parse_scope_selector("@current") == ActiveScopeSelector("current")
    assert parse_scope_selector("gh:Chemitaro/Spec-Dock#409") == GithubScopeSelector("chemitaro", "spec-dock", 409)


@pytest.mark.parametrize("bad", ["409", "#409", "plan iss-00409", "@root", "iss-0", "https://github.com/a/b/pull/2"])
def test_scope_selector_rejects_ambiguous_or_wrong_resource(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_scope_selector(bad)


def test_import_ref_requires_exact_github_issue_identity() -> None:
    expected = GithubScopeSelector("chemitaro", "spec-dock", 409)
    assert parse_github_ref("https://github.com/chemitaro/spec-dock/issues/409") == expected
    assert parse_github_ref("409", repo_hint="chemitaro/spec-dock") == expected
    assert parse_github_ref("gh:chemitaro/spec-dock#409") == expected


@pytest.mark.parametrize(
    ("value", "hint"),
    [
        ("#409", "chemitaro/spec-dock"),
        ("409", None),
        ("https://github.com/a/b/issues/1?x=2", None),
        ("https://github.com/a/b/issues/1#section", None),
        ("https://user:pass@github.com/a/b/issues/1", None),
        ("https://github.com/a/b/pull/1", None),
        ("gh:a/b#1", "other/b"),
    ],
)
def test_import_ref_rejects_bare_or_foreign_or_non_issue(value: str, hint: str | None) -> None:
    with pytest.raises(ValueError):
        parse_github_ref(value, repo_hint=hint)


def test_artifact_root_is_available_only_to_artifact_selector() -> None:
    assert parse_artifact_selector("@root") == ArtifactRootSelector()
    with pytest.raises(ValueError):
        parse_scope_selector("@root")


def test_worktree_selector_requires_registered_shape() -> None:
    assert parse_worktree_selector("wt:planning-1") == WorktreeIdSelector("planning-1")
    assert parse_worktree_selector("/tmp/worktrees/planning") == WorktreePathSelector("/tmp/worktrees/planning")
    for bad in ("../planning", "/tmp/../private", "wt:../../x", "", "file:///tmp/planning"):
        with pytest.raises(ValueError):
            parse_worktree_selector(bad)


def test_absolute_worktree_path_preserves_significant_whitespace() -> None:
    assert parse_worktree_selector("/tmp/planning ") == WorktreePathSelector("/tmp/planning ")
    with pytest.raises(ValueError):
        parse_worktree_selector(" wt:planning-1")
    with pytest.raises(ValueError):
        parse_worktree_selector("planning-1 ")

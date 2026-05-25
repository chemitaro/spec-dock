import sys
import tempfile
import unittest
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.delegated_authoring import (
            DelegatedAuthoringManifestRequest,
            generate_delegated_authoring_manifest,
        )
        from spec_dock_runtime.domain import delegated_authoring
    finally:
        sys.path.pop(0)
    return DelegatedAuthoringManifestRequest, generate_delegated_authoring_manifest, delegated_authoring


class TestDelegatedAuthoringRuntimeDomain(unittest.TestCase):
    def test_manifest_request_returns_deprecated_blocked_result_without_artifacts(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = repo_root / "input-authority.json"
            authority_file.write_text("{}\n", encoding="utf-8")

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00003",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "deprecated")
            self.assertEqual(result.reason, "deprecated_scope_local_discussion_drafts")
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_diff_guard_allows_new_flat_discussion_markdown(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "discussions" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            self.assertTrue(result.ok, result.details)
            self.assertEqual(result.status, "pass")

    def test_diff_guard_rejects_new_discussion_without_frontmatter_editable_state(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "discussions" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text("# draft\n\nadoption_status: unreviewed\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            self.assertFalse(result.ok)
            self.assertIn("reason=new_discussion_missing_proposed_state", "\n".join(result.details))

    def test_diff_guard_rejects_new_discussion_with_non_editable_state_claim(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "discussions" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text("---\nadoption_status: adopted\n---\n# draft\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            self.assertFalse(result.ok)
            self.assertIn("reason=new_discussion_claims_non_editable_state", "\n".join(result.details))

    def test_diff_guard_rejects_mixed_staged_and_unmerged_discussion_statuses(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussions_dir = issue_dir / "discussions"
            mixed_create = discussions_dir / "20260525t010203z-disc-mixed-create.md"
            mixed_create.write_text("---\nadoption_status: unreviewed\n---\n# mixed create\n", encoding="utf-8")
            mixed_update = discussions_dir / "20260525t010204z-disc-mixed-update.md"
            mixed_update.write_text("---\nadoption_status: unreviewed\n---\n# mixed update\n", encoding="utf-8")
            unmerged_add = discussions_dir / "20260525t010205z-disc-unmerged-add.md"
            unmerged_add.write_text("---\nadoption_status: unreviewed\n---\n# unmerged add\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(
                    domain.DiffGuardEntry(status="AM", path=mixed_create.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="MM", path=mixed_update.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="AA", path=unmerged_add.relative_to(repo_root)),
                ),
                allow_existing_discussions=(mixed_update.relative_to(repo_root),),
            )

            self.assertFalse(result.ok)
            joined = "\n".join(result.details)
            self.assertEqual(joined.count("reason=mixed_staged_unstaged_discussion"), 2)
            self.assertIn("reason=unmerged_status", joined)

    def test_diff_guard_allows_allowlisted_existing_discussion_update(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "discussions" / "20260525t010203z-01-research-agent-draft.md"
            discussion.write_text("---\nadoption_status: unreviewed\n---\n# draft\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status=" M", path=discussion.relative_to(repo_root)),),
                allow_existing_discussions=(discussion.relative_to(repo_root),),
            )

            self.assertTrue(result.ok, result.details)

    def test_diff_guard_rejects_allowlisted_existing_discussion_without_proposed_state(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            unstated = issue_dir / "discussions" / "20260525t010204z-disc-unstated-draft.md"
            unstated.write_text("# missing state\n", encoding="utf-8")
            non_editable_paths = []
            for index, state in enumerate(
                (
                    "accepted",
                    "adopted",
                    "partially_adopted",
                    "integrated",
                    "partially_integrated",
                    "rejected",
                    "superseded",
                    "blocked",
                    "stale",
                ),
                start=1,
            ):
                discussion = issue_dir / "discussions" / f"20260525t0102{index:02d}z-disc-{state.replace('_', '-')}.md"
                field = "adoption_status" if "adopted" in state else "status"
                discussion.write_text(f"---\n{field}: {state}\n---\n# {state}\n", encoding="utf-8")
                non_editable_paths.append(discussion)

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=tuple(
                    domain.DiffGuardEntry(status=" M", path=path.relative_to(repo_root))
                    for path in (*non_editable_paths, unstated)
                ),
                allow_existing_discussions=tuple(path.relative_to(repo_root) for path in (*non_editable_paths, unstated)),
            )

            self.assertFalse(result.ok)
            joined = "\n".join(result.details)
            self.assertIn("reason=existing_discussion_not_proposed", joined)
            self.assertEqual(joined.count("reason=existing_discussion_not_proposed"), len(non_editable_paths))
            self.assertIn("reason=existing_discussion_missing_proposed_state", joined)

    def test_diff_guard_rejects_allowlisted_update_when_editable_state_is_only_body_text(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "discussions" / "20260525t010203z-01-research-agent-draft.md"
            discussion.write_text("# body-only\n\nstatus: proposed\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status=" M", path=discussion.relative_to(repo_root)),),
                allow_existing_discussions=(discussion.relative_to(repo_root),),
            )

            self.assertFalse(result.ok)
            self.assertIn("reason=existing_discussion_missing_proposed_state", "\n".join(result.details))

    def test_diff_guard_rejects_symlinked_discussions_dir_without_status_entries(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            external_discussions = repo_root / "external-discussions"
            external_discussions.mkdir()
            discussions_dir = issue_dir / "discussions"
            discussions_dir.rmdir()
            discussions_dir.symlink_to(external_discussions, target_is_directory=True)

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(),
            )

            self.assertFalse(result.ok)
            self.assertIn("reason=discussions_dir_symlink", "\n".join(result.details))

    def test_diff_guard_rejects_discussion_symlink_without_status_entries(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            symlink = issue_dir / "discussions" / "20260525t010203z-disc-link.md"
            symlink.symlink_to(issue_dir / "design.md")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(),
            )

            self.assertFalse(result.ok)
            self.assertIn("reason=discussion_symlink", "\n".join(result.details))


    def test_diff_guard_rejects_forbidden_paths(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            forbidden_entries = (
                domain.DiffGuardEntry(status=" M", path=(issue_dir / "design.md").relative_to(repo_root)),
                domain.DiffGuardEntry(status=" M", path=Path("src/spec_dock/cli.py")),
                domain.DiffGuardEntry(status=" M", path=Path("tests/test_runtime.py")),
                domain.DiffGuardEntry(status="??", path=Path(".agents/agent.md")),
                domain.DiffGuardEntry(status="??", path=Path(".codex/config.toml")),
                domain.DiffGuardEntry(status="??", path=Path(".github/workflows/ci.yml")),
                domain.DiffGuardEntry(status="??", path=Path(".env.local")),
            )

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=forbidden_entries,
            )

            self.assertFalse(result.ok)
            joined = "\n".join(result.details)
            self.assertIn("reason=canonical_doc", joined)
            self.assertIn("reason=forbidden_root", joined)
            self.assertIn("reason=env_file", joined)

    def test_diff_guard_rejects_malformed_discussion_diffs(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            other_issue_dir = _make_issue_scope(repo_root, scope_id="iss-00004", slug="other")
            discussions_dir = issue_dir / "discussions"
            nested = discussions_dir / "nested" / "20260525t010203z-disc-nested.md"
            nested.parent.mkdir()
            nested.write_text("# nested\n", encoding="utf-8")
            symlink = discussions_dir / "20260525t010203z-disc-link.md"
            symlink.symlink_to(issue_dir / "design.md")
            dangling_symlink = discussions_dir / "20260525t010203z-disc-dangling-link.md"
            dangling_symlink.symlink_to(issue_dir / "missing.md")
            non_md = discussions_dir / "20260525t010203z-disc-agent-draft.txt"
            non_md.write_text("text\n", encoding="utf-8")
            bad_name = discussions_dir / "20260525t010203z-disc.md"
            bad_name.write_text("# bad\n", encoding="utf-8")
            retired_note_kind = discussions_dir / "20260525t010203z-note-retired-kind.md"
            retired_note_kind.write_text("# retired note kind\n", encoding="utf-8")
            unallowlisted = discussions_dir / "20260525t010204z-disc-existing-draft.md"
            unallowlisted.write_text("# existing\n", encoding="utf-8")
            other_discussion = other_issue_dir / "discussions" / "20260525t010205z-disc-other.md"
            other_discussion.write_text("# other\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(
                    domain.DiffGuardEntry(status="??", path=nested.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=symlink.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=dangling_symlink.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=non_md.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=bad_name.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=retired_note_kind.relative_to(repo_root)),
                    domain.DiffGuardEntry(
                        status=" D",
                        path=(discussions_dir / "20260525t010206z-disc-old.md").relative_to(repo_root),
                    ),
                    domain.DiffGuardEntry(
                        status="R ",
                        path=(discussions_dir / "20260525t010207z-disc-new.md").relative_to(repo_root),
                        original_path=(discussions_dir / "20260525t010207z-disc-old.md").relative_to(repo_root),
                    ),
                    domain.DiffGuardEntry(status=" M", path=unallowlisted.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=other_discussion.relative_to(repo_root)),
                ),
            )

            self.assertFalse(result.ok)
            joined = "\n".join(result.details)
            self.assertIn("reason=outside_target_discussions", joined)
            self.assertIn("reason=symlink", joined)
            self.assertIn("reason=non_markdown", joined)
            self.assertIn("reason=discussion_name_noncompliant", joined)
            self.assertIn("reason=delete", joined)
            self.assertIn("reason=rename_or_copy", joined)
            self.assertIn("reason=existing_discussion_not_allowlisted", joined)


def _make_issue_scope(repo_root: Path, *, scope_id: str = "iss-00003", slug: str = "delegated-authoring") -> Path:
    issue_dir = (
        repo_root
        / "spec-dock"
        / "initiatives"
        / "init-00001-architecture"
        / "epics"
        / "epic-00112-delegated-authoring"
        / "issues"
        / f"{scope_id}-{slug}"
    )
    issue_dir.mkdir(parents=True)
    (issue_dir / "discussions").mkdir()
    (issue_dir / ".meta.json").write_text(f'{{"id": "{scope_id}"}}\n', encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_dir / name).write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    return issue_dir


def _draft_text(body: str) -> str:
    return f"---\nadoption_status: unreviewed\n---\n{body}\n"


if __name__ == "__main__":
    unittest.main()

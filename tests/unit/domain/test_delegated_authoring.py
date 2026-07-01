from pathlib import Path
import sys
import tempfile


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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


def _application_diff_guard_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.delegated_authoring import (
            DelegatedAuthoringDiffGuardRequest,
            run_delegated_authoring_diff_guard,
        )
    finally:
        sys.path.pop(0)
    return DelegatedAuthoringDiffGuardRequest, run_delegated_authoring_diff_guard


class TestDelegatedAuthoringRuntimeDomain:
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

            assert not result.ok
            assert result.status == "deprecated"
            assert result.reason == "deprecated_scope_local_discussion_drafts"
            assert not (issue_dir / "artifacts" / "delegated-authoring").exists()

    def test_application_diff_guard_rejects_missing_baseline_status(self) -> None:
        request_cls, run_diff_guard = _application_diff_guard_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _make_issue_scope(repo_root)

            result = run_diff_guard(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00003",
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    baseline_status=None,
                )
            )

            assert not result.ok
            assert result.status == "blocked"
            assert result.reason == "missing_baseline_status"

    def test_diff_guard_allows_new_flat_artifact_markdown(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert result.ok, result.details
            assert result.status == "pass"

    def test_diff_guard_allows_new_pr_repair_batch_artifact_markdown(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-pr-repair-batch-agent-draft.md"
            discussion.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert result.ok, result.details
            assert result.status == "pass"

    def test_diff_guard_allows_blank_artifact_markdown(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-agent-draft.md"
            discussion.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                authorized_role="system-architect",
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert result.ok, result.details
            assert result.status == "pass"

    def test_diff_guard_rejects_future_discussion_output(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "discussions" / "20260525t010203z-disc-agent-draft.md"
            discussion.parent.mkdir()
            discussion.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            joined = "\n".join(result.details)
            assert "reason=future_noncompliant_discussion_output" in joined
            assert "reason=expected_exactly_one_new_artifact_draft count=0" in joined

    def test_diff_guard_rejects_artifact_with_mismatched_scope(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-pr-repair-batch-pr-repair-batch.md"
            discussion.write_text(_draft_text("# draft").replace("scope_id: iss-00003", "scope_id: iss-99999"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=new_artifact_scope_id_mismatch" in "\n".join(result.details)

    def test_diff_guard_allows_implementation_planner_artifact_markdown(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text(_draft_text("# draft", role="implementation-planner"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                authorized_role="implementation-planner",
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert result.ok, result.details
            assert result.status == "pass"

    def test_diff_guard_allows_quoted_role_and_scope_frontmatter_scalars(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            text = _draft_text("# draft", role="implementation-planner")
            text = text.replace(
                "created_by_role: implementation-planner",
                'created_by_role: "implementation-planner"',
            ).replace("scope_id: iss-00003", "scope_id: 'iss-00003'")
            discussion.write_text(text, encoding="utf-8")

            result = domain.evaluate_diff_guard(
                authorized_role="implementation-planner",
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert result.ok, result.details
            assert result.status == "pass"

    def test_diff_guard_rejects_artifact_created_by_different_authorized_role(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text(_draft_text("# draft", role="implementation-planner"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                authorized_role="system-architect",
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=new_artifact_created_by_role_mismatch" in "\n".join(result.details)

    def test_diff_guard_rejects_arbitrary_diff_guard_result_frontmatter(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text(
                _draft_text("# draft").replace("diff_guard_result: pending", "diff_guard_result: banana"),
                encoding="utf-8",
            )

            result = domain.evaluate_diff_guard(
                authorized_role="system-architect",
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=new_artifact_missing_provenance:diff_guard_result" in "\n".join(result.details)

    def test_diff_guard_rejects_new_artifact_without_frontmatter_editable_state(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text("# draft\n\nadoption_status: unreviewed\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=new_artifact_missing_proposed_state" in "\n".join(result.details)

    def test_diff_guard_rejects_new_artifact_with_non_editable_state_claim(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text("---\nadoption_status: adopted\n---\n# draft\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=new_artifact_claims_non_editable_state" in "\n".join(result.details)

    def test_diff_guard_rejects_new_artifact_with_quoted_accepted_authority(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            text = _draft_text("# draft").replace(
                "adoption_status: unreviewed",
                'authority: "accepted"\nmirror_eligible: true\nadoption_status: unreviewed',
            )
            discussion.write_text(text, encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=new_artifact_claims_non_editable_state" in "\n".join(result.details)

    def test_diff_guard_rejects_new_artifact_without_required_provenance(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text("---\nadoption_status: unreviewed\n---\n# draft\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert not result.ok
            joined = "\n".join(result.details)
            assert "reason=new_artifact_missing_provenance:" in joined
            assert "created_by_role" in joined
            assert "diff_guard_result" in joined

    def test_diff_guard_rejects_mixed_staged_and_unmerged_discussion_statuses(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussions_dir = issue_dir / "artifacts"
            mixed_create = discussions_dir / "20260525t010203z-disc-mixed-create.md"
            mixed_create.write_text(_draft_text("# mixed create"), encoding="utf-8")
            mixed_update = discussions_dir / "20260525t010204z-disc-mixed-update.md"
            mixed_update.write_text(_draft_text("# mixed update"), encoding="utf-8")
            unmerged_add = discussions_dir / "20260525t010205z-disc-unmerged-add.md"
            unmerged_add.write_text(_draft_text("# unmerged add"), encoding="utf-8")

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

            assert not result.ok
            joined = "\n".join(result.details)
            assert joined.count("reason=mixed_staged_unstaged_artifact") == 2
            assert "reason=unmerged_status" in joined

    def test_diff_guard_rejects_existing_artifact_update_even_when_allowlisted(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-01-research-agent-draft.md"
            discussion.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status=" M", path=discussion.relative_to(repo_root)),),
                allow_existing_discussions=(discussion.relative_to(repo_root),),
            )

            assert not result.ok
            assert "reason=existing_artifact_update_unsupported" in "\n".join(result.details)

    def test_diff_guard_ignores_unchanged_allow_existing_discussion_with_valid_artifact(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            legacy_discussion = issue_dir / "discussions" / "001-legacy-evidence.md"
            legacy_discussion.parent.mkdir()
            legacy_discussion.write_text("# legacy evidence\n", encoding="utf-8")
            artifact = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            artifact.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=artifact.relative_to(repo_root)),),
                allow_existing_discussions=(legacy_discussion.relative_to(repo_root),),
            )

            assert result.ok
            joined = "\n".join(result.details)
            assert "reason=existing_artifact_update_unsupported" not in joined
            assert f"allowed path={artifact.relative_to(repo_root).as_posix()}" in joined

    def test_diff_guard_rejects_new_artifact_rules_md_output(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            rules = issue_dir / "artifacts" / "rules.md"
            rules.write_text(_draft_text("# draft"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=rules.relative_to(repo_root)),),
            )

            assert not result.ok
            assert "reason=artifact_name_noncompliant" in "\n".join(result.details)

    def test_diff_guard_rejects_multiple_new_artifact_drafts(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            first = issue_dir / "artifacts" / "20260525t010203z-disc-first-draft.md"
            second = issue_dir / "artifacts" / "20260525t010204z-disc-second-draft.md"
            first.write_text(_draft_text("# first"), encoding="utf-8")
            second.write_text(_draft_text("# second"), encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(
                    domain.DiffGuardEntry(status="??", path=first.relative_to(repo_root)),
                    domain.DiffGuardEntry(status="??", path=second.relative_to(repo_root)),
                ),
            )

            assert not result.ok
            assert "reason=expected_exactly_one_new_artifact_draft count=2" in "\n".join(result.details)

    def test_diff_guard_rejects_zero_new_artifact_drafts(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(),
            )

            assert not result.ok
            assert "reason=expected_exactly_one_new_artifact_draft count=0" in "\n".join(result.details)

    def test_diff_guard_rejects_new_artifact_with_mismatched_scope_or_role(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        cases = (
            (
                "scope",
                _draft_text("# draft").replace("scope_id: iss-00003", "scope_id: iss-99999"),
                "scope_id_mismatch",
            ),
            (
                "role",
                _draft_text("# draft").replace("created_by_role: system-architect", "created_by_role: dev-coder"),
                "missing_provenance:created_by_role",
            ),
        )
        for name_, text, expected in cases:
            case = f"case={name_}"
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                issue_dir = _make_issue_scope(repo_root)
                discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
                discussion.write_text(text, encoding="utf-8")

                result = domain.evaluate_diff_guard(
                    scope_id="iss-00003",
                    repo_root=repo_root,
                    scope_dir=issue_dir,
                    entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
                )

                assert not result.ok, case
                assert f"reason=new_artifact_{expected}" in "\n".join(result.details), case

    def test_diff_guard_rejects_new_artifact_with_empty_source_or_target_provenance(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        cases = (
            (
                "source_paths",
                "source_paths:\n  - spec-dock/active/issue/requirement.md",
                "source_paths: []",
                "empty_source_paths",
            ),
            (
                "intended_targets",
                "intended_targets:\n  - spec-dock/active/issue/design.md",
                "intended_targets: []",
                "empty_intended_targets",
            ),
            (
                "scalar_source_paths",
                "source_paths:\n  - spec-dock/active/issue/requirement.md",
                "source_paths: spec-dock/active/issue/requirement.md",
                "empty_source_paths",
            ),
            (
                "scalar_intended_targets",
                "intended_targets:\n  - spec-dock/active/issue/design.md",
                "intended_targets: spec-dock/active/issue/design.md",
                "empty_intended_targets",
            ),
            (
                "quoted_empty_source_paths",
                "source_paths:\n  - spec-dock/active/issue/requirement.md",
                'source_paths:\n  - ""',
                "empty_source_paths",
            ),
            (
                "list_like_empty_intended_targets",
                "intended_targets:\n  - spec-dock/active/issue/design.md",
                "intended_targets:\n  - []",
                "empty_intended_targets",
            ),
        )
        for name_, old, new, expected in cases:
            case = f"case={name_}"
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                issue_dir = _make_issue_scope(repo_root)
                discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
                discussion.write_text(_draft_text("# draft").replace(old, new), encoding="utf-8")

                result = domain.evaluate_diff_guard(
                    scope_id="iss-00003",
                    repo_root=repo_root,
                    scope_dir=issue_dir,
                    entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
                )

                assert not result.ok, case
                assert f"reason=new_artifact_{expected}" in "\n".join(result.details), case

    def test_diff_guard_accepts_new_artifact_with_inline_source_and_target_lists(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
            discussion.write_text(
                _draft_text("# draft")
                .replace(
                    "source_paths:\n  - spec-dock/active/issue/requirement.md",
                    'source_paths: ["spec-dock/active/issue/requirement.md"]',
                )
                .replace(
                    "intended_targets:\n  - spec-dock/active/issue/design.md",
                    "intended_targets: ['spec-dock/active/issue/design.md']",
                ),
                encoding="utf-8",
            )

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
            )

            assert result.ok

    def test_diff_guard_rejects_duplicate_frontmatter_provenance_keys(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        cases = (
            ("created_by_role", "created_by_role: system-architect"),
            ("scope_id", "scope_id: iss-00003"),
            ("source_paths", "source_paths:\n  - spec-dock/active/issue/requirement.md"),
            ("intended_targets", "intended_targets:\n  - spec-dock/active/issue/design.md"),
            ("adoption_status", "adoption_status: unreviewed"),
            ("reflected_to", "reflected_to: []"),
            ("diff_guard_result", "diff_guard_result: pending"),
        )
        for key, duplicate_line in cases:
            case = f"key={key}"
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                issue_dir = _make_issue_scope(repo_root)
                discussion = issue_dir / "artifacts" / "20260525t010203z-disc-agent-draft.md"
                discussion.write_text(
                    _draft_text("# draft").replace("---\n", f"---\n{duplicate_line}\n", 1),
                    encoding="utf-8",
                )

                result = domain.evaluate_diff_guard(
                    scope_id="iss-00003",
                    repo_root=repo_root,
                    scope_dir=issue_dir,
                    entries=(domain.DiffGuardEntry(status="??", path=discussion.relative_to(repo_root)),),
                )

                assert not result.ok, case
                assert f"reason=new_artifact_duplicate_provenance:{key}" in "\n".join(result.details), case

    def test_diff_guard_rejects_allowlisted_existing_artifact_without_state_as_unsupported_update(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            unstated = issue_dir / "artifacts" / "20260525t010204z-disc-unstated-draft.md"
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
                discussion = issue_dir / "artifacts" / f"20260525t0102{index:02d}z-disc-{state.replace('_', '-')}.md"
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
                allow_existing_discussions=tuple(
                    path.relative_to(repo_root) for path in (*non_editable_paths, unstated)
                ),
            )

            assert not result.ok
            joined = "\n".join(result.details)
            assert joined.count("reason=existing_artifact_update_unsupported") == len(non_editable_paths) + 1

    def test_diff_guard_rejects_allowlisted_update_with_body_only_state_as_unsupported_update(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            discussion = issue_dir / "artifacts" / "20260525t010203z-01-research-agent-draft.md"
            discussion.write_text("# body-only\n\nstatus: proposed\n", encoding="utf-8")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(domain.DiffGuardEntry(status=" M", path=discussion.relative_to(repo_root)),),
                allow_existing_discussions=(discussion.relative_to(repo_root),),
            )

            assert not result.ok
            assert "reason=existing_artifact_update_unsupported" in "\n".join(result.details)

    def test_diff_guard_rejects_symlinked_discussions_dir_without_status_entries(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            external_discussions = repo_root / "external-discussions"
            external_discussions.mkdir()
            discussions_dir = issue_dir / "artifacts"
            discussions_dir.rmdir()
            discussions_dir.symlink_to(external_discussions, target_is_directory=True)

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(),
            )

            assert not result.ok
            assert "reason=artifacts_dir_symlink" in "\n".join(result.details)

    def test_diff_guard_rejects_artifact_symlink_without_status_entries(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            symlink = issue_dir / "artifacts" / "20260525t010203z-disc-link.md"
            symlink.symlink_to(issue_dir / "design.md")

            result = domain.evaluate_diff_guard(
                scope_id="iss-00003",
                repo_root=repo_root,
                scope_dir=issue_dir,
                entries=(),
            )

            assert not result.ok
            assert "reason=artifact_symlink" in "\n".join(result.details)

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

            assert not result.ok
            joined = "\n".join(result.details)
            assert "reason=canonical_doc" in joined
            assert "reason=forbidden_root" in joined
            assert "reason=env_file" in joined

    def test_diff_guard_rejects_malformed_discussion_diffs(self) -> None:
        _request_cls, _generate, domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            other_issue_dir = _make_issue_scope(repo_root, scope_id="iss-00004", slug="other")
            discussions_dir = issue_dir / "artifacts"
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
            other_discussion = other_issue_dir / "artifacts" / "20260525t010205z-disc-other.md"
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

            assert not result.ok
            joined = "\n".join(result.details)
            assert "reason=outside_target_artifacts" in joined
            assert "reason=symlink" in joined
            assert "reason=non_markdown" in joined
            assert "reason=artifact_name_noncompliant" in joined
            assert "reason=delete" in joined
            assert "reason=rename_or_copy" in joined
            assert "reason=existing_artifact_update_unsupported" in joined


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
    (issue_dir / "artifacts").mkdir()
    (issue_dir / ".meta.json").write_text(f'{{"id": "{scope_id}"}}\n', encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_dir / name).write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    return issue_dir


def _draft_text(body: str, *, role: str = "system-architect") -> str:
    return (
        "---\n"
        f"created_by_role: {role}\n"
        "scope_id: iss-00003\n"
        "source_paths:\n"
        "  - spec-dock/active/issue/requirement.md\n"
        "intended_targets:\n"
        "  - spec-dock/active/issue/design.md\n"
        "adoption_status: unreviewed\n"
        "reflected_to: []\n"
        "diff_guard_result: pending\n"
        "---\n"
        f"{body}\n"
    )

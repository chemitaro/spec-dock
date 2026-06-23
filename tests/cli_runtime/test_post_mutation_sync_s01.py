from pathlib import Path
import sys


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
        from spec_dock_runtime.application import contracts as app_contracts, sync_state as app_sync_state
        from spec_dock_runtime.domain import models as domain_models
    finally:
        sys.path.pop(0)
    return app_contracts, app_sync_state, domain_models


def _sync_result(app_contracts, domain_models, *, warnings=None, artifact_failure=None):
    state = app_contracts.SyncStateResult(
        graph=domain_models.SpecGraph(nodes_by_id={}),
        active=None,
        issue_statuses={},
        progress=domain_models.ProgressMap(by_node_id={}, counts={}),
        deps_state=domain_models.DepsState(nodes=[], warnings=[]),
        deps_eval_by_id={},
        generated_at="2026-05-14T00:00:00Z",
        warnings=list(warnings or []),
        deps_preflight_error=None,
        repo_root=Path("/repo"),
    )
    write_result = app_contracts.ArtifactWriteResult(
        index_all_path="spec-dock/.agent/index-all.json",
        index_todo_path="spec-dock/.agent/index.json",
        tree_all_path="spec-dock/.agent/tree-all.json",
        tree_todo_path="spec-dock/.agent/tree.json",
        tree_all_puml_path="spec-dock/tree-all.puml",
        tree_todo_puml_path="spec-dock/tree.puml",
        deps_issues_json_path="spec-dock/.agent/deps-issues.json",
        deps_issues_puml_path="spec-dock/deps-issues.puml",
        deps_raw_puml_path="spec-dock/deps-raw.puml",
        dashboard_md_path="spec-dock/dashboard.md",
    )
    return app_contracts.SyncCommandResult(
        state=state,
        write_result=None if artifact_failure is not None else write_result,
        active_update=None,
        artifact_failure=artifact_failure,
    )


class TestPostMutationSyncS01:
    def test_tc_s01_001_success_outcome_preserves_sync_result(self) -> None:
        app_contracts, app_sync_state, domain_models = _runtime_modules()
        expected = _sync_result(app_contracts, domain_models)

        original = app_sync_state.sync_after_mutation
        app_sync_state.sync_after_mutation = lambda _ports: expected
        try:
            outcome = app_sync_state.post_mutation_sync(object())
        finally:
            app_sync_state.sync_after_mutation = original

        assert outcome.sync_result is expected
        assert not outcome.failed
        assert outcome.exception_reason is None
        assert outcome.skipped_reason is None
        assert outcome.guidance == []

    def test_tc_s01_002_exception_outcome_does_not_erase_mutation_success(self) -> None:
        _app_contracts, app_sync_state, _domain_models = _runtime_modules()

        def _raise(_ports):
            raise RuntimeError("boom")

        original = app_sync_state.sync_after_mutation
        app_sync_state.sync_after_mutation = _raise
        try:
            outcome = app_sync_state.post_mutation_sync(object())
        finally:
            app_sync_state.sync_after_mutation = original

        assert outcome.failed
        assert outcome.sync_result is None
        assert outcome.exception_reason == "boom"
        assert any("mutation succeeded" in line for line in outcome.guidance)
        assert any("./spec-dock/scripts/spec-dock sync" in line for line in outcome.guidance)

    def test_tc_s01_003_artifact_failure_is_failed_and_guided(self) -> None:
        app_contracts, _app_sync_state, domain_models = _runtime_modules()
        failure = app_contracts.ArtifactWriteFailure(status="failed_partial_or_stale", reason="disk full")
        result = _sync_result(app_contracts, domain_models, artifact_failure=failure)

        outcome = app_contracts.PostMutationSyncOutcome.from_sync_result(result)

        assert outcome.failed
        assert outcome.sync_result is result
        assert any("stale or partially written" in line for line in outcome.guidance)

    def test_tc_s01_004_gh_fetch_failed_warning_is_failed(self) -> None:
        app_contracts, _app_sync_state, domain_models = _runtime_modules()
        result = _sync_result(app_contracts, domain_models, warnings=["gh_fetch_failed"])

        outcome = app_contracts.PostMutationSyncOutcome.from_sync_result(result)

        assert outcome.failed
        assert outcome.fatal_warnings == ["gh_fetch_failed"]
        assert any("gh_fetch_failed" in line for line in outcome.guidance)

    def test_tc_s01_005_gh_index_incomplete_warning_is_non_fatal(self) -> None:
        app_contracts, _app_sync_state, domain_models = _runtime_modules()
        result = _sync_result(app_contracts, domain_models, warnings=["gh_index_incomplete"])

        outcome = app_contracts.PostMutationSyncOutcome.from_sync_result(result)

        assert not outcome.failed
        assert outcome.warnings == ["gh_index_incomplete"]
        assert outcome.fatal_warnings == []
        assert outcome.guidance == []

    def test_tc_s01_006_request_policy_uses_github_no_branch_update_and_no_migrate(self) -> None:
        app_contracts, app_sync_state, domain_models = _runtime_modules()
        calls = []

        def _fake_sync_impl(req, _ports, *, active_manifest_mode):
            calls.append((req, active_manifest_mode))
            return _sync_result(app_contracts, domain_models)

        original = app_sync_state._sync_impl
        app_sync_state._sync_impl = _fake_sync_impl
        try:
            result = app_sync_state.sync_after_mutation(object())
        finally:
            app_sync_state._sync_impl = original

        assert result is not None
        assert len(calls) == 1
        req, active_manifest_mode = calls[0]
        assert req.github_enabled
        assert req.issue_limit == 10000
        assert not req.force
        assert not req.update_active_from_branch
        assert active_manifest_mode == "no_migrate"

    def test_tc_s01_007_helper_has_no_side_effect_until_explicit_success_call(self) -> None:
        _app_contracts, app_sync_state, _domain_models = _runtime_modules()
        calls = []

        def _unexpected(_ports):
            calls.append("called")
            raise AssertionError("post-mutation sync should require an explicit call")

        original = app_sync_state.sync_after_mutation
        app_sync_state.sync_after_mutation = _unexpected
        try:
            skipped = app_sync_state.skipped_post_mutation_sync("unchanged")
        finally:
            app_sync_state.sync_after_mutation = original

        assert calls == []
        assert not skipped.failed
        assert skipped.skipped_reason == "unchanged"

    def test_tc_s01_008_skip_outcome_is_successful_without_guidance(self) -> None:
        app_contracts, _app_sync_state, _domain_models = _runtime_modules()

        outcome = app_contracts.PostMutationSyncOutcome.skipped("unchanged")

        assert not outcome.failed
        assert outcome.sync_result is None
        assert outcome.skipped_reason == "unchanged"
        assert outcome.exception_reason is None
        assert outcome.guidance == []

import ast
import sys
from pathlib import Path

import pytest


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import deps as domain_deps
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import status as domain_status
        from spec_dock_runtime.domain import tree as domain_tree
    finally:
        sys.path.pop(0)

    return domain_deps, domain_models, domain_status, domain_tree


def _runtime_active_module():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import active as domain_active
    finally:
        sys.path.pop(0)
    return domain_active


def _runtime_validation_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import tree as domain_tree
        from spec_dock_runtime.domain import validation as domain_validation
    finally:
        sys.path.pop(0)
    return domain_models, domain_tree, domain_validation


def _shared_graph(domain_models, domain_tree):
    seeds = [
        domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Auth Platform",
            slug="auth-platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        domain_models.SpecNodeSeed(
            kind="epic",
            id="epic-local-00001",
            title="JWT Auth",
            slug="jwt-auth",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json"),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00001",
            title="Dependency One",
            slug="dependency-one",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-dependency-one"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-dependency-one/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00002",
            title="Dependency Two",
            slug="dependency-two",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00002-dependency-two"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00002-dependency-two/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=302,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00003",
            title="Target Issue",
            slug="target-issue",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00003-target-issue"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00003-target-issue/.meta.json"
            ),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=303,
        ),
    ]
    return domain_tree.build_graph(seeds)


def _issue_status_snapshot(
    domain_models,
    *,
    issue_id: str,
    effective_status: str,
    source: str,
    github_number: int | None,
    authority: str | None = None,
    stale: bool | None = None,
    last_sync_at: str | None = None,
):
    resolved_authority = authority
    if resolved_authority is None:
        resolved_authority = "local" if github_number is None else "github"
    resolved_stale = stale
    if resolved_stale is None:
        resolved_stale = source == "cache"
    return domain_models.IssueStatusSnapshot(
        issue_id=issue_id,
        authority=resolved_authority,
        effective_status=effective_status,
        source=source,
        stale=resolved_stale,
        last_sync_at=last_sync_at,
        github_number=github_number,
    )


class TestRuntimeDomainS03:
    def test_validate_graph_rejects_local_only_initiative_under_github_mandatory_contract(self) -> None:
        domain_models, domain_tree, domain_validation = _runtime_validation_modules()
        graph = domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-local-00001",
                    title="Platform",
                    slug="platform",
                    path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                )
            ]
        )

        report = domain_validation.validate_graph(graph, repo_root=Path("/repo"))

        assert report.errors
        assert "initiative missing github.issue_number" in report.errors[0]

    def test_validate_graph_rejects_legacy_unscoped_issue_linkage(self) -> None:
        domain_models, domain_tree, domain_validation = _runtime_validation_modules()
        graph = domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00001",
                    title="Platform",
                    slug="platform",
                    path=Path("/repo/spec-dock/initiatives/init-00001-platform"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/.meta.json"),
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=1,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00002",
                    title="Delivery",
                    slug="delivery",
                    path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/.meta.json"),
                    parent_id="init-00001",
                    initiative_id="init-00001",
                    epic_id=None,
                    github_issue_number=2,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00003",
                    title="Current issue",
                    slug="current-issue",
                    path=Path(
                        "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-current-issue"
                    ),
                    meta_path=Path(
                        "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-current-issue/.meta.json"
                    ),
                    parent_id="epic-00002",
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    github_issue_number=3,
                ),
            ]
        )

        report = domain_validation.validate_graph(graph, repo_root=Path("/repo"))

        assert report.errors
        assert "legacy unscoped github linkage" in report.errors[0]

    def test_validate_graph_rejects_partially_scoped_issue_linkage(self) -> None:
        domain_models, domain_tree, domain_validation = _runtime_validation_modules()

        for github_fields in (
            {"github_repo_owner": "example", "github_repo_name": None},
            {"github_repo_owner": None, "github_repo_name": "repo"},
            {"github_repo_owner": "", "github_repo_name": "repo"},
            {"github_repo_owner": "   ", "github_repo_name": "repo"},
            {"github_repo_owner": "example", "github_repo_name": ""},
            {"github_repo_owner": "example", "github_repo_name": "   "},
        ):
            case = f"github_fields={github_fields!r}"
            graph = domain_tree.build_graph(
                [
                    domain_models.SpecNodeSeed(
                        kind="initiative",
                        id="init-00001",
                        title="Platform",
                        slug="platform",
                        path=Path("/repo/spec-dock/initiatives/init-00001-platform"),
                        meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/.meta.json"),
                        parent_id=None,
                        initiative_id=None,
                        epic_id=None,
                        github_issue_number=1,
                        github_repo_owner="example",
                        github_repo_name="repo",
                    ),
                    domain_models.SpecNodeSeed(
                        kind="epic",
                        id="epic-00002",
                        title="Delivery",
                        slug="delivery",
                        path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery"),
                        meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/.meta.json"),
                        parent_id="init-00001",
                        initiative_id="init-00001",
                        epic_id=None,
                        github_issue_number=2,
                        github_repo_owner="example",
                        github_repo_name="repo",
                    ),
                    domain_models.SpecNodeSeed(
                        kind="issue",
                        id="iss-00003",
                        title="Current issue",
                        slug="current-issue",
                        path=Path(
                            "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-current-issue"
                        ),
                        meta_path=Path(
                            "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-current-issue/.meta.json"
                        ),
                        parent_id="epic-00002",
                        initiative_id="init-00001",
                        epic_id="epic-00002",
                        github_issue_number=3,
                        **github_fields,
                    ),
                ]
            )

            report = domain_validation.validate_graph(graph, repo_root=Path("/repo"))

            assert report.errors, case
            assert "invalid github linkage" in report.errors[0], case
            assert "github.repo_owner and github.repo_name must be provided together" in report.errors[0], case

    def test_validate_graph_relaxed_mode_still_rejects_partially_scoped_issue_linkage(self) -> None:
        domain_models, domain_tree, domain_validation = _runtime_validation_modules()

        for github_fields in (
            {"github_repo_owner": "example", "github_repo_name": None},
            {"github_repo_owner": "   ", "github_repo_name": "repo"},
        ):
            case = f"github_fields={github_fields!r}"
            graph = domain_tree.build_graph(
                [
                    domain_models.SpecNodeSeed(
                        kind="initiative",
                        id="init-00001",
                        title="Platform",
                        slug="platform",
                        path=Path("/repo/spec-dock/initiatives/init-00001-platform"),
                        meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/.meta.json"),
                        parent_id=None,
                        initiative_id=None,
                        epic_id=None,
                        github_issue_number=1,
                        github_repo_owner="example",
                        github_repo_name="repo",
                    ),
                    domain_models.SpecNodeSeed(
                        kind="epic",
                        id="epic-00002",
                        title="Delivery",
                        slug="delivery",
                        path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery"),
                        meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/.meta.json"),
                        parent_id="init-00001",
                        initiative_id="init-00001",
                        epic_id=None,
                        github_issue_number=2,
                        github_repo_owner="example",
                        github_repo_name="repo",
                    ),
                    domain_models.SpecNodeSeed(
                        kind="issue",
                        id="iss-00003",
                        title="Current issue",
                        slug="current-issue",
                        path=Path(
                            "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-current-issue"
                        ),
                        meta_path=Path(
                            "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-current-issue/.meta.json"
                        ),
                        parent_id="epic-00002",
                        initiative_id="init-00001",
                        epic_id="epic-00002",
                        github_issue_number=3,
                        **github_fields,
                    ),
                ]
            )

            report = domain_validation.validate_graph(
                graph,
                repo_root=Path("/repo"),
                enforce_github_mandatory_linkage=False,
            )

            assert report.errors, case
            assert "invalid github linkage" in report.errors[0], case
            assert "github.repo_owner and github.repo_name must be provided together" in report.errors[0], case

    def test_validate_graph_allows_explicit_foreign_issue_linkage(self) -> None:
        domain_models, domain_tree, domain_validation = _runtime_validation_modules()
        graph = domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-00001",
                    title="Platform",
                    slug="platform",
                    path=Path("/repo/spec-dock/initiatives/init-00001-platform"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/.meta.json"),
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=1,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-00002",
                    title="Delivery",
                    slug="delivery",
                    path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/.meta.json"),
                    parent_id="init-00001",
                    initiative_id="init-00001",
                    epic_id=None,
                    github_issue_number=2,
                    github_repo_owner="example",
                    github_repo_name="repo",
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-00123",
                    title="Imported issue",
                    slug="imported-issue",
                    path=Path(
                        "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00123-imported-issue"
                    ),
                    meta_path=Path(
                        "/repo/spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00123-imported-issue/.meta.json"
                    ),
                    parent_id="epic-00002",
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    github_issue_number=123,
                    github_repo_owner="other",
                    github_repo_name="repo",
                ),
            ]
        )

        report = domain_validation.validate_graph(graph, repo_root=Path("/repo"))

        assert report.errors == []

    def _branch_inference_overlap_graph(self):
        _domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()
        seeds = [
            domain_models.SpecNodeSeed(
                kind="initiative",
                id="init-local-00001",
                title="Platform",
                slug="platform",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
                meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="epic",
                id="epic-local-00001",
                title="Delivery",
                slug="delivery",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"
                ),
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00001",
                title="Current issue",
                slug="current-issue",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00002",
                title="Foreign issue",
                slug="foreign-issue",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-foreign-issue"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-foreign-issue/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
        ]
        return domain_tree.build_graph(seeds)

    def _branch_inference_foreign_only_graph(self):
        _domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()
        seeds = [
            domain_models.SpecNodeSeed(
                kind="initiative",
                id="init-local-00001",
                title="Platform",
                slug="platform",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
                meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="epic",
                id="epic-local-00001",
                title="Delivery",
                slug="delivery",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"
                ),
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00001",
                title="Foreign issue",
                slug="foreign-issue",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-foreign-issue"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-foreign-issue/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
        ]
        return domain_tree.build_graph(seeds)

    def _branch_inference_scoped_ambiguity_graph(self):
        _domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()
        seeds = [
            domain_models.SpecNodeSeed(
                kind="initiative",
                id="init-local-00001",
                title="Platform",
                slug="platform",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
                meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="epic",
                id="epic-local-00001",
                title="Delivery",
                slug="delivery",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"
                ),
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00001",
                title="Current issue a",
                slug="current-issue-a",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue-a"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue-a/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00002",
                title="Current issue b",
                slug="current-issue-b",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-current-issue-b"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-current-issue-b/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="current",
                github_repo_name="repo",
            ),
            domain_models.SpecNodeSeed(
                kind="issue",
                id="iss-local-00003",
                title="Foreign issue",
                slug="foreign-issue",
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00003-foreign-issue"
                ),
                meta_path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00003-foreign-issue/.meta.json"
                ),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
            ),
        ]
        return domain_tree.build_graph(seeds)

    def test_infer_active_node_from_branch_prefers_current_repo_under_numeric_overlap(self) -> None:
        domain_active = _runtime_active_module()
        graph = self._branch_inference_overlap_graph()

        node, reason = domain_active.infer_active_node_from_branch(
            graph,
            branch="123-fix-login",
            current_repo_slug="current/repo",
        )

        assert node is not None
        assert node is not None
        assert node.id == "iss-local-00001"
        assert reason == "matched github.issue_number=123 from branch"

    def test_infer_active_node_from_branch_keeps_fail_closed_when_current_repo_unknown(self) -> None:
        domain_active = _runtime_active_module()
        graph = self._branch_inference_overlap_graph()

        node, reason = domain_active.infer_active_node_from_branch(
            graph,
            branch="issue-123",
            current_repo_slug=None,
        )

        assert node is None
        assert reason == "ambiguous github issue numbers [123]: issue:iss-local-00001, issue:iss-local-00002"

    def test_infer_active_node_from_branch_keeps_explicit_id_priority_over_numeric_fallback(self) -> None:
        domain_active = _runtime_active_module()
        graph = self._branch_inference_overlap_graph()

        node, reason = domain_active.infer_active_node_from_branch(
            graph,
            branch="feature/iss-local-00002-issue-123",
            current_repo_slug="current/repo",
        )

        assert node is not None
        assert node is not None
        assert node.id == "iss-local-00002"
        assert reason == "matched id in branch: iss-local-00002"

    def test_infer_active_node_from_branch_fails_closed_on_foreign_only_numeric_match_with_known_scope(self) -> None:
        domain_active = _runtime_active_module()
        graph = self._branch_inference_foreign_only_graph()

        node, reason = domain_active.infer_active_node_from_branch(
            graph,
            branch="123-fix-login",
            current_repo_slug="current/repo",
        )

        assert node is None
        assert reason == (
            "no current-repo matches for github issue numbers [123] "
            "in scope (current/repo); refusing foreign fallback: issue:iss-local-00001"
        )

    def test_infer_active_node_from_branch_fails_closed_on_scoped_numeric_ambiguity(self) -> None:
        domain_active = _runtime_active_module()
        graph = self._branch_inference_scoped_ambiguity_graph()

        node, reason = domain_active.infer_active_node_from_branch(
            graph,
            branch="issue-123",
            current_repo_slug="current/repo",
        )

        assert node is None
        assert reason == (
            "ambiguous github issue numbers [123] in current repo scope (current/repo): "
            "issue:iss-local-00001, issue:iss-local-00002"
        )

    def test_resolve_issue_statuses_selects_source(self) -> None:
        _domain_deps, domain_models, domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        snapshots = [
            domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Dependency One",
                labels=[],
                updated_at="2026-01-01T00:00:00Z",
                url="https://example.invalid/301",
            )
        ]
        cached = {
            "iss-local-00001": "open",
            "iss-local-00002": "done",
            "iss-local-00003": "open",
        }

        github_statuses = domain_status.resolve_issue_statuses(
            graph,
            github_enabled=True,
            issue_snapshots=snapshots,
            cached_issue_status_by_id=cached,
        )
        assert github_statuses["iss-local-00001"].authority == "github"
        assert github_statuses["iss-local-00001"].effective_status == "done"
        assert github_statuses["iss-local-00001"].source == "github"
        assert not github_statuses["iss-local-00001"].stale
        assert github_statuses["iss-local-00001"].last_sync_at == "2026-01-01T00:00:00Z"
        assert github_statuses["iss-local-00002"].effective_status == "unknown"
        assert github_statuses["iss-local-00002"].source == "unknown"
        assert github_statuses["iss-local-00002"].stale

        cache_statuses = domain_status.resolve_issue_statuses(
            graph,
            github_enabled=False,
            issue_snapshots=snapshots,
            cached_issue_status_by_id=cached,
        )
        assert cache_statuses["iss-local-00001"].authority == "github"
        assert cache_statuses["iss-local-00001"].effective_status == "open"
        assert cache_statuses["iss-local-00001"].source == "cache"
        assert cache_statuses["iss-local-00001"].stale
        assert cache_statuses["iss-local-00002"].effective_status == "done"
        assert cache_statuses["iss-local-00002"].source == "cache"
        assert cache_statuses["iss-local-00002"].stale

    def test_build_progress_map_aggregates_counts(self) -> None:
        _domain_deps, domain_models, domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00001",
                effective_status="done",
                source="github",
                stale=False,
                github_number=301,
            ),
            "iss-local-00002": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00002",
                effective_status="open",
                source="github",
                stale=False,
                github_number=302,
            ),
            "iss-local-00003": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00003",
                effective_status="unknown",
                source="unknown",
                stale=True,
                github_number=303,
            ),
        }

        progress = domain_status.build_progress_map(graph, issue_statuses)
        assert progress.by_node_id["epic-local-00001"] == {"total": 3, "done": 1, "open": 1, "unknown": 1}
        assert progress.by_node_id["init-local-00001"] == {"total": 3, "done": 1, "open": 1, "unknown": 1}
        assert progress.counts == {"total": 3, "done": 1, "open": 1, "unknown": 1}

    def test_resolve_issue_statuses_local_only_is_deterministic_open(self) -> None:
        _domain_deps, domain_models, domain_status, domain_tree = _runtime_modules()
        graph = domain_tree.build_graph(
            [
                domain_models.SpecNodeSeed(
                    kind="initiative",
                    id="init-local-00001",
                    title="init",
                    slug="init",
                    path=Path("/repo/spec-dock/initiatives/init-local-00001-init"),
                    meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-init/.meta.json"),
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                domain_models.SpecNodeSeed(
                    kind="epic",
                    id="epic-local-00001",
                    title="epic",
                    slug="epic",
                    path=Path("/repo/spec-dock/initiatives/init-local-00001-init/epics/epic-local-00001-epic"),
                    meta_path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-init/epics/epic-local-00001-epic/.meta.json"
                    ),
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
                domain_models.SpecNodeSeed(
                    kind="issue",
                    id="iss-local-00001",
                    title="issue",
                    slug="issue",
                    path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-init/epics/epic-local-00001-epic/issues/iss-local-00001-issue"
                    ),
                    meta_path=Path(
                        "/repo/spec-dock/initiatives/init-local-00001-init/epics/epic-local-00001-epic/issues/iss-local-00001-issue/.meta.json"
                    ),
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=None,
                ),
            ]
        )

        statuses = domain_status.resolve_issue_statuses(
            graph,
            github_enabled=False,
            issue_snapshots=[],
            cached_issue_status_by_id={},
        )
        issue = statuses["iss-local-00001"]
        assert issue.authority == "local"
        assert issue.effective_status == "open"
        assert issue.source == "local"
        assert not issue.stale
        assert issue.last_sync_at is None

    def test_build_effective_deps_map_merges_parent_dependencies(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_depends_on_map = {
            "init-local-00001": ["iss-local-00002"],
            "epic-local-00001": ["iss-local-00001"],
            "iss-local-00003": ["iss-local-00001"],
        }

        effective = domain_deps.build_effective_deps_map(graph, issue_depends_on_map)
        assert effective["iss-local-00003"] == ["iss-local-00001", "iss-local-00002"]

    def test_evaluate_readiness_uses_explicit_issue_depends_on_map(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00001",
                effective_status="open",
                source="cache",
                github_number=301,
            ),
            "iss-local-00002": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00002",
                effective_status="open",
                source="cache",
                github_number=302,
            ),
            "iss-local-00003": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00003",
                effective_status="open",
                source="cache",
                github_number=303,
            ),
        }
        issue_depends_on_map = {
            "iss-local-00001": ["iss-local-00002"],
            "iss-local-00002": [],
            "iss-local-00003": ["iss-local-00001"],
        }

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
        )
        assert not result.ready
        assert result.guard_reason == "blocked"
        assert result.blockers == ["iss-local-00001", "iss-local-00002"]
        assert result.blockers_top == ["iss-local-00001", "iss-local-00002"]
        assert result.closure == ["iss-local-00001", "iss-local-00002"]

    def test_evaluate_readiness_reports_unknown_guard_reason(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00001",
                effective_status="open",
                source="cache",
                github_number=301,
            ),
            "iss-local-00002": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00002",
                effective_status="unknown",
                source="cache",
                github_number=302,
            ),
            "iss-local-00003": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00003",
                effective_status="open",
                source="cache",
                github_number=303,
            ),
        }
        issue_depends_on_map = {
            "iss-local-00001": ["iss-local-00002"],
            "iss-local-00002": [],
            "iss-local-00003": ["iss-local-00001"],
        }

        result = domain_deps.evaluate_readiness(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
        )
        assert not result.ready
        assert result.guard_reason == "unknown"

    def test_inspect_target_deps_active_decoration_only(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)
        issue_statuses = {
            "iss-local-00001": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00001",
                effective_status="open",
                source="cache",
                github_number=301,
            ),
            "iss-local-00002": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00002",
                effective_status="closed",
                source="cache",
                github_number=302,
            ),
            "iss-local-00003": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00003",
                effective_status="open",
                source="cache",
                github_number=303,
            ),
        }
        issue_depends_on_map = {
            "iss-local-00001": ["iss-local-00002"],
            "iss-local-00002": [],
            "iss-local-00003": ["iss-local-00001"],
        }

        without_active = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
            active_issue_id=None,
        )
        with_active = domain_deps.inspect_target_deps(
            graph,
            issue_depends_on_map,
            domain_models.NodeId("iss-local-00003"),
            issue_statuses,
            active_issue_id="iss-local-00001",
        )

        assert without_active.evaluation == with_active.evaluation
        assert without_active.node_states["iss-local-00001"].status != with_active.node_states["iss-local-00001"].status
        assert with_active.node_states["iss-local-00001"].status == "doing"

    def test_build_deps_state_and_cycle_validation(self) -> None:
        domain_deps, domain_models, _domain_status, domain_tree = _runtime_modules()

        graph = _shared_graph(domain_models, domain_tree)

        with pytest.raises(RuntimeError):
            domain_deps.validate_deps_cycles(
                {
                    "iss-local-00001": ["iss-local-00002"],
                    "iss-local-00002": ["iss-local-00001"],
                }
            )

        issue_statuses = {
            "iss-local-00001": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00001",
                effective_status="open",
                source="cache",
                github_number=301,
            ),
            "iss-local-00002": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00002",
                effective_status="done",
                source="cache",
                github_number=302,
            ),
            "iss-local-00003": _issue_status_snapshot(
                domain_models,
                issue_id="iss-local-00003",
                effective_status="open",
                source="cache",
                github_number=303,
            ),
        }
        state = domain_deps.build_deps_state(
            graph,
            {
                "iss-local-00001": ["iss-local-00002"],
                "iss-local-00002": [],
                "iss-local-00003": ["iss-local-00001"],
            },
            issue_statuses,
            domain_models.ActiveSelection(
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                issue_id="iss-local-00001",
            ),
            warnings=["gh_index_incomplete"],
        )
        assert state.warnings == ["gh_index_incomplete"]
        by_id = {node.node_id: node for node in state.nodes}
        assert by_id["iss-local-00001"].status == "doing"
        assert by_id["iss-local-00001"].ready
        assert by_id["iss-local-00002"].status == "done"
        assert by_id["iss-local-00002"].ready
        assert by_id["iss-local-00003"].status == "blocked"
        assert not by_id["iss-local-00003"].ready

    def test_domain_modules_have_no_shell_io_imports(self) -> None:
        domain_deps, _domain_models, domain_status, _domain_tree = _runtime_modules()
        module_paths = [
            domain_status.__file__,
            domain_deps.__file__,
            domain_status.__file__.replace("status.py", "active.py"),
        ]
        forbidden_import_roots = {
            "argparse",
            "json",
            "os",
            "shutil",
            "subprocess",
            "sys",
        }

        for module_path in module_paths:
            source = Path(module_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".", 1)[0]
                        assert root not in forbidden_import_roots, f"Forbidden import '{root}' in {module_path}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        continue
                    root = node.module.split(".", 1)[0]
                    assert root not in forbidden_import_roots, f"Forbidden import '{root}' in {module_path}"

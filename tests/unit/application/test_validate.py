from pathlib import Path
import sys
import tempfile


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            ports as app_ports,
            validate_tree as app_validate_tree,
        )
        from spec_dock_runtime.domain import (
            models as domain_models,
            tree as domain_tree,
            validation as domain_validation,
        )
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return (
        app_contracts,
        app_ports,
        app_validate_tree,
        domain_models,
        domain_tree,
        domain_validation,
        infra_contracts,
    )


class _StubNodeReader:
    def __init__(self, records):
        self.records = list(records)

    def load_node_records(self):
        return list(self.records)


class TestValidateApplication:
    def test_discussion_doc_parser_catalog_handles_hyphenated_and_existing_types(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.domain import discussion_docs
        finally:
            sys.path.pop(0)

        parsed = discussion_docs.parse_timestamp_discussion_doc_filename(
            "20260329t123456z-draft-requirement-kickoff.md"
        )
        assert parsed is not None
        assert parsed.doc_type == "draft-requirement"
        assert parsed.doc_id == "20260329t123456z-draft-requirement"

        suffixed = discussion_docs.parse_timestamp_discussion_doc_filename("20260329t123456z-09-draft-plan-plan.md")
        assert suffixed is not None
        assert suffixed.doc_type == "draft-plan"
        assert suffixed.doc_id == "20260329t123456z-09-draft-plan"

        note = discussion_docs.parse_timestamp_discussion_doc_filename("20260329t123457z-note-current.md")
        assert note is not None
        assert note.doc_id == "20260329t123457z-note"
        assert not discussion_docs.is_creatable_discussion_doc_type("note")
        assert discussion_docs.is_retired_discussion_doc_type("note")

        legacy = discussion_docs.parse_legacy_discussion_doc_filename("001-research-legacy-spike.md")
        assert legacy is not None
        assert legacy.doc_type == "research"
        assert discussion_docs.parse_legacy_discussion_doc_filename("001-scratch-legacy-capture.md") is None

    def test_discussion_doc_malformed_candidates_remain_fail_closed(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.domain import discussion_docs
        finally:
            sys.path.pop(0)

        for name in (
            "draft-requirement-kickoff.md",
            "20260329t123456z-00-draft-plan-bad-suffix.md",
            "20260329t123456z-draft-design.md",
            "001-scratch-legacy-capture.md",
            "20260329x-draft-requirement-kickoff.md",
            "pr-repair-batch.md",
        ):
            assert discussion_docs.is_malformed_discussion_doc_candidate(Path(name)), name

    def _records(self, infra_contracts, repo_root: Path):
        init_dir = repo_root / "spec-dock" / "initiatives" / "init-00001-platform"
        epic_dir = init_dir / "epics" / "epic-00002-delivery"
        issue_dir = epic_dir / "issues" / "iss-00003-target"
        return [
            infra_contracts.StoredMetaRecord(
                kind="initiative",
                id="init-00001",
                title="Platform",
                slug="platform",
                path=init_dir.as_posix(),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=1,
                meta_path=(init_dir / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="epic",
                id="epic-00002",
                title="Delivery",
                slug="delivery",
                path=epic_dir.as_posix(),
                parent_id="init-00001",
                initiative_id="init-00001",
                epic_id=None,
                github_issue_number=2,
                meta_path=(epic_dir / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
            infra_contracts.StoredMetaRecord(
                kind="issue",
                id="iss-00003",
                title="Target",
                slug="target",
                path=issue_dir.as_posix(),
                parent_id="epic-00002",
                initiative_id="init-00001",
                epic_id="epic-00002",
                github_issue_number=3,
                meta_path=(issue_dir / ".meta.json").as_posix(),
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ]

    def _materialize_artifacts(self, records, *, omit: tuple[str, str] | None = None) -> None:
        for record in records:
            node_dir = Path(record.path)
            node_dir.mkdir(parents=True, exist_ok=True)
            for name in (".meta.json", "requirement.md", "design.md", "plan.md", "report.md"):
                if omit == (record.id, name):
                    continue
                (node_dir / name).write_text(f"{record.id}:{name}\n", encoding="utf-8")

    def test_validate_tree_reports_missing_required_artifact_docs_without_cli(self) -> None:
        (
            app_contracts,
            app_ports,
            app_validate_tree,
            _domain_models,
            _domain_tree,
            _domain_validation,
            infra_contracts,
        ) = _runtime_modules()

        required_docs = ("requirement.md", "design.md", "plan.md", "report.md")
        for node_kind in ("initiative", "epic", "issue"):
            for artifact_name in required_docs:
                case = f"node_kind={node_kind} artifact_name={artifact_name}"
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp) / "repo"
                    records = self._records(infra_contracts, repo_root)
                    target = next(record for record in records if record.kind == node_kind)
                    self._materialize_artifacts(records, omit=(target.id, artifact_name))

                    result = app_validate_tree.validate_tree(
                        app_contracts.ValidateTreeRequest(),
                        app_ports.Ports(node_reader=_StubNodeReader(records), repo_root=repo_root),
                    )

                assert result.checked_node_count == 3, case
                assert result.report.errors, case
                assert "Missing required artifact" in result.report.errors[0], case
                assert f"kind={node_kind} id={target.id}" in result.report.errors[0], case
                assert artifact_name in result.report.errors[0], case
                assert (Path(target.path) / artifact_name).relative_to(repo_root).as_posix() in result.report.errors[
                    0
                ], case

    def test_validate_tree_reports_missing_required_meta_without_cli(self) -> None:
        (
            app_contracts,
            app_ports,
            app_validate_tree,
            _domain_models,
            _domain_tree,
            _domain_validation,
            infra_contracts,
        ) = _runtime_modules()

        for node_kind in ("initiative", "epic", "issue"):
            case = f"node_kind={node_kind} artifact_name=.meta.json"
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp) / "repo"
                records = self._records(infra_contracts, repo_root)
                target = next(record for record in records if record.kind == node_kind)
                self._materialize_artifacts(records, omit=(target.id, ".meta.json"))

                result = app_validate_tree.validate_tree(
                    app_contracts.ValidateTreeRequest(),
                    app_ports.Ports(node_reader=_StubNodeReader(records), repo_root=repo_root),
                )

            assert result.checked_node_count == 3, case
            assert result.report.errors, case
            assert "Missing required artifact" in result.report.errors[0], case
            assert f"kind={node_kind} id={target.id}" in result.report.errors[0], case
            assert ".meta.json" in result.report.errors[0], case
            assert Path(target.meta_path).relative_to(repo_root).as_posix() in result.report.errors[0], case

    def test_validate_graph_reports_linkage_and_parent_diagnostics_without_cli(self) -> None:
        (
            _app_contracts,
            _app_ports,
            _app_validate_tree,
            domain_models,
            domain_tree,
            domain_validation,
            _infra_contracts,
        ) = _runtime_modules()
        root = Path("/repo/spec-dock/initiatives/init-00001-platform")

        graph = domain_tree.build_graph([
            domain_models.SpecNodeSeed(
                kind="initiative",
                id="init-00001",
                title="Platform",
                slug="platform",
                path=root,
                meta_path=root / ".meta.json",
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
                path=root / "epics" / "epic-00002-delivery",
                meta_path=root / "epics" / "epic-00002-delivery" / ".meta.json",
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
                title="Target",
                slug="target",
                path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00003-target",
                meta_path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00003-target" / ".meta.json",
                parent_id="epic-99999",
                initiative_id="init-00001",
                epic_id="epic-00002",
                github_issue_number=3,
                github_repo_owner="example",
                github_repo_name="repo",
            ),
        ])
        broken_parent = domain_validation.validate_graph(graph, repo_root=Path("/repo"))
        assert broken_parent.errors
        assert "issue parent_id mismatch" in broken_parent.errors[0]

        unscoped = domain_tree.build_graph([
            domain_models.SpecNodeSeed(
                kind="initiative",
                id="init-00001",
                title="Platform",
                slug="platform",
                path=root,
                meta_path=root / ".meta.json",
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
                path=root / "epics" / "epic-00002-delivery",
                meta_path=root / "epics" / "epic-00002-delivery" / ".meta.json",
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
                title="Target",
                slug="target",
                path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00003-target",
                meta_path=root / "epics" / "epic-00002-delivery" / "issues" / "iss-00003-target" / ".meta.json",
                parent_id="epic-00002",
                initiative_id="init-00001",
                epic_id="epic-00002",
                github_issue_number=3,
            ),
        ])
        legacy = domain_validation.validate_graph(unscoped, repo_root=Path("/repo"))
        assert legacy.errors
        assert "legacy unscoped github linkage" in legacy.errors[0]

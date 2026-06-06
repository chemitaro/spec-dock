import sys
import tempfile
import unittest
from pathlib import Path


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
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.application import validate_tree as app_validate_tree
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.domain import tree as domain_tree
        from spec_dock_runtime.domain import validation as domain_validation
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


class TestValidateApplication(unittest.TestCase):
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
                with self.subTest(kind=node_kind, artifact=artifact_name):
                    with tempfile.TemporaryDirectory() as tmp:
                        repo_root = Path(tmp) / "repo"
                        records = self._records(infra_contracts, repo_root)
                        target = next(record for record in records if record.kind == node_kind)
                        self._materialize_artifacts(records, omit=(target.id, artifact_name))

                        result = app_validate_tree.validate_tree(
                            app_contracts.ValidateTreeRequest(),
                            app_ports.Ports(node_reader=_StubNodeReader(records), repo_root=repo_root),
                        )

                    self.assertEqual(result.checked_node_count, 3)
                    self.assertTrue(result.report.errors)
                    self.assertIn("Missing required artifact", result.report.errors[0])
                    self.assertIn(f"kind={node_kind} id={target.id}", result.report.errors[0])
                    self.assertIn(artifact_name, result.report.errors[0])
                    self.assertIn(
                        (Path(target.path) / artifact_name).relative_to(repo_root).as_posix(),
                        result.report.errors[0],
                    )

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
            with self.subTest(kind=node_kind):
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp) / "repo"
                    records = self._records(infra_contracts, repo_root)
                    target = next(record for record in records if record.kind == node_kind)
                    self._materialize_artifacts(records, omit=(target.id, ".meta.json"))

                    result = app_validate_tree.validate_tree(
                        app_contracts.ValidateTreeRequest(),
                        app_ports.Ports(node_reader=_StubNodeReader(records), repo_root=repo_root),
                    )

                self.assertEqual(result.checked_node_count, 3)
                self.assertTrue(result.report.errors)
                self.assertIn("Missing required artifact", result.report.errors[0])
                self.assertIn(f"kind={node_kind} id={target.id}", result.report.errors[0])
                self.assertIn(".meta.json", result.report.errors[0])
                self.assertIn(Path(target.meta_path).relative_to(repo_root).as_posix(), result.report.errors[0])

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

        graph = domain_tree.build_graph(
            [
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
            ]
        )
        broken_parent = domain_validation.validate_graph(graph, repo_root=Path("/repo"))
        self.assertTrue(broken_parent.errors)
        self.assertIn("issue parent_id mismatch", broken_parent.errors[0])

        unscoped = domain_tree.build_graph(
            [
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
            ]
        )
        legacy = domain_validation.validate_graph(unscoped, repo_root=Path("/repo"))
        self.assertTrue(legacy.errors)
        self.assertIn("legacy unscoped github linkage", legacy.errors[0])

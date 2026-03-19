import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    _EXPECTED_MANAGED_SKILL_NAMES,
    _expected_spec_dock_version,
    main,
)


class TestInitUpdate(CliRuntimeHarness):
    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", str(target)])
            self.assertEqual(exit_code, 0)

            self._assert_version_file(target)

            # Repo-root shortcut (best-effort; only assert when symlinks are supported).
            if self._can_create_symlink(target):
                self.assertTrue((target / "spec").is_symlink(), "repo-root shortcut missing: spec")

            self.assertTrue((target / "spec-dock" / "docs").is_dir())
            self.assertTrue((target / "spec-dock" / "templates").is_dir())
            self.assertTrue((target / "spec-dock" / "scripts").is_dir())
            self.assertTrue((target / "spec-dock" / "system").is_dir())
            self.assertTrue((target / "spec-dock" / "initiatives").is_dir())
            self.assertTrue((target / "spec-dock" / "active").is_dir())
            self.assertTrue((target / "spec-dock" / ".agent").is_dir())
            self.assertTrue((target / "spec-dock" / ".gitignore").is_file())
            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".agent/", gitignore)
            self.assertIn("active/", gitignore)

            docs_dir = target / "spec-dock" / "docs"
            self.assertTrue((docs_dir / "README.md").is_file())
            self.assertTrue((docs_dir / "guide.md").is_file())
            self.assertTrue((docs_dir / "workflow_initiative.md").is_file())
            self.assertTrue((docs_dir / "workflow_epic.md").is_file())
            self.assertTrue((docs_dir / "workflow_issue.md").is_file())
            self.assertTrue((docs_dir / "workflow_adr.md").is_file())
            self.assertTrue((docs_dir / "phase_requirement.md").is_file())
            self.assertTrue((docs_dir / "phase_design.md").is_file())
            self.assertTrue((docs_dir / "phase_plan.md").is_file())
            self.assertTrue((docs_dir / "reference_github.md").is_file())
            self.assertTrue((docs_dir / "reference_naming.md").is_file())
            self.assertTrue((docs_dir / "reference_sync.md").is_file())

            docs_readme = (docs_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("spec-driven-tdd-workflow", docs_readme)
            self.assertIn("spec-dock-initiative-planning", docs_readme)
            self.assertIn("spec-dock-epic-planning", docs_readme)
            self.assertIn("spec-dock-issue-execution", docs_readme)
            self.assertIn("spec-dock-adr-facilitation", docs_readme)
            self.assertIn("reference レイヤ", docs_readme)
            self.assertIn("[phase_requirement.md](phase_requirement.md)", docs_readme)
            self.assertIn("[phase_design.md](phase_design.md)", docs_readme)
            self.assertIn("[phase_plan.md](phase_plan.md)", docs_readme)

            guide_text = (docs_dir / "guide.md").read_text(encoding="utf-8")
            self.assertIn("phase playbook（共通の作り方）", guide_text)
            self.assertIn("[phase_requirement.md](phase_requirement.md)", guide_text)
            self.assertIn("[phase_design.md](phase_design.md)", guide_text)
            self.assertIn("[phase_plan.md](phase_plan.md)", guide_text)

            workflow_initiative = (docs_dir / "workflow_initiative.md").read_text(encoding="utf-8")
            workflow_epic = (docs_dir / "workflow_epic.md").read_text(encoding="utf-8")
            workflow_issue = (docs_dir / "workflow_issue.md").read_text(encoding="utf-8")
            workflow_adr = (docs_dir / "workflow_adr.md").read_text(encoding="utf-8")
            self.assertIn("spec-dock-initiative-planning", workflow_initiative)
            self.assertIn("spec-dock-epic-planning", workflow_epic)
            self.assertIn("spec-dock-issue-execution", workflow_issue)
            self.assertIn("spec-dock-adr-facilitation", workflow_adr)
            self.assertIn("plan upfront approval", workflow_issue)
            self.assertIn("step result approval", workflow_issue)
            self.assertIn("docs impact", workflow_issue)
            self.assertIn("final diff review quality gate", workflow_issue)
            self.assertIn("reviewer approval", workflow_issue)

            # v2 does not ship legacy docs/old/ (keep the published docs minimal).
            self.assertFalse((docs_dir / "old").exists())

            # Runtime script exists; legacy close scripts must not be present.
            scripts_dir = target / "spec-dock" / "scripts"
            self.assertTrue((scripts_dir / "spec-dock").is_file())
            self.assertEqual(list(scripts_dir.glob("spec-dock-close*.sh")), [])

            # Placeholders exist (active pointers must never be broken).
            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertTrue((placeholder_root / "initiative" / "README.md").is_file())
            self.assertTrue((placeholder_root / "epic" / "README.md").is_file())
            self.assertTrue((placeholder_root / "issue" / "README.md").is_file())
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )
            context_pack_text = (target / "spec-dock" / "active" / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)

            # Legacy (v1) templates should not be installed.
            templates_dir = target / "spec-dock" / "templates"
            for legacy in ("requirement.md", "design.md", "plan.md", "report.md"):
                self.assertFalse((templates_dir / legacy).exists(), f"legacy template leaked: {legacy}")
            self.assertEqual(list(templates_dir.rglob("current")), [])
            self.assertEqual(list(templates_dir.rglob("completed")), [])

            # Issue templates should be sufficiently detailed (regression guard).
            initiative_templates_dir = templates_dir / "initiative"
            epic_templates_dir = templates_dir / "epic"
            issue_templates_dir = templates_dir / "issue"

            req_text = (issue_templates_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertIn("## 対象ユーザー / 利用シナリオ", req_text)
            self.assertIn("## 用語（ドメイン語彙）", req_text)
            for scope_templates in (
                initiative_templates_dir,
                epic_templates_dir,
                issue_templates_dir,
            ):
                self.assertTrue((scope_templates / "discussions" / "rules.md").is_file())
                self.assertFalse((scope_templates / "adrs").exists())
                self.assertFalse((scope_templates / "artifacts").exists())
                self.assertEqual(list((scope_templates / "discussions").glob("new-*")), [])

            discussions_templates_dir = templates_dir / "discussions"
            self.assertTrue((discussions_templates_dir / "adr.md").is_file())
            self.assertTrue((discussions_templates_dir / "note.md").is_file())
            self.assertTrue((discussions_templates_dir / "disc.md").is_file())
            self.assertTrue((discussions_templates_dir / "research.md").is_file())
            self.assertEqual(list(initiative_templates_dir.rglob("README.md")), [])
            self.assertEqual(list(epic_templates_dir.rglob("README.md")), [])
            self.assertEqual(list(issue_templates_dir.rglob("README.md")), [])

            design_text = (issue_templates_dir / "design.md").read_text(encoding="utf-8")
            # UML is embedded as small subsections (not a single block at the end).
            self.assertIn("```plantuml", design_text)
            self.assertIn("### UML（", design_text)

            plan_text = (issue_templates_dir / "plan.md").read_text(encoding="utf-8")
            self.assertIn("#### update_plan（着手時に登録）", plan_text)
            self.assertIn("./spec-dock/active/issue/report.md", plan_text)
            self.assertIn("## 実行ルール（全ステップ共通）", plan_text)
            self.assertIn("Red → Green → Refactor → review → fix → re-review → report → commit/no-op", plan_text)
            self.assertIn("S90 — docs impact resolution / docs refresh", plan_text)
            self.assertIn("S99 — final diff review quality gate", plan_text)
            self.assertIn("`git diff <base>...HEAD`", plan_text)
            self.assertIn("reviewer verdict", plan_text)

            report_text = (issue_templates_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## 遭遇した問題と解決", report_text)

            skills_root = target / ".agents" / "skills"
            self._assert_managed_skills_installed(target)

            skill_text = (skills_root / "spec-driven-tdd-workflow" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("`discussions/`", skill_text)
            self.assertIn("./spec-dock/scripts/spec-dock new doc adr --issue", skill_text)
            self.assertNotIn("adrs/new-adr", skill_text)
            self.assertFalse(
                (target / ".github" / "workflows" / "spec-dock-close.yml").exists()
            )

    def test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/templates/initiative/discussions/rules.md",
                "spec-dock/templates/epic/discussions/rules.md",
                "spec-dock/templates/issue/discussions/rules.md",
                "spec-dock/docs/reference_naming.md",
                "spec-dock/docs/workflow_adr.md",
                "spec-dock/docs/workflow_issue.md",
                "spec-dock/docs/workflow_epic.md",
                "spec-dock/docs/workflow_initiative.md",
                "spec-dock/docs/phase_requirement.md",
                "spec-dock/docs/phase_design.md",
                "spec-dock/docs/phase_plan.md",
                "spec-dock/docs/README.md",
                "spec-dock/docs/guide.md",
                "spec-dock/scripts/README.md",
                ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ]
            text_map = self._read_text_map(target, guidance_paths)
            self._assert_discussion_guidance_contract(text_map)

    def test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._write_text_force(
                target / "spec-dock" / "docs" / "workflow_adr.md",
                "./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title \"...\"\n",
            )
            self._write_text_force(
                target / "spec-dock" / "templates" / "initiative" / "discussions" / "rules.md",
                "legacy naming: <type>-00001-<slug>.md\n",
            )
            self._write_text_force(
                target / "spec-dock" / "scripts" / "README.md",
                "legacy example: new adr --issue ...\n",
            )
            self._write_text_force(
                target / ".agents" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md",
                "legacy skill example: new adr --issue ...\n",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/templates/initiative/discussions/rules.md",
                "spec-dock/templates/epic/discussions/rules.md",
                "spec-dock/templates/issue/discussions/rules.md",
                "spec-dock/docs/reference_naming.md",
                "spec-dock/docs/workflow_adr.md",
                "spec-dock/docs/workflow_issue.md",
                "spec-dock/docs/workflow_epic.md",
                "spec-dock/docs/workflow_initiative.md",
                "spec-dock/docs/phase_requirement.md",
                "spec-dock/docs/phase_design.md",
                "spec-dock/docs/phase_plan.md",
                "spec-dock/docs/README.md",
                "spec-dock/docs/guide.md",
                "spec-dock/scripts/README.md",
                ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ]
            text_map = self._read_text_map(target, guidance_paths)
            self._assert_discussion_guidance_contract(text_map)

    def test_current_guidance_documents_match_discussion_numbering_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        guidance_paths = [
            "src/spec_dock/assets/spec_dock/templates/README.md",
            "src/spec_dock/assets/spec_dock/templates/initiative/discussions/rules.md",
            "src/spec_dock/assets/spec_dock/templates/epic/discussions/rules.md",
            "src/spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
            "src/spec_dock/assets/spec_dock/docs/reference_naming.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_adr.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_epic.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_initiative.md",
            "src/spec_dock/assets/spec_dock/docs/phase_requirement.md",
            "src/spec_dock/assets/spec_dock/docs/phase_design.md",
            "src/spec_dock/assets/spec_dock/docs/phase_plan.md",
            "src/spec_dock/assets/spec_dock/docs/README.md",
            "src/spec_dock/assets/spec_dock/docs/guide.md",
            "src/spec_dock/assets/spec_dock/scripts/README.md",
            "src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md",
            "spec-deps/current/discussions/rules.md",
            "spec-deps/README.md",
        ]
        text_map = self._read_text_map(repo_root, guidance_paths)
        self._assert_discussion_guidance_contract(text_map)

    def test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(runtime_script.is_file(), f"dogfooding runtime script missing: {runtime_script}")

        doctor_help = subprocess.run(
            [sys.executable, str(runtime_script), "doctor", "--help"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            doctor_help.returncode,
            0,
            msg=(
                "checked-in dogfooding runtime must expose 'doctor'\n"
                f"stdout:\n{doctor_help.stdout}\n"
                f"stderr:\n{doctor_help.stderr}\n"
            ),
        )
        self.assertIn("usage: spec-dock/scripts/spec-dock doctor", doctor_help.stdout)

        legacy_active = subprocess.run(
            [sys.executable, str(runtime_script), "active", "set", "--initiative", "1"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(legacy_active.returncode, 2)
        self.assertIn("'active set' supports explicit targets:", legacy_active.stderr)
        self.assertIn("active set --id <node-id>", legacy_active.stderr)

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_import_uniqueness_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self.records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), str(repo_slug)))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Foreign #123",
            labels=[],
            updated_at="2026-03-19T00:00:00Z",
            url="https://github.com/other/repo/issues/123",
            repo_owner="other",
            repo_name="repo",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-00123",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00123-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
        ),
    ]
    _materialize_required_artifacts(records)

    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    request = app_contracts.ImportNodeRequest(
        issue_number=123,
        title="Foreign Issue",
        slug=None,
        parent_id="epic-local-00001",
        target_repo_owner="other",
        target_repo_name="repo",
        allow_foreign_url=True,
    )
    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        result = app_import_node.import_issue(request, ports)
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert result.node.id.startswith("iss-local-"), result.node.id
    assert result.node.github_issue_number == 123
    assert result.node.github_repo_owner == "other"
    assert result.node.github_repo_name == "repo"
    assert issue_gateway.calls, "issue_view_minimal was not called"
    assert issue_gateway.calls[-1][2] == "other/repo", issue_gateway.calls[-1]
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_import_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
        self.on_view = None
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.on_view is not None:
            self.on_view()
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Race",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://github.com/example/repo/issues/{{issue_number}}",
        )

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    node_repo = _StubNodeRepo(records, events)
    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    raced_record = _record(
        kind="issue",
        node_id="iss-00555",
        title="Race winner import",
        path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00555-race-winner-import",
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=555,
    )
    injected = {{"done": False}}
    def _inject_race_winner():
        if injected["done"]:
            return
        _materialize_required_artifacts([raced_record])
        node_repo.records.append(raced_record)
        injected["done"] = True

    issue_gateway.on_view = _inject_race_winner

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=555,
                    title="Imported issue",
                    slug=None,
                    parent_id="epic-local-00001",
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
            assert "already linked" in message, message
        else:
            raise AssertionError("expected import/import race to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert injected["done"], injected
    assert events == [], events
    assert issue_gateway.calls == [(str(repo_root), 555, None)], issue_gateway.calls
    assert sum(1 for record in node_repo.records if record.id == "iss-00555") == 1, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_new_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
        self.on_view = None
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.on_view is not None:
            self.on_view()
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Race",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://github.com/other/repo/issues/{{issue_number}}",
            repo_owner="other",
            repo_name="repo",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    node_repo = _StubNodeRepo(records, events)
    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    raced_record = _record(
        kind="issue",
        node_id="iss-00123",
        title="Race winner new issue",
        path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00123-race-winner-new-issue",
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
    )
    injected = {{"done": False}}
    def _inject_race_winner():
        if injected["done"]:
            return
        _materialize_required_artifacts([raced_record])
        node_repo.records.append(raced_record)
        injected["done"] = True

    issue_gateway.on_view = _inject_race_winner

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        result = app_import_node.import_issue(
            app_contracts.ImportNodeRequest(
                issue_number=123,
                title="Imported foreign issue",
                slug=None,
                parent_id="epic-local-00001",
                target_repo_owner="other",
                target_repo_name="repo",
                allow_foreign_url=True,
            ),
            ports,
        )
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert injected["done"], injected
    assert result.node.id == "iss-local-00001", result.node.id
    assert result.node.github_issue_number == 123
    assert result.node.github_repo_owner == "other"
    assert result.node.github_repo_name == "repo"
    assert issue_gateway.calls == [(str(repo_root), 123, "other/repo")], issue_gateway.calls
    assert events == ["copy_scaffolded_tree", "write_meta"], events
    assert sum(1 for record in node_repo.records if record.id == "iss-00123") == 1, node_repo.records
    assert sum(1 for record in node_repo.records if record.id == "iss-local-00001") == 1, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_no_write_preflight_collision_with_active_parent_fallback_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Issue",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://example.invalid/issues/{{issue_number}}",
        )

class _StubActiveStateStore:
    def __init__(self, manifest):
        self._manifest = manifest
        self.calls = []
    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )
    def load_active_manifest_no_migrate(self, specdock_dir):
        self.calls.append(("load_active_manifest_no_migrate", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    (issue_template_dir / "README.md").write_text("issue=<ISS_ID>\\n", encoding="utf-8")
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00001-jwt-auth",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    issue_gateway = _StubIssueGateway()
    active_state_store = _StubActiveStateStore(
        infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-local-00001",
                path="spec-dock/path/init-local-00001",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-local-00001",
                path="spec-dock/path/epic-local-00001",
            ),
            issue=None,
        )
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records, events),
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        active_state_store=active_state_store,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    collision = (
        Path(records[1].path)
        / "issues"
        / "iss-00124-add-refresh-token"
        / "README.md"
    )
    collision.parent.mkdir(parents=True, exist_ok=True)
    collision.write_text("existing", encoding="utf-8")

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=124,
                    title="Add refresh token",
                    slug=None,
                    parent_id=None,
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
            assert "Destination already exists" in message, message
        else:
            raise AssertionError("expected preflight collision to fail")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert events == [], events
    assert issue_gateway.calls == [], issue_gateway.calls
    assert [name for name, _path in active_state_store.calls] == ["load_active_manifest_no_migrate"], active_state_store.calls
    assert not (collision.parent / ".meta.json").exists()
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_sync_snapshot_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
    from spec_dock_runtime.presentation import json_state as presentation_json_state
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_manifest_no_migrate(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "main"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / ".meta.json").write_text("{{}}", encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    _materialize_required_artifacts(records)
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=301,
                state="OPEN",
                title="Current repo #301",
                labels=[],
                updated_at="2026-03-18T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        ],
        foreign_snapshots={{
            ("other/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Foreign #301",
                labels=["bugfix"],
                updated_at="2026-03-18T02:00:00Z",
                url="https://github.com/other/repo/issues/301",
                repo_owner="other",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )
    result = app_sync_state.collect_sync_state(
        app_contracts.SyncRequest(
            force=False,
            github_enabled=True,
            issue_limit=10000,
            update_active_from_branch=False,
        ),
        ports,
    )
    current_status = result.issue_statuses["iss-local-00001"]
    foreign_status = result.issue_statuses["iss-local-00002"]
    assert current_status.effective_status == "open"
    assert foreign_status.effective_status == "done"
    index_all = json.loads(presentation_json_state.render_index_artifact(result).all_json_text)
    current_payload = index_all["nodes"]["iss-local-00001"]["github"]
    foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
    assert current_payload["url"] == "https://github.com/current/repo/issues/301"
    assert current_payload["state"] == "OPEN"
    assert foreign_payload["url"] == "https://github.com/other/repo/issues/301"
    assert foreign_payload["state"] == "CLOSED"
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_active_deps_status_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=301,
                state="OPEN",
                title="Current repo #301",
                labels=[],
                updated_at="2026-03-18T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        ],
        foreign_snapshots={{
            ("other/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Foreign #301",
                labels=["bugfix"],
                updated_at="2026-03-18T02:00:00Z",
                url="https://github.com/other/repo/issues/301",
                repo_owner="other",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"

    deps_result = app_check_deps.check_deps(
        app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    current_status = deps_result.inspection.issue_statuses["iss-local-00001"]
    assert current_status.effective_status == "open"
    assert deps_result.inspection.evaluation.ready is True
    assert deps_result.inspection.evaluation.guard_reason == "ready"
    assert len(issue_gateway.view_calls) == 2
    assert all(call[2] == "other/repo" for call in issue_gateway.view_calls)
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_same_repo_index_missing_view_fallback_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": ["iss-local-00001"]}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo Scoped",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo-scoped",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Target",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-target",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[],
        foreign_snapshots={{
            ("current/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Current repo #301",
                labels=["done"],
                updated_at="2026-03-19T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"

    deps_result = app_check_deps.check_deps(
        app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert deps_result.inspection.evaluation.ready is True
    dep_status = deps_result.inspection.issue_statuses["iss-local-00001"]
    assert dep_status.source == "github"
    assert dep_status.effective_status == "done"
    assert len(issue_gateway.view_calls) == 2
    assert all(call[2] == "current/repo" for call in issue_gateway.view_calls)
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_validation_doctor_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import doctor as app_doctor
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import validate_tree as app_validate_tree
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    _materialize_required_artifacts(records)

    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        node_repo=_StubNodeRepo(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        git_gateway=_StubGitGateway(),
    )
    validation = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)
    assert not validation.report.errors, validation.report.errors

    doctor_result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
    assert doctor_result.ok, doctor_result.findings

    loaded_graph = app_create_node.load_graph(ports, validate=True)
    assert "iss-local-00001" in loaded_graph.nodes_by_id
    assert "iss-local-00002" in loaded_graph.nodes_by_id
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_tool_version_fallback_reads_pyproject(self) -> None:
        import spec_dock.cli as cli

        expected = _expected_spec_dock_version()
        old_version = getattr(cli, "__version__", None)
        old_file = getattr(cli, "__file__", None)
        try:
            cli.__version__ = "0.0.0+unknown"
            repo_root = Path(__file__).resolve().parents[1]
            cli.__file__ = str(repo_root / "src" / "spec_dock" / "cli.py")
            self.assertEqual(cli._tool_version(), expected)
        finally:
            if old_version is not None:
                cli.__version__ = old_version
            if old_file is not None:
                cli.__file__ = old_file

    def test_no_skill_option_is_rejected(self) -> None:
        import spec_dock.cli as cli

        with self.assertRaises(SystemExit) as cm:
            cli._parse_args(["init", "--no-skill", "."])
        self.assertEqual(cm.exception.code, 2)

    def test_update_migrates_legacy_single_skill_and_preserves_custom_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            skills_root = target / ".agents" / "skills"
            for skill_name in _EXPECTED_MANAGED_SKILL_NAMES:
                if skill_name == "spec-driven-tdd-workflow":
                    continue
                shutil.rmtree(skills_root / skill_name)

            custom_dir = skills_root / "my-custom-skill"
            custom_dir.mkdir(parents=True, exist_ok=True)
            (custom_dir / "SKILL.md").write_text("# custom\n", encoding="utf-8")
            (custom_dir / "notes.txt").write_text("keep\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)
            self.assertTrue((custom_dir / "SKILL.md").is_file())
            self.assertTrue((custom_dir / "notes.txt").is_file())

    def test_update_installs_full_skill_set_for_legacy_no_skill_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            skills_root = target / ".agents" / "skills"

            self.assertEqual(main(["init", str(target)]), 0)
            shutil.rmtree(skills_root)
            self.assertFalse(skills_root.exists())
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

            for skill_name in _EXPECTED_MANAGED_SKILL_NAMES:
                shutil.rmtree(skills_root / skill_name)
            self.assertEqual(list(skills_root.glob("*")), [])
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

    def test_update_skill_sync_converges_after_interrupted_run(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            original_copy_file = cli._copy_file
            failed_once = False

            def interrupted_copy(src: Path, dest: Path) -> None:
                nonlocal failed_once
                if (
                    not failed_once
                    and dest.as_posix().endswith("/.agents/skills/spec-dock-epic-planning/SKILL.md")
                ):
                    failed_once = True
                    raise RuntimeError("simulated skill sync interruption")
                original_copy_file(src, dest)

            cli._copy_file = interrupted_copy
            try:
                self.assertEqual(main(["update", str(target)]), 1)
            finally:
                cli._copy_file = original_copy_file

            self.assertTrue(failed_once)
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

    def test_bundled_skill_assets_cover_managed_manifest(self) -> None:
        import spec_dock.cli as cli

        self.assertEqual(cli._managed_skill_names(), _EXPECTED_MANAGED_SKILL_NAMES)
        with cli._assets_dir() as assets_dir:
            for skill_name in cli._managed_skill_names():
                skill_path = assets_dir / "codex_skills" / skill_name / "SKILL.md"
                self.assertTrue(skill_path.is_file(), f"missing bundled skill asset: {skill_path}")

    def test_bundled_skill_routing_contract(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            skills_dir = assets_dir / "codex_skills"
            hub_text = (skills_dir / "spec-driven-tdd-workflow" / "SKILL.md").read_text(encoding="utf-8")
            initiative_text = (skills_dir / "spec-dock-initiative-planning" / "SKILL.md").read_text(encoding="utf-8")
            epic_text = (skills_dir / "spec-dock-epic-planning" / "SKILL.md").read_text(encoding="utf-8")
            issue_text = (skills_dir / "spec-dock-issue-execution" / "SKILL.md").read_text(encoding="utf-8")
            adr_text = (skills_dir / "spec-dock-adr-facilitation" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(
            "`spec-dock-initiative-planning`: initiative-level requirement/design/plan planning.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-epic-planning`: epic-level requirement/design/plan planning.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-issue-execution`: issue-level TDD execution and report updates.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-adr-facilitation`: ADR drafting/decision facilitation linked to the current workflow.",
            hub_text,
        )
        self.assertIn("`spec-dock/docs/reference_github.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", hub_text)
        self.assertIn("`spec-dock/active/context-pack.md`", hub_text)

        self.assertIn("`spec-dock/docs/workflow_initiative.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", initiative_text)
        self.assertIn("create/import an initiative", initiative_text)
        self.assertIn("scope-specific constraints and decisions", initiative_text)

        self.assertIn("`spec-dock/docs/workflow_epic.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", epic_text)
        self.assertIn("create/import an epic", epic_text)
        self.assertIn("scope-specific constraints and decisions", epic_text)

        self.assertIn("`spec-dock/docs/workflow_issue.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", issue_text)
        self.assertIn("`spec-dock/active/context-pack.md`", issue_text)
        self.assertIn("implement the active issue via TDD", issue_text)
        self.assertIn("source of truth", issue_text)
        self.assertIn("docs impact resolution step", issue_text)
        self.assertIn("final diff review quality gate", issue_text)

        self.assertIn("`spec-dock/docs/workflow_adr.md`", adr_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", adr_text)
        self.assertIn("Return to the current parent workflow", adr_text)
        self.assertIn("create/update an ADR", adr_text)

        for skill_text in (hub_text, initiative_text, epic_text, issue_text, adr_text):
            self.assertNotIn("runtime-operations", skill_text)

    def test_init_fails_without_force_when_spec_dock_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Second init without --force should fail.
            self.assertNotEqual(main(["init", str(target)]), 0)

    def test_update_keeps_initiatives_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            marker = target / "spec-dock" / "initiatives" / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")

            # Simulate legacy (v1) leftovers that v2 should prune on update.
            legacy_workflow = target / ".github" / "workflows" / "spec-dock-close.yml"
            legacy_workflow.parent.mkdir(parents=True, exist_ok=True)
            legacy_workflow.write_text("legacy\n", encoding="utf-8")

            legacy_symlink = target / "spec-dock" / "current-initiative"
            created_symlink = False
            try:
                # v1 style link target (so v2 can safely prune without deleting v2-generated shortcuts).
                os.symlink("initiative/current", legacy_symlink)
                created_symlink = True
            except OSError:
                # Some environments may restrict symlinks; workflow pruning is still validated.
                created_symlink = False

            self.assertEqual(main(["update", str(target)]), 0)
            self.assertTrue(marker.is_file())
            self._assert_version_file(target)
            self.assertFalse(legacy_workflow.exists())
            if created_symlink:
                self.assertFalse(legacy_symlink.is_symlink())

    def _clear_active_entrypoints(self, target: Path) -> Path:
        active_dir = target / "spec-dock" / "active"
        for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
            p = active_dir / name
            if p.is_symlink() or p.is_file():
                p.unlink(missing_ok=True)
            elif p.is_dir():
                shutil.rmtree(p)
        self.assertEqual(list(active_dir.iterdir()), [])
        return active_dir

    def _overlay_checked_in_dogfooding_runtime(self, target: Path) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        checked_in_scripts_dir = repo_root / "spec-dock" / "scripts"
        target_scripts_dir = target / "spec-dock" / "scripts"
        self.assertTrue(checked_in_scripts_dir.is_dir(), f"checked-in scripts dir missing: {checked_in_scripts_dir}")
        self.assertTrue(target_scripts_dir.is_dir(), f"target scripts dir missing: {target_scripts_dir}")

        target_runtime_dir = target_scripts_dir / "spec_dock_runtime"
        if target_runtime_dir.exists():
            shutil.rmtree(target_runtime_dir)
        shutil.copytree(checked_in_scripts_dir / "spec_dock_runtime", target_runtime_dir)
        shutil.copy2(checked_in_scripts_dir / "spec-dock", target_scripts_dir / "spec-dock")

    def _create_minimal_local_tree(self, target: Path) -> tuple[Path, Path, Path]:
        self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
        self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
        self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

        initiative_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
        epic_dir = initiative_dir / "epics" / "epic-local-00001-jwt-auth"
        issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
        self.assertTrue((initiative_dir / ".meta.json").is_file())
        self.assertTrue((epic_dir / ".meta.json").is_file())
        self.assertTrue((issue_dir / ".meta.json").is_file())
        return initiative_dir, epic_dir, issue_dir

    def test_checked_in_dogfooding_runtime_subprocess_keeps_sync_deps_active_validate_doctor_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            deps_result = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-local-00001"])
            self.assertEqual(
                deps_result.returncode,
                0,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            self.assertIn("spec-dock: ok (deps check)", deps_result.stdout)

            active_result = self._run_runtime_capture(target, ["active", "set", "--id", "iss-local-00001"])
            self.assertEqual(
                active_result.returncode,
                0,
                msg=f"active stdout:\n{active_result.stdout}\nactive stderr:\n{active_result.stderr}",
            )
            self.assertIn("spec-dock: ok (active set)", active_result.stdout)

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                0,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("spec-dock: ok (doctor) findings=0", doctor_result.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)

            broken_epic_meta_path = epic_dir / ".meta.json"
            broken_epic_meta = json.loads(broken_epic_meta_path.read_text(encoding="utf-8"))
            broken_epic_meta.pop("parent_id", None)
            self._write_json_force(broken_epic_meta_path, broken_epic_meta)
            (initiative_dir / "report.md").chmod((initiative_dir / "report.md").stat().st_mode | 0o200)
            (initiative_dir / "report.md").unlink()
            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                1,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("epic missing parent_id", validate_result.stderr)
            self.assertNotIn("Missing required artifact", validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                1,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("epic missing parent_id", doctor_result.stderr)
            self.assertNotIn("Missing required artifact", doctor_result.stderr)

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("epic missing parent_id", sync_result.stderr)
            self.assertNotIn("Missing required artifact", sync_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("preflight validate failed: Missing required artifact", sync_result.stderr)
            self.assertIn("report.md", sync_result.stderr)
            self.assertNotIn("spec-dock: ok (sync)", sync_result.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_import_fails_fast_when_required_artifact_missing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            import_result = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertEqual(
                import_result.returncode,
                1,
                msg=f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}",
            )
            self.assertIn("preflight validate failed", import_result.stderr)
            self.assertIn("Missing required artifact", import_result.stderr)
            self.assertIn("report.md", import_result.stderr)
            self.assertFalse(
                (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-local-00001-auth-platform"
                    / "epics"
                    / "epic-local-00001-jwt-auth"
                    / "issues"
                    / "iss-00123-imported-issue"
                ).exists()
            )
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

    def test_checked_in_dogfooding_runtime_subprocess_sync_force_degrades_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)
            agent_dir = target / "spec-dock" / ".agent"

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("preflight validate failed", sync_result.stderr)
            self.assertIn("report.md", sync_result.stderr)
            self.assertTrue(
                "deps_preflight_failed" in sync_result.stderr or "DEPS_DISABLED" in sync_result.stderr,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("preflight validate failed", str(index["deps"]["error"]))

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertIn("preflight validate failed", str(tree["deps"]["error"]))

    def test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)

            broken_epic_meta_path = epic_dir / ".meta.json"
            broken_epic_meta = json.loads(broken_epic_meta_path.read_text(encoding="utf-8"))
            broken_epic_meta.pop("parent_id", None)
            self._write_json_force(broken_epic_meta_path, broken_epic_meta)
            (initiative_dir / "report.md").chmod((initiative_dir / "report.md").stat().st_mode | 0o200)
            (initiative_dir / "report.md").unlink()
            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("epic missing parent_id", sync_result.stderr)
            self.assertNotIn("Missing required artifact", sync_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                1,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("Missing required artifact", validate_result.stderr)
            self.assertIn("design.md", validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                1,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("[missing_artifact] Missing required artifact", doctor_result.stderr)
            self.assertIn("design.md", doctor_result.stderr)

    def test_update_rebuilds_active_entrypoints_from_persisted_manifest_when_valid_and_active_dir_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/report.md`", context_pack_text)
            self.assertNotIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_rewrites_stale_context_pack_when_rebuilding_active_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            # Simulate partial deletion: entrypoints disappeared but stale context-pack remains.
            for name in ("initiative", "epic", "issue", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.write_text(
                "# Context Pack (stale)\n\n## Active\n- initiative: (none)\n- epic: (none)\n- issue: (none)\n",
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_keeps_context_pack_aligned_with_existing_active_entrypoints_when_persisted_manifest_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001"])

            active_dir = target / "spec-dock" / "active"
            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "report.md"))

    def test_update_regenerates_context_pack_from_existing_active_entrypoints_when_manifest_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001"])

            active_dir = target / "spec-dock" / "active"
            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.unlink(missing_ok=True)
            self.assertFalse(context_pack_path.exists())

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_keeps_context_pack_aligned_with_existing_active_pathfiles_when_persisted_manifest_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            for layer, node_dir in (
                ("initiative", initiative_dir),
                ("epic", epic_dir),
                ("issue", issue_dir),
            ):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_target = os.path.relpath(node_dir, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_target + "\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "report.md"))

    def test_update_recovers_active_entrypoints_from_id_when_persisted_paths_are_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, _issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-00001", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-00001",
                        "path": "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": (
                            "spec-dock/initiatives/init-local-00001-auth-platform/epics/"
                            "epic-local-00001-jwt-auth/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "requirement.md"))

    def test_update_falls_back_to_placeholder_when_persisted_active_manifest_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_bootstraps_active_fallback_entrypoints_when_active_dir_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            self.assertEqual(list(active_dir.iterdir()), [])
            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)

    def test_update_regenerates_context_pack_from_persisted_active_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.unlink(missing_ok=True)
            self.assertFalse(context_pack_path.exists())

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/report.md`", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertNotIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_bootstraps_active_path_files_when_active_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            self.assertEqual(list(active_dir.iterdir()), [])

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            for layer in ("initiative", "epic", "issue"):
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    self.assertFalse(link.exists())
                    self.assertFalse(link.is_symlink())
                    self.assertTrue(pathfile.is_file())
                    resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                    self.assertEqual(resolved, (placeholder_root / layer).resolve())
                    self.assertEqual(
                        self._read_active_pointer_text(target, layer, "README.md"),
                        (placeholder_root / layer / "README.md").read_text(encoding="utf-8"),
                    )

    def test_update_rebuilds_active_path_files_from_persisted_manifest_when_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    self.assertFalse(link.exists())
                    self.assertFalse(link.is_symlink())
                    self.assertTrue(pathfile.is_file())
                    resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                    self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_repairs_stale_active_path_files_to_persisted_targets_when_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            stale_rel = "../system/active-none/missing-node"
            for layer in ("initiative", "epic", "issue"):
                (active_dir / f"{layer}.path").write_text(stale_rel + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    pathfile = active_dir / f"{layer}.path"
                    self.assertTrue(pathfile.is_file())
                    rel_target = pathfile.read_text(encoding="utf-8").strip()
                    self.assertNotEqual(rel_target, stale_rel)
                    resolved = (active_dir / rel_target).resolve()
                    self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

    def test_update_repairs_stale_active_path_files_to_placeholder_when_persisted_manifest_broken_and_symlink_creation_fails(
        self,
    ) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            stale_rel = "../system/active-none/missing-node"
            for layer in ("initiative", "epic", "issue"):
                (active_dir / f"{layer}.path").write_text(stale_rel + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            for layer in ("initiative", "epic", "issue"):
                with self.subTest(layer=layer):
                    pathfile = active_dir / f"{layer}.path"
                    self.assertTrue(pathfile.is_file())
                    rel_target = pathfile.read_text(encoding="utf-8").strip()
                    self.assertNotEqual(rel_target, stale_rel)
                    resolved = (active_dir / rel_target).resolve()
                    self.assertEqual(resolved, (placeholder_root / layer).resolve())
                    self.assertEqual(
                        self._read_active_pointer_text(target, layer, "README.md"),
                        (placeholder_root / layer / "README.md").read_text(encoding="utf-8"),
                    )

    def test_update_prefers_existing_active_entrypoints_over_stale_persisted_manifest_for_context_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            # Keep healthy entrypoints via pathfiles, then inject stale persisted ids.
            entry_targets = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, target_dir in entry_targets.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    if link.is_symlink() or link.is_file():
                        link.unlink(missing_ok=True)
                    elif link.is_dir():
                        shutil.rmtree(link)
                    rel_target = os.path.relpath(target_dir, start=active_dir)
                    (active_dir / f"{layer}.path").write_text(rel_target + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_dangling_active_symlink_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            pointer = active_dir / "initiative"
            pointer.unlink(missing_ok=True)
            os.symlink("../system/active-none/missing-initiative", pointer)
            self.assertTrue(pointer.is_symlink())
            self.assertFalse(pointer.exists())

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder = target / "spec-dock" / "system" / "active-none" / "initiative" / "README.md"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                placeholder.read_text(encoding="utf-8"),
            )

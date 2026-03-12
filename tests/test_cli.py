import re
import os
import sys
import tempfile
import subprocess
import shutil
import unittest
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    from spec_dock.cli import main
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from spec_dock.cli import main


import importlib.util
from types import SimpleNamespace

def _expected_spec_dock_version() -> str:
    try:
        return version("spec-dock")
    except PackageNotFoundError:
        text = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
        if not match:
            raise AssertionError("failed to read version from pyproject.toml")
        return match.group(1)


_EXPECTED_MANAGED_SKILL_NAMES = (
    "spec-driven-tdd-workflow",
    "spec-dock-initiative-planning",
    "spec-dock-epic-planning",
    "spec-dock-issue-execution",
    "spec-dock-adr-facilitation",
)


class TestCli(unittest.TestCase):
    def _can_create_symlink(self, target: Path) -> bool:
        if not hasattr(os, "symlink"):
            return False
        if os.name == "nt":
            return False
        try:
            tmp = target / ".symlink-test"
            tmp.mkdir(parents=True, exist_ok=True)
            src = tmp / "src.txt"
            dst = tmp / "dst.txt"
            src.write_text("x\n", encoding="utf-8")
            os.symlink("src.txt", dst)
            return dst.is_symlink()
        except OSError:
            return False
        finally:
            try:
                shutil.rmtree(tmp)
            except Exception:
                pass

    def _run_runtime(self, target: Path, args: list[str], *, env: dict[str, str] | None = None) -> None:
        script = target / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")

        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        p = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
            env=merged_env,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            raise AssertionError(
                "runtime command failed:\n"
                f"- cmd: {args}\n"
                f"- stdout:\n{p.stdout}\n"
                f"- stderr:\n{p.stderr}\n"
            )

    def _run_runtime_expect_fail(self, target: Path, args: list[str], *, env: dict[str, str] | None = None) -> None:
        script = target / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")

        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        p = subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
            env=merged_env,
            capture_output=True,
            text=True,
        )
        if p.returncode == 0:
            raise AssertionError(
                "runtime command unexpectedly succeeded:\n"
                f"- cmd: {args}\n"
                f"- stdout:\n{p.stdout}\n"
                f"- stderr:\n{p.stderr}\n"
            )

    def _run_runtime_capture(
        self, target: Path, args: list[str], *, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        script = target / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(script.is_file(), f"runtime script missing: {script}")

        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
            env=merged_env,
            capture_output=True,
            text=True,
        )

    def _run_wrapper_capture(
        self,
        script: Path,
        args: list[str],
        *,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self.assertTrue(script.is_file(), f"wrapper script missing: {script}")
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            [str(script), *args],
            cwd=str(cwd if cwd is not None else script.parent),
            env=merged_env,
            capture_output=True,
            text=True,
        )

    def _read_active_pointer_text(self, target: Path, pointer: str, rel_file: str) -> str:
        active_dir = target / "spec-dock" / "active"
        direct = active_dir / pointer
        if direct.exists():
            return (direct / rel_file).read_text(encoding="utf-8")

        pathfile = active_dir / f"{pointer}.path"
        self.assertTrue(pathfile.is_file(), f"missing pointer: {pointer} or {pointer}.path")
        rel = pathfile.read_text(encoding="utf-8").strip()
        resolved = (active_dir / rel).resolve()
        return (resolved / rel_file).read_text(encoding="utf-8")

    def _run_git(self, target: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
        p = subprocess.run(
            ["git", *args],
            cwd=str(target),
            capture_output=True,
            text=True,
        )
        if check and p.returncode != 0:
            raise AssertionError(
                "git command failed:\n"
                f"- cmd: {args}\n"
                f"- stdout:\n{p.stdout}\n"
                f"- stderr:\n{p.stderr}\n"
            )
        return p

    def _make_gh_issue_view_stub(
        self,
        bin_dir: Path,
        *,
        failing_numbers: set[int] | None = None,
        log_path: Path | None = None,
    ) -> None:
        fail_nums = " ".join(str(n) for n in sorted(failing_numbers or set()))
        log_line = ""
        if log_path is not None:
            log_line = f'  echo "$@" >> "{log_path.as_posix()}"\n'

        gh_path = bin_dir / "gh"
        gh_path.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f'fail_nums="{fail_nums}"\n'
            'if [[ "$1" == "issue" && "$2" == "view" ]]; then\n'
            '  n="$3"\n'
            f"{log_line}"
            '  for f in $fail_nums; do\n'
            '    if [[ "$n" == "$f" ]]; then\n'
            '      echo "issue not found: $n" >&2\n'
            "      exit 1\n"
            "    fi\n"
            "  done\n"
            '  echo "{\\"number\\": $n, \\"url\\": \\"https://github.com/example/repo/issues/$n\\"}"\n'
            "  exit 0\n"
            "fi\n"
            'echo "unexpected gh args: $@" >&2\n'
            "exit 99\n",
            encoding="utf-8",
        )
        gh_path.chmod(0o755)

    def _make_gh_issue_list_stub(
        self,
        bin_dir: Path,
        *,
        issues: list[dict[str, object]],
        fail: bool = False,
        log_path: Path | None = None,
    ) -> None:
        log_line = ""
        if log_path is not None:
            log_line = f'  echo "$@" >> "{log_path.as_posix()}"\n'

        payload = json.dumps(issues, ensure_ascii=False)

        gh_path = bin_dir / "gh"
        gh_path.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
            f"{log_line}"
            + ("  echo \"gh stub: simulated failure\" >&2\n  exit 1\n" if fail else "")
            + "  cat <<'JSON'\n"
            + f"{payload}\n"
            + "JSON\n"
            "  exit 0\n"
            "fi\n"
            'echo "unexpected gh args: $@" >&2\n'
            "exit 99\n",
            encoding="utf-8",
        )
        gh_path.chmod(0o755)

    def _assert_version_file(self, target: Path) -> None:
        version_file = target / "spec-dock" / "spec-dock.version"
        self.assertTrue(version_file.is_file())
        self.assertEqual(version_file.read_text(encoding="utf-8").strip(), _expected_spec_dock_version())

    def _assert_spec_dock_meta_marker(self, meta: dict[str, object]) -> None:
        marker = meta.get("_spec_dock")
        self.assertIsInstance(marker, dict)
        marker_dict = marker
        self.assertEqual(marker_dict.get("managed"), True)
        self.assertEqual(marker_dict.get("do_not_edit"), True)
        self.assertEqual(marker_dict.get("edit_via"), "spec-dock")

    def _assert_readonly_on_posix(self, path: Path) -> None:
        if os.name != "posix":
            return
        mode = path.stat().st_mode
        self.assertEqual(
            mode & 0o222,
            0,
            f"expected no write bits on POSIX: {path} (mode={oct(mode)})",
        )

    def _write_text_force(self, path: Path, text: str) -> None:
        if path.exists():
            try:
                path.chmod(path.stat().st_mode | 0o200)
            except OSError:
                pass
        path.write_text(text, encoding="utf-8")

    def _write_json_force(self, path: Path, data: object) -> None:
        self._write_text_force(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    def _installed_skill_files(self, target: Path) -> list[str]:
        skills_root = target / ".agents" / "skills"
        if not skills_root.exists():
            return []
        return sorted(p.relative_to(skills_root).as_posix() for p in skills_root.glob("*/SKILL.md"))

    def _assert_managed_skills_installed(self, target: Path) -> None:
        managed_names = set(_EXPECTED_MANAGED_SKILL_NAMES)
        installed_managed = sorted(
            skill_file
            for skill_file in self._installed_skill_files(target)
            if skill_file.split("/", 1)[0] in managed_names
        )
        self.assertEqual(
            installed_managed,
            sorted(f"{name}/SKILL.md" for name in _EXPECTED_MANAGED_SKILL_NAMES),
        )

    def _read_text_map(self, base: Path, rel_paths: list[str]) -> dict[str, str]:
        out: dict[str, str] = {}
        for rel in rel_paths:
            path = base / rel
            self.assertTrue(path.is_file(), f"missing guidance file: {path}")
            out[rel] = path.read_text(encoding="utf-8")
        return out

    def _assert_discussion_guidance_contract(self, text_map: dict[str, str]) -> None:
        combined = "\n".join(text_map.values())

        self.assertIn("new doc adr", combined)
        self.assertIn("new doc disc", combined)
        self.assertIn("new doc research", combined)
        self.assertIn("new doc note", combined)
        self.assertIn("NNN-type-slug.md", combined)
        self.assertIn("nonconforming", combined)
        self.assertIn("follow-up issue", combined)
        self.assertIn("archive", combined)

        self.assertNotIn("new adr --", combined)
        self.assertNotIn("<type>-00001-<slug>.md", combined)
        self.assertNotIn("<type>-xxxxx-<slug>.md", combined)

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

    def test_new_and_active_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create nodes without touching GitHub.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            # Parent ids accept shorthand numeric forms (e.g. `1` -> `init-local-00001` / `epic-local-00001`).
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            self.assertTrue((issue_dir / "requirement.md").is_file())
            self.assertTrue((issue_dir / "design.md").is_file())
            self.assertTrue((issue_dir / "plan.md").is_file())
            self.assertTrue((issue_dir / "report.md").is_file())

            # Placeholders should be rendered in generated files.
            requirement = (issue_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertNotIn("<ISS_ID>", requirement)
            self.assertNotIn("<ISS_TITLE>", requirement)
            self.assertIn("iss-local-00001", requirement)

            # Active pointers are set by a single target argument (node id or GitHub issue number).
            self._run_runtime(target, ["active", "set", "iss-local-00001", "--force"])
            self.assertTrue((target / "spec-dock" / ".agent" / "active.json").is_file())
            self.assertTrue(
                (target / "spec-dock" / "active" / "issue").exists()
                or (target / "spec-dock" / "active" / "issue.path").is_file()
            )
            self.assertTrue((target / "spec-dock" / "active" / "context-pack.md").is_file())

            self._run_runtime(target, ["sync"])
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())

            # Index: flat nodes (agent-friendly).
            state = (target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8")
            self.assertIn("\"nodes\"", state)
            self.assertNotIn("\"tree\"", state)

            # Tree: nested layer view (human-friendly).
            tree_text = (target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8")
            tree = json.loads(tree_text)
            self.assertIn("tree", tree)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            index_nodes = index["nodes"]

            init_item = tree["tree"][0]
            self.assertEqual(init_item["id"], "init-local-00001")
            self.assertEqual(init_item["type"], "initiative")
            self.assertIn("epics", init_item)

            epic_item = init_item["epics"][0]
            self.assertEqual(epic_item["id"], "epic-local-00001")
            self.assertEqual(epic_item["type"], "epic")
            self.assertIn("issues", epic_item)

            issue_item = epic_item["issues"][0]
            self.assertEqual(issue_item["id"], "iss-local-00001")
            self.assertEqual(issue_item["type"], "issue")

            # `tree.json` nodes match the same node schema as `index.json` nodes.
            self.assertEqual(issue_item, index_nodes["iss-local-00001"])
            self._run_runtime(target, ["validate"])

    def test_sync_emits_all_and_todo_json_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            self._run_runtime(target, ["sync"])

            agent_dir = target / "spec-dock" / ".agent"
            index_all_path = agent_dir / "index-all.json"
            tree_all_path = agent_dir / "tree-all.json"
            index_todo_path = agent_dir / "index.json"
            tree_todo_path = agent_dir / "tree.json"

            self.assertTrue(index_all_path.is_file())
            self.assertTrue(tree_all_path.is_file())
            self.assertTrue(index_todo_path.is_file())
            self.assertTrue(tree_todo_path.is_file())

            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            tree_all = json.loads(tree_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            tree_todo = json.loads(tree_todo_path.read_text(encoding="utf-8"))

            self.assertEqual(index_all["schema_version"], 2)
            self.assertEqual(tree_all["schema_version"], 2)
            self.assertEqual(index_todo["schema_version"], 2)
            self.assertEqual(tree_todo["schema_version"], 2)

            def _collect_tree_node_ids(items: list[dict[str, object]]) -> set[str]:
                ids: set[str] = set()
                for initiative in items:
                    init_id = initiative.get("id")
                    if isinstance(init_id, str):
                        ids.add(init_id)

                    for epic in initiative.get("epics", []):
                        if not isinstance(epic, dict):
                            continue
                        epic_id = epic.get("id")
                        if isinstance(epic_id, str):
                            ids.add(epic_id)

                        for issue in epic.get("issues", []):
                            if not isinstance(issue, dict):
                                continue
                            issue_id = issue.get("id")
                            if isinstance(issue_id, str):
                                ids.add(issue_id)
                return ids

            index_all_nodes = set(index_all["nodes"].keys())
            tree_all_nodes = _collect_tree_node_ids(tree_all["tree"])
            index_todo_nodes = set(index_todo["nodes"].keys())
            tree_todo_nodes = _collect_tree_node_ids(tree_todo["tree"])

            self.assertNotEqual(index_all_nodes, set())
            self.assertEqual(index_all_nodes, tree_all_nodes)
            self.assertEqual(index_todo_nodes, tree_todo_nodes)
            self.assertTrue(index_todo_nodes.issubset(index_all_nodes))
            self.assertEqual(index_all_nodes, index_todo_nodes)

    def test_sync_compiles_shorthand_to_issue_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"])

            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Deps init"])
            self._run_runtime(target, ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Deps epic"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Dep issue 1"])
            self._run_runtime(target, ["new", "issue", "--epic", "202", "--github-issue", "402", "--title", "Dep issue 2"])

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-main-init"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps(
                    {"schema_version": 1, "depends_on": ["epic-00202", "102", 401]},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            expected_edges = [
                {"from": "iss-00301", "to": "iss-00401", "kind": "depends_on"},
                {"from": "iss-00301", "to": "iss-00402", "kind": "depends_on"},
            ]
            self.assertEqual(index_all["deps"]["issue_edges"], expected_edges)
            self.assertEqual(index_todo["deps"]["issue_edges"], expected_edges)
            for edge in expected_edges:
                self.assertTrue(edge["from"].startswith("iss-"))
                self.assertTrue(edge["to"].startswith("iss-"))

    def test_sync_warns_when_shorthand_expands_to_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target issue"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Empty init"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "2", "--title", "Empty epic"])

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-main-init"
                / "epics"
                / "epic-local-00001-main-epic"
                / "issues"
                / "iss-local-00001-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps(
                    {"schema_version": 1, "depends_on": ["epic-local-00002", "init-local-00002"]},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("deps_ref_expanded_to_empty", p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["deps"]["issue_edges"], [])

    def test_sync_fails_on_unresolved_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target issue"])

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-main-init"
                / "epics"
                / "epic-local-00001-main-epic"
                / "issues"
                / "iss-local-00001-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-99999"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-99999", p.stderr)
            self.assertIn("deps.json", p.stderr)

    def test_sync_fails_on_descendant_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target issue"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-main-init"
            deps_path = init_dir / "deps.json"
            deps_path.write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn(str(deps_path), p.stderr)
            self.assertIn("iss-local-00001", p.stderr)

    def test_sync_fails_on_self_or_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Main init"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Main epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue two"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-main-init"
                / "epics"
                / "epic-local-00001-main-epic"
            )
            issue_one_dir = epic_dir / "issues" / "iss-local-00001-issue-one"
            issue_two_dir = epic_dir / "issues" / "iss-local-00002-issue-two"
            issue_one_deps_path = issue_one_dir / "deps.json"

            # Self dependency must fail.
            issue_one_deps_path.write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            p_self = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p_self.returncode, 1, p_self.stdout + p_self.stderr)
            self.assertIn("iss-local-00001", p_self.stderr)
            self.assertIn(str(issue_one_deps_path), p_self.stderr)

            # Shorthand self (issue depends on own epic) must also fail.
            issue_one_deps_path.write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            p_shorthand_self = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p_shorthand_self.returncode, 1, p_shorthand_self.stdout + p_shorthand_self.stderr)
            self.assertIn("iss-local-00001", p_shorthand_self.stderr)
            self.assertIn("epic-local-00001", p_shorthand_self.stderr)
            self.assertIn(str(issue_one_deps_path), p_shorthand_self.stderr)

            # Cycle dependency must fail.
            issue_one_deps_path.write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (issue_two_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            p_cycle = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p_cycle.returncode, 1, p_cycle.stdout + p_cycle.stderr)
            self.assertIn("iss-local-00001", p_cycle.stderr)
            self.assertIn("iss-local-00002", p_cycle.stderr)
            self.assertIn("->", p_cycle.stderr)

    def test_sync_derives_deps_fields_ready_and_blockers(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done dep"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Open mid"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open target"],
            )

            issue_mid_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-open-mid"
            )
            issue_target_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00303-open-target"
            )
            (issue_mid_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (issue_target_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [302]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Open mid", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Open target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index_all["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "done")
            self.assertEqual(nodes["iss-00301"]["deps"], {"ready": True, "depends_on": [], "blockers_top": []})
            self.assertEqual(nodes["iss-00302"]["deps"], {"ready": True, "depends_on": [], "blockers_top": []})
            self.assertEqual(
                nodes["iss-00303"]["deps"],
                {"ready": False, "depends_on": ["iss-00302"], "blockers_top": ["iss-00302"]},
            )

            tree = json.loads((target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8"))
            tree_issue = [i for i in tree["tree"][0]["epics"][0]["issues"] if i["id"] == "iss-00303"][0]
            self.assertEqual(tree_issue["deps"], nodes["iss-00303"]["deps"])

    def test_unknown_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Unknown issue"])

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            issue = index["nodes"]["iss-local-00001"]
            self.assertEqual(issue["status"], "unknown")
            self.assertEqual(issue["deps"], {"ready": False, "depends_on": [], "blockers_top": []})

    def test_sync_outputs_are_deterministically_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue two"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue three"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue target"])

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
            )
            (issues_root / "iss-local-00002-issue-two" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (issues_root / "iss-local-00003-issue-three" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (issues_root / "iss-local-00004-issue-target" / "deps.json").write_text(
                json.dumps(
                    {"schema_version": 1, "depends_on": ["iss-local-00003", "iss-local-00001"]},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            p1 = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            index1 = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            p2 = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)
            index2 = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))

            self.assertEqual(
                index1["deps"]["issue_edges"],
                [
                    {"from": "iss-local-00002", "to": "iss-local-00001", "kind": "depends_on"},
                    {"from": "iss-local-00003", "to": "iss-local-00002", "kind": "depends_on"},
                    {"from": "iss-local-00004", "to": "iss-local-00001", "kind": "depends_on"},
                    {"from": "iss-local-00004", "to": "iss-local-00003", "kind": "depends_on"},
                ],
            )
            self.assertEqual(index2["deps"]["issue_edges"], index1["deps"]["issue_edges"])

            deps1 = index1["nodes"]["iss-local-00004"]["deps"]
            deps2 = index2["nodes"]["iss-local-00004"]["deps"]
            self.assertEqual(deps1, deps2)
            self.assertEqual(deps1["depends_on"], ["iss-local-00001", "iss-local-00002", "iss-local-00003"])
            self.assertEqual(deps1["blockers_top"], deps1["depends_on"][: len(deps1["blockers_top"])])

    def test_sync_emits_deps_issues_json_and_puml_todo_only(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done prereq"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Open blocked"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open prereq"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Open done dep"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "305", "--title", "Open isolated"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            (issues_root / "iss-00302-open-blocked" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [303]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (issues_root / "iss-00304-open-done-dep" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Blocked", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Prereq", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 304, "state": "OPEN", "title": "Done dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 305, "state": "OPEN", "title": "Isolated", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            deps_issues_path = target / "spec-dock" / ".agent" / "deps-issues.json"
            deps_issues_puml_path = target / "spec-dock" / "deps-issues.puml"
            self.assertTrue(deps_issues_path.is_file())
            self.assertTrue(deps_issues_puml_path.is_file())

            deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
            self.assertEqual(deps_issues["schema_version"], 1)
            self.assertEqual(
                set(deps_issues["nodes"].keys()),
                {"iss-00302", "iss-00303", "iss-00304", "iss-00305"},
            )

            node_302 = deps_issues["nodes"]["iss-00302"]
            node_304 = deps_issues["nodes"]["iss-00304"]
            node_305 = deps_issues["nodes"]["iss-00305"]
            self.assertEqual(node_302["ready"], False)
            self.assertEqual(node_302["depends_on"], ["iss-00303"])
            self.assertEqual(node_302["state"], "blocked")
            self.assertEqual(node_304["ready"], True)
            self.assertEqual(node_304["depends_on"], [])
            self.assertEqual(node_304["state"], "ready")
            self.assertEqual(node_305["ready"], True)
            self.assertEqual(node_305["depends_on"], [])
            self.assertEqual(node_305["state"], "ready")

            edge_pairs = [(edge["from"], edge["to"]) for edge in deps_issues["edges"]]
            self.assertEqual(edge_pairs, [("iss-00302", "iss-00303")])

            puml = deps_issues_puml_path.read_text(encoding="utf-8")
            self.assertIn("iss-00302", puml)
            self.assertIn("iss-00303", puml)
            self.assertIn("iss-00305", puml)
            self.assertNotIn("iss-00301", puml)
            self.assertIn("Niss_00303 --> Niss_00302 : blocks", puml)

    def test_sync_todo_projection_excludes_done_and_empty_branches(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Branch A: mixed done/open issues.
            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done prereq"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Open target"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open mid"],
            )

            # Branch B: done-only; should be removed from todo projection.
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Legacy platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Legacy epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Done legacy issue"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            (issues_root / "iss-00302-open-target" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [303]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (issues_root / "iss-00303-open-mid" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init A", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic A", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done prereq", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Open target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Open mid", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 102, "state": "OPEN", "title": "Init B", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Epic B", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "CLOSED", "title": "Done legacy", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            tree_todo = json.loads((target / "spec-dock" / ".agent" / "tree.json").read_text(encoding="utf-8"))
            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))

            self.assertIn("iss-00301", index_all["nodes"])  # done issue remains in all
            self.assertIn("iss-00401", index_all["nodes"])  # done-only branch remains in all

            # todo projection: done issues + empty ancestors are removed.
            todo_nodes = set(index_todo["nodes"].keys())
            self.assertNotIn("iss-00301", todo_nodes)
            self.assertNotIn("iss-00401", todo_nodes)
            self.assertNotIn("epic-00202", todo_nodes)
            self.assertNotIn("init-00102", todo_nodes)
            self.assertIn("iss-00302", todo_nodes)
            self.assertIn("iss-00303", todo_nodes)
            self.assertIn("epic-00201", todo_nodes)
            self.assertIn("init-00101", todo_nodes)

            # deps.issue_edges for todo keeps only edges with both endpoints in todo issues.
            self.assertEqual(
                index_todo["deps"]["issue_edges"],
                [{"from": "iss-00302", "to": "iss-00303", "kind": "depends_on"}],
            )

            # tree.json node set must match index.json todo node set.
            def collect_tree_ids(items: list[dict]) -> set[str]:
                ids: set[str] = set()
                for init_item in items:
                    ids.add(init_item["id"])
                    for epic_item in init_item.get("epics", []):
                        ids.add(epic_item["id"])
                        for issue_item in epic_item.get("issues", []):
                            ids.add(issue_item["id"])
                return ids

            self.assertEqual(collect_tree_ids(tree_todo["tree"]), todo_nodes)

            # deps-issues nodes should match todo issue set from index.json.
            todo_issue_ids = {
                node_id
                for node_id, item in index_todo["nodes"].items()
                if isinstance(item, dict) and item.get("type") == "issue"
            }
            self.assertEqual(set(deps_issues["nodes"].keys()), todo_issue_ids)

    def test_sync_emits_tree_puml_ready_board_at_spec_dock_root(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Blocked issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Ready issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Ready second"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "305", "--title", "Doing issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "306", "--title", "Unknown issue"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            (issues_root / "iss-00302-blocked-issue" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [303]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (issues_root / "iss-00304-ready-second" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p_active = self._run_runtime_capture(target, ["active", "set", "305", "--force", "--no-checkout"])
            self.assertEqual(p_active.returncode, 0, p_active.stdout + p_active.stderr)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Blocked", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Ready", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 304, "state": "OPEN", "title": "Ready2", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 305, "state": "OPEN", "title": "Doing", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            tree_all_puml_path = target / "spec-dock" / "tree-all.puml"
            tree_todo_puml_path = target / "spec-dock" / "tree.puml"
            self.assertTrue(tree_all_puml_path.is_file())
            self.assertTrue(tree_todo_puml_path.is_file())

            tree_all_puml = tree_all_puml_path.read_text(encoding="utf-8")
            self.assertIn("iss-00301\\n[DONE]", tree_all_puml)
            self.assertIn("iss-00302\\n[BLOCKED]", tree_all_puml)
            self.assertIn("iss-00303\\n[READY]", tree_all_puml)
            self.assertIn("iss-00305\\n[DOING]", tree_all_puml)
            self.assertIn("iss-00306\\n[UNKNOWN]", tree_all_puml)
            self.assertIn("blockers:", tree_all_puml)

            tree_todo_puml = tree_todo_puml_path.read_text(encoding="utf-8")
            self.assertNotIn("iss-00301", tree_todo_puml)
            self.assertIn("iss-00302", tree_todo_puml)
            self.assertIn("iss-00303", tree_todo_puml)
            self.assertIn("iss-00305", tree_todo_puml)
            self.assertIn("iss-00306", tree_todo_puml)

    def test_sync_emits_dashboard_md_at_spec_dock_root(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Blocked issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Ready issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "304", "--title", "Unknown issue"],
            )

            issues_root = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
            )
            (issues_root / "iss-00302-blocked-issue" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [303]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Blocked", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Ready", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            dashboard_path = target / "spec-dock" / "dashboard.md"
            self.assertTrue(dashboard_path.is_file())
            dashboard = dashboard_path.read_text(encoding="utf-8")
            self.assertIn("spec-dock/.agent/index.json", dashboard)
            self.assertIn("spec-dock/tree.puml", dashboard)
            self.assertIn("spec-dock/deps-issues.puml", dashboard)
            self.assertIn("## Ready", dashboard)
            self.assertIn("## Blocked", dashboard)
            self.assertIn("## Unknown", dashboard)
            self.assertIn("`iss-00303`", dashboard)
            self.assertIn("`iss-00302`", dashboard)
            self.assertIn("blockers: iss-00303", dashboard)
            self.assertIn("`iss-00304`", dashboard)
            self.assertNotIn("`iss-00301`", dashboard)

    def test_spec_dock_gitignore_ignores_human_facing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("tree-all.puml", gitignore)
            self.assertIn("tree.puml", gitignore)
            self.assertIn("deps-issues.puml", gitignore)
            self.assertIn("dashboard.md", gitignore)

    def test_new_rejects_duplicate_id_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            # Explicit --id must not allow creating a duplicated node id.
            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "issue",
                    "--no-github",
                    "--epic",
                    "1",
                    "--id",
                    "iss-local-00001",
                    "--title",
                    "Duplicate ID",
                ],
            )

    def test_new_rejects_duplicate_id_width_agnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["id"] = "iss-local-1"  # old-style width (should conflict with iss-local-00001)
            self._write_json_force(issue_meta, meta)

            # Even if the string differs, the numeric suffix must be treated as duplicated.
            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "issue",
                    "--no-github",
                    "--epic",
                    "1",
                    "--id",
                    "iss-local-00001",
                    "--title",
                    "Duplicate by numeric id",
                ],
            )

    def test_new_rejects_duplicate_github_issue_link_with_conflict_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--title", "Linked initiative", "--github-issue", "1"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--no-github", "--initiative", "init-local-00001", "--title", "JWT auth"],
            )

            p = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "epic-local-00001", "--title", "Add refresh token", "--github-issue", "1"],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("github.issue_number=1", p.stderr)
            self.assertIn("initiative:init-00001", p.stderr)
            self.assertIn("spec-dock/initiatives/init-00001-linked-initiative/.meta.json", p.stderr)
            self.assertIn("different GitHub issue number", p.stderr)
            self.assertNotIn("--github-issue", p.stderr)

            created = list((target / "spec-dock" / "initiatives").rglob("iss-00001-*"))
            self.assertEqual(created, [])

    def test_new_rejects_unsafe_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            # User-provided --slug must be safe for filesystem paths.
            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "issue",
                    "--no-github",
                    "--epic",
                    "1",
                    "--title",
                    "Custom slug test",
                    "--slug",
                    "bad slug!!",
                ],
            )

    def test_new_rejects_uppercase_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime_expect_fail(
                target,
                [
                    "new",
                    "initiative",
                    "--no-github",
                    "--title",
                    "Auth platform",
                    "--slug",
                    "Bad-Slug",
                ],
            )

    def test_new_derives_kebab_slug_from_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(
                target,
                ["new", "initiative", "--no-github", "--id", "init-local-00001", "--title", "Add Refresh Token"],
            )
            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-add-refresh-token"
            self.assertTrue(init_dir.is_dir())
            meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["slug"], "add-refresh-token")

    def test_new_rejects_invalid_slug_before_gh_issue_create(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--create-github-issue",
                    "--title",
                    "Add Refresh Token",
                    "--slug",
                    "Bad!Slug",
                ],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--slug", p.stderr)
            self.assertIn("expected regex", p.stderr)

            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")
            self.assertEqual(list((target / "spec-dock" / "initiatives").glob("*")), [])

    def test_validate_detects_broken_parent_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-local-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_detects_issue_initiative_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Payments platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["initiative_id"] = "init-local-00002"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_reports_invalid_meta_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            self._write_text_force(issue_meta, "[]\n")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("Invalid .meta.json", p.stderr)
            self.assertIn(str(issue_meta), p.stderr)

    def test_validate_detects_duplicate_github_issue_numbers_with_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / ".meta.json"
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1}
            self._write_json_force(issue_meta, issue_data)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate github.issue_number detected", p.stderr)
            self.assertIn("github.issue_number=1", p.stderr)
            self.assertIn("initiative:init-local-00001", p.stderr)
            self.assertIn("issue:iss-local-00001", p.stderr)
            self.assertIn("spec-dock/initiatives/init-local-00001-auth-platform/.meta.json", p.stderr)
            self.assertIn(
                "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json",
                p.stderr,
            )
            self.assertIn("Fix github.issue_number", p.stderr)

    def test_sync_fails_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-local-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["sync", "--no-update-active"])

    def test_sync_force_continues_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            self._run_runtime(target, ["sync", "--no-update-active"])
            agent_dir = target / "spec-dock" / ".agent"
            baseline_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertTrue(baseline_index["deps"]["valid"])
            self.assertEqual(baseline_index["deps"]["issue_edges"], [])
            self.assertIsNone(baseline_index["deps"]["error"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-local-99999"
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertEqual(index["deps"]["issue_edges"], [])
            self.assertIn("preflight validate failed", str(index["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index["warnings"])
            self.assertIsNone(index["nodes"]["iss-local-00001"]["deps"])

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertIn("preflight validate failed", str(tree["deps"]["error"]))

            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            self.assertFalse(deps_issues["deps"]["valid"])
            self.assertIn("preflight validate failed", str(deps_issues["deps"]["error"]))
            self.assertEqual(deps_issues["nodes"], {})
            self.assertEqual(deps_issues["edges"], [])

            tree_puml = (target / "spec-dock" / "tree.puml").read_text(encoding="utf-8")
            self.assertIn("deps_preflight_failed", tree_puml)
            self.assertIn("deps.valid=false", tree_puml)
            self.assertIn("--force", tree_puml)
            dashboard = (target / "spec-dock" / "dashboard.md").read_text(encoding="utf-8")
            self.assertIn("DEPS_DISABLED", dashboard)
            self.assertIn("deps_preflight_failed", dashboard)
            self.assertIn("deps.valid=false", dashboard)

            # Legacy v1 deps artifacts must always be removed.
            self.assertFalse((agent_dir / "deps.json").exists())
            self.assertFalse((agent_dir / "deps.puml").exists())
            self.assertFalse((agent_dir / "deps.todo.puml").exists())

    def test_sync_force_continues_when_meta_id_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["id"] = "broken-id"
            self._write_json_force(issue_meta, meta)

            agent_dir = target / "spec-dock" / ".agent"
            (agent_dir / "index.json").unlink(missing_ok=True)
            (agent_dir / "tree.json").unlink(missing_ok=True)
            (agent_dir / "index-all.json").unlink(missing_ok=True)
            (agent_dir / "tree-all.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())
            self.assertTrue((agent_dir / "index-all.json").is_file())
            self.assertTrue((agent_dir / "tree-all.json").is_file())

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("deps_preflight_failed", index["warnings"])
            self.assertEqual(index["deps"]["issue_edges"], [])

    def test_sync_force_does_not_update_active_from_branch(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Prepare a minimal git repository so `sync` can read the current branch name.
            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create nodes (local-only).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            # Branch name includes the node id. Without --force, `sync` would update active.
            self._run_git(target, ["checkout", "-b", "feature/iss-local-0001-test"])

            self._run_runtime(target, ["active", "clear"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsNone(active.get("issue"))

            self._run_runtime(target, ["sync", "--force"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsNone(active.get("issue"))

    def test_new_nodes_include_discussions_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
            for scope_dir in (init_dir, epic_dir, issue_dir):
                self.assertTrue((scope_dir / "discussions" / "rules.md").is_file())
                self.assertFalse((scope_dir / "adrs").exists())
                self.assertFalse((scope_dir / "artifacts").exists())
                self.assertEqual(list((scope_dir / "discussions").glob("new-*")), [])

    def test_new_doc_adr_increments_id_within_scope_discussions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-local-00001", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-local-00001", "--title", "Decision two"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            self.assertNotEqual(sorted(discussions_dir.glob("001-adr-*.md")), [])
            self.assertNotEqual(sorted(discussions_dir.glob("002-adr-*.md")), [])
            self.assertEqual(list(issue_dir.glob("adrs")), [])

    def test_new_doc_adr_uses_shared_sequence_across_discussion_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "iss-local-00001", "--title", "Discussion one"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-local-00001", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "research", "--issue", "iss-local-00001", "--title", "Research one"])
            self._run_runtime(target, ["new", "doc", "note", "--issue", "iss-local-00001", "--title", "Note one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            self.assertNotEqual(sorted(discussions_dir.glob("001-disc-*.md")), [])
            self.assertNotEqual(sorted(discussions_dir.glob("002-adr-*.md")), [])
            self.assertNotEqual(sorted(discussions_dir.glob("003-research-*.md")), [])
            self.assertNotEqual(sorted(discussions_dir.glob("004-note-*.md")), [])

    def test_new_doc_disc_increments_after_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])
            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-local-00001", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "iss-local-00001", "--title", "Discussion one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            self.assertNotEqual(sorted(discussions_dir.glob("001-adr-*.md")), [])
            self.assertNotEqual(sorted(discussions_dir.glob("002-disc-*.md")), [])

    def test_new_doc_ignores_nonconforming_files_for_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "adr-00001-legacy.md").write_text("legacy\n", encoding="utf-8")
            (discussions_dir / "foo.md").write_text("nonconforming\n", encoding="utf-8")
            (discussions_dir / "002-bogus-random.md").write_text("nonconforming type\n", encoding="utf-8")
            (discussions_dir / "009-disc-migrated.md").write_text("existing new format\n", encoding="utf-8")
            (discussions_dir / "1000-adr-legacy-overflow.md").write_text("4-digit should be ignored\n", encoding="utf-8")

            self._run_runtime(target, ["new", "doc", "adr", "--issue", "iss-local-00001", "--title", "Decision one"])

            self.assertNotEqual(sorted(discussions_dir.glob("010-adr-*.md")), [])
            self.assertEqual(list(discussions_dir.glob("001-adr-*.md")), [])

    def test_new_doc_fails_on_duplicate_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--issue", "iss-local-00001", "--title", "Note one"],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate discussion sequence", p.stderr)
            self.assertEqual(list(discussions_dir.glob("002-note-*.md")), [])

    def test_new_doc_fails_on_sequence_overflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            (discussions_dir / "999-disc-capacity-limit.md").write_text("maxed\n", encoding="utf-8")

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "adr", "--issue", "iss-local-00001", "--title", "Decision one"],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Discussion sequence overflow", p.stderr)
            self.assertIn("follow-up issue", p.stderr)
            self.assertIn("archive", p.stderr)
            self.assertIn("extend sequence width", p.stderr)
            self.assertEqual(list(discussions_dir.glob("1000-adr-*.md")), [])

    def test_new_doc_rejects_invalid_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "doc",
                    "adr",
                    "--issue",
                    "iss-local-00001",
                    "--title",
                    "Decision one",
                    "--slug",
                    "Bad!Slug",
                ],
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--slug", p.stderr)
            self.assertIn("expected regex", p.stderr)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            self.assertEqual(list(discussions_dir.glob("001-adr-*.md")), [])

    def test_new_doc_rejects_unexpected_sequence_override_option(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(
                target,
                [
                    "new",
                    "doc",
                    "adr",
                    "--issue",
                    "iss-local-00001",
                    "--seq",
                    "1",
                    "--title",
                    "Decision one",
                ],
            )
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("unrecognized arguments: --seq 1", p.stderr)

    def test_new_discussion_per_type_commands_are_not_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            for per_type in ("adr", "disc", "research", "note"):
                p = self._run_runtime_capture(
                    target,
                    ["new", per_type, "--issue", "iss-local-00001", "--title", "Doc title"],
                )
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn(f"invalid choice: '{per_type}'", p.stderr)

    def test_new_help_exposes_only_doc_discussion_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p_new = self._run_runtime_capture(target, ["new", "--help"])
            self.assertEqual(p_new.returncode, 0, p_new.stdout + p_new.stderr)
            self.assertIn(" doc ", p_new.stdout)
            self.assertNotIn("\n    adr", p_new.stdout)
            self.assertNotIn("\n    disc", p_new.stdout)
            self.assertNotIn("\n    research", p_new.stdout)
            self.assertNotIn("\n    note", p_new.stdout)

            p_doc = self._run_runtime_capture(target, ["new", "doc", "--help"])
            self.assertEqual(p_doc.returncode, 0, p_doc.stdout + p_doc.stderr)
            self.assertIn("adr", p_doc.stdout)
            self.assertIn("disc", p_doc.stdout)
            self.assertIn("research", p_doc.stdout)
            self.assertIn("note", p_doc.stdout)
            self.assertNotIn("--id", p_doc.stdout)
            self.assertNotIn("--seq", p_doc.stdout)

    def test_internal_issue_status_resolution_marks_cached_source(self) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "spec_dock"
            / "assets"
            / "spec_dock"
            / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime import app as runtime_app
        finally:
            sys.path.pop(0)

        nodes = {
            "iss-00301": SimpleNamespace(
                id="iss-00301",
                type="issue",
                github_issue_number=301,
                epic_id="epic-00201",
                initiative_id="init-00101",
            )
        }
        resolved = runtime_app._resolve_issue_statuses(
            nodes,
            github=False,
            issue_index={},
            cached_issue_status_by_id={"iss-00301": "done"},
        )

        self.assertEqual(resolved["iss-00301"].status, "done")
        self.assertEqual(resolved["iss-00301"].source, "cache")

    def test_new_doc_rejects_unknown_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(
                target,
                ["new", "doc", "unknown", "--issue", "iss-local-00001", "--title", "Doc title"],
            )
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("invalid choice: 'unknown'", p.stderr)

    def test_new_nodes_do_not_generate_readme_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            readmes = list(init_dir.rglob("README.md"))
            self.assertEqual(readmes, [])

    def test_wrappers_are_executable(self) -> None:
        if os.name == "nt":
            self.skipTest("Wrapper executable bit checks are for macOS/Linux only.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"

            wrappers = [
                init_dir / "epics" / "new-epic",
                epic_dir / "issues" / "new-issue",
            ]
            for wrapper in wrappers:
                self.assertTrue(wrapper.is_file(), f"missing wrapper: {wrapper}")
                self.assertTrue(os.access(wrapper, os.X_OK), f"wrapper is not executable: {wrapper}")

    def test_new_epic_wrapper_creates_local_epic(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"

            bin_dir = target / ".bin-no-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for cmd in ("bash", "python3", "dirname"):
                cmd_path = shutil.which(cmd)
                self.assertIsNotNone(cmd_path, f"{cmd} not available")
                link_path = bin_dir / cmd
                try:
                    os.symlink(cmd_path, link_path)
                except OSError:
                    shutil.copy2(cmd_path, link_path)
                    link_path.chmod(0o755)

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"], env={"PATH": str(bin_dir)})
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertTrue((init_dir / "epics" / "epic-local-00001-jwt-auth" / ".meta.json").is_file())

    def test_new_issue_wrapper_creates_github_issue_by_default(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            wrapper = epic_dir / "issues" / "new-issue"

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            p = self._run_wrapper_capture(
                wrapper,
                ["Add refresh token"],
                env={"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"},
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            issue_meta_path = epic_dir / "issues" / "iss-00123-add-refresh-token" / ".meta.json"
            self.assertTrue(issue_meta_path.is_file())
            issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(issue_meta["id"], "iss-00123")
            self.assertEqual(issue_meta["github"]["issue_number"], 123)

    def test_new_nodes_do_not_include_new_adr_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            self.assertFalse((issue_dir / "adrs").exists())
            self.assertFalse((issue_dir / "discussions" / "new-adr").exists())

    def test_wrappers_reject_invalid_args(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
            wrappers = [
                init_dir / "epics" / "new-epic",
                epic_dir / "issues" / "new-issue",
            ]

            for wrapper in wrappers:
                p0 = self._run_wrapper_capture(wrapper, [])
                self.assertNotEqual(p0.returncode, 0)
                self.assertIn("usage:", p0.stderr)

                p2 = self._run_wrapper_capture(wrapper, ["one", "two"])
                self.assertNotEqual(p2.returncode, 0)
                self.assertIn("usage:", p2.stderr)

    def test_wrapper_fails_when_meta_missing_or_invalid(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"
            meta_path = init_dir / ".meta.json"

            meta_path.unlink()
            p_missing = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p_missing.returncode, 0)
            self.assertIn("missing .meta.json", p_missing.stderr)

            self._write_text_force(meta_path, "{ invalid json")
            p_invalid = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p_invalid.returncode, 0)
            self.assertIn("invalid .meta.json", p_invalid.stderr)

    def test_wrapper_fails_when_only_legacy_meta_json_exists(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"
            dot_meta_path = init_dir / ".meta.json"
            legacy_meta_path = init_dir / "meta.json"

            dot_meta_path.rename(legacy_meta_path)
            self.assertTrue(legacy_meta_path.is_file())
            self.assertFalse(dot_meta_path.exists())

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("missing .meta.json", p.stderr)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())
            self.assertFalse((init_dir / "epics" / "epic-local-00001-jwt-auth" / ".meta.json").is_file())

    def test_wrapper_fails_when_runtime_not_found(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"
            runtime_script = target / "spec-dock" / "scripts" / "spec-dock"
            runtime_backup = target / "spec-dock" / "scripts" / "spec-dock.bak"
            runtime_script.rename(runtime_backup)

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("runtime script not found", p.stderr)
            self.assertIn("spec-dock init", p.stderr)

    def test_runtime_entrypoint_fails_fast_when_runtime_module_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            runtime_app = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py"
            runtime_backup = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py.bak"
            runtime_app.rename(runtime_backup)

            p = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("runtime module missing", p.stderr)
            self.assertIn("spec-dock update", p.stderr)

    def test_new_epic_wrapper_does_not_require_gh_even_with_github_parent(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--github-issue", "123", "--title", "Auth platform"])

            init_dir = target / "spec-dock" / "initiatives" / "init-00123-auth-platform"
            wrapper = init_dir / "epics" / "new-epic"

            bin_dir = target / ".bin-no-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for cmd in ("bash", "python3", "dirname"):
                cmd_path = shutil.which(cmd)
                self.assertIsNotNone(cmd_path, f"{cmd} not available")
                link_path = bin_dir / cmd
                try:
                    os.symlink(cmd_path, link_path)
                except OSError:
                    shutil.copy2(cmd_path, link_path)
                    link_path.chmod(0o755)

            p = self._run_wrapper_capture(wrapper, ["JWT Auth"], env={"PATH": str(bin_dir)})
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertTrue((init_dir / "epics" / "epic-local-00001-jwt-auth" / ".meta.json").is_file())

    def test_new_issue_wrapper_fails_without_gh_and_shows_guidance(self) -> None:
        if os.name == "nt":
            self.skipTest("This test executes bash wrapper scripts; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            wrapper = epic_dir / "issues" / "new-issue"

            bin_dir = target / ".bin-no-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for cmd in ("bash", "python3", "dirname"):
                cmd_path = shutil.which(cmd)
                self.assertIsNotNone(cmd_path, f"{cmd} not available")
                link_path = bin_dir / cmd
                try:
                    os.symlink(cmd_path, link_path)
                except OSError:
                    shutil.copy2(cmd_path, link_path)
                    link_path.chmod(0o755)

            p = self._run_wrapper_capture(wrapper, ["Add refresh token"], env={"PATH": str(bin_dir)})
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("option 1)", p.stderr)
            self.assertIn("option 2)", p.stderr)
            self.assertIn("--no-github", p.stderr)
            self.assertEqual(list((epic_dir / "issues").glob("iss-*")), [])

    def test_active_set_initiative_and_epic_keep_missing_layers_as_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create a minimal local tree.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            # Initiative-only active: epic/issue are placeholders.
            self._run_runtime(target, ["active", "set", "init-local-00001", "--force"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsInstance(active.get("initiative"), dict)
            self.assertIsNone(active.get("epic"))
            self.assertIsNone(active.get("issue"))
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("Active Epic: （なし）", self._read_active_pointer_text(target, "epic", "README.md"))
            self.assertIn("Active Issue: （なし）", self._read_active_pointer_text(target, "issue", "README.md"))

            # Epic-only active: issue is a placeholder.
            self._run_runtime(target, ["active", "set", "epic-local-00001", "--force"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsInstance(active.get("initiative"), dict)
            self.assertIsInstance(active.get("epic"), dict)
            self.assertIsNone(active.get("issue"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("Active Issue: （なし）", self._read_active_pointer_text(target, "issue", "README.md"))

            # Clear: all placeholders.
            self._run_runtime(target, ["active", "clear"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsNone(active.get("initiative"))
            self.assertIsNone(active.get("epic"))
            self.assertIsNone(active.get("issue"))
            self.assertIn("Active Initiative: （なし）", self._read_active_pointer_text(target, "initiative", "README.md"))
            self.assertIn("Active Epic: （なし）", self._read_active_pointer_text(target, "epic", "README.md"))
            self.assertIn("Active Issue: （なし）", self._read_active_pointer_text(target, "issue", "README.md"))

    def test_sync_updates_active_from_branch_id(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Prepare a minimal git repository so `sync` can read the current branch name.
            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create nodes (local-only).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            # Branch name includes the node id.
            self._run_git(target, ["checkout", "-b", "feature/iss-local-0001-test"])

            self._run_runtime(target, ["sync"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["initiative"]["id"], "init-local-00001")
            self.assertEqual(active["epic"]["id"], "epic-local-00001")
            self.assertEqual(active["issue"]["id"], "iss-local-00001")

    def test_sync_github_populates_issue_statuses(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Rotate refresh token"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Issue 301", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Issue 302", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index_all["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "done")
            self.assertEqual(nodes["iss-00301"]["github"]["state"], "CLOSED")
            self.assertEqual(nodes["iss-00302"]["status"], "open")
            self.assertEqual(nodes["iss-00302"]["github"]["state"], "OPEN")
            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertNotIn("iss-00301", index_todo["nodes"])

    def test_sync_generates_index_deps_and_deps_issues_artifacts(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "303", "--title", "Open blocker"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            done_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00301-dep-issue"
            )
            (done_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [303]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            self.assertTrue(index_all["deps"]["valid"])
            self.assertIsNone(index_all["deps"]["error"])
            self.assertEqual(
                index_all["deps"]["issue_edges"],
                [
                    {"from": "iss-00301", "to": "iss-00303", "kind": "depends_on"},
                    {"from": "iss-00302", "to": "iss-00301", "kind": "depends_on"},
                ],
            )
            self.assertEqual(index_all["nodes"]["iss-00301"]["deps"]["depends_on"], [])
            self.assertTrue(index_all["nodes"]["iss-00301"]["deps"]["ready"])

            index_todo = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            self.assertTrue(index_todo["deps"]["valid"])
            self.assertIsNone(index_todo["deps"]["error"])
            self.assertEqual(index_todo["deps"]["issue_edges"], [])
            nodes = index_todo["nodes"]
            self.assertNotIn("iss-00301", nodes)
            self.assertEqual(nodes["iss-00302"]["deps"]["depends_on"], [])
            self.assertTrue(nodes["iss-00302"]["deps"]["ready"])

            deps_issues_path = target / "spec-dock" / ".agent" / "deps-issues.json"
            deps_issues_puml_path = target / "spec-dock" / "deps-issues.puml"
            self.assertTrue(deps_issues_path.is_file())
            self.assertTrue(deps_issues_puml_path.is_file())
            deps_issues = json.loads(deps_issues_path.read_text(encoding="utf-8"))
            self.assertTrue(deps_issues["deps"]["valid"])
            self.assertIsNone(deps_issues["deps"]["error"])
            self.assertNotIn("iss-00301", deps_issues["nodes"])  # done issue is filtered from todo projection
            self.assertIn("iss-00302", deps_issues["nodes"])
            self.assertIn("iss-00303", deps_issues["nodes"])

            deps_issues_puml = deps_issues_puml_path.read_text(encoding="utf-8")
            self.assertIn("iss-00302", deps_issues_puml)
            self.assertIn("iss-00303", deps_issues_puml)
            self.assertNotIn("iss-00301", deps_issues_puml)

            # Legacy v1 deps artifacts are no longer generated.
            self.assertFalse((target / "spec-dock" / ".agent" / "deps.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "deps.puml").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "deps.todo.puml").exists())

    def test_sync_deps_progress_aggregation_for_epic_and_initiative(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "OAuth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "303", "--title", "Second epic issue"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Epic2", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 303, "state": "OPEN", "title": "Second", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["epic-00201"]["progress"], {"total": 2, "done": 1, "open": 1, "unknown": 0})
            self.assertEqual(nodes["epic-00202"]["progress"], {"total": 1, "done": 0, "open": 1, "unknown": 0})
            self.assertEqual(nodes["init-00101"]["progress"], {"total": 3, "done": 1, "open": 2, "unknown": 0})
            self.assertEqual(nodes["iss-00301"]["status"], "done")
            self.assertEqual(nodes["iss-00302"]["status"], "open")
            self.assertEqual(nodes["iss-00303"]["status"], "open")

    def test_sync_deps_empty_epic_and_initiative_are_done_and_non_blocking(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Empty init"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Empty epic"],
            )
            self._run_runtime(target, ["new", "initiative", "--github-issue", "102", "--title", "Work init"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "102", "--github-issue", "202", "--title", "Work epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "301", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00102-work-init"
                / "epics"
                / "epic-00202-work-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [201]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Empty init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Empty epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 102, "state": "OPEN", "title": "Work init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Work epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["epic-00201"]["progress"], {"total": 0, "done": 0, "open": 0, "unknown": 0})
            self.assertEqual(nodes["init-00101"]["progress"], {"total": 0, "done": 0, "open": 0, "unknown": 0})
            self.assertTrue(nodes["iss-00301"]["deps"]["ready"])
            self.assertEqual(nodes["iss-00301"]["deps"]["depends_on"], [])
            self.assertEqual(nodes["iss-00301"]["deps"]["blockers_top"], [])

    def test_sync_deps_ignores_parent_github_closed_for_done(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "CLOSED", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "CLOSED", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["epic-00201"]["progress"], {"total": 2, "done": 0, "open": 2, "unknown": 0})
            self.assertEqual(nodes["init-00101"]["progress"], {"total": 2, "done": 0, "open": 2, "unknown": 0})
            self.assertFalse(nodes["iss-00302"]["deps"]["ready"])
            self.assertEqual(nodes["iss-00302"]["deps"]["depends_on"], ["iss-00301"])

    def test_sync_deps_active_leaf_makes_epic_and_initiative_doing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Active issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Sibling issue"],
            )
            self._run_runtime(target, ["active", "set", "iss-00301", "--force"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Active", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Sibling", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            nodes = deps_issues["nodes"]
            self.assertEqual(nodes["iss-00301"]["state"], "doing")
            self.assertEqual(nodes["iss-00302"]["state"], "ready")

    def test_sync_deps_active_epic_makes_initiative_doing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Child issue"],
            )
            self._run_runtime(target, ["active", "set", "epic-00201", "--force"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Child", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            deps_issues = json.loads((target / "spec-dock" / ".agent" / "deps-issues.json").read_text(encoding="utf-8"))
            nodes = deps_issues["nodes"]
            self.assertEqual(nodes["iss-00301"]["state"], "ready")

    def test_sync_github_passes_gh_limit_to_gh(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[{"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"}],
                log_path=log_path,
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["sync", "--github", "--gh-limit", "123", "--no-update-active"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            self.assertTrue(log_path.is_file())
            lines = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertNotEqual(lines, [])
            argv = lines[-1].split()
            self.assertIn("--limit", argv)
            i = argv.index("--limit")
            self.assertLess(i + 1, len(argv))
            self.assertEqual(argv[i + 1], "123")

    def test_sync_github_index_incomplete_warns_and_marks_unknown(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            # Missing 301 on purpose.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("gh_index_incomplete", p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "unknown")
            self.assertEqual(nodes["iss-00301"]["github"], {"issue_number": 301})

    def test_sync_github_fetch_failure_warns_and_continues(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("gh_fetch_failed", p.stderr)

            index = json.loads((target / "spec-dock" / ".agent" / "index.json").read_text(encoding="utf-8"))
            nodes = index["nodes"]
            self.assertEqual(nodes["iss-00301"]["status"], "unknown")

    def test_deps_check_no_deps_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertIn("spec-dock: blocked (deps check)", p.stderr)
            self.assertIn("ready=false", p.stderr)

    def test_deps_check_returns_ready_and_blockers_and_closure_json(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Open blocker"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "402", "--title", "Done issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "203", "--title", "Transitive epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "203", "--github-issue", "403", "--title", "Transitive blocker"],
            )

            main_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (main_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-00202"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            blocker_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00202-deps-epic"
                / "issues"
                / "iss-00401-open-blocker"
            )
            (blocker_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [403]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 203, "state": "OPEN", "title": "Trans epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 402, "state": "CLOSED", "title": "Done", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 403, "state": "OPEN", "title": "Transitive", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00301", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(
                list(data.keys()),
                ["schema_version", "target", "ready", "effective_depends_on", "blockers", "nodes", "warnings"],
            )
            self.assertEqual(data["target"], "iss-00301")
            self.assertFalse(data["ready"])
            self.assertEqual(data["effective_depends_on"], ["iss-00401", "iss-00403"])
            self.assertEqual(data["blockers"], ["iss-00401", "iss-00403"])
            self.assertEqual(data["warnings"], [])

    def test_deps_check_without_github_uses_index_snapshot_when_present(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)

            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00301"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00301"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            guard_log = bin_dir / "gh-guard.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertFalse(guard_log.exists(), "gh must not be invoked without --github")
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")

    def test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            (target / "spec-dock" / ".agent" / "index-all.json").unlink(missing_ok=True)
            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertFalse(data["ready"])
            self.assertEqual(data["blockers"], ["iss-00301"])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "unknown")

    def test_deps_check_missing_target_is_argparse_exit_2_not_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            p = self._run_runtime_capture(target, ["deps", "check"])
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)

    def test_deps_check_accepts_github_number_forms_and_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Add refresh token"],
            )

            forms = [
                "301",
                "#301",
                "https://github.com/example/repo/issues/301",
            ]
            for form in forms:
                p = self._run_runtime_capture(target, ["deps", "check", form, "--json"])
                self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
                data = json.loads(p.stdout)
                self.assertEqual(data["target"], "iss-00301")
                self.assertFalse(data["ready"])

    def test_deps_check_github_ready_when_deps_closed(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["effective_depends_on"], [])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")

    def test_deps_check_without_github_uses_synced_index_status(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)

            # Guard: `deps check` without --github must not fetch GitHub.
            guard_log = bin_dir / "gh-guard.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertFalse(guard_log.exists(), "gh must not be invoked without --github")
            data = json.loads(p.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")

    def test_deps_check_without_github_missing_index_defaults_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertFalse(data["ready"])
            self.assertEqual(data["blockers"], ["iss-00301"])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "unknown")

    def test_deps_check_github_blocked_when_dep_open(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertFalse(data["ready"])
            self.assertEqual(data["effective_depends_on"], ["iss-00301"])
            self.assertEqual(data["blockers"], ["iss-00301"])

    def test_deps_check_github_index_incomplete_warns_and_blocks(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            # Missing 301 on purpose.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertEqual(p.stderr.strip(), "")
            data = json.loads(p.stdout)
            self.assertIn("gh_index_incomplete", data["warnings"])
            self.assertEqual(data["blockers"], ["iss-00301"])

    def test_deps_check_github_fetch_failure_warns_and_blocks(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--github", "--json"], env=test_env)
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            self.assertEqual(p.stderr.strip(), "")
            data = json.loads(p.stdout)
            self.assertIn("gh_fetch_failed", data["warnings"])
            self.assertEqual(data["blockers"], ["iss-00301"])

    def test_deps_check_json_stdout_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            json.loads(p.stdout)  # must be valid JSON
            self.assertEqual(p.stderr.strip(), "")

    def test_deps_check_missing_deps_json_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], [])

    def test_deps_json_parse_error_fails_with_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            (issue_dir / "deps.json").write_text("{\n", encoding="utf-8")  # invalid JSON

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("deps.json", p.stderr)
            self.assertIn("Invalid JSON", p.stderr)

    def test_deps_json_schema_error_fails_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 2, "depends_on": []}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("deps.json", p.stderr)
            self.assertIn("schema_version", p.stderr)

    def test_deps_json_schema_rejects_boolean_dep_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [True]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("deps.json", p.stderr)
            self.assertIn("depends_on[0]", p.stderr)

    def test_deps_unresolved_ref_reports_ref_and_deps_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-issue-one"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-99999"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-99999", p.stderr)
            self.assertIn("deps.json", p.stderr)

    def test_deps_canonicalizes_width_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue two"])

            issue_two_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00002-issue-two"
            )
            (issue_two_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-1"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00002", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], ["iss-local-00001"])

    def test_deps_github_number_requires_imported_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-issue-one"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [123]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("123", p.stderr)
            self.assertIn("deps.json", p.stderr)

    def test_deps_effective_depends_on_merges_parents_and_dedups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep two"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])

            # Dependency targets must not be within the same hierarchy, otherwise parent-merge would
            # create a self-dependency for that issue. Create an external dep issue.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "External deps"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "2", "--title", "External epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "External issue"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            target_issue_dir = epic_dir / "issues" / "iss-local-00003-target"

            # Parent initiative/epic both depend on the same dep (dedup expected).
            (init_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-4"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (epic_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00004"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00003", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], ["iss-local-00002", "iss-local-00004"])

    def test_deps_effective_depends_on_merges_epic_and_initiative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Dep two"])

            # External deps (must not be under the same parents as the target epic).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "External deps"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "2", "--title", "External epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "External issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "External issue two"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"

            (init_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (epic_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00004"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "epic-local-00001", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["effective_depends_on"], ["iss-local-00003", "iss-local-00004"])

    def test_deps_self_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-issue-one"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-00001", p.stderr)
            self.assertIn("self edge produced", p.stderr)

    def test_deps_descendant_dependency_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            deps_path = init_dir / "deps.json"
            deps_path.write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "init-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn(str(deps_path), p.stderr)
            self.assertIn("iss-local-00001", p.stderr)

    def test_deps_cycle_detected_in_reachable_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue one"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Issue two"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            issue_one_dir = epic_dir / "issues" / "iss-local-00001-issue-one"
            issue_two_dir = epic_dir / "issues" / "iss-local-00002-issue-two"

            (issue_one_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (issue_two_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-00001", p.stderr)
            self.assertIn("iss-local-00002", p.stderr)
            self.assertIn("->", p.stderr)

    def test_deps_check_ignores_unreachable_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle b"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-local-00002-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-local-00003-cycle-b"
            (cycle_a_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (cycle_b_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("Dependency cycle detected", p.stderr)
            self.assertIn("iss-local-00002", p.stderr)
            self.assertIn("iss-local-00003", p.stderr)

    def test_sync_fails_on_deps_structural_error_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle b"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-local-00002-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-local-00003-cycle-b"
            (cycle_a_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (cycle_b_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-local-00002", p.stderr)
            self.assertIn("iss-local-00003", p.stderr)
            self.assertIn("->", p.stderr)

    def test_sync_force_sets_deps_valid_false_and_emits_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle a"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle b"])

            agent_dir = target / "spec-dock" / ".agent"
            self._run_runtime(target, ["sync", "--no-update-active"])
            baseline_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertTrue(baseline_index["deps"]["valid"])
            self.assertEqual(baseline_index["deps"]["issue_edges"], [])
            self.assertIsNone(baseline_index["deps"]["error"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            cycle_a_dir = epic_dir / "issues" / "iss-local-00002-cycle-a"
            cycle_b_dir = epic_dir / "issues" / "iss-local-00003-cycle-b"
            (cycle_a_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00003"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (cycle_b_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            (agent_dir / "index.json").unlink(missing_ok=True)
            (agent_dir / "tree.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())
            self.assertTrue((agent_dir / "index-all.json").is_file())
            self.assertTrue((agent_dir / "tree-all.json").is_file())

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertEqual(index["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(index["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index["warnings"])
            self.assertIsNone(index["nodes"]["iss-local-00001"]["deps"])
            self.assertIsNone(index["nodes"]["iss-local-00002"]["deps"])
            self.assertIsNone(index["nodes"]["iss-local-00003"]["deps"])

            index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            self.assertFalse(index_all["deps"]["valid"])
            self.assertEqual(index_all["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(index_all["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index_all["warnings"])
            self.assertIsNone(index_all["nodes"]["iss-local-00001"]["deps"])
            self.assertIsNone(index_all["nodes"]["iss-local-00002"]["deps"])
            self.assertIsNone(index_all["nodes"]["iss-local-00003"]["deps"])

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertEqual(tree["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(tree["deps"]["error"]))
            self.assertIn("deps_preflight_failed", tree["warnings"])
            tree_issues = tree["tree"][0]["epics"][0]["issues"]
            tree_issue_deps = {issue["id"]: issue.get("deps") for issue in tree_issues}
            self.assertIsNone(tree_issue_deps["iss-local-00001"])
            self.assertIsNone(tree_issue_deps["iss-local-00002"])
            self.assertIsNone(tree_issue_deps["iss-local-00003"])

            tree_all = json.loads((agent_dir / "tree-all.json").read_text(encoding="utf-8"))
            self.assertFalse(tree_all["deps"]["valid"])
            self.assertEqual(tree_all["deps"]["issue_edges"], [])
            self.assertIn("Dependency cycle detected", str(tree_all["deps"]["error"]))
            self.assertIn("deps_preflight_failed", tree_all["warnings"])
            tree_all_issues = tree_all["tree"][0]["epics"][0]["issues"]
            tree_all_issue_deps = {issue["id"]: issue.get("deps") for issue in tree_all_issues}
            self.assertIsNone(tree_all_issue_deps["iss-local-00001"])
            self.assertIsNone(tree_all_issue_deps["iss-local-00002"])
            self.assertIsNone(tree_all_issue_deps["iss-local-00003"])

            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            self.assertFalse(deps_issues["deps"]["valid"])
            self.assertIn("Dependency cycle detected", str(deps_issues["deps"]["error"]))
            self.assertEqual(deps_issues["nodes"], {})
            self.assertEqual(deps_issues["edges"], [])

            tree_all_puml = (target / "spec-dock" / "tree-all.puml").read_text(encoding="utf-8")
            tree_todo_puml = (target / "spec-dock" / "tree.puml").read_text(encoding="utf-8")
            deps_issues_puml = (target / "spec-dock" / "deps-issues.puml").read_text(encoding="utf-8")
            dashboard = (target / "spec-dock" / "dashboard.md").read_text(encoding="utf-8")
            for text in (tree_all_puml, tree_todo_puml, deps_issues_puml, dashboard):
                self.assertIn("deps_preflight_failed", text)
                self.assertIn("deps.valid=false", text)
                self.assertIn("--force", text)

            self.assertFalse((agent_dir / "deps.json").exists())
            self.assertFalse((agent_dir / "deps.puml").exists())
            self.assertFalse((agent_dir / "deps.todo.puml").exists())

    def test_sync_force_removes_legacy_v1_deps_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target"])

            agent_dir = target / "spec-dock" / ".agent"
            agent_dir.mkdir(parents=True, exist_ok=True)
            (agent_dir / "deps.json").write_text("{\"stale\": true}\n", encoding="utf-8")
            (agent_dir / "deps.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")
            (agent_dir / "deps.todo.puml").write_text("@startuml\n@enduml\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            self.assertFalse((agent_dir / "deps.json").exists())
            self.assertFalse((agent_dir / "deps.puml").exists())
            self.assertFalse((agent_dir / "deps.todo.puml").exists())

    def test_deps_commands_do_not_mutate_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            before = issue_meta.read_text(encoding="utf-8")
            p = self._run_runtime_capture(target, ["deps", "check", "iss-local-00001", "--json"])
            self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
            after = issue_meta.read_text(encoding="utf-8")
            self.assertEqual(after, before)

    def test_sync_and_validate_do_not_backfill_or_relock_existing_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / ".meta.json"
            )
            epic_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / ".meta.json"
            )
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta_paths = [init_meta_path, epic_meta_path, issue_meta_path]

            before_texts: dict[Path, str] = {}
            before_modes: dict[Path, int] = {}

            for meta_path in meta_paths:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta.pop("_spec_dock", None)
                self._write_json_force(meta_path, meta)
                if os.name == "posix":
                    try:
                        meta_path.chmod(meta_path.stat().st_mode | 0o200)
                    except OSError:
                        pass

                before_text = meta_path.read_text(encoding="utf-8")
                before_texts[meta_path] = before_text
                self.assertNotIn("_spec_dock", json.loads(before_text))
                if os.name == "posix":
                    before_modes[meta_path] = meta_path.stat().st_mode

            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync"])

            for meta_path in meta_paths:
                after_text = meta_path.read_text(encoding="utf-8")
                self.assertEqual(after_text, before_texts[meta_path])
                self.assertNotIn("_spec_dock", json.loads(after_text))
                if os.name == "posix":
                    after_mode = meta_path.stat().st_mode
                    self.assertEqual(after_mode, before_modes[meta_path])
                    self.assertEqual(after_mode & 0o222, before_modes[meta_path] & 0o222)

    def test_validate_and_sync_fail_fast_on_legacy_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"
            self.assertTrue(dot_meta_path.is_file())

            meta = json.loads(dot_meta_path.read_text(encoding="utf-8"))
            meta.pop("_spec_dock", None)
            self._write_json_force(dot_meta_path, meta)
            if os.name == "posix":
                dot_meta_path.chmod(dot_meta_path.stat().st_mode | 0o200)

            before_text = dot_meta_path.read_text(encoding="utf-8")
            dot_meta_path.rename(legacy_meta_path)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0)
            self.assertIn("Unsupported legacy meta.json detected", p_validate.stderr)
            self.assertIn(str(legacy_meta_path), p_validate.stderr)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())
            self.assertEqual(legacy_meta_path.read_text(encoding="utf-8"), before_text)

            p_sync = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p_sync.returncode, 0)
            self.assertIn("Unsupported legacy meta.json detected", p_sync.stderr)
            self.assertIn(str(legacy_meta_path), p_sync.stderr)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())
            self.assertEqual(legacy_meta_path.read_text(encoding="utf-8"), before_text)

    def test_validate_and_sync_fail_fast_when_dot_meta_and_legacy_coexist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"

            before_text = dot_meta_path.read_text(encoding="utf-8")
            legacy_meta_path.write_text("{ invalid legacy json\n", encoding="utf-8")

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0, p_validate.stdout + p_validate.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_validate.stderr)
            self.assertIn(str(legacy_meta_path), p_validate.stderr)

            self.assertEqual(dot_meta_path.read_text(encoding="utf-8"), before_text)
            self.assertTrue(legacy_meta_path.is_file())

            p_sync = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_sync.stderr)
            self.assertIn(str(legacy_meta_path), p_sync.stderr)

            self.assertEqual(dot_meta_path.read_text(encoding="utf-8"), before_text)
            self.assertTrue(legacy_meta_path.is_file())

    def test_active_set_rejects_legacy_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Legacy flags were removed in favor of a single `target` argument.
            self._run_runtime_expect_fail(target, ["active", "set", "--issue", "1"])

    def test_active_set_github_issue_checkout_sets_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create parent nodes locally, but link the issue to an existing GitHub issue number.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Provide a fake `gh` binary outside the git repo (keep working tree clean).
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ \"$1\" == \"issue\" && \"$2\" == \"checkout\" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                self._run_runtime(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00123-add-refresh-token")
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00123")

    def test_active_set_local_only_node_does_not_rename_branch(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            self._run_git(target, ["checkout", "-b", "feature/local-keep-branch"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])
            self._run_runtime(target, ["active", "set", "iss-local-00001", "--force"])

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "feature/local-keep-branch")

    def test_active_set_detached_head_creates_desired_branch(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(
                target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"]
            )
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            self._run_git(target, ["checkout", "--detach"])
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "HEAD")

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

            desired = "iss-00123-add-refresh-token"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, desired)

    def test_active_set_reuses_existing_desired_branch_without_gh_checkout(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            desired = "iss-00123-add-refresh-token"
            self._run_git(target, ["checkout", "-b", desired])
            self._run_git(target, ["checkout", base_branch])

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("spec-dock: (warn)", p.stderr)
                self.assertIn("reusing existing branch", p.stderr)
                self.assertIn("content is not verified", p.stderr)

                if counter.exists():
                    self.assertEqual(counter.read_text(encoding="utf-8").strip(), "0")

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, desired)

    def test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_github_issue_target(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Prepare an existing desired branch whose .meta.json.slug differs from the base branch.
            desired_before = "iss-00123-add-refresh-token"
            self._run_git(target, ["checkout", "-b", desired_before])
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["slug"] = "refresh-token"
            self._write_json_force(issue_meta, meta)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "change slug"],
            )
            self._run_git(target, ["checkout", base_branch])

            # Ensure the reuse branch path does not call gh.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                if counter.exists():
                    self.assertEqual(counter.read_text(encoding="utf-8").strip(), "0")

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00123-add-refresh-token")

    def test_active_set_reuses_existing_branch_recomputes_desired_after_checkout_for_node_id_target(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Prepare an existing desired branch whose .meta.json.slug differs from the base branch.
            desired_before = "iss-00123-add-refresh-token"
            self._run_git(target, ["checkout", "-b", desired_before])
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["slug"] = "refresh-token"
            self._write_json_force(issue_meta, meta)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "change slug"],
            )
            self._run_git(target, ["checkout", base_branch])

            # Ensure the reuse branch path does not call gh.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(
                    target, ["active", "set", "iss-00123", "--checkout", "--force"], env=test_env
                )
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                if counter.exists():
                    self.assertEqual(counter.read_text(encoding="utf-8").strip(), "0")

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00123-add-refresh-token")

    def test_active_set_fallbacks_to_id_when_id_slug_is_non_ascii(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            data = json.loads(issue_meta.read_text(encoding="utf-8"))
            data["slug"] = "日本語"
            self._write_json_force(issue_meta, data)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "non-ascii slug"],
            )

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("spec-dock: (warn)", p.stderr)
                self.assertIn("non-ascii", p.stderr)
                self.assertIn("fallback to id", p.stderr)

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00123")

    def test_active_set_fallbacks_to_id_when_id_slug_is_invalid_ref(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            data = json.loads(issue_meta.read_text(encoding="utf-8"))
            data["slug"] = "a..b"
            self._write_json_force(issue_meta, data)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "invalid-ref slug"],
            )

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ "$1" == "issue" && "$2" == "checkout" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  exit 0\n"
                    "fi\n"
                    'if [[ "$1" == "issue" && "$2" == "develop" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                p = self._run_runtime_capture(target, ["active", "set", "123", "--checkout", "--force"], env=test_env)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("spec-dock: (warn)", p.stderr)
                self.assertIn("invalid ref", p.stderr)
                self.assertIn("fallback to id", p.stderr)

            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00123")

    def test_active_set_parses_hash_and_url_targets(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create parent nodes locally, but link the issue to an existing GitHub issue number.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Provide a fake `gh` binary that records invocations and checks out a branch.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ \"$1\" == \"issue\" && \"$2\" == \"checkout\" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # Both `#123` and issue URL should be accepted and behave the same.
                # Default is no-checkout, so gh should not be invoked.
                self._run_runtime(target, ["active", "set", "#123", "--force"], env=test_env)
                self._run_runtime(
                    target, ["active", "set", "https://github.com/example/repo/issues/123", "--force"], env=test_env
                )
                self.assertFalse(counter.exists())

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00123")

    def test_active_set_github_issue_number_requires_linked_node(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create a spec tree locally (no GitHub links).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ \"$1\" == \"issue\" && \"$2\" == \"checkout\" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # GitHub issue number requires a linked node; command fails without checkout side effects.
                self._run_runtime_expect_fail(target, ["active", "set", "999"], env=test_env)
                self.assertFalse(counter.exists())

    def test_active_set_blocked_by_deps_refuses_without_force(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            # Baseline: active is set to the dependency issue (ready).
            self._run_runtime(target, ["active", "set", "iss-00301", "--force"])
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            # Blocked: active must not be updated.
            p = self._run_runtime_capture(target, ["active", "set", "iss-00302", "--github"], env=test_env)
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-00301", p.stderr)

            after = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after, before)

    def test_active_set_force_allows_blocked_target_and_warns(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["active", "set", "iss-00302", "--github", "--force"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: (warn)", p.stderr)
            self.assertIn("iss-00301", p.stderr)

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00302")

    def test_active_set_is_blocked_when_deps_not_ready(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Open blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-00202"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00401", "--force"])
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--github"], env=test_env)
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-00401", p.stderr)
            self.assertNotIn("epic-00202", p.stderr)
            after = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after, before)

    def test_active_set_force_overrides_deps_guard(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Open blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-00202"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "OPEN", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--github", "--force"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("deps_blocked", p.stderr)
            self.assertIn("iss-00401", p.stderr)
            self.assertNotIn("epic-00202", p.stderr)

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00301")

    def test_active_set_fails_fast_on_unreachable_cycle_and_does_not_run_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle A"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Cycle B"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target C"])

            # Prepare cached `.agent/index*.json` / `.agent/tree*.json` to verify active-only patching.
            self._run_runtime(target, ["sync", "--no-update-active"])

            agent_dir = target / "spec-dock" / ".agent"
            self.assertTrue((agent_dir / "index-all.json").is_file())
            self.assertTrue((agent_dir / "tree-all.json").is_file())
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
            )
            (issue_dir / "iss-local-00001-cycle-a" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00002"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (issue_dir / "iss-local-00002-cycle-b" / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["iss-local-00001"]}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )

            # S06: topology invalid/cycle is fail-fast even when unreachable from target.
            p = self._run_runtime_capture(target, ["active", "set", "iss-local-00003", "--force"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Dependency cycle detected", p.stderr)
            self.assertFalse((agent_dir / "active.json").exists())

            # `active set` must not run `sync`: cached active field must remain unchanged.
            state_index_all = json.loads((agent_dir / "index-all.json").read_text(encoding="utf-8"))
            state_tree_all = json.loads((agent_dir / "tree-all.json").read_text(encoding="utf-8"))
            state_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            state_tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertIsNone(state_index_all["active"])
            self.assertIsNone(state_tree_all["active"])
            self.assertIsNone(state_index["active"])
            self.assertIsNone(state_tree["active"])

    def test_active_set_without_github_uses_synced_index_for_deps_guard(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "JWT auth"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Dep issue"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "302", "--title", "Target issue"],
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-jwt-auth"
                / "issues"
                / "iss-00302-target-issue"
            )
            (issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": [301]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            # Baseline: set ready dep issue to active.
            self._run_runtime(target, ["active", "set", "iss-00301", "--force"])
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            # 1) Dependency is OPEN on GitHub -> index says open -> blocked.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            p_sync_open = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p_sync_open.returncode, 0, p_sync_open.stdout + p_sync_open.stderr)

            # Guard: `active set` without --github must not fetch GitHub.
            guard_log_open = bin_dir / "gh-guard-open.log"
            guard_log_open.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log_open)

            p_blocked = self._run_runtime_capture(target, ["active", "set", "iss-00302"], env=test_env)
            self.assertEqual(p_blocked.returncode, 1, p_blocked.stdout + p_blocked.stderr)
            self.assertIn("iss-00301", p_blocked.stderr)
            after_blocked = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after_blocked, before)
            self.assertFalse(guard_log_open.exists(), "gh must not be invoked without --github")

            # 2) Dependency is CLOSED on GitHub -> index says done -> allowed.
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Epic", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "CLOSED", "title": "Dep", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 302, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            p_sync_closed = self._run_runtime_capture(
                target, ["sync", "--github", "--no-update-active"], env=test_env
            )
            self.assertEqual(p_sync_closed.returncode, 0, p_sync_closed.stdout + p_sync_closed.stderr)

            # Inject a conflicting snapshot in todo view.
            # non-`--github` deps guard must still prefer `index-all.json`.
            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00301"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00301"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            # Guard again: no gh calls on active set without --github.
            guard_log_closed = bin_dir / "gh-guard-closed.log"
            guard_log_closed.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log_closed)

            p_allowed = self._run_runtime_capture(target, ["active", "set", "iss-00302"], env=test_env)
            self.assertEqual(p_allowed.returncode, 0, p_allowed.stdout + p_allowed.stderr)
            self.assertFalse(guard_log_closed.exists(), "gh must not be invoked without --github")
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00302")

            # The cached index statuses must survive a successful active set,
            # so non-`--github` deps checks can continue to use `.agent/index.json`.
            guard_log_after = bin_dir / "gh-guard-after-active.log"
            guard_log_after.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log_after)
            p_after = self._run_runtime_capture(target, ["deps", "check", "iss-00302", "--json"], env=test_env)
            self.assertEqual(p_after.returncode, 0, p_after.stdout + p_after.stderr)
            self.assertFalse(guard_log_after.exists(), "gh must not be invoked without --github")
            data = json.loads(p_after.stdout)
            self.assertTrue(data["ready"])
            self.assertEqual(data["blockers"], [])
            self.assertEqual(data["nodes"]["iss-00301"]["state"], "done")

    def test_active_set_without_github_uses_index_snapshot_when_present(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Done blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-00202"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00301", "--force"])
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_list_stub(
                bin_dir,
                issues=[
                    {"number": 101, "state": "OPEN", "title": "Init", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 201, "state": "OPEN", "title": "Main", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 202, "state": "OPEN", "title": "Deps", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 301, "state": "OPEN", "title": "Target", "labels": [], "updatedAt": "t", "url": "u"},
                    {"number": 401, "state": "CLOSED", "title": "Blocker", "labels": [], "updatedAt": "t", "url": "u"},
                ],
            )
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p_sync = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"], env=test_env)
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)

            index_all_path = target / "spec-dock" / ".agent" / "index-all.json"
            index_todo_path = target / "spec-dock" / ".agent" / "index.json"
            index_all = json.loads(index_all_path.read_text(encoding="utf-8"))
            index_todo = json.loads(index_todo_path.read_text(encoding="utf-8"))
            shadow = dict(index_all["nodes"]["iss-00401"])
            shadow["status"] = "open"
            index_todo["nodes"]["iss-00401"] = shadow
            index_todo_path.write_text(json.dumps(index_todo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            guard_log = bin_dir / "gh-guard-snapshot.log"
            guard_log.unlink(missing_ok=True)
            self._make_gh_issue_list_stub(bin_dir, issues=[], fail=True, log_path=guard_log)

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301"], env=test_env)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertFalse(guard_log.exists(), "gh must not be invoked without --github")
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00301")

    def test_active_set_without_github_blocks_when_snapshot_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--github-issue", "101", "--title", "Auth platform"])
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "201", "--title", "Main epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "201", "--github-issue", "301", "--title", "Target issue"],
            )
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "101", "--github-issue", "202", "--title", "Deps epic"],
            )
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "202", "--github-issue", "401", "--title", "Unknown blocker"],
            )

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00101-auth-platform"
                / "epics"
                / "epic-00201-main-epic"
                / "issues"
                / "iss-00301-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-00202"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            baseline = self._run_runtime_capture(target, ["active", "set", "iss-00401", "--force"])
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")

            (target / "spec-dock" / ".agent" / "index-all.json").unlink(missing_ok=True)
            (target / "spec-dock" / ".agent" / "index.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["active", "set", "iss-00301"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("iss-00401", p.stderr)
            self.assertNotIn("epic-00202", p.stderr)
            after = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after, before)

    def test_active_set_without_github_blocks_unknown_issue_even_without_deps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Unknown issue"])
            self._run_runtime(target, ["active", "clear"])

            agent_dir = target / "spec-dock" / ".agent"
            (agent_dir / "index-all.json").unlink(missing_ok=True)
            (agent_dir / "index.json").unlink(missing_ok=True)

            before = (agent_dir / "active.json").read_text(encoding="utf-8")
            p = self._run_runtime_capture(target, ["active", "set", "iss-local-00001"])
            self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
            self.assertIn("active set blocked", p.stderr)
            self.assertIn("ready=false", p.stderr)
            after = (agent_dir / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after, before)

    def test_active_set_epic_and_initiative_use_v2_deps_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Main epic"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Blocker epic"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Target issue"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "2", "--title", "Blocker issue"])

            target_issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-main-epic"
                / "issues"
                / "iss-local-00001-target-issue"
            )
            (target_issue_dir / "deps.json").write_text(
                json.dumps({"schema_version": 1, "depends_on": ["epic-local-00002"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            self._run_runtime(target, ["sync", "--no-update-active"])
            agent_dir = target / "spec-dock" / ".agent"
            self._run_runtime(target, ["active", "clear"])

            before_epic = (agent_dir / "active.json").read_text(encoding="utf-8")
            blocked_epic = self._run_runtime_capture(target, ["active", "set", "epic-local-00001"])
            self.assertEqual(blocked_epic.returncode, 1, blocked_epic.stdout + blocked_epic.stderr)
            self.assertIn("active set blocked", blocked_epic.stderr)
            self.assertIn("iss-local-00002", blocked_epic.stderr)
            after_epic = (agent_dir / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after_epic, before_epic)

            forced_epic = self._run_runtime_capture(target, ["active", "set", "epic-local-00001", "--force"])
            self.assertEqual(forced_epic.returncode, 0, forced_epic.stdout + forced_epic.stderr)
            self.assertIn("deps_blocked", forced_epic.stderr)
            self.assertIn("blocker: iss-local-00002", forced_epic.stderr)

            active_after_epic_force = json.loads((agent_dir / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active_after_epic_force["initiative"]["id"], "init-local-00001")
            self.assertEqual(active_after_epic_force["epic"]["id"], "epic-local-00001")
            self.assertIsNone(active_after_epic_force["issue"])

            self._run_runtime(target, ["active", "clear"])
            before_init = (agent_dir / "active.json").read_text(encoding="utf-8")
            blocked_init = self._run_runtime_capture(target, ["active", "set", "init-local-00001"])
            self.assertEqual(blocked_init.returncode, 1, blocked_init.stdout + blocked_init.stderr)
            self.assertIn("active set blocked", blocked_init.stderr)
            self.assertIn("iss-local-00002", blocked_init.stderr)
            after_init = (agent_dir / "active.json").read_text(encoding="utf-8")
            self.assertEqual(after_init, before_init)

            forced_init = self._run_runtime_capture(target, ["active", "set", "init-local-00001", "--force"])
            self.assertEqual(forced_init.returncode, 0, forced_init.stdout + forced_init.stderr)
            self.assertIn("deps_blocked", forced_init.stderr)
            self.assertIn("blocker: iss-local-00002", forced_init.stderr)

            active_after_init_force = json.loads((agent_dir / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active_after_init_force["initiative"]["id"], "init-local-00001")
            self.assertIsNone(active_after_init_force["epic"])
            self.assertIsNone(active_after_init_force["issue"])

    def test_active_set_issue_auto_checkouts_when_github_linked(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create parent nodes locally, but link the issue to an existing GitHub issue number.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Provide a fake `gh` binary that records invocations and checks out a branch.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                counter = bin_dir / "counter.txt"
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    f"counter_file='{counter.as_posix()}'\n"
                    'if [[ \"$1\" == \"issue\" && \"$2\" == \"checkout\" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout -b \"$branch\" >/dev/null 2>&1 || git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  c=0\n"
                    "  if [[ -f \"$counter_file\" ]]; then\n"
                    "    c=$(cat \"$counter_file\")\n"
                    "  fi\n"
                    "  echo $((c+1)) > \"$counter_file\"\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # Explicit checkout should switch branches, but gh should not be invoked.
                self._run_runtime(target, ["active", "set", "iss-0123", "--checkout", "--force"], env=test_env)
                self.assertFalse(counter.exists())

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00123")
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            self.assertEqual(current, "iss-00123-add-refresh-token")

    def test_active_set_re_resolves_node_after_checkout_when_id_format_changes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            base_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            # Create parent nodes locally, and a GitHub-linked issue (id is canonical: iss-00123).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            # Make the working tree clean so checkout is allowed.
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "spec tree"],
            )

            # Prepare the checkout branch where the node id format differs (e.g. iss-00123 -> iss-0123).
            self._run_git(target, ["checkout", "-b", "gh-issue-123"])
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["id"] = "iss-0123"
            self._write_json_force(issue_meta, meta)
            self._run_git(target, ["add", "-A"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "change id format"],
            )
            self._run_git(target, ["checkout", base_branch])

            # Provide a fake `gh` binary that checks out the prepared branch.
            with tempfile.TemporaryDirectory() as bin_tmp:
                bin_dir = Path(bin_tmp)
                gh_path = bin_dir / "gh"
                gh_path.write_text(
                    "#!/usr/bin/env bash\n"
                    "set -euo pipefail\n"
                    'if [[ \"$1\" == \"issue\" && \"$2\" == \"checkout\" ]]; then\n'
                    "  n=\"$3\"\n"
                    "  branch=\"gh-issue-${n}\"\n"
                    "  git checkout \"$branch\" >/dev/null 2>&1\n"
                    "  exit 0\n"
                    "fi\n"
                    "echo \"unexpected gh args: $@\" >&2\n"
                    "exit 1\n",
                    encoding="utf-8",
                )
                gh_path.chmod(0o755)
                test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                # Active is resolved before checkout and must remain stable.
                self._run_runtime(target, ["active", "set", "iss-00123", "--checkout", "--force"], env=test_env)

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-00123")

    def test_active_set_github_issue_checkout_refuses_dirty_working_tree(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )

            # Create a node linked to GH #123, but keep the working tree dirty (uncommitted).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--github-issue", "123"])

            # Provide a fake `gh` binary (should not be invoked due to dirty tree).
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "echo \"gh should not be invoked when working tree is dirty\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime_expect_fail(target, ["active", "set", "123", "--checkout"], env=test_env)
            self.assertFalse((target / "spec-dock" / ".agent" / "active.json").exists())

    def test_new_no_github_does_not_invoke_gh(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Provide a fake `gh` binary that always errors; --no-github must not call it.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "echo \"gh should not be invoked in --no-github mode\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"], env=test_env)
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"], env=test_env)

    def test_new_rejects_invalid_title_before_gh_issue_create(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$@" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "https://github.com/example/repo/issues/999"\n'
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--create-github-issue", "--title", "日本語"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--title", p.stderr)
            self.assertIn("expected regex", p.stderr)

            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")
            self.assertEqual(list((target / "spec-dock" / "initiatives").glob("*")), [])

    def test_new_initiative_and_epic_default_to_local_even_when_gh_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Default for initiative/epic is local-only; `gh` must not be invoked even if it is present.
            bin_dir = target / ".bin-gh"
            bin_dir.mkdir(parents=True, exist_ok=True)
            called_path = target / ".gh.called"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo \"$@\" >> \"{called_path.as_posix()}\"\\n'
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                '  echo \"https://github.com/example/repo/issues/123\"\n'
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth"], env=test_env)

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            self.assertTrue(init_dir.is_dir())
            self.assertTrue(epic_dir.is_dir())
            self.assertFalse(called_path.exists(), f"gh was invoked unexpectedly: {called_path}")

            init_meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(init_meta["id"], "init-local-00001")
            self.assertEqual(epic_meta["id"], "epic-local-00001")
            self.assertNotIn("github", init_meta)
            self.assertNotIn("github", epic_meta)
            self._assert_spec_dock_meta_marker(init_meta)
            self._assert_spec_dock_meta_marker(epic_meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self._assert_readonly_on_posix(epic_dir / ".meta.json")

    def test_new_initiative_warns_and_continues_when_readonly_lock_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            runtime_io_json = (
                target / "spec-dock" / "scripts" / "spec_dock_runtime" / "io_json.py"
            )
            self.assertTrue(runtime_io_json.is_file())
            runtime_io_json.write_text(
                runtime_io_json.read_text(encoding="utf-8")
                + "\n\n"
                + "def _try_make_readonly(path):\n"
                + '    return False, "simulated"\n',
                encoding="utf-8",
            )

            p = self._run_runtime_capture(
                target,
                ["new", "initiative", "--no-github", "--title", "Auth platform"],
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: (warn)", p.stderr)

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            self.assertTrue((init_dir / ".meta.json").is_file())

    def test_new_initiative_and_epic_github_flags_are_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"])

            p1 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform 2",
                    "--create-github-issue",
                    "--github-issue",
                    "123",
                ],
            )
            self.assertEqual(p1.returncode, 2, p1.stdout + p1.stderr)
            self.assertIn("not allowed with argument", p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "1",
                    "--title",
                    "JWT auth",
                    "--create-github-issue",
                    "--no-github",
                ],
            )
            self.assertEqual(p2.returncode, 2, p2.stdout + p2.stderr)
            self.assertIn("not allowed with argument", p2.stderr)

            p3 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "initiative",
                    "--title",
                    "Auth platform 3",
                    "--github-issue",
                    "123",
                    "--no-github",
                ],
            )
            self.assertEqual(p3.returncode, 2, p3.stdout + p3.stderr)
            self.assertIn("not allowed with argument", p3.stderr)

            p4 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "epic",
                    "--initiative",
                    "1",
                    "--title",
                    "JWT auth 2",
                    "--github-issue",
                    "123",
                    "--no-github",
                ],
            )
            self.assertEqual(p4.returncode, 2, p4.stdout + p4.stderr)
            self.assertIn("not allowed with argument", p4.stderr)

    def test_new_issue_can_create_github_issue_and_use_its_number(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create parent nodes locally, but create the issue on GitHub (default).
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            # Provide a fake `gh` binary so the test doesn't require network/auth.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  echo \"https://github.com/example/repo/issues/123\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(
                target,
                ["new", "issue", "--epic", "1", "--title", "Add refresh token"],
                env=test_env,
            )

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            meta = json.loads((issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["id"], "iss-00123")
            self.assertEqual(meta["github"]["issue_number"], 123)
            self._assert_spec_dock_meta_marker(meta)
            self._assert_readonly_on_posix(issue_dir / ".meta.json")

    def test_import_aborts_without_local_changes_when_gh_issue_view_fails(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir, failing_numbers={99999})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "99999", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-99999-*"))
            self.assertEqual(imported, [])
            self.assertFalse((target / "spec-dock" / ".agent" / "index.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "tree.json").exists())

    def test_import_fails_preflight_on_legacy_meta_without_creating_nodes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Import target lineage (canonical .meta.json)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])
            # Unrelated legacy file to trigger preflight failure.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Legacy holder"])

            legacy_init_dir = target / "spec-dock" / "initiatives" / "init-local-00002-legacy-holder"
            dot_meta_path = legacy_init_dir / ".meta.json"
            legacy_meta_path = legacy_init_dir / "meta.json"
            dot_meta_path.rename(legacy_meta_path)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "99999", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p.stderr)
            self.assertIn(str(legacy_meta_path), p.stderr)

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-99999-*"))
            self.assertEqual(imported, [])
            self.assertFalse((target / "spec-dock" / ".agent" / "index.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "tree.json").exists())

    def test_new_fails_preflight_on_legacy_meta_without_creating_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Legacy holder"])

            initiatives_root = target / "spec-dock" / "initiatives"
            parent_init_dir = initiatives_root / "init-local-00001-parent-initiative"
            parent_epic_dir = parent_init_dir / "epics" / "epic-local-00001-parent-epic"
            legacy_init_dir = initiatives_root / "init-local-00002-legacy-holder"
            dot_meta_path = legacy_init_dir / ".meta.json"
            legacy_meta_path = legacy_init_dir / "meta.json"
            dot_meta_path.rename(legacy_meta_path)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())

            before_inits = sorted(p.name for p in initiatives_root.glob("init-*"))
            before_epics = sorted(p.name for p in (parent_init_dir / "epics").glob("epic-*"))
            before_issues = sorted(p.name for p in (parent_epic_dir / "issues").glob("iss-*"))

            p_init = self._run_runtime_capture(
                target,
                ["new", "initiative", "--no-github", "--title", "Should fail initiative"],
            )
            self.assertNotEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_init.stderr)
            self.assertIn(str(legacy_meta_path), p_init.stderr)

            p_epic = self._run_runtime_capture(
                target,
                ["new", "epic", "--no-github", "--initiative", "1", "--title", "Should fail epic"],
            )
            self.assertNotEqual(p_epic.returncode, 0, p_epic.stdout + p_epic.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_epic.stderr)
            self.assertIn(str(legacy_meta_path), p_epic.stderr)

            p_issue = self._run_runtime_capture(
                target,
                ["new", "issue", "--no-github", "--epic", "1", "--title", "Should fail issue"],
            )
            self.assertNotEqual(p_issue.returncode, 0, p_issue.stdout + p_issue.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_issue.stderr)
            self.assertIn(str(legacy_meta_path), p_issue.stderr)

            self.assertEqual(before_inits, sorted(p.name for p in initiatives_root.glob("init-*")))
            self.assertEqual(before_epics, sorted(p.name for p in (parent_init_dir / "epics").glob("epic-*")))
            self.assertEqual(before_issues, sorted(p.name for p in (parent_epic_dir / "issues").glob("iss-*")))

    def test_import_initiative_creates_node_and_runs_sync_without_updating_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            self._run_git(target, ["checkout", "-b", "feature/init-00010-check"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "initiative", "10", "--title", "Auth platform"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import initiative)", p.stdout)
            self.assertIn("id=init-00010", p.stdout)
            self.assertIn("path=", p.stdout)
            self.assertIn("github=#10", p.stdout)

            init_dir = target / "spec-dock" / "initiatives" / "init-00010-auth-platform"
            self.assertTrue(init_dir.is_dir())
            meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["id"], "init-00010")
            self.assertEqual(meta["github"]["issue_number"], 10)
            self._assert_spec_dock_meta_marker(meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())
            self.assertFalse((target / "spec-dock" / ".agent" / "active.json").exists())

    def test_import_epic_and_initiative_create_nodes(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "initiative", "10", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["import", "epic", "11", "--title", "JWT auth", "--initiative", "10"], env=test_env)

            init_dir = target / "spec-dock" / "initiatives" / "init-00010-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00011-jwt-auth"
            self.assertTrue(init_dir.is_dir())
            self.assertTrue(epic_dir.is_dir())

            init_meta = json.loads((init_dir / ".meta.json").read_text(encoding="utf-8"))
            epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(init_meta["id"], "init-00010")
            self.assertEqual(init_meta["github"]["issue_number"], 10)
            self.assertEqual(epic_meta["id"], "epic-00011")
            self.assertEqual(epic_meta["parent_id"], "init-00010")
            self.assertEqual(epic_meta["initiative_id"], "init-00010")
            self.assertEqual(epic_meta["github"]["issue_number"], 11)
            self._assert_spec_dock_meta_marker(init_meta)
            self._assert_spec_dock_meta_marker(epic_meta)
            self._assert_readonly_on_posix(init_dir / ".meta.json")
            self._assert_readonly_on_posix(epic_dir / ".meta.json")

    def test_import_issue_creates_node_and_runs_sync_without_updating_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_git(target, ["init"])
            self._run_git(
                target,
                ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
            )
            self._run_git(target, ["checkout", "-b", "feature/iss-00123-check"])

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["active", "set", "epic-local-00001"])

            active_path = target / "spec-dock" / ".agent" / "active.json"
            before = active_path.read_text(encoding="utf-8")

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (import issue)", p.stdout)
            self.assertIn("id=iss-00123", p.stdout)
            self.assertIn("epic=epic-local-00001", p.stdout)
            self.assertIn("initiative=init-local-00001", p.stdout)
            self.assertIn("path=", p.stdout)
            self.assertIn("github=#123", p.stdout)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            meta = json.loads((issue_dir / ".meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["id"], "iss-00123")
            self.assertEqual(meta["github"]["issue_number"], 123)
            self._assert_spec_dock_meta_marker(meta)
            self._assert_readonly_on_posix(issue_dir / ".meta.json")
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())

            after = active_path.read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_import_accepts_number_hash_and_url_equivalently(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        targets = [
            "123",
            "#123",
            "https://github.com/example/repo/issues/123",
        ]
        for issue_target in targets:
            with self.subTest(issue_target=issue_target):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
                    self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

                    bin_dir = target / ".bin"
                    bin_dir.mkdir(parents=True, exist_ok=True)
                    log_path = target / ".gh.log"
                    self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
                    test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

                    self._run_runtime(
                        target,
                        ["import", "issue", issue_target, "--title", "Imported issue", "--epic", "epic-local-00001"],
                        env=test_env,
                    )

                    issue_dir = (
                        target
                        / "spec-dock"
                        / "initiatives"
                        / "init-local-00001-auth-platform"
                        / "epics"
                        / "epic-local-00001-jwt-auth"
                        / "issues"
                        / "iss-00123-imported-issue"
                    )
                    self.assertTrue(issue_dir.is_dir())
                    log = log_path.read_text(encoding="utf-8")
                    self.assertIn("issue view 123", log)

    def test_import_issue_uses_active_epic_when_parent_not_specified(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["active", "set", "epic-local-00001"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())

    def test_import_epic_uses_active_initiative_when_parent_not_specified(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["active", "set", "init-local-00001"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "epic", "124", "--title", "JWT auth"], env=test_env)
            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-00124-jwt-auth"
            )
            self.assertTrue(epic_dir.is_dir())

    def test_import_issue_requires_parent_when_no_epic_and_active_unavailable(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--epic", p.stderr)

    def test_import_parent_fallback_errors_on_stale_active(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            broken_active = {
                "schema_version": 2,
                "updated_at": "2026-01-01T00:00:00+00:00",
                "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-x"},
                "epic": {"id": "epic-local-99999", "path": "spec-dock/initiatives/init-local-99999-x/epics/epic-local-99999-y"},
                "issue": None,
            }
            (target / "spec-dock" / ".agent" / "active.json").write_text(
                json.dumps(broken_active, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--epic", p.stderr)

    def test_import_rejects_invalid_or_wrong_type_parent_id(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p1 = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "init-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p1.returncode, 0, p1.stdout + p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                ["import", "issue", "124", "--title", "Add refresh token", "--epic", "epic-99999"],
                env=test_env,
            )
            self.assertNotEqual(p2.returncode, 0, p2.stdout + p2.stderr)

            p3 = self._run_runtime_capture(
                target,
                ["import", "epic", "125", "--title", "JWT auth", "--initiative", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p3.returncode, 0, p3.stdout + p3.stderr)

    def test_import_rejects_already_linked_github_issue_number(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--title", "Linked initiative", "--github-issue", "123"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("already linked", p.stderr)
            self.assertIn("different GitHub issue number", p.stderr)
            self.assertNotIn("--github-issue", p.stderr)

    def test_import_rejects_invalid_slug_and_invalid_title(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p1 = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001", "--slug", "Bad!Slug"],
                env=test_env,
            )
            self.assertNotEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            self.assertIn("--slug", p1.stderr)
            self.assertIn("expected regex", p1.stderr)

            p2 = self._run_runtime_capture(
                target,
                ["import", "issue", "124", "--title", "!!!", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p2.returncode, 0, p2.stdout + p2.stderr)
            self.assertIn("--title", p2.stderr)
            self.assertIn("expected regex", p2.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00124-*"))
            self.assertEqual(imported, [])

    def test_import_rejects_invalid_title_before_gh_issue_view(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "日本語", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("--title", p.stderr)
            self.assertIn("expected regex", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])

    def test_import_fails_when_sync_preflight_fails(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / ".meta.json"
            )
            data = json.loads(init_meta.read_text(encoding="utf-8"))
            data["slug"] = "BrokenSlug"
            self._write_json_force(init_meta, data)

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Add refresh token", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("slug must be lowercase", p.stderr)
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])

    def test_import_rejects_ambiguous_parent_id_shorthand_when_both_local_and_github_exist(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create both GitHub and local variants with the same numeric suffix.
            self._run_runtime(target, ["new", "initiative", "--github-issue", "10", "--title", "GitHub initiative"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--id", "10", "--title", "Local initiative"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "epic", "11", "--title", "JWT auth", "--initiative", "10"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("ambiguous", p.stderr.lower())

            imported = list((target / "spec-dock" / "initiatives").rglob("epic-00011-*"))
            self.assertEqual(imported, [])

    def test_import_aborts_without_local_changes_when_gh_issue_view_returns_non_json(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Parent initiative"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "Parent epic"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"view\" ]]; then\n'
                "  echo \"NOT_JSON\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 99\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)

            imported = list((target / "spec-dock" / "initiatives").rglob("iss-00123-*"))
            self.assertEqual(imported, [])
            self.assertFalse((target / "spec-dock" / ".agent" / "index.json").exists())
            self.assertFalse((target / "spec-dock" / ".agent" / "tree.json").exists())

    def test_import_does_not_migrate_legacy_active_manifest(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            init_path = "spec-dock/initiatives/init-local-00001-auth-platform"
            epic_path = f"{init_path}/epics/epic-local-00001-jwt-auth"

            legacy_dir = target / "spec-dock" / ".work"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            legacy_active_path = legacy_dir / "active.json"
            legacy_active_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "updated_at": "2026-01-01T00:00:00+00:00",
                        "initiative": {"id": "init-local-00001", "path": init_path},
                        "epic": {"id": "epic-local-00001", "path": epic_path},
                        "issue": None,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            self._run_runtime(target, ["import", "issue", "123", "--title", "Add refresh token"], env=test_env)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            self.assertFalse((target / "spec-dock" / ".agent" / "active.json").exists())
            self.assertTrue(legacy_active_path.is_file())

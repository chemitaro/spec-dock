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

    def _assert_version_file(self, target: Path) -> None:
        version_file = target / "spec-dock" / "spec-dock.version"
        self.assertTrue(version_file.is_file())
        self.assertEqual(version_file.read_text(encoding="utf-8").strip(), _expected_spec_dock_version())

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

            self.assertTrue(
                (target / "spec-dock" / "docs" / "spec-dock-guide.md").is_file()
            )
            self.assertTrue(
                (target / "spec-dock" / "docs" / "spec-dock-guide-old.md").is_file()
            )
            self.assertTrue((target / "spec-dock" / "docs" / "README.md").is_file())
            self.assertTrue((target / "spec-dock" / "docs" / "github.md").is_file())
            self.assertTrue((target / "spec-dock" / "docs" / "sync.md").is_file())
            self.assertTrue((target / "spec-dock" / "docs" / "workflow-tree.md").is_file())
            self.assertTrue((target / "spec-dock" / "docs" / "workflow-issue.md").is_file())
            self.assertTrue((target / "spec-dock" / "docs" / "workflow-adr.md").is_file())

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
            issue_templates_dir = templates_dir / "issue"
            req_text = (issue_templates_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertIn("## 対象ユーザー / 利用シナリオ", req_text)
            self.assertIn("## 用語（ドメイン語彙）", req_text)

            design_text = (issue_templates_dir / "design.md").read_text(encoding="utf-8")
            # UML is embedded as small subsections (not a single block at the end).
            self.assertIn("```plantuml", design_text)
            self.assertIn("### UML（", design_text)

            plan_text = (issue_templates_dir / "plan.md").read_text(encoding="utf-8")
            self.assertIn("#### update_plan（着手時に登録）", plan_text)
            self.assertIn("./spec-dock/active/issue/report.md", plan_text)

            report_text = (issue_templates_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## 遭遇した問題と解決", report_text)

            self.assertTrue(
                (
                    target
                    / ".codex"
                    / "skills"
                    / "spec-driven-tdd-workflow"
                    / "SKILL.md"
                ).is_file()
            )
            self.assertFalse(
                (target / ".github" / "workflows" / "spec-dock-close.yml").exists()
            )

    def test_init_no_skill_skips_skill_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", "--no-skill", str(target)])
            self.assertEqual(exit_code, 0)

            self._assert_version_file(target)

            self.assertFalse(
                (
                    target
                    / ".codex"
                    / "skills"
                    / "spec-driven-tdd-workflow"
                    / "SKILL.md"
                ).exists()
            )
            self.assertFalse((target / ".github" / "workflows" / "spec-dock-close.yml").exists())

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
            # Parent ids accept shorthand numeric forms (e.g. `1` -> `init-local-0001` / `epic-local-0001`).
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-0001-auth-platform"
                / "epics"
                / "epic-local-0001-jwt-auth"
                / "issues"
                / "iss-local-0001-add-refresh-token"
            )
            self.assertTrue((issue_dir / "requirement.md").is_file())
            self.assertTrue((issue_dir / "design.md").is_file())
            self.assertTrue((issue_dir / "plan.md").is_file())
            self.assertTrue((issue_dir / "report.md").is_file())

            # Placeholders should be rendered in generated files.
            requirement = (issue_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertNotIn("<ISS_ID>", requirement)
            self.assertNotIn("<ISS_TITLE>", requirement)
            self.assertIn("iss-local-0001", requirement)

            # Active pointers are set by a single target argument (node id or GitHub issue number).
            self._run_runtime(target, ["active", "set", "iss-local-0001"])
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
            self.assertEqual(init_item["id"], "init-local-0001")
            self.assertEqual(init_item["type"], "initiative")
            self.assertIn("epics", init_item)

            epic_item = init_item["epics"][0]
            self.assertEqual(epic_item["id"], "epic-local-0001")
            self.assertEqual(epic_item["type"], "epic")
            self.assertIn("issues", epic_item)

            issue_item = epic_item["issues"][0]
            self.assertEqual(issue_item["id"], "iss-local-0001")
            self.assertEqual(issue_item["type"], "issue")

            # `tree.json` nodes match the same node schema as `index.json` nodes.
            self.assertEqual(issue_item, index_nodes["iss-local-0001"])
            self._run_runtime(target, ["validate"])

    def test_active_set_initiative_and_epic_keep_missing_layers_as_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Create a minimal local tree.
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            # Initiative-only active: epic/issue are placeholders.
            self._run_runtime(target, ["active", "set", "init-local-0001"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsInstance(active.get("initiative"), dict)
            self.assertIsNone(active.get("epic"))
            self.assertIsNone(active.get("issue"))
            self.assertIn("init-local-0001", self._read_active_pointer_text(target, "initiative", "README.md"))
            self.assertIn("Active Epic: （なし）", self._read_active_pointer_text(target, "epic", "README.md"))
            self.assertIn("Active Issue: （なし）", self._read_active_pointer_text(target, "issue", "README.md"))

            # Epic-only active: issue is a placeholder.
            self._run_runtime(target, ["active", "set", "epic-local-0001"])
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertIsInstance(active.get("initiative"), dict)
            self.assertIsInstance(active.get("epic"), dict)
            self.assertIsNone(active.get("issue"))
            self.assertIn("epic-local-0001", self._read_active_pointer_text(target, "epic", "README.md"))
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
            self.assertEqual(active["initiative"]["id"], "init-local-0001")
            self.assertEqual(active["epic"]["id"], "epic-local-0001")
            self.assertEqual(active["issue"]["id"], "iss-local-0001")

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

                self._run_runtime(target, ["active", "set", "123"], env=test_env)
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-0123")

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

                # GitHub issue number requires a linked node; checkout runs, then the command errors.
                self._run_runtime_expect_fail(target, ["active", "set", "999"], env=test_env)
                self.assertEqual(counter.read_text(encoding="utf-8").strip(), "1")

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

                # Activating a GitHub-linked node id also triggers checkout.
                self._run_runtime(target, ["active", "set", "iss-0123"], env=test_env)
                self.assertEqual(counter.read_text(encoding="utf-8").strip(), "1")

            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active["issue"]["id"], "iss-0123")

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

            self._run_runtime_expect_fail(target, ["active", "set", "123"], env=test_env)

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

    def test_new_nodes_default_to_github_issue_creation(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Provide a fake `gh` binary that returns unique issue URLs per `issue create`.
            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            counter = bin_dir / "counter.txt"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f"counter_file='{counter.as_posix()}'\n"
                'if [[ \"$1\" == \"issue\" && \"$2\" == \"create\" ]]; then\n'
                "  n=0\n"
                "  if [[ -f \"$counter_file\" ]]; then\n"
                "    n=$(cat \"$counter_file\")\n"
                "  fi\n"
                "  n=$((n+1))\n"
                "  echo \"$n\" > \"$counter_file\"\n"
                "  issue_num=$((122 + n))\n"
                "  echo \"https://github.com/example/repo/issues/${issue_num}\"\n"
                "  exit 0\n"
                "fi\n"
                "echo \"unexpected gh args: $@\" >&2\n"
                "exit 1\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            # Default: GitHub issue is created and its number becomes the node id suffix.
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"], env=test_env)
            self._run_runtime(target, ["new", "epic", "--initiative", "123", "--title", "JWT auth"], env=test_env)
            self._run_runtime(target, ["new", "issue", "--epic", "124", "--title", "Add refresh token"], env=test_env)

            init_dir = target / "spec-dock" / "initiatives" / "init-0123-auth-platform"
            epic_dir = init_dir / "epics" / "epic-0124-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-0125-add-refresh-token"
            self.assertTrue(init_dir.is_dir())
            self.assertTrue(epic_dir.is_dir())
            self.assertTrue(issue_dir.is_dir())

            init_meta = (init_dir / "meta.json").read_text(encoding="utf-8")
            epic_meta = (epic_dir / "meta.json").read_text(encoding="utf-8")
            issue_meta = (issue_dir / "meta.json").read_text(encoding="utf-8")
            self.assertIn('\"id\": \"init-0123\"', init_meta)
            self.assertIn('\"issue_number\": 123', init_meta)
            self.assertIn('\"id\": \"epic-0124\"', epic_meta)
            self.assertIn('\"issue_number\": 124', epic_meta)
            self.assertIn('\"id\": \"iss-0125\"', issue_meta)
            self.assertIn('\"issue_number\": 125', issue_meta)

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
                / "init-local-0001-auth-platform"
                / "epics"
                / "epic-local-0001-jwt-auth"
                / "issues"
                / "iss-0123-add-refresh-token"
            )
            self.assertTrue(issue_dir.is_dir())
            meta = (issue_dir / "meta.json").read_text(encoding="utf-8")
            self.assertIn('\"id\": \"iss-0123\"', meta)
            self.assertIn('\"issue_number\": 123', meta)

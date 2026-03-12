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


class TestCliActive(CliRuntimeHarness):
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


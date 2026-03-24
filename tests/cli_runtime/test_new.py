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


class TestCliNew(CliRuntimeHarness):
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

    def test_new_doc_scope_shorthand_resolves_local_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            p_init = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--initiative", "1", "--title", "Initiative note"],
            )
            p_epic = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--epic", "1", "--title", "Epic note"],
            )
            p_issue = self._run_runtime_capture(
                target,
                ["new", "doc", "note", "--issue", "1", "--title", "Issue note"],
            )
            self.assertEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
            self.assertEqual(p_epic.returncode, 0, p_epic.stdout + p_epic.stderr)
            self.assertEqual(p_issue.returncode, 0, p_issue.stdout + p_issue.stderr)
            self.assertIn("scope=init-local-00001", p_init.stdout)
            self.assertIn("scope=epic-local-00001", p_epic.stdout)
            self.assertIn("scope=iss-local-00001", p_issue.stdout)

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
            self.assertNotEqual(sorted((init_dir / "discussions").glob("001-note-*.md")), [])
            self.assertNotEqual(sorted((epic_dir / "discussions").glob("001-note-*.md")), [])
            self.assertNotEqual(sorted((issue_dir / "discussions").glob("001-note-*.md")), [])

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
            Path(__file__).resolve().parents[2]
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

            runtime_fs_repo = (
                target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            )
            self.assertTrue(runtime_fs_repo.is_file())
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
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

    def test_new_github_flags_are_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth"])

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

            p5 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "1",
                    "--title",
                    "Issue 1",
                    "--create-github-issue",
                    "--github-issue",
                    "123",
                ],
            )
            self.assertEqual(p5.returncode, 2, p5.stdout + p5.stderr)
            self.assertIn("not allowed with argument", p5.stderr)

            p6 = self._run_runtime_capture(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "1",
                    "--title",
                    "Issue 2",
                    "--create-github-issue",
                    "--no-github",
                ],
            )
            self.assertEqual(p6.returncode, 2, p6.stdout + p6.stderr)
            self.assertIn("not allowed with argument", p6.stderr)

    def test_new_issue_create_github_issue_flag_alias_is_accepted(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

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
                ["new", "issue", "--epic", "1", "--title", "Add refresh token", "--create-github-issue"],
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

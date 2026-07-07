from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


_DEFERRED_COMMANDS = (
    (["authoring", "pack", "prepare"], "authoring pack prepare", "iss-00299"),
    (["authoring", "backend", "invoke"], "authoring backend invoke", "iss-00300"),
    (["authoring", "pack", "review"], "authoring pack review", "iss-00301"),
    (["authoring", "pack", "stage"], "authoring pack stage", "iss-00301"),
    (
        ["authoring", "validate", "initiative-epic-candidates"],
        "authoring validate initiative-epic-candidates",
        "iss-00302",
    ),
    (
        ["authoring", "validate", "epic-issue-candidates"],
        "authoring validate epic-issue-candidates",
        "iss-00302",
    ),
    (
        ["authoring", "validate", "issue-draft-adoption"],
        "authoring validate issue-draft-adoption",
        "iss-00303",
    ),
    (
        ["authoring", "validate", "selected-skeleton-fill"],
        "authoring validate selected-skeleton-fill",
        "iss-00303",
    ),
    (["authoring", "approval", "check"], "authoring approval check", "iss-00305"),
)

_FORBIDDEN_AUTHORITY_CLAIMS = (
    "canonical docs",
    ".assurance.json",
    "authorized profile",
    "set-authorized-profile",
    "success",
    "adoption_status",
    "adopted",
    "reviewer pass",
    "execution-ready",
    "pr-ready",
    "merge-ready",
)


class TestAuthoringCli(CliRuntimeHarness):
    def test_authoring_help_exposes_deferred_command_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "Run deferred ChatGPT authoring helper commands" in p.stdout
            for expected in ("preflight", "pack", "backend", "validate", "approval"):
                assert expected in p.stdout
            assert "authoring preflight github-sync" in p.stdout
            for _args, command, _next_issue in _DEFERRED_COMMANDS:
                assert command in p.stdout

    @pytest.mark.parametrize(("args", "command", "next_issue"), _DEFERRED_COMMANDS)
    def test_authoring_deferred_commands_fail_closed_with_stable_diagnostics(
        self, args: list[str], command: str, next_issue: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, args)

            assert p.returncode != 0, p.stdout + p.stderr
            assert f"spec-dock: deferred (authoring) command={command}" in p.stdout
            assert "status=deferred" in p.stdout
            assert "authority=evidence_only" in p.stdout
            assert f"next_issue={next_issue}" in p.stdout
            assert "reason=not_implemented_in_this_issue" in p.stdout

            output = (p.stdout + p.stderr).lower()
            for forbidden in _FORBIDDEN_AUTHORITY_CLAIMS:
                assert forbidden not in output

    def test_authoring_preflight_github_sync_passes_for_clean_synced_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            repo = _create_synced_git_repo(target)

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--source-path",
                    "source.txt",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["evidence_mode"] == "github-synced"
            assert payload["sync_state"] == "synced"
            assert payload["github_sync"] == "verified"
            assert payload["requested_ref"] == "main"
            assert payload["effective_ref"] == "main"
            assert payload["local_head"] == payload["remote_head"]
            assert payload["source_manifest_hash"]
            assert payload["source_hash_mismatch_checked"] is False
            assert payload["source_paths"] == ["source.txt"]
            assert "source.txt" in payload["source_hashes"]

    @pytest.mark.parametrize(
        ("mutate", "reason"),
        (
            (lambda repo: (repo / "source.txt").write_text("dirty\n", encoding="utf-8"), "dirty_tracked"),
            (lambda repo: _stage_change(repo), "staged_changes"),
            (lambda repo: (repo / "untracked.txt").write_text("new\n", encoding="utf-8"), "untracked_files"),
        ),
    )
    def test_authoring_preflight_github_sync_blocks_unsafe_worktree_states(self, mutate, reason: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            mutate(repo)

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "blocked"
            assert reason in payload["blockers"]
            assert payload["github_sync"] != "verified"

    @pytest.mark.parametrize(
        ("mutate", "expected_status", "reason"),
        (
            ("ahead", "blocked", "ahead_of_remote"),
            ("behind", "stale", "behind_remote"),
            ("diverged", "blocked", "diverged_from_remote"),
        ),
    )
    def test_authoring_preflight_github_sync_blocks_ahead_behind_and_diverged(
        self, mutate, expected_status: str, reason: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            {
                "ahead": _make_ahead,
                "behind": _make_behind,
                "diverged": _make_diverged,
            }[mutate](repo)

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == expected_status
            assert reason in payload["blockers"]

    def test_authoring_preflight_github_sync_blocks_missing_origin_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            _git(repo, "update-ref", "-d", "refs/remotes/origin/main")

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "blocked"
            assert "remote_branch_missing" in payload["blockers"]

    def test_authoring_preflight_github_sync_blocks_non_origin_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            _git(repo, "remote", "add", "fork", (repo.parent / "remote.git").as_posix())
            _git(repo, "update-ref", "refs/remotes/fork/main", _git(repo, "rev-parse", "HEAD").stdout.strip())
            _git(repo, "branch", "--set-upstream-to=fork/main", "main")

            payload = _run_preflight_json(self, repo, expected_returncode=1)

            assert payload["status"] == "blocked"
            assert "origin_mismatch" in payload["blockers"]

    def test_authoring_preflight_github_sync_blocks_connector_unavailable_observer(self) -> None:
        runtime_root = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        if str(runtime_root) not in sys.path:
            sys.path.insert(0, str(runtime_root))

        from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (
            GitHubSyncPreflightRequest,
            run_github_sync_preflight,
        )
        from spec_dock_runtime.domain.authoring_pack.preflight_contract import (
            GitVisibleRef,
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            result = run_github_sync_preflight(
                GitHubSyncPreflightRequest(repo_root=repo, source_paths=("source.txt",)),
                remote_observer=lambda _repo, requested_ref, _fallback: GitVisibleRef(
                    state="connector_unavailable",
                    requested_ref=requested_ref,
                    effective_ref=None,
                    remote_head=None,
                    blockers=("connector_unavailable",),
                ),
            )

            assert result.status == "blocked"
            assert result.github_sync == "failed"
            assert "connector_unavailable" in result.blockers

    def test_authoring_preflight_github_sync_blocks_unresolved_ref_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(self, repo, "--ref", "missing", expected_returncode=1)

            assert payload["status"] == "blocked"
            assert payload["requested_ref"] == "missing"
            assert payload["effective_ref"] is None
            assert "remote_branch_missing" in payload["blockers"]

    def test_authoring_preflight_github_sync_records_explicit_default_branch_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(
                self,
                repo,
                "--ref",
                "missing",
                "--allow-default-branch-fallback",
                expected_returncode=0,
            )

            assert payload["status"] == "pass"
            assert payload["requested_ref"] == "missing"
            assert payload["effective_ref"] == "main"

    def test_authoring_preflight_github_sync_blocks_unknown_default_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            _git(repo, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")

            payload = _run_preflight_json(
                self,
                repo,
                "--ref",
                "missing",
                "--allow-default-branch-fallback",
                expected_returncode=1,
            )

            assert payload["status"] == "blocked"
            assert "default_branch_unknown" in payload["blockers"]

    def test_authoring_preflight_github_sync_reports_source_hash_mismatch_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            payload = _run_preflight_json(
                self,
                repo,
                "--expected-source-hash",
                "not-the-current-hash",
                expected_returncode=1,
            )

            assert payload["status"] == "stale"
            assert payload["source_hash_mismatch_checked"] is True
            assert "source_hash_mismatch" in payload["blockers"]
            assert payload["expected_source_hash"] == "not-the-current-hash"
            assert payload["current_source_hash"] == payload["source_manifest_hash"]

    def test_authoring_preflight_source_manifest_ignores_python_cache_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            package = repo / "package"
            cache = package / "__pycache__"
            cache.mkdir(parents=True)
            (package / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            (cache / "module.cpython-312.pyc").write_bytes(b"cache")

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--source-path",
                    "package",
                    "--diff-summary",
                    "local source manifest fixture",
                    "--unsynced-reason",
                    "testing cache exclusion",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "package/module.py" in payload["source_hashes"]
            assert all("__pycache__" not in path for path in payload["source_hashes"])
            assert all(not path.endswith(".pyc") for path in payload["source_hashes"])

    def test_authoring_preflight_github_sync_compares_expected_manifest_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))
            manifest = repo / "expected.json"
            manifest.write_text(json.dumps({"source_manifest_hash": "old"}) + "\n", encoding="utf-8")
            _git(repo, "add", "expected.json")
            _git(repo, "commit", "-m", "add expected manifest")
            _git(repo, "push", "origin", "main")

            payload = _run_preflight_json(
                self,
                repo,
                "--expected-source-manifest",
                str(manifest),
                expected_returncode=1,
            )

            assert payload["status"] == "stale"
            assert payload["source_hash_mismatch_checked"] is True
            assert "source_hash_mismatch" in payload["blockers"]

    def test_authoring_preflight_local_context_emits_lower_authority_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--provided-context-path",
                    "source.txt",
                    "--unsynced-reason",
                    "local-only review packet",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 0, p.stdout + p.stderr
            assert payload["status"] == "pass"
            assert payload["github_sync"] == "not_verified"
            assert payload["sync_state"] == "local_context"
            assert payload["adoption_requires"] == "explicit_eal_disposition"
            assert payload["provided_context_paths"] == ["source.txt"]
            assert payload["unsynced_reason"] == "local-only review packet"

    def test_authoring_preflight_local_context_reports_source_hash_mismatch_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--provided-context-path",
                    "source.txt",
                    "--unsynced-reason",
                    "local-only review packet",
                    "--expected-source-hash",
                    "not-the-current-hash",
                    "--format",
                    "json",
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "stale"
            assert payload["github_sync"] == "not_verified"
            assert payload["source_hash_mismatch_checked"] is True
            assert "source_hash_mismatch" in payload["blockers"]
            assert payload["expected_source_hash"] == "not-the-current-hash"
            assert payload["current_source_hash"] == payload["source_manifest_hash"]

    @pytest.mark.parametrize(
        ("args", "reason"),
        (
            (["--provided-context-path", "source.txt"], "missing_unsynced_reason"),
            (["--unsynced-reason", "dirty local state"], "missing_context_provenance"),
        ),
    )
    def test_authoring_preflight_local_context_blocks_missing_provenance(self, args: list[str], reason: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            p = _run_authoring_capture(
                self,
                repo,
                [
                    "authoring",
                    "preflight",
                    "github-sync",
                    "--repo-root",
                    str(repo),
                    "--evidence-mode",
                    "local-context",
                    "--format",
                    "json",
                    *args,
                ],
            )

            payload = _json_stdout(p)
            assert p.returncode == 1, p.stdout + p.stderr
            assert payload["status"] == "blocked"
            assert reason in payload["blockers"]

    def test_authoring_preflight_diagnostics_avoid_forbidden_authority_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _create_synced_git_repo(Path(tmp))

            outputs = [
                _run_authoring_capture(self, repo, ["authoring", "preflight", "github-sync", "--repo-root", str(repo)]),
                _run_authoring_capture(
                    self,
                    repo,
                    [
                        "authoring",
                        "preflight",
                        "github-sync",
                        "--repo-root",
                        str(repo),
                        "--expected-source-hash",
                        "old",
                    ],
                ),
                _run_authoring_capture(
                    self,
                    repo,
                    [
                        "authoring",
                        "preflight",
                        "github-sync",
                        "--repo-root",
                        str(repo),
                        "--evidence-mode",
                        "local-context",
                        "--diff-summary",
                        "local edits",
                        "--unsynced-reason",
                        "offline review",
                    ],
                ),
            ]

            for p in outputs:
                output = (p.stdout + p.stderr).lower()
                for forbidden in _FORBIDDEN_AUTHORITY_CLAIMS:
                    assert forbidden not in output

    def test_authoring_preflight_dogfood_runtime_path_exposes_implemented_local_context(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "spec-dock" / "scripts" / "spec-dock"

        p = subprocess.run(
            [
                str(script),
                "authoring",
                "preflight",
                "github-sync",
                "--repo-root",
                str(repo_root),
                "--evidence-mode",
                "local-context",
                "--diff-summary",
                "dogfood mirror smoke",
                "--unsynced-reason",
                "mirror behavior smoke",
                "--format",
                "json",
            ],
            cwd=str(repo_root),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True,
            text=True,
        )

        payload = _json_stdout(p)
        assert p.returncode == 0, p.stdout + p.stderr
        assert payload["status"] == "pass"
        assert payload["github_sync"] == "not_verified"
        assert payload["sync_state"] == "local_context"
        assert "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py" in payload["source_paths"]
        assert "spec-dock/scripts/spec_dock_runtime/commands/authoring.py" in payload["source_paths"]
        assert all("__pycache__" not in path for path in payload["source_hashes"])
        assert all(not path.endswith(".pyc") for path in payload["source_hashes"])


def _run_preflight_json(
    testcase: CliRuntimeHarness,
    repo: Path,
    *extra_args: str,
    expected_returncode: int = 0,
) -> dict[str, object]:
    p = _run_authoring_capture(
        testcase,
        repo,
        [
            "authoring",
            "preflight",
            "github-sync",
            "--repo-root",
            str(repo),
            "--source-path",
            "source.txt",
            "--format",
            "json",
            *extra_args,
        ],
    )
    assert p.returncode == expected_returncode, p.stdout + p.stderr
    return _json_stdout(p)


def _run_authoring_capture(
    testcase: CliRuntimeHarness, repo: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    return testcase._run_runtime_capture(
        repo,
        args,
        env={"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"},
    )


def _json_stdout(p: subprocess.CompletedProcess[str]) -> dict[str, object]:
    try:
        payload = json.loads(p.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(p.stdout + p.stderr) from error
    assert isinstance(payload, dict)
    return payload


def _create_synced_git_repo(root: Path) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git not available")
    remote = root / "remote.git"
    repo = root / "repo"
    _git(root, "init", "--bare", str(remote))
    _git(root, "clone", str(remote), str(repo))
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")
    assert main(["init", str(repo)]) == 0
    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "branch", "-M", "main")
    _git(repo, "push", "-u", "origin", "main")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    return repo


def _stage_change(repo: Path) -> None:
    (repo / "source.txt").write_text("staged\n", encoding="utf-8")
    _git(repo, "add", "source.txt")


def _make_ahead(repo: Path) -> None:
    (repo / "source.txt").write_text("ahead\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "ahead")


def _make_behind(repo: Path) -> None:
    other = repo.parent / "other"
    _git(repo.parent, "clone", str(repo.parent / "remote.git"), str(other))
    _git(other, "config", "user.name", "Test User")
    _git(other, "config", "user.email", "test@example.com")
    (other / "source.txt").write_text("behind\n", encoding="utf-8")
    _git(other, "add", "source.txt")
    _git(other, "commit", "-m", "behind")
    _git(other, "push", "origin", "main")
    _git(repo, "fetch", "origin", "main")


def _make_diverged(repo: Path) -> None:
    _make_behind(repo)
    (repo / "source.txt").write_text("diverged\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "diverged")


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(f"git failed: {args}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

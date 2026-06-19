import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pytest

try:
    from spec_dock.cli import main
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from spec_dock.cli import main


def _expected_spec_dock_version() -> str:
    try:
        return version("spec-dock")
    except PackageNotFoundError:
        text = (Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
        if not match:
            raise AssertionError("failed to read version from pyproject.toml")
        return match.group(1)


_EXPECTED_MANAGED_SKILL_NAMES = (
    "spec-dock-hub",
    "spec-dock-initiative-planning",
    "spec-dock-epic-planning",
    "spec-dock-issue-planning",
    "spec-dock-issue-execution",
    "spec-dock-clarification",
    "spec-dock-adr-facilitation",
    "spec-dock-codex-adapter",
    "spec-dock-copilot-adapter",
    "git-commit-conventional-ja",
    "github-pr-observation",
    "github-pr-creator",
    "github-pr-merge-preparer",
)
_DELETED_ROLE_SKILL_NAMES = (
    "spec-dock-system-architect",
    "spec-dock-implementation-planner",
)


def _assert_is_file(path: Path, message: str | None = None) -> None:
    if not path.is_file():
        raise AssertionError(message or f"expected file to exist: {path}")


def _assert_equal(actual: object, expected: object, message: str | None = None) -> None:
    if actual != expected:
        raise AssertionError(message or f"{actual!r} != {expected!r}")


def _assert_is_instance(value: object, expected_type: type[object]) -> None:
    if not isinstance(value, expected_type):
        raise AssertionError(f"{value!r} is not an instance of {expected_type!r}")


def _assert_is_not_none(value: object, message: str | None = None) -> None:
    if value is None:
        raise AssertionError(message or "unexpected None")


def _assert_in(needle: str, haystack: str, message: str | None = None) -> None:
    if needle not in haystack:
        raise AssertionError(message or f"{needle!r} not found")


def _assert_not_in(needle: str, haystack: str, message: str | None = None) -> None:
    if needle in haystack:
        raise AssertionError(message or f"{needle!r} unexpectedly found")


class CliRuntimeHarness:
    def _init_origin_repo(self, target: Path, *, owner: str = "example", repo: str = "repo") -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")
        self._run_git(target, ["init"])
        self._run_git(target, ["config", "gc.auto", "0"])
        self._run_git(target, ["config", "maintenance.auto", "false"])
        origin_url = f"https://github.com/{owner}/{repo}.git"
        current = self._run_git(target, ["remote", "get-url", "origin"], check=False)
        if current.returncode == 0:
            if current.stdout.strip() != origin_url:
                self._run_git(target, ["remote", "set-url", "origin", origin_url])
            return
        self._run_git(target, ["remote", "add", "origin", origin_url])

    def _create_same_repo_linked_hierarchy(
        self,
        target: Path,
        *,
        owner: str = "example",
        repo: str = "repo",
        initiative_issue_number: int = 1,
        epic_issue_number: int = 2,
        issue_issue_number: int = 3,
        initiative_title: str = "Auth platform",
        epic_title: str = "JWT auth",
        issue_title: str = "Add refresh token",
    ) -> None:
        self._init_origin_repo(target, owner=owner, repo=repo)
        self._run_runtime(
            target,
            [
                "new",
                "initiative",
                "--title",
                initiative_title,
                "--github-issue",
                str(initiative_issue_number),
            ],
        )
        self._run_runtime(
            target,
            [
                "new",
                "epic",
                "--initiative",
                str(initiative_issue_number),
                "--title",
                epic_title,
                "--github-issue",
                str(epic_issue_number),
            ],
        )
        self._run_runtime(
            target,
            [
                "new",
                "issue",
                "--epic",
                str(epic_issue_number),
                "--title",
                issue_title,
                "--github-issue",
                str(issue_issue_number),
            ],
        )

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
        _assert_is_file(script, f"runtime script missing: {script}")

        merged_env = self._runtime_env(target, env)

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
        _assert_is_file(script, f"runtime script missing: {script}")

        merged_env = self._runtime_env(target, env)

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
        _assert_is_file(script, f"runtime script missing: {script}")

        merged_env = self._runtime_env(target, env)

        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(target),
            env=merged_env,
            capture_output=True,
            text=True,
        )

    def _runtime_env(self, target: Path, env: dict[str, str] | None) -> dict[str, str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
            return merged_env
        bin_dir = target / ".test-gh-default"
        bin_dir.mkdir(parents=True, exist_ok=True)
        self._make_default_gh_issue_list_stub(bin_dir)
        merged_env["PATH"] = f"{bin_dir}{os.pathsep}{merged_env.get('PATH', '')}"
        return merged_env

    def _make_default_gh_issue_list_stub(self, bin_dir: Path) -> None:
        gh_path = bin_dir / "gh"
        if gh_path.exists():
            return
        gh_path.write_text(
            "#!/bin/bash\n"
            "set -euo pipefail\n"
            'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
            "  cat <<'JSON'\n"
            "[\n"
            "  {\"number\": 1, \"state\": \"OPEN\", \"title\": \"Issue 1\", \"labels\": [], \"updatedAt\": \"2026-05-13T00:00:01Z\", \"url\": \"https://github.com/example/repo/issues/1\"},\n"
            "  {\"number\": 2, \"state\": \"CLOSED\", \"title\": \"Issue 2\", \"labels\": [], \"updatedAt\": \"2026-05-13T00:00:02Z\", \"url\": \"https://github.com/example/repo/issues/2\"},\n"
            "  {\"number\": 3, \"state\": \"UNKNOWN\", \"title\": \"Issue 3\", \"labels\": [], \"updatedAt\": \"2026-05-13T00:00:03Z\", \"url\": \"https://github.com/example/repo/issues/3\"}\n"
            "]\n"
            "JSON\n"
            "  exit 0\n"
            "fi\n"
            'if [[ "$1" == "issue" && "$2" == "view" ]]; then\n'
            '  n="$3"\n'
            "  python - \"$n\" <<'PY'\n"
            "import json\n"
            "import sys\n"
            "n = int(sys.argv[1].lstrip('#'))\n"
            "print(json.dumps({\n"
            "    'number': n,\n"
            "    'state': 'OPEN',\n"
            "    'title': f'Issue {n}',\n"
            "    'labels': [],\n"
            "    'updatedAt': f'2026-05-13T00:00:{n % 60:02d}Z',\n"
            "    'url': f'https://github.com/example/repo/issues/{n}',\n"
            "}))\n"
            "PY\n"
            "  exit 0\n"
            "fi\n"
            'echo "unexpected gh args: $@" >&2\n'
            "exit 99\n",
            encoding="utf-8",
        )
        gh_path.chmod(0o755)

    def _remove_generated_sync_artifacts(self, target: Path) -> None:
        for rel_path in (
            "spec-dock/.agent/index.json",
            "spec-dock/.agent/tree.json",
            "spec-dock/.agent/index-all.json",
            "spec-dock/.agent/tree-all.json",
            "spec-dock/.agent/deps-issues.json",
            "spec-dock/tree-all.puml",
            "spec-dock/tree.puml",
            "spec-dock/deps-issues.puml",
            "spec-dock/dashboard.md",
        ):
            (target / rel_path).unlink(missing_ok=True)

    def _run_wrapper_capture(
        self,
        script: Path,
        args: list[str],
        *,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        _assert_is_file(script, f"wrapper script missing: {script}")
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
        _assert_is_file(pathfile, f"missing pointer: {pointer} or {pointer}.path")
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
            "#!/bin/bash\n"
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

        normalized: list[dict[str, object]] = []
        for issue in issues:
            item = dict(issue)
            number = item.get("number")
            url = item.get("url")
            if isinstance(number, int) and not (
                isinstance(url, str) and url.startswith("https://github.com/")
            ):
                item["url"] = f"https://github.com/example/repo/issues/{number}"
            normalized.append(item)

        payload = json.dumps(normalized, ensure_ascii=False)
        view_cases = ""
        for item in normalized:
            number = item.get("number")
            if not isinstance(number, int):
                continue
            view_cases += (
                f"    {number})\n"
                "      cat <<'JSON'\n"
                f"{json.dumps(item, ensure_ascii=False)}\n"
                "JSON\n"
                "      exit 0\n"
                "      ;;\n"
            )

        gh_path = bin_dir / "gh"
        gh_path.write_text(
            "#!/bin/bash\n"
            "set -euo pipefail\n"
            'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
            f"{log_line}"
            + ("  echo \"gh stub: simulated failure\" >&2\n  exit 1\n" if fail else "")
            + "  cat <<'JSON'\n"
            + f"{payload}\n"
            + "JSON\n"
            "  exit 0\n"
            "fi\n"
            'if [[ "$1" == "issue" && "$2" == "view" ]]; then\n'
            f"{log_line}"
            '  n="$3"\n'
            "  case \"$n\" in\n"
            f"{view_cases}"
            "  esac\n"
            '  echo "issue not found: $n" >&2\n'
            "  exit 1\n"
            "fi\n"
            'echo "unexpected gh args: $@" >&2\n'
            "exit 99\n",
            encoding="utf-8",
        )
        gh_path.chmod(0o755)

    def _assert_version_file(self, target: Path) -> None:
        version_file = target / "spec-dock" / "spec-dock.version"
        _assert_is_file(version_file)
        _assert_equal(version_file.read_text(encoding="utf-8").strip(), _expected_spec_dock_version())

    def _assert_spec_dock_meta_marker(self, meta: dict[str, object]) -> None:
        marker = meta.get("_spec_dock")
        _assert_is_instance(marker, dict)
        marker_dict = marker
        _assert_equal(marker_dict.get("managed"), True)
        _assert_equal(marker_dict.get("do_not_edit"), True)
        _assert_equal(marker_dict.get("edit_via"), "spec-dock")

    def _assert_readonly_on_posix(self, path: Path) -> None:
        if os.name != "posix":
            return
        mode = path.stat().st_mode
        _assert_equal(
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

    def _remove_github_link(self, node_dir: Path) -> None:
        meta_path = node_dir / ".meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta.pop("github", None)
        self._write_json_force(meta_path, meta)

    def _remove_all_github_links(self, target: Path) -> None:
        for meta_path in (target / "spec-dock").glob("**/.meta.json"):
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if "github" in meta:
                meta.pop("github", None)
                self._write_json_force(meta_path, meta)

    def _to_local_compat_id(self, node_id: str, *, counters: dict[str, int]) -> str:
        match = re.fullmatch(r"(init|epic|iss)(-local)?-(\d{5})", node_id)
        _assert_is_not_none(match, f"unexpected node id format: {node_id}")
        assert match is not None

        prefix, local_marker, number_text = match.groups()
        number = int(number_text)
        if local_marker is not None:
            counters[prefix] = max(counters.get(prefix, 0), number)
            return node_id

        next_number = counters.get(prefix, 0) + 1
        counters[prefix] = next_number
        return f"{prefix}-local-{next_number:05d}"

    def _materialize_local_compat_ids(self, target: Path) -> dict[str, str]:
        spec_root = target / "spec-dock" / "initiatives"
        meta_paths = sorted(spec_root.glob("**/.meta.json"))
        mapping: dict[str, str] = {}
        counters: dict[str, int] = {}
        renames: list[tuple[Path, Path]] = []

        for meta_path in meta_paths:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            node_id = meta.get("id")
            _assert_is_instance(node_id, str)
            assert isinstance(node_id, str)
            local_id = self._to_local_compat_id(node_id, counters=counters)
            mapping[node_id] = local_id

            node_dir = meta_path.parent
            old_prefix = f"{node_id}-"
            assert node_dir.name == node_id or node_dir.name.startswith(old_prefix), (
                f"unexpected node dir name for {node_id}: {node_dir}"
            )
            if node_dir.name == node_id:
                new_name = local_id
            else:
                new_name = node_dir.name.replace(old_prefix, f"{local_id}-", 1)
            renames.append((node_dir, node_dir.with_name(new_name)))

        for meta_path in meta_paths:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta.pop("github", None)
            for field in ("id", "parent_id", "initiative_id", "epic_id"):
                value = meta.get(field)
                if isinstance(value, str) and value in mapping:
                    meta[field] = mapping[value]
            self._write_json_force(meta_path, meta)

        for file_path in sorted(spec_root.glob("**/*")):
            if not file_path.is_file() or file_path.name == ".meta.json":
                continue
            text = file_path.read_text(encoding="utf-8")
            updated = text
            for old_id, local_id in mapping.items():
                updated = updated.replace(old_id, local_id)
            if updated != text:
                self._write_text_force(file_path, updated)

        for old_dir, new_dir in sorted(renames, key=lambda item: len(item[0].parts), reverse=True):
            old_dir.rename(new_dir)

        return mapping

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
        _assert_equal(
            installed_managed,
            sorted(f"{name}/SKILL.md" for name in _EXPECTED_MANAGED_SKILL_NAMES),
        )
        installed_skill_names = {
            skill_file.split("/", 1)[0] for skill_file in self._installed_skill_files(target)
        }
        for deleted_skill_name in _DELETED_ROLE_SKILL_NAMES:
            _assert_equal(
                deleted_skill_name not in installed_skill_names,
                True,
                f"deleted role skill must not be installed: {deleted_skill_name}",
            )

    def _read_text_map(self, base: Path, rel_paths: list[str]) -> dict[str, str]:
        out: dict[str, str] = {}
        for rel in rel_paths:
            path = base / rel
            _assert_is_file(path, f"missing guidance file: {path}")
            out[rel] = path.read_text(encoding="utf-8")
        return out

    def _assert_discussion_guidance_contract(self, text_map: dict[str, str]) -> None:
        combined = "\n".join(text_map.values())

        _assert_in("new doc adr", combined)
        _assert_in("new doc disc", combined)
        _assert_in("new doc research", combined)
        _assert_in("new doc interview", combined)
        _assert_in("new doc scratch", combined)
        _assert_in("new doc draft-requirement", combined)
        _assert_in("new doc draft-design", combined)
        _assert_in("new doc draft-plan", combined)
        _assert_in("canonical docs remain main-orchestrator-only", combined)
        _assert_in("<ts>-<kind>-<slug>.md", combined)
        _assert_in("<ts>-<nn>-<kind>-<slug>.md", combined)
        _assert_in("yyyymmddthhmmssz", combined)
        _assert_in("01..99", combined)
        _assert_in("doc_id", combined)
        _assert_in("grandfathered", combined)
        _assert_in("unrelated files", combined)
        _assert_in("explicit failure", combined)
        _assert_in("archive", combined)

        _assert_not_in("new adr --", combined)
        _assert_not_in("new doc note", combined)
        _assert_not_in("<type>-00001-<slug>.md", combined)
        _assert_not_in("<type>-xxxxx-<slug>.md", combined)
        for rel_path, text in text_map.items():
            if rel_path.endswith("templates/README.md") or rel_path.endswith("scripts/README.md"):
                _assert_in(
                    "<ts>-<kind>-<slug>.md",
                    text,
                    f"timestamp naming contract missing from {rel_path}",
                )
                _assert_in(
                    "yyyymmddthhmmssz",
                    text,
                    f"timestamp token guidance missing from {rel_path}",
                )
                _assert_not_in(
                    "NNN-type-slug.md",
                    text,
                    f"stale sequential naming guidance survived in {rel_path}",
                )
                _assert_in(
                    "unrelated files",
                    text,
                    f"unrelated-file guidance missing from {rel_path}",
                )
                _assert_in(
                    "grandfathered",
                    text,
                    f"legacy-grandfathering guidance missing from {rel_path}",
                )
                _assert_in(
                    "explicit failure",
                    text,
                    f"malformed-filename failure guidance missing from {rel_path}",
                )
                _assert_in(
                    "rules.md",
                    text,
                    f"rules.md ignore example missing from {rel_path}",
                )
                _assert_not_in(
                    "3-digit filename",
                    text,
                    f"stale sequential example survived in {rel_path}",
                )

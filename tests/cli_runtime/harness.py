import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

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
    "spec-driven-tdd-workflow",
    "spec-dock-initiative-planning",
    "spec-dock-epic-planning",
    "spec-dock-issue-execution",
    "spec-dock-adr-facilitation",
)


class CliRuntimeHarness(unittest.TestCase):
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


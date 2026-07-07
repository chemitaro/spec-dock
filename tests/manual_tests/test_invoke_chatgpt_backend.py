import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/authoring-pack/invoke_chatgpt_backend.py"


def run_backend(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    clean_env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"SPECDOCK_CHATGPT_COMMAND", "ORACLE_CHATGPT_COMMAND"}
    }
    clean_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=clean_env,
    )


def base_args(tmp_path: Path) -> list[str]:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("prompt", encoding="utf-8")
    return ["--slug", "test-slug", "-p", "hello", "--file", str(prompt_file)]


def read_json_output(text: str) -> dict:
    return json.loads(text)


def assert_no_host_paths(text: str) -> None:
    assert "/Users/" not in text
    assert "/home/" not in text
    assert "/Volumes/" not in text
    assert "/private/" not in text
    assert ".oracle" not in text


def test_unset_backend_command_fails_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("SPECDOCK_CHATGPT_COMMAND", raising=False)
    monkeypatch.delenv("ORACLE_CHATGPT_COMMAND", raising=False)

    result = run_backend([*base_args(tmp_path), "--dry-run"], {})

    assert result.returncode == 2
    payload = read_json_output(result.stderr)
    assert payload["status"] == "blocked"
    assert "SPECDOCK_CHATGPT_COMMAND" in payload["errors"][0]
    assert "ORACLE_CHATGPT_COMMAND" in payload["errors"][0]
    assert result.stdout == ""
    assert_no_host_paths(result.stderr)


def test_primary_env_takes_precedence_over_fallback(tmp_path) -> None:
    result = run_backend(
        [*base_args(tmp_path), "--dry-run"],
        {
            "SPECDOCK_CHATGPT_COMMAND": "primary-backend --mode 'two words'",
            "ORACLE_CHATGPT_COMMAND": "fallback-backend",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = read_json_output(result.stdout)
    assert payload["backend_env"] == "SPECDOCK_CHATGPT_COMMAND"
    assert payload["backend_argv"] == ["primary-backend", "--mode", "two words"]
    assert payload["invocation_argv"][:5] == ["primary-backend", "--mode", "two words", "--slug", "test-slug"]


def test_fallback_env_is_used_when_primary_is_empty(tmp_path) -> None:
    result = run_backend(
        [*base_args(tmp_path), "--dry-run"],
        {
            "SPECDOCK_CHATGPT_COMMAND": "   ",
            "ORACLE_CHATGPT_COMMAND": "fallback-backend --flag",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = read_json_output(result.stdout)
    assert payload["backend_env"] == "ORACLE_CHATGPT_COMMAND"
    assert payload["backend_argv"] == ["fallback-backend", "--flag"]


def test_malformed_env_command_fails_without_shell(tmp_path) -> None:
    result = run_backend(
        [*base_args(tmp_path), "--dry-run"],
        {"SPECDOCK_CHATGPT_COMMAND": "unterminated 'quote"},
    )

    assert result.returncode == 2
    payload = read_json_output(result.stderr)
    assert payload["status"] == "blocked"
    assert "could not be parsed" in payload["errors"][0]


def test_missing_attachment_fails_before_backend_execution(tmp_path) -> None:
    result = run_backend(
        ["--slug", "test-slug", "-p", "hello", "--file", str(tmp_path / "missing.md"), "--dry-run"],
        {"SPECDOCK_CHATGPT_COMMAND": "backend-command"},
    )

    assert result.returncode == 2
    payload = read_json_output(result.stderr)
    assert payload["status"] == "blocked"
    assert "attachment file does not exist" in payload["errors"][0]
    assert str(tmp_path) not in result.stderr


def test_directory_attachment_fails_before_backend_execution(tmp_path) -> None:
    attachment_dir = tmp_path / "attachment-dir"
    attachment_dir.mkdir()

    result = run_backend(
        ["--slug", "test-slug", "-p", "hello", "--file", str(attachment_dir), "--dry-run"],
        {"SPECDOCK_CHATGPT_COMMAND": "backend-command"},
    )

    assert result.returncode == 2
    payload = read_json_output(result.stderr)
    assert payload["status"] == "blocked"
    assert "attachment path is not a file" in payload["errors"][0]
    assert str(tmp_path) not in result.stderr


def test_dry_run_does_not_invoke_backend(tmp_path) -> None:
    backend = tmp_path / "backend.py"
    sentinel = tmp_path / "sentinel"
    backend.write_text(
        textwrap.dedent(
            f"""
            from pathlib import Path
            Path({str(sentinel)!r}).write_text("called", encoding="utf-8")
            """
        ),
        encoding="utf-8",
    )

    result = run_backend(
        [*base_args(tmp_path), "--dry-run"],
        {"SPECDOCK_CHATGPT_COMMAND": f"{sys.executable} {backend}"},
    )

    assert result.returncode == 0, result.stderr
    payload = read_json_output(result.stdout)
    assert payload["dry_run"] is True
    assert not sentinel.exists()


def test_backend_receives_oracle_compatible_argv_without_shell(tmp_path) -> None:
    backend = tmp_path / "backend.py"
    capture = tmp_path / "argv.json"
    backend.write_text(
        textwrap.dedent(
            f"""
            import json
            from pathlib import Path
            import sys

            Path({str(capture)!r}).write_text(json.dumps(sys.argv[1:]), encoding="utf-8")
            print("backend-ok")
            """
        ),
        encoding="utf-8",
    )
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("prompt", encoding="utf-8")
    context_file = tmp_path / "context.md"
    context_file.write_text("context", encoding="utf-8")

    result = run_backend(
        [
            "--slug",
            "slug-1",
            "-p",
            "hello; exit 99",
            "--file",
            str(prompt_file),
            "--file",
            str(context_file),
        ],
        {"SPECDOCK_CHATGPT_COMMAND": f"{sys.executable} {backend}"},
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "backend-ok\n"
    assert read_json_output(capture.read_text(encoding="utf-8")) == [
        "--slug",
        "slug-1",
        "-p",
        "hello; exit 99",
        "--file",
        str(prompt_file),
        "--file",
        str(context_file),
    ]


def test_backend_exit_code_is_preserved(tmp_path) -> None:
    backend = tmp_path / "backend_fail.py"
    backend.write_text(
        "import sys\nprint('backend-fail')\nprint('backend-error', file=sys.stderr)\nsys.exit(7)\n",
        encoding="utf-8",
    )

    result = run_backend(base_args(tmp_path), {"SPECDOCK_CHATGPT_COMMAND": f"{sys.executable} {backend}"})

    assert result.returncode == 7
    assert result.stdout == "backend-fail\n"
    assert result.stderr == "backend-error\n"


def test_backend_timeout_is_reported_as_blocked(tmp_path) -> None:
    backend = tmp_path / "backend_sleep.py"
    backend.write_text("import time\ntime.sleep(2)\n", encoding="utf-8")

    result = run_backend(
        [*base_args(tmp_path), "--timeout-seconds", "0.1"],
        {"SPECDOCK_CHATGPT_COMMAND": f"{sys.executable} {backend}"},
    )

    assert result.returncode == 2
    payload = read_json_output(result.stderr)
    assert payload["status"] == "blocked"
    assert "timed out" in payload["errors"][0]

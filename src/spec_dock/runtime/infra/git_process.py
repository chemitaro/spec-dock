"""Git subprocess boundary preserving native stderr and timeout uncertainty."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.git_cli import sanitized_git_environment

if TYPE_CHECKING:
    from pathlib import Path


class GitProcessError(RuntimeError):
    def __init__(
        self,
        argv: tuple[str, ...],
        stderr: bytes,
        returncode: int | None,
        *,
        uncertain: bool = False,
        stdout: bytes = b"",
    ) -> None:
        self.argv = argv
        self.stderr = stderr
        self.stdout = stdout
        self.returncode = returncode
        self.uncertain = uncertain
        super().__init__(stderr.decode("utf-8", errors="replace"))

    def details(self) -> dict[str, object]:
        text = self.stderr.decode("utf-8", errors="replace")
        stdout = self.stdout.decode("utf-8", errors="replace")
        return {
            "git": {
                "argv": list(self.argv),
                "stderr": text,
                "stdout": stdout,
                "returncode": self.returncode,
                "decoding_replaced": text.encode("utf-8") != self.stderr or stdout.encode("utf-8") != self.stdout,
                "redacted": False,
            }
        }


def run_git(root: Path, *args: str, timeout: float = 30, mutation: bool = False, missing_ok: bool = False) -> bytes:
    argv = ("git", "-C", str(root), *args)
    try:
        result = subprocess.run(
            argv, capture_output=True, check=False, env=sanitized_git_environment(), timeout=timeout
        )
    except subprocess.TimeoutExpired as error:
        stderr = error.stderr if isinstance(error.stderr, bytes) else (error.stderr or "").encode()
        stdout = error.stdout if isinstance(error.stdout, bytes) else (error.stdout or "").encode()
        raise GitProcessError(argv, stderr, None, uncertain=mutation, stdout=stdout) from error
    except OSError as error:
        raise GitProcessError(argv, str(error).encode(), None) from error
    if result.returncode:
        if missing_ok and result.returncode == 1:
            return b""
        raise GitProcessError(argv, result.stderr, result.returncode, stdout=result.stdout)
    return result.stdout

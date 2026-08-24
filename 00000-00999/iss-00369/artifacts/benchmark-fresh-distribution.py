from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Callable


def _repository_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "pyproject.toml").is_file() and (candidate / "src/spec_dock").is_dir():
            return candidate
    raise RuntimeError("repository root not found")


REPOSITORY = _repository_root()
sys.path.insert(0, str(REPOSITORY / "src"))

from spec_dock import cli  # noqa: E402
from spec_dock import managed_distribution  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark public fresh distribution provisioning.")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--median-seconds", type=float, default=5.0)
    parser.add_argument("--max-seconds", type=float, default=8.0)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.warmup < 0 or args.runs <= 0:
        parser.error("--warmup must be non-negative and --runs must be positive")
    if args.median_seconds <= 0 or args.max_seconds <= 0:
        parser.error("time limits must be positive")
    return args


def _counted_call(
    counters: dict[str, int],
    name: str,
    function: Callable[..., object],
) -> Callable[..., object]:
    def counted(*args: object, **kwargs: object) -> object:
        counters[name] += 1
        return function(*args, **kwargs)

    return counted


def _run_once() -> dict[str, object]:
    counters = {
        "observe_target": 0,
        "open_distribution_parent_chain": 0,
        "journal_publications": 0,
        "os_open": 0,
    }
    real_observe = managed_distribution._observe_target
    real_open_chain = managed_distribution._open_distribution_parent_chain
    real_journal_write = managed_distribution.OperationJournalStore._write
    real_os_open = managed_distribution.os.open
    managed_distribution._observe_target = _counted_call(counters, "observe_target", real_observe)
    managed_distribution._open_distribution_parent_chain = _counted_call(
        counters,
        "open_distribution_parent_chain",
        real_open_chain,
    )
    managed_distribution.OperationJournalStore._write = _counted_call(
        counters,
        "journal_publications",
        real_journal_write,
    )
    managed_distribution.os.open = _counted_call(counters, "os_open", real_os_open)
    try:
        with tempfile.TemporaryDirectory(prefix="spec-dock-i369-benchmark-") as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            output = io.StringIO()
            started = time.perf_counter()
            with redirect_stdout(output), redirect_stderr(output):
                exit_code = cli.main(["init", str(target)])
            elapsed_seconds = time.perf_counter() - started
            if exit_code != 0:
                raise RuntimeError(f"fresh init failed with exit code {exit_code}: {output.getvalue()}")
    finally:
        managed_distribution._observe_target = real_observe
        managed_distribution._open_distribution_parent_chain = real_open_chain
        managed_distribution.OperationJournalStore._write = real_journal_write
        managed_distribution.os.open = real_os_open
    return {"elapsed_seconds": round(elapsed_seconds, 6), **counters}


def main() -> int:
    args = _parse_args()
    for _ in range(args.warmup):
        _run_once()
    runs = [_run_once() for _ in range(args.runs)]
    elapsed = [float(run["elapsed_seconds"]) for run in runs]
    median_seconds = statistics.median(elapsed)
    max_seconds = max(elapsed)
    status = "pass" if median_seconds <= args.median_seconds and max_seconds <= args.max_seconds else "fail"
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = {
        "schema_version": 1,
        "status": status,
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "candidate_sha": head,
        "contract": {
            "warmup": args.warmup,
            "runs": args.runs,
            "median_seconds_max": args.median_seconds,
            "max_seconds_max": args.max_seconds,
        },
        "summary": {
            "median_seconds": round(median_seconds, 6),
            "max_seconds": round(max_seconds, 6),
        },
        "runs": runs,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output_path = args.output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import codecs
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


LEDGER = Path(__file__).with_name("full-regression-ledger.json")
TIMING_WEIGHTS = Path(__file__).with_name("full-regression-timing-weights.json")
DEFAULT_TIMEOUT_SECONDS = 600.0
DEFAULT_MAX_TOTAL_SECONDS = 600.0


def _normalize(message: str, repository: Path) -> str:
    message = message.split(" +  where ", 1)[0]
    message = message.replace(str(repository), "<repo>")
    message = re.sub(r"/tmp/tmp[^/`'\"\\ ]*", "<tmp>", message)
    message = re.sub(
        r"/(?:private/)?var/folders/[^/]+/[^/]+/T/tmp[^/`'\"\\ ]*",
        "<tmp>",
        message,
    )
    message = re.sub(r"/(?:private/)?var/folders/[^'\" ,]+", "<tmp-runtime-path>", message)
    message = re.sub(
        r"(\n\s*Right contains one more item:[^\n]*)\n(?:\s*\n)?\s*Full diff:.*\Z",
        r"\1\n  Use -v to get more diff",
        message,
        flags=re.DOTALL,
    )
    message = message.replace("<repo>/.venv/bin/python3", "<python>")
    message = message.replace("<repo>/.venv/bin/python", "<python>")
    return " ".join(message.split())


def _junit_nodeid(testcase: ET.Element) -> str:
    parts = testcase.attrib["classname"].split(".")
    class_parts: list[str] = []
    while parts and parts[-1][:1].isupper():
        class_parts.insert(0, parts.pop())
    return "/".join(parts) + ".py::" + "::".join((*class_parts, testcase.attrib["name"]))


def _junit_nodeids(junit_path: Path) -> set[str]:
    return {_junit_nodeid(testcase) for testcase in ET.parse(junit_path).getroot().iter("testcase")}


def _failure_signatures(junit_path: Path, repository: Path) -> tuple[dict[str, str], list[str]]:
    failures: dict[str, str] = {}
    errors: list[str] = []
    for testcase in ET.parse(junit_path).getroot().iter("testcase"):
        nodeid = _junit_nodeid(testcase)
        failure = testcase.find("failure")
        if failure is not None:
            normalized = _normalize(failure.attrib.get("message", ""), repository)
            failures[nodeid] = hashlib.sha256(normalized.encode()).hexdigest()
        if testcase.find("error") is not None:
            errors.append(nodeid)
    return failures, errors


def _run_streamed(
    argv: list[str],
    *,
    cwd: Path,
    output_path: Path,
    timeout_seconds: float,
    stream: bool = True,
) -> tuple[int, bool]:
    """Run a verifier subprocess with live output and a hard deadline."""

    started = time.monotonic()
    timed_out = False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as saved:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            start_new_session=True,
        )
        assert process.stdout is not None
        os.set_blocking(process.stdout.fileno(), False)
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        pending = ""

        def emit_available(chunk: bytes, *, final: bool = False) -> None:
            nonlocal pending
            pending += decoder.decode(chunk, final=final)
            lines = pending.splitlines(keepends=True)
            if lines and not lines[-1].endswith(("\n", "\r")) and not final:
                pending = lines.pop()
            else:
                pending = ""
            for line in lines:
                rendered = f"[{time.monotonic() - started:8.1f}s] {line}"
                if stream:
                    print(rendered, end="", flush=True)
                saved.write(rendered)
            if lines:
                saved.flush()

        def drain_available() -> None:
            while True:
                try:
                    chunk = os.read(process.stdout.fileno(), 65536)
                except BlockingIOError:
                    return
                if not chunk:
                    return
                emit_available(chunk)

        try:
            while True:
                elapsed = time.monotonic() - started
                if elapsed >= timeout_seconds:
                    timed_out = True
                    break
                if process.poll() is not None:
                    drain_available()
                    emit_available(b"", final=True)
                    break
                events = selector.select(timeout=min(0.25, timeout_seconds - elapsed))
                if not events:
                    continue
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    continue
                emit_available(chunk)
            if timed_out and process.poll() is None:
                if hasattr(os, "killpg"):
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    if hasattr(os, "killpg"):
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait()
            else:
                process.wait()
            if timed_out:
                drain_available()
                emit_available(b"", final=True)
        finally:
            selector.close()
            if process.stdout is not None:
                process.stdout.close()
    if timed_out:
        timeout_line = f"[timeout] pytest exceeded {timeout_seconds:.1f}s and was terminated\n"
        print(timeout_line, end="", file=sys.stderr, flush=True)
        with output_path.open("a", encoding="utf-8") as saved:
            saved.write(timeout_line)
    return 124 if timed_out else process.returncode or 0, timed_out


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and validate the Issue 368 full-regression ledger.")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="hard timeout for each pytest phase (default: 600 seconds)",
    )
    parser.add_argument(
        "--max-total-seconds",
        type=float,
        default=DEFAULT_MAX_TOTAL_SECONDS,
        help="hard deadline including collection and every shard (default: 600 seconds)",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help="directory in which collection, log, JUnit, and result files are retained",
    )
    parser.add_argument(
        "--shards",
        type=int,
        default=4,
        help="number of deterministic pytest processes to run concurrently (default: 4)",
    )
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be greater than zero")
    if args.max_total_seconds <= 0:
        parser.error("--max-total-seconds must be greater than zero")
    if args.shards <= 0:
        parser.error("--shards must be greater than zero")
    return args


def _timing_evidence(
    *,
    overall_started: float,
    collection_seconds: float,
    shard_elapsed_seconds: float,
    slo_seconds: float,
) -> dict[str, object]:
    total_elapsed_seconds = time.monotonic() - overall_started
    return {
        "collection_seconds": round(collection_seconds, 3),
        "shard_elapsed_seconds": round(shard_elapsed_seconds, 3),
        "total_elapsed_seconds": round(total_elapsed_seconds, 3),
        "slo_seconds": slo_seconds,
        "slo_status": "pass" if total_elapsed_seconds <= slo_seconds else "fail",
    }


def _finalize_result(
    result: dict[str, object],
    *,
    overall_started: float,
    collection_seconds: float,
    shard_elapsed_seconds: float,
    slo_seconds: float,
) -> dict[str, object]:
    finalized = {
        **result,
        **_timing_evidence(
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            shard_elapsed_seconds=shard_elapsed_seconds,
            slo_seconds=slo_seconds,
        ),
    }
    if finalized["slo_status"] != "pass" and finalized["status"] != "total-timeout":
        finalized["underlying_status"] = finalized["status"]
        finalized["status"] = "total-timeout"
    return finalized


def _remaining_phase_budget(
    *,
    overall_started: float,
    max_total_seconds: float,
    phase_timeout_seconds: float,
) -> float:
    remaining = max_total_seconds - (time.monotonic() - overall_started)
    return max(0.0, min(phase_timeout_seconds, remaining))


def _load_timing_weights(repository: Path, head: str) -> tuple[dict[str, float], float]:
    """Load an ancestor-bound timing profile used only for shard balancing."""

    payload = json.loads(TIMING_WEIGHTS.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("full-regression timing weights have an unsupported schema")
    observed_sha = payload.get("observed_sha")
    if not isinstance(observed_sha, str):
        raise ValueError("full-regression timing weights have no observation SHA")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", observed_sha, head],
        cwd=repository,
        check=False,
    )
    if ancestry.returncode != 0:
        raise ValueError("full-regression timing weights are not an ancestor of HEAD")
    default_weight = payload.get("default_seconds")
    raw_weights = payload.get("node_seconds")
    if (
        isinstance(default_weight, bool)
        or not isinstance(default_weight, (int, float))
        or not math.isfinite(default_weight)
        or default_weight <= 0
        or not isinstance(raw_weights, dict)
    ):
        raise ValueError("full-regression timing weights are malformed")
    weights: dict[str, float] = {}
    for nodeid, raw_weight in raw_weights.items():
        if (
            not isinstance(nodeid, str)
            or isinstance(raw_weight, bool)
            or not isinstance(raw_weight, (int, float))
            or not math.isfinite(raw_weight)
            or raw_weight < default_weight
        ):
            raise ValueError("full-regression timing weights are malformed")
        weights[nodeid] = float(raw_weight)
    return weights, float(default_weight)


def _partition_nodeids(
    nodeids: list[str],
    shard_count: int,
    *,
    timing_weights: dict[str, float],
    default_weight: float,
) -> list[list[str]]:
    """Balance estimated runtime deterministically and preserve per-shard order."""

    collection_order = {nodeid: index for index, nodeid in enumerate(nodeids)}
    shards: list[list[str]] = [[] for _ in range(shard_count)]
    shard_weights = [0.0] * shard_count
    weighted_nodes = sorted(
        nodeids,
        key=lambda nodeid: (-timing_weights.get(nodeid, default_weight), collection_order[nodeid]),
    )
    for nodeid in weighted_nodes:
        destination = min(
            range(shard_count),
            key=lambda index: (shard_weights[index], len(shards[index]), index),
        )
        shards[destination].append(nodeid)
        shard_weights[destination] += timing_weights.get(nodeid, default_weight)
    for shard in shards:
        shard.sort(key=collection_order.__getitem__)
    return shards


def main() -> int:
    args = _parse_args()
    overall_started = time.monotonic()
    repository = Path.cwd().resolve()
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    observed = ledger.get("current_head_sha")
    if not isinstance(observed, str):
        print("full-regression ledger has no observation SHA", file=sys.stderr)
        return 2
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", observed, head],
        cwd=repository,
        check=False,
    )
    if ancestry.returncode != 0:
        print("full-regression ledger observation is not an ancestor of HEAD", file=sys.stderr)
        return 2
    expected = {
        entry["nodeid"]: entry["fixed_point_signature_sha256"]
        for entry in ledger.get("failure_paths", [])
        if entry.get("current_status") == "failed"
        and entry.get("fixed_point_status") == "failed"
        and entry.get("disposition") == "approved-no-op"
        and entry.get("failure_signature_match") is True
        and entry.get("current_signature_sha256") == entry.get("fixed_point_signature_sha256")
    }
    if len(expected) != len(ledger.get("failure_paths", [])) or not expected:
        print("full-regression ledger contains incomplete failure signatures", file=sys.stderr)
        return 2
    artifact_root = args.artifact_dir
    if artifact_root is None:
        artifact_root = repository / "spec-dock" / ".workbench" / "full-regression"
    artifact_root = artifact_root.resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = artifact_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    collection_log = run_dir / "collection.log"
    collection_started = time.monotonic()
    collection_budget = _remaining_phase_budget(
        overall_started=overall_started,
        max_total_seconds=args.max_total_seconds,
        phase_timeout_seconds=min(args.timeout_seconds, 120.0),
    )
    if collection_budget <= 0:
        result = {
            "status": "total-timeout",
            **_timing_evidence(
                overall_started=overall_started,
                collection_seconds=0.0,
                shard_elapsed_seconds=0.0,
                slo_seconds=args.max_total_seconds,
            ),
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return 1
    collection_code, collection_timeout = _run_streamed(
        [sys.executable, "-m", "pytest", "--run-full-regression", "--collect-only", "-q"],
        cwd=repository,
        output_path=collection_log,
        timeout_seconds=collection_budget,
        stream=False,
    )
    collection_seconds = time.monotonic() - collection_started
    if collection_timeout or collection_code != 0:
        result = {
            "status": "collection-timeout" if collection_timeout else "collection-failed",
            "exit_code": collection_code,
            "timeout_seconds": args.timeout_seconds,
            **_timing_evidence(
                overall_started=overall_started,
                collection_seconds=collection_seconds,
                shard_elapsed_seconds=0.0,
                slo_seconds=args.max_total_seconds,
            ),
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return 1

    nodeids = [
        line.split("] ", 1)[1].strip()
        for line in collection_log.read_text(encoding="utf-8").splitlines()
        if "] tests/" in line and "::" in line
    ]
    if not nodeids:
        result = {
            "status": "collection-empty",
            "collection_log": str(collection_log),
            **_timing_evidence(
                overall_started=overall_started,
                collection_seconds=collection_seconds,
                shard_elapsed_seconds=0.0,
                slo_seconds=args.max_total_seconds,
            ),
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    print(f"[collection] {len(nodeids)} tests collected; running {min(args.shards, len(nodeids))} shards", flush=True)
    shard_count = min(args.shards, len(nodeids))
    try:
        timing_weights, default_weight = _load_timing_weights(repository, head)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "timing-weights-invalid",
            "reason": str(exc),
            **_timing_evidence(
                overall_started=overall_started,
                collection_seconds=collection_seconds,
                shard_elapsed_seconds=0.0,
                slo_seconds=args.max_total_seconds,
            ),
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    shards = _partition_nodeids(
        nodeids,
        shard_count,
        timing_weights=timing_weights,
        default_weight=default_weight,
    )

    shard_started = time.monotonic()

    def run_shard(index: int, selected: list[str]) -> tuple[int, bool, Path, Path]:
        junit_path = run_dir / f"shard-{index + 1}.xml"
        pytest_log = run_dir / f"shard-{index + 1}.log"
        remaining_total_seconds = _remaining_phase_budget(
            overall_started=overall_started,
            max_total_seconds=args.max_total_seconds,
            phase_timeout_seconds=args.timeout_seconds,
        )
        if remaining_total_seconds <= 0:
            return 124, True, junit_path, pytest_log
        code, timed_out = _run_streamed(
            [
                sys.executable,
                "-m",
                "pytest",
                "--run-full-regression",
                "--full-regression-shard",
                "-q",
                "--durations=50",
                f"--junitxml={junit_path}",
                *selected,
            ],
            cwd=repository,
            output_path=pytest_log,
            timeout_seconds=remaining_total_seconds,
        )
        return code, timed_out, junit_path, pytest_log

    with ThreadPoolExecutor(max_workers=shard_count) as executor:
        shard_results = list(executor.map(lambda item: run_shard(*item), enumerate(shards)))
    shard_elapsed_seconds = time.monotonic() - shard_started
    timing = _timing_evidence(
        overall_started=overall_started,
        collection_seconds=collection_seconds,
        shard_elapsed_seconds=shard_elapsed_seconds,
        slo_seconds=args.max_total_seconds,
    )
    if timing["slo_status"] != "pass":
        result = {
            "status": "total-timeout",
            "timeout_seconds": args.timeout_seconds,
            **timing,
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    invalid_shards = [
        {
            "shard": index + 1,
            "exit_code": code,
            "timed_out": timed_out,
            "junit_path": str(junit_path),
            "pytest_log": str(pytest_log),
        }
        for index, (code, timed_out, junit_path, pytest_log) in enumerate(shard_results)
        if timed_out or code not in {0, 1} or not junit_path.is_file()
    ]
    if invalid_shards:
        result = {
            "status": "shard-timeout-or-failed",
            "timeout_seconds": args.timeout_seconds,
            "shards": invalid_shards,
            **timing,
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    selected_nodes = set(nodeids)
    executed_nodes: set[str] = set()
    actual: dict[str, str] = {}
    errors: list[str] = []
    for _code, _timed_out, junit_path, _pytest_log in shard_results:
        shard_nodes = _junit_nodeids(junit_path)
        overlap = executed_nodes & shard_nodes
        if overlap:
            result = {
                "status": "duplicate-shard-node",
                "nodeids": sorted(overlap),
                **timing,
            }
            (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result, sort_keys=True), file=sys.stderr)
            return 1
        executed_nodes.update(shard_nodes)
        shard_actual, shard_errors = _failure_signatures(junit_path, repository)
        failure_overlap = set(actual) & set(shard_actual)
        if failure_overlap:
            result = {
                "status": "duplicate-shard-node",
                "nodeids": sorted(failure_overlap),
                **timing,
            }
            (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result, sort_keys=True), file=sys.stderr)
            return 1
        actual.update(shard_actual)
        errors.extend(shard_errors)
    if executed_nodes != selected_nodes:
        result = {
            "status": "node-coverage-mismatch",
            "missing_nodes": sorted(selected_nodes - executed_nodes),
            "unexpected_nodes": sorted(executed_nodes - selected_nodes),
            **timing,
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    if errors or actual != expected:
        result = {
            "status": "ledger-mismatch",
            "candidate_sha": head,
            "unexpected_errors": sorted(errors),
            "missing_failures": sorted(set(expected) - set(actual)),
            "unexpected_failures": sorted(set(actual) - set(expected)),
            "signature_mismatches": sorted(
                nodeid for nodeid in set(actual) & set(expected) if actual[nodeid] != expected[nodeid]
            ),
            "shards": [
                {"junit_path": str(junit_path), "pytest_log": str(pytest_log)}
                for _code, _timed_out, junit_path, pytest_log in shard_results
            ],
            **timing,
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    result = _finalize_result(
        {
            "status": "verified",
            "candidate_sha": head,
            "approved_failure_count": len(actual),
            "shards": [
                {"junit_path": str(junit_path), "pytest_log": str(pytest_log)}
                for _code, _timed_out, junit_path, pytest_log in shard_results
            ],
        },
        overall_started=overall_started,
        collection_seconds=collection_seconds,
        shard_elapsed_seconds=shard_elapsed_seconds,
        slo_seconds=args.max_total_seconds,
    )
    (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "verified":
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 1
    print(f"verified {len(actual)} approved failure signatures on candidate {head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

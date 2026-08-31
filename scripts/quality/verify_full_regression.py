"""Run sharded Full Regression and evaluate its pytest observations."""

from __future__ import annotations

import argparse
import codecs
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Literal, cast

from scripts.quality.full_regression_baseline import (
    BaselineContractError,
    CandidateObservation,
    RetirementEvidenceObservation,
    evaluate_baseline,
    parse_baseline,
)

LEDGER = Path(__file__).resolve().parents[2] / "full-regression-ledger.json"
TIMING_WEIGHTS = Path(__file__).resolve().parents[2] / "full-regression-timing-weights.json"
OBSERVATION_SCHEMA_VERSION = 1
_OUTCOMES = frozenset({"passed", "failed", "skipped", "xfailed", "xpassed", "error"})
_RETIREMENT_OUTCOMES = frozenset({"absent", "present", "unknown"})


def observation_to_json(observation: CandidateObservation) -> dict[str, object]:
    """Serialize a typed pytest observation without applying policy."""

    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "collected": list(observation.collected),
        "executed": list(observation.executed),
        "outcomes": dict(observation.outcomes),
        "failure_signatures": dict(observation.failure_signatures),
        "retirement_evidence": {
            evidence_id: {"checked": evidence.checked, "outcome": evidence.outcome}
            for evidence_id, evidence in observation.retirement_evidence.items()
        },
    }


def _observation_array(payload: Mapping[str, object], field: str) -> tuple[str, ...]:
    value = payload.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"observation {field} must be a JSON array of non-empty node IDs")
    return tuple(value)


def _observation_mapping(payload: Mapping[str, object], field: str) -> Mapping[str, object]:
    value = payload.get(field)
    if not isinstance(value, Mapping):
        raise ValueError(f"observation {field} must be a JSON object")
    return cast("Mapping[str, object]", value)


def observation_from_json(payload: Mapping[str, object]) -> CandidateObservation:
    """Deserialize one hook observation; lifecycle policy remains in the evaluator."""

    schema_version = payload.get("schema_version")
    if isinstance(schema_version, bool) or schema_version != OBSERVATION_SCHEMA_VERSION:
        raise ValueError("observation schema_version is unsupported")
    collected = _observation_array(payload, "collected")
    executed = _observation_array(payload, "executed")

    raw_outcomes = _observation_mapping(payload, "outcomes")
    outcomes: dict[str, str] = {}
    for nodeid, outcome in raw_outcomes.items():
        if not isinstance(nodeid, str) or not nodeid or not isinstance(outcome, str) or outcome not in _OUTCOMES:
            raise ValueError("observation contains an invalid outcome")
        outcomes[nodeid] = outcome

    raw_signatures = _observation_mapping(payload, "failure_signatures")
    signatures: dict[str, str] = {}
    for nodeid, signature in raw_signatures.items():
        if not isinstance(nodeid, str) or not nodeid or not isinstance(signature, str) or not signature:
            raise ValueError("observation contains an invalid failure signature")
        signatures[nodeid] = signature

    raw_evidence = _observation_mapping(payload, "retirement_evidence")
    evidence: dict[str, RetirementEvidenceObservation] = {}
    for evidence_id, raw_observation in raw_evidence.items():
        if not isinstance(evidence_id, str) or not evidence_id or not isinstance(raw_observation, Mapping):
            raise ValueError("observation contains invalid retirement evidence")
        checked = raw_observation.get("checked")
        outcome = raw_observation.get("outcome")
        if not isinstance(checked, bool) or not isinstance(outcome, str) or outcome not in _RETIREMENT_OUTCOMES:
            raise ValueError("observation contains invalid retirement evidence")
        evidence[evidence_id] = RetirementEvidenceObservation(
            checked=checked,
            outcome=cast("Literal['absent', 'present', 'unknown']", outcome),
        )

    return CandidateObservation(
        collected=collected,
        executed=executed,
        outcomes=cast("Mapping[str, Literal['passed', 'failed', 'skipped', 'xfailed', 'xpassed', 'error']]", outcomes),
        failure_signatures=signatures,
        retirement_evidence=evidence,
    )


def merge_observations(observations: Sequence[CandidateObservation]) -> CandidateObservation:
    """Concatenate shard observations; duplicate coverage is left for evaluation to reject."""

    collected: list[str] = []
    executed: list[str] = []
    outcomes: dict[str, str] = {}
    signatures: dict[str, str] = {}
    retirement_evidence: dict[str, RetirementEvidenceObservation] = {}
    for observation in observations:
        if not isinstance(observation, CandidateObservation):
            raise TypeError("all shard observations must be CandidateObservation values")
        collected.extend(observation.collected)
        executed.extend(observation.executed)
        outcomes.update(observation.outcomes)
        signatures.update(observation.failure_signatures)
        retirement_evidence.update(observation.retirement_evidence)
    return CandidateObservation(
        collected=tuple(collected),
        executed=tuple(executed),
        outcomes=cast("Mapping[str, Literal['passed', 'failed', 'skipped', 'xfailed', 'xpassed', 'error']]", outcomes),
        failure_signatures=signatures,
        retirement_evidence=retirement_evidence,
    )


def _run_streamed(
    argv: list[str],
    *,
    cwd: Path,
    output_path: Path,
    stream: bool = True,
) -> int:
    """Run a pytest process with live output and retain its complete log."""

    started = time.monotonic()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as saved:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )
        assert process.stdout is not None
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

        while True:
            chunk = process.stdout.read(65536)
            if not chunk:
                break
            emit_available(chunk)
        process.wait()
        emit_available(b"", final=True)
        process.stdout.close()
    return process.returncode or 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and validate the repository Full Regression baseline.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help="directory in which collection, shard, and result artifacts are retained",
    )
    parser.add_argument(
        "--shards",
        type=int,
        default=4,
        help="number of deterministic pytest processes to run concurrently (default: 4)",
    )
    args = parser.parse_args()
    if args.shards <= 0:
        parser.error("--shards must be greater than zero")
    return args


def _timing_evidence(
    *,
    overall_started: float,
    collection_seconds: float,
    shard_elapsed_seconds: float,
) -> dict[str, float]:
    total_elapsed_seconds = time.monotonic() - overall_started
    return {
        "collection_seconds": round(collection_seconds, 3),
        "shard_elapsed_seconds": round(shard_elapsed_seconds, 3),
        "total_elapsed_seconds": round(total_elapsed_seconds, 3),
    }


def _load_timing_weights(repository: Path, head: str) -> tuple[dict[str, float], float]:
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


def _write_result(run_dir: Path, result: Mapping[str, object]) -> None:
    (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _status_result(
    run_dir: Path,
    *,
    status: str,
    overall_started: float,
    return_code: int = 1,
    collection_seconds: float = 0.0,
    shard_elapsed_seconds: float = 0.0,
    **details: object,
) -> int:
    result: dict[str, object] = {
        "status": status,
        **details,
        **_timing_evidence(
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            shard_elapsed_seconds=shard_elapsed_seconds,
        ),
    }
    _write_result(run_dir, result)
    print(json.dumps(result, sort_keys=True), file=sys.stderr)
    return return_code


def main() -> int:
    args = _parse_args()
    overall_started = time.monotonic()
    repository = Path.cwd().resolve()
    artifact_root = args.artifact_dir or repository / "spec-dock" / ".workbench" / "full-regression"
    run_dir = artifact_root.resolve() / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir.mkdir(parents=True, exist_ok=False)

    try:
        ledger_payload = json.loads(LEDGER.read_text(encoding="utf-8"))
        baseline = parse_baseline(ledger_payload)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        observed = ledger_payload.get("current_head_sha")
        if not isinstance(observed, str):
            raise BaselineContractError("full-regression ledger has no observation SHA")
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", observed, head],
            cwd=repository,
            check=False,
        )
        if ancestry.returncode != 0:
            raise BaselineContractError("full-regression ledger observation is not an ancestor of HEAD")
    except (BaselineContractError, OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        return _status_result(
            run_dir,
            status="ledger-invalid",
            overall_started=overall_started,
            return_code=2,
            reason=f"{type(exc).__name__}: {exc}",
        )

    collection_log = run_dir / "collection.log"
    collection_started = time.monotonic()
    collection_code = _run_streamed(
        [sys.executable, "-m", "pytest", "--run-full-regression", "--collect-only", "-q"],
        cwd=repository,
        output_path=collection_log,
        stream=False,
    )
    collection_seconds = time.monotonic() - collection_started
    if collection_code != 0:
        return _status_result(
            run_dir,
            status="collection-failed",
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            exit_code=collection_code,
            collection_log=str(collection_log),
        )

    nodeids = [
        line.split("] ", 1)[1].strip()
        for line in collection_log.read_text(encoding="utf-8").splitlines()
        if "] tests/" in line and "::" in line
    ]
    if not nodeids:
        return _status_result(
            run_dir,
            status="collection-empty",
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            collection_log=str(collection_log),
        )

    shard_count = min(args.shards, len(nodeids))
    try:
        timing_weights, default_weight = _load_timing_weights(repository, head)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        return _status_result(
            run_dir,
            status="timing-weights-invalid",
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            reason=str(exc),
        )
    shards = _partition_nodeids(
        nodeids,
        shard_count,
        timing_weights=timing_weights,
        default_weight=default_weight,
    )
    print(f"[collection] {len(nodeids)} tests collected; running {shard_count} shards", flush=True)

    shard_started = time.monotonic()

    def run_shard(index: int, selected: list[str]) -> tuple[int, Path, Path]:
        observation_path = run_dir / f"shard-{index + 1}.json"
        pytest_log = run_dir / f"shard-{index + 1}.log"
        code = _run_streamed(
            [
                sys.executable,
                "-m",
                "pytest",
                "--run-full-regression",
                "--full-regression-shard",
                f"--full-regression-observation={observation_path}",
                "-q",
                *selected,
            ],
            cwd=repository,
            output_path=pytest_log,
        )
        return code, observation_path, pytest_log

    with ThreadPoolExecutor(max_workers=shard_count) as executor:
        shard_results = list(executor.map(lambda item: run_shard(*item), enumerate(shards)))
    shard_elapsed_seconds = time.monotonic() - shard_started
    shard_details = [
        {
            "shard": index + 1,
            "exit_code": code,
            "observation_path": str(observation_path),
            "pytest_log": str(pytest_log),
        }
        for index, (code, observation_path, pytest_log) in enumerate(shard_results)
    ]
    invalid_shards = [
        shard
        for shard in shard_details
        if shard["exit_code"] not in {0, 1} or not Path(cast("str", shard["observation_path"])).is_file()
    ]
    if invalid_shards:
        return _status_result(
            run_dir,
            status="shard-execution-invalid",
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            shard_elapsed_seconds=shard_elapsed_seconds,
            shards=invalid_shards,
        )

    try:
        observations = [
            observation_from_json(json.loads(observation_path.read_text(encoding="utf-8")))
            for _code, observation_path, _pytest_log in shard_results
        ]
        observation = merge_observations(observations)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return _status_result(
            run_dir,
            status="observation-invalid",
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            shard_elapsed_seconds=shard_elapsed_seconds,
            reason=f"{type(exc).__name__}: {exc}",
            shards=shard_details,
        )

    selected_nodes = set(nodeids)
    if (
        len(observation.collected) != len(set(observation.collected))
        or set(observation.collected) != selected_nodes
        or set(observation.executed) != selected_nodes
    ):
        return _status_result(
            run_dir,
            status="node-coverage-mismatch",
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            shard_elapsed_seconds=shard_elapsed_seconds,
            missing_nodes=sorted(selected_nodes - set(observation.executed)),
            unexpected_nodes=sorted(set(observation.executed) - selected_nodes),
            shards=shard_details,
        )

    evaluation = evaluate_baseline(baseline, observation)
    result = {
        "status": "verified" if evaluation.verified else "ledger-mismatch",
        "candidate_sha": head,
        "evaluation": evaluation.to_dict(),
        "shards": shard_details,
        **_timing_evidence(
            overall_started=overall_started,
            collection_seconds=collection_seconds,
            shard_elapsed_seconds=shard_elapsed_seconds,
        ),
    }
    _write_result(run_dir, result)
    if evaluation.verified:
        print(f"verified {len(evaluation.active_verified)} active baseline failures on candidate {head}")
        return 0
    print(json.dumps(result, sort_keys=True), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

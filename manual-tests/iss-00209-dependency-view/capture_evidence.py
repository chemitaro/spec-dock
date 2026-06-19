#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TRIAL = ROOT / "trial-repo"
SPEC = TRIAL / "spec-dock"
EVIDENCE = ROOT / "evidence"
FAKE_BIN = ROOT / "fake-bin"
SPEC_DOCK = TRIAL / "spec-dock" / "scripts" / "spec-dock"
REPO_ROOT = ROOT.parents[1]
FIXTURE_SPEC = ROOT / "fixture" / "spec-dock"


COMMANDS = [
    (
        "sync-github",
        [str(SPEC_DOCK), "sync", "--github", "--no-update-active"],
        True,
    ),
    (
        "deps-check-ready-iss-01940-github",
        [str(SPEC_DOCK), "deps", "check", "iss-01940", "--github", "--json"],
        True,
    ),
    (
        "deps-check-blocked-iss-01933-github",
        [str(SPEC_DOCK), "deps", "check", "iss-01933", "--github", "--json"],
        True,
    ),
    (
        "deps-check-blocked-iss-01933-no-github",
        [str(SPEC_DOCK), "deps", "check", "iss-01933", "--no-github", "--json"],
        False,
    ),
    (
        "deps-check-unknown-iss-01942-github",
        [str(SPEC_DOCK), "deps", "check", "iss-01942", "--github", "--json"],
        True,
    ),
    (
        "verifier",
        ["./verify_projection.py"],
        False,
    ),
]


def run_command(name, argv, cwd, env):
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    (EVIDENCE / f"{name}.stdout").write_text(proc.stdout, encoding="utf-8")
    (EVIDENCE / f"{name}.stderr").write_text(proc.stderr, encoding="utf-8")
    (EVIDENCE / f"{name}.exit").write_text(f"{proc.returncode}\n", encoding="utf-8")
    return proc.returncode


def prepare_trial_repo(env):
    if not (TRIAL / "spec-dock" / "initiatives").exists():
        (TRIAL / "spec-dock").mkdir(parents=True, exist_ok=True)
        shutil.copytree(FIXTURE_SPEC / "initiatives", TRIAL / "spec-dock" / "initiatives")
    subprocess.run(["git", "init"], cwd=TRIAL, env=env, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "remote", "remove", "origin"],
        cwd=TRIAL,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/example/repo.git"],
        cwd=TRIAL,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["uv", "run", "python", "-m", "spec_dock.cli", "update", str(TRIAL)],
        cwd=REPO_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PATH"] = f"{FAKE_BIN}{os.pathsep}{env.get('PATH', '')}"
    prepare_trial_repo(env)
    results = []
    for name, argv, use_trial_cwd in COMMANDS:
        cwd = TRIAL if use_trial_cwd else ROOT
        code = run_command(name, argv, cwd, env)
        results.append((name, code))

    for rel in [
        ".agent/deps-issues.json",
        "deps-issues.puml",
        "deps-raw.puml",
        "tree.puml",
        "tree-all.puml",
        "dashboard.md",
    ]:
        src = SPEC / rel
        if src.is_file():
            dest = EVIDENCE / rel.replace("/", "__")
            shutil.copy2(src, dest)

    summary = "\n".join(f"{name}: exit={code}" for name, code in results) + "\n"
    (EVIDENCE / "capture-summary.txt").write_text(summary, encoding="utf-8")
    print(summary, end="")
    return 0 if all(code in {0, 3} for _, code in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

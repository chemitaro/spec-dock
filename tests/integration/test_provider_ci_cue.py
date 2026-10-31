"""Provider CI installs the pinned `cue`, checked by SHA-256, before the test suite (iss-00472 AC-09)."""

from __future__ import annotations

from pathlib import Path
import re

from tests.support.cue import CUE_RELEASE_SHA256, PINNED_CUE_VERSION

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/provider-ci.yml"


def _job(workflow: str, name: str) -> str:
    body = workflow.split("\njobs:\n", 1)[1]
    parts = re.split(r"^  (?=[a-z][a-z0-9-]*:\n)", body, flags=re.MULTILINE)
    return next(part for part in parts if part.startswith(f"{name}:\n"))


def _steps(job: str) -> list[str]:
    return job.split("    steps:\n", 1)[1].split("\n      - ")


def _step_name(step: str) -> str:
    match = re.search(r"name: (.+)", step)
    return match.group(1) if match else step.split("\n", 1)[0]


def test_the_test_job_installs_the_pinned_cue_before_running_pytest() -> None:
    steps = _steps(_job(WORKFLOW.read_text(encoding="utf-8"), "provider-tests"))
    names = [_step_name(step) for step in steps]
    assert "Install pinned cue" in names
    assert names.index("Install pinned cue") < names.index("Run provider pytest suite")
    install = steps[names.index("Install pinned cue")]
    assert f"CUE_VERSION: {PINNED_CUE_VERSION}\n" in install
    for platform, digest in CUE_RELEASE_SHA256.items():
        assert re.search(rf"CUE_SHA256_{platform.upper()}: {digest}\n", install), platform
    assert 'Linux/X64) platform=linux_amd64; sha256="$CUE_SHA256_LINUX_AMD64"' in install
    assert 'Linux/ARM64) platform=linux_arm64; sha256="$CUE_SHA256_LINUX_ARM64"' in install
    assert "exit 1" in install.split("esac", 1)[0]
    assert (
        "https://github.com/cue-lang/cue/releases/download/${CUE_VERSION}/cue_${CUE_VERSION}_${platform}.tar.gz"
        in install
    )
    assert 'echo "$sha256  $archive" | sha256sum -c -' in install
    assert install.index("sha256sum -c") < install.index("tar -xzf")
    assert '>> "$GITHUB_PATH"' in install
    assert '"$RUNNER_TEMP/cue-bin/cue" version' in install.rstrip().splitlines()[-1]

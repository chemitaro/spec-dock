"""The spec-dock check workflow runs the verified read-only wheel check once (iss-00440, G4).

Moved from tests/integration/test_ci_fixed_validation.py, whose other tests covered the retired
.github/scripts/specdock-ci-validate.sh (`workspace validate --ci`, removed in 0.5.0). The script half now reads
.github/scripts/specdock-ci-check.sh, which keeps the same source hardening.
"""

from __future__ import annotations

from pathlib import Path

PROVIDER = Path(__file__).resolve().parents[2]
SCRIPT = PROVIDER / ".github/scripts/specdock-ci-check.sh"
WORKFLOW = PROVIDER / ".github/workflows/spec-dock-check.yml"


def test_ci_workflow_uses_verified_read_only_wheel_validator() -> None:
    # Since the canonical cutover, spec-dock checks itself with specdock-ci-check.sh; ci.yml is gone.
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert not (PROVIDER / ".github/workflows/ci.yml").exists()
    assert workflow.count("bash .github/scripts/specdock-ci-check.sh") == 1
    assert "${{ github.sha }}" in workflow
    for forbidden in ("spec-dock sync", "spec-dock/scripts/spec-dock", "workspace sync"):
        assert forbidden not in workflow
    script = SCRIPT.read_text(encoding="utf-8")
    assert "rev-parse --verify 'HEAD^{commit}'" in script
    assert '"$actual_sha" != "$expected_sha"' in script
    assert "fixed_bundle" not in script and "runtime_loader" not in script
    assert 'python-version: "3.11"' in workflow and "python -m pip install uv" in workflow

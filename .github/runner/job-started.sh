#!/bin/sh
# ACTIONS_RUNNER_HOOK_JOB_STARTED for the SpecDock runners (iss-00454). A non-zero exit fails the job before
# its first step, so only a trusted same-repository pull request reaches the job steps.
set -eu
exec /usr/bin/python3 -I /opt/spec-dock-ci/ci-runner-job-gate.py admit --repository chemitaro/spec-dock

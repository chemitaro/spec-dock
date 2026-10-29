#!/bin/sh
# ACTIONS_RUNNER_HOOK_JOB_STARTED for the SpecDock runners on Linux and macOS (iss-00454, iss-00463). A non-zero exit
# fails the job before its first step, so only a trusted same-repository pull request reaches the job steps.
# /opt/spec-dock-ci/python3 is root's link to a fixed interpreter, never a shim that the job's environment can redirect.
set -eu
exec /opt/spec-dock-ci/python3 -I /opt/spec-dock-ci/ci-runner-job-gate.py admit --repository chemitaro/spec-dock

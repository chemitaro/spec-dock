# Shared settings for the SpecDock Linux runner scripts (iss-00454, iss-00463). Sourced, not executed.
SPEC_DOCK_REPOSITORY=chemitaro/spec-dock
RUNNER_VERSION=2.338.2
RUNNER_SHA256=670adb2f268fe21dcbb58b3db0e0aa9d5b3bddfe2c651481336e561ff86de945
RUNNER_USERS="spec-dock-runner-1 spec-dock-runner-2"
RUNNER_HOME=/home
RUNNER_LABEL=spec-dock-ci
# GitHub-hosted runners keep Python in /opt/hostedtoolcache, and the setup-python builds look for libpython there.
TOOL_CACHE=/opt/hostedtoolcache
PYTHON_VERSION=3.11.18
PYTHON_URL=https://github.com/actions/python-versions/releases/download/3.11.18-40260280589/python-3.11.18-linux-24.04-arm64.tar.gz
PYTHON_SHA256=6838120f353f3bbbeb7b234843c4a6c32e5039ee5350acdcd47726c8e7067fa9
# uv comes from this exact wheel, not from a PyPI resolution. To update it, change all three lines (iss-00463 R-4).
UV_VERSION=0.13.6
UV_WHEEL_URL=https://files.pythonhosted.org/packages/05/3b/f78583af6504f1270da95fd0d0935e381f58330c007260f450e81a1e5e1b/uv-0.13.6-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64.whl
UV_WHEEL_SHA256=7ec5486476d67a4214c460b5492393ee2300d84e1de17b293100a019b413568b
# The hooks run the gate with this interpreter through /opt/spec-dock-ci/python3.
GATE_PYTHON=/usr/bin/python3

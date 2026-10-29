# Shared settings for the SpecDock runner scripts (iss-00454). Sourced, not executed.
SPEC_DOCK_REPOSITORY=chemitaro/spec-dock
RUNNER_VERSION=2.338.2
RUNNER_SHA256=670adb2f268fe21dcbb58b3db0e0aa9d5b3bddfe2c651481336e561ff86de945
RUNNER_USERS="spec-dock-runner-1 spec-dock-runner-2"
RUNNER_LABEL=spec-dock-ci
# GitHub-hosted runners keep Python in /opt/hostedtoolcache, and the setup-python builds look for libpython there.
TOOL_CACHE=/opt/hostedtoolcache
PYTHON_VERSION=3.11.18
PYTHON_URL=https://github.com/actions/python-versions/releases/download/3.11.18-40260280589/python-3.11.18-linux-24.04-arm64.tar.gz
PYTHON_SHA256=6838120f353f3bbbeb7b234843c4a6c32e5039ee5350acdcd47726c8e7067fa9
UV_VERSION=0.13.6

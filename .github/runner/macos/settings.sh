# Settings for the SpecDock macOS runner scripts (iss-00463). Sourced, not executed.
SPEC_DOCK_REPOSITORY=chemitaro/spec-dock
RUNNER_VERSION=2.338.2
RUNNER_SHA256=25a065af409ffa317ab4d5a3b614dd15fc9c40f2172bc1b35a1b1258e919a388
RUNNER_USERS=spec-dock-runner
RUNNER_HOME=/Users
RUNNER_LABEL=spec-dock-ci-macos
DAEMON_LABEL=com.chemitaro.spec-dock-ci-runner
ADMIN_USER=admin
# softnet stops the guest from reaching the Mac, including the Mac's DNS, so the guest asks these resolvers.
DNS_SERVERS="1.1.1.1 1.0.0.1"
CACHE=/Library/Caches/spec-dock-ci
# setup-python's macOS builds work only from this path.
TOOL_CACHE=/Users/runner/hostedtoolcache
PYTHON_VERSION=3.11.9
PYTHON_URL=https://github.com/actions/python-versions/releases/download/3.11.9-9947079978/python-3.11.9-darwin-arm64.tar.gz
PYTHON_SHA256=8039644e495c8afb213d3ecb04e9cc3739bb4ddac258432a205cf463997bbeff
PYTHON_SIGNER="Developer ID Installer: Python Software Foundation (BMM5U3QVKW)"
# uv comes from this exact wheel, not from a PyPI resolution. To update it, change all three lines.
UV_VERSION=0.13.6
UV_WHEEL_URL=https://files.pythonhosted.org/packages/f4/14/77230cc4f6a73a31578cb8070a5f67f58a76946ead643ae8a4155620d6da/uv-0.13.6-py3-none-macosx_11_0_arm64.whl
UV_WHEEL_SHA256=51361029b7cf91185d0092c4b356d110b4ad629e9cb11593f1e006ac72a72ca9
# The hooks run the gate with this interpreter through /opt/spec-dock-ci/python3. /usr/bin/python3 is a shim that
# follows DEVELOPER_DIR and similar variables, so it is not used.
GATE_PYTHON=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11

# The Mac side (host-install.sh, host-run-macos-vm.sh, host-ssh.sh).
TART_VERSION=2.41.1
TART_SHA256=e680a734febccfce7d4e910c1f7f13fc3b00f19a181c945e2d746de3214c32c2
SOFTNET_VERSION=0.24.1
SOFTNET_SHA256=8ff8ff099c2b5ac1b1128e7999c4a730ac85f486c8a4cb0239eb98432859a0f7
IMAGE=ghcr.io/cirruslabs/macos-tahoe-vanilla@sha256:eeec54bfe1f076e27786c5d92b89187a05b1d109b5071eb2dcdf02d596e34640
VM_NAME=spec-dock-ci-macos
VM_CPU=4
VM_MEMORY_MB=6144
HOST_TART_HOME=/Volumes/990p2t/vm/spec-dock-ci-tart
HOST_APP_DIR="$HOME/Library/Application Support/spec-dock-ci-macos-vm"
# softnet must be setuid root, which /Volumes/990p2t (owners disabled) cannot hold.
HOST_SOFTNET_DIR=/usr/local/libexec/spec-dock-ci-macos-vm
HOST_AGENT_LABEL=com.chemitaro.spec-dock-ci-macos-vm
# Block new connections from the guest to the Mac side of the vmnet bridge; replies to the Mac's SSH still pass.
SOFTNET_BLOCK="out @host"

#!/bin/sh
# Runs a command in the SpecDock macOS runner VM as its admin user over SSH with the VM's own key (iss-00463):
#   sh .github/runner/macos/host-ssh.sh sudo /opt/spec-dock-ci/register-runner.sh
# The key and known_hosts stay in ~/Library/Application Support/spec-dock-ci-macos-vm/ssh. ~/.ssh and the user's SSH
# configuration and agent are not used, and nothing is forwarded.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
. "$here/settings.sh"
ip=$(TART_HOME=$HOST_TART_HOME "$HOST_APP_DIR/tart.app/Contents/MacOS/tart" ip "$VM_NAME")
exec ssh -F /dev/null -i "$HOST_APP_DIR/ssh/id_ed25519" -o IdentitiesOnly=yes -o IdentityAgent=none \
  -o UserKnownHostsFile="$HOST_APP_DIR/ssh/known_hosts" -o StrictHostKeyChecking=accept-new \
  -o ForwardAgent=no -o ClearAllForwardings=yes -o BatchMode=yes "$ADMIN_USER@$ip" "$@"

#!/bin/sh
# Runs the SpecDock macOS runner VM in the foreground for its LaunchAgent (iss-00463). launchd starts it again when it
# exits, so a VM that shut down comes back. Without the external volume, the VM or a setuid softnet it waits and exits.
# It uses no GitHub credential.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
. "$here/settings.sh"
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
export TART_HOME=$HOST_TART_HOME
softnet=$HOST_SOFTNET_DIR/softnet
if [ ! -d "$TART_HOME/vms/$VM_NAME" ]; then
  echo "$(now) waiting for $TART_HOME/vms/$VM_NAME"
  sleep 240
  exit 0
fi
# Without softnet the VM would get the default NAT network, which reaches the Mac and the LAN; never start it so.
if [ ! -u "$softnet" ] || [ "$(stat -f %u "$softnet")" != 0 ]; then
  echo "$(now) $softnet is not setuid root" >&2
  sleep 240
  exit 1
fi
echo "$(now) starting $VM_NAME"
exec "$HOST_APP_DIR/tart.app/Contents/MacOS/tart" run --no-graphics --net-softnet --net-softnet-block="$SOFTNET_BLOCK" \
  "$VM_NAME"

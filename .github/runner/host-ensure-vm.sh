#!/bin/sh
# Starts the SpecDock runner VM when it is stopped (iss-00454). The LaunchAgent calls this at login and every five
# minutes. It never stops the VM and uses no GitHub credential.
set -eu
LIMACTL="$HOME/Library/Application Support/spec-dock-ci-vm/lima/bin/limactl"
export LIMA_HOME=/Volumes/990p2t/vm/spec-dock-ci-lima
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
[ -d "$LIMA_HOME/spec-dock-ci" ] || { echo "$(now) waiting for $LIMA_HOME/spec-dock-ci"; exit 0; }
status=$("$LIMACTL" list --format '{{.Status}}' spec-dock-ci)
case "$status" in
  Running) ;;
  Stopped) echo "$(now) starting spec-dock-ci"; "$LIMACTL" start spec-dock-ci ;;
  *) echo "$(now) unexpected status of spec-dock-ci: $status" >&2; exit 1 ;;
esac

#!/bin/sh
# Installs the Mac side of the SpecDock macOS runner VM for the current user (iss-00463). Run from the repository root:
#   sh .github/runner/macos/host-install.sh tools   # tart and softnet into ~/Library/Application Support/spec-dock-ci-macos-vm
#   sh .github/runner/macos/host-install.sh vm      # the VM from the pinned image and the Mac's key for its admin user
#   sh .github/runner/macos/host-install.sh agent   # the LaunchAgent that keeps the VM running
#   sh .github/runner/macos/host-install.sh key     # once, on the image's admin password: put the Mac's key in the VM
#   sh .github/runner/macos/host-install.sh guest   # copy the guest files into the VM and run guest-setup.sh there
# None of these uses Homebrew, sudo or a GitHub credential. softnet needs one sudo step after `tools`, which it prints.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
. "$here/../lib.sh"
. "$here/settings.sh"
tart="$HOST_APP_DIR/tart.app/Contents/MacOS/tart"
plist="$HOME/Library/LaunchAgents/$HOST_AGENT_LABEL.plist"
key="$HOST_APP_DIR/ssh/id_ed25519"
export TART_HOME=$HOST_TART_HOME

install_tools() {
  [ ! -e "$HOST_APP_DIR/tart.app" ] || { echo "$HOST_APP_DIR/tart.app already exists" >&2; exit 1; }
  tmp=$(mktemp -d)
  trap 'rm -rf -- "$tmp"' EXIT
  fetch_verified "https://github.com/openai/tart/releases/download/$TART_VERSION/tart.tar.gz" "$tmp/tart.tar.gz" \
    "$TART_SHA256"
  fetch_verified "https://github.com/openai/softnet/releases/download/$SOFTNET_VERSION/softnet.tar.gz" \
    "$tmp/softnet.tar.gz" "$SOFTNET_SHA256"
  # Extract beside the downloads and move into place last, so a failed step leaves nothing half installed.
  mkdir "$tmp/tart" "$tmp/softnet"
  tar -xzf "$tmp/tart.tar.gz" -C "$tmp/tart"
  tar -xzf "$tmp/softnet.tar.gz" -C "$tmp/softnet"
  "$tmp/tart/tart.app/Contents/MacOS/tart" --version
  mkdir -p "$HOST_APP_DIR"
  mv "$tmp/softnet/softnet" "$HOST_APP_DIR/softnet"
  mv "$tmp/tart/tart.app" "$HOST_APP_DIR/tart.app"
  echo "softnet must be setuid root on the internal disk. Run once:"
  echo "  sudo install -d -o root -g wheel -m 755 $HOST_SOFTNET_DIR && sudo install -o root -g wheel -m 4755" \
    "\"$HOST_APP_DIR/softnet\" $HOST_SOFTNET_DIR/softnet"
}

install_vm() {
  [ ! -e "$TART_HOME/vms/$VM_NAME" ] || { echo "$TART_HOME/vms/$VM_NAME already exists" >&2; exit 1; }
  mkdir -p "$TART_HOME"
  "$tart" clone "$IMAGE" "$VM_NAME"
  "$tart" set "$VM_NAME" --cpu "$VM_CPU" --memory "$VM_MEMORY_MB"
  install -d -m 700 "$HOST_APP_DIR/ssh"
  [ -f "$key" ] || ssh-keygen -q -t ed25519 -N '' -C "$VM_NAME admin" -f "$key"
}

install_agent() {
  [ ! -e "$plist" ] || { echo "$plist already exists" >&2; exit 1; }
  mkdir -p "$HOST_APP_DIR" "$(dirname "$plist")"
  install -m 755 "$here/host-run-macos-vm.sh" "$HOST_APP_DIR/host-run-macos-vm.sh"
  install -m 644 "$here/settings.sh" "$HOST_APP_DIR/settings.sh"
  cat >"$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$HOST_AGENT_LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/sh</string><string>$HOST_APP_DIR/host-run-macos-vm.sh</string></array>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>$HOST_SOFTNET_DIR:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>60</integer>
  <key>StandardOutPath</key><string>$HOST_APP_DIR/run-vm.log</string>
  <key>StandardErrorPath</key><string>$HOST_APP_DIR/run-vm.err</string>
</dict>
</plist>
PLIST
  plutil -lint "$plist"
  launchctl bootstrap "gui/$(id -u)" "$plist"
}

install_key() {
  # The image's admin password is "admin" until guest-setup.sh replaces it. Use it once to place the Mac's key.
  tmp=$(mktemp -d)
  trap 'rm -rf -- "$tmp"' EXIT
  printf '#!/bin/sh\necho admin\n' >"$tmp/askpass"
  chmod 700 "$tmp/askpass"
  ip=$("$tart" ip "$VM_NAME")
  SSH_ASKPASS="$tmp/askpass" SSH_ASKPASS_REQUIRE=force DISPLAY=none ssh -F /dev/null -o IdentityAgent=none \
    -o PubkeyAuthentication=no -o PreferredAuthentications=password,keyboard-interactive \
    -o UserKnownHostsFile="$HOST_APP_DIR/ssh/known_hosts" -o StrictHostKeyChecking=accept-new \
    "$ADMIN_USER@$ip" 'umask 077 && mkdir -p ~/.ssh && cat >>~/.ssh/authorized_keys' <"$key.pub"
}

install_guest() {
  # The copy lives in admin's home, where the runner user cannot write; guest-setup.sh refuses any other copy.
  tar -cf - -C "$here" guest-setup.sh settings.sh register-runner.sh -C "$here/.." lib.sh job-started.sh \
    job-completed.sh -C "$here/../../scripts" ci-runner-job-gate.py |
    sh "$here/host-ssh.sh" 'rm -rf ~/spec-dock-runner && mkdir -m 700 ~/spec-dock-runner &&
      tar -xf - -C ~/spec-dock-runner && chmod 644 ~/spec-dock-runner/*'
  sh "$here/host-ssh.sh" sudo sh spec-dock-runner/guest-setup.sh
}

case "${1:-}" in
  tools) install_tools ;;
  vm) install_vm ;;
  agent) install_agent ;;
  key) install_key ;;
  guest) install_guest ;;
  *) echo "usage: $0 tools|vm|agent|key|guest" >&2; exit 2 ;;
esac

#!/bin/sh
# Installs the Mac side of the SpecDock runner VM for the current user (iss-00454).
#   sh .github/runner/host-install.sh lima    # Lima into ~/Library/Application Support/spec-dock-ci-vm/lima
#   sh .github/runner/host-install.sh agent   # the LaunchAgent that keeps the VM running
# Neither step uses Homebrew, sudo or a GitHub credential.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
LIMA_VERSION=2.2.1
app="$HOME/Library/Application Support/spec-dock-ci-vm"
label=com.chemitaro.spec-dock-ci-vm
plist="$HOME/Library/LaunchAgents/$label.plist"

install_lima() {
  [ ! -e "$app/lima" ] || { echo "$app/lima already exists" >&2; exit 1; }
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  archive=lima-$LIMA_VERSION-Darwin-arm64.tar.gz
  base=https://github.com/lima-vm/lima/releases/download/v$LIMA_VERSION
  curl -fsSL -o "$tmp/$archive" "$base/$archive"
  curl -fsSL -o "$tmp/SHA256SUMS" "$base/SHA256SUMS"
  (cd "$tmp" && grep " $archive\$" SHA256SUMS | shasum -a 256 -c -)
  mkdir -p "$app/lima"
  tar -xzf "$tmp/$archive" -C "$app/lima"
  "$app/lima/bin/limactl" --version
}

install_agent() {
  [ ! -e "$plist" ] || { echo "$plist already exists" >&2; exit 1; }
  install -m 755 "$here/host-ensure-vm.sh" "$app/host-ensure-vm.sh"
  cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key>
  <array><string>/bin/sh</string><string>$app/host-ensure-vm.sh</string></array>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>300</integer>
  <key>StandardOutPath</key><string>$app/ensure-vm.log</string>
  <key>StandardErrorPath</key><string>$app/ensure-vm.err</string>
</dict>
</plist>
PLIST
  plutil -lint "$plist"
  launchctl bootstrap "gui/$(id -u)" "$plist"
}

case "${1:-}" in
  lima) install_lima ;;
  agent) install_agent ;;
  *) echo "usage: $0 lima|agent" >&2; exit 2 ;;
esac

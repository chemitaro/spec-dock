#!/bin/sh
# Prepares the SpecDock macOS runner VM as root (iss-00463). host-install.sh guest copies this directory, the shared
# lib.sh and job hooks and ci-runner-job-gate.py into the admin user's home, where no runner user can write, and runs:
#   sudo sh ~/spec-dock-runner/guest-setup.sh
# It is safe to run again: a registered runner restarts when its .env or LaunchDaemon changed. Registration is a
# separate step (register-runner.sh).
set -eu
umask 022
here=$(cd "$(dirname "$0")" && pwd)
. "$here/lib.sh"
# Run only from a copy that no runner user could have replaced.
require_private_copy "$here" "${SUDO_UID:-0}"
. "$here/settings.sh"
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT

# softnet stops the guest from reaching the Mac side of the network, including the DNS it hands out.
networksetup -listallnetworkservices | tail -n +2 | sed 's/^\*//' | while IFS= read -r service; do
  # shellcheck disable=SC2086 # one argument per server
  networksetup -setdnsservers "$service" $DNS_SERVERS
done

# The image's admin has the password "admin", automatic login and screen sharing. Keep admin for the Mac's key with
# passwordless sudo, and leave nobody able to log in to it otherwise.
[ -s "/Users/$ADMIN_USER/.ssh/authorized_keys" ] || { echo "admin has no SSH key yet (host-install.sh key)" >&2; exit 1; }
install -d -m 755 /etc/ssh/sshd_config.d
cat >/etc/ssh/sshd_config.d/010-spec-dock.conf <<SSHD
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
AllowUsers $ADMIN_USER
SSHD
marker=/var/db/spec-dock-ci-admin-password
if [ ! -f "$marker" ]; then
  # Before any runner user exists, so no other account sees the password while dscl runs.
  id -u "$(echo "$RUNNER_USERS" | cut -d ' ' -f 1)" >/dev/null 2>&1 && {
    echo "runner users exist before admin's password was replaced" >&2
    exit 1
  }
  dscl . -passwd "/Users/$ADMIN_USER" "$(openssl rand -base64 32)"
  touch "$marker"
fi
rm -f /etc/kcpassword
defaults delete /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null || true
launchctl disable system/com.apple.screensharing
launchctl bootout system/com.apple.screensharing 2>/dev/null || true
spctl --global-enable
# Routine updates install themselves inside the VM; a major macOS version means rebuilding the VM.
for key in AutomaticCheckEnabled AutomaticDownload CriticalUpdateInstall ConfigDataInstall AutomaticallyInstallMacOSUpdates; do
  defaults write /Library/Preferences/com.apple.SoftwareUpdate "$key" -bool true
done

# git comes from the Command Line Tools.
if [ ! -x /Library/Developer/CommandLineTools/usr/bin/git ]; then
  touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
  label=$(softwareupdate -l 2>/dev/null | sed -n 's/^\* Label: \(Command Line Tools for Xcode.*\)$/\1/p' | sort -V | tail -n 1)
  [ -n "$label" ] || { echo "softwareupdate offers no Command Line Tools" >&2; exit 1; }
  softwareupdate -i "$label"
  rm -f /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
fi

install -d -m 755 /opt /opt/spec-dock-ci "$CACHE"
install -m 644 "$here/settings.sh" "$here/lib.sh" "$here/ci-runner-job-gate.py" /opt/spec-dock-ci/
install -m 755 "$here/job-started.sh" "$here/job-completed.sh" "$here/register-runner.sh" /opt/spec-dock-ci/

# A root-owned tool cache at the hosted path: setup-python finds this Python, and jobs cannot change it.
python_archive=$CACHE/python-$PYTHON_VERSION-darwin-arm64.tar.gz
fetch_verified "$PYTHON_URL" "$python_archive" "$PYTHON_SHA256"
python=$TOOL_CACHE/Python/$PYTHON_VERSION/arm64
if [ ! -f "$python.complete" ]; then
  install -d -m 755 /Users/runner "$TOOL_CACHE" "$tmp/python"
  tar -xzf "$python_archive" -C "$tmp/python" --no-same-owner
  pkgutil --check-signature "$tmp/python/python-$PYTHON_VERSION-macos11.pkg" | grep -q -F "$PYTHON_SIGNER"
  (cd "$tmp/python" && AGENT_TOOLSDIRECTORY=$TOOL_CACHE sh ./setup.sh)
fi
# The Python.org installer leaves the framework writable by the admin group; keep it to root like the rest.
chmod -R go-w "$TOOL_CACHE" /Library/Frameworks/Python.framework "/Applications/Python 3.11"
ln -sfn "$GATE_PYTHON" /opt/spec-dock-ci/python3
uv_wheel=$CACHE/${UV_WHEEL_URL##*/}
fetch_verified "$UV_WHEEL_URL" "$uv_wheel" "$UV_WHEEL_SHA256"
# -I and a neutral working directory keep root's pip from importing anything from where it was started.
(cd / && PIP_ROOT_USER_ACTION=ignore "$python/bin/python3" -I -m pip install --disable-pip-version-check \
  --no-warn-script-location --no-index --no-deps "$uv_wheel")

archive=$CACHE/actions-runner-osx-arm64-$RUNNER_VERSION.tar.gz
fetch_verified "https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-osx-arm64-$RUNNER_VERSION.tar.gz" \
  "$archive" "$RUNNER_SHA256"

n=0
for user in $RUNNER_USERS; do
  n=$((n + 1))
  if ! id -u "$user" >/dev/null 2>&1; then
    # A standard account with a password nobody keeps. It cannot log in over SSH (AllowUsers) or at the login window.
    sysadminctl -addUser "$user" -fullName "SpecDock runner $n" -home "$RUNNER_HOME/$user" \
      -password "$(openssl rand -base64 32)"
    createhomedir -c -u "$user" >/dev/null
    dscl . -create "/Users/$user" IsHidden 1
  fi
  if id -Gn "$user" | tr ' ' '\n' | grep -q -x -E 'admin|wheel|_developer|staffadmin'; then
    echo "$user must not belong to an administrative group" >&2
    exit 1
  fi
  dir=$RUNNER_HOME/$user/actions-runner
  if [ ! -f "$dir/config.sh" ]; then
    sudo -u "$user" mkdir -p "$dir"
    sudo -u "$user" tar -xzf "$archive" -C "$dir"
  fi
  # The runner user edits its own .env, so root never opens a file that user controls.
  changed=$(sudo -u "$user" sh -c '. /opt/spec-dock-ci/lib.sh && set_env_lines "$@"' sh "$dir/.env" \
    ACTIONS_RUNNER_HOOK_JOB_STARTED=/opt/spec-dock-ci/job-started.sh \
    ACTIONS_RUNNER_HOOK_JOB_COMPLETED=/opt/spec-dock-ci/job-completed.sh "AGENT_TOOLSDIRECTORY=$TOOL_CACHE")
  # Root writes the LaunchDaemon itself instead of running svc.sh, whose template the runner user could change.
  label=$DAEMON_LABEL-$n
  cat >"$tmp/plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array><string>$dir/bin/runsvc.sh</string></array>
  <key>UserName</key><string>$user</string>
  <key>WorkingDirectory</key><string>$dir</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Interactive</string>
  <key>SessionCreate</key><true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>ACTIONS_RUNNER_SVC</key><string>1</string>
    <key>HOME</key><string>$RUNNER_HOME/$user</string>
  </dict>
</dict>
</plist>
PLIST
  plutil -lint "$tmp/plist" >/dev/null
  if ! cmp -s "$tmp/plist" "/Library/LaunchDaemons/$label.plist"; then
    install -o root -g wheel -m 644 "$tmp/plist" "/Library/LaunchDaemons/$label.plist"
    changed=changed
  fi
  # A registered runner reads its .env and LaunchDaemon only when it starts.
  if [ -n "$changed" ] && [ -f "$dir/.runner" ]; then
    launchctl bootout "system/$label" 2>/dev/null || true
    launchctl bootstrap system "/Library/LaunchDaemons/$label.plist"
  fi
done

check_root_tree /opt/spec-dock-ci "$TOOL_CACHE" /Library/Frameworks/Python.framework /Library/LaunchDaemons/"$DAEMON_LABEL"-*
echo "SpecDock macOS runner VM is ready for register-runner.sh"

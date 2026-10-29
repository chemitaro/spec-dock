#!/bin/sh
# Registers and starts the SpecDock macOS runner as root inside the VM (iss-00463). Reads one registration token from
# standard input and hands it to config.sh through a pipe, so it never appears in an argument, an environment that sudo
# records, a file or a log:
#   gh api -X POST repos/chemitaro/spec-dock/actions/runners/registration-token --jq .token \
#     | sh .github/runner/macos/host-ssh.sh sudo /opt/spec-dock-ci/register-runner.sh
# It is safe to run again: a runner that is already registered is only started, so no token is needed then.
set -eu
. "$(cd "$(dirname "$0")" && pwd)/settings.sh"
IFS= read -r token || true

n=0
for user in $RUNNER_USERS; do
  n=$((n + 1))
  cd "$RUNNER_HOME/$user/actions-runner"
  if [ ! -f .runner ]; then
    [ -n "${token:-}" ] || { echo "no registration token on standard input" >&2; exit 1; }
    # config.sh reads ACTIONS_RUNNER_INPUT_TOKEN; the runner user's shell sets it from the pipe after sudo has logged.
    printf '%s\n' "$token" | sudo -u "$user" sh -c \
      'IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN && export ACTIONS_RUNNER_INPUT_TOKEN &&
        exec ./config.sh --unattended --url "$1" --name "$2" --labels "$3" --work _work --replace' \
      sh "https://github.com/$SPEC_DOCK_REPOSITORY" "$RUNNER_LABEL-$n" "$RUNNER_LABEL"
  fi
  # guest-setup.sh wrote this LaunchDaemon as root; it runs the runner as the runner user.
  launchctl print "system/$DAEMON_LABEL-$n" >/dev/null 2>&1 ||
    launchctl bootstrap system "/Library/LaunchDaemons/$DAEMON_LABEL-$n.plist"
done

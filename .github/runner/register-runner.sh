#!/bin/sh
# Registers and starts the SpecDock Linux runners as root inside the VM (iss-00454, iss-00463). Reads one registration
# token from standard input and hands it to each runner's config.sh through a pipe, so it never appears in an argument,
# an environment that sudo records, a file or a log:
#   gh api -X POST repos/chemitaro/spec-dock/actions/runners/registration-token --jq .token \
#     | limactl shell spec-dock-ci sudo /opt/spec-dock-ci/register-runner.sh
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
  systemctl enable --now "actions.runner.$(echo "$SPEC_DOCK_REPOSITORY" | tr / -).$RUNNER_LABEL-$n.service"
done

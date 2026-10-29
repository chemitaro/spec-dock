#!/bin/sh
# Registers and starts the SpecDock runners as root inside the VM (iss-00454). Reads one registration token from
# standard input so it never appears in an argument, a file or a log:
#   gh api -X POST repos/chemitaro/spec-dock/actions/runners/registration-token --jq .token \
#     | limactl shell spec-dock-ci sudo /opt/spec-dock-ci/register-runner.sh
set -eu
. /opt/spec-dock-ci/settings.sh
IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN || true
[ -n "${ACTIONS_RUNNER_INPUT_TOKEN:-}" ] || { echo "no registration token on standard input" >&2; exit 1; }
export ACTIONS_RUNNER_INPUT_TOKEN

n=0
for user in $RUNNER_USERS; do
  n=$((n + 1))
  cd "/home/$user/actions-runner"
  sudo --preserve-env=ACTIONS_RUNNER_INPUT_TOKEN -u "$user" ./config.sh --unattended \
    --url "https://github.com/$SPEC_DOCK_REPOSITORY" --name "spec-dock-ci-$n" --labels "$RUNNER_LABEL" \
    --work _work --replace
  ./svc.sh install "$user"
  ./svc.sh start
done

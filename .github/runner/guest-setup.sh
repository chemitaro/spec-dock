#!/bin/sh
# Prepares the SpecDock Linux runner VM as root (iss-00454, iss-00463). Run it inside the guest from a copy of
# .github/runner that also holds .github/scripts/ci-runner-job-gate.py, kept in the Lima user's home where runner users
# cannot write:
#   sudo sh ~/spec-dock-runner/guest-setup.sh
# It is safe to run again: a registered runner restarts when its .env or unit changed. Registration is a separate
# step (register-runner.sh).
set -eu
umask 022
here=$(cd "$(dirname "$0")" && pwd)
. "$here/lib.sh"
# Run only from a copy that no runner user could have replaced.
require_private_copy "$here" "${SUDO_UID:-0}"
. "$here/settings.sh"
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gzip make nftables python3 software-properties-common tar
# Same Git source as the GitHub-hosted Ubuntu image: Ubuntu's 2.43 git-subtree cannot split without a work tree.
add-apt-repository -y ppa:git-core/ppa
apt-get install -y --no-install-recommends git
# Unattended upgrades follow only Ubuntu's own origins unless told otherwise; keep the PPA's git updated as well.
printf '%s\n' 'Unattended-Upgrade::Origins-Pattern { "origin=LP-PPA-git-core"; };' \
  >/etc/apt/apt.conf.d/51spec-dock-git-ppa

# Check the rules before they replace the boot-time file: a broken file would leave the next boot unfiltered.
nft -c -f "$here/nftables.conf"
install -m 644 "$here/nftables.conf" /etc/nftables.conf
systemctl enable nftables
nft -f /etc/nftables.conf

install -d -m 755 /opt/spec-dock-ci
install -m 644 "$here/settings.sh" "$here/lib.sh" "$here/ci-runner-job-gate.py" /opt/spec-dock-ci/
install -m 755 "$here/job-started.sh" "$here/job-completed.sh" "$here/register-runner.sh" /opt/spec-dock-ci/
ln -sfn "$GATE_PYTHON" /opt/spec-dock-ci/python3

install -d -m 755 /var/cache/spec-dock-ci
archive=/var/cache/spec-dock-ci/actions-runner-linux-arm64-$RUNNER_VERSION.tar.gz
fetch_verified "https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-linux-arm64-$RUNNER_VERSION.tar.gz" \
  "$archive" "$RUNNER_SHA256"
# Root runs nothing from a runner user's copy: the dependency installer comes from a root-owned extraction.
dist=/opt/spec-dock-ci/runner-dist-$RUNNER_VERSION
if [ ! -f "$dist/.complete" ]; then
  rm -rf -- "$dist"
  install -d -m 755 "$tmp/dist"
  tar -xzf "$archive" -C "$tmp/dist" --no-same-owner --no-same-permissions
  touch "$tmp/dist/.complete"
  mv -- "$tmp/dist" "$dist"
fi
"$dist/bin/installdependencies.sh"

# A root-owned tool cache at the hosted path: setup-python finds this Python, and jobs cannot change it.
python_archive=/var/cache/spec-dock-ci/python-$PYTHON_VERSION-linux-24.04-arm64.tar.gz
fetch_verified "$PYTHON_URL" "$python_archive" "$PYTHON_SHA256"
python=$TOOL_CACHE/Python/$PYTHON_VERSION/arm64
if [ ! -f "$python.complete" ]; then
  install -d -m 755 "$TOOL_CACHE" "$tmp/python"
  tar -xzf "$python_archive" -C "$tmp/python" --no-same-owner --no-same-permissions
  (cd "$tmp/python" && AGENT_TOOLSDIRECTORY=$TOOL_CACHE sh ./setup.sh)
fi
chmod -R go-w "$TOOL_CACHE"
uv_wheel=/var/cache/spec-dock-ci/${UV_WHEEL_URL##*/}
fetch_verified "$UV_WHEEL_URL" "$uv_wheel" "$UV_WHEEL_SHA256"
# -I and a neutral working directory keep root's pip from importing anything from where it was started.
(cd / && PIP_ROOT_USER_ACTION=ignore "$python/bin/python3" -I -m pip install --disable-pip-version-check \
  --no-warn-script-location --no-index --no-deps "$uv_wheel")

n=0
restart=
for user in $RUNNER_USERS; do
  n=$((n + 1))
  id -u "$user" >/dev/null 2>&1 || useradd --create-home --home-dir "$RUNNER_HOME/$user" --shell /bin/bash --user-group "$user"
  if id -nG "$user" | tr ' ' '\n' | grep -q -x -E 'sudo|admin|adm|wheel|docker|lxd|incus-admin'; then
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
  # Root writes the unit itself instead of running svc.sh, whose template the runner user could change.
  unit=actions.runner.$(echo "$SPEC_DOCK_REPOSITORY" | tr / -).$RUNNER_LABEL-$n.service
  cat >"$tmp/unit" <<UNIT
[Unit]
Description=GitHub Actions Runner ($RUNNER_LABEL-$n)
After=network-online.target

[Service]
ExecStart=$dir/bin/runsvc.sh
User=$user
WorkingDirectory=$dir
KillMode=process
KillSignal=SIGTERM
TimeoutStopSec=5min

[Install]
WantedBy=multi-user.target
UNIT
  if ! cmp -s "$tmp/unit" "/etc/systemd/system/$unit"; then
    install -m 644 "$tmp/unit" "/etc/systemd/system/$unit"
    changed=changed
  fi
  # A registered runner reads its .env and unit only when it starts.
  if [ -n "$changed" ] && [ -f "$dir/.runner" ]; then restart="$restart $unit"; fi
done
systemctl daemon-reload
for unit in $restart; do systemctl restart "$unit"; done

install -d -m 755 /etc/needrestart/conf.d
printf '%s\n' '$nrconf{override_rc}{qr(^actions\.runner\.chemitaro-spec-dock\.spec-dock-ci-\d+\.service$)} = 0;' \
  >/etc/needrestart/conf.d/spec-dock-runner.conf
check_root_tree /opt/spec-dock-ci "$TOOL_CACHE" /etc/systemd/system/actions.runner.*
echo "SpecDock runner VM is ready for register-runner.sh"

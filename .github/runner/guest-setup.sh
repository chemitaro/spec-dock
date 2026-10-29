#!/bin/sh
# Prepares the SpecDock runner VM as root (iss-00454). Run it inside the guest from a copy of .github/runner that
# also holds .github/scripts/ci-runner-job-gate.py, kept in the Lima user's home where runner users cannot write:
#   sudo sh ~/spec-dock-runner/guest-setup.sh
# It is safe to run again. Registration is a separate step (register-runner.sh).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
# Run only from a copy that no runner user could have replaced: owned by root or the invoking user, writable by no one else.
owner=${SUDO_UID:-0}
for path in "$here" "$here"/*; do
  if [ -L "$path" ] || ! stat -c '%u %a' "$path" | grep -q -E "^(0|$owner) [0-7][0145][0145]\$"; then
    echo "refusing to run from $path: it must be owned by root or uid $owner and writable by no one else" >&2
    exit 1
  fi
done
. "$here/settings.sh"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl git gzip make nftables python3 tar

install -m 644 "$here/nftables.conf" /etc/nftables.conf
nft -c -f /etc/nftables.conf
systemctl enable nftables
nft -f /etc/nftables.conf

install -d -m 755 /opt/spec-dock-ci
install -m 644 "$here/settings.sh" "$here/ci-runner-job-gate.py" /opt/spec-dock-ci/
install -m 755 "$here/job-started.sh" "$here/job-completed.sh" "$here/register-runner.sh" /opt/spec-dock-ci/

archive=/var/cache/spec-dock-ci/actions-runner-linux-arm64-$RUNNER_VERSION.tar.gz
install -d -m 755 /var/cache/spec-dock-ci
if [ ! -f "$archive" ]; then
  curl -fsSL -o "$archive.part" \
    "https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-linux-arm64-$RUNNER_VERSION.tar.gz"
  mv "$archive.part" "$archive"
fi
echo "$RUNNER_SHA256  $archive" | sha256sum -c -
# Root runs nothing from a runner user's copy: the dependency installer comes from a root-owned extraction.
dist=/opt/spec-dock-ci/runner-dist-$RUNNER_VERSION
if [ ! -f "$dist/bin/installdependencies.sh" ]; then
  install -d -m 755 "$dist"
  tar -xzf "$archive" -C "$dist" --no-same-owner
fi
"$dist/bin/installdependencies.sh"

n=0
for user in $RUNNER_USERS; do
  n=$((n + 1))
  id -u "$user" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash --user-group "$user"
  if id -nG "$user" | tr ' ' '\n' | grep -q -x -E 'sudo|admin|adm|wheel|docker|lxd|incus-admin'; then
    echo "$user must not belong to an administrative group" >&2
    exit 1
  fi
  dir=/home/$user/actions-runner
  if [ ! -f "$dir/config.sh" ]; then
    sudo -u "$user" mkdir -p "$dir"
    sudo -u "$user" tar -xzf "$archive" -C "$dir"
  fi
  for hook in ACTIONS_RUNNER_HOOK_JOB_STARTED=/opt/spec-dock-ci/job-started.sh \
    ACTIONS_RUNNER_HOOK_JOB_COMPLETED=/opt/spec-dock-ci/job-completed.sh; do
    sudo -u "$user" touch "$dir/.env"
    grep -q -x -F "$hook" "$dir/.env" || echo "$hook" | sudo -u "$user" tee -a "$dir/.env" >/dev/null
  done
  # Root writes the unit itself instead of running svc.sh, whose template the runner user could change.
  unit=/etc/systemd/system/actions.runner.$(echo "$SPEC_DOCK_REPOSITORY" | tr / -).$RUNNER_LABEL-$n.service
  cat > "$unit" <<UNIT
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
  chmod 644 "$unit"
done
systemctl daemon-reload

install -d -m 755 /etc/needrestart/conf.d
printf '%s\n' '$nrconf{override_rc}{qr(^actions\.runner\.chemitaro-spec-dock\.spec-dock-ci-\d+\.service$)} = 0;' \
  > /etc/needrestart/conf.d/spec-dock-runner.conf
echo "SpecDock runner VM is ready for register-runner.sh"

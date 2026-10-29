#!/bin/sh
# ACTIONS_RUNNER_HOOK_JOB_COMPLETED for the SpecDock runners (iss-00454). Removes the checkout and temporary
# files and downloaded actions the job left in this runner's work directory. Only the tool cache stays.
set -eu
work="$HOME/actions-runner/_work"
[ "$(dirname "${RUNNER_TEMP:?}")" = "$work" ] || { echo "unexpected RUNNER_TEMP: $RUNNER_TEMP" >&2; exit 1; }
[ -d "$work" ] && [ ! -L "$work" ] || { echo "unexpected work directory: $work" >&2; exit 1; }
find "$work" -mindepth 1 -maxdepth 1 ! -name _tool -exec rm -rf -- {} +
echo "SpecDock runner removed the job files under $work"

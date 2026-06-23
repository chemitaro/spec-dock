#!/usr/bin/env bash

set -u

TARGETS=(src/spec_dock tests)

run_check() {
  local label="$1"
  shift

  printf '==> %s\n' "$label"
  "$@"
  local status=$?

  if [ "$status" -eq 0 ]; then
    RESULTS+=("$label: pass")
  else
    RESULTS+=("$label: fail ($status)")
    EXIT_CODE=1
  fi
}

EXIT_CODE=0
RESULTS=()

run_check "ruff check" uv run ruff check "${TARGETS[@]}"

printf '\nSummary:\n'
for result in "${RESULTS[@]}"; do
  printf -- '- %s\n' "$result"
done

exit "$EXIT_CODE"

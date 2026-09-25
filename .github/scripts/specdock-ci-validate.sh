#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: specdock-ci-validate.sh SOURCE_CHECKOUT TARGET_CHECKOUT EXPECTED_SOURCE_SHA" >&2
  exit 2
fi

source_root="$(cd "$1" && pwd -P)"
target_root="$(cd "$2" && pwd -P)"
expected_sha="$3"
if [[ ! "$expected_sha" =~ ^([0-9a-f]{40}|[0-9a-f]{64})$ ]]; then
  echo "expected source SHA must be a complete Git commit ID" >&2
  exit 2
fi
if [[ "$(git -C "$source_root" rev-parse --show-toplevel)" != "$source_root" ]]; then
  echo "source must be a Git checkout root" >&2
  exit 2
fi
if [[ "$(git -C "$target_root" rev-parse --show-toplevel)" != "$target_root" ]]; then
  echo "target must be a Git checkout root" >&2
  exit 2
fi
actual_sha="$(git -C "$source_root" rev-parse --verify 'HEAD^{commit}')"
if [[ "$actual_sha" != "$expected_sha" ]]; then
  echo "fixed SpecDock source SHA mismatch" >&2
  exit 3
fi
if [[ -n "$(git -C "$source_root" status --porcelain --untracked-files=all)" ]]; then
  echo "fixed SpecDock source checkout is dirty" >&2
  exit 3
fi

scratch="$(mktemp -d "${TMPDIR:-/tmp}/specdock-ci.XXXXXXXX")"
scratch="$(cd "$scratch" && pwd -P)"
trap 'rm -rf "$scratch"' EXIT
engine_root="$scratch/engine"
package_root="$scratch/package"
mkdir "$package_root"
cp -R "$source_root/src/spec_dock" "$package_root/spec_dock"
version="$(python3 -c 'import sys, tomllib; print(tomllib.load(open(sys.argv[1], "rb"))["project"]["version"])' "$source_root/pyproject.toml")"
printf '%s\n' "$version" > "$package_root/spec_dock/version.txt"
build_output="$(cd "$scratch" && PYTHONPATH="$package_root" PYTHONDONTWRITEBYTECODE=1 python3 -m spec_dock.fixed_bundle "$engine_root")"
engine_path="$engine_root/bin/spec-dock"
if [[ "$build_output" != "$engine_path "* ]]; then
  echo "fixed SpecDock engine builder returned an unexpected result" >&2
  exit 3
fi
distribution_digest="${build_output#"$engine_path "}"
if [[ ! "$distribution_digest" =~ ^[0-9a-f]{64}$ ]]; then
  echo "fixed SpecDock engine digest is invalid" >&2
  exit 3
fi
printf 'SpecDock CI source=%s distribution=%s\n' "$actual_sha" "$distribution_digest"
"$engine_path" --project "$target_root" workspace validate --ci --json

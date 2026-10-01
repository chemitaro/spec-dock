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
  echo "SpecDock source SHA mismatch" >&2
  exit 3
fi
if [[ -n "$(git -C "$source_root" status --porcelain --untracked-files=all)" ]]; then
  echo "SpecDock source checkout is dirty" >&2
  exit 3
fi

scratch="$(mktemp -d "${TMPDIR:-/tmp}/specdock-ci.XXXXXXXX")"
scratch="$(cd "$scratch" && pwd -P)"
trap 'rm -rf "$scratch"' EXIT
build_root="$scratch/source"
wheel_dir="$scratch/wheels"
venv_root="$scratch/installed"
mkdir "$build_root"
git -C "$source_root" archive "$actual_sha" src/spec_dock pyproject.toml README.md setup.py | tar -x -C "$build_root"
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE PYTHONSTARTUP
export PYTHONDONTWRITEBYTECODE=1
cd "$scratch"
uv build --wheel --out-dir "$wheel_dir" "$build_root" >&2
wheels=("$wheel_dir"/*.whl)
if [[ ${#wheels[@]} -ne 1 || ! -f "${wheels[0]}" ]]; then
  echo "SpecDock build must produce exactly one wheel" >&2
  exit 3
fi
wheel="${wheels[0]}"
wheel_sha="$(python3 -c 'import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$wheel")"
python3 -m venv --without-pip "$venv_root"
uv pip install --python "$venv_root/bin/python" "$wheel" >&2
printf 'SpecDock CI source=%s wheel_sha256=%s\n' "$actual_sha" "$wheel_sha"
"$venv_root/bin/spec-dock" --project "$target_root" workspace validate --ci --json

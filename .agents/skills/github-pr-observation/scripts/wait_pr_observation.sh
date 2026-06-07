#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: wait_pr_observation.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA

S01 scaffold only: deterministic PR observation is not implemented yet.
USAGE
}

repo=""
pr=""
head_sha=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo)
      [ "$#" -ge 2 ] || { usage; exit 64; }
      repo="$2"
      shift 2
      ;;
    --pr)
      [ "$#" -ge 2 ] || { usage; exit 64; }
      pr="$2"
      shift 2
      ;;
    --head-sha)
      [ "$#" -ge 2 ] || { usage; exit 64; }
      head_sha="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 64
      ;;
  esac
done

if [ -z "$repo" ] || [ -z "$pr" ] || [ -z "$head_sha" ]; then
  usage
  exit 64
fi

printf '{"status":"not_implemented","script":"wait_pr_observation.sh","message":"S01 scaffold only; PR observation wait behavior is not implemented yet."}\n'
exit 70

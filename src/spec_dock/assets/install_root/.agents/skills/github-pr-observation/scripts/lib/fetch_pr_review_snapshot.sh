#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: fetch_pr_review_snapshot.sh --repo OWNER/REPO --pr NUMBER [--head-sha SHA]

S01 scaffold only: review/comment/thread collection is not implemented yet.
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

if [ -z "$repo" ] || [ -z "$pr" ]; then
  usage
  exit 64
fi

printf '{"status":"not_implemented","script":"fetch_pr_review_snapshot.sh","message":"S01 scaffold only; PR review snapshot behavior is not implemented yet."}\n'
exit 70

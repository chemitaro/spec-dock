---
name: github-pr-observation
description: Observe pull request checks, statuses, reviews, comments, and review threads through fixed read-only scripts. Use when a PR needs deterministic snapshot or wait evidence after creation or push.
---

# GitHub PR Observation

## Overview

Use this skill to collect read-only PR observation evidence through fixed
scripts. The public entrypoints are:

- `scripts/wait_pr_observation.sh`
- `scripts/fetch_pr_observation_snapshot.sh`

The scripts expose a stable public contract for PR observation. `stdout` is
machine-readable JSON only. Progress and diagnostics belong on `stderr` and are
non-authoritative.

## Public Script Contract

- The scripts are read-only and call only fixed GitHub read APIs internally.
- The scripts reject invalid `--repo`, `--pr`, `--head-sha`, timing, progress,
  trigger, body mode, and output options before any `gh` command can run.
- The scripts do not accept arbitrary GitHub endpoints, methods, GraphQL
  queries, request bodies, headers, `jq` expressions, or raw `gh` arguments.
- GitHub auth, rate-limit, schema, or collection failures that can still be
  represented as JSON are returned as non-success observation payloads with
  machine-readable `limitations`.
- `summary.md` is never generated.

## Entry Points

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo owner/repo \
  --pr 13 \
  --head-sha <sha> \
  [--timeout-seconds 1800] \
  [--poll-interval-seconds 30] \
  [--quiet-seconds 90] \
  [--same-fingerprint-count 2] \
  [--zero-check-grace-polls 2] \
  [--trigger-comment-id <issue-comment-id>] \
  [--trigger-created-at <iso8601>] \
  [--body-mode none|trigger-window-truncated|trigger-window-full|out-only] \
  [--progress stderr-summary|none] \
  [--out <dir>]

./.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh \
  --repo owner/repo \
  --pr 13 \
  [--head-sha <sha>] \
  [--trigger-comment-id <issue-comment-id>] \
  [--trigger-created-at <iso8601>] \
  [--body-mode none|trigger-window-truncated|trigger-window-full|out-only] \
  [--out <dir>]
```

## Output Boundary

- `stdout`: exactly one JSON text result.
- `stderr`: progress or diagnostics only.
- default progress: `--progress stderr-summary`.
- progress opt-out: `--progress none`.
- progress lines use bounded ASCII key/value summaries such as `poll`,
  `elapsed`, `remain`, `phase`, `ci`, `review`, `quiet`, and `limit`.
- `--out <dir>` writes debug/audit artifacts, including a `result.json` copy of
  stdout and snapshot/debug files. These artifacts are optional and are not a
  separate authority.

## Current Implementation Limit

This step fixes the public script contract and stream boundary. Detailed CI,
review, thread, body-window, quiet-window, timeout, and final status collection
are implemented by later issue steps. Until then, fixed collection failures and
pending collector details are represented as limitations and non-success JSON.

## Safety Boundary

Do not use the retired `pr-monitor` sub-agent or the retired
`github-codex-pr-review-comments` skill. Do not add a compatibility shim.

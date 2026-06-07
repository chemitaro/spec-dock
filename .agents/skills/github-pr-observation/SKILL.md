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

This S01 scaffold only establishes the installed skill surface and retires the
old `pr-monitor` and `github-codex-pr-review-comments` assets. The scripts are
placeholders until the later implementation steps add the observation behavior.

## Current Scaffold Contract

- The scripts are read-only placeholders.
- The scripts do not accept arbitrary GitHub endpoints, methods, GraphQL
  queries, request bodies, headers, `jq` expressions, or raw `gh` arguments.
- Valid placeholder invocations return a clear `not_implemented` JSON payload.
- Invalid invocations print usage and fail before any GitHub command can run.

## Planned Entry Points

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo owner/repo \
  --pr 13 \
  --head-sha <sha>

./.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh \
  --repo owner/repo \
  --pr 13
```

## Safety Boundary

Do not use the retired `pr-monitor` sub-agent or the retired
`github-codex-pr-review-comments` skill. Do not add a compatibility shim.

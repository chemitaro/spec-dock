---
name: github-pr-observation
description: Trigger a fixed Codex PR review request and observe pull request checks, statuses, reviews, comments, and review threads through bounded scripts. Use when a PR needs deterministic wait or snapshot evidence after creation or push.
---

# GitHub PR Observation

## Overview

Use this skill to request one fixed Codex PR review and collect PR observation
evidence through bounded scripts. The public entrypoints are:

- `scripts/wait_pr_observation.sh`
- `scripts/fetch_pr_observation_snapshot.sh`

`wait_pr_observation.sh` is the normal orchestration entrypoint. By default it
posts exactly one fixed `@codex review` issue comment, then observes CI and
Codex review completion for that trigger boundary. `fetch_pr_observation_snapshot.sh`
is read-only and collects one snapshot. `stdout` is machine-readable JSON only.
Progress and diagnostics belong on `stderr` and are non-authoritative.

This skill has a collection-only boundary. It performs evidence collection and
returns authoritative observation evidence; it does not assign `risk_class`,
decide `need_to_fix`, set `disposition`, or perform repair unit grouping.
Triage and judgment over collected evidence belong to
`github-pr-merge-preparer`.

## Public Script Contract

- `wait_pr_observation.sh` may perform one fixed GitHub write through the
  internal `trigger_codex_review.sh` helper in default `post-once` mode.
- The only allowed write is `POST repos/{owner}/{repo}/issues/{pr}/comments`
  with the fixed body `@codex review`.
- `fetch_pr_observation_snapshot.sh` and the collector libraries remain
  read-only and call only fixed GitHub read APIs internally.
- Check snapshot collection uses a shell wrapper plus the
  `scripts/lib/pr_observation_checks.py` Python entrypoint. The wrapper owns
  public argument validation and script-relative dispatch; the Python entrypoint
  owns fixed `gh` reads, JSON parsing, CI taxonomy, limitations, and payload
  rendering.
- The scripts reject invalid `--repo`, `--pr`, `--head-sha`, timing, progress,
  trigger, body mode, and output options before any `gh` command can run.
- The scripts do not accept arbitrary GitHub endpoints, methods, GraphQL
  queries, request bodies, headers, `jq` expressions, or raw `gh` arguments.
- Callers must not ask an agent to post `@codex review` manually for the normal
  wait flow. The script owns that deterministic trigger action.
- GitHub auth, rate-limit, schema, or collection failures that can still be
  represented as JSON are returned as non-success observation payloads with
  machine-readable `limitations`.
- `summary.md` is never generated.

## Permission Limitations

- The final JSON written to `stdout` is the authority for permission limitation
  semantics; `stderr` progress is non-authoritative.
- `Actions` read is the normal GitHub token permission for CI observation. It
  covers the GitHub Actions workflow runs and jobs used as the primary CI
  evidence for a PR head SHA.
- Checks, commit statuses, and PR status rollup are supplemental observation
  surfaces. When Actions evidence is decisive, unavailable supplemental
  coverage is represented as an informational limitation rather than the normal
  remediation path.
- Blocking GitHub token permission failures are reported with
  `limitations[].code="github_token_permission_denied"` and, when permission
  repair is the needed operator action,
  `recommended_next_action="fix_github_token_permissions"`.
- If `Actions` read is unavailable or CI cannot otherwise be observed
  decisively, final JSON can still be returned with process exit success, but
  the semantic result remains non-success such as
  `normalized_status="unknown"` and `overall_status="unknown"`.
- Do not treat missing Checks read or unavailable status rollup as the ordinary
  fix for Actions-decisive green CI. Treat it as supplemental coverage that may
  limit what was proven, unless readable supplemental evidence shows a failure,
  pending state, or other blocker.
- The fixed `@codex review` trigger comment write failure is separate from read
  collection failures. It returns `normalized_status="human_gate"`,
  `overall_status="human_gate"`, and a
  `limitations[].capability="trigger_comment_write"` permission limitation.
- These scripts remain a fixed PR observation surface, not an arbitrary GitHub
  permission scanner. Do not add caller-provided endpoints, methods, GraphQL,
  headers, request bodies, `jq`, or raw `gh` arguments.
- Token values, `hosts.yml` secrets, and private payloads must never be emitted.

## Entry Points

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo owner/repo \
  --pr 13 \
  --head-sha <sha> \
  [--trigger-mode post-once|resume] \
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

## Trigger Modes

- Default mode is `post-once`.
- In `post-once`, `wait_pr_observation.sh` validates the current PR head, posts
  one fixed `@codex review` comment, captures the helper JSON internally, and
  uses the returned `comment_id` / `created_at` as the observation boundary.
- `post-once` rejects caller-supplied `--trigger-comment-id` and
  `--trigger-created-at`; those values must come from the helper result.
- `resume` never posts a new comment. It requires explicit
  `--trigger-comment-id` and `--trigger-created-at` from a previous final JSON
  result, and continues observation for the same trigger boundary.
- Do not implement an automatic "reuse existing trigger if present" mode. It can
  mix old manual comments, delayed review output, and unrelated automation into
  the current run.

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
- Selected Codex PR review bodies and selected review comment bodies are present
  in the final `stdout` JSON. They are not available only through `--out`.
- Final readiness is scoped to the current `@codex review` trigger or resume
  boundary. The top-level `decision` object and `decision_fingerprint` are the
  authoritative final-status inputs for that boundary.
- `review.current` is explanatory current-boundary context for the same
  decision. It helps explain selected reviews, comments, and threads, but
  callers should treat `decision` as the final decision-facing contract.
- `review.audit`, legacy `review.signals`, legacy `review.threads`, and legacy
  `review.codex_authored` are all-fetched audit/debug context. They can include
  historical artifacts and are not decision-authoritative.
- `audit_fingerprint` is a debug fingerprint for all-fetched audit context. It
  may change because historical or otherwise non-current artifacts changed, and
  must not drive final readiness or wait stability.

## Observation Semantics

Snapshot, wait CI, review, thread, body-window, quiet-window, timeout, and final
status collection are implemented by the public scripts.

- The final JSON written to `stdout` is authoritative.
- Within that JSON, `decision` and `decision_fingerprint` are authoritative for
  the final status, recommended next action, observation completion, progress,
  and wait stability for the current trigger or resume boundary.
- `stderr` progress is bounded and non-authoritative.
- `--out` artifacts are optional debug/audit copies.
- Observation statuses include `passed`, `failed`, `pending`, `running`,
  `none`, `timeout`, `stale_head`, `unknown`, `review_completion_unknown`,
  and `human_gate`.
- CI terminal state and Codex review lifecycle are observed independently and
  merged only in the final wait result.
- Zero Actions workflow runs do not by themselves prove CI success. Readable
  green external check-runs or commit statuses may be sufficient pass evidence
  when no required-missing, pending, failed, unknown, or other blocking evidence
  is observed; no Actions runs plus no readable external evidence remains
  non-pass, and any external non-green evidence wins.
- Actions job expansion is bounded. Failed, running, pending, and unknown
  workflow runs keep diagnostic priority, while terminal-green run expansion may
  be skipped or capped. Collection metadata under
  `ci.actions.jobs_summary.collection` is non-secret operational context;
  failed and non-terminal diagnostics remain preserved where available.
- Codex review completion is primarily detected from Codex-authored submitted PR
  review objects. Issue comments, reactions, or quiet windows are fallback or
  supporting evidence only.
- `review_completion_unknown` is a non-pass terminal-like review state. It means
  CI passed, the observed head matched, no current blocker was selected, and no
  trusted Codex review completion signal was found after the trigger-age and
  CI-passed-age guards are satisfied.
- Stable no-completion evidence for the current boundary must not be collapsed
  into a generic timeout. The top-level result is `human_gate`, with the decision
  reason indicating `review_completion_unknown`, so a human can review the
  no-completion condition explicitly.
- `review_completion_unknown` remains a human gate, not `passed` or
  merge-ready. Below the latency guards, stable no-completion evidence stays in
  the wait/resume path instead of being promoted early.
- `fallback_issue_comment` remains low-confidence evidence. It keeps the final
  status in the `human_gate` / `wait_or_resume` path and does not promote a run
  to `passed`, complete, or merge-ready.
- `fallback_pass_candidate` is a non-promoting signal that a current-boundary
  fallback issue comment appears positive. It is useful context, but it does not
  override the `fallback_issue_comment` gate.
- S102 is deferred until there is an explicit no-findings artifact contract.
  Generic issue comments, zero selected comments, or review request disappearance
  alone must not mark review completion.
- Historical unresolved threads in `review.audit` or the legacy all-fetched
  review fields are audit/debug context only. Only current-boundary selected
  blockers represented through `decision` can drive final review-feedback
  readiness decisions.
- Review bodies selected for the current trigger boundary are included in the
  final `stdout` JSON regardless of `--body-mode`.
- When a timeout or limit occurs before CI and review complete, the final JSON
  includes resume metadata and a resume command hint for continuing the same
  boundary without posting another trigger.
- Same-boundary resume preserves CI-passed age through additive wait metadata so
  delayed `review_completion_unknown` evaluation can continue without posting a
  new trigger.

## Safe Usage

Normal wait after creating or updating a PR:

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo owner/repo \
  --pr 13 \
  --head-sha <sha>
```

Resume after a timeout or external limit:

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo owner/repo \
  --pr 13 \
  --head-sha <sha> \
  --trigger-mode resume \
  --trigger-comment-id <issue-comment-id> \
  --trigger-created-at <iso8601>
```

## Safety Boundary

Do not use the retired `pr-monitor` sub-agent or the retired
`github-codex-pr-review-comments` skill. Do not add a compatibility shim.
Do not bypass this skill by assembling raw `gh api` or GraphQL calls to fetch
review bodies; the final `stdout` JSON is the intended information boundary for
agents.

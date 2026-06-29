---
種別: 設計書（Issue）
ID: "iss-00231"
タイトル: "Inject Trusted Base Branch Codex Review Policy"
関連GitHub: ["#231"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00231 Inject Trusted Base Branch Codex Review Policy — 設計

## 全体像
- 既存の fixed trigger helper を拡張し、PR metadata に `baseRefOid` が含まれる場合だけ trusted base policy を取得する。
- Base policy が取得できる場合、投稿 body は runtime が合成する deterministic multiline text とし、caller-provided body は引き続き受け付けない。
- Base policy が取得できない場合は compatibility fallback として従来の `@codex review` を使い、JSON payload の `review_policy` / `limitations` に状態を記録する。

## 変更対象
- Provider source:
  - `src/spec_dock/assets/install_root/.github/codex/review-policy.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- Dogfooding mirror:
  - `.github/codex/review-policy.md`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- Tests:
  - `tests/unit/infra/test_init_update.py`

## Trigger body contract
- Base policy loaded:
  - first line: `@codex review`
  - metadata block:
    - `source: <owner>/<repo>@<base_sha>:.github/codex/review-policy.md`
    - `policy_sha256: <sha256(policy_text)>`
    - `reviewed_head_sha: <expected_head_sha>`
  - policy text: base SHA contents decoded as UTF-8.
- Base policy unavailable:
  - body remains exact `@codex review`.
  - payload records `review_policy.status` as `missing`, `invalid`, `too_large`, or `base_sha_missing`.

## JSON payload contract
- Existing fields remain:
  - `success`
  - `overall_status`
  - `expected_head_sha`
  - `current_head_sha`
  - `final_head_sha`
  - `trigger`
  - `limitations`
- Added fields:
  - `base_sha`
  - `review_policy`
    - `source`: `base_sha` or `fixed_default`
    - `path`
    - `base_sha`
    - `hash`
    - `bytes`
    - `status`: `loaded`, `missing`, `invalid`, `too_large`, `base_sha_missing`, or `not_requested`

## Policy validation
- The policy source path is fixed to `.github/codex/review-policy.md`.
- The policy source revision is fixed to PR `baseRefOid`.
- The policy content must decode as non-empty UTF-8 text.
- The policy content must be 32 KiB or smaller before it can be included in the trigger body.
- A missing `baseRefOid`, missing contents API result, invalid decode, or size violation keeps the trigger on the fixed `@codex review` fallback and records a limitation.

## Trust boundary
- `gh pr view` supplies current head and base SHA.
- `gh api repos/{owner}/{repo}/contents/.github/codex/review-policy.md?ref=<base_sha>` is the only policy fetch.
- The helper never reads `.github/codex/review-policy.md` from the local checkout or PR head.
- The helper never accepts `--body`, arbitrary endpoint, arbitrary method, GraphQL query, or raw `gh` args.

## Compatibility
- Existing fake fixtures without `baseRefOid` continue to exercise the old fixed-body path.
- Existing recovery logic still compares new comments against the expected `fixed_body`, which is now either exact `@codex review` or the deterministic multiline body.
- Permission-denied behavior remains unchanged.

## I05 trace decisions
- Policy schema / validator / max size:
  - This Issue treats the Markdown policy contract as fixed path + base SHA binding + UTF-8 + non-empty + 32 KiB runtime validation.
  - A standalone JSON schema is not introduced because the policy artifact is Markdown instruction text, not structured JSON.
- Doctor capability:
  - No new `doctor` subcommand branch is introduced in this Issue.
  - Machine-readable trigger limitations are the immediate operational evidence.
  - Dedicated doctor surfacing is deferred to the Epic rollout / operationalization work so it can be validated with the final PR observation workflow.

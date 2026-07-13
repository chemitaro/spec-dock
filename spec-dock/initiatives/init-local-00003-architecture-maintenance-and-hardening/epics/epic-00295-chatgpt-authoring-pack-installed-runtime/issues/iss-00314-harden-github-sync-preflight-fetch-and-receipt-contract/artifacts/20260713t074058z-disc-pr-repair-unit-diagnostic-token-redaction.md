---
種別: disc
ID: "20260713t074058z-disc"
タイトル: "PR Repair Unit U002 Diagnostic Token Redaction"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00314"]
関連: ["20260713t064556z-pr-repair-batch", "PR #321", "comment 3568746650"]
authority: "proposed"
derived_from: ["R003"]
reflected_to: ["report.md"]
---

# PR Repair Unit U002 Diagnostic Token Redaction

- source_batch: `20260713t064556z-pr-repair-batch-pr-repair-batch.md`
- unit_id: U002
- root_cause_family: `fetch-diagnostic-redaction`
- covered_ids: R003
- source_links: PR review comment 3568746650
- failure_class: `review_feedback:fetch-diagnostic-redaction`
- decided_priority: `P1`
- merge_blocking: yes
- disposition: `fix-now`

## Validity Analysis

Valid. `safe_diagnostic` redacts a bare `token=` but not credential-like query keys such as `access_token` or `oauth_token`. The bounded excerpt and its digest can therefore preserve a secret.

## Need-To-Fix Decision

Fix now. Durable diagnostic credential exposure is P1 and belongs in this PR.

## Root Cause

The credential-key redaction pattern is narrower than common URL query parameter names and is not delimiter-aware for `?` / `&` query pairs.

## Options Considered

- Add an allowlist of credential-like query keys and redact values before excerpt/digest: selected.
- Remove all diagnostic excerpts: rejected because it breaks the approved typed diagnostic contract.
- Redact every query value: rejected as unnecessarily destructive to diagnostic usefulness.

## Recommended Design

Extend the existing fail-safe credential redaction stage to case-insensitively cover `access_token`, `oauth_token`, `id_token`, `refresh_token`, `api_key`, and equivalent credential keys when used as URL/query or key-value parameters. Preserve delimiters and redact only the value. Compute digest after redaction.

## Implementation Plan

1. Add red-first parametrized tests for query keys, case variants, `?` and `&` delimiters, and bounded/non-UTF8 input.
2. Extend the existing redaction pattern without changing classification/retry policy.
3. Synchronize provider/dogfood mirror.
4. Run focused security tests, full fetch/writer unit, preflight/pack CLI, Ruff format/lint, mypy, parity, and diff check.

## Validation Plan

- query secrets absent from excerpt and serialized diagnostic
- redacted digest equals digest of safe text
- existing path/key redaction remains green
- `uv run ruff format --check src tests`
- `uv run ruff check src tests`
- `uv run mypy src tests`
- focused tests and provider/dogfood parity

## Out of Scope

The six P2 families, classifier expansion, default source manifest expansion, Windows/relative-origin hardening, pack semantic expansion, and policy constants.

## Implementation Result

Credential-like query/key valuesをdelimiter-preserving allowlistでexcerpt/digest生成前にredactした。red-first 5 failures、Green 38 passed。provider/dogfood parityとfresh code-reviewer PASSを確認。

## Commit Evidence

`4429681577c46d891ac59fb6ad7e0968352077f6`。fetch/writer 56、preflight/pack 78、installed parity 1、Ruff/mypy/diff pass。

## Re-observation Result

new head push後に実行する。

## Residual Risk / Follow-up

Low after focused credential corpus and latest-head re-observation.

---
種別: "Issue draft requirement"
ID: "epic-00295-03"
Issue候補: "C03"
タイトル: "block-first GitHub sync preflight を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["02-add-authoring-command-skeleton"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C03 block-first GitHub sync preflight を実装する — draft requirement

## Purpose

repo-aware ChatGPT invocation 前に local branch / GitHub connector-visible branch / HEAD / source hash が一致していることを fail-closed に確認する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- local repo root、origin、current branch、local HEAD、worktree state を観測する。
- remote tracking branch と GitHub connector-visible branch / HEAD を比較する。
- dirty / staged / untracked / ahead / behind / diverged / missing branch / origin mismatch / source hash mismatch を block する。
- default branch fallback は explicit opt-in の場合だけ `requested_ref` と `effective_ref` を分けて記録する。
- `github-synced` と `local-context` evidence mode の provenance 差分を出力する。

## Non-scope

- ChatGPT backend invocation。
- ZIP review/stage。
- canonical adoption。
- `-f` / `--force` bypass。

## Requirements

- default evidence mode は `github-synced` とする。
- sync preflight pass なしに repo-aware backend invocation を開始しない。
- `local-context` は明示 mode でのみ許可し、`github_sync: not_verified` と `adoption_requires: explicit_eal_disposition` を記録する。
- `local-context` evidence は `github-synced` evidence より低い authority として扱う。
- connector failure、unknown default branch、branch missing は block する。

## Acceptance criteria

- clean/synced branch fixture で `pass` し、requested/effective ref、local HEAD、GitHub HEAD、source hashes を出力する。
- dirty/staged/untracked/unpushed/behind/diverged/branch missing/origin mismatch/source hash mismatch/connector failure/unknown default branch が `blocked` または `stale` になる。
- default fallback は explicit opt-in なしでは発生しない。
- `local-context` mode は synced evidence と同じ authority を主張しない。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）

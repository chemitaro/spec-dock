---
種別: 要件定義書（Issue）
ID: "iss-00297"
タイトル: "Authoring Command Skeleton"
関連GitHub: ["#297"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295", "init-local-00003"]
---

# C02 runtime `authoring` command group skeleton を追加する — draft requirement

## Purpose

installed runtime の primary entrypoint として `./spec-dock/scripts/spec-dock authoring ...` を追加し、help / dispatch / status output の土台を作る。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `commands/authoring.py` を追加する。
- 既存 parser / command registry に `authoring` command group を登録する。
- 初期 supported subcommands を stub または thin use-case call として並べる。
- `CommandOutcome` 互換の machine-readable summary と human-readable diagnostics を返す。

## Non-scope

- GitHub sync preflight の実質ロジック。
- prompt pack 生成、backend invocation、ZIP validation の詳細。
- unsupported/deferred command を実装済みとして見せること。
- PR delivery。

## Requirements

- `authoring --help` は supported command と deferred/unsupported boundary を誤読なく表示する。
- 初期 scope で作らない command は存在しないか、存在しても fail-closed / unsupported とする。
- status taxonomy は `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` / `unreviewed` の意味を維持する。
- command は canonical docs を直接上書きしない。

## Acceptance criteria

- `./spec-dock/scripts/spec-dock authoring --help` が command group と supported subcommands を表示する。
- parser / dispatch tests が通る。
- unsupported command は success status を返さない。
- 中間 Issue として PR delivery を Issue 12 へ defer する evidence が残る。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）

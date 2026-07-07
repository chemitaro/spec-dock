---
種別: "Issue draft requirement"
ID: "epic-00295-05"
Issue候補: "C05"
タイトル: "backend invocation adapter を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["04-prepare-prompt-pack-and-safe-output-constraints"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C05 backend invocation adapter を実装する — draft requirement

## Purpose

ChatGPT backend command を明示設定された場合だけ fail-closed に呼び出し、prompt pack と invocation summary を接続する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `authoring backend invoke` use case を実装する。
- `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` の解決順を実装する。
- 設定値を `shlex.split` 相当に解釈し、shell injection を避ける。
- dry-run と invocation summary を提供する。
- stdout/stderr の保存・表示に redaction policy を適用する。
- `local-context` evidence mode の invocation summary を区別する。

## Non-scope

- 任意の external AI provider registry。
- backend 未設定時の推測実行。
- ChatGPT output の採用・展開。
- PR readiness automation。

## Requirements

- backend command 未設定時は `blocked` とし、推測実行しない。
- CLI override は env vars より優先する。
- `ORACLE_CHATGPT_COMMAND` は compatibility fallback として optional に扱い、廃止時期は open question とする。
- broad `-f` / `--force` を invocation bypass として導入しない。
- host-local absolute path や secret を canonical docs に保存しない。

## Acceptance criteria

- unset backend negative test が `blocked` を返す。
- env var resolution と CLI override tests が通る。
- dry-run が実 process を起動せず invocation plan を出す。
- backend non-zero exit は no adoption の diagnostics になる。
- `local-context` invocation summary が github-synced と区別される。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）

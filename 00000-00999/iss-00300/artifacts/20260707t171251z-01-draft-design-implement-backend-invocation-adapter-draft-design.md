---
種別: 設計書（Issue）
ID: "iss-00300"
タイトル: "Backend Invocation Adapter"
Issue Grade: "standard"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C05 backend invocation adapter を実装する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `authoring backend invoke` use case を実装する。
- `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` の解決順を実装する。
- 設定値を `shlex.split` 相当に解釈し、shell injection を避ける。
- dry-run と invocation summary を提供する。
- stdout/stderr の保存・表示に redaction policy を適用する。
- `local-context` evidence mode の invocation summary を区別する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/cli_json.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/cli_text.py

## Runtime / docs / skill impact

- Runtime: backend process adapter と dry-run を追加する。
- Docs: backend command reference と env var priority を更新する。
- Skill: ChatGPT evidence lane の backend availability gate になる。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- 未設定 backend を暗黙に選ぶ。
- shell=True 相当で command injection risk を作る。
- stderr に secret や host-local absolute path を残す。
- backend success を adoption success と誤記する。

## Tests / validation impact

- backend unset fail-closed test
- CLI override priority test
- env var priority test
- dry-run summary test
- non-zero exit diagnostics test
- force bypass rejection test

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

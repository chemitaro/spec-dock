---
種別: 設計書（Issue）
ID: "iss-00297"
タイトル: "Authoring Command Skeleton"
Issue Grade: "standard"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C02 runtime `authoring` command group skeleton を追加する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `commands/authoring.py` を追加する。
- 既存 parser / command registry に `authoring` command group を登録する。
- 初期 supported subcommands を stub または thin use-case call として並べる。
- `CommandOutcome` 互換の machine-readable summary と human-readable diagnostics を返す。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/* parser / registry
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/*

## Runtime / docs / skill impact

- Runtime: command group skeleton と dispatch table を追加する。
- Docs: help snapshot と supported/deferred command list を後続 docs の source にする。
- Skill: 後続 skill docs が呼ぶ installed runtime command の surface を固定する。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- stub が実行成功や adoption 完了を主張する。
- `authoring adopt` など deferred command が初期 scope に紛れ込む。
- human-readable output しかなく automation が status を読めない。
- help wording が未実装 command を利用可能に見せる。

## Tests / validation impact

- CLI help snapshot test
- parser dispatch unit test
- unsupported/deferred command fail-closed test
- machine-readable summary schema test

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

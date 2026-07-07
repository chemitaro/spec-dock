---
種別: 設計書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
Issue Grade: "standard"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C10 approval check と stop-gate evidence reports を実装する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `authoring approval check` を実装する。
- approval evidence schema を定義する。
- requested scope、effective scope、candidate pack digest、approver、timestamp、approval statement を検査する。
- missing approval、stale digest、scope mismatch を block する。
- unsupported auto-creation diagnostics を出す。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/approval_check.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py

## Runtime / docs / skill impact

- Runtime: approval gate report command を追加する。
- Docs: Issue Decomposition Approval Gate と Epic Portfolio Approval Gate の evidence shape を更新する。
- Skill: Initiative/Epic planning の human stop gate を machine-readable にする。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- approval check pass を node creation execution と誤解する。
- approval statement と candidate digest の紐付けがない。
- ChatGPT self-approval を許容する。
- approval evidence が stale でも pass する。

## Tests / validation impact

- approval pass fixture
- missing approval blocked fixture
- stale candidate digest fixture
- scope mismatch fixture
- unsupported auto-creation diagnostics test

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

---
種別: 設計書（Issue）
ID: "iss-00306"
タイトル: "Runtime Workflow Guidance"
Issue Grade: "standard"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C11 runtime docs / reference docs / workflow guidance を更新する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- ChatGPT authoring pack workflow docs を追加・更新する。
- backend reference、safe ZIP handling、candidate validation、approval gate、local-context mode を文書化する。
- Initiative/Epic/Issue workflow docs に skill ordering と stop gate を反映する。
- deferred commands を利用可能と誤読させない wording にする。
- manual fallback と `local-context` の adoption limitation を明示する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md
- src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md
- src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md
- src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
- src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
- src/spec_dock/assets/spec_dock/docs/workflow_epic.md
- src/spec_dock/assets/spec_dock/docs/workflow_issue.md

## Runtime / docs / skill impact

- Runtime: help text と docs examples の整合性を検証する。
- Docs: user-facing guide を完成させる。
- Skill: skill docs との cross-reference を追加する。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- 未実装 command を usage example として載せる。
- `local-context` を synced evidence と同じ authority に見せる。
- final Issue のみ PR delivery という policy を抜かす。
- manual fallback が canonical adoption を bypass できるように読める。

## Tests / validation impact

- docs trace matrix review
- command example smoke check
- git diff --check
- deferred command wording check
- terminology consistency check

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

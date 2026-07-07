---
種別: 設計書（Issue）
ID: "iss-00299"
タイトル: "Prompt Pack Constraints"
Issue Grade: "standard"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C04 prompt pack prepare と safe output constraints を実装する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `authoring pack prepare` use case を実装する。
- source-manifest、stale-if、safe-output-constraints、mode-specific prompt config を生成する。
- forbidden authority claims を prompt と validator contract に埋め込む。
- Initiative/Epic/Issue/selected-skeleton の mode selection を扱う。
- `local-context` prompt pack では provided context と unsynced reason を明記する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/prepare_chatgpt_authoring_pack.py

## Runtime / docs / skill impact

- Runtime: `authoring pack prepare` を実装する。
- Docs: safe output constraints と forbidden claim list の source になる。
- Skill: `spec-dock-chatgpt-authoring` が生成する prompt pack の標準形になる。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- prompt pack が stale source を区別しない。
- ChatGPT に forbidden authority claims を禁止し忘れる。
- raw transcript や secret-looking path を pack に含める。
- local-context と github-synced の provenance を混同する。

## Tests / validation impact

- deterministic prompt pack generation test
- metadata schema fixture test
- forbidden claims instruction fixture test
- local-context prompt fixture test
- secret/raw transcript exclusion test

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

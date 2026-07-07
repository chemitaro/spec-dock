---
種別: "Issue draft design"
ID: "epic-00295-08"
Issue候補: "C08"
タイトル: "Issue draft adoption と selected skeleton validation contracts を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C08 Issue draft adoption と selected skeleton validation contracts を実装する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `authoring validate issue-draft-adoption` を実装する。
- `authoring validate selected-skeleton-fill` を実装または runtime 化する。
- Issue node exists、parent trace、draft pack digest、draft-to-canonical target mapping を検査する。
- selected profile、template hash、section inventory、missing/extra section diagnostics を検査する。
- `.assurance.json` は observation-only とし、mutation を拒否する。
- fresh reviewer pass 前に execution-ready を主張しない。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/candidate_validation.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_draft_adoption.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_selected_skeleton_fill.py
- Issue-local artifacts/draft-requirement.md
- Issue-local artifacts/draft-design.md
- Issue-local artifacts/draft-plan.md

## Runtime / docs / skill impact

- Runtime: Issue draft adoption と skeleton fill validator を追加する。
- Docs: draft-adoption mode と execution-ready gate の違いを明記する。
- Skill: `spec-dock-issue-planning` draft-adoption mode の input gate になる。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- Issue node 作成前の draft を Issue adoption input として扱う。
- draft validation pass を fresh reviewer pass と誤認する。
- profile/template mismatch を warning のみで通す。
- `.assurance.json` を ChatGPT output から mutation する。

## Tests / validation impact

- issue draft adoption positive fixture
- selected skeleton fill positive fixture
- missing/extra section fixture
- profile/template hash mismatch fixture
- assurance mutation negative fixture
- execution-ready forbidden claim fixture

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

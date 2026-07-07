---
種別: "Issue draft design"
ID: "epic-00295-06"
Issue候補: "C06"
タイトル: "ZIP/tree review と staging を runtime command へ昇格する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C06 ZIP/tree review と staging を runtime command へ昇格する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `authoring pack review` と `authoring pack stage` を実装する。
- ZIP central directory を safe extraction 前に検査する。
- required metadata、root、source hashes、stale-if、forbidden authority claims を検査する。
- unsafe entry、secret-looking content、raw transcript、nested archive、binary、symlink 等を reject する。
- stage report、dry-run diff、EAL candidates、ownership marker を生成する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_stage.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py

## Runtime / docs / skill impact

- Runtime: ZIP/tree safety review and staging を installed command 化する。
- Docs: reject categories と stage/adoption boundary を明文化する。
- Skill: `spec-dock-chatgpt-authoring` の evidence review gate になる。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- unsafe ZIP を extraction 後に検査する。
- stage report を canonical adoption と誤読させる。
- forbidden authority claim を warning 扱いにする。
- tree fallback を ZIP review pass と同等に扱う。

## Tests / validation impact

- valid ZIP fixture test
- unsafe ZIP fixtures
- forbidden claim scanner tests
- tree fallback classification test
- stage output ownership marker test
- canonical unchanged test

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

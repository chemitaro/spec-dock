---
種別: "Issue draft design"
ID: "epic-00295-01"
Issue候補: "C01"
タイトル: "authoring pack assets を provider-side installed layout へ昇格する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C01 authoring pack assets を provider-side installed layout へ昇格する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `scripts/authoring-pack/` 相当の helper を provider asset 配下へ移設する。
- `spec_dock_runtime/application/authoring_pack/` と `domain/authoring_pack/` の初期 module boundary を作る。
- fixtures / manual test reference が provider-side assets を参照するように整理する。
- 旧 dogfood helper surface は standalone / compatibility surface として位置づけ、source of truth ではないことを文書化する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/authoring-pack/*
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/*
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/*
- tests / fixtures referencing provider asset paths

## Runtime / docs / skill impact

- Runtime: provider-side module placement の土台を作る。
- Docs: dogfood helper と installed runtime source-of-truth の差分を短く記録する。
- Skill: 直接変更なし。ただし後続 skill docs の前提になる。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- root dogfood helper を source of truth と誤認する。
- consumer installed path に入らない場所へ実装してしまう。
- 移設時に canonical workspace evidence を混入する。
- 既存 helper tests が provider asset path を見ない。

## Tests / validation impact

- provider-side file inventory check
- legacy helper compatibility smoke test
- asset path fixture resolution test

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

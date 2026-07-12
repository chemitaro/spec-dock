---
種別: 設計書（Issue）
ID: "iss-00307"
タイトル: "Final Quality Gate PR Delivery"
Issue Grade: "standard"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C12 final quality gate と mergeable PR delivery を実施する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- C01〜C11 の completion evidence を確認する。
- installed repo simulation と `spec-dock init/update` asset verification を行う。
- `authoring` commands の help、preflight、local-context fixture、pack prepare、backend dry-run、pack review/stage、validators、approval check を確認する。
- deferred command absence / fail-closed behavior を確認する。
- full test / lint / validation、manual scenario、docs consistency を実行する。
- reviewer / CI / PR review findings を修正し、Epic 単位の mergeable PR を作成する。

## Target provider-side paths

- all Epic 00295 changed provider-side assets
- all installed skill/docs paths touched by C01-C11
- spec-dock/initiatives/.../epic-00295.../report.md
- PR body / final quality gate evidence

## Runtime / docs / skill impact

- Runtime: end-to-end behavior の最終確認を行う。
- Docs: docs consistency と final open risk list を確定する。
- Skill: installed skill presence と workflow guidance を最終確認する。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- preceding Issue の evidence が未完了なのに PR delivery へ進む。
- manual test failure / reviewer finding / CI failure を未修正で readiness とする。
- deferred command が実装済みとして露出する。
- per-Issue PR が作られて relay policy と矛盾する。

## Tests / validation impact

- ./spec-dock/scripts/spec-dock validate
- git diff --check
- related unit / cli_runtime tests
- installed asset simulation
- manual dogfood scenarios
- reviewer / CI / PR review repair evidence

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

---
種別: "Issue draft design"
ID: "epic-00295-03"
Issue候補: "C03"
タイトル: "block-first GitHub sync preflight を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C03 block-first GitHub sync preflight を実装する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- local repo root、origin、current branch、local HEAD、worktree state を観測する。
- remote tracking branch と GitHub connector-visible branch / HEAD を比較する。
- dirty / staged / untracked / ahead / behind / diverged / missing branch / origin mismatch / source hash mismatch を block する。
- default branch fallback は explicit opt-in の場合だけ `requested_ref` と `effective_ref` を分けて記録する。
- `github-synced` と `local-context` evidence mode の provenance 差分を出力する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/preflight_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py

## Runtime / docs / skill impact

- Runtime: `authoring preflight github-sync` の core gate を追加する。
- Docs: block conditions、fallback、local-context authority を明文化する。
- Skill: ChatGPT evidence lane の最初の gate になる。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- branch mismatch を silent fallback する。
- untracked files を見落として source manifest が不完全になる。
- `local-context` を broad force として乱用できる。
- connector inaccessible を manual evidence と混同する。

## Tests / validation impact

- positive exact remote match fixture
- dirty/staged/untracked negative fixtures
- ahead/behind/diverged negative fixtures
- branch missing / origin mismatch / connector failure fixtures
- default fallback requested/effective ref fixture
- local-context provenance fixture

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

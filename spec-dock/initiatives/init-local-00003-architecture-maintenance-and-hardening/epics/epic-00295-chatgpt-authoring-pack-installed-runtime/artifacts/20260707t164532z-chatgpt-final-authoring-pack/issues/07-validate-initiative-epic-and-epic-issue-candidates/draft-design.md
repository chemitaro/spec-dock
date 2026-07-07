---
種別: "Issue draft design"
ID: "epic-00295-07"
Issue候補: "C07"
タイトル: "Initiative/Epic と Epic/Issue 候補 validators を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C07 Initiative/Epic と Epic/Issue 候補 validators を実装する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `authoring validate initiative-epic-candidates` を実装する。
- `authoring validate epic-issue-candidates` を実装する。
- parent trace、scope/non-scope、dependencies、duplicate/overlap diagnostics を検査する。
- per-candidate draft requirement/design/plan の存在と target mapping を検査する。
- profile recommendation は advisory-only とし、`authorized_profile` claim を拒否する。

## Target provider-side paths

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/candidate_validation.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_candidates.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_initiative_epic_candidates.py

## Runtime / docs / skill impact

- Runtime: candidate validators を追加する。
- Docs: candidate-only evidence と approval gate の関係を更新する。
- Skill: initiative/epic planning の stop gate を machine-readable evidence にする。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- candidate validation pass を node creation approval と誤読する。
- draft pack を canonical Issue docs として扱う。
- advisory profile recommendation が authorized_profile に昇格する。
- duplicate scope を検出できない。

## Tests / validation impact

- Initiative -> Epic positive fixture
- Epic -> Issue positive fixture
- duplicate/overlap negative fixture
- parent trace missing fixture
- profile authority negative fixture

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.

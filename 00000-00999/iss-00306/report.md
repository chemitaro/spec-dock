---
種別: 実装報告書（Issue）
ID: "iss-00306"
タイトル: "Runtime Workflow Guidance"
関連GitHub: ["#306"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00306 Runtime Workflow Guidance — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options Considered | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | C11でdocs/workflow guidance以外へ広がる可能性 | docs-only中心で進める; runtime behaviorも追加する | docs/workflow guidanceを主対象にし、runtime help wordingはbehaviorを変えないtext-only correctionが必要な場合だけ扱う | Epic plan C11はruntime docs/reference/workflow guidanceを対象にしており、新runtime behaviorは非スコープ | applied | `requirement.md`, `design.md`, `plan.md` | none |
| D-002 | resolved | operation | orchestrator | 中間IssueでPR deliveryを行うか | 中間IssueごとにPR; final Issueにdefer | C11ではPR deliveryせず、`iss-00307`でfinal quality gateとmergeable PR deliveryを行う | Epic plan relay policyとuser instructionがfinal Issueで一つのPR deliveryを要求している | applied | `requirement.md`, `plan.md` | `iss-00307` |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | ChatGPT ZIP draft artifacts | `requirement.md`, `design.md`, `plan.md` | C11の目的、scope、target docs、supported/deferred command分離、relay policyは採用した。古いbranch名、frontmatter状態候補、authority claimに見える表現は採用しない。 | `artifacts/20260707t171317z-draft-requirement-update-runtime-docs-and-workflow-guidance-draft-requirement.md`; `artifacts/20260707t171317z-01-draft-design-update-runtime-docs-and-workflow-guidance-draft-design.md`; `artifacts/20260707t171317z-02-draft-plan-update-runtime-docs-and-workflow-guidance-draft-plan.md` | fresh spec-reviewer gate |
| EAL-002 | partially_adopted | ChatGPT-Use / GPT-5.5 Pro Extended analysis | `requirement.md`, `design.md`, `plan.md` | draft-adoption decision、docs architecture、verification plan、reviewer focusを採用した。ChatGPTの検証未実施事項や推測はauthorityとして採用しない。 | `artifacts/20260708t073000z-chatgpt-runtime-workflow-guidance-planning-analysis.md` | fresh spec-reviewer gate |

## Objective Alignment Ledger

| Target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| OAL-001 | ChatGPT authoring pack installed runtimeのdocs/workflow guidanceを現行runtime/skill surfaceに合わせる | runtime help wording correctionは必要時のみ、PR deliveryは`iss-00307`へdefer | low | pass; spec-reviewer found only non-blocking P3 cleanup |

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Issue-local draft requirement、Epic requirement/design/plan、ChatGPT-Use analysisを確認した | none | partially adopted into canonical requirement by main orchestrator | pass | no | execute approved plan |
| design | Issue-local draft design、runtime command help、installed skill boundary、provider/mirror source-of-truthを確認した | none | partially adopted into canonical design by main orchestrator | pass | no | execute approved plan |
| plan | Issue-local draft plan、Epic relay policy、verification command surfaceを確認した | none | partially adopted into executable plan by main orchestrator | pass | no | execute approved plan |

## Delegated Draft Evidence

| role | scope_id | draft artifact path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT-Use / GPT-5.5 Pro Extended | iss-00306 | `artifacts/20260708t073000z-chatgpt-runtime-workflow-guidance-planning-analysis.md` | `artifacts/20260707t171317z-draft-requirement-update-runtime-docs-and-workflow-guidance-draft-requirement.md`; `artifacts/20260707t171317z-01-draft-design-update-runtime-docs-and-workflow-guidance-draft-design.md`; `artifacts/20260707t171317z-02-draft-plan-update-runtime-docs-and-workflow-guidance-draft-plan.md` | `requirement.md`; `design.md`; `plan.md` | partially_integrated | `requirement.md`; `design.md`; `plan.md` | pass: external read-only analysis created no delegated workspace-write output; adoption controlled by EAL-001 and EAL-002 | C11 planning claims were manually re-authored by the orchestrator into canonical docs | 古いbranch名、authority claimに見える表現、未検証主張 | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual evidence: ChatGPT-Use analysis in `artifacts/20260708t073000z-chatgpt-runtime-workflow-guidance-planning-analysis.md` plus manual-authored canonical docs `requirement.md`, `design.md`, and `plan.md` | pass | ready |

## Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | passed | no | execute approved plan | spec-reviewer 019f40bb resolved prior P1 blockers; non-blocking P3 closure reference cleanup applied |

## 実装サマリー

Planning phase completed. Implementation has not started.

## 実装記録

No implementation steps have run yet.

## 最終品質ゲート（Final Quality Gate）

| target | status | evidence | result |
|---|---|---|---|
| planning readiness | pass | `requirement.md`, `design.md`, `plan.md`, `report.md`, spec-reviewer 019f40bb | ready for issue execution |
| PR delivery | deferred | `plan.md` relay policy | deferred to `iss-00307` |

---
種別: 実装報告書（Issue）
ID: "iss-00209"
タイトル: "Improve dependency PlantUML view rendering"
関連GitHub: ["#209"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00209 Improve dependency PlantUML view rendering — Planning Report

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / clarification | Initial issue title was rendering-focused, but rendering and blocker readiness would diverge if fixed separately. | A: scope amendment; B: split issue; C: rendering-only | Adopt Option A: this issue covers readiness authority and PlantUML rendering together. | User explicitly selected Option A and confirmed blocker logic must change. | applied | `discussions/20260619t010926z-interview-dependency-disposition-scope-amendment.md`; `requirement.md`; `design.md`; `plan.md` | none |
| D-002 | resolved | interpretation | user / consultant / orchestrator | GitHub open/closed lifecycle differs from dependency readiness. | lifecycle-only; rendering-only visibility; lifecycle + disposition model | Separate `lifecycle_state` from `dependency_disposition`. | GitHub-open all-descendant-done high-level dependency is satisfied; empty GitHub-open high-level dependency remains blocking. | applied | `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md`; `discussions/20260619t002903z-interview-dependency-plantuml-closed-node-policy.md`; `requirement.md`; `design.md` | none |
| D-003 | resolved | compatibility | design reviewer | `.agent/deps-issues.json` must not lose satisfied-but-not-rendered context. | remove satisfied context; keep active graph only; separate active graph from context list | Keep schema v2 active graph `nodes` / `edges` separate from top-level `dependency_contexts`. | PUML can hide resolved noise while machine consumers still explain readiness. | applied | `design.md`; plan closure `cl-010`; `tc-s03-002` | none |
| D-004 | resolved | implementation | requirement/design/plan review | `deps-raw.puml` is raw direct view but should not become complete audit. | complete raw audit artifact; active raw direct view; readiness view | Keep `deps-raw.puml` as active raw direct visual/debug output; complete audit remains `.meta.json.depends_on` / `.agent/index-all.json`. | User accepted `raw_direct` for deps-raw; adding `deps-raw-all.puml` is out of scope. | applied | `requirement.md`; `design.md`; `plan.md` | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | requirement / design / plan | Source-grounded analysis identified rendering, JSON authority, and high-level lifecycle gaps. | `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md` | none |
| EAL-002 | adopted | interview | requirement / design / plan | User accepted Option A visibility semantics for high-level nodes and clarified empty open high-level nodes remain active. | `discussions/20260619t002903z-interview-dependency-plantuml-closed-node-policy.md` | none |
| EAL-003 | adopted | interview | requirement / design / plan | User selected Option A scope amendment: readiness authority and rendering are one coherent issue. | `discussions/20260619t010926z-interview-dependency-disposition-scope-amendment.md` | none |
| EAL-004 | adopted | system-architect draft | design.md | Delegated architecture draft was inspected and integrated into canonical design; canonical `design.md` then passed fresh spec review after fixes. | `discussions/20260619t013310z-draft-design-dependency-disposition-plantuml-rendering.md`; `design.md` | none |
| EAL-005 | adopted | implementation-planner draft | plan.md | Delegated plan draft was inspected and rewritten into canonical executable plan; reviewer findings were fixed until pass. | `discussions/20260619t014201z-draft-plan-dependency-disposition-rendering.md`; `plan.md` | none |
| EAL-006 | adopted | spec-reviewer | requirement.md | Requirement review found closure gaps; fixes added descendant traversal, active raw view wording, and issue-start verification. | requirement review findings; `requirement.md` | none |
| EAL-007 | adopted | spec-reviewer | design.md | Design review found satisfied context would be lost; fix added top-level `dependency_contexts` separate from active graph. | design review findings; `design.md` | none |
| EAL-008 | adopted | spec-reviewer | plan.md | Plan review found executable-plan gaps; fixes added EC-003/EC-002 closure, concrete test cards, delegation contracts, field contracts, no-op gate, final exit contract, and exit-code expectations. | plan review findings; `plan.md` | none |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| iss-00209 planning | `requirement.md` / `design.md` / `plan.md` now define one readiness authority consumed by `deps check`, active guards, JSON, and PlantUML. | PlantUML readability is still covered by active graph filtering, `blocks` labels, package high-level nodes, docs, and manual evidence. | low | requirement/design/plan reviewer gates passed after fixes |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Active issue docs, reference deps/sync docs, runtime domain/application/presentation code, tests, user feedback, consultant analysis. | Closed/all-done high-level visibility answered in `20260619t002903z`; scope amendment answered in `20260619t010926z`. | adopted into `requirement.md` | passed after fixes; final P2 wording reflected | no | promoted to design |
| design | Reviewed requirement, research/interviews, runtime layer boundaries, JSON/PUML contracts, delegated system-architect draft. | No remaining user interview needed. | adopted into `design.md` | passed after fixing `dependency_contexts` separation | no | promoted to plan |
| plan | Reviewed requirement/design, `phase_plan_issue.md`, `authoring/issue-plan.md`, delegated implementation-planner draft, repeated spec-reviewer findings. | No remaining user interview needed. | adopted into `plan.md` | passed after final exit-code precision re-review | no | ready for issue execution handoff |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | discussion draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00209 | `discussions/20260619t013310z-draft-design-dependency-disposition-plantuml-rendering.md` | requirement, discussions, runtime source, reference docs | `design.md`, `plan.md`, `report.md` | adopted | `design.md`, `report.md` | `git diff --check` passed after integration | canonical design rewritten by orchestrator | none material | none | design spec-reviewer passed after one fix | promoted to plan |
| implementation-planner | iss-00209 | `discussions/20260619t014201z-draft-plan-dependency-disposition-rendering.md` | requirement, design, workflow/authoring docs, runtime source, discussions | `plan.md`, `report.md` | adopted | `plan.md`, `report.md` | `git diff --check` passed after integration | canonical plan rewritten by orchestrator and reviewer findings applied | draft was compressed and tightened to current plan schema | none | plan spec-reviewer passed after fixes | ready for execution handoff |

## ワークフロー委任同意の証跡（Workflow Delegation Consent）

| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction with `spec-dock-issue-planning` | `/Users/iwasawayuuta/.codex/worktrees/7d89/spec-dock` | iss-00209 | current session | deep-consultant, system-architect, implementation-planner, spec-reviewer | same repo, active issue, read-only/review or scope-local discussion drafts; canonical docs owned by orchestrator | issue completion, scope change, user revocation, host policy conflict | none | proceed to issue execution when user requests |

## Planning Verification

| check | result | evidence |
|---|---|---|
| `git diff --check` after plan fixes | pass | no whitespace errors |
| requirement reviewer gate | pass | requirement reviewer passed after fixes |
| design reviewer gate | pass | design reviewer passed after `dependency_contexts` separation fix |
| plan reviewer gate | pass | final plan reviewer returned `review_status: pass` after P2 exit-code precision was reflected |

## Execution Handoff Readiness

- Requirement, design, and plan are concrete enough to start implementation under `spec-dock-issue-execution`.
- No additional user interview is currently required.
- Implementation must proceed step by step from S01 to S99, with per-step reviewer pass and commit/no-op closure.
- This report currently records planning evidence only. Runtime implementation evidence, test output, reviewer gates, commits, and final closeout evidence must be appended during issue execution.

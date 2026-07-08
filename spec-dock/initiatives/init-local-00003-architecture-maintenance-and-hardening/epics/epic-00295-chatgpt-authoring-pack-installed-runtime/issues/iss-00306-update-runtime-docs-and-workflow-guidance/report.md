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
| D-003 | resolved | delegation | orchestrator | `doc-writer` 実装委任が利用上限で失敗した | 再試行を待つ; 親orchestratorが例外的に直接実装する | Parent Implementation Exception として、承認済みplanの許可範囲内でprovider docs、dogfooding mirror docs、runtime help textのみ直接更新する | sub-agent status が usage limit error であり、C11の実装を進めるには同じplan範囲のdocs/help更新が必要。変更後にfresh `spec-reviewer` と、help text変更分の `code-reviewer` を通す | applied | subagent notification `019f40c2-e09e-7393-8c2d-a3093585c402`; changed files inventory below | none |

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

実装完了。ChatGPT authoring pack workflow、backend invocation reference、prompt pack / ZIP / staged evidence reference を provider docs に追加し、既存 workflow docs と index docs に薄い導線と authority boundary を追加した。dogfooding mirror docs へ同内容を反映した。

runtime behavior は変更していない。`authoring preflight` / `authoring validate` の help text だけ、旧 “Deferred skeleton” 表現を現行 command surface に合う説明へ修正した。

## 実装記録

| step | status | implementation | changed files | verification | notes |
|---|---|---|---|---|---|
| S02 | done | provider docs に ChatGPT authoring workflow、backend invocation reference、prompt pack / ZIP reference を追加し、既存 workflow/index docs に導線を追加した | `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`; `src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md`; `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`; `src/spec_dock/assets/spec_dock/docs/README.md`; `src/spec_dock/assets/spec_dock/docs/guide.md`; `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`; `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`; `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`; `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | docs inspection; forbidden authority grep | ChatGPT output / ZIP / validation pass は evidence-only と明記 |
| S03 | done | provider docs と同内容を dogfooding mirror へ反映した | `spec-dock/docs/workflow_chatgpt_authoring_pack.md`; `spec-dock/docs/reference_authoring_pack_backend.md`; `spec-dock/docs/authoring/chatgpt-pack.md`; `spec-dock/docs/README.md`; `spec-dock/docs/guide.md`; `spec-dock/docs/workflow_spec_authoring.md`; `spec-dock/docs/workflow_initiative.md`; `spec-dock/docs/workflow_epic.md`; `spec-dock/docs/workflow_issue.md` | `diff -u` on representative provider/mirror pairs: pass | mirror は source of truth ではなく dogfooding confirmation surface |
| S04 | done | runtime help text の旧 “Deferred skeleton” 表現を挙動変更なしで修正した | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`; `spec-dock/scripts/spec_dock_runtime/cli/parser.py` | all authoring help smoke: pass; `uv run pytest tests/cli_runtime/test_authoring.py`: pass | behavior changeなし、help wordingのみ |
| S05 | done | 実装後検証とfresh reviewer gateを完了した | `report.md` | `git diff --check`: pass; `./spec-dock/scripts/spec-dock validate`: pass; `./spec-dock/scripts/spec-dock assurance verify --format json`: pass; `uv run pytest tests/cli_runtime/test_authoring.py`: 314 passed, 1 skipped | `spec-reviewer` pass; help text変更分の `code-reviewer` pass |

## Parent Implementation Exception

| field | value |
|---|---|
| reason | `doc-writer` sub-agent `019f40c2-e09e-7393-8c2d-a3093585c402` が usage limit error で停止したため |
| user approval source | user requested continuing Epic execution; approved plan S02 allowed parent direct implementation only if recorded |
| allowed files | provider docs, dogfooding mirror docs, runtime help text files listed in `plan.md` |
| forbidden files | runtime behavior beyond help text, tests except verification, `.assurance.json`, canonical requirement/design/plan |
| rollback plan | revert this implementation commit before `issue finish` if reviewer fails and fix cannot be bounded |
| post-change verification | diff check, SpecDock validate, assurance verify, authoring help smoke, `tests/cli_runtime/test_authoring.py` |
| reviewer gate | fresh `spec-reviewer`; fresh `code-reviewer` because parser help text changed |

## 検証証跡

| command / inspection | result | evidence |
|---|---|---|
| `diff -u src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md spec-dock/docs/workflow_chatgpt_authoring_pack.md` | pass | no diff |
| `diff -u src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md spec-dock/docs/reference_authoring_pack_backend.md` | pass | no diff |
| `diff -u src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md spec-dock/docs/authoring/chatgpt-pack.md` | pass | no diff |
| `diff -u src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py spec-dock/scripts/spec_dock_runtime/cli/parser.py` | pass | no diff |
| `rg -n "Deferred authoring|Deferred GitHub|Deferred .*skeleton" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime` | pass | no matches |
| all `./spec-dock/scripts/spec-dock authoring ... --help` commands listed in `plan.md` S04 | pass | each command exited 0 |
| `rg -n "authoring adopt|create-issues-from-zip|mark-reviewer-pass|set-authorized-profile|issue-execution-ready|pr-ready" src/spec_dock/assets/spec_dock/docs spec-dock/docs` | pass with intentional negative context | matches only unsupported-command warning in `workflow_chatgpt_authoring_pack.md` |
| `rg -n "canonical adoption completed|\\.assurance\\.json mutation|authorized_profile decision|execution-ready|PR-ready|merge-ready" src/spec_dock/assets/spec_dock/docs spec-dock/docs` | pass with intentional negative/authority-boundary context | matches are “not this state” / “does not claim” contexts or existing readiness definitions |
| `git diff --check` | pass | no output |
| `./spec-dock/scripts/spec-dock validate` | pass | `spec-dock: ok (validate) nodes=202` |
| `./spec-dock/scripts/spec-dock assurance verify --format json` | pass | `ok: true`, `status: valid`, `issue_id: iss-00306` |
| `uv run pytest tests/cli_runtime/test_authoring.py` | pass | `314 passed, 1 skipped in 208.44s` |

## Closure Coverage

| closure_id | status | evidence | reviewer state |
|---|---|---|---|
| CLOS-001 | closed | Provider docs and dogfooding mirror docs now expose [workflow_chatgpt_authoring_pack.md](../../../../../../docs/workflow_chatgpt_authoring_pack.md), [reference_authoring_pack_backend.md](../../../../../../docs/reference_authoring_pack_backend.md), and [authoring/chatgpt-pack.md](../../../../../../docs/authoring/chatgpt-pack.md). Representative provider/mirror `diff -u` checks returned no diff. | spec-reviewer 019f40f2 pass |
| CLOS-002 | closed | Supported authoring commands are listed in `workflow_chatgpt_authoring_pack.md`; all help smoke commands exited 0. Deferred command names are mentioned only as unsupported examples. Old “Deferred skeleton” help wording has no grep matches. | code-reviewer 019f40ee-ad3f pass; spec-reviewer 019f40f2 pass |
| CLOS-003 | closed | `workflow_chatgpt_authoring_pack.md` defines `github-synced` as default repo-aware evidence and `local-context` as explicit lower-authority evidence. `reference_authoring_pack_backend.md` repeats the mode split for backend invocation. | spec-reviewer 019f40f2 pass |
| CLOS-004 | closed | `workflow_chatgpt_authoring_pack.md`, `reference_authoring_pack_backend.md`, and `authoring/chatgpt-pack.md` state that ZIP/tree/staged/candidate/validation outputs are evidence-only and cannot claim canonical adoption, reviewer pass, execution-ready, PR-ready, or merge-ready. Forbidden authority grep matches are negative/authority-boundary contexts. | spec-reviewer 019f40f2 pass |
| CLOS-005 | closed | Initiative/Epic docs and `workflow_chatgpt_authoring_pack.md` require human approval before Epic/Issue node creation. Issue docs and prompt-pack reference separate Issue draft adoption validation from canonical adoption and fresh review. | spec-reviewer 019f40f2 pass |
| CLOS-006 | closed | Relay policy is documented as a reviewed-Epic-plan exception: intermediate Issues defer PR only when the Epic plan names a final delivery Issue; otherwise normal PR Delivery / Merge Preparation Gate applies. This Issue defers PR delivery to `iss-00307`. | spec-reviewer 019f40f2 pass |
| CLOS-007 | closed | Verification commands passed: `git diff --check`; `spec-dock validate`; `assurance verify`; all authoring help smoke; `uv run pytest tests/cli_runtime/test_authoring.py`. code-reviewer passed. First implementation spec-review failed with P1 findings; fixes were applied and fresh re-review passed. | code-reviewer 019f40ee-ad3f pass; spec-reviewer 019f40f2 pass |

## Reviewer Follow-up Log

| reviewer | status | findings | disposition | evidence |
|---|---|---|---|---|
| code-reviewer 019f40ee-ad3f | pass | none | accepted | help text correction is behavior-preserving and mirrored |
| spec-reviewer 019f40ee-ac01 | fail | P1 relay PR delivery overgeneralized; P1 draft-adoption automation claim; P1 missing closure coverage | fixed; fresh re-review passed | `workflow_chatgpt_authoring_pack.md`; `guide.md`; this `Closure Coverage` section |
| spec-reviewer 019f40f2 | pass | none | accepted | prior P1 findings fixed; CLOS-001 through CLOS-007 coverage accepted |

## 最終品質ゲート（Final Quality Gate）

| target | status | evidence | result |
|---|---|---|---|
| planning readiness | pass | `requirement.md`, `design.md`, `plan.md`, `report.md`, spec-reviewer 019f40bb | ready for issue execution |
| implementation verification | pass | commands in 検証証跡 | ready for reviewer gates |
| spec-reviewer | pass | spec-reviewer 019f40f2 | docs/spec alignment, authority boundary, supported/deferred command separation, evidence mode semantics, relay policy accepted |
| code-reviewer | pass | code-reviewer 019f40ee-ad3f | parser help text correction accepted |
| PR delivery | deferred | `plan.md` relay policy and Epic final delivery Issue | deferred to `iss-00307` |

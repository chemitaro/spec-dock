---
種別: 実装報告書（Issue）
ID: "iss-00358"
タイトル: "Simplify Authoring Kit and Document Contracts"
関連GitHub: ["#358"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00358 Simplify Authoring Kit and Document Contracts — 計画承認・着手準備報告

## 現在の結論

- Product Ownerは2026-08-10に、親EpicのRequirement / Design / Planと、本IssueのDraft 1を承認した。
- Draft 1と承認済みinterview decisionsはevidence-onlyの入力として正本`requirement.md`、`design.md`、`plan.md`へ統合し、repository factsと独立review findingsで精度を補った。
- Requirement、Design、Planはすべてapprovedで、各phaseのfresh `spec-reviewer`がpassした。
- 実装、asset / test変更、PR、merge、`issue finish`はまだ実行していない。本報告の`ready`は「承認済みPlanのE00から着手できる」という意味であり、実装完了を意味しない。
- materialな製品判断の追加はない。Profile / Assuranceを使わず、one Plan + docs-only Planning Level、thin Report、Current六種というProduct Owner承認をそのまま保持する。

## 承認済み正本

| 文書 | 状態 | 主な固定内容 |
|---|---|---|
| `requirement.md` | approved | thin R/D/P/Report、文書責務、scope layering、Planning Level、Artifact / authority、Current / Historical、preservation / handoff |
| `design.md` | approved | exact asset tree / Add-Modify contract、template / Guide link、Report exact shape、Level examples、IC-1、ownership / rollback |
| `plan.md` | approved | E00〜S99の縦スライス、`CL-358-001`〜`CL-358-015`、step-local delegation、docs-only alternative evidence、具体テストカード、review gate |

## Spec Interpretation / Decision Ledger

- No material interpretation changes.
- No decision entries.
- Reviewで行った変更は、承認済みOption A、thin Report、Current六種を変えないpath、trace、ownership、test cardの精度向上である。新しいauthoring policyは追加していない。

## Objective Alignment Ledger

| target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| planning adoption | `requirement.md`のAuthoring Kit簡素化を`design.md`のthin asset contractと`plan.md`の利用者flowへ直接追跡した | preservation、parity、IC-1、359 / 360 handoffをprimary contractへ従属させた | none | pass |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-358-001 | adopted | `artifacts/20260809t125148z-draft-requirement-strict-vertical-slice-requirement.md` | `requirement.md` | Product OwnerがDraft 1とOption Aを承認し、interview decisionsと親Epic契約へ照合して正本化した | `requirement.md`とfresh requirement review pass | execute approved plan |
| EAL-358-002 | adopted | `artifacts/20260809t125149z-draft-design-strict-vertical-slice-design.md` | `design.md` | approved Requirementをexact asset path、thin contract、navigation、preservation、handoffへ割り当てた | `design.md`とfresh design review pass | execute approved plan |
| EAL-358-003 | adopted | `artifacts/20260809t125150z-draft-plan-strict-vertical-slice-plan.md` | `plan.md` | Draftのvertical sliceをStrict Plan契約へ統合し、closure、ownership、docs-only verification、test cardを具体化した | `plan.md`と最終fresh plan review pass | execute approved plan |
| EAL-358-004 | adopted | `artifacts/20260808t083300z-interview-issue-profile-and-draft-routing.md` | `requirement.md` | Profile / Assuranceを完全に外し、複雑なworkflow機構を導入しない判断を固定した | `requirement.md`のProduct Owner判断とscope | execute approved plan |
| EAL-358-005 | adopted | `artifacts/20260808t085519z-interview-planning-level-authoring-architecture-adoption.md` | `requirement.md` and `design.md` | Option Aのone Plan + Base Guide + four independent Completion Guidesを固定した | `requirement.md` RQ-358-004と`design.md` §7 | execute approved plan |
| EAL-358-006 | adopted | `artifacts/20260809t025001z-interview-target-report-contract.md` | `requirement.md` and `design.md` | Reportを三必須heading + optional Notes、empty-valid、non-gatingに固定した | `requirement.md` AC-358-006と`design.md` §5.4 | execute approved plan |

未解決のstale / blocked evidenceはない。Draft / interview artifactsは履歴証跡として保持し、正本authorityにはしない。

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親Epic R/D/P、承認済みDraft 1、三つのinterview decisions、現行template / docs / preservation surfaceを照合した | none | adopted | pass | no | execute approved plan |
| design | 承認済みRequirement、provider / dogfood asset tree、copy mechanism、Guide / template / Historical ownershipを照合した | none | adopted | pass | no | execute approved plan |
| plan | 承認済みR/D、Strict Plan Guide、全RQ / EC / AC、Design file-change contract、Issue 357とのIC-1境界を照合した | none | adopted | pass | no | execute approved plan |

## Delegated Draft Evidence

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT-use-strict | iss-00358 | `artifacts/20260809t125148z-draft-requirement-strict-vertical-slice-requirement.md` | 親Epic R/D/P、baseline SHA `2c75e0c02cb65a6e74040a72dc161d342d661091`、approved interview decisions | `requirement.md` | adopted | `requirement.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 requirement integrated with approved Option A and Report decisions | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00358 | `artifacts/20260809t125149z-draft-design-strict-vertical-slice-design.md` | `requirement.md`、parent Design / Plan、provider / dogfood asset inventory | `design.md` | adopted | `design.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 design integrated with exact paths and ownership | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00358 | `artifacts/20260809t125150z-draft-plan-strict-vertical-slice-plan.md` | `requirement.md`、`design.md`、Strict Plan Guide、specialist evidence | `plan.md` | adopted | `plan.md` | pass: canonical diff inspected and final plan review passed | Draft 1 plan integrated as executable step-local contract | none | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect and implementation-planner | used | system-architectのexact authoring tree / thin shape / empty-valid Report / parity / preservation / IC-1境界を`design.md`へ統合し、implementation-plannerのE00・S01〜S10・S90・S99 slicingを`plan.md`へ統合した | pass | ready |

## Reviewer Gate Status

| phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | evidence |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase gate | spec-reviewer | fresh | pass | no | execute approved plan | parent trace、Planning Level selection、Guide semantics、full preservation surfaceを確認 |
| design | design phase gate | spec-reviewer | fresh | pass | no | execute approved plan | exact paths、Report shape、Level examples、handoff timing、file-change contractを確認 |
| plan | final plan phase gate | spec-reviewer | fresh | pass | no | execute approved plan | findingsなし、overall confidence 0.98、全closure / step contract / test card / ownershipを確認 |

## Workflow-Scoped Authorization

| authorization source | repo / worktree | active scope | named roles | boundary | result |
|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と2026-08-10の文書承認 | current `spec-dock` checkout | iss-00358 planning | system-architect、implementation-planner、spec-reviewer | current repo / scope / session内のread-only planning / review。実装、外部公開、PR、mergeは含まない | pass |

## 実装開始契約

| 最初のstep | 担当 | 入力 | 完了条件 |
|---|---|---|---|
| E00 | `repo-analyst` | approved R/D/P、baseline SHA、Design §4.1 asset / link / preservation surface | 全rowにAction、owner、before hash、planned testがあり、暗黙Deleteがない |
| S01以降 | stepごとのfresh `doc-writer` / `dev-coder` | `plan.md` §9の該当contract | Redまたはdocs-only代替証拠、Green、report更新、fresh reviewer passをstep単位で満たす |

Issue 357とは同時に進められる。358はtemplate prose / Authoring Guideのsingle writerであり、Runtime / parser / scaffold mechanismを編集しない。両者の実生成契約はS09 / IC-1で照合する。

## 計画時の検証結果

- Canonical Requirement review: pass。
- Canonical Design review: pass。
- Canonical Plan final review: pass、findingsなし、confidence 0.98。
- Exact-current R/D/P/report readiness review: pass、findingsなし、confidence 0.98。E00/M0、S09〜S90/M4、S99/M99のreview / commit / clean check契約を確認した。
- `git diff --check`: pass。
- SpecDock `workflow status --format json`: `state=ready`、`reason_code=strict-legacy-missing-assurance`、`artifact_readiness=substantive`。
- SpecDock `deps check --no-github`: `ready=true`、blockerなし。cacheは`stale=true`の警告を返したため、実装開始時に必要ならGitHub同期を更新する。
- SpecDock `validate`: pass、`nodes=221`。
- `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`: 72 passed、44 skipped。
- `docs/rules/**`はPlanの許可変更から除外し、S04はIssue 357 evidenceなしでthin Report assetだけを完了できる。
- 正本とDraft / interview artifactsは別物として保持し、evidenceをauthorityへ自動昇格していない。

## 実装記録

実装は未着手である。E00以降のRed / Green / refactor、changed files、commands、step reviewer結果は、実際に観測した時点で本節と各Plan指定のreport destinationへ追記する。

### Step Contract Closure

| step | closure ids | planned close condition | observed evidence | result | notes |
|---|---|---|---|---|---|
| E00 | `CL-358-010/011/013` | Design §4.1全rowにAction、owner、before hash、planned testがあり、暗黙Deleteがない | 実装・調査実行はまだ開始していない | not started | approved Plan §9 E00から開始する |

### Test Contract Closure

| test id | step | evidence level | pre-implementation evidence | verification path | observed result |
|---|---|---|---|---|---|
| `tc-e00-001` | E00 | inspect-only | baseline asset / preservation manifestはE00で収集する | Plan §9 E00のtree / link / hash / copy-depth inspection | not started |

### Delegated Worker Evidence

| step | delegated role | worker summary | changed files | tests or docs-only verification | reviewer verdict | unresolved risks | integration decision |
|---|---|---|---|---|---|---|---|
| E00 | `repo-analyst` | delegationは実装開始時に行う | none | not run because execution has not started | not reviewed | E00でasset / owner ambiguityを確認する | start with approved E00 contract |

### Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E00 | planned delegation | asset / link / preservation baselineの横断read-only分析が必要 | `repo-analyst` | Design §4.1 asset / hash / link inventory | approved `requirement.md` / `design.md` / `plan.md` | read-only repository inspectionとmainによるreport統合 | asset / source / tests / user content / metadata / deps / active / Git mutation | `tc-e00-001` inspect evidence | action / owner不明、Design外path、baseline drift | manifest、hash、link evidence、risk、next action | not started |

### Closure Coverage

| closure range | owner steps | planning evidence | implementation evidence | state |
|---|---|---|---|---|
| `CL-358-001`〜`CL-358-015` | E00、S01〜S10、S90、S99 | `plan.md`のClosure Indexと最終fresh Plan review pass | 実装開始後にstep単位で記録する | not started |

### Closure Delta

| change | closure ids | reason | plan amendment required | re-review required | current result |
|---|---|---|---|---|---|
| none | `CL-358-001`〜`CL-358-015` | planning readiness時点ではapproved closureの追加・削除・意味変更なし | no | no | implementation not started |

### Docs Impact Resolution

| step | target | planned verification | current state |
|---|---|---|---|
| S90 | Design §4.1で358-ownedのREADME / Guide / authoring docs / templates | link / vocabulary / wording inspection、fresh spec review | not started |

### Milestone / Commit Candidate Gate

| milestone / step | reviewer verdict | commit candidate / scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|
| M0 / E00 | fresh `spec-reviewer` docs/spec alignment pass required before commit; not run because execution has not started | `docs(iss-00358): Authoring asset baselineを記録` / E00 report evidence | planned | not created because execution has not started | not run |
| M99 / S99 | not reviewed because execution has not started | `docs(iss-00358): 最終実装証跡を確定` / final report ledger | planned | not created because execution has not started | not run |

## 残余リスクと停止条件

- Existing node-local content、`.assurance.json`、Profile由来文書、Historical evidenceをrewrite / rename / deleteしない。
- Planning LevelをRuntime state / metadataへ追加せず、level別canonical Planを作らない。
- Issue 357のRuntime / parser / scaffold mechanismを358から修正しない。IC-1 mismatchはcontentとmechanismへ一意にroutingする。
- Skill本文、installer inventory、obsolete assetの物理pruneは359 / 360へ渡し、本Issueで先行しない。
- PR、merge、Issue close、Epic完了は別workflowであり、本報告では許可・実行しない。

## 次のアクション

`plan.md`のE00から実装を開始し、step gateを順に閉じる。Issue 357のE00とは並行可能である。

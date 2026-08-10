---
種別: 実装報告書（Issue）
ID: "iss-00357"
タイトル: "Reduce Runtime to Storage Core"
関連GitHub: ["#357"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00357 Reduce Runtime to Storage Core — 計画承認・着手準備報告

## 現在の結論

- Product Ownerは2026-08-10に、親EpicのRequirement / Design / Planと、本IssueのDraft 1を承認した。
- Draft 1はevidence-onlyの入力として正本`requirement.md`、`design.md`、`plan.md`へ統合し、repository factsと独立review findingsで精度を補った。
- Requirement、Design、Planはすべてapprovedで、各phaseのfresh `spec-reviewer`がpassした。
- 実装、テスト変更、PR、merge、`issue finish`はまだ実行していない。本報告の`ready`は「承認済みPlanのE00から着手できる」という意味であり、実装完了を意味しない。
- materialな製品判断の追加はない。正本のlocked expectationを変える必要が生じた場合は、該当stepを停止してR/D/P amendmentとfresh reviewへ戻る。

## 承認済み正本

| 文書 | 状態 | 主な固定内容 |
|---|---|---|
| `requirement.md` | approved | Storage Core CLI、selection-only active、start / finish順序、Current / Historical Artifact、generic import、Fresh scaffold、互換性、handoff |
| `design.md` | approved | 既存`ActiveManifestEntry` / schema v2、dependency-only readiness、partial result、module delta、migration / rollback、ownership |
| `plan.md` | approved | E00〜S99の縦スライス、`CL-357-001`〜`CL-357-015`、step-local delegation、Red / Green、具体テストカード、review gate |

## Spec Interpretation / Decision Ledger

- No material interpretation changes.
- No decision entries.
- Reviewで行った変更は、承認済みCLI / lifecycle / Artifact契約を変えないtrace、failure card、実在pathの精度向上である。locked expectationの追加・変更はない。

## Objective Alignment Ledger

| target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| planning adoption | `requirement.md`のStorage Core縮小と`design.md`のTarget boundaryを`plan.md`の縦スライスへ直接追跡した | compatibility、migration、handoff、step-local review / test evidenceを同じclosureへ従属させた | none | pass |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-357-001 | adopted | `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md` | `requirement.md` | Product OwnerがDraft 1の内容を承認し、親Epic契約と現行Runtime事実に照合して正本化した | `requirement.md`とfresh requirement review pass | execute approved plan |
| EAL-357-002 | adopted | `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md` | `design.md` | 承認済み要件を既存layer / model / portへ割り当て、fresh design reviewの精度指摘を反映した | `design.md`とfresh design review pass | execute approved plan |
| EAL-357-003 | adopted | `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md` | `plan.md` | Draftのvertical sliceをStrict Plan契約へ統合し、closure、failure、delegation、test cardを具体化した | `plan.md`と最終fresh plan review pass | execute approved plan |

未解決のstale / blocked evidenceはない。Draft artifactsは履歴証跡として保持し、正本authorityにはしない。

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親Epic R/D/P、承認済みDraft 1、CLI / active / lifecycle / Artifact / validateの現行契約を照合した | none | adopted | pass | no | execute approved plan |
| design | 承認済みRequirement、Runtime layered architecture、既存model / ports、module ownership、failure resultを照合した | none | adopted | pass | no | execute approved plan |
| plan | 承認済みR/D、Strict Plan Guide、全RQ / EC / AC、selector / failure / parity test、step-local delegationを照合した | none | adopted | pass | no | execute approved plan |

## Delegated Draft Evidence

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md` | 親Epic R/D/P、baseline SHA `2c75e0c02cb65a6e74040a72dc161d342d661091`、approved interview decisions | `requirement.md` | adopted | `requirement.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 requirement integrated and repository-grounded | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md` | `requirement.md`、親Epic Design / Plan、Runtime source layout | `design.md` | adopted | `design.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 design integrated with exact model and module boundaries | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md` | `requirement.md`、`design.md`、Strict Plan Guide、specialist evidence | `plan.md` | adopted | `plan.md` | pass: canonical diff inspected and final plan review passed | Draft 1 plan integrated as executable step-local contract | none | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect and implementation-planner | used | system-architectの既存active model / `check_deps` / finish result / copy mechanism / import safety境界を`design.md`へ統合し、implementation-plannerのE00・S01〜S10・S90・H91・S99 slicingを`plan.md`へ統合した | pass | ready |

## Reviewer Gate Status

| phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | evidence |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase gate | spec-reviewer | fresh | pass | no | execute approved plan | parent trace、retained CLI、truth table、Historical catalog、validate boundaryを確認 |
| design | design phase gate | spec-reviewer | fresh | pass | no | execute approved plan | model owner、partial result、module dependency deltaを確認 |
| plan | final plan phase gate | spec-reviewer | fresh | pass | no | execute approved plan | findingsなし、overall confidence 0.98、全closure / failure / delegation / test cardを確認 |

## Workflow-Scoped Authorization

| authorization source | repo / worktree | active scope | named roles | boundary | result |
|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と2026-08-10の文書承認 | current `spec-dock` checkout | iss-00357 planning | system-architect、implementation-planner、spec-reviewer | current repo / scope / session内のread-only planning / review。実装、外部公開、PR、mergeは含まない | pass |

## 実装開始契約

| 最初のstep | 担当 | 入力 | 完了条件 |
|---|---|---|---|
| E00 | `repo-analyst` | approved R/D/P、baseline SHA、Runtime / tests / docs | retained / removed / shared inventoryにpath、symbol、consumer、Action、ownerが揃い、曖昧rowがない |
| S01以降 | stepごとのfresh worker | `plan.md` §8の該当contract | Redまたは代替証拠、Green、report更新、fresh reviewer passをstep単位で満たす |

Issue 358とは同時に進められる。ただしparser / registry / Runtimeは357、template prose / Authoring Guideは358のsingle writerとし、共有contractはIC-1で照合する。

## 計画時の検証結果

- Canonical Requirement review: pass。
- Canonical Design review: pass。
- Canonical Plan final review: pass、findingsなし、confidence 0.98。
- Exact-current R/D/P/report readiness review: pass、findingsなし、confidence 0.99。E00/M0のfresh `spec-reviewer` → commit → clean check契約を確認した。
- `git diff --check`: pass。
- SpecDock `workflow status --format json`: `state=ready`、`reason_code=strict-legacy-missing-assurance`、`artifact_readiness=substantive`。
- SpecDock `deps check --no-github`: `ready=true`、blockerなし。cacheは`stale=true`の警告を返したため、実装開始時に必要ならGitHub同期を更新する。
- SpecDock `validate`: pass、`nodes=221`。
- `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`: 72 passed、44 skipped。
- 正本とDraft artifactは別物として保持し、Draftをauthorityへ昇格していない。

## 実装記録

実装は未着手である。E00以降のRed / Green / refactor、changed files、commands、step reviewer結果は、実際に観測した時点で本節と各Plan指定のreport destinationへ追記する。

### Step Contract Closure

| step | closure ids | planned close condition | observed evidence | result | notes |
|---|---|---|---|---|---|
| E00 | `CL-357-001/012/013` | retained / removed / shared inventoryの全rowにpath、symbol、consumer、Action、ownerがある | 実装・調査実行はまだ開始していない | not started | approved Plan §8 E00から開始する |

### Test Contract Closure

| test id | step | evidence level | pre-implementation evidence | verification path | observed result |
|---|---|---|---|---|---|
| `tc-e00-001` | E00 | inspect-only | baseline inventoryはE00で収集する | Plan §8 E00のregistry / import / consumer inspection | not started |

### Delegated Worker Evidence

| step | delegated role | worker summary | changed files | tests or docs-only verification | reviewer verdict | unresolved risks | integration decision |
|---|---|---|---|---|---|---|---|
| E00 | `repo-analyst` | delegationは実装開始時に行う | none | not run because execution has not started | not reviewed | E00でinventory ambiguityを確認する | start with approved E00 contract |

### Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E00 | planned delegation | Runtime inventoryの横断read-only分析が必要 | `repo-analyst` | retained / removed / shared inventory | approved `requirement.md` / `design.md` / `plan.md` | read-only repository inspectionとmainによるreport統合 | source / tests / docs / metadata / deps / active / Git mutation | `tc-e00-001` inspect evidence | owner不明、公開surface変更、retained consumerを持つDelete候補 | inventory、path / symbol evidence、risk、next action | not started |

### Closure Coverage

| closure range | owner steps | planning evidence | implementation evidence | state |
|---|---|---|---|---|
| `CL-357-001`〜`CL-357-015` | E00、S01〜S10、S90、H91、S99 | `plan.md`のClosure Indexと最終fresh Plan review pass | 実装開始後にstep単位で記録する | not started |

### Closure Delta

| change | closure ids | reason | plan amendment required | re-review required | current result |
|---|---|---|---|---|---|
| none | `CL-357-001`〜`CL-357-015` | planning readiness時点ではapproved closureの追加・削除・意味変更なし | no | no | implementation not started |

### Docs Impact Resolution

| step | target | planned verification | current state |
|---|---|---|---|
| S90 | 357-owned Runtime reference / migration docs | help照合、relative-link scan、fresh spec review | not started |

### Milestone / Commit Candidate Gate

| milestone / step | reviewer verdict | commit candidate / scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|
| M0 / E00 | fresh `spec-reviewer` docs/spec alignment pass required before commit; not run because execution has not started | `docs(iss-00357): Runtime baseline inventoryを記録` / E00 report evidence | planned | not created because execution has not started | not run |
| M99 / S99 | not reviewed because execution has not started | `docs(iss-00357): 最終実装証跡を確定` / final report ledger | planned | not created because execution has not started | not run |

## 残余リスクと停止条件

- Runtime削除対象にretained consumerが見つかった場合はE00で停止する。
- schema v2互換、GitHub partial failure、Artifact path safety、Existing Historical preservationのlocked expectationを変えない。
- Issue 358のtemplate / Guide内容を357から修正しない。IC-1 mismatchはcontentとmechanismへ一意にroutingする。
- PR、merge、Issue close、Epic完了は別workflowであり、本報告では許可・実行しない。

## 次のアクション

`plan.md`のE00から実装を開始し、step gateを順に閉じる。Issue 358のE00とは並行可能である。

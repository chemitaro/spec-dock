---

kind: "tdd-ready-implementation-handoff-candidate"
issue: "iss-00395"
title: "Issue #395 LunaMax TDD Implementation Handoff"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_tip_sha: "25b33cfaf6214d8c78494f0e0520ef8738bc862f"
verified_tip_tree: "ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-dispatch-and-return-contract"
---

# Issue #395 LunaMax TDD Implementation Handoff

## 1. Current instruction

**Do not mutate Product source、tests、ledger、dogfood、policy、workflow at the current state.**

現在の状態は次のとおりです。

| Field                    | Value                                                                     |
| ------------------------ | ------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                     |
| Issue branch             | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Verified document tip    | `25b33cfaf6214d8c78494f0e0520ef8738bc862f`                                |
| Verified tree            | `ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8`                                |
| P392 entry               | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |
| Implementation allowed   | `false`                                                                   |
| Owner decisions required | `[]`                                                                      |
| Merge authority          | Human only                                                                |

Read-only preflightは実行できます。File mutationへ進むには、canonical replacement packの採用、clean pushed exact specification tip、independent specification review、explicit implementation dispatchが別途必要です。

## 2. Document responsibilities

* Requirement: value、behavior、acceptance
* Design: boundaries、responsibilities、invariants、state transitions、testable contracts
* Plan: TDD execution order、RED、minimal-change intent、GREEN、evidence、stop
* Handoff: dispatch input、authority、scope、return contract

LunaMaxは本handoffをPlanの代替実装手順として扱いません。Plan内のstepを順に実行し、本handoffは開始条件と返却条件を固定します。

## 3. Required execution packet

Mutation dispatchには、次のactual valuesが必要です。

| Field                                  | Requirement                                                                             |
| -------------------------------------- | --------------------------------------------------------------------------------------- |
| `packet_schema`                        | Supported version                                                                       |
| `issue`                                | `iss-00395`                                                                             |
| `repository`                           | `chemitaro/spec-dock`                                                                   |
| `branch`                               | `iss-00395-regression-baseline-terminalization-and-product-defect-repair`               |
| `integration_branch`                   | `codex/epic-00384-provider-test-strategy-planning`                                      |
| `p392_sha` / `p392_tree`               | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3` / `190bc566a18cd84813c4b7c043f8724e275cb55d` |
| `spec_freeze_sha` / `spec_freeze_tree` | Clean pushed canonical specification identity                                           |
| `spec_review.target_sha/tree`          | Spec freezeとexact一致                                                                     |
| `spec_review.status`                   | `pass`                                                                                  |
| `spec_review.p0` / `p1`                | 0 / 0                                                                                   |
| `spec_review.receipt_identity`         | Non-empty immutable identity                                                            |
| `spec_review.receipt_sha256`           | Receipt bytesのSHA-256                                                                   |
| `implementation_authorized`            | `true`                                                                                  |
| `concurrent_writer.absent`             | `true`                                                                                  |
| `concurrent_writer.assertion_id`       | Non-empty identity                                                                      |
| `concurrent_writer.scope_paths`        | Exact implementation paths、generated projection roots、Issue branch refを包含               |
| `concurrent_writer.expires_at`         | Mutation時点で有効                                                                           |
| `commit_push_authorized`               | Separate boolean                                                                        |
| `pr_prepare_authorized`                | Separate boolean                                                                        |
| `human_merge_only`                     | `true`                                                                                  |

Missing、inconsistent、expired、unverifiable fieldがあれば変更0で停止します。

## 4. Mutation scope

### 4.1 Hand-edit allowed after authorization

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
* `tests/cli_runtime/test_delete.py`
* `tests/cli_runtime/test_import.py`
* `tests/cli_runtime/test_runtime_import_s10.py`
* `tests/cli_runtime/test_sync.py`
* `tests/cli_runtime/test_workbench.py`
* `full-regression-ledger.json`。ただしledgerはPlan Step 10まで編集禁止です。

### 4.2 Generated only

* `spec-dock/scripts/spec_dock_runtime/infra/git_cli.py`
* `spec-dock/spec-dock.version`
* `.agents/skills/spec-dock/.spec-dock-provider-slot.json`
* `.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json`

Generated pathsを手編集しません。

### 4.3 No-touch

Timing、policy、sharder、verifier、workflows、Provider Lifecycle Wire、Issue #392 lifecycle implementation、Issue #396 scope、row 12 source/test、parent contracts、managed metadata、active pointer、dependency storageを変更しません。

## 5. TDD dispatch sequence

LunaMaxはPlanの次のunit順を守ります。

1. Read-only identity・baseline・authorization gate
2. Row-specific first RED inventory
3. Rows 4–11 test-double seam
4. Rows 1・13・14・15 observer migration
5. Row 3 test-first security observation
6. Row 3 Product boundary repair
7. Row 12 no-edit guard
8. 14 historical nodes + row 2 successor normal pass
9. Provider-first dogfood projection
10. Ledger final transition
11. Working-tree complete verification
12. Separate permission時だけexact clean candidate、strict reviews、optional PR preparation
13. Human merge前で停止し、post-merge B1/B2 contractを引き渡す

Method bodyやlarge shell/Python snippetを本handoffから転記しません。Current source、protocol、testsを読み、Design contract内で最小変更を導きます。

## 6. Non-negotiable row handling

| Rows  | Required handling                                                                     |
| ----- | ------------------------------------------------------------------------------------- |
| 1     | Retired active observer argumentだけを直し、delete non-reobservationを保持                     |
| 2     | Read-only resolved/superseded、successor unchanged                                     |
| 3     | Same existing nodeでcredential non-exposureを観測し、identity/publication responsibilityを分離 |
| 4–11  | `_StubTemplateScaffolder`をcurrent descriptor-bound portへ追随。本番を旧APIへ戻さない               |
| 12    | Product/test edit 0。Evaluator coverage REDとnode GREENを別に扱う                            |
| 13–14 | Retired active observer argumentsだけを直し、sync outputsを保持                                |
| 15    | Retired argumentを除去し、active successをstate readより先に確認し、Workbench opacityを保持            |

Nodeid、signature、row orderを変更しません。

## 7. Required GREEN evidence

LunaMaxは少なくとも次を返します。

### 7.1 Identity

* Repository、Issue branch、P392 SHA/tree
* Specification SHA/tree
* Working-tree HEADとdiff SHA-256
* Commit/push許可時のimplementation SHA/tree

### 7.2 TDD evidence

* 13 repair rowsのindividual first RED
* Row 12 evaluator REDとnode normal pass
* 13 repaired rowsのindividual GREEN
* Row 2 successor GREEN
* Pre-ledgerとpost-ledgerの15-node normal pass
* Changed path/symbolとprotected assertions

### 7.3 Security and boundary evidence

* Row 3 four-case publication matrix
* Credential exposure 0
* Same-repo、numeric-scope、foreign rejection preservation
* Row 12 exact no-edit boundary

### 7.4 Dogfood and lifecycle evidence

* Provider/dogfood runtime byte equality
* Old/new digest inequality
* Update result、ready record、two markersのdigest equality
* Version/state/operation/seed-policy preservation
* Two `SKILL.md` bytesとprotected-data equality
* Dogfood/package parity normal pass

### 7.5 Ledger evidence

* Entry ledger hash
* Final ledger hash
* Exact two-field delta for rows 1、3–15
* Row 2 exact preservation
* Top-level historical metadata preservation
* 15/0/15、14 fixed-in-place、1 superseded

### 7.6 Gate evidence

* Evaluator unit
* Current full verifier
* Ordinary lane
* Provider lifecycle unit
* Distribution cutover
* Platform/coordination
* Packaged distribution
* Complete dogfood suite
* Lint
* SpecDock validate
* Timing 243、required-fast 4
* Policy/workflow/wire no-touch
* Exact 11-path final diff

### 7.7 Review evidence

Commit/push許可時は、exact clean SHA/treeへCode Review StrictとFinal Quality Gate Strictのreceiptを束縛します。

## 8. Stop-and-return

停止時は、次を簡潔に返します。

* stopped stage
* exact expected and actual identity
* violated contract ID
* applicable row/nodeid
* operations actually attempted and observed results
* changed paths。Mutation前ならempty
* sanitized failure summaryとevidence hash
* owner decisionが必要か
* causeを分離する次のread-only check

原因が確定していない場合は`原因未特定`と明記します。実行していない操作は`未実行`と明記します。Permission failure、filesystem failure、credential issueを推測で作りません。

次のいずれかで即時停止します。

* Identity、review、authorization、writer scope不一致
* Baseline、row、signature、timing、required-fast drift
* Expected first REDと異なる
* Heavy test skip/xfail/error
* Credential exposureまたはpublication weakening
* Row 12 drift
* Dogfood/lifecycle/protected-data drift
* Ledgerの許容差分超過
* Policy、workflow、wire、#396 scope変更が必要
* Unexpected failureまたはnew owner decision

## 9. Terminal points

### 9.1 Read-only return

Implementation authorizationがない場合、preflight結果だけを返します。Product/test/ledger/dogfood変更は0です。

### 9.2 Working-tree provisional return

Implementation authorizationはあるがcommit/push permissionがない場合、working-tree candidateとprovisional evidenceを返します。

* Candidate state: `working-tree-provisional`
* Implementation SHA/tree: null
* Merge ready: false

### 9.3 Clean pushed exact return

Commit/push permissionがあり、exact clean rerunとindependent reviewsがpassした場合、reviewed candidateを返します。

* Candidate state: `clean-pushed-exact`
* Implementation SHA/tree: non-null
* Merge ready: true
* Human merge: not performed

`merge_ready=true`はmerge authorizationではありません。

### 9.4 PR preparation

`pr_prepare_authorized=true`の場合だけ、headをIssue branch、baseをEpic integration branchとしてPRを作成または更新します。Final reviewed SHA/treeとPR headが一致しなければ操作しません。

## 10. Human and post-merge boundary

LunaMaxは次を実行しません。

* PR merge
* Integration branch direct push
* Main merge
* Revert
* Required-contextまたはbranch-protection変更
* #392/#395 closure
* #396 start
* Policy retirement
* Automatic rollback

Human merge後、Human/Codexがsame exact integration SHA/treeでB1を先に、B2を続けて確認します。PR head treeとmerged treeが異なる場合、PR-head CIをB1 evidenceとして再利用しません。

B1はcurrent gates、provider parity、unexpected 0を要求します。B2は15/0/15、14 fixed-in-place、1 superseded、approved 0、unexpected 0、timing 243、historical preservationを要求します。

## 11. Current completion state

* Specification candidate materialized: true
* Canonical adoption: false
* Independent spec review: false
* Implementation authorized: false
* Product/test/ledger mutation: not performed
* Commit/push/PR/merge: not performed
* Human merge only: true

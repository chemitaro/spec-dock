---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-02"
親: ["init-local-00003"]
実装開始許可: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

本Epicの正本は、本書、[Design](design.md)、[Plan](plan.md)、accepted ADR、[Epic Integration Branch Contract](artifacts/epic-integration-branch-contract.md)、[Rolling-Wave Issue Elaboration Contract](artifacts/rolling-wave-issue-elaboration-contract.md)、[Provider Lifecycle Wire Contract](artifacts/provider-lifecycle-wire-contract.md)、[Post-#387 Regression Baseline Register](artifacts/active-failure-disposition-register.md)である。

## 1. Outcome

Epic #384は、一つの長大なimplementation Issueを三つの依存順vertical sliceへ置換する。各Issueは実装と自身の検証を一体で完了し、人間だけがIssue PRをEpic integration branchへmergeする。各merge後のintegration branchはGREENかつ内部整合でなければならない。三Issue完了後にだけ、同branchをmainへ一度だけ人間がmergeする。

実在するdelivery chainは次で固定する。

| Order | SpecDock ID | GitHub | Outcome |
|---:|---|---:|---|
| predecessor | `iss-00387` | #387 | CLOSED、mainへmerge済み。Current surface residue cleanup。 |
| 1 | `iss-00392` | #392 | Fixed Ownership Provider Lifecycle Hard Cutover。既存nodeをscope縮小して再利用。 |
| 2 | `iss-00395` | #395 | Regression Baseline Terminalization and Product Defect Repair。`iss-00392`へ依存。 |
| 3 | `iss-00396` | #396 | Build Once Provider Gate and Regression Policy Cutover。`iss-00395`へ依存。 |

CLOSEDの`iss-00388`〜`iss-00390`はhistorical superseded nodeのまま保持し、再利用・reopen・dependency先への変更を行わない。

## 2. Verified current baseline

Authoring authorityはrepository `chemitaro/spec-dock`、branch `codex/epic-00384-provider-test-strategy-planning`、full SHA `240e561e94b50250a4a6309452a7fd0fb511458a`、tree `181f7eb28da0edff3ca1352edf4cb2ae1f21d433`である。

- `iss-00387` / GitHub #387はCLOSED/completedである。
- PR #394はbase `main`、head `4f018da3790d7aeeb16410a386e6e586fb2e803d`、merge commit `db13d047e0a9fb2df31b1a5fc44da0673d8fb9cd`で、人間によりmainへmerge済みである。
- Current branchはそのmergeを含むpost-#387 integration baselineである。
- `iss-00395`と`iss-00396`は実在し、metadata dependencyはそれぞれ`iss-00392`、`iss-00395`である。
- Packageとchecked-in dogfoodはtransitional `0.2.3`である。
- Root `full-regression-ledger.json`の`failure_paths`は15行で、14 `active`、1 `resolved/superseded`である。
- Root `full-regression-timing-weights.json`は243 node weightsを持つ。
- Ledger top-levelの27件集計、古いhead SHA、conclusionはIssue #368時点のhistorical metadataであり、current row-count authorityではない。
- Current Provider CI、policy skip、ledger evaluator、4-shard Full Regression、main-push workflowはまだtransitional stateとして存在する。
- Issue #392は未startである。本packのimport、review、commitはIssue startではない。

## 3. Requirements

### E384-RQ-001 — Epic integration branch authority

`codex/epic-00384-provider-test-strategy-planning`をEpic integration branchとして使用する。各implementation Issue branchは、そのIssue start時点の同branch tipから分岐し、PR baseを同branchへ固定する。Issue PRをmainへ向けない。Direct push、partial cherry-pick、parallel writer、agent mergeを許可しない。

### E384-RQ-002 — Ordered human merge and GREEN state

Issue PRは`iss-00392`、`iss-00395`、`iss-00396`の順で、人間だけが一件ずつmergeする。各merge後にbranch-tip identityを固定し、required verificationを再実行し、GREENと内部整合を確認するまで次Issueをstartしない。

### E384-RQ-003 — Rolling-wave elaboration

現在の各Issue R/D/Pはdraft contractであり、実装file、symbol、test code、exact command、step-by-step手順を固定しない。各Issue start直前にcurrent Epic branch tipへ再基準化し、stable contractを変更せずimplementation-ready R/D/PとLuna Max handoffを生成し、独立Strict reviewでacceptされてからだけstartできる。

### E384-RQ-004 — Fixed provider ownership and closed wire

Durable provider mutation authorityは、四つのfixed roots、二つのfixed skill slots、`spec-dock/spec-dock.version`に限定する。Fresh-only seed creationとshared-container bootstrapは別にboundedとする。Public lifecycle record/result/action/text/JSON/exitはwire artifactのclosed inventoryだけを使用する。

### E384-RQ-005 — Legacy migration, seed policy and tooling-only uninstall

Exact clean `0.2.3`だけを`0.2.4`へone-shot migrateする。Strict seven-key recordはimmutable `seed_policy`を保持し、resume identityをoperation/candidate/policyへ固定する。Uninstallはtooling-only、default dry-run、durable `tooling-absent-preserved-data`を保持する。`--remove-specs`はmutation-zero exit 2である。

### E384-RQ-006 — Filesystem safety, recovery and protected data

Candidate validation、descriptor binding、no-follow、hard-link/special-type rejection、same-filesystem persistent stage、native no-replace/exchange、terminal cleanup continuationを維持する。Initiatives、Artifacts、repository workbench、consumer seeds、unknown path、unrelated skills、user dataをpreserveする。Lifecycle operationとevidence workspaceのcleanup authorityを混同しない。

### E384-RQ-007 — Post-#387 regression baseline authority

[Post-#387 Regression Baseline Register](artifacts/active-failure-disposition-register.md)がcurrent regression debtの唯一のauthorityである。Current authorityはexact 15 rows、14 active、1 resolvedである。古い27-row conditional register、Issue #387 future-admission model、stale top-level countをcurrent authorityとして使用しない。

### E384-RQ-008 — Issue #392 lifecycle outcome

Issue #392はfixed ownership lifecycle、closed wire、exact migration、tooling-only uninstall、safe recovery、public compatibility、complete dogfood migration、old lifecycle writer removalを一つのobservable Product outcomeとして実装する。Regression terminalizationとfinal provider-gate redesignを所有しない。

### E384-RQ-009 — Issue #392 baseline and gate preservation

Issue #392は14 active rowのnode identity、signature、lifecycleを追加・削除・変更しない。Current test-policy machineryを維持し、Issue merge後もknown baseline以外のunexpected failure 0、current PR gateとexact full-regression pathがGREENでなければならない。既にresolvedのrowは、old lifecycle test removalに必要なpre-decided behavior-preserving successor rebindingだけを許可する。

### E384-RQ-010 — Issue #395 terminalization

Issue #395はregisterの14 active rowsを、それぞれProduct実装修正によりnormal passへterminalizeする。Parentで別successorが明示されていないactive rowはfixed-in-placeとする。新しいapproved failure、skip、xfail、silent retirement、row追加、scope外cleanupを認めない。

### E384-RQ-011 — Issue #395 current-gate continuity

Issue #395完了時は、15 rowsすべてresolved、active 0、approved failure 0、unexpected failure 0である。Current ledger、timing、sharder、policy hook、current PR workflow、main-push Full Regressionは整合したままGREENであり、Issue #396のtoolingへ依存しない。

### E384-RQ-012 — Issue #396 build-once provider gate

Issue #396はclean zero-approved-failure baselineだけを入力とし、one Linux packaging producer、same-candidate downstream roles、Linux canonical、sdist smoke、macOS delta、stable qualification、actual-byte evidenceを持つfinal provider gateを実装する。

### E384-RQ-013 — Consumer-first regression-policy removal

Issue #396だけがold regression policyを削除できる。Replacement consumers/providersを先に成立させ、old consumer 0を証明してから、ledger、243-node timing、sharder、policy skip machinery、old policy hook、quality providers、main-push Full Regressionを同一Issue内で削除する。

### E384-RQ-014 — Compatibility, required context and external evidence

Final gate cutoverはold/new contextsのno-gap coexistence、new required contextのintentional RED block、GREEN recovery、old required context removal、final readbackを人間操作で行う。Workflow/API/artifact/evidenceはactual source/treeとactual bytesへ束縛し、tracked reportへfuture identityまたはpost-merge factを書かない。

### E384-RQ-015 — Dogfood and documentation convergence

Provider sourceを先に変更し、candidate-changing Issueは四roots、二slots、record、markersをcomplete candidateとしてdogfoodへ反映する。Partial projectionをmergeしない。Issue #392がlifecycle guidance、Issue #396がfinal test-policy/provider-gate guidanceを所有する。

### E384-RQ-016 — Rollback and recovery

Rollback unitはIssue PR merge全体である。Dependent Issue start前は直前mergeをhuman revertできる。Dependent work開始後はsuffixを逆順revertするか、owned boundary内でforward-fixする。Stable contract writerの一部だけを戻すpartial rollback、automatic rollback、old writer fallbackを禁止する。

### E384-RQ-017 — Evidence, Issue closure and final main merge

各Issue acceptanceは、Issue PRのhuman merge、integration branch GREEN、acceptance evidence readback後に成立する。三Issue完了後だけEpic PRをmainへ一度human mergeし、final branch treeとmerge treeのequality、final main verification、Issue/Epic closure evidenceを取得する。

### E384-RQ-018 — Historical non-authority and no extra Issue

旧single-Issue HTML、historical research/discussions、single-Issue guide、CLOSED #388〜#390は削除せずhistorical evidenceとして保持するが、current implementation authorityではない。調査、意思決定、文書、test、verification-only Issueを追加しない。`owner_decisions_required=[]`。

## 4. Parent acceptance coverage

| Requirement | Primary owner | Shared consumers |
|---|---|---|
| E384-RQ-001–003 | Parent Epic | #392, #395, #396 |
| E384-RQ-004–006 | #392 | #395 and #396 read-only |
| E384-RQ-007 | Parent register | all three Issues |
| E384-RQ-008–009 | #392 | Parent gate |
| E384-RQ-010–011 | #395 | #392 output, #396 input |
| E384-RQ-012–014 | #396 | Parent human gate |
| E384-RQ-015 | #392 lifecycle / #396 final policy | #395 protection |
| E384-RQ-016–018 | Parent Epic | all three Issues |

## 5. Final acceptance

Epic acceptance requires all three Issue merges on the integration branch, GREEN evidence after each merge, complete final provider gate, old regression-policy machinery absent, stable contracts unchanged, human review complete, and one final human merge to main. Main must never observe Issue-level intermediate states.

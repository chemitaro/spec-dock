---
種別: 要件定義書（Issue）
ID: "iss-00382"
タイトル: "Full Regression Baseline Lifecycle And Successor Evidence"
関連GitHub: ["#382"]
状態: "planned"
最終更新: "2026-08-30"
親: ["epic-00365", "init-local-00003"]
---

# iss-00382 Full Regression Baseline Lifecycle And Successor Evidence — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

Full Regression baselineのhistorical failureを削除せず、current candidateでactive failure、resolved successor、retired surfaceを正しく区別できるrepository-level quality contractを実現する。standalone verifierとpytest guardが同じpolicyを評価し、既知failureの正当な解消をcoverage lossと区別する。

本Issueの完了により、Issue `iss-00372` はdistribution production semanticsを変更せず、accepted Full Regression policyでfinal candidate evidenceを取得できる。

## 背景

Issue `iss-00368` のledger schema 1とverifierは、全rowがcurrent candidateでも同じnode ID・signatureで失敗し続けることを成功条件とする。Issue `iss-00372` では、Issue 359固定digestをauthorityとする旧testがcurrent provider/dogfood parityをauthorityとするsuccessor testへ置換された。Report上、unexpected failure、unexpected error、signature mismatchは0だが、旧failureが観測されないため`ledger-mismatch`となった。

old row削除、failure test復活、failure count更新、Issue 372固有exceptionのいずれも、historical evidenceまたはcurrent coverageを失う。accepted ADR `20260830t085007z-adr` に従い、baseline lifecycleとsuccessor evidenceをrepository-level authorityへ移す。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I382-R01 | baseline rowは`active`、`resolved`、`retired`を明示できる。schema 1 rowは互換読取時に`active`として扱い、historical node/signature/rationaleを失わない。 |
| I382-R02 | `active` rowはcurrent candidateでexact node ID・failure signatureのfailureを要求する。missing、passed、skipped、xfail、signature driftをfail closedする。 |
| I382-R03 | `resolved/fixed-in-place` rowはexact node IDがcollected・executed・passed・not-skippedであることを要求する。 |
| I382-R04 | `resolved/superseded` rowは明示された完全なpytest successor node IDがbyte-for-byte一致し、collected・executed・passed・not-skippedであることを要求する。関数名だけの指定やsuffix/fuzzy match、old nodeのfailure継続、successor absence/skip/failureを拒否する。 |
| I382-R05 | `retired` rowはbaselineにnon-emptyで一意な`retirement_evidence_id`とaccepted authority referenceを要求し、observationの同一IDが`checked=true`かつ`outcome=absent`の場合だけverifiedとする。retiredを単なるunchecked ignoreにしない。Issue 382のcurrent ledgerにはretired row/evidence providerを追加せず、adapterはevidenceを供給できないretired rowをfail closedする。 |
| I382-R06 | schema validationとobservation evaluationは一つのpure evaluator moduleが所有し、standalone verifierとpytest guardは同じtyped resultを利用する。 |
| I382-R07 | evaluator resultはactive verified、resolved successor verified、retired verified、unexpected failure/error、signature mismatch、coverage mismatchを区別し、machine-readableに出力できる。 |
| I382-R08 | existing active 26 rowsのfailure/signature contractを維持し、retained-skill rowだけを`resolved/superseded`としてcurrent provider/dogfood successorへ束縛する。 |
| I382-R09 | global Full Regression workflow、manual command、pytest policy guardはrepository-level canonical pathを使用する。Issue 368 artifact pathを暗黙fallback authorityにしない。 |
| I382-R10 | distribution production code、managed distribution journal/recovery、public CLI/JSON、ordinary fast-lane skip policyを変更しない。 |

## スコープ

### 対象

- repository-level Full Regression policy/evaluator
- baseline schema 2とschema 1 read compatibility
- retained-skill rowのresolved successor移行
- standalone verifier adapter
- `tests/conftest.py` pytest adapter
- evaluator unit tests、adapter contract tests、negative tests
- `.github/workflows/provider-full-regression.yml` のcanonical verifier path
- Issue 368 historical artifactのauthority縮退とmigration guidance
- Issue 372の追加dependencyおよび再開条件

### 対象外

- distribution production codeとD1〜D4 semantics
- historical failure自体の修復
- Issue 372 M1〜M5の再実装
- failure countをacceptance constantにすること
- successor testのskip/xfail
- generic quality-gate framework
- topology simplification、module split、recovery protocol変更
- post-merge workflowをPR merge blockerへ変更すること

## 失敗・境界条件

- unknown schema/lifecycle/resolution mode、duplicate current/successor node、missing signature、invalid cross-referenceはtest実行前または結果受理前にfail closedする。
- zero collected successor、deselected、skipped、xfail、xpass、setup/collection errorはsuccessor passではない。
- resolved rowのold nodeが再びfailureした場合はunexpected/coverage mismatchとして拒否する。
- baselineにないfailure/errorは従来どおり拒否する。
- JUnitまたはpytest observationからrequired evidenceを証明できない場合、推測でpassにしない。
- Issue 368 artifactとrepository-level policyが矛盾する場合、repository-level accepted policyをauthorityとし、artifactをsilent fallbackしない。

## 受け入れ条件

| AC | 条件 |
|---|---|
| I382-AC01 | pure evaluatorのtable testsがactive/resolved-fixed/resolved-supersededに加え、syntheticなexact `retirement_evidence_id`、accepted authority、`checked=true`、`outcome=absent`を持つretired green caseと、missing/unknown/present/unchecked evidenceを含む全negative caseを通す。 |
| I382-AC02 | retained-skill old rowがhistorical evidence付きで残り、完全なsuccessor node `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` のcollected・executed・passed・not-skippedを証明したcandidateだけがgreenになる。 |
| I382-AC03 | successor missing/skip/xfail/fail/uncollected、old failure再発、signature drift、unknown failure/errorをそれぞれ検出するred-first regression testがある。 |
| I382-AC04 | standalone verifierとpytest guardへ同じobservationを与えると同じclassification/resultになるcontract testがある。policy logicの重複実装がない。 |
| I382-AC05 | existing active rowsのexpected node/signature集合がmigration前後で一致する。retained-skill row以外のdisposition driftが0。 |
| I382-AC06 | provider full-regression workflowとdocumented commandがrepository-level verifierを使い、Issue 368 pathへのcanonical runtime dependencyがない。 |
| I382-AC07 | focused evaluator/adapter tests、ordinary `uv run pytest`、`make lint`、`spec-dock validate`がgreen。 |
| I382-AC08 | exact candidateでFull Regression verifierがgreenとなり、active failures、resolved successors、unexpected resultsをmachine-readable receiptに記録する。 |
| I382-AC09 | Issue #382のStrict reviewがpassし、人間merge後にIssue #372のdependencyがsatisfiedになる。 |

## 制約・前提

- TDDはrepository-level evaluator interfaceを合意済みseamとし、private helperをtest surfaceにしない。
- testsとstandalone verifierは同じmodule interfaceを通る。二つ目のpolicy implementationを作らない。
- historical ledgerは移行前後の対応を機械検証できる形で保持する。
- tracked Reportは実装・検証方法を記録し、post-freeze run receiptでcandidate SHAを変更しない。
- PR mergeは人間が行う。Implementation Completion、Strict Review、merge、`issue finish`を分離する。

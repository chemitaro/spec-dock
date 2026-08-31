---
種別: ADR（Architecture Decision Record）
ID: "20260830t085007z-adr"
タイトル: "Full Regression Baseline Lifecycle And Successor Evidence"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-08-30"
親: ["epic-00365"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-08-30"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from: ["iss-00368", "iss-00372"]
reflected_to: ["iss-00382", "iss-00372"]
---

# 20260830t085007z-adr Full Regression Baseline Lifecycle And Successor Evidence

## Context

- Issue `iss-00368` の Full Regression ledger schema 1 は、すべての ledger row が current candidate でも同じ node ID・failure signatureで失敗し続けることを唯一の成功形としている。
- Issue `iss-00372` では historical Issue 359 digestをauthorityとする `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source` が、current provider/dogfood bytes・mode parityをauthorityとする `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` へ置換された。
- current verifierは旧nodeのfailureが観測されないことを `missing_failures` として拒否する。Issue 372 Reportでは unexpected failure、unexpected error、signature mismatchは0であり、停止理由はdistribution regressionではなくbaseline lifecycleの表現不足である。
- historical rowを削除してgreenにすると、過去の受理根拠とsuccessor coverageが失われる。旧failureを復活させるとcurrent source of truthを弱める。
- Epic `epic-00365` とIssue `iss-00372`はunrelated failure remediationおよびbaseline policyの独自変更を対象外としている。この判断はrepository-level quality governanceとして別authorityを持つ必要がある。

## Decision

### 1. Baseline row lifecycle

Full Regression baseline rowは削除せず、次のlifecycleを持つ。

- `active`: current candidateでも同一node ID・failure signatureのfailureを要求する。
- `resolved`: historical failureは解消済み。`fixed-in-place`または`superseded`のresolution modeを必須とする。
- `retired`: owning surfaceの廃止によりsuccessor testを持たない。明示的なabsence evidenceを必須とする。

schema 1 rowは互換読取時に`active`として扱う。schema 2への移行でhistorical signature、fixed point、rationaleを失わない。

### 2. Resolved successor evidence

`resolved`かつ`superseded`のrowは、次をすべて満たすsuccessor evidenceがある場合だけ合格する。

- successor node IDがbaselineに明示される。
- candidate test collectionにexact node IDが1件存在する。
- successorが実行される。
- outcomeがpassedである。
- skipped、xfail、xpass、deselected、uncollectedではない。
- successor node IDとresolution metadataがbaseline observationへ束縛される。

今回のretained-skill rowは`resolved/superseded`とし、successorを完全なpytest node ID `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` に固定する。suffix、関数名だけ、fuzzy matchは認めない。

### 3. One evaluator, two adapters

baseline schema validationとcandidate observation評価を一つのrepository-level pure evaluator moduleへ集約する。

- standalone Full Regression verifierはrun/JUnitを収集するadapterに留まる。
- pytest collection/session guardはpytest eventを収集するadapterに留まる。
- 両adapterは同じtyped evaluation resultを使い、active/resolved/retiredの意味を重複実装しない。

評価結果は少なくともactive failure verification、resolved successor verification、retired absence verification、unexpected failure/error、coverage mismatchを区別する。

### 4. Authority and rollout

- implementation ownerはIssue `iss-00382` とする。
- Issue `iss-00372` は `iss-00382` の完了に依存し、accepted evaluatorでFull Regressionを再実行する。
- Issue 368配下のverifier/ledger artifactを永続repository-level authorityとしてfallbackしない。移行後はhistorical evidenceまたはthin compatibility entrypointに縮退させる。
- distribution production code、D1〜D4 semantics、journal/recovery modelは変更しない。

## Options

- **採用: lifecycle + successor evidence**。履歴、現在coverage、fail-closedを同時に保持できる。
- 不採用: old rowの削除。履歴と解消根拠が消える。
- 不採用: old failing testの復活。current provider/dogfood authorityを弱める。
- 不採用: failure countの更新。node/signature/successor coverageを証明しない。
- 不採用: Issue 372内のad hoc exception。repository全体のbaseline semanticsがIssue-local patchへ分散する。
- 不採用: resolved rowを単純pass扱い。successor skip/uncollectedによるcoverage holeを見逃す。

## Consequences

- ledger schema、standalone verifier、pytest guard、tests、workflow pathを同一change setで移行する。
- active rowsのexact failure/signature contractは維持する。
- known failureが正当に解消された場合、failure countは減少し、gateはgreenになり得る。
- successor testのrename/removeはbaseline updateなしにfail closedする。
- schema complexityを抑えるため、resolution modeやevidence kindを追加する場合は新しいhuman decisionを要求する。
- rollbackはquality-governance changeのcode/schema/workflowを一体でrevertする。historical failing testを復活させず、consumer distribution dataへ触れない。
- 見直し条件: JUnit/pytestからcollected・executed・not-skippedを一意に証明できない、retired absence evidenceが過度に一般化する、または複数adapterで同じpolicyが再び分岐した場合。

## References

- `iss-00368` Full Regression ledger/verifier
- `iss-00372` Requirement R08/R10、Plan Step 10、Report Decision Required
- `iss-00382` Requirement/Design/Plan
- ChatGPT Use Strict fixed-SHA analysis `8a77a0a6d7d159b491cd654889b19e8bd32fedbe`

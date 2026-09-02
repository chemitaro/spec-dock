---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "design.md"
  - "artifacts/20260902t070000z-adr-multi-issue-epic-integration-branch-and-rolling-wave-elaboration-policy.md"
  - "artifacts/epic-integration-branch-contract.md"
  - "artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

## 1. Planning status

本計画は三Issue deliveryを固定する親計画である。前回multi-Issue replacement packはfailed reviewed candidate `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83`へimport、structural validation、commit、push済みである。Reviewer session `required-strict-github-connector-verificati-723`はP1 x1、P2 x1でfailしたため、現在は本remediationのadoptionと同一reviewer re-reviewがpendingである。Issue #392を含めimplementation startは許可せず、Product implementationも未startである。

## 2. Issue order and acceptance gates

| Gate | Entry | Observable acceptance | Exit |
|---|---|---|---|
| G0 Parent freeze | Imported failing candidate、authorized remediation、current connector-verified tip | R/D/P、ADRs、contracts、three Issue draftsと`E384-QUAL-001`が整合し、同一reviewerがP0/P1=0かつpass、owner decisions 0 | Reviewed tipをexternal `PARENT_FREEZE_SHA` receiptへ記録し、#384/#392/#395/#396 body projection/readback後に#392 elaboration可能。 |
| G1 #392 | G0 GREEN | Fixed ownership lifecycleがcomplete、wire適合、dogfood complete、14 active identities unchanged、transitional gates GREEN | Human merge to Epic branch、B1 GREEN readback。 |
| G2 #395 | B1 GREEN | 14 active rowsがProduct修正でnormal pass、15 resolved、approved 0、transitional gates GREEN | Human merge、B2 GREEN readback。 |
| G3 #396 | B2 GREEN | Build-once final gate、`E384-QUAL-001` conformance evidence、consumer-first old policy removal、final docs/dogfood、context/evidence GREEN | Human merge、B3 GREEN readback。 |
| G4 Epic main | B3 accepted | Final human review、tree equality、required contexts、rollback record | One human merge to main、B4 closure。 |

## 3. Rolling-wave cycle

各Issueについて同じcycleを適用する。

- external `PARENT_FREEZE_SHA` receiptまたはaccepted predecessor tip、dependency evidence、GREEN observationsを固定する。
- Issue draft contractとparent stable contractsを比較する。
- Current treeからowned/shared/no-touch inventory、representative RED、implementation design、tests、commands、rollback procedureを具体化する。
- Issue-specific R/D/PとLuna Max handoffを独立Strict reviewする。
- Review accept後にだけIssueをstartする。
- 実装、Issue-level verification、human PR review、human integration mergeを完了する。
- Exact merged tipでGREENを再確認し、Issue acceptanceを記録する。
- 次Issueのelaborationまでbranchをsingle-writerに戻す。

このcycleのimplementation detailは本parent Planに固定しない。

## 4. G1 — Issue #392 contract gate

G1はlifecycle Product outcomeだけを受け入れる。Failure baselineのactive identitiesとcurrent regression systemはcompatibility inputであり、terminalizationまたはfinal policy cutoverを先取りしない。Final qualification guaranteeは削除せず、parent `E384-QUAL-001`と#396へ移管済みのread-only non-goalとして保持する。Lifecycle candidateを変更するためcomplete dogfood convergenceを必要とする。

## 5. G2 — Issue #395 contract gate

G2はregisterの14 active rowsだけをProduct defect scopeとして扱う。各rowは自身のRED/GREENとcurrent integrated behaviorを持つ。全検証をG3へ延期しない。Current policyを利用してactive/approved 0を証明し、final policy toolingまたは`E384-QUAL-001` implementationを先取りしない。

## 6. G3 — Issue #396 contract gate

G3はB2 clean baselineをadmission条件とする。Replacement gateを成立させた後、old consumersを0にしてからold providers/data/workflowを削除する。Build-once、same bytes、platform role、`E384-QUAL-001`のmechanical evaluation/evidence、required-context transition、final operator guidanceを同一Issue acceptanceへ統合する。Issue-start elaborationはimplementation mechanismを具体化できるが、`E384-QUAL-001`のvalue、population、window、aggregation、scope、rejectionまたはescape prohibitionを変更・複製しない。

## 7. Merge and rollback governance

- Human alone merges Issue PRs and final Epic PR。
- Issue PR merge後のGREEN未確認中は次Issue branchを作らない。
- Revertはwhole Issue mergeを単位とする。
- Later Issue開始前なら直前mergeをrevertできる。
- Later Issue開始後のrollbackはunmerged workを破棄し、accepted suffixを逆順に戻す。
- Partial stable-contract rollback、automatic Issue creation、automatic branch-setting change、agent mergeは禁止する。
- Recoveryでstable contract変更が必要ならIssueを停止し、parent R/D/PとADRを再承認する。

## 8. Evidence and reporting

各Issue reportは既存draft scaffoldから、そのIssue実装時にだけ更新する。本packではIssue reportを置換しない。Epic reportはplanning adoptionとverified baselineだけを記録し、実装完了を主張しない。

Required evidence is distributed:

| Issue | Evidence category |
|---|---|
| #392 | Lifecycle behavior、migration/uninstall、filesystem recovery、wire、dogfood/protection、transitional-gate non-regression |
| #395 | Exact row RED/GREEN、Product behavior、15-row terminal state、ordinary/full current gates、dogfood/protection |
| #396 | Workflow structure、same artifact bytes、platform roles、`E384-QUAL-001` raw/mechanical evidence、policy consumer-zero/removal、contexts、final dogfood/docs |
| Epic | Three merged-tip GREEN receipts、B3 tree、final main merge tree equality、closure readback |

## 9. Stop policy

Stop before Issue start or merge for dependency mismatch、non-GREEN branch、stable contract drift、unexpected baseline identity、`E384-QUAL-001` omission/duplication/semantic drift/incomplete evidence、scope outside Issue boundary、partial dogfood、protected-data drift、new approved failure、later-Issue tooling dependency、consumer-before-provider ordering violation、context gap、unreadable evidence、rollback ambiguity、or human gate bypass。

Stop result must return exact observed branch tip、failed contract ID、affected Issue、expected/actual state、and whether whole-merge revert is still available. Luna Max does not choose an alternate architecture.

## 10. Completion

G0 is complete only after the same reviewer accepts the exact clean pushed remediation tip, external `PARENT_FREEZE_SHA` is recorded without a tracked self-reference, and all four GitHub Issue body projections are read back. Epic is complete only after G1–G3 are accepted on the integration branch and G4 is human-merged once to main. `owner_decisions_required=[]`.

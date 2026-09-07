---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-08"
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

本計画は三つの実装・検証単位を順次統合する親計画である。2026-09-02の親候補 `1429c2f899c6d2086d5bd03c0dcea01f5b168435` はreview execution `required-strict-github-connector-verificati-747` でpass、findings `[]` となり、freeze receiptとGitHub body projection/readbackまで完了した。過去の「review 740 fail後の修正待ち」は現在の残作業ではない。後続編集のacceptanceは別のexact-candidate reviewで判定する。

2026-09-08のユーザー指示により、この環境はEpicの要件・設計・Issue境界・統合契約の具体化に専念する。各Issueの詳細化も実装も、後日新しく作るIssue branch/worktreeで行う。本環境でIssue start、Issue branch/worktree作成、Product変更は行わない。

### 作業場所と引き継ぎ境界

| 場所 | 行うこと | 行わないこと |
|---|---|---|
| 本Epic worktree | 親R/D/P、横断契約、Issueのgoal/non-goal/acceptance境界、独立review、人間向け説明 | 個別Issueの詳細手順作成、Issue start、実装 |
| 将来のIssue専用worktree | 受理済みEpic tipから分岐し、そのIssueだけの詳細R/D/PとLuna Max handoffを作る。review後に実装・検証 | 親の要件を推測変更すること、mainへの直接統合 |
| Epic integration branch | 人間がIssue PRを順番にmergeし、各merged tipのGREENを確認する | 複数Issueの並列writer、検証を後続Issueへ先送りすること |

### レビュー方式

外部ChatGPT Useが動作しない状況について、ユーザーがGPT-6で進めることを明示的に承認した。現在の独立reviewはGPT-6（`gpt-6-astra`）・推論Maxのfreshサブエージェントで開始し、修正後は同じreviewerを再利用する。主担当が指摘を現物で判断し、親文書だけを修正する。Luna Maxは将来の実装担当であり、このEpicのreviewerには使用しない。既存Issue draftにある「Strict review」の現行経路・証拠要件は[Rolling-Wave Contract §5](artifacts/rolling-wave-issue-elaboration-contract.md)で一元的に定義する。ローカルreviewを外部ChatGPT Strict passとは呼ばない。

## 2. Issue order and acceptance gates

| Gate | Entry | Observable acceptance | Exit |
|---|---|---|---|
| G0 Parent freeze | 親候補、current Git-verified tip | R/D/P、ADRs、contracts、three Issue draftsと`E384-QUAL-001`が整合し、当該候補の独立reviewがP0/P1=0かつpass、owner decisions 0 | Reviewed tipをexternal `PARENT_FREEZE_SHA` receiptへ記録し、#384/#392/#395/#396 body projection/readback後に#392 elaboration可能。 |
| G1 #392 | G0 GREEN | Fixed ownership lifecycleがcomplete、wire適合、dogfood complete、14 active identities unchanged、transitional gates GREEN | Human merge to Epic branch、B1 GREEN readback。 |
| G2 #395 | B1 GREEN | 14 active rowsがProduct修正でnormal pass、15 resolved、approved 0、transitional gates GREEN | Human merge、B2 GREEN readback。 |
| G3 #396 | B2 GREEN | Build-once final gate、`E384-QUAL-001` conformance evidence、consumer-first old policy removal、final docs/dogfood、context/evidence GREEN | Human merge、B3 GREEN readback。 |
| G4 Epic main | B3 accepted | Final human review、tree equality、required contexts、rollback record | One human merge to main、B4 closure。 |

## 3. Rolling-wave cycle

各Issueについて同じcycleを適用する。

- external `PARENT_FREEZE_SHA` receiptまたはaccepted predecessor tip、dependency evidence、GREEN observationsを固定する。
- Issue draft contractとparent stable contractsを比較する。
- Current treeからowned/shared/no-touch inventory、representative RED、implementation design、tests、commands、rollback procedureを具体化する。
- 別のIssue専用worktreeで作成したIssue-specific R/D/PとLuna Max handoffを、Rolling-Wave Contract §5に従って独立reviewする。
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

G0 is complete only after the independent reviewer accepts the exact candidate under the Rolling-Wave Contract, the accepted clean pushed tip is recorded as external `PARENT_FREEZE_SHA` without a tracked self-reference, and all four GitHub Issue body projections are read back. Epic is complete only after G1–G3 are accepted on the integration branch and G4 is human-merged once to main. `owner_decisions_required=[]`.

---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "detailed-review-candidate"
詳細化状態: "independent-review-pending"
最終更新: "2026-09-08"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "14a72044738ce698c3113a0ee70f052015e3be8a"
  tree: "af8e50ed3e20e5a03ef1e2a46332142befa1251f"
---

# #392 要件定義 — Provider lifecycleを固定所有境界へ切り替える

## 1. このIssueで完成させるもの

利用者の仕様データを残したまま、SpecDockのインストール・更新・toolingだけのアンインストール・再インストールを、一つの小さな固定所有モデルへ切り替える。最終成果は**実際のpublic CLI、失敗後の復旧、通常runtimeとの排他、完全なdogfood、旧writer撤去まで揃った0.2.4**である。新しい内部moduleだけ、testだけ、仕様だけを#392の実装完了としない。

実装は一つのIssue内の逐次checkpointに分ける。#392 PRのbaseは `codex/epic-00384-provider-test-strategy-planning`。人間のmergeとB1再検証後にだけ#395を開始し、#396の完了後にEpicをmainへ一度mergeする。

[親Requirement](../../requirement.md)、[Wire](../../artifacts/provider-lifecycle-wire-contract.md)、[Integration Contract](../../artifacts/epic-integration-branch-contract.md)が上位の正本。旧titleの「Regression Gate」は履歴上の名称であり、final gateの実装は本Issueに含まない。

## 2. 開始状態・証拠

- #387は完了・main merge済み。現行調査基準は上記SHA/treeのpost-#387実装。
- #392は同worktreeで正式 `issue start` 済み。branch/active選択とProduct実装開始許可は別。
- 親の `E384-DEC-001/002` は採用済み。P392-001/002はユーザー承認の[準備失敗ADR](../../artifacts/20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md)とWire v12で解消し、親内容レビューはP0/P1=0、pass。
- 本書・Design・Plan・handoffはそのv12から導くIssue詳細候補。独立内容reviewと公開freeze/projectionの成立前にコーダーを起動しない。
- 旧調査の停止記録は[親差し戻しArtifact](artifacts/20260908t010201z-issue-392-elaboration-parent-return.md)に履歴として残す。そこにある「承認未取得」は当時の状態であり現在の未決事項ではない。

## 3. Goal / Non-goal

### Goal

1. 四つのfixed roots、二つのskill slots、七key record、二つのfresh-only seedの所有権を分離する。
2. 正常系だけでなく準備・初期record・root間・terminal・cleanupの中断をexact-tuple recoveryへ閉じる。
3. supported runtimeが混在世代を実行しない。managed Git checkout/worktreeも排他の対象に含める。
4. exact clean 0.2.3 migrationとold-package mutation-zero、public互換、complete dogfoodを証明する。
5. 旧per-file engineと旧契約だけのtestsを同じIssueで撤去し、現行gateを維持する。

### Non-goal

- #395の14 active baseline failuresの修正・skip・xfail・retirement・signature変更。
- #396のbuild-once gate、test-policy切替、ledger/timing/sharder削除、`E384-QUAL-001`測定・再定義。
- arbitrary migration、旧writer fallback、汎用journal、whole-operation automatic rollback、任意manifest ownership。
- 利用者のspecs、active、projection、workbenchをinstallerが生成・修復・削除すること。
- manual Git/filesystem編集や任意consumer hookまで含む完全な並行制御。
- 調査/検証だけの新Issue、checkpointの単独merge、agentによるPR merge。

## 4. 所有と保護

| 対象 | #392の契約 |
|---|---|
| `spec-dock/{docs,templates,system,scripts}` | 所有成立後はroot全体をcandidateへ交換。inner local editsは保存しない。scriptsが最後。 |
| `.agents/skills/spec-dock`, `spec-dock-grill-with-docs` | exact slotとvalid owner markerだけがauthority。共有親や他skillをscan/deleteしない。 |
| `spec-dock/spec-dock.version` | Wireの七key record。incomplete/ready/tooling-absentをdurableに公開。 |
| `spec-dock/.gitignore`, `.github/workflows/ci.yml` | create-if-absentのfresh-only seed。既存bytesを更新・削除しない。 |
| `spec-dock`, `.github`, `.github/workflows` | 必要な初回containerだけbounded creation。既存container全体の所有権を取得しない。 |
| initiatives、Artifacts、active、.agent、diagrams、.workbench、unknown、unrelated skills | lifecycleのread/rebuild/delete対象ではない。opaqueに保持する。 |
| private stage/ACTIVE/receipt | Consumer外・同一filesystem・owner/repository-boundな有限bookkeeping。public ownershipの追加ではない。 |

## 5. 要件と受入条件

「pass」は検証を実行して証拠が揃った状態をいう。以下のT-IDは[test所有表](artifacts/20260908t011846z-01-lifecycle-test-ownership-and-migration.md)の実装先へ対応する。

| ID | 要件 | 完了時の観測可能な受入条件 | 主なproof |
|---|---|---|---|
| I392-RQ-001 | 一つの実装受入単位 | public 0.2.4 routeに到達し、旧writer import/call/旧manifest dependencyが0。内部checkpointは非mergeable。 | T01,T12,T14 |
| I392-RQ-002 | fixed authority | roots/slots/record以外のsentinelはbytes/type/inodeが不変。unknown shared pathsは探索しない。root内obsoleteは残らない。 | T03,T04,T07 |
| I392-RQ-003 | recordとimmutable seed policy | 七keyの厳密parse/serialize、duplicate/unknown/type違反拒否。seedの有無でoperation policyを再推論しない。 | T01,T02,T03 |
| I392-RQ-004 | closed wire | Wire §10の168 rows、41 codes、40 public/4 record goldensとtext/exitが一致。未列挙relationはconstructor defect。 | T01,T02 |
| I392-RQ-005 | filesystem/preparation/recovery | no-follow/binding/native primitives、WIR-PREP-001 P0/P1/P2、root間中断、terminal/receipt全faultがexact結果とcontinuationへ収束。protected data不変。 | T04,T05,T06 |
| I392-RQ-006 | migration/uninstall/old-package | 指定legacy fixtureのみ移行。tooling-only absent recordを残す。purge flagはexit2/mutation0。旧0.2.3でfinal stateを変更できない。 | T02,T07,T12 |
| I392-RQ-007 | provider-first/dogfood | 四roots/二slots/record/markersが同candidateに一致。seeds/specs/workbench/projectionは不変。packaged wheel/sdistでも同じ成果。 | T12,T13 |
| I392-RQ-008 | baseline不変 | 15 rows/14 active/1 resolvedを維持。active node/signature/lifecycleと243 timing entriesを変更せず、unexpected failure 0。 | T14 |
| I392-RQ-009 | B1 integration GREEN | current PR/full pathの機構を保持。focused Linux/macOS parityと全current gateの証拠があり、human merge後tipを再検証。 | T14 |
| I392-RQ-010 | 実装開始gate | 詳細R/D/P・handoffのP0/P1=0/pass、同内容のclean pushed freeze/projection、次の一stepのhandoff承認を揃える。 | Plan G0 |
| I392-RQ-011 | pre-import/lease | runtime SH、installer EXをroot inodeでNB取得。busy/unsafe/unavailableはwrite/import前。parent死亡後もmanaged writerの最後のwriteまでleaseが残る。 | T08,T09 |
| I392-RQ-012 | terminal handoff | update/uninstallの全retained flag/target形でA leaseを閉じて外部installerがBを再admit。old moduleへ戻らずstreams/status/127を保持。 | T09 |
| I392-RQ-013 | managed Git generation | pinned same-closure checkoutだけ許可。different generationはcheckout前、post driftはactive/sync前に停止。B birth/removeはB EXとentrypoint-last、reused path保護。 | T10,T11 |
| I392-RQ-014 | consumer hook境界 | make detection/initは全A/B lease解放後、nonlocking original-B fdで実行。Cへredirectせず、現行bootstrap status/warning/outer exit0を保持。 | T11 |

### 親へのtrace

Owned: E384-RQ-004/005/006/008/009/019、およびE384-RQ-015のlifecycle部分。Shared/read-only: E384-RQ-001〜003/007/016〜018。Final qualificationは親 `E384-QUAL-001` / #396がsole authority。#392で数値や母集団を再定義しない。

## 6. エラー・復旧の利用者体験

不正入力は変更前に停止する。通常I/O失敗を所有者違反に偽装しない。出力する次コマンドはWireの一つに限定し、seed policy・candidate・operationを変えてretryしない。cleanup retryのtokenはgeneration-boundで、通常操作を兼ねない。cleanup後のdeferred requestは別invocationとして利用者が実行する。

四roots全体のatomicityは約束しない。中断後の通常runtimeはbusyまたはnot-ready（script自体がない場合は起動不能）であり、外部installerのexact recoveryだけが進める。ready+cleanup warningは通常runtimeを許可する。詳細な出力の正本はWire一つとする。

## 7. 停止条件・残るgate

wire変更、未知のauthority、baseline変化、#395/#396への越境、未決Product判断、Linux/macOSでnative proof不成立は停止して親へ戻す。coderは別診断・fallback・skipを発明しない。

仕様内容の完成、公開済みfreeze、Product実装、Issue完了は別の証拠である。今回の仕様作成ではProductを変更せず、残る公開・実装gateを[Report](report.md)に明記する。完了後の保守責任は通常repository maintainer、#395/#396はこのlifecycleをread-onlyに利用する。

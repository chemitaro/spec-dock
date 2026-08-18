---
種別: 要件定義書（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
状態: "planned"
最終更新: "2026-08-18"
親: ["epic-00365", "init-local-00003"]
---

# iss-00372 Distribution Hard Cutover And Parity — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

D1〜D4で移行した全public distribution flowについて、legacy execution seamが各owner Issueで物理的に除去済みであることを検証し、provider checkout、dogfooding workspace、wheel、sdist、fresh consumer、Linux、macOSで同じcontractが成立することを確定する。利用者に見えるcommand/flag/data/JSON semanticsとdata-preservation safetyを維持したまま、single ownership boundaryのabsence evidenceを完成させる。

## 背景

vertical cutover後もdead code、private import、compatibility callback、legacy writer、package surface drift、Linux-only evidenceが残れば、次の変更で第二経路が復活し得る。D5は新featureを作るIssueではなく、absence/parity/evidenceを完成させるIssueである。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I372-R01 | all public intentsがsingle Distribution Operation Service、action grammar、filesystem kernel、journal protocol、ProcessResultを使用する。 |
| I372-R02 | `cli.py`はparse、package asset location、dispatch、render、exit mappingだけを持ち、ownership policy、recursive mutation、journal transition、staging cleanupを持たない。 |
| I372-R03 | `_UninstallAction`、old uninstall plan/apply/postverify、CLI recursive mutation、dual marker writer、private `_rename_distribution_no_replace` import、`scaffold_applier`/blocked-path fallback等のlegacy seamがproduction call graphに存在しない。 |
| I372-R04 | provider source、checked-in dogfood、wheel、sdist、installed resources、fresh consumerのmanaged inventory/bytes/modes/symlinks/manifest contractが一致する。 |
| I372-R05 | `init`、`init --force`、`update`、deprovision、purgeのpublic command/flag/exit/text/JSON semanticsがpre-Epic contractと一致する。 |
| I372-R06 | ownership/preservation matrixとfailure/resume matrixがall intentsを覆い、single implementation pathを検証する。 |
| I372-R07 | LinuxとmacOSでfocused distribution safety suiteが同一candidate SHAに対して成功する。required capabilityがないplatformはwrite前にstable diagnosticで停止する。 |
| I372-R08 | migration/recovery docsがnew journal、legacy marker fail-closed、code rollback/forward recovery distinction、exact pre-action SHA ruleを正確に説明する。 |
| I372-R09 | affected fast testsとtargeted full-regression testsが成功し、pre-Epic exact baselineと比較してEpic attributable new Full Regression failureが0件である。 |
| I372-R10 | Full Regressionのunrelated existing failures、Windows、new product feature、AI orchestration、generic transaction、whole-operation rollbackをscopeへ追加しない。 |

## スコープ

### 対象

- legacy symbol/import/call-edge/writer/fallback absence
- CLI/domain/kernel dependency boundary tests
- provider/dogfood/wheel/sdist/installed/fresh parity
- Linux/macOS focused CI/evidence
- public CLI/JSON semantic regression
- migration/recovery/README docs
- exact SHA Full Regression attribution

### 対象外

- D1〜D4のbehavior redesign
- new operation/action/product feature
- Full Regression unrelated failure repair
- Windows support
- broad repository refactor/line-count goal
- node metadata/title/path changes

## 失敗・境界条件

- legacy helperがdead codeとして残る場合もexit不可。absenceをsymbol/import/AST/call graphで検証する。
- package surfaceの一つだけがnew code/assets/testsを欠く場合はparity failure。
- macOS evidenceが未実行、best-effort、別SHAの場合はexit不可。
- Full Regression total countを旧26件と仮定しない。exact baseline/candidate command/resultを記録する。
- public JSON field/semantics drift、one-object violation、absolute path/content leakはcompatibility failure。
- docsがimplementationと異なる場合はdocsだけでpassにしない。

## 受け入れ条件

1. production import/call graphとabsence testsでsingle service/kernel/writerを証明する。
2. listed legacy symbols/seamsがsourceから削除されるか、migration readerとして残る場合はwrite authorityを持たず明示的allowlist testがある。
3. provider/dogfood/wheel/sdist/installed/fresh consumer inventoryとbytes/mode/link contractが一致する。
4. Linux/macOS focused suiteがsame candidate SHAでgreen。
5. all public flowのownership/preservation/failure/resume matrixがgreen。
6. public command/flag/text/JSON/exit golden testsがgreen。
7. README、canonical docs、ADR、HTML、recovery guidanceがimplemented names/behaviorと一致する。
8. affected fast suiteがgreen。
9. Full Regression exact baseline/candidate comparisonを実行・分類し、Epic attributable new failureが0。
10. no new Issue、node rename、metadata edit、scope reintroductionがない。

## 制約・前提

- dependencies `iss-00368`〜`iss-00371`が完了済みである。
- D5でbehavior gapが見つかった場合はowner IssueのRequirement/Designへ戻し、D5で黙ってnew semanticsを決めない。
- production executable pathまたはwriterを持つlegacy seamが見つかった場合はowner Issueのexit未達としてD5をblockし、D5 scopeでcleanupを代行しない。migration-only readerはexplicit allowlistとwrite-zero testで判定する。
- platform evidenceはcommand、runner、OS、Python/package version、candidate SHAを記録する。
- Full Regression未解決unrelated failureはsibling Epic handoff evidenceに分類するが、本Issueでnodeを作らない。

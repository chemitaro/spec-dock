# Issue 344 Final Plan Review

対象は GitHub connector で取得した `chemitaro/spec-dock`、branch `iss-00344-workbench-shell-scaffolding`、commit `bba8fd5531a9ca03d6c61fa0dc095a653e4af260`。branch と指定 commit は connector 上で identical と確認した。

## Verdict

**FAIL**

S01、S02、S03、S90 の step schema と、S99 の大部分は実行可能な粒度まで整備されている。先行 B-001/B-002/B-003 の修正も反映済みである。

ただし、**S99 の final commit 後の commit SHA / clean-check 証跡の保存先が repository workflow と矛盾している**。このままでは、final commit 後に `report.md` を再度変更して worktree を dirty にするか、さらに別 commit を必要とする自己参照構造になる。repository-schema fail condition に該当するため、昇格不可と判定する。

## Findings

### B-004 — Blocking: S99 が post-commit SHA を committed `report.md` の EVD へ書き戻す自己参照契約になっている

`plan.md` の S99 は、次のように規定している。

* planned contract の report evidence destination に `commit SHA` を含める。
* step closure evidence に `commit SHA` と EVD-009/010 を含める。
* final report/review evidence commit の**後**に HEAD SHA と clean status を確認し、commit SHA を EVD-009/010 へ記録する。
* EVD-009 と EVD-010 は明示的に `Report記録` と定義されている。

一方、canonical `workflow_issue.md` は、三者 PASS 後に report ledger と post-commit external evidence の**記録先**を report に入れて final commit を作成し、final commit hash と clean check の実測値は、commit 後にしか確定しないため、**committed `report.md` の必須記録ではなく external delivery evidence に残す**と明記している。

`report.md` の正本 schema も、Final Commit 行に求めているのは actual SHA ではなく、`post-commit external evidence destination` である。

したがって、現行 S99 を文字どおり実行すると次の循環が生じる。

```text
final evidence commit
  -> HEAD SHA / clean status を取得
  -> EVD-009/010 の report 記録へ SHA を追記
  -> report.md が dirty
  -> clean check が不成立
  -> 追記を commit すると、先に取得した SHA は final SHA ではなくなる
```

**必要な bounded correction:**

1. S99 の `report evidence destination` と step closure evidence から、actual `commit SHA` の report 内記録要求を削除する。
2. final commit 前に、report の Final Commit ledgerへ次だけを記録する。

   * final report ledger
   * final commit scope
   * `post-commit external evidence destination`
   * ready / blocked
3. 三者 fresh PASS、report 追記、orchestrator approval の後に mandatory final evidence commit を作成する。`approved-no-op` 禁止は維持する。
4. commit 後に `git rev-parse HEAD` と `git status --short` を確認する。
5. actual SHA と clean-check result は、report に指定済みの final response、Issue 346 handoff、issue comment等の **external delivery evidence** にのみ記録する。commit 後に `report.md` を変更しない。
6. EVD-009 は reviews、EVD-010 は handoff の report ledgerとして維持し、actual post-commit SHA の保存先にはしない。

## Scope and consistency checked

| 対象                             | 判定        | 確認内容                                                                                                                                                                                                                                                                                              |
| ------------------------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S01                            | 適合        | behavior slice、planned contract、依存・target、9項目 delegation、4 test cards、TC-344-001〜005 closure、report-before-review/result/commit gateが揃っている。vertical tracer は fresh init → filesystem → real Git observationまで通り、generic exact-copy、changed-placeholder rendering、path-agnostic guardrailも明示されている。 |
| S02                            | 適合        | S01依存、opacity/copy test-only target、read-only production boundary、planned contract、9項目 delegation、opaque/checkout/source-wins/root-rejection cards、closure、review/result/commit gateが整合している。                                                                                                      |
| S03                            | 適合        | `pyproject.toml` exclusion、installer prune、custom `build_py` post-build prune、temporary wheel/sdist/install、exact five-path inventory、stale nested README除去、scoped Ruff/format/Mypy/diffを具体的な test nodeとclosureへ結び付けている。                                                                          |
| S90                            | 適合        | behavior sliceとplanned contractが追加され、primary workerは `doc-writer`、reviewerは `spec-reviewer`。provider docs 4件を所有し、canonical Workbench README 4件は S01-owned / S90 read-only reference と固定されている。docs-only alternative evidence、cards、closure、approved-no-op条件もある。                                    |
| S99                            | 一部不適合     | behavior slice、planned contract、三者 read-only delegation、aggregate/governance cards、closureは存在する。report → three fresh PASS → orchestrator approval → mandatory final evidence commit → clean check、および no approved-no-op も明記された。ただし post-commit evidence destination が B-004 のとおり不適合。              |
| Repository step schema         | S01〜S90適合 | 各 step に behavior goal、planned contract、delegation、card tests、closure、report destination、gateを要求し、delegationには9項目、cardには前提・操作・期待結果・失敗検出・検証方法を要求する正本 schemaと照合した。                                                                                                                                  |
| Docs ownership / diagrams      | 適合        | execution overviewとPlantUMLは M1/M2/M3 → S90 → S99、impact tableは provider docsをS90、canonical READMEをS01、S90はread-onlyとする。designのprovider/output/copy図および責任表とも矛盾しない。                                                                                                                                |
| Current provider/build seams   | 適合する変更対象  | 現行 scaffolder はUTF-8 fileをtext read/writeするため unchanged CRLF等をrewriteし得る。現行 `setup.py` と `pyproject.toml` は broad nested README patternを持ち、custom `build_py` は通常copy後にpruneを実行する。計画のgeneric exact-copyとdual exclusion/prune修正は実際のseamを対象としている。                                                    |
| Distribution test feasibility  | 適合        | existing `TestInitUpdate` helperはisolated build environment、local wheelhouse、`python -m build --wheel --sdist --no-isolation`、environment injectionを既に提供し、現行 prune testもpre-prune snapshotとwheel inventoryを観測している。計画はこの既存seamを再利用している。                                                            |
| Parent Epic / sibling boundary | 適合        | Issue 344はWorkbench shellのfocused owner、Issue 345はgeneric import、Issue 346はcandidate distribution・dogfood・full regression・delivery ownerという分離を維持している。Issue 344はPR、merge、finishを主張しない。                                                                                                             |
| Assurance / report lifecycle   | 未昇格状態と整合  | `.assurance.json` は現行 requirement/design/planをbindingし、authorized profileを `standard` としているが、statusは `provisional`。reportのplan authoring gateも、先行修正適用後のfresh re-review待ちとして failed/blocking のままである。                                                                                               |

先行 B-001/B-002/B-003については、S90/S99 planned contract、S99 ordering、docs ownershipの修正が canonical plan と report EAL-018へ反映されているため、解決済み findingとして再掲していない。

添付された `設計判断と提案.txt` は例外 taxonomy に関する別件資料であり、Issue 344の判定根拠には使用していない。

## Residual risks

* 本レビューは repository 文書、provider source、build configuration、既存 test codeの静的照合であり、pytest、build、Git matrix、wheel/sdist install等は実行していない。
* 新規 `tests/unit/infra/test_runtime_template_scaffolder.py` は指定HEADにはまだ存在しないが、S01の明示された新規作成targetであり、現時点の欠落はplan defectではない。
* B-004修正後も、actual executionでは reportに記録した external evidence destinationと、最終応答またはIssue 346 handoffで使用したdestinationが一致することを確認する必要がある。
* current assuranceは provisional、reportのplan gateもblockingであるため、本回答をfresh `spec-reviewer` PASSやimplementation readinessの代替にはできない。

## Promotion decision

**Promotion denied.**

`plan.md` の S99だけを bounded correctionし、actual final SHA / clean-check resultを committed reportから external delivery evidenceへ移す必要がある。修正後は fresh final plan reviewを再実施し、blocking findingがなくなった場合にのみ fresh `spec-reviewer` plan reviewへ進める。実装開始、PR、merge、Issue finishへの昇格はまだ認められない。

# Issue 344 Fresh Final Plan Review

## Source Verification

| 項目                      | 確認結果                                                    |
| ----------------------- | ------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                   |
| GitHub Issue            | `#344 Workbench Shell Scaffolding`、open                 |
| Branch                  | `iss-00344-workbench-shell-scaffolding`                 |
| 指定 HEAD                 | `a6d923b8bb942eec72cb72d96c874d9d3ec79ce8`              |
| Branch HEAD             | branch ref を直接取得して指定 SHA と一致                            |
| Compare                 | `status=identical`、ahead/behind `0/0`、`total_commits=0` |
| Default branch fallback | 使用していない                                                 |
| 読み取り基準                  | 全ファイルを指定 SHA の `ref` に固定                                |

指定 SHA から、Issue の `requirement.md`、`design.md`、`plan.md`、`report.md`、親 Epic 343 の requirement/design/plan、`workflow_issue.md`、`authoring/issue-plan.md`、`phase_plan_issue.md`、ならびに `setup.py`、`pyproject.toml`、generic scaffolder、既存 build/test harness、Issue 346 dependency metadataを確認した。

実装可能性の静的確認では、custom `build_py`、stale fixture seed、pre-prune snapshot seamが実在し、既存 `TestInitUpdate` にはrepository外 temporary build、local wheelhouse、wheel/sdist生成のhelperがある。`TestCliNew` harnessも存在し、Issue 346にはIssue 344/345へのdirect dependency edgeが登録されている。

本レビューはread-onlyの仕様・計画レビューであり、pytest、Ruff、Mypy、build、またはGit mutationは実行していない。したがって、コマンドの成功実績ではなく、指定HEADにおける計画の完全性とsource seamの存在を判定した。

添付の `設計判断と提案.txt` は例外・Failure設計に関する別テーマの資料であり、Issue 344の正本または補助証跡ではないため、判定根拠から除外した。

## Verdict

**FAIL**

B-001〜B-007およびB-005-R1の修正内容は閉じている。B-008についても、各step内部の

`orchestrator report統合 → fresh reviewer PASS → actual commit / approved-no-op → clean確認 → close state確定 → Result Approval`

という順序と、S99のreport-before-final-commit／external-only SHA・clean境界は修正されている。

しかし、**Result Approval後にどのstepだけが入場可能になるかという依存グラフが、計画内で一意になっていない**。さらに、S99のpredecessor条件が正当な`approved-no-op`を受け入れるかも矛盾している。これはユーザー指定の「then and only then next-step admission」と、Issue planの実行可能なcommand queue要件を満たさないstructural blockerである。

## Blocking Findings

### B-008-R1 — next-step admissionとpredecessor close-stateが一意でない

計画の上位記述は、3つのmicro-batchを「順番に」実行し、図と実装順序でも次の一本道を定義している。

```text
S01 → S02 → S03 → S90 → S99
```

M2はM1を、M3はM1/M2を前提とし、S03の後にS90、最後にS99を置いている。

一方、step dependency表と各step gateは別のグラフを定義している。

| Step | 現在の記述                                      | 問題                                    |
| ---- | ------------------------------------------ | ------------------------------------- |
| S01  | `S02、S03`をunblockし、Result Approval前の両方を禁止  | S01承認直後にS03を開始でき、宣言済みのS02先行順序を迂回できる   |
| S02  | `S90、S99`をunblockし、Result Approval前の両方を禁止  | 直後のS03をgateしていない一方、後続S90/S99をgateしている |
| S03  | `S99`のみをunblockし、Result Approval前のS99のみを禁止 | 直後とされるS90をgateしていない                   |
| S90  | S99をunblockし、Result Approval前のS99を禁止       | この部分単独は整合している                         |

この不一致はstep tableに明記され、S01/S02/S03のgateにも反映されている。

したがって実行者は、少なくとも次を補完判断しなければならない。

1. S01承認後、S02を完了せずS03を開始してよいか。
2. S02承認後、S03より先にS90を開始してよいか。
3. S03承認がS90の入場条件なのか。
4. 上位の一本道とstep-local dependency表のどちらを優先するか。

`workflow_issue.md`は、current stepのclosure、verification、fresh reviewer PASS、commit/no-op、post-commit cleanが閉じ、Result Approvalを得た後だけ次stepのimplementation/review/commitを開始できると定義している。Issue planも、実装者が上から判断なしで実行できるcommand queueでなければならない。

加えて、S99は「S01、S02、S03、S90の`committed result`」へ依存するとしているが、各predecessor gateとFinal Quality Gateは正当な`approved-no-op`も有効なclose stateとしている。

このままでは、predecessorが正当に`approved-no-op`で閉じた場合にS99へ入場できるかが不明である。S99自身はmandatory final commitで閉じるため、predecessor条件とS99自身のclose stateを明確に分ける必要がある。

必要な修正はplan-localで、次のように一本道へ統一できる。

```text
S01 Result Approval
  → S02 admission

S02 Result Approval
  → S03 admission

S03 Result Approval
  → S90 admission

S90 Result Approval
  → S99 admission
```

併せて、S99の依存条件を次の意味へ変更する必要がある。

```text
S01/S02/S03/S90:
  Result Approval済み
  AND close state ∈ {committed, approved-no-op}

S99:
  final evidence commit必須
  AND external HEAD SHA/clean確認済み
  AND close state = committed
```

並列または前倒し実行を意図するのであれば、逆に「順番に実行」、PlantUML、4.5実装順序、S99前提をすべてその並列グラフへ改訂する必要がある。現状の両立しない二つのグラフを残すことはできない。

## Non-blocking Findings

なし。

上記blocker以外では、以下を確認した。

* S01/S02/S03/S90の各step内部は、orchestrator evidence統合、fresh review、actual commitまたは限定的`approved-no-op`、clean確認、close state、Result Approvalの順へ修正されている。S90ではtest側とdocs側の二段階reviewもこの順序に組み込まれている。
* S99はpre-commit判断を`final evidence commit authorization`と明記し、最終Result Approvalとは区別している。final commit後にHEAD SHAとcleanを外部証跡だけへ記録し、`committed` close state確認後にのみ最終Result Approvalを与える。
* S99はfinal report/review evidence commitを必須とし、過去stepの未commit実装を救済するcatch-up commitにしていない。これはworkflowのfinal commit境界とも一致する。
* exact pytest nodes、repository外temporary build、custom prune、wheel/sdist/installed resource inventory、Ruff check/formatの同一path list、Mypy、`git diff --check`は具体化されている。
* provider/docs/testの所有権、Issue 345/346の禁止境界、per-Issue PR/merge/finish禁止、human-only mergeは維持されている。

## Closure Review

| Finding                                                   | 状態                              | 再確認結果                                                                                                                                                                                                   |
| --------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B-001 — generic unchanged-byte exact-copy                 | **CLOSED**                      | `TC-344-002B`がCRLFを含むunchanged UTF-8のpath-agnostic exact-copy、placeholder render、README専用分岐禁止を固定し、3つのexact test nodeを持つ。現在のscaffolderはUTF-8を常にrender/writeするため、Redの検出対象も実在する。                           |
| B-002 — distribution/static exact execution               | **CLOSED**                      | custom `build_py` pre/post-prune、repository外temporary build、wheel/sdist/installed inventory、byte parity、stale nested README removalを2 exact pytest nodesへ割り当て、static commandもexact pathで固定している。         |
| B-003 — executable schema / S90/S99 contracts / ownership | **CLOSED**                      | 全implementation stepにbehavior slice、planned contract、delegation contract、test cards、step closure、report destination、amendment triggerがある。canonical READMEはS01-owned、S90 read-only referenceで統一されている。    |
| B-004 — S99 SHA self-reference                            | **CLOSED**                      | report ledger、commit scope、external evidence destinationをfinal commit前に確定し、実SHA/cleanはexternal-only。EVD-009はreviews、EVD-010はhandoffのまま維持されている。                                                          |
| B-005 — S90 role separation                               | **CLOSED**                      | `dev-coder`がexact Python assertionのみを作りfresh `code-reviewer`が確認した後、`doc-writer`がprovider docs 4件のみを変更しfresh `spec-reviewer`が確認する。cross-role editingも禁止されている。                                            |
| B-005-R1 — canonical report single writer                 | **CLOSED**                      | Workerはsummary/Ledger Noteを返し、main orchestratorだけがcanonical reportへ統合する。workflowのsingle-writer authorityとも一致する。                                                                                         |
| B-006 — exact two-node no-backfill coverage               | **CLOSED**                      | existing root/Initiative/Epic/Issueに対し、existing init/update、validate、sync、active switching、Artifact、ADR、future childを列挙し、entry inventory、bytes、names、mtime、ancestor/sibling不変をexact 2 pytest nodesで閉じる。 |
| B-007 — Ruff check/format path list                       | **CLOSED**                      | Ruff checkとformatが同一path listを使用し、双方に`tests/cli_runtime/test_new.py`を含む。test cardは`git diff --name-only`との照合も要求している。                                                                                    |
| B-008 — commit/clean/Result Approval/next-step admission  | **PARTIALLY CLOSED / BLOCKING** | step内のcommit順序とS99のfinal authorization境界は修正済み。ただし、global順序、dependency表、gateのnext-step admission、および`approved-no-op` predecessorのS99入場条件が一致していない。                                                        |
| Closure Index / test cards                                | **CLOSED**                      | 全required rowにspec link、owner、observable state、locked expectation、bug class、evidence level、closure evidenceがあり、各stepに具体cardとclosure contractがある。                                                        |
| Exact command/source executability                        | **CLOSED — static assessment**  | custom build seam、local wheelhouse helper、test harness、current broad README exclusionなど、計画が修正・再利用するsource面は指定HEADに存在する。実行結果自体は未検証。                                                                      |
| Issue 345/346・human-only boundary                         | **CLOSED**                      | Generic importはIssue 345、candidate consumer/dogfood/full regression/PR deliveryはIssue 346に残し、Issue 344はhandoffで停止する。Issue 346 dependency edgeも実在する。                                                     |

## Recommendation

**現HEADのplan promotionおよびimplementation startを承認しない。**

必要なamendmentはplan/reportに限定できる。

1. Section 4.6、S01/S02/S03/S90の`depends on`、`unblocks`、各step gateの最終項目を、宣言済みの`S01 → S02 → S03 → S90 → S99`へ完全一致させる。
2. S99のpredecessor条件を、`Result Approval済み`かつclose stateが`committed | approved-no-op`であることへ明文化する。S99自身は現行どおりmandatory final commit、external SHA/clean確認、`committed` close stateで閉じる。
3. `report.md`のEAL-022とSpec Authoring Gateへ修正内容を反映し、assurance source bindingを更新する。
4. 修正後の新しいexact HEADに対してfresh GitHub plan reviewとfresh `spec-reviewer` reviewを実施する。

この修正が実行順とclose-state表現だけに留まる限り、requirement/design phaseへ戻る必要はない。

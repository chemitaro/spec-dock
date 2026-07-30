# Issue 344 Final Plan Review

## Source Verification

Connected GitHub で `chemitaro/spec-dock` を参照し、最終照合時点でも次を確認した。

| 項目                      | 確認結果                                       |
| ----------------------- | ------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                      |
| Branch                  | `iss-00344-workbench-shell-scaffolding`    |
| 指定 HEAD                 | `b638bbb2ecae893791259304fce0546704b89e6d` |
| GitHub compare          | `status=identical`                         |
| Ahead / Behind          | `0 / 0`                                    |
| Branch と指定 SHA の差分      | `total_commits=0`                          |
| Default branch fallback | 使用していない                                    |
| 全ファイル参照                 | 指定 SHA を `ref` として固定                       |

主要な正本ファイルも同一 commit から取得した。

| 対象                                  | Blob SHA                                   |
| ----------------------------------- | ------------------------------------------ |
| Issue `requirement.md`              | `d28e39489e32a42b7438cb3fa763abeb857cd7ff` |
| Issue `design.md`                   | `fc0d6060417472890ca2d01250d6fef7c8485355` |
| Issue `plan.md`                     | `f862fa9406b5d9b387b6f910e3c00cb683c3735d` |
| Issue `report.md`                   | `ae75b7e6f7bca1c733ca0f37e897d439ea9d0f3a` |
| `workflow_issue.md`                 | `63751788f5b9e5cd358bbd1c4113aa9bd8a808f4` |
| `authoring/issue-plan.md`           | `afbd4468fbc8f5c2956be9c5fb75189a8cecad97` |
| Parent Epic requirement/design/plan | `4c8fd0…` / `fbd698…` / `b65568…`          |

関連実装面についても、現在の generic scaffolder が UTF-8 file を常に text rewrite していること、`setup.py` に custom `build_py`、stale fixture seed、pre-prune snapshot seam が存在すること、既存 `TestInitUpdate` に repository 外 temporary build と local wheelhouse を使う build helper が存在すること、`tests/cli_runtime/test_new.py` に `TestCliNew` runtime harness が存在することを確認した。したがって、計画された exact-copy、distribution、no-backfill test の配置先自体は実在し、実装可能である。

本レビューは read-only の仕様・計画レビューであり、pytest、Ruff、Mypy、build、Git mutation は実行していない。添付の `設計判断と提案.txt` は別テーマの例外・Failure 設計資料であり、Issue 344 の GitHub 正本または補助証跡ではないため判定根拠から除外した。

## Verdict

**FAIL**

指定されていた既往 finding の実質的な修正内容はすべて閉じている。しかし、`S01`、`S02`、`S03`、`S90` の各 milestone gate が、repository workflow の `Step / Milestone Result Approval` 定義と逆順になっており、commit・post-commit clean・次 step admission を実行者が補完判断しなければならない。

これは plan の実行順と milestone isolation に関する structural blocker である。したがって、現 commit を implementation-ready として昇格できない。

## Blocking Findings

### B-008 — Step / Milestone Result Approval が commit と post-commit clean より前に置かれている

`workflow_issue.md` は Standard plan について、次を明示している。

* milestone 完了時には commit candidate を使用する。
* commit 後に `git status --short` 等で次 milestone へ持ち越す変更がないことを確認する。
* closure unit は `committed` または正当な `approved-no-op` で閉じる。
* `Step / Milestone Result Approval` は、closure contract、required verification、fresh reviewer pass、commit candidate または approved-no-op、post-commit clean check がすべて閉じた状態である。
* 次 step の implementation、review、commit を開始できるのは、その Result Approval 後だけである。

現在の plan は、各 gate で先に `main orchestrator` が step result を承認し、その後に単に「commit候補」を列挙している。

* `S01`: step result approval が第4項、commit候補が第5項であり、actual commit、`committed` close state、post-commit clean check がない。
* `S02`: 同じく approval が先、commit候補が後で、post-commit clean check がない。
* `S03`: 同じ順序であり、distribution commit 後の clean admission がない。
* `S90`: test contract review、docs review、orchestrator approval の後に commit候補が置かれ、commit/no-op close state と clean check がない。

一方、`S99` は `S01`〜`S90` の **committed result** を前提にする。 現在の各 predecessor gate には、その committed result を成立させる明示的な遷移がない。

このままでは実行者が次を判断する必要がある。

1. 「commit候補」は actual commit の実行命令なのか、単なる推奨 message なのか。
2. commit は step result approval の前後どちらで行うのか。
3. `approved-no-op` と `committed` のどちらで close したかをいつ確定するのか。
4. post-commit clean をいつ実行し、何をもって次 step を開始可能とするのか。
5. approval 済みだが dirty または uncommitted の状態で次 step へ進んでよいのか。

これは wording 上の軽微な不足ではなく、review scope、commit scope、milestone isolation、stale evidence 防止に影響する。

必要な修正は、`S01`、`S02`、`S03`、`S90` の各 step gate を少なくとも次の順序へ固定することである。

1. Worker output と Red/Green/refactor evidence を main orchestrator が検証し、canonical `report.md` へ統合する。
2. Required fresh reviewer を `passed` にする。
3. 対象 milestone の actual commit を作成する。または、差分が本当にない場合だけ、所定の evidence を持つ `approved-no-op` を確定する。
4. commit 後に `git status --short` を実行し、意図しない staged/unstaged change がないことを確認する。
5. milestone close state を `committed` または `approved-no-op` として確定する。
6. main orchestrator が `Step / Milestone Result Approval` を与える。
7. この approval 後にだけ次 step を開始する。

`S99` の report-before-final-commit と external-only post-commit SHA/clean evidence は変更してはならない。ただし、現在の final commit 前の「S99 result approval」は、最終 closure と混同しないよう `final evidence commit authorization` 等の pre-commit approval と明示し、S99 の最終 close は外部 SHA/clean evidence確認後であることを固定すべきである。これにより、`report.md` の post-commit 編集や自己参照 commit loop を再導入せずに Result Approval の意味を一意にできる。

## Non-blocking Findings

なし。

`plan.md` と `report.md` がまだ `draft` であり、plan review / fresh `spec-reviewer` の checklist が未チェックであることは、現在が plan promotion 前であるため正常であり、別 finding とはしない。

## Closure Review

既往 B-ID は review round ごとに一部再利用されているため、`report.md` の EAL-015〜EAL-021 に記録された実際の correction content を基準に再照合した。

| 対象                                                                | 状態               | 再確認結果                                                                                                                                                                                                                                                         |
| ----------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B-001: generic unchanged-byte exact-copy                          | **CLOSED**       | `TC-344-002B` が unchanged CRLF UTF-8 exact-copy、placeholder render、path-agnostic behavior を固定し、3つの exact test node と Green sequence がある。README 専用分岐は禁止されている。                                                                                                  |
| B-002: distribution/static exact execution                        | **CLOSED**       | custom `build_py` pre/post-prune、repository 外 temporary build、wheel/sdist/installed inventory、bytes、stale nested README removal が2つの exact pytest nodeに割り当てられている。                                                                                             |
| B-003: executable step schema、S90/S99 planned contracts、ownership | **CLOSED**       | 各 step に behavior slice、planned contract、delegation contract、test card、step closure、report destination、amendment trigger がある。4 canonical Workbench README は S01-owned、S90 read-only reference で一貫している。                                                        |
| B-004: S99 commit-SHA self-reference                              | **CLOSED**       | report ledger、commit scope、external destination を final commit 前に確定し、commit 後の HEAD SHA / clean result は final response、Issue 346 handoff、または Issue comment のみに記録する。EVD-009 は reviews、EVD-010 は handoff のままである。                                               |
| B-005: S90 role/reviewer separation                               | **CLOSED**       | `dev-coder` が exact Python assertion のみを作成し fresh `code-reviewer` が確認、その後 `doc-writer` がprovider docs 4件のみを変更し fresh `spec-reviewer` が確認する。cross-role edit も明示禁止されている。                                                                                        |
| B-005-R1: canonical report single writer                          | **CLOSED**       | S01/S02/S03/S90 のworkerは EVD転記用summaryを返すだけであり、main orchestrator が検証後に canonical `report.md` へ統合する。                                                                                                                                                           |
| B-006: no-backfill exact trigger coverage                         | **CLOSED**       | `TC-344-005` と `tc-s01-002` は existing root / Initiative / Epic / Issue のsnapshotに対し、existing init/update、validate、sync、active switching、Artifact作成、ADR作成、future child作成を列挙する。entry inventory、bytes、names、mtime、ancestor/sibling不変を exact 2 pytest nodesで閉じる。 |
| B-007: Ruff check/format exact path list                          | **CLOSED**       | Ruff check と Ruff format は同一のexact path listを持ち、その両方に `tests/cli_runtime/test_new.py` が含まれる。test cardでも同一path listと `git diff --name-only` の照合を要求する。                                                                                                          |
| Vertical slicing                                                  | **CLOSED**       | S01 shell、S02 opacity/copy、S03 distribution、S90 docs、S99 final gate の依存順と integration checkpoint が明示されている。Active TDD は fresh init から filesystem / real Git observation までの thin vertical tracer で始まる。                                                         |
| Closure Index / test cards                                        | **CLOSED**       | 全required rowに spec link、owner、observable state、locked expectation、bug class、evidence level、closure evidenceがあり、各stepのcardは前提・操作・期待結果・失敗検出・検証方法・closure IDを持つ。                                                                                                |
| Issue 345 boundary                                                | **CLOSED**       | generic one-file Artifact import implementationは明示的に `iss-00345` へ残されている。                                                                                                                                                                                     |
| Issue 346 boundary                                                | **CLOSED**       | candidate wheel consumer E2E、dogfood projection、full regression、Epic-wide review、PR deliveryは `iss-00346` 所有である。Issue 344はfocused evidenceとdependency handoffで停止する。                                                                                           |
| Human-only delivery                                               | **CLOSED**       | Parent Epicはmergeをhuman-onlyとし、Issue planはper-Issue PR、merge、Issue finishを禁止してIssue 346 handoffで停止する。                                                                                                                                                         |
| Milestone commit/clean/result approval                            | **OPEN — B-008** | S01/S02/S03/S90 が result approval 後にcommit候補を置き、actual commit、post-commit clean、`committed \| approved-no-op` close state、次step admissionを明示していない。                                                                                                            |

## Recommendation

**現 commit の plan promotion と implementation start を承認しない。**

必要な amendment は B-008 に限定できる。

1. `S01`、`S02`、`S03`、`S90` の step gate を、review pass → actual commitまたはapproved-no-op → post-commit clean → close state確定 → main-orchestrator Result Approval の順へ修正する。
2. 各 gate に「Result Approval 前は次 step の implementation / review / commit を開始しない」を明記する。
3. `S99` の external-only HEAD SHA / clean evidence と report-before-commit 境界はそのまま維持する。
4. `S99` final commit 前の orchestrator judgment は、最終 closure ではなく commit authorization であることを明示する。
5. `Final Quality Gate` または Final Exit に、S01/S02/S03/S90 が `committed` または正当な `approved-no-op` かつ post-commit clean で閉じていることを追加する。
6. 修正後の exact new HEAD に対して fresh plan review と fresh `spec-reviewer` reviewを行う。

B-008 の修正が既存の locked expectations、test cards、S90 ownership、S99 external evidence boundary、Issue 345/346 ownershipを変更しない限り、requirement/design phaseへ戻る必要はない。

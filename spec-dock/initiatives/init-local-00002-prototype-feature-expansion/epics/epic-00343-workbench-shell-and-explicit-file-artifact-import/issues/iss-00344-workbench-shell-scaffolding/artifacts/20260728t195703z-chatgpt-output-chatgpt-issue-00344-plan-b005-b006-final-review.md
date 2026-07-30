# Issue 344 Final Plan Review

## Source Verification

| 項目                            | 確認結果                                                                                                                                                                                                 |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository                    | `chemitaro/spec-dock`                                                                                                                                                                                |
| Branch                        | `iss-00344-workbench-shell-scaffolding`                                                                                                                                                              |
| 指定 commit                     | `fc74ec7bef95a32fe276387594f4a3b27610331d`                                                                                                                                                           |
| Branch / commit 関係            | GitHub connector の比較結果は `identical`、`ahead_by=0`、`behind_by=0`。指定 commit が branch HEAD であることを確認した。                                                                                                   |
| Commit 内容                     | `docs(iss-00344): 実装計画の最終指摘を反映`。B-005/B-006 の反映を目的とする commit である。                                                                                                                                    |
| Issue 文書                      | exact commit の `requirement.md`、`design.md`、`plan.md`、`report.md`、`.assurance.json` を確認した。                                                                                                           |
| Parent Epic                   | `epic-00343` の `requirement.md`、`design.md`、`plan.md` を確認した。                                                                                                                                         |
| Workflow / authoring contract | `workflow_issue.md`、`docs/authoring/issue-plan.md`、`docs/phase_plan_issue.md` を確認した。                                                                                                                 |
| Source / tests                | `setup.py`、`pyproject.toml`、`template_scaffolder.py`、`tests/unit/infra/test_init_update.py`、`tests/cli_runtime/test_new.py` などの現行 seam を確認した。現行 `setup.py` には `super().run()` 後の custom prune が実在する。 |
| 実行有無                          | read-only review。計画された将来のテスト、build、lint、reviewer gate は実行していない。                                                                                                                                      |

指定外の添付 `設計判断と提案.txt` は例外 taxonomy に関する別件資料であり、Issue 344 の判定根拠には使用していない。

## Verdict

**FAIL**

B-004 と B-006 の主要修正、および B-005 の test/docs 分離そのものは反映されている。しかし、次の二点が execution-ready contract を妨げる。

1. S90 を含む delegation contract が delegated worker に canonical `report.md` の変更を許可しており、`doc-writer changes only provider docs` と canonical-doc single-writer policy の双方に反する。
2. required static-quality gate の exact command が、S01 で変更すると明記された `tests/cli_runtime/test_new.py` を Ruff / format 対象から漏らしている。

したがって、現 commit にはまだ、実行者が plan を補正または上位 workflow を優先解釈しなければならない箇所が残っている。

## Blocking Findings

### B-005-R1 — S90 の role split は成立したが、canonical report ownership が未解決

**Finding**

S90 は次の本体作業については適切に分離されている。

* `dev-coder` が exact Python semantic assertion を追加する。
* fresh `code-reviewer` が assertion をレビューする。
* `doc-writer` が provider docs 4件を変更する。
* fresh `spec-reviewer` が docs/spec alignment をレビューする。

しかし同じ delegation contract は、`dev-coder` と `doc-writer` の両方に Issue `report.md` を allowed path として許可している。さらに step gate は、各 worker 自身が Red、docs inspection、delegation evidence、closure delta を report に記録する順序になっている。

これは次の authoritative workflow contract と矛盾する。

* canonical `requirement.md`、`design.md`、`plan.md`、`report.md` の single-writer authority は main orchestrator に残る。
* delegated worker は evidence と `Ledger Note` または no-decision declaration を返す。
* orchestrator が worker output を検証し、canonical report に統合する。

同じ問題は、S02 と S03 の `dev-coder` allowed paths にも Issue report が含まれているため、S90 だけに限定されない。

**Impact**

現状のままでは、実行時に次のいずれかを選ぶ必要がある。

* plan に従って worker に canonical report を編集させる。
* workflow を優先し、worker の allowed paths と step gate を実行時に読み替える。
* report 更新用の orchestrator substep を非明示的に挿入する。

これは ownership と evidence adoption に関する material governance interpretation であり、`doc-writer changes only provider docs` という今回の明示的な確認条件も満たさない。

**Required correction**

* S02、S03、S90 の delegated-worker allowed paths から Issue `report.md` を除外する。
* worker の `output required` は、changed files、verification result、unresolved risk、EVD 転記用 summary、`Ledger Note` または no-decision declaration に限定する。
* 各 worker の結果を受けた main orchestrator が、reviewer gate より前に canonical `report.md` を更新する、と step gate に明記する。
* S90 の本体順序は変更しない。

  1. `dev-coder` が exact assertion のみを作成して Red evidence を返す。
  2. orchestrator が report を更新する。
  3. fresh `code-reviewer`。
  4. `doc-writer` が provider docs 4件のみを変更して Green evidence を返す。
  5. orchestrator が report を更新する。
  6. fresh `spec-reviewer`。
  7. orchestrator approval と commit。

### B-007 — Required static-quality exact command が既知の変更対象を漏らしている

**Finding**

S01 は `tests/cli_runtime/test_new.py` を明示的な変更面とし、次の新規 exact node を追加する計画である。

`tests/cli_runtime/test_new.py::TestCliNew::test_workbench_no_backfill_preserves_existing_scopes_across_all_triggers`

この node は S01 の Red seed、Gate、TC-344-005 closure のすべてに組み込まれている。

一方、M3/S03 の exact Ruff check と Ruff format command は `tests/cli_runtime/test_new.py` を列挙していない。しかも `tc-s03-003` は「S01〜S03 の changed Python/test paths」を対象とし、「未対象 changed Python path がない」ことを close condition にしている。

S99 は M3 の static commands をそのまま final gate として再利用するため、この漏れは S99 でも解消されない。

**Impact**

計画どおり `test_new.py` を変更すると、次の二つを同時には満たせない。

* 記載された exact Ruff / format command を変更せず実行する。
* 全 changed Python/test path が static gate の対象であると証明する。

実行者は command list を独自に拡張するか、既知の変更ファイルを lint/format gate の対象外にする必要がある。required static-quality closure の exact command defect であるため、execution-ready と判定できない。

**Required correction**

M3/S03 と S99 が参照する次の両 command に、`tests/cli_runtime/test_new.py` を追加する。

```bash
uv run ruff check ... tests/cli_runtime/test_new.py
uv run ruff format --check ... tests/cli_runtime/test_new.py
```

併せて `tc-s03-003` の exact path list と final static gate が同一であることを明記する。現行方針どおり Mypy を production source のみに限定するなら、Mypy への追加は不要である。

## Non-blocking Findings

追加の non-blocking finding はない。

`report.md` の plan gate が現在も `failed (ChatGPT B-005/B-006; fixes applied)`、`.assurance.json` が `provisional` であることは、fresh re-review 待ちの lifecycle state として妥当であり、独立した plan defect ではない。

## Closure Review

| Review area                         | Result                | Assessment                                                                                                                                                                                                                                   |
| ----------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact source verification           | **PASS**              | branch HEAD と指定 commit は connector 上で identical。                                                                                                                                                                                             |
| B-004 S99 ordering                  | **PASS**              | final report ledger、commit scope、external destination、ready/blocked を commit 前に固定し、commit 後の SHA/clean は外部証跡だけに置く。final commit 後の report edit も禁止されている。                                                                                      |
| EVD-009 identity                    | **PASS**              | reviews の finding、採否、fix commit、fresh verdict のままであり、post-commit SHA 保存先へ転用されていない。                                                                                                                                                           |
| EVD-010 identity                    | **PASS**              | dependency edge、deferred gates、delivery owner の handoff evidence のままである。                                                                                                                                                                     |
| B-005 test/docs role split          | **PASS with blocker** | test と docs の worker/reviewer 分離は正しい。ただし canonical report の worker write permission が ownership contract を破る。                                                                                                                                |
| B-006 / TC-344-005 trigger coverage | **PASS**              | existing init/update、validate、sync、active switching、Artifact、ADR、future child が明記され、existing root/Initiative/Epic/Issue の inventory、bytes、names、mtime と ancestor/sibling preservation を exact 2 nodes で閉じる。要求された no-backfill contract と一致する。 |
| Current test seam feasibility       | **PASS**              | `TestCliNew` には linked hierarchy、active switching、Artifact/ADR 作成の既存 seam があり、計画された統合 regression の配置先は妥当である。                                                                                                                                 |
| Vertical slices / dependencies      | **PASS**              | S01 shell、S02 opacity/copy、S03 distribution、S90 docs、S99 final gate が provider-first の依存順になっている。                                                                                                                                             |
| Step-local contracts / test cards   | **PASS with blocker** | behavior、depends/unblocks、allowed/forbidden paths、Red/Green、stop condition、closure、reviewer focus は具体的。ただし report ownership と static exact-command 漏れが残る。                                                                                    |
| Distribution/build contract         | **PASS**              | design と plan は active custom `build_py` prune、exact five-path preservation、allowlist 外 stale nested README removal、source/wheel/sdist/installed comparisonを一貫して扱う。                                                                          |
| Human-only delivery                 | **PASS**              | Issue 344 は PR/merge/finish を行わず Issue 346 handoff で停止し、親 Epic は Issue 346 の final delivery 後も human merge 前で停止する。                                                                                                                           |
| Execution without interpretation    | **FAIL**              | canonical report writer と exact static path listについて、実行者による補正が必要。                                                                                                                                                                            |

## Recommendation

commit `fc74ec7bef95a32fe276387594f4a3b27610331d` の plan を execution-ready として promoteしない。

次の二点だけを bounded plan correction として適用する。

1. delegated worker から canonical `report.md` の write permission を除去し、worker evidence の canonical report 統合を main orchestrator の明示的な step に戻す。
2. M3/S99 の Ruff check と Ruff format exact path listへ `tests/cli_runtime/test_new.py` を追加する。

B-004 の final-commit/external-evidence 境界、EVD-009/EVD-010 の意味、S90 の test→code review→docs→spec review 順序、および B-006 の exact two-node no-backfill evidence は変更しない。

修正 commit で Evidence Adoption Ledger、Spec Authoring Gate、assurance source binding を更新した後、fresh final plan review と fresh `spec-reviewer` plan reviewを再実行する。

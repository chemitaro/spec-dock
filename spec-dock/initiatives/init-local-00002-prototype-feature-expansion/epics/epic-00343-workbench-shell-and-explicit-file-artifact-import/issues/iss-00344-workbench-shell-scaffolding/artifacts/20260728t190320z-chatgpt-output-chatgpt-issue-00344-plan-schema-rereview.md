# Issue 344 Plan Schema Re-review

## Verdict

**FAIL**

GitHub app で `chemitaro/spec-dock` の branch `iss-00344-workbench-shell-scaffolding` を検査し、指定 commit `33e0dde15eeea0a7458bde6e511e03f4d997a7c8` を開いた。branch と commit の比較結果は identical だった。対象 commit は、前回 `spec-reviewer` の P1/P2 指摘を反映したものとして、S01/S02/S03/S90/S99 の delegation、test card、closure、gate、fresh-init tracer、Closure Index、scaffolder test path を追加している。

多くの修正は正しく反映されているが、**実行可能 step schema に関する blocking finding が3件残っている**。現状の `plan.md` は execution-ready へ昇格できない。

## Findings

### B-001 — S90 と S99 に step-local の behavior slice / planned contract がない

repository の Issue-plan authoring contract は、各 implementation step に次を要求している。

* behavior goal
* planned contract

  * scope
  * test obligation
  * red または代替 evidence
  * green verification
  * refactor guardrail
  * amendment trigger
* delegation contract
* 具体テストケース
* step closure contract
* report evidence destination
* step gate

さらに phase checklist は、各 step の `depends on`、`unblocks`、`target files` を要求している。

現行 plan では、明示的な `behavior slice execution` と `Planned contract` があるのは S01、S02、S03 だけである。S01 では `depends on`、`unblocks`、`target files` に続いて planned contract が置かれている。 S02 と S03 も同形である。

一方、S90 は概要から直接 `delegation contract` へ進み、S99 も final-gate の概要から直接 `delegation contract` へ進んでいる。どちらにも step-local な `behavior slice execution`、`Planned contract`、`depends on`、`unblocks`、`target files`、integration checkpoint、amendment trigger がない。

全体表には S90/S99 の依存関係があり、delegation の `allowed paths` から対象パスを推測することもできるが、これは repository schema が要求する **step-local executable contract** の代替にならない。実行者が複数節を合成して scope、順序、停止条件を再判断する必要が残る。

**必要な訂正**

S90 と S99 のそれぞれに、少なくとも次を追加する必要がある。

```text
#### S90/S99 behavior slice execution
- depends on
- unblocks
- target files
- integration checkpoint
- HITL / AFK annotation

Planned contract:
- scope
- test obligation
- red / covered-existing / inspect-only evidence
- green verification
- refactor guardrail
- report evidence destination
- amendment trigger
```

S99 は review-only gate であっても、`inspect-only` または aggregate-verification step として同じ schema を満たす必要がある。

---

### B-002 — S99 に report-before-commit / reviewer / result approval / commit-or-no-op の step gate がない

S01、S02、S03、S90 には、次の順序を明示する `step gate` がある。

1. report を commit 前に更新
2. fresh reviewer finding を閉じる
3. main orchestrator が step result を承認
4. commit 候補または approved-no-op

たとえば S90 はこの順序を明示している。

S99 は `step closure contract` の末尾に「final report/review evidence commit」という commit 候補を記載しているだけで、その直後に Verification Ladder へ移っている。明示的な `S99 step gate`、main orchestrator の result approval、approved-no-op の可否、post-commit clean check がない。

これは repository execution contract と一致しない。正本は、各 step を次の順序で閉じるよう要求している。

```text
step closure
→ delegation
→ bounded implementation / verification
→ report draft update
→ reviewer gate
→ fix / re-review
→ step or milestone result approval
→ commit / approved-no-op
→ clean check
```

また closure state は `committed` または正当な `approved-no-op` でなければならず、次 step へ進めるのは Result Approval 後だけである。

S99 については、三者 final review の後に final report ledger を更新し、final commit を作成する順序も workflow に固定されている。

**必要な訂正**

明示的な `S99 step gate` を追加し、少なくとも次を固定する必要がある。

1. aggregate verification と closure evidence を `report.md` に記録する。
2. fresh `qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer` がすべて `passed` になるまで修正・再レビューする。
3. main orchestrator が S99 result を承認する。
4. final report/review evidence commit を作成する。
5. S99 で approved-no-op を認めないなら、その旨を明記する。認めるなら、差分なし条件と必要 evidence を明記する。
6. post-commit clean check と、commit hash の external evidence destination を明記する。

---

### B-003 — provider docs の step ownership が S02 と S90 の間で矛盾している

S02 の delegation contract は、許可パスを opacity/copy tests と Issue report に限定し、**docs を forbidden changes** としている。

S90 は `doc-writer` が provider docs 4件と `templates/README.md` を更新・検証する step として定義されている。

しかし Section 15 の impact resolution table は、provider docs 4件を「**S02で新operator contractへ更新**」としている。 また、Execution Overview の図にも stale な `M2 opacity / worktree / docs` が残っている一方、現在の S02 overview と strategy は docs を S90 へ分離している。

さらに S90 冒頭の「Workbench README templates: update required」は、S90 の allowed paths に4つの canonical `.workbench/README.md` が含まれていないこと、およびそれらを S01 が所有することと曖昧に競合する。S90 の実際の allowed paths は provider docs 3件、`templates/README.md`、docs assertion、Issue report だけである。

これは単なる表記差ではなく、実行者に次の相反する指示を与える。

* S02 で docs を変更する。
* S02 では docs を変更してはならない。
* S90 で docs を変更する。
* S90 で canonical Workbench README も変更するように読めるが、パスは許可されていない。

**必要な訂正**

* provider docs 4件の更新 owner を S90 に統一する。
* PlantUML の M2 から docs を除く。
* 4つの canonical Workbench README は S01-owned implementation、S90 では read-only parity/reference と明記する。
* S90 が実際に変更する `templates/README.md` と、照合だけ行う4つの `.workbench/README.md` を分ける。
* canonical README wording の変更が必要な場合は、既存 design contractどおり design amendment と fresh review に戻す。

---

### 確認済みで、今回の blocking finding ではない項目

| 確認項目                                 | 判定                                                                                                                                                                                                              |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Closure Index                        | **適合**。全行に Required、Spec link、Owner、Observable input/state、Locked expectation、Bug class、Evidence level、Closure evidence がある。                                                                                    |
| delegation contract                  | **適合**。S01/S02/S03/S90/S99 の全てに9項目がある。                                                                                                                                                                          |
| concrete test cards                  | **適合**。全stepにカード型ケースがあり、前提、操作、期待結果、失敗検出、検証方法、関連 closure id がある。                                                                                                                                                 |
| step closure contract                | **適合**。5 stepすべてに存在する。ただし S99 の後続 step gate が欠落している。                                                                                                                                                            |
| Active TDD                           | **適合**。fresh temporary Git repositoryで current provider の fresh initを実行し、生成 bytes、`git check-ignore`、`git status --short` まで観測する vertical tracerから始まる。                                                          |
| 新規 scaffolder test path              | **適合**。`tests/unit/infra/test_runtime_template_scaffolder.py` が許可変更面と S01 delegation に含まれる。                                                                                                                     |
| generic exact-copy                   | **適合**。unchanged CRLF UTF-8 の exact copy、placeholder-containing template の従来 render、path-agnostic guardrailが concrete tests と planned contractに残っている。現行 scaffolder が全UTF-8 textを `write_text` しているため、検出対象も実在する。 |
| distribution / static exact commands | **適合**。custom `build_py`、pre-prune snapshot、wheel/sdist/installed resource、exact five-path inventory、2つのexact pytest nodes、scoped Ruff/format/Mypy/`git diff --check` が維持されている。                                 |
| packaging Red の根拠                    | **適合**。現行 `setup.py` と `pyproject.toml` には broad nested README prune/exclude が実在し、S03 の expected Red と一致する。                                                                                                     |
| sibling boundary                     | **適合**。Issue 344 は shell/copy focused evidence、Issue 346 は candidate-wheel consumer、dogfood、full regression、Epic-wide review、PR deliveryを所有する。                                                                  |

## Scope and consistency checked

次を exact commit 上で照合した。

* Issue `requirement.md`: `approved`。fresh/future shell、no-backfill、opacity、copy、exact distribution、docs境界。
* Issue `design.md`: `approved` / Standard。generic exact-copy、three-rule ignore、custom build prune、exact five-path contract。
* Issue `plan.md`: current draft、Closure Index、全step、final gate。
* Issue `report.md`: 前回 `spec-reviewer` FAIL の採用記録と、plan gate が fresh re-review待ちであること。
* `.assurance.json`: `authorized_profile=standard`。
* 親 Epic requirement/design/plan: Issue 344/345/346 の責務分割と dependency boundary。
* `authoring/issue-plan.md`、`phase_plan_issue.md`、`workflow_issue.md`: executable step、delegation、test card、closure、result approval、commit/no-op schema。
* provider/build seams:

  * `src/spec_dock/cli.py`
  * `template_scaffolder.py`
  * `setup.py`
  * `pyproject.toml`
  * provider `.gitignore`
* relevant tests:

  * `tests/unit/infra/test_init_update.py`
  * `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`
  * `tests/cli_runtime/test_runtime_new_doc_s09.py`
  * `tests/cli_runtime/test_workbench.py`

添付された `設計判断と提案.txt` は例外・failure taxonomy に関する別件の設計メモであり、Issue 344 の plan/schema 判定根拠には使用していない。

## Residual risks

* 本レビューではコマンドやテストを実行していない。exact commands の存在と計画上の接続を確認しただけで、実行成功は未検証である。
* 新規 `tests/unit/infra/test_runtime_template_scaffolder.py` は planned target であり、現 commit における実装済み test evidence ではない。
* `.assurance.json` は Standard profile を認可している一方、status は `provisional`、plan 自体は `draft`、report の plan gate は前回 FAIL のままである。これは現在の review phase と整合するが、promotion evidence にはならない。
* 親 Epic 文書は draft 状態であるため、本レビューでは Issue ownershipとの整合だけを確認し、親 Epic の最終 promotion は検証していない。
* provider/test 実装については、計画の Red 感度と変更 seam を確認したものであり、実装完了・回帰不在・distribution成立を示すものではない。

## Promotion decision

**Plan phase promotion は保留。実装開始不可。**

次の3点を修正し、同一 revision に対する fresh plan re-review が必要である。

1. S90/S99 に step-local `behavior slice execution` と full `Planned contract` を追加する。
2. S99 に report-before-commit、三者 reviewer pass、main orchestrator result approval、final commitまたは明示的 no-op policy、clean checkを含む `S99 step gate` を追加する。
3. docs/template ownershipを S90へ統一し、S02・PlantUML・Section 15・S90 allowed pathsの記述を一致させる。

現行 plan 自身も、ChatGPT review と fresh `spec-reviewer` review が PASSするまでは実装へ進まないと定めている。

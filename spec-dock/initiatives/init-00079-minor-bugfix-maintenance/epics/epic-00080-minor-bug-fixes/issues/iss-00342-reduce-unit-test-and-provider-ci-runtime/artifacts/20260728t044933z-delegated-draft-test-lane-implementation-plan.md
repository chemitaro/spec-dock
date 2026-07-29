---
種別: delegated planning evidence
ID: "20260728t044933z"
タイトル: "Delegated Draft Test Lane Implementation Plan"
状態: "draft"
作成者: "implementation-planner"
最終更新: "2026-07-28"
親: ["iss-00342"]
template: "blank"
authority: "raw"
created_by_role: implementation-planner
scope_id: iss-00342
source_paths:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
  - ".assurance.json"
  - "artifacts/20260728t041725z-delegated-draft-test-lane-architecture.md"
  - "artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md"
  - "artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md"
  - "artifacts/20260728t015759z-01-interview-full-regression-merge-gate-policy.md"
  - "spec-dock/templates/issue-profiles/standard/plan.md"
  - "spec-dock/docs/authoring/issue-plan.md"
  - "spec-dock/docs/phase_plan.md"
  - "spec-dock/docs/phase_plan_issue.md"
  - "spec-dock/docs/workflow_issue.md"
  - "pyproject.toml"
  - "Makefile"
  - ".github/workflows/provider-ci.yml"
  - "README.md"
  - "AGENTS.md"
  - "tests/unit/cli/test_cli_smoke.py"
  - "tests/unit/infra/test_init_update.py"
  - "tests/cli_runtime/harness.py"
intended_targets:
  - "plan.md"
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
specialist_status: usable
source_hashes:
  requirement.md: "3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097"
  design.md: "dcba55f97e3159525d4b707a71f09ac6c69d6b5e2ea777e1371fdf7748470811"
  plan.md: "50aecab18b17a67f25867c7ff398ce8b69136b1ca225949b4efa110ca52bd8db"
  report.md: "d18dbd2487618d68a03e1d78aadd3be4c85beeb2cad5f1351fc6c5c110272e53"
  .assurance.json: "572de6214ddd4054302b09d4c6e85df3db333d7301ea2c4b505e1eacebd1990e"
  delegated_architecture: "4ecf5a906b12a1a5469cff65086421eaae6138caafd3a148be77fc51090f0792"
  accepted_adr: "8f89d2e64824822d78606bce067aa68957db3263a68b44fd01ecf86dcb73de8e"
  research: "10cb4396962b4a396ff5aa1ef71015e466c5aa612c9eeb55105a50ffb2914f0d"
  interview: "e3c53cb67975c2ab99852c5454dcf662525e604ec7ce3e299ce20f38ba278dc5"
  standard_plan_template: "5ba854ef23abef52a5eb19a0a8121d477369eba42ac001c357e4bb9ec27fdd09"
  issue_plan_authoring: "bc6f633c47143d8acac7d3714198f3ce73b09c4f8e38c1d55d9365205c171909"
  phase_plan: "b3001b177d74d5edd517434935d5966f6256005d9be9cf6b3442024497c20994"
  phase_plan_issue: "4f75861ac245cdc6b282e0644109d976d5179da50cba49e9c696d1c8c22a2f2d"
  workflow_issue: "da3b4d9f244583a5b1aa805d8e752f89f87af633afee8970e73ce28e4241af55"
  pyproject.toml: "d6347e896a753079da2fcaf4b43e273baebe33fe5cba23b1d2599d2438bf523e"
  Makefile: "dbdb4868a682f1730f0f15523008e76bfbccf3541a0b8d2d22f3b310a37e206c"
  provider_ci_workflow: "1c5ae8807d9911ce1949d54e1ade906d685c230e4eca9670296bb8d7e73db36d"
  README.md: "f11d42d3b84127312b7ad88881b17e235e2ad9b6f4bff3efdf4db178c47adeab"
  AGENTS.md: "61ceb050bf9b1d5d1bf08cf677b695ef15a68c237883a97bf8fa2b7e0bb70ba5"
  cli_smoke_test: "211fdcf46485477dc075eaa9f1cbbbc17524c53fcf7c5b52ce1159a8d9df56b7"
  init_update_test: "2a581172839417dcac9040aed31e662661c8fc9bc412795018353cc7a26e8384"
  cli_runtime_harness: "74cdf88585eedc7949d1fc826baa4b9fe95957d6baf252f59195103e328762cd"
canonical_diff_guard:
  before:
    requirement.md: "3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097"
    design.md: "dcba55f97e3159525d4b707a71f09ac6c69d6b5e2ea777e1371fdf7748470811"
    plan.md: "50aecab18b17a67f25867c7ff398ce8b69136b1ca225949b4efa110ca52bd8db"
    report.md: "d18dbd2487618d68a03e1d78aadd3be4c85beeb2cad5f1351fc6c5c110272e53"
  after:
    requirement.md: "3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097"
    design.md: "dcba55f97e3159525d4b707a71f09ac6c69d6b5e2ea777e1371fdf7748470811"
    plan.md: "50aecab18b17a67f25867c7ff398ce8b69136b1ca225949b4efa110ca52bd8db"
    report.md: "d18dbd2487618d68a03e1d78aadd3be4c85beeb2cad5f1351fc6c5c110272e53"
---

# 20260728t044933z Delegated Draft Test Lane Implementation Plan

この文書は `iss-00342` の approved requirement / design を、main orchestrator が canonical `plan.md` へ統合するための Standard / TDD planning evidence である。観測結果は canonical `report.md` へ main orchestrator が記録し、本artifactは採用、phase promotion、reviewer pass、implementation readiness、Issue完了を自己主張しない。

## 1. Plan Summary

### 1.1 成果

- bare/default pytestとPRの`provider-tests`をfast laneへ限定し、formal fullは`make test-provider-full`から`F ∪ H`を実行する。
- `Provider CI` / `provider-tests` identityを維持したPR fast workflowと、`main` push / `workflow_dispatch`専用の`Provider Full Regression` workflowを分ける。
- `schedule`を導入せず、provider-only workflowを`src/spec_dock/assets/install_root/**`やconsumer workspaceへshipしない。
- 全itemのexactly-one分類、required-fast 7 node、full collection completeness、event truth table、coverage weakening防止をRed-firstで固定する。
- 最終統合状態まで30〜40分のfullを繰り返さず、S06のfast/full 3 paired runsに3回のfinal full evidenceを統合する。

### 1.2 マイルストーン

| Milestone | Steps | 独立して成立する成果 | Gate |
|---|---|---|---|
| M0 Baseline lock | S00 | full node IDs、skip/xfail、known flaky、workflow/commandの変更前snapshot | baseline manifestとhashが再現可能 |
| M1 Local lane contract | S01-S02 | partial-safe classifier、global completeness、bare/fast/full command | focused tests + collect-only verifier |
| M2 CI routing | S03 | 2 workflow truth table、identity、non-shipping | deterministic workflow tests |
| M3 Contributor operation | S04 | commands、failure owner、rerun、rollbackのdocs整合 | docs/spec inspection |
| M4 Integrated local gate | S05-S06 | lint/fast Green、coverage delta、3 paired final measurement | focused/lint/fast + 3 paired runs |
| M5 External observation | S07 | fresh reviews、PR fast 3 run、human merge boundary、post-merge gate分離 | review pass + PR evidence |

### 1.3 Success / stop

- successは全closure IDがobserved evidenceへ結び付き、unexpected regression、unexplained node/skip/xfail/assertion delta、identity欠落、schedule、permission拡張、consumer shippingがない状態である。
- known flakyはlaneから除外、skip、xfailせず、baseline-known failureまたはobserved full failureとして他のregressionから分離する。
- full commandはS06の3回だけ実行する。S00-S05の集合検証は`--collect-only`とfocused testsを使う。

## 2. Requirement / Design Traceability

### 2.1 Spec-Locked Closure Index

| Closure ID | Spec link | Design | Locked expectation | Observable input/state | Evidence level | Owner |
|---|---|---|---|---|---|---|
| `CLOS-TL-AC-001` | AC-001 | DES-TL-001/003 | default、`tests/unit`、formal fastでH実行0 | selector別collection / execution | automated | S01/S02/S05 |
| `CLOS-TL-AC-002` | AC-002 | DES-TL-001/003 | formal full=`F ∪ H`、交差0、未分類0、H>0 | full/fast/heavy node ID集合 | automated | S01/S02/S06 |
| `CLOS-TL-AC-003` | AC-003 | DES-TL-004 | PRはexisting identityでlint+fastのみ | provider-ci workflow | automated + PR observation | S03/S07 |
| `CLOS-TL-AC-004` | AC-004 | DES-TL-005 | main pushでfull 1 job、PR full重複なし | full workflow event/job | automated + post-merge | S03/S07-PM |
| `CLOS-TL-AC-005` | AC-005 | DES-TL-003/005 | dispatch/local fullあり、scheduleなし | Make/docs/workflow | automated + inspect | S02-S04 |
| `CLOS-TL-AC-006` | AC-006 | DES-TL-002 | required-fast 7 nodeが存在しFで実行される | exact node IDs | focused automated | S01/S05 |
| `CLOS-TL-AC-007` | AC-007 | DES-TL-001/006 | node削除、skip/xfail増、assertion弱体化のunexplained delta 0 | before/after manifest/diff | automated + diff review | S00/S05/S06 |
| `CLOS-TL-AC-008` | AC-008 | DES-TL-006 | 3 pairすべてfast<full、PR 3 runすべて38.1m未満 | same-condition timings / PR runs | measured | S06/S07 |
| `CLOS-TL-AC-009` | AC-009 | DES-TL-004/005/006 | PR yes/no、non-main no/no、main no/yes、dispatch no/yes、schedule no/no | deterministic truth table | automated | S03 |
| `CLOS-TL-AC-010` | AC-010 | DES-TL-005/007 | failed runにSHA/test/log/rerun/ownerがある | docs + Actions run | inspect + post-merge | S04/S07-PM |
| `CLOS-TL-AC-011` | AC-011 | DES-TL-007 | PRをformal fullへ戻せ、manual full/evidenceを保持 | rollback diff/rehearsal | inspect + review | S04/S07 |
| `CLOS-TL-BH-001` | BH-001 | DES-TL-001/003 | opt-inなしはfast、failureはnonzero | bare pytest | automated | S01/S02 |
| `CLOS-TL-BH-002` | BH-002 | DES-TL-001/003 | opt-in fullはdefault除外をoverride | Make full collection | automated | S02/S06 |
| `CLOS-TL-BH-003` | BH-003 | DES-TL-004 | pull_requestはfastのみ | provider-ci workflow | automated | S03 |
| `CLOS-TL-BH-004` | BH-004 | DES-TL-005 | refs/heads/main pushはpost-merge full | full workflow | automated + observed | S03/S07-PM |
| `CLOS-TL-BH-005` | BH-005 | DES-TL-003/005 | local/dispatchが同じformal full contract | Make target invocation | automated | S02/S03 |
| `CLOS-TL-BH-006` | BH-006 | DES-TL-005 | schedule/cron entry 0 | both workflows | automated | S03 |
| `CLOS-TL-BH-007` | BH-007 | DES-TL-005/007 | full failureをredで可視化し遡及blockしない | workflow/docs/run | inspect + observed | S03/S04/S07-PM |
| `CLOS-TL-CON-001` | CON-001 | DES-TL-001..007 | accepted ADRのOption A/no-scheduleを変更しない | integrated diff | spec review | S07 |
| `CLOS-TL-CON-002` | CON-002 | DES-TL-004/005/006 | provider-only policy。consumer/provider assets不変 | forbidden tree + non-shipping tests | automated + diff | S03/S07 |
| `CLOS-TL-CON-003` | CON-003 | DES-TL-005 | scheduleを追加しない | workflow trigger inspection | automated | S03 |
| `CLOS-TL-CON-004` | CON-004 | DES-TL-001/002/006 | deletion/skip/xfail/assertion weakeningで高速化しない | diff + baseline delta | automated + review | S00/S05/S07 |

全`DES-TL-001`〜`DES-TL-007`は少なくとも1つのrequired closureに結び付く。closure rowの削除、locked expectation変更、required-fast inventory変更、truth table変更はcanonical plan amendmentとfresh `spec-reviewer` re-reviewを要する。

## 3. Milestones

### M0 Baseline lock

- S00でcurrent full collectionのnode ID、count、skip/xfail、Python/cache条件、known flakyをcharacterization evidenceとして固定する。
- full実行はしない。既存research/designの`C=2696`をcurrent collect-onlyでrefreshし、差分があればRed実装前に停止する。

### M1 Local lane contract

- S01でobservable selector behaviorをRed-firstにし、partial-safe classifierとrepo-root completeness verifierを最小Greenにする。
- S02でMake facadeの存在・selector overrideをRed-firstにし、workflowがraw marker expressionを複製しないsingle command surfaceを作る。

### M2 CI routing

- S03でexisting deterministic workflow testを先にRedにし、2 workflow、truth table、identity、provider-only non-shippingを一つのrouting sliceとしてGreenにする。

### M3 Contributor operation

- S04でREADME/AGENTSをdoc-writerへ委任し、default/fast/full、no schedule、full failure owner、rerun、rollbackを同じ語彙で整合させる。

### M4 Integrated local gate

- S05でfocused tests、`make lint`、`make test-provider-fast`、collect-only set verifier、before/after coverage deltaを確認する。
- S06でのみformal fullを3回実行し、同一checkout/Python/cache条件の3 paired measurementsを取る。

### M5 External observation

- S07でfresh QA/code/spec reviewを通し、PRの`provider-tests`を3 run観測する。mergeはhuman-only boundaryで停止する。
- human merge後のmain full observationは`S07-PM`として分離し、pre-merge reviewer/PR readinessの代替にしない。

## 4. Dependency-Derived Execution Order

```text
S00 baseline
  -> S01 classifier / pytest config
      -> S02 Make fast/full facade
          -> S03 PR/full workflows + deterministic routing/non-shipping
              -> S04 README/AGENTS operation
                  -> S05 focused/lint/fast integrated gate
                      -> S06 final paired fast/full batch
                          -> S07 QA/code/spec review + PR fast observation
                              -> [human-only merge]
                                  -> S07-PM main post-merge full observation
```

- classifierが集合意味論を所有し、pyprojectがdefault selector、Makeがstable facade、workflowがMakeを呼び、docsがそのcontractを説明するため、この順序にする。
- Issue dependency graph上のexternal blockerは0である。`deps check iss-00342`のlocal/cache observationは`ready=true, blockers=0`だったが、lifecycle authorityやimplementation readinessの主張には使わない。
- S01-S04のRed/Greenは一度に一つだけactiveにする。Red理由が想定外なら後続へ進まない。
- S05がGreenになるまでS06のfull batchを開始しない。S06後にsource/tests/workflows/docsを変更した場合、S05を再実行し、S06 batchをstaleとして扱う。full再計測はmain orchestratorがfresh plan/review判断を行うまで開始しない。

## 5. Issue / Step Slicing

### S00 Baseline full collection / skip / xfail / known flaky characterization

- behavior goal: 変更前の`C`、node IDs、skip/xfail、assertion-bearing target diff、Python/cache条件を固定し、既知flakyを他のregressionと区別する。
- delegated role: `dev-coder`（read-only characterization）。canonical `report.md`転記はmain orchestrator。
- allowed paths: writeなし。readは`tests/**`、`pyproject.toml`、`Makefile`、`.github/workflows/**`、Issue sources。
- forbidden paths: repository fileの変更すべて。特にtest deletion/skip/xfail/assertion変更、`src/spec_dock/**`、`spec-dock/**` consumer data、workflow mutation。
- Red / alternative: `characterization-first`。current collect-only set/countがapproved baseline `C=2696`から説明なく変わる、required-fast nodeが欠ける、known flaky以外のbaseline focused failureが出る場合はstop。
- minimal Green: node ID sorted manifest、count、skip/xfail inventory、Python version、cache condition、source SHAをworker outputへ返す。repoにmanifest fileは追加しない。
- focused checks:
  - `uv run pytest --collect-only -q -p no:cacheprovider`
  - required-fast 7 nodeのexact focused pytest（S01前のbaseline behavior確認）
  - `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state -q`
- stop / rollback: unexplained `C` delta、missing required-fast、known flaky以外のfailureで停止。writeなしのためrollback不要。
- report destination: `report.md`の実装セッションログ、Test Contract Closure、EVD-TL-001/002/008。
- step closure: `CLOS-TL-AC-006/007`、`CLOS-TL-CON-004`のpre-implementation evidenceが揃う。

#### 具体テストケース一覧

- `tc-s00-001` characterization: full node setを固定する
  - 前提: current checkoutとPython/cache条件を記録する。
  - 操作: repo-root collect-onlyを実行しnode IDsをsortする。
  - 期待結果: current `C`が再現でき、approved baselineとの差分を説明できる。
  - 失敗検出: selector実装前からcollection driftがある状態で誤ったbaselineを採ることを防ぐ。
  - 検証方法: collect-only output、SHA、countをworker evidenceとして返す。
  - 関連 closure id: `CLOS-TL-AC-007`

- `tc-s00-002` characterization: known flakyを隠さない
  - 前提: exact node `test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state`は既知flaky候補である。
  - 操作: exact nodeをfocused実行し、pass/failとlogをそのまま記録する。
  - 期待結果: baseline-known pass/failureとして別欄に記録し、skip/xfail/selector除外を追加しない。
  - 失敗検出: lane変更がflakyをfast/fullのどちらからも消す回帰を防ぐ。
  - 検証方法: exact pytest resultとS06 full collection membership。
  - 関連 closure id: `CLOS-TL-AC-007`、`CLOS-TL-CON-004`

### S01 Red-first partial-safe classifier / global completeness

- behavior goal: focused collectionを壊さず、collected subsetをexactly-one分類し、repo-root verifierだけがglobal completenessを保証する。
- delegated role: `dev-coder`。
- allowed paths: `tests/conftest.py`、`tests/unit/test_provider_test_lanes.py`、`pyproject.toml`。
- forbidden paths: 上記以外。特に既存test body/assertion、heavy file移動、skip/xfail、dependency追加、xdist、`src/spec_dock/**`、workflow/docs。
- Red expectation: classifier/config実装前に、partial collection、marker conflict、required-fast override、H>0/global set equality、default heavy 0の新規testsが契約欠落でfailする。既存regression Redは0。
- minimal Green:
  - `tests/conftest.py`が今回収集したitemだけを`fast`/`full_regression`へexactly-one分類する。
  - `pyproject.toml`がmarkers、`--strict-markers`、default `-m fast`を登録する。
  - global verifier/testが`F∩H=∅`、`F∪H=C`、`U=0`、`H>0`、required-fast 7 nodeをrepo-root collectionで検査する。
- focused checks:
  - `uv run pytest tests/unit/test_provider_test_lanes.py -q`
  - `uv run pytest tests/unit/cli/test_cli_smoke.py -q`
  - `uv run pytest --collect-only -q -m fast -p no:cacheprovider`
  - `uv run pytest --collect-only -q -m "fast or full_regression" -p no:cacheprovider`
- stop / rollback: focused subsetでmissing global node/H=0を理由にfail、explicit marker conflictを黙って解決、required-fast inventory変更が必要、既存nodeが消える場合はstop。rollbackはS01の3 pathだけをrevert候補にする。
- report destination: `report.md` Red/Green/Refactor Evidence、Step/Test Contract Closure、EVD-TL-001/002。
- step closure: `CLOS-TL-AC-001/002/006/007`、`CLOS-TL-BH-001/002`、`CLOS-TL-CON-004`。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: focused collectionはpartial-safe
  - 前提: CLI smoke 1 nodeだけ、またはheavy 0のsubsetを指定する。
  - 操作: pytest collection/executionを行う。
  - 期待結果: collected itemsだけがexactly-one分類され、global required-fast/H>0 checkは発火しない。
  - 失敗検出: global completenessをhookへ誤配置してfocused testを使用不能にする回帰を検出する。
  - 検証方法: `tests/unit/test_provider_test_lanes.py`のRed-first subprocess case。
  - 関連 closure id: `CLOS-TL-AC-001`、`CLOS-TL-BH-001`

- `tc-s01-002` invariant: repo-root集合は完全かつ排他的
  - 前提: repo-root full collectionとrequired-fast 7 node inventoryがある。
  - 操作: default/fast/heavy/formal-fullのnode ID集合を比較する。
  - 期待結果: `F∩H=∅`、`F∪H=C`、`U=0`、`H>0`、7 nodeがFに存在する。
  - 失敗検出: test omission、missing required-fast、selector outsideを検出する。
  - 検証方法: dedicated global verifier test。
  - 関連 closure id: `CLOS-TL-AC-002/006/007`

- `tc-s01-003` negative: marker conflictはfail-close
  - 前提: synthetic itemが両marker、required-fastが明示full、heavy non-exceptionが明示fastのいずれか。
  - 操作: collectionを行う。
  - 期待結果: collection errorでtest実行前に停止する。
  - 失敗検出:優先順位でconflictを黙殺する欠陥を検出する。
  - 検証方法: focused classifier contract test。
  - 関連 closure id: `CLOS-TL-AC-007`、`CLOS-TL-CON-004`

### S02 Red-first Make fast/full commands

- behavior goal: contributor/CIが同じstable Make facadeからfast/fullを選び、formal fullがdefault `-m fast`を明示overrideする。
- delegated role: `dev-coder`。
- allowed paths: `Makefile`、`tests/unit/test_provider_test_lanes.py`。
- forbidden paths: classifier semantics変更、workflow/docs、dependency追加、test weakening、`src/spec_dock/**`、consumer workspace。
- Red expectation: target不存在、wrong selector、formal fullがHを含まない、workflow用commandをraw selectorへ分散するケースが実装前にfailする。
- minimal Green: `.PHONY`へ`test-provider-fast`/`test-provider-full`を追加し、それぞれ`uv run pytest -m fast`、`uv run pytest -m "fast or full_regression"`だけを呼ぶ。
- focused checks:
  - `uv run pytest tests/unit/test_provider_test_lanes.py -q -k "make or command or selector"`
  - `make -n test-provider-fast`
  - `make -n test-provider-full`
  - collect-only set verifier。`make test-provider-full`本実行は禁止しS06へ送る。
- stop / rollback: full targetがHを含まない、fast targetがHを実行、別dependency/flagが必要、Make以外へraw selector duplicationが必要ならstop。S02 pathだけをrevert候補にする。
- report destination: `report.md` Red/Green/Refactor Evidence、Step/Test Contract Closure、EVD-TL-003。
- step closure: `CLOS-TL-AC-001/002/005`、`CLOS-TL-BH-001/002/005`。

#### 具体テストケース一覧

- `tc-s02-001` acceptance: fast/full targetのselector契約
  - 前提: pyproject defaultはfastである。
  - 操作: Make target commandをinspectし、selector別collectionを比較する。
  - 期待結果: fast=F、full=`F∪H`で、formal fullがdefault除外をoverrideする。
  - 失敗検出: full targetがfastだけを再実行する欠陥を検出する。
  - 検証方法: Red-first command contract test + `make -n` + collect-only verifier。
  - 関連 closure id: `CLOS-TL-AC-002`、`CLOS-TL-BH-002`

### S03 Red-first 2-workflow truth table / identity / non-shipping

- behavior goal: PR fastとmain/manual fullを2 workflowで分離し、identityとprovider-only boundaryをdeterministic testで固定する。
- delegated role: `dev-coder`。
- allowed paths: `.github/workflows/provider-ci.yml`、`.github/workflows/provider-full-regression.yml`、`tests/unit/infra/test_init_update.py`。
- forbidden paths: `.github/workflows/ci.yml`、workflow permissions/secrets、schedule、branch protection mutation、`src/spec_dock/assets/**`、consumer workspace、他tests。
- Red expectation: existing testを先に拡張し、PR workflowのpush/full、missing full workflow、identity rename、wrong truth-table、schedule、provider workflow shippingがfailする。
- minimal Green:
  - `Provider CI` / `provider-tests`を維持し、`pull_request`で`make lint` + `make test-provider-fast`のみ。
  - `Provider Full Regression` / `provider-full-regression`は`main` pushと`workflow_dispatch`で`make test-provider-full`のみ。
  - main push concurrencyはlatest SHAを残し、manual groupを暗黙cancelしない。`continue-on-error`、permission拡張、scheduleなし。
  - rootの両provider workflowはinstall_rootおよびrepresentative init/update targetへ生成されない。
- focused checks:
  - `uv run pytest tests/unit/infra/test_init_update.py -q -k "provider_only_workflow or workflow_seed or provider_full_regression"`
  - `rg -n "Provider CI|provider-tests|test-provider-fast|test-provider-full|workflow_dispatch|schedule|permissions" .github/workflows/provider-ci.yml .github/workflows/provider-full-regression.yml`
- stop / rollback: identityを維持できない、branch protection mutationが必要、permission/secret/scheduleが必要、consumer shippingが必要、truth table外eventが起動する場合はstop。rollbackはPR commandを`make test-provider-full`へ戻す案を保持する。
- report destination: `report.md` Red/Green/Refactor Evidence、Step/Test Contract Closure、EVD-TL-004。
- step closure: `CLOS-TL-AC-003/004/005/009`、`CLOS-TL-BH-003/004/005/006/007`、`CLOS-TL-CON-002/003`。

#### 具体テストケース一覧

- `tc-s03-001` acceptance: event truth table
  - 前提: rootに2 provider workflowsがある。
  - 操作: deterministic text inspectionでtrigger/job/Make targetを抽出する。
  - 期待結果: PR=yes/no、non-main=no/no、main=no/yes、dispatch=no/yes、schedule=no/no。
  - 失敗検出: full重複、wrong event、schedule追加を検出する。
  - 検証方法: existing `test_init_update.py`のRed-first contract test。
  - 関連 closure id: `CLOS-TL-AC-009`、`CLOS-TL-CON-003`

- `tc-s03-002` compatibility: check identity
  - 前提: existing workflow name/job identityは`Provider CI`/`provider-tests`である。
  - 操作: provider-ciのname、job key/name、commandをinspectする。
  - 期待結果: identity不変でPR fastを呼ぶ。
  - 失敗検出: required checkが意図せず消えるrenameを検出する。
  - 検証方法: deterministic exact assertions。
  - 関連 closure id: `CLOS-TL-AC-003`

- `tc-s03-003` negative: provider-only workflowsはshipしない
  - 前提: rootにprovider-ci/full-regressionがある。
  - 操作: install_rootとrepresentative init/update outputをinspectする。
  - 期待結果:両provider workflowsがconsumer artifactsに存在しない。
  - 失敗検出: provider運用物をshipped scaffoldへ混入する回帰を検出する。
  - 検証方法: existing non-shipping testを2 filesへ拡張する。
  - 関連 closure id: `CLOS-TL-CON-002`

### S04 README / AGENTS docs

- behavior goal: contributor/agent向けcommandとpost-merge operationをcanonical designと同じ語彙で説明する。
- delegated role: `doc-writer`。source/tests/workflowsは変更しない。
- allowed paths: `README.md`、`AGENTS.md`。
- forbidden paths: 上記以外、canonical Issue docs、source/tests/workflows、schedule案、hard SLA化。
- Red / alternative: `inspect-only`。変更前はbare pytest=fast、formal full、workflow names、failure owner/rerun/rollbackの説明が欠落していることをdocs checklistで確認する。
- minimal Green:
  - bare/default、`make test-provider-fast`、`make test-provider-full`を説明。
  - PR fast、main/manual full、no schedule、maintainer owner、Actions log/SHA/test、local reproduction、rerun、rollbackを説明。
  - 120秒/10分は非blocking targetでありhard thresholdと書かない。
- focused checks:
  - `rg -n "test-provider-fast|test-provider-full|Provider Full Regression|schedule|maintainer|rollback" README.md AGENTS.md`
  - `git diff --check -- README.md AGENTS.md`
- stop / rollback: docsが実装済みcommand/workflowと不一致、schedule/permission/automatic rollbackを新規契約化、public product/scaffold docs変更が必要ならstop。docs2 filesだけをrevert候補にする。
- report destination: `report.md` S90 Docs Impact Resolution、Delegated Worker Evidence、EVD-TL-007。
- step closure: `CLOS-TL-AC-005/010/011`、`CLOS-TL-BH-007`。

#### 具体テストケース一覧

- `tc-s04-001` inspect: contributor commandとfailure operation
  - 前提: S01-S03のGreen command/workflowが確定している。
  - 操作: README/AGENTSのcommand、event、owner、rerun、rollbackを実装と照合する。
  - 期待結果: raw selectorを推奨せずMake facadeを案内し、no scheduleとpost-merge semanticsを明記する。
  - 失敗検出: docs driftまたはfull failureをmerge blockerと誤記する欠陥を検出する。
  - 検証方法: docs checklist、diff inspection、fresh spec review。
  - 関連 closure id: `CLOS-TL-AC-005/010/011`

### S05 Integrated focused / lint / fast / coverage-delta gate

- behavior goal: fullを実行せず、S01-S04統合状態がfocused、lint、fast、collection/coverage guardsでGreenであることを確認する。
- delegated role: `dev-coder`がcommandsを実行しevidenceを返す。canonical reportはmain orchestrator。
- allowed paths:原則writeなし。failure修正はorigin stepへ戻し、同role/allowed pathsで行う。
- forbidden paths: adhoc skip/xfail/assertion weakening、full execution、S01-S04外修正、baseline manifestのrepo追加。
- Red / alternative: `covered-existing`。ここはintegration gateであり新規Redを作らない。failureはorigin stepへ戻す。
- minimal Green:
  - focused lane/workflow tests pass。
  - `make lint` pass。
  - `make test-provider-fast` pass、H実行0。
  - before/after full node IDs同一、skip/xfail unexplained delta 0、test deletion/assertion weakening 0。
- focused checks:
  - `uv run pytest tests/unit/test_provider_test_lanes.py -q`
  - required-fast 7 exact nodes
  - `uv run pytest tests/unit/infra/test_init_update.py -q -k "provider_only_workflow or workflow_seed or provider_full_regression"`
  - `make lint`
  - `make test-provider-fast`
  - collect-only set verifier
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- stop / rollback: unexpected failure、H execution、node/skip/xfail/assertion unexplained delta、SpecDock validation failure、forbidden path deltaでstop。origin stepへrollbackし、S05全体を再実行する。
- report destination: `report.md` Regression Result、Closure Coverage、EVD-TL-001/002/003/004/008。
- step closure: S01-S04所有closureのlocal Greenと`CLOS-TL-AC-007`。

#### 具体テストケース一覧

- `tc-s05-001` regression: integrated fast gate
  - 前提: S01-S04がGreen。
  - 操作: focused、lint、formal fast、validateを順に実行する。
  - 期待結果:すべて0 exit、fastにH item 0。
  - 失敗検出:層間統合でselector/command/workflow/docsがずれる回帰を検出する。
  - 検証方法:上記command bundleとreport evidence。
  - 関連 closure id: `CLOS-TL-AC-001/003/006/007/009`

### S06 Final integrated fast/full paired 3-run batch

- behavior goal:最終統合状態・同一checkout/Python/cache条件で3組のfast/fullを測定し、3 full runsをfinal full evidenceに兼用する。
- delegated role: `dev-coder`がmeasurement operator。`qa-reviewer`は後続S07でevidence十分性を確認する。
- allowed paths: writeなし。timing/count/logはworker outputからmain orchestratorがreportへ転記。
- forbidden paths: measurement間のsource/test/workflow/docs変更、4回目のroutine full、cache条件変更、failureをskip/xfail化、result改変。
- Red / alternative: `manual-required` measurement。各pairでfast<fullでなければAC-008未達。full failureはraw redのまま記録する。
- minimal Green:
  - pair 1: `make test-provider-fast` -> `make test-provider-full`
  - pair 2:同じ順序
  - pair 3:同じ順序
  - SHA、Python、cache条件、elapsed、counts、skip、failed nodeを各runで記録し、各pair `fast < full`。
- focused checks:
  - preflight: `git diff --check`、`make lint`、collect-only set verifier。
  - batch内full commandは`make test-provider-full`ちょうど3回。
- known flaky policy:
  - `test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state`はHに残し、fullで必ずcollect/execution対象にする。
  - exact nodeだけが失敗した場合もcommandをpassへ読み替えず、`baseline-known-flaky observed failure`として別欄へ記録する。skip/xfail/selector除外はしない。
  - planned 3 runs外のfull rerunは自動で行わない。exact focused rerunとlog comparisonでtriageし、unexpected regressionと分離する。
  - known flaky以外のfailure、別node併発、node omissionはunexpected regressionとして即stopする。
  - final gateは、3 runs内のGreen full evidenceとfresh QA/code/spec judgment、または別Issue/明示risk dispositionなしにpass扱いしない。
- stop / rollback: source drift、condition drift、unexpected regression、fast>=full、H=0、unexplained deltaでstop。lane defectならPR commandをformal fullへ戻すrollback候補をS07へ送る。
- report destination: `report.md` EVD-TL-003/005/008、Final QA Gate、実装セッションログ。
- step closure: `CLOS-TL-AC-002/007/008`、`CLOS-TL-BH-002`、`CLOS-TL-CON-004`。

#### 具体テストケース一覧

- `tc-s06-001` measurement: 3 paired local runs
  - 前提: S05 Green、同一SHA/Python/cache条件。
  - 操作: fast→fullを3組実行する。
  - 期待結果:各組fast<full、full collection=`F∪H`、3 full runsがfinal full evidenceになる。
  - 失敗検出:計測揺れだけの速度claim、stale full evidence、4回目の無用なfullを防ぐ。
  - 検証方法: command timestamps、counts、node membership、elapsed ledger。
  - 関連 closure id: `CLOS-TL-AC-008`

- `tc-s06-002` failure: known flakyとunexpected regressionを分離する
  - 前提: exact known flaky identityとS00 baselineがある。
  - 操作: full failure logをnode単位で分類する。
  - 期待結果: known flakyはvisible red evidence、その他はstop。いずれもskip/xfailしない。
  - 失敗検出:lane変更でflakyまたはregressionを隠すことを防ぐ。
  - 検証方法: full log + exact focused triage + diff review。
  - 関連 closure id: `CLOS-TL-AC-007`、`CLOS-TL-BH-007`

### S07 Fresh reviews / PR observation / human merge boundary

- behavior goal: integrated diffとevidenceをfresh rolesで検査し、PR fast performanceを3 run観測してmerge-ready boundaryで停止する。
- delegated roles:
  - fresh `qa-reviewer`: closure/test obligation、known flaky、3 paired evidence。
  - fresh issue-wide `code-reviewer`: source/tests/workflows integrated diff、identity、rollback。
  - fresh `spec-reviewer`: requirement/design/plan/report/docs alignment。
  - PR observation: main orchestratorがdocumented PR workflowを使う。mergeはhuman-only。
- allowed paths: reviewはread-only。finding修正はS01-S04へ戻し、適切な`dev-coder`/`doc-writer` allowed pathsだけを再委任する。canonical docs/reportはmain orchestratorのみ。
- forbidden paths: reviewer-pass自己主張、GitHub merge/close、branch protection mutation、schedule、permission変更、reviewer waiverのpass扱い。
- Red / alternative: `manual-required`。fresh reviewer failまたはPR run threshold未達はgate fail。PR3 runsはqueueを除くstarted-to-completed elapsedを測る。
- minimal Green:
  - fresh QA/code/specがそれぞれpass。
  -同一reviewed head SHAの`provider-tests` 3 runsが各38.1分未満で、PRにはfull runがない。
  - `Provider CI`/`provider-tests` identityがvisible。
  - merge-ready evidenceを記録し、human merge前に停止。
- focused checks / evidence:
  - `git diff --check`
  - `make lint`
  - `make test-provider-fast`
  - PR `provider-tests` 3 runのURL、head SHA、started/completed、elapsed、test count/skip count。
- stop / rollback:
  - identity欠落、selector escape、required-fast omission、unexpected regression、いずれかのfresh review fail、各PR runが38.1分以上ならstop。
  - identity/escape時は`.github/workflows/provider-ci.yml`のPR commandを`make test-provider-full`へ戻す。bare defaultがunsafeなら`pyproject.toml`のdefault `-m fast`を外す。markers、manual full command、full workflow、measurement evidenceは保持する。
- report destination: `report.md` Final QA/Code/Spec Review Gate、PR Delivery/Merge Preparation Gate、EVD-TL-006。
- step closure:全closureのpre-merge review closure。`CLOS-TL-AC-004/010`のpost-merge observationは`S07-PM`に残す。

#### 具体テストケース一覧

- `tc-s07-001` observation: PR provider-tests 3 runs
  - 前提: fresh-reviewed head SHAのPRがある。
  - 操作: provider-testsを3回観測しstarted-to-completed elapsedを計算する。
  - 期待結果:各run<38.1m、identity不変、full regressionなし。
  - 失敗検出:queue time混入、別SHA/stale run、full merge blocker残存を検出する。
  - 検証方法:Actions run metadataとPR checks。
  - 関連 closure id: `CLOS-TL-AC-003/008`

### S07-PM Post-merge / manual full observation gate

- precondition: humanがmergeした後だけ。S07のmerge-ready判定やhuman-only merge boundaryの代替ではない。
- owner: repository maintainer。
- observe: `Provider Full Regression` main push runのSHA、status、duration、counts、failed test、log。必要なら同じworkflowのmanual `workflow_dispatch`経路を別に観測する。
- failure handling:
  -通常はsame SHAでlocal `make test-provider-full`を再現し、Actions rerunまたはforward fixを行う。
  - Actions rerun候補は`gh run rerun <run-id>`だが、実行権限と対象runをmain orchestratorがread-only確認してから行う。
  - test regressionならforward fix、lane omission/identity defectならPR gateをformal fullへrollbackする。
  -自動rollback、自動Issue作成、既存mergeの遡及blockは行わない。
  -scheduleは追加しない。
- exit: latest main SHAにfull runが1件残り、failureならowner/next action/rerun/rollback dispositionがreportに記録される。red runは隠さない。

## 6. Test Strategy Mapping

| Risk / obligation | First evidence | Green / final evidence | Full timing |
|---|---|---|---|
| partial collection破壊 | S01 Red focused subset | S01/S05 focused | 不要 |
| silent omission / marker conflict | S01 Red global verifier/negative | S05 set equality + S06 full membership | S06のみ |
| required-fast 7 node消失 | S00 baseline + S01 Red | S05 exact 7 node | 不要 |
| command drift | S02 Red | S05 fast + S06 full | S06 fullのみ |
| workflow routing/identity | S03 Red deterministic test | S05 focused + S07 PR observation | 不要 |
| provider workflow shipping | S03 Red non-shipping | S05 focused + review | 不要 |
| coverage weakening | S00 baseline | S05/S06 node/skip/xfail/assertion delta | S06のみ |
| local performance | S06 manual-required | 3 paired evidence | S06の3回 |
| PR performance | S07 manual-required | 3 PR runs each <38.1m | PR fastのみ |
| known flaky | S00 exact characterization | S06 visible full result + focused triage | S06 fullに含む |
| post-merge failure operation | S04 inspect | S07-PM run/owner/rerun evidence | merge後 |

### Exact command candidates

```bash
uv run pytest tests/unit/test_provider_test_lanes.py -q
uv run pytest tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_legacy_flag_reports_parser_error tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess -q
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_provider_only_workflow_is_not_shipped_via_install_root tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets -q
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state -q
uv run pytest --collect-only -q -m fast -p no:cacheprovider
uv run pytest --collect-only -q -m "fast or full_regression" -p no:cacheprovider
make lint
make test-provider-fast
make test-provider-full
git diff --check
./spec-dock/scripts/spec-dock validate
```

`make test-provider-full`はS06のpaired batchでだけ3回使う。上記listingは候補command inventoryであり、S00-S05でfullを実行する許可ではない。

## 7. Review Gates

| Gate | Reviewer / owner | Pass condition | Fail action |
|---|---|---|---|
| G-S01 classifier | fresh `code-reviewer`またはmilestone review | partial-safe、exactly-one、global verifier分離 | S01へ戻る |
| G-S03 routing | fresh `code-reviewer` | truth table、identity、non-shipping、no permission/schedule | S03へ戻る |
| G-S04 docs | fresh `spec-reviewer` docs focus | commands/operation/rollback整合 | S04 doc-writerへ戻る |
| G-S05 local | main orchestrator evidence check | focused/lint/fast/validate/delta Green | origin stepへ戻る |
| G-S06 measurement | fresh `qa-reviewer` | 3 paired、counts、known flaky separation、no extra full | blocked/replan |
| G-FINAL-QA | fresh `qa-reviewer` |全required closuresとrisk-calibrated testsが十分 | fix + fresh review |
| G-FINAL-CODE | fresh issue-wide `code-reviewer` | integrated diff、rollback、forbidden paths | fix + fresh review |
| G-FINAL-SPEC | fresh `spec-reviewer` | requirement/design/plan/report/implementation/docs alignment | canonical修正 + fresh review |
| G-PR | PR observation | 3 provider-tests <38.1m、identity維持、blocking checks Green | merge-readyを主張しない |
| G-HUMAN-MERGE | human | human判断のみ | agentはmergeしない |
| G-POST-MERGE | maintainer | latest main full visible、failure dispositionあり | rerun/forward-fix/rollback |

Reviewer unavailable/denied/waived/provisionalはpassではない。worker evidenceはreviewer verdictの代替にならない。

## 8. Rollback / Compatibility

### Compatibility invariants

- public `spec-dock` CLI/API、Python 3.10+方針、Provider CI Python 3.11、test node IDs/directory layoutを不必要に変えない。
- `Provider CI` / `provider-tests` identityを維持する。
- root provider workflowsはconsumerへshipしない。
- permissions、secret、credential、branch protectionを変更しない。

### Rollback map

1. selector omission、required-fast欠落、identity欠落、許容不能なescapeを確認したらmerge/次工程を停止する。
2. PR workflowのcommandを`make test-provider-full`へ戻し、pre-merge coverageを保守側へ戻す。
3. bare defaultがunsafeなら`pyproject.toml`のdefault `-m fast`を外す。
4. markers、`make test-provider-full`、post-merge/manual full workflow、baseline/measurement evidenceは削除しない。
5. classifier修正をfresh code/spec reviewし、fast gate再導入は別のreviewed判断にする。

Post-merge full failureは自動rollbackしない。repository maintainerがsame SHAの`make test-provider-full`、Actions rerun、forward fixを選ぶ。lane defectの場合だけ上記rollbackを優先する。schedule追加はfailure responseに含めない。

## 9. Docs Impact

- `README.md`: contributor向けdefault/fast/full、PR/main/manual routing、no schedule、failure owner、local reproduction、rerun、rollback。
- `AGENTS.md`: agent向けcommand選択、routineはfast、formal fullは明示、S06/final evidence以外で長時間fullを繰り返さない。
- docs実装は`doc-writer`、docs/spec alignmentはfresh `spec-reviewer`。
- `src/spec_dock/assets/**`、templates、skills、consumer `spec-dock/**`はno-change。変更が必要ならscope/design reviewへ戻す。
- canonical `plan.md`/`report.md`への統合・観測証跡記録はmain orchestratorだけが行う。

## 10. Final Quality Gate

- [ ] 全22 closure rowsがstep closure/report evidenceへ結び付く。
- [ ] S00 baseline node/skip/xfail/known flaky evidenceがある。
- [ ] S01-S04のRed理由、minimal Green、focused checks、worker handoffがreportにある。
- [ ] S05 focused/lint/fast/validate/deltaがGreen。
- [ ] S06 fast/full 3 paired runsが最終統合SHAで実施され、3 full runs以外のroutine fullを追加していない。
- [ ] known flakyはfullから消えず、raw pass/failureとtriageが他のregressionから分離されている。
- [ ] source/test/workflow/docs diffはallowed pathsだけで、`src/spec_dock/**`とconsumer workspaceは不変。
- [ ] test deletion、skip/xfail増加、assertion weakening、xdist/dependency、schedule、permission/secret、branch protection mutationがない。
- [ ] fresh QA/code/spec reviewsがpassed。
- [ ] PR `provider-tests` 3 runが各38.1分未満でidentityが維持される。
- [ ] human-only merge boundaryで停止する。
- [ ] human merge後はS07-PMでmain fullを観測し、failure owner/rerun/rollback dispositionを残す。
- [ ] `git diff --check`と`./spec-dock/scripts/spec-dock validate`がpass。
- [ ] main orchestratorがcanonical report ledgers、commit/no-op、PR delivery/merge preparation evidenceを更新する。

## 11. Plan Blockers

### Design / owner blockers

- owner判断が必要なrequirement/design gap: none。
- implementation planを作れない設計不足: none。`DES-TL-001`〜`007`、required-fast 7 node、truth table、rollback、measurement orderはapproved designで固定済み。

### Canonical promotion readiness gaps

- current `.assurance.json`のdesign source bindingは`b8e88c10...68c7e4a`だが、current approved `design.md`は`dcba55f9...470811`である。authorized profile=`standard`はplanning profileとして使用できるが、canonical plan promotion前にmain orchestratorがsource bindingをrefresh/verifyする必要がある。
- current canonical `plan.md`はStandard scaffoldのplaceholderが残る一方、frontmatterは`approved`で、`report.md`のPlan gateは`not started / blocking=yes`である。本artifactの採用後、main orchestratorがsubstantive planへ再記述しfresh `spec-reviewer` passを取得するまでexecution readinessを主張できない。
- 上記はowner質問ではなくauthoring/lifecycle整合の修正項目である。

## 12. Integration Notes for Main Orchestrator

### Adoption / canonical ownership

1. 本artifactをEvidence Adoption LedgerとDelegated Draft Evidenceへ`adopted`/`partially_adopted`/`rejected`のいずれかで記録する。
2. current source hashesとcanonical diff guardを照合する。
3. canonical `plan.md`へmain orchestrator自身が再記述する。本artifactのcopyをauthority化しない。
4. `.assurance.json` source bindingをcurrent approved requirement/design bytesへrefresh/verifyする。
5. fresh `spec-reviewer`へAC/BH/CON closure、S00-S07順序、known flaky、3 paired runs、post-merge gate分離を確認させる。

### Lightweight provenance

- requirement/design revision: SHA-256 `3e281337...f5f097` / `dcba55f9...470811`。
- design review evidence: canonical `report.md`のdesign-R3 `passed`記録。
- architecture evidence: `20260728t041725z-delegated-draft-test-lane-architecture.md`、SHA-256 `4ecf5a90...f0792`。
- accepted policy: ADR SHA-256 `8f89d2e6...de8e`、Option A / no schedule。
- leaf evidence used: none。追加sub-agent/leaf specialistは使用していない。
- fallback decision: delegated artifact authoringが成功したためmanual fallbackは未使用。
- report evidence destination: `report.md`のEvidence Adoption Ledger、Delegated Draft Evidence、Workflow-Scoped Authorization、Step Contract Closure、Test Contract Closure、Reviewer Gate Status。

### Forbidden actions avoided

- canonical requirement/design/plan/report、source、tests、workflow、config、README/AGENTSを編集していない。
- GitHub mutation、commit、push、issue start/finish、phase promotion、reviewer-pass claim、implementation-readiness claimを行っていない。
- `src/spec_dock/**`、consumer workspace、branch protection、schedule、permissions、test deletion/skip/xfail/assertion、xdist/dependencyを変更していない。

### Recommended next action

- main orchestratorがpost-run diff guardを確認して本artifactの採否を記録し、canonical `plan.md`へ統合する。その後、current source bindingをrefreshし、fresh `spec-reviewer` passを取得する。

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

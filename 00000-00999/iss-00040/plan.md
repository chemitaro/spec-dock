---
種別: 実装計画書（Issue）
ID: "iss-00040"
タイトル: "Sync Fail Closed Hardening And Test Realignment"
関連GitHub: ["#40"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00040 Sync Fail Closed Hardening And Test Realignment — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - runtime contract は read-only unless true defect is proven
  - stale tests を skip で隠さない
  - checked-in dogfooding mirror parity を回復する

## マイルストーン一覧
- M1:
  - 対象:
    - stale-contract cluster の baseline と scope boundary 固定
  - exit:
    - representative failures と scope が report / discussions / plan で追える
- M2:
  - 対象:
    - `active` / `deps` / `sync` の fixture realignment
  - exit:
    - targeted CLI runtime suites が green
- M3:
  - 対象:
    - `wrappers` / `domain` expectation realignment
  - exit:
    - targeted suites が green
- M4:
  - 対象:
    - dogfooding mirror parity recovery と final regression
  - exit:
    - parity evidence と full regression evidence が揃う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - representative failures が current stale-contract cluster として再現し、issue scope と対応づけられている
  - closes:
    - AC-004
    - EC-001
  - review gate:
    - failing signatures と scope boundary が report に残っている
- S02:
  - 観測可能な振る舞い:
    - `active` / `deps` / `sync` tests が repo-initialized GitHub-linked fixture で intended assertion まで到達して pass する
  - closes:
    - AC-001
    - EC-001
    - EC-002
  - review gate:
    - targeted CLI runtime suites が green
- S03:
  - 観測可能な振る舞い:
    - wrappers/docs expectation と domain validation expectation が current source of truth に整列して pass する
  - closes:
    - AC-002
  - review gate:
    - targeted wrapper/domain suites が green
- S04:
  - 観測可能な振る舞い:
    - provider asset と checked-in dogfooding mirror の parity drift が解消される
  - closes:
    - AC-003
    - EC-003
  - review gate:
    - targeted parity test が green
- S05:
  - 観測可能な振る舞い:
    - issue scope の stale-contract cluster が regression evidence 上で解消されている
  - closes:
    - AC-004
  - review gate:
    - full regression evidence と remaining failures の仕分けが report に残る

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S03
- AC-003 -> S04
- AC-004 -> S01, S05
- EC-001 -> S01, S02
- EC-002 -> S02
- EC-003 -> S04

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S02, S03, S04, S05 完了後
  - scope:
    - fixture strategy, expectation meaning, parity correction, contract non-regression
- QG1 QA review:
  - timing:
    - S04, S05 完了後
  - scope:
    - targeted suite outputs, parity evidence, full regression evidence
- SG1 spec review:
  - timing:
    - 実装着手前
  - scope:
    - scope, guardrails, verification mapping, step decomposition

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。

## 実装ステップ

### S01 — baseline failure clustering and scope lock
- target:
  - representative failing tests
  - scope boundary
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260329t053816z-01-research-active-and-deps-test-failure-clustering.md`
- step boundary:
  - implementation 前に stale-contract cluster を baseline 化し、scope 内外を仕分ける

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — reproduce representative failures
- purpose:
  - stale-contract cluster を観測可能な形で固定する
- files:
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/domain_runtime/test_runtime_domain_s01.py`
  - `tests/test_init_update.py`

##### I1 — capture signatures
- slice goal:
  - `--no-github` reject、`origin` missing、docs expectation mismatch、validation ordering mismatch、parity drift を押さえる

###### Red
- failing test:
  - representative targeted tests
- expected failure:
  - current stale-contract signatures が出る

###### Green
- minimum implementation:
  - なし
- pass condition:
  - cluster と scope が report に整理される

###### Refactor
- cleanup target:
  - report / discussions / plan の整合
- invariants to keep green:
  - issue scope を広げすぎない

#### step gate
- review:
  - scope boundary が requirement と一致
- expected tests:
  - representative failures only
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — cli runtime fixture realignment for active deps sync
- target:
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_sync.py`
  - 必要なら `tests/cli_runtime/harness.py`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `tests/cli_runtime/test_new.py`
- step boundary:
  - current-contract fixture と explicit legacy fixture の切り分けを完了し、CLI runtime suites を green にする

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — active and deps
- purpose:
  - stale fixture を current contract へ寄せる
- files:
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/harness.py`

##### I1 — replace unsupported setup
- slice goal:
  - `new --no-github` fixture と `origin` missing fixture を normal path tests から除去する

###### Red
- failing test:
  - representative `test_active_set_*`
  - representative `test_deps_check_*`
- expected failure:
  - `--no-github` reject / `git remote get-url origin`

###### Green
- minimum implementation:
  - helper 再利用または薄い helper 追加で repo-initialized linked hierarchy に置換する
- pass condition:
  - representative targeted tests が pass

###### Refactor
- cleanup target:
  - fixture duplication の圧縮
- invariants to keep green:
  - intended behavior assertion を維持する
  - legacy-compat tests の explicit fixture coverage を落とさない

#### B2 — sync regressions
- purpose:
  - sync suite に残る同系統 drift を解消する
- files:
  - `tests/cli_runtime/test_sync.py`

##### I1 — align sync setup and expectations
- slice goal:
  - sync tests が current contract 前提で走るようにする

###### Red
- failing test:
  - representative `test_sync_*`
- expected failure:
  - stale fixture 由来 failure

###### Green
- minimum implementation:
  - fixture と ID expectation を現行 naming / linkage に更新する
- pass condition:
  - targeted sync tests が pass

###### Refactor
- cleanup target:
  - duplicated setup
- invariants to keep green:
  - sync output semantics を変えない
  - sync の legacy read-path coverage を落とさない

#### step gate
- review:
  - runtime contract に手を入れていない
- expected tests:
  - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_deps tests.cli_runtime.test_sync -v`
  - legacy-compat evidence:
    - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_local_only_node_does_not_rename_branch -v`
    - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_without_github_local_issue_without_deps_is_ready -v`
    - `python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing -v`
    - `python -m unittest tests.cli_runtime.test_sync.TestCliSync.test_local_only_issue_is_open_and_ready_without_deps -v`
- report update:
  - `./spec-dock/active/issue/report.md`

### S03 — wrappers and domain expectation realignment
- target:
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/domain_runtime/test_runtime_domain_s01.py`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/docs/workflow_issue.md`
- step boundary:
  - docs expectation と validation expectation を current source of truth に揃える

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — wrapper docs contract
- purpose:
  - stale docs expectation を current workflow docs へ追随させる
- files:
  - `tests/cli_runtime/test_wrappers.py`

##### I1 — align command examples
- slice goal:
  - wrapper tests が現行 docs を検証する

###### Red
- failing test:
  - representative wrapper test
- expected failure:
  - old `--no-github` command example expectation

###### Green
- minimum implementation:
  - docs expectation を current workflow text に更新する
- pass condition:
  - targeted wrapper tests が pass

###### Refactor
- cleanup target:
  - repeated command string assertions
- invariants to keep green:
  - docs source of truth は変えない

#### B2 — domain fail-closed ordering
- purpose:
  - validation ordering change に沿って domain test を更新する
- files:
  - `tests/domain_runtime/test_runtime_domain_s01.py`

##### I1 — align structural error expectation
- slice goal:
  - current fail-closed ordering を expectation へ反映する

###### Red
- failing test:
  - representative domain test
- expected failure:
  - old parent mismatch message expectation

###### Green
- minimum implementation:
  - current validation error expectation へ更新する
- pass condition:
  - targeted domain tests が pass

###### Refactor
- cleanup target:
  - assertion wording の重複
- invariants to keep green:
  - product validation order は変えない

#### step gate
- review:
  - docs/validation source of truth に寄せている
- expected tests:
  - `python -m unittest tests.cli_runtime.test_wrappers tests.domain_runtime.test_runtime_domain_s01 -v`
- report update:
  - `./spec-dock/active/issue/report.md`

### S04 — dogfooding runtime mirror parity recovery
- target:
  - checked-in dogfooding mirror files
- design refs:
  - `spec-dock/active/issue/design.md`
  - `tests/test_init_update.py`
- step boundary:
  - provider asset を正本に checked-in mirror parity を回復する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — refresh checked-in mirror
- purpose:
  - parity drift を解消する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `spec-dock/scripts/spec_dock_runtime/application/sync_state.py`

##### I1 — eliminate parity drift
- slice goal:
  - targeted parity test failure を消す

###### Red
- failing test:
  - targeted parity test
- expected failure:
  - provider vs checked-in mirror mismatch

###### Green
- minimum implementation:
  - checked-in mirror refresh または equivalent parity correction
- pass condition:
  - targeted parity test が pass

###### Refactor
- cleanup target:
  - 不要差分の確認
- invariants to keep green:
  - provider asset が source of truth

#### step gate
- review:
  - parity drift が消えている
- expected tests:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v`
- report update:
  - `./spec-dock/active/issue/report.md`

### S05 — final regression and diff quality gate
- target:
  - changed tests
  - changed harness helper if any
  - changed checked-in mirror files
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/report.md`
- step boundary:
  - targeted reruns, broad rerun, report, final diff review を完了する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — regression confirmation
- purpose:
  - issue scope の stale-contract cluster が解消されたことを示す
- files:
  - changed files

##### I1 — targeted then broad rerun
- slice goal:
  - targeted suites と broad regression evidence を揃える

###### Red
- failing test:
  - 該当なし
- expected failure:
  - 該当なし

###### Green
- minimum implementation:
  - targeted rerun と `discover` rerun を実施する
- pass condition:
  - stale-contract cluster 由来 failures が消えている

###### Refactor
- cleanup target:
  - report と diff の整理
- invariants to keep green:
  - report が追跡可能である

#### step gate
- review:
  - final diff review quality gate
- expected tests:
  - `python -m unittest discover -v`
- report update:
  - `./spec-dock/active/issue/report.md`

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - none
- 対応:
  - 現時点では product docs refresh は主要対象外。
  - 実装中に source-of-truth docs 自体の不整合が見つかった場合のみ、scope 逸脱かどうかを確認した上で追加する。

### S99 — final diff review quality gate
- branch diff scope:
  - changed tests
  - changed harness helper if any
  - changed checked-in dogfooding mirror files
- required validation:
  - targeted suite reruns
  - parity test
  - final regression evidence
- reviewer approvals:
  - implementation review
  - QA review if requested
  - spec review pass

## 未確定事項
- なし:
  - close 判定は AC-004 と final exit contract に固定した

## final exit contract
- AC/EC 達成:
  - AC-001〜AC-004 と EC-001〜EC-003 の evidence が report で追える
- close criteria:
  - targeted suites と parity test は pass している
  - `python -m unittest discover -v` の remaining failures がある場合は、それぞれについて scope 外判定と参照先 issue を report に記録済みである
- docs impact resolved:
  - `none` として扱うか、必要なら scope 内の最小 docs correction まで完了している
- final diff approved:
  - S99 quality gate を通過している

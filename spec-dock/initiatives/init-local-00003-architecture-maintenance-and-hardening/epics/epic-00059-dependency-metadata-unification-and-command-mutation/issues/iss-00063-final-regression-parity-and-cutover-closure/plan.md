---
種別: 実装計画書（Issue）
ID: "iss-00063"
タイトル: "Final regression parity and cutover closure"
関連GitHub: ["#63"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00063 Final regression parity and cutover closure — 実装計画（Execution Contract）

## この計画で満たす要件ID
- epic mapping:
  - `E-AC-005`
  - epic final close review
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
- 制約:
  - T3 は cutover readiness/judgment owner、T4 は final closure owner
  - source code は変更しない
  - `./spec-dock/scripts/spec-dock validate` を required command とする
  - epic `report.md` は close summary のみ、詳細 evidence は issue `report.md`
  - `iss-00062/report.md` が completed state になるまで S02-S99 に着手しない

## 実行前提 / blocker
- prerequisite:
  - `iss-00062/report.md` が template / placeholder ではなく、hard cutover judgment、docs 更新、manual fix、`validate` / `sync` evidence を実値で持つ completed state であること。
  - `iss-00062/report.md` に active parity の観測対象 `<target-id>` が記録されていること。未記録なら T4 は blocker。
- blocker policy:
  - prerequisite 不成立時は S02 以降へ進まず、T4 issue `report.md` に blocker / next action を記録する。
  - prerequisite 不成立の間は epic `report.md` を更新しない。

## マイルストーン一覧
- M1:
  - 対象:
    - T4 closure boundary と required deliverable の固定
  - exit:
    - issue docs が T3/T4 ownership、required evidence、close summary 責務を説明できる
- M2:
  - 対象:
    - final regression suite と parity confirmation
  - exit:
    - fixed final regression suite の review-only inherited item と rerun-required item が `report.md` に残り、parity verdict が出る
- M3:
  - 対象:
    - T3 evidence bundle review / packaging
  - exit:
    - T3 evidence の参照先、review 結果、欠落時の扱いが `report.md` から追える
- M4:
  - 対象:
    - T4 final parity/spec review record と epic close summary
  - exit:
    - `E-AC-005` close evidence が issue `report.md` と epic `report.md` の両方で整合する

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - upstream / prerequisite である T3 judgment fixed と issue spec lock を先に確認する
  - command / regression evidence を取得してから T3 bundle review に進む
  - final report / epic close summary は evidence と review verdict が揃ってから実施する
- step ordering notes:
  - S01 が baseline 固定、S02 が command / regression evidence、S03 が T3 evidence packaging、S04 が close record、S90/S99 が docs refresh と最終品質ゲートを担当する
  - `iss-00062/report.md` completed state の prerequisite check が通るまで S02-S99 は開始しない
  - epic `report.md` を更新してよいのは S04 だけで、S02/S03/S90 は issue `report.md` 以外へ close claim を広げない

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - T4 closure boundary と deliverable が issue docs に固定される
  - closes:
    - baseline lock
  - review gate:
    - requirement/design/plan が T3/T4 ownership、deliverable、blocker path を含んでいる
- S02:
  - 観測可能な振る舞い:
    - fixed final regression suite と `set-active` / `sync` / `validate` parity confirmation の結果が issue `report.md` に残る
  - closes:
    - AC-001
    - AC-002
    - EC-002
    - EC-004
  - review gate:
    - final regression suite の review-only inherited item / rerun-required item / parity verdict が記録されている
    - `validate` 成功または failure reason / next action が記録されている
- S03:
  - 観測可能な振る舞い:
    - T3 evidence bundle の review / packaging 結果が T4 issue `report.md` に残る
  - closes:
    - AC-003
    - EC-001
  - review gate:
    - required evidence reference が一覧化され、欠落時は blocker と next action が明記されている
- S04:
  - 観測可能な振る舞い:
    - T4 final parity/spec review record と epic close summary が整合して更新される
  - closes:
    - AC-004
    - EC-003
  - review gate:
    - issue `report.md` が final evidence の正本として読める
    - epic `report.md` が close summary のみを保持し、issue `report.md` と矛盾しない

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S04
- EC-001 -> S03
- EC-002 -> S02
- EC-003 -> S04, S99
- EC-004 -> S02

## レビュー / QA ゲート方針
- RG1 evidence review:
  - timing:
    - S02 完了後
    - S03 完了後
  - scope:
    - regression / parity evidence の妥当性
    - T3 bundle review / packaging の妥当性
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 close-out review:
  - timing:
    - S04 完了後
  - scope:
    - `E-AC-005` close evidence
    - epic close summary と issue report の整合
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` と必要なら epic `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - 実行着手前
    - S04 完了後
  - scope:
    - requirement/design/plan の ownership / step / gate 整合
    - final parity/spec review record の妥当性
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする

- step approval loop:
  - SG1/spec review pass を取得するまで implementation を開始しない
  - `iss-00062/report.md` completed prerequisite を満たすまで S02 を開始しない
  - S01 後は prerequisite check と RG1/evidence review pass を `report.md` に記録してから S02 を開始する
  - S02 後は RG1/evidence review pass を `report.md` に記録してから S03 を開始する
  - S03 後は RG1/evidence review pass を `report.md` に記録してから S04 を開始する
  - S04 後は final QG1/close-out review pass と final SG1/spec review pass を `report.md` に記録して close / commit する

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、docs / evidence issue では failing command / missing evidence / report gap を `Red` として扱う。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。
- required step（`validate` / required review / required report update）が pass しなければ `complete` としない。
- epic `report.md` を更新できるのは S04 のみ。S02/S03/S90 での先行更新は禁止する。

## 実装ステップ

### S01 — T4 closure baseline / ownership lock
- target:
  - `iss-00063` の requirement/design/plan を T4 closure owner 用に具体化する
- design refs:
  - `design.md` の `依存関係分析`
  - `design.md` の `close reporting boundary`
- step boundary:
  - source code や report 実更新には進まず、issue spec 固定だけを扱う

#### update_plan（着手時に登録）
- [ ] `update_plan` に S01-S99 の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — issue spec lock
- purpose:
  - T3/T4 ownership と deliverable を固定する
- files:
  - `requirement.md`
  - `design.md`
  - `plan.md`

##### I1 — spec concrete-fill cycle
- slice goal:
  - placeholder を issue-specific contract に置き換える

###### Red
- failing review:
  - issue docs が template / placeholder のため、T4 close path を説明できない
- expected failure:
  - reviewer が execution へ進めない

###### Green
- minimum implementation:
  - requirement/design/plan に ownership、deliverable、step、gate、blocker path を記入する
- pass condition:
  - SG1 で plan upfront approval を得られる

###### Refactor
- 目的:
  - 用語を epic docs と揃え、重複表現を減らす
- guardrail:
  - 振る舞いを変えない
  - T4 の責務を広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - spec review で T3/T4 ownership と step 順が pass
- expected tests:
  - `git --no-pager diff -- requirement.md design.md plan.md`
- report update:
  - S01 承認結果を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — final regression suite / parity confirmation
- target:
  - final regression suite と final parity confirmation を実行し、結果を issue `report.md` に残す
- design refs:
  - `design.md` の `regression boundary`
  - `design.md` の `parity boundary`
- step boundary:
  - prerequisite として `iss-00062/report.md` completed state を確認してから着手する
  - drift が見つかった場合は close を止め、補修実装へは進まない
  - epic `report.md` はこの step では更新しない

#### B1 — required command evidence
- purpose:
  - final close に必要な command evidence を取得する
- files:
  - `report.md`

##### I1 — regression/parity evidence cycle
- slice goal:
  - required command / regression result を pass か blocker か判定可能にする

###### Red
- failing command / missing evidence:
  - final regression suite の正本、review-only inherited item、`validate`、`sync`、必要時 `set-active` の要約が report に無い
- expected failure:
  - AC-001 / AC-002 を close できない

###### Green
- minimum implementation:
  - `iss-00062/report.md` から final regression suite の review-only inherited item を review し、次を fixed item として T4 issue `report.md` に記録する
    - `python -m unittest tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_delete_s13 -v`
    - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_validate_s02 -v`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity -v`
  - rerun-required final command として次を実行し、`same dependency graph` 観測値とともに report に記録する
    - `./spec-dock/scripts/spec-dock sync`
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock active set <target-id>` ただし `<target-id>` は `iss-00062/report.md` 記録済み id を使う
- pass condition:
  - RG1 で regression / parity evidence が pass

###### Refactor
- 目的:
  - evidence 記述順を reviewer が追いやすい形に整える
- guardrail:
  - command 結果を書き換えない
  - 新しい required command を増やさない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - final regression suite の正本、review-only inherited item、rerun-required item、parity verdict、failure 時 next action が report にある
- expected tests:
  - review-only inherited item:
    - `python -m unittest tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_delete_s13 -v`
    - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_validate_s02 -v`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock active set <target-id>` ただし `iss-00062/report.md` の記録済み id がある場合
- report update:
  - S02 の command / review 結果を `./spec-dock/active/issue/report.md` に残す
  - `final_regression_suite.source`、`final_regression_suite.items.reviewed`、`final_regression_suite.items.rerun`、`final_regression_suite.pass`、`parity_confirmation.graph_contract`、`parity_confirmation.observations.active_set`、`parity_confirmation.observations.sync`、`parity_confirmation.observations.validate` を読める形で残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S03 — T3 evidence bundle review / packaging
- target:
  - `iss-00062/report.md` を T3 evidence bundle として review し、T4 close 用 index を作る
- design refs:
  - `design.md` の `evidence review boundary`
  - `design.md` の `escalation boundary`
- step boundary:
  - T3 report を rewrite せず、review 結果は T4 report にのみ追記する
  - epic `report.md` はこの step では更新しない

#### B1 — evidence review bundle
- purpose:
  - T3 judgment fixed の参照先を reviewer 向けに整理する
- files:
  - `report.md`
  - read only: `../iss-00062-downstream-parity-and-cutover-readiness/report.md`

##### I1 — bundle review cycle
- slice goal:
  - required evidence の有無と欠落時の扱いを明確にする

###### Red
- failing review:
  - T3 evidence 参照先が不足し、T4 close record から judgment fixed を追えない
- expected failure:
  - AC-003 を close できない

###### Green
- minimum implementation:
  - required evidence reference、review 結果、欠落時 blocker / next action を T4 report に記録する
- pass condition:
  - RG1 で bundle review / packaging が pass

###### Refactor
- 目的:
  - evidence index の並びを close review 順に整理する
- guardrail:
  - T3 judgment の内容を書き換えない
  - 欠落を隠さない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - T3 evidence reference、review verdict、blocker 有無が report にある
- expected tests:
  - `git --no-pager diff -- report.md`
- report update:
  - S03 の bundle review 結果を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S04 — final parity/spec review record / epic close summary
- target:
  - `E-AC-005` の close evidence を T4 issue `report.md` と epic `report.md` に反映する
- design refs:
  - `design.md` の `close reporting boundary`
- step boundary:
  - prerequisite として `iss-00062/report.md` completed state と S02/S03 pass を確認してから着手する
  - issue `report.md` を detailed evidence の正本にし、epic `report.md` は close summary のみを更新する
  - epic `report.md` を更新してよい唯一の step とする

#### B1 — close reporting
- purpose:
  - final review verdict と epic close summary を整合させる
- files:
  - `report.md`
  - `../../report.md`

##### I1 — close record cycle
- slice goal:
  - reviewer が 2 つの report から同じ close claim を読めるようにする

###### Red
- failing review:
  - issue `report.md` と epic `report.md` の close claim が不整合、または final verdict が追えない
- expected failure:
  - AC-004 / EC-003 を close できない

###### Green
- minimum implementation:
  - T4 final parity/spec review record を issue `report.md` に作成し、epic `report.md` に close summary を転記する
- pass condition:
  - QG1 / SG1 で final close review が pass

###### Refactor
- 目的:
  - close summary を concise に保ち、詳細 evidence は issue `report.md` へ寄せる
- guardrail:
  - detailed evidence を epic `report.md` へ複製しすぎない
  - review verdict を曖昧にしない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - final parity/spec review verdict と epic close summary が整合している
- expected tests:
  - `git --no-pager diff -- report.md ../../report.md`
- report update:
  - S04 の reviewer verdict / close summary 反映結果を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs
- 対応:
  - `iss-00063/report.md` の wording / evidence index を最終調整する
  - no-op の場合でも、docs impact が no-op である理由を issue `report.md` に残す

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00063` issue docs / report
  - S04 で更新した場合のみ epic `report.md`
- required validation:
  - `./spec-dock/scripts/spec-dock validate`
  - required review verdict（RG1 / QG1 / SG1）
- reviewer approvals:
  - final spec review `pass`
  - epic final close review `pass`
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- 現時点ではなし。

## final exit contract
- AC/EC 達成:
  - AC-001..004 と EC-001..004 が issue `report.md` と epic `report.md` から追える
  - T3 judgment fixed を再判定していない
- docs impact resolved:
  - issue docs / report と epic close summary が同期されている
- final diff approved:
  - `./spec-dock/scripts/spec-dock validate` が成功し、required review が pass している

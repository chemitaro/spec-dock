---
種別: 実装計画書（Issue）
ID: "iss-00078"
タイトル: "Installer coexistence contract and migration flow"
関連GitHub: ["#78"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md"]
親: ["epic-00077", "init-local-00003"]
---

# iss-00078 Installer coexistence contract and migration flow — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
  - AC-005
  - AC-006
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - auto-migration engine は追加しない
  - legacy/current dual-read は追加しない
  - legacy auto-delete は追加しない

## マイルストーン一覧
- M1:
  - 対象:
    - spec gate と current failing installer contract の固定
  - exit:
    - SG1 spec review pass
    - installer red tests が coexistence contract を表現している
- M2:
  - 対象:
    - installer coexistence contract 実装
  - exit:
    - `_install_spec_dock()` が legacy coexistence で install を継続できる
    - init/update targeted tests が pass
- M3:
  - 対象:
    - no-rename guidance と doctor/validate observability 実装
  - exit:
    - `_require_specdock()` が rename を案内しない
    - `doctor` が legacy-only / cleanup-pending を区別できる
    - runtime targeted tests が pass
- M4:
  - 対象:
    - final readiness bundle、docs impact resolution、final review closure
  - exit:
    - S04 が final evidence bundle を固定している
    - S90 が完了している
    - S99 で final SG1/RG1/QG1 と required validation が完了している

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の dependency UML と interface contract を参照する
- sequencing rule:
  - installer gate tests を先に red にし、entrypoint contract を固定してから runtime observability へ進む
  - docs は実装が固まった後に refresh する
- step ordering notes:
  - S01 で review target と red tests を固定
  - S02 で `_install_spec_dock()` を実装
  - S03 で `_require_specdock()` と `doctor`/`validate` observability を実装
  - S04 で final evidence bundle を先に固定する
  - S90 で docs impact を必ず解消する
  - S99 で final diff / validation / review closure を完了する

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - spec-reviewer が implementation-ready と判断でき、installer red tests が current bug を再現する
  - closes:
    - AC-006 baseline
  - review gate:
    - SG1/spec review pass
- S02:
  - 観測可能な振る舞い:
    - legacy `.spec-dock/` があっても `spec-dock/` install が止まらない
  - closes:
    - AC-001
    - EC-002 の install/update 側
  - review gate:
    - RG1/code review pass
- S03:
  - 観測可能な振る舞い:
    - rename guidance が manual migration guidance に置き換わり、doctor/validate が migration state を観測できる
  - closes:
    - AC-002
    - AC-003
    - AC-004
    - AC-005
    - EC-001
    - EC-002 の runtime 側
    - EC-003
  - review gate:
    - RG1/code review pass
    - QG1/QA review pass
- S04:
  - 観測可能な振る舞い:
    - final evidence bundle で single-issue close readiness を S99 に渡せる
  - closes:
    - AC-006 close readiness
  - review gate:
    - S99 に渡す close packet が揃っている

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S03
- AC-003 -> S03
- AC-004 -> S03
- AC-005 -> S03
- AC-006 -> S01, S04
- EC-001 -> S03
- EC-002 -> S02, S03
- EC-003 -> S03

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前
    - S04 close 前
  - scope:
    - requirement/design/plan の decision completeness
    - implementation 後の final diff が spec と一致しているか
  - commit gate:
    - SG1 pass 後に `report.md` を更新し、docs-only なら docs-only commit、実装後なら final close commit に含める
- RG1 code review:
  - timing:
    - S02 完了後
    - S03 完了後
  - scope:
    - installer/runtime diff が no-dual-read/no-auto-delete を守っているか
  - commit gate:
    - pass まで fix -> re-review を繰り返し、pass 後に `report.md` を更新して stage commit を作る
- QG1 QA review:
  - timing:
    - S03 完了後
    - S99 前の final regression 確認
  - scope:
    - installer/runtime targeted tests
    - `doctor` / `validate` command evidence
  - commit gate:
    - pass まで fix -> re-test を繰り返し、pass 後に `report.md` を更新して final stage へ進む
- review loop rule:
  - reviewer status は `pass` になるまで修正と再レビューを繰り返す

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red -> Green -> Refactor -> review -> fix -> re-review -> report -> commit/no-op`
- failing test は step ごとに観測したい behavior を最短で固定する。
- S90 は必須ステップとして実行し、docs impact を解消する。
- S99 で base branch との差分を対象に final diff review を行う。
- reviewer verdict と command/test evidence は `./spec-dock/active/issue/report.md` に残す。

## 実装ステップ

### S01 — spec lock and failing installer regression
- target:
  - active issue spec docs
  - `tests/test_cli.py`
  - 必要なら `tests/test_init_update.py`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/requirement.md`
- step boundary:
  - rename guidance が bug であることを installer red tests で固定し、spec-reviewer が implementation-ready と判断できる状態を作る

#### update_plan（着手時に登録）
- [ ] `update_plan` に S01 の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の S01 記録位置を決めた

#### B1 — failing installer contract
- purpose:
  - coexistence install を要求する red test を置く
- files:
  - `tests/test_cli.py`
  - 必要なら `tests/test_init_update.py`

##### I1 — reproduce rename blocker
- slice goal:
  - legacy `.spec-dock/` only 状態で install が止まる現状を red に固定する

###### Red
- failing test:
  - legacy `.spec-dock/` only state で `spec-dock init` が success すべきことを表す test
- expected failure:
  - current implementation は rename guidance RuntimeError を返す

###### Green
- minimum implementation:
  - なし
- pass condition:
  - red test が正しく current bug を示している

###### Refactor
- 目的:
  - test 名と fixture を coexistence contract に合わせて整理する
- guardrail:
  - production code はまだ変えない

#### step gate
- review:
  - SG1/spec review pass
- expected tests:
  - targeted installer test red evidence
- report update:
  - spec review verdict と red evidence を `./spec-dock/active/issue/report.md` に残す

### S02 — coexistence install contract
- target:
  - `src/spec_dock/cli.py`
  - `tests/test_cli.py`
  - `tests/test_init_update.py`
- design refs:
  - `_install_spec_dock()` interface contract
- step boundary:
  - legacy `.spec-dock/` があっても `spec-dock/` install を止めない

#### update_plan（着手時に登録）
- [ ] `update_plan` に S02 の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の S02 記録位置を決めた

#### B1 — installer gate correction
- purpose:
  - `_install_spec_dock()` の rename blocker を除去する
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_cli.py`
  - `tests/test_init_update.py`

##### I1 — allow install beside legacy
- slice goal:
  - legacy `.spec-dock/` only state で current `spec-dock/` を作成できるようにする

###### Red
- failing test:
  - S01 で追加した coexistence install regression
- expected failure:
  - rename guidance RuntimeError

###### Green
- minimum implementation:
  - `_install_spec_dock()` の legacy-only reject branch を coexistence install branch に置き換える
- pass condition:
  - `spec-dock/` が作成され、legacy `.spec-dock/` は unchanged のまま残る

###### Refactor
- 目的:
  - legacy presence 判定の重複を整理する
- guardrail:
  - write target は `spec-dock/` に限定する

#### step gate
- review:
  - RG1/code review pass
- expected tests:
  - `python -m unittest tests.test_cli -v`
  - targeted `python -m unittest tests.test_init_update -v`
- report update:
  - code review verdict と installer test results を `./spec-dock/active/issue/report.md` に残す

### S03 — no-rename guidance and migration observability
- target:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - runtime and installer tests
- design refs:
  - `_require_specdock()` interface contract
  - `doctor` state contract
  - `validate` current-only contract
- step boundary:
  - current workspace missing guidance、legacy coexistence diagnosis、no-dual-read/no-auto-delete を揃える

#### update_plan（着手時に登録）
- [ ] `update_plan` に S03 の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の S03 記録位置を決めた

#### B1 — current workspace missing guidance
- purpose:
  - `_require_specdock()` の rename guidance を manual migration guidance に置き換える
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_cli.py`
  - 必要なら `tests/test_init_update.py`

##### I1 — replace rename message
- slice goal:
  - legacy only 状態で `spec-dock init` と manual migration を案内する

###### Red
- failing test:
  - current-workspace-required path が rename を返さないことを確認する test
- expected failure:
  - current implementation は rename guidance を返す

###### Green
- minimum implementation:
  - `_require_specdock()` message と branch を置き換える
- pass condition:
  - legacy path を返さず、manual migration guidance error を返す

###### Refactor
- 目的:
  - installer error message の wording を docs と整合させる
- guardrail:
  - legacy/current compatibility を示唆しない

#### B2 — doctor and validate observability
- purpose:
  - `legacy_only_workspace` と `legacy_cleanup_pending` を command output で観測できるようにする
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
  - 必要なら `tests/cli_runtime/test_runtime_validate_s02.py`

##### I1 — legacy only finding
- slice goal:
  - `spec-dock/` missing + legacy present を install required finding にする

###### Red
- failing test:
  - doctor が legacy only state を non-ok finding として返す test
- expected failure:
  - current doctor はこの state を区別できない

###### Green
- minimum implementation:
  - doctor に legacy only diagnosis を追加する
- pass condition:
  - doctor が rename ではなく install + manual migration を案内する

###### Refactor
- 目的:
  - finding message と guidance の冗長さを整理する
- guardrail:
  - cleanup pending warning と混同しない

##### I2 — cleanup pending warning
- slice goal:
  - coexistence + valid current state を warning で観測できるようにする

###### Red
- failing test:
  - doctor が coexistence state を ok + warning として返す test
- expected failure:
  - current doctor は warning 契約を持たない

###### Green
- minimum implementation:
  - doctor warning path を追加し、validate は current-only pass のままにする
- pass condition:
  - validate pass、doctor warning、legacy unchanged が揃う

###### Refactor
- 目的:
  - current-only validation と doctor diagnostics の責務境界を明確にする
- guardrail:
  - validate が legacy cleanup pending を failure にしない
  - doctor が legacy data を current graph として読まない

#### step gate
- review:
  - RG1/code review pass
  - QG1/QA review pass
- expected tests:
  - `python -m unittest tests.test_cli -v`
  - targeted `python -m unittest tests.test_init_update -v`
  - `python -m unittest tests.cli_runtime.test_validate -v`
  - `python -m unittest tests.cli_runtime.test_runtime_doctor_s04 -v`
  - 必要なら `python -m unittest tests.cli_runtime.test_runtime_validate_s02 -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock doctor`
- report update:
  - code review verdict、QA verdict、command evidence を `./spec-dock/active/issue/report.md` に残す

### S04 — final close readiness bundle
- target:
  - issue report
  - final review notes
- design refs:
  - issue design verification mapping
  - epic final exit contract
- step boundary:
  - single-issue close readiness を S99 reviewer が再判定できる packet を先に作る

#### update_plan（着手時に登録）
- [ ] `update_plan` に S04 の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の S04 記録位置を決めた

#### B1 — evidence packaging
- purpose:
  - installer/runtime/docs/tests/review evidence を close bundle にまとめる
- files:
  - `spec-dock/active/issue/report.md`
  - 必要なら active epic/issue spec docs

##### I1 — close packet
- slice goal:
  - AC/EC と command/test/review evidence の対応が 1 箇所で追えるようにする

###### Red
- failing test:
  - なし
- expected failure:
  - evidence が散在して close 判定しづらい

###### Green
- minimum implementation:
  - report に final evidence map と S99 input packet を記録する
- pass condition:
  - `iss-00078` 単体で epic close readiness を説明できる

###### Refactor
- 目的:
  - report と spec docs の言い回しを合わせる
- guardrail:
  - scope を広げない

#### step gate
- review:
  - S99 に渡す close packet readiness をセルフチェックできる
- expected tests:
  - S02/S03 で要求した evidence が再参照できる
- report update:
  - close packet の内容と closing evidence を `./spec-dock/active/issue/report.md` に残す

### S90 — docs impact resolution / docs refresh
- 対象:
  - installer docs
  - user-facing migration guidance
- 対応:
  - rename guidance を除去する
  - coexistence install、manual migration、manual deletion、doctor/validate roles を明記する
  - provider-side source of truth を先に更新し、必要な dogfooding docs を同期する

### S99 — final diff review quality gate
- branch diff scope:
  - installer gate、runtime observability、docs、tests、report
- required validation:
  - `python -m unittest tests.test_cli -v`
  - targeted `python -m unittest tests.test_init_update -v`
  - `python -m unittest tests.cli_runtime.test_validate -v`
  - `python -m unittest tests.cli_runtime.test_runtime_doctor_s04 -v`
  - 必要なら `python -m unittest tests.cli_runtime.test_runtime_validate_s02 -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock doctor`
- reviewer approvals:
  - SG1 spec review pass
  - RG1 implementation review pass
  - QG1 QA review pass
- report update:
  - final diff review verdict / closing evidence / no-op reason を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - report 更新後に差分確認し、追加修正があれば closing commit を作る

## 未確定事項
- なし:
  - step sequencing、review cadence、verification surface は確定

## final exit contract
- AC/EC 達成:
  - installer coexistence contract、manual migration guidance、doctor/validate observability が実装・検証済みである
- docs impact resolved:
  - rename guidance が除去され、manual migration/manual deletion が docs に反映済みである
- final diff approved:
  - SG1/RG1/QG1 が pass し、`report.md` に closing evidence が残っている

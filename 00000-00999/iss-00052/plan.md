---
種別: 実装計画書（Issue）
ID: "iss-00052"
タイトル: "Reject Non Canonical Git Issue Targets"
関連GitHub: ["#52"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-04-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00052 Reject Non Canonical Git Issue Targets — 実装計画（Execution Contract）

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
  - parser 層で fail-closed する
  - repo-scope / deps guard / checkout 契約は変えない

## マイルストーン一覧
- M1:
  - 対象:
    - shared parser に対する期待挙動を failing test で固定する
  - exit:
    - non-canonical URL-like target reject の Red が再現できる
- M2:
  - 対象:
    - shared parser を厳格化して `active set` / `deps check` の target 契約を整える
  - exit:
    - active/deps 系の新旧テストが green
- M3:
  - 対象:
    - import parity と docs impact を確認し、最終差分を review/QA に通す
  - exit:
    - required tests と review gate が pass

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - upstream / prerequisite / lower-dependency slice から先に step を組む
  - downstream / dependent slice は前提が固まってから置く
- step ordering notes:
  - S01 で shared parser contract を failing test として固定する
  - S02 は S01 で固定した contract を満たす実装変更
  - S90 は docs impact の有無を確認し、本 issue では existing docs との整合確認を行う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `active set git@github.com:owner/repo/issues/123` が invalid target で失敗し、active state も更新されない期待を test で表現できる
  - closes:
    - AC-001
    - EC-003
  - review gate:
    - failing test が現在の bug を再現していること
- S02:
  - 観測可能な振る舞い:
    - strict parser により canonical URL だけが URL target として受理される
  - closes:
    - AC-002
    - AC-003
    - AC-004
    - EC-001
    - EC-002
  - review gate:
    - active/import 回帰を含む関連 runtime test が green
- S90:
  - 観測可能な振る舞い:
    - docs 契約との不整合が残っていない
  - closes:
    - AC-001
    - AC-002
  - review gate:
    - spec/report 更新方針が明確
- S99:
  - 観測可能な振る舞い:
    - 最終 diff が parser 契約変更として妥当で、不要な副作用がない
  - closes:
    - AC-001
    - AC-002
    - AC-003
  - review gate:
    - implementation/spec/QA gate の最終 pass

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S02
- AC-004 -> S02
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S01

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S02 完了後
  - scope:
    - parser 変更が requirement/design の範囲内に収まっているか
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S02 完了後
  - scope:
    - `test_active.py` / `test_runtime_deps_s04.py` / `test_import.py` の関連回帰
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - 実装着手前と S90 時点
  - scope:
    - requirement/design/plan と実装方針の整合
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする

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
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。
- no-op の場合のみ `report.md` に理由を残し、commit を省略できる。

## 実装ステップ

### S01 — non-canonical target reject を test で固定する
- target:
  - `active set` の malformed target handling
- design refs:
  - `design.md` の `採用方針 / トレードオフ`
  - `design.md` の `インターフェース契約`
- step boundary:
  - test 追加まで。実装変更は含めない。

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — active parser regression
- purpose:
  - bug を deterministic に再現する failing test を追加する
- files:
  - `tests/cli_runtime/test_active.py`

##### I1 — reject case を Red にする
- slice goal:
  - `git@github.com:.../issues/123` を active set したとき invalid target になり、active state が不変であることを固定する

###### Red
- failing test:
  - `tests/cli_runtime/test_active.py` に non-canonical URL-like target reject case を追加し、reject 後の `spec-dock/.agent/active.json` 不変も assert する
- expected failure:
  - 現状は `spec-dock: ok (active set)` になり、期待どおり失敗しない

###### Green
- minimum implementation:
  - なし。S02 で実施
- pass condition:
  - failing test が bug を正しく再現していることを確認できる

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - failing test が issue の観測事実と一致している
- expected tests:
  - 追加した単独 test の失敗確認
  - active manifest 不変 assert の失敗確認
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — shared parser を fail-closed に寄せる
- target:
  - `parse_active_like_target()` とその利用コマンド
- design refs:
  - `design.md` の `既存実装 / 規約の理解`
  - `design.md` の `要件 → 設計マッピング`
- step boundary:
  - parser 修正と回帰テスト green まで

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — parser strictness
- purpose:
  - canonical URL full match 以外の URL-like string を reject する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py`

##### I1 — active/deps shared parser を Green にする
- slice goal:
  - non-canonical target reject と既存 success path 維持を両立する

###### Red
- failing test:
  - S01 で追加した reject test
- expected failure:
  - parser が `/issues/<n>` 部分一致で受理してしまう

###### Green
- minimum implementation:
  - `parse_active_like_target()` から broad な `/issues/<n>` 部分一致を除去または URL-like reject ガードへ置き換える
  - canonical URL、`#<n>`、`<n>`、node id は維持する
- pass condition:
  - reject test が green
  - existing active/import success tests が green

###### Refactor
- 目的:
  - reject 条件の重複が大きければ小さな helper へ整理する
- guardrail:
  - parser 契約の外へ広げない
  - import parser の意味論は変えない

#### B2 — regression sweep
- purpose:
  - shared parser 変更の影響を active/deps/import に対して確認する
- files:
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - `tests/cli_runtime/test_import.py`

##### I1 — regression を確認する
- slice goal:
  - shared parser strictness による意図しない regressions を防ぐ

###### Red
- failing test:
  - `deps check` の non-canonical URL-like reject case
  - 必要なら invalid URL / canonical URL / numeric shorthand の補助 case
- expected failure:
  - parser の副作用があれば既存 test が落ちる

###### Green
- minimum implementation:
  - 追加修正なし、既存回帰群の green 確認で足りるならそれを採用
- pass condition:
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - `tests/cli_runtime/test_import.py`

###### Refactor
- 目的:
  - テスト名と fixture を読みやすく整える
- guardrail:
  - 仕様変更を増やさない

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - none
- 対応:
  - `workflow_issue.md` / `reference_github.md` / `reference_deps.md` は shared parser 契約と矛盾しないことを確認する
  - docs 変更が不要でも `report.md` に確認結果を残す

### S99 — final diff review quality gate
- branch diff scope:
  - `commands/targets.py`
  - `tests/cli_runtime/test_active.py`
  - 必要なら関連 test のみ
- required validation:
  - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_import -v`
  - 追加した reject case の individual run
- reviewer approvals:
  - implementation review pass
  - QA review pass
  - spec review pass
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- なし

## final exit contract
- AC/EC 達成:
  - non-canonical URL-like target が active set と deps check で reject され、canonical URL / numeric / node-id 経路は維持されている
- docs impact resolved:
  - docs と実装契約の不整合がない
- final diff approved:
  - implementation/spec/QA gate が pass し、`report.md` に証跡が残っている

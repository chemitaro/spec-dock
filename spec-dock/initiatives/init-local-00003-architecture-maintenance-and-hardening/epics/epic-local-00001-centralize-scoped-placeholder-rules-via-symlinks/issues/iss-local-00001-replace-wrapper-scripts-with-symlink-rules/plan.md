---
種別: 実装計画書（Issue）
ID: "iss-local-00001"
タイトル: "Replace Wrapper Scripts With Symlink Rules"
関連GitHub: [""]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md"]
親: ["epic-local-00001", "init-local-00003"]
---

# iss-local-00001 Replace Wrapper Scripts With Symlink Rules — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - lowercase path 維持
  - wrapper と symlink の二重運用禁止

## マイルストーン一覧
- M1:
  - 対象:
    - 契約固定と変更対象の洗い出し
  - exit:
    - requirement / design / plan approved
- M2:
  - 対象:
    - provider docs/assets / installer / runtime の symlink contract 実装
  - exit:
    - tests green、docs/rules と新規生成 contract が整合

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - provider docs/assets と node creation が wrapper なしの `rules.md` symlink contract を生成できる
  - closes:
    - AC-002, EC-002
  - review gate:
    - implementation review
- S02:
  - 観測可能な振る舞い:
    - installer `init/update` が `docs/rules/` 原本を配布し、新規生成フローの前提を揃える
  - closes:
    - AC-001, EC-001, EC-003
  - review gate:
    - implementation review + QA review
- S03:
  - 観測可能な振る舞い:
    - discussion/new/validate 系 regression が維持され、wrapper 前提の docs/tests が更新される
  - closes:
    - AC-003
  - review gate:
    - QA review

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S01
- AC-003 -> S03
- EC-001 -> S02
- EC-002 -> S01, S03
- EC-003 -> S02

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - 実装完了後
  - scope:
    - symlink path、collision、copy semantics、dogfooding diff
- QG1 QA review:
  - timing:
    - tests 実行後
  - scope:
    - regression coverage と不足リスク
- SG1 spec review:
  - timing:
    - final close-out 前
  - scope:
    - requirement/design との整合

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小単位 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。

## 実装ステップ

### S01 — wrapper なしの rules symlink scaffold を生成できる
- target:
  - provider-side docs/assets
  - runtime create flow
- design refs:
  - `docs/rules/` 原本
  - 新規 node 作成時の symlink 明示配置
- step boundary:
  - runtime `new` の public CLI contract は変えない

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — assets/runtime
- purpose:
  - `docs/rules/` 原本と新規 node 向け symlink 配置を導入する
- files:
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `src/spec_dock/assets/spec_dock/templates/**`
  - runtime create flow

##### I1 — runtime scaffold
- slice goal:
  - `new initiative` `new epic` `new issue` で `rules.md` symlink が作られる

###### Red
- failing test:
  - wrapper presence 前提を置き換える runtime new tests
- expected failure:
  - 現状は wrapper が存在し、`rules.md` symlink ではない

###### Green
- minimum implementation:
  - docs 原本追加、wrapper 削除、create flow で symlink 明示配置
- pass condition:
  - runtime new tests が通る

###### Refactor
- cleanup target:
  - symlink helper 共通化、docs/rules 参照整理
- invariants to keep green:
  - no wrapper、discussion sequencing non-regression

#### step gate
- review:
  - create/runtime path の整合
- expected tests:
  - `tests/cli_runtime/test_new.py`
  - 必要な runtime unit/integration tests
- observable command:
  - `python -m unittest tests.cli_runtime.test_new -v`
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — installer が docs/rules 原本を配布できる
- target:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - `src/spec_dock/assets/spec_dock/docs/`
- design refs:
  - `docs/rules/` 原本配布
- step boundary:
  - managed asset replacement の既存責務を壊さない
- observable command:
  - `python -m unittest tests.test_init_update -v`

### S03 — docs/tests/regression を新契約へ揃える
- target:
  - wrapper tests removal/replacement
  - workflow/docs wording refresh
  - regression execution
- design refs:
  - runtime command 正本化
- step boundary:
  - 無関係な docs rewrite はしない
- observable command:
  - `python -m unittest discover -v`

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - wrapper 前提の記述を runtime command + `docs/rules/` 前提へ更新
  - 既存 checked-in tree の wrapper は legacy / out of scope であり、新規生成 contract と混同しない

### S99 — final diff review quality gate
- branch diff scope:
  - provider docs/assets / runtime / installer / tests / docs
- required validation:
  - 対象 tests
  - `rg --files | rg '[A-Z]'` 非増加確認
- reviewer approvals:
  - code review
  - QA review

## 未確定事項
- なし:
  - `docs/rules/` 本文は最小記述方針で進める。

## final exit contract
- AC/EC 達成:
  - symlink contract と non-regression の証跡がある
- docs impact resolved:
  - wrapper 前提の docs/tests が残っていない
- final diff approved:
  - review / QA 結果を report に記録済み

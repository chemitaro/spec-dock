---
種別: 実装計画書（Issue）
ID: "iss-00023"
タイトル: "runtime CLI の責務分割と sync 状態導出をリファクタリングする"
関連GitHub: ["#23", "https://github.com/chemitaro/spec-dock/issues/23"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-03-11"
依存: ["requirement.md", "design.md"]
親: []
---

# iss-00023 runtime CLI の責務分割と sync 状態導出をリファクタリングする — 実装計画（TDD: Red → Green → Refactor）

## この計画で満たす要件ID (必須)
- 対象AC: AC-001, AC-002, AC-003, AC-004
- 対象EC: EC-001, EC-002
- 対象制約（該当があれば）: unittest green, lowercase path, shipped assets の docs/tests 同期

## ステップ一覧（観測可能な振る舞い） (必須)
- [ ] S01: `sync` の status/source 導出が helper/module に分離され、`app.py` から読みやすく参照できる
- [ ] S02: GitHub なし時の cached status 利用が明示的な構造で扱われ、`deps check` / `active set` は互換確認対象として関連回帰テストが更新される
- [ ] S90: README の CLI 例が実装契約と一致する
- [ ] S99: 全体テストと最終 diff review を通過する

### 要件 ↔ ステップ対応表 (必須)
- AC-001 → S01
- AC-002 → S02
- AC-003 → S90
- AC-004 → S99
- EC-001 → S02
- EC-002 → S90
- 非交渉制約 → S01, S02, S90, S99

---

## 実行ルール（全ステップ共通） (必須)
- plan 全体は実装着手前に承認する。
- 各ステップは 1 つの観測可能な振る舞いを単位とする。
- 各ステップは `Red → Green → Refactor → review → fix → re-review → report → commit/no-op` の順で完了する。
- reviewer の blocking 指摘が残っている間は、そのステップを完了扱いにしない。
- docs impact があるため `S90` を必須で通す。
- 最後に `git diff main...HEAD` を対象に `S99 final diff review quality gate` を実施し、spec reviewer に今回の差分スコープをレビューさせる。

---

## 実装ステップ（各ステップは“観測可能な振る舞い”を1つ） (必須)

### S01 — sync の status/source 導出が helper/module に分離される (必須)
- 対象: AC-001
- 設計参照:
  - 対象IF/API: IF-001, IF-002, IF-003
  - 対象テスト: `tests/test_cli.py` の `sync` 系テスト
- このステップで「追加しないこと（スコープ固定）」:
  - 全 command の全面再編
  - GitHub adapter の全面刷新

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に S01 の作業単位を登録する

#### 期待する振る舞い（テストケース） (必須)
- Given: `sync` が issue 状態を導出する
- When: code reader が status 導出箇所を見る
- Then: helper/module から status/source 導出責務を把握できる
- 観測点: `app.py`, 新規 helper/module, `tests/test_cli.py`
- 追加/更新するテスト: `tests/test_cli.py` の `sync` 系ケース

#### Red（失敗するテストを先に書く） (任意)
- 期待する失敗:
  - helper 抽出前提の新規回帰テストが失敗する

#### Green（最小実装） (任意)
- 変更予定ファイル:
  - Add: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/sync_state.py`
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
- 実装方針:
  - 既存の `_sync()` から pure な導出処理を外だしする

#### Refactor（振る舞い不変で整理） (任意)
- 目的:
  - local variable 群を意味のある helper 呼び出しへ置き換える
- 変更対象:
  - `app.py`, `sync_state.py`

#### ステップ末尾（省略しない） (必須)
- [ ] step diff を reviewer にレビュー依頼した
- [ ] blocking 指摘を解消し、report に記録した
- [ ] 期待するテストを実行し、成功した
- [ ] `report.md` に実行コマンド/結果/変更ファイルを記録した
- [ ] `update_plan` を更新した
- [ ] 実差分がある場合は step-scoped commit、ない場合は no-op を記録した

---

### S02 — GitHub なし時の cached status 利用が明示的に扱われる (必須)
- 対象: AC-002, EC-001
- 設計参照:
  - 対象IF/API: IF-001
  - 対象テスト: cached/GitHub 分岐テスト、`deps check` / `active set` の互換確認テスト
- このステップで「追加しないこと（スコープ固定）」:
  - artifact schema の不要な大変更
  - `deps check` / `active set` 自体の主機能リファクタ

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に S02 の作業単位を登録する

#### 期待する振る舞い（テストケース） (必須)
- Given: `--github` なしで `sync` / `deps check` / `active set` を扱うコード
- When: cached snapshot が存在する
- Then: cached 由来であることがコード上で追える
  - Then: cached 由来であることがコード上で追え、`deps check` / `active set` は必要最小限の追従または互換確認に留まる
- 観測点: helper/module, 関連テスト
- 追加/更新するテスト: `tests/test_cli.py` の cached status ケースと `deps check` / `active set` 互換ケース

#### Red（失敗するテストを先に書く） (任意)
- 期待する失敗:
  - source 明示前提のテストが失敗する

#### Green（最小実装） (任意)
- 変更予定ファイル:
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - Modify/Add: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/sync_state.py`
  - Modify: `tests/test_cli.py`

#### Refactor（振る舞い不変で整理） (任意)
- 目的:
  - cached/GitHub 分岐の意図を命名で表す

#### ステップ末尾（省略しない） (必須)
- [ ] step diff を reviewer にレビュー依頼した
- [ ] blocking 指摘を解消し、report に記録した
- [ ] 期待するテストを実行し、成功した
- [ ] `report.md` に実行コマンド/結果/変更ファイルを記録した
- [ ] `update_plan` を更新した
- [ ] 実差分がある場合は step-scoped commit、ない場合は no-op を記録した

---

### S90 — docs impact resolution / docs refresh を行う (条件付き必須)
- 条件: docs impact あり
- 対象: `README.md`
- Given: CLI 例と実装にズレがある
- When: README を更新する
- Then: 実装済み command に一致する
- ステップ末尾:
  - [ ] docs impact の判定結果を `report.md` に記録した
  - [ ] `README.md` を更新した、または no-op 理由を記録した
  - [ ] reviewer に確認を依頼し、承認レベルに達した

### S99 — final diff review quality gate を通す (必須)
- 対象: このブランチの差分全体
- Given: 実装ステップと docs refresh が完了している
- When:
  - `python -m unittest discover -v` を実行する
  - `git diff main...HEAD` を reviewer が確認する
  - `git diff main...HEAD` を対象に spec reviewer が今回の実装差分スコープをレビューする
- Then:
  - blocking finding が残っていない
  - reviewer が承認するまで修正と再レビューを反復する
- ステップ末尾:
  - [ ] 全体テストが成功した
  - [ ] reviewer の最終 verdict を `report.md` に記録した
  - [ ] 修正があれば commit、なければ no-op を記録した

---

## 未確定事項（TBD） (必須)
- 該当なし

## 完了条件（Definition of Done） (必須)
- 対象 AC / EC がすべて満たされ、テストで保証されている
- MUST NOT / OUT OF SCOPE を破っていない
- docs impact が解決されている
- `S99 final diff review quality gate` で reviewer 承認レベルに達している

## 省略/例外メモ (必須)
- step-scoped commit は user 指示があれば実施し、現時点では no-op 記録で運用可能

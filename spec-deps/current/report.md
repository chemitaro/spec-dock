---
種別: 実装報告書（Issue）
ID: "iss-00023"
タイトル: "runtime CLI の責務分割と sync 状態導出をリファクタリングする"
関連GitHub: ["#23", "https://github.com/chemitaro/spec-dock/issues/23"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-03-11"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# iss-00023 runtime CLI の責務分割と sync 状態導出をリファクタリングする — 実装報告（LOG）

## 実装サマリー (任意)
- runtime CLI の `sync` 周辺責務を整理し、README と実装契約のズレを解消する issue として進行する。

## 実装記録（セッションログ） (必須)

### 2026-03-11 00:00 - 00:30

#### 対象
- Step: spec setup
- AC/EC: AC-001, AC-002, AC-003

#### 実施内容
- GitHub issue `#23` を作成した。
- 作業ブランチ `iss-00023-runtime-cli-refactor` へ checkout した。
- `spec-deps/current/` を issue `iss-00023` の正本へ更新した。
- newer issue 文書フォーマットに合わせて current 文書を差し替えた。
- requirement / design / plan を spec review に通し、指摘反映後に pass を取得した。

#### 実行コマンド / 結果
```bash
gh issue create --title 'runtime CLI の責務分割と sync 状態導出をリファクタリングする' ...
git checkout -b iss-00023-runtime-cli-refactor

issue #23 を作成し、対応ブランチへ切り替えた。
```

#### 変更したファイル
- `spec-deps/current/requirement.md` - newer issue template に合わせて要件を更新
- `spec-deps/current/design.md` - newer issue template に合わせて設計を更新
- `spec-deps/current/plan.md` - newer issue template に合わせて計画を更新
- `spec-deps/current/report.md` - newer issue template に合わせて報告書を更新

#### コミット
- 未実施

#### メモ
- 次段で requirement/design/plan を spec review に通してから実装へ進む。

### 2026-03-11 00:30 - 01:10

#### 対象
- Step: spec review gate
- AC/EC: AC-001, AC-002, AC-003

#### 実施内容
- requirement.md を spec reviewer にレビュー依頼し、AC-002 の契約固定、AC-001 の客観性、README 修正範囲の明確化を反映した。
- design.md を spec reviewer にレビュー依頼し、source 契約の internal-only 固定、`active set` の互換確認対象化を反映した。
- plan.md を spec reviewer にレビュー依頼し、`deps check` / `active set` の互換確認境界と final spec diff review gate を明記した。
- requirement/design/plan の pass を確認した。

#### 実行コマンド / 結果
```bash
spec reviewer x 3

requirement.md: pass
design.md: pass
plan.md: pass
```

#### 変更したファイル
- `spec-deps/current/requirement.md` - review 指摘を反映
- `spec-deps/current/design.md` - review 指摘を反映
- `spec-deps/current/plan.md` - review 指摘を反映
- `spec-deps/current/report.md` - review 履歴を追記

#### コミット
- 未実施

#### メモ
- 次段で dev_coder に実装委任し、実装完了後に code review / QA / final spec diff review を行う。

### 2026-03-11 01:10 - 02:20

#### 対象
- Step: S01, S02, S90, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002

#### 実施内容
- `app.py` で `_IssueStatusResolution`, `_load_cached_issue_snapshot`, `_resolve_issue_statuses`, `_build_progress_map` を導入し、`_sync()` から状態導出を in-file helper へ委譲する形で責務分割した。
- `tests/test_cli.py` に cached source 解決の内部表現を確認する回帰テストを追加した。
- README の ADR 作成例を `new doc adr` 契約へ修正した。
- code review を実施し、コード差分について blocking finding なしを確認した。
- final spec review で設計差分不整合と README 未修正の指摘を受けたため、design と README を修正して再整合させた。
- `python -m unittest discover -v` を実行し、162 tests が成功した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -v

Ran 162 tests in 17.045s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - sync 状態導出 helper を抽出
- `tests/test_cli.py` - cached source 解決のテストを追加
- `README.md` - `new doc adr` 契約へ修正
- `spec-deps/current/design.md` - 実装に合わせて in-file helper 方針へ更新
- `spec-deps/current/report.md` - 実装/検証ログを追記

#### コミット
- 未実施

#### メモ
- final spec reviewer による diff review が pass し、issue スコープの品質ガードを通過した。

## 省略/例外メモ (必須)
- Initiative/Epic は存在しないため issue 単位で進める

---
種別: 設計書（Issue）
ID: "manual-regression-sweep"
タイトル: "manual-tests 環境を再整備し手動回帰テストで潜在バグを洗い出す"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-15"
依存: ["requirement.md"]
親: []
---

# manual-regression-sweep manual-tests 環境を再整備し手動回帰テストで潜在バグを洗い出す — 設計（HOW）

## 全体方針
- 今回は `manual-tests/` を clean slate に近い状態へ整理したうえで、新しい isolated workspace を作る。
- テスト成果物は `manual-tests/reports/<date>-manual-regression-sweep/` に集約する。
- 正本は次の 3 つに分ける。
  - `checklist.md`: テスト計画
  - `execution-log.md`: 実施記録
  - `summary.md`: 最終報告

## 対象領域
- `init`
- `update`
- runtime `new initiative|epic|issue|doc`
- `active`
- `sync`
- `deps`
- `validate`
- `import`
- 複数回作成時の採番・整合性
- active pointer / symlink 的導線
- generated artifact の整合性

## テスト観点
- 正常系:
  - 単純作成
  - 複数件連続作成
  - active 切替
  - sync / validate / deps の基本操作
- 境界系:
  - 同一種別を 2件, 3件, 4件作る
  - title / slug / id 指定の境界
  - active 未設定 / partial state
- 異常系:
  - duplicate / collision
  - invalid input
  - stale / partial artifact
  - broken active 導線
- 複雑系:
  - 紛らわしい順番での操作
  - 同じ対象への繰り返し実行
  - 並列 create
  - create 後に validate/sync/deps/active を交差実行

## 実行構成
- consultant:
  - テスト観点の洗い出しと test plan の第三者レビュー
- utility_worker:
  - manual-tests 整理
  - workspace 作成
  - テスト実施
  - 実施記録と summary 反映
- main agent:
  - 契約文書の固定
  - 調査観点の統合
  - 最終結果の取りまとめ

## 記録ルール
- `execution-log.md` の各項目には必ず以下を残す。
  - 実行コマンド
  - 期待結果
  - 実際の結果
  - 副作用
  - 確認したファイル / 状態
  - 判定
- `summary.md` では以下を整理する。
  - 発見 bug 一覧
  - 再現性
  - 影響度
  - 推定原因
  - 推奨 next action

## ガードレール
- 既存の manual test 記録で残すべきものは `manual-tests/README.md` のみ保持する。
- live GitHub を使う場合でも、破壊的な外部操作は極力避ける。
- 今回の sweep は bug 洗い出しが目的であり、成功率を上げるための操作回避はしない。


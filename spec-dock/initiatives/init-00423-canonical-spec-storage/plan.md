---
種別: 計画書（Initiative）
ID: "init-00423"
タイトル: "Canonical Spec Storage Architecture"
関連GitHub: ["#423"]
状態: "draft"
最終更新: "2026-10-25"
依存: ["requirement.md", "design.md"]
---

# init-00423 Canonical Spec Storage Architecture — 計画

詳細: [Scope Layering Guide](../../docs/authoring/scope-layering.md)

## 目標
Initiative として達成する成果を記述する。

## 順序・依存

1. epic-00424：仕様の内容の正本を `spec-dock/canonical` に、構造の正本を GitHub Issue に移す。GitHub の構造を一括で取得して持つ仕組みと、つなぎの Markdown と PlantUML のダッシュボードも作る。
2. epic-00425：epic-00424 の正本と構造のスナップショットを読む HTML のダッシュボードを作り、仕様の文書を CUE と HTML に移す。epic-00424 に依存する（登録済み）。要件の議論は、epic-00424 を終えた後に行う。

## 実装step
成果を届ける Epic と主要なマイルストーンを記述する。

## 検証
全体として成果を確認する方法を記述する。

## rollback
問題時に戻す範囲と判断を記述する。

## exit / handoff
Epic への引き渡しと Initiative 完了条件を記述する。

---
種別: 計画書（Initiative）
ID: "init-00423"
タイトル: "Canonical Spec Storage Architecture"
関連GitHub: ["#423"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
---

# init-00423 Canonical Spec Storage Architecture — 計画

詳細: [Scope Layering Guide](../../docs/authoring/scope-layering.md)

## 目標
Initiative として達成する成果を記述する。

## 順序・依存

1. epic-00424：仕様の内容の正本を `spec-dock/canonical` に、構造の正本を GitHub Issue に移す。GitHub の構造を一括で取得して持つ仕組みと、つなぎの Markdown と PlantUML のダッシュボードも作る。利用者の5つのリポジトリをすべて移し、従来の仕組みのコードを撤去して、SpecDock 0.4.0 にする。
2. epic-00427：epic-00424 の構造のスナップショットとカタログを読む HTML のダッシュボードを作る。2026-10-25 に epic-00425 から分け、epic-00424 と並べて要件を整理している。構造の画面（段階1）は epic-00424 の後、epic-00425 の前に出し、文書を描く機能（段階2）は epic-00425 の後に足す。Epic 単位の依存は付けず、実装の Issue を作るときに、epic-00424 の該当する Issue への依存を付ける。
3. epic-00425：仕様の文書を CUE（エージェントが確かめるもの）と HTML（人が読むもの）に移す。epic-00424 に依存する（登録済み）。要件の議論は、epic-00424 を終えた後に行う。

## 実装step
成果を届ける Epic と主要なマイルストーンを記述する。

## 検証
全体として成果を確認する方法を記述する。

## rollback
問題時に戻す範囲と判断を記述する。

## exit / handoff
Epic への引き渡しと Initiative 完了条件を記述する。

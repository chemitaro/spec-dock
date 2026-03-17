---
種別: 要件定義書（Issue）
ID: "manual-regression-sweep"
タイトル: "manual-tests 環境を再整備し手動回帰テストで潜在バグを洗い出す"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-15"
親: []
---

# manual-regression-sweep manual-tests 環境を再整備し手動回帰テストで潜在バグを洗い出す — 要件定義（WHAT / WHY）

## 目的
- `manual-tests/` を整理し、実使用を想定した手動テスト環境を再整備する。
- `spec-dock` の通常操作と紛らわしい操作を網羅的に手動実行し、既知バグ以外の潜在バグを洗い出す。
- テスト計画、実施記録、最終報告を repo 内に正本として残す。

## 背景・現状
- `manual-tests/` には過去の workspace や report が多数残っており、今回の sweep 用としては散らかっている。
- これまでの手動確認は「1件作れて OK」といった単発確認を通過していた可能性がある。
- 今回、`new epic` の duplicate id が実使用に近い並列操作で顕在化し、単発確認では不十分だと判明した。
- 今後の bugfix を正しく優先づけるには、通常操作と複雑操作を含む manual regression sweep が必要である。

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - `spec-dock` の maintainer
  - `spec-dock` を操作する coding agent / 開発者
- 代表シナリオ:
  - 新しい workspace を作り、initiative / epic / issue / doc を複数作成する。
  - active / sync / deps / validate / import などを組み合わせて運用する。
  - 紛らわしい指定、複数回実行、複数リソース作成、整合性確認を行う。

## スコープ
- MUST:
  - `manual-tests/` を今回の sweep 用に整理する。
  - 手動テスト計画を先に作成する。
  - 手動テストの実施記録を残す。
  - 最終報告を作成する。
  - 単発操作ではなく、複数リソース作成と整合性確認を含める。
  - 通常操作、境界操作、紛らわしい操作、複雑操作を含める。
  - duplicate id 以外の潜在バグも広く洗い出す。
- MUST NOT:
  - 事前計画なしに場当たりで試すだけにしない。
  - 実行ログを残さずに結果だけまとめない。
  - 1件成功しただけで健全性を判断しない。
- OUT OF SCOPE:
  - バグ修正そのもの
  - 自動テストコードの追加
  - GitHub live 環境を前提とした外部依存テストの常時化

## 境界
- Always:
  - テスト計画、実施記録、最終報告を分離して残す。
  - 1操作ごとにコマンド、結果、副作用、確認項目を記録する。
  - 2件、3件、4件と複数リソースを連続で作り、整合性を確認する。
- Ask:
  - 外部サービスへの破壊的操作が必要な場合
  - テスト中に重大なデータ破損が起きた場合
- Never:
  - 本番的な外部 repo や実 GitHub Issue に対して無断で破壊的変更しない。

## 非交渉制約
- `manual-tests/README.md` は保持する。
- manual test は isolated workspace で行う。
- 失敗結果も成功結果と同じ粒度で記録する。
- 報告では、再現条件、観測結果、推定原因、影響度を切り分ける。

## 受け入れ条件
- AC-001:
  - Given:
    - 散らかった `manual-tests/` がある
  - When:
    - 今回の sweep 用に整備する
  - Then:
    - 今回のテスト対象 workspace / reports が識別しやすく整理されている
- AC-002:
  - Given:
    - 手動テストを始める前
  - When:
    - テスト実施に入る
  - Then:
    - テスト計画書が存在し、網羅観点と実施順が定義されている
- AC-003:
  - Given:
    - manual regression sweep を実施する
  - When:
    - 通常操作と複雑操作を進める
  - Then:
    - 複数リソース作成、整合性確認、紛らわしい操作、複合操作が実行され、記録される
- AC-004:
  - Given:
    - テスト実施後
  - When:
    - 報告をまとめる
  - Then:
    - 発見した問題、再現条件、影響、推定原因、次アクションがレポート化されている


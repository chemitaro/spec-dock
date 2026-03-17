---
種別: 実装計画書（Issue）
ID: "manual-regression-sweep"
タイトル: "manual-tests 環境を再整備し手動回帰テストで潜在バグを洗い出す"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-15"
依存: ["requirement.md", "design.md"]
親: []
---

# manual-regression-sweep manual-tests 環境を再整備し手動回帰テストで潜在バグを洗い出す — 実装計画

## ゴール
- `manual-tests/` を整理し、今回の sweep 用の clean workspace と report 一式を作る。
- consultant による test plan を作成する。
- utility_worker による manual regression sweep を実施する。
- 再現 bug と潜在 bug を summary にまとめる。

## ステップ
- S01:
  - `manual-tests/` を整理する
  - `README.md` を残し、過去 workspace / reports を一掃する
- S02:
  - consultant に網羅的テスト観点の洗い出しを依頼する
  - `checklist.md` を作成する
- S03:
  - isolated workspace を作成する
  - installer / init / update の基本確認を行う
- S04:
  - initiative / epic / issue / doc を複数作成する
  - 2件, 3件, 4件作成時の整合性を確認する
- S05:
  - active / validate / sync / deps / import を交差実行する
  - 通常操作と紛らわしい操作を混ぜる
- S06:
  - 並列 create や collision 系を含む bug 誘発ケースを実施する
- S07:
  - `execution-log.md` を整理し、`summary.md` を作成する
- S08:
  - live GitHub repo を使った連携 manual test を実施する
  - create/import/active/deps/sync の GitHub 連携経路を確認する
  - GitHub issue の create / link / close-ready state の整合を確認する

## 実施順序
- cleanup を最初に行う
- plan を先に固定する
- 正常系から入り、次に複数作成、最後に異常系・複雑系へ進む
- 既知バグ確認だけで終わらず、隣接操作を意図的に混ぜる
- live GitHub 連携は local/stub sweep の後段で実施する

## 完了条件
- checklist / execution-log / summary が揃っている
- 複数リソース作成と複合操作の結果が記録されている
- bug 一覧に再現条件と影響が付いている
- live GitHub 連携を実施した場合は、外部副作用を含む結果が明示的に記録されている

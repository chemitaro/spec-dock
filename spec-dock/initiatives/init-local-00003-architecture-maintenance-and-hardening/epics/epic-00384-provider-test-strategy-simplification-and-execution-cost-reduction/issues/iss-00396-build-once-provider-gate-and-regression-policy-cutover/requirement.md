---
種別: 要件定義書（Issue）
ID: "iss-00396"
タイトル: "固定ディレクトリ再配置への実装切替"
状態: "approved"
最終更新: "2026-09-19"
---

# Issue #396 — 単純な配置処理への切替

## 正本と変更承認

2026-09-19のユーザー指示と、親Epicの新しい[Requirement](../../requirement.md)、[Design](../../design.md)、[Plan](../../plan.md)に従う。旧build-once qualification計画・P02・Wire v12・issue-local schema/ownership/fault/receipt artifactは履歴であり、実装入力ではない。

## 実装すること

親R1〜R10を実装する。#392の複雑なlifecycleを小さい固定ディレクトリ再配置へ置換し、旧専用テストも撤去する。#395の残る機能に関する修正は保持する。新しいCPU認証・history evaluatorは作らない。

## 合格条件

親の受入条件1〜7を満たす。特に配布元との一致、非対象データ不変、古い内部ファイルの除去、失敗報告と再実行、導入後runtime起動、通常の機能回帰とpackage配布を確認する。旧プロトコルの後方互換は要求しない。

## 非ゴール

データの削除や書換え、GitHub設定の自動変更、Issue #395のclose/reopen、新しい並行更新/トランザクション/計測基盤を追加しない。

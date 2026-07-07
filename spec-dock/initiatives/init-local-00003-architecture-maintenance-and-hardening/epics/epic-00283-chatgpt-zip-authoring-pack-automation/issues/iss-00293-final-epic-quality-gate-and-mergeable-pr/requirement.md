---
種別: 要件定義書（Issue）
ID: "iss-00293"
タイトル: "最終品質ゲートとマージ可能な Pull Request を作成する"
関連GitHub: ["#293"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00293 最終品質ゲートとマージ可能な Pull Request を作成する — Issue 要件定義

## 目的

この Issue は、`epic-00283` の最後に実行する Epic 単位の品質ゲートである。`iss-00284` から `iss-00292` までを個別 PR に分割せず、各 Issue の完了後に `issue finish` して次 Issue を `issue start` するリレー型で進め、すべての先行 Issue が完了した後に、この Issue で手動テスト、品質確認、レビュー指摘対応、再 push、マージ可能な Pull Request 作成までを担当する。

この Issue は、先行 Issue の主要実装を肩代わりするものではない。Epic 全体の統合品質を確認し、発見された不具合・仕様不整合・レビュー指摘を Epic スコープ内で修正し、PR が mergeable になる状態まで運ぶための実務 Issue である。

## スコープ

### 対象

- `iss-00284` から `iss-00292` までの完了証跡確認。
- Epic 単位の `spec-dock validate` と関連テストの実行。
- Epic の manual test evidence 作成。
- Pull Request の作成または更新。
- CI、レビュー、自己レビュー、手動テストで見つかった不具合・仕様不整合の修正。
- 修正後の再検証、再 push、mergeable 状態の確認。
- Epic `report.md` とこの Issue `report.md` への最終証跡記録。
- Pull Request 作成前に、ChatGPT Use / Oracle 実行まわりの個人環境絶対パス依存を解消し、SpecDock 側の backend command adapter / invocation contract を検証すること。

### 対象外

- `iss-00284` から `iss-00292` で定義された主要実装 slice を、この Issue で先取りして実装すること。
- 個別 Issue ごとに Pull Request を作成すること。
- Epic 外の機能追加や、品質ゲートで発見された不具合と無関係なリファクタリング。
- レビュー未通過の ChatGPT output を、そのまま正本完了として扱うこと。
- Oracle 本体、ChatGPT automation、ユーザー個人環境の `oracle-chatgpt` wrapper を SpecDock repo に抱え込むこと。
- 個人環境固有の ChatGPT Use / Oracle wrapper 絶対パスを正式ワークフローやスクリプトに直書きすること。

## 受け入れ条件

- AC-001: `iss-00284` から `iss-00292` までの実装が完了し、それぞれの `report.md` に完了証跡がある。
- AC-002: Epic 単位で `./spec-dock/scripts/spec-dock validate` が成功している。
- AC-003: 変更範囲に対して必要な自動テストまたは代替検証が実行され、結果がこの Issue の `report.md` に記録されている。
- AC-004: Epic の manual test evidence が作成され、成功、失敗、未実施、代替確認の区別が記録されている。
- AC-005: Pull Request が作成または更新され、対象ブランチが GitHub に push されている。
- AC-006: CI、レビュー、手動テストで発見された P0/P1 相当の不具合またはブロッカーが解消され、再検証結果が記録されている。
- AC-007: Pull Request が mergeable であること、または mergeable でない場合は残ブロッカーと次アクションが明記されている。
- AC-008: 個別 Issue ごとに PR を作成していないことが Epic `report.md` またはこの Issue `report.md` から確認できる。
- AC-009: 不具合修正がこの Epic のスコープ内に収まり、無関係な機能追加や広範なリファクタリングを含まない。
- AC-010: Epic `report.md` に最終品質ゲート、手動テスト、PR URL、mergeable 確認の証跡が追記されている。
- AC-011: SpecDock repo 内の正式ワークフローやスクリプトが、個人環境固有の ChatGPT Use / Oracle wrapper 絶対パスに依存していない。
- AC-012: ChatGPT / Oracle backend command は `SPECDOCK_CHATGPT_COMMAND` を第一候補、`ORACLE_CHATGPT_COMMAND` を互換 fallback とする設定、または同等の設定ファイル / CLI 引数で差し替え可能であり、未設定時は明確なエラーメッセージで fail する。
- AC-013: 既存のローカル `oracle-chatgpt` wrapper は、ユーザー環境で指定できる backend の一例としてのみ扱われ、SpecDock repo の必須依存として扱われない。

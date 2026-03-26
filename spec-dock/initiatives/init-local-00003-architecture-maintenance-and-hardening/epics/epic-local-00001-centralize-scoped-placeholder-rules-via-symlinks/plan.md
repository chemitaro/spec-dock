---
種別: 計画書（Epic）
ID: "epic-local-00001"
タイトル: "Centralize scoped placeholder rules via symlinks"
関連GitHub: [""]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-local-00001 Centralize scoped placeholder rules via symlinks — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003

## Issue 分割方針
- slicing principle:
  - まず provider/docs/template/runtime/installer をまたぐ contract を 1 issue で閉じる。dogfooding 専用でシンプルな変更に留める。
- exceptions:
  - 既存 tree cleanup や docs 本文粒度の拡張が必要になった場合だけ follow-up 化する。

## Issue 一覧（順序 / tranche 付き）
- iss-local-00001:
  - 目的:
    - wrapper script 依存を除去し、`docs/rules/` を正本にした新規生成向け rules symlink contract を provider assets / installer / runtime / docs / tests まで通して成立させる。
  - deliverable:
    - `docs/rules/` 原本
    - 新規 node 向け symlink 生成設計
    - runtime / installer regression tests
    - wrapper 廃止に合わせた docs 更新
  - tranche:
    - tranche-1 / now
  - closes:
    - E-RQ-001, E-RQ-002, E-RQ-003
  - depends on:
    - なし

## 統合チェックポイント
- G1 decomposition review:
  - issue requirement/design/plan で symlink contract と影響範囲が固定されている。
- G2 integration readiness:
  - provider docs/assets、installer、runtime、tests の変更が揃っている。
- G3 rollout/docs impact:
  - 新規生成 contract と docs 導線が一致しており、既存 checked-in tree は legacy / out of scope と明記されている。
- G9 final epic spec review:
  - E-AC ごとの証跡と未解決事項が report に残っている。

## 品質ゲート
- test / observability / migration / docs:
  - `init/update/new` の regression が通る。
  - symlink 観測テストが入る。
  - docs/workflow に wrapper 前提が残らない。

## ロールアウト / docs impact
- rollout order:
  - provider docs/assets更新 -> installer/runtime更新 -> tests更新 -> docs refresh
- contract / docs refresh:
  - runtime command を正本とする docs 表記へ寄せる。

## Issue readiness contract
- Issue に要求する最低条件:
  - `docs/rules/` 配置案が明記されている。
  - runtime/installer/test/docs の変更対象が列挙されている。
  - symlink contract の検証方法がある。

## final exit contract
- E-AC closure:
  - 全 E-AC に対して passing evidence がある。
- integration / rollout complete:
  - 新規 repo と新規生成 node で symlink contract が確認できる。
- docs impact resolved:
  - wrapper 前提の案内が repo docs に残っていない。

## 依存 / ブロッカー
- D-001:
  - filesystem の symlink サポート

## 未確定事項
- なし:
  - `docs/rules/` は既存 workflow / naming / phase docs 参照中心で進める。

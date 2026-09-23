---
種別: 実装計画書（Issue）
ID: "iss-00407"
タイトル: "Fix Workbench Readme Only Git Ignore Contract"
関連GitHub: ["#407"]
状態: "draft"
最終更新: "2026-09-24"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00407 Fix Workbench Readme Only Git Ignore Contract — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level
暫定 `standard`。修正対象は小さいが、既存 workspace の設定ファイル更新は利用者編集を損なう可能性がある。未知 drift の扱いが拡大したり、Git index migration を含める判断が出た場合は再評価する。

## 目標
Requirement の AC-407-01〜04 を、provider-first の実装と実 Git テストで満たす。利用先 project の既追跡 payload は対象に含めない。

## 順序・依存
1. `.gitignore` 所有権、既知旧版、未知独自編集時の update 挙動を Design で確定する。
2. 現行の fresh root 欠落、update 欠落・旧版保持、README-only 実効規則を focused Red tests で再現する。
3. installer / 配布 asset を修正し、dogfooding projection を正規更新経路で確認する。
4. focused tests、通常回帰、`validate`、差分を確認して実装結果を Report に記録する。

## 実装step
- S01: provider `.gitignore` の正本、現行 installer の対象範囲、既知旧版候補を inventory する。
- S02: fresh / existing / partial init と4 scope の ignore matrix をテストで固定する。
- S03: 決定済みの安全な更新方針で installer を変更し、fresh root README を生成する。
- S04: shipped docs と dogfooding projection を同期し、既存 Workbench payload の不変性を確認する。

## 検証
- AC-407-01: fresh init の root と新規 node で README の存在・byte equality、実 Git の ignored/unignored matrix を確認する。
- AC-407-02: 既知旧版・欠落・未知独自編集の update / force-init 結果を確認する。
- AC-407-03: 既存 Workbench と README の snapshot を update 前後で比較する。
- AC-407-04: 正規 update 経路、focused pytest、`uv run pytest`、`make lint`、`spec-dock validate` を確認する。

## rollback
provider 修正の revert と再配布を基本とする。利用先の `.gitignore` は事前状態を確認し、未知編集や payload を自動復元・削除しない。

## exit / handoff
AC-407-01〜04 の実測証拠、変更した provider / dogfooding paths、利用先移行が対象外であることを Report に残す。Issue 作成と仕様草案だけでは実装完了としない。

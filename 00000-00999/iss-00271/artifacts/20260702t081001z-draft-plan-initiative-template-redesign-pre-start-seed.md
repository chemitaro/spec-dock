---
種別: draft-plan
ID: "20260702t081001z-draft-plan"
タイトル: "Redesign Initiative Requirement Design Plan Templates draft-plan pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00271", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00271"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical plan.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00271-PLAN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["plan.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00271 Redesign Initiative Requirement Design Plan Templates — draft-plan pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `plan.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `plan.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 実装計画書ドラフト（Issue）
ID: "iss-00271"
タイトル: "Redesign Initiative Requirement Design Plan Templates"
関連GitHub: ["#271"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00271 Initiative テンプレート再設計 — 実装計画ドラフト

## ドラフト扱い
- この計画は実行前のバトン設計であり、Issue 実施時に正規計画へ更新する。
- 実装開始前に `./spec-dock/scripts/spec-dock issue start iss-00271` を実行し、Issue Planning workflow に従って `design.md` / `plan.md` を正規化する。
- この Issue では PR を作らない。完了時は `issue finish` で次の `iss-00272` へ進む。

## この計画で満たす要件ID
- `I271-AC-001` から `I271-AC-007`
- `I271-EC-001` から `I271-EC-004`

## 依存関係から導く実行順
1. 正規化ゲート: active Issue 化、既存テンプレートとテストの再調査、ドラフト設計・計画の確定。
2. Initiative requirement template 更新。
3. Initiative design / plan template 更新。
4. テンプレート構造と日本語ファースト guidance の検証。
5. report 更新、reviewer gate、`issue finish`。

## ステップ案

### S00 Issue開始と正規計画化
- 目的: このドラフトを、実行時点の現物に合わせた正規設計・正規計画へ変換する。
- 入力: `requirement.md`、この `design.md` / `plan.md`、Epic docs、関連 ADR。
- 検証: placeholder / stale assumption が残っていないことを文書点検する。
- 出力: reviewer に出せる正規 `design.md` / `plan.md`。

### S01 Initiative requirement template 更新
- 目的: Initiative requirement template が戦略的目的と Epic handoff を誘導できるようにする。
- 対象候補: `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`
- 検証候補: template diff inspection、既存 scaffold test、必要なら focused assertion。
- 停止条件: Issue-level implementation detail を必須化する必要が出た場合。

### S02 Initiative design / plan template 更新
- 目的: Initiative design / plan template が source-of-truth、artifact adoption、reviewer gate、controlled Epic decomposition を扱えるようにする。
- 対象候補:
  - `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- 検証候補: template diff inspection、禁止語彙確認、日本語ファースト確認。
- 停止条件: scope-layering reference 本文をテンプレートへ重複させる必要が出た場合。

### S90 docs / scaffold 影響確認
- 目的: provider-side template 変更が dogfooding workspace と docs に与える影響を確認する。
- 検証候補: `uv run pytest ...`、`./spec-dock/scripts/spec-dock validate`、必要に応じた scaffold read-through。
- report: 実行したコマンド、未実施の理由、残リスクを `report.md` に記録する。

### S99 Issue完了ゲート
- 目的: この Issue の変更が `iss-00272` へ渡せる状態か確認する。
- reviewer focus: `spec-reviewer` による template scope、artifact authority、日本語ファースト guidance の確認。
- 完了動作: PR は作らず、Issue完了後に `issue finish` を行い、`iss-00272` を開始する。

## 要件とステップの対応
| 要件 | 主担当ステップ |
|---|---|
| `I271-AC-001` | S01 |
| `I271-AC-002` | S02 |
| `I271-AC-003` | S02 |
| `I271-AC-004` | S01, S02 |
| `I271-AC-005` | S01, S02 |
| `I271-AC-006` | S01, S02, S90 |
| `I271-AC-007` | S02, S99 |

## バトン出力
- 更新された Initiative templates。
- `iss-00272` が再利用できる scope / handoff / 日本語ファーストの語彙。
- `iss-00273` が接続する scope-layering reference link の未完了事項。
- report に残した検証結果と未解決リスク。

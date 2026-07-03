---
種別: draft-plan
ID: "20260702t081003z-draft-plan"
タイトル: "Redesign Epic Requirement Design Plan Templates draft-plan pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00272", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00272"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical plan.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00272-PLAN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["plan.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00272 Redesign Epic Requirement Design Plan Templates — draft-plan pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `plan.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `plan.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 実装計画書ドラフト（Issue）
ID: "iss-00272"
タイトル: "Redesign Epic Requirement Design Plan Templates"
関連GitHub: ["#272"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00272 Epic テンプレート再設計 — 実装計画ドラフト

## ドラフト扱い
- この計画は実行前のバトン設計である。
- 実装開始前に `./spec-dock/scripts/spec-dock issue start iss-00272` を実行し、`iss-00271` の完了結果を確認してから正規計画へ更新する。
- この Issue では PR を作らず、完了後に `iss-00273` へ進む。

## この計画で満たす要件ID
- `I272-AC-001` から `I272-AC-007`
- `I272-EC-001` から `I272-EC-004`

## 依存関係から導く実行順
1. `iss-00271` の report / diff / reviewer result を確認する。
2. Epic requirement template を更新する。
3. Epic design / plan templates を更新する。
4. Issue handoff fields と日本語ファースト guidance を検証する。
5. report 更新、reviewer gate、`issue finish`。

## ステップ案

### S00 Issue開始と正規計画化
- 目的: `iss-00271` の成果を取り込み、Epic template 実装の正規計画を確定する。
- 検証: 前段 Issue の未解決リスクがこの Issue をブロックしないこと。

### S01 Epic requirement template 更新
- 対象候補: `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
- 目的: Epic-level capability / model envelope / acceptance / scope を記述できるようにする。
- 検証候補: template diff inspection、既存 scaffold test、focused assertion。

### S02 Epic design / plan template 更新
- 対象候補:
  - `src/spec_dock/assets/spec_dock/templates/epic/design.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- 目的: design slice catalog、Issue handoff package、suggested grade、dependencies、final quality gate を記述できるようにする。
- 検証候補: handoff field presence check、禁止 wording check、日本語ファースト確認。

### S90 docs / scaffold 影響確認
- 目的: template 更新が後続 guidance / execution readiness と矛盾しないことを確認する。
- 検証候補: `uv run pytest ...`、`./spec-dock/scripts/spec-dock validate`、dogfooding read-through。

### S99 Issue完了ゲート
- reviewer focus: scope ownership、artifact authority、handoff completeness、日本語ファースト guidance。
- 完了動作: PR は作らず `issue finish` し、`iss-00273` を開始する。

## 要件とステップの対応
| 要件 | 主担当ステップ |
|---|---|
| `I272-AC-001` | S01 |
| `I272-AC-002` | S02 |
| `I272-AC-003` | S02 |
| `I272-AC-004` | S02 |
| `I272-AC-005` | S01, S02 |
| `I272-AC-006` | S01, S02, S90 |
| `I272-AC-007` | S02, S99 |

## バトン出力
- 更新された Epic templates。
- `iss-00273` が docs / skills / reference へ接続する handoff field と scope-layering 語彙。
- `iss-00274` が readiness inspection の入力にできる Issue handoff package。
- report に残した検証結果と未解決リスク。

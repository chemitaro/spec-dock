---
種別: draft-plan
ID: "20260702t081009z-draft-plan"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation draft-plan pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00275", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00275"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical plan.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00275-PLAN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["plan.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00275 Add Upstream Planning Smoke Tests And Template Validation — draft-plan pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `plan.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `plan.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 実装計画書ドラフト（Issue）
ID: "iss-00275"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation"
関連GitHub: ["#275"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00275 Upstream planning smoke tests と template validation 追加 — 実装計画ドラフト

## ドラフト扱い
- この計画は実行前のバトン設計である。
- 実装開始前に `./spec-dock/scripts/spec-dock issue start iss-00275` を実行し、`iss-00271` から `iss-00274` の成果を確認してから正規計画へ更新する。
- この Issue では PR を作らず、完了後に `iss-00276` へ進む。

## この計画で満たす要件ID
- `I275-AC-001` から `I275-AC-007`
- `I275-EC-001` から `I275-EC-004`

## 依存関係から導く実行順
1. 前段4 Issue の変更と検証証跡を確認する。
2. 既存 test suite / validation commands を調査する。
3. focused tests / smoke checks を追加または更新する。
4. 必要な gate repair を最小範囲で行う。
5. `validate` と関連 test command を実行し、`issue finish` する。

## ステップ案

### S00 Issue開始と正規計画化
- 目的: 前段差分から検証対象とテスト配置を確定する。
- 検証: 既存 test suite の配置と対象 layer を report に記録する。

### S01 Focused tests / smoke checks 追加
- 対象候補: `tests/`
- 目的: scope-layering reference、thin links、artifact authority、architecture-neutral wording、handoff readiness、日本語ファースト guidance を構造的に検査する。
- 検証候補: new / updated tests の red/green または inspect-only rationale。

### S02 Gate repair
- 対象候補: 前段で更新された templates / docs / skills。
- 目的: tests / smoke checks が見つけた in-scope 不足を最小修正する。
- 停止条件: Epic design / plan に戻るべき新しい要求や責務境界の変更が見つかった場合。

### S90 Integrated validation
- 目的: 追加した検証と `validate` を実行し、結果を report に残す。
- 検証候補:
  - `uv run pytest ...`
  - `./spec-dock/scripts/spec-dock validate`
  - 必要に応じた `./spec-dock/scripts/spec-dock sync`
  - manual dogfooding read-through

### S99 Issue完了ゲート
- reviewer focus: smoke coverage relevance、false positive risk、日本語ファースト確認粒度。
- 完了動作: PR は作らず `issue finish` し、`iss-00276` を開始する。

## 要件とステップの対応
| 要件 | 主担当ステップ |
|---|---|
| `I275-AC-001` | S01, S90 |
| `I275-AC-002` | S01, S02 |
| `I275-AC-003` | S01 |
| `I275-AC-004` | S01 |
| `I275-AC-005` | S01, S02 |
| `I275-AC-006` | S01, S99 |
| `I275-AC-007` | S90, S99 |

## バトン出力
- Test / smoke / validation evidence。
- Final quality Issue が再実行すべき command list と manual scenario。
- gate repair の有無と残リスク。

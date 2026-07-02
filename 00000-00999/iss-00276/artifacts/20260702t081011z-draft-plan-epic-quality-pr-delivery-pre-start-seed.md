---
種別: draft-plan
ID: "20260702t081011z-draft-plan"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery draft-plan pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00276", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00276"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical plan.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00276-PLAN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["plan.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00276 Epic Quality Gate Manual Tests And PR Delivery — draft-plan pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `plan.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `plan.md` に置かれていた旧本文
- specialist obligation: specialist output がない場合は原則 blocked。manual fallback は明示的 risk acceptance と追加 gate が必要

## 移行前本文

---
種別: 実装計画書ドラフト（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — 実装計画ドラフト

## ドラフト扱い
- この計画は実行前のバトン設計である。
- 実装開始前に `./spec-dock/scripts/spec-dock issue start iss-00276` を実行し、前段5 Issue の完了証跡を確認してから正規計画へ更新する。
- この Issue だけが PR readiness / PR creation を扱う。

## この計画で満たす要件ID
- `I276-AC-001` から `I276-AC-008`
- `I276-EC-001` から `I276-EC-005`

## 依存関係から導く実行順
1. 前段5 Issue の完了状態、reports、validation evidence、未解決リスクを確認する。
2. final automated checks と manual smoke を実行する。
3. reviewer gates と必要な repair loop を行う。
4. Epic report / PR description を整える。
5. branch / staged state を確認し、PR を作成する。

## ステップ案

### S00 Issue開始と正規計画化
- 目的: final gate の対象と command list を前段 evidence から確定する。
- 検証: 未完了 Issue / unresolved blocker / stale reviewer pass がないこと。

### S01 前段Issue完了証跡の統合確認
- 対象候補: `iss-00271` から `iss-00275` の `report.md`。
- 目的: implementation chain が完了しているか、defer が正当化されているかを確認する。
- 停止条件: 前段の blocking entry が未解決。

### S02 Automated checks / validate
- 目的: test suite と `validate` を実行し、結果を final report に残す。
- 検証候補:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - 必要に応じた `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - 必要に応じた `./spec-dock/scripts/spec-dock sync`

### S03 Manual dogfooding / Japanese-first check
- 目的: templates、docs、skills、handoff readiness、日本語ファースト guidance を人間が読める形で確認する。
- 検証候補: manual summary、docs diff inspection、raw manual files not staged check。

### S04 Reviewer gates / repair loop
- 目的: `spec-reviewer`、必要に応じて `qa-reviewer` / `code-reviewer` を通し、in-scope 指摘を修正して再検証する。
- 停止条件: reviewer が blocking finding を残す、または repair が Epic scope を超える。

### S05 PR readiness / PR creation
- 目的: PR description を作成し、branch / staged state / untracked raw files を確認した上で PR を作成する。
- 検証候補: `git status`、PR作成結果、PR URL。
- 境界: PR merge / GitHub Issue close は行わない。

## 要件とステップの対応
| 要件 | 主担当ステップ |
|---|---|
| `I276-AC-001` | S01 |
| `I276-AC-002` | S02 |
| `I276-AC-003` | S03 |
| `I276-AC-004` | S04 |
| `I276-AC-005` | S04 |
| `I276-AC-006` | S05 |
| `I276-AC-007` | S00, S05 |
| `I276-AC-008` | S03, S04 |

## バトン出力
- Final validation evidence。
- Updated `epic-00270/report.md`。
- PR URL と PR readiness evidence。
- Merge / closeout へ進むための残課題。

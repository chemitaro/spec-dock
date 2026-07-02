---
種別: draft-plan
ID: "20260702t081007z-draft-plan"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow draft-plan pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00274", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00274"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical plan.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00274-PLAN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["plan.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00274 Update Epic Execution Handoff And Issue Readiness Workflow — draft-plan pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `plan.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `plan.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 実装計画書ドラフト（Issue）
ID: "iss-00274"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow"
関連GitHub: ["#274"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00274 Epic execution handoff と Issue readiness workflow 更新 — 実装計画ドラフト

## ドラフト扱い
- この計画は実行前のバトン設計である。
- 実装開始前に `./spec-dock/scripts/spec-dock issue start iss-00274` を実行し、`iss-00272` / `iss-00273` の成果を確認してから正規計画へ更新する。
- この Issue では PR を作らず、完了後に `iss-00275` へ進む。

## この計画で満たす要件ID
- `I274-AC-001` から `I274-AC-006`
- `I274-EC-001` から `I274-EC-004`

## 依存関係から導く実行順
1. 前段 handoff package / reference guidance を確認する。
2. Epic execution skill を readiness-aware に更新する。
3. workflow / phase docs に必要最小限の補助説明を追加する。
4. runtime behavior change の要否を判定し、必要な場合だけ focused tests を追加する。
5. read-through / validate / reviewer gate を実行し、`issue finish` する。

## ステップ案

### S00 Issue開始と正規計画化
- 目的: 前段成果を読み、docs-only / skill-only / runtime-change の境界を確定する。
- 検証: runtime 変更が必要かどうかを根拠付きで report に残す。

### S01 Epic execution skill 更新
- 対象候補: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
- 目的: handoff package、structural blockers、reviewer findings、no per-Issue PR を案内する。
- 検証候補: skill read-through、禁止 wording check。

### S02 Workflow / phase docs 補助更新
- 対象候補: `workflow_epic.md`, `workflow_issue.md`, 必要な `phase_*` docs。
- 目的: execution / readiness と Issueリレーを docs からも追えるようにする。
- 検証候補: docs diff inspection、reference link check。

### S03 Runtime test 要否判断と必要最小限の検証
- 目的: runtime behavior を変更した場合だけ tests を追加し、guidance 変更のみなら docs-only verification に留める。
- 検証候補: `uv run pytest ...`、manual read-through、`./spec-dock/scripts/spec-dock validate`。

### S99 Issue完了ゲート
- reviewer focus: lifecycle authority、structural blocker / reviewer finding 分離、日本語ファースト guidance。
- 完了動作: PR は作らず `issue finish` し、`iss-00275` を開始する。

## 要件とステップの対応
| 要件 | 主担当ステップ |
|---|---|
| `I274-AC-001` | S01 |
| `I274-AC-002` | S01, S02 |
| `I274-AC-003` | S01, S02 |
| `I274-AC-004` | S01 |
| `I274-AC-005` | S01, S02 |
| `I274-AC-006` | S01, S02, S99 |

## バトン出力
- 更新された Epic execution readiness guidance。
- `iss-00275` が検証できる structural blocker / reviewer finding の観点。
- `iss-00276` が final quality gate で参照できる Issueリレー方針。

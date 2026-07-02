---
種別: draft-plan
ID: "20260702t081005z-draft-plan"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs draft-plan pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00273", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00273"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical plan.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00273-PLAN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["plan.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00273 Update Scope Layering Reference Planning Skills And Workflow Docs — draft-plan pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `plan.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `plan.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 実装計画書ドラフト（Issue）
ID: "iss-00273"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs"
関連GitHub: ["#273"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00273 Scope-layering reference と planning guidance 更新 — 実装計画ドラフト

## ドラフト扱い
- この計画は実行前のバトン設計である。
- 実装開始前に `./spec-dock/scripts/spec-dock issue start iss-00273` を実行し、`iss-00271` / `iss-00272` の完了結果を確認してから正規計画へ更新する。
- この Issue では PR を作らず、完了後に `iss-00274` へ進む。

## この計画で満たす要件ID
- `I273-AC-001` から `I273-AC-007`
- `I273-EC-001` から `I273-EC-004`

## 依存関係から導く実行順
1. 前段テンプレート変更と link 導線を確認する。
2. `docs/authoring/scope-layering.md` を作成する。
3. workflow / phase docs に薄いリンクを追加する。
4. planning / clarification skills と templates を reference / 日本語ファースト guidance へ接続する。
5. focused checks / validate / reviewer gate を実行し、`issue finish` する。

## ステップ案

### S00 Issue開始と正規計画化
- 目的: 前段の成果を取り込み、reference / links / skills の正確な対象を確定する。
- 検証: 前段 Issue の未解決リスクがこの Issue をブロックしないこと。

### S01 Scope-layering reference 作成
- 対象候補: `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
- 目的: scope ownership、decision radius、authority flow、anti-rules を1つの狭い reference に集約する。
- 検証候補: docs diff inspection、リンク存在確認。

### S02 Workflow / phase docs の thin link 更新
- 対象候補: `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md`, 必要な `phase_*` docs。
- 目的: lifecycle docs に責務表を重複させず、必要箇所から reference へ到達できるようにする。
- 検証候補: grep / docs link inspection。

### S03 Planning / clarification skills と templates の接続
- 対象候補: planning skills、clarification skill、Initiative / Epic templates。
- 目的: source-grounded clarification、artifact authority、日本語ファースト authoring、scope-layering reference を案内する。
- 検証候補: skill read-through、禁止 wording check。

### S90 docs / scaffold 影響確認
- 目的: reference / links / skills が dogfooding workspace と矛盾しないことを確認する。
- 検証候補: `./spec-dock/scripts/spec-dock validate`、`uv run pytest ...`、manual read-through。

### S99 Issue完了ゲート
- reviewer focus: discoverability、重複回避、artifact authority、日本語ファースト guidance。
- 完了動作: PR は作らず `issue finish` し、`iss-00274` を開始する。

## 要件とステップの対応
| 要件 | 主担当ステップ |
|---|---|
| `I273-AC-001` | S01 |
| `I273-AC-002` | S02, S03 |
| `I273-AC-003` | S03 |
| `I273-AC-004` | S01, S02, S03 |
| `I273-AC-005` | S03, S90 |
| `I273-AC-006` | S03 |
| `I273-AC-007` | S90, S99 |

## バトン出力
- `docs/authoring/scope-layering.md` と関連 thin links。
- planning / clarification skills の更新済み guidance。
- `iss-00274` が readiness workflow に使える structural / semantic boundary 語彙。
- `iss-00275` が検証対象にできる focused check 観点。

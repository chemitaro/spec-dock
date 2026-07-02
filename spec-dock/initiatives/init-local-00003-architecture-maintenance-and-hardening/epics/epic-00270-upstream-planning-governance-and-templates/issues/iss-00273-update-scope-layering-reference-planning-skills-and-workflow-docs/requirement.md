---
種別: 要件定義書（Issue）
ID: "iss-00273"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs"
関連GitHub: ["#273"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270", "init-local-00003"]
---

# iss-00273 Scope-layering reference と planning guidance 更新 — Issue 要件定義

## 文書の位置づけ
- この文書は `epic-00270` 配下の正規 Issue 要件定義である。
- Canonical `design.md` と `plan.md` は、Issue Start 後に assurance classify / assurance compose / fresh reviewer gate を通して正規化するまで `awaiting-assurance-compose` placeholder とする。
- Issue Start 前の設計・計画 seed は、Issue-local `draft-design` / `draft-plan` artifact として保持し、canonical authority ではなく handoff evidence として扱う。
- この Issue では PR を作成しない。完了後は `issue finish` により `iss-00274` へバトンを渡す。

## Pre-start draft handoff
- draft-design artifact: `artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md`
- artifact authority: evidence only
- canonical adoption: `issue start` 後に Issue Planning EAL で adopted / partially_adopted / rejected / stale / blocked を判断する。
- issue grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 目的
Initiative / Epic / Issue の scope ownership、decision radius、artifact authority、handoff flow を、provider-side reference `docs/authoring/scope-layering.md` に集約し、planning skills / workflow docs / phase docs / templates から薄く参照できるようにする。

## 背景
- Scope-layering の責務を各テンプレートやスキルに重複して書くと、情報が散らばり、将来の agent が適切な情報へ到達しにくくなる。
- 一方で参照が少なすぎると、上流 planning の境界や artifact authority が下流 Issue planning に伝わらない。
- そのため、1つの狭い reference と薄いリンクの組み合わせを採用する。

## 親スコープから継承する要件
- `E-RQ-010`: Issue-local draft artifact boundary and grade-aware role policy
- `E-AC-008`: pre-start Issue draft migration readiness
- `E-RQ-002`: source-grounded clarification workflow
- `E-RQ-003`: artifact-to-canonical authority flow
- `E-RQ-005`: scope layering and reference publication
- `E-RQ-009`: Japanese-first spec and artifact authoring
- `E-AC-003`: planning skills and workflow alignment
- `E-AC-007`: Japanese-first authoring readiness

## 親設計から継承する判断
- `D-001`: scope-layering reference publication。
- `D-003`: complete understanding before canonical authoring。
- `D-005`: flexible six-Issue baseline。
- `D-008`: Japanese-first spec authoring。

## 対象
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- 必要な `phase_*` docs / authoring docs
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
- `iss-00271` / `iss-00272` で準備された Initiative / Epic templates の thin link 接続
- 必要な focused docs / link / scaffold tests

## 対象外
- Scope-layering の全文をすべての template / docs / skills に複製すること。
- ADR を日常的な operational reference として使わせること。
- Issue planning / execution workflow の authority を置き換えること。
- runtime command behavior の大規模変更。必要になった場合は `iss-00274` または再計画へ回す。
- PR 作成、GitHub Issue close、merge 操作。

## 受け入れ条件
- `I273-AC-001`: `docs/authoring/scope-layering.md` が provider-side reference として存在し、Initiative / Epic / Issue の責務、decision radius、authority flow、anti-rules を狭く説明する。
- `I273-AC-002`: workflow docs / phase docs / skills / templates は、責務モデル全文を重複させず、必要な箇所から薄く reference へ誘導する。
- `I273-AC-003`: planning skills は、source-grounded clarification、調査で分かることを人間へ聞かないこと、一問ずつの interview、採用知識の外部化を誘導する。
- `I273-AC-004`: docs / skills は、raw `artifacts/`、research、interview、delegated draft が canonical authority ではないことを明示する。
- `I273-AC-005`: 日本語運用で canonical docs / artifacts の本文を日本語ファーストにする guidance が docs / skills / artifact guidance へ反映される。
- `I273-AC-006`: `iss-00271` / `iss-00272` の template 更新で残された dangling でない link 導線が、実際の reference へ接続される。
- `I273-AC-007`: `validate` または focused checks により、reference の存在、主要リンク、重複回避、artifact authority leak の欠如を確認できる。
- `I273-AC-008`: Epic Planning / workflow docs / planning skills は、downstream Issue handoff package に Issue-local `draft-design` と `draft-plan` の path index、または明示的な blocked / fallback evidence を含める。
- `I273-AC-009`: Epic Planning は Issue Start 前に canonical Issue `design.md` / `plan.md` 本文を作成してはならず、pre-start seed は Issue-local artifacts として扱うことを誘導する。

## 例外条件 / 失敗条件
- `I273-EC-001`: full responsibility table を各 surface に重複させてはならない。
- `I273-EC-002`: `artifacts/` を accepted authority と誤認させる文言を入れてはならない。
- `I273-EC-003`: DDD / EDA を SpecDock の標準アーキテクチャとして記述してはならない。
- `I273-EC-004`: 日本語ファースト guidance が、識別子や外部固有名詞まで日本語化する圧力になってはならない。

## バトン / 依存
- 前提:
  - `iss-00271` と `iss-00272` のテンプレート更新が完了していること。
- 後続:
  - `iss-00274` は、この Issue で整備した reference / guidance を使って Epic execution handoff readiness を更新する。
  - `iss-00275` は、この Issue の reference / link / authority flow を smoke tests の対象にする。

## 検証期待
- 新規 reference と関連 docs / skills の差分点検。
- リンク・grep・snapshot などの focused checks。
- `./spec-dock/scripts/spec-dock validate`。
- 必要に応じた `uv run pytest ...` と dogfooding read-through。

## 実行開始時の確認事項
- 前段テンプレート変更で確定した文言を確認する。
- canonical `design.md` / `plan.md` は placeholder であり、`issue start` 後に現物と Issue-local draft artifacts を踏まえて正規化する。

---
種別: 要件定義書（Issue）
ID: "iss-00272"
タイトル: "Redesign Epic Requirement Design Plan Templates"
関連GitHub: ["#272"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270", "init-local-00003"]
---

# iss-00272 Epic 要件・設計・計画テンプレート再設計 — Issue 要件定義

## 文書の位置づけ
- この文書は `epic-00270` 配下の正規 Issue 要件定義である。
- Canonical `design.md` と `plan.md` は、Issue Start 後に assurance classify / assurance compose / fresh reviewer gate を通して正規化するまで `awaiting-assurance-compose` placeholder とする。
- Issue Start 前の設計・計画 seed は、Issue-local `draft-design` / `draft-plan` artifact として保持し、canonical authority ではなく handoff evidence として扱う。
- この Issue では PR を作成しない。完了後は `issue finish` により `iss-00273` へバトンを渡し、PR delivery は `iss-00276` がまとめて扱う。

## Pre-start draft handoff
- draft-design artifact: `artifacts/20260702t081002z-draft-design-epic-template-redesign-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081003z-draft-plan-epic-template-redesign-pre-start-seed.md`
- artifact authority: evidence only
- canonical adoption: `issue start` 後に Issue Planning EAL で adopted / partially_adopted / rejected / stale / blocked を判断する。
- issue grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 目的
Epic の `requirement.md` / `design.md` / `plan.md` テンプレートを、capability / model envelope、cross-Issue constraints、design slice catalog、Issue handoff package、suggested grade、dependencies、final quality gate を表現できる下流接続 surface に再設計する。

## 背景
- Epic は Initiative と Issue の間で、複数 Issue にまたがる責務境界、受け入れ条件、検証期待、実行順序を束ねる必要がある。
- 現状の上流 planning では、Epic から Issue へ渡す handoff package が明確でないため、Issue planning 時に親設計の再定義や抜け漏れが起きやすい。
- 日本語運用では、Epic docs の説明本文が日本語ファーストで作成される必要がある。

## 親スコープから継承する要件
- `E-RQ-010`: Issue-local draft artifact boundary and grade-aware role policy
- `E-AC-008`: pre-start Issue draft migration readiness
- `E-RQ-001`: Initiative / Epic template upgrade
- `E-RQ-004`: architecture-neutral / architecture-aware authoring
- `E-RQ-006`: Epic-to-Issue slicing and handoff
- `E-RQ-009`: Japanese-first spec and artifact authoring
- `E-AC-002`: Epic template readiness
- `E-AC-007`: Japanese-first authoring readiness

## 親設計から継承する判断
- `D-001`: scope-layering reference は provider-side reference に集約する。
- `D-002`: Epic templates は DDD / EDA を標準前提にしない。
- `D-003`: source-grounded understanding と採用証跡を要求する。
- `D-004`: canonical docs は採用済み decision、scope boundary、handoff contract、gate を持つ。
- `D-005`: 6 Issue baseline は柔軟だが、再分割には plan 更新と fresh review を要求する。
- `D-008`: 日本語ファースト authoring を誘導する。

## 対象
- `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/epic/design.md`
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- 必要な場合の template snapshot / scaffold tests
- 必要な場合の local dogfooding workspace 確認

## 対象外
- Issue grade templates / Issue profile templates の再設計。
- Issue-level TDD cadence や implementation step schema を Epic template へ移すこと。
- decision-only Issue を execution-ready と扱うこと。
- PR 作成、GitHub Issue close、merge 操作。

## 受け入れ条件
- `I272-AC-001`: Epic requirement template が capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope を記述できる。
- `I272-AC-002`: Epic design template が cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy を記述できる。
- `I272-AC-003`: Epic plan template が Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を記述できる。
- `I272-AC-004`: Epic template が Issue plan の詳細 TDD step や private implementation design を必須にしない。
- `I272-AC-005`: Epic template が `artifacts/` を raw evidence として扱い、採用判断は canonical docs / accepted ADR / report ledger へ置くことを誘導する。
- `I272-AC-006`: 日本語運用で新規 Epic docs の説明文が日本語ファーストになる guidance を含む。
- `I272-AC-007`: 後続 Issue が親 requirement / design trace、allowed local delta、forbidden parent boundary changes、expected evidence を受け取れる。

## 例外条件 / 失敗条件
- `I272-EC-001`: Epic templates が Issue planning / execution workflow の authority を置き換えてはならない。
- `I272-EC-002`: DDD / EDA 固有語彙を、architecture 未定義の repo にも必須化してはならない。
- `I272-EC-003`: Issue handoff package が抽象的すぎて、後続 Issue が acceptance seed と禁止範囲を特定できない状態にしてはならない。
- `I272-EC-004`: 日本語ファースト guidance が、識別子やコマンド名の原文保持を妨げてはならない。

## バトン / 依存
- 前提:
  - `iss-00271` の Initiative template 語彙と上流責務境界。
  - `epic-00270` の canonical docs と accepted ADR。
- 後続:
  - `iss-00273` は、この Issue で整えた Epic template の handoff / scope-layering 語彙を workflow docs / skills / reference へ接続する。
  - `iss-00274` は、ここで定義した Issue handoff package を Epic execution readiness の入力として使う。

## 検証期待
- Epic template 差分の文書点検。
- template / scaffold tests の更新または focused assertion。
- handoff package fields が過不足なく存在することの構造確認。
- 日本語ファースト guidance の確認。
- 必要に応じた `uv run pytest ...`、`./spec-dock/scripts/spec-dock validate`、dogfooding read-through。

## 実行開始時の確認事項
- `iss-00271` の実装結果と語彙を確認してから着手する。
- canonical `design.md` / `plan.md` は placeholder であり、`issue start` 後に現物と Issue-local draft artifacts を踏まえて正規化する。

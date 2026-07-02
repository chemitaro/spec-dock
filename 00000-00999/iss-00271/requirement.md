---
種別: 要件定義書（Issue）
ID: "iss-00271"
タイトル: "Redesign Initiative Requirement Design Plan Templates"
関連GitHub: ["#271"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270", "init-local-00003"]
---

# iss-00271 Initiative 要件・設計・計画テンプレート再設計 — Issue 要件定義

## 文書の位置づけ
- この文書は `epic-00270` 配下の正規 Issue 要件定義である。
- Canonical `design.md` と `plan.md` は、Issue Start 後に assurance classify / assurance compose / fresh reviewer gate を通して正規化するまで `awaiting-assurance-compose` placeholder とする。
- Issue Start 前の設計・計画 seed は、Issue-local `draft-design` / `draft-plan` artifact として保持し、canonical authority ではなく handoff evidence として扱う。
- この Issue では PR を作成しない。完了時は `issue finish` により次の `iss-00272` へバトンを渡し、PR delivery は `iss-00276` がまとめて扱う。

## Pre-start draft handoff
- draft-design artifact: `artifacts/20260702t081000z-draft-design-initiative-template-redesign-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081001z-draft-plan-initiative-template-redesign-pre-start-seed.md`
- artifact authority: evidence only
- canonical adoption: `issue start` 後に Issue Planning EAL で adopted / partially_adopted / rejected / stale / blocked を判断する。
- issue grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 目的
Initiative の `requirement.md` / `design.md` / `plan.md` テンプレートを、戦略的変更、capability landscape、source-of-truth、artifact adoption、reviewer gate、Epic handoff を表現できる上流 planning surface に再設計する。

## 背景
- 現在の上流 planning では、Initiative / Epic / Issue の責務境界と下流 handoff がテンプレート上で十分に誘導されず、agent が Issue-level の実装詳細や TDD 手順を上流へ混ぜやすい。
- Phase 1 の Issue grade / TDD planning と Phase 2 の `artifacts/` evidence surface は存在するが、Initiative テンプレートがそれらへ接続する戦略レイヤーを十分に持っていない。
- 日本語運用では、要件定義書、設計書、計画書、report、artifacts の本文を日本語ファーストで作成できる必要がある。

## 親スコープから継承する要件
- `E-RQ-010`: Issue-local draft artifact boundary and grade-aware role policy
- `E-AC-008`: pre-start Issue draft migration readiness
- `E-RQ-001`: Initiative / Epic template upgrade
- `E-RQ-004`: architecture-neutral / architecture-aware authoring
- `E-RQ-009`: Japanese-first spec and artifact authoring
- `E-AC-001`: Initiative template readiness
- `E-AC-007`: Japanese-first authoring readiness

## 親設計から継承する判断
- `D-001`: scope-layering reference は provider-side reference に集約し、テンプレートは薄くリンクする。
- `D-002`: Initiative / Epic templates は DDD / EDA を標準前提にしない。
- `D-003`: canonical authoring 前に source-grounded understanding を外部化する。
- `D-005`: 6 Issue baseline を維持し、必要な場合だけ再分割する。
- `D-008`: 日本語運用では spec / artifact 本文を日本語ファーストにする。

## 対象
- `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- 必要な場合の template snapshot / scaffold tests
- 必要な場合の local dogfooding workspace 確認

## 対象外
- Issue grade templates の再設計。
- Issue-level の TDD cycle、private class / file design、詳細な実装順序の導入。
- DDD / EDA を Initiative テンプレートの必須語彙にすること。
- `docs/authoring/scope-layering.md` の作成そのもの。これは `iss-00273` が担当する。
- PR 作成、GitHub Issue close、merge 操作。

## 受け入れ条件
- `I271-AC-001`: Initiative requirement template が、strategic purpose、capability landscape、source-of-truth、stakeholder / trigger、Epic handoff の入力を誘導できる。
- `I271-AC-002`: Initiative design template が、system context、scope boundary、decision authority、artifact adoption、reviewer gate、Epic boundary を表現できる。
- `I271-AC-003`: Initiative plan template が、Epic decomposition、handoff readiness、fresh reviewer gate、report evidence、controlled re-slicing を表現できる。
- `I271-AC-004`: Initiative templates が Issue-level implementation detail、TDD cycle、private code design を必須にしない。
- `I271-AC-005`: Initiative templates が DDD / EDA を標準前提にせず、既存 architecture が明確な場合にだけその語彙へ適応できる。
- `I271-AC-006`: 日本語運用で新規作成される Initiative docs の説明文が日本語ファーストになるよう guidance を含む。ファイルパス、コマンド、コード識別子、SpecDock 固定語は原文保持を許可する。
- `I271-AC-007`: `iss-00273` が scope-layering reference を作成した後に薄いリンクを追加できるよう、リンク導線の置き場所または文言が破綻しない。

## 例外条件 / 失敗条件
- `I271-EC-001`: `authoring/scope-layering.md` が未作成の段階で、壊れた相対リンクを Initiative templates に入れてはならない。
- `I271-EC-002`: V3 planning pack や調査メモの長文をテンプレートへそのまま貼り付けてはならない。
- `I271-EC-003`: `artifacts/` を canonical authority と誤認させる文言を追加してはならない。
- `I271-EC-004`: 日本語ファースト guidance が、技術識別子や外部固有名詞の翻訳を強制してはならない。

## バトン / 依存
- 前提:
  - `epic-00270` の canonical requirement / design / plan。
  - accepted ADRs: scope-layering reference、architecture-neutral template policy、complete-understanding、Japanese-first authoring。
- 後続:
  - `iss-00272` は、この Issue で固めた Initiative / Epic 共通語彙と日本語ファースト guidance を踏まえて Epic templates を再設計する。
  - `iss-00273` は、この Issue で準備した薄いリンク導線を、実際の `docs/authoring/scope-layering.md` 作成後に接続する。

## 検証期待
- Initiative template 差分の文書点検。
- 既存 template / scaffold tests の更新または追加。
- `rg` などによる禁止語彙・必須 guidance の構造確認。
- 必要に応じた `uv run pytest ...`、`./spec-dock/scripts/spec-dock validate`、dogfooding read-through。

## 実行開始時の確認事項
- この要件は固定入力として扱う。canonical `design.md` / `plan.md` は placeholder であり、pre-start seed は Issue-local artifact を参照する。
- `issue start` 後、対象ファイルと既存テストを再調査し、必要に応じて Issue grade / assurance compose に合わせて正規設計・正規計画へ更新する。

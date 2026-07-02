---
種別: 要件定義書（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270", "init-local-00003"]
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — Issue 要件定義

## 文書の位置づけ
- この文書は `epic-00270` 配下の正規 Issue 要件定義である。
- Canonical `design.md` と `plan.md` は、Issue Start 後に assurance classify / assurance compose / fresh reviewer gate を通して正規化するまで `awaiting-assurance-compose` placeholder とする。
- Issue Start 前の設計・計画 seed は、Issue-local `draft-design` / `draft-plan` artifact として保持し、canonical authority ではなく handoff evidence として扱う。
- この Issue は、`iss-00271` から `iss-00275` の完了後に、Epic 全体の final quality gate と PR delivery をまとめて扱う唯一の Issue である。

## Pre-start draft handoff
- draft-design artifact: `artifacts/20260702t081010z-draft-design-epic-quality-pr-delivery-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md`
- artifact authority: evidence only
- canonical adoption: `issue start` 後に Issue Planning EAL で adopted / partially_adopted / rejected / stale / blocked を判断する。
- issue grade: `critical`
- specialist obligation: specialist output がない場合は原則 blocked。manual fallback は risk acceptance / extra reviewer / rollback-safety evidence がある場合だけ例外

## 目的
Epic 全体の automated checks、manual tests、dogfooding inspection、review repair、final report、PR readiness / PR creation を統合して扱い、原則1PRで delivery できる状態にする。

## 背景
- この Epic は、Issueごとに PR を作らず、Issue完了リレーで実装を積み上げる方針を採用している。
- そのため、最後に Epic 全体の一貫性、検証証跡、未解決リスク、PR説明、manual test summary をまとめて確認する Issue が必要である。
- final quality gate は、新機能を広げる場所ではなく、統合品質、証跡、PR readiness を確定する場所である。

## 親スコープから継承する要件
- `E-RQ-010`: Issue-local draft artifact boundary and grade-aware role policy
- `E-AC-008`: pre-start Issue draft migration readiness
- `E-RQ-008`: quality and delivery gate
- `E-RQ-009`: Japanese-first spec and artifact authoring
- `E-AC-006`: delivery readiness
- `E-AC-007`: Japanese-first authoring readiness

## 親設計から継承する判断
- `D-007`: one-PR delivery default。
- `D-008`: Japanese-first spec authoring。
- `D-005`: re-slicing / PR split は必要性が明確な場合だけ再計画する。

## 対象
- Epic 全体の changed files / docs / templates / skills / tests。
- `iss-00271` から `iss-00275` の reports、validation evidence、unresolved risks。
- `uv run pytest ...`、`./spec-dock/scripts/spec-dock validate`、必要な `sync`。
- local dogfooding workspace inspection。
- final `epic-00270/report.md` 更新。
- PR readiness と PR creation。

## 対象外
- `iss-00271` から `iss-00275` の範囲を超える新しい upstream planning policy の追加。
- 1PR delivery を破綻させる大規模 scope expansion。
- raw manual test workspaces / logs / captures の commit。
- 明示許可のない PR merge、GitHub issue close、credentialed external mutation。

## 受け入れ条件
- `I276-AC-001`: `iss-00271` から `iss-00275` が完了済み、または未完了 / deferred が理由と次アクション付きで記録されている。
- `I276-AC-002`: automated checks と `validate` が実行され、成功または失敗理由 / 次アクションが report に記録されている。
- `I276-AC-003`: manual dogfooding / scaffold / skill read-through の結果が summary として記録され、raw manual files は commit されていない。
- `I276-AC-004`: `spec-reviewer` が Epic requirement / design / plan fulfillment と日本語ファースト authoring を確認する。
- `I276-AC-005`: 実装 diff が大きい場合は `code-reviewer`、検証十分性には `qa-reviewer` を使う、または利用不可理由と fallback を report に残す。
- `I276-AC-006`: PR description が scope、背景、変更内容、影響範囲、検証、リスク、フォローアップを説明する。
- `I276-AC-007`: 1PR delivery が破綻する場合は、PR分割前に `epic-00270/plan.md` を更新し、fresh review を通す。
- `I276-AC-008`: 日本語運用の canonical docs / artifacts が、識別子を除き日本語ファーストになっていることを確認する。
- `I276-AC-009`: `iss-00271` から `iss-00275` の completion evidence に加え、pre-start draft migration が完了していることを確認する。
- `I276-AC-010`: canonical Issue `design.md` / `plan.md` に misplaced draft body が残っていないことを確認する。
- `I276-AC-011`: PR description で handoff-ready / execution-ready boundary、draft artifact adoption、final validation を説明する。

## 例外条件 / 失敗条件
- `I276-EC-001`: 前段 Issue が未完了なのに、理由なしで PR を作成してはならない。
- `I276-EC-002`: failing checks を隠して PR readiness を主張してはならない。
- `I276-EC-003`: final gate repair を超える新規 scope を無断で導入してはならない。
- `I276-EC-004`: raw manual test workspace、temporary logs、local-only artifacts を staged してはならない。
- `I276-EC-005`: PR merge や GitHub issue close をこの Issue の暗黙作業にしてはならない。

## バトン / 依存
- 前提:
  - `iss-00271` から `iss-00275` の完了または明示的 defer。
- 後続:
  - PR 作成後、レビュー / CI / repair loop は PR workflow に従う。
  - merge / closeout はユーザー明示指示後に扱う。

## 検証期待
- `uv run pytest tests/unit`
- `uv run pytest tests/cli_runtime`
- 必要に応じた `uv run pytest`
- `./spec-dock/scripts/spec-dock validate`
- 必要に応じた `./spec-dock/scripts/spec-dock sync`
- dogfooding read-through / manual smoke summary
- fresh reviewer gates

## 実行開始時の確認事項
- 前段 Issue の report をすべて読み、未解決 entry がないか確認する。
- 現在の branch / diff / staged state を確認する。
- PR作成はこの Issue の最後に行い、前段 Issue中には行わない。

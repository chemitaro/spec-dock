---
種別: 要件定義書（Issue）
ID: "iss-00275"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation"
関連GitHub: ["#275"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270", "init-local-00003"]
---

# iss-00275 Upstream planning smoke tests と template validation 追加 — Issue 要件定義

## 文書の位置づけ
- この文書は `epic-00270` 配下の正規 Issue 要件定義である。
- Canonical `design.md` と `plan.md` は、Issue Start 後に assurance classify / assurance compose / fresh reviewer gate を通して正規化するまで `awaiting-assurance-compose` placeholder とする。
- Issue Start 前の設計・計画 seed は、Issue-local `draft-design` / `draft-plan` artifact として保持し、canonical authority ではなく handoff evidence として扱う。
- この Issue では PR を作成しない。完了後は `issue finish` により `iss-00276` へバトンを渡す。

## Pre-start draft handoff
- draft-design artifact: `artifacts/20260702t081008z-draft-design-upstream-planning-validation-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081009z-draft-plan-upstream-planning-validation-pre-start-seed.md`
- artifact authority: evidence only
- canonical adoption: `issue start` 後に Issue Planning EAL で adopted / partially_adopted / rejected / stale / blocked を判断する。
- issue grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 目的
`iss-00271` から `iss-00274` で更新した templates、scope-layering reference、workflow docs、planning / execution skills、日本語ファースト guidance が、構造的に破綻していないことを focused tests / smoke checks で確認できるようにする。

## 背景
- 上流 planning の改善は自然言語 artifact が中心になるため、すべてを機械判定することはできない。
- 一方で、reference の欠落、リンク断絶、必須 field の欠落、raw artifact authority leak、DDD / EDA mandatory wording、日本語ファースト guidance 欠落などは構造的に検出できる。
- final quality Issue だけに検証を寄せると、前段の破綻が最後にまとめて発覚するため、この Issue で統合 smoke matrix を先に整える。

## 親スコープから継承する要件
- `E-RQ-010`: Issue-local draft artifact boundary and grade-aware role policy
- `E-AC-008`: pre-start Issue draft migration readiness
- `E-RQ-003`: artifact-to-canonical authority flow
- `E-RQ-004`: architecture-neutral / architecture-aware authoring
- `E-RQ-005`: scope layering and reference publication
- `E-RQ-007`: handoff inspection and execution readiness
- `E-RQ-009`: Japanese-first spec and artifact authoring
- `E-AC-005`: upstream planning validation
- `E-AC-007`: Japanese-first authoring readiness

## 親設計から継承する判断
- `D-001`: scope-layering reference publication。
- `D-002`: architecture-neutral template policy。
- `D-003`: artifact-to-canonical authority flow。
- `D-005`: flexible six-Issue baseline。
- `D-006`: Option B structural blocker / reviewer finding split。
- `D-008`: Japanese-first spec authoring。

## 対象
- Template / docs / skills の focused tests。
- 既存の scaffold / snapshot / CLI runtime tests のうち、上流 planning structure を検証する箇所。
- `./spec-dock/scripts/spec-dock validate` を含む validation flow。
- 必要な dogfooding read-through / manual smoke summary。

## 対象外
- 意味的品質をすべて machine-only tests に固定すること。
- 技術識別子、コマンド、ファイルパスまで日本語化する machine check。
- raw manual test workspace、capture、log を repository に追加すること。
- final PR description / delivery。これは `iss-00276` が担当する。

## 受け入れ条件
- `I275-AC-001`: `docs/authoring/scope-layering.md` の存在と主要 surface からの到達性を確認できる。
- `I275-AC-002`: full responsibility table の過剰重複、raw artifact authority language、decision-only Issue ready language を構造的に検出できる。
- `I275-AC-003`: Initiative / Epic templates が DDD / EDA を mandatory sections として要求していないことを確認できる。
- `I275-AC-004`: Epic template / execution guidance が Issue handoff package と Option B readiness separation を含むことを確認できる。
- `I275-AC-005`: 日本語ファースト authoring guidance が templates / skills / docs / artifact guidance の必要箇所に存在することを確認できる。
- `I275-AC-006`: focused tests / smoke checks が false positive を増やしすぎないよう、自然言語の意味品質は reviewer に残す境界を説明している。
- `I275-AC-007`: `validate` と関連 test command の結果が `report.md` に記録され、未実施または失敗には理由と次アクションがある。
- `I275-AC-008`: 未開始 Issue の canonical `design.md` / `plan.md` に `artifact_state: "draft-before-issue-start"` が残らないことを検証できる。
- `I275-AC-009`: Issue-local `draft-design` / `draft-plan` artifact path index が report / handoff package にあることを検証できる。
- `I275-AC-010`: `new artifact draft-design` / `draft-plan` が canonical docs を変更せず、missing / invalid / stale `.assurance.json` では no-write fail-closed することを検証できる。
- `I275-AC-011`: Strict / Critical が draft artifact の存在だけで readiness にならないことを検証できる。

## 例外条件 / 失敗条件
- `I275-EC-001`: brittle な文字列一致だけで自然言語品質を合否判定してはならない。
- `I275-EC-002`: DDD / EDA 語彙の存在自体を禁止してはならない。必須化だけを問題にする。
- `I275-EC-003`: 日本語ファースト検証が固定語・識別子・コマンド名の英語を失敗扱いしてはならない。
- `I275-EC-004`: manual smoke artifacts を追跡対象として commit してはならない。

## バトン / 依存
- 前提:
  - `iss-00271` から `iss-00274` の変更が完了していること。
- 後続:
  - `iss-00276` は、この Issue の test / smoke / validation evidence を final quality gate の入力にする。

## 検証期待
- `uv run pytest ...` の focused subset。
- `./spec-dock/scripts/spec-dock validate`。
- 必要に応じた `./spec-dock/scripts/spec-dock sync`。
- manual dogfooding read-through summary。

## 実行開始時の確認事項
- 前段 Issue の変更範囲と未解決リスクを読む。
- tests を足す前に、既存テスト配置と対象 layer を確認する。
- この Issue の成果は final delivery の証跡入力であり、PR は作らない。

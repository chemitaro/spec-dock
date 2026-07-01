---
種別: interview
ID: "20260701t055220z-interview"
タイトル: "Legacy Discussions Validation Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "epic-00259"
created_at: "2026-07-01THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t043248z-interview-artifacts-future-only-policy-boundary.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t050929z-interview-adr-artifact-boundary.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py"
  - "tests/cli_runtime/test_new.py"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t055220z-interview Legacy Discussions Validation Boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Legacy `discussions/` validity and compatibility requirements.
  - `design.md`:
    - Validation behavior for old `discussions/`, new `artifacts/`, and ADR mirror collection.
  - `plan.md`:
    - Validation test updates and migration risk controls.
  - `ADR`:
    - Future-only adoption decision for read-only legacy surfaces.
- chat 上の軽微な一問では足りない理由:
  - Existing `discussions/` files remain source material and may still feed ADR mirror collection. Whether validation remains strict affects safety and operator burden.

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner.
- 何を明確にする質問か:
  - Whether Phase 2 keeps strict validation of legacy `discussions/` filenames and duplicate IDs, or relaxes it after new creation moves to `artifacts/`.
- 回答が後続判断へ与える影響:
  - Determines `validate` behavior, sync/mirror safety, and tests for old/mixed workspaces.

## 質問 (必須)
- pressure-test question:
  - New files will use `artifacts/`, but old `discussions/` remain. Should invalid-looking files under legacy `discussions/` still fail `validate`, or should legacy `discussions/` become mostly read-only/lenient?
- 質問:
  - Phase 2 後も、既存 `discussions/` 配下の malformed discussion filename / duplicate doc_id validation は厳格に維持しますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - Current `validate` scans every scope-local `discussions/` directory and fails on malformed discussion-document candidates or duplicate timestamp/doc_id slots.
  - Current tests expect malformed discussion candidates to block new doc creation and validation-like behavior.
  - Adopted policy: existing `discussions/` files remain; new creation moves to `artifacts/`; ADR mirror collects both `discussions/` and `artifacts/`.
- local context で解決できたこと:
  - `discussions/` is no longer a future creation target, but still contains legacy authoritative evidence and existing ADR originals.
  - New `artifacts/` validation must be added separately.
- まだ人間判断が必要な理由:
  - Strict legacy validation improves safety but may block old workspaces for a directory that is no longer edited by new commands.

## 回答案 (必須)
- Option A:
  - Keep strict legacy validation: existing `discussions/` remain valid legacy surfaces, and `validate` continues to fail malformed discussion-intent filenames and duplicate IDs. Add separate `artifacts/` validation.
- Option B:
  - Relax legacy validation: `validate` no longer fails malformed `discussions/` filenames except for ADR files needed by mirror collection. New strictness applies only to `artifacts/`.
- Option C:
  - Warn-only legacy validation: malformed `discussions/` candidates become warnings, not failures; `artifacts/` remains strict.

## Codex の分析 (必須)
- 判断軸:
  - Safety, old workspace friction, ADR mirror correctness, and clarity of validation results.
- tradeoff:
  - Option A preserves current safety and catches broken legacy evidence, but may keep old cleanup burden. Option B/C reduce friction but can let confusing legacy files persist unnoticed.
- リスク:
  - If mirror collection reads both directories, malformed or duplicate ADR-like files under `discussions/` can produce ambiguous mirror outputs unless validation remains clear.
- 具体シナリオ / edge case:
  - A legacy `discussions/foo-adr-topic.md` appears in an old node. Under Option A, validate fails and forces cleanup. Under Option B, it may be ignored unless mirror collection treats it as ADR-intent.

## Codex の推奨案 (必須)
- 推奨:
  - Option A.
- 理由:
  - It best preserves safety while the system reads both old and new surfaces. Because new creation no longer writes `discussions/`, strict validation mostly protects existing evidence and ADR mirror inputs rather than constraining future authoring.
- 未回答時の影響:
  - Cannot finalize validation contract for mixed old/new workspaces.

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。
- 回答:
  - 「オプションAを採用します。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `ADR`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option A を明示採用した。既存 `discussions/` は legacy surface として残すが、malformed discussion-intent filenames と duplicate IDs の validation は fail として維持する。`artifacts/` には別途 strict validation を追加する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Existing `discussions/` directories remain valid legacy surfaces, but malformed discussion-intent filenames and duplicate IDs remain validation failures.
- `design.md`:
  - `validate` continues strict legacy `discussions/` checks while adding separate strict `artifacts/` filename / duplicate checks.
- `plan.md`:
  - Validation tests must cover old `discussions/` strictness, new `artifacts/` strictness, and mixed nodes.
- `ADR`:
  - Future-only adoption decision must record strict validation for both legacy and future artifact surfaces.
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Adopted policy preserves current safety behavior for legacy `discussions/` while preventing future creation there.

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...

---
種別: interview
ID: "20260701t052324z-interview"
タイトル: "Draft Artifact Command Boundary"
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
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t051314z-interview-future-adr-command-surface.md"
  - "/Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
  - "tests/cli_runtime/test_new.py"
  - "src/spec_dock/assets/spec_dock/templates/README.md"
  - "src/spec_dock/assets/spec_dock/docs/phase_design.md"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t052324z-interview Draft Artifact Command Boundary

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
    - Definition of "all artifacts" and the scope of command unification.
  - `design.md`:
    - `new artifact` support for draft-requirement/design/plan, assurance contract preservation, and artifact filename/template rules.
  - `plan.md`:
    - Implementation issue breakdown, especially whether draft artifact migration becomes a required slice.
  - `ADR`:
    - Command-unification decision and exceptions.
- chat 上の軽微な一問では足りない理由:
  - Draft artifacts are currently special: issue design/plan drafts require valid `.assurance.json`, profile-specific templates, and fail-closed behavior. Moving them under `new artifact` changes a safety-sensitive path.

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner.
- 何を明確にする質問か:
  - Whether `draft-requirement`, `draft-design`, and `draft-plan` are included in the unified `new artifact` command surface and `artifacts/` output location.
- 回答が後続判断へ与える影響:
  - Determines supported artifact type enum, safety checks, tests, docs, and whether ZIP's "draft-* out of scope" guardrail is superseded.

## 質問 (必須)
- pressure-test question:
  - You decided `new doc` need not remain and future artifact creation should be unified under `new artifact`. Does that include the current draft-* artifacts, even though they have special assurance/profile safety gates?
- 質問:
  - `draft-requirement` / `draft-design` / `draft-plan` も `new artifact` で作成し、出力先を `artifacts/` に移しますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - ZIP pack: `draft-requirement` / `draft-design` / `draft-plan` are explicitly excluded from Phase 2 artifact templates.
  - Current runtime: draft documents are created by `new doc draft-*` into `discussions/`.
  - Current runtime: issue `draft-design` / `draft-plan` require valid `.assurance.json` and authorized profile-specific templates; missing/stale/invalid contracts fail without writing.
  - Current tests: `test_new_doc_creates_draft_artifacts_from_scope_specific_templates`, `test_new_doc_issue_design_and_plan_use_authorized_profile_templates`, and fail-closed tests pin this behavior.
  - User decision: `new doc` compatibility is not required; future artifact creation should be unified under `new artifact`.
- local context で解決できたこと:
  - Draft artifacts are not ordinary templates; they source canonical or profile-specific templates and remove placeholder markers.
  - Moving them is feasible but must preserve assurance/profile fail-closed behavior.
- まだ人間判断が必要な理由:
  - The latest command-unification decision conflicts with the ZIP pack's draft-* exclusion, so owner intent is required.

## 回答案 (必須)
- Option A:
  - Full unification: include `draft-requirement`, `draft-design`, and `draft-plan` in `new artifact`; write them to `artifacts/`; preserve all current assurance/profile checks and fail-closed behavior; remove or disable `new doc`.
- Option B:
  - Non-draft unification only: migrate generic artifacts and ADR to `new artifact`, but keep draft-* out of Phase 2 because they are tied to assurance/profile authoring. This keeps ZIP's draft-* exclusion as an explicit exception.
- Option C:
  - Split command but same destination: write draft-* into `artifacts/`, but keep a dedicated command path or subcommand for draft generation because it is safety-sensitive and not a normal template render.

## Codex の分析 (必須)
- 判断軸:
  - Command uniformity, safety preservation, implementation size, and clarity for agents.
- tradeoff:
  - Option A gives the cleanest user-facing command model but expands implementation and test scope significantly. Option B reduces risk but conflicts with the latest command-unification goal. Option C preserves safety semantics but adds conceptual complexity.
- リスク:
  - If draft-* migration drops assurance/profile checks, agents could create misleading draft design/plan artifacts from the wrong template. This must be fail-closed.
- 具体シナリオ / edge case:
  - `new artifact draft-plan --issue iss-00003 --title "Plan Draft"` must fail without a valid `.assurance.json`, just like current `new doc draft-plan`.

## Codex の推奨案 (必須)
- 推奨:
  - Option A, with a strict safety condition.
- 理由:
  - It matches your latest command-unification direction. The key is to treat draft-* as special artifact types with preserved assurance/profile checks, not as ordinary static templates.
- 未回答時の影響:
  - Cannot finalize artifact type catalog, command migration plan, or test coverage for removing `new doc`.

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。
- 回答:
  - 「オプションAを採用します。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `new doc` を削除・無効化する際の CLI failure / migration guidance の形。

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
  - ユーザーが Option A を明示採用した。draft-* も `new artifact` に統一し、出力先を `artifacts/` に移す。ただし現行の assurance/profile 検査と missing/stale/invalid 時の no-write fail-closed behavior は維持する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `draft-requirement` / `draft-design` / `draft-plan` も future artifact creation surface に含め、`new artifact` で作成する。
- `design.md`:
  - Draft artifacts are special artifact types: they write under `artifacts/` but preserve existing canonical/profile template sourcing, `.assurance.json` validation, authorized profile selection, and no-write fail-closed behavior.
- `plan.md`:
  - Draft artifact migration requires dedicated tests replacing current `new doc draft-*` tests with `new artifact draft-*` tests, including issue design/plan assurance failure cases.
- `ADR`:
  - Command unification includes draft artifacts, not only generic working artifacts and ADR.
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Adopted policy supersedes the ZIP pack's draft-* exclusion. Draft-* must be implemented as safety-sensitive artifact types, not static generic templates.

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

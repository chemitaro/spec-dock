---
種別: interview
ID: "20260701t051314z-interview"
タイトル: "Future ADR Command Surface"
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
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t050929z-interview-adr-artifact-boundary.md"
  - "/Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip"
  - "src/spec_dock/assets/spec_dock/docs/workflow_adr.md"
  - "src/spec_dock/assets/spec_dock/docs/reference_naming.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t051314z-interview Future ADR Command Surface

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
    - Future ADR creation requirement and legacy command compatibility.
  - `design.md`:
    - Command routing, template catalog, filename contract, and mirror source discovery.
  - `plan.md`:
    - Issue slicing for new artifact command, ADR behavior, docs/skills updates, and compatibility tests.
  - `ADR`:
    - Decision record for future ADR creation surface.
- chat 上の軽微な一問では足りない理由:
  - `new doc adr` is an existing public command, while `new artifact <template>` was planned with ADR explicitly excluded. Moving future ADRs to `artifacts/` requires a clear command-level compatibility contract.

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner.
- 何を明確にする質問か:
  - Future ADRs under `artifacts/` should be created through which CLI surface.
- 回答が後続判断へ与える影響:
  - Determines whether `adr` enters the `new artifact` template enum, whether `new doc adr` changes output location, and what legacy compatibility tests are required.

## 質問 (必須)
- pressure-test question:
  - You decided new ADR originals should be created under `artifacts/`, while existing ADRs in `discussions/` remain. Should users create those future ADRs via the new artifact command, or should the existing ADR command silently switch destinations?
- 質問:
  - 新規 ADR を `artifacts/` に作成する command surface はどれにしますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - Current `workflow_adr.md`: ADR creation uses `./spec-dock/scripts/spec-dock new doc adr --{initiative|epic|issue} ...` and writes originals to `discussions/`.
  - Current `new doc --help`: `adr` is in the discussion doc type catalog.
  - ZIP pack originally excluded `adr` from artifact templates, but user decision now includes future ADR originals under `artifacts/`.
  - Adopted mixed ADR policy: existing `discussions/` ADRs remain; future ADRs go to `artifacts/`; mirror collects both.
- local context で解決できたこと:
  - Existing `new doc adr` cannot simply disappear because old workflows and docs rely on it.
  - If `adr` becomes a `new artifact` template, it is an exception to the prior 6-template catalog decision and must be documented separately as decision-authority artifact, not generic working artifact.
- まだ人間判断が必要な理由:
  - Backward-compatible command behavior vs explicit new command adoption is a product/API contract decision.

## 回答案 (必須)
- Option A:
  - Explicit new surface: future ADRs are created by `spec-dock new artifact adr --{initiative|epic|issue} ...`; `new doc adr` remains legacy-compatible and continues writing to `discussions/` unless later deprecated. Mirror collects both locations.
- Option B:
  - Existing command switches destination: `new doc adr` remains the ADR command but, after Phase 2, writes new ADR originals to `artifacts/`; legacy existing ADR files under `discussions/` remain and mirror collects both.
- Option C:
  - Dedicated ADR command: introduce `spec-dock new adr --{initiative|epic|issue} ...` writing to `artifacts/`; keep `new doc adr` legacy-compatible for `discussions/`.

## Codex の分析 (必須)
- 判断軸:
  - Explicitness, backward compatibility, user surprise, implementation size, and alignment with future artifact vocabulary.
- tradeoff:
  - Option A is explicit and aligns with artifact migration, but it makes `adr` part of the artifact command despite earlier exclusion. Option B preserves the old command spelling but silently changes output location. Option C is clean semantically but adds another command surface.
- リスク:
  - Option B risks surprising existing users and tests because `new doc adr` would no longer behave like other `new doc` commands. Option C may over-expand CLI surface for this Epic.
- 具体シナリオ / edge case:
  - Existing scripts that run `new doc adr` may expect a `discussions/` path. If the output silently changes to `artifacts/`, downstream path guards may fail.

## Codex の推奨案 (必須)
- 推奨:
  - Option A.
- 理由:
  - It keeps `new doc` compatibility stable and makes the new destination explicit. `adr` can be documented as a special authority-bearing artifact template distinct from generic working artifact templates, while mirror collection bridges old and new locations.
- 未回答時の影響:
  - Cannot finalize command contract, template catalog, or tests for future ADR creation.

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。ただし、互換維持として `new doc` を残す必要はなく、ADR に限らず新規 artifact 作成 command は `new artifact` に統一する。
- 回答:
  - 「オプションAを採用します。うん。また、この後方互反性ですね、保つために、new docコマンドは残さなくてもよいです。うん。完全にnew artifactに移行してよいです。これはADRだけではなくて、それ以下のすべてのアーティファクトは、このnew artifactで作成できるように、コマンドを統一してほしいです。ADRのみを例外にする必要もなく、統一する。で、new docコマンドも不要。後方互換性として残す必要もありません。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `draft-requirement` / `draft-design` / `draft-plan` も `new artifact` の creatable artifact type に含め、出力先を `artifacts/` に移すか。

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
  - ユーザーが `new artifact` への command 統一を明示した。これは ZIP 原案の `new doc` legacy compatibility 維持より強い方針であり、future artifact creation は ADR を含めて `new artifact` に統一する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Phase 2 の future artifact creation command は `new artifact` に統一する。Backward compatibility として `new doc` を残すことは必須ではない。
- `design.md`:
  - `new artifact adr` を含め、新規 artifact type creation surface を統一する。`new doc` は削除または無効化の対象になり得るため、CLI contract / tests / docs / skills の全面更新が必要。
- `plan.md`:
  - `new doc` removal / replacement と command migration tests を後続 Issue に含める。既存 docs / skills / runtime tests の変更範囲が ZIP 原案より広がる。
- `ADR`:
  - Future artifact command unification decision として、ADR には `new doc` compatibility を requirement にしないことを記録する。
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Adopted policy supersedes the earlier compatibility-preserving assumption. It also raises a follow-up question about whether draft artifacts are part of the unified `new artifact` command surface.

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

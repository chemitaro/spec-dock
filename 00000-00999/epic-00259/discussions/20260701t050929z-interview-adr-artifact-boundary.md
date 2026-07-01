---
種別: interview
ID: "20260701t050929z-interview"
タイトル: "ADR Artifact Boundary"
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
  - "/Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip"
  - "src/spec_dock/assets/spec_dock/docs/workflow_adr.md"
  - "src/spec_dock/assets/spec_dock/templates/discussions/adr.md"
  - "src/spec_dock/assets/spec_dock/docs/reference_naming.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t043624z-interview-delegated-authoring-artifact-boundary.md"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t050929z-interview ADR Artifact Boundary

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
    - Phase 2 の scope / non-scope と `artifacts/` の意味。
  - `design.md`:
    - ADR original location、ADR mirror、`new doc adr` / `new artifact` の責務境界。
  - `plan.md`:
    - ADR runtime / sync 変更を後続 Issue に含めるかどうか。
  - `ADR`:
    - この Epic の方針 ADR 自体をどこに置くか。
- chat 上の軽微な一問では足りない理由:
  - ADR は working artifact ではなく architecture decision authority を持ち得るため、`artifacts/` 移行の対象に含めるかどうかで system-of-record と sync mirror 契約が変わる。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner。
- 何を明確にする質問か:
  - ADR original を Phase 2 でも legacy `new doc adr` / `discussions/` に残すか、`artifacts/` に移すか。
- 回答が後続判断へ与える影響:
  - ADR workflow、reference_naming、sync_state ADR mirror、template catalog、Issue breakdown の範囲が決まる。

## 質問 (必須)
- pressure-test question:
  - delegated authoring output は Phase 2 で `artifacts/` に移すことにしました。一方 ADR は accepted decision authority を持ち得る別種の記録です。ADR original もこの Epic で `artifacts/` に移しますか。
- 質問:
  - ADR は Phase 2 でも既存 `new doc adr` / `discussions/` original + `spec-dock/adrs/` mirror のまま残しますか。それとも ADR original も `artifacts/` へ移す対象に含めますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - ZIP pack: ADR は Phase 2 対象外、`templates/artifacts/adr.md` は追加しない、既存 `new doc adr` を維持すると明記。
  - `workflow_adr.md`: ADR original は常に scope-local `discussions/` に残り、mirror / sync があっても original location は変わらない。
  - `guide.md` / `workflow-tree.md`: `spec-dock/adrs/` は generated ADR mirror。
  - `sync_state.py`: ADR mirror rebuild logic があり、ADR sources を discussion docs から収集する。
  - prior interview: delegated authoring output は Phase 2 で `artifacts/` へ移行する方針を採用済み。
- local context で解決できたこと:
  - ADR は raw / draft / research とは違い、accepted 後に architecture decision authority を持ち得る。
  - ADR original location を動かす場合、artifact command だけでなく ADR mirror source collection と naming docs の変更が必要になる。
- まだ人間判断が必要な理由:
  - delegated authoring を scope 拡張したため、ZIP pack の「ADR 対象外」をそのまま維持するか再確認が必要。

## 回答案 (必須)
- Option A:
  - Keep ADR out of Phase 2: ADR original は既存 `new doc adr` / `discussions/` に残し、`spec-dock/adrs/` mirror も現行 contract を維持する。`artifacts/` は working artifacts と delegated authoring output の store とし、accepted decision authority の original store にはしない。
- Option B:
  - Move ADR originals to artifacts: ADR original も `artifacts/` に移し、`new artifact adr` または ADR-specific artifact command を追加する。ADR mirror source collection、workflow_adr、reference_naming、sync tests も Phase 2 scope に含める。
- Option C:
  - New ADRs only to artifacts: 既存 ADR original は `discussions/` に残し、Phase 2 後の新規 ADR だけ `artifacts/` に作成する。old/new mixed ADR source collection と mirror support を追加する。

## Codex の分析 (必須)
- 判断軸:
  - `artifacts/` を working artifact store と定義するか、decision authority original も含む broader store と定義するか。
- tradeoff:
  - ADR も移すと表面的な統一感は増えるが、working artifact と accepted decision authority の境界が曖昧になり、ADR mirror / naming / sync の変更量が大きい。
- リスク:
  - Option B / C は Phase 2 の blast radius を大きくし、ADR mirror の source-of-truth migration を伴う。既存 ADR links / sync behavior への退行リスクが高い。
- 具体シナリオ / edge case:
  - この Epic の方針 ADR は今すぐ作成する必要があり、`new artifact` はまだ存在しない。ADR を `artifacts/` only にすると、Phase 2 自身の方針 ADR 作成が bootstrapping 問題になる。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - ADR は working artifact ではなく durable decision record であり、ZIP pack の明示的 non-goal と現行 ADR mirror contract を保つ方が安全。delegated authoring は evidence output なので `artifacts/` 移行対象にできるが、ADR original は authority-bearing document として別に扱うのが境界として明確。
- 未回答時の影響:
  - ADR draft の保存先、ADR workflow の変更有無、Issue breakdown に ADR migration slice を含めるかを確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User selected a mixed policy: existing ADR originals under `discussions/` remain in place; newly created ADR originals move to `artifacts/`; ADR mirror collection must read both `discussions/` and `artifacts/`.
- 回答:
  - 「オプションAを採用します。これから新たに作成するADRはArtifactsに作成をします。一方で、これまでに作成してきたDiscussionsにあるADRはそのまま残します。そして、specs-docs/adrsにシンボリックリンクを収集する仕組みがありますが、これはDiscussionsとArtifacts両方を収集するようにしてください。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - 新規 ADR を `artifacts/` に作成する command surface を、`new artifact adr` にするか、`new doc adr` の出力先だけを切り替えるか。

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
  - ユーザーが mixed ADR policy を明示した。ZIP 原案の「ADR は Phase 2 対象外」から変更し、新規 ADR original は `artifacts/` に移す。ただし既存 ADR original は `discussions/` に残し、mirror collection は両方を対象にする。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Future ADR original creation is in scope for Phase 2 and should target `artifacts/`; existing ADR originals under `discussions/` remain valid and are not migrated.
- `design.md`:
  - ADR mirror collection must collect ADR originals from both legacy `discussions/` and new `artifacts/`. The source-of-truth rules must distinguish existing legacy ADRs from future ADR creation.
- `plan.md`:
  - ADR command/template/mirror behavior requires a dedicated implementation slice, including sync mirror source collection and tests for mixed old/new ADR sources.
- `ADR`:
  - The future-only adoption ADR must record that new ADR originals move to `artifacts/`, while existing `discussions/` ADR originals remain valid and mirrored.
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Adopted policy is a modified / mixed option, not the originally recommended Option A. It expands Phase 2 to include future ADR original creation under `artifacts/` and mixed-source ADR mirror collection.

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

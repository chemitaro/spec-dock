---
種別: interview
ID: "20260701t043248z-interview"
タイトル: "Artifacts Future Only Policy Boundary"
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
  - "spec-dock/docs/workflow_clarification.md"
  - "spec-dock/docs/authoring/decision-routing.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_adr.md"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t043248z-interview Artifacts Future Only Policy Boundary

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
    - `artifacts/` と `discussions/` の normative policy、scope / non-scope、compatibility requirements。
  - `design.md`:
    - `new artifact` と legacy `new doc` の責務境界、validation / sync / projection の扱い。
  - `plan.md`:
    - Issue 01 を独立 Issue ではなく Epic / ADR decision として先に閉じる前提、および後続 Issue の acceptance。
  - `ADR`:
    - future-only adoption policy を長期に参照できる architecture decision として残すかどうか。
- chat 上の軽微な一問では足りない理由:
  - この回答は docs の表現だけでなく、runtime command の互換性、agent guidance、validation の厳しさ、後続 Issue 分割に影響する。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner。
- 何を明確にする質問か:
  - Phase 2 後の `discussions/` を、どの強さで legacy 扱いするか。
- 回答が後続判断へ与える影響:
  - ADR の Decision、Epic requirement の MUST / SHOULD wording、Issue 04 / 05 / 07 の command and docs behavior が決まる。

## 質問 (必須)
- pressure-test question:
  - `artifacts/` を新しい標準にする一方で、既存互換として残す `discussions/` に対して、どの程度の新規利用制限を明文化しますか。
- 質問:
  - Phase 2 の方針として、`discussions/` は今後どの位置づけにしますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - ZIP pack: README / codex-handoff / Epic / Issues 01-08 / reference command-contract / filename-contract / guardrails / expected-final-state / validation-plan / suggested-file-map。
  - `spec-dock/docs/workflow_clarification.md`: 重要判断は interview で確認し、採用後に canonical docs / ADR / report ledger へ反映する。
  - `spec-dock/docs/authoring/decision-routing.md`: cross-issue design backbone は Epic、long-lived architecture decision は ADR に置く。
  - `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`: ADR は scope-local `discussions/` に原本を作り、未決の間は draft のままにする。
  - 現行 implementation: `new doc` は `discussions/` に書き、draft docs と ADR も同じ surface を使う。
- local context で解決できたこと:
  - Issue 01 は単一 Issue に閉じる実装作業ではなく、複数後続 Issue の前提になる Epic-level policy decision である。
  - Phase 2 は migration ではなく future-only adoption であり、既存 `discussions/` と既存リンクは壊さない。
  - `draft-requirement` / `draft-design` / `draft-plan` と ADR は Phase 2 の artifact templates には含めない。
- まだ人間判断が必要な理由:
  - `discussions/` を「互換のため有効だが新規作成は原則しない」とするのか、「新規にも許容する soft preference」とするのかで、docs / skills / tests / diagnostics の強さが変わる。

## 回答案 (必須)
- Option A:
  - Compatibility-only legacy: 既存 `discussions/` は valid / readable / link-stable のまま残す。Phase 2 後の新規 generic working artifact は `new artifact` / `artifacts/` を MUST とする。ただし `new doc` は互換のため残し、draft-* と ADR は Phase 2 では既存 `new doc` 経路を維持する。警告や失敗は導入しない。
- Option B:
  - Soft preference: 新規 working artifact は `artifacts/` を SHOULD とするが、research / interview / disc / scratch / pr-repair-batch の `new doc` による新規作成も通常利用として許容する。skills/docs は推奨を変えるが、legacy という表現は弱める。
- Option C:
  - Hard deprecation: Phase 2 後、draft-* / ADR 以外の `new doc` 新規作成に警告または失敗を導入する。既存 `discussions/` は読むが、新規 generic working artifact 作成は runtime で強制的に `artifacts/` へ寄せる。

## Codex の分析 (必須)
- 判断軸:
  - future-only adoption の強さ、既存互換の安全性、agent guidance の明確さ、実装リスク、後続 Issue のテスト可能性。
- tradeoff:
  - 強い legacy 化ほど将来の混乱は減るが、既存 `new doc` workflow や現在の clarification / ADR lifecycle との過渡期が難しくなる。
- リスク:
  - Option B は「標準を変えたのに実運用は変わらない」リスクがある。Option C は互換を壊さないという Phase 2 guardrail に近接し、既存 agent / docs / tests を一気に壊すリスクがある。
- 具体シナリオ / edge case:
  - この Epic 自身の clarification / ADR は、`new artifact` 実装前なので legacy `new doc` / `discussions/` を使う必要がある。
  - `new artifact` 実装後も ADR と draft-* は Phase 2 対象外なので、少なくともその範囲では `new doc` が残る。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - ZIP pack の guardrails と最も整合し、既存を壊さず、しかし future default を明確に変えられる。`new doc` を削除・警告化しないため互換リスクを抑えつつ、skills/docs では新規 generic working artifact の作成先を `artifacts/` に固定できる。
- 未回答時の影響:
  - ADR の Decision、Epic requirement、後続 Issue 04 / 05 / 07 の acceptance wording を確定できない。

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
  - delegated authoring / sub-agent drafts / scope-local direct-write outputs も Phase 2 で `artifacts/` に移すか、既存 `discussions/` 経路を例外として残すか。

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
  - ユーザーが Option A を明示採用した。既存 `discussions/` を壊さず、future default を `artifacts/` に切り替える方針として後続設計の基準にできる。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `discussions/` は compatibility-only legacy として valid / readable / link-stable に維持する。新規 generic working artifact は `artifacts/` を MUST とする。
- `design.md`:
  - `new artifact` は `artifacts/` に書く。legacy `new doc` は互換のため維持し、Phase 2 では警告や失敗を導入しない。
- `plan.md`:
  - Issue 01 相当の policy decision は Epic / ADR で先に確定し、後続 Issue の acceptance wording に反映する。
- `ADR`:
  - Future-only adoption policy の Decision として Option A を記録する。
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Option A は採用済み。ただし delegated authoring output の扱いは次の interview で分離して確定する。

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

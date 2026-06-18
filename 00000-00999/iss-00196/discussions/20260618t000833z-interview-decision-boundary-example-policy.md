---
種別: interview
ID: "20260618t000833z-interview"
タイトル: "Decision Boundary Example Policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00196"]
関連: []
scope: "issue"
scope_id: "iss-00196"
created_at: "2026-06-18T00:08:33Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "GitHub issue #196"
  - "spec-dock/active/issue/discussions/20260617t154620z-research-decision-implementation-layer-source-grounding.md"
  - "spec-dock/active/issue/discussions/20260617t154625z-interview-decision-boundary-primary-intent.md"
  - "spec-dock/active/issue/discussions/20260618t000451z-disc-deep-consultant-decision-scope-synthesis.md"
  - "deep-consultant:019ed813-114a-7550-80b3-2669ab29325e"
  - "spec-dock/active/issue/discussions/20260618t001353z-disc-deep-consultant-example-policy-synthesis.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260618t000833z-interview Decision Boundary Example Policy

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
    - Examples / non-scope / acceptance criteria が変わる。
  - `design.md`:
    - workflow docs / templates に載せる example policy が変わる。
  - `plan.md`:
    - docs/template update step の編集対象と検証観点が変わる。
  - `ADR`:
    - 通常は不要。ただし project-specific examples を shipped docs に継続採用するなら documentation policy として ADR 候補になり得る。
- chat 上の軽微な一問では足りない理由:
  - 回答により shipped docs/templates の例示方針が変わり、将来の agent context surface に残るため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / user
- 何を明確にする質問か:
  - Persistent workflow docs / templates に project-specific dogfooding example を入れるか、generic example に留めるか。
- 回答が後続判断へ与える影響:
  - `requirement.md` の scope / non-scope、`design.md` の example policy、`plan.md` の docs/template update step が決まる。

## 質問 (必須)
- pressure-test question:
  - SpecDock の shipped docs/templates は、今回のきっかけになった `management_core` / shared kernel boundary のような具体例を持つべきか、それとも汎用例だけにして project-specific context は issue evidence に留めるべきか。
- 質問:
  - `iss-00196` で追加する decision-boundary の例示は、どの粒度にしますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。必要なら、載せたい具体例や避けたい表現も教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#196` は、dogfooding で `management_core` の位置づけや shared kernel boundary のような判断を Issue として先に分解してしまった違和感を背景にしている。
  - Parent epic は shipped docs / skills / templates の agent-facing context surface を扱う。
  - Parent epic は provider-side source を shipped asset authority とし、dogfooding mirror を validation target とする。
  - Deep consultant は minimal template readiness prompts を推奨しつつ、template を policy authority にしてはいけないと警告した。
- local context で解決できたこと:
  - Examples are useful for agent prompt/context reliability.
  - Project-specific dogfooding context is valid evidence for this issue.
  - Shipped docs/templates are reused by other repos, so overly project-specific examples can reduce portability.
- まだ人間判断が必要な理由:
  - How much project-specific dogfooding narrative should remain in shipped docs is a product/documentation judgment, not derivable from local source alone.

## 回答案 (必須)
- Option A:
  - Generic examples only. Use abstract examples such as `shared ownership boundary` / `cross-module dependency direction`; keep `management_core` / shared kernel details only in issue discussions/report.
- Option B:
  - Include one short dogfooding example in docs/templates, naming `management_core` / shared kernel boundary as the motivating case.
- Option C:
  - Hybrid: shipped docs/templates use generic examples, while this issue's requirement/report records `management_core` / shared kernel as source evidence and optional dogfooding note. No product-specific names in templates.
- Option C+:
  - Option C に加えて、generic examples must be concrete enough to be actionable を明示する。例: shared ownership boundary, cross-module dependency direction, platform/shared-kernel extraction, workflow policy vs implementation task boundary.

## Codex の分析 (必須)
- 判断軸:
  - Portability of shipped docs, agent comprehension, evidence traceability, risk of product-specific leakage into generic scaffolds.
- tradeoff:
  - A is clean and portable, but may feel too abstract.
  - B is concrete, but risks making reusable SpecDock docs feel tied to one product architecture.
  - C preserves traceability while keeping shipped surfaces portable.
  - C+ keeps C's portability, while preventing examples from becoming too abstract to guide agents.
- リスク:
  - Product-specific examples in templates may be copied into downstream repos and confuse users.
  - Generic examples without issue evidence may lose the original failure mode.
- 具体シナリオ / edge case:
  - A future agent reading only a template should understand the boundary without needing `management_core` context.
  - A maintainer auditing this issue should still see why the rule was introduced.

## Codex の推奨案 (必須)
- 推奨:
  - Option C+.
- 理由:
  - Deep consultant independently recommended C and strengthened it as C+: product-specific dogfooding names should stay out of shipped templates, but generic examples must be concrete/actionable enough for agents and future eval scenarios.
- 未回答時の影響:
  - Requirement scope can say examples are needed, but cannot specify whether docs/templates may include product-specific names.

## ユーザー回答 (回答後に必須)
- answer capture:
  - User challenged the premise that templates should carry examples. Templates are for producing clean requirement/design/plan artifacts. Examples may help during authoring, but once the artifact is created they become noise for downstream implementation agents.
  - User later adopted this revised clean-template policy as the current fixed direction: templates stay thin, skills stay thin for workflow control, and detailed conceptual explanation plus concrete examples live in documentation.
- 回答:
  - Templates should remain minimal and clean, without extra example text. If concrete examples are needed to teach models how to author decision-boundary content, those examples should live in documentation, not in templates. The completed requirement/design docs should not carry instructional examples that distract future agents.
  - Skills should also remain thin: they should route and manage workflow, while deep conceptual understanding belongs in docs.
- 回答日時:
  - 2026-06-18

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
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Adopt the clean-template revision fully. Templates are final-artifact scaffolds, not authoring textbooks. Documentation may include concrete, reusable examples for authoring guidance; templates should contain only minimal prompts needed in the final artifact. Skills should remain lightweight workflow gates and reference docs for conceptual detail.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Required scope should distinguish docs guidance, skill workflow routing, and template scaffolds. Docs may include generic concrete examples; templates and skills should stay clean and minimal.
- `design.md`:
  - Design must place examples in docs/authoring guidance, not in templates or skill bodies. Template changes, if any, should be minimal field prompts without examples.
- `plan.md`:
  - Plan should include verification that templates do not embed examples or product-specific dogfooding details.
- `ADR`:
  - Not required.
- reflected_to 更新方針:
  - Reflect after canonical requirement/report update.
- adoption reflection:
  - This answer supersedes the earlier C+ template-example recommendation where it implied examples could appear in templates.

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

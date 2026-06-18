---
種別: disc
ID: "20260618t001353z-disc"
タイトル: "Deep Consultant Example Policy Synthesis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00196"]
関連: []
authority: "proposed"
derived_from:
  - "deep-consultant:019ed813-114a-7550-80b3-2669ab29325e"
  - "spec-dock/active/issue/discussions/20260618t000833z-interview-decision-boundary-example-policy.md"
  - "spec-dock/active/issue/discussions/20260617t154620z-research-decision-implementation-layer-source-grounding.md"
reflected_to: []
---

# 20260618t001353z-disc Deep Consultant Example Policy Synthesis

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - `iss-00196` で追加する decision-boundary examples を、shipped workflow docs/templates に product-specific dogfooding case として載せるか、generic examples に留めるか。
- この synthesis が必要な理由:
  - User asked for deep-consultant decision support before answering the interview. The decision affects shipped reusable scaffold text and issue-local evidence boundaries.

## derived question sheets / research (必須)
- `interview`:
  - `20260618t000833z-interview-decision-boundary-example-policy.md`
- `research`:
  - `20260617t154620z-research-decision-implementation-layer-source-grounding.md`
- その他の根拠:
  - Deep consultant result from `019ed813-114a-7550-80b3-2669ab29325e`.

## synthesis (必須)
- 合意済みのこと:
  - Adopted Option D means templates may carry minimal readiness prompts, but templates are not canonical policy authority.
  - `management_core` / shared kernel boundary was the dogfooding motivation for this issue.
  - Provider-side docs/templates are shipped scaffold surfaces copied into consumer repositories.
- 未合意 / 未確定のこと:
  - Whether shipped docs/templates may name product-specific dogfooding concepts.
- source-grounded に解決できたこと:
  - Product-specific examples are useful as issue-local evidence, but shipped surfaces need portability.
  - Future eval/harness can derive reusable scenarios from dogfooding evidence without embedding product names in templates.

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - Clean and portable shipped surfaces.
  - Cons:
    - Can become too abstract; may lose motivation and dogfooding traceability if issue evidence is not kept.
- Option B:
  - Pros:
    - Concrete and memorable for agents.
  - Cons:
    - Product-specific names leak into consumer repos and may be mistaken for standard SpecDock policy or examples.
- Option C:
  - Pros:
    - Separates reusable shipped surfaces from issue-local dogfooding evidence.
    - Preserves portability and traceability.
  - Cons:
    - Generic examples must be concrete enough; vague abstractions would still fail agents.
- Option C+:
  - Pros:
    - Same as C, but explicitly requires generic examples to be actionable and scenario-like.
  - Cons:
    - Requires careful wording to avoid drifting into B.

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - Persistent shipped docs/templates should use product-agnostic examples only.
  - Generic examples should still be concrete enough for agent decision-making, e.g. shared ownership boundary, cross-module dependency direction, platform/shared-kernel extraction, workflow policy vs implementation task boundary.
  - `management_core` / shared kernel dogfooding case should be recorded in issue requirement/report as source evidence and motivation.
- まだ proposal に留める理由:
  - User has not yet adopted this interview answer.

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Add example policy and acceptance criteria.
- `design.md`:
  - Decide exact wording and separation between generic shipped examples and issue-local dogfooding evidence.
- `plan.md`:
  - Add scenario inspection for product-specific leakage and actionable generic examples.
- `ADR`:
  - Not required unless documentation example policy becomes a broader durable policy.
- `report.md` Evidence Adoption Ledger:
  - Record consultant recommendation and user adoption decision.

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `interview`, `disc`, `requirement.md`, `design.md`, `plan.md`, `report.md`

## 推奨案 (必須)
- Deep consultant recommends Option C, strengthened as C+:
  - Shipped docs/templates use only generic, reusable decision-boundary examples.
  - Product-specific dogfooding cases such as `management_core` positioning / shared kernel boundary must not appear in shipped templates.
  - Those cases should be recorded in issue requirement/report as source evidence and may be used to derive future generic eval scenarios.
  - Generic examples must be concrete enough to guide agents; abstract labels alone are insufficient.

## 推奨反映先 (必須)
- `requirement.md`:
  - Require reusable product-agnostic shipped examples, plus issue-local dogfooding evidence.
- `design.md`:
  - Design example wording with product-specific leakage guard.
- `plan.md`:
  - Verify no provider-side scaffold text names dogfooding-specific concepts; verify at least one architectural boundary example and one workflow decomposition example.
- `ADR`:
  - None by default.
- `report.md` Evidence Adoption Ledger:
  - Record consultant evidence and user answer.

## 未採用 / deferred 理由 (必須)
- 未採用:
  - B should not be adopted because product-specific names in shipped scaffold text reduce reuse and can be mistaken for standard policy.
  - A should not be adopted alone because it risks losing motivation and future eval scenario traceability.
- deferred:
  - Full eval harness implementation.
  - Solving the original `management_core` / shared kernel architecture decision.

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Ask user whether to adopt C+ as the answer for the example policy interview.
- 追加で作る discussion docs:
  - None unless user answer introduces a new high-impact question.

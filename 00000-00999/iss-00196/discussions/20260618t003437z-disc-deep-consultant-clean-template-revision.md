---
種別: disc
ID: "20260618t003437z-disc"
タイトル: "Deep Consultant Clean Template Revision"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00196"]
関連: []
authority: "proposed"
derived_from:
  - "deep-consultant:019ed826-05d9-7863-be3d-1d2fb0744c95"
  - "spec-dock/active/issue/discussions/20260618t000833z-interview-decision-boundary-example-policy.md"
  - "spec-dock/active/issue/discussions/20260618t001353z-disc-deep-consultant-example-policy-synthesis.md"
reflected_to: []
---

# 20260618t003437z-disc Deep Consultant Clean Template Revision

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
  - Whether examples should be placed in templates at all, given templates become final requirement/design/plan artifacts read by downstream implementation agents.
- この synthesis が必要な理由:
  - User challenged the previous C/C+ recommendation as insufficiently separating authoring-time guidance from final-artifact cleanliness.

## derived question sheets / research (必須)
- `interview`:
  - `20260618t000833z-interview-decision-boundary-example-policy.md`
- `research`:
  - `20260617t154620z-research-decision-implementation-layer-source-grounding.md`
- その他の根拠:
  - Deep consultant result from `019ed826-05d9-7863-be3d-1d2fb0744c95`.

## synthesis (必須)
- 合意済みのこと:
  - Templates are scaffolds for final artifacts, not primary teaching material.
  - Completed requirement/design/plan artifacts are downstream context for implementation agents.
  - Examples are useful for authoring models, but can become noise if they remain in final artifacts.
  - Templates should remain subordinate scaffolds and not canonical policy authority.
- 未合意 / 未確定のこと:
  - none for this point if user adopts the consultant-supported clean-template policy.
- source-grounded に解決できたこと:
  - The previous C/C+ recommendation should be revised: generic examples should not be added to templates merely because they are product-agnostic.

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - Examples in templates help authoring-time models.
  - Cons:
    - Examples persist into final artifacts and create downstream noise.
- Option B:
  - Pros:
    - Examples in docs/authoring guidance influence authoring agents without polluting final artifacts.
  - Cons:
    - Requires planning skills/docs to route authoring agents to guidance before template completion.
- Option C:
  - Pros:
    - Clean templates plus docs examples preserve final-artifact quality and model guidance.
  - Cons:
    - The authoring workflow must enforce reading the docs/skill guidance; templates alone will not teach all examples.

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - Examples belong in docs / authoring guidance / planning skills / issue-local evidence, not templates.
  - Templates should contain only headings, minimal prompts, and checklist fields that are meaningful in the completed artifact.
  - Avoid `例:` / sample prose / product-specific references in templates unless there is a generation-time stripping mechanism, which is not in scope.
  - If template guidance is necessary, phrase it as a final-artifact field or checkbox, not as an example.
- まだ proposal に留める理由:
  - The user has provided the core judgment, but canonical requirement/report have not yet adopted it.

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Add clean-template policy to required scope / acceptance criteria.
- `design.md`:
  - Design file responsibilities: examples in docs/authoring guidance; templates as clean scaffolds.
- `plan.md`:
  - Add verification that templates do not include examples/instructional noise.
- `ADR`:
  - Not required.
- `report.md` Evidence Adoption Ledger:
  - Record supersession of previous C+ template-example recommendation.

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
- Deep consultant revised the prior C/C+:
  - Templates should generally contain no examples.
  - Examples should live in docs / authoring guidance / planning skill references / issue-local evidence.
  - Templates should remain minimal final-artifact scaffolds: headings, short questions, checklist fields.
  - Generic examples in templates are still noise if they remain in completed artifacts.
- This supersedes the prior reading of C+ where generic concrete examples might appear in templates.

## 推奨反映先 (必須)
- `requirement.md`:
  - Require examples-out-of-templates and guidance-in-docs.
- `design.md`:
  - Specify docs/templates separation and clean-template verification.
- `plan.md`:
  - Include inspection step for templates to ensure no examples/instructional noise are added.
- `ADR`:
  - none
- `report.md` Evidence Adoption Ledger:
  - Record user correction, consultant revision, and adoption decision.

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Previous C+ implication that generic examples may be placed in templates should be rejected.
- deferred:
  - Generation-time stripping of authoring hints from templates.
  - Full eval harness.

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Adopt clean-template policy in `requirement.md` and `report.md`.
- 追加で作る discussion docs:
  - None.

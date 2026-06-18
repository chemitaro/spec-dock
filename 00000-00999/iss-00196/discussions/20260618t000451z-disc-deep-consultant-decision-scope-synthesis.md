---
種別: disc
ID: "20260618t000451z-disc"
タイトル: "Deep Consultant Decision Scope Synthesis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00196"]
関連: []
authority: "proposed"
derived_from:
  - "deep-consultant:019ed80a-0631-7543-bdfe-f5896e16e451"
  - "spec-dock/active/issue/discussions/20260617t154620z-research-decision-implementation-layer-source-grounding.md"
  - "spec-dock/active/issue/discussions/20260617t154625z-interview-decision-boundary-primary-intent.md"
reflected_to: []
---

# 20260618t000451z-disc Deep Consultant Decision Scope Synthesis

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
  - `iss-00196` の scope boundary として、workflow docs / skills だけに留めるか、Issue / Epic template readiness checklist まで必須に含めるか。
- この synthesis が必要な理由:
  - User asked for independent deep-consultant support before deciding. The consultant was instructed not to conform to the parent agent recommendation and to prioritize harness / prompt / context engineering correctness.

## derived question sheets / research (必須)
- `interview`:
  - `20260617t154625z-interview-decision-boundary-primary-intent.md`
- `research`:
  - `20260617t154620z-research-decision-implementation-layer-source-grounding.md`
- その他の根拠:
  - Deep consultant result from `019ed80a-0631-7543-bdfe-f5896e16e451`.

## synthesis (必須)
- 合意済みのこと:
  - `iss-00196` should not implement runtime gate / CLI enforcement / automated harness in this issue.
  - Workflow docs and planning skills need explicit decision-locus / decision-only issue detection guidance.
  - Templates must not become compliance authority.
- 未合意 / 未確定のこと:
  - Whether minimal Issue / Epic template readiness checklists are mandatory in this issue.
- source-grounded に解決できたこと:
  - Parent epic allows docs / skills / templates context surface cleanup.
  - Parent epic defers runtime enforcement until cleaned text surfaces stabilize.
  - Existing docs mention scope roles but do not yet provide a practical decision-routing gate.

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - Smallest scope; avoids template drift.
  - Cons:
    - Too weak for first-read reliability and future harness/eval surfaces because durable issue artifacts would lack readiness prompts.
- Option B:
  - Pros:
    - Strongest immediate context surface; rule appears where agents create/read work.
  - Cons:
    - Can scope-creep into broad template redesign or make scaffolds look like compliance authority.
- Option C:
  - Pros:
    - Allows design-phase split if template impact becomes too large.
  - Cons:
    - If phrased loosely, it can collapse back to A by deferring template work too easily.
- Option D: B-lite / contract-first
  - Pros:
    - Keeps minimal template readiness prompts mandatory while preserving docs/skills as canonical policy authority.
    - Better supports harness/prompt/context engineering by placing structured cues in durable issue/epic artifacts.
  - Cons:
    - Requires careful wording so templates remain prompts/scaffolds, not independent rules.

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - Add decision locus contract to `workflow_issue.md`, `workflow_epic.md`, and `workflow_initiative.md`.
  - Add decision-only issue detection gate to `spec-dock-issue-planning` skill.
  - Add minimal Issue and Epic template readiness prompts that point back to docs/skills and do not invent separate policy.
  - Define lightweight local judgment exception: narrow, reversible, implementation-adjacent decisions may stay in Issue.
- まだ proposal に留める理由:
  - User has not yet approved the final scope boundary.

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Scope / non-scope / acceptance criteria should adopt Option D if user approves.
- `design.md`:
  - Decide exact docs / skills / template file changes and wording ownership.
- `plan.md`:
  - Split docs/skills and template checklist work into separate reviewable steps if needed.
- `ADR`:
  - Not mandatory unless decision-locus policy is judged durable and surprising enough to require ADR.
- `report.md` Evidence Adoption Ledger:
  - Record consultant evidence and user decision adoption.

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - maybe
- hard to reverse:
  - no, if limited to docs/skills/templates; yes only if later runtime enforcement is added
- surprising without context:
  - maybe
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `interview`, `disc`, `requirement.md`, `design.md`, `plan.md`, `report.md`

## 推奨案 (必須)
- Deep consultant recommends Option D: B-lite / contract-first.
- Option D means workflow docs + skills + minimal Issue/Epic template readiness checklists are mandatory, but templates remain prompts/context surfaces and must not become policy authority.
- Consultant explicitly judged A too weak, B directionally correct but too broad if unconstrained, and C risky unless it says minimal checklist is mandatory and only broad migration can be follow-up.

## 推奨反映先 (必須)
- `requirement.md`:
  - Adopt Option D as required scope if user approves.
  - Include decision locus, issue readiness, epic decision/readiness, lightweight local judgment exception, scenario checks, and out-of-scope runtime enforcement.
- `design.md`:
  - Keep policy authority in workflow docs / skills; use templates as short readiness prompts with references.
- `plan.md`:
  - Include separate steps for workflow docs/skills and minimal template checklist, with review gates.
- `ADR`:
  - Defer unless requirement/design reveals a durable architecture decision beyond docs/skill/template guidance.
- `report.md` Evidence Adoption Ledger:
  - Record deep-consultant evidence, user answer, adoption status, and canonical reflection targets.

## 未採用 / deferred 理由 (必須)
- 未採用:
  - A should not be adopted as-is because it leaves durable Issue/Epic artifact surfaces without readiness cues.
  - B should not be adopted without limits because template overgrowth can create drift and false authority.
- deferred:
  - Runtime gate / CLI enforcement / automated harness.
  - Broad migration of existing issues/epics or large template redesign.

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Ask user whether to adopt Option D.
  - If approved, update the unanswered interview with the user answer, then reflect into `requirement.md` and `report.md` Evidence Adoption Ledger / Spec Authoring Gate.
- 追加で作る discussion docs:
  - None unless user answer introduces a new high-impact question.

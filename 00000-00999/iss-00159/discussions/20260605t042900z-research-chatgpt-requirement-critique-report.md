---
種別: research
ID: "20260605t042900z-research"
タイトル: "ChatGPT Requirement Critique Report for Issue Planning Skill Spine"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00159"]
関連:
  - "20260605t041318z-research"
  - "epic-00158"
authority: "evidence"
answer_now_used: false
thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224da1-5968-83a6-bc8b-79ae1933982e"
extraction_method: "Chrome DOM assistant message extraction; no copy button or clipboard"
completion_signal: "assistant message present; stop control absent; thinking text absent; stable after second check"
---

# 20260605t042900z-research ChatGPT Requirement Critique Report for Issue Planning Skill Spine

## 実行メタデータ

- thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224da1-5968-83a6-bc8b-79ae1933982e
- project_boundary: Codex-only Project under for codex app
- model_visible: じっくり思考 Pro
- answer_now_used: false
- extraction_method: Chrome DOM assistant message extraction; no copy button or clipboard
- completion_signal: assistant message present; stop control absent; thinking text absent; stable after second check

## 位置づけ

この report は ChatGPT による外部 critique evidence である。formal `spec-reviewer` pass / fail 判定ではない。

## ChatGPT 出力

結論

この requirement draft は、ユーザー最新 insight を概ね正しく捉えています。
つまり、skill には agent が最初に守るべき mandatory workflow spine を薄く・明示的に置き、各 artifact の意味、field semantics、詳細 schema、長い authoring guidance は docs 側に残す、という分離は適切に反映されています。

ただし、formal spec-reviewer に送る前に小さく revision することを推奨します。
理由は、現状の draft summary だと「workflow spine」「fresh reviewer pass」「skill alone exposes」「over-copy しない」の境界がまだやや曖昧で、reviewer が testability / scope clarity の観点で finding を出す可能性があるためです。

外部影響について: 提示された task package 以外の記憶、過去チャット、未提示 repo 状態、Web 情報は使っていません。外部影響は検出していません。

1. Overall judgment
Advisory judgment

Revise first, then send to formal spec-reviewer.

この requirement は方向性としては良いです。特に以下は強いです。

runtime gate / CLI enforcement を first issue から外している。

skill に置くべきものを「必須手順の spine」に限定している。

detailed schema / field semantics を docs に残す方針が明確。

delegated drafts を canonical artifact と混同しない制約が入っている。

stale / failed / unavailable / provisional reviewer result を pass 扱いしない方針が入っている。

一方で、formal review 前に詰めたい点は以下です。

fresh spec-reviewer pass の意味を最小限で定義する。

workflow spine に最低限含める operational content を列挙する。

skill alone exposes phase order を、より testable な acceptance criterion にする。

plan.md must be executable を skill にどの深さで書くかを明確にする。

dogfooding mirror の open question を requirement 内で閉じる。

2. Findings ordered by severity
High: fresh spec-reviewer pass がまだ曖昧

Confirmed from supplied context: draft は requirement → fresh reviewer pass → design → fresh reviewer pass → plan → fresh reviewer pass → execution handoff を scope に入れている。非 pass 状態も pass ではないと明記する方針です。

Issue:
fresh が何に対して fresh なのかが requirement 上で曖昧です。時刻ベースなのか、artifact の最新変更後なのか、canonical candidate に対してなのかが不明なままだと、design / plan でぶれます。

Recommended requirement edit:

Markdown
A fresh `spec-reviewer` pass means the reviewer was run against the current artifact candidate for the phase after the latest substantive change to that artifact. A pass from before later edits, from a different artifact, from a delegated draft not adopted by the main orchestrator, or from an earlier phase does not satisfy the gate.

これは detailed reviewer policy ではなく、skill に載せるべき minimal gate semantics です。

High: workflow spine の最低内容を requirement で定義した方がよい

Issue:
draft は「mandatory workflow spine を skill に追加する」と言っていますが、spine に最低限何が含まれるべきかがやや設計者任せです。これだと implementation がまた bullet-only reference list に近づくリスクがあります。

Recommended requirement edit:

Markdown
The skill must include a short, front-loaded `Mandatory Issue Authoring Workflow` section. Reading the skill alone must be enough for an agent to know the required phase order, the review gate before each promotion, the non-pass states that block promotion, the canonical ownership rule, the unresolved-gap fallback, and the execution handoff blocker for non-executable plans.

この wording なら、docs の長い内容をコピーせずに、skill 側に必要な operational spine を置けます。

High: AC-001 がやや主観的

Current AC:

AC-001: skill alone exposes phase order.

Issue:
「exposes」は reviewer によって解釈が分かれます。単に doc link があるだけでも expose と読めてしまう可能性があります。

Recommended replacement:

Markdown
AC-001: A reviewer reading only `SKILL.md` can identify the mandatory sequence `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> execution handoff`, without opening linked docs.

さらに強くするなら:

Markdown
AC-001: The required sequence appears in a named mandatory workflow section before the reference-doc list.

これは instruction-design issue としてかなり有効です。agent が docs を開かない場合でも最低限の gate を見る、というユーザー hypothesis に合っています。

Medium-High: plan.md must be executable の深さを明確にする必要がある

Confirmed from supplied context: draft は issue plan.md must be executable before execution handoff を scope に入れています。また field semantics / executable step schema は docs 側に置く方針です。

Issue:
executable を skill 内で詳述しすぎると schema copy になります。一方で、単に plan.md must be executable だけだと agent にとって operational blocker として弱いです。

Recommended requirement edit:

Markdown
The skill must state that execution handoff is blocked unless the issue `plan.md` is executable according to the issue-plan docs. The skill should point to `spec-dock/docs/phase_plan_issue.md` and `spec-dock/docs/authoring/issue-plan.md` for the executable-step schema, without copying that schema into the skill.

これにより、skill は blocker を明示し、詳細 schema は docs に残せます。

Medium: mirror update の open question は requirement review 前に閉じた方がよい

Confirmed from supplied context: open question は「root .agents/skills/... mirror を同じ issue で更新するか」。current recommended answer は provider source and dogfooding mirror together。

Issue:
AC-006 は「consistent or report records why not」となっていますが、open question のままだと scope ambiguity が残ります。

Recommended edit:

Markdown
This issue updates both the provider-side skill source and the dogfooding mirror. If they cannot be kept semantically identical, the issue report must record the exact divergence and reason.

AC-006 も以下のようにできます。

Markdown
AC-006: The provider-side skill source and dogfooding mirror are semantically identical for the rewritten instruction content, or `report.md` records the exact divergence and reason.
Medium: report recording が acceptance criteria として弱い可能性がある

Confirmed from supplied context: current skill already says to record each Spec Authoring Gate in issue report.md, including investigation, questions/answers, reviewer verdict, fixes, promotion decision, and handoff readiness. Draft summary includes report evidence mostly under canonical adoption.

Issue:
ユーザー insight は workflow visibility に関するものなので、gate recording も mandatory workflow の一部として requirement / AC に入れておくとよいです。これがないと implementation で report instruction が薄まる可能性があります。

Recommended AC addition:

Markdown
AC-007: `SKILL.md` explicitly instructs agents to record each Spec Authoring Gate in the issue `report.md`, including reviewer verdict, fixes, promotion decision, and execution handoff readiness, while leaving detailed report semantics to the docs.

長くなりすぎる場合は:

Markdown
AC-007: The mandatory workflow spine includes report recording for each authoring gate, without duplicating detailed report schema.
Medium: non-pass reviewer states are not pass は良いが、status vocabulary の扱いに注意

Confirmed from supplied context: draft wants missing / stale / failed / unavailable / denied / waived / provisional reviewer states to be not pass.

Issue:
この list は instruction として強い一方、実際の spec-reviewer schema に存在しない status label が混ざっている可能性があります。提示 context だけでは schema は確認不能です。

Recommended wording:

Markdown
Only an explicit fresh `review_status: pass` satisfies a promotion or handoff gate. Any missing reviewer result, stale result, failed result, unavailable reviewer, denied review, waived review, provisional result, or any other non-pass state does not satisfy the gate.

この形なら、status enum を勝手に拡張するのではなく、「explicit pass 以外は pass ではない」という rule にできます。

Low-Medium: canonical ownership は adoption evidence まで書くとより testable

Confirmed from supplied context: canonical requirement.md / design.md / plan.md / report.md は main-orchestrator-owned。delegated drafts are evidence only。

Issue:
「delegated drafts are not canonical」は良いですが、「どうなったら canonical に反映されたと言えるか」が少し弱いです。

Recommended edit:

Markdown
Delegated `system-architect` or `implementation-planner` drafts may be used only as scope-local evidence until the main orchestrator explicitly adopts their content into the canonical issue artifacts and records that adoption in `report.md`.

これで「draft が存在する」ことと「canonical artifact に統合された」ことを分離できます。

Low: 「docs を案内する」だけでなく「phase ごとの読むべき docs」を明示するとよい

Issue:
現在の skill は docs list を持っていますが、agent がどの局面でどの doc を読むべきかは薄いです。requirement が「skill は特定 artifact を作るときに読むべき docs を案内する」と言うなら、phase mapping を要求してもよいです。

Recommended requirement edit:

Markdown
The skill should keep detailed semantics in linked docs, but it must map each authoring activity to the docs an agent should open before writing or revising that artifact.

ただし、これは scope を広げすぎないように、short mapping に留めるべきです。

Example acceptable shape:

Markdown
For requirement/design promotion workflow, read `workflow_spec_authoring.md`.
For unresolved ambiguity, read `workflow_clarification.md`.
For issue plan authoring and executable steps, read `phase_plan_issue.md` and `authoring/issue-plan.md`.
3. Specific recommended edits to requirement.md
Add a concise “Instruction boundary” paragraph
Markdown
This issue changes the instruction surface of `spec-dock-issue-planning`; it does not change workflow policy, runtime enforcement, reviewer behavior, or validation logic. The skill must expose the mandatory operational gates that an agent must obey before opening detailed docs, while linked docs remain the source of truth for conceptual meaning, field semantics, schemas, and detailed authoring guidance.
Add a concrete “minimum spine” requirement
Markdown
The rewritten skill must include a short, front-loaded `Mandatory Issue Authoring Workflow` section that states the minimum phase spine:

1. Requirement authoring must reach a fresh `spec-reviewer` `review_status: pass` before design promotion.
2. Design authoring must start from the current passed requirement and reach a fresh `spec-reviewer` `review_status: pass` before plan promotion.
3. Plan authoring must start from the current passed design and reach a fresh `spec-reviewer` `review_status: pass` before execution handoff.
4. Execution handoff is blocked unless the issue `plan.md` is executable according to the issue-plan docs.
5. Missing, stale, failed, unavailable, denied, waived, provisional, or otherwise non-pass reviewer states do not satisfy a gate.
6. Unresolved requirement/design/plan gaps return to clarification or the relevant authoring phase, not execution assumptions.

This is short enough for skill-level instruction and avoids copying detailed schema.

Add a definition of fresh
Markdown
For this issue, `fresh` means the reviewer pass was run against the current artifact candidate after the latest substantive change to that artifact. A pass from before later edits, from another artifact, from an unadopted delegated draft, or from an earlier phase is not fresh for the current gate.
Tighten canonical ownership wording
Markdown
Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` remain main-orchestrator-owned. Delegated drafts are evidence only until the main orchestrator explicitly adopts their content into canonical artifacts and records the adoption and gate history in `report.md`.
Tighten docs-vs-skill split
Markdown
The skill must not copy long policy text, field tables, executable-step schema, or detailed artifact semantics. It should instead link to the relevant docs and state which docs to read for lifecycle workflow, spec authoring, clarification, issue plan phase guidance, and issue-plan field/executable-step semantics.
Replace or refine acceptance criteria

Suggested AC set:

Markdown
AC-001: Reading only `SKILL.md`, a reviewer can identify the mandatory sequence `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> execution handoff`.

AC-002: `SKILL.md` states that only an explicit fresh `review_status: pass` satisfies a promotion or handoff gate, and that missing, stale, failed, unavailable, denied, waived, provisional, or otherwise non-pass states do not satisfy the gate.

AC-003: `SKILL.md` states that unresolved requirement/design/plan gaps return to clarification or the relevant authoring phase instead of being absorbed as execution assumptions.

AC-004: `SKILL.md` states that canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` remain main-orchestrator-owned, and delegated drafts are evidence only until explicitly adopted with report evidence.

AC-005: `SKILL.md` keeps detailed field semantics, schemas, and long authoring guidance in linked docs rather than copying them into the skill.

AC-006: `SKILL.md` states that execution handoff is blocked unless `plan.md` is executable according to the issue-plan docs, while the detailed executable-step schema remains in docs.

AC-007: The provider-side skill source and dogfooding mirror are semantically identical for the rewritten instruction content, or `report.md` records the exact divergence and reason.

AC-008: `SKILL.md` preserves or improves references to the lifecycle, spec authoring, clarification, issue plan phase, and issue-plan authoring docs.

AC-008 is optional, but useful if doc routing is part of the user insight.

4. Recommended follow-up issues

These should remain follow-ups, not part of iss-00159.

Follow-up: runtime / CLI gate enforcement

A later issue can consider runtime gate checks, validation logic, or gate status --json. This should remain out of the first issue because the current problem is instruction visibility, not enforcement.

Follow-up: manual compliance harness or reviewer checklist

A later issue can test whether coding agents actually follow the rewritten skill. This is separate because iss-00159 should only improve the skill spine, not build evaluation infrastructure.

Follow-up: align hub / execution / epic skills

After the issue-planning skill is hardened, a separate issue can check whether related skills point to the same lifecycle assumptions. This should not be mixed into the first issue because it expands the blast radius.

Follow-up: normalize reviewer status vocabulary

If missing / stale / failed / unavailable / denied / waived / provisional are not already documented as status concepts, a later docs issue can normalize terminology. For iss-00159, the safe rule is simply: only explicit fresh review_status: pass passes.

Follow-up: reduce fragmentation in detailed docs

The current hypothesis says docs can remain the detailed source of truth. A later issue could improve doc discoverability or create a concise doc index, but that should not block the skill-spine issue.

5. Risks for later design.md and plan.md
Risk: design turns the skill into a copied mini-manual

The design should avoid copying workflow_issue.md, workflow_spec_authoring.md, workflow_clarification.md, phase_plan_issue.md, or authoring/issue-plan.md. The skill should contain only the operational gates and doc routing.

Good design target:

Markdown
Mandatory gates in skill.
Detailed semantics in docs.

Bad design target:

Markdown
Reproduce phase docs, field definitions, executable step schema, and reviewer policy inside SKILL.md.
Risk: design leaves the spine as another compact bullet list

The current skill already has gate reminders, but the problem is salience and readability. A rewrite that merely adds more bullets to the existing reference list may not solve the issue.

The design should prefer a named section such as:

Markdown
## Mandatory Issue Authoring Workflow

placed before the doc references.

Risk: plan adds runtime work despite non-scope

The plan should not add CLI changes, validation checks, runtime gates, command output, or automation. Verification should be content-level: inspect the skill text, compare provider source and mirror, and confirm the report records any divergence.

Risk: fresh pass semantics become policy drift

The design should define fresh only enough for authoring gates. It should not invent new reviewer lifecycle policy or override existing docs.

Risk: executable plan becomes schema duplication

The skill should state that execution handoff is blocked if plan.md is not executable, then point to the issue-plan docs for the schema. The design should not inline step field definitions.

Risk: canonical ownership wording blocks legitimate draft use

The skill should not say delegated drafts are useless. It should say they are evidence only until main orchestrator adoption. That preserves the intended collaboration model.

6. What not to do

Do not solve this by adding only more doc links. The user’s point is that agents may not open the docs; the mandatory workflow must be visible in the skill itself.

Do not copy long schemas, field semantics, or detailed authoring explanations into the skill. That would reverse the intended skill/docs split.

Do not introduce runtime enforcement, CLI gates, gate status --json, validation logic, or compliance harness work in this issue.

Do not treat unavailable, waived, provisional, stale, or missing reviewer results as acceptable substitutes for review_status: pass.

Do not let delegated system-architect or implementation-planner drafts replace canonical requirement.md, design.md, plan.md, or report.md without main-orchestrator adoption and report evidence.

Do not promote design or plan in this task package based on this critique. This output is third-party reasoning evidence only, not a formal spec-reviewer pass.

Do not embed issue-specific context such as iss-00159 or epic-00158 into the reusable skill text unless the actual implementation intentionally needs temporary dogfooding notes. The skill should remain generally applicable to issue planning.

根拠

提示 context では、現行 skill はすでに workflow docs への参照、canonical ownership、fresh reviewer pass、unresolved gaps、report recording を bullet で持っています。ただし、ユーザー補足では「必ず守ってほしい作業手順が docs 側に埋もれ、agent が docs を開かなかった場合に workflow を知らない状態になる」ことが本質とされています。

Requirement draft summary は、その本質に対して、skill に mandatory workflow spine を追加し、詳細 schema / semantics は docs に置く、という方向を取っています。したがって、中心仮説は正しく捕捉されています。

仮定

実際の requirement.md 本文ではなく、提示された summary を critique 対象としています。

spec-reviewer の厳密な status enum は提示されていないため、status vocabulary は未確認です。

SKILL.md は coding agent が最初に読む instruction surface として機能する前提で評価しています。

Codex 側で最終判断、formal review、実装統合、検証が行われる前提です。

不確実性

実際の repository docs の内容は確認していません。

fresh の定義が既存 docs にすでにあるかは不明です。

provider-side source と dogfooding mirror の同期手順は提示 context からは判断不能です。

denied / waived / provisional が実際の reviewer schema に存在する status かは未確認です。

未検証主張

「named mandatory workflow section を前方に置くと agent compliance が改善する」は instruction-design 上の推論であり、この repo で実測された事実ではありません。

fresh を “latest substantive change after reviewer run” と定義する案は、この issue の目的に合う最小定義としての提案であり、既存 policy との完全一致は未検証です。

mirror を同 issue で更新するのが最適という判断は、提示 context の “current recommended answer” に沿った advisory judgment であり、実際の repo maintenance workflow は未確認です。

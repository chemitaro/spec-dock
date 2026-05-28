---
種別: research
ID: "research-20260528t011700z"
タイトル: "spec-dock-requirement-grill skill design from ChatGPT follow-up"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["disc-20260528t010000z", "scratch-20260528t011400z"]
authority: "synthesized"
derived_from:
  - "discussions/20260528t010300z-scratch-chatgpt-skill-design-followup-prompt.md"
  - "discussions/20260528t011400z-scratch-chatgpt-skill-design-response.md"
reflected_to:
  - "requirement.md"
---

# research-20260528t011700z spec-dock-requirement-grill skill design from ChatGPT follow-up

## 調査目的
- `spec-dock-requirement-grill` を shipped skill として設計する場合の contract、責務境界、artifact contract、first implementation slice を具体化する。

## 調査方法
- 同じ ChatGPT thread に follow-up prompt を送り、`spec-dock-requirement-grill/SKILL.md` の具体ドラフトを作成させた。
- ChatGPT thread:
  - `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a1790e9-2be8-83a4-aa7c-3350ef063f6f`
- ChatGPT は追加 Web 確認や Matt Pocock 原文コピーなしで、前回の方針と spec-dock context に基づき設計した。

## 調査結果
- proposed provider path:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md`
- skill の中心責務:
  - active issue の曖昧な requirement/design/plan を、local source inspection と one-question-at-a-time clarification によって implementation-ready に近づける。
  - discussion artifacts を使って調査・質問・選択肢・ADR candidate を記録し、canonical docs への patch proposal を出す。
- input source priority:
  1. current task instruction
  2. active issue docs
  3. parent epic / initiative docs
  4. issue-local discussions
  5. `spec-dock/.agent` generated state
  6. relevant source files / tests / assets
  7. external sources only when allowed or required
- output artifacts:
  - source-grounding research artifact
  - requirement-grill interview artifact
  - requirement/design option discussion artifact
  - ADR triage artifact
  - requirement/design/plan patch proposal
- core guardrails:
  - local inspection before human questioning
  - exactly one human question at a time
  - no source-answerable human questions
  - unresolved ambiguity must not be written into requirement/design/plan as confirmed content
  - discussion artifacts are not canonical until adopted/reflected
  - ADR candidates are identified but not finalized inside this skill
- stop conditions:
  - synthesize when high-impact ambiguity is resolved
  - ask one question when top ambiguity cannot be resolved locally
  - hand off when initiative/epic planning, ADR facilitation, or implementation execution is the correct next workflow
- first implementation slice recommended by ChatGPT:
  - Add only `src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md`.
  - Avoid in slice 1: installed `.agents/` mirror, `.codex/agents` wrapper, discussion templates, CLI command, installer changes.
  - Rationale: keeps scope small, follows provider-side authority, reduces license/copy risk, and avoids agent/template sprawl before the core skill contract is reviewed.

## 推測 / 未検証事項
- 推測:
  - Slice 1 can be docs-only / inspect-only with validation via tree inspection and spec-dock sync/validate.
  - Existing consultant/deep-consultant/spec-manager can invoke the new shared skill before adding a dedicated agent.
- 未検証:
  - Exact local style of existing provider-side `SKILL.md` files.
  - Whether dogfooding installed assets under `.agents/skills/` must be updated in the same commit.
  - Whether `./spec-dock/scripts/spec-dock sync` and `validate` are sufficient validation for this asset-only addition.
  - Existing template layout convention for nested discussion templates.
  - Matt Pocock license/copy policy.

## 判断への含意
- `requirement.md` should frame this issue as adding a spec-dock-native clarification skill, not as directly importing Matt Pocock skills.
- `design.md` should keep Slice 1 narrow: provider-side shared skill asset only.
- Template and agent wrapper additions should be follow-up slices unless issue scope is intentionally expanded.
- Before implementation, local existing skill style must be inspected and the draft normalized to repository conventions.

## リスク/制約
- Skill overlap risk with initiative/epic planning, ADR facilitation, and issue execution.
- Discussion artifacts can become shadow source-of-truth unless adoption/reflection rules are explicit.
- If one-question-at-a-time rule is weak, the workflow can regress into broad questionnaire dumping.
- If local inspection rule is weak, the workflow can waste user attention on questions already answered by repo/docs.

## 反映先
- reflected_to:
  - 未反映。次の step で `requirement.md` / `design.md` / `plan.md` に反映する候補。

## 参考（References）
- `discussions/20260528t010300z-scratch-chatgpt-skill-design-followup-prompt.md`
- `discussions/20260528t011400z-scratch-chatgpt-skill-design-response.md`

---
種別: scratch
ID: "20260520t075311z-scratch"
タイトル: "Current plan workflow audit notes"
状態: "draft | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00102"]
関連: []
authority: "raw"
derived_from: []
reflected_to: []
---

# 20260520t075311z-scratch Current plan workflow audit notes

## 位置づけ
- 用途: 未整理の発話、観察、思考、会話ログ、作業中の下書きを低摩擦に置く。
- authority default: `raw`。raw capture は非 authoritative であり、この文書だけで決定済み、調査済み、要件確定として扱わない。
- 長期保存する価値が出たら、文脈をもとに `interview` / `research` / `disc` / `adr` を新規作成するか、`requirement.md` / `design.md` / `plan.md` を修正する。
- 既存 `note` artifact は grandfathered だが、新規 raw capture には `scratch` を使う。

## メモ (必須)
- Local audit scope:
  - provider docs/templates:
    - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - installed agent assets:
    - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
    - `src/spec_dock/assets/install_root/.codex/agents/*reviewer*.toml`
  - dogfooding mirrors:
    - `spec-dock/docs/...`
    - `spec-dock/templates/...`
    - `.codex/prompts/execute-issue.md`
    - `.agents/skills/spec-dock-issue-execution/SKILL.md`
- Immediate finding:
  - `1〜3 件程度` appears in provider and dogfooding issue plan template and phase playbook.
  - This is the only `1〜3` occurrence that is problematic for test density; other `1〜3 行` or reviewer JSON schema examples are unrelated.
- Important ownership memory:
  - `workflow_issue.md` should own issue execution/completion policy.
  - `phase_plan_issue.md` should own how to write plans, not commit/no-op or execution policy.
  - `docs/authoring/issue-plan.md` is the agent-facing plan authoring entrypoint.
  - `templates/issue/plan.md` should remain scaffold, not become a full policy manual.

## 整理メモ（任意）
- facts:
  - `templates/issue/plan.md` already says the central index is not an issue-wide test case list and should not pin private methods, algorithms, mocks, or assertion details.
  - The same template nevertheless says normal issues write `1〜3 件程度` per step/behavior slice, which conflicts with risk-based test obligations.
  - `phase_plan_issue.md` already has stronger concepts than the template: evidence levels, plan amendment, test sensitivity evidence, step-local concrete cases, and final QA gate.
  - `workflow_issue.md` already has a strict evidence sequence, but the current wording says `agent-native TDD cycle` is embedded in step/block/behavior slice without defining how step and slice relate.
  - `authoring/issue-plan.md` emphasizes concrete cases and the five fields, but it does not yet distinguish:
    - test obligation matrix as planning inventory;
    - step-local concrete red tests as pre-implementation oracle;
    - discovered tests as implementation-time findings.
  - `execute-issue.md` hard-stops when `具体テストケース一覧` is missing, but does not yet say the list is floor/not cap or that step-local red tests must be fixed before implementation.
  - `dev-coder.toml` says "minimal necessary tests"; this is fine only if plan obligations are strong. If the plan is weak, it reinforces under-testing.
  - `qa-reviewer.toml` is focused on test adequacy after diff review. There is no explicit Plan QA Gate before implementation.
- questions:
  - Should `具体テストケース一覧` be renamed, or should it remain Japanese while adding `Test Obligation Matrix` and `Concrete Red Tests` as English/Japanese paired terms?
  - Should Plan QA Gate be mandatory for Medium/High risk, or optional guidance for this issue?
  - Should docs lint / validate strictness be in this issue, or deferred?
- decisions:
  - Proposed: remove the `1〜3 件程度` heuristic from plan template and phase playbook.
  - Proposed: replace count guidance with risk-based obligation coverage:
    - AC coverage;
    - negative/error;
    - regression/characterization;
    - invariant/property;
    - integration/manual where relevant.
  - Proposed: define `1 implementation step = normally 1 behavior slice / 1 Agentic TDD cycle / 1 review scope / 1 commit`.
  - Proposed: permit bundled slices only when same implementation surface, validation path, review context, and rollback boundary; require per-slice red/green evidence.
- actions:
  - Ask consultants to audit:
    - high-level direction;
    - detailed doc/template redundancy;
    - Agentic TDD testing rules;
    - document architecture ownership.
  - Produce final discussion report under iss-00102 with:
    - current problem analysis;
    - desired state;
    - delete/simplify/add matrix;
    - proposed implementation steps.
- links:
  - `spec-dock/active/issue/discussions/20260520t074027z-disc-agentic-tdd-cycle-and-plan-step-contract-analysis.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
- discard condition:
  - This scratch can be archived after the final analysis report is created and reflected into requirement/design/plan.

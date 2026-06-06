---
種別: 実装計画書（Issue）
ID: "iss-00163"
タイトル: "Revise Spec Dock Clarification As Skill Owned Grill Workflow"
関連GitHub: ["#163"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00163 Revise Spec Dock Clarification As Skill Owned Grill Workflow — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005
- EC:
  - EC-001, EC-002, EC-003
- 制約:
  - Runtime gate / automated harness は作らない。
  - Hub route table / broader leaf routing は変更しない。
  - Global template consistency は `iss-00166` に残す。
  - Provider source を正本、dogfooding mirror を verification target とする。

## ステップ一覧

- S01:
  - 観測可能な振る舞い: `spec-dock-clarification` skill だけで source-grounded grill loop の次アクションを実行できる。
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
    - `.agents/skills/spec-dock-clarification/SKILL.md`
  - 閉じる要件: AC-001, AC-005, EC-002, EC-003
  - レビューゲート: `spec-reviewer`
- S02:
  - 観測可能な振る舞い: `workflow_clarification.md` が skill-owned workflow を隠さない bridge/reference doc として読める。
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
    - `spec-dock/docs/workflow_clarification.md`
  - 閉じる要件: AC-002, AC-005, EC-001
  - レビューゲート: `spec-reviewer`
- S03:
  - 観測可能な振る舞い: `interview` / `research` / `disc` templates が clarification-specific scaffold slots を持つ。
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
    - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
    - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
    - `spec-dock/templates/discussions/interview.md`
    - `spec-dock/templates/discussions/research.md`
    - `spec-dock/templates/discussions/disc.md`
  - 閉じる要件: AC-003, AC-004, AC-005
  - レビューゲート: `spec-reviewer`
- S90:
  - 観測可能な振る舞い: sync / validate / docs impact が unresolved で残っていない。
  - 閉じる要件: AC-005 / docs impact
  - レビューゲート: `spec-reviewer`
- S99:
  - 観測可能な振る舞い: issue-wide QA/code/spec final gates が pass し、issue finish 可能な report になっている。
  - 閉じる要件: all
  - レビューゲート: `qa-reviewer`, `code-reviewer`, `spec-reviewer`

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S03
- AC-005 -> S01, S02, S03, S90, S99
- EC-001 -> S02
- EC-002 -> S01
- EC-003 -> S01

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子 | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | skill spine loop | acceptance | AC-001 | skill exposes read sources -> provisional understanding -> one pressure-test question -> artifact capture -> iterate/handoff | skill text | generic Q&A drift | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-002 | S01 | user question boundary | edge | EC-003 | if user-intent clarification is blocking, stop and ask user directly; no deep-consultant/specialist proxy | skill text | proxy user interview | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-003 | S01 | analysis-only / draft-only / canonical modes | edge | EC-002 | skill distinguishes mode outputs without forcing canonical docs | skill text | canonical overreach | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-004 | S01 | skill provider/mirror parity | regression | AC-005 | provider and mirror skill are byte-equivalent | `cmp` and parity unittest | stale mirror | yes | covered-existing | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-005 | S02 | workflow doc bridge | acceptance | AC-002, EC-001 | workflow doc is retained as bridge/reference and does not claim mandatory runbook authority | docs text | hidden workflow authority | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-006 | S02 | docs provider/mirror parity | regression | AC-005 | provider and mirror workflow doc are byte-equivalent | `cmp` | stale mirror | yes | covered-existing | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-007 | S03 | interview scaffold | acceptance | AC-003 | interview template supports unanswered before asking, answer capture, pressure-test question, adoption reflection | template text | missing interview lifecycle | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-008 | S03 | research/disc support scaffold | acceptance | AC-004 | research has facts/uncertainty/question candidates; disc has synthesis/ADR triage/adoption target | template text | weak clarification support | yes | inspect-only | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-009 | S03 | template provider/mirror parity | regression | AC-005 | provider and mirror discussion templates are byte-equivalent | `cmp` | stale mirror | yes | covered-existing | Step Contract Closure / Test Contract Closure / Closure Coverage |
| cl-010 | S90 | docs impact resolved | final | AC-005 | `sync`, `validate`, `git diff --check` pass | commands/report | stale projections | yes | manual-required | Docs Impact Resolution / Reviewer Gate Status |
| cl-011 | S99 | final gates | final | all | QA/code/spec reviewers pass and final report is committed | reviewer outputs | incomplete issue | yes | manual-required | Final QA Gate / Final Code Review Gate / Final Spec Review Gate / Final Commit |

## 実装ステップ S01 — Skill-owned clarification grill spine

- 振る舞いの目標:
  - Agent が `spec-dock-clarification/SKILL.md` だけで、source-grounded read、provisional understanding、gap classification、one pressure-test question、artifact capture、answer adoption / handoff を実行できる。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - `.agents/skills/spec-dock-clarification/SKILL.md`
- 計画済み契約:
  - allowed changes:
    - first-read workflow spine、mode outputs、handoff output、direct-user-only blocker wording。
  - forbidden changes:
    - docs field semantics の大量コピー。
    - hub route table / other skills / runtime / templates / docs。
  - Red / 代替証跡:
    - pre-change text says `workflow_clarification.md` is source of truth and skill is concise.
  - Green 検証:
    - `rg -n 'source-grounded grill loop' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'provisional understanding' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'gap classification' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'pressure-test question' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'artifact capture' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'answer adoption' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'iterate|handoff' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'ask the user directly' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'analysis-only' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'draft-only' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - `rg -n 'canonical authoring' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
    - negative inspection: no stale wording that `workflow_clarification.md` is the source of truth for the workflow.
    - `rg -n 'workflow_clarification[.]md.*source of truth|Keep this skill concise' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md` must return no matches.
    - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`
  - Refactor / cleanup guardrail:
    - Keep the diff limited to the two clarification skill files and report evidence.
    - Do not modify route table, `workflow_clarification.md`, templates, runtime, or tests in S01.
  - report evidence destination:
    - TDD / Red-Green-Refactor Evidence
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage / Closure Delta
    - Reviewer Gate Status
    - Step Commit Gate
  - close 条件:
    - cl-001..cl-004 pass and fresh `spec-reviewer` pass.
  - commit gate:
    - committed.
  - delegation contract:
    - delegated role: N/A / parent-local docs edit is permitted because the write set is exactly two small mirror files and the step is blocked on fresh `spec-reviewer`.
    - input docs: `requirement.md`, `design.md`, `plan.md`, `workflow_clarification.md`, S01 inventory discussion.
    - allowed paths: the two S01 target files only.
    - forbidden changes: all paths outside the two S01 target files before reviewer pass.
    - acceptance criteria: cl-001, cl-002, cl-003, cl-004.
    - required tests or docs-only verification: all S01 Green verification commands, S01 negative inspection, `cmp`, targeted parity unittest, and diff inspection proving no outside-path changes.
    - reviewer focus: skill first-read workflow completeness, direct-user-only blocker, analysis/draft/canonical mode distinction, provider/mirror parity, no docs/hub/template scope absorption.
    - stop conditions: wording requires hub route changes; user-intent clarification is actually blocking; provider/mirror parity cannot be preserved.
    - required output: changed files, command results, stale wording negative inspection, unresolved risks.
  - concrete test cases:
    - `tc-s01-001` inspect-only: skill exposes source-grounded grill loop.
      - 前提: S01 target skill files are updated.
      - 操作: run the `source-grounded grill loop`, `provisional understanding`, `gap classification`, `pressure-test question`, `artifact capture`, `answer adoption`, and `iterate|handoff` `rg` commands.
      - 期待結果: each command finds matches in both provider and mirror skill files.
      - 失敗検出: missing loop term means an agent can still read the skill without learning the required interaction loop.
      - 検証方法: the seven loop positive `rg -n` commands listed in S01 Green verification.
      - related closure id: cl-001.
    - `tc-s01-002` inspect-only: direct-user-only blocker and modes are present.
      - 前提: S01 target skill files are updated.
      - 操作: run the `ask the user directly`, `analysis-only`, `draft-only`, and `canonical authoring` `rg` commands, then run the stale wording negative command.
      - 期待結果: direct-user and mode terms are present; stale source-of-truth wording has no matches.
      - 失敗検出: proxy interview wording or mode omission allows clarification to overreach or use non-user proxy.
      - 検証方法: the four positive `rg -n` commands plus the negative `rg -n 'workflow_clarification[.]md.*source of truth|Keep this skill concise' ...`.
      - related closure id: cl-002, cl-003.
    - `tc-s01-003` covered-existing: skill provider/mirror parity.
      - 前提: S01 target skill files are updated.
      - 操作: run `cmp` and targeted parity unittest.
      - 期待結果: `cmp` exits 0 and unittest passes.
      - 失敗検出: stale dogfooding mirror or install-root mismatch.
      - 検証方法: `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md`; `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`.
      - related closure id: cl-004.

## 実装ステップ S02 — Workflow clarification bridge/reference doc

- 振る舞いの目標:
  - `workflow_clarification.md` は skill-owned workflow を隠さず、artifact selection / formal question trigger / adoption evidence semantics の reference として機能する。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `spec-dock/docs/workflow_clarification.md`
- 計画済み契約:
  - allowed changes:
    - bridge/reference positioning。
    - Skill-owned workflow への参照。
    - artifact lifecycle / adoption detail の整理。
  - forbidden changes:
    - doc deletion。
    - hub routing changes。
    - issue planning/execution policy rewrite。
  - Red / 代替証跡:
    - pre-change doc presents itself as first-class workflow and contains mandatory runbook steps.
  - Green 検証:
    - `rg -n 'bridge/reference' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`
    - `rg -n 'skill-owned' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`
    - `rg -n 'artifact semantics' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`
    - `rg -n 'formal question trigger' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`
    - `rg -n 'Evidence Adoption Ledger' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`
    - negative inspection: no claim that workflow doc is the mandatory runbook authority over the skill.
    - `rg -n 'source of truth|first-class entrypoint|mandatory runbook authority' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md` must not find wording that makes the doc authoritative over the skill; any remaining matches must be bridge/reference context and recorded in report.
    - `cmp -s src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
  - Refactor / cleanup guardrail:
    - Keep link compatibility; do not delete or rename `workflow_clarification.md`.
    - Do not modify hub skill, issue/authoring workflow docs, runtime, or templates in S02.
  - report evidence destination:
    - TDD / Red-Green-Refactor Evidence
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage / Closure Delta
    - Reviewer Gate Status
    - Step Commit Gate
  - close 条件:
    - cl-005..cl-006 pass and fresh `spec-reviewer` pass.
  - commit gate:
    - committed.
  - delegation contract:
    - delegated role: N/A / parent-local docs edit is permitted because the write set is exactly two mirror docs and the step is blocked on fresh `spec-reviewer`.
    - input docs: passed S01 skill, `requirement.md`, `design.md`, `plan.md`, current workflow doc.
    - allowed paths: the two S02 target files only.
    - forbidden changes: doc deletion, route table changes, issue planning/execution policy rewrites, templates.
    - acceptance criteria: cl-005, cl-006.
    - required tests or docs-only verification: all S02 Green verification commands, contextual stale-authority inspection, `cmp`, and diff inspection proving link surface retained.
    - reviewer focus: bridge/reference positioning, no mandatory runbook authority over skill, link compatibility, provider/mirror parity, no hub/policy/template scope absorption.
    - stop conditions: bridge wording cannot preserve existing link surface; user-intent clarification is actually blocking; provider/mirror parity cannot be preserved.
    - required output: changed files, command results, link-compatibility note, unresolved risks.
  - concrete test cases:
    - `tc-s02-001` inspect-only: workflow doc is bridge/reference and points to skill-owned workflow.
      - 前提: S02 workflow docs are updated.
      - 操作: run `bridge/reference`, `skill-owned`, `artifact semantics`, `formal question trigger`, and `Evidence Adoption Ledger` `rg` commands.
      - 期待結果: each command finds matches in both provider and mirror workflow docs.
      - 失敗検出: missing bridge/detail wording makes the doc read like hidden workflow authority.
      - 検証方法: the five positive `rg -n` commands listed in S02 Green verification.
      - related closure id: cl-005.
    - `tc-s02-002` inspect-only: workflow doc does not claim authority over skill.
      - 前提: S02 workflow docs are updated.
      - 操作: run the `source of truth|first-class entrypoint|mandatory runbook authority` inspection command and inspect any matches.
      - 期待結果: no match makes the doc authoritative over the skill; any remaining match is explicitly bridge/reference context in report.
      - 失敗検出: doc continues to hide mandatory runbook steps away from the skill.
      - 検証方法: S02 negative inspection command and report note for contextual matches.
      - related closure id: cl-005.
    - `tc-s02-003` covered-existing: docs provider/mirror parity.
      - 前提: S02 workflow docs are updated.
      - 操作: run `cmp`.
      - 期待結果: `cmp` exits 0.
      - 失敗検出: stale dogfooding doc or install-root mismatch.
      - 検証方法: `cmp -s src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md`.
      - related closure id: cl-006.

## 実装ステップ S03 — Clarification-specific discussion template slots

- 振る舞いの目標:
  - `interview` / `research` / `disc` templates が clarification workflow の evidence scaffolds として最低限の slots を持つ。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
  - `spec-dock/templates/discussions/interview.md`
  - `spec-dock/templates/discussions/research.md`
  - `spec-dock/templates/discussions/disc.md`
- 計画済み契約:
  - allowed changes:
    - interview: pressure-test question、blocking/user-direct condition、answer capture、adoption reflection。
    - research: facts / uncertainty / question candidates。
    - disc: synthesis / adoption target / ADR triage。
  - forbidden changes:
    - all templates global rewrite。
    - phase/issue/epic/initiative templates。
    - template compliance authority wording。
  - Red / 代替証跡:
    - pre-change templates lack explicit pressure-test question / question candidates / adoption target emphasis.
  - Green 検証:
    - `rg -n 'pressure-test question' src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md`
    - `rg -n 'unanswered' src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md`
    - `rg -n 'answer capture|ユーザー回答' src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md`
    - `rg -n 'adoption' src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md`
    - `rg -n 'Evidence Adoption Ledger' src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md`
    - `rg -n 'facts|観測できた事実' src/spec_dock/assets/spec_dock/templates/discussions/research.md spec-dock/templates/discussions/research.md`
    - `rg -n 'question candidates' src/spec_dock/assets/spec_dock/templates/discussions/research.md spec-dock/templates/discussions/research.md`
    - `rg -n 'unverified' src/spec_dock/assets/spec_dock/templates/discussions/research.md spec-dock/templates/discussions/research.md`
    - `rg -n 'synthesis' src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/disc.md`
    - `rg -n 'ADR candidate' src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/disc.md`
    - `rg -n 'adoption target' src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/disc.md`
    - `rg -n 'Evidence Adoption Ledger' src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/disc.md`
    - negative inspection: templates do not claim compliance authority.
    - `rg -n 'compliance authority|source of truth|must pass validation' src/spec_dock/assets/spec_dock/templates/discussions/interview.md src/spec_dock/assets/spec_dock/templates/discussions/research.md src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/interview.md spec-dock/templates/discussions/research.md spec-dock/templates/discussions/disc.md` must return no matches.
    - `cmp -s src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md`
    - `cmp -s src/spec_dock/assets/spec_dock/templates/discussions/research.md spec-dock/templates/discussions/research.md`
    - `cmp -s src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/disc.md`
  - Refactor / cleanup guardrail:
    - Keep changes limited to clarification-specific slots in `interview`, `research`, and `disc`.
    - Do not modify phase/issue/epic/initiative templates or global template README in S03.
  - report evidence destination:
    - TDD / Red-Green-Refactor Evidence
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage / Closure Delta
    - Reviewer Gate Status
    - Step Commit Gate
  - close 条件:
    - cl-007..cl-009 pass and fresh `spec-reviewer` pass.
  - commit gate:
    - committed.
  - delegation contract:
    - delegated role: N/A / parent-local template edit is permitted because the write set is six mirror template files and the step is blocked on fresh `spec-reviewer`.
    - input docs: passed S01/S02 artifacts, `requirement.md`, `design.md`, `plan.md`, current templates.
    - allowed paths: the six S03 target files only.
    - forbidden changes: global template normalization, non-discussion templates, template README, runtime, skills, workflow docs.
    - acceptance criteria: cl-007, cl-008, cl-009.
    - required tests or docs-only verification: all S03 Green verification commands, template authority negative inspection, three `cmp` commands, and diff inspection proving no non-discussion-template changes.
    - reviewer focus: clarification-specific scaffold slots, no compliance-authority wording, no global template consistency absorption, provider/mirror parity.
    - stop conditions: clarification-specific slots require global style/wording decisions; user-intent clarification is actually blocking; provider/mirror parity cannot be preserved.
    - required output: changed files, command results, template authority negative inspection, unresolved risks.
  - concrete test cases:
    - `tc-s03-001` inspect-only: interview template supports unanswered pressure-test question and adoption reflection.
      - 前提: S03 discussion templates are updated.
      - 操作: run `pressure-test question`, `unanswered`, `answer capture|ユーザー回答`, `adoption`, and `Evidence Adoption Ledger` commands against interview templates.
      - 期待結果: all terms are present in provider and mirror interview templates.
      - 失敗検出: important human decisions can be asked without pre-question artifact or adoption reflection.
      - 検証方法: the five interview-specific positive `rg -n` commands.
      - related closure id: cl-007.
    - `tc-s03-002` inspect-only: research/disc templates support question candidates, synthesis, ADR triage, adoption target.
      - 前提: S03 discussion templates are updated.
      - 操作: run research `facts`, `question candidates`, and `unverified` commands and disc `synthesis`, `ADR candidate`, `adoption target`, and `Evidence Adoption Ledger` commands.
      - 期待結果: each command finds matches in the intended provider and mirror template pair.
      - 失敗検出: research/disc cannot support clarification synthesis and adoption handoff.
      - 検証方法: the seven research/disc positive `rg -n` commands.
      - related closure id: cl-008.
    - `tc-s03-003` covered-existing: template provider/mirror parity.
      - 前提: S03 discussion templates are updated.
      - 操作: run three `cmp` commands.
      - 期待結果: all `cmp` commands exit 0.
      - 失敗検出: stale dogfooding templates or install-root mismatch.
      - 検証方法: the three explicit `cmp -s` commands listed in S03 Green verification.
      - related closure id: cl-009.

## ドキュメント影響の解消ステップ S90

- 対象:
  - skill / workflow doc / discussion templates / generated projections。
- 対応:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - report S90 evidence and no-change rationale for runtime / hub route table / global templates.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: cl-010 pass.
- execution contract:
  - delegated role: N/A / parent-local verification step.
  - allowed paths: `spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md`, and `report.md` evidence updates only if `sync` rewrites projections.
  - forbidden changes: provider/runtime/docs/templates changes beyond S01-S03 without returning to the relevant step.
  - acceptance criteria: cl-010.
  - required tests or docs-only verification: `sync`, `validate`, `git diff --check`, and `git status --short` inspection.
  - reviewer focus: generated projections, docs impact completeness, no unresolved runtime/hub/global template impact.
  - report evidence destination: Docs Impact Resolution, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
  - stop conditions: `sync` rewrites unexpected provider assets; `validate` fails; diff-check fails; user-intent clarification becomes blocking.
  - concrete test case:
    - `tc-s90-001` manual-required: docs impact resolved.
      - 前提: S01-S03 are committed.
      - 操作: run `./spec-dock/scripts/spec-dock sync`, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, and inspect `git status --short`.
      - 期待結果: commands pass; any generated projection diff is expected and recorded; no unresolved docs/templates/runtime impact remains.
      - 失敗検出: stale projections or hidden docs/runtime impact.
      - 検証方法: the three commands and status inspection.
      - related closure id: cl-010.

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - issue start / planning commit から HEAD。
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - provider/mirror parity command evidence already recorded.
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage と docs/skill/template-only verification adequacy。
- final code review:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、provider/mirror consistency、scope absorption、stale wording。
- final spec review:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
- final commit gate:
  - final report ledger committed.
- execution contract:
  - delegated role: N/A for local final report updates; reviewers are `qa-reviewer`, `code-reviewer`, and `spec-reviewer`.
  - allowed paths: `report.md` final gate evidence only after S01-S03/S90 commits.
  - forbidden changes: implementation/docs/template content changes after final reviewers unless returning to the relevant step and re-running gates.
  - acceptance criteria: cl-011.
  - required tests or docs-only verification: final `validate`, `git diff --check`, issue-wide diff inspection, QA/code/spec reviewer pass evidence.
  - reviewer focus: obligation coverage, provider/mirror parity, no scope absorption, report consistency, issue finish readiness.
  - report evidence destination: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit.
  - stop conditions: any final reviewer fails; report ledger contradiction; user-intent clarification becomes blocking.
  - concrete test case:
    - `tc-s99-001` manual-required: final gates and report commit.
      - 前提: S01-S03 and S90 are committed.
      - 操作: run final validation commands, obtain QA/code/spec reviewer passes, update and commit final report ledger.
      - 期待結果: all reviewer gates pass and final report commit leaves worktree clean.
      - 失敗検出: incomplete closure evidence or final issue finish blocker.
      - 検証方法: reviewer outputs, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, `git status --short`.
      - related closure id: cl-011.

## 未確定事項

- Blocking question:
  - なし。
- Amendment trigger:
  - Skill rewrite requires hub route table changes。
  - Template updates require global template wording/style normalization beyond clarification-specific slots。
  - Workflow doc cannot be made bridge/reference without deleting existing link surface。

## 最終完了条件

- AC-001..AC-005 / EC-001..EC-003 達成。
- cl-001..cl-011 が pass。
- S01/S02/S03/S90/S99 reviewer gates pass。
- All changes committed and `issue finish` succeeds。

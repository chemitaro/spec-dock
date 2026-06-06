---
種別: 実装計画書（Issue）
ID: "iss-00166"
タイトル: "Align Templates As Scaffolds And Examples"
関連GitHub: ["#166"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00166 Align Templates As Scaffolds And Examples — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001 template boundary.
  - AC-002 discussion clarification support.
  - AC-003 report evidence slots.
  - AC-004 issue plan scaffold.
  - AC-005 provider / mirror validation.
  - AC-006 scope containment.
- EC:
  - EC-001 over-explaining templates.
  - EC-002 missing evidence slots.
  - EC-003 stale source-of-truth wording.

## 依存関係から導く実装順序

- S01 aligns template README and canonical report/plan/design surfaces first because they define generated artifact expectations and evidence slots.
- S02 aligns discussion templates next because they feed interview/research/synthesis evidence into canonical report ledgers.
- S90 runs provider/mirror validation and generated projection checks after template wording commits.
- S99 runs final QA/code/spec review and final report ledger commit.

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | template boundary wording | acceptance | AC-001, EC-003 | Templates read as scaffold / evidence slot / example surfaces and do not claim workflow/compliance authority | provider template diff | template authority drift | yes | inspect-only | report Step/Test Closure |
| cl-002 | S01 | report evidence slots | acceptance | AC-003, EC-002 | Initiative / Epic / Issue report templates preserve EAL, delegated evidence, spec authoring gate, reviewer state, blocking/next action, and closure/follow-up slots | report template inspection | missing evidence ledgers | yes | inspect-only | report Step/Test Closure |
| cl-003 | S01 | issue plan scaffold | acceptance | AC-004, EC-001 | Issue plan template remains executable scaffold and routes detailed policy / field semantics to docs/skills without owning policy | issue plan template inspection | hidden policy authority in plan template | yes | inspect-only | report Step/Test Closure |
| cl-004 | S02 | discussion templates | acceptance | AC-002, EC-002 | `interview`, `research`, and `disc` support source-grounded question, facts/inference separation, synthesis, adoption target, and reflection without becoming canonical authority | discussion template inspection | clarification evidence split / raw dump | yes | inspect-only | report Step/Test Closure |
| cl-005 | S01/S02 | scope containment | regression | AC-006 | No skill, workflow-doc, runtime, test, or GitHub metadata changes are included | `git diff --name-only` | scope absorption | yes | inspect-only | report Closure Coverage |
| cl-006 | S90 | provider/mirror validation | regression | AC-005 | Provider and dogfooding mirror templates match for changed paths; `sync`, `validate`, and diff-check pass or no-op rationale is recorded | commands and parity checks | provider/mirror drift | yes | manual-required | Docs Impact Resolution |
| cl-007 | S99 | final gate | final | all AC/EC | QA/code/spec reviewers pass and final report ledger is committed | reviewers / commands / commit | incomplete finish evidence | yes | manual-required | Final Quality Gate |

## 実装ステップ S01 — Canonical Template Boundary And Evidence Slots

- 振る舞いの目標:
  - Template README and canonical report / plan / design templates consistently read as scaffold / evidence slot / example surfaces.
- design 参照:
  - Directory / File Change Plan; Template surface ownership and verification flow.
- 依存:
  - Requirement and design reviewer pass.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/report.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/design.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/report.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - dogfooding mirror equivalents under `spec-dock/templates/`
- planned contract:
  - allowed paths:
    - Provider and mirror templates listed above.
    - `report.md` evidence.
  - forbidden changes:
    - `.agents/skills/`, `src/spec_dock/assets/install_root/.agents/skills/`
    - `src/spec_dock/assets/spec_dock/docs/`, `spec-dock/docs/`
    - runtime scripts / Python code / tests / GitHub metadata.
  - Red / alternative evidence:
    - Inspect old templates for stale `正本`, `source of truth`, or policy-authority wording.
    - Confirm report slots are present before/after.
  - Green verification:
    - Positive `rg` for scaffold / evidence slot / detail-reference wording.
    - Negative `rg` for stale template authority wording in changed templates.
    - Provider/mirror `diff -q` for changed pairs.
    - `git diff --name-only` scope guard.
    - `git diff --check`.
  - closure ids:
    - cl-001, cl-002, cl-003, cl-005.
  - amendment trigger:
    - Need to edit skills/docs/runtime/tests.
    - Need to remove report evidence slots instead of boundary wording.

### S01 delegation contract

- delegated role:
  - `doc-writer`
- required reason:
  - shipped templates / persistent workflow text changes are docs/template worker work under `workflow_issue.md`.
- step scope:
  - Align canonical template README, report templates, Epic design template, and Issue plan template as scaffold / evidence slot / example surfaces.
  - Close cl-001, cl-002, cl-003, and cl-005 only; do not absorb S02 discussion-template work.
- source of truth:
  - approved requirement / design / plan.
  - Epic ADRs and `iss-00162` inventory.
  - provider templates under `src/spec_dock/assets/spec_dock/templates/`.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `docs/authoring/issue-plan.md`, and S01 target templates.
- allowed changes:
  - S01 target provider templates and dogfooding mirror templates.
- forbidden changes:
  - skills, docs, runtime, tests, GitHub state, issue metadata.
- acceptance criteria:
  - cl-001: changed canonical templates use scaffold / evidence slot / example wording and avoid workflow authority claims.
  - cl-002: Initiative / Epic / Issue report templates retain observable evidence ledgers needed by `workflow_issue.md`.
  - cl-003: Issue plan template stays an executable scaffold and routes policy / field semantics to skills and docs.
  - cl-005: changed paths remain limited to S01 provider/mirror templates plus issue report evidence.
- required verification:
  - changed file list, provider/mirror parity, targeted positive / negative `rg`, `git diff --check`.
- required tests or docs-only verification:
  - docs-only / template-only verification through targeted `rg`, provider/mirror parity checks, scope guard, and whitespace diff check.
- reviewer focus:
  - `spec-reviewer` checks docs/spec alignment, stale authority wording removal, report evidence slot preservation, and S01 scope containment.
- required output:
  - changed files, verification result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Need for skill/doc/runtime/test change.
  - Need for user intent clarification.
  - Verification cannot run.

### S01 concrete checks

- `tc-s01-001` inspect-only: scaffold / evidence boundary wording.
  - 前提: S01 target provider/mirror templates are checked out before implementation, and requirement/design/plan have fresh authoring approval.
  - 操作: Inspect the S01 template diff and run targeted `rg` over changed S01 templates for scaffold / evidence slot / example-reference wording and stale authority wording.
  - 期待結果: Changed templates identify templates as scaffold / evidence slot / example surfaces and do not claim workflow/compliance authority.
  - 失敗検出: A changed template still says it is the source of truth for workflow/compliance policy, or no positive scaffold/evidence/example wording is present.
  - 検証方法: targeted `rg` plus human diff inspection of changed S01 templates.
  - 記録先: `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
  - related closure id: cl-001.
- `tc-s01-002` inspect-only: report evidence slots retained.
  - 前提: S01 report templates are the provider and mirror Initiative / Epic / Issue report template pairs.
  - 操作: Run targeted `rg` over S01 report templates for EAL, Delegated Draft Evidence, Spec Authoring Gate, reviewer state, blocking / next action, closure, and follow-up slots.
  - 期待結果: Initiative / Epic / Issue report templates retain the evidence slots needed for observed evidence ledger usage.
  - 失敗検出: Any required ledger slot is absent from a changed report template, or the template removes evidence destinations required by workflow docs.
  - 検証方法: targeted `rg` over report templates and diff inspection for removed ledger headings.
  - 記録先: `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
  - related closure id: cl-002.
- `tc-s01-003` inspect-only: issue plan policy routing.
  - 前提: The Issue plan template is changed only as a copyable scaffold, while `docs/authoring/issue-plan.md` and `workflow_issue.md` remain the policy/detail references.
  - 操作: Inspect `templates/issue/plan.md` provider/mirror diff and run targeted `rg` for references to skill/docs routing and for stale template-owned policy claims.
  - 期待結果: Issue plan template routes lifecycle / execution / reviewer / field semantics detail to skills/docs and does not claim template-owned policy.
  - 失敗検出: The template embeds new detailed policy as template authority, omits routing to skills/docs, or keeps stale source-of-truth wording.
  - 検証方法: targeted `rg` and human diff inspection of the Issue plan template pair.
  - 記録先: `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
  - related closure id: cl-003.
- `tc-s01-004` inspect-only: scope boundary.
  - 前提: S01 is executed before S02, S90, and S99, and no unrelated local changes are intentionally staged.
  - 操作: Run `git diff --name-only` for the S01 worktree diff before S01 review/commit.
  - 期待結果: Only S01 provider/mirror templates and issue report evidence are changed.
  - 失敗検出: Any skill, workflow doc, runtime, test, GitHub metadata, or S02-only discussion template appears in the S01 diff.
  - 検証方法: `git diff --name-only` plus path comparison against S01 allowed paths.
  - 記録先: `report.md` Implementation Delegation Gate, Step Contract Closure, Closure Coverage, Step Commit Gate.
  - related closure id: cl-005.

### S01 report evidence destination

- pre-implementation and delegation decision:
  - `report.md` Implementation Delegation Gate.
- delegated worker summary / changed files / verification result:
  - `report.md` Delegated Draft Evidence if a worker produces a draft summary, and Implementation Delegation Gate for handoff result.
- observed verification and closure:
  - `report.md` Step Contract Closure, Test Contract Closure, and Closure Coverage.
- reviewer verdict:
  - `report.md` Reviewer Gate Status.
- commit or approved-no-op evidence:
  - `report.md` Step Commit Gate.
- material decision or plan deviation:
  - `report.md` Spec Interpretation / Decision Ledger before any canonical adoption.

### S01 step gate

- reviewer:
  - `spec-reviewer`
- pass condition:
  - `review_status: pass`
- commit boundary:
  - S01 template changes + report evidence.

## 実装ステップ S02 — Discussion Template Evidence Flow

- 振る舞いの目標:
  - Discussion templates support source-grounded clarification / research / synthesis without claiming canonical authority.
- design 参照:
  - Discussion templates under Directory / File Change Plan.
- 依存:
  - S01 commit or approved no-op.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
  - dogfooding mirror equivalents under `spec-dock/templates/discussions/`
- planned contract:
  - allowed paths:
    - S02 target provider/mirror discussion templates.
    - `report.md` evidence.
  - forbidden changes:
    - skills, docs, runtime, tests, GitHub state, issue metadata.
  - Red / alternative evidence:
    - Inspect existing discussion templates for missing source-grounding / adoption-reflection slots and stale authority claims.
  - Green verification:
    - Positive `rg` for one-question, answer capture, facts/inference/unverified, question candidates, synthesis, adoption target, ADR triage.
    - Negative `rg` for discussion templates claiming accepted/canonical authority outside ADR criteria.
    - Provider/mirror `diff -q`.
    - `git diff --check`.
  - closure ids:
    - cl-004, cl-005.
  - amendment trigger:
    - Need to change `spec-dock-clarification` skill or workflow docs.
    - Need to change runtime discussion doc renderer.

### S02 delegation contract

- delegated role:
  - `doc-writer`
- required reason:
  - shipped discussion template text changes.
- step scope:
  - Align discussion templates as source-grounded interview / research / synthesis evidence surfaces.
  - Close cl-004 and cl-005 only; do not change skill, workflow docs, runtime, or canonical spec templates.
- source of truth:
  - approved requirement / design / plan.
  - `iss-00163` clarification workflow result.
  - current provider discussion templates.
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_clarification.md`, `workflow_issue.md`, `docs/authoring/issue-plan.md`, and S02 target discussion templates.
- allowed changes:
  - S02 target provider and mirror discussion templates.
- forbidden changes:
  - skills, docs, runtime, tests, GitHub state, issue metadata.
- acceptance criteria:
  - cl-004: `interview`, `research`, and `disc` templates support source-grounded question, facts/inference separation, synthesis, adoption target, and reflection without canonical authority claims.
  - cl-005: changed paths remain limited to S02 provider/mirror discussion templates plus issue report evidence.
- required verification:
  - changed file list, targeted positive / negative `rg`, provider/mirror parity, `git diff --check`.
- required tests or docs-only verification:
  - docs-only / template-only verification through targeted `rg`, provider/mirror parity checks, scope guard, and whitespace diff check.
- reviewer focus:
  - `spec-reviewer` checks clarification workflow alignment, source-grounding support, evidence/adoption separation, and S02 scope containment.
- required output:
  - changed files, verification result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Need for skill/doc/runtime/test change.
  - Need for user intent clarification.
  - Verification cannot run.

### S02 concrete checks

- `tc-s02-001` inspect-only: interview source-grounded one-question flow.
  - 前提: `interview.md` provider/mirror pair is the only interview-template target for S02.
  - 操作: Inspect the provider/mirror diff and run targeted `rg` for one essential question, source-grounded context, answer capture, adoption target, and reflection fields.
  - 期待結果: `interview.md` supports one-question user interviews grounded in prior source inspection and records answer/adoption/reflection evidence.
  - 失敗検出: The template encourages broad questioning, omits source-grounding or answer capture, or treats interview notes as canonical authority.
  - 検証方法: targeted `rg` over provider/mirror `interview.md` plus human diff inspection.
  - 記録先: `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
  - related closure id: cl-004.
- `tc-s02-002` inspect-only: research / disc evidence separation.
  - 前提: `research.md` and `disc.md` provider/mirror pairs are the only research/synthesis template targets for S02.
  - 操作: Inspect the provider/mirror diff and run targeted `rg` for facts/inference/unverified/question candidates in `research.md`, and synthesis/reflection/adoption target/ADR triage in `disc.md`.
  - 期待結果: `research.md` separates facts, inference, unverified points, and question candidates; `disc.md` supports synthesis, reflection proposal, adoption target, and ADR triage.
  - 失敗検出: Research facts and inference are mixed without labels, synthesis has no adoption target, or discussion templates claim accepted/canonical authority outside ADR criteria.
  - 検証方法: targeted `rg` over provider/mirror `research.md` and `disc.md` plus human diff inspection.
  - 記録先: `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status.
  - related closure id: cl-004.
- `tc-s02-003` inspect-only: scope boundary.
  - 前提: S02 starts from a clean post-S01 commit or an explicitly recorded S01 approved-no-op state.
  - 操作: Run `git diff --name-only` for the S02 worktree diff before S02 review/commit.
  - 期待結果: Only S02 provider/mirror discussion templates and issue report evidence are changed.
  - 失敗検出: Any skill, workflow doc, runtime, test, GitHub metadata, or S01-only canonical template appears in the S02 diff.
  - 検証方法: `git diff --name-only` plus path comparison against S02 allowed paths.
  - 記録先: `report.md` Implementation Delegation Gate, Step Contract Closure, Closure Coverage, Step Commit Gate.
  - related closure id: cl-005.

### S02 report evidence destination

- pre-implementation and delegation decision:
  - `report.md` Implementation Delegation Gate.
- delegated worker summary / changed files / verification result:
  - `report.md` Delegated Draft Evidence if a worker produces a draft summary, and Implementation Delegation Gate for handoff result.
- observed verification and closure:
  - `report.md` Step Contract Closure, Test Contract Closure, and Closure Coverage.
- reviewer verdict:
  - `report.md` Reviewer Gate Status.
- commit or approved-no-op evidence:
  - `report.md` Step Commit Gate.
- material decision or plan deviation:
  - `report.md` Spec Interpretation / Decision Ledger before any canonical adoption.

### S02 step gate

- reviewer:
  - `spec-reviewer`
- pass condition:
  - `review_status: pass`
- commit boundary:
  - S02 template changes + report evidence.

## ドキュメント影響の解消ステップ S90

- 対象:
  - Dogfooding mirror and generated projections after template changes.
- 対応:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `git status --short`
  - provider/mirror `diff -q` for all changed template pairs.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: cl-006 pass.
- allowed paths:
  - `spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md`, `report.md` evidence only if sync rewrites projections.
- forbidden changes:
  - Additional provider templates / skills / docs / runtime changes after S01/S02 without returning to the relevant step.
- concrete check:
  - `tc-s90-001` manual-required: sync / validate / mirror validation.
  - 前提: S01 and S02 are committed or recorded as approved-no-op; no unreviewed implementation diff remains except S90-generated projections and report evidence.
  - 操作: Run `./spec-dock/scripts/spec-dock sync`, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, `git status --short`, and provider/mirror parity checks for all changed template pairs.
  - 期待結果: sync and validate succeed; whitespace check passes; changed provider/mirror template pairs match; any projection diff is limited to allowed S90 paths.
  - 失敗検出: sync/validate failure, provider/mirror mismatch, whitespace error, or unexpected non-S90 path appears.
  - 検証方法: command results plus path inspection of generated projection diffs.
  - 記録先: `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, and Final Quality Gate docs-impact subsection if created.
  - related closure id: cl-006.

### S90 report evidence destination

- sync / validate / parity command results:
  - `report.md` Step Contract Closure and Test Contract Closure.
- closure mapping:
  - `report.md` Closure Coverage.
- docs/spec reviewer verdict:
  - `report.md` Reviewer Gate Status.
- commit or approved-no-op evidence:
  - `report.md` Step Commit Gate.
- generated projection or mirror deviation:
  - `report.md` Spec Interpretation / Decision Ledger if material; otherwise Step Contract Closure notes.

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - issue planning commit to HEAD.
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - final `git status --short`
  - issue-wide diff inspection.
- final QA gate:
  - reviewer: `qa-reviewer`
  - scope: obligation coverage and verification adequacy.
- final code review:
  - reviewer: `code-reviewer`
  - scope: issue-wide integrated diff, scope boundary, markdown safety.
- final spec review:
  - reviewer: `spec-reviewer`
  - scope: requirement / design / plan / report / implementation / templates alignment.
- final commit gate:
  - final report ledger committed.
- concrete check:
  - `tc-s99-001` manual-required: final gates and report commit.
  - 前提: S01, S02, and S90 are committed or approved-no-op with reviewer gates recorded; no unresolved decision ledger entry remains.
  - 操作: Run final `./spec-dock/scripts/spec-dock validate`, `git diff --check`, final `git status --short`, issue-wide diff inspection, then obtain final `qa-reviewer`, `code-reviewer`, and `spec-reviewer` pass before final report commit.
  - 期待結果: validation and whitespace checks pass; final status contains only expected final report evidence before commit; all three final reviewers pass; final report ledger records closure and gate evidence.
  - 失敗検出: any final reviewer fails, validation fails, unexpected diff remains, unresolved ledger entry exists, or final report lacks required closure / reviewer / commit evidence destinations.
  - 検証方法: command results, issue-wide diff inspection, three reviewer outputs, and final report inspection.
  - 記録先: `report.md` Final Quality Gate, Reviewer Gate Status, Step Contract Closure, Closure Coverage, and Step Commit Gate.
  - related closure id: cl-007.

### S99 report evidence destination

- final validation and diff evidence:
  - `report.md` Final Quality Gate and Step Contract Closure.
- final QA/code/spec reviewer verdicts:
  - `report.md` Final QA Gate, Final Code Review Gate, Final Spec Review Gate, and Reviewer Gate Status.
- closure completeness:
  - `report.md` Closure Coverage.
- final report commit scope and external post-commit evidence pointer:
  - `report.md` Step Commit Gate and Final Commit.

## 未確定事項

- Blocking question:
  - なし。
- Amendment trigger:
  - Required scope expands into skills/docs/runtime/tests.
  - Template alignment requires policy change rather than scaffold/example wording.
  - GitHub #167 becomes part of `epic-00158` tree; currently it is not.

## 最終完了条件

- AC-001..AC-006 / EC-001..EC-003 達成。
- cl-001..cl-007 pass。
- S01/S02/S90/S99 reviewer gates pass。
- Final report commit complete。
- `issue finish` succeeds。

---
種別: 実装計画書（Issue）
ID: "iss-00268"
タイトル: "Dogfood artifacts without migrating discussions"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00268 Dogfood artifacts without migrating discussions — 実装計画

## この計画で満たす要件ID
- AC-268-001: dogfooding workspace で blank artifact が `artifacts/` に作成される。
- AC-268-002: typed artifact が expected filename contract で作成される。
- AC-268-003: 既存 `discussions/` paths は before/after で移動/rename/delete/link rewrite されない。
- AC-268-004: validate and sync pass, and projection distinguishes artifacts/discussions/canonical docs.
- AC-268-005: safe ADR / draft / delegated output smoke のうち少なくとも1つを記録する。
- AC-268-006: all Issues complete 後、Epic-wide spec/code/QA review gate を通し、問題がなければ Epic単位 PR 作成へ進める。

## 依存関係から導く実装順序
1. S00 planning readiness and assurance gate.
2. S01 dogfooding baseline snapshot.
3. S02 blank and typed artifact command smoke.
4. S03 Issue-scope draft artifact smoke.
5. S04 non-migration comparison, validate, sync, projection inspection.
6. S90 Epic report closeout via `doc-writer`.
7. S99 Issue final spec review, issue finish, commit.
8. Epic-wide pre-PR review and one Epic PR handoff after this Issue commit.

## ステップ一覧
- S00: Plan readiness and assurance gate.
- S01: Baseline snapshot.
- S02: Blank and typed artifact smoke.
- S03: Draft artifact smoke.
- S04: Validate / sync / non-migration verification.
- S90: Epic report closeout.
- S99: Issue final gate, finish, and commit.
- E99: Epic-wide pre-PR gate and PR handoff.

## 要件 ↔ ステップ対応
- AC-268-001: S02, S04, S99.
- AC-268-002: S02, S04, S99.
- AC-268-003: S01, S04, S99.
- AC-268-004: S04, S99.
- AC-268-005: S03, S99.
- AC-268-006: S90, E99.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-268-001 | AC-268-001 | DES-268-001, DES-268-003 | `new artifact blank --issue iss-00268` creates a direct-child Markdown artifact under `artifacts/` | command output / path inspection |
| CLOS-268-002 | AC-268-002 | DES-268-001, DES-268-003 | `new artifact research --issue iss-00268` creates a typed artifact with expected filename/frontmatter | command output / path and content inspection |
| CLOS-268-003 | AC-268-003 | DES-268-002 | before/after `discussions/` regular-file list and `rules.md` symlink state are identical | sorted snapshot plus `ls -l` / `readlink` comparison |
| CLOS-268-004 | AC-268-005 | DES-268-004 | `new artifact draft-requirement --issue iss-00268` creates an artifact draft and does not mutate canonical requirement | command output / diff inspection |
| CLOS-268-005 | AC-268-004 | DES-268-005 | `validate` and `sync` pass after artifact creation | command output |
| CLOS-268-006 | AC-268-004 | DES-268-005 | projection / generated output distinguishes canonical docs, future artifacts, and legacy discussions | read-only inspection |
| CLOS-268-007 | AC-268-006 | DES-268-006 | Epic report records all Issue completion and dogfooding closeout evidence | doc-writer evidence |
| CLOS-268-008 | AC-268-006 | DES-268-006 | Epic-wide spec/code/QA review gates are planned before one Epic PR | reviewer evidence / PR handoff notes |
| CLOS-268-009 | all | DES-268-007 | Issue 268 itself does not edit provider runtime/source/tests | diff inspection |

## 実装ステップ

## S00 Plan Readiness and Assurance Gate
- Owner: main orchestrator.
- Allowed edits:
  - Issue `design.md`, `plan.md`, `report.md`.
  - `.assurance.json` via SpecDock commands.
- Activities:
  - Confirm `iss-00268` active issue and dependency readiness.
  - Promote design / plan from draft to approved substantive artifacts.
  - Run `assurance classify --stage requirement` and `assurance verify`.
  - Obtain fresh `spec-reviewer` planning pass before command smoke.
- Exit criteria:
  - `guidance issue-planning` is ready.
  - `guidance issue-execution` allows executing approved plan.

## S01 Baseline Snapshot
- Owner: main orchestrator command execution.
- Target:
  - `spec-dock/active/issue` (`iss-00268`).
- Activities:
  - Record target Issue path.
  - Record `find <issue>/discussions -maxdepth 1 -type f -print | sort`.
  - Record `discussions/rules.md` symlink state with `ls -l` and `readlink`, and whether `artifacts/` exists.
  - Record current `git status --short`.
- Closure:
  - CLOS-268-003 baseline half.

## S02 Blank and Typed Artifact Smoke
- Owner: main orchestrator command execution.
- Commands:
  - `./spec-dock/scripts/spec-dock new artifact blank --issue iss-00268 --title "Dogfood Blank Artifact"`
  - `./spec-dock/scripts/spec-dock new artifact research --issue iss-00268 --title "Dogfood Research Artifact"`
- Activities:
  - Capture command stdout including `path=...`.
  - Inspect created paths are under `iss-00268/artifacts/` direct child.
  - Inspect frontmatter / title enough to prove template rendering.
- Closure:
  - CLOS-268-001, CLOS-268-002.
- Stop condition:
  - If command fails or writes outside `artifacts/`, stop and classify as Epic blocker.

## S03 Draft Artifact Smoke
- Owner: main orchestrator command execution.
- Precondition:
  - `assurance verify` passes for `iss-00268`.
- Command:
  - `./spec-dock/scripts/spec-dock new artifact draft-requirement --issue iss-00268 --title "Dogfood Draft Requirement"`
- Activities:
  - Capture command stdout including `path=...`.
  - Inspect artifact path and enough content to confirm requirement template reuse.
  - Confirm canonical `requirement.md` was not modified by this command.
  - Record delegated-output smoke as skipped because `iss-00266` already covered delegated diff guard and draft smoke satisfies AC-268-005.
- Closure:
  - CLOS-268-004.

## S04 Non-migration, Validate, Sync, Projection
- Owner: main orchestrator command execution.
- Activities:
  - Re-run `find <issue>/discussions -maxdepth 1 -type f -print | sort` and compare with S01.
  - Re-run `ls -l <issue>/discussions/rules.md` and `readlink <issue>/discussions/rules.md`, then compare with S01.
  - Record after `artifacts/` direct-child file list.
  - Run `./spec-dock/scripts/spec-dock validate`.
  - Run `./spec-dock/scripts/spec-dock sync`.
  - Inspect sync-generated projection output enough to show canonical docs, artifacts, and legacy discussions remain distinct.
  - Treat sync-generated projection diffs as allowed evidence only when they are deterministic SpecDock outputs from this command; record any such paths in `report.md`. If `sync` produces unrelated or unstable diffs, stop and classify them before commit.
- Closure:
  - CLOS-268-003, CLOS-268-005, CLOS-268-006, CLOS-268-009.

## S90 Epic Report Closeout
- Delegation: `doc-writer`.
- Allowed path:
  - `spec-dock/active/epic/report.md`.
- Source of truth:
  - This Issue report.
  - Git log / Issue commits for `iss-00262` through `iss-00268`.
  - Validation / sync / dogfooding evidence from S01-S04.
- Activities:
  - Update Epic progress summary from planning-only state to executed Issue sequence state.
  - Record executable Issues `iss-00262` through `iss-00268` completion and commit hashes.
  - Record dogfooding evidence and one-Epic-PR policy.
  - Leave PR creation itself to E99 after final review gates.
- Closure:
  - CLOS-268-007.

## S99 Issue Final Gate, Finish, Commit
- Owner: main orchestrator.
- Required checks:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock assurance verify`
  - final `spec-reviewer` pass for Issue 268 evidence.
- Completion:
  - Run `./spec-dock/scripts/spec-dock issue finish` after final Issue gates pass.
  - Commit Issue 268 diff.
  - Do not create per-Issue PR.

## E99 Epic-wide Pre-PR Gate and PR Handoff
- Owner: main orchestrator with reviewer subagents / PR skill.
- Timing:
  - After Issue 268 commit and all executable Issues complete.
- Required reviews:
  - Epic-wide `spec-reviewer`.
  - Epic-wide `code-reviewer` for the full Epic diff because earlier Issues include runtime/test changes.
  - Epic-wide `qa-reviewer` for verification sufficiency.
- PR:
  - Create one Epic-level PR only after all Epic-wide reviews pass.
  - PR body must link Epic `#259`, abolished `#261`, executable `#262` through `#268`, and quality gate evidence.

## Allowed Files / Outputs
- Dogfooding generated artifacts under active Issue `artifacts/`.
- Issue `design.md`, `plan.md`, `report.md`, `.assurance.json`.
- Epic `report.md` only via `doc-writer`.
- Deterministic `sync` projection output, if produced by S04, only as command evidence; commit only when the diff is expected and recorded in `report.md`.

## Forbidden Files / Actions
- Do not edit provider runtime/source/tests in this Issue unless a dogfood failure proves prior implementation incomplete and user/plan are updated.
- Do not move, rename, delete, or rewrite legacy `discussions/`.
- Do not create per-Issue PR.
- Do not create the Epic PR before E99 gates pass.

---
種別: 実装計画書（Issue）
ID: "iss-00304"
タイトル: "ChatGPT Authoring Skill"
関連GitHub: ["#304"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00304 ChatGPT Authoring Skill — 実装計画

## 1. 実装方針

この Issue は installed skill layer を更新する。実装は provider-side source of truth である `src/spec_dock/assets/install_root/.agents/skills/` から行い、必要最小限の docs index / installer tests を追加する。

中間 Issue のため、この Issue では PR を作成しない。すべての検証と reviewer pass を report に記録した上で commit / push / `issue finish` を行い、次 Issue へリレーする。Epic 単位の PR delivery は `iss-00307` が行う。

## 2. Closure IDs

| ID | Close condition | Evidence |
|---|---|---|
| CLOS-001 | `spec-dock-chatgpt-authoring/SKILL.md` exists with valid skill header | file inspection / tests |
| CLOS-002 | New skill is installed into consumer repo by init/update | installer test or install simulation |
| CLOS-003 | Existing planning skill names remain unchanged | inventory inspection / test |
| CLOS-004 | Initiative planning skill references ChatGPT authoring as evidence lane only | file inspection / snapshot assertion |
| CLOS-005 | Epic planning skill references ChatGPT ZIP/tree and Issue drafts as evidence-only handoff | file inspection / snapshot assertion |
| CLOS-006 | Issue planning skill documents `zero-base`, `requirement-first`, and `draft-adoption` modes | file inspection / snapshot assertion |
| CLOS-007 | Forbidden authority claims are explicitly listed in the new skill | file inspection / test |
| CLOS-008 | Stop gate / responsibility matrix is present | file inspection / report evidence |
| CLOS-009 | No hardcoded personal ChatGPT wrapper path is introduced in shipped installed assets/tests | `rg` scan |
| CLOS-010 | `spec-dock validate` passes | command output |
| CLOS-011 | `assurance verify` passes | command output |
| CLOS-012 | `git diff --check` passes | command output |
| CLOS-013 | fresh `spec-reviewer`, `code-reviewer`, and `qa-reviewer` pass where required | reviewer outputs |
| CLOS-014 | no per-Issue PR is created; PR delivery deferred to `iss-00307` | report evidence |
| CLOS-015 | branch is committed, pushed, and issue is finished | git / spec-dock output |

## 3. Requirement Coverage

| Requirement / AC | Covered by steps | Verification |
|---|---|---|
| AC-001, BH-001 | S02, S05 | skill file existence / front matter test |
| AC-002 | S05 | init/update install simulation or installer inventory test |
| AC-003, BH-002 | S01, S03, S05 | inventory and path inspection |
| AC-004, BH-005 | S03, S05 | mode wording assertion |
| AC-005, BH-003, BH-004 | S02, S03, S04, S05 | wording assertion / reviewer |
| AC-006, BH-006 | S02, S05 | forbidden claim assertion |
| AC-007 | S02, S04 | matrix in skill/report |
| AC-008 | S05 | installer test / simulation |
| AC-009, BH-007 | S05 | local path scan |
| AC-010 | S99 | validate / assurance / diff-check |
| AC-011 | S99 | report relay evidence |

## 4. 実装ステップ（Step Sequence）

This section is the planned executable workflow contract / command queue. Each step has a behavior goal, planned verification, step closure contract, report evidence destination, and step gate. Observed evidence must be recorded in `report.md`, not back-written into this plan.

### S00: Planning evidence adoption

Actions:

- Adopt Issue-local draft requirement/design/plan into canonical docs.
- Record ChatGPT Use attempt and failure as evidence, not authority.
- Record no-per-Issue-PR relay policy.

Verification:

- `./spec-dock/scripts/spec-dock guidance issue-planning`
- `./spec-dock/scripts/spec-dock validate`

Closure:

- CLOS-014 partial.

Step closure contract:

- Close when canonical docs are substantive, source binding is refreshed, and Evidence Adoption Ledger records draft / ChatGPT evidence without granting authority.
- Report evidence destination: Evidence Adoption Ledger, Spec Authoring Gate, Delegated Draft Evidence, Execution Evidence Log.
- Step gate: do not start implementation until fresh spec-reviewer pass is recorded.

### S01: Installed skill inventory baseline

Actions:

- Inspect existing provider-side installed skills.
- Confirm existing planning skill names and paths.
- Inspect whether installer has recursive install_root behavior or explicit allowlist.

Verification:

```bash
find src/spec_dock/assets/install_root/.agents/skills -maxdepth 2 -name SKILL.md | sort
rg -n "install_root|\\.agents/skills|managed skill" src/spec_dock tests -g '!tests/unit/infra/test_init_update.py'
```

Closure:

- CLOS-003.

Step closure contract:

- Close when provider installed skill inventory, managed list behavior, and existing planning skill names are inspected.
- Report evidence destination: Execution Evidence Log and Step Contract Closure.
- Step gate: do not edit inventory until provider source-of-truth path is confirmed.

### S02: Add `spec-dock-chatgpt-authoring`

Actions:

- Create `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
- Include purpose, Read First, modes, operating spine, evidence contract, forbidden claims, and stop conditions.
- Keep it as a concise operational kernel, not a generated runbook.

Verification:

- File exists and header is valid.
- Forbidden claims are present.
- Local wrapper path scan passes.

Closure:

- CLOS-001, CLOS-007, CLOS-008, CLOS-009.

Step closure contract:

- Close when new skill asset exists, frontmatter is valid, forbidden authority claims are listed as stop conditions, and local wrapper path scan is clean.
- Report evidence destination: Step Contract Closure, Test Contract Closure, Delegated Worker Evidence.
- Step gate: do not proceed if the skill presents ChatGPT output as canonical authority or hardcodes a personal wrapper path.

### S03: Update existing planning skills

Actions:

- Update `spec-dock-initiative-planning/SKILL.md` with ChatGPT evidence lane note and human approval stop gate.
- Update `spec-dock-epic-planning/SKILL.md` with ZIP/tree Issue draft handoff note and Issue creation approval gate.
- Update `spec-dock-issue-planning/SKILL.md` with `zero-base`, `requirement-first`, and `draft-adoption` modes.

Verification:

- Inspect names remain unchanged.
- Assert key mode names and evidence-only wording.

Closure:

- CLOS-003, CLOS-004, CLOS-005, CLOS-006.

Step closure contract:

- Close when hub and planning skill wording are updated, existing `name:` fields remain stable, and Issue planning modes are visible.
- Report evidence destination: Step Contract Closure, Test Contract Closure, Reviewer Gate Status.
- Step gate: do not proceed if a skill rename or broad workflow rewrite becomes necessary.

### S04: Update discoverability docs only if needed

Actions:

- Inspect `src/spec_dock/assets/spec_dock/docs/README.md` and workflow docs index.
- If the new skill is missing from the installed docs index, add a small entry.
- Do not perform broad workflow rewrite; defer broad guidance to `iss-00306`.

Verification:

- Docs diff is minimal or approved no-op recorded.

Closure:

- CLOS-008 partial if docs index is used as install/discovery evidence.

Step closure contract:

- Close when docs index either lists the new skill or a documented approved-no-op explains why discoverability is already covered.
- Report evidence destination: Step Contract Closure and Closure Coverage.
- Step gate: do not proceed if installed docs and managed inventory diverge.

### S05: Add or update focused tests

Actions:

- Add focused test coverage for installed skill presence and install simulation if existing tests do not already cover all install_root files.
- Add content assertions only for safety-critical wording:
  - skill header
  - issue planning modes
  - evidence-only boundary
  - forbidden claims
  - no local wrapper path

Verification:

```bash
uv run pytest tests/unit/infra/test_init_update.py -q -k "skill or install_root or chatgpt"
uv run pytest tests/unit/infra -q -k "skill or install_root or chatgpt"
```

Use narrower actual test names after inspecting the suite.

Closure:

- CLOS-001 through CLOS-009.

Step closure contract:

- Close when focused tests protect managed inventory, installed skill presence, existing skill names, Issue planning modes, forbidden claims, and local wrapper path absence.
- Report evidence destination: Test Contract Closure and Closure Coverage.
- Step gate: do not proceed if only manual inspection covers an automatable installed-skill behavior.

### S90: Reviewer and docs impact resolution

Actions:

- Run spec review after canonical docs and implementation changes.
- If docs index changed, ensure spec-reviewer covers user-facing workflow consistency.
- Run code-reviewer for installed asset / installer / tests.
- Run qa-reviewer for install simulation and safety wording coverage.

Verification:

- fresh reviewer pass outputs.

Closure:

- CLOS-013.

Step closure contract:

- Close when fresh spec-reviewer, code-reviewer, and qa-reviewer pass or an approved no-op is explicitly allowed by workflow for unchanged surfaces.
- Report evidence destination: Reviewer Gate Status and Final Quality Gate evidence.
- Step gate: unavailable, denied, waived, provisional, stale, or failed reviewer results block issue finish.

### S99: Final local quality gate and relay closeout

Actions:

- Run focused tests and core SpecDock verification.
- Record evidence in `report.md`.
- Commit and push.
- Run `./spec-dock/scripts/spec-dock issue finish`.
- Start the next Issue if dependencies allow.

Verification:

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify
git diff --check
rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  tests/cli_runtime/test_wrappers.py \
  tests/cli_runtime/harness.py \
  tests/unit/infra/test_init_update.py
git status --short
```

Closure:

- CLOS-010 through CLOS-015.

Step closure contract:

- Close when final verification commands pass, report evidence is current, branch is committed and pushed, no per-Issue PR exists, and `issue finish` succeeds.
- Report evidence destination: Closure Coverage, No-PR Relay Policy, Final Commit / Deferred PR Delivery evidence.
- Step gate: do not finish while any closure remains pending or the worktree is dirty after final commit.

## 5. 具体テストケース（Concrete Test Cases）

- `tc-s00-001` planning adoption: draft and ChatGPT evidence stay evidence-only
  - 前提: Issue-local draft artifacts and ChatGPT Use planning result exist.
  - 操作: Inspect `report.md` Evidence Adoption Ledger, Delegated Draft Evidence, and canonical docs.
  - 期待結果: Draft / ChatGPT claims are integrated only as review candidates; fresh spec-reviewer pass remains required before execution.
  - 失敗検出: `report.md` treats delegated evidence as reviewer pass, execution-ready, or final promotion before fresh review.
  - 検証方法: docs inspection plus `./spec-dock/scripts/spec-dock guidance issue-planning`.
  - 関連 closure id: CLOS-014.

- `tc-s01-001` inventory baseline: managed skill mechanism is understood
  - 前提: provider-side installed assets and installer code are available.
  - 操作: Inspect `src/spec_dock/assets/install_root/.agents/skills`, `src/spec_dock/cli.py`, and expected managed skill tests.
  - 期待結果: source-of-truth path and managed inventory update point are identified before edits.
  - 失敗検出: implementation edits dogfood-only `.agents/skills` or misses `_MANAGED_SKILL_NAMES`.
  - 検証方法: file inspection and focused grep output recorded in `report.md`.
  - 関連 closure id: CLOS-003.

- `tc-s02-001` new skill: provider skill file is installed-ready
  - 前提: new provider asset path is in scope.
  - 操作: Create and inspect `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
  - 期待結果: front matter has `name: spec-dock-chatgpt-authoring` and the text defines evidence-only behavior.
  - 失敗検出: file is missing, named differently, or claims canonical adoption / reviewer / execution / PR authority.
  - 検証方法: focused pytest or text assertion.
  - 関連 closure id: CLOS-001, CLOS-007.

- `tc-s03-001` planning skills: existing names are preserved
  - 前提: hub and planning skill files are updated.
  - 操作: Inspect frontmatter names and route text.
  - 期待結果: existing planning skill `name:` values remain unchanged, and ChatGPT lane appears only as shared evidence lane.
  - 失敗検出: a planning skill is renamed or the new lane replaces scope planning authority.
  - 検証方法: focused text assertion and spec-reviewer inspection.
  - 関連 closure id: CLOS-003, CLOS-004, CLOS-005.

- `tc-s03-002` issue planning modes: draft adoption modes are explicit
  - 前提: `spec-dock-issue-planning/SKILL.md` is updated.
  - 操作: Inspect the skill text for `zero-base`, `requirement-first`, and `draft-adoption`.
  - 期待結果: all three modes are present and tied to evidence adoption / fresh reviewer pass.
  - 失敗検出: Issue planning still leaves draft adoption mode implicit.
  - 検証方法: focused text assertion.
  - 関連 closure id: CLOS-006.

- `tc-s04-001` docs discoverability: installed docs list the new skill
  - 前提: docs README is updated or intentionally left unchanged with no-op rationale.
  - 操作: Inspect `src/spec_dock/assets/spec_dock/docs/README.md`.
  - 期待結果: README lists `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` when used as the installed entrypoint index.
  - 失敗検出: users can install the skill but docs entrypoints omit it.
  - 検証方法: focused text assertion.
  - 関連 closure id: CLOS-008.

- `tc-s05-001` install simulation: consumer repo receives the skill
  - 前提: managed inventory and provider asset are updated.
  - 操作: Run installer/wrapper tests that initialize a temp repo.
  - 期待結果: temp repo contains `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
  - 失敗検出: asset exists in provider tree but is omitted from managed installation.
  - 検証方法: `uv run pytest tests/cli_runtime/test_wrappers.py -q` and focused `test_init_update` selection.
  - 関連 closure id: CLOS-002.

- `tc-s99-001` final guard: no local wrapper dependency is shipped
  - 前提: implementation and tests are complete.
  - 操作: Run the planned `rg` scan for `/Users/iwasawayuuta`, `.codex/skills/chatgpt-use`, and `oracle-chatgpt`.
  - 期待結果: no shipped installed skill / docs / tests introduce a personal local wrapper dependency.
  - 失敗検出: installed skill text hardcodes the user's local wrapper path.
  - 検証方法: path scan command in S99.
  - 関連 closure id: CLOS-009.

- `tc-s99-002` final verification: SpecDock and git checks pass
  - 前提: implementation is complete.
  - 操作: Run `spec-dock validate`, `assurance verify`, `git diff --check`, focused pytest, and reviewer gates.
  - 期待結果: all required checks pass and report evidence is current.
  - 失敗検出: stale source binding, whitespace error, failing focused test, or reviewer non-pass.
  - 検証方法: command output and reviewer results recorded in `report.md`.
  - 関連 closure id: CLOS-010, CLOS-011, CLOS-012, CLOS-013.

## 6. Delegation Contract

### S01 delegation contract

- delegated role: repo-analyst or main orchestrator inspection.
- input docs: `requirement.md`, `design.md`, provider installed skill tree, `src/spec_dock/cli.py`, relevant tests.
- allowed paths: read-only.
- forbidden changes: none because this is inspection only.
- acceptance criteria: CLOS-003.
- required tests or docs-only verification: inventory grep and file inspection.
- reviewer focus: source-of-truth path is correct.
- stop conditions: inventory mechanism is ambiguous or points outside provider install_root.
- output required: inventory and install mechanism summary in `report.md`.

### S02 delegation contract

- delegated role: doc-writer.
- input docs: `requirement.md`, `design.md`, existing installed skills.
- allowed paths: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
- forbidden changes: runtime commands, tests, existing planning skill names, local absolute wrapper dependency.
- acceptance criteria: CLOS-001, CLOS-007, CLOS-008, CLOS-009.
- required tests or docs-only verification: frontmatter and forbidden-claim text inspection.
- reviewer focus: evidence-only lane and stop conditions.
- stop conditions: new skill needs canonical write authority or backend command implementation.
- output required: changed file, wording summary, risk notes.

### S03 delegation contract

- delegated role: doc-writer.
- input docs: parent Epic skill taxonomy, existing hub and planning skills.
- allowed paths: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`, `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`, `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`.
- forbidden changes: skill rename, broad workflow rewrite, execution skill changes unless a direct inconsistency is found and recorded.
- acceptance criteria: CLOS-003, CLOS-004, CLOS-005, CLOS-006.
- required tests or docs-only verification: text assertions for route, mode names, evidence-only wording, and preserved frontmatter names.
- reviewer focus: scope planning authority remains with planning skills.
- stop conditions: human approval or reviewer pass would be bypassed by the wording.
- output required: changed files, wording summary, unresolved risks.

### S04 delegation contract

- delegated role: doc-writer.
- input docs: docs README and updated skill inventory.
- allowed paths: `src/spec_dock/assets/spec_dock/docs/README.md`.
- forbidden changes: broad workflow guidance rewrite, runtime command reference expansion beyond entrypoint list.
- acceptance criteria: CLOS-008.
- required tests or docs-only verification: docs README text assertion or approved no-op rationale.
- reviewer focus: installed discoverability and consistency with hub / managed inventory.
- stop conditions: docs update overlaps with `iss-00306` broad workflow guidance.
- output required: docs diff or no-op rationale.

### S05 delegation contract

- delegated role: dev-coder.
- input docs: changed skills/docs, `src/spec_dock/cli.py`, test harness expectations.
- allowed paths: `src/spec_dock/cli.py`, `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_wrappers.py`, `tests/unit/infra/test_init_update.py`.
- forbidden changes: unrelated installer refactor, weakening existing managed asset assertions, broad test rewrites.
- acceptance criteria: CLOS-001 through CLOS-009.
- required tests or docs-only verification: focused pytest covering managed inventory / installed skill presence / wording.
- reviewer focus: regression tests fail for real install/list mismatch and avoid brittle prose overreach.
- stop conditions: the test surface cannot observe a required AC without changing production behavior outside scope.
- output required: changed files, focused test results, discovered risks.

### S90 delegation contract

- delegated role: spec-reviewer, code-reviewer, qa-reviewer.
- input docs: all changed planning docs, installed skills, docs, installer inventory, tests.
- allowed paths: read-only.
- forbidden changes: edits.
- acceptance criteria: CLOS-013.
- required verification: fresh reviewer outputs with `review_status: pass`.
- reviewer focus: spec alignment, code/test correctness, QA coverage.
- stop conditions: any non-pass, unavailable, denied, waived, provisional, or stale review.
- output required: prioritized findings and authoritative review status.

### S99 delegation contract

- delegated role: main orchestrator / spec-manager for commands.
- input docs: final report, git diff, test output.
- allowed paths: report evidence updates and lifecycle commands.
- forbidden changes: per-Issue PR creation, unrelated cleanup, closing with dirty worktree.
- acceptance criteria: CLOS-010 through CLOS-015.
- required verification: focused pytest, `validate`, `assurance verify`, `git diff --check`, path scan, commit/push/finish evidence.
- reviewer focus: final evidence completeness and relay policy.
- stop conditions: any closure remains pending or final worktree is not clean after commit.
- output required: verification, commit/push/finish evidence.

## 6.1 Step-Local Executable Contracts

### S00 executable contract: planning evidence adoption

Behavior goal:

- Convert Issue-local draft artifacts into canonical Issue docs without treating ChatGPT output or draft artifacts as authority.

Planned contract:

- Scope: `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json` source binding.
- Test obligation: manual-required, because this is canonical authoring and assurance binding rather than product code.
- Red or alternative evidence requirement: inspect-only. `guidance issue-planning` must initially show a planning blocker such as `requirement-capture` or equivalent, proving execution cannot start from scaffold docs.
- Green verification: `assurance classify --stage requirement`, `assurance verify`, `spec-dock validate`, and `git diff --check` pass after canonical rewrite.
- Refactor guardrail: do not rewrite source/tests/installed assets in S00.
- Amendment trigger: any new scope, non-scope, acceptance criterion, or authority boundary discovered during spec-review requires plan/report amendment and re-review.

Delegation contract:

- Delegated role: main orchestrator only for issue docs; no worker edits.
- Input docs: active Issue draft artifacts, active Epic docs, `workflow_issue.md`, `workflow_spec_authoring.md`, `docs/authoring/issue-plan.md`.
- Allowed paths: active Issue `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`.
- Forbidden changes: provider source, tests, installed skill assets, runtime docs outside active Issue docs.
- Acceptance criteria: CLOS-014 partial, substantive canonical docs, report EAL entries, no authority claim leakage.
- Required verification: `guidance issue-planning`, `assurance classify`, `assurance verify`, `spec-dock validate`, `git diff --check`.
- Reviewer focus: spec-reviewer checks evidence adoption, authority boundaries, executable plan readiness.
- Stop conditions: ChatGPT result claims authority; draft adoption evidence missing; assurance verification fails.
- Output required: updated canonical docs, EAL entries, command output summary, unresolved risks.

Report evidence destination:

- Evidence Adoption Ledger, Spec Authoring Gate, Delegated Draft Evidence, Step Contract Closure, Test Contract Closure.

Step gate:

- Do not proceed to implementation until fresh spec-reviewer pass is recorded.

具体テストケース一覧:

- `tc-s00-001` inspect-only: scaffold planning blocker is observed
  - 前提: active Issue docs may still be scaffold or draft-derived.
  - 操作: `./spec-dock/scripts/spec-dock guidance issue-planning` を実行する。
  - 期待結果: execution is not allowed before canonical rewrite and reviewer gate.
  - 失敗検出: draft/scaffold docs are treated as execution-ready.
  - 検証方法: command output inspection.
  - 関連 closure id: CLOS-014.

- `tc-s00-002` manual-required: canonical docs are adopted without ChatGPT authority
  - 前提: Issue-local draft artifacts exist and ChatGPT Use result is unavailable.
  - 操作: `requirement.md`, `design.md`, `plan.md`, `report.md` を確認する。
  - 期待結果: canonical docs are substantive and report records ChatGPT attempt as rejected/no result, not authority.
  - 失敗検出: report or docs imply ChatGPT result provided reviewer pass, canonical adoption, execution-ready, or PR-ready.
  - 検証方法: file inspection plus spec-reviewer.
  - 関連 closure id: CLOS-014.

### S01 executable contract: installed skill inventory baseline

Behavior goal:

- Establish current installed skill inventory and installer behavior before editing assets.

Planned contract:

- Scope: read-only inspection of provider install_root, installer managed skill list, and relevant tests.
- Test obligation: inspect-only.
- Red or alternative evidence requirement: inspect-only. Confirm `spec-dock-chatgpt-authoring` is absent before implementation.
- Green verification: inventory and installer behavior summary recorded in report.
- Refactor guardrail: no file edits in S01.
- Amendment trigger: if installer uses a strict allowlist or non-recursive install path not captured in design, amend design/plan and re-review.

Delegation contract:

- Delegated role: repo-analyst optional; main inspection allowed because read-only.
- Input docs: `design.md`, `src/spec_dock/cli.py`, `tests/unit/infra/test_init_update.py`, `tests/cli_runtime/harness.py`.
- Allowed paths: read-only.
- Forbidden changes: all writes.
- Acceptance criteria: CLOS-003 partial; existing skill names and install mechanism known.
- Required verification: `find .../.agents/skills`, `rg install_root|.agents/skills`.
- Reviewer focus: code-reviewer later checks that implementation matches observed installer behavior.
- Stop conditions: install behavior cannot be determined from repo inspection.
- Output required: inventory summary and affected test candidates.

Report evidence destination:

- Step Contract Closure, Implementation Delegation Gate, Closure Coverage.

Step gate:

- Do not edit installed assets until provider source-of-truth and managed list behavior are known.

具体テストケース一覧:

- `tc-s01-001` inspect-only: managed skill inventory baseline
  - 前提: provider install_root contains existing SpecDock skills.
  - 操作: `find src/spec_dock/assets/install_root/.agents/skills -maxdepth 2 -name SKILL.md | sort` を実行する。
  - 期待結果: existing planning skill paths are present and `spec-dock-chatgpt-authoring` is absent before implementation.
  - 失敗検出: target skill already exists or existing planning skill path is missing.
  - 検証方法: command output inspection.
  - 関連 closure id: CLOS-003.

- `tc-s01-002` inspect-only: installer inventory mechanism
  - 前提: installer may use recursive install_root plus `_MANAGED_SKILL_NAMES`.
  - 操作: `rg -n "install_root|_MANAGED_SKILL_NAMES|\\.agents/skills" src/spec_dock tests` を実行する。
  - 期待結果: implementation knows whether adding the skill requires `_MANAGED_SKILL_NAMES` and test expectation updates.
  - 失敗検出: edits proceed without identifying an allowlist or inventory test expectation.
  - 検証方法: command output inspection.
  - 関連 closure id: CLOS-002, CLOS-003.

### S02 executable contract: add `spec-dock-chatgpt-authoring`

Behavior goal:

- Add a shipped installed skill that describes ChatGPT authoring as evidence-only lane.

Planned contract:

- Scope: new `SKILL.md` under provider install_root.
- Test obligation: covered-existing plus focused content assertions if no current test covers the new asset.
- Red or alternative evidence requirement: covered-existing/inspect-only. Existing inventory test should fail after `_MANAGED_SKILL_NAMES` update until file exists, or file absence inspection is recorded.
- Green verification: file exists, frontmatter name is exact, forbidden claims list exists, local wrapper path scan is clean.
- Refactor guardrail: do not change runtime command behavior in this step.
- Amendment trigger: if the skill needs backend command syntax beyond existing runtime, amend scope or defer to a later Issue.

Delegation contract:

- Delegated role: doc-writer.
- Input docs: `requirement.md`, `design.md`, `plan.md`, existing planning skill files, `workflow_issue.md`, `workflow_spec_authoring.md`.
- Allowed paths: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
- Forbidden changes: runtime scripts, tests except via S05, `.assurance.json`, local wrapper absolute paths, broad workflow docs.
- Acceptance criteria: CLOS-001, CLOS-007, CLOS-008, CLOS-009.
- Required tests or docs-only verification: file inspection, focused content assertion, local wrapper path scan.
- Reviewer focus: spec-reviewer checks authority boundary; code-reviewer checks installed asset placement.
- Stop conditions: skill wording claims canonical adoption, reviewer pass, readiness, PR delivery, or requires a personal local wrapper.
- Output required: changed file, wording summary, verification commands, unresolved risks.

Report evidence destination:

- Delegated Worker Evidence, Step Contract Closure, Test Contract Closure.

Step gate:

- Do not proceed if the new skill is not provider-side installed asset.

具体テストケース一覧:

- `tc-s02-001` acceptance: new skill file and header
  - 前提: provider install_root is the source of truth for installed skills.
  - 操作: Inspect `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
  - 期待結果: file exists and frontmatter has `name: spec-dock-chatgpt-authoring`.
  - 失敗検出: file is only under dogfood workspace, missing, or has a different name.
  - 検証方法: focused test or file inspection.
  - 関連 closure id: CLOS-001.

- `tc-s02-002` negative: forbidden authority claims are blocked by wording
  - 前提: ChatGPT authoring output may include unsafe claims.
  - 操作: Inspect new skill text.
  - 期待結果: forbidden claims include canonical adoption, `.assurance.json` mutation, authorized profile decision, reviewer pass, execution-ready, PR-ready, merge-ready, Issue finish, Epic completion, and PR delivery.
  - 失敗検出: skill allows or omits a safety-critical forbidden claim.
  - 検証方法: focused content assertion and spec-reviewer.
  - 関連 closure id: CLOS-007.

### S03 executable contract: update existing planning skills

Behavior goal:

- Make planning skills route ChatGPT output as evidence while preserving canonical planning authority.

Planned contract:

- Scope: existing provider install_root planning skill `SKILL.md` files.
- Test obligation: inspect-only plus focused wording assertions.
- Red or alternative evidence requirement: inspect-only. Baseline lacks explicit ChatGPT lane and Issue planning modes.
- Green verification: touched skill docs contain evidence-only relationship notes, human approval stop gates, and `zero-base` / `requirement-first` / `draft-adoption`.
- Refactor guardrail: do not rename existing skills or split Issue planning.
- Amendment trigger: if a skill rename/split becomes necessary, stop and return to Epic planning/user decision.

Delegation contract:

- Delegated role: doc-writer.
- Input docs: `requirement.md`, `design.md`, `plan.md`, existing planning skill files.
- Allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- Forbidden changes: existing skill `name:` values, broad workflow docs, runtime scripts, tests.
- Acceptance criteria: CLOS-003, CLOS-004, CLOS-005, CLOS-006.
- Required tests or docs-only verification: focused content assertions for mode names and evidence-only language.
- Reviewer focus: spec-reviewer checks planning authority and stop gates.
- Stop conditions: wording creates a shortcut around human approval, EAL, or fresh spec-reviewer.
- Output required: changed files, wording summary, safety boundary summary.

Report evidence destination:

- Delegated Worker Evidence, Step Contract Closure, Test Contract Closure, Reviewer Gate Status.

Step gate:

- Do not proceed if existing planning skill names change.

具体テストケース一覧:

- `tc-s03-001` acceptance: Issue planning modes are explicit
  - 前提: `spec-dock-issue-planning` is the Issue planning entrypoint.
  - 操作: Inspect or assert `zero-base`, `requirement-first`, and `draft-adoption` in the skill body.
  - 期待結果: all three modes are present with distinct starting evidence and stop gates.
  - 失敗検出: mode names are missing or `draft-adoption` bypasses spec-reviewer.
  - 検証方法: focused content assertion and spec-reviewer.
  - 関連 closure id: CLOS-006.

- `tc-s03-002` regression: existing skill names preserved
  - 前提: users already rely on existing planning skill names.
  - 操作: Inspect frontmatter `name:` and installed skill paths.
  - 期待結果: `spec-dock-initiative-planning`, `spec-dock-epic-planning`, and `spec-dock-issue-planning` remain unchanged.
  - 失敗検出: any touched planning skill is renamed or moved.
  - 検証方法: inventory assertion / file inspection.
  - 関連 closure id: CLOS-003.

### S04 executable contract: discoverability docs impact

Behavior goal:

- Keep docs entrypoint list aligned with installed skills without expanding into broad workflow rewrite.

Planned contract:

- Scope: docs README/index only if required.
- Test obligation: inspect-only/manual-required.
- Red or alternative evidence requirement: inspect-only. Determine whether docs index omits the new installed skill.
- Green verification: docs index includes the new skill or report records approved-no-op with rationale.
- Refactor guardrail: defer broad workflow guidance to `iss-00306`.
- Amendment trigger: if workflow docs need semantic changes beyond discoverability, defer or amend scope.

Delegation contract:

- Delegated role: doc-writer if docs change; main inspection for approved no-op.
- Input docs: `src/spec_dock/assets/spec_dock/docs/README.md`, requirement/design/plan.
- Allowed paths: `src/spec_dock/assets/spec_dock/docs/README.md` only unless re-reviewed.
- Forbidden changes: broad workflow docs, phase docs, runtime command docs.
- Acceptance criteria: CLOS-008 partial.
- Required tests or docs-only verification: docs diff inspection, spec-reviewer if changed.
- Reviewer focus: spec-reviewer checks discoverability without scope expansion.
- Stop conditions: discoverability update requires workflow rewrite.
- Output required: changed docs or approved-no-op rationale.

Report evidence destination:

- Step Contract Closure, Closure Delta if docs scope changes, Reviewer Gate Status.

Step gate:

- Do not update broad workflow docs in this Issue.

具体テストケース一覧:

- `tc-s04-001` inspect-only: docs entrypoint alignment
  - 前提: docs README lists installed operational entrypoint skills.
  - 操作: Inspect `src/spec_dock/assets/spec_dock/docs/README.md`.
  - 期待結果: `spec-dock-chatgpt-authoring` is listed, or report records why docs update is intentionally deferred/non-blocking.
  - 失敗検出: installed skill is undiscoverable and no no-op rationale exists.
  - 検証方法: docs inspection and spec-reviewer.
  - 関連 closure id: CLOS-008.

### S05 executable contract: focused tests and installer verification

Behavior goal:

- Prove the new installed skill ships to consumer repositories and safety-critical wording is protected.

Planned contract:

- Scope: focused installer / infra tests and optional cli harness expected skill list.
- Test obligation: red-required when adding a managed skill to expected inventory; otherwise covered-existing with new assertions.
- Red or alternative evidence requirement: if `_MANAGED_SKILL_NAMES` is updated before the new file, managed skill install test must fail. If implementation order differs, record file-absence inspection as red alternative.
- Green verification: focused pytest passes and install simulation target contains the new skill.
- Refactor guardrail: do not rewrite large installer tests unrelated to skill inventory.
- Amendment trigger: if installer logic needs architectural change rather than expected-list update, amend design and re-review.

Delegation contract:

- Delegated role: dev-coder.
- Input docs: `requirement.md`, `design.md`, `plan.md`, `src/spec_dock/cli.py`, relevant tests.
- Allowed paths:
  - `src/spec_dock/cli.py` if `_MANAGED_SKILL_NAMES` must change
  - `tests/unit/infra/test_init_update.py`
  - `tests/cli_runtime/harness.py` if expected skill list exists there
- Forbidden changes: runtime authoring command implementation, broad installer refactor, unrelated tests.
- Acceptance criteria: CLOS-001 through CLOS-009.
- Required tests or docs-only verification: focused pytest for managed skills/install_root; local wrapper path scan.
- Reviewer focus: code-reviewer checks installer impact; qa-reviewer checks test coverage and install simulation.
- Stop conditions: tests require broad fixture rewrite, network access, or non-hermetic behavior.
- Output required: changed files, tests run, before/after inventory evidence, risks.

Report evidence destination:

- Implementation Delegation Gate, Delegated Worker Evidence, Test Contract Closure, Closure Coverage.

Step gate:

- Do not proceed to final quality gate without a passing install verification.

具体テストケース一覧:

- `tc-s05-001` red/green: installed repo contains ChatGPT authoring skill
  - 前提: `spec-dock init` installs managed skills into a temp target.
  - 操作: Run the focused installer test or init simulation.
  - 期待結果: target contains `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`.
  - 失敗検出: provider file exists but consumer repo does not receive it.
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py -q -k "managed_skills or chatgpt_authoring"`.
  - 関連 closure id: CLOS-002.

- `tc-s05-002` negative: personal wrapper path is not shipped through changed formal surfaces
  - 前提: local ChatGPT Use wrapper exists on the operator machine.
  - 操作: scan the new ChatGPT authoring skill, changed shipped planning/hub skills, and touched regression tests that formalize this Issue's contract.
  - 期待結果: no `/Users/iwasawayuuta`, `.codex/skills/chatgpt-use`, or `oracle-chatgpt` formal dependency is found in changed shipped/formal surfaces.
  - 失敗検出: product workflow depends on the operator-local wrapper path.
  - 検証方法: the scoped `rg` command in S99 over changed formal skill/docs/test surfaces. Existing unrelated fixtures under broader `tests/` are not product workflow dependencies for this Issue.
  - 関連 closure id: CLOS-009.

### S90 executable contract: reviewer and docs impact resolution

Behavior goal:

- Confirm specs, installed assets, tests, and docs impact align before closeout.

Planned contract:

- Scope: read-only reviewer gates and report updates.
- Test obligation: manual-required reviewer evidence.
- Red or alternative evidence requirement: any prior reviewer fail remains blocking until fixed and re-reviewed.
- Green verification: fresh spec-reviewer, code-reviewer, and qa-reviewer pass.
- Refactor guardrail: reviewer-fail fixes must stay within approved allowed paths or return to planning.
- Amendment trigger: P0/P1/P2 findings that change scope, acceptance, or delegation contract require plan/report amendment and re-review.

Delegation contract:

- Delegated role: spec-reviewer, code-reviewer, qa-reviewer.
- Input docs: final diff, requirement/design/plan/report, changed files, verification output.
- Allowed paths: read-only.
- Forbidden changes: edits, waiver-as-pass, stale review reuse.
- Acceptance criteria: CLOS-013.
- Required tests or docs-only verification: reviewer result must include `review_status`.
- Reviewer focus: as defined in design section 9.
- Stop conditions: any reviewer returns fail, unavailable, denied, waived, or provisional.
- Output required: findings, `review_status`, confidence/risk notes.

Report evidence destination:

- Reviewer Gate Status, Final Quality Gate, Closure Coverage.

Step gate:

- Do not commit/finish until all required reviewer gates pass.

具体テストケース一覧:

- `tc-s90-001` manual-required: reviewer gates pass
  - 前提: implementation and verification evidence are available.
  - 操作: Run spec-reviewer, code-reviewer, and qa-reviewer.
  - 期待結果: all three return fresh `review_status: pass`.
  - 失敗検出: any non-pass, stale, unavailable, denied, waived, or provisional result.
  - 検証方法: reviewer outputs recorded in report.
  - 関連 closure id: CLOS-013.

### S99 executable contract: final local quality gate and relay closeout

Behavior goal:

- Close the intermediate Issue with verified local quality, commit/push, no per-Issue PR, and relay to next Issue.

Planned contract:

- Scope: final verification commands, report evidence, commit/push/finish lifecycle.
- Test obligation: manual-required command evidence.
- Red or alternative evidence requirement: not applicable; this is final closeout after implementation.
- Green verification: focused tests, `spec-dock validate`, `assurance verify`, `git diff --check`, local wrapper scan, git clean after commit, branch push, `issue finish`.
- Refactor guardrail: no new product changes during final closeout except reviewer-approved fixes.
- Amendment trigger: any final verification failure requiring product/spec change returns to the relevant step and re-review.

Delegation contract:

- Delegated role: spec-manager for lifecycle commands if needed; main orchestrator records report evidence.
- Input docs: all canonical docs, report, final diff, reviewer outputs.
- Allowed paths: `report.md` evidence updates and lifecycle commands.
- Forbidden changes: per-Issue PR creation, PR merge, GitHub issue close, unrelated cleanup.
- Acceptance criteria: CLOS-010 through CLOS-015.
- Required tests or docs-only verification: final command queue in section 4/S99.
- Reviewer focus: final spec/code/QA reviewer results must already be pass.
- Stop conditions: dirty worktree after final commit, push failure, `issue finish` failure, or missing no-PR relay evidence.
- Output required: commit hash, push evidence, issue finish output, next issue start evidence if performed.

Report evidence destination:

- Milestone / Commit Candidate Gate, No-PR Relay Policy, Final Quality Gate, Closure Coverage.

Step gate:

- Do not call `issue finish` until all closures are pass or approved-no-op.

具体テストケース一覧:

- `tc-s99-001` manual-required: final verification command queue
  - 前提: implementation and reviewer gates are complete.
  - 操作: run focused tests, `spec-dock validate`, `assurance verify`, `git diff --check`, and local wrapper scan.
  - 期待結果: all commands exit 0 or scan has no matches.
  - 失敗検出: any failed command or forbidden local wrapper path match.
  - 検証方法: command output recorded in report.
  - 関連 closure id: CLOS-010, CLOS-011, CLOS-012.

- `tc-s99-002` manual-required: deferred PR relay closeout
  - 前提: this is an intermediate Issue and PR delivery is assigned to `iss-00307`.
  - 操作: commit, push, record no-per-Issue-PR rationale, run `issue finish`.
  - 期待結果: branch is pushed, worktree is clean after commit, no PR is created, and active Issue advances per relay workflow.
  - 失敗検出: per-Issue PR is created or issue finishes without relay evidence.
  - 検証方法: git/spec-dock output and report evidence.
  - 関連 closure id: CLOS-014, CLOS-015.

## 7. Report Evidence Destinations

| Evidence type | Report section |
|---|---|
| draft adoption and ChatGPT Use attempt | Evidence Adoption Ledger |
| mode / naming decisions | Spec Interpretation / Decision Ledger |
| implementation delegation | Implementation Delegation Gate / Delegated Worker Evidence |
| test commands | Test Contract Closure / Closure Coverage |
| reviewer verdicts | Reviewer Gate Status |
| no-per-Issue-PR rationale | Final Quality Gate / Deferred PR delivery |
| commit and finish | Milestone / Commit Candidate Gate |

## 8. Final Exit Contract

`iss-00304` may finish only when:

- canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are substantive and current.
- fresh spec-reviewer pass confirms planning readiness.
- implementation is complete in provider-side installed assets and required tests.
- code-reviewer and qa-reviewer pass, or no code/test changes are made and the relevant reviewer gate records an approved no-op where workflow allows.
- CLOS-001 through CLOS-013 and CLOS-015 are satisfied. Only CLOS-014 PR delivery is intentionally deferred to `iss-00307`; all other required closures are non-deferrable for this Issue.
- no per-Issue PR has been created.
- branch is committed, pushed, and `issue finish` succeeds.

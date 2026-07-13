---
種別: 実装計画書（Issue候補）
ID: "iss-00313"
タイトル: "PR Merge Preparer Repair Continuation Policy 実装計画"
Issue Grade Candidate: "strict"
状態: "draft-candidate"
作成者: "ChatGPT 5.6 Pro"
最終更新: "2026-07-13"
関連Requirement: ["candidates/requirement.md"]
関連Design: ["candidates/design.md"]
親: ["epic-00158", "init-local-00003"]
authority: "evidence_only"
adoption_status: "unreviewed"
profile_authority: "recommendation_only"
source_manifest_hash: "5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d"
---

# iss-00313 PR Merge Preparer Repair Continuation Policy — 実装計画候補（Strict）

> このplanは、実装者が曖昧な設計判断を追加せずに進められる粒度のcandidate execution contractである。ただし、evidence-only / unreviewedであり、local integration decision、authorized profile、fresh reviewer approval、implementation handoff eligibility、pull-request handoff eligibility、pull-request handoffを意味しない。実行開始には、actual local branchでのEAL disposition、canonical authoring、assurance/profile gate、fresh spec reviewが別途必要である。

## 0. Plan の位置づけ

### 0.1 Plan owns

- dependency-resolved implementation sequence。
- step-local allowed / forbidden paths。
- Red/Green/Refactor expectations。
- concrete test cases and commands。
- delegation contracts and report evidence destinations。
- closure index、S90 impact resolution、strict review gate、S99 final gate、Final Exit Contract。
- stop / amendment / escalation conditions。

### 0.2 Plan does not own

- actual observed pass/fail result。
- commit SHA、push status、PR state。
- local integration decisionまたはreviewer verdict。
- `.assurance.json` mutation / authorized profile決定。
- GitHub mutation / pull-request handoff。

実施結果はcanonical `report.md` のobserved evidence ledgerに記録する。本candidate packはresultを先取りしない。

## 1. Plan Readiness and Pre-Execution Gates

### 1.1 Current candidate state

| Input | State | Evidence | Execution implication |
|---|---|---|---|
| GitHub repo access | available | connector inspection | source baseline usable |
| requested branch | not found on GitHub | branch search | local branch must be verified before adoption |
| fallback `main` | inspected | head `081ba648...` | remote baseline only |
| Issue #313 | open | GitHub issue | identity confirmed |
| local Issue docs | unverified | prompt metadata only | canonical diff unknown |
| local clarification artifacts | bodies unverified | filenames/hashes only | EAL disposition required |
| candidate requirement/design | generated here | evidence-only | not canonical |
| profile | strict recommended | risk analysis | not authorized |
| spec review | not run | none | blocks execution start |
| implementation/tests | not run | none | no result claim |

### 1.2 Mandatory gate before S01 is promoted from candidate to executable work

- [ ] requested local branch is opened and `git rev-parse HEAD` recorded。
- [ ] prompt-pack source hashes are recomputed or explicitly dispositioned as stale/current。
- [ ] listed local artifact bodies are read。
- [ ] `adoption/eal-candidates.json` entries receive explicit local disposition。
- [ ] mandatory consultation scope in local synthesis matches `ASSUMP-001`。
- [ ] main orchestrator writes/updates canonical Issue requirement/design/plan。
- [ ] actual assurance workflow selects/validates the profile; this pack does not do so。
- [ ] fresh spec-fresh reviewer approvales requirement and design, then plan, under repository workflow。
- [ ] working tree ownership and allowed paths are confirmed。

If any item fails, do not silently execute this plan. Update canonical specs or mark the pack stale.

### 1.3 No-blocking-question claim boundary

The candidate has no unresolved question that proves the Issue boundary unsafe. It does have adoption-verification gates. Those gates block execution but do not require Epic repair.

## 2. Implementation Strategy

### 2.1 Strategy

Use a contract-first vertical slice:

1. Bind exact current source and characterize old policy。
2. Add failing regression assertions for the target contract and forbidden old markers。
3. Replace the primary workflow contract in provider `SKILL.md` and align `openai.yaml`。
4. Update all three provider repair-batch templates in lockstep。
5. Refresh installed/dogfooding projections through the standard update path。
6. Run focused, static, integration, parity, validate/sync, and non-scope gates。
7. Perform fresh strict review and final closure audit。

### 2.2 TDD interpretation

This Issue is mostly Markdown/YAML contract work with Python regression assertions.

- Red is required where a generated/installed contract can be asserted before provider prose/template changes。
- A failing test must fail because the old fixed-limit contract remains or the new consultation/continuation contract is absent—not because of an invalid fixture or unrelated environment error。
- If an existing test already detects the contract and is Green before implementation, record a characterization/no-op rationale and add only the missing falsification sensitivity。
- Implementation steps must not weaken tests to obtain Green。

### 2.3 Smallest coherent change

The minimum coherent implementation includes all of:

- skill policy,
- agent prompt wording,
- skill-local batch template,
- artifact batch template,
- discussion batch template,
- generated/installed contract tests,
- provider/mirror verification.

Changing only the skill or only one template is incomplete and must not be committed as a finished behavior slice.

## 3. Change Surface

### 3.1 Allowed provider paths

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md
tests/cli_runtime/test_new.py
tests/cli_runtime/test_runtime_new_doc_s09.py
tests/cli_runtime/test_wrappers.py
```

### 3.2 Allowed generated/dogfooding changes after standard update

```text
.agents/skills/github-pr-merge-preparer/SKILL.md
.agents/skills/github-pr-merge-preparer/agents/openai.yaml
.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
spec-dock/templates/artifacts/pr-repair-batch.md
spec-dock/templates/discussions/pr-repair-batch.md
```

Generated path names must be confirmed from the actual update diff. Direct mirror-only edits are forbidden.

### 3.3 Forbidden paths / actions

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/**
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**
src/spec_dock/cli.py
.github/**
.assurance.json
unrelated Issue/Epic/Initiative canonical docs
```

Forbidden operations:

- merge / auto-merge / branch deletion。
- review comment reply / thread resolve / dismiss / admin override。
- GitHub issue close or `spec-dock issue finish`。
- secret/token/private data transmission。
- raw model conversation record inclusion。
- local integration decision or profile mutation from worker output。

### 3.4 Scope guard command

At every commit candidate and S99:

```bash
git diff --name-only -- \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  src/spec_dock/cli.py \
  .github
```

Expected: no output. Any output is a plan amendment trigger.

## 4. Milestones and Dependency Graph

### 4.1 Milestones

| Milestone | Steps | Outcome | Commit candidate |
|---|---|---|---|
| M0 Source binding | S01 | exact local baseline and old-policy inventory | no commit |
| M1 Contract Red | S02 | tests fail for intended missing new contract | `test(pr-repair): 継続契約の回帰テストを追加` |
| M2 Workflow Green | S03 | skill/prompt express evidence-gated continuation | combine with M3 if tests require atomicity |
| M3 Template Green | S04 | three provider templates record same contract | `feat(pr-repair): 証拠駆動の修復継続契約へ更新` |
| M4 Integration | S05 | generated/mirror output and focused suite pass | `test(pr-repair): 配布投影と互換性を固定` if separate |
| M90 Impact closure | S90 | docs/template/skill/mirror impact fully resolved | no separate commit unless required |
| M95 Strict reviews | S95 | fresh spec/code/QA findings dispositioned | fix commits as needed |
| M99 Final quality | S99 | closure index and full exit evidence collected | no new semantic change |

Commit messages are candidates only; actual commit boundaries must follow the local execution workflow.

### 4.2 Dependency graph

```text
S01 baseline/source binding
  -> S02 Red contract tests
     -> S03 skill + prompt contract
        -> S04 template contract
           -> S05 generated/mirror integration
              -> S90 impact resolution
                 -> S95 fresh strict reviews
                    -> S99 final quality and exit
```

No implementation step may skip its predecessor. S03 and S04 may be one atomic Green commit but must retain separate step evidence.

## 5. Acceptance Envelope

### 5.1 Positive contract markers

Implementation may choose equivalent headings, but tests must anchor stable semantic markers. Recommended markers:

- `Repair continuation and human-gate policy`
- `ChatGPT Consultation Gate`
- `Integrated Repair Strategy`
- `Repair Iteration Ledger`
- `strategy_delta`
- `consultation_status`
- `orchestrator disposition`
- `iteration count is telemetry` or equivalent
- `same root_cause_family recurrence` + `re-analysis` or equivalent
- `verbatim model conversation record` + prohibition

### 5.2 Forbidden old markers

At minimum:

- `Default autonomous repair limit: 1 repair attempt for P0`
- `Default autonomous repair limit for the same failure family: 2 attempts for P1`
- `Default total autonomous repair limit: 4 repair attempts per invocation`
- `Loop limits for the same failure class or total repair attempts are reached`
- wording where same `root_cause_family` recurrence alone requires stop

Use robust assertions that detect the semantic clause, not only exact punctuation.

### 5.3 Preserved markers

- P0/P1 blocking and P2/P3 non-blocking definitions。
- no P2/P3-only branch mutation。
- latest head / trigger freshness。
- permission/auth/external/flaky/base conflict/scope expansion/breaking/migration/secrets/deployment/ambiguous intent/platform-only human gates。
- forbidden merge/thread/issue actions。
- review-clean vs merge-prepared。
- required/non-required CI behavior。

## 6. Spec-Locked Closure Index

| Closure ID | Requirement / AC | Design | Implementation step | Verification | Evidence destination | Close condition |
|---|---|---|---|---|---|---|
| CLOS-001 | BH-001, AC-001, CON-007 | DES-001 | S02-S04 | forbidden-marker tests + inspection | report S02/S03/S04 | no numeric cap authority on any provider/generated surface |
| CLOS-002 | BH-005, AC-002 | DES-002 | S02-S04 | recurrence wording assertions | report S03/S04 | recurrence alone is not stop; re-analysis/delta required |
| CLOS-003 | BH-002/BH-003, AC-003 | DES-003 | S02-S04 | sequence/section assertions | report S03/S04 | integrated consultation precedes blocking repair delegation |
| CLOS-004 | AC-004, CON-012 | DES-003 | S03-S04 | freshness field/invalidator assertions | report S04 | consultation binds current material state |
| CLOS-005 | BH-004, AC-005, CON-001 | DES-004 | S03-S04 | disposition/authority negative assertions | report S03/S04 | no automatic adoption/authorization language |
| CLOS-006 | BH-006, AC-006 | DES-005/DES-006 | S03-S04 | continuation decision table/prose inspection | report S03/S04 | continue requires all semantic gates |
| CLOS-007 | AC-007 | DES-006 | S03-S04 | failed/unavailable/stale/unsafe states inspection | report S03/S04 | consultation non-pass states lead to human gate |
| CLOS-008 | BH-007, AC-008 | DES-006/DES-010 | S02-S05 | preserved-marker regression | report S05 | hard gates not weakened |
| CLOS-009 | BH-008, AC-009 | DES-007 | S02/S04 | generated template field assertions | report S04/S05 | batch has consultation/disposition/iteration evidence slots |
| CLOS-010 | AC-010 | DES-007 | S03-S05 | cross-file semantic matrix | report S05 | skill/prompt/templates agree |
| CLOS-011 | BH-009, AC-011/AC-012 | DES-008 | S02/S05 | temp generation, update, cmp, validate/sync | report S05/S90 | provider and projections match; metadata compatible |
| CLOS-012 | BH-010 | DES-009 | S02/S04/S05 | runtime-opaque/append compatibility test + inspection | report S05 | no runtime schema/migration; legacy content preserved |
| CLOS-013 | AC-013, CON-004/5/9/10 | DES-010 | S01/S05/S99 | diff guard + focused suite | report S99 | no out-of-scope implementation or policy change |
| CLOS-014 | AC-014 | plan sections | all/S90/S95/S99 | plan audit + fresh spec review | report planning/review gate | closure/delegation/tests/exit contract complete |
| CLOS-015 | CON-011 | DES security | S03-S05/S99 | unsafe-token/path scan | report S99 | no verbatim model conversation record/secrets/host paths in changed payloads |
| CLOS-016 | Issue boundary | DES boundary | S01/S90/S99 | changed-path and design-radius audit | report S90/S99 | one coherent workflow-contract slice remains |

No closure row may be marked complete from planned commands alone. Only observed evidence in the canonical report closes it.

## 7. Behavior Backlog

| Behavior ID | Description | Priority | Step | State at plan creation |
|---|---|---|---|---|
| B-001 | fixed numeric limits are not continuation authority | P0 | S02-S04 | planned |
| B-002 | same-family recurrence triggers re-analysis | P0 | S02-S04 | planned |
| B-003 | integrated ChatGPT consultation before blocking repair mutation | P0 | S02-S04 | planned |
| B-004 | consultation evidence-only + orchestrator disposition | P0 | S02-S04 | planned |
| B-005 | semantic continuation/human-gate decision | P0 | S03-S04 | planned |
| B-006 | hard gates and P2/P3 policy preserved | P0 | S02-S05 | planned |
| B-007 | batch audit ledger supports consultation and strategy delta | P1 | S02/S04 | planned |
| B-008 | generated/provider/mirror parity | P1 | S05/S90 | planned |
| B-009 | legacy batch/runtime compatibility | P1 | S02/S05 | planned |
| B-010 | strict closure/review/final gates | P1 | S90/S95/S99 | planned |

## 8. Active Behavior and TDD Cycle

Initial active behavior after gates pass:

- Active behavior: `B-001 + B-003 + B-007` as the first testable contract slice。
- Red target: generated/installed repair-batch content lacks consultation/strategy fields and still contains old limit semantics。
- Green target: provider skill/templates express new contract; generated output and installed projection satisfy tests。
- Refactor target: remove duplicated assertion helpers only after Green; do not generalize a cross-skill framework。

TDD cycle rule:

```text
one contract assertion set
  -> prove intended Red
  -> smallest provider change
  -> focused Green
  -> inspect semantic preservation
  -> record evidence
  -> next behavior
```

## 9. Detailed Execution Steps

# S01 — Local Source Binding and Characterization

### S01 Goal

Bind this candidate to the actual local branch and characterize every current fixed-limit / recurrence-stop clause before edits.

### Dependency

- Depends on: adoption/pre-execution gates in section 1。
- Unblocks: S02。

### Allowed actions

- read-only repository inspection。
- source hash calculation。
- baseline focused tests。
- report evidence entry preparation。

### Forbidden actions

- provider or mirror edits。
- canonical spec mutation by a delegated worker。
- `.assurance.json` mutation。

### Delegation contract

| Field | Contract |
|---|---|
| delegated role | main orchestrator; optional read-only explorer |
| objective | bind exact source and enumerate old semantics |
| allowed paths | repository read-only |
| forbidden paths | all writes |
| required inputs | canonical local Issue docs, prompt-pack manifest, provider/mirror files |
| required output | source-binding table, old-marker inventory, branch/head/status, mismatch list |
| validation | commands below; hashes/path existence |
| stop conditions | requested local branch absent locally; source manifest mismatch without disposition; local synthesis contradicts candidate scope |
| evidence destination | canonical `report.md` planning/preflight section and EAL |

### S01 Commands

```bash
git status --short --branch
git rev-parse HEAD
git branch --show-current

python - <<'PY'
from hashlib import sha256
from pathlib import Path
paths = [
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md"),
    Path("tests/cli_runtime/test_new.py"),
    Path("tests/cli_runtime/test_runtime_new_doc_s09.py"),
    Path("tests/cli_runtime/test_wrappers.py"),
]
for path in paths:
    data = path.read_bytes()
    print(sha256(data).hexdigest(), path.as_posix())
PY

rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Fix loop limits|Loop limits|root_cause_family.*repair commit" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md

uv run pytest -q \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_artifact_full_direct_catalog_success \
  tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_doc_type_parity_template_selection_regression \
  tests/cli_runtime/test_wrappers.py::TestCliRulesContract::test_scaffold_docs_point_to_runtime_commands_and_rules_docs
```

### Concrete test cases

#### TC-S01-001 Source manifest binding

- Objective: detect local drift from prompt-pack snapshot。
- Preconditions: local target branch checked out。
- Action: hash the 8 planned source files。
- Assertions:
  - all files exist and are regular files。
  - hash differences are explicitly classified as expected local context, stale pack, or blocker。
- Falsification sensitivity: fails on missing/renamed/unreadable file or unexplained hash mismatch。
- Evidence destination: report source-binding table。

#### TC-S01-002 Old-policy inventory

- Objective: ensure no fixed-limit clause is missed。
- Action: `rg` provider skill and templates。
- Assertions: each known cap/recurrence stop location is listed with path/line and target replacement step。
- Falsification sensitivity: inventory incomplete if later S99 finds another old marker。
- Evidence destination: report decision ledger + S01 evidence。

#### TC-S01-003 Baseline behavior

- Objective: prove current generation/type/scaffold tests are Green before new contract tests。
- Action: run three focused existing tests。
- Expected: pass, or pre-existing failure classified before edits。
- Falsification sensitivity: any failure prevents interpreting S02 Red correctly。

### S01 Exit gate

- exact branch/head/status recorded。
- actual local artifact bodies reviewed and EAL disposition updated。
- target path/hash matrix complete。
- old policy inventory complete。
- baseline failures none or explicitly resolved outside implementation diff。
- Issue boundary still coherent。

If not, stop and amend canonical specs; do not proceed to S02.

---

# S02 — Red Contract Tests

### S02 Goal

Add tests that fail against the current fixed-limit contract for the intended reasons and preserve existing path/front-matter/runtime behavior.

### Dependency

- Depends on: S01 exit gate。
- Unblocks: S03 and S04。

### Allowed paths

```text
tests/cli_runtime/test_new.py
tests/cli_runtime/test_runtime_new_doc_s09.py
tests/cli_runtime/test_wrappers.py
```

### Forbidden paths

All provider production/asset files in this step.

### Delegation contract

| Field | Contract |
|---|---|
| delegated role | `dev-coder` |
| objective | add sensitive contract tests without changing provider assets |
| allowed paths | three test files only |
| forbidden paths | all `src/**`, `.agents/**`, `spec-dock/**`, specs, assurance |
| required inputs | requirement AC-001..AC-013, design DES-001..DES-010, S01 marker inventory |
| required output | focused tests with positive, negative, preservation, and runtime-opaque assertions |
| test requirement | demonstrate intended Red before Green changes |
| stop conditions | Red caused by fixture/environment error; runtime change appears necessary; existing test naming/location differs materially |
| report destination | S02 Red/Green evidence table; worker output remains evidence until verified |

### Planned tests

#### 1. `test_new.py`

Add a dedicated test, candidate name:

```python
def test_new_artifact_pr_repair_batch_uses_evidence_gated_continuation_contract(self) -> None:
    ...
```

Test behavior:

- init temp repository and create linked issue hierarchy。
- create `pr-repair-batch` artifact through supported CLI path。
- assert existing filename/front matter/type/title/parent/date behavior。
- assert positive semantic markers: consultation gate, integrated strategy, iteration ledger, strategy delta, disposition, telemetry-only count。
- assert forbidden fixed-limit markers absent。
- assert verbatim model conversation record inclusion is prohibited。

#### 2. `test_runtime_new_doc_s09.py`

Add/extend a test, candidate name:

```python
def test_pr_repair_batch_continuation_fields_remain_markdown_only_and_runtime_opaque(self) -> None:
    ...
```

Test behavior:

- provide a template containing new consultation/continuation sections。
- use existing create-discussion/artifact path without adding request fields or parser options。
- assert rendered content preserves the fields。
- assert ID/path/type behavior remains unchanged。
- this proves no runtime schema is needed。

#### 3. `test_wrappers.py`

Add a provider-to-installed projection test, candidate name:

```python
def test_scaffolded_pr_merge_preparer_uses_evidence_gated_repair_continuation_policy(self) -> None:
    ...
```

Test behavior:

- init a temp target from current provider checkout。
- read installed `.agents/.../SKILL.md`, installed skill-local template, and `spec-dock/templates/{artifacts,discussions}/pr-repair-batch.md`。
- assert positive markers and forbidden old markers。
- assert artifact/discussion templates are byte-identical if that is the current provider invariant。
- assert no new runtime option is exposed。

### Concrete test cases

#### TC-S02-001 Generated positive contract

- Precondition: current provider still old。
- Action: generated batch content assertions。
- Expected Red: missing consultation/strategy/telemetry markers。
- Must not fail because: CLI setup, GitHub stub, timestamp, path fixture。

#### TC-S02-002 Generated negative contract

- Action: assert old cap markers absent。
- Expected Red: at least one old marker present in generated template。
- Falsification sensitivity: each known marker is independently checked or normalized into a forbidden list。

#### TC-S02-003 Preservation

- Action: assert filename, ID, parent, title, date, artifact type。
- Expected before/after: Green in both states。
- Purpose: detect accidental public contract drift during Green。

#### TC-S02-004 Runtime opacity

- Action: render template with new Markdown fields through existing runtime path。
- Expected: content preserved without new command/request/schema fields。
- Red policy: may be Green as characterization; record no-op if already supported。

#### TC-S02-005 Installed projection

- Action: init temp target and inspect installed skill/templates。
- Expected Red: old policy / missing new fields。
- Falsification sensitivity: reads actual target files, not provider files by mistake。

#### TC-S02-006 Preserved hard gates

- Action: assertions for permission/auth, external/flaky, scope expansion, breaking/migration/secret/deployment, P2/P3 no-mutation, forbidden GitHub actions。
- Expected: Green before and after。
- Purpose: stop over-broad rewrite。

### S02 Commands

Run new focused tests by exact node IDs after implementation chooses names:

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test> \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>
```

Then record:

- failing assertion(s),
- why they map to CLOS-001/003/009/011,
- confirmation that preservation/hard-gate assertions are not the source of failure。

### S02 Exit gate

- intended Red observed for missing new contract / old fixed-limit markers。
- no provider asset changed。
- no unrelated baseline regression。
- tests have explicit positive + negative + preservation sensitivity。

---

# S03 — Provider Skill and Agent Prompt Contract

### S03 Goal

Replace count-based fix-loop policy in the primary workflow authority and align the agent invocation prompt.

### Dependency

- Depends on: S02 intended Red。
- May proceed in parallel with S04 only if one worker owns no overlapping files and final Green is integrated after both。

### Allowed paths

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml
```

### Forbidden paths

- templates, tests, mirror files in this step。
- observation skill/runtime/GitHub workflows。

### Delegation contract

| Field | Contract |
|---|---|
| delegated role | `doc-writer` |
| objective | rewrite the workflow spine without authority or scope expansion |
| allowed paths | two provider files above |
| forbidden paths | all other paths |
| required inputs | DES-001..DES-006, hard-gate inventory, S02 tests |
| required output | concise first-read policy, consultation sequence, recurrence/strategy semantics, aligned prompt |
| mandatory preservation | P2/P3 policy, hard gates, forbidden writes/actions, merge-prepared/human merge boundary |
| stop conditions | exact consultation scope cannot be reconciled with local synthesis; wording implies auto-adoption; runtime automation is proposed |
| evidence destination | report S03 diff summary, test output, decision ledger |

### Implementation contract

#### Skill changes

- Rename/remove `Fix loop limits` section。
- Remove numeric P0/P1/total cap clauses。
- State iteration index/count is telemetry only。
- Add integrated blocking batch consultation sequence before repair delegation。
- Define consultation status/freshness non-pass states。
- Define ChatGPT as evidence-only; main orchestrator disposition owner。
- Define recurrence categories or equivalent analysis requirements。
- Define materially distinct bounded strategy requirement。
- Define semantic human gate conditions。
- Preserve all existing hard gate and forbidden action categories。
- Update response checklist to report consultation/disposition/continuation evidence without claiming authorization。

#### `openai.yaml` changes

- Replace ambiguous count-bounded wording。
- Keep prompt concise and subordinate to `SKILL.md`。
- Mention integrated batch, evidence-gated repair, re-observation, human merge judgment。
- Do not claim automatic ChatGPT execution if the skill workflow relies on host capability; describe required consultation outcome, not runtime implementation。

### Concrete test cases

#### TC-S03-001 Numeric caps absent

- Action: run focused skill/prompt assertions and `rg` forbidden markers。
- Expected: no count-based authority phrase。

#### TC-S03-002 Consultation sequence present

- Action: inspect workflow order。
- Expected order: observation -> triage -> integrated consultation -> disposition -> worker -> push -> re-observe。

#### TC-S03-003 Authority boundary

- Action: inspect terms around ChatGPT。
- Expected: evidence/advisory; no authorize/adopt/pass/merge-ready authority。

#### TC-S03-004 Recurrence semantics

- Action: inspect same-family wording。
- Expected: re-analysis and strategy delta; no automatic stop solely due to recurrence。

#### TC-S03-005 Hard gates preserved

- Action: run preservation test list。
- Expected: all existing safety categories and forbidden actions remain。

### S03 Focused commands

```bash
uv run pytest -q \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>

rg -n \
  "Repair continuation|ChatGPT|consultation|strategy|root_cause_family|human gate|telemetry" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml

if rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Loop limits.*repair attempts" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer; then
  echo "obsolete fixed-limit contract remains" >&2
  exit 1
fi
```

The installed-projection test may remain Red until S05 update. In S03, provider-content assertions must be Green; distinguish expected mirror Red from provider failure in evidence.

### S03 Exit gate

- primary workflow contract is complete and first-read executable。
- prompt aligns without duplicating full policy。
- no old numeric authority remains in these two files。
- hard gates and forbidden actions preserved。
- no authority escalation language。

---

# S04 — Repair Batch Templates Contract

### S04 Goal

Update all provider repair-batch templates to record integrated strategy, consultation evidence, orchestrator disposition, recurrence analysis, and semantic continuation without numeric limits.

### Dependency

- Depends on: S02 Red and DES-007 fields。
- Must integrate with S03 before full Green。

### Allowed paths

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md
```

### Forbidden paths

All other paths, including mirrors.

### Delegation contract

| Field | Contract |
|---|---|
| delegated role | `doc-writer` |
| objective | implement the evidence worksheet without changing runtime/front matter semantics |
| allowed paths | three provider templates |
| forbidden paths | skill, prompt, tests, runtime, mirrors |
| required inputs | DES-007, template current sections, S02 generated test expectations |
| required output | synchronized templates with new fields and semantic stop conditions |
| compatibility | preserve placeholders/front matter/type/parent/date; no new runtime placeholder requirement unless existing renderer supports it |
| stop conditions | template needs parser/schema change; artifact/discussion templates cannot remain compatible; verbatim model conversation record field requested |
| evidence destination | report S04 diff/test/compatibility table |

### Implementation contract

#### Required section semantics

- preserve metadata, purpose, concern catalog, inventory, per-concern analysis, repair queue/unit plan, merge-prepared gate。
- add/rename sections for:
  - root-cause family/coupling analysis,
  - integrated repair strategy,
  - ChatGPT consultation gate,
  - orchestrator disposition,
  - repair iteration ledger,
  - semantic stop/human-gate conditions。

#### Iteration ledger

Include at least:

- iteration index (telemetry only),
- head SHA / observation status,
- family IDs / recurrence class,
- prior/proposed strategy IDs,
- material strategy delta,
- consultation ID/status/freshness,
- orchestrator disposition,
- action / fix commit,
- re-observation result,
- continuation decision / semantic stop reason。

#### Consultation section

Include:

- required/not-required and why,
- fresh/stale/failed/unavailable/denied/unsafe status,
- current evidence bindings,
- sanitized input summary reference,
- recommendation summary reference,
- open risks,
- disposition summary,
- verbatim model conversation record/secret/absolute-path prohibition。

#### Stop conditions

Remove:

- numeric limit reached。
- same family reappeared as a sufficient stop。

Add/preserve:

- no materially distinct bounded strategy。
- same ineffective strategy repeated。
- stale/incomplete observation。
- consultation non-pass state。
- hard safety categories。
- scope/requirement expansion。
- unapproved trigger/resume metadata failure。

### Template consistency rule

- artifact and discussion provider templates are expected to remain byte-identical unless S01 proves a documented intentional difference。
- skill-local template may contain more operational detail but must not contradict the two shipped templates。
- exact headings can vary only if tests and all required semantic fields remain stable。

### Concrete test cases

#### TC-S04-001 Required fields

- Action: generated template and provider text assertions。
- Expected: all consultation/strategy/ledger fields present。

#### TC-S04-002 Old stop semantics absent

- Action: forbidden marker scan across all three templates。
- Expected: no numeric/same-recurrence-only stop authority。

#### TC-S04-003 Artifact/discussion parity

- Action: `cmp -s` provider artifact and discussion templates。
- Expected: equal unless a reviewed exception is documented。

#### TC-S04-004 Runtime compatibility

- Action: runtime-opaque focused test。
- Expected: existing renderer handles new Markdown body with no parser/request changes。

#### TC-S04-005 Safe output

- Action: scan for verbatim model conversation record instruction, secret/token placeholder, absolute host path examples。
- Expected: only prohibition/metadata references; no unsafe payload slot。

### S04 Commands

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test>

cmp -s \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md

rg -n \
  "ChatGPT Consultation|Integrated Repair Strategy|strategy_delta|consultation_status|orchestrator|iteration|human gate" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md

if rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Loop limits.*repair attempts" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md; then
  echo "obsolete fixed-limit template contract remains" >&2
  exit 1
fi
```

### S04 Exit gate

- all three provider templates satisfy positive/negative tests。
- artifact/discussion parity resolved。
- runtime opacity/metadata compatibility preserved。
- no unsafe output slot。
- integrated S03+S04 focused contract tests are Green on provider sources。

---

# S05 — Provider-to-Dogfooding Integration and Compatibility

### S05 Goal

Refresh generated/installed projections through the standard current-checkout update path, verify provider parity, run focused regression/static checks, and prove non-scope surfaces remain unchanged.

### Dependency

- Depends on: S03 and S04 exit gates。
- Unblocks: S90。

### Allowed paths

- three test files for integration fixes only。
- provider files from S03/S04 for defects found by tests。
- generated/dogfooding projection paths produced by the standard update command。

### Forbidden actions

- hand-edit mirrors to make tests pass。
- introduce runtime or observation changes。
- overwrite user-authored `spec-dock/initiatives/**` content。

### Delegation contract

| Field | Contract |
|---|---|
| delegated role | `dev-coder` |
| objective | execute update/parity/test integration and make only contract-preserving fixes |
| allowed paths | test files, S03/S04 provider files, generated projection from standard update |
| forbidden paths | runtime/observation/GitHub mutation/spec authority |
| required inputs | all prior step evidence, provider change list, current checkout update command |
| required output | update log, projection diff, focused/full target tests, static results, parity matrix |
| stop conditions | update touches unrelated user-authored data; projection requires hand edit; runtime change needed; broad unrelated failures |
| evidence destination | report S05 integration ledger |

### Standard update

Use the current checkout as provider:

```bash
uvx --from . spec-dock update .
```

If repository policy requires the installed command instead, record the reason and exact command; do not silently switch provider source.

### Projection parity checks

```bash
cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md \
  .agents/skills/github-pr-merge-preparer/SKILL.md

cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml \
  .agents/skills/github-pr-merge-preparer/agents/openai.yaml

cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md \
  .agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md

cmp -s \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  spec-dock/templates/artifacts/pr-repair-batch.md

cmp -s \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md \
  spec-dock/templates/discussions/pr-repair-batch.md
```

If a target path differs in the actual install layout, update the path only after documenting the repository evidence; do not weaken parity.

### Focused tests

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test> \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>

uv run pytest -q \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_artifact_full_direct_catalog_success \
  tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_doc_type_parity_template_selection_regression \
  tests/cli_runtime/test_wrappers.py::TestCliRulesContract::test_scaffold_docs_point_to_runtime_commands_and_rules_docs
```

### Target file suites

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

### Static checks for changed Python tests

```bash
uv run ruff format --check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py

uv run ruff check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py

uv run mypy \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

### Concrete test cases

#### TC-S05-001 Update preservation

- Preconditions: snapshot user-authored active Issue paths and hashes where safe。
- Action: run current-checkout update。
- Assertions:
  - intended mirrors updated。
  - user-authored Issue/artifact content not rewritten/deleted。
  - no unexpected path proliferation。
- Falsification sensitivity: compare pre/post inventory and git diff。

#### TC-S05-002 Provider/mirror parity

- Action: all `cmp -s` checks。
- Expected: zero status。
- Failure: inspect update/provider authority; never patch mirror only。

#### TC-S05-003 Full target regression

- Action: run three full test modules。
- Expected: all pass with no newly skipped contract tests。

#### TC-S05-004 Static quality

- Action: ruff format/check and mypy on changed tests。
- Expected: pass, or repository-documented no-op reason if no Python diff in a listed file。

#### TC-S05-005 Non-scope diff

- Action: scope guard and `git diff --stat`/`--name-only`。
- Expected: only allowed provider/test/generated paths plus canonical issue docs owned by main orchestrator。

#### TC-S05-006 Safe payload scan

- Action: scan changed Markdown/YAML for host absolute paths, authentication material placeholders that invite values, verbatim model conversation record inclusion, forbidden authority claims。
- Expected: none except explicit prohibitions/explanations。

Suggested scan:

```bash
python - <<'PY'
from pathlib import Path
import re
paths = [
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md"),
]
unsafe = {
    "raw_transcript_slot": re.compile(r"(?i)(paste|attach|include).*verbatim model conversation record"),
    "authority_claim": re.compile(r"(?i)(chatgpt).*(authoriz|approve|fresh reviewer approval|merge-ready)"),
}
failures = []
for path in paths:
    text = path.read_text(encoding="utf-8")
    for code_span in re.findall(r"`([^`]+)`", text):
        if code_span.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", code_span):
            failures.append((path.as_posix(), 0, "host_absolute_path", code_span))
    for name, pattern in unsafe.items():
        for match in pattern.finditer(text):
            # Explicit prohibition text must be manually dispositioned rather than blindly failed.
            line = text.count("\n", 0, match.start()) + 1
            failures.append((path.as_posix(), line, name, match.group(0)))
for row in failures:
    print(*row, sep=":")
PY
```

Manual disposition is required because prohibition statements may match. No actual unsafe example/value may remain.

### S05 Exit gate

- standard update completed without user-data damage。
- provider/mirror parity passes。
- focused and full target test modules pass。
- static checks pass or valid no-op evidence exists。
- no out-of-scope diff。
- all CLOS-001..CLOS-013 have implementation/test evidence candidates ready for report verification。

---

# S90 — Documentation, Skill, Template, and Mirror Impact Resolution

### S90 Goal

Resolve every impact surface before strict review. S90 is not a generic docs cleanup; it proves that the durable policy lives in the correct owner and no stale duplicate remains.

### Dependency

- Depends on: S05 exit gate。
- Unblocks: S95。

### Delegation contract

| Field | Contract |
|---|---|
| delegated role | `docs-researcher` or main orchestrator read-only audit |
| objective | inventory all references to old limits and verify owner/mirror placement |
| allowed paths | repository read-only; edits require plan amendment unless within established provider surfaces |
| forbidden paths | unrelated docs rewrite |
| required output | impact matrix: skill/docs/templates/tests/mirrors, old-marker search, no-op rationale per untouched surface |
| stop conditions | durable old policy exists outside planned files; general docs authority must change; cross-skill policy discovered |
| evidence destination | report S90 impact table |

### S90 Checks

```bash
rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Fix loop limits|Loop limits.*repair attempts|root_cause_family.*repair commit" \
  src .agents spec-dock tests \
  --glob '!spec-dock/initiatives/**/artifacts/**' \
  --glob '!spec-dock/initiatives/**/discussions/**' \
  --glob '!spec-dock/initiatives/**/report.md'
```

Historical evidence may legitimately retain old wording. Current authority/projection files may not.

Run:

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

Then inspect:

- skill owns full operational policy。
- templates contain evidence slots and do not contradict skill。
- no general docs duplication is required。
- `openai.yaml` remains concise。
- provider/dogfooding path parity is current。
- canonical Issue report has EAL and planned/observed separation after actual adoption。

### S90 Decision matrix

| Surface | Expected disposition |
|---|---|
| `github-pr-merge-preparer/SKILL.md` | changed; workflow authority |
| `openai.yaml` | changed; concise prompt alignment |
| skill-local template | changed; full operational worksheet |
| artifact/discussion templates | changed; generated evidence slots |
| `github-pr-observation` | no change; collection-only preserved |
| general workflow docs | no change unless S90 finds active contradictory authority |
| runtime CLI/docs | no change |
| historical Issue artifacts | no rewrite |
| dogfooding copies | generated refresh + parity |

### S90 Exit gate

- no active stale fixed-limit authority remains。
- every affected/untouched surface has a reason。
- validate/sync pass observed。
- no new cross-Issue/Epic policy requirement surfaced。
- if one surfaced, stop and amend/split before S95。

---

# S95 — Strict Review Gates

### S95 Goal

Obtain fresh, independent review of the full candidate-to-implementation story and disposition every finding without claiming pass in advance.

### Dependency

- Depends on: S90 exit gate。
- Unblocks: S99 only after all blocking findings are resolved and re-reviewed。

### Review contracts

#### S95-A Fresh spec review

| Field | Contract |
|---|---|
| role | `spec-reviewer` |
| mode | read-only, fresh context |
| inputs | canonical requirement/design/plan/report, parent Epic, actual diff, test plan/evidence |
| focus | Issue boundary, authority, consultation scope, semantic termination, AC/DES/closure trace, strict plan completeness |
| forbidden | editing files or treating this pack as canonical |
| output | verdict + severity findings + evidence references |
| gate | fresh pass required by repository workflow; non-pass is blocking |

#### S95-B Code/test review

| Field | Contract |
|---|---|
| role | `code-reviewer` |
| mode | read-only |
| inputs | provider/test/generated diff and test output |
| focus | test sensitivity, provider/mirror authority, no runtime drift, maintainability, accidental weakening |
| output | findings by severity and exact path/line |
| gate | P0/P1 resolved; P2/P3 dispositioned under repository policy |

#### S95-C QA/contract review

| Field | Contract |
|---|---|
| role | `qa-reviewer` |
| focus | generated artifact, legacy compatibility, negative markers, hard gate preservation, safe output |
| output | scenario matrix and gaps |
| gate | blocking scenario gaps resolved |

### Finding handling

- do not repair raw findings ad hoc。
- inventory findings and group by root cause。
- if changes are branch-mutating blocking repair during pull-request handoff, the newly defined merge-preparer consultation policy applies at that phase。
- planning/spec findings are dispositioned in canonical decision/EAL ledgers。
- any requirement/design change returns to the appropriate phase and invalidates stale downstream review。

### S95 Exit gate

- fresh spec review state satisfies repository promotion rules。
- code/QA blocking findings resolved and re-reviewed。
- no unresolved `needs-human` or scope-expansion finding。
- report records reviewer evidence without overclaiming。

---

# S99 — Final Quality and Closure Audit

### S99 Goal

Run the final verification ladder on the final diff, reconcile closure/index/evidence, and produce an explicit exit decision for human judgment.

### Dependency

- Depends on: S95 exit gate。

### S99 Commands

#### 1. Focused contract tests

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test> \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>
```

#### 2. Full target modules

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

#### 3. Runtime regression lane or justified broader baseline

```bash
uv run pytest tests/cli_runtime
```

If full runtime lane is infeasible due a verified unrelated pre-existing failure, record exact failure, source evidence, and why targeted closure remains valid; do not call the gate passed without repository-approved disposition.

#### 4. Static checks

```bash
uv run ruff format --check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py

uv run ruff check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py

uv run mypy \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

#### 5. Dogfooding gates

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

#### 6. Provider/mirror parity

Repeat all S05 `cmp -s` checks after final fixes.

#### 7. Forbidden marker / preserved marker audit

```bash
if rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Loop limits.*repair attempts" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md \
  .agents/skills/github-pr-merge-preparer \
  spec-dock/templates/artifacts/pr-repair-batch.md \
  spec-dock/templates/discussions/pr-repair-batch.md; then
  echo "obsolete fixed-limit contract remains" >&2
  exit 1
fi

rg -n \
  "ChatGPT Consultation|Integrated Repair Strategy|strategy_delta|consultation_status|orchestrator|telemetry|human gate" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md
```

#### 8. Diff hygiene and scope

```bash
git diff --check
git status --short --branch
git diff --stat
git diff --name-only
```

Review every changed path against section 3.

### S99 Closure audit

For each `CLOS-*` row:

- planned test/inspection exists。
- observed result is in report。
- source/diff/test/reviewer evidence agrees。
- no stale review after a later change。
- no unresolved blocker or unreviewed plan amendment。

### S99 No-op rule

If implementation discovers current local branch already satisfies part/all of this design:

- do not manufacture a semantic diff。
- strengthen only missing regression sensitivity。
- record no-op evidence and exact current source。
- still execute compatibility, authority, mirror, review, and final gates。

### S99 Exit gate

- all required tests/static/validate/sync/parity/diff checks have observed disposition。
- all closure entries resolved or explicitly blocked; none silently omitted。
- final report separates planned vs observed evidence。
- no forbidden authority claim。
- no GitHub mutation beyond the user-approved external delivery workflow。

## 10. Verification Ladder

Run from narrowest to broadest; a failed lower rung blocks higher-rung success claims.

| Rung | Scope | Examples | Purpose |
|---|---|---|---|
| V0 | source binding | hash/path/old-marker inventory | stale-context defense |
| V1 | single test | each new test node | fast Red/Green |
| V2 | focused contract set | three new tests + existing neighbors | cross-surface behavior |
| V3 | target modules | three full files | regression in affected lane |
| V4 | static | ruff/mypy | test code quality |
| V5 | projection | update + cmp | provider/mirror parity |
| V6 | dogfooding | validate/sync | workspace consistency |
| V7 | broader runtime lane | `pytest tests/cli_runtime` | adjacent regression |
| V8 | review | spec/code/QA | semantic and implementation audit |
| V9 | final diff/closure | S99 | complete story |

## 11. Contract, Compatibility, Recovery, and Rollback Gates

### 11.1 Contract gate

Pass candidate only if:

- numeric attempt authority absent everywhere current。
- consultation / disposition / strategy delta present and coherent。
- recurrence alone not automatic stop。
- hard gates preserved。
- ChatGPT authority remains evidence-only。

### 11.2 Compatibility gate

- no CLI option/parser/schema change。
- generated filename/front matter/type unchanged。
- old batches remain readable。
- new fields are Markdown-only and append-compatible。
- no user-authored content overwritten by update。

### 11.3 Recovery gate

Skill/templates must explicitly handle:

- stale observation -> reobserve。
- stale consultation -> refresh。
- unavailable/failed/denied/unsafe consultation -> human gate。
- no strategy delta -> human gate。
- scope expansion -> amendment/human gate。

### 11.4 Rollback gate

Before final closure, confirm:

- provider changes can be reverted without migration。
- update restores mirrors from provider。
- historical batches do not need deletion/rewrite。
- no new persistent state exists。

## 12. Delegation Policy

### 12.1 General rules

- main orchestrator retains canonical docs, EAL, scope decisions, and final integration ownership。
- workers receive one bounded step with explicit allowed paths and tests。
- worker output is evidence, not accepted implementation until diff/test inspection。
- no worker may mutate `.assurance.json`, GitHub review state, merge state, issue lifecycle, or canonical authority independently。
- parallel delegation allowed only for S03/S04 non-overlapping paths and only after S02 Red; integration remains serial。

### 12.2 Worker handoff minimum fields

Every delegated task must include:

- Issue/step/closure IDs。
- objective and non-objectives。
- exact allowed/forbidden paths。
- source contracts/IDs。
- expected Red/Green behavior。
- exact test commands or placeholders resolved before execution。
- required output: diff summary, tests, uncertainties, no-op evidence。
- stop/escalation conditions。
- report evidence destination。

### 12.3 Worker acceptance checklist

- [ ] changed only allowed paths。
- [ ] did not reinterpret scope/requirements。
- [ ] showed intended test evidence。
- [ ] did not weaken assertions。
- [ ] disclosed uncertainties/no-op/limitations。
- [ ] no authority/GitHub/assurance mutation。

## 13. Report Evidence Mapping

After local integration decision, `report.md` should receive observed evidence in these slots.

| Report section | Required observed evidence |
|---|---|
| Source binding | branch/head/status, file hashes, prompt-pack freshness |
| Decision ledger | local synthesis interpretation, consultation scope, any plan amendment |
| EAL | each research/interview/ChatGPT/synthesis disposition |
| S01 | baseline tests and old-marker inventory |
| S02 | intended Red and falsification explanation |
| S03 | skill/prompt diff, provider-focused Green, preserved hard gates |
| S04 | template diff, generated Green, parity/safe-output evidence |
| S05 | update log, provider/mirror cmp, target tests, static checks, scope diff |
| S90 | impact matrix, validate/sync, no stale authority |
| S95 | reviewer verdicts/findings/fixes/re-review |
| S99 | final commands, dirty-tree scope, closure matrix, residual risks |
| Rollback | tested/inspected rollback path and no migration |

Raw worker notes, raw model conversation record, secrets, or host-local paths must not be pasted into report.

## 14. Plan Amendment and Stop Rules

### 14.1 Mandatory plan amendment

Stop current step and update requirement/design/plan if:

- local adopted synthesis defines a different mandatory consultation boundary。
- runtime/CLI/schema/observation change is needed。
- new public template/front matter/filename behavior is required。
- P2/P3 or hard gate policy must change。
- active old-limit authority exists in an unplanned durable surface。
- historical batch migration is necessary。
- cross-skill policy is required。
- security/privacy impact changes from guarded/no to true/unknown。

### 14.2 Immediate human gate

- secret/authentication material/private data required for consultation。
- consultation unavailable/failed/denied/unsafe with blocking mutation pending。
- ambiguous/conflicting requirements or review intent。
- GitHub mutation outside current authority。
- destructive or rollback-unsafe change。
- same ineffective strategy proposed without material delta。
- worker modifies forbidden path or canonical authority。

### 14.3 Stale-plan triggers

- requested branch or main changes materially from bound head。
- source-manifest hash changes。
- target file hashes change outside this execution。
- parent Epic or repository authority rules change。
- local artifact bodies invalidate assumptions。
- reviewer changes requirement/design after plan review。

## 15. Final Quality Gate

The final quality gate is not satisfied by tests alone. It requires:

1. requirement/design/plan traceability complete。
2. all CLOS entries with observed evidence。
3. fresh review status under repository workflow。
4. provider/mirror/generated contract parity。
5. no old fixed-limit authority。
6. no weakened hard gate or P2/P3 policy。
7. no runtime/observation/GitHub/assurance scope expansion。
8. safe output and no verbatim model conversation record/secrets/host paths。
9. compatibility/rollback/no-migration evidence。
10. final diff and dirty-tree scope understood。

## 16. Final Exit Contract

### 16.1 Candidate success outcome

After downstream execution and review, the human/orchestrator may conclude implementation closure only when all of the following are observed:

- fixed numeric attempt caps are removed from current authority and projections。
- recurrence is a re-analysis trigger, not an automatic stop。
- mandatory integrated consultation and evidence-only disposition are explicit。
- semantic continuation/human-gate policy is complete and safe。
- batch templates are auditable and compatible。
- targeted/broader/static/dogfooding/parity gates have accepted results。
- fresh reviews have accepted results under repository workflow。
- no forbidden action or authority escalation occurred。
- report contains complete observed evidence and residual risk。

This outcome still does not itself merge the PR or finish the Issue; those remain external authorized actions.

### 16.2 Candidate blocked outcome

Return a blocked/human-gate result with exact evidence when any of the following remains:

- source or local synthesis mismatch。
- consultation contract ambiguity。
- unresolved blocking review/test failure。
- provider/mirror drift。
- out-of-scope diff。
- unsafe data handling。
- missing review/assurance/adoption disposition。
- no viable materially distinct strategy for a blocking repair。

### 16.3 Prohibited exit labels from this pack

Do not label this candidate or its ZIP as:

- adopted / canonical
- implementation handoff eligibility
- reviewer-passed
- pull-request handoff eligibility / merge-ready
- delivered
- authorized profile

## 17. Follow-up Candidates

| Follow-up | Trigger | Relationship |
|---|---|---|
| ChatGPT consultation adapter/runtime | manual host consultation becomes operational bottleneck | separate runtime/network Issue |
| Machine validation of repair batch | Markdown drift recurs after this contract | separate validation Issue |
| Cross-skill retry/consultation ADR | policy needed in multiple unrelated skills | Epic/ADR candidate |
| Observation schema enrichment | current evidence cannot bind freshness safely | separate observation contract Issue |
| Legacy batch migration tool | active old batches cannot be append-resumed | separate migration Issue |

None is required to keep iss-00313 coherent under the current candidate scope.

## 18. Candidate Approval Checklist

These checkboxes are intentionally unchecked.

### Adoption

- [ ] prompt-pack EAL dispositions completed。
- [ ] local synthesis assumptions confirmed。
- [ ] canonical requirement/design/plan written by main orchestrator。

### Profile and review

- [ ] actual assurance/profile workflow completed。
- [ ] fresh requirement review passed。
- [ ] fresh design review passed。
- [ ] fresh plan review passed。

### Execution readiness gate outside this pack

- [ ] source binding current。
- [ ] working tree ownership clear。
- [ ] step commands resolved to actual test node names。
- [ ] report evidence slots ready。
- [ ] no blocker or stale input。

Until those actions occur outside this evidence-only pack, this remains an unreviewed strict-plan candidate.

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6adb67-cee8-83ee-9bc3-b3025a6c5aa6

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Required repository connector context is injected. Inspect the exact current branch and HEAD 9855eda91d6f279ace07dfa3cd9ee261984476e3; do not use the default branch. The attached original-filename ZIP is the terminal output of one completed live Planner submission. It is a valid ZIP with exactly requirement.md, design.md, plan.md, and one onboarding companion, but SpecDock rejected it with authoring_payload_invalid. Independent validation proved all three canonical documents parse successfully; only validate_onboarding_companion failed with "onboarding companion required section is missing". The validator assigns thirteen concept groups to thirteen distinct nonempty markdown sections. In particular one distinct section must jointly contain purpose and scope, and another distinct section must jointly contain current architecture and target architecture. The current Planner prompt only says "cover lineage, purpose, scope, current and target architecture" and the generated guide split Purpose/Scope and Current/Target into separate sections. Provide a bounded defect diagnosis and the exact minimal wording/heading contract to add to provider planner-prompt.md and revision-prompt.md so future ZIPs satisfy the existing validator without weakening it. Include production/test allowlist, regression tests, and stop conditions. Do not produce a replacement ZIP, patch, redesign, or optional improvements. Final disposition GO_BOUNDED_PROMPT_REPAIR or STOP.

## Answer

# Conclusion

The defect is a **provider prompt–validator contract mismatch**, not a malformed ZIP, canonical-document parser defect, or validator defect.

The GitHub connector verified that `chemitaro/spec-dock` branch `iss-00334-implement-chatgpt-issue-planning-workflow` is exactly at HEAD `9855eda91d6f279ace07dfa3cd9ee261984476e3`; the default branch was not used.

The bounded repair is to make the existing thirteen-section validator contract explicit in both provider authoring prompts, retain the validator unchanged, project the two prompt resources through the official provider/projection path, and add targeted regressions.

**Final disposition: `GO_BOUNDED_PROMPT_REPAIR`**

# Source lock

Inspected sources:

* Exact repository, branch, and HEAD above.
* Provider `planner-prompt.md`. Its current wording merely says to “cover” the concepts and does not require their co-location or distinct-section assignment.
* Provider `revision-prompt.md`, which has the same ambiguity.
* Exact onboarding validator and its section-assignment algorithm.
* The supplied completed Planner artifact: [submitted authoring ZIP](sandbox:/mnt/data/iss-00334-issue-planning-documents.zip).

The ZIP contains exactly the expected four files under one root:

```text
requirement.md
design.md
plan.md
artifacts/20260730t044125z-guide-new-member-chatgpt-first-issue-planning.md
```

No Web sources were used.

# Bounded defect diagnosis

## 1. The validator contract is intentionally section-structural

`validate_onboarding_companion` defines thirteen concept groups. A qualifying Markdown section must have a nonempty body and contain every token group assigned to it. The validator then finds a distinct section for every one of the thirteen groups.

The Markdown parser recognizes H2–H6 headings and derives each section’s heading-plus-body content.  The matching algorithm is a distinct-owner assignment, so thirteen concept groups cannot all be discharged by fewer than thirteen assignable sections.

When this validation raises `ValueError`, the authoring boundary deliberately collapses it to:

```text
authoring_payload_invalid
```

There is therefore no basis for weakening or changing the validator.

## 2. The current prompts specify topics, not the required grouping

The Planner prompt says:

```text
cover lineage, purpose, scope, current and target architecture, ChatGPT First workflow, ...
```

The Semantic Revision prompt uses effectively the same topic list.

That wording permits all of the following outputs, even though the validator rejects some of them:

* separate `Purpose` and `Scope` sections;
* separate `Current architecture` and `Target architecture` sections;
* a `ChatGPT First planning sequence` section that never says `planning workflow` or `planning lifecycle`;
* current-status and roadmap prose that does not put `S01`, `S07`, `S08`, and `S14` in one assignable section.

The provider gives the model a topical completeness instruction while the runtime enforces a structural matching contract. That is the defect.

## 3. Exact result for the submitted companion

Applying the exact current validator token rules to the supplied companion produces two concept groups with no candidate section:

1. **Current architecture + target architecture**

   * `## 5. Current architecture`
   * `## 6. Target architecture and remaining outcome`
   * Neither section jointly contains both accepted concepts.

2. **ChatGPT First + planning lifecycle/workflow**

   * `## 8. ChatGPT First planning sequence`
   * The validator accepts `planning lifecycle` or `planning workflow`, not `planning sequence`.
   * No section jointly contains `ChatGPT First` and one of the two accepted planning terms.

There is also a genuine heading-level split between:

* `## 1. Lineage、purpose、価値`
* `## 2. Scopeとnon-goals`

However, in this particular payload, the first section’s table has a `Scope` column. The token matcher therefore incidentally treats that first section as containing both `purpose` and `scope`. Thus:

* **Purpose/scope is a latent prompt defect and must be repaired.**
* **It is not one of the two empty candidate groups directly causing this particular ZIP’s rejection.**
* The repair must prohibit reliance on incidental token leakage of this kind.

This additional `ChatGPT First planning sequence` mismatch is material. Repairing only the two heading pairs named in the request would leave a reproducible failure path.

# Exact minimal prompt contract

Use the following shared text **unchanged in both provider files**, in place of their current generic onboarding-companion and PlantUML sentences:

```text
Subordinate; canonical precedence. 13 nonempty H2s, exact labels, no split/merge: init-/epic-/iss- lineage; Purpose/scope; System context; Authority/responsibility; Current architecture/target architecture; ChatGPT First planning workflow; Provider-owned direct Oracle/reference-only chatgpt-use; Candidate/Review/Human/apply lifecycle; Exact branch failure; S01/S07/S08/S14 status/roadmap; Provider/projection; Failure modes; First-day checklist.
4+ valid `plantuml` fences: system-context/responsibility-boundary/planning-sequence/implementation-roadmap.
```

The semicolon-delimited labels are normative exact H2 headings:

```markdown
## init-/epic-/iss- lineage

## Purpose/scope

## System context

## Authority/responsibility

## Current architecture/target architecture

## ChatGPT First planning workflow

## Provider-owned direct Oracle/reference-only chatgpt-use

## Candidate/Review/Human/apply lifecycle

## Exact branch failure

## S01/S07/S08/S14 status/roadmap

## Provider/projection

## Failure modes

## First-day checklist
```

Contract interpretation:

* Each of these thirteen headings must start a separate H2 section.
* Each section must have a nonempty body.
* One listed concept group must not be divided between sections.
* Two listed groups must not be merged into one required section.
* Additional explanatory sections remain permitted.
* Canonical precedence must still identify the companion as subordinate to `requirement.md`, `design.md`, and `plan.md`; those exact filenames are already supplied in the authoring output expectation.
* The four PlantUML blocks remain separate from the thirteen-section assignment requirement.

Each proposed exact heading independently satisfies one and only one intended validator group. The wording does not alter accepted output, authority, lifecycle, or validation semantics.

## Existing prompt-budget compatibility

The current tests cap the fixed synthesized prompts at:

* Planner: `3,248`
* Reviewer: `3,657`
* Semantic Revision: `3,385`

A static reconstruction using the exact current synthesis fixture and the shared wording above gives:

```text
Planner:          3,245 characters
Semantic Revision: 3,206 characters
```

These are static calculations, not a claim that the repository tests were executed. The existing ceilings do not need to be increased.

# Production allowlist

## Provider authority

Only:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
```

The runtime selects these managed resources through its provider resource resolver.

## Generated dogfood projection

Only through the official projection mechanism:

```text
.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
```

The current projected files have the same respective Git blob identities as the provider resources.

## Explicit production exclusions

No changes are admitted to:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
reviewer-prompt.md
transport-output-contract.md
SKILL.md
requirement.md
design.md
plan.md
report.md
Oracle adapter or transport code
Candidate/Review/Human/apply contracts
CLI commands or public result reasons
```

The attached ZIP is evidence only and must not be repaired or resubmitted as part of this work.

# Test allowlist

Only:

```text
tests/unit/application/test_issue_planning_prompt.py
tests/unit/domain/test_issue_planning_candidate.py
tests/integration/test_issue_planning_e2e.py
```

The existing prompt tests currently check only that generic topic strings and diagram roles appear; they do not assert the thirteen-section grouping contract.  The Semantic Revision test similarly checks generic subject phrases rather than exact assignable sections.

The integration fake companion already demonstrates valid combined sections such as `Purpose and scope`, `Current architecture and target architecture`, and `ChatGPT First planning lifecycle`; it does not require redesign.

# Required regression tests

## 1. Prompt synthesis contract

In `tests/unit/application/test_issue_planning_prompt.py`:

### Planner positive test

Assert the synthesized Planner prompt contains:

* `13 nonempty H2s, exact labels, no split/merge`;
* all thirteen exact labels;
* each label exactly once in the provider role fragment;
* all four PlantUML roles.

Suggested test identity:

```text
test_planner_prompt_requires_exact_thirteen_companion_h2s
```

### Semantic Revision positive test

Make the same assertions against the Semantic Revision synthesis path:

```text
test_semantic_revision_prompt_requires_exact_thirteen_companion_h2s
```

### Reviewer isolation test

Assert the Reviewer prompt does not inherit the authoring-only thirteen-heading contract:

```text
test_reviewer_prompt_excludes_authoring_companion_h2_contract
```

### Budget regression

Retain the existing character ceilings unchanged. Do not increase them to accommodate the repair.

## 2. Validator regressions

In `tests/unit/domain/test_issue_planning_candidate.py`, retain the current positive fixture, which already uses joined headings for the affected groups.

Add one exact positive fixture using all thirteen new headings and nonempty bodies:

```text
test_onboarding_companion_accepts_exact_thirteen_h2_contract
```

Add parameterized negatives that independently prove each structural failure:

```text
test_onboarding_companion_rejects_split_purpose_and_scope
test_onboarding_companion_rejects_split_current_and_target_architecture
test_onboarding_companion_rejects_chatgpt_first_planning_sequence_without_workflow_or_lifecycle
test_onboarding_companion_rejects_merged_required_sections
```

The first negative must remove incidental `scope` tokens from the Purpose section so it tests an actual split rather than reproducing the submitted ZIP’s accidental table-column match.

For every invalid fixture, assert both levels:

```text
validate_onboarding_companion(...) raises
validate_issue_authoring_files(...) == ("authoring_payload_invalid",)
```

Retain the existing no-headings, all-in-one-section, PlantUML, authority, and framing negatives.

## 3. Installed-path integration

In `tests/integration/test_issue_planning_e2e.py`:

* For authoring expectations, assert the captured installed Planner prompt contains all thirteen exact labels and `no split/merge`.
* Exercise the same assertion during the existing Semantic Revision flow.
* Do not apply the assertion to Reviewer calls.
* Preserve the existing fake ZIP content and the Candidate/Review/Human/apply chain unchanged.
* Confirm the provider and installed prompt bytes remain projected consistently.

# Stop conditions

Return `STOP` rather than expanding the repair if any of the following occurs:

1. The current branch no longer resolves exactly to HEAD `9855eda91d6f279ace07dfa3cd9ee261984476e3` before implementation begins.
2. Satisfying the prompt contract would require changing, weakening, or adding exceptions to `validate_onboarding_companion`.
3. Any production file outside the four-file production/projection allowlist changes.
4. Official projection modifies an additional managed path or leaves provider and projection prompt bytes unequal.
5. Either existing fixed prompt-budget ceiling would need to be raised.
6. The exact thirteen-heading positive fixture does not pass the unchanged validator.
7. The split-section negative fixtures do not map to `authoring_payload_invalid` through the unchanged authoring boundary.
8. Reviewer behavior, output schema, Candidate construction, Human authority, apply semantics, or Oracle transport would need modification.
9. A post-repair live Planner output still fails with `onboarding companion required section is missing` despite containing the thirteen exact nonempty H2 sections. That would be a separate output-retrieval or payload-integrity defect; do not respond by relaxing the validator.
10. Completion would require editing the submitted ZIP or canonical Issue documents.

# Verification status

**Verified through GitHub connector**

* Exact repository, branch, and HEAD.
* Current provider and projected prompt contents.
* Current validator token groups and distinct-section algorithm.
* Current test coverage and prompt-budget ceilings.

**Verified from the supplied ZIP**

* Exact four-file inventory.
* Companion heading structure.
* Absence of a joint current/target section.
* Absence of a joint `ChatGPT First` plus `planning workflow`/`planning lifecycle` section.
* Incidental Purpose/scope match through the table’s `Scope` token.

**Accepted from the task’s supplied validation evidence**

* Independent successful parsing of all three canonical documents.

**Not performed**

* Repository mutation.
* Test execution.
* Official projection.
* Live Planner resubmission.
* Replacement ZIP generation.

# Final disposition

`GO_BOUNDED_PROMPT_REPAIR`

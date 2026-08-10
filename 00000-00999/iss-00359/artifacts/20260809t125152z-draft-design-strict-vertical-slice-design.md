---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_design_draft"
title: "iss-00359 Replace Managed Workflow Skills with SpecDock Skills — Vertical Slice Design Draft"
target: "iss-00359"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00359"
github_issue_number: 359
depends_on:
  - "iss-00357"
  - "iss-00358"
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# 1. Design objective

Skill layer を「product-owned workflow engine」ではなく、Core / Kit の discoverable client contract として設計する。Skill は Markdown guidance であり、Runtime authority adapter ではない。

# 2. Target asset layout

```text
src/spec_dock/assets/install_root/.agents/skills/
├── spec-dock/
│   ├── SKILL.md
│   └── references/
│       ├── storage-core.md
│       ├── authoring-kit.md
│       └── compatibility.md
└── spec-dock-grill-with-docs/
    ├── SKILL.md
    └── references/
        ├── evidence-output.md
        ├── question-patterns.md
        └── failure-behavior.md
```

Exact subordinate file count may be reduced after authoring. `SKILL.md` remains the only required entry file. Dogfood projection uses the same relative paths. 360 owns installed inventory and obsolete path prune.

# 3. `spec-dock` interaction model

```text
User intent
  -> resolve repository / scope
    -> read Core state and Kit guidance
      -> choose one explicit action
        -> structural mutation: invoke CLI
        -> prose authoring: edit canonical Markdown under user control
        -> evidence authoring: invoke Artifact command
      -> report observed result without promotion claim
```

Decision rules:

- Prefer explicit target over active target.
- When target identity is ambiguous, stop before write.
- Read CLI help rather than duplicating unstable syntax.
- Read Guide rather than embedding full Authoring policy.
- Use node-local R/D/P as canonical candidate source.
- Use Artifact / Report as evidence / result summary.
- Never infer implementation handoff status from dependency `ready`.

# 4. `spec-dock-grill-with-docs` interaction model

Ports are conceptual, not Runtime interfaces:

```text
LocalReader
ArtifactCreator
OptionalExternalClarifier
```

- `LocalReader`: repository-local files only, within explicit scope.
- `ArtifactCreator`: retained Core `new artifact` command.
- `OptionalExternalClarifier`: operator environment capability; absence is normal.

Sequence:

1. Build a bounded context digest.
2. Ask / organize questions.
3. Separate observed facts、user decisions、recommendations、open questions。
4. Select Current Artifact type.
5. Create one Artifact.
6. Return path and reflection guidance.

No direct canonical writer port exists. This makes auto-apply structurally unavailable.

# 5. External boundary

Skill text may say:

- use a suitable installed clarification / domain-modeling capability when available
- otherwise proceed with local question organization or stop if the requested mode requires that capability

Skill text must not say:

- call a fixed provider / model / browser
- use a personal wrapper as product fallback
- produce a successful independent review outcome
- obtain Runtime authority token
- import provider output through a specialized command

Any connector / browser / model verification remains caller-controlled.

# 6. Evidence output schema

A suggested Markdown shape, not a Runtime schema:

```markdown
# Clarification / Synthesis

## Scope and Question
## Observed Facts
## User-supplied Decisions
## Alternatives and Trade-offs
## Open Questions
## Authoring Brief
## Suggested Reflection Targets
```

Fields may be omitted when not applicable. Artifact front matter does not self-claim `adopted` or `accepted`. Durable decision is reflected later into R/D/P or accepted ADR.

# 7. Skill testing

## Static

- exact entry files
- required front matter
- no removed skill references
- no removed Runtime command
- no fixed Oracle / ChatGPT planning route
- no `analysis`
- no canonical auto-write instruction
- valid relative links
- Current Guide paths exist

## Scenario

- inspect active Issue
- inspect explicit Epic
- show dependencies without claiming readiness for implementation
- create research Artifact
- create interview Artifact
- synthesize disc Artifact
- missing external capability
- ambiguous target
- Artifact command failure
- user asks for canonical auto-apply → skill refuses automatic mutation and explains human-controlled reflection
- historical old skill files present → no fallback

## Integration

- 357 CLI fixture
- 358 Guide fixture
- provider / dogfood copies
- handoff inventory consumed by 360

# 8. Legacy inventory design

Create a machine-readable handoff in implementation evidence containing:

- old managed skill path
- ownership source
- Target disposition: prune / preserve historical / rename not allowed
- conflict rule for modified consumer file
- docs references to reroute
- tests to remove / replace
- native shim / adapter consequence
- uninstall behavior

Do not physically prune provider-installed consumer assets in this Issue; 360 applies the inventory transactionally.

# 9. Failure and recovery

| Failure | Behavior |
|---|---|
| no repository / scope | no write; exact required input |
| missing Core command | no direct file mutation fallback; report contract mismatch |
| missing Guide | no invented policy; report missing asset |
| missing external capability | no misleading result; no canonical write |
| external output incomplete | label evidence candidate; retain open questions |
| Artifact creation fails | return command failure; no second output |
| old skill still installed | do not invoke; 360 migration required |
| user asks for PR workflow | treat as external workflow, not SpecDock product behavior |

# 10. Trade-offs

- Two skills are less specialized than the current inventory, reducing discoverability of fine-grained workflow but eliminating duplicated state and maintenance.
- No direct canonical writer in grill requires a human reflection step, intentionally preserving authority.
- Optional external capability means behavior is environment-sensitive, but Core remains fully usable and failures are explicit.

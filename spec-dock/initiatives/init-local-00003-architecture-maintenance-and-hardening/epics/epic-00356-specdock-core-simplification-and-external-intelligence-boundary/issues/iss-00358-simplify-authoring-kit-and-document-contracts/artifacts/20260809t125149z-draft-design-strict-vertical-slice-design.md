---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_design_draft"
title: "iss-00358 Simplify Authoring Kit and Document Contracts — Vertical Slice Design Draft"
target: "iss-00358"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00358"
github_issue_number: 358
depends_on:
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# 1. Design objective

Thin Template と detailed Guide を分離し、Fresh authoring surface を provider-neutral、scope-aware、docs-only にする。Runtime mechanism と prose ownership を明確に分け、357 と並行実装できる asset architecture を採用する。

# 2. Target provider tree

```text
src/spec_dock/assets/spec_dock/
├── templates/
│   ├── initiative/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── report.md
│   ├── epic/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── report.md
│   ├── issue/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── report.md
│   └── artifacts/
│       ├── blank.md
│       ├── research.md
│       ├── interview.md
│       ├── disc.md
│       ├── decision-candidate.md
│       └── adr.md
└── docs/
    ├── README.md
    ├── authoring/
    │   ├── overview.md
    │   ├── requirement.md
    │   ├── design.md
    │   ├── plan.md
    │   ├── report.md
    │   ├── scope-layering.md
    │   ├── artifacts.md
    │   └── issue-plan-levels/
    │       ├── light.md
    │       ├── standard.md
    │       ├── strict.md
    │       └── critical.md
    └── reference/
```

Dogfood projection は `spec-dock/` 以下に同じ relative target tree を持つ。Installer ownership / prune は 360。

# 3. Template / Guide separation

Template contains:

- final document に残る headings
- section purpose の一行 prompt
- minimum placeholders
- optional section の明確な表示
- Guide への一つの stable link

Template does not contain:

- workflow state / phase promotion
- reviewer / grade / EAL / authority language
- full examples / anti-pattern catalog
- provider / model / browser instructions
- duplicated CLI syntax
- completion gate
- PR state

Guide contains:

- section intent
- good / bad examples
- scope differences
- optional section decision
- diagram selection
- test / rollback / migration guidance
- pressure tests
- common omissions
- anti-patterns
- related stable reference links

# 4. Scope layering

## Initiative

- strategic problem / outcome
- multiple Epic boundary
- portfolio dependency / sequencing
- broad risk / governance
- no Issue Planning Level

## Epic

- coherent product / architecture outcome
- vertical Issue slices
- cross-Issue contracts
- rollout / integration / final exit
- no implementation task micro-detail

## Issue

- one end-to-end observable value
- requirement / design / implementation / tests / docs / migration in one slice
- Planning Level
- exact acceptance / rollback / handoff

Guide uses comparison tables rather than duplicating three full policy documents.

# 5. Report template

```markdown
# Result Summary

## Outcome

## Verification

## Residual Risks / Follow-ups
```

Optional:

```markdown
## Notes
```

Front matter, if retained by repository conventions, is minimal and must not imply `approved` / completion. Report is created for all Fresh scopes. Empty sections are valid. Existing Report content is not normalized.

# 6. Planning Level architecture

## 6.1 Base Guide

Defines:

- Plan responsibility
- vertical slicing
- sequencing / dependency
- verification
- migration / rollback
- completion criteria
- Level selection and re-evaluation
- anti-patterns

## 6.2 Completion Guides

Each file is an independent delta against Base Guide:

- expected finished state
- mandatory planning depth
- test / verification obligations
- rollback / migration obligations
- security / performance / operability obligations
- examples of justified N/A
- escalation triggers

No cross-level inheritance chain.

## 6.3 Plan template section

```markdown
## Planning Level

- Selected level:
- Rationale:
- Guide:
- Risk factors:
- Re-evaluation condition:
```

This is normal Markdown. Tests verify no Runtime / metadata coupling, not the selected string value.

# 7. Authority design

```text
Artifact evidence
  -> human synthesis / review
    -> R/D/P or accepted ADR
      -> implementation
        -> thin Report result summary
```

- Artifact existence does not grant authority.
- Report does not become a durable decision store.
- Accepted ADR is durable only according to ADR's explicit accepted state, not by file type alone.
- Bundle / delegated draft may be read as evidence but cannot self-promote.
- Guide explains this without installing a mandatory EAL schema.

# 8. Current / Historical navigation

Current index:

- six Artifact templates
- Authoring Guides
- thin R/D/P/Report
- Storage Core references
- two skill entrypoints after 359 / 360

Historical page:

- names obsolete profile / workflow / draft / repair surfaces
- explains preservation
- says not for new creation
- gives reflection destination
- does not link them as recommended route

Vocabulary tests use path classification so Historical pages / fixtures may contain old terms while Current pages may not.

# 9. Shared contract with 357

357 consumes only machine-stable facts from 358:

- exact scope file names
- exact six Current Artifact type names
- Report template path and empty-valid property
- one Issue Plan path
- provider / dogfood relative asset paths

358 does not import Runtime classes or edit parser / registry. Contract is represented in a small fixture / manifest usable by both test suites. IC-1 compares actual scaffold output against it.

# 10. Projection and parity

- Provider source is package source.
- Dogfood is a checked-in projection used by repository contributors.
- Parity comparison distinguishes exact-byte files from environment-specific/generated files.
- Link checks run in both trees.
- Installed consumer parity is 360 responsibility.
- Existing node-local docs are excluded from managed byte parity because they are user-owned.

# 11. Test design

- template heading / size / forbidden section tests
- exact file catalog
- one Plan template
- four Guide links
- no `analysis`
- Current / Historical navigation classification
- Report 3–4 section and empty-valid wording
- provider / dogfood parity
- relative link validity
- forbidden Current vocabulary
- no provider/model-specific mandatory language
- existing consumer preservation fixture
- IC-1 scaffold fixture
- Initiative / Epic Level absence
- selected Level behavior invariance in Runtime supplied by 357 test

# 12. Migration

- Add Target files before deleting provider obsolete source.
- Reroute Current navigation.
- Mark removed inventory for 360.
- Keep historical docs / fixtures needed for compatibility tests.
- Do not run content migration against existing repositories.
- Update release / migration text only when 360 has exact install / prune behavior.

# 13. Trade-offs

- More Guide files than a single document, but progressive disclosure and ownership are clearer.
- Thin templates provide less inline instruction, but stable Guide links avoid policy duplication and stale divergence.
- Historical content remains, increasing repository volume, but protects evidence and compatibility.
- Docs-only Level is not machine-enforced, intentionally keeping Runtime small and human judgment explicit.

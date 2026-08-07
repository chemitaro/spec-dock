# SpecDock Core Simplification and External Intelligence Boundary — Epic materialization guide

## Recommended hierarchy

This change should be created as **one Epic with four Issues** under the existing
`init-local-00003 Architecture Maintenance and Hardening` Initiative.

A new Initiative is not recommended because the existing Initiative is explicitly
open-ended and already owns architecture contracts, source-of-truth boundaries,
runtime/scaffold/docs parity, and structural hardening.

Do not place this Epic under `init-00322 GPT 56 ChatGPT First Intelligence Architecture`.
That Initiative exists to automate Planning, Review, Execution, and Delivery through a
ChatGPT-first workflow. This Epic deliberately replaces that product-owned workflow with
a lightweight storage core, an authoring kit, and replaceable external intelligence.

## Proposed Epic

- Title: `SpecDock Core Simplification and External Intelligence Boundary`
- Parent: `init-local-00003`
- Suggested slug: `spec-dock-core-simplification-and-external-intelligence-boundary`

Create the real Epic through SpecDock so the GitHub Issue number and canonical Epic ID
are assigned correctly:

```bash
./spec-dock/scripts/spec-dock new epic \
  --initiative init-local-00003 \
  --title "SpecDock Core Simplification and External Intelligence Boundary"
```

After creation:

1. Replace `<EPIC_ID>` and `<GITHUB_ISSUE_NUMBER_OR_URL>` in the three draft documents.
2. Copy `requirement.md`, `design.md`, and `plan.md` into the returned Epic directory.
3. Add this Epic to the parent Initiative plan as the current architecture-simplification Epic.
4. Create the four Issues listed in `plan.md` through the SpecDock CLI.
5. Register the dependency edges from `plan.md`.
6. Run `validate` and `sync`.

## Baseline used for this draft

- Repository: `chemitaro/spec-dock`
- Branch: `main`
- Reviewed HEAD: `ecdac90d157ac3bc3680bca833d7bdf88e46de45`
- Date reviewed: `2026-08-07`

## Scope discipline

This bundle intentionally avoids:

- a new Initiative;
- multiple Epics;
- a separate planning-only Issue;
- a separate final-quality Issue;
- detailed file-by-file implementation steps at Epic level.

The four Issues are the minimum coherent slices:

1. Storage Core runtime reduction.
2. Authoring Kit simplification.
3. Two-skill integration boundary.
4. Distribution cutover, migration, and legacy retirement.

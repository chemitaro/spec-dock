---
種別: manifest
ID: "20260708t162512z-manifest"
タイトル: "ChatGPT Formal Spec Pack Manifest For iss-00309"
状態: "draft"
作成者: "ChatGPT GPT-5.5 Pro draft"
最終更新: "2026-07-08"
親: ["iss-00309"]
authority: "evidence_only"
adoption_status: "unreviewed"
---

# ChatGPT Formal Spec Pack Manifest For iss-00309

## 1. 結論

この ZIP は `iss-00309` 向けの issue-local canonical draft 候補を含む。内容は Codex が現在ブランチで採用・編集・検証するための evidence pack であり、canonical adoption、fresh `spec-reviewer` pass、execution-ready、PR-ready、merge-ready、Issue finish、Epic completion を主張しない。

## 2. ZIP contents

| Path | Purpose |
|---|---|
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/requirement.md` | Strict Issue requirement draft。scope / non-scope、AC / EC、risk signals、accepted ADR trace を含む。 |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/design.md` | Strict Issue design draft。primary skills、manual backup skills、ChatGPT evidence lane、workflow docs、Epic plan template、installed distribution の設計契約を含む。 |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/plan.md` | Strict Issue implementation plan draft。closure IDs、milestones、commands、reviewer gates、rollback / follow-up notes を含む。 |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/artifacts/20260708t162513z-research-workflow-impact-map.md` | Workflow / skill / doc / template impact matrix。 |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/artifacts/20260708t162514z-disc-implementation-scope-and-test-strategy.md` | Implementation grouping、test strategy、reviewer focus、non-scope notes。 |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md` | この manifest。 |

## 3. Repository connector observations used

- Repository: `chemitaro/spec-dock`
- Requested branch: `iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign`
- Default branch: `main`
- Effective branch used: requested current branch; default branch fallback was not used.
- Current branch was opened successfully through the GitHub connector by fetching current-branch files including `README.md`, target Issue docs, provider skill files, parent Epic docs, workflow docs, templates, and `src/spec_dock/cli.py`.
- Exact branch search returned no branch search rows, but direct file fetch with the requested ref succeeded; this pack therefore uses the requested ref as accessible repository state.

## 4. Source assumptions

- Prompt-provided current pushed HEAD `339845abfb098d4c0ae9cd65887b385bb3082fe8` was treated as prompt context. This pack did not independently verify commit object metadata beyond GitHub connector file fetches on the requested ref.
- Existing `iss-00309` `requirement.md` was mostly template/scaffold text.
- Existing `iss-00309` `design.md` and `plan.md` were placeholder files with `artifact_state: awaiting-assurance-compose`.
- `.assurance.json` for `iss-00309` was not found through direct GitHub connector fetch; prompt-provided `authorized_profile: strict` was therefore used as task authority for this draft.
- `spec-dock-initiative-planning-manual`, `spec-dock-epic-planning-manual`, and `spec-dock-issue-planning-manual` were not found through direct current-branch file fetch and are treated as new provider assets to add.
- `src/spec_dock/cli.py` `_MANAGED_SKILL_NAMES` was treated as the observed installed skill distribution registry.
- Provider-side source of truth was treated as:
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
- Dogfooding workspace `spec-dock/` was treated as validation / confirmation surface, not implementation source of truth.
- The attached file `設計判断と提案.txt` concerns a different exception/failure taxonomy topic and was not used as a source for this SpecDock planning-skill ZIP.

## 5. Adopted source decisions reflected

- ChatGPT-first is primary planning route.
- Existing planning skill names remain primary:
  - `spec-dock-initiative-planning`
  - `spec-dock-epic-planning`
  - `spec-dock-issue-planning`
- Old planning route becomes manual backup:
  - `spec-dock-initiative-planning-manual`
  - `spec-dock-epic-planning-manual`
  - `spec-dock-issue-planning-manual`
- Browser / ChatGPT capacity failures wait / retry / recover first.
- Manual route requires hard / unrecoverable failure and explicit human approval.
- Option 3+ accepted:
  - Epic Planning creates Issue draft R/D/P and handoff.
  - Canonical Issue Planning occurs just before or after Issue start.
  - Issue Planning refreshes against current repository state, prior completed Issues, dependency state, unresolved ledgers.
  - Non-local drift returns to Epic Planning repair / clarification / ADR.
- Multi-Issue implementation Epic requires final quality gate / PR delivery Issue.
- Single-Issue / docs-only / no-op Epic may skip separate final quality Issue with rationale and evidence.
- Accepted ADR / research diagrams must be incorporated into provider docs/templates, not remain ADR-only.

## 6. Adoption caveats

Codex should treat this ZIP as a draft evidence pack.

Before adopting as canonical:

1. Unpack into a temporary tree or review diff.
2. Compare with current local worktree, especially any changes after the GitHub connector observation.
3. Record EAL disposition in `report.md`.
4. Adjust wording to match local `.assurance.json` / reviewer / runtime guidance if present.
5. Obtain fresh `spec-reviewer` pass for adopted `requirement.md`, `design.md`, and `plan.md`.
6. Only then use the docs as implementation planning authority.

## 7. Verification caveats

This ZIP was generated without executing repository tests in the user's worktree. The included test commands are planned checks, not executed evidence.

Recommended first checks after unpacking:

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
uv run pytest tests/cli_runtime
```

Installed asset simulation should be run after implementation changes, not merely after unpacking these draft specs.

## 8. No authority claims

This manifest and all files in the ZIP do not claim:

- canonical adoption completed;
- `.assurance.json` mutation;
- authorized_profile decision by ChatGPT;
- fresh `spec-reviewer` pass;
- execution-ready;
- PR-ready;
- merge-ready;
- Issue finish;
- Epic completion;
- PR delivery.

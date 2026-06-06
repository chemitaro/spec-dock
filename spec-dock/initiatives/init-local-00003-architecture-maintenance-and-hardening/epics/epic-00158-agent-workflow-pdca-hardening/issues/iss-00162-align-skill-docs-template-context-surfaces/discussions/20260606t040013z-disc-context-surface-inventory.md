---
created_by_role: doc-writer
scope_id: iss-00162
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
  - src/spec_dock/assets/install_root/.agents/skills/
  - src/spec_dock/assets/spec_dock/docs/
  - src/spec_dock/assets/spec_dock/templates/
  - .agents/skills/
  - spec-dock/docs/
  - spec-dock/templates/
intended_targets:
  - spec-dock/active/issue/report.md#Evidence-Adoption-Ledger
  - spec-dock/active/issue/report.md#Delegated-Draft-Evidence
  - spec-dock/active/issue/report.md#Step-Contract-Closure
  - spec-dock/active/issue/report.md#Test-Contract-Closure
  - spec-dock/active/issue/report.md#Closure-Coverage
  - spec-dock/active/issue/report.md#Closure-Delta
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending_parent_verification
---

# iss-00162 Context Surface Inventory

## Positioning

This discussion is scope-local evidence for S01 only. It inventories provider and dogfooding context surfaces so later issue owners can see the current claim, target ownership category, contradiction risk, and handoff boundary.

The main trace matrix contains rows where wording or ownership risk matters. The exhaustive coverage appendix classifies every provider skill/doc/template path found by the planned `find` commands, including paths that are non-specdock operational, bridge/reference only, or covered by a family row.

It does not claim canonical authority, reviewer pass, phase completion, implementation readiness, or adoption into `report.md`.

## Ownership Model Used For Classification

- `skill-owned spine`: compact first-read operational workflow that an agent must follow during the task.
- `docs-owned detail`: concepts, field meanings, lifecycle policy, hard cases, references, and detailed decision criteria.
- `template-owned scaffold`: copyable scaffold, evidence slots, and examples. Templates are not compliance authorities.
- `bridge/reference`: navigation, adapter, or mirror surface that should route to the proper owner without becoming the owner.
- `non-specdock operational`: helper workflows outside the core SpecDock authoring / execution boundary.

## Inventory / Trace Matrix

| surface path | family | current ownership claim | target ownership category | contradiction/risk | owner issue | action in this issue | action deferred | evidence/verification path |
|---|---|---|---|---|---|---|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` | provider skill | Says `spec-dock/docs/` is source of truth, skills stay concise, and workflow explanations live in docs. | `skill-owned spine` plus `bridge/reference` | Cross-cutting hub wording can imply mandatory workflow is doc-owned, contradicting the accepted ownership ADR. | `iss-00162` for inventory and bounded first cleanup; `iss-00164` for broader hub routing | Record as priority contradiction and baseline for S02 bounded wording cleanup. | Do not change route table, clarification routing, or leaf ownership structure here; hand those to `iss-00164`. | `sed -n '1,220p' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`; provider/mirror parity via `cmp` observed pass before S01 write |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | provider skill | Contains mandatory issue authoring sequence, fresh reviewer pass semantics, unresolved gap return, and canonical ownership guardrails. | `skill-owned spine` | Low contradiction. It is the completed specimen for the new pattern and should guide vocabulary. | none for rewrite; reference for `iss-00162` and downstream issues | Use as positive reference row for cross-surface vocabulary. | Any future expansion should avoid copying full docs into the skill. | `sed -n '1,220p' src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` | provider skill | Calls `workflow_issue.md` source of truth and says the skill is a concise reminder, while also listing execution obligations and ledger requirements. | mixed `skill-owned spine` and `docs-owned detail` routing | Some wording still leans doc-owned, but the skill exposes enough mandatory execution gates to function as first-read spine. Risk is moderate and localized. | `iss-00165` for workflow docs boundary if policy text needs bridge wording; no S01 rewrite | Classify as mostly aligned skill spine with docs-detail routing. | Do not rewrite execution policy or completion semantics in this issue. | `sed -n '1,220p' .agents/skills/spec-dock-issue-execution/SKILL.md`; source path listed by provider skills find command |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | provider skill | Explicitly says keep the skill concise and `workflow_clarification.md` is the source of truth. | `skill-owned spine` for clarification grill workflow | High contradiction: clarification mandatory interaction loop is hidden in docs instead of first-read skill surface. | `iss-00163` | Record handoff row only. | Rewrite clarification as skill-owned grill workflow, and bridge or retire doc-owned workflow wording in `iss-00163`. | `sed -n '1,220p' src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`; accepted decomposition ADR item 3 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`, `spec-dock-epic-planning/SKILL.md`, `spec-dock-adr-facilitation/SKILL.md` | provider skills | Leaf skills route to primary workflow docs and related phase/reference docs. | `skill-owned spine` for first actions, `docs-owned detail` for phase/policy | Potential hidden workflow risk if mandatory gates remain only in docs. No specific contradiction was classified as blocking for S01. | `iss-00165` if docs/skill bridge wording must be aligned; future follow-up if each leaf needs first-read expansion | Represent as family-level row and do not rewrite. | Detailed leaf-by-leaf expansion is outside this S01 inventory and outside bounded hub cleanup. | Provider skill list from `find src/spec_dock/assets/install_root/.agents/skills -maxdepth 2 -name SKILL.md \| sort`; targeted search for `Primary workflow` / `source of truth` |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md` and `spec-dock-copilot-adapter/SKILL.md` | provider skills | Thin host adapters follow `workflow_issue.md` and use docs references for command details. | `bridge/reference` | Low risk if kept adapter-only. Risk would rise if adapters claim lifecycle authority or diverge from issue execution skill. | none in first wave unless discovered by `iss-00164` hub/leaf routing | Classify as bridge/reference. | Keep adapter details out of context-surface ownership cleanup unless routing conflict appears. | Provider skill list and `rg 'canonical issue workflow|Keep this adapter thin' src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-adapter/SKILL.md` |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md` and `spec-dock-implementation-planner/SKILL.md` | provider skills | Scope-local discussion writers; canonical docs remain main-orchestrator-owned; no final authority or implementation readiness claims. | `skill-owned spine` for delegated authoring boundaries | Mostly aligned. They are useful references for direct-write provenance and non-authority wording. | none for rewrite; `iss-00165` if docs need matching field semantics | Use as evidence model for S01 provenance and authority disclaimers. | Do not broaden delegated write policy here. | `rg 'canonical docs remain|Do not claim|adoption_status' src/spec_dock/assets/install_root/.agents/skills/spec-dock-{system-architect,implementation-planner}/SKILL.md` |
| `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` | provider docs | Presents clarification as a first-class workflow and contains mandatory source-grounded read, one-question-at-a-time, artifact selection, and adoption rules. | `docs-owned detail` or bridge after skill rewrite | Hidden workflow risk: detailed mandatory operational loop is currently doc-owned and paired with a thin clarification skill. | `iss-00163` primary; `iss-00165` for global docs boundary wording if needed | Classify as docs hidden workflow and hand off. | Convert to thin bridge/reference or align with clarification skill rewrite in `iss-00163`; do not rewrite here. | `sed -n '1,180p' src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`; ADR decomposition item 3 |
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | provider docs | Owns phase promotion gates, authority boundary, delegated draft evidence schema, and discussion direct-write gate. | `docs-owned detail` with visible routes from skills | Contains mandatory authoring workflow detail. Risk is acceptable only if issue planning/hub skills expose the first-read spine and route here for detail. | `iss-00165` for docs boundary alignment | Classify as docs hidden-workflow/detail boundary risk, not a S01 rewrite target. | Bridge wording and any redistribution of operational steps to skills belongs to docs alignment or relevant skill owner issue. | `sed -n '1,220p' src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`; `spec-dock-issue-planning/SKILL.md` specimen |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | provider docs | Owns issue lifecycle, execution contract, delegation/reviewer/completion policy, and report evidence requirements. | `docs-owned detail` | High-density mandatory execution policy can be hidden unless `spec-dock-issue-execution` remains a first-read spine. Risk is docs hidden workflow rather than template authority. | `iss-00165` for global workflow docs boundary | Record as docs hidden workflow classification and keep as detail authority. | Do not move lifecycle policy or completion semantics in S01. | `sed -n '1,260p' spec-dock/docs/workflow_issue.md`; active plan S01 source list |
| `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md` and `phase_plan_issue.md` | provider docs | Own issue plan field semantics, executable step schema, concrete test case card shape, and plan authoring philosophy. | `docs-owned detail` | Appropriate detail authority, but risk appears when templates or skills imply these docs are the only place for mandatory execution order. | `iss-00165` for docs alignment; no S01 rewrite | Use as source for S01 file provenance and classification vocabulary. | Keep detailed field semantics in docs; ensure skills route to them without hiding mandatory spine. | `sed -n '1,260p' spec-dock/docs/authoring/issue-plan.md`; `sed -n '1,220p' src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md` |
| `src/spec_dock/assets/spec_dock/docs/README.md` and `guide.md` | provider docs | Entry/navigation docs route readers to skills, workflows, phase docs, references, and templates. | `bridge/reference` plus `docs-owned detail` | Moderate risk: README says clarification uses `workflow_clarification.md` as source of truth and `spec-dock-clarification` as entry, which may lag after `iss-00163`. | `iss-00165`; possibly `iss-00164` if hub routing vocabulary changes | Record as docs entry surface to revisit. | Do not rewrite docs entrypoints in S01; align after skill/hub decisions. | `sed -n '1,180p' src/spec_dock/assets/spec_dock/docs/README.md`; provider docs find command |
| `src/spec_dock/assets/spec_dock/templates/README.md` | provider templates | Says templates are used by `new`, editable after generation, and discussion docs are work surfaces; also references creation/operation rules as docs-owned. | `template-owned scaffold` plus `bridge/reference` | Mostly aligned. Authority risk exists where template README describes operational workflow details for interview/research/disc, but it frames generated files as editable and non-final. | `iss-00166` for template consistency | Classify as representative template row. | Template-wide wording cleanup and examples belong to `iss-00166`. | `sed -n '1,220p' src/spec_dock/assets/spec_dock/templates/README.md`; provider templates find command |
| `src/spec_dock/assets/spec_dock/templates/issue/plan.md` | provider template | Starts with scaffold disclaimer, then includes many execution contract headings, review/QA gates, and docs source references. | `template-owned scaffold` | Template authority risk: detailed required-looking headings can be read as compliance authority unless the scaffold boundary stays explicit. | `iss-00166` primary; `iss-00165` for docs link wording if needed | Classify as template authority risk and hand off. | Do not rewrite issue plan template in S01. Align scaffold/example language in `iss-00166`. | `sed -n '1,260p' src/spec_dock/assets/spec_dock/templates/issue/plan.md` |
| `src/spec_dock/assets/spec_dock/templates/issue/report.md` | provider template | Defines observed evidence ledger sections, decision ledger, Evidence Adoption Ledger, delegated draft evidence, and warnings against authority claims. | `template-owned scaffold` with evidence slots | Mixed: strong evidence-slot model is desired, but detailed completion semantics in a template may be mistaken for policy authority. | `iss-00166` primary | Classify as template authority risk with good non-authority wording examples. | Keep template as scaffold; ensure any global template rewrite preserves report evidence slots without making template the rule owner. | `sed -n '1,220p' src/spec_dock/assets/spec_dock/templates/issue/report.md` |
| `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`, `research.md`, `disc.md` | provider templates | Provide frontmatter and structured prompts for clarification evidence, research, and synthesis. | `template-owned scaffold` | Clarification templates currently support doc-owned clarification flow. They likely need alignment with skill-owned grill workflow. | `iss-00163` for clarification-specific template support; `iss-00166` for global scaffold consistency | Record handoff rows. | Do not update discussion templates in S01. | `sed -n '1,220p' src/spec_dock/assets/spec_dock/templates/discussions/interview.md`; provider templates find command |
| `.agents/skills/spec-driven-tdd-workflow/SKILL.md` | dogfooding mirror | Mirrors provider hub skill text byte-for-byte before S01 write. | `bridge/reference` verification target | Same contradiction as provider hub, but mirror is not source of truth. | `iss-00162` for mirror verification during S02; `iss-00164` for broader hub routing | Record as dogfooding mirror row. | Do not edit mirror in S01. S02 may update provider and mirror together if parent authorizes that step. | `find .agents/skills -maxdepth 2 -name SKILL.md \| sort`; `cmp -s src/.../spec-driven-tdd-workflow/SKILL.md .agents/.../spec-driven-tdd-workflow/SKILL.md` returned `0` |
| `spec-dock/docs/workflow_clarification.md`, `spec-dock/docs/workflow_issue.md`, `spec-dock/docs/authoring/issue-plan.md` | dogfooding mirrors | Mirror shipped docs used for local dogfooding and active workflow reads. | `bridge/reference` verification target | Same docs hidden workflow risks as provider docs, but dogfooding mirror should verify provider changes rather than become authority. | `iss-00165` after provider docs alignment; `iss-00163` for clarification mirror after provider skill/doc changes | Record mirror coverage. | Do not edit mirror docs in S01. | `find spec-dock/docs -maxdepth 2 -type f \| sort`; targeted reads of active workflow docs |
| `spec-dock/templates/issue/plan.md`, `spec-dock/templates/issue/report.md`, `spec-dock/templates/discussions/interview.md` | dogfooding mirrors | Mirror shipped templates used for local dogfooding. | `bridge/reference` verification target | Same template authority/scaffold risks as provider templates; mirror is not source of truth. | `iss-00166` after provider template alignment | Record mirror coverage. | Do not edit mirror templates in S01. | `find spec-dock/templates -maxdepth 3 -type f \| sort`; targeted provider template reads |

## Handoff Summary

- `iss-00163`: Owns the clarification-specific rewrite. Rows handed off: `spec-dock-clarification/SKILL.md`, `workflow_clarification.md`, and clarification discussion templates.
- `iss-00164`: Owns broader hub / leaf routing wording. Rows handed off: `spec-driven-tdd-workflow/SKILL.md` route table, clarification routing, and leaf ownership restructuring.
- `iss-00165`: Owns workflow docs boundary alignment. Rows handed off: `workflow_spec_authoring.md`, `workflow_issue.md`, `authoring/issue-plan.md`, `phase_plan_issue.md`, README / guide entry wording, and any docs bridge wording after skill cleanup.
- `iss-00166`: Owns template scaffold/example consistency. Rows handed off: `templates/README.md`, `templates/issue/plan.md`, `templates/issue/report.md`, and discussion templates.

## Coverage Notes

- Provider skills were inventoried by file list and classified in the appendix; main matrix rows highlight contradiction and handoff risks.
- Provider docs were inventoried by file list and classified in the appendix; targeted reads were used for workflow, authoring, and entrypoint docs where hidden workflow risk is highest.
- Provider templates were inventoried by file list and classified in the appendix; targeted reads were used for README, issue plan/report, and clarification-supporting discussion templates.
- Dogfooding mirrors were treated as verification targets only. The provider-side source of truth remains under `src/spec_dock/assets/...` per the active requirement/design.

## Exhaustive Provider Surface Coverage Appendix

These tables bind S01 coverage to the planned provider file-list commands. Rows here are classification evidence, not rewrite instructions.

### Provider Skills

| provider path | coverage classification | owner issue / disposition |
|---|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/git-commit-conventional-ja/SKILL.md` | non-specdock operational | No first-wave ownership rewrite; keep outside SpecDock authoring boundary unless later integration issue discovers a conflict. |
| `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md` | non-specdock operational | No first-wave ownership rewrite; GitHub helper surface only. |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md` | non-specdock operational | No first-wave ownership rewrite; PR helper surface only. |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | non-specdock operational | No first-wave ownership rewrite; PR merge-preparation helper surface only. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-adr-facilitation/SKILL.md` | skill-owned spine plus docs-detail routing | Family row in main matrix; potential docs/skill bridge alignment belongs to `iss-00165` or later leaf-specific follow-up. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | skill-owned spine target with current docs-hidden workflow risk | Main matrix row; primary rewrite owner `iss-00163`. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md` | bridge/reference | Main matrix family row; no first-wave rewrite unless `iss-00164` finds routing conflict. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md` | bridge/reference | Main matrix family row; no first-wave rewrite unless `iss-00164` finds routing conflict. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | skill-owned spine plus docs-detail routing | Family row in main matrix; potential docs/skill bridge alignment belongs to `iss-00165` or later leaf-specific follow-up. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md` | skill-owned spine for delegated discussion boundaries | Main matrix family row; no S01 rewrite. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | skill-owned spine plus docs-detail routing | Family row in main matrix; potential docs/skill bridge alignment belongs to `iss-00165` or later leaf-specific follow-up. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` | mixed skill-owned spine and docs-detail routing | Main matrix row; execution policy rewrite deferred to `iss-00165` if needed. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | skill-owned spine specimen | Main matrix row; no rewrite. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md` | skill-owned spine for delegated discussion boundaries | Main matrix family row; no S01 rewrite. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` | skill-owned spine plus bridge/reference | Main matrix row; bounded wording cleanup in `iss-00162` S02, broader routing owner `iss-00164`. |

### Provider Docs

| provider path | coverage classification | owner issue / disposition |
|---|---|---|
| `src/spec_dock/assets/spec_dock/docs/README.md` | bridge/reference plus docs-owned detail | Main matrix row; entry wording revisit belongs to `iss-00165` and possibly `iss-00164`. |
| `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md` | docs-owned detail | Main matrix family row; boundary alignment owner `iss-00165`. |
| `src/spec_dock/assets/spec_dock/docs/guide.md` | bridge/reference plus docs-owned detail | Covered by README/guide row; revisit belongs to `iss-00165`. |
| `src/spec_dock/assets/spec_dock/docs/github.md` | docs-owned detail / reference | No first-wave rewrite; GitHub guidance reference. |
| `src/spec_dock/assets/spec_dock/docs/phase_design.md` | docs-owned detail | No S01 rewrite; phase semantics stay docs-owned. |
| `src/spec_dock/assets/spec_dock/docs/phase_plan.md` | docs-owned detail | No S01 rewrite; phase semantics stay docs-owned. |
| `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md` | docs-owned detail | No S01 rewrite; phase semantics stay docs-owned. |
| `src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md` | docs-owned detail | No S01 rewrite; phase semantics stay docs-owned. |
| `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md` | docs-owned detail | Main matrix family row; boundary alignment owner `iss-00165`. |
| `src/spec_dock/assets/spec_dock/docs/phase_requirement.md` | docs-owned detail | No S01 rewrite; phase semantics stay docs-owned. |
| `src/spec_dock/assets/spec_dock/docs/reference_deps.md` | docs-owned detail / reference | No first-wave rewrite; dependency reference. |
| `src/spec_dock/assets/spec_dock/docs/reference_github.md` | docs-owned detail / reference | No first-wave rewrite; GitHub reference. |
| `src/spec_dock/assets/spec_dock/docs/reference_hard_cutover.md` | docs-owned detail / reference | No first-wave rewrite; lifecycle/reference surface. |
| `src/spec_dock/assets/spec_dock/docs/reference_naming.md` | docs-owned detail / reference | No first-wave rewrite; naming reference. |
| `src/spec_dock/assets/spec_dock/docs/reference_sync.md` | docs-owned detail / reference | No first-wave rewrite; sync reference. |
| `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` | docs-owned detail / reference | No first-wave rewrite; worktree reference. |
| `src/spec_dock/assets/spec_dock/docs/workflow-tree.md` | bridge/reference | No S01 rewrite; tree/navigation reference. |
| `src/spec_dock/assets/spec_dock/docs/workflow_adr.md` | docs-owned detail | No S01 rewrite; ADR workflow detail may need later skill-spine pass only if surfaced as hidden mandatory workflow. |
| `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` | docs-owned detail with hidden workflow risk | Main matrix row; primary rewrite owner `iss-00163`, global boundary owner `iss-00165` if needed. |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | docs-owned detail | No S01 rewrite; planning leaf bridge alignment belongs to `iss-00165` or later leaf-specific follow-up. |
| `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | docs-owned detail | No S01 rewrite; planning leaf bridge alignment belongs to `iss-00165` or later leaf-specific follow-up. |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | docs-owned detail with hidden execution-policy density | Main matrix row; global docs boundary owner `iss-00165`. |
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | docs-owned detail with authoring-gate density | Main matrix row; issue-planning skill already exposes spine; docs boundary owner `iss-00165`. |

### Provider Templates

| provider path | coverage classification | owner issue / disposition |
|---|---|---|
| `src/spec_dock/assets/spec_dock/templates/README.md` | template-owned scaffold plus bridge/reference | Main matrix row; template consistency owner `iss-00166`. |
| `src/spec_dock/assets/spec_dock/templates/discussions/adr.md` | template-owned scaffold | Covered by discussion-template family; template consistency owner `iss-00166`, ADR-specific changes only if later ADR issue requires them. |
| `src/spec_dock/assets/spec_dock/templates/discussions/disc.md` | template-owned scaffold | Main matrix discussion-template family; template consistency owner `iss-00166`. |
| `src/spec_dock/assets/spec_dock/templates/discussions/interview.md` | template-owned scaffold supporting clarification | Main matrix row; clarification-specific owner `iss-00163`, global template owner `iss-00166`. |
| `src/spec_dock/assets/spec_dock/templates/discussions/research.md` | template-owned scaffold | Main matrix discussion-template family; template consistency owner `iss-00166`. |
| `src/spec_dock/assets/spec_dock/templates/discussions/scratch.md` | template-owned scaffold | Covered by discussion-template family; template consistency owner `iss-00166` if wording drift appears. |
| `src/spec_dock/assets/spec_dock/templates/epic/design.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/epic/report.md` | template-owned scaffold with evidence slots | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/initiative/design.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/initiative/plan.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/initiative/report.md` | template-owned scaffold with evidence slots | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/issue/design.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |
| `src/spec_dock/assets/spec_dock/templates/issue/plan.md` | template-owned scaffold with authority-risk wording | Main matrix row; template consistency owner `iss-00166`. |
| `src/spec_dock/assets/spec_dock/templates/issue/report.md` | template-owned scaffold with evidence slots and authority-risk wording | Main matrix row; template consistency owner `iss-00166`. |
| `src/spec_dock/assets/spec_dock/templates/issue/requirement.md` | template-owned scaffold | Template consistency owner `iss-00166`; no S01 rewrite. |

## Unresolved Risks

- The main matrix is not a line-by-line rewrite plan for every provider skill/doc/template; exhaustive path classification is provided in the appendix.
- Hidden workflow classification may need refinement after `iss-00163` and `iss-00164` change the first-read skill surfaces.
- Template authority risk is classified here, but exact wording changes belong to `iss-00166`.
- This file remains `adoption_status: unreviewed` until the parent orchestrator verifies diff guard and records adoption or rejection in `report.md`.

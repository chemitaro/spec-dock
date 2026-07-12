---
種別: disc
ID: "20260708t162514z-disc"
タイトル: "Implementation Scope And Test Strategy For ChatGPT First Planning Skills"
状態: "draft"
作成者: "ChatGPT GPT-5.5 Pro draft"
最終更新: "2026-07-08"
親: ["iss-00309"]
authority: "evidence_only"
adoption_status: "unreviewed"
intended_targets: ["design.md", "plan.md"]
---

# Implementation Scope And Test Strategy For ChatGPT First Planning Skills

## 1. 位置づけ

この artifact は、`iss-00309` の実装者が provider-side assets、tests、dogfooding validation、reviewer focus を具体化するための issue-local discussion draft である。Codex が採用するまでは canonical authority ではない。

## 2. 実装スコープの束ね方

### Group A: Skill surface

目的:

- primary planning skills を ChatGPT-first route として明確化する。
- manual backup skills を別 skill として追加する。
- ChatGPT authoring skill を evidence lane として保つ。

対象:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning-manual/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning-manual/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
```

Key tests:

```bash
grep -R "ChatGPT-first" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning/SKILL.md
grep -R "human-approved emergency backup" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning-manual/SKILL.md
grep -R "canonical adoption" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
```

Reviewer focus:

- primary / manual role separation;
- no automatic fallback wording;
- no authority leak.

### Group B: Installed distribution

目的:

- manual backup skills が provider asset として存在するだけでなく、consumer repo へ installed managed skill として届くようにする。

対象:

```text
src/spec_dock/cli.py
tests/cli_runtime/
```

Key tests:

```bash
grep -n '"spec-dock-initiative-planning-manual"' src/spec_dock/cli.py
grep -n '"spec-dock-epic-planning-manual"' src/spec_dock/cli.py
grep -n '"spec-dock-issue-planning-manual"' src/spec_dock/cli.py

tmpdir="$(mktemp -d)"
uv run spec-dock init "$tmpdir"
test -f "$tmpdir/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-epic-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-issue-planning-manual/SKILL.md"
```

Reviewer focus:

- `_MANAGED_SKILL_NAMES` order does not make manual route primary;
- init/update simulation is deterministic;
- legacy managed skill cleanup is not disturbed.

### Group C: Workflow docs

目的:

- accepted ADR の Option 3+ を durable provider docs に反映する。
- PlantUML diagrams を ADR-only から docs / templates update target へ移す。
- handoff-ready / execution-ready / final quality policy を future agents が誤読しないようにする。

対象:

```text
src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md
src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
src/spec_dock/assets/spec_dock/docs/workflow_epic.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md
src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md
src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md
```

Key tests / checks:

```bash
grep -R "Option 3+" -n src/spec_dock/assets/spec_dock/docs
grep -R "ChatGPT First SpecDock Planning And Delivery Workflow" -n src/spec_dock/assets/spec_dock/docs
grep -R "Issue Draft To Canonical Planning And Execution" -n src/spec_dock/assets/spec_dock/docs
grep -R "handoff-ready" -n src/spec_dock/assets/spec_dock/docs
grep -R "execution-ready" -n src/spec_dock/assets/spec_dock/docs
```

Reviewer focus:

- diagram placement is not duplicated inconsistently;
- validation `pass` is not reviewer pass;
- draft adoption is not execution readiness.

### Group D: Epic plan template

目的:

- future Epic plans で final quality Issue policy と Issue draft handoff を必ず見える形にする。

対象:

```text
src/spec_dock/assets/spec_dock/templates/epic/plan.md
```

Required content:

```text
Epic classification:
  - multi-Issue implementation / single-Issue / docs-only / no-op
Final quality Issue:
  - required / skipped
skip rationale
completion evidence
Issue-local draft path index
pre-start canonical Issue boundary
intermediate deferred PR delivery policy
```

Key checks:

```bash
grep -n "Epic classification" src/spec_dock/assets/spec_dock/templates/epic/plan.md
grep -n "final quality" src/spec_dock/assets/spec_dock/templates/epic/plan.md
grep -n "skip rationale" src/spec_dock/assets/spec_dock/templates/epic/plan.md
grep -n "Issue-local draft path index" src/spec_dock/assets/spec_dock/templates/epic/plan.md
```

Reviewer focus:

- multi-Issue implementation Epic must not omit final quality Issue;
- single-Issue/docs-only/no-op skip remains allowed with evidence;
- template does not make canonical Issue docs upfront Epic Planning outputs.

### Group E: Dogfooding validation

目的:

- provider-side source-of-truth changes are reflected and validated in dogfooding workspace when applicable.

対象:

```text
spec-dock/docs/
spec-dock/templates/
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/report.md
```

Key checks:

```bash
./spec-dock/scripts/spec-dock validate
git diff -- src/spec_dock/assets spec-dock/docs spec-dock/templates
```

Reviewer focus:

- no source-of-truth inversion;
- report evidence states which mirror updates are validation only;
- no claim that dogfood mirror alone completes provider update.

## 3. Test strategy

### 3.1 Static content tests

Add focused tests or assertions that read provider asset files and assert:

- primary skill files contain `ChatGPT-first` or agreed Japanese equivalent;
- manual skill files exist and contain `human-approved emergency backup`;
- manual skill frontmatter `name` exactly matches skill directory;
- ChatGPT authoring skill forbidden claims remain present;
- Epic plan template includes final quality / skip / draft path index fields.

### 3.2 Installed simulation tests

Use temporary target repository:

```bash
tmpdir="$(mktemp -d)"
uv run spec-dock init "$tmpdir"
find "$tmpdir/.agents/skills" -maxdepth 2 -name SKILL.md | sort
```

Expected:

- primary planning skills exist;
- `spec-dock-chatgpt-authoring` exists;
- all three `-manual` skills exist;
- no missing source asset error.

### 3.3 Workflow validation

Run:

```bash
./spec-dock/scripts/spec-dock validate
```

Expected:

- no validation error introduced by docs/templates/skills.
- if validation does not inspect these docs, record limitation and rely on additional focused tests.

### 3.4 Python tests

Run focused runtime tests:

```bash
uv run pytest tests/cli_runtime
```

If this is too broad for the implementation environment, minimum focused subset must include whichever tests cover installer init/update and managed assets. If such tests do not exist, add them.

### 3.5 Diff hygiene

Run:

```bash
git diff --check
```

Expected:

- no trailing whitespace or conflict markers.

### 3.6 Forbidden claim sweep

Run inspection grep:

```bash
grep -R "reviewer pass" -n src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates | head -50
grep -R "execution-ready" -n src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates | head -50
grep -R "PR-ready" -n src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates | head -50
```

Expected:

- occurrences are allowed only when they describe forbidden claims, required gates, or non-authority caveats.

## 4. Non-scope reminders

- Do not implement new runtime `authoring adopt`.
- Do not implement automatic Issue creation from ChatGPT ZIP.
- Do not mark reviewer pass or `.assurance.json`.
- Do not claim execution-ready, PR-ready, merge-ready, Issue finish, or Epic completion.
- Do not rely on dogfooding mirror as provider source of truth.
- Do not create PR delivery from this intermediate Issue unless parent Epic final quality policy explicitly says this Issue is the final delivery owner.

## 5. Main risks

| Risk | Mitigation |
|---|---|
| Manual backup becomes normal route | Skill names include `-manual`, descriptions say emergency backup, docs say explicit human approval only. |
| Primary skills become too long | Keep durable kernel concise; put detailed workflow in docs. |
| Docs duplicate diagrams inconsistently | Place canonical diagram in one or two docs with cross-reference; template contains checklist not duplicate full rationale. |
| Installer registry omission | Add `_MANAGED_SKILL_NAMES` test and init simulation. |
| Unsupported commands advertised | Grep docs and preserve deferred command section. |
| Option 3+ forgotten in templates | Add Epic plan template fields and tests. |
| Strict reviewer rejects lack of specialist evidence | Record this ChatGPT draft as evidence-only; Codex must obtain or record specialist/reviewer evidence per workflow. |

## 6. Reviewer focus checklist

- [ ] Does every primary planning skill preserve existing name and become ChatGPT-first?
- [ ] Are all manual backup skills clearly emergency-only and human-approved?
- [ ] Does the design avoid automatic fallback on tab cap / timeout / browser retryable failure?
- [ ] Does `spec-dock-chatgpt-authoring` remain evidence-only?
- [ ] Do docs encode Option 3+ and not Option 1 / Option 2?
- [ ] Does Issue Planning own canonical Issue docs just-in-time?
- [ ] Are final quality Issue required/skipped rules explicit?
- [ ] Are provider-side assets updated before dogfooding mirror?
- [ ] Does installed simulation include manual skills?
- [ ] Are unsupported commands still deferred / omitted?

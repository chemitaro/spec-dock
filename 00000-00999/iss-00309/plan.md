---
種別: 実装計画書（Issue）
ID: "iss-00309"
タイトル: "ChatGPT First Planning Skills And Fallback Route Redesign"
関連GitHub: ["#309"]
状態: "review-ready"
作成者: "ChatGPT GPT-5.5 Pro / Codex adopted candidate"
最終更新: "2026-07-08"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "strict"
authorized_profile: "strict"
draft_authority: "evidence_only"
adoption_status: "codex_adopted_review_pending"
---

# iss-00309 ChatGPT First Planning Skills And Fallback Route Redesign — Issue 実装計画書（Strict / 仕様固定TDD）

## 0. 文書の位置づけ

この文書は `iss-00309` の canonical `plan.md` 候補である。ChatGPT が生成した候補を Codex が比較・検査し、採用判断を `report.md` に記録して canonical docs へ統合した。fresh `spec-reviewer` pass を得るまでは承認済み・execution-ready ではない。

この計画は、承認済みの `requirement.md` と `design.md` を前提に、provider-side skills / docs / templates / installed asset distribution を安全に更新するための実行単位を定義する。実行中の Red / Green / Refactor evidence、逸脱、追加判断、未実施検証、reviewer verdict は `report.md` に記録する。

## 1. 計画開始条件

| 入力 | 期待状態 | 確認事項 |
|---|---|---|
| `requirement.md` | Codex adopted draft または approved | AC / EC / scope / non-scope が埋まっている。 |
| `design.md` | Codex adopted draft または approved | DES-001〜DES-014 相当の設計契約が固定されている。 |
| Accepted ADR | accepted | `artifacts/20260708t161533z-adr-chatgpt-first-option-3-plus-issue-planning-workflow.md` を参照済み。 |
| `report.md` | exists | EAL-001〜EAL-005 と adoption destination を確認済み。 |
| Provider assets | accessible | `src/spec_dock/assets/...` を source of truth として確認済み。 |
| Current branch | accessible | `iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign` の current state を確認済み。 |

Blocking conditions:

- Current branch / provider assets が読めない。
- `requirement.md` / `design.md` に unresolved blocking gap がある。
- Accepted ADR と実装方針が矛盾する。
- Human approval なしの automatic manual fallback を要求される。
- `spec-reviewer` gate を省略する必要がある。

## 2. 実装戦略

- Provider-side source of truth を先に更新する。
- Manual backup skills を新規追加し、primary planning skills の既存名を残す。
- Primary skills は ChatGPT-first route を先に扱うが、canonical authority を持つのは main orchestrator / planning skill であることを維持する。
- Workflow docs と Epic plan template へ accepted ADR diagrams / lifecycle を反映し、ADR-only knowledge にしない。
- Dogfooding workspace は mirror / validation として後半に確認する。
- Tests は installed asset distribution、managed skill registry、docs/template consistency、forbidden authority claims を中心に置く。
- Implementation は commit しやすい単位へ分けるが、final quality gate / PR delivery はこの Issue 内では主張しない。Parent Epic relay policy に従い、必要な delivery は final quality Issue が所有する。

## 3. Allowed change surface

| 種別 | Path / target | 許可する変更 | Design IDs |
|---|---|---|---|
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | ChatGPT-first primary route / wait-retry-recover / manual backup boundary を追加。 | DES-001, DES-003, DES-005 |
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | Option 3+ Issue draft handoff / final quality policy / manual backup boundary を追加。 | DES-001, DES-006, DES-009 |
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | draft-adoption freshness / prior Issues / drift repair / ChatGPT-first route を追加。 | DES-001, DES-007, DES-008 |
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md` | 新規 manual backup skill。 | DES-002, DES-004 |
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning-manual/SKILL.md` | 新規 manual backup skill。 | DES-002, DES-004 |
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning-manual/SKILL.md` | 新規 manual backup skill。 | DES-002, DES-004 |
| skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | Shared evidence lane / forbidden claims / failure classification を補強。 | DES-005 |
| installer | `src/spec_dock/cli.py` | `_MANAGED_SKILL_NAMES` に manual skills を追加し order を確認。 | DES-011 |
| docs | `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | ChatGPT evidence adoption / EAL / reviewer gate / manual backup boundary。 | DES-005 |
| docs | `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md` | Primary planning route relationship、PlantUML、deferred commands。 | DES-005, DES-012 |
| docs | `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | Initiative planning ChatGPT-first / manual backup relation。 | DES-001, DES-002 |
| docs | `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Option 3+ handoff、Issue drafts、final quality policy、PlantUML。 | DES-006, DES-009, DES-012 |
| docs | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Draft adoption lifecycle、just-in-time planning、drift repair、execution-ready rule。 | DES-007, DES-008, DES-012 |
| docs | `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md` | final quality Issue required/skipped checklist、draft path index。 | DES-009, DES-010 |
| docs | `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md` | draft adoption / current-state refresh / reviewer handoff。 | DES-007, DES-008 |
| docs | `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md` | executable Issue plan prerequisites and adoption matrix。 | DES-007 |
| docs | `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md` | prompt/output contract and forbidden authority claim consistency。 | DES-005, DES-014 |
| template | `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | Epic classification、final quality Issue required/skipped、Issue draft path index。 | DES-009, DES-010, DES-012 |
| tests | `tests/cli_runtime/` | Installed skill distribution, docs/template content checks, managed skill registry tests。 | all |
| dogfood mirror | `spec-dock/docs/`, `spec-dock/templates/`, active Issue report | Provider update validation / mirror consistency only。 | DES-013 |

## 4. Forbidden changes

| Target | Forbidden change | Required action if needed |
|---|---|---|
| Primary skill names | Rename away from `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` | Stop and return to requirement / ADR. |
| Manual route | Automatic fallback from recoverable ChatGPT failure | Stop and record conflict with EAL-001 / ADR. |
| ChatGPT authoring | Grant canonical adoption / reviewer pass / readiness / PR authority | Reject change. |
| Runtime commands | Implement or advertise deferred `authoring adopt` / `create-issues-from-zip` / reviewer-pass commands | Defer to parent Epic runtime issue. |
| Dogfooding workspace | Treat dogfood-only update as source-of-truth implementation | Move change to provider assets or record validation-only evidence. |
| Existing workspace user artifacts | Mass rewrite or migration | Create separate migration / compatibility issue. |
| GitHub / PR state | Create PR / merge / close issues from this plan | Out of scope; final quality Issue / PR delivery path owns it. |

## 5. Milestone overview

| Milestone | Outcome | Primary gates | Suggested commit boundary |
|---|---|---|---|
| M0 | Baseline inventory and characterization | Current files / missing manual skills / registry / docs baseline | no commit or docs evidence only |
| M1 | Manual backup skills added | New `-manual` skill files, emergency backup contract | commit: manual backup skills |
| M2 | Primary planning skills ChatGPT-first | Existing skill names updated, no auto fallback | commit: primary skill rewrite |
| M3 | ChatGPT authoring evidence lane hardening | Evidence-only / forbidden claims / failure classifications | commit: shared skill boundary |
| M4 | Managed skill registry / installer distribution | `_MANAGED_SKILL_NAMES` includes manual skills | commit: installer registry |
| M5 | Workflow docs and PlantUML incorporation | Option 3+ and lifecycle diagrams in provider docs | commit: workflow docs |
| M6 | Epic plan template update | final quality / skip / path index / pre-start boundary | commit: template update |
| M7 | Dogfooding mirror and validation evidence | provider-first consistency confirmed | commit if mirror updates are tracked |
| M90 | Tests and static checks | pytest / validate / diff check / grep checks | commit: tests |
| M95 | Spec reviewer gate preparation | report evidence updated, reviewer focus ready | no readiness claim |
| M99 | Final local quality check | all planned verification commands run or blockers recorded | final issue-local evidence |

## 6. Acceptance Envelope

| Outcome ID | Related AC | Completion evidence |
|---|---|---|
| OUT-001 | AC-001〜AC-003 | Primary skill diffs show ChatGPT-first operating spine and no automatic manual fallback. |
| OUT-002 | AC-004〜AC-007 | Three `-manual` skill files exist and state human-approved emergency backup. |
| OUT-003 | AC-008 | `src/spec_dock/cli.py` `_MANAGED_SKILL_NAMES` includes manual skills in acceptable order. |
| OUT-004 | AC-009 | `spec-dock-chatgpt-authoring` still forbids canonical / reviewer / readiness claims. |
| OUT-005 | AC-010〜AC-013 | Provider docs describe EAL, reviewer gate, Option 3+, draft lifecycle, drift repair. |
| OUT-006 | AC-014〜AC-016 | Epic plan template includes final quality required/skipped and draft handoff fields; diagrams incorporated. |
| OUT-007 | AC-017〜AC-020 | Provider-first validation, installed asset simulation, pytest, validate, diff check. |
| OUT-008 | AC-021 | Codex updates `report.md` evidence if adopting; no ChatGPT self-adoption claim. |

## 7. Closure Index

| Closure ID | Requirement | Design | Closes | Verification |
|---|---|---|---|---|
| CLOS-001 | REQ-001 | DES-001 | Existing planning names are ChatGPT-first primary route. | skill text inspection + grep tests |
| CLOS-002 | REQ-002〜REQ-004 | DES-002〜DES-004 | Manual backup skills exist and require hard failure + human approval. | file existence + content tests |
| CLOS-003 | REQ-005〜REQ-006 | DES-005 | ChatGPT authoring remains evidence-only. | forbidden claim checks |
| CLOS-004 | REQ-008〜REQ-011 | DES-006〜DES-008 | Option 3+ handoff / just-in-time Issue Planning / drift repair documented. | docs/template inspection |
| CLOS-005 | REQ-012〜REQ-013 | DES-009〜DES-010 | final quality Issue required/skipped policy documented. | docs/template inspection |
| CLOS-006 | REQ-014 | DES-011 | installer managed skill list includes manual skills. | unit/static test + init simulation |
| CLOS-007 | REQ-015〜REQ-017 | DES-012 | PlantUML diagrams incorporated into docs/templates. | grep / docs inspection |
| CLOS-008 | REQ-018 | DES-013 | provider-side update precedes dogfood mirror. | report evidence + diff review |
| CLOS-009 | REQ-019 | DES-014 | unsupported commands not advertised as supported. | grep docs |
| CLOS-010 | REQ-020 | all | all verification gates run or blockers recorded. | `report.md` + command output |

## 8. Behavior Backlog

| Behavior ID | Milestone | Behavior / Guarantee | Closure | Priority |
|---|---|---|---|---|
| B-001 | M1 | `spec-dock-initiative-planning-manual` is installed skill source and says human-approved emergency backup. | CLOS-002 | high |
| B-002 | M1 | `spec-dock-epic-planning-manual` is installed skill source and says human-approved emergency backup. | CLOS-002 | high |
| B-003 | M1 | `spec-dock-issue-planning-manual` is installed skill source and says human-approved emergency backup. | CLOS-002 | high |
| B-004 | M2 | `spec-dock-initiative-planning` uses ChatGPT-first evidence route while preserving Initiative gates. | CLOS-001 | high |
| B-005 | M2 | `spec-dock-epic-planning` uses ChatGPT-first route and Option 3+ draft handoff. | CLOS-001, CLOS-004 | high |
| B-006 | M2 | `spec-dock-issue-planning` uses ChatGPT-first modes and draft adoption refresh. | CLOS-001, CLOS-004 | high |
| B-007 | M3 | `spec-dock-chatgpt-authoring` remains evidence-only and documents forbidden claims. | CLOS-003 | high |
| B-008 | M4 | installed managed skill distribution includes manual backup skills. | CLOS-006 | high |
| B-009 | M5 | workflow docs include end-to-end and draft lifecycle diagrams. | CLOS-007 | high |
| B-010 | M5 | workflow docs distinguish handoff-ready from execution-ready. | CLOS-004 | high |
| B-011 | M6 | Epic plan template includes final quality Issue policy and skip evidence. | CLOS-005 | high |
| B-012 | M7 | dogfooding workspace mirrors / validates provider asset changes without becoming source of truth. | CLOS-008 | medium |
| B-013 | M90 | focused tests and static checks guard the new contracts. | CLOS-010 | high |

## 9. 実装ステップ（Detailed milestone plan）

この section の M0〜M99 を、この Issue の実行可能な実装ステップとする。各 step は `report.md` の session log、TDD evidence、closure coverage、test contract closure に観測証跡を記録して閉じる。

### M0 Baseline inventory

Actions:

1. Inspect current provider skill files.
2. Confirm manual backup skill files are absent or stale.
3. Inspect `src/spec_dock/cli.py` `_MANAGED_SKILL_NAMES`.
4. Inspect provider workflow docs and Epic plan template for current wording.
5. Record baseline in `report.md` when Codex adopts this plan.

Commands / checks:

```bash
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
test ! -e src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md || true
grep -n "_MANAGED_SKILL_NAMES" -n src/spec_dock/cli.py
```

Stop if another managed skill registry is discovered and cannot be reconciled.

### M1 Manual backup skills

Actions:

1. Create `spec-dock-initiative-planning-manual/SKILL.md`.
2. Create `spec-dock-epic-planning-manual/SKILL.md`.
3. Create `spec-dock-issue-planning-manual/SKILL.md`.
4. Base content on current old planning route language, but strip ChatGPT-first primary route claims.
5. Add mandatory usage conditions:
   - hard / unrecoverable ChatGPT / browser / automation / provider failure;
   - explicit human approval;
   - fallback reason and approval evidence in `report.md`;
   - no reviewer pass / readiness claim.
6. Add stop conditions for retryable / recoverable / capacity failures.

Test seeds:

```bash
grep -R "human-approved emergency backup" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning-manual/SKILL.md
grep -R "manual route" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning-manual/SKILL.md
```

Commit candidate:

- `Add human-approved manual planning backup skills`.

### M2 Primary planning skills ChatGPT-first

Actions:

1. Update `spec-dock-initiative-planning/SKILL.md`.
   - Keep existing name.
   - State ChatGPT-first primary route for non-trivial Initiative planning.
   - Route ChatGPT output back through EAL / canonical rewrite / fresh reviewer pass.
   - Keep Epic node creation human approval.
2. Update `spec-dock-epic-planning/SKILL.md`.
   - Keep existing name.
   - State ChatGPT-first primary route.
   - Include Issue draft R/D/P handoff, dependency order, boundary, final quality candidate / skip rationale.
   - State canonical child Issue docs remain Issue Planning outputs.
3. Update `spec-dock-issue-planning/SKILL.md`.
   - Keep existing name.
   - Use ChatGPT-first in `zero-base`, `requirement-first`, `draft-adoption`.
   - Add current repo / prior Issues / dependency state / unresolved ledger check.
   - Add drift repair rule.
4. Add primary/manual fallback boundary:
   - wait/retry/recover before manual backup;
   - manual backup only with explicit human approval.

Test seeds:

```bash
grep -R "ChatGPT-first" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
grep -R "wait" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning/SKILL.md
grep -R "human-approved" -n src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning/SKILL.md
```

Commit candidate:

- `Make existing planning skills ChatGPT-first primary routes`.

### M3 Shared ChatGPT authoring skill boundary

Actions:

1. Update `spec-dock-chatgpt-authoring/SKILL.md`.
2. Preserve evidence-only statement.
3. Add explicit "invoked by primary planning skills" relationship.
4. Add failure classification:
   - retryable / recoverable;
   - blocked / stale;
   - rejected / unsafe;
   - hard / unrecoverable.
5. Preserve forbidden claims section.

Forbidden claim grep:

```bash
grep -n "canonical adoption" src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
grep -n "execution-ready" src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
grep -n "PR-ready" src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
```

Commit candidate:

- `Clarify ChatGPT authoring evidence lane and failure boundary`.

### M4 Installed skill registry / distribution

Actions:

1. Add manual skill names to `src/spec_dock/cli.py` `_MANAGED_SKILL_NAMES`.
2. Keep primary skills in normal user-facing order.
3. Decide order:
   - preferred: primary skill cluster first, then `spec-dock-chatgpt-authoring`, then manual backup skills; or
   - acceptable: each manual skill immediately after its primary if docs emphasize backup.
4. Add/extend tests under `tests/cli_runtime/` or installer tests to assert manual skill names are copied on init/update.

Static checks:

```bash
grep -n '"spec-dock-initiative-planning-manual"' src/spec_dock/cli.py
grep -n '"spec-dock-epic-planning-manual"' src/spec_dock/cli.py
grep -n '"spec-dock-issue-planning-manual"' src/spec_dock/cli.py
```

Installed simulation:

```bash
tmpdir="$(mktemp -d)"
uv run spec-dock init "$tmpdir"
test -f "$tmpdir/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-epic-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-issue-planning-manual/SKILL.md"
```

Commit candidate:

- `Install manual planning backup skills`.

### M5 Workflow docs and PlantUML incorporation

Actions:

1. Update `workflow_spec_authoring.md`.
   - ChatGPT evidence adoption: EAL, canonical rewrite, fresh `spec-reviewer`.
   - Manual fallback: explicit approval and failure evidence.
2. Update `workflow_chatgpt_authoring_pack.md`.
   - Primary planning skills own route.
   - ChatGPT authoring is evidence lane.
   - Include primary/manual route boundary or reference section.
   - Keep deferred commands unsupported.
3. Update `workflow_initiative.md`.
   - Initiative planning uses ChatGPT-first primary route and manual backup condition.
4. Update `workflow_epic.md`.
   - Add Option 3+ handoff requirements.
   - Include end-to-end workflow PlantUML or link to canonical doc section that contains it.
   - Include final quality Issue policy.
5. Update `workflow_issue.md`.
   - Add Issue draft lifecycle PlantUML.
   - Add just-in-time Issue Planning and drift repair.
   - State draft-only / validation-only / raw ChatGPT output is not execution-ready.
6. Update `phase_plan_epic.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, and `authoring/chatgpt-pack.md` for checklist consistency.

Checks:

```bash
grep -R "Option 3+" -n src/spec_dock/assets/spec_dock/docs
grep -R "Issue Draft To Canonical Planning And Execution" -n src/spec_dock/assets/spec_dock/docs
grep -R "ChatGPT First SpecDock Planning And Delivery Workflow" -n src/spec_dock/assets/spec_dock/docs
grep -R "human-approved emergency backup" -n src/spec_dock/assets/spec_dock/docs
grep -R "draft-only" -n src/spec_dock/assets/spec_dock/docs
```

Commit candidate:

- `Document ChatGPT-first Option 3+ planning workflow`.

### M6 Epic plan template

Actions:

1. Update `src/spec_dock/assets/spec_dock/templates/epic/plan.md`.
2. Add or strengthen:
   - Epic classification;
   - final quality Issue required / skipped;
   - skip rationale;
   - completion evidence;
   - Issue-local draft path index;
   - pre-start canonical Issue boundary;
   - intermediate deferred PR delivery policy;
   - dependency on all implementation Issues for final quality Issue.
3. Avoid making separate final quality Issue mandatory for single-Issue / docs-only / no-op Epics.

Checks:

```bash
grep -n "Epic classification" src/spec_dock/assets/spec_dock/templates/epic/plan.md
grep -n "final quality" src/spec_dock/assets/spec_dock/templates/epic/plan.md
grep -n "skip rationale" src/spec_dock/assets/spec_dock/templates/epic/plan.md
grep -n "Issue-local draft path index" src/spec_dock/assets/spec_dock/templates/epic/plan.md
```

Commit candidate:

- `Update Epic plan template for Option 3+ handoff and final quality policy`.

### M7 Dogfooding mirror / validation

Actions:

1. Compare provider docs/templates with dogfooding mirrors.
2. Update mirrors only where current workflow expects provider-aligned dogfood docs/templates.
3. Do not treat mirror-only changes as implementation completion.
4. Record provider-first evidence and mirror validation in `report.md`.

Possible checks:

```bash
./spec-dock/scripts/spec-dock validate
git diff -- src/spec_dock/assets spec-dock/docs spec-dock/templates
```

Commit candidate:

- `Mirror provider workflow updates in dogfood workspace`, only if mirror changes are tracked and required.

### M90 Tests and static checks

Add or update tests for:

- Manual skill files exist in provider assets.
- Manual skills appear in installed output after `spec-dock init/update`.
- `_MANAGED_SKILL_NAMES` contains manual skills.
- Primary skills contain ChatGPT-first wording.
- Manual skills contain human-approved emergency backup wording.
- Workflow docs include Option 3+ and diagrams.
- Epic plan template includes final quality / skip / draft path index fields.
- Unsupported commands are not presented as supported examples.

Recommended commands:

```bash
uv run pytest tests/cli_runtime
./spec-dock/scripts/spec-dock validate
git diff --check
```

Optional broader checks if runtime budget allows:

```bash
uv run pytest
```

Commit candidate:

- `Add tests for ChatGPT-first planning skill distribution and docs contracts`.

### M95 Reviewer gate preparation

Actions:

1. Update `report.md` Evidence Adoption Ledger if this ChatGPT draft is adopted.
2. Record:
   - adopted / partially adopted / rejected claims;
   - affected docs / skills / templates;
   - commands run;
   - dogfood validation;
   - unresolved blockers.
3. Request fresh `spec-reviewer` after substantive requirement/design/plan changes and after implementation changes as required by workflow.

Do not mark reviewer pass in the documents unless the actual reviewer output exists.

### M99 Final local quality check

Commands:

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
uv run pytest tests/cli_runtime
```

Installed asset simulation:

```bash
tmpdir="$(mktemp -d)"
uv run spec-dock init "$tmpdir"
test -f "$tmpdir/.agents/skills/spec-dock-initiative-planning/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-epic-planning/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-issue-planning/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-epic-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-issue-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md"
```

Final checks:

```bash
grep -R "execution-ready" -n src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs | head -50
grep -R "PR-ready" -n src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs | head -50
grep -R "human-approved emergency backup" -n src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs
```

The grep commands are inspection aids. Findings are acceptable only if wording is forbidden-claim-safe and clearly says the state is not granted by ChatGPT / validation / draft artifacts.

## 10. 具体テストケース（Verification contract）

| Test ID | 対象 closure | 検証内容 | 実行方法 | 合格条件 |
|---|---|---|---|---|
| TC-001 | CLOS-001, CLOS-002, CLOS-003 | Primary / manual / ChatGPT authoring skill の責務文言が要求と矛盾しない | `grep` / docs inspection | ChatGPT-first primary、human-approved emergency backup、evidence-only boundary が確認できる |
| TC-002 | CLOS-004, CLOS-005, CLOS-007 | Option 3+、Issue draft lifecycle、final quality Issue policy、PlantUML 図が docs/template に反映されている | `grep` / docs inspection | provider-side docs/templates に必要な workflow 表現が存在する |
| TC-003 | CLOS-006 | manual backup skills が installed managed skill registry と scaffold 出力に含まれる | `uv run pytest tests/cli_runtime` / installed asset simulation | managed skill list と init output に manual skill が含まれる |
| TC-004 | CLOS-008, CLOS-010 | SpecDock tree と Markdown 差分が破綻していない | `./spec-dock/scripts/spec-dock validate` / `git diff --check` | 両コマンドが pass する |
| TC-005 | CLOS-009 | deferred / unsupported authoring commands を supported route として案内していない | `grep` / docs inspection | unsupported command を正規利用可能な手順として主張していない |
| TC-006 | CLOS-010 | strict Issue として fresh reviewer gate へ渡せる evidence が揃っている | `report.md` inspection / spec-reviewer | reviewer verdict が記録され、blocking finding が残らない |

## 11. Step Closure Contract

| Step | Closure IDs | Required evidence destination | Completion rule |
|---|---|---|---|
| M0 | CLOS-010 | `report.md` baseline inventory | provider skills/docs/templates/registry の初期状態を記録する |
| M1 | CLOS-002 | `report.md` session log / diff | 3 つの `-manual` skill が provider assets に存在し、human approval boundary を持つ |
| M2 | CLOS-001, CLOS-004 | `report.md` session log / diff | 既存 planning skills が ChatGPT-first primary route を示す |
| M3 | CLOS-003 | `report.md` session log / diff | `spec-dock-chatgpt-authoring` が evidence-only boundary を保つ |
| M4 | CLOS-006 | `report.md` command evidence | managed skill registry と init simulation が manual skills を含む |
| M5 | CLOS-004, CLOS-005, CLOS-007 | `report.md` docs inspection evidence | workflow docs に Option 3+ / final quality / diagrams が反映される |
| M6 | CLOS-005, CLOS-007 | `report.md` docs inspection evidence | Epic plan template が final quality Issue policy と draft handoff index を持つ |
| M7 | CLOS-008 | `report.md` mirror evidence | dogfooding workspace が provider update の validation surface として整合する |
| M90 | CLOS-010 | `report.md` test evidence | relevant pytest / validate / diff check / grep checks を実行または blocker として記録する |
| M95 | CLOS-010 | Spec Authoring Gate | fresh spec-reviewer verdict を記録し、fail なら修正する |
| M99 | CLOS-010 | Closure Coverage | open blocker / unresolved stale evidence が残っていないことを確認する |

## 12. Report evidence destinations

When Codex adopts and executes this plan, record evidence in `report.md`:

- Spec Interpretation / Decision Ledger:
  - any changes to manual skill order;
  - any diagram placement decision;
  - any provider vs dogfood mirror scope decision.
- Evidence Adoption Ledger:
  - adoption disposition for this ChatGPT formal spec pack;
  - adoption disposition for accepted ADR diagrams;
  - rejected / stale claims, if any.
- Spec Authoring Gate:
  - requirement / design / plan reviewer verdicts.
- Delegated Draft Evidence:
  - this ZIP pack as delegated evidence, not canonical authority.
- Grade Specialist Evidence Gate:
  - strict grade specialist evidence or unavailable/manual fallback evidence if applicable.
- Verification evidence:
  - commands run, status, failures, retry/fix loops.
- Deferred PR delivery evidence:
  - if this is an intermediate Issue in parent Epic relay, defer PR delivery to the final quality Issue and do not claim merge-prepared.

## 13. Rollback / follow-up notes

Rollback plan:

1. Revert changed provider skill files.
2. Remove new `-manual` skill directories.
3. Remove manual skill names from `_MANAGED_SKILL_NAMES`.
4. Revert workflow docs and Epic plan template changes.
5. Re-run installed asset simulation to verify removal.
6. If rollback contradicts accepted ADR, create a superseding ADR or mark current ADR superseded before adopting the rollback as canonical workflow.

Potential follow-up Issues:

- Add runtime validation that detects missing final quality Issue in multi-Issue implementation Epic plans.
- Add docs generator / link consistency tests for PlantUML placement.
- Add `authoring validate issue-draft-adoption` richer drift diagnostics, if current runtime validator is too shallow.
- Add installer-specific tests for managed skill ordering if absent.
- Add migration guide for existing workspaces that already installed old planning skills.

## 14. Completion caveats

This plan does not itself complete the Issue. Completion still requires Codex to:

- adopt or reject this draft in `report.md`;
- update provider-side assets;
- run checks;
- obtain required fresh reviewer gates;
- record implementation evidence;
- follow parent Epic final quality / PR delivery policy.

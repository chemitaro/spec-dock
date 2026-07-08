---
種別: research
ID: "20260708t162513z-research"
タイトル: "Workflow Impact Map For ChatGPT First Planning Skills And Manual Backup"
状態: "draft"
作成者: "ChatGPT GPT-5.5 Pro draft"
最終更新: "2026-07-08"
親: ["iss-00309"]
authority: "evidence_only"
adoption_status: "unreviewed"
intended_targets: ["requirement.md", "design.md", "plan.md"]
---

# Workflow Impact Map For ChatGPT First Planning Skills And Manual Backup

## 1. 位置づけ

この artifact は、`iss-00309` 実装時に変更対象を見落とさないための issue-local research draft である。Codex が採用するまでは canonical authority ではない。

## 2. 結論

`iss-00309` の主要変更は、単なる skill 文言更新ではなく、planning workflow の authority path を **primary ChatGPT-first route** と **human-approved manual backup route** に分け、accepted ADR の Option 3+ を provider-side docs / templates / installed distribution に定着させることである。

## 3. Impact matrix

| Surface | File / target | Current branch observation | Intended change | Verification |
|---|---|---|---|---|
| Primary skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | Initiative planning entrypoint exists and treats ChatGPT output as evidence. | ChatGPT-first primary route、wait/retry/recover、manual backup approval condition、Initiative human approval gate を明記。 | `grep -n "ChatGPT-first" .../spec-dock-initiative-planning/SKILL.md` |
| Primary skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | Epic planning entrypoint exists and already says ChatGPT output is evidence-only. | Option 3+、Issue draft R/D/P handoff、Issue slice approval、final quality Issue / skip rationale、manual backup condition を明記。 | grep for `Option 3+`, `draft requirement`, `final quality` |
| Primary skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | Issue planning modes `zero-base` / `requirement-first` / `draft-adoption` exist. | ChatGPT-first for all modes、current repo / prior Issues / dependency state / unresolved ledgers による adoption、drift repair rule を追加。 | grep for `prior Issues`, `drift`, `draft-adoption` |
| Manual skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md` | Missing on current branch. | 新規。従来 Initiative planning route を human-approved emergency backup として定義。 | file existence + frontmatter `name: spec-dock-initiative-planning-manual` |
| Manual skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning-manual/SKILL.md` | Missing on current branch. | 新規。従来 Epic planning route を human-approved emergency backup として定義。 | file existence + `human-approved emergency backup` |
| Manual skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning-manual/SKILL.md` | Missing on current branch. | 新規。従来 Issue planning route を human-approved emergency backup として定義。 | file existence + `human-approved emergency backup` |
| Shared evidence lane | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | Evidence-only skill exists and has forbidden claims. | Primary planning skill から呼ばれる shared evidence lane であること、failure classification、manual backup boundary を補強。 | grep forbidden claims / evidence-only wording |
| Installer / distribution | `src/spec_dock/cli.py` | `_MANAGED_SKILL_NAMES` includes primary skills and `spec-dock-chatgpt-authoring`, not manual skills. | Three `-manual` skills を managed installed skill list に追加し、primary skills が先に出る order を維持。 | grep names + init/update simulation |
| Authoring workflow | `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | EAL / reviewer / evidence-only baseline exists. | ChatGPT-first adoption path and manual backup evidence gate を明記。 | docs grep |
| ChatGPT workflow | `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md` | Evidence modes and supported/deferred commands exist. | Primary route relationship、manual backup is not automatic、end-to-end PlantUML を追加または参照。 | grep `ChatGPT First SpecDock Planning And Delivery Workflow` |
| Initiative workflow | `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | Initiative workflow entrypoint exists. | Initiative planning の ChatGPT-first primary route と human approval fallback を追加。 | docs grep |
| Epic workflow | `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Issue draft handoff / handoff-ready distinction already exists. | Option 3+、Issue draft lifecycle、final quality Issue required/skipped policy を accepted ADR wording で強化。 | grep `Option 3+`, `final quality` |
| Issue workflow | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Handoff-ready / execution-ready and draft adoption baseline exists. | Issue Draft To Canonical Planning And Execution PlantUML、current-state refresh、prior Issues、drift repair rule を追加。 | grep lifecycle title |
| Epic plan playbook | `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md` | Epic plan phase guidance exists. | final quality required/skipped checklist、all implementation Issues dependency、intermediate deferred PR delivery gate を追加。 | docs grep |
| Issue plan playbook | `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md` | Issue plan phase guidance exists. | draft-adoption plan readiness、just-in-time canonical planning、drift feedback rule を追加。 | docs grep |
| Issue plan authoring | `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md` | Issue plan contract exists. | executable plan prerequisites に draft adoption / reviewer / EAL / prior Issue freshness を追加。 | docs grep |
| Prompt/output contract | `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md` | Prompt pack reference exists. | forbidden authority claims and ZIP/tree output contract wording を primary/manual route と一致させる。 | docs grep for forbidden claims |
| Epic template | `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | Handoff package / final quality sections exist. | Epic classification、final quality required/skipped、skip rationale、completion evidence、Issue draft path index、pre-start canonical boundary を強化。 | grep template fields |
| Dogfood mirror | `spec-dock/docs/`, `spec-dock/templates/` | Dogfooding workspace exists. | Provider-first update 後の validation / mirror consistency に限定。 | `git diff -- src/spec_dock/assets spec-dock/docs spec-dock/templates` |
| Issue report | `spec-dock/.../iss-00309.../report.md` | EAL-001〜EAL-005 exist. | ChatGPT formal spec pack adoption / rejection、implementation decisions、reviewer gates、verification results を記録。 | report inspection |
| Tests | `tests/cli_runtime/` | CLI runtime tests exist. | Managed skill installation / docs-template content checks / forbidden claim checks を追加または既存 tests へ統合。 | `uv run pytest tests/cli_runtime` |
| Static validation | repo root | Existing validation command available. | Final local quality: `git diff --check`, `./spec-dock/scripts/spec-dock validate`, pytest。 | command output recorded |

## 4. Provider-first update order

1. `src/spec_dock/assets/install_root/.agents/skills/`
2. `src/spec_dock/cli.py`
3. `src/spec_dock/assets/spec_dock/docs/`
4. `src/spec_dock/assets/spec_dock/templates/`
5. `tests/cli_runtime/`
6. Dogfooding mirror / validation under `spec-dock/`
7. `report.md` evidence update

## 5. High-risk consistency checks

| Check | Rationale |
|---|---|
| Primary skills mention ChatGPT-first but not automatic manual fallback | Prevents old route from remaining hidden normal path. |
| Manual skills require explicit human approval | Prevents emergency backup from becoming default. |
| ChatGPT skill still says evidence-only | Prevents authority leak. |
| Docs include PlantUML diagrams | Prevents accepted ADR from remaining issue-local context only. |
| Epic template includes skip rationale | Prevents over-process for single-Issue/docs-only/no-op Epics. |
| Installer registry includes manual skills | Prevents provider assets from existing but not installing. |
| Dogfood mirror not treated as source | Prevents source-of-truth inversion. |

---
種別: 設計書（Issue）
ID: "iss-00304"
タイトル: "ChatGPT Authoring Skill"
関連GitHub: ["#304"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00304 ChatGPT Authoring Skill — 設計

## 1. 設計結論

`spec-dock-chatgpt-authoring` を、新しい scope planning skill ではなく shared evidence lane skill として追加する。

既存 planning skills は保持する。

- `spec-dock-initiative-planning`: Initiative docs と Epic decomposition approval を所有する。
- `spec-dock-epic-planning`: Epic docs と Issue slicing / draft artifact handoff を所有する。
- `spec-dock-issue-planning`: Issue docs の正式化、draft adoption、fresh spec review、execution handoff を所有する。
- `spec-dock-chatgpt-authoring`: ChatGPT / Oracle authoring pack の準備、実行前提、ZIP/tree evidence、candidate / draft evidence の扱いを説明する補助 lane。

この分離により、ChatGPT の長時間推論能力を利用しながら、SpecDock の canonical authority と reviewer gate を保持する。

## 2. Provider-Side Placement

### 2.1 Source of truth

```text
src/spec_dock/assets/install_root/.agents/skills/
  spec-dock-chatgpt-authoring/
    SKILL.md
  spec-dock-initiative-planning/
    SKILL.md
  spec-dock-epic-planning/
    SKILL.md
  spec-dock-issue-planning/
    SKILL.md
```

`src/spec_dock/assets/install_root/` は installed agent-tooling assets の source of truth である。実装はここから始める。

### 2.2 Dogfood workspace

`spec-dock/` 配下の active Issue docs は dogfooding evidence であり、installed skill implementation source ではない。必要に応じて install / update simulation で dogfood surface を確認するが、skill source は provider-side install_root に置く。

### 2.3 Install behavior

Existing installer behavior recursively installs files from `src/spec_dock/assets/install_root/`. Therefore, the primary install task is adding the new skill directory and any tests / inventory assertions required to prove it is included.

If tests reveal an explicit managed skill allowlist, that allowlist must be updated. If install_root recursion already covers it, add or update inventory test evidence rather than adding unnecessary installer logic.

## 3. Skill Taxonomy

| Skill | Primary responsibility | ChatGPT authoring relationship | Stop gate |
|---|---|---|---|
| `spec-dock-initiative-planning` | Initiative requirement/design/plan and Epic decomposition | May use ChatGPT for high-depth decomposition evidence | Human approval before Epic node creation; fresh spec review before handoff |
| `spec-dock-epic-planning` | Epic requirement/design/plan and Issue slicing / draft handoff | May request ChatGPT ZIP/tree authoring pack for Epic docs and Issue drafts | Human approval before Issue node creation; draft-only Issues are not execution-ready |
| `spec-dock-issue-planning` | Issue requirement/design/plan formalization and execution handoff | Uses ChatGPT drafts in `draft-adoption` mode as evidence | Evidence Adoption Ledger + fresh spec review required before execution |
| `spec-dock-chatgpt-authoring` | Shared guidance for prompt pack, sync/local-context modes, ZIP/tree evidence, forbidden claims | Produces evidence only | Cannot adopt canonical docs, mutate assurance, claim reviewer pass, or claim readiness |

## 4. `spec-dock-chatgpt-authoring` Skill Design

### 4.1 Header

The skill header should be discoverable and concise:

```yaml
---
name: spec-dock-chatgpt-authoring
description: Shared evidence-lane skill for using ChatGPT / Oracle with SpecDock planning workflows, including sync/local-context modes, prompt packs, ZIP/tree outputs, validation, and adoption boundaries.
---
```

### 4.2 Read First

The new skill should point to:

- current active scope via `./spec-dock/scripts/spec-dock active show`
- relevant planning skill for the scope being authored
- parent / active requirement/design/plan/report
- Issue or Epic `artifacts/`
- authoring runtime command help:
  - `./spec-dock/scripts/spec-dock authoring --help`
  - `./spec-dock/scripts/spec-dock authoring preflight --help`
  - `./spec-dock/scripts/spec-dock authoring pack --help`
  - `./spec-dock/scripts/spec-dock authoring validate --help`

### 4.3 Operating Spine

The skill should guide agents to:

1. Resolve scope and target workflow.
2. Choose evidence mode.
   - `github-synced`: local branch is committed/pushed and connector-visible.
   - `local-context`: sync is intentionally unavailable; local files/diff are attached and output is lower-confidence evidence.
3. Prepare prompt pack and safe output contract.
4. Invoke configured backend only through approved local runtime / environment configuration.
5. Review / stage ZIP or tree output as evidence.
6. Validate candidates or draft adoption input.
7. Return to the relevant planning skill for canonical adoption.
8. Record EAL entries and reviewer gate status in `report.md`.

### 4.4 Forbidden Claims

The skill must explicitly reject output or workflow text claiming:

- canonical adoption completed
- canonical docs were written by ChatGPT / runtime validator
- `.assurance.json` mutation
- `authorized_profile` decision
- fresh `spec-reviewer`, `code-reviewer`, or `qa-reviewer` pass
- execution-ready
- PR-ready / merge-ready
- Issue finish
- Epic completion
- PR delivery

## 5. Updates to Existing Planning Skills

### 5.1 Initiative planning

Add a concise relationship note:

- ChatGPT authoring may be used for Initiative-level decomposition evidence.
- Initiative planning still owns canonical Initiative docs and Epic decomposition approval.
- Candidate Epic nodes require human approval before creation.
- Generated candidates are evidence-only until adopted.

### 5.2 Epic planning

Add a concise relationship note:

- ChatGPT authoring may produce Epic docs and Issue draft artifacts as ZIP/tree output.
- Epic planning owns Issue slicing and human approval before Issue node creation.
- Issue draft artifacts are handoff evidence only.
- Canonical Issue docs remain Issue planning outputs.

### 5.3 Issue planning

Add explicit modes:

| Mode | Starting point | Required adoption evidence |
|---|---|---|
| `zero-base` | user discussion, code/docs, artifacts | requirement/design/plan authored in order; fresh spec review for each promotion |
| `requirement-first` | approved or human-authored requirement | design/plan created from requirement; gaps return to requirement/clarification |
| `draft-adoption` | Issue-local draft requirement/design/plan from Epic planning or ChatGPT authoring pack | EAL entries for adopted/rejected draft claims; fresh spec review before execution |

This note must not make `draft-adoption` a shortcut around `spec-reviewer`.

## 6. Responsibility / Stop Gate Matrix

| Capability | ChatGPT authoring lane | Planning skill | Reviewer gate |
|---|---|---|---|
| prompt pack preparation | yes | chooses scope and constraints | no reviewer pass claimed |
| ZIP/tree output | yes | consumes as evidence | review/stage validation only |
| candidate validation | yes via runtime validation | decides creation proposal | human approval before node creation |
| draft artifact generation | yes | stores / indexes as evidence | not execution-ready |
| canonical requirement/design/plan adoption | no | yes | fresh `spec-reviewer` pass |
| `.assurance.json` mutation | no | assurance workflow only | verify after changes |
| execution-ready claim | no | issue planning after gates | spec-reviewer pass required |
| PR-ready / merge-ready claim | no | final quality issue / PR workflow | code/QA/check gates required |

## 7. Tests / Validation Design

Implementation should verify:

- New skill file exists in provider install_root.
- New skill has valid front matter and `name: spec-dock-chatgpt-authoring`.
- `uvx --from . spec-dock init <tmpdir>` or equivalent installer test installs the new skill.
- Existing planning skill names remain in install_root.
- `spec-dock-issue-planning` contains the three mode names.
- Touched skill docs contain evidence-only / forbidden-claim language.
- No touched shipped asset hardcodes `/Users/iwasawayuuta`, `.codex/skills/chatgpt-use`, or `oracle-chatgpt` as required product dependency.
- `spec-dock validate`, `assurance verify`, and `git diff --check` pass.

## 8. Failure Modes

| Failure mode | Expected mitigation |
|---|---|
| New skill is added under dogfood workspace only | Move to provider-side `src/spec_dock/assets/install_root/.agents/skills/` and prove install simulation. |
| Skill wording implies ChatGPT replaces planning skills | Rewrite as evidence-lane wording; planning skills retain canonical authority. |
| Issue planning mode wording makes draft adoption execution-ready | Require EAL entries and fresh spec-reviewer pass. |
| Local Oracle wrapper path becomes shipped dependency | Remove absolute path and describe configurable backend / operator local setup only. |
| Installer test misses skill inventory | Add focused inventory assertion or init/update simulation. |
| Broad workflow docs change expands into `iss-00306` scope | Keep only discoverability/index changes; defer broad guidance to `iss-00306`. |

## 9. Reviewer Focus

Spec reviewer should focus on:

- authority boundaries are explicit and non-contradictory
- `spec-dock-chatgpt-authoring` does not replace planning skills
- stop gates are preserved
- Issue planning modes are clear enough for future workflow use
- PR delivery remains deferred to `iss-00307`

Code reviewer should focus on:

- installed asset placement
- installer / inventory test correctness
- no hardcoded local wrapper dependency
- no unintended source/dogfood authority inversion

QA reviewer should focus on:

- install simulation proves consumer availability
- wording assertions cover the safety-critical claims
- existing skills are not renamed or lost

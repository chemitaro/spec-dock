---
種別: research
ID: "20260707t150325z-research"
タイトル: "ChatGPT workflow best practices final analysis"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295"]
関連: []
scope: "epic"
scope_id: "epic-00295"
created_at: "2026-07-07T15:03:25Z"
created_by: "codex"
status: "proposed"
authority: "evidence_only"
adoption_status: "unreviewed"
derived_from:
  - "ChatGPT Use session: specdock-chatgpt-workflow-best-practices"
  - "artifacts/20260707t143000z-interview-workflow-first-chatgpt-authoring-redesign-interview-1.md"
  - "artifacts/20260707t144547z-interview-human-approval-checkpoint-for-batch-planning-workflow.md"
  - "artifacts/20260707t140041z-01-research-chatgpt-workflow-integration-analysis.md"
  - "artifacts/20260707t140041z-research-authoring-pack-install-architecture-analysis.md"
  - "artifacts/20260707t143719z-research-workflow-first-chatgpt-authoring-redesign-provisional-analysis.md"
reflected_to:
  - "report.md#Evidence Adoption Ledger EAL-006"
---

# ChatGPT workflow best practices final analysis

## 位置づけ

この research は、ユーザー interview で確定した前提を含めて ChatGPT-Use / GPT-5.5 Pro Extended に依頼した最終分析の要約です。

前提:

- Option A「大きな仕事を一括で計画する体験」が第一優先。
- Option B「Issue 実行直前の正本化」は A の下流 continuation。
- Issue node 作成前の分解案承認だけを human approval checkpoint とする。
- Issue draft adoption / canonicalization は自動化対象とする。
- Epic requirement 作成には ChatGPT-generated path と human/Codex-authored path の両方を許容する。

## ChatGPT 実行メモ

- session: `specdock-chatgpt-workflow-best-practices`
- model: `gpt-5.5-pro`
- mode: Pro Extended
- files: 17
- prompt estimate: 約 62,160 tokens
- caveat:
  - GitHub connector では current branch `codex/authoring-pack-installed-runtime` が開けず、default branch `main` と添付 files を基準に分析した。
  - code patch、tests、`spec-reviewer`、runtime command 実行、installer packaging verification は未実施。

## Executive summary

ChatGPT の最終提案は、**ChatGPT Batch Evidence Lane** と **Codex Local Canonical Adoption / Execution Lane** の二車線設計である。

```text
large work
  -> Initiative / Epic planning
  -> Epic requirement/design/plan concretization
  -> Issue decomposition proposal + draft issue packs
  -> human approval before Issue nodes are created
  -> Codex creates Issue nodes and draft artifacts
  -> Epic Execution starts one Issue at a time
  -> Issue Planning(mode=draft-adoption) canonicalizes drafts
  -> fresh spec-reviewer gates
  -> Issue Execution implements
  -> PR delivery / issue finish gates
```

最初の deliverable は runtime scripts ではなく、`workflow_chatgpt_authoring_pack.md`、`spec-dock-chatgpt-authoring` skill、既存 Planning / Execution skills の mode update にするべき、という結論だった。

## End-to-end target workflow

### 基本状態遷移

```text
Input: large work / vague product objective / existing Epic requirement
  -> Scope routing
  -> Planning mode selection
  -> ChatGPT Batch Evidence Lane
  -> Codex Local Canonical Adoption Lane
  -> Human approval gate before Issue node creation
  -> Issue creation + draft artifact placement
  -> Epic Execution
  -> Issue Planning(mode=draft-adoption)
  -> Issue Execution
```

### Handoff-ready と execution-ready の分離

- Epic Planning から Issue へ渡す draft pack は `handoff-ready` の材料。
- Issue implementation を開始するには `execution-ready` が必要。
- `execution-ready` は Issue Planning が evidence 採否、canonical compose、fresh `spec-reviewer` pass、executable plan、verification、delegation contract、reviewer focus を揃えた状態。

## Workflow modes and use cases

### Initiative Planning: large-work portfolio mode

ChatGPT:

- outcome / user value / product boundary の構造化
- Epic candidate portfolio
- cross-Epic dependency / risk / sequencing
- rejected alternatives
- 初期 Epic requirement seed

Codex:

- 既存 Initiative / Epic fit の確認
- Initiative canonical docs への採否反映
- Epic node 作成判断
- `report.md` EAL / Spec Authoring Gate
- fresh `spec-reviewer`

### Epic Planning: full-batch mode

ChatGPT が Epic requirement/design/plan と Issue draft packs を batch 生成する path。

成果物:

- Epic requirement draft
- Epic design draft
- Epic plan draft
- Issue decomposition proposal
- per-Issue draft requirement/design/plan
- dependency proposal
- reviewer focus proposal
- risk / non-scope / follow-up proposal

### Epic Planning: requirement-first mode

Human/Codex が Epic requirement を先に固め、その approved requirement に基づいて ChatGPT が design/plan/Issue slicing/draft packs を生成する path。

これは product boundary が繊細な場合、または人間が requirement authority を強く持ちたい場合に使う。

### Issue Planning: zero-base mode

単体 Issue をゼロから作る mode。

- Codex の quick dialogue と `spec-dock-clarification` が主。
- ChatGPT は requirement が固まった後の design / plan brainstorm に限定。

### Issue Planning: draft-adoption mode

Epic handoff で渡された draft pack を、Issue canonical docs に正本化する mode。

- draft は evidence。
- EAL disposition を行う。
- canonical `requirement.md` / `design.md` / `plan.md` を作る。
- fresh `spec-reviewer` gate を通す。

### Epic Execution

one-Issue-at-a-time coordinator。

- active Issue があれば別 Issue を始めない。
- `deps check` / dependency order / priority / risk で 1 Issue を選ぶ。
- draft-only / unreviewed docs は Issue Planning へ route。
- reviewer-passed executable plan は Issue Execution へ route。

### Issue Execution

approved-plan-only execution。

- ChatGPT lane から切り離す。
- spec gap が出たら Issue Planning / clarification に戻す。

## Human approval and automation policy

### Human approval checkpoint

人間の明示承認は、**Epic-level concretization と Issue decomposition proposal の後、Issue node 作成前**に置く。

承認対象:

- Issue slicing
- Issue node creation decision
- proposed Issue list
- responsibility boundary
- dependency summary
- draft pack summary

承認対象ではない:

- 各 Issue の execution-ready
- `spec-reviewer` pass
- canonical docs adoption
- `.assurance.json`
- `authorized_profile`

### Report schema proposal

Epic `report.md` に `Issue Decomposition Approval Gate` を置く。

最小 fields:

- `gate_id`
- `source_pack_id`
- `source_artifact_paths`
- `target_epic_id`
- `proposed_issue_count`
- `issue_candidate_ids_or_titles`
- `dependency_summary`
- `draft_pack_summary`
- `approval_state`
- `approved_by`
- `approved_at`
- `approval_scope`
- `non-approved_items`
- `next_action`

`approval_state=approved` になって初めて `spec-dock new issue --epic <epic-id> --title ...` を実行できる。

### Automation boundary

Issue node 作成後の Issue draft adoption は人間承認なしに自動化してよい。

ただし、以下は自動化できない。

- canonical adoption の自己主張
- fresh `spec-reviewer` pass の自己主張
- `.assurance.json` / `authorized_profile` authority
- execution readiness
- PR readiness
- issue finish / Epic completion

## ChatGPT vs Codex responsibility split

| 領域 | ChatGPT GPT-5.5 Pro Extended | Codex / local workflow | Human |
|---|---|---|---|
| 大規模理解 | 長文 context の整理、論点発見、候補生成 | source selection、prompt pack 作成、repo state 確認 | product priority / intent 判断 |
| Initiative/Epic 分解 | Epic/Issue candidate portfolio、dependency案、risk案 | 既存 fit、canonical docs 採用、node 作成 | Issue decomposition 承認 |
| Requirement | draft / concretization / alternatives | canonical rewrite、reviewer gate | scope / non-scope / AC 判断 |
| Design | architecture draft、diagram案、tradeoff | canonical rewrite、ADR routing、spec-reviewer | durable decision 承認が必要な場合 |
| Plan | implementation slice / verification案 | canonical plan、dependency mutation、runtime commands | high-risk plan approval |
| Issue draft adoption | draft consistency check、gap候補 | EAL disposition、assurance compose、fresh reviewer | 原則不要 |
| Execution | 原則使わない | file edits、commands、tests、reviewers、PR | destructive / external / risk acceptance |
| Authority | evidence-only | canonical authority / repo mutation / reviewer orchestration | product approval authority |

## Proposed skills and skill modes

### 新 skill

ChatGPT の推奨名:

```text
spec-dock-chatgpt-authoring
```

役割:

- ChatGPT Batch Evidence Lane の first-read skill。
- prompt pack / backend / ZIP review / staging / validation / EAL candidate の operational spine。
- authority boundary と forbidden claims を明示。
- planning leaf skills から呼ばれる cross-scope evidence producer。
- canonical adoption はしない。
- Issue execution はしない。

### 既存 skill 変更

`spec-dock-hub`:

- `spec-dock-chatgpt-authoring` route を追加。

`spec-dock-initiative-planning`:

- `batch-epic-portfolio` mode を追加。
- non-trivial Initiative planning では ChatGPT lane を検討。

`spec-dock-epic-planning`:

- `full-batch` mode を追加。
- `requirement-first` mode を追加。
- Issue decomposition proposal / draft issue pack / approval gate を first-class にする。
- canonical Issue docs は作らない。

`spec-dock-issue-planning`:

- `zero-base` mode。
- `draft-adoption` mode。
- split はまだしない。
- `draft-adoption` では EAL disposition -> compose/rewrite -> fresh reviewer -> execution handoff readiness。

`spec-dock-epic-execution`:

- draft-only Issue は `spec-dock-issue-planning(mode=draft-adoption)` へ route。
- ChatGPT lane は直接使わず、planning repair に戻す時だけ使う。

`spec-dock-issue-execution`:

- ChatGPT output を execution input として直接扱わない。
- spec gap は planning / clarification へ戻す。

## Planning workflow redesign

### Initiative Planning

1. existing Initiative / Epic fit を確認。
2. ChatGPT に `Initiative -> Epic portfolio` を batch 生成させる。
3. Codex が candidate を採否判断。
4. Initiative `requirement.md` / `design.md` / `plan.md` へ再記述。
5. fresh `spec-reviewer` pass。
6. bounded scope だけ Epic 作成。

Reject:

- ChatGPT 生成 Epic list をそのまま大量 `new epic`。
- cross-Epic product decision を Epic / Issue に押し込む。
- reviewer pass なしで Initiative plan 完了扱い。

### Epic Planning

#### full-batch path

```text
large work or rough Epic objective
  -> ChatGPT creates Epic requirement/design/plan + Issue draft packs
  -> Codex reviews candidate claims
  -> canonical Epic requirement
  -> fresh spec-reviewer
  -> canonical Epic design
  -> fresh spec-reviewer
  -> canonical Epic plan + Issue decomposition proposal
  -> fresh spec-reviewer
  -> human approval before Issue node creation
```

#### requirement-first path

```text
Human/Codex finalizes Epic requirement
  -> fresh spec-reviewer
  -> ChatGPT creates Epic design/plan + Issue draft packs
  -> Codex canonicalizes design
  -> fresh spec-reviewer
  -> Codex canonicalizes plan/decomposition
  -> fresh spec-reviewer
  -> human approval before Issue node creation
```

### Issue Planning

#### zero-base

Codex-led / clarification-first。

#### draft-adoption

```text
issue start
  -> read Epic handoff package + Issue-local draft artifacts
  -> classify stale / blocked / usable
  -> EAL disposition per claim
  -> compose/rewrite requirement/design/plan
  -> fresh spec-reviewer per phase
  -> report evidence gate
  -> execution-ready
```

## Execution workflow redesign

### Epic Execution

追加 wording 案:

```text
If the selected Issue has Epic-generated draft artifacts and lacks current reviewer-passed canonical docs, route to `spec-dock-issue-planning` in `draft-adoption` mode. Do not invoke ChatGPT directly from Epic Execution except to generate new planning evidence after routing back to the relevant planning skill.
```

### Issue Execution

現行 gate を緩めない。

- reviewer-passed docs と executable plan が必要。
- ChatGPT output は execution input ではない。
- spec gap は planning / clarification へ戻す。

## ZIP / multi-file output best practices

必須ルール:

1. Raw ZIP は repo 外 scratch に置く。
2. 展開先も repo 外または隔離領域に置く。
3. ZIP root は固定 root を要求する。
4. path traversal、nested archive、secret-looking content、absolute host path、raw transcript を reject。
5. ChatGPT output の `pass` は helper validation pass であり、SpecDock reviewer pass ではない。
6. staged artifact は EAL candidate であり、final `report.md` EAL row ではない。
7. canonical docs への反映は Codex が再記述する。
8. `adoption_status: unreviewed` を初期値にする。
9. stale source hash / branch / profile / skeleton mismatch は adoption block。
10. ZIP から直接 `.assurance.json`、`authorized_profile`、`requirement.md`、`design.md`、`plan.md` を上書きしない。

## Runtime command / script architecture

### Source-of-truth placement

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  commands/authoring.py
  application/authoring_pack/
  domain/authoring_pack/
  presentation/authoring_pack/

src/spec_dock/assets/spec_dock/docs/
  workflow_chatgpt_authoring_pack.md
  reference_authoring_pack_backend.md
  authoring/chatgpt-pack.md

src/spec_dock/assets/install_root/.agents/skills/
  spec-dock-chatgpt-authoring/SKILL.md
```

任意の thin wrapper:

```text
src/spec_dock/assets/spec_dock/scripts/authoring-pack/
  prepare_chatgpt_authoring_pack.py
  invoke_chatgpt_backend.py
  review_chatgpt_authoring_pack.py
  stage_chatgpt_authoring_pack.py
  validate_*.py
```

### Minimal command set

```text
./spec-dock/scripts/spec-dock authoring pack prepare
./spec-dock/scripts/spec-dock authoring backend invoke
./spec-dock/scripts/spec-dock authoring pack review
./spec-dock/scripts/spec-dock authoring pack stage
./spec-dock/scripts/spec-dock authoring validate epic-issue-candidates
./spec-dock/scripts/spec-dock authoring validate initiative-epic-candidates
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill
./spec-dock/scripts/spec-dock authoring approval check
```

### 作らない command

初期 `epic-00295` では以下を作らない。

```text
authoring adopt
authoring create-issues-from-zip
authoring mark-reviewer-pass
authoring set-authorized-profile
authoring issue-execution-ready
authoring pr-ready
```

## Best-practice wording

### ChatGPT authority boundary

```text
ChatGPT output is batch planning evidence, not SpecDock authority. It may propose requirements, designs, plans, Issue slices, draft artifacts, reviewer focus, and risk lists. It must not claim canonical adoption, `.assurance.json` authority, `authorized_profile`, fresh `spec-reviewer` pass, execution readiness, implementation completion, PR readiness, or issue/Epic completion.
```

### Batch Evidence Lane

```text
Use the ChatGPT Batch Evidence Lane for large-work planning, Initiative/Epic decomposition, Epic design/plan concretization, and Issue draft pack generation. The lane ends at reviewed/staged evidence and EAL candidates. Canonical adoption is a Codex/main-orchestrator action recorded in `report.md` and followed by fresh reviewer gates.
```

### Human approval gate

```text
Human approval is required after Epic-level concretization and Issue decomposition proposal, before actual Issue nodes are created. This approval covers the slicing and node creation decision. It does not make Issue draft packs execution-ready and does not replace Issue Planning, Evidence Adoption Ledger disposition, canonical docs, or fresh `spec-reviewer` gates.
```

### Issue Planning modes

```text
`spec-dock-issue-planning` has two modes:
- `zero-base`: create or repair Issue requirement/design/plan from local sources and user clarification.
- `draft-adoption`: adopt, partially adopt, reject, stale, or block Epic-generated draft evidence before composing canonical Issue docs.

Both modes end at canonical `requirement.md` / `design.md` / `plan.md`, `report.md` evidence, fresh `spec-reviewer` pass, and explicit execution handoff readiness.
```

### ZIP handling

```text
ZIP/tree output is never copied into canonical docs directly. Review and validate it first, stage only evidence candidates, then adopt at claim/section/artifact granularity through canonical rewrite and `report.md` Evidence Adoption Ledger.
```

### Runtime-first after workflow

```text
Runtime commands are derived from workflow needs. Do not add script surfaces merely because a helper exists. A command is justified only when a skill needs repeatable local observation, safety review, validation, staging, or backend invocation inside installed consumer repositories.
```

## Migration plan for epic-00295

### Phase 0: Epic docs を workflow-first に更新

- `requirement.md`: Option A primary / B downstream / human approval before Issue creation / provider asset install requirement。
- `design.md`: `ChatGPT Batch Evidence Lane + Codex Canonical Adoption Lane`。
- `plan.md`: migration sequence。
- phase ごとの fresh `spec-reviewer` gate。

### Phase 1: shipped docs

追加:

- `workflow_chatgpt_authoring_pack.md`
- `reference_authoring_pack_backend.md`
- `authoring/chatgpt-pack.md`

更新:

- `workflow_spec_authoring.md`
- `workflow_initiative.md`
- `workflow_epic.md`
- `workflow_issue.md`
- `phase_plan_epic.md`
- `phase_plan_issue.md`

### Phase 2: skills

追加:

- `spec-dock-chatgpt-authoring/SKILL.md`

更新:

- `spec-dock-hub`
- `spec-dock-initiative-planning`
- `spec-dock-epic-planning`
- `spec-dock-issue-planning`
- `spec-dock-epic-execution`

`src/spec_dock/cli.py` の `_MANAGED_SKILL_NAMES` に追加する必要がある。

### Phase 3: runtime command design

`spec_dock_runtime` に `authoring` command group を追加。

初期は `prepare/review/stage/validate/backend invoke` に限定し、`adopt` は作らない。

### Phase 4: wrapper / compatibility

optional installed wrapper を thin wrapper として追加。

### Phase 5: tests

最低限:

- `spec-dock init` 後に docs/skills/runtime authoring command が入る。
- `spec-dock update` 後に更新される。
- `./spec-dock/scripts/spec-dock authoring --help` が通る。
- backend 未設定は fail-closed。
- `SPECDOCK_CHATGPT_COMMAND` は shell injection されない。
- unsafe ZIP claims are rejected。
- ChatGPT output with `.assurance.json` / `authorized_profile` / reviewer pass claim is rejected。
- Issue candidate validation は human approval gate なしに issue creation-ready としない。
- `handoff-ready` と `execution-ready` を混同しない。
- stale source hash / branch / profile mismatch は adoption block。

### Phase 6: dogfood

```text
Epic requirement-first
  -> ChatGPT design/plan/Issue draft packs
  -> approval before Issue creation
  -> create 2-4 small Issues
  -> Issue Planning draft-adoption
  -> Issue Execution
```

## Risks and rejected alternatives

Reject:

- script-first redesign。
- ZIP を canonical docs として直接採用。
- ChatGPT に `authorized_profile` を決めさせる。
- 各 Issue draft adoption 前の人間承認。
- `spec-dock-issue-planning` の即時 split。
- backend を Oracle 固定。
- ChatGPT を Issue Execution 中の即席 spec 補完に使う。

## Open questions

1. 新 skill 名を `spec-dock-chatgpt-authoring` に固定するか、backend-neutral な `spec-dock-authoring-batch` にするか。
2. `Issue Decomposition Approval Gate` の schema を docs only にするか、runtime validator が読む structured block にするか。
3. `authoring approval check` を初期 runtime command に入れるか。
4. `draft-requirement` を Issue node 作成直後に必ず作るか。
5. `validate issue-draft-adoption` がどこまで semantic validation するか。
6. `selected-skeleton-fill` validation と `authorized_profile` selection の実行順。
7. ChatGPT pack metadata の stable schema version の配置。
8. Initiative-level execution coordinator を作るか。
9. `ORACLE_CHATGPT_COMMAND` fallback を shipped docs に残すか。
10. EAL candidate lint を runtime に含めるか。

## 採用候補

特に採用価値が高いもの:

- 二車線設計: `ChatGPT Batch Evidence Lane` と `Codex Canonical Adoption Lane`。
- `Issue Decomposition Approval Gate`。
- `spec-dock-chatgpt-authoring` skill。
- `spec-dock-issue-planning` の `zero-base` / `draft-adoption` mode。
- `authoring adopt` を作らない方針。
- 最初の deliverable を docs / skill / mode updates にする方針。

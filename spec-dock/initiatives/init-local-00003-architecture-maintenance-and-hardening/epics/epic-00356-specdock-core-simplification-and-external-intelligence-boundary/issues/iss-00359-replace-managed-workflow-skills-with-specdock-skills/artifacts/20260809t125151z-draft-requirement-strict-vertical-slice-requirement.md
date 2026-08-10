---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_requirement_draft"
title: "iss-00359 Replace Managed Workflow Skills with SpecDock Skills — Vertical Slice Requirement Draft"
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

# 1. Slice outcome

Agent / operator が、workflow state machine ではなく Storage Core と Authoring Kit を直接利用する二つの repo-local skill から、Current scope の理解、構造操作、明確化 evidence 作成までを end-to-end 実行できるようにする。

Target managed skill surface:

1. `spec-dock`
2. `spec-dock-grill-with-docs`

この Issue は skill file の横断置換だけではない。Skill contract、provider asset、docs pointer、external-capability failure、no-canonical-write behavior、tests、legacy handoff inventory を同じ Issue で閉じる。Installer の physical prune / distribution cutover は 360。

# 2. Current problem

exact source SHA の managed inventory は Hub、Clarification、Initiative / Epic / Issue Planning、Epic / Issue Execution、ChatGPT Authoring、manual planning、ADR、host adapters、PR helpers 等を含む。Docs は skill を operational authority とし、workflow / reviewer / Oracle / planning pack route を案内する。

この inventory は Storage Core + Authoring Kit という Target boundary と不整合であり、削除した Runtime workflow を skill layer から再実装する危険がある。

# 3. Observable value

Issue 後に provider / dogfood の skill test environment で確認できること:

- `spec-dock` が current scope、parent chain、canonical R/D/P、Artifact、dependency、CLI help を読み、構造操作を deterministic CLI へ委譲する。
- `spec-dock` は Initiative / Epic / Issue の planning / execution state machine を所有しない。
- `spec-dock` は Review、Assurance、Profile、EAL、Promotion、change-set submission status、Issue completion を判定しない。
- Agent は Authoring Kit Guide を直接参照できる。
- `spec-dock-grill-with-docs` は user が explicit に起動した場合だけ動く。
- Grill skill は local scope context を調べ、必要なら operator-owned external `grilling` / `domain-modeling` capability を利用し、exactly one scope-local evidence Artifact を生成する。
- Grill skill は R/D/P/ADR を自動変更しない。
- External capability がない、scope が不明、Artifact creation が失敗した場合は no canonical write で明示停止する。
- Output type は用途に応じ `research` / `interview` / `disc` / `decision-candidate` を使い、`analysis` を作らない。
- Skill docs は Current CLI / Guide path だけを参照し、removed command / workflow / provider-specific import へ fallback しない。
- Legacy managed skill list と removal / preservation handling が 360 へ渡る。

# 4. `spec-dock` contract

## Inputs

- repository-local `spec-dock/`
- Current active or explicit target
- R/D/P/Report / Artifact / `.meta.json`
- CLI `--help`
- Authoring Kit Guide
- user intent

## Responsibilities

- resolve scope and parent context
- identify canonical versus evidence files
- show dependencies / current selection
- invoke deterministic Core commands for structure mutations
- guide direct Markdown authoring under user control
- explain docs-only Planning Level
- stop on missing structural prerequisites
- preserve exact branch / repository context when required by caller

## Non-responsibilities

- choose model / provider
- run browser / Oracle as product-owned dependency
- impose Planning / Review / Execution workflow
- generate hidden authority metadata
- decide promotion into repository authority
- decide test sufficiency / quality gate
- create / monitor / repair / merge PR
- close Issue except through explicit Core command requested by operator
- invent new IDs or GitHub linkage without structural command

# 5. `spec-dock-grill-with-docs` contract

## Trigger

Explicit user / operator invocation. It does not automatically intercept planning.

## Read set

- target scope R/D/P/Report
- existing relevant Artifact
- parent / child boundary as needed
- dependency context
- Authoring Kit Guide
- local code/docs only when user intent requires

## Process

1. Resolve target and purpose.
2. Gather facts without changing canonical documents.
3. Identify ambiguity / conflicting assumptions.
4. Use external clarification capability only if available and explicitly permitted by the execution environment.
5. Produce one synthesis with Facts、Decisions supplied by user、Alternatives、Open Questions、Authoring Brief。
6. Create exactly one scope-local Artifact using Current Core syntax.
7. Report artifact path / type and state that canonical reflection is a separate human-controlled action.

## Failure

- capability unavailable → explicit no-write result
- target ambiguous → explicit no-write result
- Core Artifact command fails → no fallback direct unsafe write
- derived recommendation lacks evidence → label as candidate
- never claim adopted / successful review outcome / implementation authorization

# 6. Artifact choice

| Situation | Type |
|---|---|
| single-source factual investigation | `research` |
| unresolved questions / user answers | `interview` |
| multi-source synthesis / trade-off | `disc` |
| concrete but unadopted durable option | `decision-candidate` |
| accepted architecture decision authoring requested separately | `adr` under ADR contract, not automatic grill output |
| free-form | `blank` when no stronger semantic type applies |

`analysis` is forbidden as a Current type.

# 7. In scope

- provider and dogfood skill sources
- two skill contracts and examples
- Guide / CLI references
- external capability boundary
- no-canonical-write behavior
- one-Artifact output behavior
- skill tests / static contract tests / negative tests
- old managed skill inventory
- docs explaining new entrypoints
- handoff to 360
- compatibility note for existing user-installed skills

# 8. Out of scope

- Runtime command implementation
- Authoring Guide prose ownership
- external skill installation / vendor code
- installer prune / update / uninstall
- historical skill file deletion in consumer
- PR workflow
- final full regression / change-set handoff
- canonical document auto-apply

# 9. Dependencies

- 357 supplies retained CLI inventory、Artifact syntax、active / dependency / lifecycle semantics。
- 358 supplies Guide paths、scope layering、Planning Level、Artifact semantics、authority hierarchy。
- Skill implementation must not start from placeholder assumptions if either contract changes at IC-1.

# 10. Compatibility

- Existing repositories may still contain old skill directories until 360 update / uninstall.
- This Issue supplies exact obsolete managed list and collision / ownership expectations.
- New skills do not call old skills as fallback.
- Historical docs / reports referring to old skills remain evidence.
- Existing external third-party skills are operator-owned and not deleted by provider inventory unless explicitly managed by SpecDock ownership.
- Skill names, paths, front matter, host discovery rules must be tested in provider / dogfood layout.

# 11. Acceptance criteria

Future verification criteria:

1. Provider / dogfood target has exactly the two SpecDock product skills defined by this slice, subject to 360 packaging transition.
2. `spec-dock` uses retained Core commands and Authoring Kit Guide paths only.
3. `spec-dock` contains no Planning / Review / Execution / Assurance / PR workflow state machine.
4. `spec-dock-grill-with-docs` requires explicit invocation and produces at most one Artifact.
5. Grill never modifies canonical R/D/P/ADR automatically.
6. Missing external capability、ambiguous scope、command failure are no-write failures.
7. No skill creates `analysis` or provider-specific imported Artifact.
8. Skill tests verify current scope resolution、canonical/evidence distinction、dependency context、CLI delegation、no-go behavior。
9. Static scans find no removed command names / old skill fallback / provider-owned Oracle requirement in Current skill sources.
10. Docs identify external Intelligence as replaceable operator-owned client.
11. Obsolete managed skill / adapter / PR helper inventory is complete and handed to 360.
12. Existing user-owned skill paths outside managed ownership are not selected for deletion.

# 12. Negative requirements

- Do not merge both skills into a hidden workflow coordinator.
- Do not make grill mandatory before R/D/P edits.
- Do not treat skill output as canonical.
- Do not invoke arbitrary external service from Runtime.
- Do not silently fall back to old skills.
- Do not recreate `spec-dock-chatgpt` planning pack behavior.

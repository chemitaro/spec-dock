---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_requirement_draft"
title: "iss-00358 Simplify Authoring Kit and Document Contracts — Vertical Slice Requirement Draft"
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

# 1. Slice outcome

利用者が特定の model、Skill、workflow state、Assurance Profile に依存せず、Fresh Initiative / Epic / Issue の `requirement.md`、`design.md`、`plan.md`、薄い `report.md` を読み書きし、必要な Guide へ到達できる Authoring Kit を提供する。

この Issue は template だけを横断的に編集する作業ではない。Fresh node を作成し、文書責務を理解し、Issue Plan の depth を選び、Artifact evidence を durable decision へ反映する end-to-end authoring experience を、templates、guides、navigation、tests、projection、migration / compatibility まで同じ Issue で閉じる。

# 2. Current problem

exact source SHA の Current assets には次が混在する。

- Requirement / Design / Plan template に Grade、Reviewer Gate、Promotion、EAL、Delegated Authoring、change-set submission status 等の workflow policy が埋め込まれている。
- Issue Design / Plan scaffold は Assurance classification / compose を前提とする。
- Issue profile template と `draft-*` routing が存在する。
- `report.md` は大規模な ledger / gate scaffold である。
- docs entrypoint は skill、phase promotion、fresh reviewer、ChatGPT authoring pack を正規導線として案内する。
- Current / Historical Artifact catalog が分離されていない。
- Planning Level の user-adopted docs-only structure が canonical templates / guides に反映されていない。

# 3. Observable value

Issue 後に利用者が確認できるべきこと:

- Fresh Initiative / Epic / Issue に single `requirement.md`、`design.md`、`plan.md`、`report.md` がある。
- 各 template は完成文書に残る headings と短い prompt だけを持ち、workflow policy を複製しない。
- `report.md` は Outcome、Verification、Residual Risks / Follow-ups の 3 section、必要なら Notes の 4 section目だけを持つ。
- Report 内容は optional、空でも valid、workflow authority ではない。
- Common Authoring Overview と Requirement / Design / Plan / Report Guide が存在する。
- Scope Layering Guide が Initiative / Epic / Issue の責務差を説明する。
- Issue `plan.md` は一つだけである。
- Base Plan Guide と `light`、`standard`、`strict`、`critical` Completion Guide が独立に参照できる。
- Planning Level は `plan.md` 本文に選択・理由・再評価条件を書く docs-only concept である。
- Current Artifact catalog は `blank`、`research`、`interview`、`disc`、`decision-candidate`、`adr` の六つ。
- `analysis`、repair badge、`draft-*`、`pr-repair-batch` は Current creation / navigation に現れない。
- Historical evidence の存在と読み方が説明され、削除・rename・validation failure を要求しない。
- Durable decision の置き場は R/D/P または accepted ADR、Artifact は evidence、Report は result summary と説明される。
- Provider source と dogfood projection の asset catalog、links、bytes / normalized content が検証できる。
- Existing consumer の node-local R/D/P/Report/Artifact は template update で書き換わらない。

# 4. Document responsibility contract

## `requirement.md`

- Problem、why now、stakeholder / user outcome
- scope / non-scope
- observable behavior
- constraints、compatibility、acceptance
- risks / assumptions / open human decisions

実装順、class / module design、test implementation detail は置かない。

## `design.md`

- Current / Target architecture
- responsibility boundary
- data / interface / failure contract
- migration / compatibility strategy
- testability / observability design
- meaningful diagrams where useful

Business acceptance を再定義せず、Requirement を実現する構造を扱う。

## `plan.md`

- Planning Level selection as prose
- vertical implementation sequence
- dependency / parallelism
- verification strategy
- migration / rollback
- completion / exit criteria
- handoff / residual risk

Design decision を新たに隠して決めず、durable change は Design へ戻す。

## `report.md`

- Outcome
- Verification
- Residual Risks / Follow-ups
- optional Notes

Decision ledger、EAL、Objective Alignment Ledger、Authoring Gate、Reviewer Status、Delegated Draft Evidence、Promotion、Completion Gate を Fresh template に含めない。

# 5. Planning Level contract

| Level | Intended use | Completion emphasis |
|---|---|---|
| light | 局所的・低 blast radius・容易な revert | direct AC、targeted verification、残作業なし |
| standard | 通常 feature / bug fix | E2E sequence、major errors、regression、basic rollback |
| strict | public contract、Runtime、data、migration、compatibility | As-Is / To-Be、failure modes、negative tests、rollback / forward recovery |
| critical | security / privacy、高 blast radius、不可逆・困難な回復 | threat / data、staged rollout、kill switch、backup / restore、incident response |

Common rules:

- Level は文章量ではなく failure impact / recovery difficulty で選ぶ。
- Priority、severity、dependency readiness、implementation handoff status を意味しない。
- Runtime は parse / validate / persist / route / enforce しない。
- `.meta.json` へ書かない。
- Level変更は Markdown + Git diff。
- selected Guide は Base Guide への独立差分。Critical を読むために Standard / Strict の順読を強制しない。
- 未指定時 `standard` は authoring recommendation にできるが Runtime default ではない。

# 6. Artifact semantics

| Type | Use | Durable reflection |
|---|---|---|
| `blank` | 弱い template の自由形式 evidence | 必要な内容を R/D/P/ADR へ再記述 |
| `research` | source-grounded single investigation | facts / constraints を適切な canonical section へ |
| `interview` | explicit questions and answers | adopted answer を R/D/P/ADR へ |
| `disc` | multiple evidence の synthesis / trade-off | durable conclusion を R/D/P/ADR へ |
| `decision-candidate` | 未採用 decision option | human disposition 後に R/D/P/ADR へ |
| `adr` | architecture decision candidate / record | accepted status の ADR が durable authority |

`analysis` は追加しない。Single-source investigation は `research`、multiple-source synthesis は `disc`。

# 7. In scope

- Initiative / Epic / Issue R/D/P/Report templates
- Authoring overview
- Requirement / Design / Plan / Report Guide
- Scope Layering Guide
- Artifact Guide / rules
- one Plan template
- Base Plan Guide + four Completion Guides
- Current / Historical navigation
- Provider / dogfood asset projection
- template / link / catalog / vocabulary / parity tests
- existing consumer preservation fixtures
- removed docs / templates inventory
- 357 / 359 / 360 handoffs

# 8. Out of scope

- Runtime parser / registry / lifecycle / dependency / artifact filename implementation
- node scaffolder mechanism
- repo-local skill content
- installer prune execution
- existing node-local document rewrite
- external Intelligence
- runtime quality gate
- new Artifact type
- multiple Plan files
- final release / change-set handoff

# 9. Compatibility

- Template changes apply to Fresh node creation only.
- Existing R/D/P/Report bytes are preserved by update.
- Existing `.assurance.json`、profile-derived docs、draft / repair / legacy discussion remain historical evidence.
- Current docs stop routing users to obsolete workflow, but historical docs need not be deleted from user repositories.
- Provider source may delete obsolete managed template sources only when 360 packages the prune; 358 supplies exact inventory.
- Broken links are not tolerated in Current navigation.
- Historical vocabulary is allowed in explicitly Historical pages / fixtures, not in Current contract pages.

# 10. Acceptance criteria

Future verification criteria:

1. All three scopes have thin R/D/P/Report templates.
2. Fresh Issue has exactly one `plan.md`.
3. Base Plan Guide and four Completion Guides exist with valid links and no common-rule duplication.
4. Initiative / Epic plans do not require Issue Planning Level.
5. Fresh Report has 3–4 sections、content optional、empty-valid、non-gating language。
6. Current six Artifact types have distinct purposes; `analysis` is absent.
7. repair badge、`draft-*`、`pr-repair-batch` are absent from Current creation and navigation.
8. Durable decision guidance points to R/D/P or accepted ADR.
9. Current templates / guides do not require Grade、Reviewer Gate、Promotion、EAL、Delegated Authoring、change-set submission status。
10. Provider / dogfood asset catalogs match.
11. Link / forbidden-current-vocabulary / exact inventory tests pass.
12. Existing consumer canonical docs / reports / historical evidence remain unchanged in preservation fixture.
13. IC-1 contract with 357 is satisfied.
14. Guide paths and semantic summary are handed to 359; obsolete managed asset inventory is handed to 360.

# 11. Negative requirements

- Do not create `plan-light.md`、`plan-standard.md` 等。
- Do not add Planning Level metadata or parser.
- Do not make Report presence/content a completion gate.
- Do not promote Artifact automatically.
- Do not reintroduce Model / Provider / Prompt requirements through Guide wording.
- Do not hide policy in Template comments that users must delete.
- Do not remove historical user content.

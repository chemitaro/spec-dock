---
種別: 実装計画書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
Issue Grade: "strict"
状態: "approved"
作成者: "Blue Team"
最終更新: "2026-07-27"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00331", "init-00322"]
planning_profile_guidance_source: "Main-supplied current guidance; no assurance mutation by Candidate"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — Issue 実装計画書（Strict / Spec-Locked TDD）

## 0. 文書の位置づけ

本書はcanonical planned executable workflow contractである。実績、逸脱、Review結果、commit evidenceはcanonical `report.md`へMainが記録する。Candidate provenanceは`report.md`へ分離し、このPlanの存在だけではfresh reviewer passまたはimplementation startを許可しない。

Mainは実装開始前に既存assurance workflowを実行する。Runtimeの`authorized_profile=standard`を保持しつつ、public command、archive security、multi-file recovery、credentialed live dogfoodのIssue-local riskに対して`strict` obligationsを手動強化する。本Planはassurance authorityを自己付与せず、強化理由、delta、revert conditionを`report.md`へ記録する。

## 1. この計画で満たす要件ID

`REQ-001`〜`REQ-024`、`AC-001`〜`AC-017`、`EC-001`〜`EC-010`。ID数自体はproduct acceptanceではなく、Requirement本文のmeaningとobservable behaviorがauthorityである。

## 2. Plan Readiness and Stop Gate

Implementationは次がすべて成立するまで開始しない。

- one exact `ReviewedPlanningIdentityV1`が次のどちらかとして確定していること。
  - archive-candidate: exact logical filename、observed transport filename、ZIP SHA、internal root、Candidate ID、source repository／branch／HEAD。
  - git-bound: exact repository、branch、reviewed HEAD、sorted unique target paths、必要なbase。
- 上記identity objectと`reviewed_identity_sha256`へbindされたfresh `PlanningReviewResultV1`があり、`reviewer_role=spec-reviewer`、`freshness=fresh`、`authority=read-only`、`verdict=pass`であること。
- 同じidentity object／digestおよびexact Review-result file SHAへbindされた`PlanningHumanDecisionV1`があり、`decision=approved`、`plan_adoption=true`、`implementation_start=true`であること。
- archive identityをgit-bound identityとして、またはgit-bound identityをCandidate identityとして再解釈していないこと。mode切替、waiver、silent fallbackはnew reviewed identityとfresh Review／Human decisionなしでは禁止する。
- Mainによるcanonical adoption／source refresh／assurance classification and compositionが完了していること。
- adopted `requirement.md`／`design.md`／`plan.md`とfresh spec review evidenceが一致していること。
- clean named branch、upstream、local HEAD == remote HEAD、no unresolved ledger entryであること。
- planning repair baseline `eadbfa544ad972c799162552f5684482d26e89b5`以降のrelevant implementation source manifestにdriftがないこと。planning docs／report／assuranceだけのcommitであっても、current三文書hash、reviewed identity、Review result、Human decisionをcurrent HEADへ再束縛すること。
- archive Candidate source、git-bound reviewed HEAD／target blobs、またはimplementation-relevant sourceがReview後に変化した場合は`stale`とし、new Candidateまたはnew git-bound Review identityを取得すること。

不足時は`blocked`、`stale`、`rejected`、または`未完了`としてMainがreason／next actionをCandidate外reportへ記録する。

## 3. Implementation Strategy

- one observable behavior per implementation step。
- provider-first。root dogfood projectionを直接編集しない。
- Mainはinspect／plan／delegate／verify／integrate／reportを所有し、product code／tests／shipped docsを通常は直接実装しない。
- code/runtime/testsは`dev-coder`、shipped docs／Skill／Prompt textは`doc-writer`へ委任する。
- each step: closure contract → delegation → bounded batch → verification → tidy → Main report integration → fresh reviewer → Result Approval → commit candidate → clean check。
- unknown failure、new authority、shared policy change、scope expansionは実装で吸収せずamendment／owning scopeへ戻す。

## 4. Scope and Change Surface

### Allowed provider surfaces

- `src/spec_dock/cli.py`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/**`の本Planで列挙したPlanning docs
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/**`
- `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`の本Planで列挙したPlanning modules
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`のS05 bounded additive extension
- focused `tests/**` paths listed per step
- `pyproject.toml` only if packaging declaration is required by S07

### Forbidden changes

- current Portfolio boundary／dependency。
- downstream Issue Requirement／Design／Plan。
- `.assurance.json`。
- shared Issue delivery／merge／finish／lifecycle authority。
- root generated `spec-dock/` direct implementation edits。
- arbitrary legacy removal owned by E1-I3。
- new workflow database、receipt registry、custom Git ref、または新しいpersistent coordination subsystem。

## 5. Dependency-derived Order

```text
S01 CLI shell
 → S02A official Skill / closed Prompt authority
 → S02B Skill / Prompt structural tests
 → S03 Planner response / Git preflight
 → S04 revise response
 → S05 Runtime Candidate packaging / Review / archive integrity
 → S06 Human gate / adoption / publication / readiness
 → S07 installer / projection
 → S08 integrated compatibility
 → S09A hermetic dogfood contract
 → S09B Main/Human live dogfood gate
 → S90 docs impact resolution
 → S99 final quality gate
 → Final Exit via current shared delivery workflow
```

## 6. Step Summary

| Step | Outcome | Depends on | Unblocks | Related AC |
|---|---|---|---|---|
| S01 | Independent CLI walking skeleton including public `planning apply` help contract and exact positive／negative Issue target resolution | mode-neutral exact reviewed planning identity、fresh `PlanningReviewResultV1` pass、same-identity `PlanningHumanDecisionV1` approval for Plan adoption and implementation start | S02A | AC-002, AC-003 (target-resolution portion) |
| S02A | Official Skill and closed Prompt resources | S01 | S02B | AC-001, AC-011 |
| S02B | Skill／Prompt inventory and route structural tests | S02A | S03 | AC-001, AC-011 |
| S03 | Git-bound Planner response flow | S02B | S04 | AC-003, AC-011 |
| S04 | Semantic and mechanical revision response | S03 | S05 | AC-004 (revision-lane behavior) |
| S05 | Runtime Issue Candidate packaging, read-only Planning Review, and archive integrity | S04 | S06 | AC-001, AC-004, AC-005, AC-006, AC-007, AC-017 |
| S06 | Human gate, adoption, publication, and derived readiness | S05 | S07 | AC-008, AC-009, AC-010, AC-013 |
| S07 | Installer and provider projection | S06 | S08 | AC-012, AC-015 |
| S08 | Integration, compatibility, and adoption negatives | S07 | S09A | AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-015 |
| S09A | Hermetic dogfood selection／abort／recovery contract | S08 | S09B | AC-014 |
| S09B | Main/Human-owned live dogfood operation gate | S09A | S90 | AC-014 |
| S90 | docs／Skill／reference impact resolved | S09B | S99 | AC-001, AC-012, AC-015 |
| S99 | final QA/code/spec quality evidence | S90 | Final Exit | all |

## 7. 要件 ↔ ステップ対応

| Requirement group | Owning implementation step(s) |
|---|---|
| Official Skill／CLI／Prompt | S01, S02A, S02B |
| Planner response／revision lane | S03, S04 |
| Runtime final Candidate packaging／Dual Review／archive safety | S05 |
| Human Gate／adoption／publication／readiness | S06 |
| Provider/install/update parity | S07 |
| Integrated regression／PA-NF | S08 |
| Hermetic live-operation contract | S09A |
| Human-selected real-use validation／metrics | S09B |
| Docs/Skill reference alignment | S90 |
| Final test sufficiency／integrated diff／spec conformance | S99 |
| PR delivery／Human merge | Final Exit, external shared workflow |

## 8. Spec-Locked Closure Index

この索引はmaterial obligationsのbounded coverage ledgerであり、全test implementation inventoryやglobal proof registryではない。

### 8.0 Closure graph semantics

`required=no` summary rowはnavigation aliasだけである。

- summary aliasはClosure ownerを持たない。
- summary aliasはowner portion、state、aggregate stateを持たない。
- summary aliasをstep closure contract、S99 closure target、Report closure-state rowとして`open`、`passed`、`failed`、`blocked`、`closed`へ遷移させない。
- test cardはsummary aliasをnavigation referenceとして記載できるが、required closure evidenceの代用にしない。

`required=yes` individual rowだけがexecutable closure nodeである。

Allowed owner order:

```text
S01
< S02A
< S02B
< S03
< S04
< S05
< S06
< S07
< S08
< S09A
< S09B
< S90
< S99
```

`Final Exit`はClosure ownerではない。

- single-owner rowは一つのowner portionを持つ。
- multi-owner rowは上記step orderでsortedされた独立owner portionsを持つ。
- owner portion stateの許可値は`open`、`passed`、`failed`、`blocked`だけである。
- stepはClosure Indexで自身がownerとして列挙されたportionだけを更新できる。
- aggregate stateは全owner portionが`passed`のときだけ`closed`。一つでも`open|failed|blocked`なら`open`。
- 後続drift、invalidated evidence、failed re-reviewは該当portionを再openし、aggregateを再openする。
- step-local testだけ、reviewerだけ、commit候補だけではportionを`passed`にしない。required evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkをすべて要求する。

S99 entryでは、ownerがS01〜S90の全portionが`passed`であることを要求する。S99-owned portionはentry時点で`open`でよい。S99が自身のportionを`passed`にした後、全`required=yes` aggregateが`closed`であることを再計算し、そこで初めてFinal Exitをunblockする。

MainはReportへ次のexact fieldsをowner portionごとに記録する。

```text
closure_id
closure_owner
owner_portion_state
observed_evidence
reviewer_verdict
commit_or_approved_noop
post_commit_clean
recorded_at_head
```

### Summary aliases — navigation only

| Closure ID | Spec link | Navigation meaning | Required | Closure owner | Evidence alias |
|---|---|---|---|---|---|
| `CLOS-CLI` | REQ-002 / AC-002 | command family and parser | no | — | `tc-s01-001`, `tc-s01-004` |
| `CLOS-CREATE` | REQ-004 / AC-001,004 | Planner response and Candidate package | no | — | `tc-s05-001`, `tc-s05-003`, `tc-s05-006` |
| `CLOS-GIT` | REQ-003 / AC-003,017 | Git/source preflight | no | — | `tc-s01-003`, `tc-s03-002` |
| `CLOS-SEC` | REQ-021 / AC-011 | direct argv and prohibited-content preflight | no | — | `tc-s03-003`, `tc-s03-004` |
| `CLOS-REVISION` | REQ-007 / AC-004 | semantic／mechanical revision | no | — | `tc-s04-001`, `tc-s04-002` |
| `CLOS-REVIEW` | REQ-006,008 / AC-005,007 | read-only dual-mode Review | no | — | `tc-s05-001`, `tc-s05-005` |
| `CLOS-ARCHIVE` | REQ-010,022 / AC-006 | Candidate controls and archive safety | no | — | `tc-s05-003`, `tc-s05-004[*]`, `tc-s05-006[*]` |
| `CLOS-ADOPTION` | REQ-009–012 / AC-008,009 | approved adoption／rejected decision record | no | — | `tc-s06-001`, `tc-s06-002`, `tc-s06-009`–`tc-s06-012B` |
| `CLOS-READINESS` | REQ-013,014 / AC-010,013 | typed readiness conjunction and exact non-ready statuses | no | — | `tc-s06-003[*]`, `tc-s08-003[*]` |
| `CLOS-SKILL` | REQ-001,005 / AC-001,011 | Skill／Prompt route | no | — | `tc-s02a-001`, `tc-s02b-001` |
| `CLOS-PROJECTION` | REQ-017,023 / AC-012,015 | install/update projection | no | — | `tc-s07-001`, `tc-s07-002` |
| `CLOS-INTEGRATION` | REQ-019,023 / AC-015 | fake-remote integration and compatibility | no | — | `tc-s08-001`, `tc-s08-002`, `tc-s08-003` |
| `CLOS-DOGFOOD` | REQ-018,024 / AC-014 | hermetic and Human/Main dogfood gates | no | — | `tc-s09a-001`, `tc-s09b-001` |
| `CLOS-DOCS` | REQ-020 / AC-016 | docs and delivery-boundary alignment | no | — | `tc-s90-001` |
| `CLOS-QUALITY` | AC-001–017 / EC-001–010 | final issue-wide quality | no | — | `tc-s99-001`, `tc-s99-002` |

### 8.1 Requirement and Acceptance Closure

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence / verification | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-REQ-001` | REQ-001 / AC-001 | Human invokes official Skill | Skill reaches create/review/revise/apply route | bypass／legacy entry | S02A/S02B | yes | inspect-only + red-required | `tc-s02a-001`, `tc-s02b-001` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-002` | REQ-002 / AC-002 / Design §3 | CLI help and parser argv matrix | four commands; exact archive/git review/apply options; repository/branch derived; mode options closed | lifecycle available only through internals／placeholder argv | S01 | yes | red-required | `tc-s01-001`, `tc-s01-004` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-003` | REQ-003 / AC-003,017 | repo／branch／HEAD／upstream／tree | exact Git binding before backend or mutation | stale／dirty／default fallback | S03 | yes | red-required | `tc-s03-001`, `tc-s03-002` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-004` | REQ-004 / AC-001,004 / Design §4.2 | complete three-doc response and four exact controls | canonical v1 control bytes, exact inventory/checksums/cross-file binding, no overwrite | schema-divergent／identity-inconsistent artifact | S03/S05 | yes | red-required | `tc-s05-001`, `tc-s05-003`, `tc-s05-006[*]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-005` | REQ-005 / AC-011 | prompt resource selection | declared provider resources only | raw override／prompt injection | S02A/S02B | yes | red-required | `tc-s02b-002` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-006` | REQ-006 / AC-005 / Design §§3,4.3 | explicit Review mode and full parser identity | archive identity or git identity with exact Issue/base; no silent fallback／reuse | cross-mode／base-field evidence reuse | S05 | yes | red-required | `tc-s05-005`, `tc-s01-004` + archive positive | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-007` | REQ-007 / AC-004 | semantic／mechanical revision input | complete replacement or closed bounded edit creates new identity | semantic drift hidden in mechanical lane | S04 | yes | red-required | `tc-s04-001`, `tc-s04-002` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-008` | REQ-008 / AC-007 | pre/post Candidate and Git inventory | reviewer writes only separate result | Candidate／repo mutation | S05 | yes | red-required | `tc-s05-001` mutation assertions | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-009` | REQ-009 / AC-008,009 / Design §§3,4.3–5.1 | exact CLI identity + Review v1 + Human decision v1 | approved full apply; rejected decision-record; both modes admitted without reinterpretation | ad-hoc call／Candidate-only gate／undurable rejection | S01/S06 | yes | red-required | `tc-s01-004`, `tc-s06-001`, `tc-s06-002`, `tc-s06-009`–`tc-s06-012` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-010` | REQ-010 / AC-008 / Design §5.1 | archive identity and canonical targets | staged validation, fixed-order replacement, parity, rollback | mixed canonical bytes | S06 | yes | red-required | `tc-s06-001`, `tc-s06-004`, `tc-s06-005` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-011` | REQ-011 / AC-009 | reviewed HEAD／paths and blobs | git-bound blobs remain exact; approval-only diff | post-review semantic mutation | S06 | yes | red-required | `tc-s06-002` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-012` | REQ-012 / AC-008,009 | H0/H1/local/remote/tree | push success yields parity; failure is resumable | commit loss／force/reset recovery | S06 | yes | red-required | `tc-s06-006`, `tc-s06-007` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-013` | REQ-013 / AC-008–010,013 | all named readiness and status conditions | only full approved conjunction returns `ready`; each named non-ready condition has one exact status／reason; stage-only orphan is not false recovery | partial gate／nondeterministic status／false recovery | S06/S08 | yes | red-required | `tc-s06-003[11 fixtures]`, `tc-s06-012A`, `tc-s06-012B`, `tc-s08-003[11 fixtures]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-014` | REQ-014 / AC-010 | PA-NF-01〜09、10A、10B | 11／11 exact status、exit 1、allowed mutation only | grouped negative hides validation or publication gap | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-01..10b]`, `tc-s08-003[pa-nf-01..10b]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-015` | REQ-015 / AC-013 / Design §§4.4–5.1 | exact Review bytes／Human decision bytes／decision artifact／publication | approved adoption or durable rejected decision-record; revoked unsupported; no authority registry | evidence substitution／false revocation／partial approval | S06 | yes | red-required | `tc-s06-009`, `tc-s06-010`, `tc-s06-011`, state-boundary assertions | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-016` | REQ-016 / AC-013 | `.assurance.json` before/after candidate flow | product flow leaves assurance unchanged | hidden profile mutation | S06/S08 | yes | red-required | state-boundary fixture | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-017` | REQ-017 / AC-012 | provider/wheel/sdist/fresh/update/dogfood bytes | provider-first parity | generated tree as authority | S07 | yes | red-required | `tc-s07-001`, `tc-s07-002` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-018` | REQ-018 / AC-014 / Design §13 | eligible target + explicit Human authority | hermetic gate first; Main alone runs live chain | worker-owned credentialed mutation | S09A/S09B | yes | manual-required | `tc-s09a-001`, `tc-s09b-001` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-019` | REQ-019 / AC-015 / Design §§5.1,8 | archive/runbook/transaction primitives | bounded shared reuse with characterization Green | duplicated safety subsystem | S05/S06/S08 | yes | covered-existing + red-required | archive default + runbook + scoped transaction suites | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-020` | REQ-020 / AC-016 | one Issue／branch／Delivery PR contract and pre-handoff evidence | S90 aligns docs; S99 verifies final branch／handoff preconditions; Final Exit owns no Closure portion | delivery cycle／Final Exit circularity／issue-level policy rewrite | S90/S99 | yes | inspect-only + final-required | `tc-s90-001`, `tc-s99-001`, `tc-s99-002` | `report.md#Final-Quality-Gate` |
| `CLOS-REQ-021` | REQ-021 / AC-011 | benign metacharacter and prohibited sentinel fixtures | benign values remain argv elements; prohibited content rejected before backend call | shell injection／secret disclosure to backend | S03/S08 | yes | red-required | `tc-s03-003`, `tc-s03-004`, integrated security fixture | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-022` | REQ-022 / AC-006 | every archive matrix row | inclusive ceilings pass; every prohibited class rejects; outputs 0 | incomplete archive safety coverage | S05 | yes | red-required | `tc-s05-004[arc-01..25]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-023` | REQ-023 / AC-015 | Core CLI/generic archive/lifecycle behavior | additive route and existing behavior Green | compatibility regression | S05/S07/S08 | yes | covered-existing | `tc-s05-002`, `tc-s08-002` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-024` | REQ-024 / AC-014 | representative run metrics | intervention, bytes, invocations, result, time, failure recorded outside Candidate | unobservable dogfood | S09B | yes | manual-required | `tc-s09b-001` evidence artifact | `report.md#Test-Contract-Closure` |

### 8.2 Error-condition Closure

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence / verification | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-EC-001` | EC-001 | named target／Git fixtures | unknown Issue／dirty tree／upstream or remote unavailable=`blocked`; branch/upstream、local/remote、expected HEAD mismatch=`stale`; backend/mutation 0 | arbitrary blocked/stale classification／wrong source execution | S01/S03 | yes | red-required | `tc-s01-002`, `tc-s01-003`, `tc-s03-002[git-preflight-*]` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-002` | EC-002 | malformed Planner response | `rejected`, final Candidate absent | partial Candidate leak | S03/S05 | yes | red-required | incomplete response/package fixture | `report.md#Test-Contract-Closure` |
| `CLOS-EC-003` | EC-003 | Review identity/mode/mutation mismatch | `rejected`; invalid Review evidence is not accepted and no fallback occurs | false Review authority | S05 | yes | red-required | `tc-s05-005` + mutation fixture | `report.md#Test-Contract-Closure` |
| `CLOS-EC-004` | EC-004 | any archive matrix violation | `rejected`, extraction/review/adoption output absent | unsafe archive side effects | S05 | yes | red-required | `tc-s05-004[arc-01..25]` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-005` | EC-005 / Design §4.4.3 | named missing／malformed／negative／mismatched／stale／destination fixtures | missing Review/Human=`blocked`; malformed/cross-binding/unsafe/unsupported-revoked=`rejected`; source drift=`stale`; valid rejection publishes decision-only then returns `blocked`; no named fixture accepts multiple status | approval bypass／wrong status masking／undurable rejection | S06 | yes | red-required | `tc-s06-003`, `tc-s06-009`, `tc-s06-010`, `tc-s06-011` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-006` | EC-006 | replace/validation fault before commit | exact rollback or `recovery_required` | mixed canonical state | S06 | yes | red-required | `tc-s06-004`, `tc-s06-005` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-007` | EC-007 | commit failure | baseline restored or `recovery_required` | dirty/index drift | S06 | yes | red-required | `tc-s06-005[commit-failure]` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-008` | EC-008 | commit success + push failure/response loss | `publication_pending`; same-operation resume | destructive history rollback | S06 | yes | red-required | `tc-s06-006` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-009` | EC-009 | retry with remote/tree/operation mismatch | `blocked_remote_diverged`, no force/reset | publishing wrong history | S06 | yes | red-required | `tc-s06-007` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-010` | EC-010 | ineligible/unapproved live target | block before live backend/write/push | unauthorized external mutation | S09A/S09B | yes | red-required + manual-required | `tc-s09a-002`, S09B preflight record | `report.md#Test-Contract-Closure` |

### 8.3 PA-NF Closure

| Closure ID | Spec link | Named input/state | Exact locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-PA-NF-01` | PA-NF-01 | archive Review only | `blocked: missing_human_source`, exit 1, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-01]`, `tc-s08-003[pa-nf-01]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-02` | PA-NF-02 | git Review only | `blocked: missing_human_source`, exit 1, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-02]`, `tc-s08-003[pa-nf-02]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-03` | PA-NF-03 | Human approved only | `blocked: missing_review_source`, exit 1, mutation 0 | approval-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-03]`, `tc-s08-003[pa-nf-03]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-04` | PA-NF-04 | parity only | `blocked: missing_review_source`, exit 1, mutation 0 | parity-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-04]`, `tc-s08-003[pa-nf-04]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-05` | PA-NF-05 | wrong archive identity | `rejected: identity_object_mismatch`, exit 1, mutation 0 | Candidate substitution | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-05]`, `tc-s08-003[pa-nf-05]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-06` | PA-NF-06 | wrong git identity／base | `rejected: identity_object_mismatch`, exit 1, mutation 0 | git target substitution | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-06]`, `tc-s08-003[pa-nf-06]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-07` | PA-NF-07 | source drift | `stale: source_identity_drift`, exit 1, mutation 0 | stale approval reuse | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-07]`, `tc-s08-003[pa-nf-07]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-08` | PA-NF-08 | semantic mutation + successful restore | `rolled_back: precommit_fault_restored`, exit 1, exact H0 | post-review meaning drift | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-08]`, `tc-s08-003[pa-nf-08]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-09` | PA-NF-09 | parity failure + successful restore | `rolled_back: precommit_fault_restored`, exit 1, exact H0 | partial canonical adoption | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-09]`, `tc-s08-003[pa-nf-09]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-10A` | PA-NF-10A | validation failure + successful restore | `rolled_back: precommit_fault_restored`, exit 1, exact H0 | validation failure treated ready | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-10a]`, `tc-s08-003[pa-nf-10a]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-10B` | PA-NF-10B | H1 commit + publication failure | `publication_pending: publication_incomplete`, exit 1, local H1 retained | commit loss／false ready | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-10b]`, `tc-s08-003[pa-nf-10b]` | `report.md#Test-Contract-Closure` |

### 8.4 Archive-safety Closure

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence / verification | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-ARC-01` | REQ-022 root | wrong/multiple/unsafe root | `rejected`, outputs 0 | root confusion | S05 | yes | red-required | `tc-s05-004[arc-01-root]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-02` | REQ-022 traversal | `..` path | `rejected`, outputs 0 | ZIP slip | S05 | yes | red-required | `tc-s05-004[arc-02-traversal]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-03` | REQ-022 absolute | POSIX/drive/UNC absolute path | `rejected`, outputs 0 | host path overwrite | S05 | yes | red-required | `tc-s05-004[arc-03-absolute]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-04` | REQ-022 backslash | backslash-ambiguous path | `rejected`, outputs 0 | platform path ambiguity | S05 | yes | red-required | `tc-s05-004[arc-04-backslash]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-05` | REQ-022 NUL | NUL in name/content boundary | `rejected`, outputs 0 | parser truncation | S05 | yes | red-required | `tc-s05-004[arc-05-nul]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-06` | REQ-022 symlink | symlink entry | `rejected`, outputs 0 | link escape | S05 | yes | red-required | `tc-s05-004[arc-06-symlink]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-07` | REQ-022 hardlink | hardlink entry | `rejected`, outputs 0 | alias overwrite | S05 | yes | red-required | `tc-s05-004[arc-07-hardlink]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-08` | REQ-022 device | block/char device entry | `rejected`, outputs 0 | special-device abuse | S05 | yes | red-required | `tc-s05-004[arc-08-device]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-09` | REQ-022 FIFO | FIFO entry | `rejected`, outputs 0 | blocking special file | S05 | yes | red-required | `tc-s05-004[arc-09-fifo]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-10` | REQ-022 socket | socket entry | `rejected`, outputs 0 | special-file escape | S05 | yes | red-required | `tc-s05-004[arc-10-socket]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-11` | REQ-022 duplicate | exact duplicate path | `rejected`, outputs 0 | last-write-wins ambiguity | S05 | yes | red-required | `tc-s05-004[arc-11-duplicate]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-12` | REQ-022 casefold | casefold collision | `rejected`, outputs 0 | cross-filesystem collision | S05 | yes | red-required | `tc-s05-004[arc-12-casefold]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-13` | REQ-022 Unicode | NFC/NFD collision | `rejected`, outputs 0 | normalization collision | S05 | yes | red-required | `tc-s05-004[arc-13-unicode]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-14` | REQ-022 encryption | encrypted entry/archive | `rejected`, outputs 0 | uninspectable payload | S05 | yes | red-required | `tc-s05-004[arc-14-encryption]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-15` | REQ-022 nested archive | nested archive suffix/signature | `rejected`, outputs 0 | recursive expansion | S05 | yes | red-required | `tc-s05-004[arc-15-nested]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-16` | REQ-022 executable | executable mode/forbidden file | `rejected`, outputs 0 | executable payload | S05 | yes | red-required | `tc-s05-004[arc-16-executable]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-17` | REQ-022 binary | invalid UTF-8/NUL-like binary | `rejected`, outputs 0 | opaque payload | S05 | yes | red-required | `tc-s05-004[arc-17-binary]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-18` | REQ-022 CRC | corrupt CRC/data | `rejected`, outputs 0 | corrupted content acceptance | S05 | yes | red-required | `tc-s05-004[arc-18-crc]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-19` | REQ-004,022 inventory／controls | each required control key, canonical bytes, MANIFEST inventory, CHECKSUMS coverage, cross-file digest | valid exact v1 controls pass; every missing／unknown／duplicate／wrong-version／serialization／inventory／digest parameter rejects with outputs 0 | missing/substituted/ambiguous control file | S05 | yes | red-required | `tc-s05-004[arc-19-inventory]`, `tc-s05-006[ctl-*]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-20` | REQ-022 outer size | `10,000,000` and `10,000,001` byte ZIP | ceiling passes; +1 rejects; outputs 0 on reject | oversized transport | S05 | yes | red-required | `tc-s05-004[arc-20-outer-size]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-21` | REQ-022 entry count | `64` and `65` entries | ceiling passes; +1 rejects; outputs 0 on reject | entry-count exhaustion | S05 | yes | red-required | `tc-s05-004[arc-21-entry-count]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-22` | REQ-022 per-file size | `2,000,000` and `2,000,001` expanded bytes | ceiling passes; +1 rejects; outputs 0 on reject | single-file exhaustion | S05 | yes | red-required | `tc-s05-004[arc-22-file-size]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-23` | REQ-022 aggregate size | `10,000,000` and `10,000,001` expanded bytes | ceiling passes; +1 rejects; outputs 0 on reject | aggregate exhaustion | S05 | yes | red-required | `tc-s05-004[arc-23-total-size]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-24` | REQ-022 path length | `240` and `241` UTF-8 bytes | ceiling passes; +1 rejects; outputs 0 on reject | path resource/portability failure | S05 | yes | red-required | `tc-s05-004[arc-24-path-length]` | `report.md#Test-Contract-Closure` |
| `CLOS-ARC-25` | REQ-022 ratio | ratio `100` and `>100` | ceiling passes; exceed rejects; outputs 0 on reject | decompression bomb | S05 | yes | red-required | `tc-s05-004[arc-25-ratio]` | `report.md#Test-Contract-Closure` |

### 8.5 Design-risk Closure

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence / verification | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-RISK-001` | Design RISK-001 | fault after each file/validation/commit phase | exact rollback or explicit recovery stop | mixed canonical bytes | S06 | yes | red-required | `tc-s06-004`, `tc-s06-005` | `report.md#Discovered-Tests` |
| `CLOS-RISK-002` | Design RISK-002 | all archive classes and boundaries | fail-closed, outputs 0 | path/resource exploit | S05 | yes | red-required | `tc-s05-004[arc-01..25]` | `report.md#Discovered-Tests` |
| `CLOS-RISK-003` | Design RISK-003 | live target without full Human authorization | block before credentialed mutation | cross-Issue unauthorized write | S09A/S09B | yes | red-required + manual-required | `tc-s09a-002`, S09B preflight | `report.md#Discovered-Tests` |
| `CLOS-RISK-004` | Design RISK-004 | generic archive/runbook regressions | existing behavior unchanged | shared primitive regression | S05/S06/S08 | yes | covered-existing | `tc-s05-002`, runbook suite, `tc-s08-002` | `report.md#Discovered-Tests` |
| `CLOS-RISK-005` | Design RISK-005 | push failure/response loss/divergence | resumable same operation, no reset/force | ambiguous publication identity | S06 | yes | red-required | `tc-s06-006`, `tc-s06-007` | `report.md#Discovered-Tests` |

### 8.6 Final-quality and Closure-graph Closure

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence / verification | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-S99-001` | AC-001–017 / EC-001–010 / Plan §8 | all pre-S99 owner portions、full diff、tests/build/validate、closure graph | non-S99 portions passed before entry; S99 portions pass during S99; owner graph is valid and acyclic; all required aggregates closed before Final Exit | circular gate／summary-row state／undeclared owner／focused-only Green | S99 | yes | final-required | `tc-s99-001`, `tc-s99-002`, three fresh reviewers | `report.md#Final-Quality-Gate` |

## 9. Implementation Steps

### S01 Independent CLI walking skeleton

#### behavior goal

`spec-dock-chatgpt`が独立entrypointとして`planning create`、`planning revise`、`review planning`、`planning apply`を公開し、exact Issue targetを解決する。

#### depends on / unblocks

- depends on: mode-neutral exact `ReviewedPlanningIdentityV1`、fresh bound `PlanningReviewResultV1` pass、same-identity `PlanningHumanDecisionV1` with both Plan-adoption and implementation-start authorization
- unblocks: S02A

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`
- `tests/cli_runtime/test_chatgpt_planning.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- `tests/unit/presentation/test_issue_planning.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation:
  - four-command public help。
  - exact archive／git-bound `review planning` and `planning apply` option inventory。
  - required `--issue`。
  - deterministic repository／branch derivation and absence of public overrides。
  - git base `none`／`semantic-base` positive contract。
  - omitted、cross-mode、contradictory、unsupported merge-base negative matrix。
  - known-valid Issue exact target resolution。
  - unknown Issue fail-closed resolution。
- positive target oracle: known-valid fixtureはrepo root、canonical Issue path、parent Epic／Initiative、declared dependencies、explicit branch／HEADをexactに返し、default branch、active alias、attached／tracked file、first-match searchへのfallbackがないことを観測する。
- red or alternative evidence requirement: red-required: current source has no complete public parser surface or approved exact target-resolution contract。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいcommand family、repository／branch override、merge-base support、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`
  - `tests/cli_runtime/test_chatgpt_planning.py`
  - `tests/unit/domain/test_issue_planning_contracts.py`
  - `tests/unit/presentation/test_issue_planning.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-002`, `AC-003`のtarget-resolution portion
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s01-001` acceptance: 独立CLIが四つのsupported commandとexact mode helpを公開する
  - 前提: temp managed repositoryを使う。
  - 操作: entrypoint、各command、archive／git mode helpを直接実行する。
  - 期待結果:
    - planning create／planning revise／review planning／planning applyだけが表示される。
    - archive Review helpは`--issue --mode archive-candidate --candidate --logical-filename --zip-sha256 --output`を示す。
    - git Review helpは`--issue --mode git-bound --reviewed-head --target --base-kind [--base-head] --output`を示す。
    - archive apply helpとgit apply helpがDesign §3のexact argsを示す。
    - `[mode identity]`、public repository／branch override、Core lifecycle commandは表示されない。
  - 失敗検出: incomplete public identity、placeholder contract、entrypoint混線を検出する。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-CLI`, `CLOS-REQ-002`

- `tc-s01-002` negative: unknown targetをexact statusでfail closedにする
  - 前提: canonical Issue treeに存在しないsyntactically valid Issue IDを指定する。
  - 操作: planning createのtarget-resolution phaseを実行する。
  - 期待結果: `status=blocked`、`reason=unknown_issue`、exit 1、backend call 0、filesystem／Git mutation 0、default branch／active alias／attached file／first-match fallback 0。
  - 失敗検出: unknown targetを任意に`rejected`または`stale`へ分類する回帰を防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 required closure: `CLOS-EC-001`

- `tc-s01-003` acceptance: known-valid Issueをexactに解決する
  - 前提: temp managed repositoryにknown-valid Issue、parent Epic／Initiative、declared dependency、explicit named branch／HEADを用意する。別locationに同じ短縮IDまたはfallback候補を置く。
  - 操作: backendを起動せずplanning createのtarget-resolution phaseを実行する。
  - 期待結果: resolved repository root、canonical Issue path、parent Epic ID、parent Initiative ID、dependency set、explicit branch／HEADがfixtureとexact一致し、`fallback_used=false`相当を観測する。別location、default branch、active alias、attached／tracked fileは選択されない。
  - 失敗検出: positive pathが偶然のfirst match、default fallback、parent／dependency omissionでGreenになることを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-CLI`, `CLOS-EC-001`

- `tc-s01-004` contract: mode-specific parser matrixを閉じる
  - 前提:
    - positive: `archive-review`、`archive-apply-approved`、`archive-apply-rejected`、`git-review-none`、`git-review-semantic-base`、`git-apply-none`、`git-apply-semantic-base`。
    - negative: `missing-issue`、`missing-mode-identity`、`archive-with-git-option`、`git-with-archive-option`、`missing-target`、`unsorted-targets`、`duplicate-target`、`none-with-base-head`、`semantic-base-without-base-head`、`semantic-base-nonancestor`、`unsupported-merge-base`、`repository-override`、`branch-override`。
  - 操作: parserとidentity constructorを各named parameterで実行する。
  - 期待結果:
    - positiveはone exact `ReviewedPlanningIdentityV1`を構築する。
    - missing Review／Human authority sourceだけは`blocked`。
    - 他negativeは`rejected`。
    - backend call、filesystem mutation、Git mutationは0。
    - repository／branchはfixture current Git/upstreamから導出される。
  - 失敗検出: hidden defaults、Issue inference、cross-mode option、base field omission、silent sortingを防ぐ。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`, `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-CLI`, `CLOS-REQ-002`, `CLOS-REQ-006`, `CLOS-REQ-009`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S01は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-002` / S01
- `CLOS-REQ-009` / S01
- `CLOS-EC-001` / S01

exact help／parser matrix、unknown-target negative、known-valid target positive、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkが揃った場合だけ上記portionsを`passed`にする。

`CLOS-CLI`を含む`required=no` summary aliasにstateを付与しない。`CLOS-REQ-009`と`CLOS-EC-001`のaggregateは後続owner portionsがpassedになるまでopenのままとする。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S02A Official Skill and closed Prompt resources

#### behavior goal

official Skillがnew CLIをHuman entrypointとして使い、closed provider Prompt inventoryとHuman Gateを正しく案内する。

#### depends on / unblocks

- depends on: S01
- unblocks: S02B

#### exact target files

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/create.md`
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/revise.md`
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/review.md`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh spec-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: Skill operating spine、four-command route、closed Prompt inventory、Human Gate／apply authority boundaryをdocs inspectionで検証する。code assertion ownershipはS02Bへ分離する。
- red or alternative evidence requirement: inspect-only: current Skill routes through the legacy evidence/rewrite lane and must be replaced by the approved integrated bundle route.
- green verification: `git diff --check`と、Skill／三Prompt resourceのclosed inventory、four-command references、raw override禁止、Human Gate後にMainがapplyを起動する記述のdocs inspection。
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `doc-writer`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/create.md`
  - `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/revise.md`
  - `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/review.md`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-001`, `AC-011`
- required tests or docs-only verification: `git diff --check`とexact four filesのdocs inspection。automated structural assertionsはS02Bが所有する。
- reviewer focus: `spec-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s02a-001` docs: Skillからnew CLIへ到達する
  - 前提: provider Skillとthree Prompt resourcesをinspectする。
  - 操作: Skillのoperating spineとcommandsを解析する。
  - 期待結果: official entrypoint、four supported commands、dual mode/lane、Human Gate、Main-owned apply invocationが一致する。
  - 失敗検出: 旧evidence laneやmanual fallbackの通常経路復活を防ぐ。
  - 検証方法: four-file docs inspection + `git diff --check`
  - 関連 closure id: `CLOS-SKILL`

- `tc-s02a-002` security: Prompt inventoryをclosedにする
  - 前提: undeclared Prompt fileまたはraw overrideを指定するfixtureを用意する。
  - 操作: planning commandを実行する。
  - 期待結果: backend起動前に拒否し、allowed provider Promptだけが使用される。
  - 失敗検出: prompt injection surfaceの拡張を防ぐ。
  - 検証方法: Prompt inventory inspection。automated negativeは`tc-s02b-002`。
  - 関連 closure id: `CLOS-SKILL`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S02Aは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-001` / S02A
- `CLOS-REQ-005` / S02A

docs inspection、fresh `spec-reviewer`、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-SKILL` summary aliasにstateを付与しない。

#### step gate

`git diff --check`とexact four-file inspectionを成功させ、scope外diff 0、fresh `spec-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S02B Skill／Prompt inventory and route structural tests

#### behavior goal

S02Aで確定したSkill／Prompt contractをprovider sourceへbindするstructural assertionsを追加し、legacy route、raw override、apply omissionを自動検出する。

#### depends on / unblocks

- depends on: S02A
- unblocks: S03

#### exact target files

- `tests/cli_runtime/test_chatgpt_planning.py`

#### behavior slice execution

1. MainがS02Aのfour filesとS01 parser contractをbaselineとして固定する。
2. MainがImplementation Delegation Gateを記録し、`dev-coder`へexact test fileだけを渡す。
3. Workerがlegacy Skill／missing apply／undeclared Prompt fixtureでRedを観測し、one-test／minimal assertionでGreenにする。
4. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
5. fresh code-reviewerがtest sensitivityとoverfittingを確認する。
6. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記test fileだけ。
- test obligation: official Skill route、exact Prompt inventory、four-command references、raw override禁止、Human Gate／apply authority boundaryをsource assertionする。
- red or alternative evidence requirement: red-required: S02A前のlegacy Skillまたはmissing Prompt/apply fixtureで少なくとも一つのassertionが失敗する。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py -q`
- refactor guardrail: production／Skill／Prompt bytesをこのstepで変更しない。assertion helperはsingle test file内のbounded helperだけ。
- amendment trigger: production behavior変更、別test module、shared fixture、Skill contract変更が必要なら停止しplan amendmentへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、S01 parser source、S02A Skill／Prompt resources。
- allowed paths:
  - `tests/cli_runtime/test_chatgpt_planning.py`
- forbidden changes:
  - production source、Skill／Prompt、canonical docs、`.assurance.json`
  - root generated `spec-dock/` projection direct edit
  - any path not explicitly listed in this step
- acceptance criteria: `AC-001`, `AC-011`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py -q`
- reviewer focus: `code-reviewer` verifies test sensitivity、closed inventory、no implementation coupling beyond public/source contract。
- stop conditions: source drift、allowlist外変更、test cannot fail against known bad fixture、unresolved material decision。
- output required: changed file、Red/Green evidence、verification result、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s02b-001` regression: official Skillはfour-command contractを参照する
  - 前提: missing apply／legacy routeを含むknown-bad source fixtureを用意する。
  - 操作: Skill structural assertionsを実行する。
  - 期待結果: known-badはRed、S02A provider sourceはGreen。
  - 失敗検出: S02A docsとCLI contractのdriftを防ぐ。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-SKILL`, `CLOS-REQ-001`

- `tc-s02b-002` security: undeclared Prompt／raw overrideを拒否するcontractを固定する
  - 前提: extra Prompt fileまたはraw override flagを宣言するknown-bad fixtureを用意する。
  - 操作: inventory／parser source assertionsを実行する。
  - 期待結果: known-badはRed、exact create/revise/review inventoryはGreen。
  - 失敗検出: prompt injection surfaceの拡張を防ぐ。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-SKILL`, `CLOS-REQ-005`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`へevidenceを統合する。

#### step closure contract

S02Bは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-001` / S02B
- `CLOS-REQ-005` / S02B

sensitivity Red、targeted Green、fresh `code-reviewer`、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-SKILL` summary aliasにstateを付与しない。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py -q`を成功させ、production／docs diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。

### S03 Git-bound Planner response flow

#### behavior goal

exact Git preflight、pre-produced closed Prompt、direct-argv backendを通してcomplete三文書Planner responseを取得・検証する。final immutable Candidate ZIPの構築とidentity確定はS05だけが所有する。

#### depends on / unblocks

- depends on: S02B
- unblocks: S04

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation:
  - exact Git preflight。
  - backend non-invocation on source mismatch。
  - complete three-document response validation。
  - benign shell metacharacterのplanning-specific direct argv capture。
  - prohibited secret-like contentのpre-invocation rejection。
  - no repository mutation。
- direct-argv fixtureとprohibited-content fixtureを分離し、一つのfixtureで双方をcloseしない。
- planning-specific fixture ownerは`tests/unit/application/test_issue_planning.py`または`tests/integration/test_chatgpt_planning_fake_oracle.py`のS03 allowed pathだけ。authoring-pack fixtureをS03 Red ownerにしない。
- prohibited-content validationはPrompt rendering、attachment materialization、backend argv construction、backend invocationより前に行う。
- red or alternative evidence requirement:
  - direct-argv Red: benign metacharacterがshell stringへ結合されるknown-bad。
  - prohibited-content Red: sentinelがbackend argvまたはrendered inputへ到達するknown-bad。
- owned Green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- covered-existing regression: `uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q`。file変更、planning fixture追加、S03 Red ownershipは禁止する。
- refactor guardrail: Candidate packaging、archive identity、new persistent state、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - Candidate ZIP packaging or identity finalization owned by S05
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-003`, `AC-011`
- required tests or docs-only verification:
  - owned: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
  - covered-existing, read-only: `uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q`
- reviewer focus: `code-reviewer` verifies source fail-closed behavior、exact three-document response、direct argv、redaction、no hidden mutation、no premature packaging authority。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s03-001` acceptance: fake backendからcomplete three-document responseを取得する
  - 前提: clean named branch、upstream、local=remote、fake backend responseにexact `requirement.md`／`design.md`／`plan.md`がある。
  - 操作: planning createのbackend-response phaseを実行する。
  - 期待結果: safe external work areaへ三文書responseがbyte-preservingに取得され、repositoryとfinal Candidate targetは不変。
  - 失敗検出: partial response、unexpected file、hidden repository write、S05前のfinal identity確定を検出する。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`

- `tc-s03-002` negative: Git preflight named conditionsを一つのexact statusへ分類する
  - 前提: named fixturesを一件ずつ用意する。
  - expected mapping:
    - `git-preflight-dirty-tree` → `blocked: dirty_tree`
    - `git-preflight-upstream-missing` → `blocked: upstream_missing`
    - `git-preflight-remote-unavailable` → `blocked: remote_unavailable`
    - `git-preflight-branch-upstream-mismatch` → `stale: branch_upstream_mismatch`
    - `git-preflight-local-remote-mismatch` → `stale: local_remote_mismatch`
    - `git-preflight-expected-head-mismatch` → `stale: expected_head_mismatch`
  - 操作: planning createのpreflightを各parameterで実行する。
  - 期待結果: each parameterが上記exact status／reason、exit 1、backend call 0、repository mutation 0。test reportはparameter IDを保持する。
  - 失敗検出: `stale/blocked` union、all-blocked、all-stale実装を防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 required closure: `CLOS-REQ-003`, `CLOS-EC-001`

- `tc-s03-003` security: benign shell metacharacterをseparate direct argv elementsとして扱う
  - 前提: spaces、quotes、semicolon、dollar、parentheses、Unicodeを含むがREQ-021 prohibited contentではないoperator contextとsafe external path、argv-capturing fake backendを用意する。
  - 操作: planning createのbackend invocationを実行する。
  - 期待結果:
    - backend call countは1。
    - each untrusted valueはone argv elementとしてbyte-preservingに保持される。
    - `shell=False`相当でshell string construction／shell executionは0。
    - repository mutationは0。
  - 失敗検出: command injection、argv element collapse、shell fallbackを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`, `CLOS-REQ-021`

- `tc-s03-004` security: prohibited secret-like contentをbackend invocation前に拒否する
  - 前提: unique secret sentinelと、secret／token／cookie／credential／private-key marker、`.env` path、production-dump marker、private-customer-data markerを各独立parameterとしてoperator context、explicit file、attachment candidateへ配置する。
  - 操作: planning createのpre-invocation input validationを実行する。
  - 期待結果:
    - status=`rejected`、exit 1。
    - backend call countは0。
    - rendered Prompt、attachment staging tree、attachment inventory、captured argv、diagnostics、text／JSON result、Planner response、Candidate outputのいずれにもsentinelが存在しない。
    - repository／output final artifact mutationは0。
  - 失敗検出: direct argvでshell injectionだけを防ぎ、secretをbackendへ送信する回帰を防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-SEC`, `CLOS-REQ-021`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S03は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-003` / S03
- `CLOS-REQ-004` / S03
- `CLOS-REQ-021` / S03
- `CLOS-EC-001` / S03
- `CLOS-EC-002` / S03

exact source matrix、complete response、benign direct-argv、prohibited-content backend-call-zero、covered-existing Git-fetch regression、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。

`CLOS-GIT`、`CLOS-SEC`、`CLOS-CREATE` summary aliasesにstateを付与しない。S05またはS08をownerに含むaggregatesは後続portionsがpassedになるまでopenのままとする。

#### step gate

次を双方成功させる。

```bash
uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q
uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q
```

scope外diff 0、`tests/unit/authoring_pack/test_github_fetch_policy.py` diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S04 Semantic and mechanical revision

#### behavior goal

Skill-selected laneを維持し、Semantic complete replacementとbounded Mechanical revisionを決定的に生成する。

#### depends on / unblocks

- depends on: S03
- unblocks: S05

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: red-required: current authoring primitives do not expose the approved revision-lane contract.
- green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-004`
- required tests or docs-only verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s04-001` acceptance: Semantic revisionはcomplete replacementを返す
  - 前提: valid prior Candidateとsemantic lane、fake backend complete responseを用意する。
  - 操作: planning reviseを実行する。
  - 期待結果: complete三文書replacement responseを返し、旧Candidateは不変。new Candidate identityとfinal ZIPはS05の共通packaging pathだけが確定する。
  - 失敗検出: 部分patchや旧version上書きを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-REVISION`

- `tc-s04-002` negative: Mechanical revisionのscope拡張を拒否する
  - 前提: allowed path/field外を変更するfake resultを用意する。
  - 操作: mechanical laneでreviseを実行する。
  - 期待結果: 非成功となりfinal Candidate outputは生成されない。
  - 失敗検出: bounded correctionをsemantic changeへ悪用する回帰を防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-REVISION`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S04は`CLOS-REQ-007` / S04だけを`passed`にできる。targeted Red／Green、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-REVISION` summary aliasにstateを付与しない。

#### step gate

`uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S05 Runtime Issue Candidate packaging, read-only Planning Review, and archive integrity

#### behavior goal

S03／S04のcomplete three-document responseからmandatory controlsを含むimmutable Issue Candidate ZIPを一意に構築し、そのfinal ZIPまたはexact git-bound identityをread-only Planning Reviewへ渡す。S05だけがlogical filename、version、Candidate ID、internal root、source binding、external ZIP SHAをfinalizeする。

#### depends on / unblocks

- depends on: S04
- unblocks: S06

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
- `tests/cli_runtime/test_authoring.py`
- `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
- `tests/unit/infra/test_issue_planning_archive.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがexisting generic authoring-pack defaultのcharacterizationを先に実行する。
4. Workerがshared `zip_contract.py`へdata-only named contractをbounded追加し、one-test／minimal implementationでIssue Candidate packagingとReviewを通す。
5. Workerがtargeted verificationとdiff summaryを返す。
6. Mainがdiff、tests、scope、generic default compatibilityを検証し、`report.md`へevidenceを統合する。
7. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
8. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- packaging owner: S05のみ。ChatGPT responseはexact三文書、Runtime final artifactは三文書＋Design §4.2のexact-versioned four controlsのimmutable ZIP。
- control serialization:
  - JSON controlsはCanonicalControlJsonV1。
  - Placeholder map v1はexact empty。
  - CHECKSUMSはall covered entries except itself。
  - external ZIP SHAはarchive外で計算。
- identity rule: initial createはversion 1、revisionはpredecessor version + 1。one timestampからlogical filename／Candidate ID／internal rootを導出する。source bindingはS03 preflight resultを使う。
- publication rule: owned temporary fileからsafe external output directoryのnew final filenameへatomic publishし、existing final targetを上書きしない。
- shared primitive rule: `zip_contract.py`へclosed data-only Issue Candidate contractを追加し、argument omitted時のexisting authoring-pack default behaviorを完全に保持する。
- test obligation:
  - create→exact final ZIP→archive Review direct handoff。
  - generic default regression。
  - exact control-schema positive。
  - every required-key／unknown／duplicate／version／canonical-byte／inventory／checksum／cross-file／external-SHA negative。
  - archive／git Review identity including Issue and git base。
  - read-only mutation guard。
- red or alternative evidence requirement:
  - red-required for direct handoff and Issue-specific control schema。
  - covered-existing for generic authoring-pack default。
- green verification: `uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: generic default意味変更、dynamic placeholder support、merge-base support、new schema registry、parallel validator、unrelated cleanupを追加しない。
- amendment trigger: existing generic behaviorを保てない、control schema拡張、target追加、new persistent state、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact `zip_contract.py`、generic compatibility tests、S03／S04 response contracts。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
  - `tests/cli_runtime/test_authoring.py`
  - `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
  - `tests/unit/infra/test_issue_planning_archive.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - existing generic authoring-pack default root、metadata、limits、status taxonomy
  - parallel archive validator、allocator、plugin/callback registry、general archive framework
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-001`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-017`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- reviewer focus: `code-reviewer` verifies sole packaging ownership、direct create→Review handoff、generic default compatibility、scope、identity/inventory/checksum correctness、read-only Review、no duplicated subsystem。
- stop conditions: generic default regression、source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、generic compatibility result、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s05-001` acceptance: planning create final ZIPをそのままarchive Reviewへ渡す
  - 前提: fake Plannerがexact三文書を返し、safe external output directoryとsource preflightがある。
  - 操作: `planning create`を実行し、そのresultのZIP pathを変更・再packagingせず`review planning --mode archive-candidate`へ渡す。
  - 期待結果: final ZIPはmandatory seven files、single root、new identity、source binding、external SHAを持ち、Review resultはそのexact identityへbindする。repositoryとCandidate bytesはReview前後で不変。
  - 失敗検出: raw three-file tree、manual repack、missing controls、identity取り違え、hidden repository writeを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-REVIEW`, `CLOS-ARCHIVE`

- `tc-s05-002` regression: existing generic authoring-pack defaultを変えない
  - 前提: current `specdock-authoring-pack/` root、required metadata、status taxonomyのpositive/negative fixturesがある。
  - 操作: contract引数なしのexisting `authoring pack review`とmanual compatibility suiteを実行する。
  - 期待結果: current generic valid packは従来どおりpassし、wrong root／metadata missing／source mismatch／unsafe entryは従来のstatusとfindingを維持する。
  - 失敗検出: Issue Candidate追加がgeneric root、metadata、limits、statusを破壊する回帰を防ぐ。
  - 検証方法: `tests/cli_runtime/test_authoring.py`, `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
  - 関連 closure id: `CLOS-ARCHIVE`, `CLOS-INTEGRATION`

- `tc-s05-003` acceptance: exact v1 Candidate controlsとidentityを検証する
  - 前提: Design §4.2のcanonical source baseline、manifest、empty placeholder map、checksums、三文書を持つsafe Candidateを用意する。
  - 操作: Issue Candidate named contractでpackagingとarchive validationを実行する。
  - 期待結果:
    - required seven rolesがexactly one。
    - actual inventory == MANIFEST entries。
    - JSON controlsはcanonical bytes。
    - source／placeholder digests、CHECKSUMS lines、entry bytesが一致する。
    - Candidate ID／version／timestamp／logical filename／root／Issue／source bindingが一致する。
    - actual external ZIP SHAがresultへ返る。
  - 失敗検出: mandatory control omission、cross-Candidate substitution、stale source、ambiguous serialization、checksum mismatchを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-ARCHIVE`, `CLOS-REQ-004`

- `tc-s05-004` negative: unsafeまたはincomplete Issue Candidateをpartial outputなしで拒否する
  - 前提: 下記`REQ-022 archive safety closure matrix`の`arc-01`〜`arc-25`を独立parameterとして用意する。
  - 操作: archive packagingまたはReviewを各parameterで実行し、resource ceilingはinclusive値とexceed値の双方を実行する。
  - 期待結果: safe inclusive boundaryだけがpassし、禁止class／exceed値は`rejected`となりfinal ZIP、final extraction tree、Review result、adoption output、operation temp leakは存在しない。
  - 失敗検出: ZIP slip、resource exhaustion、incomplete Candidate publication、partial evidenceを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-REVIEW`, `CLOS-ARCHIVE`

#### REQ-022 archive safety closure matrix

各rowは独立parameter IDを持つ。parameterizationで実装してよいが、test reportはrow IDを保持し、一つの代表fixtureで複数rowを暗黙closeしない。拒否rowの共通cleanup contractはfinal ZIP／extraction tree／Review result／adoption output／owned temp entryが0であること。

| Matrix ID | Required class / boundary | Fixture | Expected status / reason | Cleanup evidence |
|---|---|---|---|---|
| `arc-01-root` | single safe root | wrong root／multiple root／root file | `rejected: unsafe_root` | common cleanup contract |
| `arc-02-traversal` | no traversal | `../` segment | `rejected: unsafe_path` | common cleanup contract |
| `arc-03-absolute` | no absolute path | POSIX、drive、UNC forms | `rejected: absolute_path` | common cleanup contract |
| `arc-04-backslash` | no backslash ambiguity | `root\\child` | `rejected: ambiguous_path` | common cleanup contract |
| `arc-05-nul` | no NUL | NUL-bearing name／payload boundary | `rejected: nul_not_allowed` | common cleanup contract |
| `arc-06-symlink` | no symlink | symlink mode entry | `rejected: special_file` | common cleanup contract |
| `arc-07-hardlink` | no hardlink | hardlink metadata entry | `rejected: special_file` | common cleanup contract |
| `arc-08-device` | no device | block／char device mode | `rejected: special_file` | common cleanup contract |
| `arc-09-fifo` | no FIFO | FIFO mode entry | `rejected: special_file` | common cleanup contract |
| `arc-10-socket` | no socket | socket mode entry | `rejected: special_file` | common cleanup contract |
| `arc-11-duplicate` | no exact duplicate | same normalized path twice | `rejected: path_collision` | common cleanup contract |
| `arc-12-casefold` | no casefold collision | `A.md`／`a.md` | `rejected: path_collision` | common cleanup contract |
| `arc-13-unicode` | no Unicode-normalization collision | NFC／NFD equivalents | `rejected: path_collision` | common cleanup contract |
| `arc-14-encryption` | no encryption | encrypted flag／encrypted archive | `rejected: encryption_not_allowed` | common cleanup contract |
| `arc-15-nested` | no nested archive | archive suffix or signature in entry | `rejected: nested_archive` | common cleanup contract |
| `arc-16-executable` | no executable | executable mode／forbidden executable payload | `rejected: executable_not_allowed` | common cleanup contract |
| `arc-17-binary` | regular UTF-8 text only | invalid UTF-8／unexpected binary | `rejected: non_text_entry` | common cleanup contract |
| `arc-18-crc` | CRC valid | corrupt stored data／CRC | `rejected: integrity_mismatch` | common cleanup contract |
| `arc-19-inventory` | MANIFEST／CHECKSUMS／controls exact | missing／extra／digest mismatch | `rejected: inventory_mismatch` | common cleanup contract |
| `arc-20-outer-size` | outer ZIP `<=10,000,000` | exactly ceiling and ceiling+1 | exact ceiling pass; +1 `rejected: resource_limit` | reject uses common cleanup |
| `arc-21-entry-count` | entries `<=64` | 64 and 65 entries | 64 pass; 65 `rejected: resource_limit` | reject uses common cleanup |
| `arc-22-file-size` | expanded file `<=2,000,000` | exactly ceiling and ceiling+1 | exact ceiling pass; +1 `rejected: resource_limit` | reject uses common cleanup |
| `arc-23-total-size` | expanded total `<=10,000,000` | exactly ceiling and ceiling+1 | exact ceiling pass; +1 `rejected: resource_limit` | reject uses common cleanup |
| `arc-24-path-length` | UTF-8 path `<=240` bytes | 240 and 241 bytes | 240 pass; 241 `rejected: resource_limit` | reject uses common cleanup |
| `arc-25-ratio` | compression ratio `<=100` | exactly 100 and >100 | 100 pass; >100 `rejected: resource_limit` | reject uses common cleanup |

- `tc-s05-005` contract: Review identityはexact Issueとclosed git baseを要求する
  - 前提:
    - archive positive。
    - git positive `base=none`。
    - git positive `base=semantic-base` with exact ancestor。
    - negative `missing-issue`、`missing-reviewed-head`、`missing-target`、`unsorted-target`、`duplicate-target`、`none-with-head`、`semantic-base-without-head`、`semantic-base-nonancestor`、`unsupported-merge-base`、cross-mode options。
  - 操作: `review planning` identity constructionとpreflightを実行する。
  - 期待結果: positiveはexact `ReviewedPlanningIdentityV1`へbindする。negativeはbackend前に`rejected`でarchive fallbackなし。
  - 失敗検出: Issue inference、base omission、mode混同、silent fallbackを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-REVIEW`, `CLOS-REQ-006`

- `tc-s05-006` contract: Candidate control-file schemasをfield-by-fieldにfail closedで検証する
  - 前提: valid Candidateをbaselineとし、次のnamed parameter generatorを各controlへ適用する。
    - `ctl-<file>-missing-<required-key>`: 各required keyを一件ずつ除去。
    - `ctl-<file>-unknown-key`。
    - `ctl-<file>-duplicate-<key>`: 各representative object level。
    - `ctl-<file>-wrong-version`。
    - `ctl-<file>-bom`、`ctl-<file>-crlf`、`ctl-<file>-trailing-space`、`ctl-<file>-extra-line`。
    - SOURCE: wrong Issue／parent／repository／branch／HEAD、unsorted／duplicate dependencies、unsorted／unsafe／untracked relevant path。
    - MANIFEST: wrong Candidate ID／version／timestamp／filename／root、wrong source digest、wrong placeholder digest、missing／extra／duplicate／unsorted entry、wrong role、wrong coverage、nonstatic content mode。
    - PLACEHOLDER: nonempty files、unknown token field。
    - CHECKSUMS: missing／extra／duplicate line、self-entry、wrong digest、uppercase digest、wrong order、one-space／tab separator、root-prefixed path、CRLF。
    - archive: supplied external ZIP SHA mismatch。
  - 操作: each named parameterをpackaging validationまたはReview validationへ渡す。
  - 期待結果: 全negativeが`rejected`、exit 1。final ZIP、extraction tree、Review result、adoption output、owned temp leakは0。parameter IDはtest reportへ保持する。
  - 失敗検出: permissive control parsing、unknown-key tolerance、serialization divergence、self-referential checksum、cross-file substitutionを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-ARCHIVE`, `CLOS-REQ-004`, `CLOS-ARC-19`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S05は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-004`, `CLOS-REQ-006`, `CLOS-REQ-008`, `CLOS-REQ-019`, `CLOS-REQ-022`, `CLOS-REQ-023` / S05
- `CLOS-EC-002`, `CLOS-EC-003`, `CLOS-EC-004` / S05
- `CLOS-ARC-01`〜`CLOS-ARC-25` / S05
- `CLOS-RISK-002`, `CLOS-RISK-004` / S05

direct create→Review、control-schema positives／field negatives、git identity matrix、generic archive regression、archive 25／25、cleanup evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。

`CLOS-CREATE`、`CLOS-REVIEW`、`CLOS-ARCHIVE` summary aliasesにstateを付与しない。S03／S06／S07／S08を含むaggregatesは後続portionsがpassedになるまでopenのままとする。

#### step gate

`uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`を成功させ、scope外diff 0、existing generic default unchanged、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S06 Human gate, adoption, publication, and derived readiness

#### behavior goal

public `planning apply`からclosed `PlanningReviewResultV1`と`PlanningHumanDecisionV1`を検証し、同じexact reviewed identity、exact Review-result SHA、Human dual authorizationへbindしたtransactional mode-specific adoption、parity、validation、publicationを実行し、その論理積だけからreadinessを導出する。

#### depends on / unblocks

- depends on: S05
- unblocks: S07

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/scoped_file_transaction.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`
- `tests/cli_runtime/test_chatgpt_planning.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- `tests/unit/infra/test_scoped_file_transaction.py`
- `tests/unit/infra/test_runbook_store.py`
- `tests/unit/presentation/test_issue_planning.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- evidence schema obligation: Design §§4.3–4.4のclosed Review／Human schemasを実装する。Human v1 decisionはapproved／rejectedだけで、revokedを拒否する。
- parser obligation: Design §3のexact archive／git apply args、Issue、derived repository／branch、git base rules、mutual exclusionsを実装する。
- no-new-subsystem obligation: external schema registry、authority／revocation registry、database、custom Git ref、general approval frameworkを追加しない。
- status obligation:
  - missing Review/Human source=`blocked`。
  - malformed／partial／cross-binding／unsafe destination／unsupported revoked=`rejected`。
  - current source drift=`stale`。
  - Review fail + Human approved=`blocked`。
  - valid Human rejectedはdecision-record transaction。
- adoption obligation: approved + Review passだけがdecision artifact＋canonical三文書をtransactionalに処理する。
- rejection obligation: rejected decisionはdecision artifactだけをtransactionalに処理し、verified publication後も`blocked`。publicationでHEADを変更し、old H0-bound evidenceをstaleにする。
- revocation boundary: post-publication withdrawalはshared Human／Main stop-or-revert ownerへrouteし、planning runtime内でsupersession lookupを実装しない。
- transaction obligation: adoptionとrejection-recordの双方でpre-commit rollback、restore verification、post-commit no-resetを維持する。
- recovery lookup obligation:
  - operation directoryは`<canonical-output>/.spec-dock-planning-operations/<operation-id>/`。
  - manifestとcommit workspace trailerへoutput-directory identityをbindする。
  - pre-commit same-operation retryはsame exact output directoryを必須とする。
  - missing／different outputでpartial stateを検出した場合は`recovery_required`、new mutation 0、directory scan 0。
- shared reuse obligation: `runbook_store.py`のstage／backup／restoreを`scoped_file_transaction.py`へ抽出し、existing runbook testsをcharacterizationとして先にGreenにする。private helper import／duplicate transactionは禁止する。
- test obligation:
  - Review schema matrix。
  - Human approved／rejected truth table。
  - revoked unsupported。
  - exact Review SHA／identity binding。
  - exact public CLI mode matrix。
  - archive／git approved positives。
  - durable rejected decision-record。
  - PA-NF exact status 11/11。
  - replacement／validation／commit fault。
  - rollback failure。
  - same-output crash recovery。
  - wrong-output recovery failure。
  - push retry／remote divergence。
  - runbook regression／state boundary。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_scoped_file_transaction.py tests/unit/infra/test_runbook_store.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Designで承認済みのclosed evidence validation、approved adoption、rejected decision-record、deterministic recovery workspace、shared transaction以外のpublic contract／shared policyを追加しない。
- amendment trigger: revocation implementation、merge-base support、new state registry、target追加、parent boundary変更、existing behavior破壊が必要なら停止しplan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/scoped_file_transaction.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`
  - `tests/cli_runtime/test_chatgpt_planning.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/unit/domain/test_issue_planning_contracts.py`
  - `tests/unit/infra/test_scoped_file_transaction.py`
  - `tests/unit/infra/test_runbook_store.py`
  - `tests/unit/presentation/test_issue_planning.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-008`, `AC-009`, `AC-010`, `AC-013`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_scoped_file_transaction.py tests/unit/infra/test_runbook_store.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- reviewer focus: `code-reviewer` verifies public apply contract、transaction fault coverage、idempotent publication resume、runbook compatibility、scope、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s06-001` acceptance: exact archive applyでapproved full conjunctionだけがreadyになる
  - 前提: valid archive Candidate v1 controls、Review pass、Human approved、safe new decision destination、clean local=remote=expected H0を用意する。
  - 操作: Design §3 archive apply exact argvでpublic CLIを実行する。
  - 期待結果: decision artifactと三文書だけをPlanning adoption commitに含め、remote/tree parity後にtext／JSONとも`status=ready`、exit 0。operation／workspace trailersとevidence locatorsを返す。
  - 失敗検出: hidden args、Review-only／Human-only start、control substitutionを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

- `tc-s06-002` acceptance: exact git-bound applyでtarget blobとbase identityを維持する
  - 前提:
    - positive `base=none`。
    - positive `base=semantic-base` with exact ancestor。
    - Review pass、Human approved、approval-only diff。
  - 操作: Design §3 git-bound apply exact argvでpublicationを実行する。
  - 期待結果: reviewed target blobsとbase identityが不変でlocal／remote publication parityが成立し`ready`。
  - 失敗検出: Review後semantic mutation、base omission、CLI identity driftを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

- `tc-s06-003` negative: PA-NF 11件をexact statusで評価する
  - 前提: PA-NF-01〜PA-NF-09、PA-NF-10A、PA-NF-10Bを一件ずつ満たすnamed fixturesを用意する。
  - 操作: each fixtureをpublic `planning apply`／readiness evaluatorへ渡す。
  - 期待結果:
    - PA-NF-01 → `blocked: missing_human_source`
    - PA-NF-02 → `blocked: missing_human_source`
    - PA-NF-03 → `blocked: missing_review_source`
    - PA-NF-04 → `blocked: missing_review_source`
    - PA-NF-05 → `rejected: identity_object_mismatch`
    - PA-NF-06 → `rejected: identity_object_mismatch`
    - PA-NF-07 → `stale: source_identity_drift`
    - PA-NF-08 → `rolled_back: precommit_fault_restored`
    - PA-NF-09 → `rolled_back: precommit_fault_restored`
    - PA-NF-10A → `rolled_back: precommit_fault_restored`
    - PA-NF-10B → `publication_pending: publication_incomplete`
  - 全11件exit 1、readinessなし。
  - pre-mutation fixtureはmutation 0。
  - rollback fixtureはbytes／mode／index／HEAD／clean stateがexact H0。
  - publication fixtureはexact local H1だけを保持する。
  - 失敗検出: PA-NF-10の一括close、status union、generic failureを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 required closure: `CLOS-REQ-013`, `CLOS-REQ-014`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-10B`

- `tc-s06-004` recovery: replacement／validationの各fault pointをrollbackする
  - 前提: decision artifact追加後、requirement後、design後、plan後、parity／validation中に例外を注入できるbaselineを用意する。
  - 操作: 各fault parameterでarchive applyを実行する。
  - 期待結果: reverse-order restore後にoriginal bytes／mode／index／HEAD／clean statusが一致し`rolled_back`。Planning commit／remote mutation／owned temp leakは0。
  - 失敗検出: mixed canonical bytesとpartial decision artifactを防ぐ。
  - 検証方法: `tests/unit/infra/test_scoped_file_transaction.py`, `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-REQ-010`, `CLOS-EC-006`, `CLOS-RISK-001`

- `tc-s06-005` recovery: rollback／commit failureをfail closedにする
  - 前提: restore failureまたはcommit failureを注入する。
  - 操作: apply transactionを実行する。
  - 期待結果: commit failureでrestore成功なら`rolled_back`、restore不一致なら`recovery_required`。後者はbackup／digest／bounded remediationを保持し自動retryしない。
  - 失敗検出: rollback failureをcleanとして扱う事故を防ぐ。
  - 検証方法: `tests/unit/infra/test_scoped_file_transaction.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-EC-006`, `CLOS-EC-007`, `CLOS-RISK-001`

- `tc-s06-006` recovery: commit後push failure／response lossをsame operationで再開する
  - 前提: exact operation trailerを持つlocal H1を作り、push failureまたはpush成功後response lossを注入する。
  - 操作: 初回applyとsame-operation retryを実行する。
  - 期待結果: 初回は`publication_pending`、local H1を保持。retryはH1 tree／parent／trailerを照合してpushまたはremote verificationから再開し、二重commitなしで`ready`へ収束する。
  - 失敗検出: commit破棄、duplicate commit、false non-ready／false readyを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-REQ-012`, `CLOS-EC-008`, `CLOS-RISK-005`

- `tc-s06-007` negative: retry時のremote divergenceを止める
  - 前提: local H1と異なるremote commit、operation ID mismatch、tree mismatchを各fixtureで用意する。
  - 操作: same-operation retryを実行する。
  - 期待結果: `blocked_remote_diverged`、exit 1、force push／reset／amend／new commit 0。
  - 失敗検出: unrelated remote historyの上書きとwrong-operation resumeを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-EC-009`, `CLOS-RISK-005`

- `tc-s06-008` regression: runbook projectionはshared transaction抽出後も同じ
  - 前提: current `tests/unit/infra/test_runbook_store.py` positive／second-replace failure／symlink casesをbaselineにする。
  - 操作: shared primitiveを経由してrunbook suiteを実行する。
  - 期待結果: existing projection bytes、atomic failure restoration、error semanticsが変わらない。
  - 失敗検出: Issue adoption用抽出が既存workflow projectionを壊す回帰を検出する。
  - 検証方法: `tests/unit/infra/test_runbook_store.py`
  - 関連 closure id: `CLOS-REQ-019`, `CLOS-RISK-004`

- `tc-s06-009` contract: `PlanningReviewResultV1`のclosed schemaを検証する
  - 前提: valid archive identity、valid git-bound identityと、named negative fixtures `review-wrong-version`、`review-wrong-kind`、`review-missing-key`、`review-unknown-key`、`review-duplicate-key`、`review-wrong-role`、`review-wrong-freshness`、`review-wrong-authority`、`review-invalid-verdict`、`review-invalid-time`、`review-identity-digest-mismatch`を用意する。
  - 操作: 各JSON bytesをReview-result validatorへ渡し、同じbytesのSHA-256を取得する。
  - 期待結果: archive／git positiveはexact parsed identityとdigestを返す。named negativeは全件`rejected`、exit 1、repository／index／HEAD／operation manifest mutation 0。`verdict=fail`はschema上validとしてparseされ、authority gateでだけ`blocked`になる。
  - 失敗検出: permissive versioning、unknown-key tolerance、wrong reviewer authority、digest substitution、mode-neutral field unionによるambiguous identityを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-REQ-009`, `CLOS-REQ-015`

- `tc-s06-010` contract: Human decision truth table、exact Review SHA、mode-neutral gateを検証する
  - 前提: valid archive／git Review resultsとnamed fixtures:
    - `approved-archive`
    - `approved-git-none`
    - `approved-git-semantic-base`
    - `rejected-review-pass`
    - `rejected-review-fail`
    - `partial-plan-only`
    - `partial-start-only`
    - `wrong-review-sha`
    - `wrong-mode`
    - `wrong-issue`
    - `wrong-archive-identity`
    - `wrong-git-identity`
    - `stale-source`
    - `review-fail-human-approved`
    - `review-only-archive`
    - `review-only-git`
    - `human-only`
    - `revoked-unsupported`
  - 操作: preflight／authority evaluationを各parameterで実行する。
  - 期待結果:
    - approved three positivesだけがfull adoptionへ進む。
    - rejected two positivesだけがdecision-recordへ進む。
    - partial、wrong SHA／mode／Issue／identity、revoked unsupportedは`rejected`。
    - source driftは`stale`。
    - Review fail + Human approved、Review-only、Human-onlyは`blocked`。
    - pre-mutation negativeでrepository／index／HEAD／manifest mutation 0。
  - 失敗検出: Candidate-only gate、git exclusion、partial approval、Review substitution、false revocationを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-REQ-009`, `CLOS-REQ-015`, `CLOS-EC-005`

- `tc-s06-011` acceptance／recovery: rejected decisionをdurable decision-only transactionとしてpublishする
  - 前提: valid Review passまたはfail、same-identity Human rejected、safe new decision destination、clean H0を用意する。
  - 操作:
    1. rejected decisionで`planning apply`を実行する。
    2. decision artifact add後、commit前validation、commit、pushに各faultを注入する。
    3. published rejection H1へold H0-bound approved decisionを再投入する。
  - 期待結果:
    - normal pathはdecision artifact一件だけをcommit／pushし、remote parity後`blocked`、exit 1。
    - canonical三文書bytes、`.assurance.json`は不変。
    - pre-commit faultは`rolled_back`または`recovery_required`。
    - post-commit push faultは`publication_pending`。
    - H1でold H0 Review／approvalは`stale`となりfull adoptionへ進まない。
  - 失敗検出: nondurable rejection、rejectionによるcanonical rewrite、old approval reuseを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-REQ-015`, `CLOS-EC-005`

- `tc-s06-012A` recovery: stage-only clean-H0 orphanをbounded workspaceとして扱う
  - 前提:
    - canonical output A。
    - different output B。
    - same semantic operation ID。
    - output Aでexternal staging完了後、repository target変更前にcrash。
  - 操作:
    1. Aのmanifestとstageを確認する。
    2. same args + output Aでrecovery classificationを実行する。
    3. fresh stage-only crashを作り、same args + output Bでclassificationを実行する。
    4. exact A operation pathへstage-only cleanupを実行する。
  - 期待結果:
    - crash後のworktree／index／HEADはexact clean H0。
    - A retryは`workspace_only_stage`を検出し、owned stage／manifestをcleanupしてpreflightから再開できる。
    - Bはsupplied outputにmanifestがなくclean H0なので`new_workspace_attempt`となり、`recovery_required`を返さない。
    - B classificationはA、home、repository内の他output directoryをscanしない。
    - exact-path cleanupはvalid stage-only manifest、completed target 0、backup 0、operation commit 0のときだけA operation directoryを削除する。
    - repository mutation、custom ref、global registryは0。
  - 失敗検出: 不可視stage orphanをfalse repository recoveryとしてblockする回帰と、broad workspace discoveryを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`
  - 関連 required closure: `CLOS-REQ-013`, `CLOS-EC-006`, `CLOS-RISK-001`

- `tc-s06-012B` recovery: repository-visible partial stateとcommitted stateはoriginal workspaceを要求する
  - 前提:
    - output Aでdecision artifact追加後またはfirst canonical replacement後にcrash。
    - separate fixtureでexact H1 commit後にpublication failure。
    - different output B。
  - 操作:
    1. pre-commit partial stateへsame args + output Bを渡す。
    2. same partial stateへoutput Aを渡す。
    3. committed publication stateへoutput Bを渡す。
    4. committed publication stateへoutput Aを渡す。
    5. exact operation prefixに一致しないunrelated dirty-tree fixtureを実行する。
  - 期待結果:
    - pre-commit partial + B → `recovery_required: repository_visible_partial_without_workspace`、new operation directory 0、new repository mutation 0。
    - pre-commit partial + A → manifestを使いrollbackまたはresume。
    - committed H1 + B → `recovery_required: committed_operation_workspace_mismatch`、reset／amend／force push 0。
    - committed H1 + A → `publication_pending`からpush／remote verificationをresume。
    - unrelated dirty tree → `blocked: dirty_tree`であり、recovery prefixと誤認しない。
  - 失敗検出: wrong-workspace resume、backup取り違え、unrelated dirty treeのfalse recovery、lost publication identityを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 required closure: `CLOS-EC-006`, `CLOS-EC-008`, `CLOS-RISK-001`, `CLOS-RISK-005`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S06は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-009`〜`CLOS-REQ-016`のうちClosure IndexでS06 ownerとされたrows
- `CLOS-REQ-019` / S06
- `CLOS-EC-005`〜`CLOS-EC-009` / S06
- `CLOS-PA-NF-01`〜`CLOS-PA-NF-09`, `CLOS-PA-NF-10A`, `CLOS-PA-NF-10B` / S06
- `CLOS-RISK-001`, `CLOS-RISK-004`, `CLOS-RISK-005` / S06

次をすべて要求する。

- exact archive／git apply parser positives。
- Review schema matrix。
- Human approved／rejected truth table。
- revoked unsupported。
- exact Review SHA／Issue／identity cross-binding。
- exact EC-005 status matrix。
- PA-NF 11／11 exact status。
- durable rejected decision record。
- stage-only same-output cleanup。
- different-output clean-H0 new attempt。
- repository-visible wrong-output `recovery_required`。
- unrelated dirty-tree `blocked`。
- committed wrong-workspace `recovery_required`。
- all pre-commit rollback and rollback-failure stop。
- publication resume and remote-divergence stop。
- runbook regression。
- required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean check。

`CLOS-ADOPTION`と`CLOS-READINESS` summary aliasesにstateを付与しない。S08 owner portionsが存在するaggregatesはS08完了までopenのままとする。

#### step gate

```bash
uv run pytest \
  tests/cli_runtime/test_chatgpt_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_scoped_file_transaction.py \
  tests/unit/infra/test_runbook_store.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_chatgpt_planning_fake_oracle.py \
  -q
```

scope外diff 0、exact parser matrix、Review schema matrix、Human approved／rejected truth table、revoked unsupported、archive／git approved positives、durable rejection、PA-NF 11／11 exact status、all fault matrix、stage-only same-output cleanup、different-output clean-H0 new attempt、repository-visible wrong-output stop、committed wrong-workspace stop、existing runbook unchanged、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisional、status unionをpassとして扱わない。

### S07 Installer and provider projection

#### behavior goal

wheel／sdist、fresh init、updateを通してnew CLI／Skill／Prompt／docsをregular executableなinstalled surfaceへ投影する。

#### depends on / unblocks

- depends on: S06
- unblocks: S08

#### exact target files

- `src/spec_dock/cli.py`
- `pyproject.toml`
- `tests/unit/infra/test_init_update.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: red-required: current installer only handles the existing repo-local runtime executable and lacks the new managed entrypoint contract.
- green verification: `uv build && uv run pytest tests/unit/infra/test_init_update.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/cli.py`
  - `pyproject.toml`
  - `tests/unit/infra/test_init_update.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-012`, `AC-015`
- required tests or docs-only verification: `uv build && uv run pytest tests/unit/infra/test_init_update.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s07-001` compatibility: wheel／sdist fresh initでnew CLIを直接実行する
  - 前提: fresh temp reposとbuilt wheel/sdistを用意する。
  - 操作: 各artifactをinstallしspec-dock init後にboth repo-local entrypointsのmodeと--helpを確認する。
  - 期待結果: regular non-symlink、POSIX executable、direct invocation成功。
  - 失敗検出: bytesだけ存在して実行不能なinstallを防ぐ。
  - 検証方法: `tests/unit/infra/test_init_update.py`
  - 関連 closure id: `CLOS-PROJECTION`

- `tc-s07-002` compatibility: updateでmanaged inventoryを同期する
  - 前提: old managed repoへprovider changesを用意する。
  - 操作: spec-dock updateを実行する。
  - 期待結果: new CLI/Skill/Prompt/docsがprovider bytesと一致しuser specsを保持する。
  - 失敗検出: partial projectionとuser-authored spec損失を防ぐ。
  - 検証方法: `tests/unit/infra/test_init_update.py`
  - 関連 closure id: `CLOS-PROJECTION`

- `tc-s07-003` failure: representative mode failureを非成功にする
  - 前提: new entrypointのchmodまたはpostconditionを失敗させる。
  - 操作: init/updateを実行する。
  - 期待結果: nonzeroでsuccess表示なし、既存user specs保持。
  - 失敗検出: silent successful but unusable installを防ぐ。
  - 検証方法: `tests/unit/infra/test_init_update.py`
  - 関連 closure id: `CLOS-PROJECTION`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S07は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-017` / S07
- `CLOS-REQ-023` / S07

build／install／update parity、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-PROJECTION` summary aliasにstateを付与しない。

#### step gate

`uv build && uv run pytest tests/unit/infra/test_init_update.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S08 Integration, compatibility, and adoption negatives

#### behavior goal

fake remote end-to-end、PA-NF、legacy compatibility、provider／installed／dogfood parityを一つのintegration checkpointで検証する。

#### depends on / unblocks

- depends on: S07
- unblocks: S09A

#### exact target files

- `tests/integration/test_chatgpt_planning_fake_oracle.py`
- `tests/cli_runtime/test_chatgpt_planning.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- `tests/unit/infra/test_issue_planning_archive.py`
- `tests/unit/presentation/test_issue_planning.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: covered-existing plus red-required for the new E1-I1 chain; preserve existing authoring-pack tests while adding focused planning integration.
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_issue_planning_archive.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack tests/manual_tests/test_invoke_chatgpt_backend.py tests/manual_tests/test_review_chatgpt_authoring_pack.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - `tests/cli_runtime/test_chatgpt_planning.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/unit/domain/test_issue_planning_contracts.py`
  - `tests/unit/infra/test_issue_planning_archive.py`
  - `tests/unit/presentation/test_issue_planning.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`, `AC-009`, `AC-010`, `AC-011`, `AC-015`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_issue_planning_archive.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack tests/manual_tests/test_invoke_chatgpt_backend.py tests/manual_tests/test_review_chatgpt_authoring_pack.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s08-001` integration: fake remoteでarchive／git positive chainを完走する
  - 前提: fake Git remote、fake Oracle、Human decision fixturesを用意する。
  - 操作: 両modeのfull chainを実行する。
  - 期待結果: 各modeで全conjunct後だけreadiness、remote publication parity成立。
  - 失敗検出: subsystem単体greenだがE2E不成立を検出する。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-INTEGRATION`

- `tc-s08-002` regression: existing authoring-pack safetyを維持する
  - 前提: current focused suitesをbaselineとして用意する。
  - 操作: new planning suitesとexisting authoring-pack suitesを実行する。
  - 期待結果: existing public behaviorはgreenで、new routeだけadditive。
  - 失敗検出: walking skeletonが既存safe primitivesを壊す回帰を検出する。
  - 検証方法: `tests/unit/authoring_pack and tests/manual_tests`
  - 関連 closure id: `CLOS-INTEGRATION`

- `tc-s08-003` integration: PA-NF 11件とstatus reasonをpublic CLI経由で再検証する
  - 前提: fake remote、archive／git identities、PA-NF-01〜09／10A／10B fixturesを用意する。
  - 操作: public CLIから各fixtureを独立実行する。
  - 期待結果: 11／11がRequirement表とexact status／reason一致、exit 1、readinessなし。`.assurance.json`は全fixtureで不変。rollback／publication stateは各contractどおり。
  - 失敗検出: unit evaluatorとCLI rendererのstatus drift、S06-only false Greenを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 required closure: `CLOS-REQ-013`, `CLOS-REQ-014`, `CLOS-REQ-016`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-10B`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S08は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-013`, `CLOS-REQ-014`, `CLOS-REQ-016`, `CLOS-REQ-019`, `CLOS-REQ-021`, `CLOS-REQ-023` / S08
- `CLOS-PA-NF-01`〜`CLOS-PA-NF-09`, `CLOS-PA-NF-10A`, `CLOS-PA-NF-10B` / S08
- `CLOS-RISK-004` / S08

archive／git positive E2E、PA-NF 11／11 exact public status、assurance unchanged、existing compatibility、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。

S08は`CLOS-REQ-003`〜`CLOS-REQ-012`、`CLOS-REQ-015`、`CLOS-REQ-017`、`CLOS-REQ-018`、`CLOS-REQ-020`、`CLOS-REQ-022`のowner portionを作成または更新しない。`CLOS-INTEGRATION` summary aliasにstateを付与しない。

#### step gate

focused planning／integration suitesとexisting authoring-pack suitesを成功させ、archive／git positive、PA-NF 11／11 exact status、assurance mutation 0、existing compatibility、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。S08 ownerでないrowをpassしたと記録しない。

### S09A Hermetic dogfood selection／abort／recovery contract

#### behavior goal

fake backend、fake remote、temporary repositoryだけでlive dogfoodのselection、pre-mutation abort、transaction rollback、publication retry contractを検証する。

#### depends on / unblocks

- depends on: S08
- unblocks: S09B

#### exact target files

- `tests/integration/test_chatgpt_planning_dogfood.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがfake-only pre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: eligible／ineligible selection、Human authorization欠落、live mutation destination欠落、abort before backend、rollback、publication retryをfake-onlyで検証する。
- red or alternative evidence requirement: red-required: current source has no hermetic dogfood operation harness or authorization preflight.
- green verification: `uv run pytest tests/integration/test_chatgpt_planning_dogfood.py -q`
- refactor guardrail: Green後のbounded tidyだけ。real credential、live backend、real canonical target、real push、new public contractを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `tests/integration/test_chatgpt_planning_dogfood.py`
- forbidden changes:
  - live backend invocation、real GitHub remote、real canonical Issue mutation、credential access
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-014`
- required tests or docs-only verification: `uv run pytest tests/integration/test_chatgpt_planning_dogfood.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s09a-001` integration: eligible fixtureはlive operation planまで進める
  - 前提: fake Issue、fake clean worktree／branch、fake Human authorization、fake evidence destination、Greenなrollback contractを用意する。
  - 操作: dogfood selection／operation preflightを実行する。
  - 期待結果: live operation requestをpure dataとして返し、backend／canonical／remote mutationは0。
  - 失敗検出: selection logicとcredentialed operationの混在を防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_dogfood.py`
  - 関連 closure id: `CLOS-DOGFOOD`

- `tc-s09a-002` negative: ineligible／unapproved targetを開始前に拒否する
  - 前提: dependency chain内、Portfolio change必要、rollback不明、Human credentialed-mutation approval欠落の各named fixtureを用意する。
  - 操作: dogfood selection preflightを実行する。
  - 期待結果: live backendとcanonical mutation前にblocked。
  - 失敗検出: dogfoodをPortfolio replanningへ拡張する事故を防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_dogfood.py`
  - 関連 closure id: `CLOS-DOGFOOD`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

S09Aは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-018` / S09A
- `CLOS-EC-010` / S09A
- `CLOS-RISK-003` / S09A

fake-only selection／abort／rollback／publication-retry evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-DOGFOOD` summary aliasにstateを付与しない。

#### step gate

`uv run pytest tests/integration/test_chatgpt_planning_dogfood.py -q`を成功させ、real credential／backend／canonical／remote mutation 0、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S09B Main/Human-owned live dogfood operation gate

#### behavior goal

Human-selected eligible Issueで、明示されたcredentialed mutation boundary内だけselected modeのfull positive chainをMainが完走し、実運用Evidenceを取得する。

#### depends on / unblocks

- depends on: S09A
- unblocks: S90

#### operation-owned destinations

- iss-00334 `artifacts/<timestamp>-disc-jit-dogfood-operation.md`
- Humanが選択したtarget Issueのexact canonical three-document paths
- target Issue `artifacts/` direct childに置くexact Human decision artifact
- Humanが承認したdedicated worktree／branch／remote

target未選択時にplaceholder pathを作成しない。選択後、Mainがexact paths／branch／remoteをoperation recordへ固定する。

#### operation gate execution

1. MainがS08／S09A Green、clean current branch、no open closure、transaction rollback testsを確認する。
2. Humanがtarget Issue、dedicated worktree／branch、selected mode、canonical target paths、decision artifact、push remote、evidence destinationを明示承認する。
3. MainがREQ-018 eligibility、dependency-chain外、Portfolio replanning不要、concurrent work 0、pre-commit rollback可能をread-only preflightする。
4. Mainがcreate→fresh Review→Human Gateを実行し、exact reviewed identity／decisionを固定する。
5. Mainがpublic `planning apply`をdirect argvで実行する。worker、pytest、background fixtureへcredentialed mutationを委任しない。
6. Mainがresult、local／remote HEAD、tree parity、unauthorized diff 0、metricsをoperation artifactへ記録する。
7. failureはDesign §5.1に従う。pre-commitはrollback、post-commit push failureは`publication_pending`からsame-operation retry、remote divergenceは停止する。
8. published commitの取消しが必要な場合は別のHuman-authorized revertとして扱い、このgateでautomatic reset／force pushしない。

#### planned contract

- scope: Humanがstep開始時に明示したtargetとdestinationだけ。
- test obligation: S09Aでmechanicsを証明済みとし、live gateではidentity、authorization、actual remote parity、unauthorized mutation 0、observability metricsをmanual evidenceで閉じる。
- red or alternative evidence requirement: manual-required。target／authorization未確定は正常なblocked stateであり、waiveまたはsynthetic passにしない。
- green verification: public command results、`git status --short`、local/remote HEAD、tree digest、target artifact digests、operation artifact inspection。
- refactor guardrail: live operation中にproduct code／tests／shared policyを変更しない。発見したproduct defectはS08以前へのplan amendmentとして戻す。
- amendment trigger: new public behavior、target scope expansion、unbounded rollback、unexpected external authority、product fixが必要ならoperationを停止しfresh plan/spec reviewへ戻る。

#### authority contract

- executor: Codex Main under exact Human authorization。delegated workerは使用しない。
- required inputs: Human approval message、target eligibility evidence、S09A Green、exact reviewed identity、Human decision、clean dedicated worktree／branch。
- allowed mutations: Humanが列挙したtarget canonical paths、new decision artifact、dedicated Planning commit／pushだけ。
- forbidden mutations: current Portfolio、E1 dependency-chain Issue、unlisted downstream Issue、unlisted remote、force push、automatic reset、raw transcript／credential persistence。
- reviewer focus: `qa-reviewer`またはfresh `spec-reviewer`がoperation evidence、unauthorized mutation 0、S09Aとの一致をread-only確認する。
- stop conditions: missing/ambiguous authorization、dirty/concurrent worktree、source drift、rollback evidence missing、credential unavailable、remote divergence。

#### 具体テストケース一覧

- `tc-s09b-001` manual: exact Human-authorized targetでselected positive chainを完走する
  - 前提: Human-selected targetが全eligibility条件を満たし、exact mutation/evidence destinationsが承認済み。
  - 操作: Mainがselected modeでcreate→fresh Review→Human Gate→public apply→remote/tree verificationを実行する。
  - 期待結果: `ready`、unauthorized Portfolio/downstream mutation 0、planned/unplanned intervention、handoff bytes、invocations、Review result、wall-clock、failure modeを記録する。
  - 失敗検出: synthetic-only acceptance、worker-owned credentialed mutation、scope侵入を防ぐ。
  - 検証方法: operation artifact + Git/local/remote parity inspection
  - 関連 closure id: `CLOS-DOGFOOD`, `CLOS-REQ-018`, `CLOS-REQ-024`, `CLOS-RISK-003`

#### report evidence destination

Mainが`report.md`の`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へoperation artifact locator、Human authorization、result、metrics、reviewer verdictを統合する。

#### step closure contract

S09Bは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-018` / S09B
- `CLOS-REQ-024` / S09B
- `CLOS-EC-010` / S09B
- `CLOS-RISK-003` / S09B

Human-selected eligible target、explicit live mutation authority、bounded operation、observability metrics、evidence destination、Main verificationを要求する。pytest workerはこのportionをpassできない。`CLOS-DOGFOOD` summary aliasにstateを付与しない。

#### step gate

targetまたはauthorizationがない場合は`blocked`のまま停止する。実施した場合はoperation artifact、Git parity、target digests、fresh reviewer verdict、Main Step Result Approvalを確認し、失敗／skip／unavailable／denied／provisionalをpassとして扱わない。


### S90 docs impact resolution / docs refresh

#### behavior goal

Provider docs、Skill、Prompt reference、READMEをfinal public behaviorへ揃え、Issue／Epic／Initiative boundaryとcurrent shared delivery authorityを正しく説明する。

#### depends on / unblocks

- depends on: S09B
- unblocks: S99

#### exact target files

- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_planning.md`
- `src/spec_dock/assets/spec_dock/docs/reference_chatgpt_cli.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`

#### behavior slice execution

1. Mainがimplementation behaviorとdocs deltaを確定する。
2. `doc-writer`がexact filesだけを日本語ファーストで更新する。
3. commands、mode、lane、Human Gate、external delivery boundaryをsource behaviorと照合する。
4. Mainがdiffをreportへ統合し、fresh `spec-reviewer`へ渡す。

#### planned contract

- scope: exact four provider files。
- test obligation: commands／paths／authority／security／rollback wordingのsource alignment。
- red or alternative evidence: inspect-only plus CLI help snapshot。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/infra/test_init_update.py -q && git diff --check`
- refactor guardrail: generic Review framework、shared delivery policy、sibling planning detailsを追加しない。
- amendment trigger: docsがnew product behaviorを必要とする場合はowning stepへ戻る。

#### delegation contract

- delegated role: `doc-writer`
- input docs: Requirement、Design、Plan、actual CLI help、parent Epic、accepted ADRs。
- allowed paths: exact target files only。
- forbidden changes: code、tests、canonical report、assurance、generated dogfood、shared delivery docs。
- acceptance criteria: `AC-001`, `AC-012`, `AC-015`
- required verification: targeted tests、docs diff、link/path inspection。
- reviewer focus: `spec-reviewer` docs/spec alignment。
- stop conditions: observed behaviorとdocs不一致、scope expansion、missing command evidence。
- output required: changed files、docs impact summary、verification、Ledger Note。

#### 具体テストケース一覧

- `tc-s90-001` docs: official routeとauthorityを一致させる
  - 前提: final CLI help、Skill、Prompt inventory、Requirement／Designが利用可能。
  - 操作: docs／Skillのcommands、mode、lane、Human Gate、external boundaryを照合する。
  - 期待結果: public routeが一意で、Review resultやPlanning runだけのauthority claimがない。
  - 失敗検出: stale legacy route、wrong command、Human bypass、shared policy absorptionを検出する。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py` and `git diff --check`
  - 関連 closure id: `CLOS-DOCS`

#### report evidence destination

Mainが`report.md#Docs-Impact`、`Step Contract Closure`、`Spec Interpretation / Decision Ledger`へ統合する。

#### step closure contract

S90は`CLOS-REQ-020` / S90だけを`passed`にできる。

docs／Skill／referenceがone Issue／one branch／one Delivery PR、required review、Human-only merge、shared delivery owner boundaryと一致し、fresh `spec-reviewer`、Main Result Approval、commit、post-commit clean checkが揃った場合だけpassする。

`CLOS-DOCS` summary aliasと、Closure IndexでS90 ownerに指定されていない`CLOS-REQ-023` portionにstateを付与しない。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/infra/test_init_update.py -q && git diff --check`、docs link inspection、fresh `spec-reviewer` passedを必要とする。

### S99 final quality gate

#### behavior goal

全pre-S99 owner portions、test sufficiency、integrated diff、Requirement／Design／Plan／implementation／tests／docsの整合、およびClosure owner graphのvalidityを確認する。S99はmissing product workを直接実装しない。

#### depends on / unblocks

- depends on:
  - S90 complete。
  - ownerがS01〜S90である全`required=yes` portionsが`passed`。
  - open／failed／blocked pre-S99 portion 0。
- S99-owned portionsはentry時点で`open`でよい。
- unblocks: Final Exit only after S99-owned portions pass and every required aggregate becomes `closed`。

#### exact verification surface

- full provider diff and generated projection diff。
- `requirement.md`, `design.md`, `plan.md`, canonical `report.md`。
- all focused and repository-wide tests。
- package build and fresh install/update evidence。
- dogfood evidence and open risk list。
- Closure Index required rows、summary aliases、step closure contracts、dependency graph。
- current branch／one-Issue delivery handoff preconditions。

#### behavior slice execution

1. Mainが全pre-S99 owner portions、reviewer evidence、commit candidates、clean statusを確認する。
2. MainがClosure graph structural testを実行する。
3. `uv run pytest -q`、`make lint`、`uv build`、`./spec-dock/scripts/spec-dock validate`を実行する。
4. `qa-reviewer`がtest sufficiency、integration、failure pathsを確認する。
5. issue-wide `code-reviewer`がstructure、responsibility、security、regression riskを確認する。
6. `spec-reviewer`がall requirements、non-goals、authority、docs、Closure graphを確認する。
7. failはowning stepへ戻してbounded fix／re-reviewを行う。
8. 三者passed後、Mainがfinal report ledgerを更新しfinal commitを作成、post-commit clean checkを行う。
9. S99は自身がownerであるportionsだけを`passed`にする。
10. Mainが全`required=yes` aggregateを再計算し、全件`closed`の場合だけFinal Exitをunblockする。

#### delegation contract

- delegated role: reviewer-only。product mutationはowning stepへ戻す。
- allowed repository changes by reviewer: none。
- required verification: repository-wide commands、graph structural test、three fresh reviewer passes。
- stop conditions: failed／unavailable／denied reviewer、open material ledger、dirty tree、missing pre-S99 portion、invalid graph。
- output required: reviewer results、graph result、Main disposition、final commit scope、remaining risks。

#### 具体テストケース一覧

- `tc-s99-001` quality: full suite and package verification
  - 前提: S01〜S90のrequired owner portionsがpassedし、S99 portionsだけがopen。
  - 操作: full tests、lint、build、validate、three reviewersを実行する。
  - 期待結果: commands成功、three fresh reviewers passed、open material blocker 0、final report commit、post-commit clean。
  - 失敗検出: focused-only green、docs drift、unreviewed integrated riskを検出する。
  - 検証方法: `uv run pytest -q && make lint && uv build && ./spec-dock/scripts/spec-dock validate`
  - 関連 required closure: `CLOS-REQ-020` / S99、`CLOS-S99-001` / S99

- `tc-s99-002` structure: Closure owner graphをdeterministically検証する
  - 前提: canonical Planのsummary table、required Closure tables、step dependencies、全step closure contractsを入力とする。
  - 操作: read-only parser／inspectionで次を検証する。
    1. `required=no` summary aliasはowner／stateを持たない。
    2. summary aliasがstep closure targetまたはS99 state targetに現れない。
    3. every `required=yes` ownerはallowed ordered step set内。
    4. `Final Exit` ownerは0。
    5. owner listはduplicateなし、step order ascending。
    6. each step closure contractがclaimするID setはClosure Indexでそのstepをownerに持つsetとexact一致。
    7. S08 claim setが`CLOS-REQ-013`, `014`, `016`, `019`, `021`, `023`, PA-NF 11 rows, `CLOS-RISK-004`だけと一致。
    8. S99 entry prerequisiteはpre-S99 portionsだけで、S99 portionsを事前要求しない。
    9. dependency edgesはallowed step orderのforward edgeだけ。
    10. graphはacyclic。
  - 期待結果: violations 0。each required rowには少なくとも一つのexecutable pre-terminal ownerがあり、S99完了後に全aggregateがclosedへ到達可能。
  - 失敗検出: stateless alias close、undeclared owner、Final Exit cycle、S08 overclaim、S99 self-dependencyを防ぐ。
  - 検証方法: Main-owned read-only structural parser／inspection。input、scriptまたはquery SHA、resultを`report.md#Final-Quality-Gate`へ保存する。
  - 関連 required closure: `CLOS-S99-001`

#### report evidence destination

Mainが`report.md#Final-Quality-Gate`へpre-S99 portion inventory、graph result、full verification、three reviewer results、S99-owned portion result、final commit scopeを記録する。

#### step closure contract

S99は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-020` / S99
- `CLOS-S99-001` / S99

S99 entry時点では全pre-S99 portionsがpassedしていなければならない。full verification、graph violations 0、three fresh reviewers passed、final report update、final commit、post-commit clean checkが揃った場合だけ上記S99 portionsをpassedにする。

`CLOS-QUALITY` summary aliasにstateを付与しない。S99 portionsをpassedにした後、全required aggregateがclosedであることを再計算する。

#### step gate

failed／unavailable／denied／waived／provisionalをpassedとして扱わない。pre-S99 portion missing 0、graph violations 0、three fresh reviewer passes、clean final commit、全required aggregate closedを必要とする。

## 10. Final Exit Contract

Final ExitはClosure ownerではなく、S99後のexternal shared delivery handoffである。Final Exit entry／executionはClosure Indexのowner portionまたはaggregateを変更しない。

### Entry conditions

- S01〜S90のrequired owner portions passed。
- S99-owned portions passed。
- 全`required=yes` aggregate state=`closed`。
- summary alias state 0。
- final report ledger、final commit、post-commit clean check complete。
- current source branchがintended Issue branch。
- unresolved material blocker 0。

### External delivery handoff

1. Mainはcurrent shared Issue delivery workflowを使用する。
2. one Issue／one branch／one Delivery PRを維持する。
3. PR Delivery／Merge Preparation evidence、required checks／reviews／blockersはshared workflow owner contractに従う。
4. Humanだけがmergeを決定・実行する。
5. merge後verificationとIssue lifecycle completionはcurrent shared workflowへ従い、本Planはそのsemanticsを再定義しない。

### Post-handoff evidence

PR URL、required check／review result、Human merge decision、post-merge verification、Issue lifecycle resultはReportまたはcurrent shared destinationへexternal completion evidenceとして記録する。

このpost-handoff evidenceはS99 admission prerequisite、Closure Index owner portion、S99 aggregate closureへ遡及的に組み込まない。PR／merge failureはshared workflowでblockし、S99を自己循環させない。ただしsource-changing correctionが必要な場合は該当owner portionとS99 evidenceをinvalid化し、owning stepへ戻す。

### Stop conditions

- required aggregate open。
- S99 incomplete。
- required review/check未完了。
- unresolved blocker。
- dirty tree。
- wrong branch/base。
- source drift。
- Human merge decision欠落。

Planning result、S99 result、PR readinessのいずれもHuman mergeまたはIssue completionを自己主張しない。

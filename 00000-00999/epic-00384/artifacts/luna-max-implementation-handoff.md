---
種別: Implementation Handoff
対象: "GPT-5.6 Luna / reasoning Max"
Issue: "iss-00392"
最終更新: "2026-09-02"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "f96d031ea86d3757374f3de14d588f1ba09a0864"
---

# Luna Max Implementation Handoff

## 1. Authority order

1. Execute Issue `plan.md`.
2. Use Issue Requirement for behavior and Issue Design for exact symbols/schemas.
3. Treat `provider-lifecycle-wire-contract.md` as the only public wire authority: 37 codes, 123 rows, four record and sixteen public JSON review goldens.
4. Treat `active-failure-disposition-register.md` rule `ISS387-THREE-WAY-V2` as the only #387 admission/terminalization authority.
5. Use Epic R/D/P and ADR for merge governance.
6. Follow root AGENTS until its S60/S70 owned-section transitions.
7. Do not choose Product, Policy, Security, filesystem, CI evidence, migration or closure behavior. A mismatch is a stop.
8. Never merge or write required contexts.

## 2. PR graph

```text
#387 human merge -> S00
PR-A: S10 -> S20 -> S30 only main gate
PR-B: S40 internal -> S50 internal -> S60 only main gate
PR-C: S70 internal -> external PRC_COMPAT_HEAD
      -> human context transition
      -> distinct PRC_FINAL_HEAD (provider-tests removal only)
      -> S80 read-only final evidence -> only PR-C main gate
human merge -> measured external closure
```

S40/S50/S70 are never merge-ready. S80 owns no tracked path.

## 3. Fixed lifecycle

```text
roots: spec-dock/docs, templates, system, scripts
slots: .agents/skills/spec-dock, .agents/skills/spec-dock-grill-with-docs
record: spec-dock/spec-dock.version
markers: <slot>/.spec-dock-provider-slot.json
seeds: spec-dock/.gitignore, .github/workflows/ci.yml
```

Record exact keys are `schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots`. Resume tuple is operation/candidate/policy. Fresh init alone is create-if-absent; all other intents preserve-only.

## 4. Persistent stage and terminal cleanup

```text
<repo-parent>/.spec-dock-provider-stages-v1/
  repositories/<repository-key>/ACTIVE.json
  repositories/<repository-key>/stages/<tuple-key>/STAGE-OWNER.json
```

ACTIVE is the only index; no scan. Its exact private fields include `result_family=install|legacy-migration|update|uninstall`. Before normal dispatch:

- terminal record + ACTIVE ready -> atomic terminal-cleanup;
- stage present -> remove registered entries/stage;
- stage already absent -> continue;
- remove content-bound ACTIVE and fsync parent;
- ACTIVE already absent -> fsync parent and continue;
- crash after ACTIVE unlink -> next invocation fsyncs then dispatches;
- cleanup failure -> public `terminal-cleanup-failed`, exact old-family retry, one failed `@provider-stage` action;
- cleanup success -> requested new operation may differ from old tuple.

Cleanup-warning completions also expose exact retry and leave cleanup recoverable.

## 5. Independent purpose workspaces

Create one workspace and retain one non-serializable handle for each used purpose. Exact variables:

```text
ISS392_WS_ADMISSION
ISS392_WS_BASELINE_BUILD
ISS392_WS_PROTECTED_WITNESS
ISS392_WS_FULL_REGRESSION_S00
ISS392_WS_FULL_REGRESSION_S30
ISS392_WS_FULL_REGRESSION_S60
ISS392_WS_TRIPWIRE
ISS392_WS_FRESH_CONSUMER
ISS392_WS_WORKFLOW_API
ISS392_WS_ARTIFACT_DOWNLOAD
ISS392_WS_ATTESTATION_DRAFT
```

Never create an aggregate external-root variable. Never infer cleanup authority from an env-var path. The orchestrator owns handles and registered children. Repository `.workbench` is protected read-only.

## 6. Issue #387 admission

The #387 report block contains only:

```text
schema_version,kind,issue_id,rule_id,entries
```

It has twelve mappings and no repository/PR/commit/tree/merge identity. S00:

1. reads Issue #387 timeline/cross-reference PR numbers;
2. fetches each PR and exact head SHA;
3. validates `GET /commits/<head>/pulls` contains the same PR;
4. filters same repo, base main, merged, report present, merge reachable;
5. requires exactly one;
6. requires PR-head tree equals merge tree;
7. reads report/ledger/collection from merge tree;
8. applies `ISS387-THREE-WAY-V2`.

No new #387 boundary or report-to-merge identity/tail rule. Zero/multiple PR or any mapping/signature drift stops before S10.

## 7. Step ownership highlights

### S10–S30

Lifecycle package, workspace helper, stage namespace, model/candidate/service/fault/wire tests. S30 adds mandatory cleanup recovery. Public route/dogfood stay old.

### S40/S50

Provider/public/lifecycle docs and external synthetic migration/tripwire only. Checked-in dogfood remains exact legacy.

### S60

Old engine/tests removal; current Provider CI retarget; retained Full Regression independent `full-regression-s60` workspace; ledger/timing/conftest/lane consumers; lifecycle docs; AGENTS lifecycle paragraphs; complete dogfood migration; report implementation summary. Keep current test-policy machinery operational.

### S70

Final provider gate/evidence/environment/tests/workflow, consumer-first old removal, final AGENTS/test-policy docs, complete second dogfood update and tracked report method only. Push compatibility head externally; actual head identity is not written to report.

### S80

Tracked none. Create distinct final head by compatibility-job removal, rerun final workflow, use purpose-specific API/download/attestation workspaces, verify bytes, post pre-merge comment. No local build/update/sync.

## 8. Compatibility workflow contract

Compatibility graph adds:

```text
provider-tests: [provider-build-artifacts,provider-attestation]
```

Permissions are `actions:read`, `contents:read`, `pull-requests:read`. It independently creates workflow-api and artifact-download workspaces; downloads `provider-candidate-<compat-sha>` and `provider-evidence-<compat-sha>`; fetches exact run/jobs/artifacts API JSON; invokes the same verifier flags as S80; builds zero; ignores `.github/provider-gate-canary-red`. Structural tests enforce every requirement.

Final head differs from compatibility head only by removal of this job and must have a distinct SHA/tree. Final run rebuilds once for final head.

## 9. Evidence and fixtures

All evidence JSON is exact compact UTF-8 plus LF. `EVIDENCE-FIXTURE-V1` uses distinct identities:

```text
spec freeze: 8*40
implementation base: 9*40
compatibility head/tree: a*40 / b*40
final head/tree: c*40 / d*40
merge commit: e*40
report blob: f*40
```

Candidate, roles, receipts, aggregate, pre/post/Epic payloads and comment receipts have recomputed byte sizes/hashes. Do not hand-copy old fixture hashes.

## 10. Closure sequence

1. Human merges final head.
2. Verify final-head tree equals merge tree.
3. Run `python3 ./spec-dock/scripts/spec-dock issue finish`; verify actual result.
4. Run `python3 ./spec-dock/scripts/spec-dock close --id iss-00392`; read #392 close event.
5. Generate/post/read back `post-merge-closure-v1` on #392; create external comment receipt.
6. Re-evaluate Epic acceptance.
7. Run `python3 ./spec-dock/scripts/spec-dock close --id epic-00384`; read #384 close event.
8. Generate/post/read back `epic-closure-v1` on #384; create external comment receipt.

Pre-merge comment targets #392 before merge. No payload includes its own future comment ID/hash. Post payload may reference the existing pre comment; Epic payload may reference the existing post comment.

## 11. Stop matrix

| Condition | Required action |
|---|---|
| #387 report includes identity/future fact or PR discovery is zero/multiple | stop before S10 |
| unknown register node/signature/mapping | stop before S10 |
| aggregate external root/path-only cleanup/repository workbench write | destructive stop |
| ACTIVE/stage/result-family/registered-entry mismatch | fail closed |
| terminal cleanup failure not exact wire/retry | block dispatch |
| wire count/golden/relation mismatch | test defect; do not invent |
| S40/S50 dogfood drift | restore exact legacy; no merge |
| S60 current PR/main-push gate not independently GREEN | block PR-B |
| compatibility verifier misses candidate/evidence/API input, packages, or sees canary | block context transition |
| compatibility/final identities equal or final diff beyond job removal | repeat S70/two-head sequence |
| final evidence not rerun on final head | block PR-C |
| tracked report contains actual compatibility/final identity | remove cycle; new head/evidence |
| closure payload precedes measured finish/close facts | invalidate closure |
| comment receipt/body/actor/timestamp mismatch | invalidate dependent closure |
| merge tree mismatch | do not finish Issue |

## 12. Definition of done

Only S30/S60/S80 are merge gates. All temporary data uses independent handles, terminal cleanup cannot permanently block new intent, #387 report is mapping-only, compatibility and final evidence are byte-verified on distinct heads, closure is measured in order, human merge remains pending until handoff, and `owner_decisions_required=[]`.

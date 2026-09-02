---
種別: Implementation Handoff
対象: "GPT-5.6 Luna / reasoning Max"
Issue: "iss-00392"
最終更新: "2026-09-02"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "0fafbf3e02d2fcd5b622d6a997323e0f98eb1c78"
---

# Luna Max Implementation Handoff

## 1. Authority order

1. Execute Issue `plan.md`.
2. Use Issue Requirement for behavior and Issue Design for exact symbols/schemas.
3. Treat `provider-lifecycle-wire-contract.md` as the only public wire authority: 38 codes, 142 rows, four record and thirty-three public JSON review goldens.
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

## 4. Persistent stage, deferred request and terminal cleanup

ACTIVE is the only index and stores old tuple/result family, immutable `cleanup_token`, and nullable normalized `deferred_invocation`. Before normal dispatch:

1. classify role syntactically: token absent is desired; the exact generated hidden `--provider-cleanup-token <active token>` form is cleanup-retry;
2. atomically store the first no-token desired request, even when its base form is update/init-force; tokenized retry, repeat, or third desired command preserves it byte-for-byte;
3. validate/remove registered stage and ACTIVE;
4. on failure return the tokenized cleanup retry now and deferred desired command after cleanup;
5. on success return deferred desired command only, or no action;
6. never dispatch lifecycle in the cleanup invocation.

Follow only public `continuation`. Never derive intent from result family or “same command”. Required RED: old install cleanup + desired uninstall; failure -> tokenized init-force retry -> success -> exact deferred uninstall; no-token desired update is distinct from tokenized update retry; pure retry with no deferred request -> success/no action.
## 5. Private owner roots and exact reserved trees

Each purpose creates a private owner root/live handle, then reserves the exact child in Issue Design D-007. Only the reserved child path is exported. Examples: baseline-build exports its reserved `dist`; Full Regression exports reserved `full-regression`; artifact-download exports reserved `artifacts`; attestation exports reserved `attestation`; provider jobs export their `output|role|aggregate|verification` tree. Never append an implicit purpose directory to an owner root.

The live owner alone reserves, pre-registers each fixed output or closed subtree policy, spawns, seals, begins upload, confirms actual artifact ID/name/digest and cleans. Children cannot create registration authority or clean. Exact registration policy IDs and layouts are Issue Design D-007. Unknown owner-root entry, unregistered or policy-invalid descendant, child escape, owner death, path-only reopen or cleanup before upload confirmation is a stop/preserve condition. All plan commands take the exported reserved tree.

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

Final Provider Gate/evidence/environment/tests/workflow, exact nine command argv, raw ZIP transport/safe extraction, empty workflow permissions plus read-only job overrides, consumer-first old removal, final docs, second dogfood update and tracked report. Commit compatibility head, complete human context transition, then final head by only removing provider-tests. Store identities externally; no merge.

### S80

Tracked none. Read final head, download and preserve authenticated raw candidate/evidence ZIPs plus API snapshots into exact reserved trees, safe-extract, invoke the aggregate verifier with raw/extracted/API inputs, verify permissions/metrics, and post/read pre-merge comment. No commit, build, update or sync.

## 8. Compatibility workflow and permissions

Compatibility job needs producer+attestation, creates one private provider-verification owner/tree, stores API snapshots and raw candidate/evidence ZIPs there, registers empty extraction destinations and calls the verifier, which performs extraction. It polls provider-gate terminal state and selects exact `compatibility-aggregate-green` or `compatibility-aggregate-canary`; external canary readback uses `compatibility-canary-post-run`. It builds zero and ignores canary.

Workflow-level `permissions: {}`. Exact overrides: build `contents:read`; Linux/sdist/macOS/attestation `actions:read,contents:read`; gate `contents:read`; compatibility `actions:read,contents:read,pull-requests:read`. No workflow write permission. Human comment POST/readback is outside workflow.

Final head removes only compatibility job and reruns all authoritative evidence.

## 9. Provider Gate and fixture authority

Issue Design D-013–D-026 is complete. Implement exactly nine subcommands and their ordered argv arrays, required flags, path containment, repeated role order, stdout/stderr, exits 2–14 and schemas. Raw archive bytes are first-class inputs; extracted-only verification is invalid. `RAW-ARCHIVE-DIGEST-V1` and `EVIDENCE-FIXTURE-V5` are serializer/transport oracles; regenerate size/SHA from displayed bytes, never copy an old hash after schema change.

The 38-code/142-row wire remains finite but public result is now 23 keys with continuation. Implementer must not alter counts without canonical review.

## 10. Closure and post-sync recovery

1. Human merge; verify tree equality.
2. Run issue finish attempt 1 with start/end capture.
3. If exit 0, accept attempt 1.
4. If and only if #392 closed + active cleared + issue-finish post-sync failed, bind the unique original close event, run exact `active set --id iss-00392`, verify exit/stdout/stderr, run exact `active show` and require `iss-00392`, then run issue finish attempt 2 with `already_closed=true` and no new close event. Do not expect or record active-set post-sync.
5. Repeat restore+finish once for attempt 3 if the second post-sync fails. Three failures stop; no post payload.
6. Post payload records all finish/restore rows and selects final successful attempt. No `close --id iss-00392`.
7. Post/read receipt on #392, then measure Epic acceptance, close/read #384, and post/read Epic receipt.

Repeated sync failure, ambiguous/multiple close event, reopen or active restoration failure is a hard stop.

## 11. Stop matrix

| Condition | Required action |
|---|---|
| #387 report includes identity/future fact or PR discovery is zero/multiple | stop before S10 |
| unknown register node/signature/mapping | stop before S10 |
| aggregate external root/path-only cleanup/repository workbench write | destructive stop |
| exported path is owner root or does not equal the exact reserved-tree mapping | preserve workspace; block step |
| ACTIVE/stage/result-family/registered-entry mismatch | fail closed |
| cleanup retry overwrites deferred desired request or continuation is ambiguous | block dispatch; fix wire implementation |
| cleanup warning/failure uses an un-tokenized retry or terminal cleanup lacks actual echo/cleanup-only return | block dispatch |
| wire count/golden/relation mismatch | test defect; do not invent |
| S40/S50 dogfood drift | restore exact legacy; no merge |
| S60 current PR/main-push gate not independently GREEN | block PR-B |
| verifier combines workspace trees, pre-extracts, has wrong phase/job-state/evidence-name relation, misses bytes, packages, or reads canary | block context transition |
| raw archive not preserved/rehashed/safe-extracted or workflow permission differs | block PR-C |
| compatibility/final identities equal or final diff beyond job removal | repeat S70/two-head sequence |
| final evidence not rerun on final head | block PR-C |
| S80 creates a commit or tracked change | invalidate final evidence; return to S70 |
| closure payload precedes measured finish/close facts | invalidate closure |
| post-sync retry exceeds three attempts, active-set output or active-show readback fails, or close event is ambiguous | no closure payload |
| comment receipt/body/actor/timestamp mismatch | invalidate dependent closure |
| merge tree mismatch | do not finish Issue |

## 12. Definition of done

Only S30/S60/S80 are merge gates. All temporary data uses independent handles, cleanup continuation cannot replace desired intent, each environment path is an exact reserved tree backed by a live handle, Provider Gate raw/extracted/API bytes and permissions are exact, #387 report remains mapping-only, distinct heads are verified, post-sync recovery selects one measured successful interval, human merge remains pending, and `owner_decisions_required=[]`.

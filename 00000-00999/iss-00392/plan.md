---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-02"
依存: ["requirement.md", "design.md", "../../plan.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "../../artifacts/provider-lifecycle-wire-contract.md", "../../artifacts/active-failure-disposition-register.md"]
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "f96d031ea86d3757374f3de14d588f1ba09a0864"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Execution rules

1. Entry point is this Plan; Requirement defines behavior, Design defines components/schemas, wire/register are normative finite data.
2. Product source of truth is `src/spec_dock/`; provider-first, dogfood only at S60/S70.
3. Behavior changes are test-first. Existing RED may substitute only when exact node/failure is recorded.
4. Every step includes implementation and focused verification.
5. S40/S50 are PR-B internal; S60 is its only gate. S70 is PR-C internal; S80 is its only gate.
6. S60 keeps current workflows independently GREEN and does not require S70 tooling.
7. S70 creates replacement consumers/providers before old removal.
8. S80 owns no tracked path and runs no local build/update/sync.
9. Agent never merges or changes required contexts. Human operations are exact handoffs.
10. Tracked report has no actual compatibility/final head/run identity or post-merge fact.
11. Any stop is forward-fixed in #392; no new Issue, toggle, skip, approved failure or fallback.

## 2. Common boundaries

### Protected/no-touch

- all repository `spec-dock/.workbench/**`;
- all initiatives/artifacts except exact #392 report/meta under exclusion contract;
- seeds, unknown data and unrelated skills;
- Issue #387 canonical files;
- Issue #372 canonical evidence;
- release/tag/PyPI;
- human settings/merge.

### Independent purpose workspaces

The orchestrator creates each used workspace independently and retains its non-serializable handle. Exact environment variables:

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

No an aggregate external-root variable, shared parent, implicit purpose subdirectory or path-only cleanup. A child path such as `$ISS392_WS_WORKFLOW_API/run.json` is registered to that workspace handle before creation.

### Full Regression command rule

```bash
uv run python -m scripts.quality.verify_full_regression   --shards 4   --artifact-dir "$ISS392_WS_FULL_REGRESSION_<STEP>"
```

S00/S30/S60 substitute the exact variable. Default verifier output is forbidden.

## 3. Step graph

```text
S00 admission
 -> PR-A S10 -> S20 -> S30 main gate
 -> PR-B S40 internal -> S50 internal -> S60 main gate
 -> PR-C S70 internal compatibility head/context/final-head commit
 -> S80 read-only final evidence/main gate
 -> human merge -> measured external closure
```

## I392-S00 — Specification, #387, protected witness and legacy admission

**Objective and visible outcome**

Verify specification lineage, independently discover/admit the unique merged #387 PR, capture protected/legacy/current-gate baseline, and produce no Product change.

**Exact owned repository paths/symbols**

Read-only repository. Authorized tracked write only #392 `report.md` pre-freeze admission summary and necessary `.meta.json updated_at`. Temporary outputs only in independently-created admission, baseline-build, protected-witness and full-regression-s00 workspaces.

**Explicit non-owned/no-touch**

All production/tests/workflows, #387 files, dogfood, repository workbench and settings.

**Prerequisites/dependency**

#387 human merged; replacement imported and `SPEC_FREEZE_COMMIT` recorded; clean tree; implementation base contains both.

**RED evidence**

Admission parser rejects: report identity field; missing/duplicate mapping; zero/multiple timeline+association PRs; wrong repo/base/state; head-tree/merge-tree mismatch; unreachable merge; signature/lineage/successor drift; broad exclusion; workspace containment/owner/mode/sentinel failure; legacy dogfood drift.

**Smallest action**

1. Create separate workspaces/handles for admission, baseline build, protected witness and S00 Full Regression.
2. Verify manifest payload hashes against `SPEC_FREEZE_COMMIT` blobs.
3. Fetch Issue #387 timeline; collect same-repository PR references.
4. Fetch each PR and its exact head commit association; filter and require one.
5. Fetch head/merge commits; verify tree equality and main/implementation-base lineage.
6. Read report/ledger/collection from merge tree; parse mapping-only schema4; apply register.
7. Capture protected/exclusion manifests outside repository.
8. Verify exact dogfood `0.2.3
`, marker absence and fixed-tree digests.
9. Build baseline `0.2.3` once in baseline-build workspace and capture hashes.
10. Run current ordinary/full gates with external output.

**Focused verification commands**

```bash
# Paths are created/exported by the long-lived handle-owning orchestrator.
gh api --paginate -H 'Accept: application/vnd.github+json'   repos/chemitaro/spec-dock/issues/387/timeline   > "$ISS392_WS_ADMISSION/issue-387-timeline.json"
# The admission parser fetches each referenced PR and /commits/<head>/pulls.
uv build --sdist --wheel --out-dir "$ISS392_WS_BASELINE_BUILD/dist"
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression   --shards 4 --artifact-dir "$ISS392_WS_FULL_REGRESSION_S00"
python3 ./spec-dock/scripts/spec-dock validate
```

**Expected result**

Exactly one merged #387 PR; head-tree=merge-tree; mapping-only report valid; register admission deterministic; current gates GREEN; baseline and legacy/protected witnesses fixed; repository workbench unchanged.

**Evidence in tracked report**

SPEC_FREEZE/implementation base, externally obtained #387 PR/head/tree/merge/tree equality, report/ledger/collection blobs/hashes, admitted formula, baseline package hashes, protected/exclusion summaries, commands. No future #392 head identity.

**Stop/escalation owner**

Any mismatch stops before S10. Owner: canonical spec/repository owner. Luna does not edit #387 or choose a branch.

**Cleanup**

Handle-clean each workspace only after retained hashes are recorded; unknown content preserves workspace and stops.

**Merge invariant**

No code diff; not a merge point.

**Trace**

I392-RQ-001–007; D-007–010; register.

## I392-S10 — Fixed model, candidate, record and complete wire

**Objective and visible outcome**

Add dormant strict model/candidate/legacy parser and all finite wire values including terminal-cleanup result.

**Owned paths/symbols**

```text
src/spec_dock/provider_lifecycle/{__init__,model,candidate,legacy_023,public_result}.py
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_{model,candidate,wire_contract,public_result}.py
tests/unit/infra/test_provider_assets.py
```

**Non-owned/no-touch**

Public CLI route, filesystem mutations, old engine/workflows, checked-in dogfood.

**Prerequisites**

S00 GREEN.

**RED evidence**

37-code/123-row inventory; four record and sixteen public JSON goldens; terminal-cleanup code/retry/action/guidance; warning retries; strict result-family private enum; unknown/duplicate/order rejection; candidate/legacy safety.

**Smallest action**

Implement enums/types/parsers/digests and table-driven adapter only. No public dispatch.

**Verification**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_model.py   tests/unit/infra/test_provider_lifecycle_candidate.py   tests/unit/infra/test_provider_lifecycle_wire_contract.py   tests/unit/infra/test_provider_lifecycle_public_result.py   tests/unit/infra/test_provider_assets.py
make lint
```

**Expected/evidence**

All finite wire tests GREEN, matrix count exact, no public behavior change. Record RED/GREEN nodes and parsed fixture hashes.

**Stop/cleanup/merge invariant**

Unknown wire choice or extra record/path stops to spec owner. Remove temp caches. Internal PR-A checkpoint; old public product remains.

**Trace**

I392-RQ-010–017; D-001–003; wire.

## I392-S20 — Descriptor filesystem, persistent stage and fresh install

**Objective and visible outcome**

Implement safe namespace/ACTIVE/stage, fresh container bootstrap and fresh install direct service, including process-restart points.

**Owned paths/symbols**

```text
src/spec_dock/provider_lifecycle/{filesystem,external_workspace,stage_namespace,service}.py
tests/unit/infra/test_provider_lifecycle_{filesystem,workspace,stage_namespace,service,faults}.py
```

**Non-owned/no-touch**

Public CLI, old engine/workflows, dogfood.

**Prerequisites**

S10 GREEN; supported Linux/macOS native primitives available for platform tests.

**RED evidence**

Independent workspace handles/no aggregate root; repository containment and cleanup attacks; exact sentinels; allocation/restart/bootstrap; no scan; fresh seed policy; no-follow/hard-link/native primitive; fault after each durable boundary.

**Smallest action**

Implement workspace helper, namespace/index/owner, bound filesystem and fresh install service. Terminal cleanup transition can be introduced dormant and completed in S30.

**Verification**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_workspace.py   tests/unit/infra/test_provider_lifecycle_stage_namespace.py   tests/unit/infra/test_provider_lifecycle_filesystem.py   tests/unit/infra/test_provider_lifecycle_service.py   tests/unit/infra/test_provider_lifecycle_faults.py   -k 'fresh or bootstrap or workspace or stage or binding'
make lint
```

**Expected/evidence**

Fresh direct service reaches ready; all injected crashes are classified; repository workbench/protected data unchanged. Record identities/fault table.

**Stop/cleanup/merge invariant**

Generic rename, scan, aggregate workspace, serializable cleanup or recursive container removal stops. Handle-clean test workspaces. Internal PR-A checkpoint.

**Trace**

I392-RQ-005–014; D-004–008.

## I392-S30 — Update, resume, terminal cleanup and PR-A gate

**Objective and visible outcome**

Complete update/exact-tuple resume and mandatory terminal cleanup so old cleanup cannot permanently block any later intent.

**Owned paths/symbols**

S10/S20 lifecycle modules/tests, especially `recover_terminal_cleanup()` and wire constructor tests.

**Non-owned/no-touch**

CLI old route, dogfood, workflows/policy.

**Prerequisites**

S20 GREEN; independent `ISS392_WS_FULL_REGRESSION_S30` handle exists.

**RED evidence**

- ACTIVE ready+terminal record promotion;
- stage present/already absent;
- ACTIVE present/already absent;
- crash after stage removal and after ACTIVE unlink before fsync;
- cleanup retry with next request same/different operation;
- repeated cleanup failure exact `terminal-cleanup-failed`;
- warning result non-null retry and next-call cleanup;
- result-family retry mapping;
- cross-tuple lifecycle resume remains blocked before terminal state.

**Smallest action**

Implement cleanup prelude before classifier/dispatch, update/resume and no-op/repair publication. Do not add rollback/progress list.

**Verification**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_*.py
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression   --shards 4 --artifact-dir "$ISS392_WS_FULL_REGRESSION_S30"
```

**Expected/evidence**

All cleanup crash matrices converge; different next intent proceeds after cleanup; exact failure wire emitted; public route still old; current gates GREEN. Record action/phase/retry bytes and subprocess restart table.

**Stop/cleanup/merge invariant**

Old tuple permanent block, unsafe absent handling or unclosed wire blocks PR-A. Handle-clean external output. S30 is only PR-A main gate; main remains old public product.

**Trace**

I392-RQ-008–017; D-002–006.

## I392-S40 — Public lifecycle/docs cutover with dogfood frozen

**Objective and visible outcome**

Wire final `0.2.4` CLI/uninstall/purge trap and provider-side lifecycle documentation on PR-B branch while checked-in dogfood stays exact legacy.

**Owned paths**

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/{model,service,public_result}.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
README.md lifecycle sections
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md lifecycle sections
CLI/public wire tests
```

**No-touch**

All checked-in dogfood roots/slots/record/markers, root AGENTS, workflows/policy.

**Prerequisites**

S30 merged/GREEN; S40 starts one PR-B that continues through S60.

**RED/action/verification**

Add failing CLI matrix for aliases, purge trap, terminal cleanup result/warning retry, text/JSON/exit and wrapper. Implement public wiring/version/docs. Verify focused CLI with current flags, lint and external protected/dogfood witnesses.

```bash
uv run pytest --run-full-regression --full-regression-shard -q   tests/cli_runtime/test_provider_lifecycle.py   tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_update.py
make lint
```

**Expected/evidence**

PR-B branch exposes final route, dogfood record remains exact `0.2.3
` and fixed trees/marker absence byte-identical. Record CLI goldens and witness equality.

**Stop/cleanup/invariant**

Any dogfood change, bridge/toggle/purge mutation or unknown wire stops. Internal checkpoint only; no merge handoff.

**Trace**

I392-RQ-015–020; wire.

## I392-S50 — Exact legacy and old-package tripwire on external consumers

**Objective and visible outcome**

Prove exact migration/uninstall and old-package mutation-zero without changing checked-in dogfood.

**Owned paths**

```text
src/spec_dock/provider_lifecycle/{legacy_023,service}.py
tests/integration/test_provider_lifecycle_{artifacts,tripwire}.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/**
```

**No-touch**

Checked-in dogfood, old engine deletion, current workflows/settings.

**Prerequisites**

S40 GREEN; independent baseline-build/tripwire/fresh-consumer handles.

**RED/action/verification**

Exact/modified roots/slots/recovery, preserve-only policy, fault resume, old command matrix, Python/native positive controls, terminal-cleanup after migrated operation. Build only in baseline-build purpose; consumers under fresh-consumer/tripwire purpose.

```bash
uv build --sdist --wheel --out-dir "$ISS392_WS_BASELINE_BUILD/final-dist"
uv run pytest --run-full-regression --full-regression-shard -q   tests/integration/test_provider_lifecycle_artifacts.py   tests/integration/test_provider_lifecycle_tripwire.py
```

**Expected/evidence**

Exact migration GREEN, old events empty, controls caught, all temp outside repo, checked-in dogfood unchanged.

**Stop/cleanup/invariant**

Any old mutation/control failure/dogfood drift blocks PR-B. Handle-clean external dirs. S50 is internal; continue S60.

**Trace**

I392-RQ-018–019; D legacy/tripwire.

## I392-S60 — Terminalization, retained gates, complete dogfood and PR-B gate

**Objective and visible outcome**

Remove old engine/tests, terminalize admitted failures, keep current PR/main-push gates independently GREEN with external output, update lifecycle docs/AGENTS and perform one complete dogfood migration.

**Owned paths**

```text
src/spec_dock/managed_distribution.py                         delete
src/spec_dock/assets/managed_distribution.json                delete
old distribution tests                                       delete
src/spec_dock/context_pack.py
.github/workflows/provider-ci.yml                              retarget only
.github/workflows/provider-full-regression.yml                 external output only
tests/unit/test_provider_test_lanes.py
full-regression-ledger.json
full-regression-timing-weights.json
tests/conftest.py
scripts/quality/full_regression_{baseline,verify}.py            retained
failure-owner source/tests from register
README/provider lifecycle docs
root AGENTS.md lifecycle/uninstall paragraphs only
all four dogfood roots, both slots, record and markers
#392 report implementation summary
```

**No-touch**

Final gate redesign, AGENTS test-policy sections, old policy provider deletion, protected data/seeds.

**Prerequisites**

S50 GREEN; register admission fixed; independent S60 Full Regression/protected/fresh-consumer handles.

**RED evidence**

Each admitted failure focused RED/closed resolution; current Provider CI deleted path structural RED; lane/ledger stale reference RED; retained workflow default/repository-workbench RED; dogfood exact legacy precondition; terminal cleanup/stage residue; lifecycle docs/AGENTS stale phrase checks.

**Smallest action**

1. Fix/supersede register rows to normal pass; active/approved zero.
2. Extract surviving context behavior and delete old engine/tests.
3. Retarget current provider-ci only to S10–S50 successors.
4. Update lane/ledger/timing/conftest exact references.
5. Modify retained workflow to create one independent full-regression-s60 workspace below runner.temp, pass/upload exact path and cleanup by handle.
6. Update lifecycle docs and AGENTS lifecycle paragraphs.
7. With provider bytes settled, apply new service once to exact legacy repository dogfood; commit complete roots/slots/record/markers.
8. Validate provider/dogfood/protected parity and both current gates.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/test_provider_test_lanes.py
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression   --shards 4 --artifact-dir "$ISS392_WS_FULL_REGRESSION_S60"
make lint
python3 ./spec-dock/scripts/spec-dock validate
# workflow structural tests require independent runner.temp workspace and no spec-dock/.workbench path
```

**Expected result/evidence**

Old engine absent; active/approved zero; current PR gate GREEN; retained main-push verifier GREEN; no S70 dependency; dogfood complete ready 0.2.4 with matching digest/markers; protected/workbench/seeds exact; no ACTIVE/stage residue.

**Stop/escalation**

Unterminalized row, deleted workflow consumer, default artifact-dir, repository workbench output, partial dogfood, protected drift or current gate failure blocks PR-B. Owner: Product/test/CI.

**Cleanup**

Handle-clean all purpose workspaces after evidence retained. Do not clean repository workbench or stage namespace sentinels.

**PR-B merge invariant**

S60 is only PR-B gate. Main receives complete final lifecycle and coherent current gates; S40/S50 commits are not handoffs.

**Trace**

I392-RQ-020–021/030/032; D-011–012; register.

## I392-S70 — Consumer-first final gate, compatibility sequence and second dogfood update

**Objective and visible outcome**

Build final gate/evidence implementation, remove old policy consumer-first, complete second dogfood update, finalize tracked report method, push compatibility head, complete no-gap context transition and create distinct final head. No main merge.

**Owned paths**

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_{gate,workflow}.py
tests/provider_test_ownership.json
Makefile
scripts/static_analysis/run.sh
.github/workflows/provider-ci.yml
root AGENTS.md test-policy/provider-gate sections
README/provider docs test-policy sections
all remaining old policy consumers, then providers/data/workflow deletion
all four dogfood roots, both slots, record and markers
#392 report pre-freeze method/implementation facts only
```

**No-touch**

Protected paths/seeds; actual compatibility/final identities are not written to report; human settings are external.

**Prerequisites**

PR-B S60 main state; current gates GREEN; human admin available.

**RED evidence**

Evidence schemas/fixtures/hash chain; exact job needs; one producer; compatibility job candidate/evidence/API downloads, exact verifier flags, permissions, no build, canary isolation; old consumer inventory; final diff only job removal; actual head identities forbidden in report; second dogfood completeness.

**Smallest action**

1. Add final tooling/environment/workflow/tests.
2. Retire/replace every old consumer, prove zero, then delete old providers/ledger/timing/sharder/conftest/main-push workflow.
3. Update final operator/test-policy docs.
4. Perform complete candidate-wide dogfood update; finalize tracked report without actual head/run identities; commit.
5. Push and record actual compatibility SHA/tree externally.
6. Run compatibility workflow; require both contexts GREEN. Compatibility provider-tests independently verifies candidate/evidence/API bytes.
7. Human adds new required while old remains; read back both.
8. Canary adds only marker; prove new RED, old GREEN, blocked; close canary; restore compatibility GREEN.
9. Human removes old required; read back new-only.
10. Create one descendant commit removing only provider-tests; record distinct final SHA/tree externally. Do not add identity to report.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_gate.py tests/unit/infra/test_provider_workflow.py
uv run python scripts/provider_gate.py verify-node-ownership --map tests/provider_test_ownership.json
make lint
uv run pytest -q
python3 ./spec-dock/scripts/spec-dock validate
git diff --name-only "$PRC_COMPAT_HEAD" "$PRC_FINAL_HEAD"
test "$(git diff --name-only "$PRC_COMPAT_HEAD" "$PRC_FINAL_HEAD")" = '.github/workflows/provider-ci.yml'
test "$PRC_COMPAT_HEAD" != "$PRC_FINAL_HEAD"
```

Compatibility job command uses its own purpose workspaces:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact   --repository chemitaro/spec-dock   --candidate-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/candidate"   --evidence-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/evidence"   --run-json "$ISS392_WS_WORKFLOW_API/run.json"   --jobs-json "$ISS392_WS_WORKFLOW_API/jobs.json"   --artifacts-json "$ISS392_WS_WORKFLOW_API/artifacts.json"   --source-sha "$PRC_COMPAT_HEAD" --source-tree "$PRC_COMPAT_TREE"   --workflow-run-id "$COMPAT_RUN_ID" --json
```

**Expected/evidence**

Old consumers/providers absent; second dogfood complete; report non-self-referential; compatibility candidate/evidence/API actual bytes verified; canary new RED/old GREEN; new required; distinct final head with only job removal.

**Stop/cleanup/invariant**

Any schema choice, old consumer, partial dogfood, report identity, compatibility no-op/build/canary dependency, setting gap, equal heads or extra final diff stops. Cleanup local pre-freeze purpose workspaces by handles. S70 is non-main; continue S80.

**Trace**

I392-RQ-022–029/032; D-013–025.

## I392-S80 — Read-only final-head evidence and PR-C gate

**Objective and visible outcome**

On clean distinct final head, run authoritative CI/evidence/qualification and pre-merge attestation without tracked edit/build/update/sync.

**Owned repository paths**

None. External workflow-api, artifact-download, protected-witness and attestation-draft workspaces/handles only; GitHub read APIs and human append-only pre-merge comment.

**No-touch**

All tracked files, dogfood, report/meta, repository workbench, stage namespace except read-only clean check, settings except readback.

**Prerequisites**

S70 final head clean; compatibility sequence complete; new required context active; compatibility job absent; human review available.

**RED evidence**

Run selector zero/multiple/wrong head; candidate/evidence/API missing or mismatched; final head equals compatibility; final diff extra; verifier typed failures; fixture/hash/environment/metric mismatch; tracked write/build/update/sync; comment/receipt mismatch.

**Smallest action**

1. Create independent workflow-api, artifact-download, protected-witness and attestation-draft workspaces/handles.
2. Verify final SHA/tree externally and allowed compatibility diff.
3. Snapshot runs to workflow-api workspace; dispatch Provider CI for final head and qualification; select exactly one new run; wait success.
4. Save exact run/jobs/artifacts API bytes to workflow-api workspace.
5. Download exact final candidate/evidence to artifact-download workspace.
6. Invoke exact verifier on actual bytes; inspect role metrics/build counts.
7. Read back final required contexts/reviews.
8. Render pre-merge payload/comment in attestation-draft workspace; human posts new #392 comment; read back; create comment receipt.
9. Recheck head/tree/status, dogfood identity, protected witness and repository workbench.

**Focused commands**

```bash
test "$(git rev-parse HEAD)" = "$PRC_FINAL_HEAD"
test "$PRC_COMPAT_HEAD" != "$PRC_FINAL_HEAD"
test -z "$(git status --short)"
gh workflow run provider-ci.yml --ref "$BRANCH"   -f candidate_sha="$PRC_FINAL_HEAD" -f qualification=true
uv run python scripts/provider_gate.py verify-downloaded-artifact   --repository chemitaro/spec-dock   --candidate-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/candidate"   --evidence-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/evidence"   --run-json "$ISS392_WS_WORKFLOW_API/run.json"   --jobs-json "$ISS392_WS_WORKFLOW_API/jobs.json"   --artifacts-json "$ISS392_WS_WORKFLOW_API/artifacts.json"   --source-sha "$PRC_FINAL_HEAD" --source-tree "$PRC_FINAL_TREE"   --workflow-run-id "$FINAL_RUN_ID" --json
uv run python scripts/provider_gate.py emit-attestation   --kind pre-merge-attestation-v1   --input-json "$ISS392_WS_ATTESTATION_DRAFT/input.json"   --output-json "$ISS392_WS_ATTESTATION_DRAFT/payload.json"   --output-comment "$ISS392_WS_ATTESTATION_DRAFT/comment.md" --json
test "$(git rev-parse HEAD)" = "$PRC_FINAL_HEAD"
test -z "$(git status --short)"
```

**Expected/evidence**

One final-head build invocation; all consumers zero; exact candidate/nine-file evidence/API bytes; stable 20-run qualification; final new-only context; append-only pre-merge #392 comment and external receipt; no tracked/workbench/dogfood change.

**Stop/cleanup/invariant**

Any tracked edit/local build/update/sync, wrong run/head/context, byte/schema/metric mismatch or comment failure invalidates S80. Return S70 and repeat final sequence. Handle-clean only after immutable evidence retained. S80 is only PR-C main gate.

**Trace**

I392-RQ-023–032; D-013–025.

## 4. Human merge and measured external closure

1. Human merges `PRC_FINAL_HEAD`.
2. Fetch `MERGE_COMMIT`; require `git rev-parse "$PRC_FINAL_HEAD^{tree}" == git rev-parse "$MERGE_COMMIT^{tree}"`.
3. Run `python3 ./spec-dock/scripts/spec-dock issue finish`; verify actual local/state output.
4. Run `python3 ./spec-dock/scripts/spec-dock close --id iss-00392`; read actual GitHub #392 closed state/timeline event.
5. Create a new attestation-draft purpose workspace; render `post-merge-closure-v1` from measured facts; human posts to #392; read back and create external `comment-receipt-v1`.
6. Re-evaluate all Epic acceptance.
7. Run `python3 ./spec-dock/scripts/spec-dock close --id epic-00384`; read actual #384 close event.
8. Create another independently-created attestation-draft workspace; render `epic-closure-v1`; human posts to #384; read back and create receipt.
9. Tracked report/tree are never rewritten.

No step creates payload fields for facts not yet observed. Post payload has no own comment ID; Epic payload may use already observed post comment ID/hash but has no own comment ID.

## 5. Definition of done

All I392-RQ-001–032 are verified. Only S30/S60/S80 are main gates. #387 report is mapping-only, terminal cleanup releases old tuples, each temporary purpose has a distinct handle, compatibility/final evidence uses distinct heads and actual bytes, closure follows measured order, and `owner_decisions_required=[]`.

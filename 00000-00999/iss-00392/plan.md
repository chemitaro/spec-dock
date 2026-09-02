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
  sha: "0fafbf3e02d2fcd5b622d6a997323e0f98eb1c78"
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

For each purpose the orchestrator creates a private owner root and live handle, immediately reserves the Design D-007 exact top-level tree, and exports only the reserved tree path. Owner root is never exported. Exact variables include local purposes plus provider-build/role/attestation/verification/node/workflow purposes. Every command below receives the exported reserved tree; no command receives owner root or invents a top-level child.

Before spawning a child, the owner registers every fixed output or one exact closed subtree policy through `register_output()`. The child receives the reserved path and inherited descriptor but cannot create registration or cleanup authority. The owner seals the registered inventory after child exit, keeps FDs alive through reads/uploads, confirms actual artifact ID/name/digest, then cleans by handle. Unknown owner-root entry, unregistered or policy-invalid descendant, owner death, premature cleanup or path-only authority preserves data and stops.

### Full Regression command rule

```bash
uv run python -m scripts.quality.verify_full_regression   --shards 4   --artifact-dir "$ISS392_WS_FULL_REGRESSION_S00"
```

S30 and S60 substitute `ISS392_WS_FULL_REGRESSION_S30` or `ISS392_WS_FULL_REGRESSION_S60`. Each variable is the reserved `full-regression` tree, not the private owner root. Default verifier output is forbidden.




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
8. Verify exact dogfood `0.2.3\n`, marker absence and fixed-tree digests.
9. Build baseline `0.2.3` once in baseline-build workspace and capture hashes.
10. Run current ordinary/full gates with external output.

**Focused verification commands**

```text
spawn_registered_child(
  admission_handle,
  ISS392_WS_ADMISSION,
  registrations=[fixed-file-v1:inputs/issue-387-timeline.json],
  argv=[
    "gh","api","--paginate",
    "-H","Accept: application/vnd.github+json",
    "repos/chemitaro/spec-dock/issues/387/timeline"
  ],
  stdout_registration="inputs/issue-387-timeline.json"
)
```

```bash
# Each path below is an exported reserved tree backed by its live handle.
uv build --sdist --wheel --out-dir "$ISS392_WS_BASELINE_BUILD"
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression \
  --shards 4 \
  --artifact-dir "$ISS392_WS_FULL_REGRESSION_S00"
python3 ./spec-dock/scripts/spec-dock validate
```

The admission parser uses the same registered-capture API for every referenced PR, `/commits/{head_sha}/pulls`, head commit, merge commit, report blob, ledger blob and collection result. No shell redirection or child-selected output path is permitted.

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

Add dormant strict model/candidate/legacy parser and all finite wire values including the seven-echo `terminal-cleanup-completed` and `terminal-cleanup-failed` result families.

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

38-code/142-row inventory; four record and thirty-three public JSON goldens; hidden cleanup-token parser role; no-token desired update/init-force disambiguation; terminal-cleanup code/retry/action/guidance; warning retries; strict result-family private enum; unknown/duplicate/order rejection; candidate/legacy safety.

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
- every no-token public command is atomically stored as the first desired `deferred_invocation`, even when update/init-force has the same base form as the old operation retry;
- only the exact generated `--provider-cleanup-token <active token>` command has cleanup-retry role; a missing/wrong token is exact `invalid-request`;
- each no-token init, init-force, update and four uninstall forms echoes exactly on cleanup success/failure;
- failure exposes the tokenized cleanup retry in `continuation.next_command` and exact desired command in `continuation.after_cleanup_command`;
- tokenized retry preserves deferred intent; successful retry returns that desired command, never the durable old mutation command;
- a tokenized retry with no deferred request produces explicit no-next-action cleanup success;
- present-ACTIVE cleanup success is cleanup-only and never dispatches the requested operation;
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

PR-B branch exposes final route, dogfood record remains exact `0.2.3\n` and fixed trees/marker absence byte-identical. Record CLI goldens and witness equality.

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
uv build --sdist --wheel --out-dir "$ISS392_WS_BASELINE_BUILD"
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
5. Modify retained workflow to start one background handle owner, reserve/seal one full-regression-s60 output tree, pass/upload that exact tree while owner FDs remain alive, mark the actual upload identity confirmed, and only then handle-clean. Upload failure preserves and fails.
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

## I392-S70 — Consumer-first final gate, exact CLI/permissions, both tracked heads and second dogfood update

**Objective and visible outcome**

Build the final Provider Gate with exact raw-archive dataflow and least-privilege permissions; remove old policy consumer-first; complete the second dogfood update; finalize tracked report; create compatibility and final heads. S70 is non-main.

**Owned paths**

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_gate.py
tests/unit/infra/test_provider_workflow.py
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

Protected data/seeds; actual compatibility/final identities are external; human setting writes/merge are not agent operations.

**Prerequisites**

PR-B S60 main state and both current gates GREEN. Every D-007 reserved-tree owner implementation and raw archive transport test is available.

**RED evidence**

- exact argv array and required flags for all nine subcommands;
- wrong/missing/duplicate/reordered repeated role options;
- private owner root passed instead of reserved tree;
- raw archive absent/truncated/digest mismatch/unsafe ZIP/extracted-byte mismatch;
- API prefixed digest versus upload-output bare digest mismatch;
- top-level empty permissions and every job override/needs/build/upload/download step;
- compatibility job downloads raw candidate/evidence plus API snapshots and calls aggregate verifier;
- one packager, consumers zero, canary isolation;
- old consumer inventory zero before provider deletion;
- distinct heads and exact one-job diff;
- complete second dogfood candidate.

**Smallest action**

1. Implement the nine exact Design D-019 commands and failure/success schemas.
2. Implement owner-root-private/reserved-tree APIs and all provider-purpose workspace owners.
3. Implement authenticated raw ZIP download steps, raw preservation, API/upload digest equality and safe extraction.
4. Add final workflow with `permissions: {}` and exact job overrides/needs.
5. Add structural tests comparing complete YAML job graph, permissions, artifact names and argv arrays.
6. Retire/replace every old consumer, prove zero, then delete old providers/ledger/timing/sharder/conftest/main-push workflow.
7. Update final operator/test-policy docs and perform complete candidate-wide dogfood update.
8. Finalize tracked #392 report without head/run identities and commit `PRC_COMPAT_HEAD`.
9. Run compatibility workflow and human no-gap context sequence; compatibility verifier independently GREEN.
10. Commit distinct `PRC_FINAL_HEAD` by removing only job `provider-tests`. Record both identities externally. Do not merge.

**Focused verification commands**

```bash
REPOSITORY_ROOT="$(pwd -P)"
uv run pytest -q tests/unit/infra/test_provider_gate.py tests/unit/infra/test_provider_workflow.py
uv run python scripts/provider_gate.py verify-node-ownership \
  --repository-root "$REPOSITORY_ROOT" \
  --ownership-map "$REPOSITORY_ROOT/tests/provider_test_ownership.json" \
  --collection-json "$ISS392_WS_PROVIDER_NODE_OWNERSHIP/collection.json" \
  --workspace "$ISS392_WS_PROVIDER_NODE_OWNERSHIP" \
  --json
uv run python scripts/provider_gate.py verify-workflow-structure \
  --repository-root "$REPOSITORY_ROOT" \
  --workflow "$REPOSITORY_ROOT/.github/workflows/provider-ci.yml" \
  --head-kind compatibility \
  --workspace "$ISS392_WS_PROVIDER_WORKFLOW_STRUCTURE" \
  --json
make lint
uv run pytest -q
python3 ./spec-dock/scripts/spec-dock validate
test "$(git diff --name-only "$PRC_COMPAT_HEAD" "$PRC_FINAL_HEAD")" = '.github/workflows/provider-ci.yml'
test "$PRC_COMPAT_HEAD" != "$PRC_FINAL_HEAD"
```

Compatibility job creates one private owner for `provider-verification`, exports its exact reserved tree, stores API JSON and raw archives there, creates registered empty extraction destinations, waits for provider-gate terminal state, selects the exact compatibility verification phase, and runs:

```bash
REPOSITORY_ROOT="$(pwd -P)"
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --scope aggregate \
  --verification-phase "$COMPATIBILITY_VERIFICATION_PHASE" \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$PRC_COMPAT_HEAD" \
  --source-tree "$PRC_COMPAT_TREE" \
  --workflow-run-id "$COMPAT_RUN_ID" \
  --workflow-run-attempt "$COMPAT_RUN_ATTEMPT" \
  --run-json "$ISS392_WS_PROVIDER_VERIFICATION/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_VERIFICATION/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_VERIFICATION/api/artifacts.json" \
  --artifact-archive "candidate=$ISS392_WS_PROVIDER_VERIFICATION/raw/provider-candidate-$PRC_COMPAT_HEAD.zip" \
  --artifact-archive "provider-evidence=$ISS392_WS_PROVIDER_VERIFICATION/raw/provider-evidence-$PRC_COMPAT_HEAD.zip" \
  --artifact-dir "candidate=$ISS392_WS_PROVIDER_VERIFICATION/extracted/provider-candidate-$PRC_COMPAT_HEAD" \
  --artifact-dir "provider-evidence=$ISS392_WS_PROVIDER_VERIFICATION/extracted/provider-evidence-$PRC_COMPAT_HEAD" \
  --workspace "$ISS392_WS_PROVIDER_VERIFICATION" \
  --json
```

**Expected/evidence**

All nine CLI contracts and raw vectors GREEN; permissions/needs exact; old consumers/providers absent; second dogfood complete; compatibility normal run uses `compatibility-aggregate-green`; canary provider-tests uses `compatibility-aggregate-canary` and stays GREEN while provider-gate is RED. After the canary run becomes terminal, create a new independent `provider-verification` owner/tree and rerun the same aggregate argv with `COMPATIBILITY_VERIFICATION_PHASE=compatibility-canary-post-run`; it must prove run failure, provider-gate failure, provider-tests success and exact evidence bytes. Distinct final head differs only by compatibility job removal.

**Stop/cleanup/invariant**

Any unspecified CLI flag, raw/archive/API/permission mismatch, owner-root exposure, old consumer, partial dogfood, report identity, compatibility build/canary dependency, setting gap, equal heads or extra final diff stops. Handle cleanup occurs only after actual upload/read confirmation. S70 remains non-main; continue to read-only S80.

**Trace**

I392-RQ-022–029/032; D-007, D-013–026.

## I392-S80 — Read-only final-head raw-byte evidence and PR-C gate

**Objective and visible outcome**

On the clean S70-created final head, rerun authoritative CI, independently download raw archive/API bytes, verify them, and post pre-merge evidence without tracked edits.

**Owned repository paths**

None. Independent live handles/reserved trees only; GitHub read APIs; human append-only pre-merge comment.

**Prerequisites**

Final head clean/distinct; compatibility sequence complete; new required active; compatibility job absent; final workflow structure test GREEN.

**RED evidence**

Zero/multiple/wrong run; wrong raw archive digest; missing preserved raw ZIP; pre-extraction or cross-workspace input; nonempty destination; wrong verification phase; invalid run/job/conclusion or evidence-name nullability; API/upload digest mismatch; actual extracted bytes mismatch; wrong permissions/needs; candidate/evidence schema/metrics mismatch; tracked write/build/update/sync; comment/receipt mismatch.

**Smallest action**

1. Pin existing `PRC_FINAL_HEAD`/tree and create provider-verification, protected-witness and attestation-draft private owners/reserved trees.
2. Dispatch exactly one final workflow run and wait for terminal `completed/success`.
3. Under the single provider-verification tree, save exact run/jobs/artifacts API JSON, authenticate-download exact candidate/evidence raw ZIPs, and create registered empty extraction destinations.
4. Run the aggregate verifier with phase `post-run-final`; it performs safe extraction and verifies raw/extracted/API bytes in exact order. No preceding extraction step is allowed.
5. Verify the registered verifier stdout and sealed single-tree inventory.
6. Verify environment/20-run/fault/macOS/sdist evidence and final permissions/needs from actual bytes/API.
7. Read back final required contexts/reviews.
8. Emit pre-merge payload/comment in attestation reserved tree; human posts new #392 comment; read back and create receipt.
9. Recheck head/tree/status, dogfood, protected witness and repository workbench.

**Focused commands**

```bash
test "$(git rev-parse HEAD)" = "$PRC_FINAL_HEAD"
test "$PRC_COMPAT_HEAD" != "$PRC_FINAL_HEAD"
test -z "$(git status --short)"
gh workflow run provider-ci.yml --ref "$BRANCH" -f candidate_sha="$PRC_FINAL_HEAD" -f qualification=true
REPOSITORY_ROOT="$(pwd -P)"
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --scope aggregate \
  --verification-phase post-run-final \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$PRC_FINAL_HEAD" \
  --source-tree "$PRC_FINAL_TREE" \
  --workflow-run-id "$FINAL_RUN_ID" \
  --workflow-run-attempt "$FINAL_RUN_ATTEMPT" \
  --run-json "$ISS392_WS_PROVIDER_VERIFICATION/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_VERIFICATION/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_VERIFICATION/api/artifacts.json" \
  --artifact-archive "candidate=$ISS392_WS_PROVIDER_VERIFICATION/raw/provider-candidate-$PRC_FINAL_HEAD.zip" \
  --artifact-archive "provider-evidence=$ISS392_WS_PROVIDER_VERIFICATION/raw/provider-evidence-$PRC_FINAL_HEAD.zip" \
  --artifact-dir "candidate=$ISS392_WS_PROVIDER_VERIFICATION/extracted/provider-candidate-$PRC_FINAL_HEAD" \
  --artifact-dir "provider-evidence=$ISS392_WS_PROVIDER_VERIFICATION/extracted/provider-evidence-$PRC_FINAL_HEAD" \
  --workspace "$ISS392_WS_PROVIDER_VERIFICATION" \
  --json
uv run python scripts/provider_gate.py emit-attestation \
  --repository-root "$REPOSITORY_ROOT" \
  --kind pre-merge-attestation-v1 \
  --input-json "$ISS392_WS_ATTESTATION_DRAFT/input.json" \
  --output-json "$ISS392_WS_ATTESTATION_DRAFT/payload.json" \
  --output-comment "$ISS392_WS_ATTESTATION_DRAFT/comment.md" \
  --workspace "$ISS392_WS_ATTESTATION_DRAFT" \
  --json
test "$(git rev-parse HEAD)" = "$PRC_FINAL_HEAD"
test -z "$(git status --short)"
```

**Expected/evidence**

One final producer build; consumers zero; raw candidate/evidence archives and extracted/API bytes all linked; stable qualification; final new-only context; append-only pre-merge comment/receipt; no tracked/workbench/dogfood change.

**Stop/cleanup/invariant**

Any tracked edit/local build/update/sync, wrong run/head/context, raw/extracted/API/schema/permission/metric mismatch or comment failure invalidates S80. Return to S70 and repeat final sequence. Clean by live handles only after immutable evidence readback. S80 is the sole PR-C main gate.

**Trace**

I392-RQ-023–032; D-013–026.

## 4. Human merge and measured external closure

1. Human merges `PRC_FINAL_HEAD`; fetch `MERGE_COMMIT` and require tree equality.
2. Create one fresh attestation-draft reserved tree and record finish attempt 1 start/end. Run `python3 ./spec-dock/scripts/spec-dock issue finish`.
3. If exit 0, require returned issue 392, active cleared true, post-sync completed; attempt 1 is accepted.
4. If exit 1, recovery is allowed only when result/readback proves #392 closed, active cleared true and post-sync failed. Immediately read #392 timeline and bind the unique original close event. No payload yet.
5. For attempt 2, run `python3 ./spec-dock/scripts/spec-dock active set --id iss-00392`; require exit 0 and exact active-set stdout/stderr hashes from Design D-022. Then run `python3 ./spec-dock/scripts/spec-dock active show`; require exit 0, exact stdout/stderr hashes and active issue `iss-00392`. Active-set performs no post-sync and no such field is recorded. Then rerun issue finish, requiring `already_closed=true` and no additional close event.
6. If attempt 2 again has only post-sync failure, repeat the exact active-set/readback/finish sequence once for attempt 3. Three failed finish attempts, active restore failure, ambiguous/multiple close event, reopen, or any other failure is a hard stop.
7. Build `post-merge-closure-v1` from all measured attempts/restores, the original close event and the final successful attempt number. Human posts to #392; read back and create comment receipt. Never invoke `close --id iss-00392`.
8. Re-evaluate Epic acceptance. Run `python3 ./spec-dock/scripts/spec-dock close --id epic-00384`; read the actual #384 close event. Build/post/read Epic closure on #384 and create receipt.
9. Tracked report/tree are never rewritten.

The accepted post payload always references the final successful finish interval while preserving the original #392 close event. Retry attempts have `already_closed=true` and cannot create another close event.

## 5. Definition of done

All I392-RQ-001–032 are verified. Only S30/S60/S80 are main gates. #387 report is mapping-only, terminal cleanup preserves desired continuation across tokenized cleanup retry, every exported workspace value is an exact reserved tree backed by a live upload-surviving handle, all nine Provider Gate argv/raw archive/permissions contracts are closed, both tracked heads are created in S70, S80 is read-only, issue-finish post-sync recovery is deterministic, and `owner_decisions_required=[]`.

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
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Execution rules

1. This Plan is the implementation entry point. Requirement defines observable behavior; Design defines exact components/schemas; the wire and register are normative data.
2. #392 starts only after #387 human merge and S00 admission. #392 is the sole implementation Issue.
3. Product source is `src/spec_dock/`; dogfood is updated only at complete S60/S70 checkpoints.
4. Behavior change is test-first. Every step records RED and GREEN evidence.
5. S30, S60 and S80 are the only main merge gates. S40, S50 and S70 are internal.
6. S80 owns no tracked path. The compatibility-to-final workflow edit occurs in S70 after the human context subgate.
7. Agent never merges or changes required settings. Human operations are exact gates.
8. All local temporary data is external. Persistent lifecycle stage is the separate same-filesystem namespace. Repository `.workbench` is never written or cleaned.
9. Tracked #392 report contains only pre-freeze facts. Final/pre/post closure evidence is external.
10. Stop conditions are fail-closed and forward-fixed in #392; no new Issue, toggle, old fallback, skip, approved failure or sharding escape.

## 2. Common path boundaries

### Protected/no-touch

- all `spec-dock/.workbench/**`;
- all initiatives/artifacts except exact #392 `report.md` and `.meta.json` under the exclusion ledger;
- seeds, unknown/user paths, unrelated skills;
- Issue #387 canonical Requirement/Design/Plan;
- Issue #372 canonical evidence;
- release/tag/PyPI;
- human merge/review/required settings unless the human-gate step explicitly calls for a write.

### External roots

Ephemeral `ISS392_EXTERNAL_ROOT` is mode0700 OS-temp outside repository and contains purpose subdirectories. Persistent stage root is repository-parent `.spec-dock-provider-stages-v1` and is never used for evidence. Neither root is tracked.

### Full Regression command rule

Every retained verifier command includes both flags:

```bash
uv run python -m scripts.quality.verify_full_regression \
  --shards 4 \
  --artifact-dir "$ISS392_EXTERNAL_ROOT/full-regression-STEP"
```

No S00/S30/S60 command accepts the default repository workbench path.

## 3. Step graph

```text
#387 human merge
  -> S00 admission
  -> PR-A: S10 -> S20 -> S30 main gate
  -> PR-B: S40 internal -> S50 internal -> S60 main gate
  -> PR-C/S70:
       candidate implementation -> complete dogfood -> tracked report
       -> PRC_COMPAT_HEAD -> human context transition
       -> PRC_FINAL_HEAD (remove compatibility job only)
  -> S80 read-only final evidence -> PR-C main gate
  -> human merge -> external Issue/Epic closure
```

## I392-S00 — Specification, #387, protected witness and legacy admission

**Objective and contract-visible outcome**

Prove specification lineage, discover and verify the unique merged #387 PR under `ISS387-THREE-WAY-V2`, derive admitted rows, capture protected/exclusion witnesses and establish exact legacy dogfood/current gates without production change.

**Exact owned repository paths and symbols**

- read-only repository/GitHub;
- exact `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md` pre-merge admission section;
- optional `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/.meta.json` `updated_at` only through SpecDock lifecycle;
- no production/test/workflow change.

**Explicit non-owned and no-touch paths**

All other tracked paths; all repository workbench; #387 canonical R/D/P; settings.

**Prerequisites and dependency**

Replacement imported and `SPEC_FREEZE_COMMIT` recorded; #387 human-merged; clean implementation base contains both; credentials permit read-only GitHub PR/timeline/run data.

**RED evidence or justified no-new-test rule**

Temporary external admission checker must reject: wrong spec blob; zero/multiple candidate-associated/timeline PR intersection; candidate not ancestor; report PR number; extra tail path; meta field beyond updated_at; final-head/merge tree mismatch; register mapping/signature/lineage drift; repository temp containment; unapproved protected exclusion.

**Smallest implementation action**

1. Create external purpose `admission`, `protected-witness`, `baseline-build`, `full-regression-s00` workspaces and exact sentinels.
2. Verify manifest hashes and `SPEC_FREEZE_COMMIT` ancestry.
3. Parse #387 report block, candidate SHA/tree and 12 entries.
4. Fetch candidate-associated PRs and Issue #387 timeline; intersect/filter to exactly one merged PR.
5. Verify candidate ancestry, exact report/meta evidence tail, final-head/merge tree equality and admitted-main reachability.
6. Read merge-tree report/ledger/collection and materialize external `post-387-admission.json` schema3 by the register.
7. Capture complete protected manifest and separate report/meta exclusion ledger.
8. Prove dogfood record exact `0.2.3\n`, slot markers absent and fixed roots/slots legacy digests exact.
9. Build baseline wheel/sdist once externally; run current gates with explicit external artifact directory.

**Focused verification commands**

```bash
test -z "$(git status --short)"
git merge-base --is-ancestor "$SPEC_FREEZE_COMMIT" "$IMPLEMENTATION_BASE_SHA"
gh api -H 'Accept: application/vnd.github+json' \
  "repos/chemitaro/spec-dock/commits/$ISS387_CANDIDATE_SHA/pulls" \
  > "$ISS392_EXTERNAL_ROOT/api/candidate-pulls.json"
gh api -H 'Accept: application/vnd.github+json' \
  "repos/chemitaro/spec-dock/issues/387/timeline" \
  > "$ISS392_EXTERNAL_ROOT/api/issue-387-timeline.json"
git merge-base --is-ancestor "$ISS387_CANDIDATE_SHA" "$ISS387_FINAL_PR_HEAD"
test "$(git rev-parse "$ISS387_FINAL_PR_HEAD^{tree}")" = \
  "$(git rev-parse "$ISS387_MERGE_SHA^{tree}")"
git diff --name-status "$ISS387_CANDIDATE_SHA" "$ISS387_FINAL_PR_HEAD"
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression \
  --shards 4 \
  --artifact-dir "$ISS392_EXTERNAL_ROOT/full-regression-s00"
python3 ./spec-dock/scripts/spec-dock validate
git diff --check
test -z "$(git status --short)"
```

**Expected observable result**

One qualifying PR; exact candidate/evidence tail/merge tree; register admission valid; all protected paths exact except authorized report/meta ledger; baseline `0.2.3`; current gates GREEN; repository workbench unchanged.

**Evidence to record in Issue report.md**

Specification blob identities; candidate/final PR/merge identities; tail diff; admission JSON hash; protected/exclusion manifest hashes; dogfood legacy hashes; baseline artifact hashes; exact external verifier result summary. No final #392 head or future merge facts.

**Stop conditions and escalation owner**

Any prerequisite/identity/tail/register/protection/gate mismatch stops before S10. Escalation: canonical spec/repository owner. Luna does not widen a path, tail or outcome.

**Cleanup**

Delete external baseline/API workspaces only through captured handles after report summary. Retain evidence hashes; never touch repository workbench or persistent lifecycle namespace.

**Merge-point invariant**

No product change; not a merge point.

**Requirement and design trace IDs**

I392-RQ-001–007; I392-D-007–010.

## I392-S10 — Fixed model, record, candidate and complete wire

**Objective and contract-visible outcome**

Implement dormant strict model/candidate/legacy parser and the entire finite public wire, including all uninstall states/modes/resume relations and valid goldens.

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/__init__.py
src/spec_dock/provider_lifecycle/model.py
src/spec_dock/provider_lifecycle/candidate.py
src/spec_dock/provider_lifecycle/legacy_023.py
src/spec_dock/provider_lifecycle/public_result.py
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_candidate.py
tests/unit/infra/test_provider_lifecycle_wire_contract.py
tests/unit/infra/test_provider_assets.py
```

**Explicit non-owned and no-touch paths**

Public CLI, old engine, workflows, checked-in dogfood, persistent stage namespace.

**Prerequisites and dependency**

S00 GREEN and post-#387 admission fixed.

**RED evidence**

Tests fail for malformed outer record JSON, wrong count, missing tooling-absent dry-run, missing incomplete-uninstall dry-run/resume, every unlisted phase/digest/policy/code relation, action/path order, unknown field/reason and invalid legacy fixture.

**Smallest implementation action**

Add enums/dataclasses/strict parsers/candidate digest/single legacy fixture/public table constructor only. Generate test cases from wire artifact and assert 36/123/4/16 counts.

**Focused verification commands**

```bash
uv run pytest -q   tests/unit/infra/test_provider_lifecycle_model.py   tests/unit/infra/test_provider_lifecycle_candidate.py   tests/unit/infra/test_provider_lifecycle_wire_contract.py   tests/unit/infra/test_provider_assets.py
uv run ruff check src/spec_dock/provider_lifecycle tests/unit/infra/test_provider_lifecycle_wire_contract.py
uv run mypy src/spec_dock/provider_lifecycle
```

**Expected observable result**

All finite rows/goldens parse and pass; no public route/dogfood change.

**Evidence to record**

Extracted counts, code/variant coverage, golden SHA-256 values, RED/GREEN commands.

**Stop conditions and escalation owner**

Any need for unknown/catch-all token, extra durable state or per-file historical catalog stops. Owner: Product/spec owner.

**Cleanup**

Remove generated temporary tables/caches; only source/tests/fixture remain.

**Merge-point invariant**

Internal PR-A checkpoint; old public product/current gates remain.

**Trace IDs**

I392-RQ-008–016; I392-D-001–003.

## I392-S20 — Descriptor-safe filesystem, persistent stage and fresh install

**Objective and contract-visible outcome**

Implement same-filesystem process-independent stage discovery, shared-container bootstrap and fresh install direct service without public cutover.

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/filesystem.py
src/spec_dock/provider_lifecycle/external_workspace.py
src/spec_dock/provider_lifecycle/stage_namespace.py
src/spec_dock/provider_lifecycle/service.py
tests/unit/infra/test_provider_lifecycle_filesystem.py
tests/unit/infra/test_provider_lifecycle_external_workspace.py
tests/unit/infra/test_provider_lifecycle_stage_namespace.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_faults.py
```

Symbols include namespace/repository/ACTIVE/stage owner parsers; repository/tuple-key functions; no-follow allocation/discovery/cleanup; external workspace helper; native rename/bootstrap; install service/fault hook.

**Explicit non-owned and no-touch paths**

CLI, old engine/workflows, checked-in dogfood, repository workbench.

**Prerequisites and dependency**

S10 GREEN; repository parent permits owner-only sibling namespace in tests/synthetic consumers; Linux/macOS primitive probes available.

**RED evidence**

Namespace symlink/wrong UID/mode/device; ACTIVE collision/mismatch; no scan spy; process kill/restart after ACTIVE allocation/stage/owner/container mkdir; bootstrap without record; terminal-cleanup crash; unknown stage entry; external workspace containment/collision/cleanup; fresh seed-policy/order/fault; native fallback rejection.

**Smallest implementation action**

Implement exact namespace/sentinel/index state machine and external helper, then integrate descriptor filesystem and fresh install. Create ACTIVE before stage allocation. Discover by exact repository/tuple only.

**Focused verification commands**

```bash
uv run pytest -q   tests/unit/infra/test_provider_lifecycle_external_workspace.py   tests/unit/infra/test_provider_lifecycle_stage_namespace.py   tests/unit/infra/test_provider_lifecycle_filesystem.py   tests/unit/infra/test_provider_lifecycle_service.py   tests/unit/infra/test_provider_lifecycle_faults.py   -k 'fresh or stage or restart or bootstrap or workspace or binding'
make lint
```

**Expected observable result**

Same tuple resumes across subprocess exit; mismatched tuple blocks; bootstrap-before-record recovers; no scan/repository temp; fresh install reaches ready and preserves protected bytes.

**Evidence to record**

Namespace/ACTIVE/owner canonical bytes, restart matrix, mutation timeline, native primitive results, external helper identity/cleanup matrix.

**Stop conditions and escalation owner**

Need for directory scan, random orphan adoption, repository temp, cross-device copy, generic rename or broad cleanup stops. Owner: filesystem safety/Product owner.

**Cleanup**

Synthetic namespace/workspaces removed only via exact handles; verify no repository workbench change.

**Merge-point invariant**

Internal PR-A checkpoint; dormant direct service only.

**Trace IDs**

I392-RQ-004–012; I392-D-004–008.

## I392-S30 — Update/resume convergence and PR-A gate

**Objective and contract-visible outcome**

Complete update and same-tuple convergence across record/ACTIVE/stage/process restarts while public route/dogfood remain old.

**Exact owned repository paths and symbols**

S10/S20 lifecycle modules/tests; `update_tooling`, `resume_incomplete`, terminal-cleanup resume.

**Explicit non-owned and no-touch paths**

CLI, old engine/workflows, dogfood, current policy data.

**Prerequisites and dependency**

S20 GREEN.

**RED evidence**

Each root/slot/record/cleanup boundary; cross operation/candidate/policy; process restart; ACTIVE terminal-cleanup; missing repair; marker mismatch; current root race.

**Smallest implementation action**

Reuse fixed publication and stage state machine; derive remaining targets from observation; no progress list/rollback.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_*.py
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression \
  --shards 4 \
  --artifact-dir "$ISS392_EXTERNAL_ROOT/full-regression-s30"
```

**Expected observable result**

All same-tuple retries converge; all mismatches block; current ordinary/full gates GREEN with external output; exact legacy dogfood unchanged.

**Evidence to record**

Fault/restart/convergence table, active-index cleanup, external verifier path/hash/result.

**Stop conditions and escalation owner**

Any fallback/progress schema/new public generation/workbench output. Owner: Product/filesystem owner.

**Cleanup**

Synthetic stages and external output via handles.

**Merge-point invariant**

Only PR-A main gate. Human merge leaves old public product, dormant successor, exact legacy dogfood and current gates releasable.

**Trace IDs**

I392-RQ-007–012; I392-D-004–006.

## I392-S40 — Public lifecycle/docs cutover with legacy dogfood frozen

**Objective and contract-visible outcome**

Connect final `0.2.4` lifecycle/CLI/uninstall/purge trap and provider-side lifecycle documentation on PR-B branch while preserving every checked-in dogfood byte.

**Exact owned repository paths and symbols**

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/{model,service,public_result}.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
README.md lifecycle sections
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md lifecycle sections
public result and CLI tests
```

**Explicit non-owned and no-touch paths**

All `spec-dock/{docs,templates,system,scripts}`, both fixed slots, dogfood record/markers, root AGENTS, current workflows/policy, user data.

**Prerequisites and dependency**

S30 GREEN. S40 starts PR-B and cannot be offered for merge before S60.

**RED evidence**

CLI/wire aliases/trap, docs forbidden legacy journal/purge/retry text, external dogfood witness detects any checked-in change.

**Smallest implementation action**

Wire CLI exclusively to new service, bump version, remove purge callsites, update provider-side lifecycle docs/root README lifecycle only. Do not run update/sync/copy on repository root.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_wire_contract.py   tests/cli_runtime/test_provider_lifecycle.py   tests/cli_runtime/test_uninstall.py   tests/cli_runtime/test_update.py
make lint
# external S40 witness comparison proves all dogfood fixed targets unchanged
```

**Expected observable result**

Final public behavior on branch; provider docs final lifecycle; checked-in dogfood exact legacy.

**Evidence to record**

CLI/text/JSON exits, provider docs grep, before/after dogfood witness.

**Stop conditions and escalation owner**

Any dogfood edit/sync, bridge/toggle, purge mutation or wire drift blocks. Owner: Product/spec owner.

**Cleanup**

External snapshots only.

**Internal checkpoint invariant**

S40 is not mergeable; same PR continues through S50/S60.

**Trace IDs**

I392-RQ-013–017.

## I392-S50 — Exact legacy/tripwire proof on external consumers

**Objective and contract-visible outcome**

Prove exact migration/uninstall/fault resume and old-package mutation-zero without touching checked-in dogfood.

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/legacy_023.py
src/spec_dock/provider_lifecycle/service.py
tests/integration/test_provider_lifecycle_artifacts.py
tests/integration/test_provider_lifecycle_tripwire.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/**
```

**Explicit non-owned and no-touch paths**

Checked-in dogfood fixed targets/record/markers, current workflows/policy, protected data.

**Prerequisites and dependency**

S40 branch GREEN; baseline old artifacts external.

**RED evidence**

Exact/modified roots/slots/recovery, preserve-only resume, process restart, Python/native tripwire positive controls and old-command event zero.

**Smallest implementation action**

Complete legacy adapter and startup tripwire; use external purpose baseline-build/tripwire/fresh-consumer only.

**Focused verification commands**

```bash
uv run pytest --run-full-regression --full-regression-shard -q   tests/integration/test_provider_lifecycle_artifacts.py   tests/integration/test_provider_lifecycle_tripwire.py
# macOS executes tests/platform/macos/test_provider_lifecycle_macos.py
```

**Expected observable result**

Exact migration and uninstall succeed; unsupported states block; old commands have event zero/tree unchanged; positive controls caught; dogfood unchanged.

**Evidence to record**

Old/final artifact hashes, migration matrix, stage/restart evidence, native events, dogfood witness.

**Stop conditions and escalation owner**

Any old mutation/control failure/legacy guess/dogfood drift. Owner: Product/filesystem safety owner.

**Cleanup**

External venv/consumers/tripwire outputs via handles.

**Internal checkpoint invariant**

S50 is not mergeable; same PR continues through S60.

**Trace IDs**

I392-RQ-016–017.

## I392-S60 — Terminalization, retained gate externalization, complete migration and PR-B gate

**Objective and contract-visible outcome**

Remove old engine/tests, reach failure active0, keep current PR/main-push gates independently GREEN with all output external, align lifecycle docs/AGENTS and perform the one complete checked-in legacy migration.

**Exact owned repository paths and symbols**

```text
src/spec_dock/managed_distribution.py                         delete
src/spec_dock/assets/managed_distribution.json                delete
old distribution tests                                        delete/replace
src/spec_dock/context_pack.py
.github/workflows/provider-ci.yml                              transitional retarget
.github/workflows/provider-full-regression.yml                 external artifact-dir only
full-regression-ledger.json
full-regression-timing-weights.json
tests/conftest.py
tests/unit/test_provider_test_lanes.py
admitted failure-owner source/tests
README.md lifecycle sections
src/spec_dock/assets/spec_dock/docs/{migration.md,README.md}
spec-dock/docs/{migration.md,README.md}
AGENTS.md lifecycle/uninstall sections only
spec-dock/{docs,templates,system,scripts}
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
two .spec-dock-provider-slot.json files
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md and optional meta updated_at under exclusion ledger
```

Retain unchanged in policy purpose through S60: quality baseline/verifier modules, current pytest lane behavior, current main-push trigger and AGENTS test-policy paragraphs.

**Explicit non-owned and no-touch paths**

All other initiatives/artifacts/workbench/seeds/user paths; final provider-gate tooling; required settings.

**Prerequisites and dependency**

S50 GREEN, external protected/exclusion witness valid, exact legacy checked-in dogfood.

**RED evidence**

Register active rows, stale deleted workflow paths, lane consumer allowing active/approved rows, retained workflow defaulting to repository workbench, AGENTS/docs stale lifecycle text, partial dogfood, seed/protected drift.

**Smallest implementation action**

1. Apply register's admitted fixed/superseded rules; every surviving node normally passes.
2. Retarget only deleted distribution test references in current Provider CI to S10–S50 successor tests.
3. Update ledger/timing/conftest/lane tests mechanically; active/approved zero.
4. Modify retained Full Regression workflow only to call external helper with parent `${{ runner.temp }}`, purpose full-regression-s60, pass `--artifact-dir` and upload that exact path.
5. Extract surviving context behavior, remove old engine/manifest/tests.
6. Finish provider lifecycle docs and root AGENTS lifecycle/uninstall paragraphs; retain test-policy text.
7. Run new lifecycle service once against repository root; commit complete four roots/two slots/seven-key ready record/two markers.
8. Verify provider/dogfood digest, persistent-stage clean terminal state, protected witness/exclusion ledger, seeds, validate and fresh consumer.

**Focused verification commands**

```bash
uv run pytest -q \
  tests/unit/test_provider_test_lanes.py \
  tests/unit/infra/test_provider_assets.py \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression \
  --shards 4 \
  --artifact-dir "$ISS392_EXTERNAL_ROOT/full-regression-s60"
# workflow structural test requires --artifact-dir and runner.temp output/upload
uvx --no-cache --from . spec-dock update .
python3 ./spec-dock/scripts/spec-dock validate
make lint
git diff --check
```

**Expected observable result**

Old engine absent; register active/approved zero; current Provider CI and current main-push workflow independently GREEN; no repository workbench output; lifecycle docs/AGENTS correct; dogfood complete ready `0.2.4` and candidate-aligned; protected/excluded path contracts valid.

**Evidence to record**

Terminalization table, workflow before/after scope, external output identity, PR/main-push run IDs, docs/AGENTS grep, complete dogfood record/marker/root/slot digest, stage cleanup, protected/exclusion/seed hashes, validate/fresh consumer.

**Stop conditions and escalation owner**

Unmapped failure, broken current workflow, default workbench output, final-gate redesign, partial dogfood, protected/exclusion drift or S70 tooling dependency blocks PR-B. Owner: Product/test/CI/filesystem owner.

**Cleanup**

External verifier/fresh-consumer data through handles; persistent stage only through exact terminal cleanup. Repository workbench untouched.

**Merge-point invariant**

Only PR-B main gate. Human merge yields complete final lifecycle with coherent current gates and complete dogfood; no bridge/fallback.

**Trace IDs**

I392-RQ-018–019; I392-D-011–012.

## I392-S70 — Consumer-first final gate, two-head transition and second dogfood update

**Objective and contract-visible outcome**

Implement final gate/evidence schemas/environment, retire old consumers/providers, complete second dogfood update, create compatibility head, execute the human context subgate and create final head by removing only compatibility job. S70 remains non-main.

**Exact owned repository paths and symbols**

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
AGENTS.md test-policy/provider-gate sections
README.md and provider/dogfood docs test-policy sections
all old policy consumers, then providers/data/workflow deletion
spec-dock/{docs,templates,system,scripts}
both fixed slots, record and markers
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md pre-freeze completion and optional meta updated_at
```

`PRC_FINAL_HEAD` may change only `.github/workflows/provider-ci.yml` relative to `PRC_COMPAT_HEAD`.

**Explicit non-owned and no-touch paths**

All other protected paths/workbench/seeds/user data; candidate/dogfood/report after compatibility head; human settings except explicit subgate.

**Prerequisites and dependency**

PR-B merged/known S60 tree; current gates GREEN; external witnesses valid; human admin available; new final context name observed exactly.

**RED evidence**

Structural tests reject extra packager, wrong needs/artifacts/receipt/evidence/schema/order/hash, any `EVIDENCE-FIXTURE-V1` byte/size/SHA drift, missing actual-byte check, old consumer before provider deletion, compatibility job no-op/dependent on provider-gate, canary affecting old context, final diff beyond job removal, evidence/attestation/emit CLI mismatch, partial S70 dogfood.

**Smallest implementation action**

Phase A — final candidate and compatibility head:

1. Add provider gate, exact schemas/verifiers/emitter, stable environment and structural tests.
2. Retire/replace all old policy consumers, prove zero, then delete providers/ledger/timing/sharder/conftest/old workflow.
3. Update final AGENTS/test-policy docs.
4. Perform second complete candidate-wide dogfood update and verify protected/exclusion/seed state.
5. Finalize tracked #392 report; commit/push `PRC_COMPAT_HEAD` with final workflow plus compatibility job `provider-tests`.
6. Run both old/new contexts GREEN and actual-byte checks at compatibility head.

Phase B — human context gate and final head:

7. Human adds new required while old remains; read back both.
8. Dedicated canary PR adds only `.github/provider-gate-canary-red`; prove new RED/old GREEN/merge blocked; close canary.
9. Restore compatibility-head implementation PR GREEN.
10. Human removes only old required context; read back new-only.
11. Create one descendant commit removing only exact compatibility job `provider-tests` from provider-ci.yml. Record as `PRC_FINAL_HEAD`; no report/candidate/dogfood/test edit.
12. Run structural tests proving exact compatibility-to-final diff and final context emission.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_gate.py tests/unit/infra/test_provider_workflow.py
uv run python scripts/provider_gate.py verify-node-ownership --map tests/provider_test_ownership.json
make lint
uv run pytest -q
python3 ./spec-dock/scripts/spec-dock validate
# after compatibility context transition
git diff --name-only "$PRC_COMPAT_HEAD" "$PRC_FINAL_HEAD"
test "$(git diff --name-only "$PRC_COMPAT_HEAD" "$PRC_FINAL_HEAD")" = '.github/workflows/provider-ci.yml'
```

**Expected observable result**

Final tooling/schemas/tests GREEN; old consumers/providers absent; second dogfood complete; compatibility head both contexts GREEN; canary new RED old GREEN blocked; old required removed only after proof; final head differs only by compatibility job removal and emits new context.

**Evidence to record in tracked report**

Pre-final-head implementation facts, consumer inventory/removal, schema/golden results, compatibility-head identity, dogfood/protected summaries and the planned external evidence schema/location. Do not record final-head source-bound artifacts or post-merge facts.

**Stop conditions and escalation owner**

Any consumer/provider ordering failure, schema choice, extra packager, compatibility context weakness, canary cross-impact, setting gap, final diff beyond allowed path/job, dogfood/protection drift or tracked report cycle stops. Owner: CI/Product/spec owner; settings: human admin.

**Cleanup**

Remove local pre-freeze builds/workspaces through handles. Keep tracked final candidate/docs/tests. No S70 merge handoff.

**Internal checkpoint invariant**

S70 is non-main. It ends with clean `PRC_FINAL_HEAD`, new required context active, compatibility job removed, complete dogfood and no tracked correction pending. S80 alone performs authoritative final evidence.

**Trace IDs**

I392-RQ-020–025/027; I392-D-013–023.

## I392-S80 — Read-only final frozen-head evidence and PR-C gate

**Objective and contract-visible outcome**

On clean `PRC_FINAL_HEAD`, rerun all authoritative CI/evidence/qualification, final context readback and append-only pre-merge attestation without any tracked edit/build/update/sync.

**Exact owned repository paths and symbols**

Tracked paths: none. External purpose `workflow-api`, `artifact-download`, `attestation-draft` only; GitHub read APIs and human append-only Issue comment.

**Explicit non-owned and no-touch paths**

All tracked files, dogfood, report/meta, workbench, stage namespace except read-only clean check, settings except readback, release.

**Prerequisites and dependency**

S70 final head clean; candidate/dogfood/report complete; new required context configured; compatibility job absent; human review available.

**RED evidence**

Run selector rejects zero/multiple/wrong-head run; downloaded verifier typed failures 2–12; schema/hash/actual-byte mismatch; qualification mismatch; final context missing; tracked diff/build/update/sync; attestation emission/comment identity mismatch.

**Smallest implementation action**

1. Freeze/record final head/tree externally and verify compatibility-to-final diff.
2. Snapshot existing workflow runs, dispatch Provider CI for final head/qualification, select exactly one new matching run and wait success.
3. Fetch run/jobs/artifacts API JSON externally.
4. Download exact candidate and provider-evidence artifacts externally.
5. Run exact `verify-downloaded-artifact`; inspect actual role evidence metrics/build counts and require all serializer/golden tests to match `EVIDENCE-FIXTURE-V1`.
6. Read back final required contexts/reviews and verify only new provider context replaced old.
7. Render pre-merge attestation with exact emitter; human posts new #392 comment; read back/hash/no-edit verify.
8. Recheck head/tree/status, dogfood record/markers/digest, protected witness and repository workbench read-only identity.

**Focused verification commands**

```bash
test "$(git rev-parse HEAD)" = "$PRC_FINAL_HEAD"
test -z "$(git status --short)"
gh workflow run provider-ci.yml --ref "$BRANCH" \
  -f candidate_sha="$PRC_FINAL_HEAD" \
  -f qualification=true
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --repository chemitaro/spec-dock \
  --candidate-dir "$ISS392_EXTERNAL_ROOT/download/candidate" \
  --evidence-dir "$ISS392_EXTERNAL_ROOT/download/evidence" \
  --run-json "$ISS392_EXTERNAL_ROOT/api/run.json" \
  --jobs-json "$ISS392_EXTERNAL_ROOT/api/jobs.json" \
  --artifacts-json "$ISS392_EXTERNAL_ROOT/api/artifacts.json" \
  --source-sha "$PRC_FINAL_HEAD" \
  --source-tree "$PRC_FINAL_TREE" \
  --workflow-run-id "$RUN_ID" \
  --json
uv run python scripts/provider_gate.py emit-attestation \
  --kind pre-merge-attestation-v1 \
  --input-json "$ISS392_EXTERNAL_ROOT/attestation/input.json" \
  --output-json "$ISS392_EXTERNAL_ROOT/attestation/pre-merge-attestation.json" \
  --output-comment "$ISS392_EXTERNAL_ROOT/attestation/pre-merge-comment.md" \
  --json
test "$(git rev-parse HEAD)" = "$PRC_FINAL_HEAD"
test -z "$(git status --short)"
```

**Expected observable result**

Unique final-head run; one producer, consumers zero; exact candidate/nine-file evidence bytes; stable 20-run qualification; final new-only required context; valid append-only pre-merge comment; no tracked/workbench/dogfood change.

**Evidence to record**

External only: final head/tree, run/jobs/artifacts JSON hashes, downloaded verifier output, role/evidence hashes, metrics, context snapshots, comment ID/body hash/readback, clean status/protection digest.

**Stop conditions and escalation owner**

Any tracked edit, local build/update/sync, wrong run/head/context, byte/schema/metric mismatch, comment edit or protection drift invalidates S80. Return to S70 for tracked correction and repeat context/final evidence as required. Owner: CI/Product/human admin.

**Cleanup**

External directories only through captured handles after immutable evidence identities are recorded. No repository cleanup target.

**Merge-point invariant**

Only PR-C main gate. Human may merge exact `PRC_FINAL_HEAD` after review; main receives final provider gate and evidence, no compatibility job/old machinery, complete S70 dogfood.

**Trace IDs**

I392-RQ-021–027; I392-D-013–023.

## 4. Human merge and external closure

Human merges `PRC_FINAL_HEAD`. Verify:

```bash
test "$(git rev-parse "$PRC_FINAL_HEAD^{tree}")" = \
  "$(git rev-parse "$MERGE_COMMIT^{tree}")"
```

Render/post/readback `post-merge-closure-v1` on #392, then execute/record SpecDock issue finish and GitHub #392 close. After Epic acceptance, render/post/readback `epic-closure-v1` on #384. Tracked report is not edited. A comment edit/delete/hash mismatch or tree mismatch prevents Issue/Epic finish.

## 5. Definition of done

S30/S60/S80 alone are main gates; all finite wire/register/stage/workspace/protection/gate/evidence/context contracts are satisfied; dogfood is complete at S60/S70; final evidence belongs to `PRC_FINAL_HEAD`; human merge remains external; `owner_decisions_required=[]`.

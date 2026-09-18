---
kind: "implementation-handoff"
issue: "iss-00396"
title: "Issue #396 GPT-5.6 Luna Max Implementation Handoff"
artifact_path: "luna-max-implementation-handoff.md"
generated_at: "2026-09-17"
updated_at: "2026-09-18"
repository: "chemitaro/spec-dock"
branch: "iss-00396-build-once-provider-gate-and-regression-policy-cutover"
integration_branch: "codex/epic-00384-provider-test-strategy-planning"
elaboration_input_sha: "4d68bce3f3ee977548a3c467476da39c15f43594"
elaboration_input_tree: "80ade10f57cd5f4140daa03ca8a40b844f1fcc53"
implementation_allowed: false
owner_decisions_required: []
external_prerequisite: "#395 owner corrects and accepts the owner-reported implementation defect and provides the corrected merged SHA/tree before B1/B2 admission."
human_merge_only: true
authority: "advisory-execution-handoff"
qualification_authority: "E384-QUAL-001"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "artifacts/20260917t124918z-01--b1-b2-gate-receipt.md"
---

# Issue #396 GPT-5.6 Luna Max Implementation Handoff

## 1. このhandoffの効力

本書はGPT-5.6 Luna / Max実装担当が追加仕様決定なしでIssue #396を実装するためのexecution contractである。ただし現在はdispatch不可である。

```text
implementation_allowed = false
owner_decisions_required = []
human_merge_only = true
b1_accepted = false
b2_accepted = false
same_red_rereview = not-run
issue_projection_readback = false
b3 = not-started
```

These values are the candidate-assembly snapshot; later same-Red review, Issue projection, #395 correction, and B1/B2 receipts are separate exact-identity-bound evidence.

ユーザーの最新運用事実により、#395 implementation自体がincorrectと報告され、B1/B2も未実施・未受入である。具体的defectと修正後tipは未確認である。元の#395 merge SHA/treeはhistorical identityのみで、correct Product baselineやB1/B2 targetではない。#395 ownerはdefectを#395 scopeで修正・受入し、修正後のmerged SHA/treeをGitHub readbackする必要がある。これがない場合はP01で停止し、Issue #396のProduct変更を開始しない。Issue #396は#395の実装修正を代行しない。

その後も、corrected #395 merge SHAがIssue specification freezeのancestorであること、clean pushed spec candidate、same-Red `review_status=pass`かつP0/P1=0、Issue projection readback、explicit implementation dispatch、concurrent writer absenceが必要である。P2/P3はreview contractに従いrecord-onlyとし、修正・task化・acceptance gateにしない。

本handoffはProduct code、test、workflow、policy、GitHub settings、merge、B3を変更・完了したことを示さない。一packetで一checkpointだけを実行し、exit evidenceまたはtruthful StopReturnを返す。

## 2. Fixed identity and immutable inputs

| Role | Value/status |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Issue branch | `iss-00396-build-once-provider-gate-and-regression-policy-cutover` |
| Verified authoring input | `4d68bce3f3ee977548a3c467476da39c15f43594` / `80ade10f57cd5f4140daa03ca8a40b844f1fcc53` |
| #395 human merge PR | `#401` |
| Original #395 merge identity | `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / `37eabc1aa250838dcd9f61d627309b0ff27e0db7` — historical only |
| Required B1/B2 execution source | Blocked until #395 owner correction/acceptance; then exact corrected SHA/tree from GitHub readback |
| #395 implementation disposition | Owner-reported incorrect; details and corrective outcome unverified |
| B1/B2 current status | not performed / not accepted |
| Historical B2 raw hashes | `bd4630014ee046967713c89c7b8112a2ebe7f10aa85100256aca8a677d817786`, `838f1415f2a4399a3f18cf7914dc0b2f3648cb06a5d623de4ca7a22648a87a0d`; history only |
| Role baseline | 2,214 immutable assignments |
| Planned ownership delta | exact 43 add / 1 move / 69 delete |
| Final ownership | 2,188 assignments |
| Fault definition | 20 categories / 45 atomic entries, hash `7a73bcc44bcca28e734b704e2980d439e4edd161c996515ea45004d038f4bb8f` |
| Violation inventory | 68 finite codes |
| Qualification authority | `E384-QUAL-001` only |
| Lifecycle/Product | #392/#395 read-only |
| External settings/merge | human-only |

Canonical artifact order:

1. `b1-b2-admission-status-v2.json` and `b1-b2-verification-contract-v1.json`。
2. `provider-gate-contracts-v1.schema.json`。
3. role baseline/delta/checkpoint/final manifests。
4. seeded fault catalogue and closed codes。
5. old-policy retirement contract。
6. R/D/P and this handoff。
7. HTML as explanatory projection only。

Do not modify parent Epic、#392/#395 docs、historical receipt/raw bytes、baseline/raw collection bytes、retained workflow files。

## 3. Required execution packet

Validate against `provider-gate-contracts-v1.schema.json#/$defs/ExecutionPacketV1` plus semantic invariants。

Before `implementation_authorized=true`, packet must include:

- #395 owner correction/acceptance evidence and GitHub readback of the corrected merged SHA/tree。
- Read-only proof that the corrected #395 merge SHA is an ancestor of `spec_freeze_sha` (`git merge-base --is-ancestor "$B12_TARGET_SHA" "$SPEC_FREEZE_SHA"`). If false or unavailable, return to the Epic integration/parent owner. Do not merge, rebase, cherry-pick, recreate the branch, or force-push; after an owner-authorized realignment, regenerate affected source-bound artifacts, then repeat same-Red review and Issue projection readback at the new freeze SHA/tree.
- accepted `B1B2AdmissionStatusV2` with B1/B2 on that same corrected exact tip。
- clean pushed `spec_freeze_sha/tree` matching local/upstream/remote。
- same-Red review pass/P0=0/P1=0 and review evidence。
- Issue projection readback evidence。
- explicit implementation dispatch receipt。
- `concurrent_writer_absent=true`。
- one exact `authorized_checkpoint` and matching `CheckpointInputV1`。
- stage-correct EvidenceIndex: P00–P04 preflight; P05 output onward candidate-bound。

The packet does not grant GitHub settings writes or merge。`commit_push_authorized` and `pr_authorized` remain separate explicit booleans。Unknown/missing/duplicate fields、range checkpoint、absolute evidence path、candidate identity before materialization are invalid。

`CheckpointInputV1` does not duplicate a write-path ACL. For a Product checkpoint, effective write scope is the intersection of the Requirement/Design/Plan pinned by `spec_freeze_sha/tree`, that exact checkpoint step and the Plan §3 path inventory, and this handoff §6 allowed-path envelope. These references can narrow scope but cannot override the no-touch/forbidden boundary. Commit/push and PR permissions remain separate packet booleans.

## 4. Before every checkpoint

```bash
set -euo pipefail
umask 077
REPOSITORY='chemitaro/spec-dock'
ISSUE_BRANCH='iss-00396-build-once-provider-gate-and-regression-policy-cutover'
ORIGINAL_PREDECESSOR_MERGE_SHA='fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d'
ORIGINAL_PREDECESSOR_MERGE_TREE='37eabc1aa250838dcd9f61d627309b0ff27e0db7'
# Set only after #395 owner correction/acceptance and GitHub readback.
B12_TARGET_SHA=''
B12_TARGET_TREE=''
ISSUE_DIR='spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover'

HEAD_SHA="$(git rev-parse HEAD^{commit})"
HEAD_TREE="$(git rev-parse HEAD^{tree})"
UPSTREAM_SHA="$(git rev-parse '@{upstream}^{commit}')"
REMOTE_SHA="$(git ls-remote --heads origin "$ISSUE_BRANCH" | awk '{print $1}')"

test "$HEAD_SHA" = "$SPEC_FREEZE_SHA"
test "$HEAD_TREE" = "$SPEC_FREEZE_TREE"
test "$UPSTREAM_SHA" = "$SPEC_FREEZE_SHA"
test "$REMOTE_SHA" = "$SPEC_FREEZE_SHA"
test -z "$(git status --porcelain=v1)"
```

Before the first mutation additionally verify:

```text
B1 accepted at owner-approved corrected #395 SHA/tree
B2 accepted after B1 at the same SHA/tree
corrected #395 merge SHA is an ancestor of SPEC_FREEZE_SHA
same-Red review pass P0/P1=0
Issue projection readback complete
explicit implementation dispatch present
```

Re-hash canonical schema/delta/fault/retirement artifacts and validate the checkpoint resolved ownership manifest before collecting or executing a test body。After any source mutation, the next remote/review/workflow packet binds the new clean pushed SHA/tree; do not continue under old identity。

## 5. Authority rules for the implementation

### 5.1 Never edit or duplicate parent qualification policy

- Parent clause IDs and semantics are inputs。
- Numeric values and population/window semantics are generated from parent Requirement into `_qualification_policy_generated.py`。
- Do not put independent thresholds in workflow YAML、JSON contract、test constants、docs。
- Tests may use clearly named synthetic values for boundary fixtures, but production evaluator reads generated projection only。
- If generator cannot unambiguously extract the parent contract, stop rather than hand-copying values。

### 5.2 Read-only Product boundaries

No semantic edit to:

```text
src/spec_dock/provider_lifecycle/**
tests/unit/provider_lifecycle/**
provider-lifecycle-wire-contract.md
active-failure-disposition-register.md
#392/#395 canonical Product contracts
```

`src/spec_dock/provider_lifecycle/candidate.py::capture_packaged_candidate` and related digest functions may be imported read-only. Do not modify candidate algorithm、fixed domains、wire、bootstrap、lifecycle behavior。

### 5.3 Retained workflow distinction

Never delete or modify as part of old provider Full Regression retirement:

```text
.github/workflows/ci.yml
src/spec_dock/assets/install_root/.github/workflows/ci.yml
```

They are the retained installed-consumer workflow and must remain byte-identical。The deletable root provider workflow is:

```text
.github/workflows/provider-full-regression.yml
```

Path confusion is immediate stop。

## 6. Allowed path envelope

### 6.1 Hand-edit after explicit dispatch

```text
.github/workflows/provider-ci.yml
AGENTS.md
docs/provider-gate.md
pyproject.toml
tests/conftest.py  # temporary compatibility seam only
scripts/maintenance/generate_provider_qualification_policy.py
scripts/quality/provider_gate/**
tests/unit/provider_gate/**
tests/integration/test_provider_gate_role_graph.py
tests/integration/test_provider_gate_faults.py
tests/integration/test_epic_00343_distribution.py
tests/cli_runtime/test_distribution_cutover.py
```

### 6.2 Delete only after replacement GREEN + consumer-zero + new-only readback

```text
.github/workflows/provider-full-regression.yml
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
tests/unit/test_full_regression_baseline.py
tests/unit/test_provider_test_lanes.py
tests/conftest.py  # only if no nonlegacy fixture remains
```

Permanent `scripts/quality/provider_gate/pytest_plugin.py` is never deleted at cutover。

### 6.3 Generated only

```text
scripts/quality/provider_gate/_qualification_policy_generated.py
scripts/quality/provider_gate/contracts/*  # byte-identical from canonical Issue artifacts
```

### 6.4 Forbidden / immediate parent return

Any edit to parent Epic、accepted ADR/wire/register、#392/#395 Product/docs、provider lifecycle、retained workflow pair、SpecDock metadata/active pointers、Initiative priority、GitHub settings/merge。Settings/merge are human-only even after dispatch。

## 7. Implementation order — do not reorder

0. P01 fresh B1 acceptance then same-tip B2 acceptance。No mutation before both receipts。
1. Validate execution packet/spec review/projection/dispatch/no writer。
2. Read-only external settings/environment/protected/current-consumer capture。
3. Copy reviewed schema/delta/fault/retirement contracts; obtain exact First RED only。
4. Implement preflight/candidate evidence and one-time materialization synthetic tests。
5. Implement environment/process collectors。
6. Implement permanent pytest plugin + temporary root compatibility seam and deterministic ownership。
7. Implement history/evaluator/exact 45-fault detection。
8. Implement finite consumer scanner/context relation evaluator。
9. Refactor package consumer and exact one-node move。
10. Add shadow replacement workflow; materialize PR candidate once。
11. Human additive required-context transition, intentional RED, GREEN recovery。
12. Migrate all consumers; prove scanner count 0 and retained workflow equality。
13. Human remove old required context while old emitter exists; read back `U + new`/merge-group scope。
14. Delete old providers/data/workflow/tests/temp seam; permanent plugin remains。
15. Final-source local/workflow/review gates; human merge-ready PR。
16. Human merge to Epic branch; read back merge SHA/tree/context。
17. Post-merge one-time materialization (not attempt), campaign freeze, independent attempts, exact fault campaign, aggregate evaluation/B3 receipt。

Never reorder old deletion before consumer-zero/context readback, campaign attempt before complete materialization/freeze, or test body before reviewed ownership assignment。

## 8. Module responsibilities

### 8.1 Contracts and codec

Read canonical Draft 2020-12 schema。Reject duplicate/unknown/missing fields、bool-as-int、wrong order/enum/relation。Violation code is finite inventory。Do not put parent numeric thresholds into a second runtime file。

### 8.2 Identity and materialization

`identity.py` resolves event-specific source identity。`materialization.py` owns `unmaterialized -> materializing -> materialized|poisoned` and same-SHA registry。Materialization has no attempt ID/member role。`artifacts.py` hashes actual bytes and prohibits build in resolver/role functions。

### 8.3 Evidence

`evidence.py` creates physical workspace outside tracked tree but serializes only `evidence_root_id`, logical root-relative POSIX path, size and actual-byte hash。Preflight index has no candidate identity。Candidate index requires complete candidate/environment。

### 8.4 Environment/process

`environment.py` captures provider/class、effective limits、image/OS、CPU family/quota、memory、Python/dependency/tool/filesystem and detects drift。`process_tree.py` owns root spawn-to-exit+descendant-reap interval and child-inclusive CPU/wall raw values。

### 8.5 Permanent pytest plugin

Plugin owns options、collection filtering、NodeObservation、skip/duplicate detection before and after cutover。Root conftest is a temporary bypass seam only。P15 deletion must not remove filter ownership。

### 8.6 History/evaluator

Attempt registry is immutable。Started failure/cancel/interruption/missing/rerun stays visible。Per-attempt result does not depend on aggregate completeness。Aggregate selection consumes generated parent projection only。

### 8.7 Faults

Load exact 45-entry source-controlled definition and test-only injectors。No implementation-time denominator/code/stage choice。Execute all entries and compare exact finite code/stage。

### 8.8 Consumer/context

`consumer_scan.py` interprets finite signatures and emits complete scan result。`context.py` compares read-only snapshots and no-gap relations; it has no write/admin API。

### 8.9 CLI

Thin subcommands call the above modules。CLI cannot build from `run-role`, cannot register an attempt before complete materialization, cannot infer owner from marker/prefix, cannot mutate GitHub settings。

## 9. Materialization and role commands

### 9.1 Materialization (attempt外)

```bash
uv run python -m scripts.quality.provider_gate.cli materialize-candidate   --source-identity "$SOURCE_IDENTITY"   --environment-contract "$ENVIRONMENT_CONTRACT"   --physical-evidence-root "$PHYSICAL_ROOT"   --output "$MATERIALIZATION_JSON"
```

Implementation invokes exactly one top-level `uv build --sdist --wheel ...`。Failure terminalizes `poisoned`; same SHA cannot rerun。

### 9.2 Freeze

```bash
uv run python -m scripts.quality.provider_gate.cli freeze-campaign   --materialization "$MATERIALIZATION_JSON"   --fault-definition "$ISSUE_DIR/artifacts/seeded-fault-catalogue-v1.json"   --output "$CAMPAIGN_FREEZE_JSON"
```

Only complete materialization accepted。

### 9.3 Register/run role

```bash
uv run python -m scripts.quality.provider_gate.cli register-attempt   --candidate-index "$CANDIDATE_INDEX" --purpose qualification   --campaign-freeze "$CAMPAIGN_FREEZE_JSON" --output "$REGISTRATION_JSON"
uv run python -m scripts.quality.provider_gate.cli run-role   --registration "$REGISTRATION_JSON" --role linux-canonical   --ownership "$RESOLVED_OWNERSHIP" --output "$ROLE_OUTPUT"
```

`run-role` invokes pytest once through permanent plugin and never builds。Other role IDs: `static-analysis`, `sdist-smoke`, `macos-delta`。Attempt evaluator is not a pytest role。

### 9.4 Context canary

Before campaign freeze, register `purpose=context-canary`, campaign ID null, window contract present。It still runs the normal role graph and remains rolling history member。Materialization is never a member。

## 10. Exact test-first ownership packet

`role-ownership-delta-v1.json` lists all planned nodes. Add/move/delete only those node IDs at their activation checkpoint。Before each body run, derive/verify the full checkpoint manifest from baseline+delta。

Required first RED groups:

- P04: projection/schema/evidence discriminator/closed catalogue inventory。
- P05: materialization state/poison/nonmembership/actual bytes/logical paths。
- P06: environment/process lifecycle boundaries。
- P07: plugin transition/final owner, unknown/duplicate/unplanned nodes。
- P08: chronology/rerun/member replacement/filter and exact `RED-F001`–`RED-F045` detection。
- P09: current inventory exact + final zero RED + retained workflow guard。
- P10: exact one-node move/package artifact mode。

Every plugin-based role/checkpoint run loads the full resolved ownership manifest; selectors never trim or rewrite it. A qualification role invocation has no pytest node selectors: the plugin checks the complete collected set/hash against that full manifest, then filters to the selected role. A focused checkpoint invocation may name exact fully qualified pytest node IDs only; the actual collection must equal that requested set, and every ID must have the selected role owner in the full manifest. Unselected manifest rows are not missing. File/directory, marker, glob, `-k`, `-m`, shard and ignore selectors are rejected in focused mode.

Focused runs are engineering/test-first verification only. They do not create accepted `RoleResultV1`/AttemptResult or B3 qualification evidence. Missing plugin/schema/manifest, unknown or duplicate IDs/owners, a mismatched collection, or mixed legacy flags must reject before body. Skip/xfail does not count as GREEN.

Negative inventory is closed by finite codes and includes manifest/source/artifact/producer/environment/topology/process/performance/correctness/raw/attempt/fault/consumer/retained-workflow cases。Do not add free-form fault injection or unreviewed node IDs。

## 11. `test_epic_00343_distribution.py` refactor contract

Preserve `CandidateWheel` existing fields and assertions where possible。Add qualification artifact loading without Product behavior change。

Suggested seam:

```python
@dataclass(frozen=True)
class CandidateArtifactSource:
    mode: Literal["qualification-artifact", "local-test-build"]
    manifest_path: Path | None
    bundle_root: Path | None
    qualification_eligible: bool
```

`candidate_wheel`:

- if env/pytest option points to manifest+bundle: load and verify; prohibit build helper call。
- otherwise local-only build path as existing behavior; set not eligible。

Workflow final gate tests assert artifact mode exactly。Do not use pytest skip when artifact missing in qualification mode; fail before test body。

## 12. Workflow implementation contract

### 12.1 Shadow phase

Retain old jobs temporarily and add `materialize-candidate` plus new role graph。Materialization is outside attempt history; roles consume stored actual bytes。No role job builds。Permissions read-only/minimum; evidence upload `if: always()` does not convert missing evidence to success。No cancellation that erases started attempts。

### 12.2 Human context canary

Observe actual emitted context name。Human adds new while old remains。Materialize exact PR source once, run intentional RED normal attempt, verify block, create new source for recovery if needed, materialize once, run GREEN。Keep snapshots in ContextTransitionReceiptV1。Agent never writes settings。

### 12.3 Consumer-first final phase

Migrate all consumers, complete scan with count 0, verify retained pair equality。Human removes old required context while old emitter still exists and reads `U + new`/merge_group。Only then delete old emitter/provider/data/tests/temp seam。Permanent plugin remains。Final source revalidates scanner/ownership/tests/lint/protection。

## 13. Final source and post-merge qualification

### 13.1 Human merge creates candidate boundary

PR evidence is not post-merge B3 when merge SHA differs。After human merge, read exact merge SHA/tree, require accepted tree equality and final context readback。Do not change settings here。

### 13.2 Post-merge order

1. One-time materialization for merge SHA/tree, outside attempts。
2. Environment admission and CandidateEvidenceIndex complete。
3. CampaignFreezeV1 complete before first qualification attempt registration。
4. Independent final-gate attempts each consume same stored bytes and one role graph。
5. Exact 45-entry candidate-bound fault campaign。
6. Parent-generated aggregate evaluation including history/window/context/consumer/protection。

Failure/cancel/mismatch poisons materialization or rejects attempt/campaign according to stage。Same SHA build/rerun/member replacement forbidden。Materialization never counts as first/window member。

### 13.3 B3 evidence

Exact merge identity、materialization/build actual bytes、environment、campaign freeze、attempt IDs/results、fault definition/executions、window result、consumer-zero、context final readback、protected/retained workflow、review receipts、qualification result hash。No future IDs in tracked specs。B3 false until inspected actual result accepts。

## 14. Exact verification suite

```bash
uv run python scripts/maintenance/generate_provider_qualification_policy.py --check
uv run python -m scripts.quality.provider_gate.cli validate-contracts
uv run pytest -q tests/unit/provider_gate --tb=short
uv run pytest -q \
  tests/integration/test_provider_gate_role_graph.py \
  tests/integration/test_provider_gate_faults.py \
  --tb=short
uv run pytest -q tests/unit/provider_lifecycle --tb=short
uv run pytest -q tests/cli_runtime/test_distribution_cutover.py --tb=short
make lint
uv run pytest -q --tb=short
./spec-dock/scripts/spec-dock validate
uv run python -m scripts.quality.provider_gate.cli scan-old-consumers \
  --repository . \
  --contract scripts/quality/provider_gate/contracts/old-policy-retirement-v1.json \
  --require-zero \
  --output "$EVIDENCE_ROOT/consumer-zero.json"
cmp --silent .github/workflows/ci.yml src/spec_dock/assets/install_root/.github/workflows/ci.yml
```

Expected output class:

- every command exit 0。
- generated diff 0。
- provider-gate focused tests skip/xfail 0。
- ordinary suite no old policy skip reason。
- lint Ruff check/format + mypy pass。
- SpecDock validate GREEN。
- consumer zero。
- retained workflow byte-identical。

Counts are observation, not contract literals。

## 15. Evidence workspace rules

Physical root is owner-only and outside tracked tree。Wire never records its absolute path。Create `EvidenceWorkspaceV1`, then write logical root-relative POSIX entries; hash actual bytes and size after close/fsync。Reject traversal、symlink escape、duplicate/conflicting entry、missing bytes。

P00–P04/B1/B2/review/external capture use PreflightEvidenceIndexV1。P05 materialization emits CandidateEvidenceIndexV1; P06–P22 use candidate-bound index except poisoned stop evidence。Source-controlled files use RepositoryArtifactRefV1。

Allowed external identifiers: GitHub run/artifact/check IDs and sanitized read-only JSON。Never include token/cookie/auth header/private path/runner credential。Summary always links to raw hash。

## 16. Stop conditions — immediate return, no fallback

- Owner-reported #395 implementation defect is unresolved, owner acceptance is absent, or corrected merge SHA/tree cannot be read back。
- Fresh B1/B2 accepted evidence missing or different SHA/tree。
- Historical receipt/Issue ready/closed status offered as substitute。
- Spec review pass/P0/P1, projection readback, dispatch or writer absence missing。
- Parent semantics or #392/#395/retained/protected surfaces would change。
- Materialization build count/bytes/environment/retention incomplete or poisoned same-SHA rebuild required。
- Evidence stage/path/hash invalid。
- Unknown/duplicate/unplanned test node or plugin final owner loss。
- Process topology/descendant measurement/reap not provable。
- Any of 45 faults unexecuted/undetected/wrong code/stage or denominator changed。
- Started attempt/rerun/cancel/missing cannot remain in history。
- Consumer scan incomplete/count nonzero or retained workflow mismatch。
- Required-context/ruleset/merge queue readback unknown, RED fails to block, U drift, rollback unavailable。
- Extra Issue/direct-main/agent merge/portfolio reprioritization needed。

## 17. Stop return schema

Use only `StopReturnV1`。Populate finite reason code, checkpoint, violations, stage-correct evidence, scope impact, required owners/actions, mutation flag, changed/external surfaces, rollback and recovery status。`automatic_rollback_performed=false`。

Pre-mutation stop has empty change arrays。Post-mutation stop after workflow push/settings change/deletion/attempt start must record actual change(s) and manual owner/action。Do not claim rollback executed unless human evidence exists。Cause unknown remains evidence insufficiency, not invented root cause。

## 18. Commit, PR and merge boundary

- Commit/push only when packet says authorized。
- Conventional Commit in Japanese, configured identity must match repository policy。
- PR base only Epic integration branch。
- No direct push to integration/main。
- Agent stops at merge-ready。
- Human merge/revert/settings only。
- Post-merge B3 execution/evidence is a separate phase。

## 19. Completion return

Return statuses separately:

```text
b1: not-run|rejected|accepted
b2: not-run|rejected|accepted
specification_review: not-run|failed|pass
issue_projection_readback: false|true
implementation_dispatch: false|true
implementation: not-started|partial|complete
materialization: unmaterialized|materializing|materialized|poisoned
local_verification: not-run|red|green
shadow_gate: not-run|red|green
context_canary: not-run|red|green
consumer_zero: not-run|false|true
old_policy_retired: false|true
code_review: not-run|failed|pass
final_quality_gate: not-run|failed|pass
pr: not-created|draft|merge-ready
human_merge: false|true
post_merge_materialization: unmaterialized|materialized|poisoned
campaign: incomplete|rejected|accepted
fault_campaign: incomplete|rejected|accepted
stability_window: incomplete|rejected|accepted
b3: false|true
```

Never collapse into “done”。At this handoff's candidate-assembly snapshot, B1/B2 are not-run/not-accepted、review re-run is not-run、implementation is not-started、B3 is false。Later review and predecessor receipts are separate exact-SHA-bound evidence and do not rewrite this snapshot。

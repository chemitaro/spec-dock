---
kind: "implementation-handoff"
issue: "iss-00396"
title: "Issue #396 GPT-5.6 Luna Max Implementation Handoff"
artifact_path: "luna-max-implementation-handoff.md"
generated_at: "2026-09-17"
repository: "chemitaro/spec-dock"
branch: "iss-00396-build-once-provider-gate-and-regression-policy-cutover"
integration_branch: "codex/epic-00384-provider-test-strategy-planning"
elaboration_input_sha: "fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d"
elaboration_input_tree: "37eabc1aa250838dcd9f61d627309b0ff27e0db7"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-execution-handoff"
qualification_authority: "E384-QUAL-001"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "b1-b2-gate-receipt.md"
---

# Issue #396 GPT-5.6 Luna Max Implementation Handoff

## 1. このhandoffの効力

本書は、GPT-5.6 Luna / Max実装担当へIssue #396の候補作成を渡すexecution contractである。現在の状態は次で固定する。

```text
implementation_allowed = false
owner_decisions_required = []
human_merge_only = true
```

R/D/P作成、formal `issue start`、#392/#395 CLOSED、B1/B2 GREEN、dependency ready、`owner_decisions_required=[]`は、いずれも単独ではProduct/test/workflow/policy mutationを許可しない。実効的なmutation gateは、clean pushed exact specification candidateに対するindependent `chatgpt-spec-review-strict` pass（P0/P1=0）、GitHub #396 projection readback、ユーザーのexplicit implementation dispatch、concurrent-writer absenceが揃うまで閉じる。

このhandoffはB3実装完了、qualification pass、required-context変更、PR mergeを主張しない。実装者は一checkpointだけを処理し、そのcheckpointのevidenceとstop conditionを返す。

## 2. Fixed identity and immutable inputs

| Role | Value |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Issue branch | `iss-00396-build-once-provider-gate-and-regression-policy-cutover` |
| Integration branch | `codex/epic-00384-provider-test-strategy-planning` |
| B2 entry SHA | `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` |
| B2 entry tree | `37eabc1aa250838dcd9f61d627309b0ff27e0db7` |
| Entry register | 15 total / 0 active / 15 resolved |
| Resolution modes | 14 fixed-in-place / 1 superseded |
| Approved / unexpected | 0 / 0 |
| Qualification authority | Epic Requirement `E384-QUAL-001` only |
| Lifecycle authority | Provider Lifecycle Wire Contract, read-only |
| Merge authority | Human only |

B2 SHA/treeはentry provenanceである。Canonical R/D/P publication後のreviewed `SPEC_FREEZE_SHA/TREE`は別identityとしてexecution packetに入れる。B2へresetして実装しない。

## 3. Required execution packet

Mutationを受け付けるpacketは次のexact fieldsを持つ。

```json
{
  "schema_version": 1,
  "issue_id": "iss-00396",
  "repository": "chemitaro/spec-dock",
  "issue_branch": "iss-00396-build-once-provider-gate-and-regression-policy-cutover",
  "spec_freeze_sha": "40 lowercase hex",
  "spec_freeze_tree": "40 lowercase hex",
  "b2_entry_sha": "fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d",
  "b2_entry_tree": "37eabc1aa250838dcd9f61d627309b0ff27e0db7",
  "spec_review_status": "pass",
  "spec_review_p0": 0,
  "spec_review_p1": 0,
  "github_projection_readback": true,
  "implementation_authorized": true,
  "concurrent_writer_absent": true,
  "authorized_checkpoint": "P01-P22",
  "commit_push_authorized": false,
  "pr_authorized": false,
  "external_settings_owner": "human",
  "human_merge_only": true
}
```

Unknown/missing key、identity mismatch、authorized checkpoint外ではmutation 0で停止する。`commit_push_authorized`と`pr_authorized`はProduct mutation許可と別である。

## 4. Before every checkpoint

```bash
set -euo pipefail

REPOSITORY='chemitaro/spec-dock'
ISSUE_BRANCH='iss-00396-build-once-provider-gate-and-regression-policy-cutover'
B2_SHA='fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d'
B2_TREE='37eabc1aa250838dcd9f61d627309b0ff27e0db7'

HEAD_SHA="$(git rev-parse HEAD^{commit})"
HEAD_TREE="$(git rev-parse HEAD^{tree})"
UPSTREAM_SHA="$(git rev-parse '@{upstream}^{commit}')"
REMOTE_SHA="$(git ls-remote --heads origin "$ISSUE_BRANCH" | awk '{print $1}')"

test "$HEAD_SHA" = "$SPEC_FREEZE_SHA"
test "$HEAD_TREE" = "$SPEC_FREEZE_TREE"
test "$UPSTREAM_SHA" = "$SPEC_FREEZE_SHA"
test "$REMOTE_SHA" = "$SPEC_FREEZE_SHA"
test -z "$(git status --porcelain=v1)"
git merge-base --is-ancestor "$B2_SHA" HEAD
```

After a checkpoint changes files, the next packet must identify the new exact clean pushed candidate if the task proceeds to a remote/review/workflow gate. Do not silently continue under the old identity。

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

### 6.1 Hand-edit allowed

```text
.github/workflows/provider-ci.yml
AGENTS.md
docs/provider-gate.md
pyproject.toml
scripts/maintenance/generate_provider_qualification_policy.py
scripts/quality/provider_gate/**
tests/unit/provider_gate/**
tests/integration/test_provider_gate_role_graph.py
tests/integration/test_provider_gate_faults.py
tests/integration/test_epic_00343_distribution.py
tests/cli_runtime/test_distribution_cutover.py
```

### 6.2 Deletion allowed only after consumer-zero

```text
.github/workflows/provider-full-regression.yml
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
tests/conftest.py
tests/unit/test_full_regression_baseline.py
tests/unit/test_provider_test_lanes.py
```

### 6.3 Generated only

```text
scripts/quality/provider_gate/_qualification_policy_generated.py
```

Do not hand-edit generated output。

### 6.4 Forbidden without parent return

Any other Product/source/workflow/spec-dock metadata path。If a needed change falls outside the envelope, return stop payload before editing。

## 7. Implementation order — do not reorder

1. Read-only identity/dependency/external/environment/protected capture。
2. RED/GREEN parent policy projection and closed evidence schemas。
3. RED/GREEN candidate identity、one producer、artifact actual-byte verification。
4. RED/GREEN environment capture and child-inclusive collector。
5. RED/GREEN role ownership/pytest plugin。
6. RED/GREEN attempt/history/evaluator/fault catalogue。
7. Old consumer scanner with current-inventory GREEN and final-zero RED。
8. Refactor package tests to consume stored artifact in qualification mode。
9. Move the one nonpolicy regression out of `test_provider_test_lanes.py`。
10. Add replacement workflow in shadow coexistence。
11. Freeze actual environment on a new source SHA and rerun shadow。
12. Human additive required-context change and intentional RED/GREEN canary。
13. Move all consumers to replacement。
14. Prove old consumer 0。
15. Delete old provider/data/workflow/tests/markers in same Issue PR。
16. Final-source full local/workflow verification。
17. Independent code review and Final Quality Gate。
18. Prepare PR; human merges to Epic branch。
19. Post-merge candidate build once, first five, fault campaign, latest twenty。
20. B3 receipt; only then Epic main handoff。

Deleting old files before step 14 is prohibited。

## 8. Module responsibilities

### 8.1 `contracts.py` and `codec.py`

Use frozen dataclasses/Enums/Literals and exact key order. Reject:

- duplicate JSON keys。
- unknown/missing fields。
- booleans where integers are expected。
- nonlowercase/full-length SHA values。
- nonfinite decimal inputs。
- path traversal/absolute raw evidence paths。
- free-form status/violation codes。

Serialize canonical UTF-8, compact separators, one terminal LF。Keep evidence schemas versioned and closed。

### 8.2 `identity.py`

Provide:

```python
@dataclass(frozen=True, slots=True)
class RepositoryIdentity:
    repository: str
    source_sha: str
    source_tree: str


def resolve_repository_identity(...) -> RepositoryIdentity: ...
def build_attempt_id(repository_id: int, workflow_run_id: int) -> str: ...
def build_campaign_id(candidate: CandidateIdentity, environment_fingerprint: str, gate_version: str) -> str: ...
def build_window_contract_id(gate_version: str, environment_version: str, fingerprint: str) -> str: ...
```

IDs must be deterministic from closed inputs; caller-provided arbitrary IDs are not accepted。

### 8.3 `artifacts.py`

Only producer path calls top-level packaging process:

```text
uv build --sdist --wheel --out-dir <fresh-dir>/dist --clear .
```

Enforce one wheel、one sdist、fresh output、source SHA/tree match、actual bytes hash。Downstream roles call `verify_candidate_bundle`, never build。

Actions resolver uses API run chronology and exact artifact metadata。Missing/multiple/expired producer rejects candidate; no same-SHA rebuild fallback。

### 8.4 `environment.py`

Capture actual values, not labels alone。Reject placeholder `unknown`, missing effective limits, mutable burst/quota, unsupported architecture/class/tier, GPU evidence, fingerprint drift。The source-controlled environment contract must be filled only after actual shadow observation。

### 8.5 `process_tree.py`

Linux only collector requirements:

- monotonic interval starts immediately before root spawn。
- cgroup v2 aggregate CPU includes all descendants。
- effective `cpu.max`/`memory.max` readback。
- one pytest root, worker 1, no shard/xdist。
- subreaper or equivalent waits/reaps descendants。
- root exit does not close interval while descendants remain。
- wall predicate breach terminates/reaps and records failure, not timeout escape。
- missing cgroup/effective limit/process evidence => reject。

Do not add a hidden grace acceptance threshold。Infrastructure cancellation means missing evidence/nonaccepted。

### 8.6 `pytest_plugin.py`

The plugin is inactive unless `--provider-gate-role` is supplied。When active:

- load exact role contract。
- deselect nonowned nodes; do not skip them。
- record collected/executed/outcome/skip reason/node duplicates。
- classify policy skip separately。
- fail on duplicate execution、unknown owner、role intersection、unexpected marker override。
- write canonical node observation even on failure when process remains alive。

Do not recreate old dynamic `fast/full_regression` policy under new names。

### 8.7 `history.py`

GitHub API runs are chronology authority。Started run without artifact remains a member。Never read directory mtimes to order attempts。`run_attempt > 1` is rerun rejection。First five and latest twenty return explicit incomplete results rather than filtering members。

### 8.8 `faults.py`

Catalogue is source-controlled and candidate-bound。Synthetic fixtures exercise gate boundary adapters, not production Product behavior。Every entry must execute exactly once and match the expected violation code/stage。No denominator edits after observation。

### 8.9 `consumer_scan.py`

Use:

- Python AST imports/names/calls/constants。
- YAML parser or safe structured inspection for workflows。
- JSON parse for path/data refs。
- current operational docs text checks。

Classify historical references separately。Final result must show zero runtime/workflow/test consumers before deletions。Retained workflow guard must fail if either retained path is missing or bytes differ。

### 8.10 `evaluator.py`

Pure functions only。Separate:

1. role evaluation。
2. per-attempt evaluation。
3. first-five campaign evaluation。
4. fault campaign evaluation。
5. latest-twenty evaluation。
6. final qualification conjunction。

Per-attempt status must not depend on future five/twenty completeness。Use raw integer nanosecond/microsecond values and Decimal for ratio。No float rounding as authority。

## 9. Candidate and role commands

### 9.1 Producer

```bash
uv run python -m scripts.quality.provider_gate.cli build-candidate \
  --repository . \
  --source-sha "$GITHUB_SHA" \
  --source-tree "$(git rev-parse "$GITHUB_SHA^{tree}")" \
  --workflow-run-id "$GITHUB_RUN_ID" \
  --run-attempt "$GITHUB_RUN_ATTEMPT" \
  --output "$RUNNER_TEMP/specdock-candidate"
```

Expected files:

```text
candidate-manifest.json
candidate-bundle/
  dist/<one wheel>
  dist/<one sdist>
```

The artifact upload must include actual bytes and manifest。Never reconstruct from claimed hashes。

### 9.2 Consumer verification

```bash
uv run python -m scripts.quality.provider_gate.cli verify-candidate \
  --manifest "$CANDIDATE/candidate-manifest.json" \
  --bundle "$CANDIDATE/candidate-bundle" \
  --expected-source-sha "$GITHUB_SHA" \
  --expected-source-tree "$(git rev-parse "$GITHUB_SHA^{tree}")"
```

### 9.3 Environment capture

```bash
uv run python -m scripts.quality.provider_gate.cli capture-environment \
  --contract scripts/quality/provider_gate/contracts/specdock-linux-qualification-v1.json \
  --output "$ROLE_EVIDENCE/environment.json"
```

### 9.4 Linux canonical

```bash
uv run python -m scripts.quality.provider_gate.cli run-role \
  --role linux-canonical \
  --manifest "$CANDIDATE/candidate-manifest.json" \
  --bundle "$CANDIDATE/candidate-bundle" \
  --environment "$ROLE_EVIDENCE/environment.json" \
  --output "$ROLE_EVIDENCE"
```

Internally one pytest root command only。

### 9.5 sdist / macOS / static

Same CLI with exact role IDs:

```text
static-analysis
sdist-smoke
macos-delta
```

macOS role must not evaluate Linux wall/CPU predicates。sdist role must not start packaging build backend。

### 9.6 Attempt evaluation

```bash
uv run python -m scripts.quality.provider_gate.cli evaluate-attempt \
  --registration "$ATTEMPT_EVIDENCE/attempt-registration.json" \
  --roles "$ATTEMPT_EVIDENCE/roles" \
  --output "$ATTEMPT_EVIDENCE/attempt-result.json"
```

## 10. Test-first packet

For every module:

1. add focused test/fixture。
2. run exact focused command and capture RED。
3. implement smallest coherent behavior。
4. run focused GREEN。
5. run all `tests/unit/provider_gate`。
6. run `make lint` before checkpoint commit。

Never delete old test to make RED disappear。Old tests are retired only after successor proof and consumer-zero。

Minimum negative tests:

- missing/malformed manifest、wrong source/tree/hash/bytes。
- producer ambiguity/expiry/failure/cancel。
- environment drift/unverifiable limit/GPU/high-tier。
- second pytest root/extra worker/shard。
- root exits before child、child leak、incomplete reap。
- policy skip、approved failure、duplicate node。
- role missing/duplicated/wrong owner。
- started failure/cancel/interruption/missing evidence。
- same attempt ID、run attempt increment、artifact replacement。
- first-five replacement/campaign reset。
- latest-twenty filter/replacement/window<20。
- fault catalogue miss/unexecuted/denominator shrink。
- old consumer >0 blocks deletion。
- retained workflow missing/mismatch。

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

Keep old jobs temporarily。Add new jobs with explicit `needs` graph and same-candidate artifact。Permissions read-only/minimum。No cancellation that erases attempts。Every role uploads raw result `if: always()`; evaluator treats missing result as failure。

### 12.2 Final phase

After consumer-zero:

- remove old `provider-tests` and old matrix parity jobs/commands。
- retain static analysis as new role。
- retain final per-attempt job/check。
- delete provider-full-regression workflow。
- remove old marker/flags/data/modules/tests。

The final context name is the actual emitted check-run name captured from shadow, not a guessed string in docs。

### 12.3 Human context canary

The implementation agent produces exact before/add/RED/GREEN/remove/readback evidence template。Human performs settings changes。Do not call admin APIs to mutate contexts/rulesets。

Intentional RED must precede final candidate five-run freeze and remain in rolling history。Do not rerun RED run。After RED, produce a fix commit/new source SHA and GREEN。

## 13. Final source and post-merge qualification

### 13.1 PR head is not B3 source when merge SHA differs

PR head per-attempt evidence proves code/gate behavior。Human merge to Epic branch may create a new commit SHA even when tree equality holds。Because candidate identity includes exact source SHA/tree, post-merge SHA is a new candidate and must build once independently。

### 13.2 Post-merge attempts

For exact merged SHA:

1. first workflow run builds candidate once。
2. next four new workflow runs consume same bytes -> first five population。
3. continue new workflow runs until latest twenty all accepted after intentional RED naturally exits the window。
4. no reruns/run-attempt increments。
5. same observations may be referenced by first-five and latest-twenty aggregators; no nested execution。

### 13.3 B3 final evidence

Require:

- source SHA/tree and tree equality receipt。
- producer run/artifact ID and actual hashes。
- environment fingerprint。
- five attempt IDs/results。
- fault catalogue digest/100%。
- latest twenty IDs/results。
- context final readback。
- consumer-zero/deleted old paths。
- retained workflow/protected-data proof。
- final qualification result hash。

Do not write future IDs into tracked R/D/P before they exist。

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

Use owner-only tracked-tree-external workspace for raw data。Tracked repository contains schema/contracts/tests/docs, not future run facts or credentials。

Allowed evidence references:

- repository-relative path。
- GitHub run ID/artifact ID/check-run ID。
- SHA-256。
- sanitized API JSON。

Redact/remove:

- tokens/cookies/auth headers。
- private absolute local paths。
- runner ephemeral credentials。
- environment variables not explicitly allowlisted。

Every summary points to raw evidence hash。Do not replace raw JSON with prose-only claims。

## 16. Stop conditions — immediate return, no fallback

- exact repo/branch/SHA/tree/upstream/remote mismatch。
- B2 evidence/hash mismatch。
- spec review not pass/P0/P1 nonzero or implementation packet incomplete。
- parent policy extraction ambiguity。
- runner environment/limits/image/fingerprint unprovable。
- candidate producer/actual bytes/retention ambiguity。
- same-SHA rebuild、retry、rerun required。
- role ownership not exclusive/complete without skip/shard。
- child-inclusive CPU/reap not provable。
- first-five/latest-twenty/raw history incomplete or mutable。
- seeded-fault detection <100%。
- old consumer remains。
- retained workflow affected。
- required-context/ruleset/merge queue state unknown or canary fails to block。
- Product/lifecycle/register/protected data change required。
- extra Issue/direct-main/agent merge/parent contract edit needed。

## 17. Stop return schema

```json
{
  "schema_version": 1,
  "issue_id": "iss-00396",
  "checkpoint": "Pxx",
  "status": "stopped",
  "contract_id": "exact requirement or parent clause",
  "expected": "exact expected fact",
  "actual": "sanitized observed fact",
  "verified_facts": ["facts actually observed"],
  "hypotheses": ["clearly marked hypotheses"],
  "unverified": ["未確認 points"],
  "operations_attempted": ["actual commands/API reads"],
  "operations_not_attempted": ["未実行"],
  "evidence": ["relative paths or IDs"],
  "cause": "原因未特定 or exact cause",
  "next_required_check": "one exact check",
  "mutation_performed": false
}
```

## 18. Commit, PR and merge boundary

- Commit/push only when packet says authorized。
- Conventional Commit in Japanese, configured identity must match repository policy。
- PR base only Epic integration branch。
- No direct push to integration/main。
- Agent stops at merge-ready。
- Human merge/revert/settings only。
- Post-merge B3 execution/evidence is a separate phase。

## 19. Completion return

Implementation candidate return must state separate statuses:

```text
specification_review: pass|not-run|failed
implementation: complete|partial|not-started
local_verification: green|red|not-run
shadow_gate: green|red|not-run
context_canary: green|red|not-run
consumer_zero: true|false|not-run
old_policy_retired: true|false
code_review: pass|failed|not-run
final_quality_gate: pass|failed|not-run
pr: not-created|draft|merge-ready
human_merge: false|true
post_merge_candidate: not-started|running|rejected|accepted
five_run: incomplete|rejected|accepted
fault_campaign: incomplete|rejected|accepted
latest_twenty: incomplete|rejected|accepted
b3: false|true
```

Never collapse these states into “done”。`b3=true` requires post-merge final qualification result; PR readiness or per-attempt GREEN is insufficient。

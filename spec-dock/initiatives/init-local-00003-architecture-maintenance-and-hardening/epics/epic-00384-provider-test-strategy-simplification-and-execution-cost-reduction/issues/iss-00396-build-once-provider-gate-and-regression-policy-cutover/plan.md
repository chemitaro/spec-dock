---
種別: 実装計画書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
詳細化状態: "implementation-ready-specification; product-implementation-gated"
最終更新: "2026-09-18"
依存:
  - "requirement.md"
  - "design.md"
  - "iss-00395"
  - "../../plan.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "implementation-ready"
実装開始許可: false
owner_decisions_required: []
external_prerequisites:
  - "#395 owner must correct and accept the owner-reported implementation defect, then provide the exact merged SHA/tree before B1/B2 admission."
human_merge_only: true
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00396-build-once-provider-gate-and-regression-policy-cutover"
  sha: "4d68bce3f3ee977548a3c467476da39c15f43594"
  tree: "80ade10f57cd5f4140daa03ca8a40b844f1fcc53"
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 実装計画

## 1. Execution boundary

本Planは完成authoring candidateであり、Product/test/workflow/policy実装を許可しない。Formal Issue start/active branchは維持するが、次のgateを厳密に分離する。

| Gate | Candidate-time state | Exit |
|---|---|---|
| A0 Authoring | 本packを生成 | ZIP/HTML/schema/manifest内部整合 |
| A1 Specification acceptance | **PENDING** | clean pushed exact candidateをsame Red sessionでpass、P0/P1=0。P2/P3はreview contractに従う |
| A2 Projection readback | **PENDING** | Pass後にIssue body projectionを更新しGitHubからreadback |
| A3 Predecessor admission | **BLOCKED** | #395 owner-reported defect resolved; corrected merged SHA/tree read back; fresh B1 then same-tip B2 accepted |
| A4 Explicit dispatch | **PENDING** | 別途dispatch + clean freeze identity + concurrent writerなし |
| I0–I22 Implementation/B3 | **NOT STARTED** | A0–A4成立後、P02以後のordered checkpoints |

上表と`authoring-gate-status-v1.json`は本仕様candidate作成時点のsnapshotである。後続のStrict review、Issue projection readback、B1/B2 acceptanceはexact SHAに結び付く別の実行証跡で判定する。

User correctionにより、#395 implementation自体はincorrectと報告されている。具体的defectと修正後tipは未確認なので、original #395 SHA/treeとhistorical B1/B2 receipt/raw bytesはidentity/historyに限定し、current acceptanceに使わない。#395 ownerの修正・受入と修正後merge identityのGitHub readbackが済むまでA3はBLOCKEDであり、Issue #396は#395を修正しない。Parent Epic Plan §3.2との矛盾を理由にgateを免除しない。B1/B2を本authoring task中に実行したと主張しない。

実装者はA1–A4が全部成立した後だけP02以後へ進める。一checkpointずつ実行し、stage-correct EvidenceIndexとexit evidenceを作る。後段証拠の流用、same-SHA retry、old/new partial stateのmergeを禁止する。

## 2. Fixed identities, evidence roots and shell constants

```bash
set -euo pipefail
umask 077
REPOSITORY='chemitaro/spec-dock'
ISSUE_ID='iss-00396'
ISSUE_BRANCH='iss-00396-build-once-provider-gate-and-regression-policy-cutover'
INTEGRATION_BRANCH='codex/epic-00384-provider-test-strategy-planning'
VERIFIED_AUTHORING_SOURCE_SHA='4d68bce3f3ee977548a3c467476da39c15f43594'
VERIFIED_AUTHORING_SOURCE_TREE='80ade10f57cd5f4140daa03ca8a40b844f1fcc53'
ORIGINAL_PREDECESSOR_MERGE_SHA='fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d'
ORIGINAL_PREDECESSOR_MERGE_TREE='37eabc1aa250838dcd9f61d627309b0ff27e0db7'
# Resolve only from GitHub readback after the #395 owner closes the reported defect.
B12_TARGET_SHA=''
B12_TARGET_TREE=''
QUAL_AUTHORITY='E384-QUAL-001'
ISSUE_DIR='spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover'
PREFLIGHT_PHYSICAL_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/iss396-preflight.XXXXXXXX")"
chmod 700 "$PREFLIGHT_PHYSICAL_ROOT"
```

Physical evidence rootはruntime-onlyで、wireへserializeしない。`evidence_root_id`はrandom/operation-bound 256-bit value、entry pathはroot-relative POSIX、size/hashはactual bytesから計算する。

`SPEC_FREEZE_SHA/TREE`はsame-Red review対象の将来clean pushed tipから設定する。`VERIFIED_AUTHORING_SOURCE_*`は本authoring input provenance、`ORIGINAL_PREDECESSOR_MERGE_*`はincorrectと報告された旧#395 mergeのhistory、`B12_TARGET_*`は#395 ownerがdefect correctionを受入した後にGitHub readbackする実行対象であり、相互に代用しない。`B12_TARGET_*`が空または未承認ならP01で直ちに停止する。

`role-ownership-delta-v1.json`の`verified_authoring_source_sha/tree`は、collection deltaを作成したauthoring input `4d68bce3f3ee977548a3c467476da39c15f43594` / `80ade10f57cd5f4140daa03ca8a40b844f1fcc53`へのprovenanceであり、後続の仕様freeze SHA/TREEではない。これをcurrent specification identityとして読み替えない。

Canonical machine inputs:

```text
artifacts/b1-b2-admission-status-v2.json
artifacts/b1-b2-verification-contract-v1.json
artifacts/provider-gate-contracts-v1.schema.json
artifacts/role-ownership-v1.json
artifacts/role-ownership-delta-v1.json
artifacts/role-ownership-checkpoints-v1.json
artifacts/role-ownership-resolved-final-v1.json
artifacts/seeded-fault-catalogue-v1.json
artifacts/closed-violation-codes-v1.json
artifacts/old-policy-retirement-v1.json
artifacts/authoring-gate-status-v1.json
artifacts/strict-review-p2-record-v1.json
```

## 3. Planned change inventory

### 3.1 NEW implementation paths after dispatch

```text
scripts/maintenance/generate_provider_qualification_policy.py
scripts/quality/provider_gate/{__init__,contracts,codec,identity,materialization,artifacts,environment,process_tree,pytest_plugin,history,faults,consumer_scan,context,evaluator,evidence,cli}.py
scripts/quality/provider_gate/_qualification_policy_generated.py
scripts/quality/provider_gate/contracts/{specdock-linux-qualification-v1.json,provider-gate-contracts-v1.schema.json,role-ownership-v1.json,role-ownership-delta-v1.json,seeded-fault-catalogue-v1.json,old-policy-retirement-v1.json}
tests/unit/provider_gate/{__init__,test_policy_projection,test_contracts,test_identity,test_artifacts,test_environment,test_process_tree,test_role_ownership,test_role_transition_seam,test_history,test_fault_catalogue,test_evaluator,test_consumer_inventory,test_context}.py
tests/integration/{test_provider_gate_role_graph,test_provider_gate_faults}.py
docs/provider-gate.md
```

Exact 43 added test node IDs、one moved node、69 deleted nodesは`role-ownership-delta-v1.json`だけがauthorityである。Path listやwildcardからnodeを推測しない。

### 3.2 MODIFY after dispatch

```text
.github/workflows/provider-ci.yml
AGENTS.md
pyproject.toml
tests/conftest.py                    # temporary compatibility seam only; later retire old hook
tests/integration/test_epic_00343_distribution.py
tests/cli_runtime/test_distribution_cutover.py
```

### 3.3 DELETE only after replacement GREEN + consumer zero + context readback

```text
.github/workflows/provider-full-regression.yml
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
tests/unit/test_full_regression_baseline.py
tests/unit/test_provider_test_lanes.py
tests/conftest.py  # only when remaining content is legacy-only; otherwise delete legacy symbols
```

### 3.4 NO-TOUCH / read-only

```text
.github/workflows/ci.yml
src/spec_dock/assets/install_root/.github/workflows/ci.yml
src/spec_dock/provider_lifecycle/**
tests/unit/provider_lifecycle/**
parent Epic R/D/P, accepted ADR, wire, baseline register
Issue #392/#395 canonical docs/Product behavior
spec-dock/active/** and metadata generated projections
GitHub required-context/ruleset/merge settings (human-only)
Initiative portfolio priority
```

Parent docs/historical artifacts included in the pack remain byte-preserved. This authoring task changes only Issue #396 specifications/artifacts and external download copies。

## 4. Checkpoint P00 — Complete specification artifact and same-Red re-review

Owner: primary author / independent reviewer。Product/tests/workflow/policy/settings mutation禁止。

1. Canonical Issue R/D/P、handoff、closed schema、machine artifacts、HTML、README、payload manifestをrepository-relative hierarchyでZIPへ収録する。
2. `payload-manifest-v1.json`で`modified/new/preserved`を区別し、size/SHA-256を記録する。`manifest.sha256`は全payloadをpath順・分類group付きで列挙する。
3. Historical B1/B2 receipt/raw bytes、2,214-node baseline、Linux/macOS raw collections、parent docs/contractsはbyte-preserveする。
4. Schema self-validation、concrete artifact validation、delta derivation、45 fault denominator、ZIP CRC、manifest、HTML internal/external byte equalityを検査する。
5. Repositoryへ適用する場合、spec-only diffをcommit/pushし、GitHub connectorでexact branch/full SHAをverifyする。
6. 同じsession `iss396-spec-review-red`へfollow-up reviewし、`review_status=pass`、P0=0、P1=0をrequireする。P2/P3はreview contractに従いrecord-onlyとし、task/acceptance conditionにしない。直近pre-remediation reviewのP2=3も記録のみである。
7. Pass後にだけprimary authorがIssue body projectionを更新し、GitHubからreadbackする。

`authoring-gate-status-v1.json`はcandidate組み立て時点でのgate snapshotである。後続のcommit/push、Strict review、Issue projection readbackは同ファイルを書き換えず、対象SHAを付けた外部実行証跡として記録する。

Exact local verification:

```bash
python -m zipfile -t "$ISSUE_DIR/artifacts/issue-396-specification-pack.zip"
PACK_VERIFY_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/iss396-pack.XXXXXXXX")"
python -m zipfile -e "$ISSUE_DIR/artifacts/issue-396-specification-pack.zip" "$PACK_VERIFY_ROOT"
python - "$PACK_VERIFY_ROOT" <<'PY'
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1])
for line in (root / "manifest.sha256").read_text(encoding="ascii").splitlines():
    expected, relative = line.split("  ", 1)
    actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"manifest hash mismatch: {relative}")
print("PASS manifest.sha256")
PY
python -m json.tool "$PACK_VERIFY_ROOT/$ISSUE_DIR/artifacts/provider-gate-contracts-v1.schema.json" >/dev/null
cmp "$ISSUE_DIR/artifacts/issue-396-implementation-readiness.html" \
  "$PACK_VERIFY_ROOT/$ISSUE_DIR/artifacts/issue-396-implementation-readiness.html"
/Users/iwasawayuuta/.agents/skills/japanese-explanatory-html/scripts/validate-plantuml-html.mjs \
  "$ISSUE_DIR/artifacts/issue-396-implementation-readiness.html"
```

Expected: ZIP CRC pass、all payload hashes OK、schema JSON valid、HTML bytes equal。このlocal artifact verification単独ではStrict review passやProduct GREENを意味しない。

## 5. Checkpoint P01 — #395 defect resolution, B1/B2 admission and implementation dispatch

Owner: #395 owner + implementation agent + parent owner。**現状BLOCKED**。#395 defect correctionはそのIssue scopeで完了させる。P01の操作はread-only/test executionで、Issue #396 Product fileを編集しない。

### 5.1 Resolve the reported predecessor defect and target identity

Before any B1/B2 command, the #395 owner must correct and accept the reported implementation defect under Issue #395 and provide the resulting merged commit/tree. Capture the defect disposition and exact GitHub readback in preflight evidence. The currently recorded PR #401 merge SHA/tree is historical identity only; it is not a fallback target. If the correction is not merged or the exact readback is unavailable, return a StopReturn to the #395/parent owner and stop P01.

After that owner readback, set `B12_TARGET_SHA` and `B12_TARGET_TREE` from the exact corrected merge identity. Never fill them from the Issue #396 branch, a historical receipt, or a test result from a different SHA.

### 5.2 Exact corrected predecessor identity

```bash
B12_WORKTREE='<clean worktree at exact merge SHA>'
cd "$B12_WORKTREE"
test -n "$B12_TARGET_SHA"
test -n "$B12_TARGET_TREE"
test "$(git rev-parse HEAD^{commit})" = "$B12_TARGET_SHA"
test "$(git rev-parse HEAD^{tree})" = "$B12_TARGET_TREE"
test -z "$(git status --porcelain=v1)"
export B12_PRIVATE_TMP="$(mktemp -d "${TMPDIR:-/tmp}/iss396-b12.XXXXXXXX")"
chmod 700 "$B12_PRIVATE_TMP"
export B12_TMPDIR="$B12_PRIVATE_TMP/tmp"
mkdir -m 700 "$B12_TMPDIR"
export B12_EVIDENCE_ROOT="$B12_PRIVATE_TMP/evidence"
mkdir -m 700 "$B12_EVIDENCE_ROOT"
```

Mismatch/dirty/missing commit/treeではStopReturn。Reset、fallback branch、別SHA evidence禁止。

### 5.3 Fresh B1

`b1-b2-verification-contract-v1.json`の順で実行し、stdout/stderr/exit/identity/actual-byte hashesをPreflightEvidenceIndexV1へ保存する。

```bash
env TMPDIR="$B12_TMPDIR" uv run pytest -q --tb=short   >"$B12_EVIDENCE_ROOT/b1-ordinary.stdout"   2>"$B12_EVIDENCE_ROOT/b1-ordinary.stderr"
make lint >"$B12_EVIDENCE_ROOT/b1-lint.stdout" 2>"$B12_EVIDENCE_ROOT/b1-lint.stderr"
./spec-dock/scripts/spec-dock validate   >"$B12_EVIDENCE_ROOT/b1-validate.stdout"   2>"$B12_EVIDENCE_ROOT/b1-validate.stderr"
env TMPDIR="$B12_TMPDIR" uv run pytest -q --run-full-regression --full-regression-shard   tests/unit/provider_lifecycle   tests/cli_runtime/test_distribution_cutover.py   tests/integration/test_issue_392_acceptance.py --tb=short   >"$B12_EVIDENCE_ROOT/b1-parity.stdout"   2>"$B12_EVIDENCE_ROOT/b1-parity.stderr"
```

Pass countsは事前constantにせずactual observationとして記録する。B1 parity invocationでは全selected test bodyが実行され、policy skip、skip/xfail/xpass、collection-only omissionが0であることを確認する。全command exit 0、unexpected Product/lifecycle/protected failure 0をparent ownerがacceptedとしたreceiptが必要である。

### 5.4 Same-tip fresh B2

B1 accepted後、same shell/worktreeでidentityを再確認し実行する。

```bash
test "$(git rev-parse HEAD^{commit})" = "$B12_TARGET_SHA"
test "$(git rev-parse HEAD^{tree})" = "$B12_TARGET_TREE"
uv run python -m scripts.quality.verify_full_regression --shards 4   >"$B12_EVIDENCE_ROOT/b2-verifier.stdout"   2>"$B12_EVIDENCE_ROOT/b2-verifier.stderr"
sha256sum "$B12_EVIDENCE_ROOT"/* >"$B12_EVIDENCE_ROOT/sha256sum.txt"
```

Expected class: exit 0、raw result actual bytes、15 total/0 active/15 resolved/approved 0/unexpected 0/violations empty。Historical raw resultをcurrent outputとしてcopyしない。

### 5.5 Current Issue specification admission and dispatch

B1/B2 accepted receipts後、corrected #395 merge SHAがIssue branch freezeのancestorであることをread-only確認する。

```bash
git merge-base --is-ancestor "$B12_TARGET_SHA" "$SPEC_FREEZE_SHA"
```

コマンド、`B12_TARGET_SHA`、`SPEC_FREEZE_SHA`、exit statusをPreflightEvidenceIndexV1へ保存する。Falseまたは判定不能ならStopReturnでEpic integration/parent ownerへ戻す。Agentはbranch historyを変更しない。明示許可されたbranch realignment後は、影響するsource-bound capture/artifactを再生成し、ZIP・spec freeze・same-Red review・projection readbackを新しいexact candidateに対してやり直す。B1/B2 receiptの再利用はcorrected #395 SHA/treeが変わらず、証拠が引き続き有効な場合に限る。

Ancestry pass後、Issue worktreeへ戻り、P00のStrict review passとIssue projection readbackを含む先行gateが同じ仕様candidateについて成立していることを次で再確認する。

```bash
test "$(git rev-parse HEAD^{commit})" = "$SPEC_FREEZE_SHA"
test "$(git rev-parse HEAD^{tree})" = "$SPEC_FREEZE_TREE"
test "$(git rev-parse '@{upstream}^{commit}')" = "$SPEC_FREEZE_SHA"
test -z "$(git status --porcelain=v1)"
```

Require reported #395 defect correction/owner acceptance、corrected merge ancestor proof、corrected-tip B1/B2 acceptance、same-Red pass P0/P1=0、Issue projection readback、explicit implementation dispatch、concurrent writer absent。これらが全て揃って初めてP02へ進む。Formal active state、graph ready、#395 CLOSED、original merge SHA、historical B1/B2 raw artifactsだけでは進まない。

## 6. Checkpoint P02 — Current external state capture

Owner: implementation agent read-only + human when admin read is unavailable。Mutation禁止。

Capture:

1. current `.github/workflows/provider-ci.yml` emitted check names/jobs。
2. representative PRのcheck-runs/check-suites。
3. effective required contexts/ruleset scope。
4. merge queue/merge_group state。
5. unrelated required contexts `U`。
6. Actions artifact retention policy/available maximum。
7. runner provider/class/image/effective resource observations。

Repository/API commands use actual authorized tooling. Examples:

```bash
gh api "repos/${REPOSITORY}/actions/workflows" \
  > "$EVIDENCE_ROOT/p02-workflows.json"

gh api "repos/${REPOSITORY}/actions/runs?branch=${ISSUE_BRANCH}&per_page=100" \
  > "$EVIDENCE_ROOT/p02-runs.json"
```

Ruleset/branch protection endpointsはconnection permissionに依存する。404/403/unsupportedをpermission denialと決めつけず、observed statusを記録する。未確認ならhumanがUIまたはread-only `gh api` exportを提供する。

Exit criteria:

- `OLD_REQUIRED_CONTEXTS`、`UNRELATED_REQUIRED_CONTEXTS`、merge queue scopeをactual stringsで取得。
- `NEW_CONTEXT_NAME`はreplacement shadow runのactual check-run nameから後で確定する。ここで創作しない。
- runner environment candidateがparent capability boundaryを証明可能、またはP02 stop。
- artifact retentionがpost-merge B3 campaignまでbytesを保持可能、またはP02 stop。

P02のcaptureが揃うまでworkflow codeを書かない。

## 7. Checkpoint P03 — Protected data and current-surface baseline

### 7.1 Protected snapshot

`artifacts/capture_protected_snapshot.py`が唯一のreview済みcapture実装である。P03/P16の双方で同一script SHA-256を確認し、専用evidence pathをtracked tree外へ置く。

```bash
test "$(sha256sum "$ISSUE_DIR/artifacts/capture_protected_snapshot.py" | awk '{print $1}')" = "$SNAPSHOT_HELPER_SHA256"
python "$ISSUE_DIR/artifacts/capture_protected_snapshot.py" \
  --repository . \
  --output "$EVIDENCE_ROOT/p03-protected-before.json"
```

`SNAPSHOT_HELPER_SHA256`はIssue artifact SHA manifestおよびExecutionPacket EvidenceIndexから得る。Snapshot roots/exclusionはRequirement §4.3 / Design §13.3とschema `ProtectedTreeSnapshotV1`が同一値で定義する。Symlinkをfollowしない。Outputはfresh pathへexclusive作成する。

### 7.2 Current old consumer inventory

```bash
rg -n --hidden --glob '!.git/**' \
  'full-regression-ledger|full-regression-timing-weights|verify_full_regression|full_regression_baseline|--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|provider-full-regression' \
  . > "$EVIDENCE_ROOT/p03-old-consumers-rg.txt" || true
```

これはdiscoveryのみで、mechanical proofではない。結果から`old-policy-retirement-v1.json`の初期expected inventoryを作る。Historical parent docs、receipt、retained pathsを分類する。

### 7.3 Retained workflow proof

```bash
cmp --silent \
  .github/workflows/ci.yml \
  src/spec_dock/assets/install_root/.github/workflows/ci.yml
sha256sum \
  .github/workflows/ci.yml \
  src/spec_dock/assets/install_root/.github/workflows/ci.yml \
  > "$EVIDENCE_ROOT/p03-retained-workflow.txt"
```

Expected: byte-identical。

## 8. Checkpoint P04 — Review-frozen contracts and exact First RED

P04でschema、fault denominator、ownership delta、retirement signaturesを設計しない。Canonical artifactsをruntime contract areaへbyte-identical copyし、hashをPreflightEvidenceIndexV1へ記録する。

P04で先にexact seven P04 test nodesのtest bodiesを追加し、その後に割当済みnode IDだけを直接実行する。P07で初めてpermanent pluginを導入するため、P04/P05は通常のunit-test invocationを使い、role ownership/qualification evidenceとは扱わない。

Run only the exact P04 nodes listed in `role-ownership-delta-v1.json`:

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_policy_projection.py::test_generated_policy_projection_matches_parent_authority \
  tests/unit/provider_gate/test_policy_projection.py::test_generated_policy_projection_rejects_hidden_literals \
  tests/unit/provider_gate/test_contracts.py::test_schema_inventory_is_closed_and_canonical \
  tests/unit/provider_gate/test_contracts.py::test_preflight_and_candidate_evidence_indexes_are_disjoint \
  tests/unit/provider_gate/test_contracts.py::test_logical_evidence_paths_reject_absolute_or_parent_escape \
  tests/unit/provider_gate/test_contracts.py::test_stop_return_relations_cover_pre_and_post_mutation \
  tests/unit/provider_gate/test_contracts.py::test_violation_code_inventory_is_closed \
  --tb=short
```

P04 First RED covers parent projection and schema/contract rejection, including a valid blocked execution packet and a fully gated positive authorization fixture. Negative packet cases reject empty/unknown nested fields, a true authorization with a missing gate, B1/B2 SHA/tree mismatch, review SHA/tree mismatch, and missing or negative ancestry evidence. The semantic packet validator checks these relations; it must fail on a violated invariant, not collection skip or missing plugin. The 45 fault injection/detection cases belong to P08 and must not be reported as P04 work. Then implement generator/contracts/codec skeleton sufficient to make schema/projection/definition validation GREEN.

Exit: generated parent projection diff 0、schema Draft 2020-12 valid、closed code count 68、fault entry count 45、P04 ownership exact、skip/xfail 0。

## 9. Checkpoint P05 — Materialization and two-stage evidence RED→GREEN

Implement `identity.py`, `materialization.py`, `artifacts.py`, `evidence.py` with synthetic/temp bytes only。Real candidate build is not run in this checkpoint。

Exact RED cases are the P05 additions in role delta and include:

- state transition and build count one。
- materialization not attempt/member。
- complete candidate+environment before `materialized`。
- poisoned same-SHA rebuild rejection。
- preflight/candidate evidence discriminator。
- logical path absolute/dotdot/backslash/NUL/symlink/hash mismatch rejection。
- wheel/sdist actual-byte size/hash/source/tree mismatch。

Run only the exact P05 nodes in `role-ownership-delta-v1.json`; materialization cases are owned by the existing `test_identity.py` and `test_artifacts.py` nodes, so do not add a test file or unassigned test path:

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_identity.py::test_source_identity_resolution_is_event_specific \
  tests/unit/provider_gate/test_identity.py::test_materialization_identity_is_deterministic \
  tests/unit/provider_gate/test_identity.py::test_campaign_freeze_requires_materialized_candidate_and_environment \
  tests/unit/provider_gate/test_identity.py::test_attempt_campaign_and_window_ids_are_deterministic \
  tests/unit/provider_gate/test_artifacts.py::test_materialization_build_invocation_is_exactly_one \
  tests/unit/provider_gate/test_artifacts.py::test_candidate_manifest_and_bundle_bind_actual_wheel_and_sdist_bytes \
  tests/unit/provider_gate/test_artifacts.py::test_downstream_consumer_rejects_missing_mismatched_multiple_or_expired_artifact \
  tests/unit/provider_gate/test_artifacts.py::test_materialization_failure_poisons_same_source_candidate \
  --tb=short
```

Target CLI separation:

```text
provider_gate.cli materialize-candidate  # no attempt registration
provider_gate.cli resolve-candidate      # no build
provider_gate.cli freeze-campaign        # complete materialization only
provider_gate.cli register-attempt       # build forbidden
provider_gate.cli run-role               # build forbidden
```

Real build top-level command remains exactly one invocation selected by implementation:

```bash
uv build --sdist --wheel --out-dir "$CANDIDATE_DIR/dist" --clear .
```

Exit: synthetic GREEN、skip/xfail 0、P05 CandidateEvidenceIndex generated only after complete identities。No qualification claim。

## 10. Checkpoint P06 — Environment and process collector RED→GREEN

### 10.1 Environment RED

Add tests for:

- exact contract schema/order。
- fingerprint deterministic。
- provider/class/CPU family/quota/memory/image/Python/dependency/tool/filesystem capture。
- CPU/memory unprovable/out-of-bound rejection。
- architecture wrong、GPU/high-tier/burst drift rejection。
- fingerprint drift。

```bash
uv run pytest -q tests/unit/provider_gate/test_environment.py --tb=short \
  | tee "$EVIDENCE_ROOT/p06-environment-red.txt"
```

Implement `environment.py` and freeze **candidate** contract only after P02 actual capture. No placeholder strings such as `unknown` / `ubuntu-latest` alone are accepted as final fingerprint evidence。

### 10.2 Process RED

Add controlled Linux tests:

- root + CPU child totals。
- grandchild CPU included。
- child exits after root and interval stays open。
- parent process killed、subreaper reaps orphan。
- descendant leak causes reject。
- second pytest root / worker/shard detected。
- wall/cpu raw values and Decimal ratio。
- missing cgroup v2/effective limit fail closed。

```bash
uv run pytest -q tests/unit/provider_gate/test_process_tree.py --tb=short \
  | tee "$EVIDENCE_ROOT/p06-process-red.txt"
```

Implement `process_tree.py`。通常のdeveloper環境でcgroup controlを利用できない場合、adapter unit testsはhermeticなfake filesystem/process fixtureを使う。実platform integration testは指定Linux qualification environmentで必ず実行し、そのroleではskipしない。Localで利用不能であることをpassへ変換しない。

### 10.3 GREEN

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_environment.py \
  tests/unit/provider_gate/test_process_tree.py \
  --tb=short | tee "$EVIDENCE_ROOT/p06-green.txt"
```

Expected: unit GREEN。Actual runner admission remains pending until shadow workflow。

## 11. Checkpoint P07 — Permanent plugin and deterministic role ownership

1. Copy baseline/delta/checkpoint manifests into runtime contracts byte-identically。
2. Add only P07 nodes in reviewed delta before body execution。
3. Implement plugin-owned `pytest_addoption`, `pytest_collection_modifyitems`, node observation hooks。
4. Modify root `tests/conftest.py` only as temporary exact bypass seam。Plugin—not root conftest—calls the role filter。
5. Verify ordinary pytest keeps legacy behavior until P15。
6. Verify role invocation deselects nonowned nodes and never policy-skips them。
7. Verify P15 simulation without root conftest still filters via plugin。

```bash
uv run pytest -p scripts.quality.provider_gate.pytest_plugin   --provider-gate-role linux-canonical   --provider-gate-ownership "$ISSUE_DIR/artifacts/role-ownership-checkpoints-v1.json#P07"   -q tests/unit/provider_gate/test_role_transition_seam.py      tests/unit/provider_gate/test_role_ownership.py --tb=short
```

Negative cases: plugin missing、role missing、legacy flags combined、unknown node、duplicate owner、wrong manifest/hash、unplanned node、P15 caller loss。All reject before body。Exit: resolved count/hash exact、role intersection empty、union complete、skip/xfail 0。

## 12. Checkpoint P08 — History/evaluator/exact 45-fault implementation

Use P08 resolved ownership. Do not change catalogue/code inventory。

History tests cover registration before start、started failure/cancel/interruption/missing retention、run_attempt rerun、same ID、first-member replacement、success filtering、window replacement、campaign reset。Materialization must be absent from attempt history。

Fault test iterates exact 45 source-controlled entries and requires each fixture/injector to emit exact expected code at exact stage. Wrong/missing/unexecuted/denominator drift are explicit failures。

```bash
uv run pytest -p scripts.quality.provider_gate.pytest_plugin   --provider-gate-role linux-canonical   --provider-gate-ownership "$ISSUE_DIR/artifacts/role-ownership-checkpoints-v1.json#P08"   -q tests/unit/provider_gate/test_history.py      tests/unit/provider_gate/test_evaluator.py      tests/unit/provider_gate/test_fault_catalogue.py --tb=short
```

Per-attempt result remains independent of aggregate completeness。Linux predicates come only from generated parent projection。macOS delta receives no Linux performance predicate。Exit: all exact cases GREEN、45/45 detected in synthetic campaign、skip/xfail 0。

## 13. Checkpoint P09 — Consumer scanner and retained workflow guard

### 13.1 RED

Add `test_consumer_inventory.py` first. At this checkpoint old consumer count is intentionally >0, so tests have two modes:

- `inventory-current`: exact expected current old consumers must match contract。
- `inventory-final`: requires zero and is RED until retirement checkpoint。

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_consumer_inventory.py::test_current_inventory_matches_pre_cutover_contract \
  --tb=short | tee "$EVIDENCE_ROOT/p09-current-green.txt"

set +e
uv run pytest -q \
  tests/unit/provider_gate/test_consumer_inventory.py::test_final_source_has_zero_old_policy_consumers \
  --tb=short | tee "$EVIDENCE_ROOT/p09-final-red.txt"
status=$?
set -e
test "$status" -ne 0
```

Expected final RED lists concrete current consumers; it must not fail because scanner/module is missing。

### 13.2 Scanner implementation

Implement AST/YAML/JSON/text scanner. Historical allowlist paths may mention old names but cannot import/call/execute them. The retirement contract itself is metadata, not a runtime consumer。

Retained workflow test:

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_consumer_inventory.py::test_retained_installed_consumer_workflow_is_present_and_byte_identical \
  --tb=short
```

Expected GREEN throughout all checkpoints。

## 14. Checkpoint P10 — Packaging consumer refactor and exact one-node move

Refactor `candidate_wheel` into qualification artifact mode and explicitly noneligible local-build mode。Final workflow must set materialized manifest/bundle and may not invoke local build fallback。

Move exactly:

```text
from tests/unit/test_provider_test_lanes.py::test_distribution_cutover_reuses_plain_init_only_as_update_or_uninstall_setup
to   tests/cli_runtime/test_distribution_cutover.py::test_distribution_cutover_reuses_plain_init_only_as_update_or_uninstall_setup
```

Semantic key/owner remain as delta contract specifies。Run with P10 resolved ownership/plugin:

```bash
uv run pytest -p scripts.quality.provider_gate.pytest_plugin   --provider-gate-role linux-canonical   --provider-gate-ownership "$ISSUE_DIR/artifacts/role-ownership-checkpoints-v1.json#P10"   -q tests/cli_runtime/test_distribution_cutover.py --tb=short
uv run pytest -p scripts.quality.provider_gate.pytest_plugin   --provider-gate-role sdist-smoke   --provider-gate-ownership "$ISSUE_DIR/artifacts/role-ownership-checkpoints-v1.json#P10"   -q tests/integration/test_epic_00343_distribution.py --tb=short
```

Local build-mode result is marked `qualification_eligible=false` and never enters candidate/campaign evidence。

## 15. Checkpoint P11 — Shadow replacement workflow

Modify `.github/workflows/provider-ci.yml` additively while retaining old jobs. Target planned job IDs:

```text
provider-tests                 # old, temporary
provider-distribution-parity   # old, temporary
provider-candidate             # new
provider-static-analysis       # new
provider-linux-canonical       # new
provider-sdist-smoke           # new
provider-macos-delta           # new
provider-attempt-evaluate      # new shadow result
```

Exact external check-run/context name is observed after first shadow run, not assumed from job IDs。

Workflow design gates:

- `fetch-depth: 0` and exact checkout SHA verification。
- `run_attempt == 1` check。
- permissions minimized from P02 evidence。
- no `cancel-in-progress: true` for qualification attempts。
- candidate producer/resolver uses Actions API chronology。
- all roles consume exact artifact IDs/hashes。
- evidence uploaded `if: always()` but missing evidence remains reject。
- no old flags/sharder inside new jobs。
- no packaging build in role jobs。

Static tests parse workflow and assert job needs/commands/permissions。Unit tests are a focused non-qualification development run. The role-graph and fault integration nodes use the latest existing resolved ownership checkpoint; the ownership artifact has no P11 checkpoint, so do not create one or claim new ownership assignments:

```bash
uv run pytest -q tests/unit/provider_gate --tb=short \
  | tee "$EVIDENCE_ROOT/p11-unit-focused.txt"

uv run pytest -p scripts.quality.provider_gate.pytest_plugin \
  --provider-gate-role linux-canonical \
  --provider-gate-ownership "$ISSUE_DIR/artifacts/role-ownership-checkpoints-v1.json#P10" \
  -q \
  tests/integration/test_provider_gate_role_graph.py::test_materialization_is_not_a_final_gate_attempt \
  tests/integration/test_provider_gate_role_graph.py::test_role_graph_consumes_one_candidate_and_executes_each_owned_node_once \
  tests/integration/test_provider_gate_faults.py::test_seeded_fault_catalogue_detects_every_entry \
  tests/integration/test_provider_gate_faults.py::test_post_mutation_stop_return_preserves_recovery_evidence \
  --tb=short | tee "$EVIDENCE_ROOT/p11-role-integration.txt"

make lint | tee "$EVIDENCE_ROOT/p11-lint.txt"
```

Commit/push shadow candidate only after local GREEN and authorization。First shadow run outcomes:

- one build producer。
- same manifest all new roles。
- per-attempt evaluator returns actual result。
- old jobs remain required/observed。
- runner environment capture yields acceptable exact contract candidate。

If environment cannot prove effective limits or image identity, stop before context migration/deletion。

## 16. Checkpoint P12 — Freeze environment contract and rerun shadow on new source SHA

The first shadow workflow may reveal exact environment facts. Freezing/changing `specdock-linux-qualification-v1.json` changes source SHA, therefore it creates a **new candidate**. Do not reuse first shadow artifact/campaign。

1. Populate environment contract with observed actual values。
2. Review parent capability conformance。
3. Run unit/generator/contract tests。
4. Commit/push new source SHA。
5. That SHA’s first workflow run becomes its sole build producer。
6. Confirm all shadow roles use same bytes/fingerprint。

Commands:

```bash
uv run python -m scripts.quality.provider_gate.cli validate-contracts
uv run pytest -q tests/unit/provider_gate/test_environment.py tests/unit/provider_gate/test_artifacts.py --tb=short
make lint
```

Expected: no placeholder/unknown fields; generated policy diff 0; accepted environment fingerprint stable across new roles。

## 17. Checkpoint P13 — One-time PR materialization and required-context canary

Human/settings owner boundary applies。

1. Resolve exact PR source SHA/tree and create SourceIdentityV1。
2. Run one-time materialization outside any final-gate attempt。Failure poisons source; no rerun。
3. Observe actual new check/context name from successful shadow output。
4. Human adds new required context while old remains; readback `U + old + new`。
5. Register intentional RED as a normal role-graph attempt with `purpose=context-canary`, campaign ID null, window contract ID non-null。Materialization is not a member。
6. Inject the predeclared canary condition so only new context RED; old/U remain GREEN。Human verifies merge block (and merge_group if active)。
7. Forward-fix new source if needed; no rerun of failed run/source。Materialize new source once。
8. Run fresh GREEN canary; readback recovered GREEN。

Every snapshot conforms to RequiredContextSnapshotV1 and forms ContextTransitionReceiptV1。Settings write/restore are human-only。RED remains in rolling history; no campaign freeze yet。

## 18. Checkpoint P14 — Migrate all consumers to replacement

Remove old policy use from current consumers while keeping old providers/data and old check emitter present:

1. `.github/workflows/provider-ci.yml` new jobs become authoritative per-attempt path; old jobs still present temporarily。
2. Refactored package tests consume stored artifacts in final gate。
3. docs/operator commands point to provider-gate CLI, not old verifier。
4. no code imports old evaluator/sharder except historical/retirement contract。
5. `tests/conftest.py` keeps a temporary, role-only transition seam: for `--provider-gate-role`, require the registered provider-gate plugin, validate the closed role contract and all collected node assignments, then hand the collection to the new plugin before legacy classification/skip/ledger logic. Without that option, existing ordinary and legacy behavior remains unchanged. Reject missing plugin, invalid contract, unknown node, or mixed legacy flags before test bodies run. Add focused tests for all branches. This seam and legacy hooks are deleted together only after consumer-zero.

Run scanner:

```bash
uv run python -m scripts.quality.provider_gate.cli scan-old-consumers \
  --repository . \
  --contract scripts/quality/provider_gate/contracts/old-policy-retirement-v1.json \
  --output "$EVIDENCE_ROOT/p14-consumer-scan.json"
```

Exit criteria: `runtime_consumers=0`, `workflow_consumers=0`, `test_consumers=0` excluding listed providers scheduled for deletion and historical allowlist。If any consumer remains, do not delete provider/data。

After replacement roles are GREEN and consumer-zero is proven, keep the old workflow/check emitter intact while the human removes only the old required context. Read back the final effective context set as `U + new`, including active merge-queue `merge_group` coverage. Save before/change/readback/rollback evidence. If settings are unreadable, scope changes, or readback is not exactly `U + new`, stop and retain both old provider and emitter.

## 19. Checkpoint P15 — Consumer-zero retirement; permanent plugin survives

Preconditions:

- replacement workflow and role graph GREEN。
- all consumers migrated。
- ConsumerScanResultV1 complete and old consumer count 0。
- retained workflow present/byte-equal。
- human removed old required context while emitter still existed, and new-only/final readback is complete。
- P15 resolved ownership manifest contains exact 69 deletions and final 2,188 assignments。

Then delete only paths/signatures in `old-policy-retirement-v1.json`。Remove root legacy hook/temporary seam, but retain `scripts/quality/provider_gate/pytest_plugin.py` as sole permanent filter owner。If `tests/conftest.py` contains nonlegacy fixtures, preserve file and remove only old symbols。

Run final scanner and P15 plugin ownership before any broad suite. Unknown final node/diff rejects before body。No old compatibility shim/fallback remains。

## 20. Checkpoint P16 — Final-source local verification

Run on the final source after old retirement。

### 20.1 Generated/contracts

```bash
uv run python scripts/maintenance/generate_provider_qualification_policy.py --check
uv run python -m scripts.quality.provider_gate.cli validate-contracts
```

Expected exit 0。

### 20.2 Focused tests

```bash
uv run pytest -q tests/unit/provider_gate --tb=short \
  | tee "$EVIDENCE_ROOT/p16-provider-gate-unit.txt"
uv run pytest -q \
  tests/integration/test_provider_gate_role_graph.py \
  tests/integration/test_provider_gate_faults.py \
  --tb=short | tee "$EVIDENCE_ROOT/p16-provider-gate-integration.txt"
uv run pytest -q tests/unit/provider_lifecycle --tb=short \
  | tee "$EVIDENCE_ROOT/p16-lifecycle-read-only.txt"
uv run pytest -q tests/cli_runtime/test_distribution_cutover.py --tb=short \
  | tee "$EVIDENCE_ROOT/p16-distribution.txt"
```

Expected: exit 0、unexpected/approved/policy-skip 0。Local pytest summary counts may change with role refactor; exact counts are not authority。

### 20.3 Ordinary suite and lint

```bash
make lint | tee "$EVIDENCE_ROOT/p16-lint.txt"
uv run pytest -q --tb=short | tee "$EVIDENCE_ROOT/p16-ordinary.txt"
./spec-dock/scripts/spec-dock validate | tee "$EVIDENCE_ROOT/p16-specdock-validate.txt"
```

Expected:

- Ruff check/format pass、mypy pass。
- ordinary suite exit 0。
- no old policy skip reason in output。
- validate exit 0、nodes expected 236 unless canonical spec publication changed only generated count with documented reason。

### 20.4 Source guards

```bash
test ! -e full-regression-ledger.json
test ! -e full-regression-timing-weights.json
test ! -e scripts/quality/full_regression_baseline.py
test ! -e scripts/quality/verify_full_regression.py
test ! -e .github/workflows/provider-full-regression.yml
cmp --silent .github/workflows/ci.yml src/spec_dock/assets/install_root/.github/workflows/ci.yml
! rg -n --hidden --glob '!.git/**' --glob '!spec-dock/initiatives/**' \
  -- '--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|verify_full_regression|full_regression_baseline'
```

`rg` is supplemental; canonical proof is scanner JSON。

### 20.5 Protected snapshot compare

Capture after snapshot with same script and compare exact entries, excluding the dedicated new evidence directory。Any protected drift stops。

## 21. Checkpoint P17 — Final-source workflow attempt before merge

Commit/push final source candidate only under explicit commit/push authorization。The first Actions run for this SHA is sole build producer。

Required final-source PR attempt:

- build invocation count 1。
- all roles same manifest/wheel/sdist bytes。
- per-attempt accepted。
- Linux process evidence complete。
- fault campaign 100%（candidate-bound、run once per candidate campaign）。
- consumer-zero、retained workflow、protected evidence pass。
- new required context GREEN。
- P14 human readback is exactly `U + new`; old context has already been removed while its emitter still existed.
- final candidate no longer emits the old context; no required context is missing.

For `pull_request`, resolve and test the PR head SHA/tree from event payload. If merge queue is active, separately resolve the `merge_group` SHA/tree and verify that the replacement required check is emitted there. Neither event may silently substitute the other event's source SHA.

Do not start first-five final campaign on PR head if human merge creates a different source SHA. PR evidence proves implementation and per-attempt behavior, not post-merge B3 candidate qualification。

## 22. Checkpoint P18 — Independent implementation reviews

### 22.1 Code Review Strict

On clean pushed exact final-source SHA:

- run `chatgpt-code-review-strict` fresh session。
- require pass、P0/P1=0。
- remediation stays same reviewer session for same purpose。
- any source change invalidates prior receipt。

### 22.2 Final Quality Gate Strict v2

After code review pass and full final-source verification:

- run `chatgpt-final-quality-gate-strict-v2` with Pro。
- bind exact SHA/tree、test receipts、workflow result、consumer-zero、context state。
- require pass。

Neither review authorizes agent merge。

## 23. Checkpoint P19 — Merge-ready PR and human boundary

PR base exact `codex/epic-00384-provider-test-strategy-planning`, never main。

PR evidence:

- problem/outcome and Issue #396 link。
- exact source SHA/tree。
- changed path classification NEW/MODIFY/DELETE/NO-TOUCH。
- test/lint/consumer-zero/protected receipts。
- candidate manifest and final-source per-attempt summary。
- new context RED/GREEN evidence。
- settings before/current/rollback。
- code review/final gate receipts。
- post-merge B3 runbook。

Human alone merges。Agent stops merge-ready。

## 24. Checkpoint P20 — Post-merge identity and final external readback

After human merge to Epic integration branch:

1. GitHub readback exact merge SHA/tree and accepted PR head tree。
2. Require merge tree equality; SHA may differ。
3. Treat merge SHA/tree as a new candidate identity。
4. Read back effective `U + new`, ruleset scope, review requirements and merge_group coverage。
5. Confirm old emitter absent in merge tree and old context not required。
6. Do not mutate settings in this checkpoint。

Mismatch/unavailable readback produces post-mutation StopReturn and blocks B3/materialization。No main merge。

## 25. Checkpoint P21 — Post-merge materialization, freeze and B3 campaign

### 25.1 One-time materialization (not an attempt)

Dispatch materialization for exact merged SHA/tree。Register state before build; execute packaging once; complete manifest/wheel/sdist/environment/candidate evidence。Build/cancel/missing/mismatch poisons source. Do not rerun same SHA。

```bash
uv run python -m scripts.quality.provider_gate.cli materialize-candidate   --repository "$REPOSITORY" --source-sha "$MERGED_SHA"   --output-root "$MATERIALIZATION_PHYSICAL_ROOT"
```

### 25.2 Campaign freeze

After `materialized`, bind candidate identity、environment hash、gate version、45-entry definition hash、window contract ID into immutable CampaignFreezeV1。No campaign attempt can be registered earlier。

```bash
uv run python -m scripts.quality.provider_gate.cli freeze-campaign   --materialization "$MATERIALIZATION_INDEX"   --fault-definition "$ISSUE_DIR/artifacts/seeded-fault-catalogue-v1.json"   --output "$CAMPAIGN_FREEZE_JSON"
```

### 25.3 Independent attempts and aggregates

Register each final-gate attempt before role start, consume exact stored bytes, execute one role graph, and retain all started outcomes。Parent-generated projection determines first population/window/acceptance; this Plan does not choose replacements or success filtering。Materialization is never a member。No run rerun、same attempt ID、artifact replacement、campaign reset。

### 25.4 Candidate-bound fault campaign

Bind exact 45 definitions to candidate/environment and execute all entries through test-only seams。Require exact code/stage for each and no denominator change。

### 25.5 Final evaluation

Evaluate per-attempt separately from campaign/fault/window; then evaluate B3 with context final readback、consumer-zero、protected snapshot、review receipts。B3 is not claimed until actual output says accepted and raw/API evidence has been independently inspected。

## 26. Checkpoint P22 — B3 receipt and handoff to Epic main merge

Create post-merge B3 receipt outside tracked future-fact docs first。Receipt includes:

- exact integration SHA/tree。
- producer run/artifact IDs、manifest/wheel/sdist hashes。
- environment fingerprint。
- first-five attempt IDs/raw hashes。
- fault catalogue digest/result。
- latest-twenty attempt IDs/results。
- final context before/after/readback。
- consumer-zero/deletion proof。
- protected snapshot proof。
- qualification-result hash。
- review receipts and rollback readiness。

Only after B3 GREEN may主担当 update canonical Report/Issue projection and prepare final Epic PR to main。One human Epic merge remains required。

## 27. Exact command/output matrix

| Stage | Command | Expected output class |
|---|---|---|
| Spec validation | `./spec-dock/scripts/spec-dock validate` | exit 0, nodes observed |
| Policy projection | `uv run python scripts/maintenance/generate_provider_qualification_policy.py --check` | exit 0, diff 0 |
| Contracts | `uv run python -m scripts.quality.provider_gate.cli validate-contracts` | all schema/catalogue/role contracts valid |
| Unit | `uv run pytest -q tests/unit/provider_gate --tb=short` | pass, skip/xfail 0 |
| Integration | `uv run pytest -q tests/integration/test_provider_gate_role_graph.py tests/integration/test_provider_gate_faults.py --tb=short` | pass, synthetic only |
| Lifecycle non-regression | `uv run pytest -q tests/unit/provider_lifecycle --tb=short` | pass |
| Distribution non-regression | `uv run pytest -q tests/cli_runtime/test_distribution_cutover.py --tb=short` | pass |
| Lint | `make lint` | Ruff check/format + mypy pass |
| Ordinary suite | `uv run pytest -q --tb=short` | exit 0, no old policy skip reason |
| Consumer scan | `... scan-old-consumers --require-zero` | consumer 0, retained workflow protected |
| Linux role | `... run-role --role linux-canonical` | one pytest root, worker1, no shard, raw metrics |
| sdist role | `... run-role --role sdist-smoke` | no build, actual sdist parity pass |
| macOS role | `... run-role --role macos-delta` | owned delta pass, no Linux performance predicate |
| Attempt eval | `... evaluate-attempt` | accepted only with all role/raw identity complete |
| Final eval | `... evaluate-qualification --mode final` | B3 accepted only with five/fault/twenty/context/protection |

Exact pass counts are observations, not specification constants。Any expected output class change requires diff/reason review, not blanket update。

## 28. Stop-and-return payload

Use only `provider-gate-contracts-v1.schema.json#/$defs/StopReturnV1`。It records finite reason code、stage-correct evidence、scope impact、owners/actions、mutation flag、changed/external surfaces、rollback/recovery status。Private absolute paths、credentials/tokensをwireへ入れない。`automatic_rollback_performed=false`。

Pre-mutation example: B1/B2 missing、same-Red fail。Post-mutation examples: P11 workflow pushed、P13/P14 settings changed、P15 files deleted、P21 attempt started。Post-mutation changesをfalse/emptyへ偽装しない。

## 29. Stop conditions

### Admission

- #395 merge identity不一致、fresh B1未受入、same-tip B2未受入。
- Historical claim/別SHA/Issue readyを代替にしようとした場合。
- same-Red pass P0/P1=0、projection readback、explicit dispatch未達。

### Parent/no-touch

- Parent values/population/window/aggregation/scope/rejection/escape変更が必要。
- #392/#395 Product/lifecycle、retained workflow、protected data変更が必要。

### Materialization/evidence

- producer不一意、one build/actual bytes/environment/retention不成立。
- poisoned same SHAのrebuildが必要。
- evidence stage/path/hash不成立。

### Ownership/plugin/process

- baseline/delta未計画node、duplicate/missing owner、collection mismatch。
- plugin sole filterがP15後に残らない。
- root/worker/shard/descendant measurement/reapを閉じられない。

### Fault/history/aggregate

- 45 entryの一つでも未実行/未検出/wrong code/stage/denominator drift。
- started failure/cancel/missing/rerunを除外・置換しなければpassできない。

### Cutover/external

- consumer scan不完全またはcount>0。
- context/ruleset/merge queue readback不能、REDがblockしない、U drift、rollback不明。
- partial old-policy deletionやold writer fallbackが必要。

## 30. Rollback and recovery matrix

| State | Valid recovery |
|---|---|
| B1/B2 unresolved | No implementation mutation; return exact missing evidence to parent owner |
| Spec candidate not passed | Repair specs only; same-Red re-review |
| Implementation uncommitted | Repair/abandon Issue branch; predecessor tip unchanged |
| Materialization poisoned | Forward-fix new source SHA/tree; never rebuild same SHA |
| Shadow workflow failed | New source commit and materialization; no workflow rerun |
| Context additive transition failed | Human restore captured before-state; merge blocked |
| P15 deletion failed | Preserve actual branch; forward-fix or abandon unmerged PR; no partial accepted state |
| #396 merged, B3 not accepted | Stop Epic main; human settings restore + whole-merge revert or owned forward-fix/new candidate |
| B3 accepted, main unmerged | Any source change invalidates B3; materialize/evaluate new candidate |
| Epic main merged | Parent-controlled suffix recovery/forward-fix; automatic rollback forbidden |

## 31. Completion criteria

Authoring completion and Issue/Product completion are distinct。

### 31.1 This specification pack is authoring-complete when

- R/D/P/handoff/schema/machine artifacts/HTML are synchronized。
- Historical/baseline/raw bytes are preserved。
- ZIP CRC、manifest、schema、delta/fault/HTML validations pass。
- No Product/test/workflow/policy/settings mutation occurred。

This does not mean independent review pass or implementation authorization。

### 31.2 Product implementation may start only when

1. Clean pushed spec candidate exists。
2. Same-Red `review_status=pass`, P0/P1=0; P2/P3 follow the review contract。
3. Issue projection update/readback complete。
4. #395 owner correction/acceptance and corrected merged SHA/tree are read back。
5. Fresh B1 is accepted at that corrected exact SHA/tree。
6. Fresh B2 is accepted at the same exact tip after B1。
7. Current specification freeze is clean and exact; no concurrent writer exists。
8. Explicit implementation dispatch is received。

### 31.3 Issue #396 completes only when

- replacement implemented/tested and human merged to Epic branch。
- consumer-zero then old policy retired on final source。
- permanent plugin ownership、retained workflow、protected data、context final readback GREEN。
- merged candidate materialized once, campaign/fault/window evaluated by parent projection, B3 receipt complete。

Epic main merge remains a separate human gate。

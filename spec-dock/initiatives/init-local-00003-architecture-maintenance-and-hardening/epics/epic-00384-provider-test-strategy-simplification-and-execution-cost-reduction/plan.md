---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-02"
依存: ["requirement.md", "design.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "artifacts/provider-lifecycle-wire-contract.md", "artifacts/active-failure-disposition-register.md"]
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "95d7562ca1762e0b2a717912484eba5a5c2377f1"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

## 1. Governance

GitHub #392 is the sole implementation-and-verification unit. #387 must be human-merged and admitted before S10; its canonical files are read-only to #392. #388–#390 remain superseded. Internal PRs, canary and evidence operations do not create additional Issues. Human review/merge and required-context writes remain external gates.

## 2. Purpose workspaces

Before a purpose writes data, the orchestrator independently calls the external-workspace helper and retains its non-serializable handle. Exact variables are:

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

No aggregate root variable is created. Each cleanup uses only its captured handle after registered outputs are no longer required.

## 3. Ordered execution and main gates

| PR | Steps | Sole main gate | Main state |
|---|---|---|---|
| PR-A | S00 admission; S10 model/wire; S20 filesystem/stage; S30 update/resume | S30 | Old public product and exact legacy dogfood; dormant successor; current gates GREEN. |
| PR-B | S40 public cutover/docs; S50 legacy/tripwire; S60 terminalization/current-gate repair/dogfood migration | S60 | Complete `0.2.4`, closed wire including terminal cleanup, current workflows GREEN, active failures zero, complete dogfood. |
| PR-C | S70 final gate/policy removal/dogfood update/compatibility head; S80 two-head final evidence | S80 | Distinct final head, compatibility job absent, final evidence rerun, new required context, old machinery absent. |

S40, S50 and S70 are non-main checkpoints.

## 4. S00 admission

S00 verifies replacement manifest/`SPEC_FREEZE_COMMIT`, external protected witness, exact legacy dogfood and Issue #387.

For #387 it does not read a candidate or PR identity from the report. It collects timeline/cross-reference PRs, validates each exact PR-head association through the commit-pulls endpoint, filters repository/base/merged/report/lineage, requires exactly one, verifies head-tree equals merge-tree, and reads report/ledger/collection from the merge tree. The report provides only the twelve mappings consumed by `ISS387-THREE-WAY-V2`.

Commands use purpose paths directly, for example:

```bash
uv run python -m scripts.quality.verify_full_regression   --shards 4   --artifact-dir "$ISS392_WS_FULL_REGRESSION_S00"
```

## 5. PR-A and PR-B

- S10 implements strict model, 38 codes, 136 wire rows, valid four/twenty-nine goldens and table-driven rejection.
- S20 implements descriptor-safe operations, process-independent ACTIVE/stage and fresh bootstrap.
- S30 implements exact-tuple resume plus mandatory terminal-cleanup recovery and runs current gates using `ISS392_WS_FULL_REGRESSION_S30`.
- S40 connects final public lifecycle/provider docs but does not touch checked-in dogfood.
- S50 uses `ISS392_WS_BASELINE_BUILD`, `ISS392_WS_TRIPWIRE` and independently-created fresh-consumer workspaces only.
- S60 terminalizes failures, retargets current Provider CI, externalizes retained Full Regression through an independent workflow workspace, updates lifecycle docs/AGENTS lifecycle text, removes old engine/tests and performs one complete dogfood migration.

PR-B cannot merge unless terminal cleanup crash/retry tests, current PR workflow and current main-push verifier are independently GREEN.

## 6. PR-C safe two-head plan

### E384-P-001 — Compatibility head

S70 adds final provider-gate code, the complete D-015–D-026 schema/CLI/fixture contract, stable environment, structural tests and final operator/test-policy docs; removes old consumers before providers; performs the second complete dogfood update; finalizes the tracked #392 report; creates `PRC_COMPAT_HEAD`; completes the human context sequence; and commits distinct `PRC_FINAL_HEAD` by removing only compatibility job `provider-tests`. Actual head/run identities remain external.

Push `PRC_COMPAT_HEAD` externally. Its workflow emits both contexts. Compatibility `provider-tests` needs producer and attestation, creates separate workflow-api and artifact-download workspaces, downloads candidate/evidence, fetches run/jobs/artifacts JSON, invokes the same verifier interface as S80, builds nothing and ignores the canary marker.

### E384-P-002 — Required-context transition

1. Record compatibility SHA/tree externally; require both contexts GREEN.
2. Human adds `Provider CI / provider-gate` while old `Provider CI / provider-tests` remains required.
3. Read back both contexts and review requirements.
4. Dedicated non-merge canary adds only `.github/provider-gate-canary-red`.
5. Prove new context RED, compatibility context GREEN, merge blocked.
6. Close canary without merge; restore compatibility PR GREEN.
7. Human removes only old required context and reads back new-only required.

### E384-P-003 — Read-only authoritative rerun

S70 has already created the distinct descendant `PRC_FINAL_HEAD` by removing only compatibility job `provider-tests`. S80 freezes/reads that SHA/tree externally and owns no commit. No tracked report edit is allowed. Dispatch a new final run, rerun producer/all roles/attestation/gate, download candidate/evidence/API snapshots to purpose-specific workspaces, verify actual bytes and final required contexts, then emit/post/read back pre-merge attestation. Only final head may merge.

## 7. Evidence and closure

Tracked report contains pre-freeze methodology, implementation, terminalization and protection summaries only. Actual compatibility/final SHA/tree/run IDs are external.

After human merge, execute exactly:

1. fetch merge commit and compare final-head tree with merge tree;
2. start `python3 ./spec-dock/scripts/spec-dock issue finish`; capture its start/end and returned issue number, already-closed flag, active-clear and post-sync result;
3. immediately read #392 state/timeline and bind the selected close event to the issue-finish interval/reported already-closed relation; do not invoke `close --id iss-00392`;
4. render/post/read back post-merge closure on #392, then create external comment receipt;
5. re-evaluate Epic acceptance;
6. `python3 ./spec-dock/scripts/spec-dock close --id epic-00384` and read actual #384 close event;
7. render/post/read back Epic closure on #384, then create external comment receipt.

No payload predicts its own comment identity or a future close event.

## 8. Stop policy

Stop for specification/#387 identity mismatch; report identity fields; zero/multiple merged PR; repository workbench mutation; aggregate external root; workspace-handle mismatch; unsafe ACTIVE/stage; terminal-cleanup failure without exact wire result; wire count/golden drift; S40/S50 dogfood drift; partial S60/S70 dogfood; broken current/final gate; compatibility verifier missing candidate/evidence/API bytes; canary affecting old context; final head not distinct or diff beyond job removal; extra packager; evidence/environment mismatch; tracked report head identity; wrong closure order; comment edit/hash mismatch; or merge-tree mismatch.

Forward-fix in #392 only. `owner_decisions_required=[]`.

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
  sha: "0fafbf3e02d2fcd5b622d6a997323e0f98eb1c78"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

## 1. Governance

GitHub #392 is the sole implementation-and-verification unit. #387 must be human-merged and admitted before S10; its canonical files are read-only to #392. #388–#390 remain superseded. Internal PRs, canary and evidence operations do not create additional Issues. Human review/merge and required-context writes remain external gates.

## 2. Purpose workspaces

For every purpose, the orchestrator creates a private owner root/live handle and reserves the exact child defined in Issue Design D-007. Only the reserved tree is exported in its one `ISS392_WS_*` variable. Commands receive that path directly. The private root is never exported or accepted by CLI. Owner performs reserve -> spawn -> seal -> read/upload-confirm -> cleanup; unknown entries or owner death preserve and stop.

Full Regression uses the reserved trees directly:

```bash
uv run python -m scripts.quality.verify_full_regression --shards 4 --artifact-dir "$ISS392_WS_FULL_REGRESSION_S00"
```

S30/S60 substitute their exact variable. Provider jobs use their exact provider reserved-tree variables. No aggregate root exists.

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

- S10 implements strict model, 38 codes, 142 wire rows, valid four record and thirty-three public JSON goldens and table-driven rejection.
- S20 implements descriptor-safe operations, process-independent ACTIVE/stage and fresh bootstrap.
- S30 implements exact-tuple resume plus deferred desired invocation: cleanup failure says retry cleanup then desired command; cleanup success returns desired command or none; all cleanup returns are cleanup-only. It runs current gates using the reserved `ISS392_WS_FULL_REGRESSION_S30` tree.
- S40 connects final public lifecycle/provider docs but does not touch checked-in dogfood.
- S50 uses `ISS392_WS_BASELINE_BUILD`, `ISS392_WS_TRIPWIRE` and independently-created fresh-consumer workspaces only.
- S60 terminalizes failures, retargets current Provider CI, externalizes retained Full Regression through an independent workflow workspace, updates lifecycle docs/AGENTS lifecycle text, removes old engine/tests and performs one complete dogfood migration.

PR-B cannot merge unless terminal cleanup crash/retry tests, current PR workflow and current main-push verifier are independently GREEN.

## 6. PR-C safe two-head plan

### E384-P-001 — Compatibility and final tracked heads

S70 implements all nine exact Provider Gate commands, raw ZIP transport/safe extraction, job permissions, evidence schemas, stable environment, structural tests and final operator docs. It removes old policy consumer-first, completes the second dogfood update and finalizes tracked report. It creates `PRC_COMPAT_HEAD`, runs both contexts and completes the human transition, then creates `PRC_FINAL_HEAD` by removing only compatibility `provider-tests`. Actual identities stay external. S70 owns both commits; S80 owns none.

Compatibility provider-tests creates one private provider-verification owner/reserved tree containing API snapshots, raw candidate/evidence ZIPs, empty extraction destinations and verifier stdout. It waits until provider-gate is terminal, selects the exact green/canary verification phase, and invokes the verifier, which performs safe extraction. It packages nothing and ignores the canary file.

### E384-P-002 — Required-context transition

1. Record compatibility SHA/tree externally; require both contexts GREEN.
2. Human adds `Provider CI / provider-gate` while old `Provider CI / provider-tests` remains required.
3. Read back both contexts and review requirements.
4. Dedicated non-merge canary adds only `.github/provider-gate-canary-red`.
5. Prove new context RED, compatibility context GREEN, merge blocked.
6. Close canary without merge; restore compatibility PR GREEN.
7. Human removes only old required context and reads back new-only required.

### E384-P-003 — Read-only authoritative rerun

S80 reads the S70-created final head. It creates one provider-verification owner/tree, dispatches a fresh final run, stores API snapshots and raw Actions archives there, creates registered empty extraction destinations, and invokes `post-run-final`; the verifier performs safe extraction and actual-byte checks. It reads final permissions/contexts and posts the pre-merge attestation. No tracked write, local build, update, sync or commit occurs.

## 7. Evidence and closure

Tracked report has pre-freeze methodology/implementation facts only. External evidence binds heads, raw archives, extracted/API bytes, permissions, metrics and comments.

After human merge:

1. compare final-head and merge tree;
2. run issue-finish attempt 1 and capture exact interval/result;
3. if success, select attempt 1;
4. if only issue-finish post-sync failed after #392 close/active clear, bind the unique original close event, run exact `active set --id iss-00392`, verify its exit/stdout/stderr, run `active show` and require exact active issue readback, then retry issue finish with `already_closed=true`; active-set supplies no post-sync status;
5. repeat recovery once only if the second post-sync also fails; after three failed attempts stop;
6. create post payload from all attempts/restores and the final successful interval; post/read receipt on #392;
7. re-evaluate Epic, close/read #384, post/read Epic receipt.

No `close --id iss-00392` is run. Retry finish attempts cannot create a second close event.

## 8. Stop policy

Stop for specification/#387 identity mismatch; cleanup continuation ambiguity or deferred-request loss; private owner-root exposure or reserved-tree mismatch; raw archive/API/upload digest, extraction or permission drift; report identity fields; zero/multiple merged PR; repository workbench mutation; aggregate external root; workspace-handle mismatch; unsafe ACTIVE/stage; terminal-cleanup failure without exact wire result; wire count/golden drift; S40/S50 dogfood drift; partial S60/S70 dogfood; broken current/final gate; compatibility verifier missing candidate/evidence/API bytes; canary affecting old context; final head not distinct or diff beyond job removal; extra packager; evidence/environment mismatch; tracked report head identity; post-sync recovery beyond three attempts, active restoration failure, ambiguous close event or wrong closure order; comment edit/hash mismatch; or merge-tree mismatch.

Forward-fix in #392 only. `owner_decisions_required=[]`.

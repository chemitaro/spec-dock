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
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

## 1. Governance

GitHub #392 is the sole implementation-and-verification unit. #387 must be human-merged and admitted before S10. #388–#390 remain superseded. Internal PRs, a canary PR and evidence operations do not create additional Issues. Human review/merge and required-context writes remain external gates.

## 2. Ordered execution

| PR | Steps | Sole main gate | Main state |
|---|---|---|---|
| PR-A | S00 admission; S10 model/wire; S20 filesystem/stage; S30 update/resume | S30 | Old public product and exact legacy dogfood; dormant successor; current gates GREEN. |
| PR-B | S40 public cutover/docs; S50 legacy/tripwire; S60 terminalization/current-gate repair/complete dogfood migration | S60 | Complete `0.2.4`, closed wire, current workflows externalized and GREEN, active failures zero, complete dogfood. |
| PR-C | S70 final gate/policy removal/second dogfood update/compatibility head; S80 context transition/final head/evidence | S80 | Final new required gate, old context/job absent, final evidence on final head, old machinery absent. |

S40, S50 and S70 are non-main checkpoints.

## 3. S00 admission

S00 creates an ephemeral external `admission` workspace and external witnesses. It validates manifest/`SPEC_FREEZE_COMMIT`, exact baseline, dogfood legacy identity and `ISS387-THREE-WAY-V2`.

For #387 it reads the report candidate/mapping, discovers the unique merged PR by intersecting GitHub candidate-associated PRs with Issue #387 timeline links, verifies candidate ancestry and the exact two-path evidence tail, and then evaluates final-head/merge tree, ledger and collection. The report PR number is never an input.

All Full Regression commands use:

```bash
uv run python -m scripts.quality.verify_full_regression \
  --shards 4 \
  --artifact-dir "$ISS392_EXTERNAL_ROOT/full-regression-s00"
```

## 4. PR-A and PR-B

- S10 implements the strict model, all 123 wire rows and valid 4/16 goldens.
- S20 implements descriptor-safe target operations, persistent stage namespace, ACTIVE index and bootstrap recovery.
- S30 proves cross-process exact-tuple convergence and runs ordinary/current Full Regression with purpose `full-regression-s30` externally.
- S40 connects final public lifecycle and provider-side lifecycle docs but does not touch checked-in dogfood.
- S50 uses only external synthetic consumers and tripwire workspaces.
- S60 fixes/supersedes admitted failures, retargets current Provider CI, updates lane/ledger/timing references, minimally externalizes the retained main-push workflow, updates lifecycle docs/AGENTS lifecycle text, removes old engine/tests and performs one complete dogfood migration.

S60 local Full Regression uses purpose `full-regression-s60`; the retained workflow uses the same helper below `${{ runner.temp }}`. PR-B cannot merge if either current PR gate or current main-push verifier is not independently GREEN.

## 5. PR-C two-head plan

### E384-P-001 — S70 candidate and compatibility head

S70 adds final provider-gate code, exact evidence schemas, `EVIDENCE-FIXTURE-V1` byte/size/hash conformance tests, stable environment, structural tests and final test-policy docs. It retires/replaces every old consumer before deleting old providers/data/workflow. It performs the second complete dogfood update and finalizes the tracked #392 report.

The first pushed source identity is `PRC_COMPAT_HEAD`. Final workflow includes all authoritative jobs plus exact compatibility job `provider-tests`, which needs `provider-attestation`, downloads/verifies provider evidence and succeeds independently of the `provider-gate` canary check.

### E384-P-002 — Context transition

1. require both contexts GREEN on `PRC_COMPAT_HEAD`;
2. human adds `Provider CI / provider-gate` as required while `Provider CI / provider-tests` remains required;
3. read back both and review requirements;
4. open dedicated canary PR with only `.github/provider-gate-canary-red` added;
5. prove new context RED and old context GREEN, with merge blocked;
6. close canary without merge and restore implementation PR compatibility head GREEN;
7. human removes only old required context and reads back new-only required.

### E384-P-003 — Final head and authoritative rerun

Create `PRC_FINAL_HEAD` as one descendant commit removing only job `provider-tests` from `.github/workflows/provider-ci.yml`. No candidate/dogfood/report change is allowed. Freeze this final head/tree, rerun final Provider CI from scratch, download and verify actual bytes against the closed schemas and `EVIDENCE-FIXTURE-V1` serializer contracts, repeat qualification and final required-context readback, then emit pre-merge attestation. Only `PRC_FINAL_HEAD` may be merged.

## 6. Evidence and closure

Tracked report contains only pre-freeze methodology/implementation facts. External pre-merge attestation binds final head/tree, final run, candidate/evidence bytes, role receipts/evidence, qualification, compatibility/final context snapshots and report blob observed externally.

`emit-attestation` renders canonical JSON/comment bytes. Human posts one append-only comment to #392 and verifies comment identity/hash/no edit. Human merge follows. Post-merge #392 comment records final-head/merge tree equality and lifecycle close. #384 receives a separate Epic closure comment. Any changed head or comment edit invalidates dependent evidence.

## 7. Stop policy

Stop the relevant gate for: specification/#387 identity mismatch; invalid evidence tail; repository workbench mutation; unapproved report/meta exclusion; persistent stage namespace/index drift; wire count/golden mismatch; legacy dogfood drift at S40/S50; partial S60/S70 dogfood; retained workflow writing repository workbench; active/unmapped failure; broken current/final gate; extra packager or incomplete actual-byte evidence; environment drift; context-order violation; final-head diff beyond compatibility job removal; attestation schema/comment mismatch; or merge-tree mismatch.

Forward-fix in #392 only. Do not add a new Issue, feature toggle, old fallback, skip, approved failure, sharding workaround or agent merge. Owner decisions required: none.

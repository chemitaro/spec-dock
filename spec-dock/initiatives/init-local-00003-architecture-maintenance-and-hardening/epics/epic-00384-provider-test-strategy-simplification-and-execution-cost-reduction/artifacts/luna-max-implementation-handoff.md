---
種別: Implementation Handoff
対象: "GPT-5.6 Luna / reasoning Max"
Issue: "iss-00392"
最終更新: "2026-09-02"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# Luna Max Implementation Handoff

## 1. Authority order

1. Execute Issue `plan.md`.
2. Use Issue Requirement for behavior and Issue Design for exact symbols/schemas.
3. Treat `provider-lifecycle-wire-contract.md` as the only public wire authority: 36 codes, 123 rows, 4 record and 16 public JSON review goldens.
4. Treat `active-failure-disposition-register.md` rule `ISS387-THREE-WAY-V2` as the only #387 admission/terminalization authority.
5. Use Epic R/D/P and ADR for boundaries/merge governance.
6. Follow current root AGENTS until the exact S60/S70 section updates.
7. Do not choose Product, Policy, Security, filesystem, CI evidence or migration behavior. A mismatch is a stop.
8. Never merge or write required contexts.

## 2. PR/head graph

```text
#387 merge -> S00
PR-A: S10 -> S20 -> S30 main gate
PR-B: S40 internal -> S50 internal -> S60 main gate
PR-C/S70:
  final candidate + dogfood + report -> PRC_COMPAT_HEAD
  -> human context transition -> PRC_FINAL_HEAD (provider-tests removal only)
S80: read-only final evidence -> PR-C main gate
human merge -> external closure
```

S40/S50/S70 are never merge-ready. S80 owns no tracked path.

## 3. Critical fixed contracts

### Targets and dogfood

```text
roots: spec-dock/docs, templates, system, scripts
slots: .agents/skills/spec-dock, .agents/skills/spec-dock-grill-with-docs
record: spec-dock/spec-dock.version
markers: <slot>/.spec-dock-provider-slot.json
seeds: spec-dock/.gitignore, .github/workflows/ci.yml
```

S40/S50 leave checked-in legacy dogfood exact. S60 migrates all targets as one candidate. S70 updates all targets as one candidate. S80 only reads.

### Record/resume

Exact seven keys. Resume tuple operation/candidate digest/seed policy. Fresh init only create-if-absent; every other intent preserve-only.

### Persistent stage

```text
<repo-parent>/.spec-dock-provider-stages-v1/
  repositories/<repository-key>/ACTIVE.json
  repositories/<repository-key>/stages/<tuple-key>/STAGE-OWNER.json
```

ACTIVE is created first and is the sole index. State allocating/ready/terminal-cleanup. No scan. Same tuple resumes across process exit; mismatch blocks. Bootstrap-without-record is ACTIVE+owner controlled. Stage first, ACTIVE last during cleanup.

### Ephemeral external workspaces

All admission/build/full-regression/witness/API/download/attestation temp uses owner-bound OS temp. Never write/delete repository workbench. S00/S30/S60 pass explicit external `--artifact-dir`; S60 retained workflow uses `${{ runner.temp }}` through the same helper.

### Protected exclusions

Only exact #392 `report.md` and `.meta.json` are excluded. Separate external ledger restricts report role and meta `updated_at`. All other initiatives/artifacts and entire repository workbench remain exact.

## 4. Issue #387 V2 checklist

- Report has candidate SHA/tree and 12 mappings; no PR number/merge facts.
- Candidate is last semantic commit and ancestor of final PR head.
- Tail paths: required #387 report, optional #387 meta updated_at only.
- Intersect candidate-associated PRs and Issue #387 timeline PRs; exactly one.
- Verify exact repo/base/merged/candidate ancestry/tail/final-head merge-tree equality/main reachability.
- Apply `ISS387-THREE-WAY-V2`; no fixed post-row count.
- Any zero/multiple PR, extra tail, mapping/signature/lineage drift stops before S10.

## 5. Step ownership highlights

### S10–S30

Lifecycle package, external workspace/stage namespace, model/candidate/service/fault/wire tests. Public route/dogfood old through S30.

### S40

Provider/public code and provider-side lifecycle docs/root README lifecycle only. No dogfood or AGENTS.

### S50

External artifact/migration/tripwire tests only. No dogfood.

### S60

Old engine/tests removal; current Provider CI retarget; retained Full Regression external output; ledger/timing/conftest/lane consumers; lifecycle docs; AGENTS lifecycle/uninstall paragraphs; complete dogfood migration; #392 report summary. Keep current test-policy providers/workflow operational until S70.

### S70

Final provider gate/evidence schemas/environment/tests/workflow, old consumer-first removal, final AGENTS/test-policy docs, complete second dogfood update and tracked report. Create compatibility head, execute human context sequence, then final head by removing only `provider-tests` job. No merge.

### S80

Tracked none. Final-head workflow dispatch/download/actual-byte verification/qualification/context readback/pre-merge comment only.

## 6. Final CI byte graph

```text
build -> linux canonical, sdist smoke, macOS delta
all four -> attestation -> provider-gate
attestation -> provider-tests only at compatibility head
```

Only build job invokes packaging once. Candidate artifact has manifest+wheel+sdist. Four receipt artifacts each have receipt+role evidence. Final evidence has exact nine files. Verify actual bytes, API artifact metadata, job/needs/source/tree, parent-child hashes and build counts.

## 7. Evidence schema summary

All JSON is compact UTF-8 plus LF, exact key order, no extras. Receipt common schema and role detail schemas are in Issue Design D-017–D-019. Attestation payloads and emitter are D-021–D-022. `EVIDENCE-FIXTURE-V1` in D-024 is the exact canonical byte/size/SHA-256 serializer oracle. Do not defer any field, unit, enum/nullability or hash relation.

`emit-attestation` is pure local. Human posts exact comment body as a new issue comment. Pre/post target #392; Epic target #384. Verify comment ID, actor, marker/body hash and created_at==updated_at. Edit/delete invalidates closure.

## 8. Two-head context sequence

1. `PRC_COMPAT_HEAD`: both contexts GREEN; old compatibility job validates attestation independently.
2. Human adds new required while old remains; read back.
3. Canary adds only `.github/provider-gate-canary-red`; new RED, old GREEN, merge blocked; close.
4. Implementation compatibility head GREEN.
5. Human removes old required; read back new-only.
6. `PRC_FINAL_HEAD`: remove only job `provider-tests` from provider-ci.yml.
7. S80 reruns all authoritative evidence on final head and final readback.

Any additional final-head diff requires a new compatibility head and repeat.

## 9. Stop matrix

| Condition | Required action |
|---|---|
| #387 report PR number/future merge fact, candidate not ancestor, invalid tail or zero/multiple PR | stop before S10; canonical correction/Strict rereview |
| unknown register node/signature/mapping | stop before S10 |
| wire count/golden/relation mismatch | test defect; do not invent |
| repository workbench output or broad protected exclusion | destructive stop |
| persistent stage scan/cross-device/unknown adoption/index mismatch | fail closed |
| S40/S50 dogfood drift | restore exact legacy; no merge |
| S60 current PR/main-push gate not independently GREEN | block PR-B |
| retained workflow lacks external `--artifact-dir` | block PR-B |
| S60 partial dogfood or protected/exclusion drift | block PR-B |
| S70 old consumer remains or extra packager/schema choice | block PR-C |
| compatibility job does not validate evidence independently | block context transition |
| canary does not produce new RED/old GREEN/block | restore settings; stop |
| final head changes anything beyond compatibility job removal | return S70/repeat transition |
| S80 tracked write/build/update/sync | invalidate S80 |
| actual evidence bytes/hash/environment mismatch | block PR-C |
| attestation comment edited/deleted/mismatched | invalidate dependent closure |
| merge tree mismatch | do not finish Issue |

## 10. Definition of done

Only S30/S60/S80 are merge gates. All temporary data stayed outside repository, process restarts are deterministic, protected paths/exclusions are exact, dogfood is complete at candidate gates, current and final gates are independently safe, final evidence belongs to `PRC_FINAL_HEAD`, human merge remains pending until handoff and `owner_decisions_required=[]`.

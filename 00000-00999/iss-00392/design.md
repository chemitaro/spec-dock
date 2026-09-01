---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["epic-00384", "init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "e47c1356892857e61388c7aefb2539d2061d1b9c"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Exact production topology

```text
src/spec_dock/
  cli.py
  context_pack.py                                  (new)
  provider_lifecycle/                              (new)
    __init__.py
    model.py
    candidate.py
    filesystem.py
    legacy_023.py
    service.py
    public_result.py
  assets/legacy_0_2_3.json                         (new)

scripts/provider_gate.py                           (new, PR-C)
ci/linux-qualification.Dockerfile                  (new, PR-C)
ci/linux-qualification-environment.json            (new, PR-C)
tests/provider_test_ownership.json                 (new)
```

Final deletesold managed engine/manifest、ledger/timing/quality sharder、root policy hook、main-push Full Regression onlyatdefined PR boundaries。Non-lifecycle context rendering moves to`src/spec_dock/context_pack.py::render_context_pack()`。

## 2. Exact symbols

`model.py`: version/path constants、`SeedPolicy`、`ResumeIdentity`、states/operations/status、record/marker/candidate/observation/action/result/fault protocol、strict parsers。

`candidate.py`: packaged candidate build、materialize、candidate/tree digest、stage validate、seed source load。

`filesystem.py`: repository/parent/container bindings、staging owner、POSIX filesystem、container observe/bootstrap/cleanup、native rename、record/root/slot/seed publication/cleanup。

`legacy_023.py`: fixture/observation/recognizer/loader。

`service.py`: classify/install/update/uninstall/init/update dispatch/resume。

`public_result.py`: exit/text/JSON mappings。

## 3. Code-fixed paths

`SPEC_DOCK_CONTAINER=spec-dock`; roots docs/templates/system/scripts; slots exact two; seeds exact two; record `spec-dock/spec-dock.version`; slot marker `.spec-dock-provider-slot.json`。No arbitrary path arguments。

## 4. Strict data contracts

### I392-D-001 — Record

Seven exact keys。Max4096、regular/link1、UTF-8 duplicate-reject JSON。State/operation/policy relations perRequirement。Resume identity exact `(operation,candidate_digest,seed_policy)`。

### I392-D-002 — Candidate

Canonical `provider-candidate-v1` stream containsversion andsorted logical path/kind/mode/size/content hash entries。Unsafe kinds reject。Seeds/record/generated marker excluded。

### I392-D-003 — Slot marker

Exact schema/slot/version/candidate digest。Self excluded fromcandidate digest。

### I392-D-004 — Stage owner

Exact schema、root device/inode、operation、candidate digest、seed policy、created_spec_dock null ordevice/inode。Fsync beforebootstrap andafteridentity update。Mismatch blocks。

## 5. Descriptor-safe fresh bootstrap

### I392-D-005 — Classification order

Bind root -> probe record -> validate final state orlegacy -> ifabsent observecontainer absent/real/symlink -> requirefixed roots/slots absent -> stage collision -> result。Existing real container unknown child allowed。JSON-like invalid record neverlegacy fallback。

### I392-D-006 — Bootstrap algorithm

Stage/owner/preflight -> absence witness -> exclusive mkdirat -> no-follow open -> visible/held identity -> parent fsync -> stage owner identity fsync -> incomplete record。Pre-record exact empty cleanup yieldsblocked/mutation false/bootstrap_rolled_back true。Failure tocleanup retainsstage andpartial/mutation true。Existing container nevercleanup;uninstall neverdeletes。

## 6. Native filesystem protocol

Root fd nofollow/directory/cloexec + flock。Parents dirfd-relative。Visible/held revalidate。Linux renameat2 no-replace/exchange;macOS renameatx_np excl/swap。No fallback/EXDEV support。

## 7. Dispatch and operation protocol

### I392-D-007 — Pure seed policy derivation

Create onlyinit/init-force + never-installed absent。Allother install/update/migration/uninstall preserve。Resume usesrecorded exact,notderivation fromseed state。

### I392-D-008 — Install/update

Lock/classify/policy/candidate/stage/bootstrap/incomplete/roots/slots/policy seeds/postcondition/ready/cleanup。Ready fromfresh may retaincreate policy asprovenance;later update beginsnew preserve operation andneverrecreates seeds。

### I392-D-009 — Uninstall

Remove-specs trap beforetarget observation。Then dry-run orapply incomplete preserve -> detach roots/slots -> protect/container validation -> tooling-absent preserve -> cleanup。

### I392-D-010 — Resume

Exact request/stage/record tuple。Bootstrap-without-record additionally exactcreated identity。Matching target no-op。No persistent progress list。Cross tuple blocked。

## 8. Legacy and tripwire

Single `legacy_0_2_3.json` whole-tree fixture。Migration/uninstall preserve-only。Composite sitecustomize interceptsPython audit/native symbols beforecall。Positive controls mandatory。

## 9. Public result

Result fields: status/code/operation/candidate/policy/mutation/bootstrap rollback/phase/actions/failed/pending/retry/warnings/errors。Uninstall JSON schema1 retainsmain fields andadds code/policy/mutation/bootstrap fields。

## 10. Tests

Final test paths includemodel/candidate/filesystem/service/public/fault/assets/ownership/gate、CLI lifecycle/uninstall/update、artifact/tripwire、macOS delta、tripwire support、ownership JSON。

Required policy tests: fresh seed faults resume create; update/reinstall/migration faults nevercreate; tamper/missing/unknown policy block; later update doesnotreusefresh create;uninstall terminal preserve;stage mismatch block。

Required container tests: absent success、existing real + unknown child、symlink/non-dir、absence race、failure aftermkdir/beforeowner/beforerecord、empty cleanup、cleanup failure/foreign child partial、uninstall keepscontainer、no recursive cleanup。

## 11. PR-B continuity

S60 removesold product engine/tests only。Current conftest/ledger/timing/quality/workflow stayoperational。Ledger active approved failures0 andstale node refs updated。Ownership checked bystandalone pytest。Current verifier GREEN。No provider_gate dependency。

## 12. PR-C gate replacement

### I392-D-011 — Atomic replacement set

S70 addsprovider gate、environment Dockerfile/descriptor、gate tests、Makefile/static analysis、new provider workflow、root AGENTS beforedeletingold workflow/policy/ledger/timing/quality scripts/markers。S70 non-main;S80 onlymerge。

### I392-D-012 — Provider gate subcommands

`freeze-linux-environment`、`build`、`verify-artifact`、`verify-environment`、`verify-node-ownership`、`canonical`、`macos-delta`、`qualify`、`summarize`、`emit-attestation`。Build callsoneuv build。Canonical onepytest child/no xdist。

### I392-D-013 — Environment descriptor

ID `specdock-linux-qualification-v1`; runner label、x86_64、base ref/digest、2CPU、8GiB、Python series、exactuv、lock hash。Freeze resolvesonce/refuses overwrite drift。Evidence exact fingerprint allruns。

## 13. Required context

Old retained -> newGREEN -> addnew required/keepold -> readbackboth -> dedicated non-merge canary RED/block -> closecanary/implementation GREEN -> removeold -> final readback。No setting write ifunreadable。

## 14. Specification and evidence

### I392-D-014 — S00 identities

`REPOSITORY_EVIDENCE_SHA`、manifest payload hashes、`SPEC_FREEZE_COMMIT`、#387 base/head/merge tree、implementation base areseparate。No stale self-diff。

### I392-D-015 — Attestations

`pre-merge-attestation-v1` canonical JSON includesfinal head/tree、report blob observedexternally、artifact/environment/test/context evidence andJSON hash。Post-merge/epic attestations includeclosure events。Neverwritten totracked report。

Tree compare exact PR head tree OID vsmerge commit tree OID。

## 15. Root AGENTS

S70 updatesroot AGENTS。Final positive commands andprovider-first/human gate required;old flags/ledger/shard/main-push guidance forbidden。S80 validates。

## 16. Traceability

| Requirement | Design |
|---|---|
| RQ-001 | D-014 |
| RQ-002〜003、008〜012 | D-005〜010 |
| RQ-004〜005 | D-001、D-004、D-007〜010 |
| RQ-006〜007 | D-002〜003 |
| RQ-013〜019 | D-007〜010、public result |
| RQ-020〜023 | tests、D-011〜013 |
| RQ-024 | required context |
| RQ-025〜026 | D-015、root AGENTS |

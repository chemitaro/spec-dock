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
  sha: "b094771e089c1f31618116e84be32fcf78704409"
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

## 11. PR-B transitional workflow and lane consumers

### I392-D-011 — S60 exact current-gate repair

S60 exact owned paths include:

```text
.github/workflows/provider-ci.yml
tests/unit/test_provider_test_lanes.py
tests/conftest.py                                # stale required-fast/node refs only
full-regression-ledger.json                      # zero active, all terminal
full-regression-timing-weights.json              # deleted node refs only
```

The workflow remains `Provider CI` on `pull_request` with job IDs `provider-tests` and `provider-distribution-parity`、same matrix/setup/checkouts。Only test commands are mapped to already-existing successor paths specified in I392-RQ-020。No artifact build-once、aggregate gate、environment descriptor、required-context redesign is introduced in S60。

`tests/unit/test_provider_test_lanes.py` keeps current policy imports until S70 but removes all old distribution/test_init_update constants。It owns three exact S60 assertions:

1. `test_s60_full_regression_ledger_has_zero_active_rows`: no `lifecycle=active` row。
2. `test_s60_terminal_rows_are_resolved_by_collected_current_or_successor_nodes`: every row resolved/fixed-in-place or resolved/superseded; successor collected/passing; old superseded node absent。
3. `test_s60_provider_ci_references_only_existing_successor_tests`: all workflow test paths exist/collect; the three deleted paths and other missing paths are absent。

For accepted contract retirement, `tests/unit/infra/test_provider_test_ownership.py` creates unique passing absence-proof nodes using `pytest.param(id=f"retire-{sha256(old_nodeid.encode()).hexdigest()[:12]}")`; ledger maps the old row to that exact collected successor。This satisfies the current evaluator without adding retirement-evidence transport。

`tests/unit/test_full_regression_baseline.py` remains unchanged except mechanical import formatting if needed and continues validating the temporary provider module。Current ordinary、workflow-equivalent、and main-push verifier commands all pass before PR-B merge。

## 12. PR-C consumer-first gate replacement

### I392-D-012 — Exact S70 consumer retirement set

S70 creates final provider gate/environment/workflow/AGENTS and replacement tests first。Then it retires/replaces these exact current-policy consumers before provider deletion:

```text
tests/unit/test_provider_test_lanes.py            # delete; final policy absence -> provider gate tests
tests/unit/test_full_regression_baseline.py       # delete; baseline provider retired
.github/workflows/provider-ci.yml                 # rewrite transitional commands to final topology
.github/workflows/provider-full-regression.yml    # delete after final PR workflow is GREEN
AGENTS.md                                         # rewrite old operator policy
pyproject.toml                                    # remove fast/full marker declarations
Makefile                                          # replace old commands if present
scripts/static_analysis/run.sh                    # include final tooling, remove old refs
```

Provider/data deletions occur only after those consumers/callsites are closed:

```text
tests/conftest.py
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py if empty
full-regression-ledger.json
full-regression-timing-weights.json
fast/full decorators/options/helpers
```

Before deleting providers, run exact consumer inventory over `.github scripts tests AGENTS.md Makefile pyproject.toml full-regression-*.json` for `tests.conftest`、`scripts.quality.full_regression_baseline`、`scripts.quality.verify_full_regression`、`--run-full-regression`、`--full-regression-shard`、`--full-regression-observation`、`POLICY_SKIP_REASON`、ledger/timing paths。After the two unit consumers and other callsites are deleted/replaced, only the provider files scheduled for deletion may match。Then delete providers and prove `importlib.util.find_spec(...) is None`、ordinary collection succeeds with no legacy options、final workflow references only existing final tools/tests。

### I392-D-013 — Provider gate subcommands and environment

`freeze-linux-environment`、`build`、`verify-artifact`、`verify-environment`、`verify-node-ownership`、`canonical`、`macos-delta`、`qualify`、`summarize`、`emit-attestation`。Build calls one `uv build`。Canonical launches one pytest child/no xdist。Environment ID `specdock-linux-qualification-v1`; runner label、x86_64、base ref/digest、2 CPU、8 GiB、Python series、exact uv、lock hash; all run fingerprints exact。

S70 is non-main。S80 is the only PR-C merge gate and must prove final provider workflow GREEN independently from the PR-B transitional workflow evidence。

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
| RQ-020〜023 | D-011〜013（S60 workflow/lane closure、S70 consumer-first replacement、final gate） |
| RQ-024 | required context |
| RQ-025〜026 | D-015、root AGENTS |

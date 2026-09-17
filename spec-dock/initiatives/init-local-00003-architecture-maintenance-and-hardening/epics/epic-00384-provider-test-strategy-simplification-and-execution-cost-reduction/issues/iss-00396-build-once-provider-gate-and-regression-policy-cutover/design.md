---
種別: 設計書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
詳細化状態: "implementation-ready-candidate"
最終更新: "2026-09-17"
依存:
  - "requirement.md"
  - "../../requirement.md"
  - "../../design.md"
  - "../../artifacts/active-failure-disposition-register.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../artifacts/epic-integration-branch-contract.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
owner_decisions_required: []
human_merge_only: true
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00396-build-once-provider-gate-and-regression-policy-cutover"
  sha: "fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d"
  tree: "37eabc1aa250838dcd9f61d627309b0ff27e0db7"
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 設計

## 1. Design conclusion

Targetは、workflow YAMLへ閾値やhistory logicを埋め込む構成ではなく、次の五層へ分けたprovider-gateである。

1. **Parent policy projection** — Epic Requirementの`E384-QUAL-001`からmechanical constants/predicate IDsだけを生成する。
2. **Candidate and environment identity** — source SHA/tree、provider candidate digest、wheel/sdist actual bytes、environment fingerprintをfreezeする。
3. **One-attempt role graph** — build producerまたはstored artifact resolver、static analysis、Linux canonical、sdist smoke、macOS delta、attempt evaluatorを一回ずつ実行する。
4. **History and qualification evaluator** — GitHub workflow run chronologyからfirst five、seeded-fault、latest twentyを選択なしで評価する。
5. **Consumer-first cutover** — replacementがGREEN、old consumerが0になった後に旧policy provider/data/workflowを削除し、final sourceで再実行する。

Workflowはorchestratorでありpolicy authorityではない。Python modulesはparent-generated projectionをconsumeし、raw evidenceからpure resultを作る。External ruleset/required-context mutationはhuman-onlyで、repository codeはread-only captureとreceipt generationだけを行う。

## 2. Verified current repository surface

### 2.1 Transitional workflow and policy

| Existing path / symbol | Current responsibility | #396 disposition |
|---|---|---|
| `.github/workflows/provider-ci.yml` / workflow `Provider CI` | PR上で`provider-tests`とUbuntu/macOS matrixの`provider-distribution-parity`を実行 | MODIFY。replacement final-gate orchestrationへ置換。old job/commandはconsumer-zero後に除去。 |
| `.github/workflows/provider-full-regression.yml` / workflow `Provider Full Regression` | main push / manualで4-shard verifierを実行 | DELETE。replacement + consumer-zero後。 |
| `.github/workflows/ci.yml` | installed consumer workspace validation | RETAIN / no-touch。 |
| `src/spec_dock/assets/install_root/.github/workflows/ci.yml` | 上記consumer workflowのprovider-side shipped authority | RETAIN / no-touch。root copyとのbyte equalityをguard。 |
| `tests/conftest.py::pytest_addoption` | old `--run-full-regression` / shard / observation options | RETIRE。 |
| `tests/conftest.py::pytest_collection_modifyitems` | `fast`/`full_regression` dynamic classification、policy skip、ledger load | RETIRE。 |
| `tests/conftest.py::pytest_sessionfinish` | old ledger evaluation / shard observation | RETIRE。 |
| `tests/conftest.py::build_candidate_observation` | pytest reportからold evaluator inputを構築 | RETIRE。新role observationへ置換。 |
| `scripts/quality/full_regression_baseline.py` | 15-row transitional baseline evaluator | DELETE。parent registerはhistoryとして残す。 |
| `scripts/quality/verify_full_regression.py` | collect + weighted 4-shard + old ledger verify | DELETE。 |
| `full-regression-ledger.json` | 15-row transitional runtime policy data | DELETE。receiptにraw before/resultを保存。 |
| `full-regression-timing-weights.json` | 243-node sharder weights | DELETE。 |
| `pyproject.toml [tool.pytest.ini_options].markers` | old `fast` / `full_regression` markers | MODIFYして削除。`--strict-markers`は維持。 |
| `tests/unit/test_full_regression_baseline.py` | old evaluator unit tests | DELETE after replacement evaluator RED/GREEN。 |
| `tests/unit/test_provider_test_lanes.py` | old authority/sharder/skip/workflow tests | DELETE after nonpolicy regression移設。 |
| `tests/unit/test_provider_test_lanes.py::test_distribution_cutover_reuses_plain_init_only_as_update_or_uninstall_setup` | lifecycle Product regressionでold policy非依存 | MOVE to `tests/cli_runtime/test_distribution_cutover.py` before source file deletion。 |

### 2.2 Candidate/package surfaces

| Existing path / symbol | Use in target |
|---|---|
| `src/spec_dock/provider_lifecycle/candidate.py::capture_packaged_candidate` | provider assetsのcanonical candidate digestをread-only取得。 |
| `src/spec_dock/provider_lifecycle/candidate.py::compute_candidate_digest` | downloaded/installed candidate identity cross-check。 |
| `src/spec_dock/provider_lifecycle/candidate.py::validate_staged_candidate` | package/stage parityのread-only validation。 |
| `src/spec_dock/provider_lifecycle/candidate.py::FIXED_DOMAINS` | four roots/two slotsのcurrent inventory。変更しない。 |
| `tests/integration/test_epic_00343_distribution.py::CandidateWheel` | wheel/sdist consumer fixture。final gateではstored artifactをconsumeするよう改修。 |
| `tests/integration/test_epic_00343_distribution.py::candidate_wheel` | 現在はmodule fixture内でbuild。final gate時はmanifest/envからloadし、rebuildを禁止。local-only fallbackはqualification evidenceから明確に隔離。 |
| `test_tc_346_s01_001_candidate_wheel_receipt` | wheel actual bytes/one wheelの既存proof。reuse。 |
| `test_tc_360_s80_wheel_and_sdist_catalog_bytes_and_modes_match_provider` | source/wheel/sdist asset parity。sdist roleへ所有。 |
| `pyproject.toml [tool.setuptools.package-data]` | package-data authority。変更が必要な場合のみ最小修正。 |

### 2.3 B2 proof surfaces

- Root ledgerはschema 2、15 rows全てresolved、active/retired 0である。
- Timing blobは243 entriesを持つ。
- Current full verifierは2214 collectedを4 shardへ分割し、B2 resultは15/0/15、violations 0である。
- これらはold policy retirementのbefore-stateであり、target runtime policyへ移植しない。

## 3. Target module topology

### 3.1 New provider-gate package

| Status | Exact path | Planned symbols / responsibility |
|---|---|---|
| NEW | `scripts/quality/provider_gate/__init__.py` | public versionとclosed exportsのみ。 |
| NEW | `scripts/quality/provider_gate/contracts.py` | frozen dataclasses/enums: `CandidateManifest`, `EnvironmentFingerprint`, `AttemptRegistration`, `RoleResult`, `ProcessMeasurement`, `AttemptResult`, `CampaignResult`, `StabilityWindowResult`, `FaultCampaignResult`, `QualificationResult`, `EvidenceIndex`。 |
| NEW | `scripts/quality/provider_gate/codec.py` | strict JSON parse/serialize、unknown/missing/duplicate field拒否、canonical UTF-8 one-LF。 |
| NEW | `scripts/quality/provider_gate/identity.py` | `RepositoryIdentity`, `resolve_repository_identity`, `build_attempt_id`, `build_campaign_id`, `build_window_contract_id`, SHA/tree/API binding。 |
| NEW | `scripts/quality/provider_gate/artifacts.py` | `build_candidate_manifest`, `verify_candidate_bundle`, `resolve_producer_artifact`, `hash_file`, safe archive inventory。 |
| NEW | `scripts/quality/provider_gate/environment.py` | `capture_environment`, `validate_environment_contract`, `fingerprint_environment`, effective CPU/memory/filesystem/image proof。 |
| NEW | `scripts/quality/provider_gate/process_tree.py` | `LinuxCgroupV2Collector`, `ProcessMeasurement`, subreaper/cgroup lifecycle、root/descendant CPU/wall/reap。 |
| NEW | `scripts/quality/provider_gate/pytest_plugin.py` | `--provider-gate-role`、role-owned deselection、node execution/skip/duplicate observation。normal pytestではinactive。 |
| NEW | `scripts/quality/provider_gate/history.py` | `AttemptRegistry`, immutable API observations、`select_first_five`, `select_latest_twenty`、rerun/duplicate/cancel/missing handling。 |
| NEW | `scripts/quality/provider_gate/faults.py` | source-controlled catalogue loader、synthetic injector、expected violation matching。 |
| NEW | `scripts/quality/provider_gate/consumer_scan.py` | `scan_old_policy_consumers`、AST/YAML/JSON/text-aware old policy consumer scanner、retained workflow guard。 |
| NEW | `scripts/quality/provider_gate/evaluator.py` | pure per-role/per-attempt/campaign/window/fault/final evaluation。generated parent predicatesだけを使用。 |
| NEW | `scripts/quality/provider_gate/evidence.py` | evidence workspace、index、API/raw hashes、redaction/relative path normalization。 |
| NEW | `scripts/quality/provider_gate/cli.py` | thin argparse dispatch: `validate-contracts`, `build-candidate`, `verify-candidate`, `capture-environment`, `register-attempt`, `run-role`, `evaluate-attempt`, `evaluate-faults`, `evaluate-qualification`, `scan-old-consumers`。 |
| NEW | `scripts/quality/provider_gate/_qualification_policy_generated.py` | parent Requirementから生成。手編集禁止。 |

`cli.py`へbusiness ruleを集約しない。Identity、history、artifact、environment、process、evaluationを独立pure/adapter層へ分け、testがworkflowなしで境界を検証できるようにする。

### 3.2 Source-controlled contracts

| Status | Exact path | Role |
|---|---|---|
| NEW | `scripts/quality/provider_gate/contracts/specdock-linux-qualification-v1.json` | accepted environment instance。初回measurement前に実値freeze。 |
| NEW | `scripts/quality/provider_gate/contracts/role-ownership-v1.json` | Linux canonical / sdist smoke / macOS delta / static analysisのexclusive selector。 |
| NEW | `scripts/quality/provider_gate/contracts/seeded-fault-catalogue-v1.json` | candidate-bound fault denominator。 |
| NEW | `scripts/quality/provider_gate/contracts/old-policy-retirement-v1.json` | current old consumer signatures、deletion paths、historical allowlist、retained workflow paths。 |
| NEW | `scripts/maintenance/generate_provider_qualification_policy.py` | parent Markdownのstable anchorsをparseし、generated projectionをdeterministic生成。 |

Environment JSONのrunner provider/class/image/limitsは本仕様で値を創作しない。implementation preflightで実environmentをread-only観測し、parent capability boundaryを満たす一つのcontract candidateをfreezeする。解決不能ならstopである。

### 3.3 Tests

| Status | Exact path | Scope |
|---|---|---|
| NEW | `tests/unit/provider_gate/test_policy_projection.py` | parent extraction、generated diff、hidden literal防止。 |
| NEW | `tests/unit/provider_gate/test_contracts.py` | closed schemas、goldens、unknown/missing key拒否。 |
| NEW | `tests/unit/provider_gate/test_identity.py` | SHA/tree/manifest/attempt/campaign/window IDs。 |
| NEW | `tests/unit/provider_gate/test_artifacts.py` | one producer、actual bytes、wrong source/hash、expiry/multiple artifact。 |
| NEW | `tests/unit/provider_gate/test_environment.py` | limit proof、fingerprint、drift、GPU/tier/burst/unverifiable rejection。 |
| NEW | `tests/unit/provider_gate/test_process_tree.py` | child-inclusive CPU、descendant leak/reap、second pytest root、wall interval。 |
| NEW | `tests/unit/provider_gate/test_role_ownership.py` | union complete、intersection empty、skip/duplicate 0。 |
| NEW | `tests/unit/provider_gate/test_history.py` | first five、latest twenty、cancel/failure/missing、same-ID rerun。 |
| NEW | `tests/unit/provider_gate/test_fault_catalogue.py` | denominator freeze、all injected、100% detection。 |
| NEW | `tests/unit/provider_gate/test_evaluator.py` | per-attemptとaggregate分離、parent predicate conjunction。 |
| NEW | `tests/unit/provider_gate/test_consumer_inventory.py` | old consumer count、deletion gate、retained workflow。 |
| NEW | `tests/integration/test_provider_gate_role_graph.py` | synthetic/small exact role graph、artifact reuse、evidence index。 |
| NEW | `tests/integration/test_provider_gate_faults.py` | controlled process/artifact/history faults。 |
| MODIFY | `tests/integration/test_epic_00343_distribution.py` | final gateではstored wheel/sdistをconsume。local fallbackをqualification pathから隔離。 |
| MODIFY | `tests/cli_runtime/test_distribution_cutover.py` | nonpolicy regression一件を移設。 |

### 3.4 Workflow and docs

| Status | Exact path | Change |
|---|---|---|
| MODIFY | `.github/workflows/provider-ci.yml` | final-gate jobs、artifact producer resolver、same-candidate consumers、evidence upload。compatibility中はold jobsとnew jobを併存し、final sourceではold jobsを除去。 |
| DELETE | `.github/workflows/provider-full-regression.yml` | consumer-zero後。 |
| MODIFY | `AGENTS.md` | old policy commands/skip/main-push guidanceをfinal gate guidanceへ置換。 |
| NEW | `docs/provider-gate.md` | operator runbook、evidence、failure/rollback。 |
| MODIFY | `pyproject.toml` | old markers削除。新dependency追加はstdlib/既存dependencyで不可能な場合だけ。 |

No planned provider asset/dogfood modificationがdefaultである。`src/spec_dock/assets/**`や`spec-dock/**`へ変更が生じたらscope escalationとしてPlanのdogfood branchへ入り、complete candidate projectionを要求する。

## 4. Parent qualification projection

### 4.1 Why generation is required

Parent値をPython、workflow、JSON、docsへ手で複写すると、Issue #396が第二のpolicy authorityになる。そこでgeneratorはEpic Requirement内のstable heading `#### E384-QUAL-001`とnumbered clausesをparseし、実装に必要なclosed projectionを生成する。

Generated moduleは少なくとも次を持つ。

```python
AUTHORITY_REQUIREMENT_ID = "E384-QUAL-001"
POLICY_SCHEMA_VERSION = 1
GATE_CONTRACT_VERSION = "specdock-provider-gate-v1"
# Numeric and enum projections are generated from the parent requirement.
PREDICATES = (...)
PARENT_SOURCE_SHA256 = "..."
```

Design/Planはpolicy値を独立定義しない。Generated output内の数値はparent textから機械抽出した実装projectionであり、generator testがsource text、predicate IDs、output hashを固定する。

### 4.2 Generator safety

- source pathをexact parent Requirementへ固定。
- section anchor重複/欠落をreject。
- expected clause count/order/semantic tokenが変わればrejectし、silent regenerationしない。
- `--check`はworking tree outputとの差分があればnonzero。
- generated file headerにsource path/hashと「DO NOT EDIT」を記載。
- workflowはnumeric literalを持たず、CLI evaluatorを呼ぶ。

Parent semantic changeが必要なら本Issueを停止し、親ADR/reviewへ戻す。

## 5. Candidate build, provenance and reuse graph

### 5.1 Build count unit

Count unitはcandidate source SHAに対する**top-level packaging process invocation**である。Exact command candidateは次で固定する。

```bash
uv build --sdist --wheel --out-dir "$CANDIDATE_DIR/dist" --clear .
```

この一つのprocessがwheelとsdistを生成する。後続roleは`uv build`、`python -m build`、pipのsdist-to-wheel buildを行わない。sdist smokeはactual sdistをsafe extractし、metadata/assets/source import surfaceを検証する。wheel roleはactual wheelをfresh environmentへinstallする。

### 5.2 Producer selection

Candidate source SHAごとにGitHub Actions workflow run chronologyを読み、次でproducerを一意に決める。

1. target workflow、exact source SHA、`run_attempt=1`のstarted runを列挙。
2. `created_at`, run IDで最初のrunをproducer candidateとする。
3. そのrunがbuild開始前なら、そのrunだけbuildを許可する。
4. producer runがstarted後に失敗/cancel/missing artifactとなった場合、そのsource SHAはbuild-once evidenceとしてrejectedである。後続runは再buildしない。
5. producer artifactがexactly oneで、manifest/bundle hashがAPI metadataと一致する場合だけ後続runがconsumeする。

Workflow rerunによる`run_attempt>1`はproducerにもconsumerにもならず、attempt resultをrejectedとしてhistoryへ残す。

### 5.3 Candidate manifest schema

`candidate-manifest.json` exact fields/order:

1. `schema_version`
2. `gate_contract_version`
3. `repository`
4. `source_sha`
5. `source_tree`
6. `provider_candidate_digest`
7. `build_invocation_id`
8. `build_command`
9. `builder_run_id`
10. `builder_run_attempt`
11. `wheel`
12. `sdist`
13. `manifest_core_sha256`
14. `bundle_sha256`
15. `created_at`

`wheel` / `sdist` exact fields: `filename,size,sha256`。`build_command`は監査用であり、count authorityはbuild invocation ID + process receipt + workflow chronologyである。

Manifestのhashはself-referenceを避けるため、field 1–12のcanonical bytesを`manifest_core_sha256`とし、manifest file全体とdist filesをfilename順に連結したclosed streamを`bundle_sha256`とする。Algorithmは`contracts.py`でversioned、unit goldenで固定する。

### 5.4 Artifact consumer verification

各roleは実行前に次を行う。

- checkout HEAD/source treeをmanifestへ照合。
- downloaded wheel/sdistのactual bytesをrehash。
- archive filename、size、single member expectationを照合。
- provider candidate digestをsource、wheel install、sdist extractionの各surfaceで再計算。
- producer run/artifact IDをrole resultへ記録。
- mismatch時はtest bodyを開始せずrole rejected。

Artifact retentionが短くB3前に失われる可能性がある設定はadmission failureである。retention値はhuman/context captureで確認後に選択する。

## 6. Environment contract and collector seam

### 6.1 Environment schema

`specdock-linux-qualification-v1.json` exact fields/order:

1. `schema_version`
2. `contract_id`
3. `authority_requirement_id`
4. `runner_provider`
5. `runner_class`
6. `architecture`
7. `cpu_model_family`
8. `cpu_quota_cores`
9. `memory_limit_bytes`
10. `os_release`
11. `image_digest`
12. `python_version`
13. `dependency_lock_sha256`
14. `uv_version`
15. `pytest_version`
16. `filesystem_type`
17. `filesystem_mount_options`
18. `cgroup_version`
19. `collector_version`
20. `fingerprint_sha256`

`fingerprint_sha256`はfield 1–19のcanonical bytesから計算する。runner labelだけをprovider/class/image証明にしない。actual effective quota/memory、CPU family、image digestを取得できないならadmission failにする。

### 6.2 Collector interface

```python
class LinuxCgroupV2Collector:
    def prepare(self, contract: EnvironmentContract) -> PreparedMeasurement: ...
    def spawn_pytest(self, argv: tuple[str, ...], env: Mapping[str, str]) -> RootProcess: ...
    def wait_and_reap(self, root: RootProcess) -> ProcessMeasurement: ...
    def abort_and_reap(self, root: RootProcess, reason: str) -> ProcessMeasurement: ...
```

Required observations:

- monotonic spawn-before timestamp、terminal reap-after timestamp。
- cgroup `usage_usec`, `user_usec`, `system_usec` delta。
- root PID、observed descendant PIDs、pytest-root count。
- effective `cpu.max`, `memory.max`、cgroup version。
- root exit status、signal、descendant terminal status。
- `cgroup.events populated=0`とsubreaper `waitpid` completion。
- leak/unknown process list。

CollectorはLinux only。macOS deltaへ同performance predicateを適用しない。

### 6.3 Descendant lifecycle

Process topologyは次で閉じる。

1. Parent processをLinux subreaperとして設定。
2. fresh cgroup/workspaceをowner-boundで作る。
3. effective limitをreadbackし、contract/fingerprintと照合。
4. spawn直前にwall startを取得し、pytest rootをcgroupへ入れる。
5. root and descendantsのCPUをcgroup aggregateで収集。
6. root exit後、descendantが残る間もintervalを継続。
7. Parent wall predicateの上限を超えた場合はcgroup/process groupへterminationを送り、全childをreapし、attempt rejectedを記録。
8. populated=0、waitpid complete、raw stats fsync後にwall end。

別のhidden grace timeoutをacceptance predicateにしない。Infrastructure cancellationでcollector completionが欠けた場合はmissing evidenceとしてnon-acceptedになる。

## 7. Role graph and test ownership

### 7.1 Role graph

```text
candidate-resolve/build
  -> static-analysis
  -> linux-canonical
  -> sdist-smoke
  -> macos-delta
  -> attempt-evaluate
```

Build producer runだけが`build-candidate`を行い、その他は`resolve-producer-artifact`を行う。Role jobsは同じmanifest/bundle digestをneed/outputで渡す。`attempt-evaluate`は全role resultとAPI observationをdownloadし、per-attempt resultを一回だけ構築する。

### 7.2 Linux canonical

Candidate environment setup:

```bash
uv sync --frozen --no-install-project
uv pip install --python .venv/bin/python --no-deps "$WHEEL_PATH"
```

その後、collectorがexactly one pytest rootを起動する。

```bash
.venv/bin/python -m pytest -q --tb=short \
  -p scripts.quality.provider_gate.pytest_plugin \
  --provider-gate-role linux-canonical \
  --provider-gate-observation "$ROLE_EVIDENCE/node-observation.json"
```

Pluginはrole ownership contractによりowned nodeだけをexecuteし、他role ownerをdeselectする。Policy skip、approved failure、duplicate node、unexpected failureを別countで記録する。Worker追加、`-n`、shard option、二つ目のpytest rootをrejectする。

### 7.3 sdist smoke

sdist roleはpackaging buildを行わない。

- actual sdist bytes/hashをmanifestへ照合。
- safe extract（absolute/`..`/symlink escape/special member rejection）。
- `PKG-INFO`/`pyproject.toml` identity、source SHA receipt、provider assets inventory/modesを検証。
- extracted `src`からisolated import probeを行う。
- wheel/sdist/sourceのprovider asset manifest equalityを検証。
- package build backendを再起動しない。

Existing `test_tc_360_s80_wheel_and_sdist_catalog_bytes_and_modes_match_provider`等をこのroleがconsumeする。必要ならtest fileを分けるがbehavior assertionは弱めない。

### 7.4 macOS delta

macOS roleはLinux canonicalと同じwheel bytesをinstallし、source-controlled role ownership contractに割り当てたplatform-specific boundariesだけを実行する。Current evidence上のcandidate selectorsは次である。

- `tests/cli_runtime/test_provider_lifecycle_bootstrap.py`
- `tests/cli_runtime/test_provider_lifecycle_handoff.py`
- `tests/cli_runtime/test_generation_checkout.py`
- `tests/cli_runtime/test_worktree_lifecycle_coordination.py`
- `tests/unit/provider_lifecycle/test_atomic_filesystem.py`のmacOS native cases

Exact node/path setはimplementation時にcollection readbackを行い、role contractへfreezeする。macOS deltaへLinux wall/CPU predicateを追加しない。Role absence、wrong wheel、unexpected failure、policy skip、duplicate executionはattempt rejectionになる。

### 7.5 static analysis

`make lint`を一回実行し、Ruff check/formatとmypyをone role resultへ記録する。static analysisはpytest node ownershipに含めず、role graphの独立conjunctとする。

### 7.6 Ordinary local development

Qualification workflow以外の`uv run pytest`はdeveloper convenienceであり、B3 evidenceではない。`tests/integration/test_epic_00343_distribution.py::candidate_wheel`は次の二modeを明示する。

- `qualification-artifact` mode: manifest/paths必須、rebuild禁止。
- `local-test-build` mode: local focused testのためだけにbuild可能。evidenceへ`qualification_eligible=false`を記録し、workflow final gateから到達不能にする。

Consumer scannerとworkflow testsはfinal gateがlocal fallbackを参照しないことをmechanically証明する。

## 8. Evidence schemas and separation of results

### 8.1 Attempt registration

`attempt-registration.json` exact fields/order:

1. `schema_version`
2. `attempt_id`
3. `repository_id`
4. `workflow_id`
5. `workflow_run_id`
6. `run_attempt`
7. `created_at`
8. `event_name`
9. `source_sha`
10. `source_tree`
11. `candidate_manifest_sha256`
12. `environment_fingerprint_sha256`
13. `gate_contract_version`
14. `campaign_id`
15. `window_contract_id`
16. `registration_status`

`registration_status`は`registered|rejected-rerun|rejected-identity`。Started runはAPI historyに存在した時点でmember candidateとなり、artifactが無くても消さない。

### 8.2 Role result

`role-result.json` exact fields/order:

1. `schema_version`
2. `attempt_id`
3. `role_id`
4. `candidate_manifest_sha256`
5. `candidate_bundle_sha256`
6. `environment_fingerprint_sha256`
7. `started_at`
8. `completed_at`
9. `status`
10. `command`
11. `exit_code`
12. `node_observation_sha256`
13. `process_measurement_sha256`
14. `unexpected_failures`
15. `approved_failures`
16. `policy_skips`
17. `duplicate_executions`
18. `errors`

Closed `status`: `successful|failed|cancelled|interrupted|missing-evidence|rejected`。

### 8.3 Process measurement

`process-metrics.json` exact fields/order:

1. `schema_version`
2. `attempt_id`
3. `role_id`
4. `collector_version`
5. `root_pid`
6. `pytest_root_count`
7. `descendant_pids`
8. `started_monotonic_ns`
9. `reaped_monotonic_ns`
10. `elapsed_wall_ns`
11. `cpu_user_usec`
12. `cpu_system_usec`
13. `cpu_total_usec`
14. `cpu_wall_ratio_decimal`
15. `effective_cpu_quota`
16. `effective_memory_limit_bytes`
17. `all_descendants_reaped`
18. `cgroup_populated_zero`
19. `root_exit_code`
20. `termination_reason`

Ratioはraw integer inputsからDecimalで計算し、display roundingをacceptanceに使わない。

### 8.4 Per-attempt result

`attempt-result.json`は全roleのconjunctionとidentity/raw completenessを判定する。Five-run population、fault campaign、rolling twentyの不足をper-attempt statusへ戻さない。

Exact fields/order:

1. `schema_version`
2. `attempt_id`
3. `candidate_identity`
4. `environment_fingerprint_sha256`
5. `gate_contract_version`
6. `role_results`
7. `identity_complete`
8. `raw_evidence_complete`
9. `linux_predicates`
10. `correctness_predicates`
11. `rerun_detected`
12. `status`
13. `accepted`
14. `violations`

### 8.5 Aggregate results

- `campaign-result.json`: frozen identity、chronological first five IDs、各member result、population completeness、independent conjunction。
- `fault-campaign-result.json`: catalogue digest、candidate identity、denominator、executed IDs、detected IDs、misses、100% result。
- `stability-window-result.json`: window identity、latest twenty IDs、window completeness、failed/nonaccepted/missing members、retry/rerun count。
- `qualification-result.json`: current candidate campaign + fault campaign + stability window + required-context/protected-data/consumer-zero evidenceのfinal conjunction。per-attemptへ循環参照しない。

## 9. Chronology, cancellation and missing evidence

### 9.1 Source of chronology

GitHub Actions workflow run APIをauthoritative chronological indexとして用いる。Artifact directoryのmtime、job completion time、result filename順は使わない。Order keyは`created_at`、同値時はnumeric run IDである。

### 9.2 Started but incomplete runs

APIにrunが現れた後の次をmemberとして残す。

- `failure`
- `cancelled`
- `timed_out`
- `action_required`
- `stale`
- `startup_failure`
- completedだがartifact missing
- role result missing
- identity/raw mismatch

Aggregatorはmissing resultをsynthetic successfulへ変換せず、`missing-evidence` non-accepted memberを作る。

### 9.3 Same-ID and rerun

- workflow run IDが同じで`run_attempt>1`ならrerun。
- duplicate `attempt_id` artifactが二つならidentity violation。
- API runが一つでartifact replacement/updateが観測されたらmutable evidence violation。
- `workflow_dispatch`による新run IDは独立attemptとして許可されるが、first-five/window membershipはchronologyが決める。

Campaign IDを変えて不都合なfirst fiveを捨てることは、deterministic identity conflictとしてrejectする。

## 10. Seeded-fault catalogue

Catalogue entry exact fields:

1. `fault_id`
2. `category`
3. `fixture`
4. `injector`
5. `expected_violation_code`
6. `expected_detection_stage`
7. `candidate_bound`

Initial catalogueには少なくとも次を含める。

| Fault category | Required detection |
|---|---|
| manifest missing / malformed / duplicate key | artifact admission reject |
| source SHA/tree mismatch | identity reject |
| wheel/sdist bytes or size mismatch | actual-byte reject |
| multiple producer artifacts | producer ambiguity reject |
| producer missing/cancelled/expired | candidate rejected, no rebuild |
| environment fingerprint drift | environment reject |
| effective CPU/memory limit unprovable or out-of-bound | environment admission reject |
| GPU/high-tier/burst drift signal | environment reject |
| extra pytest root / worker / shard option | topology reject |
| descendant leak or incomplete reap | process evidence reject |
| synthetic wall or CPU predicate breach | per-attempt reject |
| policy skip / approved failure / duplicate node | correctness reject |
| missing role or raw evidence | attempt reject |
| same run rerun / same attempt ID | history reject |
| cancelled/failed started attempt | member retained and nonaccepted |
| first-five replacement attempt | campaign reject |
| latest-twenty success filter/replacement | window reject |
| catalogue denominator reduction/unexecuted entry | fault campaign reject |
| old consumer remaining | retirement block |
| retained install-root workflow deletion/mismatch | protected workflow reject |

Fault injectionはproduction workflowへfree-form debug flagを残さず、test fixture/object adapter境界に限定する。

## 11. Consumer-first cutover design

### 11.1 Old consumer inventory

`old-policy-retirement-v1.json`は以下を分類する。

- production/runtime consumer
- workflow consumer
- test consumer
- data provider
- historical reference allowlist
- retained installed-consumer workflow

ScannerはPython AST import/name/call/constants、workflow YAML `run`/job/path、JSON path references、current operational docsを読む。`rg` outputだけをproofにしない。Historical parent contractsやreceiptはold namesを説明できるが、runtime consumer countには含めない。

### 11.2 Sequence

1. replacement contracts/tests/moduleをRED→GREEN。
2. replacement workflowをold workflow/jobsとshadow coexistence。
3. new attempt result/evidenceを取得。
4. required-context new RED/GREENをhuman canary。
5. 全old consumerをreplacementへ移す。
6. scannerでconsumer count 0。
7. old data/provider/workflow/tests/markersを削除。
8. final sourceでscanner、unit、integration、role graph、lint、protected workflow guardを再実行。
9. old contextをhumanが除去しfinal readback。

同一PR内のcheckpointは許すが、consumer-zero前のdeletion commitやold/new partial stateをmergeable/acceptedとしない。

### 11.3 Nonpolicy test preservation

`test_distribution_cutover_reuses_plain_init_only_as_update_or_uninstall_setup`はold policy test file削除前に`tests/cli_runtime/test_distribution_cutover.py`へ移し、node behaviorを維持する。Old evaluator/sharder/skip internalsだけを検証するtestsはreplacement tests成立後に削除する。

## 12. Workflow design and external permissions

### 12.1 Repository workflow permissions

Target workflowは原則次のread permissionsだけを持つ。

```yaml
permissions:
  contents: read
  actions: read
  checks: read
  pull-requests: read
```

Repository/org policyが`checks: read`等を許さない、または不要な場合は実際のAPI callに基づき最小化する。`contents: write`、`actions: write`、`administration: write`を要求しない。Artifact upload自体に追加write scopeを仮定しない。

### 12.2 Trigger and attempts

- PR required context: normal per-attempt result。
- `workflow_dispatch`: independent qualification attempt。same run rerunは禁止。
- Candidate producer: exact SHAのfirst started accepted run。
- main push automatic Full Regressionは削除し、B3 campaignはhuman-controlled independent dispatchesで実行する。

Workflow cancellation policyはstarted attemptを置換しない。`cancel-in-progress: true`をqualification attemptsへ使わない。Concurrencyは同じcandidateのsimultaneous producer raceを防ぐためserializeできるが、wait/cancelしたrunのchronology/evidenceを隠さない。

### 12.3 External context capture

Implementation前に次をread-only captureする。

- current branch/ruleset effective required contexts。
- check suite/job names on a representative PR。
- merge queue / merge_group usage。
- unrelated required contexts `U`。
- review requirements、dismissal/approval settingsの範囲。

GitHub App connectorがadministration permission不足でrulesetを読めない場合、それをpermission failureと断定せず「connectorで未確認」と記録し、humanによるUI/`gh api` read-only exportをrequireする。Exact external context nameはこのcaptureから選び、本仕様では創作しない。

### 12.4 No-gap migration

```text
U + old
  -> U + old + new
  -> intentional new RED: U + old GREEN / new RED / merge blocked
  -> new GREEN
  -> U + new
  -> final readback
```

Merge queueがactiveならPR headとmerge_groupを別々にcanaryする。Settings rollbackはcaptureされた`U + old`を復元する。Agentはsettings mutationを行わない。

## 13. Documentation, dogfood and protection

### 13.1 Root guidance

`AGENTS.md`のBuild/Test sectionは次へ更新する。

- ordinary local pytestとqualification evidenceの区別。
- final provider gate CLI / workflowの入口。
- build-once artifact rule。
- no rerun/retry/shard/skip。
- failure時のnew source SHA rule。
- human merge/settings boundary。

`docs/provider-gate.md`はschema、evidence、operator steps、rollbackを説明する。

### 13.2 Dogfood rule

Planned changesはroot provider workflow/scripts/tests/docsで、packaged provider assetsを変更しない。従ってdefaultでは`spec-dock update .`を実行せず、provider candidate digestがB2から不変であることを記録する。

実装中に`src/spec_dock/assets/**`へ必要変更が発見された場合は、次のstop/branchを適用する。

1. reasonとparent ownership impactを記録。
2. lifecycle wire/consumer workflow変更なら即parent stop。
3. #396-owned shipped guidanceだけであればprovider source first。
4. complete candidate after testsで`spec-dock update .`。
5. generated dogfood diffとcandidate digestを証拠化。

Partial provider/dogfood projectionをmergeしない。

### 13.3 Protected snapshot

Before/after snapshot対象:

- `spec-dock/initiatives`
- `spec-dock/active`
- `spec-dock/.agent`
- `spec-dock/diagrams`
- `spec-dock/.workbench`の既存user payload（evidence workspace新規分を除外して識別）
- unrelated `.agents/skills`
- consumer seeds

Snapshotはpath、type、mode、size、SHA-256（regular files）を記録し、private absolute pathをevidenceへ出さない。

## 14. Failure, recovery and rollback

### 14.1 Candidate poisoning

次のいずれかでsame source SHA candidateはqualification不可になる。

- first build producer失敗/cancel/artifact missing。
- first five member不合格。
- candidate/environment identity mismatch。
- rerun/retry。
- fault catalogue miss。

同じSHAでcampaign IDを変える、artifactを再buildする、runをrerunすることは禁止。Fix commitでnew source SHA/treeを作り、新candidateとして最初から進む。

### 14.2 External settings failure

Canaryがblockしない、contextがpending、unrelated context drift、merge queue scope不明の場合、humanがcaptured before-stateへ戻し、PR mergeを停止する。Repository codeをold policyへpartial fallbackしない。

### 14.3 Issue merge rollback

- pre-merge: Issue branchを修正/abandon。integration branch不変。
- merged、Epic main未merge: human whole-merge revert。必要ならsettingsをbefore-stateへ戻し、B2 current-policy files/workflow/dataをcompleteに復元してB1/B2を再検証。
- Epic main merge後: automatic revertしない。parent ownerがsuffix reverse-revertまたは#396 boundary内forward-fixを判断。

Partial ledger-only、workflow-only、context-only rollbackはaccepted stateにならない。

## 15. Requirement-to-design traceability

| Requirement | Design section |
|---|---|
| I396-RQ-001 | §2, §8.1, §12.3 |
| I396-RQ-002 | §4 |
| I396-RQ-003–004 | §5 |
| I396-RQ-005–006 | §7 |
| I396-RQ-007 | §6.2–6.3 |
| I396-RQ-008 | §6.1 |
| I396-RQ-009–013 | §8–10 |
| I396-RQ-014 | §8, §12 |
| I396-RQ-015–016 | §11 |
| I396-RQ-017 | §12 |
| I396-RQ-018 | §13 |
| I396-RQ-019–020 | §14 and Plan review/merge phases |

## 16. Unresolved operational captures, not owner decisions

`owner_decisions_required=[]`である。ただし次はimplementation時にactual repository/environmentから取得するoperational factsであり、未取得のまま推測して進めない。

1. exact runner provider/class/image digest、effective CPU/memory limit、filesystem。
2. current Actions artifact retention policyとchosen retention。
3. effective required-context names、ruleset scope、merge queue state。
4. exact check-run/job names emitted by replacement workflow。
5. human canary/rollback receipt location。

これらがparent capability/no-gap contract内で一意に確定できればProduct/Policy decisionではない。複数のsemantic optionが残る、parent値を変える必要がある、admin boundaryが閉じない場合はparent stopへ昇格する。

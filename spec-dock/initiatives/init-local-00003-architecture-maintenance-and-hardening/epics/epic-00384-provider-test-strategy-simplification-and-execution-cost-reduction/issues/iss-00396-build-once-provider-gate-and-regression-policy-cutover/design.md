---
種別: 設計書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
詳細化状態: "implementation-ready-candidate"
最終更新: "2026-09-18"
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
| NEW | `scripts/quality/provider_gate/contracts.py` | frozen dataclasses/enums for every `$defs` artifact in `provider-gate-contracts-v1.schema.json`; JSON Schema shape validation and semantic invariant validation。 |
| NEW | `scripts/quality/provider_gate/codec.py` | schema-bound parse/serialize、unknown/missing/duplicate field拒否、schema key orderのcanonical UTF-8 one-LF。 |
| NEW | `scripts/quality/provider_gate/identity.py` | `RepositoryIdentity`, event-aware `resolve_source_identity`, `build_attempt_id`, `build_campaign_id`, `build_window_contract_id`, SHA/tree/API binding。 |
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
| SPEC ARTIFACT | `artifacts/provider-gate-contracts-v1.schema.json` | all runtime, evidence, ownership, snapshot, execution-packet and stop-return wire shapes; implementation copy must be byte-identical and checked against this artifact。 |
| SPEC ARTIFACT | `artifacts/role-ownership-v1.json` | exact 2,214-node Linux/macOS baseline assignment and collection provenance for P07。 |
| SPEC ARTIFACT | `artifacts/20260917t164244z--linux-collect-only-nodeids.txt` | raw Linux collection output referenced by the ownership contract。 |
| SPEC ARTIFACT | `artifacts/20260917t164244z-01--macos-collect-only-nodeids.txt` | raw macOS collection output referenced by the ownership contract。The suffix disambiguates the SpecDock artifact timestamp slot; raw bytes and SHA-256 are unchanged。 |
| SPEC ARTIFACT | `artifacts/capture_protected_snapshot.py` | reviewed P03/P16 helper; Plan binds its exact SHA-256。 |
| SPEC ARTIFACT | `artifacts/20260917t124918z-01--b1-b2-gate-receipt.md` | #395 post-merge B1/B2 entry receipt; proves entry qualification only。 |
| SPEC ARTIFACT | `artifacts/20260917t124918z-02--iss-00395-b2-full-regression-result.json` | immutable raw B2 verifier result; Plan binds exact SHA-256。 |
| SPEC ARTIFACT | `artifacts/20260917t124919z--iss-00395-b2-ledger-before.json` | immutable pre-B2 ledger snapshot; Plan binds exact SHA-256。 |
| SPEC ARTIFACT | `artifacts/20260917t124918z--luna-max-implementation-handoff.md` | implementation handoff subordinate to canonical Requirement/Design/Plan and shared wire schema。 |
| SPEC ARTIFACT | `artifacts/20260917t162312z-strict-review-remediation-analysis.md` | Blue analysis of initial Red P1 findings and verified corrections; advisory to the canonical specs。 |
| SPEC ARTIFACT | `artifacts/issue-396-implementation-readiness.html` | self-contained Japanese human guide; explanatory only and subordinate to canonical specs/schema。 |
| SPEC ARTIFACT | `artifacts/issue-396-specification-pack.zip` | downloadable archive of canonical specs and supporting artifacts; `manifest.sha256` binds archive members。 |
| NEW | `scripts/quality/provider_gate/contracts/specdock-linux-qualification-v1.json` | accepted environment instance。初回measurement前に実値freeze。 |
| NEW | `scripts/quality/provider_gate/contracts/provider-gate-contracts-v1.schema.json` | Issue schema artifactのbyte-identical runtime copy。 |
| NEW | `scripts/quality/provider_gate/contracts/role-ownership-v1.json` | Linux canonical / sdist smoke / macOS deltaのpytest node exclusive selector。Static analysisはpytest node ownership外。 |
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

`artifacts/provider-gate-contracts-v1.schema.json#/$defs/CandidateManifestV1`が唯一のshape authorityである。Runtime copy `scripts/quality/provider_gate/contracts/provider-gate-contracts-v1.schema.json`はIssue Artifactとbyte-identicalで、schema equality testで検査する。`candidate-manifest.json`のexact fields/order:

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

Hash graphはmanifestへの自己参照を含めず、次のbyte algorithmで固定する。Canonical JSONはUTF-8、BOMなし、schema `x-key-order`順、空白なし、non-ASCIIを直接UTF-8化、NaN/Infinityなし、末尾LF一つとする。

1. `core_json`はfield 1–12のみを`CandidateManifestV1`のkey orderでserializeしたcanonical JSON bytes。
2. `manifest_core_sha256 = SHA256(ASCII("spec-dock.provider-gate.manifest-core.v1") || 0x00 || uint64_be(len(core_json)) || core_json)`。
3. wheelとsdistをfilename UTF-8 bytesの昇順に並べる。各artifact metadataは`filename,size,sha256`のcanonical JSON bytesとし、recordを`uint64_be(name_len) || name_utf8 || uint64_be(metadata_len) || metadata_json || uint64_be(actual_len) || actual_bytes`として順に連結する。
4. `bundle_sha256 = SHA256(ASCII("spec-dock.provider-gate.bundle.v1") || 0x00 || raw32(manifest_core_sha256) || records)`。実際のwheel/sdist bytesを必ず含める。
5. field 1–15全体をcanonical JSON plus one LFとして出力した後、その完成ファイルの`candidate_manifest_sha256`を計算し、EvidenceIndex／producer receipt／CandidateIdentityにだけ保存する。これはManifest内にもhash inputにも含めない。

Runtimeはunknown/missing/duplicate key、順序・canonical-byte不一致、filename重複、manifest/actual bytes/API metadata不一致を拒否する。`CandidateIdentityV1`にはsource SHA/tree、provider digest、core hash、完成manifest hash、bundle hash、wheel/sdist hashesを束縛する。Algorithmはschema artifactと`codec.py`でversionedにし、unit goldenで全中間/最終digestを固定する。

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

`specdock-linux-qualification-v1.json`は`artifacts/provider-gate-contracts-v1.schema.json#/$defs/EnvironmentFingerprintV1`に適合する、`role_id=linux-canonical` / `operating_system=linux`のaccepted environment instanceである。Runtime copyはIssue schema artifactとbyte-identicalにする。Schemaの20 required fields、key order、enum、nullable、conditional ruleが唯一のshape authorityである。`fingerprint_sha256`はfields 1–19のcanonical JSON bytesから計算する。

`cpu_quota_cores`はbinary floatでなく、正値のcanonical decimal string（例: `"2"`, `"0.5"`）で記録する。Nullはfield omissionと同義ではなく、schemaがnullableとするrole/environment propertyにだけ使う。Linux canonicalのprovider/class/OS/architecture/CPU family/effective quota/memory/image/Python/dependency lock/tool/filesystem/cgroup/collectorの必須値にnullやplaceholderを使わない。Runner labelだけでprovider/class/imageを証明せず、P02で観測した実値が親`E384-QUAL-001`の能力境界を満たさなければadmission failにする。Static, sdist, macOS roleはそれぞれ実際のrole環境を`EnvironmentFingerprintV1`で記録する。

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

Initial ownership contractは、`tests/integration/test_epic_00343_distribution.py::test_tc_360_s80_wheel_and_sdist_catalog_bytes_and_modes_match_provider`の1 nodeだけをこのroleへ割り当てる。追加・移動するtest nodeはcollection-only diffで特定し、role contractへ明示登録してから実行する。必要ならtest fileを分けるがbehavior assertionは弱めない。

### 7.4 macOS delta

macOS roleはLinux canonicalと同じwheel bytesをinstallし、`artifacts/role-ownership-v1.json`でmacOS ownerに固定されたexact 22 nodesだけを実行する。これは4 parity files内の21 nodesと、`tests/unit/infra/test_binary_artifact_publisher.py::test_macos_explicit_publication_probes_no_replace_capability_before_formal_commit`の1 native nodeから成る。`tests/unit/provider_lifecycle/test_atomic_filesystem.py::test_t05_current_host_executes_only_its_native_adapter`はbaseline上Linux ownerである。初期macOS collection raw outputとnormalized set hashは同Artifact契約が参照する。node setを実装時に推定し直したり旧markerからownerを導出しない。macOS deltaへLinux wall/CPU predicateを追加しない。Role absence、wrong wheel、unexpected failure、policy skip、duplicate executionはattempt rejectionになる。

### 7.5 static analysis

`make lint`を一回実行し、Ruff check/formatとmypyをone role resultへ記録する。static analysisはpytest node ownershipに含めず、role graphの独立conjunctとする。

### 7.6 Ordinary local development

Qualification workflow以外の`uv run pytest`はdeveloper convenienceであり、B3 evidenceではない。`tests/integration/test_epic_00343_distribution.py::candidate_wheel`は次の二modeを明示する。

- `qualification-artifact` mode: manifest/paths必須、rebuild禁止。
- `local-test-build` mode: local focused testのためだけにbuild可能。evidenceへ`qualification_eligible=false`を記録し、workflow final gateから到達不能にする。

Consumer scannerとworkflow testsはfinal gateがlocal fallbackを参照しないことをmechanically証明する。

### 7.7 Transition seam for the existing pytest policy hook

P07では`tests/conftest.py::pytest_collection_modifyitems`の最初に次のexclusive branchを置く。`--provider-gate-role`がない通常・従来実行は現行classification/skip/ledger behaviorを通る。role optionがある場合はCLIが`-p scripts.quality.provider_gate.pytest_plugin`でpluginを先に登録し、root conftestがplugin managerからこのexact moduleをrequireする。Root conftestは`prepare_role_collection(config, items)`を一度だけ呼び、role contract schema、contractと全collected nodeの集合一致、owner一意性、role/environment適合を検証してowned subsetを確定する。collection filterはこのhelperだけが行い、plugin自身は二重filter hookを登録しない。正常終了後は旧hookをbypassし、エラー時はpytest collectionを失敗させtest bodyを開始しない。Role modeと`--run-full-regression`、`--full-regression-shard`、`--full-regression-observation`の併用はUsageErrorでrejectする。

このentryはroot conftestのlegacy skip marker付与より先にrole selectionを完了する。これによりlegacy `POLICY_SKIP_REASON`が新role-owned nodeへ残らない。Plugin不在・option不在・contract不正の経路にbypass fallbackを設けない。P14 consumer-zero後、P15で旧classification/hookとtransition seamを一括削除する。通常`pytest`と旧laneの互換性はP07 focused testsで、role modeのskip 0・deselect・unknown-node failはplugin testsで検証する。

## 8. Evidence schemas and separation of results

`artifacts/provider-gate-contracts-v1.schema.json`はIssue #396が生成する全wire artifactの唯一のclosed shape authorityである。Implementationはそのbyte-identical copyを`scripts/quality/provider_gate/contracts/provider-gate-contracts-v1.schema.json`へ置き、equality testを通す。対象は`CandidateManifestV1`、`CandidateIdentityV1`、`SourceIdentityV1`、`EnvironmentFingerprintV1`、`AttemptRegistrationV1`、`RoleResultV1`、`ProcessMetricsV1`、`AttemptResultV1`、`CampaignResultV1`、`FaultCampaignResultV1`、`StabilityWindowResultV1`、`QualificationResultV1`、`EvidenceIndexV1`、`ProtectedTreeSnapshotV1`、`ExecutionPacketV1`、`StopReturnV1`、`RoleOwnershipV1`とそのnested typesである。

まず Draft 2020-12 validatorでshapeを検証し、`contracts.py`でschemaの`x-key-order`、`x-array-order`、`x-unique-by`、`x-semantic-invariants`、artifact間のidentity/evidence参照を検証する。全objectはclosed、全propertyはrequiredとし、値が該当しないfieldはschemaが許す明示nullを使う。未知field、欠落field、重複keyをdrop・補完しない。

Canonical JSON bytesはUTF-8（BOMなし）、schema記載のfield order、array order、空白なし、non-ASCIIを直接UTF-8化、NaN/Infinityなし、末尾LF一つとする。整数は非負のbase-10、浮動小数型はwire valueに使わず、CPU quotaなどのdecimalはschema指定のcanonical decimal stringとする。Object key orderやarray orderが契約にない場合はserializerが勝手にsortせず、schema contractへ戻して止める。

### 8.1 Attempt registration

`AttemptRegistrationV1`はGitHub repository/workflow/run ID、`run_attempt`、API `created_at`、event-resolved source SHA/tree、manifest digest、environment fingerprint、campaign/window IDs、registration statusを閉じる。Started runはAPI historyに現れた時点で一度登録し、結果・artifact欠落でも消さない。`run_attempt != 1`は`rejected-rerun`として保存し、同じattempt IDを再登録しない。

### 8.2 Role result

`RoleResultV1`はroleごとに一つだけ出す。CandidateIdentity、role環境fingerprint、start/completion時刻、status、argv、exit code、node observation、process metrics、unexpected/approved/policy-skip/duplicate counts、errorsを型付きで記録する。Artifact pathだけでactual-byte proofに代えず、EvidenceIndexのactual bytes hashを参照する。Missing role resultは成功扱いにしない。

### 8.3 Process measurement

`ProcessMetricsV1`はroot PID/count、descendant PID list、monotonic start/reap時刻、wall/CPU値、effective quota/memory、root exit、全descendant reap、cgroup empty、termination reasonを閉じる。CPU/wall ratioはraw integer inputsからDecimalで算出したcanonical decimal stringを使う。表示上の丸め値はpredicateへ渡さない。

### 8.4 Per-attempt result

`AttemptResultV1`は、candidate/environment identity、全role result、identity/raw evidence completeness、Linux/correctness predicates、rerun detection、status/accepted、violationsをまとめる。一回のattemptの全role conjunctionだけを判定し、first five、fault campaign、latest twentyの不足をattempt statusへ循環させない。

### 8.5 Aggregate results

`CampaignResultV1`はcandidate/campaign identityとAPI chronology上の先頭5 attemptを、`FaultCampaignResultV1`は固定catalogue denominatorとexecuted/detected/missed IDsを、`StabilityWindowResultV1`はchronological latest 20 memberをそれぞれ型付きで保持する。`QualificationResultV1`はattempt/campaign/fault/window/context/consumer-zero/protection evidenceの最終conjunctionだけを記録する。全artifactのexact required field、enum、nullability、array orderはschema `$defs`で確定し、ここに第2のfield listを作らない。

### 8.6 Evidence index and protected snapshot

`EvidenceIndexV1`の各entryはrepository-relative POSIX path、kind/schema version、actual size、actual SHA-256を持つ。Duplicate path、conflicting digest、絶対path、`.`/`..`、backslash、NUL、symlink traversal、credential/private pathは拒否する。Raw workflow/API outputはredaction後の保存bytesも再hashし、未加工credentialを残さない。

`ProtectedTreeSnapshotV1`は同schema artifactのexact roots/exclusionと、path/type/mode/size/hashを保存する。Directoryはsize/hash null、regular fileはactual bytes digest、symlinkはlink target bytes digestのみでtargetをfollowしない。詳細は§13.3のreviewed helperが唯一のcapture implementationである。

### 8.7 Execution packet and stop return

`ExecutionPacketV1`だけがcheckpoint input/authorization packetであり、`authorized_checkpoint`と`checkpoint_inputs.checkpoint_id`は一致する一つのP00–P22値である。Packetは該当Plan section hash、EvidenceIndex参照、write boundary/path allowlistを束縛し、read-only checkpointのwrite pathは空にする。`implementation_authorized=true`にはschema上review pass/P0=0/P1=0、Issue projection readback、explicit dispatch receipt、concurrent-writer absenceが必要である。現行spec artifactは`implementation_authorized=false`のままで、review passだけではProduct mutationを解禁しない。`StopReturnV1`だけがstop payloadである。PlanとHandoffは同じschema definitionへの参照であり、別のexact JSON field listを作らない。

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
7. replacement GREENとconsumer-zero後、old check emitterがbranchに残っている状態でhumanがold required contextを除去し、`U + new`とmerge-queue scopeをreadbackする。
8. `U + new`確認後に限りold data/provider/workflow/tests/markersを削除。
9. final sourceでscanner、unit、integration、role graph、lint、protected workflow guardを再実行する。Post-merge gateはcontextをread-onlyで再確認し、設定変更を繰り返さない。

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

- `pull_request`: per-attempt checkのsourceはevent payloadのPR head SHA/tree。
- `merge_group`: merge queueがactiveな場合、merge group SHA/treeを別source identityとしてper-attempt checkする。
- `workflow_dispatch`: required input `source_sha`で指定したexact commit/treeを独立attemptとして実行する。B3 dispatchはmerged integration SHAを明示する。
- Candidate producer: exact SHAのfirst started accepted run。
- main push automatic Full Regressionは削除し、B3 campaignはhuman-controlled independent dispatchesで実行する。

`SourceIdentityV1`を作る`resolve_source_identity`は次のevent rulesでsourceを一意にする。

| Event | source SHA/reference | Required validation |
|---|---|---|
| `pull_request` | `github.event.pull_request.head.sha` / `pull_request_head_sha` | head repo full nameが存在し、source repo+SHAから解決したtreeとcheckout treeが一致する。raw `GITHUB_SHA`は使わない。 |
| `workflow_dispatch` | required input `inputs.source_sha` / `workflow_dispatch_source_sha` | inputが40 lowercase hex、target repository内で解決可能、API/checkout treeが一致する。branch tipやevent `GITHUB_SHA`で代用しない。 |
| `merge_group` | event `GITHUB_SHA` / `merge_group_sha` | GitHubがmerge group SHAと定義する値を使い、checkout treeを確認する。PR head SHAへ置き換えない。 |

Resolverは各workflow attemptについて`source_identity.json`へrepository/source repository/workflow/run/run_attempt/event/reference/PR number/source SHA/treeを閉じて記録する。同じattempt内の全roleはproducer jobが保存した同じidentity bytesをconsumeし、repository/workflow/run/attempt/SHA/treeとcheckout HEAD/treeを再確認する。後続の独立attemptは自分のrun ID/attemptを持つ別のSourceIdentityV1を作るが、source SHA/treeはCandidateManifestV1と一致させる。CandidateIdentityV1はcandidate source SHA/treeと元producer provenanceを束縛し、後続attemptのrun IDをproducer IDと同一視しない。Build CLIはSourceIdentityV1内のrun ID/attemptを実行環境値と照合し、raw PR `GITHUB_SHA`を直接CandidateIdentityに使わない。

GitHubは`pull_request` eventの`GITHUB_SHA`をPR merge branchのmerge commitと定義し、head commitには`github.event.pull_request.head.sha`を指定するよう案内している。また`merge_group`ではmerge group SHAを提供し、`workflow_dispatch`には必須inputを定義できる。([GitHub Actions: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows))

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
  -> replacement consumers GREEN and old consumer inventory = 0
  -> human removes old required context while old emitter still exists
  -> readback U + new and merge-queue scope
  -> delete old emitter/provider only after readback
  -> final read-only readback U + new
```

Merge queueがactiveならPR headとmerge_groupを別々にcanaryする。Settings rollbackはcaptureされた`U + old`を復元する。Agentはsettings mutationを行わない。Required-context removal後のreadbackが不一致・取得不能ならold emitterを削除せず停止する。

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

唯一のcapture helperは`artifacts/capture_protected_snapshot.py`で、Plan P03/P16が同じscript SHA-256を確認して使う。`ProtectedTreeSnapshotV1`のfixed rootsは`spec-dock`全体、`.agents/skills`、root `.gitignore`、retained root `.github/workflows/ci.yml`、packaged `src/spec_dock/assets`である。これによりcanonical/user-owned consumer tree、unrelated skills、consumer seed、retained workflow、source assetsをbefore/afterで比較する。

`spec-dock/initiatives/**/iss-00396-*/.workbench/evidence`だけをexact exclusion pathとしてnested evidenceをsnapshotへ混入させない。他のWorkbenchやArtifactは除外しない。Directory entryはmodeのみ、regular fileはmode/size/actual-byte SHA-256、symlinkはmode/link-target-byte length/hashを記録する。Symlinkをfollowしない。Missing root、special file、UTF-8化できないpath、capture中のfile/directory/symlink mutation、protected root内または指定外のoutput pathではfail closed。Output JSONには絶対pathとtimestampを含めず、同一treeなら同一bytesにする。

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

---
種別: 設計書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "approved"
詳細化状態: "scope-simplified; product-implementation-gated"
最終更新: "2026-09-19"
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
  sha: "4d68bce3f3ee977548a3c467476da39c15f43594"
  tree: "80ade10f57cd5f4140daa03ca8a40b844f1fcc53"
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 設計

## 1. Design conclusion

本Designの実質仕様は2026-09-18に同一Red sessionのStrict reviewをpass（SHA `0c7cdd484c82142333f035df9488cf60586c2aea`、tree `4ba6fc830e7d2d5d9767ba36c00459371e360aa2`、P0=0、P1=0、findings=0）。その後の#395 corrected mergeを#396 branchへ許可された方法で統合し、新しいexact freeze candidateを作るため、当該旧receiptを新candidateのreviewとして扱わず、同一Red sessionで新freeze SHA/treeの再reviewを行う。新reviewとIssue projection readbackが揃うまで、実装許可はfalseのままとする。

Target architectureは、次の責務を順序付きで分離する。責務の数やfile分割は固定せず、Workflow YAMLやtracked docsへ親qualification valueを独立管理しない。

1. **Predecessor admission layer** — #395 A395-SEC-001 correctionはPR #403としてmerge済み（SHA `3c69af78843b04a13bde2f93eb3b1eb4081cdb33`, tree `38e2f9a50f7cae14ef24fa1187a559c592729e3b`）。同一tipでB1/B2をfresh実行して親ownerが受入済み。元PR #401 merge identity `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / `37eabc1aa250838dcd9f61d627309b0ff27e0db7`はhistorical only。別途報告された症状とA395-SEC-001の同一性は推定しない。
2. **Parent policy projection layer** — Epic Requirementの`E384-QUAL-001`からmechanical constants/predicate IDsだけを生成する。
3. **One-time materialization layer** — final-gate attemptとは別にsource SHA/treeを一度だけbuildし、wheel/sdist actual bytesとenvironment identityを完成させる。Failureはsame-SHA poisonである。
4. **Immutable freeze layer** — complete candidate/environment/fault definition/window contractをcampaign開始前にfreezeする。
5. **One-attempt stage graph** — `candidate-resolve`が登録済みcandidateと保存済みactual bytesをbuildなしで照合し、その後permanent pytest pluginがresolved ownershipに従ってstatic analysis、Linux canonical、sdist smoke、macOS deltaを同じresolved bytes上で一回ずつ実行する。Terminal `attempt-evaluate`はresolve証拠と4 execution-role resultを集約してper-attempt resultを一つ作る。
6. **History/qualification layer** — GitHub chronologyからparent contractが要求するpopulation/window/fault aggregateをselectionなしで評価する。
7. **Consumer-first cutover layer** — replacement GREEN、old consumer 0、context new-only readback後に旧provider/data/workflowを削除し、final sourceで再検証する。

Evidenceは一つのbinding-scoped append-only indexで扱う。各entryの`binding_scope`がpreflightならcandidate identityを持たず、candidateならidentity/environmentを必須とする。Wireへprivate absolute pathを保存せず、`evidence_root_id`とlogical root-relative POSIX path、actual byte size/hashだけを持つ。External settings mutationとmergeはhuman-onlyで、agentはread-only capture、request、receipt、verificationだけを行う。

Formal start/active stateは保存するが、B1/B2 acceptance、same-Red pass、Issue projection readback、explicit implementation dispatchが完了するまでProduct/test/workflow/policy mutationを行わない。

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

### 2.3 Predecessor admission and historical claim surfaces

#395 original PR #401 merge `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / `37eabc1aa250838dcd9f61d627309b0ff27e0db7`はhistorical identity onlyである。A395-SEC-001 correction PR #403はmerge済み（`3c69af78843b04a13bde2f93eb3b1eb4081cdb33` / `38e2f9a50f7cae14ef24fa1187a559c592729e3b`）。別途報告された症状との同一性を仮定せず、Issue #395はOPENのまま保持する。

Fresh B1とsame-tip B2はいずれも親owner受入済みでactual-byte evidenceを保持している。B2の最初のdefault-temp runは`unsafe-repository-binding`で失敗したため失敗証拠を残し、private TMPDIRを使った再実行のみpassとして集計する。許可済みrealignment後、corrected mergeが#396 branch祖先になった。新freezeのsame-Red reviewおよびIssue projection readbackはまだ別gateである。

- `b1-b2-admission-status-v2.json`がcurrent Issue-local statusを閉じる。
- `b1-b2-verification-contract-v1.json`が#395 ownerによるdefect correction後にGitHub readbackしたexact merge SHA/treeをexecution targetとして解決する規則、fresh execution order、evidenceを閉じる。
- Corrected #395 merge SHAはIssue #396のfinal `SPEC_FREEZE_SHA`のancestorでなければならない。`git merge-base --is-ancestor "$B12_TARGET_SHA" "$SPEC_FREEZE_SHA"`でread-only確認し、falseならIssue branchの統合方法をEpic integration/parent ownerへ戻す。明示許可なしにbranchをmerge/rebase/cherry-pick/recreate/force-pushしない。
- 許可されたbranch realignment後はsource SHA/treeに依存するcapture/artifactを再生成し、新しいspec candidateを同じRed reviewへ再提出してIssue projectionを読み戻す。#395 SHA/treeが同一ならaccepted B1/B2 bytesは再利用できるが、異なる場合は再実行する。
- #395 correction PR #403のmerge identityとsame-tip fresh B1/B2 receiptを確認済み。B1/B2 parent-owner acceptanceとactual-byte indexesはIssue Workbenchに保存する。
- Historical receipt/raw bytesは改変しない。
- 正しいtarget SHA/tree上でB1/B2をpassしても、別途報告された未特定症状との同一性は含意しない。
- Ancestryはauthorized realignment後にpassした。最終freeze、same-Red review、Issue body readback、clean exact identity/no concurrent writerが揃うまではtarget topologyはimplementation designのままで、dispatch不可である。

## 3. Target module topology

この節の表は責務の候補を示すものであり、exact file count・module name・一責務一ファイルを契約にしない。隣接責務を統合しても、candidate build、artifact identity、environment/process measurement、ownership filter、attempt/history/evaluator、one-shot cutover、CLIのobservable contractを保てばよい。実装は最小の循環しない構造を選び、authoring-onlyの表現をruntimeへ持ち込まない。

### 3.1 New provider-gate package

| Status | Exact path | Planned symbols / responsibility |
|---|---|---|
| NEW | `scripts/quality/provider_gate/__init__.py` | versionとclosed public exportsのみ。 |
| NEW | `scripts/quality/provider_gate/contracts.py` | 永続record/evidence referenceの型、codec、semantic invariant validation。必要なら隣接identity/evidence責務をここへ統合する。 |
| NEW | `scripts/quality/provider_gate/materialization.py` | candidate build、manifest、actual-byte verification、stored artifact resolver、same-SHA registry。 |
| NEW | `scripts/quality/provider_gate/environment.py` | environment admission/fingerprint、Linux root+descendant measurement/reap。必要ならprocess tree責務を統合する。 |
| NEW | `scripts/quality/provider_gate/pytest_plugin.py` | permanent `pytest_addoption`/`pytest_collection_modifyitems`/observation owner。 |
| NEW | `scripts/quality/provider_gate/evaluator.py` | role/attempt/campaign/window/fault/final evaluation、append-only history。必要ならhistory/faults責務を統合する。 |
| NEW | `scripts/quality/provider_gate/evidence.py` | binding_scope付きappend-only evidence index、logical path/byte hash。 |
| TEST-ONLY | `tests/unit/provider_gate/test_cutover.py`等 | consumer scan、required-context、protected treeの一回限りの検証。恒久runtime moduleを要求しない。 |
| NEW | `scripts/quality/provider_gate/cli.py` | thin dispatch。Business ruleを持たない。 |
| NEW | `scripts/quality/provider_gate/_qualification_policy_generated.py` | parent Requirement projection。手編集禁止。 |

Materialization CLIとrole CLIを分ける。`materialize-candidate`はattemptを登録せず、`run-role`はbuildを実行できない。`freeze-campaign`はcomplete materialization recordだけを入力にする。

### 3.2 Source-controlled contracts

| Status | Exact path | Authority/role |
|---|---|---|
| PRESERVE | `artifacts/role-ownership-v1.json` | immutable reviewed baseline。 |
| PRESERVE | `artifacts/role-ownership-delta-v1.json` | ordered reviewed delta。operation countはfileから導出する。 |
| DERIVED/HISTORICAL | `artifacts/role-ownership-checkpoints-v1.json` | 旧candidateの比較用。runtime入力・current authorityにしない。 |
| DERIVED/HISTORICAL | `artifacts/role-ownership-resolved-final-v1.json` | 旧candidateの比較用。final evidenceは実行時に生成する。 |
| PRESERVE | `artifacts/seeded-fault-catalogue-v1.json` | candidate freeze時点のfault denominator。件数はfileから導出する。 |
| DERIVED/HISTORICAL | `artifacts/closed-violation-codes-v1.json` | 旧one-to-one一覧。stable operational familyの正本にしない。 |
| NEW | `artifacts/old-policy-retirement-v1.json` | finite signatures/delete/retain/deletion gate。 |
| NEW | `artifacts/b1-b2-admission-status-v2.json` | current corrected-merge/B1/B2 admission status with accepted same-tip evidence; separate unspecified symptom identity is not inferred。 |
| NEW | `artifacts/b1-b2-verification-contract-v1.json` | fresh same-tip B1/B2 commands/evidence relation。 |
| NEW | `artifacts/authoring-gate-status-v1.json` | review/projection/dispatch/B1/B2 current status。 |
| NEW | `artifacts/strict-review-p2-record-v1.json` | six P2 record-only entries。 |
| MODIFY | `artifacts/provider-gate-contracts-v1.schema.json` | Candidate/Attempt/Qualification/Cutover/Stopと共通evidence referenceのpersisted contractだけをclosedにする。 |
| MODIFY | `artifacts/issue-396-implementation-readiness.html` | standalone human guide synchronized to these contracts。 |
| PRESERVE | Linux/macOS raw collection files | immutable baseline evidence。 |
| PRESERVE | historical B1/B2 receipt/raw JSON | historical claims only。 |

 Runtime copies under `scripts/quality/provider_gate/contracts/` are generated/copied from the small set of current canonical inputs after dispatch and are byte-identical. Derived checkpoint/full manifests and authoring receipts are runtime inputではない。Canonical artifacts are authoring inputs, not Product runtime writes during implementation。

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

## 5. Candidate materialization, provenance and reuse graph

### 5.1 State machine

```text
unmaterialized
  -> materializing
       -> materialized
       -> poisoned
```

`CandidateMaterializationV1`はsource SHA/treeごとに一つだけ作る。Materialization IDはsource identityとgate contract versionにdomain-separated hashを適用して作り、attempt IDとは別namespaceにする。

- `materializing`: build invocation durable registration後、completion前。
- `materialized`: build invocation count 1、complete manifest/wheel/sdist bytes、candidate identity、environment fingerprint、candidate evidence indexが存在。
- `poisoned`: build failure/cancel/missing/mismatch/duplicate producer。Same source SHA/treeで再入場不可。

Materializationはfinal-gate role graph、first population、rolling windowのmemberではない。Materialization outputをattempt resultへ偽装しない。

### 5.2 Exact producer/materializer selection

1. SourceIdentityV1をevent別にresolveし、checkout SHA/treeと一致させる。
2. Same source SHA/treeのmaterialization registryをread-only確認する。
3. Existing `materialized`ならstored bytesだけをresolveし、buildしない。
4. Existing `materializing`または`poisoned`ならfail closed。
5. Absentなら`materializing`をdurable登録し、top-level build commandをexactly one invocation実行する。
6. Manifest/core/bundle/final bytes hash、wheel/sdist actual bytes、provider candidate digestを完成させる。
7. Environment admission/fingerprintを完成させる。
8. Binding-scoped EvidenceIndexを完成させて`materialized`へterminalizeする。
9. 途中failureは`poisoned`へterminalizeする。

Workflow rerun、run_attempt増分、別job build、role内build、local fallbackをqualification producerにしない。

### 5.3 Non-circular manifest and actual-byte binding

Candidate manifestはsource repository/SHA/tree、provider candidate digest、build invocation identity/command、wheel/sdist filename/size/SHA-256、manifest core digest、bundle digestをclosed orderで持つ。Core hashはself fieldsを除くcanonical bytes、bundle hashはcore digestとactual artifact records/bytesをlength-frameして計算する。Final manifest bytes hashはmanifest外のCandidateIdentityV1/EvidenceIndexに保存する。

Every consumer verifies API artifact identity、downloaded manifest bytes、wheel/sdist size/hash、source/tree/provider candidate digest。Filenameやclaimed hashだけでは受理しない。

### 5.4 Campaign freeze ordering

`CampaignFreezeV1`はmaterializationが`materialized`になった後だけ作成できる。Candidate identity、environment fingerprint、gate contract version、fault definition hash、window contract ID、frozen-at、candidate evidence indexをimmutableに閉じる。

- Required-context intentional REDはmaterialized PR candidate上の通常attemptとして実行できるが、campaign freeze前なら`purpose=context-canary`、campaign ID null、window contract ID non-nullでhistoryへ残す。
- Human merge SHA/treeがPR sourceと異なる場合、merge sourceは別candidateなので新しいone-time materializationを行う。
- Final B3 campaignの最初のattempt registrationはpost-merge materializationとCampaignFreezeV1の完成後である。

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

### 7.1 Role graph and deterministic ownership

One final-gate attemptは登録済みcomplete candidate/environmentとresolved ownership manifestを入力に、次のordered stage graphを一回ずつ実行する。

```text
candidate-resolve       # read-only stored-byte resolution; no build
static-analysis
linux-canonical
sdist-smoke
macos-delta
attempt-evaluate        # terminal result aggregator; pytest roleではない
```

Build producer/materializationはattempt/stage graph外であり、`candidate-resolve`は新しいbuildやartifact置換を行わない。各attemptで`candidate-resolve`は`AttemptRegistrationV1`のsource/candidate/environment identityを、同一source SHA/treeに対するcompleted `CandidateMaterializationV1`、candidate-bound EvidenceIndex、manifest/wheel/sdistのactual bytesと照合する。Resolverはactual manifest bytesとartifact sizes/digests、bundle digest、candidate identity、environment fingerprintを検証し、`CandidateResolutionV1`へstage status、attempt/candidate/materialization/evidence identities、開始/完了、build invocation count 0、errorsを記録する。登録またはstored bytesが欠落・不一致ならfail closedし、後段roleを開始しない。これはattempt evidenceでありmaterialization registryを変更しない。

Resolved candidateの後、4つのexecution rolesだけが`RoleResultV1`を出力する。Terminal `attempt-evaluate`は同一attemptの`CandidateResolutionV1`とrole result refsを読み、`AttemptResultV1`を一度だけ出力する。正常系ではsuccessful resolutionと4つのrole resultsを集約する。Resolutionが失敗または欠落した場合はexecutionを開始せず、4 role slotsを`rejected`または`missing-evidence`、hashなしで記録し、AttemptResultをnon-acceptedにする。`AttemptResultV1.stage_id=attempt-evaluate`が終端stage artifactであり、self-referenceを作らない。Attempt resultは`candidate_resolution_sha256`と4要素のordered `role_results`を持つ。candidate resolve不成立・欠落は`identity_complete=false`または`raw_evidence_complete=false`にし、attemptはacceptedにならない。`AttemptStageIdV1`は6 stageのclosed enum、`ExecutionRoleIdV1`と`RoleResultV1.role_id`は4 execution roleだけのclosed enumとする。Stage/roleの一回性、参照先attempt/candidate/environment identityの一致はsemantic codec invariantとして検証する。

`role-ownership-v1.json` baselineへ`role-ownership-delta-v1.json`の必要なprefixを適用し、実行時manifestを決定的に導出する。Assignment countとdelta operation countはこの導出の観測値であり、別の固定受入値ではない。Checkpointごとのfull assignment fileは別の入力正本ではない。

各`baseline_sha256`と`delta_sha256`は、canonical baseline/delta JSON artifact fileの正確なbytes（末尾LFを含む）のSHA-256とする。file bytesを直接hashし、JSON parse/re-serialize、key/array order変更、newline変換その他の正規化をしない。Source artifact digestは実行時manifest evidenceへ記録し、full checkpoint assignmentをtracked artifactへ複写しない。これらのartifact identity digestは、次に定義するnode-ID collection digestとは別である。

`collection_sha256`はowner/reasonを含まないnormalized node-ID set digestである。重複IDまたはCR/LFを含むIDを先にrejectし、node IDをUTF-8 byte順にsortし、各IDのUTF-8 bytesにLFを一つずつ付けたstream（末尾LFを含む）のSHA-256を取る。これはbaseline `normalized_node_ids_sha256`と同じcanonicalizationである。Checkpoint `collection_sha256`、final projectionのdigest、実collectionの`NodeObservationV1.collection_sha256`は同じ入力表現を使う。

Pluginはbody開始前にactual collection setとresolved assignment setを照合する。Unknown、missing、duplicate owner、unplanned add/move/delete、collection hash mismatchを検出したらbodyを0件実行してrejectする。

生成manifestは全assignmentを保持し、invocation selectorに合わせて縮小しない。必要なcheckpoint evidenceはcount、owner-counts、collection hashだけを記録する。

- **Full qualification role invocation:** pytestのpositional node selector、`-k`、`-m`、shard/ignore selectorを付けず、repository全体をcollectする。Pluginはactual collection set/hashをfull resolved manifestと照合してから、指定roleのowner nodeだけを実行する。この経路だけがaccepted `RoleResultV1` / attempt qualification evidenceになれる。
- **Focused checkpoint invocation:** `path/to/test.py::...`形式の完全なpytest node IDを一つ以上指定する。Pluginはactual collection setが指定ID集合と完全一致すること、各IDがfull manifestに一度だけ存在し、selected roleのownerであることをbody前に検証する。未指定のmanifest nodeはmissing扱いしない。File/directory selector、marker、glob、`-k`、`-m`、shard/ignore selectorは拒否する。Focused resultはengineering verificationであり、accepted `RoleResultV1`、AttemptResultまたはB3 qualification evidenceには使わない。

両modeでbaseline + ordered deltaから導出したfull manifestのcount/hash/owner partitionは検証する。Unknown ID、requested IDのmissing/duplicate、duplicate owner、unplanned add/move/delete、該当modeのcollection hash mismatchはbodyを0件実行してrejectする。

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

S2前半のunit nodesは通常の`uv run pytest`で直接実行する。Permanent pluginとrole ownership filteringを導入する前のunit実行へplugin/role flagsを付けない。この実行は開発用検証であり、qualificationまたはrole ownershipの証拠にはしない。

Implementation briefにあるplugin付きpytest commandのうちnode IDを列挙するものはfocused engineering checkである。これはfull role runを代替せず、qualification resultとして登録・集約しない。実attemptのroleは`run-role`からpytest selectorなしで実行し、full qualification collectionを照合する。

### 7.7 Permanent plugin ownership and temporary root compatibility seam

`pytest_plugin.py`は移行中・final sourceの両方で`pytest_collection_modifyitems`を実装する恒久的filter ownerである。Root `tests/conftest.py`はS2–S4だけのtemporary seamとして、次を満たすexact invocationでlegacy marker/skip/ledger hookをbypassする。

- `-p scripts.quality.provider_gate.pytest_plugin`でplugin登録済み。
- `--provider-gate-role=<exact role>`が指定済み。
- resolved ownership manifest path/hashが指定済み。
- legacy full-regression flagsとの併用なし。
- plugin contract/schema/version検証済み。

Plugin未登録、role欠落、unknown node、schema/hash不一致、legacy flag併用はcollection前rejectで、legacy skipへfallbackしない。Ordinary pytestはretirement phaseまでlegacy behaviorを保つ。

S4のconsumer-zero後にlegacy hook/temporary seamを削除する。`tests/conftest.py`がold hookだけならfile削除、他fixtureがあればold symbolsだけ削除する。Pluginのfilter hookは残るため、final `run-role`にowner callerが消失しない。Retirement後のnegative testはroot conftest不存在/legacy symbols不存在とplugin filteringの同時成立を確認する。

## 8. Closed evidence and execution schema families

永続化されるrecordとcross-job evidence referenceだけをschemaで閉じる。内部helper、checkpoint作業状態、authoring status、presentation ZIP/HTMLはtyped codeまたはnon-normative evidenceであり、runtime schema familyへ複製しない。

`provider-gate-contracts-v1.schema.json`はDraft 2020-12である。今回対象の`ExecutionPacketV1`と`B1B2AdmissionStatusV2`は、nested recordを含め`additionalProperties=false`へ閉じる。Semantic codecはduplicate keys、key order、array order、cross-field relationsを追加検証する。これ以外のschema familyはこの修正で形を変えない。

`ExecutionPacketV1.spec_review`はclosed objectで、`reviewer_session_id`、`review_status`、`reviewed_sha`、`reviewed_tree`、`p0_count`、`p1_count`、`p2_count`、`p3_count`、`review_evidence`だけを持つ。Sessionは`iss396-spec-review-red`に固定する。未実施ならreviewed identity/counts/evidenceをnull、`pass`/`fail`なら全てを埋める。`B1B2AdmissionStatusV2`の全nested objectもclosed fieldsにし、`formal_issue_start`、`predecessor_human_merge`、B1/B2 acceptance、historical claims、authority conflictsは各現行fieldをrequiredにしてunknown propertyを拒否する。

`implementation_authorized`は既存のbooleanのままfalseを有効なblocked状態として保持する。`formal_issue_start.product_implementation_authorized=false`はformal start時点の履歴を表し、後続の許可判定は`ExecutionPacketV1.implementation_authorized`だけで行う。trueの場合は、corrected predecessor mergeのowner acceptanceとIssue freeze ancestor proof、B1/B2のperformed+accepted status・non-null evidence・同一corrected SHA/tree、review passかつP0/P1=0でreviewed SHA/treeがspec freezeと一致、Issue projection readback、explicit dispatch、`concurrent_writer_absent=true`を要求する。JSON Schemaで表すfield/enum/non-null条件に加え、SHA/tree等の相互一致はsemantic codec invariantとして検証する。新しいauthorization state modelやcheckpointは追加しない。

Semantic validatorは、(1) B1 SHA/tree = B2 SHA/tree = corrected predecessor merge SHA/tree、(2) review SHA/tree = spec freeze SHA/tree、(3) ancestry commandの入力が同じcorrected SHAとspec freeze SHAでexit 0、(4) B2 acceptedなら先行B1もacceptedを検証する。既存packet validator testはblocked packetのpositive caseと、空/unknown nested fields、不足gate、SHA/tree不一致、ancestor proof欠落/negative、review identity不一致のnegative casesを含む。これらは現行validator内で検証し、別state machineやtest nodeは追加しない。

### 8.1 Binding-scoped evidence

- `EvidenceWorkspaceV1`: root ID、kind、created-at、retention。Physical absolute pathはruntime-only。
- `EvidenceBlobRefV1`: root ID、logical POSIX path、size、actual-byte SHA-256。
- `EvidenceIndexV1`: specification identityとcapture evidence、candidate identity、environment hashを一つのappend-only indexで扱う。各entryは`binding_scope=preflight|candidate`を持ち、preflightではcandidate identityを禁止し、candidateではidentity/environmentを必須とする。
- `RepositoryArtifactRefV1`: source-controlled canonical artifactだけを参照。

Logical pathはabsolute、drive letter、dot/dot-dot、backslash、NUL、symlink traversalを拒否する。

### 8.2 Materialization and campaign

`CandidateMaterializationV1`、`CampaignFreezeV1`、`SourceIdentityV1`、`CandidateIdentityV1`、`EnvironmentFingerprintV1`を分離する。Materializationにはattempt IDがなく、CampaignFreezeはcomplete materializationだけを受ける。

### 8.3 Ownership and node observation

`RoleOwnershipDeltaOperationV1`、`RoleOwnershipDeltaV1`、`ResolvedRoleOwnershipV1`、`NodeExecutionV1`、`NodeObservationV1`を必要なpersisted recordとして閉じる。Resolved ownershipの`baseline_sha256`/`delta_sha256`は§7.1のexact source-file bytes digestを持つ。NodeObservationはcollected/executed/unknown/missing/duplicate setと§7.1のcanonical collection hashを持つ。Baseline、delta prefix、実collectionは同じnode-ID normalizationを使い、owner assignmentが変わらない限り同一node setは同一digestになる。

### 8.4 Attempt and results

Every started attemptはcomplete candidate/environment identityを持つ`AttemptRegistrationV1`へ事前登録される。RoleResultはbuild evidenceを持たず、static/Linux/sdist/macOSだけを表す。AttemptResultはrole/raw evidenceのconjunction、aggregate resultsはparent-generated predicatesを参照する。

### 8.5 Fault, retirement and external context

- `FaultCatalogueDefinitionV1`: candidate-freeze時点のsource-controlled entries。件数はcatalogue fileから導出する。
- `CandidateBoundFaultCatalogueV1` / `FaultExecutionResultV1`。
- `OldPolicyRetirementContractV1` / `ConsumerScanResultV1`。
- one-shot required-context transition receipt。Human readbackを保存し、恒久runtime stateは持たない。

External names/IDsはread-only captureからのみ入り、specで創作しない。

### 8.6 Finite operational failures

Violation codeはacceptance decisionまたはrecovery分岐で使うstable operational familyだけをclosedにする。Fault-specific detailはfault_id/category/detection stageで表し、旧68-value一覧をcurrent runtime authorityにしない。Unknown/free-form/catch-all codeは禁止する。

### 8.7 Truthful stop

`StopReturnV1`はpre/post mutation双方を表し、scope impact、required owners/actions、changed/external surfaces、rollback/recovery state、stage-correct evidenceを持つ。`automatic_rollback_performed=false`は不変である。Pre-mutationはchange arrays空、post-mutationは実施済みchangeを少なくとも一件記録する。

## 9. Chronology, cancellation and missing evidence

### 9.1 Three distinct chronologies

1. Materialization registry chronology — source SHA/treeごとのone-time build terminal state。Attemptではない。
2. Attempt chronology — GitHub run created/start identityとrun attemptをimmutable保存。Context canaryを含む。
3. Aggregate selection — parent-generated rulesでfirst population/windowをchronologyから導出。Result filter禁止。

### 9.2 Started incomplete attempts

Registration後のfailure、cancel、interruption、missing role/raw evidenceはhistory memberとして残り、nonaccepted resultになる。Workflow API状態、job conclusion、artifact listing/downloadのactual-byte evidenceを保存する。Run deletion/expiryでevidenceが欠けた場合もsuccessへ補正しない。

### 9.3 Retry/rerun and identity

Same attempt ID、run_attempt増分、artifact replacement、campaign reset、member replacement、success-only filterをfinite violation codeでrejectする。Old attempt rowを上書きしない。P2のattempt tuple表現差はrecord-onlyで、本P1 authoring passの合否条件へ昇格しない。

### 9.4 Campaign ordering

Required-context REDはmaterialization後のnormal role graphでありrolling historyへ残る。Final campaignはpost-merge materializationとfreeze後に開始する。Materializationをfirst/window memberへ数えない。Aggregate completenessをper-attempt statusへ逆流させない。

## 10. Seeded-fault catalogue

Normative denominatorは`seeded-fault-catalogue-v1.json`のcandidate-freeze時点のfile bytesとdefinition hashである。現在のreviewed fileは20 categories / 45 atomic entriesを持つが、件数はfileから導出する。各entryは次を閉じる。

- `F001`–`F045` fault ID。
- category ID/name。
- exact fixture ID、test-only injector ID。
- stable operational failure family（必要な場合のみ）。
- detection stage。
- catalogueから導出するFirst Red case ID。
- First Red test nodeは実装時のtest inventoryから導出する。
- `candidate_bound=true`。

Categoriesはmanifest、source identity、artifact bytes/size、producer、environment、topology、process lifecycle、performance/correctness、missing role/raw evidence、rerun/duplicate attempt、started incomplete attempts、first population/window replacement/filter、fault denominator/execution、old consumer、retained workflowを覆う。Entry count、fault code番号、First-RED test nodeはcatalogueから導出し、別のschema authorityへ複製しない。

First Redはcatalogueの全entryをenumerateし、各entryのexpected stageがまだ検出されないことをrecordする。Implementation後GREENは全件exact matchを要求する。Post-observation denominator reduction、entry omission、wrong stage、unexecuted entryをfail closedにする。Injectorはtest fixture/object adapter seamだけに存在し、production workflowへfree-form fault optionを残さない。

## 11. Consumer-first cutover design

### 11.1 Finite retirement contract

`old-policy-retirement-v1.json`はproduction/workflow/test consumers、delete candidates、retained-protected paths、historical allowlistをone-shot cutover inputとして列挙する。ScannerはPython AST、YAML jobs/run/needs、JSON paths、operational docsを解釈し、plain `rg`だけをproofにしない。Scannerはtest/evidence helperであり、恒久runtime moduleや追加serviceではない。

### 11.2 Ordered sequence

1. Candidate、attempt、fault、retirementの最小入力をreview済みとしてfreeze。
2. Permanent pluginとreplacement modules/testsをRED→GREEN。
3. Shadow workflowをadditiveに実装。
4. Candidateをone-time materializeし、new checkをobserved nameでcapture。
5. Human required-context additive migration + intentional RED + GREEN recovery。
6. 全old consumerをreplacementへ移行。
7. one-shot consumer scanがcomplete、old consumer 0、retained workflow equal。
8. Humanがold emitter存在中にold required contextだけを外し、`U + new`/merge-group scopeをreadback。
9. Old provider/data/workflow/tests/temp seamを同一Issue PR内で削除。Permanent pluginは残す。Cutover scanner/context stateは削除可能なtest/evidence helperとする。
10. Final sourceでscanner/ownership/role graph/ordinary suite/lint/protectionを再実行。

Consumer-zero前のdeletion、old required context gap、partial accepted state、compat writer/fallbackは禁止する。

### 11.3 Exact move/delete ownership

Nonpolicy nodeの移動やdelete対象はreviewed deltaから導出する。個別の件数をPlanやDesignへ重複記載せず、semantic key/ownerを維持する。

## 12. Workflow, materialization and human external boundary

### 12.1 Permissions and source identity

Repository workflowはread-only permissionsを最小化し、actual API callsで必要性を確認する。PRはpayload head SHA、workflow_dispatchはrequired source SHA input、merge_groupはmerge group SHAへbindする。Raw PR `GITHUB_SHA`やbranch tipで代用しない。

### 12.2 Jobs and non-circular ordering

Shadow/final workflowは概念上次を持つ。

```text
materialize-candidate   # attempt/stage graph外、一回限り
freeze-campaign         # complete materialization後、attempt graph外
register-attempt        # durable registration前提、stage graph外
--- one registered attempt ---
candidate-resolve       # attempt内、stored bytesのread-only照合
static-analysis         # final-gate attempt role
linux-canonical         # final-gate attempt role
sdist-smoke             # final-gate attempt role
macos-delta             # final-gate attempt role
attempt-evaluate        # result aggregate
```

Materialization job成功後だけattempt stage graphを開始できる。各attemptの最初の`candidate-resolve`はmaterialize jobをbuildせず、stored candidateをresolve/verifyする。成功後に限り4 execution rolesを開始し、terminal `attempt-evaluate`がresultを作る。Post-merge final candidateはmerge SHA/treeで別materializationを一度だけ行い、その後CampaignFreezeV1を作る。Build failureはsame-SHA poisonである。

Qualification attemptsへ`cancel-in-progress: true`を使わない。Started cancel/failure/missingをhistoryに残す。

### 12.3 Read-only external capture

P02とcutoverの外部captureは一回限りのevidenceである。必要なbefore/old-plus-new/intentional-red/recovered-green/new-only/final-readback関係を一つのtransition receiptへ記録し、exact context/ruleset/merge-queue namesはread-only captureからのみ得る。Permission-limited/empty responseを「contextなし」と解釈しない。恒久のcontext state machineやbackground serviceは追加しない。

### 12.4 Human-only transition

Humanだけがsettings add/remove/restoreとmergeを行う。Agentはrequested change set、canary attempt、readback、rollback instructionsを作る。Unrelated effective set`U`、review gate、merge queue/merge_group coverageを各snapshotで比較する。REDがblockしない、GREENが戻らない、readback不能、U driftならold emitterを削除せずStopReturnを作る。

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

Protected-data comparisonはcutover前後に一度ずつ行う。既存の`capture_protected_snapshot.py`はone-shot evidence helperとして使えるが、唯一の恒久capture authorityやruntime serviceではない。`ProtectedTreeSnapshotV1`のfixed rootsは`spec-dock`全体、`.agents/skills`、root `.gitignore`、retained root `.github/workflows/ci.yml`、packaged `src/spec_dock/assets`であり、同じno-touch結果をtracked diff/targeted hashで証明できる場合はhelperを統合してよい。

`spec-dock/initiatives/**/iss-00396-*/.workbench/evidence`だけをexact exclusion pathとしてnested evidenceをsnapshotへ混入させない。他のWorkbenchやArtifactは除外しない。Directory entryはmodeのみ、regular fileはmode/size/actual-byte SHA-256、symlinkはmode/link-target-byte length/hashを記録する。Symlinkをfollowしない。Missing root、special file、UTF-8化できないpath、capture中のfile/directory/symlink mutation、protected root内または指定外のoutput pathではfail closed。Output JSONには絶対pathとtimestampを含めず、同一treeなら同一bytesにする。

## 14. Failure, recovery and rollback

### 14.1 Materialization/candidate poisoning

次のいずれかでsource SHA/tree materializationを`poisoned`へterminalizeする。

- build producer failure/cancel/missing/expired artifact。
- manifest/source/tree/wheel/sdist/environment mismatch。
- build invocation countを1へ閉じられない。
- Materialization evidence indexが不完全。

Poisoned sourceは同じSHA/treeでbuildを再実行できない。`MATERIALIZATION_POISONED`と`SAME_SHA_REBUILD_ATTEMPTED`を区別し、fix commitによるnew sourceだけを許す。

Materialization後のattempt/campaign rejectionも同じsourceでmember replacement、campaign reset、rerunを許さない。Contract上source changeが必要な場合、new candidateとしてmaterializationから開始する。

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
| I396-RQ-001 | §2.3 and predecessor admission artifacts |
| I396-RQ-002 | §4 |
| I396-RQ-003 | §5 materialization/freeze |
| I396-RQ-004 | §8.1 evidence stages |
| I396-RQ-005 | §7.1, §12.2 |
| I396-RQ-006 | §3.2, §7.1, §7.7 |
| I396-RQ-007–008 | §6 |
| I396-RQ-009–013 | §9 and parent projection |
| I396-RQ-011 | §10 exact catalogue |
| I396-RQ-014 | §8 closed families/codes |
| I396-RQ-015–016 | §11 |
| I396-RQ-017 | §12.3–12.4 |
| I396-RQ-018 | §13 |
| I396-RQ-019–020 | §14, StopReturnV1, Plan review gates |

## 16. Unresolved operational captures, not owner decisions

`owner_decisions_required=[]`である。ただし次はimplementation時にactual repository/environmentから取得するoperational factsであり、未取得のまま推測して進めない。

1. exact runner provider/class/image digest、effective CPU/memory limit、filesystem。
2. current Actions artifact retention policyとchosen retention。
3. effective required-context names、ruleset scope、merge queue state。
4. exact check-run/job names emitted by replacement workflow。
5. human canary/rollback receipt location。

これらがparent capability/no-gap contract内で一意に確定できればProduct/Policy decisionではない。複数のsemantic optionが残る、parent値を変える必要がある、admin boundaryが閉じない場合はparent stopへ昇格する。

---
種別: 要件定義書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
詳細化状態: "implementation-ready-candidate"
最終更新: "2026-09-17"
依存:
  - "iss-00395"
  - "../../requirement.md"
  - "../../design.md"
  - "../../plan.md"
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
b2_entry_evidence:
  sha: "fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d"
  tree: "37eabc1aa250838dcd9f61d627309b0ff27e0db7"
  rows_total: 15
  rows_active: 0
  rows_resolved: 15
  approved_failures: 0
  unexpected_failures: 0
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 要件定義

## 1. 結論と現在位置

Issue #396は、B1/B2が成立したexact source `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7`をread-only entryとして、Provider CIをbuild-once・same-candidate・one-role-graph-per-attemptのfinal gateへ切り替え、replacement consumerが成立してold consumerが機械的に0になった後にだけ、旧ledger、243-node timing、sharder、policy skip、policy hook、quality provider、provider main-push Full Regressionを同一Issue PRで撤去する実装単位である。

本Issueはfinal provider qualificationの**実装・測定・証拠化**だけを所有する。量的値、five-run population、rolling twenty window、aggregation、Linux performance scope、rejection、forbidden escapeのauthorityはEpic Requirementの`E384-QUAL-001`だけである。本書、Design、Plan、workflow、Python module、JSON schemaは、その親契約を機械化する投影であり、第二のpolicy authorityになってはならない。

Formal `issue start`はbranch/active contextの選択であり、Product実装許可ではない。現在は仕様候補の作成段階で、`実装開始許可: false`である。clean pushed exact specification candidateに対する独立`chatgpt-spec-review-strict`が`review_status=pass`かつP0/P1=0となり、主担当がGitHub Issue #396のcanonical projectionを更新・readbackし、ユーザーが実装をdispatchした後にだけProduct/test/workflow/policy変更へ進む。

## 2. Authority、依存、projectionの扱い

### 2.1 Authority order

1. Epic Requirementの`E384-QUAL-001` — qualificationの量的・集計authority。
2. accepted ADR、Epic Integration Branch Contract、Rolling-Wave Issue Elaboration Contract、Provider Lifecycle Wire Contract、Post-#387 Regression Baseline Register。
3. Epic Requirement / Design / PlanのIssue #396責務境界。
4. 本IssueのRequirement / Design / Plan。
5. 本Issueのhandoff、receipt、実装後のraw evidence。
6. GitHub Issue body、generated projection、historical Issue #390 draft、旧single-Issue資料。

下位資料は上位contractを緩和、再定義、複製してはならない。矛盾時は停止し、親ownerへ`expected/actual/impact`を返す。

### 2.2 Entry state

GitHub connectorで次を直接確認済みである。

| Item | Verified state |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Issue branch | `iss-00396-build-once-provider-gate-and-regression-policy-cutover` |
| Branch full tip | `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` |
| Expected full SHA | 同上。byte-for-byte一致。 |
| Commit tree | `37eabc1aa250838dcd9f61d627309b0ff27e0db7` |
| GitHub #392 | CLOSED / completed |
| GitHub #395 | CLOSED / completed |
| GitHub #396 | OPEN |
| SpecDock dependency | `.meta.json`の`depends_on=["iss-00395"]`を維持 |

GitHub #396 bodyは「#395待ち、未開始、blocked」という過去projectionを含む。現在のentry事実を表さないため、canonical sourceとして複写しない。body更新は本成果物の範囲外であり、独立Strict review後に主担当が行う。

### 2.3 B1/B2 receiptの意味

B1/B2は同じsource/treeで成立した。詳細は`b1-b2-gate-receipt.md`とZIP内raw JSONを参照する。

- B1: ordinary pytest `1367 passed, 847 skipped`、lint GREEN、SpecDock validate `nodes=236`、#395のpublication security matrixとrow 12 guard GREEN。
- B2: 2214 collected、4 shard合計`2188 passed, 26 skipped`、`evaluation.verified=true`、15 total / 0 active / 15 resolved、14 fixed-in-place / 1 superseded、approved/unexpected 0。

これは#396 entry証拠であり、Linux canonical environment、build-once、five-run、seeded-fault、rolling twenty、required-context cutover、B3を証明しない。B1/B2のtransitional sharder/skip/evaluatorをB3証拠へ昇格しない。

### 2.4 Historical non-authority

- Issue #390はCLOSEDで、Reportが空のhistorical draftである。current policy authorityにしない。
- `src/spec_dock/assets/install_root/.github/workflows/ci.yml`はretained installed-consumer workflowのprovider-side authorityであり、Issue #390 draftだけを根拠に削除、改変、所有変更しない。
- root `.github/workflows/provider-full-regression.yml`はprovider main-push Full Regressionであり、上記installed-consumer workflowとは別物である。
- Initiative planは2026-04-10時点で#33/#59を優先し、Epic #384を列挙していない。利用者が#396を明示選択したため本Issueを進めるが、Initiative portfolioの改訂や優先順位変更は別governance follow-upであり、本Issueでは行わない。

## 3. Observable outcome

B3時点で、次の全てが同じfinal source上で成立する。

1. Candidate identityがexact source SHA/tree、parent-derived provider candidate digest、candidate manifest digest、wheel actual bytes digest、sdist actual bytes digestへ閉じている。
2. Candidateごとのpackaging build invocationがexactly oneで、全roleと全attemptが保存された同じwheel/sdist bytesをconsumeする。
3. 一つのattemptが一つのfinal-gate role graphを実行し、Linux canonical regressionはpytest root process 1、worker 1、shard 0である。
4. Linux canonicalのrootと全descendantを同じintervalで計測し、終了時に全descendantがreap済みである。
5. Environment contract `specdock-linux-qualification-v1`とaccepted fingerprintが初回測定前にfreezeされ、実効CPU/memory limitを証明できない環境はadmission failになる。
6. Parent `E384-QUAL-001`を生成projectionとmechanical evaluatorで実装し、first five、seeded-fault 100%、latest twentyをselectionなしで判定する。
7. Started failure、cancel、interruption、missing evidence、same-ID rerun、GitHub run attempt増分を履歴から除外、置換、相殺しない。
8. Replacement gate、test、evidence consumerが先に成立し、old consumer 0を証明した後、旧policy machineryが同一Issue PR内で削除される。
9. New required contextはold contextとno-gap coexistenceし、intentional REDでblockingを証明し、GREEN復旧後にold contextを人間が外し、final stateをreadbackする。
10. Final sourceでfull role graph、consumer-zero、protected-data、docs、dogfood/non-interferenceを再検証する。
11. Human merge後のexact integration SHAで、first five campaign、fault catalogue、latest twentyが成立し、B3 GREENとなる。

## 4. Scope and ownership

### 4.1 Owned write surfaces

| Surface | Ownership |
|---|---|
| Provider-gate implementation under `scripts/quality/provider_gate/` | #396 sole writer |
| Parent-policy generated projection and its generator | #396 sole implementation writer; parent Markdown remains normative |
| Provider final-gate workflow in `.github/workflows/provider-ci.yml` | #396 sole writer within this Issue |
| Root provider main-push Full Regression workflow removal | #396 sole writer |
| Old policy runtime/test modules and root data deletion | #396 sole writer after consumer-zero |
| Provider-gate tests and synthetic fault fixtures | #396 sole writer |
| Root provider operator guidance (`AGENTS.md`, `docs/provider-gate.md`) | #396 final-policy writer |
| External required-context migration evidence | #396 evidence owner; settings mutation is human-only |

### 4.2 Shared/read-only surfaces

| Surface | Rule |
|---|---|
| `src/spec_dock/provider_lifecycle/candidate.py` | `capture_packaged_candidate()`等をcandidate identityのread-only inputとして利用できる。semantic変更禁止。 |
| `src/spec_dock/provider_lifecycle/**`と`tests/unit/provider_lifecycle/**` | #392 lifecycle contract。read-only/non-regression。 |
| #395 Product behaviorと15-row register | read-only。row、signature、lifecycle、accepted behaviorを再編集しない。 |
| Epic R/D/P、Wire、register、accepted ADR | authority input。#396で編集しない。 |
| `tests/integration/test_epic_00343_distribution.py` | packaging roleのconsumerへ限定的に改修できるが、consumer/Product behaviorを変更しない。 |
| `tests/cli_runtime/test_distribution_cutover.py` | old test fileから移す非policy regressionの受け皿として限定改修可能。 |
| `pyproject.toml` | old lane marker削除と新test supportに必要な最小変更だけ。 |

### 4.3 No-touch surfaces

- `src/spec_dock/assets/install_root/.github/workflows/ci.yml`。
- root `.github/workflows/ci.yml`。両者のbyte identityを保つ。
- `spec-dock/initiatives/**`の#392/#395 canonical docs、Report、Artifacts、親contract。ただし本Issue R/D/Pを主担当が後でcanonical copyへ反映する作業は別gateである。
- `spec-dock/active/**`、`.meta.json`、dependency metadataの手編集。
- `spec-dock/.workbench`以外のconsumer-owned initiatives、Artifacts、Workbench、unknown paths、unrelated skills、consumer seeds。
- Product lifecycle wire value、record schema、migration/uninstall behavior、fixed roots/slots、bootstrap bytes。
- main、Epic integration branch、GitHub ruleset、branch protection、required-context settingsへのagent直接書込み。

## 5. Detailed requirements

### I396-RQ-001 — Exact entry admission

実装開始前にlocal HEAD、configured upstream、remote Issue branchがreview済みspecification freezeのfull SHAと一致し、clean worktree、#395 dependency closed、Issue #396 active selection、同時writerなしを確認する。B1/B2 entry identity `fd5df...` / `37eabc...`はprovenanceであり、後続spec-only commitとのdiffを明示する。identity不明、Product drift、dependency不一致では停止する。

### I396-RQ-002 — Parent policy single authority

`E384-QUAL-001`のmechanically extractable valueだけを`_qualification_policy_generated.py`へdeterministic生成する。生成元path、source blob/hash、requirement ID、抽出されたpredicate IDを同伴させ、`generate_provider_qualification_policy.py --check`が差分0を要求する。generated fileの手編集、別JSONでの独立閾値、workflow literalによる隠れた閾値を禁止する。

### I396-RQ-003 — Candidate identity and one build invocation

Candidate manifestは次を閉じる。

- repository、source SHA、source tree。
- `capture_packaged_candidate()`から得るprovider candidate digest。
- build invocation IDとexact top-level command。
- wheel filename/size/SHA-256、sdist filename/size/SHA-256。
- manifest core digest、final manifest digest、bundle digest。

一つのsource SHAに対しbuild producerは一つだけである。`uv build --sdist --wheel ...`のtop-level process invocationをcount 1とし、downstream role、rerun、別OSで再buildしない。missing artifact、複数producer、wrong source/tree、manifest mismatch、actual-byte mismatchはfail closedである。

### I396-RQ-004 — Artifact reuse and retention

最初のaccepted workflow runがcandidate bytesをuploadし、後続attemptはGitHub API/readbackでそのproducer run IDとartifact IDを解決して同じbytesをdownloadする。artifact retentionはB3 evidence readbackが完了するまでの期間を実装時にsource-controlled workflowへ明記し、actual API expiry/readbackを証拠化する。retention値を推測で決めず、current repository policyとActions上限をread-only captureしてから選択する。producer artifactが失われたcandidateを同じsource SHAでrebuildしない。

### I396-RQ-005 — One attempt / one role graph

各attemptはfresh owner-bound workspaceで、次のrole graphをexactly once実行する。

1. `candidate-resolve`
2. `static-analysis`
3. `linux-canonical`
4. `sdist-smoke`
5. `macos-delta`
6. `attempt-evaluate`

Role IDはevidence schemaでclosed enumとする。role欠落、重複、同一nodeのduplicate execution、別candidate bytes、別environment fingerprintを含むattemptはnon-acceptedである。five-runやrolling twentyを一つのattempt内で反復しない。

### I396-RQ-006 — Role ownership without policy skip

Source-controlled `role-ownership-v1.json`がtest path/node familyのownerを一意に定める。pytest pluginはrole外nodeをskip/xfailにせずdeselectし、role-owned nodeのcollection/executionをraw evidenceへ記録する。union coverage、intersection empty、unknown owner 0をmechanically検証する。旧`fast` / `full_regression` marker、`POLICY_SKIP_REASON`、`--run-full-regression`、`--full-regression-shard`をfinal sourceに残さない。

### I396-RQ-007 — Linux canonical topology and process lifecycle

Linux canonicalはone pytest root、worker 1、xdistなし、shardなしで実行する。collectorはroot spawn直前にmonotonic wall intervalを開始し、cgroup v2または同等に実効制限とchild-inclusive CPUを証明し、root exit後も全descendantが終了しreapされるまでintervalを閉じない。parent predicate違反時はprocess group/cgroupを停止・reapし、failure evidenceを残す。root-only CPU、子processの取りこぼし、残存process、二つ目のpytest rootはrejectする。

### I396-RQ-008 — Environment contract and fingerprint

`specdock-linux-qualification-v1.json`は、初回measurement前に次を固定する。

- runner provider/class、architecture。
- CPU model family、effective quota/limit。
- memory effective limit。
- OS release/image digest。
- Python、uv、pytest、dependency lock/tool versions。
- filesystem type/mount conditions。
- cgroup/collector version。

Parent能力境界を超えるrunner、GPU、high-performance tier、CPU burst/quota drift、上限を実効制限できない環境、fingerprint欠落はadmission failである。具体provider/class/imageがrepository evidenceから解決できない場合は創作せず、read-only capture + human gateで停止する。

### I396-RQ-009 — Attempt, campaign and window identity

- `attempt_id`はGitHub repository ID、workflow run IDからdeterministicに作り、`run_attempt=1`だけを受理する。
- `campaign_id`はcandidate identity、environment fingerprint、gate contract versionからdeterministicに作る。同じtupleで任意に取り直せない。
- `window_contract_id`はgate contract versionとenvironment version/fingerprintへ束縛する。
- chronologyはworkflow `created_at`とrun IDのtotal orderで決定し、結果時刻で並べ替えない。

Duplicate attempt ID、same-ID rerun、run-attempt増分、history rewriteをrejectする。

### I396-RQ-010 — Five-run population

Campaign freeze前にcandidate/campaign/environmentを事前登録し、chronological first exactly five independent attemptsのLinux canonical observationをpopulationとする。started failure、cancel、interruption、missing identity/raw evidenceは不合格memberとして残し、補充しない。各memberはparent projectionのwall/CPU/correctness predicateを独立評価し、平均、中央値、丸め、相殺を使用しない。

### I396-RQ-011 — Seeded-fault catalogue

`seeded-fault-catalogue-v1.json`はcandidate freeze時点でversioned/source-controlled/candidate-boundとし、denominatorを実行前に固定する。Gate自身のfail-closed boundaryをsynthetic fixtureで注入し、全entry実行・100% detectionを要求する。entry未実行、miss、post-observation denominator縮小はrejectする。fault campaignはcanonical Product suiteを反復実行せず、evaluator/collector/artifact/history boundaryを検証する。

### I396-RQ-012 — Rolling twenty stability

同じgate contract/environment versionへ事前登録されたlatest exactly twenty chronological final-gate attemptsをwindowとする。started failure/cancel/interruption/missing evidenceを残し、success filter、置換、相殺をしない。window<20はevidence incompleteで、正常なper-attempt resultをfailureへ書き換えないがB3を許可しない。各memberのper-attempt resultとwindow resultを別schemaで保持する。

### I396-RQ-013 — Intentional RED and recovery cost

New required contextのintentional REDはfive-run campaign freeze前に行い、rolling historyへfailure memberとして残す。RED後、latest twentyを全acceptedにするには二十件の新しいsuccessful attemptsが必要である。この導入コストをhistory削除、candidate ID再登録、rerun、同一attemptの再実行で隠さない。

### I396-RQ-014 — Actual-byte and API evidence

Evidence indexはtracked future factを書かず、実行時に次をraw保存する。

- source SHA/tree、manifestとwheel/sdist actual bytes hash。
- producer run/artifact API response、consumer run IDs。
- role result、pytest node inventory、process metrics、environment fingerprint。
- attempt/campaign/window/fault evaluation。
- artifact listing/download digest/readback。
- context/ruleset before/after readback。

File nameやclaimed digestだけでactual bytesを省略しない。auth token、credential、private absolute pathは保存しない。

### I396-RQ-015 — Consumer-first old policy retirement

Replacement code、tests、workflow role、evidence evaluatorを先にGREENにする。その後、AST/YAML/JSON/text-aware scannerでold consumer inventoryを0と証明してから、次を同一Issue PRで削除する。

- `full-regression-ledger.json`
- `full-regression-timing-weights.json`
- `scripts/quality/full_regression_baseline.py`
- `scripts/quality/verify_full_regression.py`
- `tests/conftest.py`のold lane/policy hook（内容がold policyのみならfile削除）
- `tests/unit/test_full_regression_baseline.py`
- old policy部分を持つ`tests/unit/test_provider_test_lanes.py`（非policy regressionは先に移設）
- `.github/workflows/provider-full-regression.yml`
- `pyproject.toml`の`fast` / `full_regression` marker定義
- `.github/workflows/provider-ci.yml`内のold provider jobs/commands

削除後のfinal sourceで全replacement gateを再実行する。old provider/dataを先に削除する中間状態、compat shim、old writer fallbackを禁止する。

### I396-RQ-016 — Retained workflow protection

root `.github/workflows/ci.yml`と`src/spec_dock/assets/install_root/.github/workflows/ci.yml`はretained installed-consumer workflowであり、存在・byte equalityをnegative/positive guardで維持する。#396が削除するのはroot provider main-push `.github/workflows/provider-full-regression.yml`である。pathの取り違えはP0 stopである。

### I396-RQ-017 — Required-context no-gap transition

Implementation前にcurrent effective required contexts、ruleset scope、merge queue有無、check-run namesをread-only captureする。外部名がrepositoryから分からない場合は創作しない。Humanだけが次を行う。

1. old requiredを維持したままnew contextを追加。
2. unrelated context集合とreview gateが不変であることをreadback。
3. new checkだけをintentional REDにし、merge blockを証明。
4. GREEN復旧。
5. old contextを除去。
6. final effective setとmerge queue scopeをreadback。

Agentはsettingsを書かず、captureされたbefore-stateとrollback instructionsを提供する。

### I396-RQ-018 — Docs, dogfood and protected data

Root provider guidanceからold ledger/shard/main-push Full Regression運用を除き、final gate、evidence、failure handlingへ更新する。Provider assetsに変更がない場合はdogfood projectionを不要とする理由とprovider candidate digest不変を記録する。もし実装中にshipped asset/doc変更が必要になった場合、provider sourceを先に変更し、`spec-dock update .`でcomplete dogfood candidateを同期し、partial projectionを禁止する。Protected data snapshotはbefore/afterで同一でなければならない。

### I396-RQ-019 — Verification and review separation

Specification review、implementation、code review、Final Quality Gate、human merge、post-merge B3を別gateとして記録する。実装後はclean pushed exact SHAに対して`chatgpt-code-review-strict`、その後`chatgpt-final-quality-gate-strict-v2`（Pro）を行う。過去review receiptを新candidateへ流用しない。

### I396-RQ-020 — Rollback, recovery and stop

Rollback unitはwhole #396 mergeである。Human merge前はIssue branchを修正/破棄できる。Human merge後、Epic main merge前は、external settingsをcaptured before-stateへ戻した上でwhole mergeをrevertし、B2 current-policy stateを完全に再構成してGREENを確認する。partial workflow/data/provider復元、automatic rollback、same-candidate retryは禁止する。Candidate/evidenceがpoisonedならsource SHAを変更して新candidateを作る。

## 6. Acceptance criteria

| AC | Observable fact | Primary evidence |
|---|---|---|
| AC-01 | Entry repo/branch/SHA/treeとB2がexact | `b1-b2-gate-receipt.md`, GitHub readback |
| AC-02 | Parent policy projectionがgenerated、diff 0 | generator `--check`, unit test |
| AC-03 | Candidate build invocation count 1、wheel/sdist actual bytes固定 | candidate manifest, producer API, hashes |
| AC-04 | 全roleが同じbytes/source/treeをconsume | role results, artifact verification |
| AC-05 | Linux canonicalが1 root/1 worker/no shard、descendant-inclusive | process metrics, process-tree tests |
| AC-06 | Environment capability/fingerprint固定、drift fail | environment receipt, boundary tests |
| AC-07 | first fiveがchronologicalで置換なし | campaign result + attempt registry |
| AC-08 | fault catalogue全件実行、detection 100% | fault-campaign result |
| AC-09 | latest twenty全member accepted、retry/rerun 0 | stability-window result, API history |
| AC-10 | unexpected/approved/policy-skip/duplicate 0 | per-attempt result |
| AC-11 | old consumer 0の後にold provider/data/workflow absent | scanner result, final tree |
| AC-12 | retained install-root workflow present/byte-identical | focused guard |
| AC-13 | new context RED blocks、GREEN復旧、old removal、final readback | human settings receipt |
| AC-14 | protected data不変、docs/final source整合 | snapshots, docs test |
| AC-15 | human merge後exact integration SHAでB3 GREEN | qualification result, B3 receipt |
| AC-16 | mainへのIssue direct merge、extra Issue、agent mergeなし | PR/readback evidence |

## 7. Requirement-to-component/test/evidence traceability

| Requirement | Component / data | Exact planned files / symbols | Tests | Acceptance evidence |
|---|---|---|---|---|
| I396-RQ-001 | identity admission | `scripts/quality/provider_gate/identity.py::resolve_repository_identity`, `register_attempt` | `tests/unit/provider_gate/test_identity.py` | identity receipt |
| I396-RQ-002 | policy projection | `scripts/maintenance/generate_provider_qualification_policy.py`, `_qualification_policy_generated.py` | `test_policy_projection.py` | generator diff 0 |
| I396-RQ-003–004 | build/provenance/reuse | `artifacts.py::{build_candidate_manifest,verify_candidate_bundle,resolve_producer_artifact}` | `test_artifacts.py`, role graph integration | candidate manifest/API readback |
| I396-RQ-005–006 | role ownership | `contracts/role-ownership-v1.json`, `pytest_plugin.py` | `test_role_ownership.py`, `test_provider_gate_role_graph.py` | role inventory/union/intersection |
| I396-RQ-007 | process lifecycle | `process_tree.py::{LinuxCgroupV2Collector,ProcessMeasurement}` | `test_process_tree.py`, fault integration | process metrics/reap proof |
| I396-RQ-008 | environment | `environment.py`, `specdock-linux-qualification-v1.json` | `test_environment.py` | environment fingerprint receipt |
| I396-RQ-009–010 | attempt/five-run | `history.py::{AttemptRegistry,select_first_five}` | `test_history.py` | campaign result |
| I396-RQ-011 | seeded faults | `seeded-fault-catalogue-v1.json`, `faults.py` | `test_fault_catalogue.py`, integration faults | fault campaign result |
| I396-RQ-012–013 | rolling window/RED | `history.py::select_latest_twenty`, `evaluator.py` | history boundary tests | stability result/API history |
| I396-RQ-014 | evidence codec/index | `contracts.py`, `codec.py`, `evidence.py` | schema/golden tests | evidence index/raw files |
| I396-RQ-015–016 | consumer-first retirement | `consumer_scan.py::scan_old_policy_consumers`, retirement contract | `test_consumer_inventory.py`, retained workflow guard | consumer-zero result/final tree |
| I396-RQ-017 | external context | `.github/workflows/provider-ci.yml`, human receipt template | workflow static tests + human canary | before/RED/GREEN/final readback |
| I396-RQ-018 | docs/protection | `AGENTS.md`, `docs/provider-gate.md`, snapshot helper | docs/guard tests | protected-data snapshot |
| I396-RQ-019–020 | review/rollback | handoff/Plan, no Product module | review/readback checks | Strict receipts, rollback receipt |

## 8. Non-goals and forbidden escapes

- Parent `E384-QUAL-001`、Epic R/D/P、Wire、register、#392/#395 contractの編集。
- Product defect、lifecycle behavior、migration/uninstall、candidate digest algorithmの変更。
- Additional worker、xdist、shard、retry、rerun、same attempt ID再実行、policy skip、approved failure、hardware escalation。
- Mean/median/p95/roundingや成功run選択によるparent predicate代替。
- macOS/platform deltaへLinux `<=600s` predicateを追加すること。
- Extra Issue、verification-only Issue、direct-main PR、integration branch direct push、agent merge、human merge gate removal。
- External context/ruleset名の創作、credential変更、認証設定の自動変更。
- Portfolio reprioritization、Initiative plan書換え。
- B3実装完了、qualification pass、context cutover完了を本仕様成果だけで主張すること。

## 9. Stop and return

次を観測したら、fallbackや値の再選択を行わず停止する。

- exact repository/branch/SHA/tree/dependency/B2の不一致。
- parent requirementからpolicy projectionを一意に生成できない。
- current external required set、runner provider/class、effective CPU/memory limit、image digestを確認できない。
- build producerを一意に解決できない、artifactが欠落/expired/mismatch。
- lifecycle/Product/15-row/protected data変更が必要。
- role ownershipが重複/欠落し、skipやshardなしで閉じない。
- process descendantsの計測/reapを証明できない。
- first fiveまたはlatest twentyのchronology/raw evidenceが欠落。
- fault catalogue detectionが100%でない。
- old consumerが1件以上残る、またはretained installed-consumer workflowへ削除が及ぶ。
- no-gap context移行、rollback、merge queue scopeが不明。
- independent specification reviewがpass/P0=0/P1=0でない。

Return payloadはcontract ID、expected、actual、evidence path/run ID、scope impact、必要owner/human actionを含める。`owner_decisions_required=[]`は現時点で未解決のProduct/Policy/Security decisionがないことを意味するが、上記read-only capture不足を推測で埋める許可ではない。

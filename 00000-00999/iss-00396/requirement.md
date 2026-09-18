---
種別: 要件定義書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
詳細化状態: "implementation-ready-awaiting-strict-rereview-and-b1-b2"
最終更新: "2026-09-18"
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
  sha: "4d68bce3f3ee977548a3c467476da39c15f43594"
  tree: "80ade10f57cd5f4140daa03ca8a40b844f1fcc53"
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 要件定義

## 1. 結論と現在位置

Issue #396は、親`E384-QUAL-001`を変更せず、Provider CIをbuild-once・same-candidate・one-role-graph-per-attemptのfinal gateへ切り替え、replacement consumerが成立してold consumerが機械的に0になった後にだけ旧ledger、timing、sharder、policy skip、policy hook、quality provider、provider main-push Full Regressionを同一Issue PRで撤去する実装単位である。

ただし、**現在のProduct実装許可はfalseである。** ユーザーが2026-09-18に示した最新の運用事実は「Issue #395の完了処理は行われたが、Epicが#396の前提とするB1/B2は実施されておらず、受入もされていない」である。従来のreceipt/raw JSONと親Plan §3.2の記述は歴史的主張としてbytesを保持するが、current admission authorityにはしない。

GitHub readbackで確認した#395 PR #401の人間merge identityは、source `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d`、tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7`であり、履歴上のidentityに限る。ユーザーは#395実装を誤りと報告しており、具体的defectと修正結果は未確認である。#395 ownerがIssue #395のscopeでdefectを修正・受入し、修正後のexact merged SHA/treeをGitHub readbackするまで、B1/B2 execution targetは存在しない。元merge SHA/tree、historical receipt、別SHAの結果をB1/B2 targetやacceptanceへ使ってはならない。Corrected targetでB1をfreshに受入した後、同じSHA/treeでB2をfreshに受入し、actual-byte evidenceとaccepted-state receiptを得る。Identity、log、raw evidenceまたはaccepted stateの一つでも検証できない場合は`StopReturnV1`で親ownerへ戻す。

Formal `issue start`、active branch、Issue OPEN/CLOSED、dependency readyはProduct実装許可と別状態である。Formal stateは巻き戻さず、仕様authoringだけを完了する。次の全gateが順に成立するまで、Product source、tests、workflow、policy data、GitHub settingsを変更しない。

1. 本完成仕様をcleanにIssue branchへpushし、same-Red reviewで`review_status=pass`、P0=0、P1=0を得る。P2/P3はreview contractに従う。
2. GitHub Issue #396 canonical projectionを更新し、readbackで一致を確認する。
3. #395 ownerがreported defectをIssue #395のscopeで修正・受入し、corrected exact merged SHA/treeをGitHub readbackする。
4. Corrected exact SHA/treeでfresh B1を受入する。
5. B1と同じSHA/treeでfresh B2を受入する。
6. Actual-byte evidenceと親ownerによるdefect disposition/B1/B2 acceptanceを記録する。
7. 仕様freeze SHA/treeがclean・pushed・exactで、同時writerがいないことを再確認する。
8. 別途のexplicit implementation dispatchを受領する。

Corrected SHA/tree、B1、B2のいずれにもoriginal #395 merge SHA/treeを代用しない。

本Issueはfinal provider qualificationの**実装・測定・証拠化**だけを所有する。量的値、population、window、aggregation、Linux performance scope、rejection、forbidden escapeの唯一のauthorityはEpic Requirementの`E384-QUAL-001`である。Issue artifact、workflow、Python、JSON schemaはmechanical projectionであり、第二のpolicy authorityになってはならない。

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

2026-09-18のStrict GitHub connector verificationで、次を直接確認した。

| Item | Verified state |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Issue branch | `iss-00396-build-once-provider-gate-and-regression-policy-cutover` |
| Verified Blue authoring-input identity | SHA `4d68bce3f3ee977548a3c467476da39c15f43594`, tree `80ade10f57cd5f4140daa03ca8a40b844f1fcc53` |
| #395 human merge PR | `#401` |
| #395 original human merge identity (historical) | SHA `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d`, tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7` |
| #395 implementation disposition | User-reported incorrect; defect details and corrective outcome are not independently verified |
| B1/B2 execution target | Blocked until the #395 owner corrects and accepts the implementation, then provides the exact merged SHA/tree |
| Issue #396 Product implementation | prohibited / not started |
| B1 acceptance | unresolved / not accepted |
| B2 acceptance | unresolved / not accepted |

Current branch tipはspec/evidence authoring candidateであり、predecessor merge tipやB1/B2 acceptance identityではない。`artifacts/b1-b2-admission-status-v2.json`がcurrent Issue-local admission statusを閉じる。GitHub #396 bodyの古いprojection、SpecDock dependency ready、#395 CLOSED、formal active selectionはB1/B2の代替にならない。

Owner correctionは「#395の実装が誤り」であることも示すが、具体的な不具合と修正結果はこのIssueのauthoring evidenceから確認できていない。#395の元merge SHAは履歴上のidentityだけで、正しいProduct baselineやB1/B2 execution targetとして扱わない。#395 ownerが不具合を#395のscope内で修正し、修正後のexact merged SHA/treeと受入根拠をGitHub readbackで提示するまでB1/B2 execution targetは未確定である。Issue #396は#395 Product codeや親文書を修正せず、欠けた情報を推測で補わない。

Parent Epic Plan §3.2とhistorical entry receiptの「B1/B2完了」記述は、今回のowner correctionと矛盾する。このIssue authoring taskでは親Plan/#395 docsを変更せず、矛盾をadmission hold理由として記録する。修正後の#395 tipでfresh B1/B2を実行し、親ownerが受入を記録するまで、Issue側は`not-accepted`を維持する。

### 2.3 B1/B2 historical artifactsとfresh acceptance

次の既存filesはbytesを改変せず保存する。

- `artifacts/20260917t124918z-01--b1-b2-gate-receipt.md`
- `artifacts/20260917t124918z-02--iss-00395-b2-full-regression-result.json`（SHA-256 `bd4630014ee046967713c89c7b8112a2ebe7f10aa85100256aca8a677d817786`）
- `artifacts/20260917t124919z--iss-00395-b2-ledger-before.json`（SHA-256 `838f1415f2a4399a3f18cf7914dc0b2f3648cb06a5d623de4ca7a22648a87a0d`）

これらは「当時その結果が主張された」こととraw bytesを証明するhistorical evidenceであり、current B1/B2 acceptanceを証明しない。Fresh acceptanceは`artifacts/b1-b2-verification-contract-v1.json`の順序、commands、expected output class、same-tip relationに従う。結果を事前に特定のpass countへ合わせず、actual stdout/stderr/exit/raw JSON/hashを保存する。

B1がacceptedになる前にB2を実行・受入してはならない。B2はaccepted B1と同じSHA/treeでなければならない。Fresh resultがhistorical claimと異なる場合、historical fileを書換えず、current StopReturnへexpected/actual/impactを記録する。

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
| #395 Product implementationと15-row register | read-only。implementation defectの修正やrow、signature、lifecycle、behaviorの再編集はIssue #396のscope外。現状はowner-reported incorrect / unaccepted。 |
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

Product実装前に、次の順で全条件を要求する。

1. `artifacts/b1-b2-admission-status-v2.json`を読み、#395 implementationがowner-reported incorrect、B1/B2が未実施・未受入である現状を確認する。旧receiptとraw JSONはhistorical claimとして保存し、current acceptanceへ転用しない。
2. Issue #396の完成仕様をcleanなIssue branchへcommit/pushし、local HEADとconfigured upstreamのfull SHA一致を確認する。
3. `iss396-spec-review-red`で同じ目的のStrict re-reviewを行い、`review_status=pass`、P0=0、P1=0を得る。P2/P3はreview contractに従う。
4. Pass後にIssue #396 bodyへcanonical projectionを適用し、GitHubから読み戻して一致を確認する。
5. #395 ownerがreported implementation defectを#395のscope内で修正・受入し、修正後のmerged SHA/treeをGitHub readbackした記録を取得する。Issue #396はこの修正を代行しない。
6. `b1-b2-verification-contract-v1.json`のtarget resolution ruleに従って、修正後のexact SHA/treeをP01 preflight evidenceへ固定する。元の#395 SHA/treeを代用しない。
7. 修正後の指定SHA/treeでB1をfresh実行・受入する。
8. 同じclean worktree、同じSHA/treeでB2をfresh実行・受入する。
9. Corrected #395 merge SHAがIssue #396の`SPEC_FREEZE_SHA`のancestorであることを`git merge-base --is-ancestor "$B12_TARGET_SHA" "$SPEC_FREEZE_SHA"`で確認する。ancestorでなければStopReturnでEpic integration/parent ownerへ戻し、Agentはmerge、rebase、cherry-pick、branch recreation、force pushを行わない。
10. B1/B2のactual-byte evidence index、accepted receipts、same-tip proofを生成し、親Epic ownerがreported defectの解消とgate結果の受入を記録する。
11. Current specification freezeのlocal HEAD、configured upstream、remote branch full SHAが一致し、worktree clean、同時writerなしであることを再確認する。
12. 別途のexplicit implementation dispatchを受け取る。

Ancestry checkがfalseの場合、Issue branchの統合方法はEpic integration contractに従う人間/parent ownerの判断へ戻す。明示的に許可されたbranch realignment後は、影響を受けたP02/P03などsource SHA/tree由来のcaptureとartifactを再生成し、ZIPを更新してcleanな新candidateを固定する。同じRed reviewとIssue projection readbackを新しいexact candidateでやり直す。B1/B2 receiptを再利用できるのはcorrected #395 SHA/treeが同一でevidenceが引き続き有効な場合だけである。

一つでも欠ける場合、formal start/active stateを変更せず実装を停止する。#395のreported defectが未解決、#395 CLOSED、Issue graph ready、historical raw bytes、別SHAのGREEN、過去reviewは代替にならない。B1/B2 failureまたは修正後#395 identityの欠落は#395 ownerへ戻し、Issue #396のProduct変更を開始しない。

### I396-RQ-002 — Parent policy single authority

`E384-QUAL-001`のmechanically extractable valueだけを`_qualification_policy_generated.py`へdeterministic生成する。生成元path、source blob/hash、requirement ID、抽出されたpredicate IDを同伴させ、`generate_provider_qualification_policy.py --check`が差分0を要求する。generated fileの手編集、別JSONでの独立閾値、workflow literalによる隠れた閾値を禁止する。

### I396-RQ-003 — One-time candidate materialization and campaign freeze

Candidate producerはfinal-gate attemptから分離した`CandidateMaterializationV1`である。Allowed transitionは`unmaterialized -> materializing -> materialized | poisoned`だけとする。

- Materializationはattemptではなく、attempt ID、campaign membership、first-population membership、rolling-window membershipを持たない。
- Source SHA/treeごとのpackaging build invocationはexactly oneである。
- `materialized`はcomplete source identity、provider candidate digest、manifest digest、wheel/sdist actual-byte digest、complete accepted environment fingerprint、candidate-bound evidence indexを要求する。
- Candidate bytesとenvironment identityがcompleteになる前にcampaignをfreezeしたりqualification attemptを登録してはならない。
- Materialization failure、cancel、missing producer artifact、identity mismatchはsource SHA/treeを`poisoned`にする。同じSHA/treeでのrebuild/retryは`SAME_SHA_REBUILD_ATTEMPTED`で拒否し、forward-fixしたnew source SHA/treeを要求する。
- PR sourceとhuman merge sourceが異なる場合、別candidateなのでmerge SHA/treeでone-time materializationを行う。同一sourceの再buildではない。

Materialization成功後、`CampaignFreezeV1`へcandidate identity、environment fingerprint、gate contract version、fault definition hash、window contract IDをimmutableに記録してから、最初のcampaign attemptを事前登録する。

### I396-RQ-004 — Two-stage evidence, actual bytes and retention

Evidenceをcandidate生成前後で分離する。

- `PreflightEvidenceIndexV1`: P00–P04、B1/B2、spec review、external read-only capture等。Candidate identity fieldを持たない。
- `CandidateEvidenceIndexV1`: materialized candidate/environmentへ束縛されたP05以後のevidence。
- 共通wireは`evidence_root_id`、evidence-root-relative logical POSIX path、size、actual-byte SHA-256を持つ。Private absolute path、credential、token、symlink traversal、dot/dot-dot、backslash、NULを保存しない。
- Physical workspace rootはruntime argumentでありwireへserializeしない。
- Source-controlled canonical artifactは`RepositoryArtifactRefV1`を使う。
- Missing/expired/mismatched artifact、claimed hash without bytes、wrong source/environmentはfail closed。
- Retentionはcampaign/window/rollback/auditが完了するまで全roleが同じwheel/sdist bytesを取得できる期間を必要とし、不十分なら`RETENTION_INSUFFICIENT`で拒否する。

### I396-RQ-005 — One attempt / one role graph

各attemptはfresh owner-bound workspaceで、次のrole graphをexactly once実行する。

1. `candidate-resolve`
2. `static-analysis`
3. `linux-canonical`
4. `sdist-smoke`
5. `macos-delta`
6. `attempt-evaluate`

Role IDはevidence schemaでclosed enumとする。role欠落、重複、同一nodeのduplicate execution、別candidate bytes、別environment fingerprintを含むattemptはnon-acceptedである。five-runやrolling twentyを一つのattempt内で反復しない。

### I396-RQ-006 — Immutable role baseline plus reviewed delta

`artifacts/role-ownership-v1.json`の2,214-node assignmentはimmutable baselineである。実装でbaselineを上書きしない。`artifacts/role-ownership-delta-v1.json`のexact 43 add、1 move、69 deleteをactivation checkpoint順に適用し、各checkpointの`ResolvedRoleOwnershipV1`を`role-ownership-checkpoints-v1.json`から検証する。Final populationは2,188 assignmentsであるが、これはparent qualification populationではなくtest ownership inventoryである。

- Wildcard、marker、directory prefix、runtime discoveryによるowner choiceは禁止する。
- New/moved/deleted nodeはtest body実行前にreviewed deltaへ存在しなければならない。
- Unknown node、duplicate owner、collection/hash mismatchはbody前にrejectする。
- Qualification role invocationはtest population全体をcollectし、full resolved checkpoint manifestと一致させてからrole filterを適用する。Focused checkpoint verificationは完全なnode IDだけを受け付け、実collectionと指定ID集合の完全一致、および各IDのownerをfull manifestで検証する。未指定のmanifest nodeはmissing扱いしない。File/directory/marker/glob/`-k`/`-m`/shard selectorは禁止し、focused結果はqualification evidenceに使わない。
- `pytest_plugin.py`が移行中・最終状態の恒久collection filter ownerである。
- Root `tests/conftest.py`はtemporary compatibility seamだけを所有し、exact plugin+role invocationでlegacy hookをbypassする。P15でlegacy hook/fileを削除した後もpluginの`pytest_collection_modifyitems`がsole filter ownerとして残る。
- Role外nodeはdeselectし、skip/xfailへ変換しない。Policy skip、approved failure、duplicate executionは0でなければならない。

### I396-RQ-007 — Linux canonical topology and process lifecycle

Linux canonicalはone pytest root、worker 1、xdistなし、shardなしで実行する。collectorはroot spawn直前にmonotonic wall intervalを開始し、cgroup v2または同等に実効制限とchild-inclusive CPUを証明し、root exit後も全descendantが終了しreapされるまでintervalを閉じない。parent predicate違反時はprocess group/cgroupを停止・reapし、failure evidenceを残す。root-only CPU、子processの取りこぼし、残存process、二つ目のpytest rootはrejectする。

### I396-RQ-008 — Environment contract and fingerprint

`specdock-linux-qualification-v1.json`は`artifacts/provider-gate-contracts-v1.schema.json#/$defs/EnvironmentFingerprintV1`の`linux-canonical` instanceとして、初回measurement前に次を固定する。

- runner provider/class、architecture。
- CPU model family、effective quota/limit。
- memory effective limit。
- OS release/image digest。
- Python、uv、pytest、dependency lock/tool versions。
- filesystem type/mount conditions。
- cgroup/collector version。

Parent能力境界を超えるrunner、GPU、high-performance tier、CPU burst/quota drift、上限を実効制限できない環境、fingerprint欠落はadmission failである。具体provider/class/imageがrepository evidenceから解決できない場合は創作せず、read-only capture + human gateで停止する。

### I396-RQ-009 — Attempt, materialization, campaign and window identity

Materialization IDとattempt IDを分離する。Every started final-gate attemptはcomplete candidate identity、environment fingerprint、window contract IDへ事前登録される。Campaign qualification purposeではcampaign IDもnon-nullである。Campaign freeze前のrequired-context canaryは`purpose=context-canary`、campaign ID null、window contract ID non-nullとしてrolling historyへ残す。

Same workflow runのrun-attempt増分、same attempt ID、artifact replacement、履歴行の上書きはrerun/retryとしてrejectし記録を残す。Per-attempt resultはcampaign/window completenessから独立し、started failure/cancel/interruption/missing evidenceを削除、置換、successとの相殺に使わない。

### I396-RQ-010 — Five-run population

Campaign freeze前にcandidate/campaign/environmentを事前登録し、chronological first exactly five independent attemptsのLinux canonical observationをpopulationとする。started failure、cancel、interruption、missing identity/raw evidenceは不合格memberとして残し、補充しない。各memberはparent projectionのwall/CPU/correctness predicateを独立評価し、平均、中央値、丸め、相殺を使用しない。

### I396-RQ-011 — Closed candidate-bound fault catalogue

`artifacts/seeded-fault-catalogue-v1.json`がfault denominatorの唯一のIssue-local definitionである。Exact 20 categories / 45 atomic entriesを持ち、各entryは`fault_id`、category、fixture、injector、finite expected violation code、detection stage、`RED-F001`〜`RED-F045`、exact first-RED test nodeを一対一で閉じる。

Implementation前にdefinition hash `7a73bcc44bcca28e734b704e2980d439e4edd161c996515ea45004d038f4bb8f`をfreezeし、materialization後に`CandidateBoundFaultCatalogueV1`へcandidate/environmentを結ぶ。Entry omission、unexecuted entry、denominator/order/expected-code変更、post-observation shrinkを禁止する。First REDは45 entriesを全件enumerateし、production workflowへfree-form fault flagを残さない。Detection結果はparent contractのmechanical projectionで評価する。

### I396-RQ-012 — Rolling twenty stability

同じgate contract/environment versionへ事前登録されたlatest exactly twenty chronological final-gate attemptsをwindowとする。started failure/cancel/interruption/missing evidenceを残し、success filter、置換、相殺をしない。window<20はevidence incompleteで、正常なper-attempt resultをfailureへ書き換えないがB3を許可しない。各memberのper-attempt resultとwindow resultを別schemaで保持する。

### I396-RQ-013 — Intentional RED and recovery cost

New required contextのintentional REDはfive-run campaign freeze前に行い、rolling historyへfailure memberとして残す。RED後、latest twentyを全acceptedにするには二十件の新しいsuccessful attemptsが必要である。この導入コストをhistory削除、candidate ID再登録、rerun、同一attemptの再実行で隠さない。

### I396-RQ-014 — Closed schema families and finite violation inventory

`provider-gate-contracts-v1.schema.json`はDraft 2020-12のclosed familyとして、少なくとも次を定義する。

- materialization / campaign freeze / source / candidate / environment
- preflight / candidate-bound evidence workspace/index/blob reference
- immutable baseline / delta / resolved ownership
- node execution / NodeObservation
- fault definition / candidate binding / execution result
- old-policy retirement / consumer scan
- required-context snapshots / transition receipt
- attempt / role / process / per-attempt / aggregate result
- `StopReturnV1`

`ViolationCodeV1`は`closed-violation-codes-v1.json`のfinite 68-code inventoryだけを許可し、open regexやfree-form codeを禁止する。Actual bytes、API metadata、source/tree、manifest/artifact/environment、node/process/resultを同じidentityへ結び、file nameやclaimed digestだけのevidenceを受理しない。

### I396-RQ-015 — Consumer-first old policy retirement and permanent filter ownership

`old-policy-retirement-v1.json`のfinite signaturesをAST/YAML/JSON/text-aware scannerで検査する。Replacement modules、tests、permanent pytest plugin、workflow roles、evidence evaluatorを先にGREENにし、全consumerをmigrateし、`ConsumerScanResultV1.scan_complete=true`かつ`old_consumer_count=0`、retained workflow byte equality、required-context new-only readbackが成立した後だけold provider/data/workflow/testsを削除する。

Temporary root `tests/conftest.py` seamはplugin registrationとrole contractがvalidな場合だけlegacy hookをbypassする。Plugin自身が恒久的にfilter hookを実装するため、P15でroot old hook/fileを削除してもrole ownership/filteringは失われない。Old provider/dataを先に削除する中間state、compat shim、old writer fallbackは不合格である。Final sourceでscanner、ownership、role graph、ordinary suite、lint、protected workflow guardを再実行する。

### I396-RQ-016 — Retained workflow protection

root `.github/workflows/ci.yml`と`src/spec_dock/assets/install_root/.github/workflows/ci.yml`はretained installed-consumer workflowであり、存在・byte equalityをnegative/positive guardで維持する。#396が削除するのはroot provider main-push `.github/workflows/provider-full-regression.yml`である。pathの取り違えはP0 stopである。

### I396-RQ-017 — Required-context no-gap transition

Implementation前にcurrent effective required contexts、ruleset scope、merge queue有無、check-run namesをread-only captureする。外部名がrepositoryから分からない場合は創作しない。Humanだけが次を行う。

1. old requiredを維持したままnew contextを追加。
2. unrelated context集合とreview gateが不変であることをreadback。
3. new checkだけをintentional REDにし、merge blockを証明。
4. new checkをGREENへ復旧し、replacement consumerの移行とconsumer-zeroを証明。
5. old check emitterがbranch上にまだ存在する間に、Humanがold required contextだけを除去。
6. `U + new`、merge-queue scope、required check readbackを確認する。active merge queueではPR headと`merge_group`をそれぞれ確認する。
7. readbackが`U + new`である場合に限り、Issue branchからold check emitterを含むold workflow/jobを削除する。

Agentはsettingsを書かず、captureされたbefore-stateとrollback instructionsを提供する。必要設定が読めない場合はhuman readbackを待ち、403や空配列を「required contextなし」と解釈しない。

### I396-RQ-018 — Docs, dogfood and protected data

Root provider guidanceからold ledger/shard/main-push Full Regression運用を除き、final gate、evidence、failure handlingへ更新する。Provider assetsに変更がない場合はdogfood projectionを不要とする理由とprovider candidate digest不変を記録する。もし実装中にshipped asset/doc変更が必要になった場合、provider sourceを先に変更し、`spec-dock update .`でcomplete dogfood candidateを同期し、partial projectionを禁止する。Protected data snapshotはbefore/afterで同一でなければならない。

### I396-RQ-019 — Verification and review separation

Specification review、implementation、code review、Final Quality Gate、human merge、post-merge B3を別gateとして記録する。実装後はclean pushed exact SHAに対して`chatgpt-code-review-strict`、その後`chatgpt-final-quality-gate-strict-v2`（Pro）を行う。過去review receiptを新candidateへ流用しない。

### I396-RQ-020 — Truthful stop, rollback and recovery

唯一のstop wireは`StopReturnV1`である。Pre/post mutation双方について、checkpoint、finite reason code、violations、stage-correct evidence index、scope impact、required owners/actions、`mutation_performed`、changed surfaces、external changes、rollback/recovery statusを必須化する。`automatic_rollback_performed`は常にfalseである。

Pre-mutation stopはchange arraysを空にする。P11 workflow push後、P13/P14 human settings change後、P15 deletion後、P21 attempt start後などpost-mutation stopは実施済みchangesを隠さず、ownerとmanual recovery/whole-merge revert/forward-fixを記録する。Candidate poisoningはsame-SHA retryでなくnew sourceへforward-fixする。Issue merge rollbackはwhole mergeで、partial policy/workflow/data restoreをaccepted stateにしない。

B1/B2未受入、same-Red fail、projection unread、explicit dispatchなしでは常にpre-implementation stopである。

## 6. Acceptance criteria

| AC | Observable fact | Primary evidence |
|---|---|---|
| AC-00 | #395 reported implementation defectが#395 ownerにより修正・受入され、corrected merge SHA/treeがGitHub readbackどおりで、corrected merge SHAがIssue #396の`SPEC_FREEZE_SHA`のancestor | #395 correction/acceptance receipt + corrected commit/tree readback + `git merge-base --is-ancestor` result in `PreflightEvidenceIndexV1` |
| AC-01 | B1がfresh executionでaccepted | `b1-b2-verification-contract-v1.json`, PreflightEvidenceIndexV1, accepted receipt |
| AC-02 | B2がaccepted B1とsame exact tipでfresh accepted | raw verifier bytes, 15/0/15 relation, accepted receipt |
| AC-03 | same-Red review pass、P0/P1=0。P2はrecord-only | review JSON/session receipt |
| AC-04 | Issue projection readbackとexplicit dispatchが別々に成立 | GitHub readback, dispatch receipt |
| AC-05 | Materializationがattemptから分離し、one build、complete candidate/environment後にfreeze | CandidateMaterializationV1, CampaignFreezeV1 |
| AC-06 | Same-SHA materialization failureはpoison、rebuild拒否 | violation evidence `MATERIALIZATION_POISONED` / `SAME_SHA_REBUILD_ATTEMPTED` |
| AC-07 | Preflight/Candidate evidenceがstage-correct、logical path/size/hashだけ | schema validation, actual-byte index |
| AC-08 | 2,214 baseline + exact 43 add/1 move/69 deleteを決定的に導出 | baseline, delta, checkpoint manifests, final 2,188 manifest |
| AC-09 | Pluginが移行中/最終のsole permanent filter ownerであり、full qualificationとexact-node focused collectionを正しく区別 | transition/final ownershipとqualification/focused-selector tests |
| AC-10 | Closed 45-entry fault catalogueを全件実行・検出 | definition/binding/execution results |
| AC-11 | Violation、node、scan、retirement、context、stop schemasがclosed | Draft 2020-12 schema + finite code inventory |
| AC-12 | Parent-generated predicatesをper-attempt/campaign/windowへ適用 | generator `--check`, evaluator tests |
| AC-13 | Old consumer 0の後だけold provider/data/workflow absent | retirement contract, complete scan, final tree |
| AC-14 | Retained installed-consumer workflowが存在・byte-identical | protected workflow guard |
| AC-15 | Required contextがno-gapでRED block/GREEN/new-only/final readback | ContextTransitionReceiptV1; settings writerはhuman |
| AC-16 | Protected data、#392/#395 behavior、parent policy不変 | before/after snapshot and no-touch diff |
| AC-17 | Post-merge materialization/campaign/fault/windowによりB3を評価 | final qualification result; authoring段階では未実施 |

## 7. Requirement-to-component/test/evidence traceability

| Requirement | Component/data | Exact files/symbols | First/negative tests | Exit evidence |
|---|---|---|---|---|
| RQ-001 | predecessor correction/admission | `b1-b2-admission-status-v2.json`, `b1-b2-verification-contract-v1.json` | unresolved defect/original-SHA fallback/wrong tree/different B2 SHA/missing raw log/corrected merge not ancestor of spec freeze | #395 owner correction receipt, exact corrected-tip readback, ancestry proof, accepted B1/B2 preflight indexes |
| RQ-002 | parent projection | generator, `_qualification_policy_generated.py` | hidden literal/parent drift | generator diff 0 |
| RQ-003 | materialization/freeze | `CandidateMaterializationV1`, `CampaignFreezeV1`, `artifacts.py` | producer failure, same-SHA rebuild, incomplete env | materialization + freeze records |
| RQ-004 | evidence stages | `EvidenceWorkspaceV1`, `PreflightEvidenceIndexV1`, `CandidateEvidenceIndexV1` | absolute/dotdot/symlink/hash mismatch | actual-byte indexes |
| RQ-005 | one role graph | workflow, `RoleResultV1`, evaluator | missing/duplicate role | per-attempt result |
| RQ-006 | ownership/plugin | baseline, delta, checkpoints, `pytest_plugin.py`, temporary `tests/conftest.py` seam | unknown/duplicate/unplanned/P15-owner-survival | resolved ownership/hash |
| RQ-007–008 | topology/env | `process_tree.py`, `environment.py` | leak/reap/root/worker/shard/drift/limit | process and environment evidence |
| RQ-009–013 | attempt/history/aggregates | `history.py`, `evaluator.py`, parent projection | rerun/cancel/missing/replacement/filter | attempt/campaign/window results |
| RQ-011 | fault campaign | 45-entry catalogue, `faults.py` | `RED-F001`–`RED-F045` | candidate-bound fault results |
| RQ-014 | closed schemas/codes | schema + `closed-violation-codes-v1.json` | unknown field/code/type/order | schema/golden receipt |
| RQ-015–016 | consumer-first/protection | retirement contract, `consumer_scan.py` | one remaining match, retained missing/mismatch | zero scan + retained equality |
| RQ-017 | context transition | snapshots/receipt/workflow | RED not blocking, U drift, merge-group missing | human readbacks |
| RQ-018 | docs/protected | `AGENTS.md`, `docs/provider-gate.md`, snapshot helper | protected drift | before/after equality |
| RQ-019–020 | review/stop/recovery | execution packet, StopReturnV1 | pre/post mutation examples | review receipts/stop records |

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

次を観測したら、fallbackやgate免除を行わず`StopReturnV1`で停止する。

- #395 merge SHA/tree、B1/B2 same-tip execution、raw evidence、accepted stateの欠落・不一致。
- corrected #395 merge SHAがIssue #396 specification freezeのancestorでない、またはbranch history realignmentに人間/parent ownerの明示的 dispositionがない場合。
- historical receipt、Issue graph ready、#395 CLOSED、別SHA結果でB1/B2を代替しようとした場合。
- same-Red reviewがpass/P0=0/P1=0でない、projection readbackまたはexplicit dispatchがない場合。
- parent `E384-QUAL-001`をsemantic変更、duplicate authority、hidden thresholdなしにprojectできない場合。
- materialization producer一意性、actual bytes、environment identity、retentionを閉じられない場合。
- poisoned source SHA/treeを再buildする必要がある場合。
- baseline/delta/checkpoint ownershipにunknown/duplicate/unplanned nodeがある場合。
- plugin sole filterをP15後まで維持できない場合。
- 45 fault entriesの一つでも未実行/未検出/denominator driftの場合。
- started failure/cancel/missing/rerunをhistoryから除外しなければpassできない場合。
- old consumerが残る、retained installed-consumer workflowへ削除/変更が及ぶ場合。
- external context/ruleset/merge queueをreadbackできない、no-gapやrollbackを証明できない場合。
- Product/lifecycle/15-row/protected data/parent policyの変更が必要な場合。

StopReturnはpre/post mutationの事実を区別し、scope impact、owner、required action、changed surfaces、external changes、rollback/recovery statusを記録する。Cause未特定は推測で埋めず、evidence不足としてparent ownerへ返す。Automatic rollbackは禁止する。

`owner_decisions_required=[]`は、現在のP1六件に追加のProduct/Policy/Security decisionが不要であることだけを意味する。B1/B2、review、external readback等の未完了gateを省略する意味ではない。

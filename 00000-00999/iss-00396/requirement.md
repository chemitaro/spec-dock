---
種別: 要件定義書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "approved"
詳細化状態: "scope-simplified; product-implementation-gated"
最終更新: "2026-09-19"
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

ただし、**現在のProduct実装許可はfalseである。** #395のA395-SEC-001資格情報漏えい修正PR #403は2026-09-18にEpic integration branchへ人間mergeされ、corrected merge SHA `3c69af78843b04a13bde2f93eb3b1eb4081cdb33` / tree `38e2f9a50f7cae14ef24fa1187a559c592729e3b`としてGitHubからreadbackした。これは未対応schemeのpush URL拒否診断に資格情報が漏れる具体的なIssue #395内のdefectを修正する。別途報告された具体性のない症状とA395-SEC-001が同一であるとは推定しない。

Corrected targetでfresh B1を実行し親ownerが受入済みである。続けて同じSHA/tree・同じpersistent shellでfresh B2を実行し、private TMPDIRを指定した2回目の実行を親ownerが受入済みである。B2の初回実行はmacOS既定のsymlinked temporary rootで`unsafe-repository-binding`となったため、失敗証拠を保持し、実行target・verifier・shard count・acceptance criteriaを変えずにprivate TMPDIRで再実行した。成功結果は2,216件中2,191 passed / 25 skipped、15 resolved、0 violationsである。両receipt、親owner acceptance、actual-byte evidenceはIssue-local Workbenchに保存した。

許可されたbranch realignmentでcorrected merge SHAを#396 branchへ統合した。統合merge commit `a7f66ca5f8ca2e0571505ac8bf2466144186f769` / tree `38e2f9a50f7cae14ef24fa1187a559c592729e3b`はpre-realignment Issue commit `59da598a6352c447711399d3a1adab871e6b4a8a` / tree `dfcc40204df51930d446aa65d343a5549857e381`と異なり、PR #403が変更した7 pathを含む。変更はA395-SEC-001 correctionに属する。Issue #396のS1–S5実装は未開始である。実装用specification freezeのSHA/treeはこの簡素化版R/D/Pを確定してから別途固定する。新freezeはそのexact SHA/treeでsame-Red Strict reviewを再実施し、GitHub Issue projectionをreadbackする必要がある。過去reviewのpassを新freezeのreview passとして扱わない。**現時点の`実装開始許可`はfalseのまま維持する。**

Formal `issue start`、active branch、Issue OPEN/CLOSED、dependency readyはProduct実装許可と別状態である。Formal stateは巻き戻さず、仕様authoringだけを完了する。次の全gateが順に成立するまで、Product source、tests、workflow、policy data、GitHub settingsを変更しない。

1. 現在のcorrected #395 merge PR #403 SHA/treeをGitHub readback済み。A395-SEC-001を修正・mergeした。別途報告された未特定症状との同一性は主張しない。
2. 同一corrected SHA/treeでfresh B1、その後same-tip B2を実行し、両方とも親owner受入済み。raw bytes、失敗した初回B2、成功再実行、受入記録をactual-byte indexに保存する。
3. Corrected #395 merge SHAがIssue branchの祖先であることをbranch realignment後に確認済み。最終仕様freeze SHAに対しても再確認する。
4. R/D/Pと必要なcurrent artifactを更新し、cleanな新freeze SHA/treeを固定する。
5. 新freeze SHA/treeでsame-Red Strict reviewを再実施し、P0/P1=0のpass receiptを得る。
6. review pass後、GitHub Issue #396 canonical projectionを新freezeへ更新し、bodyをreadbackして一致を確認する。
7. 新freeze SHA/tree、configured upstream、GitHub branch tipの完全一致、clean worktree、同時writer不在を確認する。
8. Userから受領済みの明示的実装dispatchを確認し、以上の全gateが揃うまでProduct source、tests、workflow、policy data、GitHub settingsは変更しない。

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
| #395 original human merge PR (historical) | `#401`; SHA `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d`, tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7` |
| #395 corrected human merge | PR `#403`; SHA `3c69af78843b04a13bde2f93eb3b1eb4081cdb33`, tree `38e2f9a50f7cae14ef24fa1187a559c592729e3b`; A395-SEC-001 corrected and merged |
| Separate reported symptom | Its relationship to A395-SEC-001 is unverified; no identity claim is made |
| B1 acceptance | accepted by parent owner on corrected SHA/tree; 1,368 passed / 848 skipped ordinary suite, lint and SpecDock validation passed, parity 524 passed |
| B2 acceptance | accepted by parent owner on same SHA/tree; attempt 2 verified 2,216 tests (2,191 passed / 25 skipped), 15 resolved, 0 violations; default-temp attempt 1 retained as environment failure |
| Corrected merge ancestry | verified after authorized realignment; final specification freeze proof remains part of new freeze capture |
| Issue #396 Product implementation | prohibited / not started pending new freeze review and projection readback |

Current branch tipはspec/evidence authoring candidateであり、predecessor merge tipやB1/B2 acceptance identityではない。`artifacts/b1-b2-admission-status-v2.json`がcurrent Issue-local admission statusを閉じる。GitHub #396 bodyの古いprojection、SpecDock dependency ready、#395 CLOSED、formal active selectionはB1/B2の代替にならない。

A395-SEC-001は#395のaccepted scope内で再現・修正され、PR #403のmergeによりEpic integration branchへ入った。Issue #395はユーザーの指示どおりOPENのままであり、これをclosedとは扱わない。Issue #395のgeneric body/commentには別途報告された症状の詳細がないため、A395-SEC-001との同一性は未確認として残す。元PR #401 merge SHA/treeは歴史上のidentityだけであり、B1/B2 targetには使用しない。

Corrected PR #403 merge `3c69af78843b04a13bde2f93eb3b1eb4081cdb33` / tree `38e2f9a50f7cae14ef24fa1187a559c592729e3b`でfresh B1とB2を順に実行し、親owner受入を取得した。B2のsymlinked-default-TMPDIR失敗は保持し、private TMPDIRでの同一target retryを成功証拠として区別した。B1/B2 raw bytes、実行結果、acceptance、ancestry記録はIssue #396のignored Workbench evidenceに保存する。親文書のhistorical記述や旧raw artifactsは書き換えない。

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
| #395 Product implementationと15-row register | read-only。PR #403のA395-SEC-001 correctionと同一corrected tip上のB1/B2は受入済みであり、GitHub Issue #395はユーザー指示によりOPENのまま保持する。#396は#395の実装・register・Issue stateを修正、再実装、closeしない。 |
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

1. `artifacts/b1-b2-admission-status-v2.json`とfresh evidence indexを読み、PR #403 corrected merge identity、A395-SEC-001 correction、親owner accepted B1/B2、actual-byte receiptsを確認する。PR #401の旧receipt/raw JSONはhistorical claimとして保持しcurrent acceptanceへ転用しない。
2. Issue #396の完成仕様をcleanなIssue branchへcommit/pushし、local HEADとconfigured upstreamのfull SHA一致を確認する。
3. 簡素化後のR/D/Pを対象にsame-Red Strict reviewを行い、review_status=pass、P0=0、P1=0を確認する。P2/P3はreview methodに従い情報として保持し、旧review receiptは歴史として保持して新freezeのreview passへ流用しない。
4. Pass後にIssue #396 bodyへcanonical projectionを適用し、GitHubから読み戻して一致を確認する。
5. #395 ownerがreported implementation defectを#395のscope内で修正・受入し、修正後のmerged SHA/treeをGitHub readbackした記録を取得する。Issue #396はこの修正を代行しない。
6. `b1-b2-verification-contract-v1.json`のtarget resolution ruleに従って、修正後のexact SHA/treeをEvidenceIndexへ固定する。元の#395 SHA/treeを代用しない。
7. 修正後の指定SHA/treeでB1をfresh実行・受入する。
8. 同じclean worktree、同じSHA/treeでB2をfresh実行・受入する。
9. Corrected #395 merge SHAがIssue #396の`SPEC_FREEZE_SHA`のancestorであることを`git merge-base --is-ancestor "$B12_TARGET_SHA" "$SPEC_FREEZE_SHA"`で確認する。ancestorでなければStopReturnでEpic integration/parent ownerへ戻し、Agentはmerge、rebase、cherry-pick、branch recreation、force pushを行わない。
10. B1/B2のactual-byte evidence index、accepted receipts、same-tip proofを生成し、親Epic ownerがreported defectの解消とgate結果の受入を記録する。
11. Current specification freezeのlocal HEAD、configured upstream、remote branch full SHAが一致し、worktree clean、同時writerなしであることを再確認する。
12. 別途のexplicit implementation dispatchを受け取る。

Ancestry checkがfalseの場合、Issue branchの統合方法はEpic integration contractに従う人間/parent ownerの判断へ戻す。明示的に許可されたbranch realignment後は、影響を受けたexternal captureとartifactを再生成し、cleanな新candidateを固定する。同じRed reviewとIssue projection readbackを新しいexact candidateでやり直す。B1/B2 receiptを再利用できるのはcorrected #395 SHA/treeが同一でevidenceが引き続き有効な場合だけである。

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

### I396-RQ-004 — Evidence, actual bytes and retention

Evidenceは一つのappend-only `EvidenceIndexV1`で管理し、各entryに`binding_scope=preflight|candidate`を持たせる。Preflight entryではcandidate identityを禁止し、candidate entryではcandidate identityとenvironment fingerprintを要求する。共通entryは`evidence_root_id`、root-relative logical POSIX path、size、actual-byte SHA-256だけを持ち、private absolute path、credential、token、symlink traversal、dot/dot-dot、backslash、NULを保存しない。

Physical workspace rootはruntime argumentでありwireへserializeしない。Source-controlled artifactは`RepositoryArtifactRefV1`で参照する。Missing/expired/mismatched artifact、claimed hash without bytes、wrong source/environmentはfail closedする。Retentionはcampaign/window/rollback/auditが完了するまで同じwheel/sdist bytesを取得できる期間を必要とし、不十分なら`RETENTION_INSUFFICIENT`で拒否する。Preflightとcandidate evidenceの意味上の分離は維持するが、同じ情報を二つのschema familyへ複製しない。

### I396-RQ-005 — One attempt / one role graph

各attemptはfresh owner-bound workspaceで、次のstage graphを順序どおりexactly once実行する。`candidate-resolve`と`attempt-evaluate`はpytest execution roleではなく、各々`CandidateResolutionV1`とterminal `AttemptResultV1`を生成する制御stageである。`static-analysis`、`linux-canonical`、`sdist-smoke`、`macos-delta`だけが`RoleResultV1`を生成するexecution roleである。Candidate materialization/buildはattempt外の一回限りのproducerであり、このstage graphに含めない。

1. `candidate-resolve`
2. `static-analysis`
3. `linux-canonical`
4. `sdist-smoke`
5. `macos-delta`
6. `attempt-evaluate`

Stage IDはevidence schemaの`AttemptStageIdV1` closed enum、execution role IDは`ExecutionRoleIdV1` closed enumとする。`candidate-resolve`は事前登録済みattempt identityに対応するcompleted materialization、candidate evidence index、manifestおよび実artifact bytesをread-onlyで照合し、candidate identityとenvironment fingerprintの一致を`CandidateResolutionV1`へ記録する。resolveはbuildせず、materialization producerの再実行やartifact置換を行わない。`attempt-evaluate`はresolve結果と4つのexecution-role resultを集約し、唯一のterminal `AttemptResultV1`を出力する。Resolve失敗時は後続executionを開始せず、evaluatorが全4 role slotを`rejected`または`missing-evidence`としてhashなしで記録し、AttemptResultをnon-acceptedにする。Candidate resolution不成立・欠落、stage/roleの欠落・重複、同一nodeのduplicate execution、別candidate bytes、別environment fingerprintを含むattemptはnon-acceptedである。five-runやrolling twentyを一つのattempt内で反復しない。

### I396-RQ-006 — Immutable role baseline plus reviewed delta

`artifacts/role-ownership-v1.json`をimmutable baseline、`artifacts/role-ownership-delta-v1.json`をordered reviewed deltaとして扱う。各実行時のownershipはbaselineへ必要なdelta prefixを決定的に適用して生成し、source-controlledなfull checkpoint assignmentやresolved-final assignmentを別の正本として保持しない。既存のcheckpoint/final JSONは履歴・比較用のderived evidenceとして扱い、実装入力にしない。

Baseline/deltaの正確なfile bytes（末尾LFを含む）のSHA-256と、実collectionのnode-ID集合`collection_sha256`は別々に検証する。Wildcard、marker、directory prefix、runtime discoveryによるowner choiceは禁止する。New/moved/deleted node、unknown node、duplicate owner、collection/hash mismatchはtest body実行前にrejectする。Full qualificationは全体をcollectしてからrole filterを適用し、focused engineering checkは完全なnode ID集合だけを受け付ける。Role外nodeをskip/xfailへ変換せず、policy skip、approved failure、duplicate executionは0とする。`pytest_plugin.py`は移行中・最終状態のsole filter ownerとして残す。

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

`artifacts/seeded-fault-catalogue-v1.json`がfault denominatorの唯一のIssue-local definitionである。Candidate freeze時点のfile bytesとSHA-256を固定し、全entryを実行してdetection 100%を要求する。各entryは`fault_id`、category、fixture/injector、detection stage、candidate binding、actual evidenceへ束縛する。現在のreviewed catalogueは45 entriesを持つが、件数や`RED-Fxxx`番号はこのIssueの実装inventoryから導出する値であり、Epicのquantitative contractとして別途固定しない。Entry omission、unexecuted entry、order/expected-stage変更、post-observation denominator shrinkを禁止し、production workflowへfree-form fault flagを残さない。Detection結果はparent contractのmechanical projectionで評価する。

### I396-RQ-012 — Rolling twenty stability

同じgate contract/environment versionへ事前登録されたlatest exactly twenty chronological final-gate attemptsをwindowとする。started failure/cancel/interruption/missing evidenceを残し、success filter、置換、相殺をしない。window<20はevidence incompleteで、正常なper-attempt resultをfailureへ書き換えないがB3を許可しない。各memberのper-attempt resultとwindow resultを別schemaで保持する。

### I396-RQ-013 — Intentional RED and recovery cost

New required contextのintentional REDはfive-run campaign freeze前に行い、rolling historyへfailure memberとして残す。RED後、latest twentyを全acceptedにするには二十件の新しいsuccessful attemptsが必要である。この導入コストをhistory削除、candidate ID再登録、rerun、同一attemptの再実行で隠さない。

### I396-RQ-014 — Closed persisted records and finite operational failures

Closed JSON schemaはcross-jobまたはpost-runで永続化するCandidate、Attempt、Qualification、Cutover、Stopのrecordと共通evidence referenceへ適用する。内部helper state、checkpoint作業状態、authoring statusはcode-level typeまたはnon-normative evidenceとし、runtime schema familyへ複製しない。Violation codeはacceptance decisionまたはrecovery分岐に使うstable operational familyへ限定し、faultの具体性は`fault_id`、category、detection stageで表す。Unknown/free-form operational codeは受理せず、actual bytes、source/tree、manifest/artifact/environment、node/process/resultのidentityをclaimed filenameやdigestだけで代用しない。

### I396-RQ-015 — Consumer-first old policy retirement and permanent filter ownership

`old-policy-retirement-v1.json`のfinite signaturesをAST/YAML/JSON/text-aware scannerで検査する。Replacement modules、tests、permanent pytest plugin、workflow roles、evidence evaluatorを先にGREENにし、全consumerをmigrateし、`ConsumerScanResultV1.scan_complete=true`かつ`old_consumer_count=0`、retained workflow byte equality、required-context new-only readbackが成立した後だけold provider/data/workflow/testsを削除する。

Temporary root `tests/conftest.py` seamはplugin registrationとrole contractがvalidな場合だけlegacy hookをbypassする。Plugin自身が恒久的にfilter hookを実装するため、consumer-zero後のretirement phaseでroot old hook/fileを削除してもrole ownership/filteringは失われない。Old provider/dataを先に削除する中間state、compat shim、old writer fallbackは不合格である。Final sourceでscanner、ownership、role graph、ordinary suite、lint、protected workflow guardを再実行する。

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

Pre-mutation stopはchange arraysを空にする。Shadow workflow push後、human settings change後、retirement deletion後、attempt start後などpost-mutation stopは実施済みchangesを隠さず、ownerとmanual recovery/whole-merge revert/forward-fixを記録する。Candidate poisoningはsame-SHA retryでなくnew sourceへforward-fixする。Issue merge rollbackはwhole mergeで、partial policy/workflow/data restoreをaccepted stateにしない。

B1/B2未受入、same-Red fail、projection unread、explicit dispatchなしでは常にpre-implementation stopである。

## 6. Acceptance criteria

| AC | Observable fact | Primary evidence |
|---|---|---|
| AC-00 | #395 reported implementation defectが#395 ownerにより修正・受入され、corrected merge SHA/treeがGitHub readbackどおりで、corrected merge SHAがIssue #396の`SPEC_FREEZE_SHA`のancestor | #395 correction/acceptance receipt + corrected commit/tree readback + `git merge-base --is-ancestor` result in `EvidenceIndexV1` |
| AC-01 | B1がfresh executionでaccepted | `b1-b2-verification-contract-v1.json`, EvidenceIndexV1, accepted receipt |
| AC-02 | B2がaccepted B1とsame exact tipでfresh accepted | raw verifier bytes, 15/0/15 relation, accepted receipt |
| AC-03 | same-Red review pass、P0/P1=0 | review JSON/session receipt |
| AC-04 | Issue projection readbackとexplicit dispatchが別々に成立 | GitHub readback, dispatch receipt |
| AC-05 | Materializationがattemptから分離し、one build、complete candidate/environment後にfreeze | CandidateMaterializationV1, CampaignFreezeV1 |
| AC-06 | Same-SHA materialization failureはpoison、rebuild拒否 | violation evidence `MATERIALIZATION_POISONED` / `SAME_SHA_REBUILD_ATTEMPTED` |
| AC-07 | binding-scoped EvidenceIndexがstage-correct、logical path/size/hashだけ | schema validation, actual-byte index |
| AC-08 | Immutable baselineとordered deltaからownershipを決定的に導出し、実collectionのcount/owner/hashと一致 | baseline, delta, generated ownership evidence |
| AC-09 | Pluginが移行中/最終のsole permanent filter ownerであり、full qualificationとexact-node focused collectionを正しく区別 | transition/final ownershipとqualification/focused-selector tests |
| AC-10 | Candidate-freeze時点のclosed fault catalogueを全件実行・検出率100% | definition/binding/execution results |
| AC-11 | 永続Candidate/Attempt/Qualification/Cutover/Stop recordsとoperational failure familiesがclosed | Draft 2020-12 schema + finite operational families |
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
| RQ-004 | evidence binding | `EvidenceIndexV1`, `EvidenceEntryV1` | absolute/dotdot/symlink/hash/binding mismatch | actual-byte index |
| RQ-005 | six-stage attempt graph | workflow, `AttemptStageIdV1`, `CandidateResolutionV1`, four `RoleResultV1`s, terminal `AttemptResultV1` | missing/duplicate stage or execution role, identity mismatch | per-attempt result |
| RQ-006 | ownership/plugin | baseline, delta, generated ownership evidence, `pytest_plugin.py` | unknown/duplicate/unplanned/final-owner-survival | generated ownership/hash |
| RQ-007–008 | topology/env | `process_tree.py`, `environment.py` | leak/reap/root/worker/shard/drift/limit | process and environment evidence |
| RQ-009–013 | attempt/history/aggregates | `history.py`, `evaluator.py`, parent projection | rerun/cancel/missing/replacement/filter | attempt/campaign/window results |
| RQ-011 | fault campaign | candidate-bound catalogue, `faults.py` | omitted/unexecuted/missed entry or denominator drift | candidate-bound fault results |
| RQ-014 | closed persisted records/codes | schema + operational failure families | unknown field/code/type/order | schema/golden receipt |
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

## 8.1 Implementation simplification boundary

親Epicのcandidate、environment、role、fault、history、cutover、protected-data、B3のobservable contractは変更しない。一方、Issueがそのcontractを証明するためのmodule数、schemaの分割、checkpointの保存形式、receiptの複写、作業phaseの数はacceptance contractではない。隣接責務を統合し、derived evidenceを実行時に生成し、one-shotのconsumer/context/snapshot確認をtestまたは外部evidenceへ置くことを許可する。実装briefは、同じobservable output・fail-closed境界・human-only settings/merge境界を保つ最小構造を選ぶ。

既存のfull checkpoint assignment、resolved-final manifest、authoring status、HTML、ZIPおよび旧violation-code一覧は、正本へ参照されない限りhistorical evidenceとして保持できる。これらをruntime input、追加の恒久service、追加のapproval gateとして復活させない。

## 9. Stop and return

次を観測したら、fallbackやgate免除を行わず`StopReturnV1`で停止する。

- #395 merge SHA/tree、B1/B2 same-tip execution、raw evidence、accepted stateの欠落・不一致。
- corrected #395 merge SHAがIssue #396 specification freezeのancestorでない、またはbranch history realignmentに人間/parent ownerの明示的 dispositionがない場合。
- historical receipt、Issue graph ready、#395 CLOSED、別SHA結果でB1/B2を代替しようとした場合。
- same-Red reviewがpass/P0=0/P1=0でない、projection readbackまたはexplicit dispatchがない場合。
- parent `E384-QUAL-001`をsemantic変更、duplicate authority、hidden thresholdなしにprojectできない場合。
- materialization producer一意性、actual bytes、environment identity、retentionを閉じられない場合。
- poisoned source SHA/treeを再buildする必要がある場合。
- baseline/deltaから生成したownershipにunknown/duplicate/unplanned nodeがある場合。
- plugin sole filterをretirement後まで維持できない場合。
- fault catalogueの一つでも未実行/未検出/denominator driftの場合。
- started failure/cancel/missing/rerunをhistoryから除外しなければpassできない場合。
- old consumerが残る、retained installed-consumer workflowへ削除/変更が及ぶ場合。
- external context/ruleset/merge queueをreadbackできない、no-gapやrollbackを証明できない場合。
- Product/lifecycle/15-row/protected data/parent policyの変更が必要な場合。

StopReturnはpre/post mutationの事実を区別し、scope impact、owner、required action、changed surfaces、external changes、rollback/recovery statusを記録する。Cause未特定は推測で埋めず、evidence不足としてparent ownerへ返す。Automatic rollbackは禁止する。

`owner_decisions_required=[]`は、本仕様のProduct/Policy/Securityに関するowner decision listが空であることだけを意味する。過去reviewでのP1件数を現在のfinding数として示すものでも、B1/B2、current projection readback、explicit dispatch等のgateを省略するものでもない。

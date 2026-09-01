---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
親: ["init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ef183ae46febe52f0152431cb3a8b4846c9972fc"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

Normative artifacts: `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md` (Issue documents use `../../artifacts/...`). Their exact wire/disposition data is not delegated to implementation.


## 1. Outcome

SpecDock providerのdistribution lifecycleとprovider test execution graphを同一のProduct変更として簡素化し、次のfinal contractへcombined hard cutoverする。

- consumer repositoryで永続的に管理するtooling mutation authorityを、4 fixed roots、2 fixed skill slots、1 fixed installation recordへ限定する。
- `spec-dock/.gitignore`と`.github/workflows/ci.yml`はfresh `init`時にpathがabsentの場合だけ作成し、作成後はconsumer-owned seedとして扱う。
- incomplete operationのresumeに必要なseed mutation authorityを、strict recordのimmutable `seed_policy`として保存し、seedの現在状態から推測しない。
- fresh targetでshared `spec-dock` containerがabsentの場合だけ、descriptor-bound bootstrapとして安全に作成・bindし、record publication前のfailureではexact identityかつemptyの場合だけcleanupする。
- exact clean `0.2.3` workspaceだけをone-shot migrateし、active legacy recovery、unsupported legacy、foreign markerless slotを推測変換しない。
- uninstallをtooling-onlyへ縮小し、user-owned spec historyを削除するpurge capabilityを廃止する。
- PR-BはS40/S50をnon-main checkpoint、S60を唯一のmerge gateとし、mainをold public productからcomplete final lifecycleへ一度だけ遷移させる。
- PR-Cはreplacement provider gate、stable Linux qualification environment、root `AGENTS.md`更新、old policy/workflow removalを一つのbranch/PRで完了し、S80だけをmerge gateとする。
- specification lineage、#387 implementation drift、tracked pre-merge report、external closure evidenceを別々のidentityで検証し、tracked treeへ自己参照するevidenceを置かない。
- provider merge gateをbuild-once、Linux canonical single pytest process、macOS platform deltaへ移行し、approved failure、policy skip、duplicate contract execution、4-shard Full Regressionをfinal stateから除去する。
- 実装と検証はGitHub #392の一つのIssue unitだけで受け入れる。

Outcomeはコード量削減そのものではない。管理権限、失敗時挙動、migration、public CLI、artifact binding、test ownership、human merge gate、evidence identityが一つの検証可能な契約へ収束した状態である。

## 2. Current evidence and problem statement

本書は`chemitaro/spec-dock`のbranch `codex/epic-00384-provider-test-strategy-planning`、full SHA `ef183ae46febe52f0152431cb3a8b4846c9972fc`を調査基準とする。このrevisionでは次を直接確認した。

- `src/spec_dock/managed_distribution.py`がfresh、update、deprovision、purge、historical identity、journal、recovery、native rename、result modelを一つの巨大なmoduleで所有している。
- `src/spec_dock/assets/managed_distribution.json`がrecognized version、historical current identity、obsolete exact fileを列挙している。
- `src/spec_dock/cli.py`がlegacy admission、fresh/recognized execution、safe removal、purge、text/JSON mappingを直接結合している。
- `pyproject.toml`のcurrent package versionは`0.2.3`で、pytestの`fast` / `full_regression` policy markerが存在する。
- `tests/conftest.py`がpath-based lane classification、policy skip、failure ledger evaluation、shard observationを所有する。
- `.github/workflows/provider-ci.yml`はordinary suiteに加えてUbuntu/macOSでdistribution contractを重複実行し、`.github/workflows/provider-full-regression.yml`はmain pushで4-shard verifierを実行する。
- Current `provider-ci.yml`は`tests/unit/infra/test_managed_distribution.py`、`tests/cli_runtime/test_distribution_cutover.py`、`tests/integration/test_epic_00343_distribution.py`を直接参照する。`tests/unit/test_provider_test_lanes.py`は`tests.conftest`と両quality modulesをimportし、`tests/unit/test_full_regression_baseline.py`はbaseline providerを直接検証する。
- `full-regression-ledger.json`、`full-regression-timing-weights.json`、`scripts/quality/full_regression_baseline.py`、`scripts/quality/verify_full_regression.py`がapproved failureとshardingを支える。
- Issue #387はopenであり、このrevisionには#387 implementationがまだ含まれない。#387のcanonical R/D/Pはmanaged distribution、provider workflow、sharder、public installer CLIを明示的に非所有としている。
- Epic `.meta.json`の`depends_on`は`iss-00387`を含む。

したがって、#387のaccepted cleanupと本Epicのmanaged distribution semanticsを混同せず、#387 merge後のexact SHAを新しいimplementation baselineとして固定する必要がある。

## 3. Actors

| Actor | Responsibility |
|---|---|
| Consumer repository owner | consumer-owned data、seed、unknown pathの最終所有者。tooling operationを明示的に実行する。 |
| SpecDock installer CLI | state classification、fixed tooling lifecycle、typed result、public compatibilityを提供する。 |
| Provider maintainer | provider source、package asset、test ownership、CI transitionをreviewする。 |
| Luna Max implementation agent | #392 `plan.md`に従い、追加のProduct判断を行わず実装・検証候補を作成する。 |
| Human reviewer / merger | PR review、required-context変更、mergeを行う唯一の主体。 |
| GitHub Actions | 同一artifactに束縛されたLinux canonical、macOS delta、static analysisを実行する。 |

## 4. Terms

- **fixed roots**: `spec-dock/docs`、`spec-dock/templates`、`spec-dock/system`、`spec-dock/scripts`。recordがownershipを証明する場合に限りroot全体をdisposable toolingとして置換・削除できる。
- **fixed skill slots**: `.agents/skills/spec-dock`、`.agents/skills/spec-dock-grill-with-docs`。new-format markerまたはexact legacy treeがownershipを証明する場合に限りslot全体を置換・削除できる。
- **shared spec-dock container**: repository root直下の`spec-dock` directory。fixed roots、record、seed、user-owned dataを収容するshared containerであり、whole-directory replacement/delete authorityを持たない。
- **fixed installation record**: `spec-dock/spec-dock.version`。final formatではstrict JSON state record。legacy `0.2.3` formatはexact bytes `0.2.3\n`。
- **seed policy**: `create-if-absent`または`preserve-only`。一operationのincomplete recordからterminal recordまで不変で、resume時にrequest/stage/recordのexact matchを要求する。
- **fresh-init-only seed**: `spec-dock/.gitignore`と`.github/workflows/ci.yml`。fresh `init`だけabsent pathを一度作成でき、その後はprovider authority外。
- **candidate**: package内の4 rootsと2 slotsから構築し、versionとcanonical tree digestで一意に識別するimmutable payload。seed、record、generated slot markerはdigestに含めない。
- **legacy-0.2.3**: post-#387 baseline artifactが生成したplain marker、exact 4 root digests、各slotのabsent/exact digest、legacy recovery marker不在を満たすworkspace。
- **tooling-absent-preserved-data**: uninstall後もrecordを保持し、never-installed `absent`と区別するdurable state。
- **SPEC_FREEZE_COMMIT**: replacement manifestのexact canonical/support bytesをrepositoryへimportしたowner-recorded Git commit。repository evidence SHAとは別identity。
- **pre-merge tracked report**: final PR treeへ含める#392 `report.md`。own hash、final PR head、post-merge factsを自己参照しない。
- **external attestation**: final head固定後に生成し、canonical JSON SHA-256付きで新規GitHub comment/check artifactとして保存するimmutable evidence。
- **tree equality**: `verified_pr_head^{tree}`とhuman merge commitの`^{tree}` object IDが等しいこと。merge commit SHA equalityは要求しない。
- **Linux qualification environment ID**: `specdock-linux-qualification-v1`。tracked descriptor hashとobserved fingerprintへ束縛される。
- **policy skip**: failure許容またはpath分類だけを理由にcanonical gateからtestをskipする仕組み。platform delta lane分離は含まない。
- **wire contract**: `artifacts/provider-lifecycle-wire-contract.md`。Record/result/action/text/exitのnormative wire authority。
- **failure disposition register**: `artifacts/active-failure-disposition-register.md`。Current ledger 27行、#387 expected delta、final dispositionのnormative authority。
- **authoritative packaging producer**: final frozen headからwheel/sdist/manifestを一度だけ生成するLinux `provider-build-artifacts` job。Local buildはauthoritative final artifactにならない。
- **Issue unit**: implementationとverificationを一体で完了・受入する一つのGitHub Issue。

## 5. Scope and requirements

### E384-RQ-001 — Fixed ownership and fresh bootstrap boundary

Providerのdurable mutation authorityは4 roots、2 slots、`spec-dock/spec-dock.version`だけに限定する。Fresh `init`では2 seedsのabsent-path creation、`.github/workflows`の不足するexact parent chain、およびabsent shared `spec-dock` containerのexclusive bootstrap creationだけを追加で許可する。Arbitrary path、manifest-provided path、historical obsolete path、wildcard deletionをauthorityにしない。

### E384-RQ-002 — Consumer data preservation

`spec-dock/initiatives/**`、nested `artifacts/**`、`.workbench/**`、generated projections、unknown non-target path、unrelated skill、consumer-owned seed、shared containerのunknown childrenを探索・正規化・移動・削除しない。Shared `spec-dock` container自体はuninstallしない。

### E384-RQ-003 — Lifecycle and immutable resume intent

fresh、ready、incomplete、tooling-absent-preserved-data、exact legacy-0.2.3を明示的に分類し、install、update、tooling-only uninstall、reinstallを提供する。Incomplete recordはoperation、candidate digest、seed policyをimmutable resume tupleとして持つ。same-operation / same-candidate / same-seed-policy rerunだけを収束経路とし、automatic rollback、cross-intent recovery、old engine fallbackを公開しない。

### E384-RQ-004 — Combined hard cutover and merge boundaries

Uninstall-first bridge、intermediate package generation、runtime toggle、dual writer、old/new behavior switchを導入しない。PR-BのS40/S50はnon-main checkpointsであり、S60まで完了した一つのPRだけをmainへmergeする。PR-A merge後はold public product、PR-B merge後はcomplete final lifecycle、PR-C merge後はfinal provider gateである。

### E384-RQ-005 — Exact legacy migration

Exact clean `0.2.3`だけをone-shot migrateする。Active legacy recovery、invalid plain-text version、unsupported version、modified root、foreign/modified markerless slotはmutation前にblockする。Legacy identityはsingle-version root/slot digest fixture以外へ拡張しない。Migration seed policyは常に`preserve-only`。

### E384-RQ-006 — Tooling-only uninstall and purge removal

Uninstallはdefault dry-run、`--apply`でconfirmationする。User history purgeを行わない。`--keep-specs`はdefault同義のcompatibility alias。`--remove-specs`は全modeでmutation zero、code `spec-history-purge-removed`、exit 2。

### E384-RQ-007 — Durable uninstall discriminator

Successful uninstall後もrecordを削除せず、`state=tooling-absent-preserved-data`、`operation=null`、`seed_policy=preserve-only`としてatomic replaceする。Reinstallはこのstateを読み、fresh-init-only seedsがabsentでも再作成しない。

### E384-RQ-008 — Safe shared-container creation and cleanup

Record absent、4 roots/2 slots absent、`spec-dock`がabsentまたはreal directoryの場合だけfresh stateを認める。Container absentならcandidate stage/validationとroot/absence binding後に`mkdirat`でexclusive createし、直ちに`O_NOFOLLOW|O_DIRECTORY`でbindする。Record publication前のfailureはexact created identityかつemptyの場合だけremoveする。Cleanup不能ならstage ownerを保持したpartial failureとし、same operation/candidate/seed policy以外をblockする。

### E384-RQ-009 — Filesystem safety

Repository root binding、parent binding、no-follow、hard-link rejection、unexpected type rejection、marker validation、candidate validationを最初のdurable tooling publication前に完了する。Existing root/slot replacementはLinux `renameat2(RENAME_EXCHANGE)`またはmacOS `renameatx_np(RENAME_SWAP)`、absent publication/uninstall detachはno-replace。Primitive不在はfail closed。

### E384-RQ-010 — Public compatibility

`init [path] [--force]`、`update [path]`、`uninstall [path] [--apply] [--keep-specs|--remove-specs] [--json]`を維持する。Accepted changes以外のsuccess text、error channel、JSON主要fieldを維持し、typed resultからstatus/code/exitを一意にmappingする。

### E384-RQ-011 — Old-package mutation-zero

Final workspaceに対するold exact `0.2.3` packageの`init --force`、`update`、tooling uninstall、`--remove-specs`をstartup composite tripwire下で実行する。Python filesystem audit eventとLinux `renameat2` / macOS `renameatx_np` native symbol callをsyscall前に捕捉し、commandごとのevent count 0、target tree digest不変を必須とする。Native positive controlが捕捉できなければ証明失敗。

### E384-RQ-012 — Test ownership

各durable invariantは一つのowner layer、一つのauthoritative lane、少なくとも一つのrepresentative failureを持つ。Pure/domain、filesystem/service、CLI、built artifact、macOS deltaを分離し、same candidate/OS/contractのduplicate ownershipを0にする。

### E384-RQ-013 — Failure terminalization with transitional workflow continuity

Post-#387 baselineのactive failure ledger entryをfix、current successor、accepted contract retirementのいずれかへ全件terminal化し、PR-B merge時点でactive approved failureを0にする。S60は`.github/workflows/provider-ci.yml`をexact owned pathとし、workflow名、event、job IDs、Ubuntu/macOS matrix、checkout、Python/uv install、static-analysis topologyを維持したまま、削除する3 test pathだけをS10〜S50で成立したsuccessor test groupsへ置換する。これはtemporary current-gate repairであり、S70のbuild-once provider-gate redesignではない。

S60は`tests/unit/test_provider_test_lanes.py`もowned pathとし、`tests/conftest.py`のcurrent policyと整合するよう、active row 0、all ledger rows terminal、deleted test path参照0、workflow successor path実在、pytest adapter/standalone evaluator parityを検証する。Rows 4〜15は#387でledgerから除去済みのまま再挿入せず、残る15行は`active-failure-disposition-register.md`で事前決定したfixed-in-placeまたはsuperseded relationへ更新する。`tests/unit/test_full_regression_baseline.py`、`tests/conftest.py`、ledger、timing、quality modules、`.github/workflows/provider-full-regression.yml`はS70まで保持する。

### E384-RQ-014 — Build-once artifact binding

Authoritative source SHAごとに一つのpackaging invocationでwheelとsdistを生成し、source SHA、filename、size、SHA-256、build invocation countをmanifestへ固定する。Linux canonicalとmacOS deltaは同じwheel bytesを使用し、sdistはLinux minimal smokeだけが所有する。

### E384-RQ-015 — Canonical provider gate and stable Linux environment

Linux canonicalはworker 1、one pytest process。Qualificationはenvironment ID `specdock-linux-qualification-v1`、tracked descriptor SHA-256、pinned container base digest、built image ID、x86_64、2.0 CPU quota、8 GiB memory、Python/uv/lock hashesへ束縛する。20-run series中のfingerprint mismatchは全seriesを無効にする。First 5各600秒以内、CPU/wall <=1.1、fault detection 100%、all 20 flake 0/retry 0。

### E384-RQ-016 — Atomic provider-gate cutover and complete consumer closure

PR-B/S60 merge後は、successor pathsへretarget済みのcurrent `.github/workflows/provider-ci.yml`と、current main-push Full Regression workflowの双方がGREENでなければならない。PR-C/S70ではreplacement `scripts/provider_gate.py`、Linux environment descriptor、final provider workflow、root `AGENTS.md`を同一branchへ先に追加する。その後、policy providersを削除する前に`tests/unit/test_provider_test_lanes.py`、`tests/unit/test_full_regression_baseline.py`を含む全remaining policy-module consumersをexplicitにretireまたはfinal gate testsへ置換し、import/grep/collection/workflowでconsumer 0を証明する。続いてold workflow、ledger、timing、sharder、`tests/conftest.py`、marker policyを同じPR-C branchで削除する。S70はnon-main checkpoint、S80後だけmergeし、mainはbroken workflowまたはmissing consumerを観測しない。

### E384-RQ-017 — Required-context transition without a gap

Old required contextsを保持したままnew contextをrequiredへ追加し、old+new required stateをread-backする。次にdedicated non-merge canary PRのintentional REDでnew contextがmergeをblockすることを証明し、canary closeとimplementation PR GREEN復帰後だけold provider-only contextを除去する。Unrelated contextsとhuman review requirementを変更しない。

### E384-RQ-018 — Deterministic specification and #387 admission

Repository evidence SHAは調査起点として記録する。本replacement manifestのcanonical/support payload hashesとowner-recorded `SPEC_FREEZE_COMMIT`のexact blobsを一致させ、commit ancestryを要求する。#387 merge deltaは#387 own base/head/merge tree/changed pathsで検証し、stale repository evidence SHAからpost-#387 tipへの単純diffをadmissionに使わない。

### E384-RQ-019 — Non-cyclic evidence and tree equality

Tracked #392 reportはpre-merge methodologyとimplementation facts、external attestation schema/locationだけを含み、own hash、final PR head、post-merge factsを自己参照しない。Final head固定後のbuild/qualificationはcontent-addressed external pre-merge attestationへ記録する。Human merge後はverified PR head tree OIDとmerge commit tree OIDを比較する。SpecDock finish、GitHub close、Epic closureはexternal closure attestationへ記録し、tracked reportへwritebackしない。

### E384-RQ-020 — Root operator guidance and Issue boundary

Root `AGENTS.md`をPR-Cでfinal pytest/provider-gate commands、no-policy-skip/no-main-push-full policy、provider-first/dogfood rule、human-only mergeへ更新する。Epic #384のimplementation-and-verification Issueは#392だけ。New decision/research/test/verification Issueを作成せず、未達は同じ#392でforward-fixする。

### E384-RQ-021 — PR-B documentation convergence

PR-B/S60 main merge時点でfinal `0.2.4` code、root README lifecycle、provider-shipped docs、dogfood docsを一致させる。S40/S60 exact ownershipは`README.md`のlifecycle sections、`src/spec_dock/assets/spec_dock/docs/migration.md`、`src/spec_dock/assets/spec_dock/docs/README.md`と対応する`spec-dock/docs/**` projectionである。Legacy journal/retry、current purge authority、compatible-newer retry、empty-boundary guidanceをtooling-only uninstall、strict record、same tuple resume、preserve-only lifecycleへ置換する。Root README/AGENTS/docsのtest-policy textはS70でfinal gateへ更新し、S80はcontentを編集せずfreeze/verificationだけを行う。

### E384-RQ-022 — Normative provider lifecycle wire

`artifacts/provider-lifecycle-wire-contract.md`をrecord、operation、observed state、resume relation、slot marker、typed result、public JSON/text/exitの唯一のnormative wire contractとする。Implementation/test/docsはexact seven-key record、enum、nullability、field relation、golden bytesへ一致し、unknown valueをfallbackしない。

### E384-RQ-023 — Pre-decided active failure dispositions

`artifacts/active-failure-disposition-register.md`をrepository evidence ledger全27行のnormative disposition authorityとする。#387後のexpected deltaはrows 4〜15のexact removalだけで、その他のnode/signatureは不変。Unexpected new/missing/signature/successor deltaはS10前に停止し、canonical spec owner updateとStrict re-reviewを要求する。S60の残存15行はall resolved、active 0へterminalizeし、Lunaはdispositionを選択しない。

### E384-RQ-024 — Final frozen-head packaging producer

Final frozen PR headのwheel、sdist、candidate manifestを生成できる主体はfinal `.github/workflows/provider-ci.yml`のLinux `provider-build-artifacts` job一つだけとする。Head freeze後、同jobがone packaging invocationでbuildし、immutable Actions artifact identityへuploadする。Linux qualification、macOS delta、sdist smoke、attestationは同じdownloaded bytesをbuild 0でconsumeする。S70 local buildはpre-freeze tooling validationのみで、S80はlocal final buildを行わずexact workflow dispatch/wait/download/verifyを実行する。

## 6. Non-scope

- user-owned spec historyを削除する機能。
- arbitrary historical versionのmigration catalog。
- release publication workflow、PyPI publication、release tag作成。
- worker増加、xdist、machine大型化、shardingによるbudget回避。
- #387のCurrent surface cleanupを本Epicで再実装すること。
- Issue #372のcanonical specification、candidate、evidenceの変更。
- decision-only、research-only、tests-only、verification-onlyの追加Issue。
- agentによるPR merge、branch protectionの推測変更。

## 7. Constraints and accepted decisions

1. Product source of truthは`src/spec_dock/`。Provider-firstで変更後、dogfood `spec-dock/`を同期・検証する。
2. Final distribution versionは`0.2.4`。Release publicationはscope外。
3. Record pathは`spec-dock/spec-dock.version`。Final JSONはold `0.2.3` parserにcanonical versionとして受理されず、pre-mutation block pointとなる。
4. New skill markerは各slot直下の`.spec-dock-provider-slot.json`。
5. Persistent recordにper-file digest、arbitrary path、checkpoint、progress bit、rollback imageを保存しない。`seed_policy`はprogressではなくresume authority。
6. Valid target-local state成立後にprovider-owned external staging cleanupだけが失敗した場合に限り`completed_with_warnings`を許可する。
7. Destructive defectはapply routeをfail closedにし、old engineへfallbackしない。
8. #388〜#390はsuperseded historical nodeでありreopenしない。
9. S40/S50/S70はmain merge pointではない。S60だけがPR-B gate、S80だけがPR-C gate。
10. PR-A merge後はold public product、PR-B merge後はcomplete final lifecycle + still-valid current gate、PR-C merge後はfinal provider gate。
11. PR-B merge時点でroot README lifecycleとprovider/dogfood migration/docs READMEがfinal codeへ一致する。
12. `provider-lifecycle-wire-contract.md`と`active-failure-disposition-register.md`はnormative accepted artifactsであり、implementation時に再決定しない。
13. Final frozen-head packaging authorityはLinux Provider CI build jobだけで、local artifactをacceptanceへ昇格しない。

## 8. Dependency on Issue #387

#392は#387がhuman mergeされる前に開始してはならない。S00は次を別々に検証する。

1. Repository evidence SHA `ef183ae46febe52f0152431cb3a8b4846c9972fc`は調査起点として記録する。
2. Replacement manifestのcanonical/support payload hashesを、owner-recorded `SPEC_FREEZE_COMMIT`のexact repository blobsへ一致させる。
3. #387 merge deltaを#387 own PR/merge graphからexact allowlist/content restrictionへ照合する。
4. Implementation baseが`SPEC_FREEZE_COMMIT`と#387 mergeをancestorに持つことを要求する。
5. Protected distribution pathsにvalidated #387 delta以外のdriftがないこと、package versionがbaseline `0.2.3`、current gatesがGREENであることを記録する。

Repository evidence SHAからfuture main tipへの単純allowlist diffをadmission authorityにしてはならない。Mismatch時はimplementationを開始せず、exact evidenceをrepository ownerへ返す。

## 9. Issue unit and merge-point policy

Epic #384のimplementation-and-verification IssueはGitHub #392だけ。

- PR-A: S10/S20 internal、S30全proof後だけmerge。Mainはold public product。
- PR-B: S40/S50 internal、S60全proof後だけmerge。Mainはcomplete final lifecycle。Current provider gate/main-push workflowはconsumerを失わずGREEN。
- PR-C: S70 internal、S80全proof・required transition・external pre-merge attestation後だけmerge。Mainはfinal provider gate。
-各main merge pointはreleasable。
- bridge generation、runtime toggle、中間public generationなし。
- implementation completion、tracked report completion、pre-merge attestation、human merge、post-merge closure、Issue finish、Epic closeを別状態として扱う。
- Acceptance未達は同じ#392でforward-fixする。

## 10. Externally observable acceptance

Epicは次のすべてが同一final PR treeと同一artifact identityに対して確認されたときだけ受入可能。

- fixed mutation set外のconsumer data、seed、unknown path、unrelated skillがbyte-identical。
- fresh container absent/existing、fresh install、ready update、exact `0.2.3` migration、tooling uninstall、tooling-absent reinstallがbuilt wheelで成功。
- incomplete operationのseed policyがrecord/stage/requestで一致し、fault resumeでseed creation semanticsが変わらない。
- shared container bootstrap/cleanupがdescriptor-safeで、uninstallがcontainerを削除しない。
- same operation/candidate/seed policy rerunで収束し、mismatchがblock。
- old `0.2.3` command matrixがtripwire event 0、native positive control capture、tree digest不変。
- public CLI text/JSON/exit、aliases、purge trapがcontractどおり。
- PR-B main merge時点でactive approved failure 0、transitional `provider-ci.yml`のsuccessor commands GREEN、current main-push verifier GREEN。
- PR-Cでall policy consumersをprovidersより先にretire/replaceし、replacement gateとold machinery removalがatomic、final provider gate GREEN、mainにbroken workflow stateなし。
- one build invocation、same wheel、Linux canonical、macOS delta、sdist smoke。
- Linux environment ID/fingerprint、five-run budget、CPU ratio、fault pack、rolling 20を満たす。
- new contextをoldと併存requiredにしてからRED blockを証明し、GREEN復帰後oldを除去。
- root `AGENTS.md`がfinal commands/policyへ一致。
- tracked reportにself-reference/post-merge factなし、external attestationsがcontent-addressed。
- human merge commit tree OIDがverified PR head tree OIDと一致。
- root/provider/dogfood lifecycle docsがPR-B final contractへ一致し、retired lifecycle phrase grepが0。
- wire contractのseven-key record、public result enum/nullability/goldenがtestsと一致。
- failure register 27行、#387 expected delta、S60 all-resolved ledgerがexact。
- final frozen headのpackaging producerがLinux CI job一つで、downstream build count 0。
- remaining owner decisions 0。

## 11. Trace to the sole implementation Issue

| Epic requirement | Issue #392 responsibility |
|---|---|
| E384-RQ-001〜010 | fixed lifecycle、seed policy、container bootstrap、record、candidate、CLI |
| E384-RQ-011 | old-package tripwire / downgrade proof |
| E384-RQ-012〜013 | test ownership、active failure terminalization、S60 workflow/lane-consumer repair、PR-B gate continuity |
| E384-RQ-014〜016 | build-once gate、stable Linux environment、policy-consumer-first atomic PR-C removal |
| E384-RQ-017 | no-gap required-context transition |
| E384-RQ-018〜019 | specification lineage、external attestations、tree equality |
| E384-RQ-020 | root AGENTS、single-Issue closure |
| E384-RQ-021 | PR-B docs convergence and S70 policy-doc split |
| E384-RQ-022 | `provider-lifecycle-wire-contract.md` exact wire implementation/tests |
| E384-RQ-023 | `active-failure-disposition-register.md`、S00 delta gate、S60 fixed dispositions |
| E384-RQ-024 | Linux CI-only final producer、downloaded-byte fan-out、S80 dispatch evidence |

No other implementation Issue is authorized。

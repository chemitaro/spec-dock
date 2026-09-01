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
  sha: "91667235c6892f025a1d9ee69cf37525537a3c9e"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

## 1. Outcome

SpecDock providerのdistribution lifecycleとprovider test execution graphを同一のProduct変更として簡素化し、次のfinal contractへcombined hard cutoverする。

- consumer repositoryで永続的に管理するtooling mutation authorityを、4 fixed roots、2 fixed skill slots、1 fixed installation recordへ限定する。
- `spec-dock/.gitignore`と`.github/workflows/ci.yml`はfresh `init`時にpathがabsentの場合だけ作成し、作成後はconsumer-owned seedとして扱う。
- exact clean `0.2.3` workspaceだけをone-shot migrateし、active legacy recovery、unsupported legacy、foreign markerless slotを推測変換しない。
- uninstallをtooling-onlyへ縮小し、user-owned spec historyを削除するpurge capabilityを廃止する。
- provider merge gateをbuild-once、Linux canonical single pytest process、macOS platform deltaへ移行し、approved failure、policy skip、duplicate contract execution、4-shard Full Regressionをfinal stateから除去する。
- 実装と検証はGitHub #392の一つのIssue unitだけで受け入れる。

Outcomeはコード量削減そのものではない。管理権限、失敗時挙動、migration、public CLI、artifact binding、test ownership、human merge gateが一つの検証可能な契約へ収束した状態である。

## 2. Current evidence and problem statement

本書は`chemitaro/spec-dock`のbranch `codex/epic-00384-provider-test-strategy-planning`、full SHA `91667235c6892f025a1d9ee69cf37525537a3c9e`を調査基準とする。このrevisionでは次を直接確認した。

- `src/spec_dock/managed_distribution.py`がfresh、update、deprovision、purge、historical identity、journal、recovery、native rename、result modelを一つの巨大なmoduleで所有している。
- `src/spec_dock/assets/managed_distribution.json`がrecognized version、historical current identity、obsolete exact fileを列挙している。
- `src/spec_dock/cli.py`がlegacy admission、fresh/recognized execution、safe removal、purge、text/JSON mappingを直接結合している。
- `pyproject.toml`のcurrent package versionは`0.2.3`で、pytestの`fast` / `full_regression` policy markerが存在する。
- `tests/conftest.py`がpath-based lane classification、policy skip、failure ledger evaluation、shard observationを所有する。
- `.github/workflows/provider-ci.yml`はordinary suiteに加えてUbuntu/macOSでdistribution contractを重複実行し、`.github/workflows/provider-full-regression.yml`はmain pushで4-shard verifierを実行する。
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

- **fixed roots**: `spec-dock/docs`、`spec-dock/templates`、`spec-dock/system`、`spec-dock/scripts`。recordがownershipを証明する場合に限り、root全体をdisposable toolingとして置換・削除できる。
- **fixed skill slots**: `.agents/skills/spec-dock`、`.agents/skills/spec-dock-grill-with-docs`。new-format markerまたはexact legacy treeがownershipを証明する場合に限りslot全体を置換・削除できる。
- **fixed installation record**: `spec-dock/spec-dock.version`。final formatではstrict JSON state recordである。legacy `0.2.3` formatはexact bytes `0.2.3\n`である。
- **fresh-init-only seed**: `spec-dock/.gitignore`と`.github/workflows/ci.yml`。fresh `init`がabsent pathを一度作成できるが、その後はprovider authority外である。
- **candidate**: package内の4 rootsと2 slotsから構築し、versionとcanonical tree digestで一意に識別するimmutable payload。seedとrecordはcandidate digestに含めない。
- **legacy-0.2.3**: post-#387 baseline artifactが生成した、plain-text version marker、exact 4 root digests、各slotのabsentまたはexact digest、legacy recovery marker不在を満たすworkspace。
- **tooling-absent-preserved-data**: uninstallがfixed toolingを除去した後もrecordを保持し、never-installed `absent`と区別するdurable state。
- **policy skip**: test failureを許容するため、またはpath分類だけを理由としてcanonical gateからtestをskipする仕組み。platform deltaのlane分離はpolicy skipに含めない。
- **Issue unit**: implementationとverificationを一体で完了・受入する一つのGitHub Issue。

## 5. Scope and requirements

### E384-RQ-001 — Fixed ownership boundary

Providerのdurable mutation authorityは、4 roots、2 slots、`spec-dock/spec-dock.version`だけに限定する。fresh `init`では、2 seedのabsent-path creationと、そのexact parent chainで不足するreal directoryの作成だけを追加で許可する。arbitrary path、manifest-provided path、historical obsolete path、wildcard deletionをauthorityにしない。

### E384-RQ-002 — Consumer data preservation

`spec-dock/initiatives/**`、nested `artifacts/**`、`.workbench/**`、generated projections、unknown non-target path、unrelated skill、consumer-owned seedを探索・正規化・移動・削除しない。fixed root内部はrecordによってprovider-ownedと証明された場合だけroot単位でdisposableである。

### E384-RQ-003 — Lifecycle

fresh、ready、incomplete、tooling-absent-preserved-data、exact legacy-0.2.3を明示的に分類し、install、update、tooling-only uninstall、reinstallを提供する。same-operation / same-candidate rerunだけを収束経路とし、automatic rollback、cross-intent recovery、old engine fallbackを公開しない。

### E384-RQ-004 — Combined hard cutover

uninstall-first bridge、intermediate package generation、runtime toggle、dual writer、old/new behavior switchを導入しない。successor codeをpublic routeへ接続するcutoverでは、new lifecycle、CLI compatibility、migration、test portfolioを同じfinal generationとして成立させる。

### E384-RQ-005 — Exact legacy migration

exact clean `0.2.3`だけをone-shot migrateする。active legacy recovery、invalid plain-text version、unsupported version、modified root、foreign/modified markerless slotはmutation前にblockする。legacy identityはsingle-version root/slot digest fixture以外へ拡張しない。

### E384-RQ-006 — Tooling-only uninstall

uninstallはdefault dry-run、`--apply`でconfirmationする。user history purgeを行わない。`--keep-specs`はdefaultと同義のcompatibility aliasである。`--remove-specs`は全modeでmutation zero、code `spec-history-purge-removed`、exit 2を返す。

### E384-RQ-007 — Durable uninstall discriminator

successful uninstall後もrecordを削除せず、`state=tooling-absent-preserved-data`としてatomic replaceする。reinstallはこのstateを読み、fresh-init-only seedsがabsentでも再作成しない。

### E384-RQ-008 — Filesystem safety

repository root binding、parent binding、no-follow、hard-link rejection、unexpected type rejection、marker validation、candidate validationを最初のdurable target mutation前に完了する。existing root/slot replacementにはLinux `renameat2(RENAME_EXCHANGE)`またはmacOS `renameatx_np(RENAME_SWAP)`、absent publicationとuninstall detachにはno-replace renameを使用し、primitive不在時はfail closedとする。

### E384-RQ-009 — Public compatibility

`init [path] [--force]`、`update [path]`、`uninstall [path] [--apply] [--keep-specs|--remove-specs] [--json]`のcommand/flag surfaceを維持する。accepted changes以外のsuccess text、error channel、JSON主要fieldを維持し、typed resultからstatus / code / exitを一意にmappingする。

### E384-RQ-010 — Old-package mutation-zero

final workspaceに対するold exact `0.2.3` packageの`init --force`、`update`、tooling uninstall、`--remove-specs`をtarget-scoped startup composite tripwire下で実行する。Python filesystem audit eventとLinux `renameat2` / macOS `renameatx_np`のnative symbol callをsyscall前に捕捉し、commandごとのtripwire event count 0、target tree digest不変を必須とする。native positive controlを各platformでcall前に捕捉できなければ証明失敗である。

### E384-RQ-011 — Test ownership

各durable invariantは一つのowner layer、一つのauthoritative lane、少なくとも一つのrepresentative failureを持つ。pure/domain、filesystem/service、CLI、built artifact、macOS deltaの責務を分離し、same candidate / OS / contractのduplicate ownershipを0にする。

### E384-RQ-012 — Failure terminalization

post-#387 baselineでactiveなfailure ledger entryを、fix、current successor、accepted contract retirementのいずれかへ全件terminal化する。approved failureを残さず、ledgerそのものを削除する。判断不能なentryをsuccess扱いしてはならない。

### E384-RQ-013 — Build-once artifact binding

Authoritative source SHAごとに一つのpackaging invocationでwheelとsdistを生成し、source SHA、filename、size、SHA-256、build invocation countをmanifestへ固定する。Linux canonicalとmacOS deltaは同じwheel bytesを使用し、sdistはLinux minimal smokeだけが所有する。

### E384-RQ-014 — Canonical provider gate

Linux canonicalはworker 1、one pytest processでmerge-required contractを実行する。macOSはexecutable mode、no-follow、native rename、installed entry pointなどplatform deltaだけを実行する。final qualificationはfixed Linux referenceで連続5回各600秒以内、process-tree CPU / wall 1.1以下、seeded fault detection 100%、rolling 20でflake 0 / retry 0を証明する。

### E384-RQ-015 — Legacy CI removal

final stateからmain-push 4-shard Full Regression、failure ledger、timing weights、sharder、path-based `fast` / `full_regression` policy-skip machinery、duplicate platform parityを除去する。main pushでcandidateを再buildしない。

### E384-RQ-016 — Human merge gate

PR mergeはhuman-onlyとする。required context transitionはbefore stateをread-onlyで取得し、新gateのGREENとintentional RED blockingを証明してからold contextを外す。外部設定を観測できない場合は推測変更せず停止する。

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

1. Product source of truthは`src/spec_dock/`であり、provider-firstで変更した後にdogfood `spec-dock/`を同期・検証する。
2. final distribution versionはcurrent `0.2.3`から`0.2.4`へpatch bumpする。release publicationは本Epicの対象外である。
3. record pathは既存legacy markerと同じ`spec-dock/spec-dock.version`とする。final JSONはold `0.2.3` parserにcanonical versionとして受理されず、old packageのpre-mutation block pointとなる。
4. new-format skill markerは各slot直下の`.spec-dock-provider-slot.json`とする。
5. persistent recordにper-file digest、arbitrary path、checkpoint、progress bit、rollback imageを保存しない。
6. valid target-local state成立後にprovider-owned external staging cleanupだけが失敗した場合に限り`completed_with_warnings`を許可する。
7. destructive defectはapply routeをfail closedにし、read-only diagnosticを残す。old engineへfallbackしない。
8. #388〜#390はsuperseded historical nodeであり、reopenまたはimplementation unitとして再利用しない。

## 8. Dependency on Issue #387

#392は#387がhuman mergeされる前に開始してはならない。開始時に次を満たすdeterministic admissionを行う。

- #387がclosedで、merge commitがmainのancestorであり、`POST_387_SHA`としてfull SHAを固定できる。
- authoring SHA `91667235c6892f025a1d9ee69cf37525537a3c9e`から`POST_387_SHA`までの差分が、#387 canonical scopeのexact allowlistとcontent restrictionだけに一致する。
- `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`src/spec_dock/assets/managed_distribution.json`、`src/spec_dock/assets/install_root/**`、provider workflows、quality sharder、distribution lifecycle testsに#387由来のsemantics driftがない。
- `pyproject.toml`のversionが`0.2.3`のままであり、#387が許可したstale mypy override / phantom package-data removal以外のbuild contract変更がない。
- current lint、ordinary pytest、current Full Regression verifier、package build、dogfood validateがbaselineとして記録できる。

admissionが不成立なら#392 implementationを開始せず、repository ownerへexact diffとfailed contractを提示する。implementation agentへ新しいProduct判断を委ねない。

## 9. Issue unit policy

Epic #384のimplementation-and-verification IssueはGitHub #392だけである。

- internal milestone、commit、複数PRは利用できるが、新しいIssue boundaryではない。
- 各PR/main merge pointはその時点のpublic productを壊さずreleasableでなければならない。
- baseline/rebaselineはadmissionとして許可するが、Product判断や仕様選択を残してはならない。
- successor proofより先にold production contractを削除しない。
- implementation completion、Issue finish、human PR merge、post-merge verification、Epic closeを別の状態として扱う。
- acceptanceが未達なら同じ#392をopenのままforward-fixする。

## 10. Externally observable acceptance

Epicは次のすべてが同一final PR treeと同一artifact identityに対して確認されたときだけ受入可能である。

- fixed mutation set外のconsumer data、seed、unknown path、unrelated skillがbyte-identicalである。
- fresh install、ready update、exact `0.2.3` migration、tooling uninstall、tooling-absent reinstallがbuilt wheelで成功する。
- durable tooling-absent recordとnever-installed absentが区別され、reinstallがseedを再作成しない。
- active legacy recovery、unsupported legacy、foreign target、unsafe bindingがmutation zeroでblockされる。
- root/slot各boundaryのfault後にsame candidate rerunで収束し、cross-intent / cross-candidateがblockされる。
- old exact `0.2.3` packageのcomposite tripwire event countが0で、native positive controlが捕捉され、tree digestが不変である。
- public CLI text/JSON/exit、`--keep-specs`、`--remove-specs` trapがcontractどおりである。
- approved failure 0、policy skip 0、duplicate contract ownership 0である。
- one build invocation、same wheel bytes、Linux canonical、macOS delta、sdist smokeがsource SHAへ束縛される。
- five-run budget、CPU ratio、seeded faults、rolling 20を満たす。
- old Full Regression、ledger、timing、sharder、policy skipがrepositoryから除去される。
- new required contextが実際にPRをblockし、human review/merge gateが維持される。
- human merge後のtree SHAがverified PR headと一致する。

## 11. Trace to the sole implementation Issue

| Epic requirement | Issue #392 responsibility |
|---|---|
| E384-RQ-001〜009 | fixed lifecycle、record、candidate、CLI hard cutover |
| E384-RQ-010 | old-package composite tripwire / downgrade proof |
| E384-RQ-011〜012 | test ownership map、active failure terminalization |
| E384-RQ-013〜015 | build-once provider gate、budget、old CI removal |
| E384-RQ-016 | required-context transition、human merge evidence |

No other implementation Issue is authorized.

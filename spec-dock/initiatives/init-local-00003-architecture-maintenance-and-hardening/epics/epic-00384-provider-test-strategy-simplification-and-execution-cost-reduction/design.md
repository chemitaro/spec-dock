---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md", "artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md"]
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

詳細: [Design Guide](../../../../docs/authoring/design.md)

## 設計目標

1. test execution graphを、fast / fullというpath分類から、durable contractを一度だけ証明する小さなportfolioへ変える。
2. shard / workerでwall timeだけを圧縮せず、単一pytest processで10分以内、平均論理core使用数1.1以下を満たす。
3. distribution product state spaceを、per-file historyとoperation checkpointの直積から、fixed root ownershipとrerun convergenceへ縮小する。
4. 利用者データ、共有skill parent、allowlist外pathをfail closedで守り、provider内部のlocal edit保存とautomatic recoveryを廃止する。
5. active failure ledger、timing weights、4-shard runnerを最終状態へ残さず、plain zero-failure GREENへ戻す。

## Current / Target

### Current

```text
same candidate
  ├─ Provider CI ordinary: 1,567 pass + 1,141 policy skip / 650.55s
  ├─ Ubuntu parity: managed + cutover + packageを再実行
  ├─ macOS parity: 共通ruleを含めて再実行
  └─ Full Regression: 2,708 nodesを4 shardで再実行
       wall 約99分 / shard-process合計 約5.51時間

distribution engine
  └─ fileごとのcurrent/historical identity
       × file kind / link / inode / parent binding
       × init / update / deprovision / purge
       × journal checkpoint / retry / recovery
```

`managed_distribution.py` は22,332行でprovider Python sourceの約44%を占め、主要4 test filesは約35,000行ある。現行testは無意味に増えたのではなく、広いproduct contractを複数boundaryで重複証明している。

### Target

```text
candidate build（1回）
  └─ exact artifact / source SHA / digestを固定

contract gate / Linux（単一pytest process、10分以内）
  ├─ pure ownership / state contracts
  ├─ root replacement + skill slot filesystem contracts
  ├─ CLI mapping smoke
  └─ built-artifact lifecycle smoke

platform boundary / macOS
  └─ macOSで差が出るfilesystem / executable / packagingだけ

result
  ├─ duplicate node = 0
  ├─ approved failure = 0
  ├─ shard / timing weights = なし
  └─ CPU / process / copy量をcandidate SHA付きで記録
```

production targetはaccepted ADR `20260831t005139z-adr` の **Option C2 — Disposable Root Replacement** とする。

## Ownership model

### Durable / opaque / generated

| class | paths | lifecycle contract |
|---|---|---|
| durable user data | `spec-dock/initiatives/**`、nested Artifacts | install / update / tooling uninstallは一切変更しない |
| opaque local data | `spec-dock/.workbench/**`、unknown paths | 探索・正規化・削除しない |
| generated projection | `active/**`、`.agent/**`、dashboard、tree / deps、ADR mirror | 配布差分を管理せず、各sync / rebuild ownerが再生成する |
| init seed | `spec-dock/.gitignore` | 初回配置後はconsumer-ownedとする案を優先。最終collision policyはR5Bで確定 |

### Disposable provider roots

次の4 pathだけをrepo-local provider contentのfixed allowlistとする。

1. `spec-dock/docs`
2. `spec-dock/templates`
3. `spec-dock/system`
4. `spec-dock/scripts`

root内部はcustomization pointではない。updateはinner fileのmodified / unknown / historical identityを判定せず、旧rootを削除してcandidate rootへ全量置換する。rootより上の `spec-dock/` は共有親なので削除しない。

### Fixed skill slots

`.agents/skills` は共有親であり、全量置換しない。SpecDockが管理するleaf rootは次だけとする。

- `.agents/skills/spec-dock`
- `.agents/skills/spec-dock-grill-with-docs`

各rootに `.spec-dock-owner.json` 相当のowner markerを同梱し、`schema_version`、`owner`、`slot`、`distribution_version` だけを持たせる。markerはexact slotのupdate / delete authorityであり、arbitrary pathやinner file digestを持たない。

## Cutover Issue ownership

4 disposable rootsと2 fixed skill slotsは同一candidate staging、同一update orchestration、同一installation record / ready markerを共有する。したがってinstall / update production cutoverは一つのchild Issueが所有し、rootsだけ、またはskillsだけがnew contractへ移行した状態を`ready(new version)`として公開しない。

tooling uninstall / purgeはinstall / updateより先に、legacy stateとfuture `InstallationRecordV2`を読むdual-reader / single-writer bridgeへcutoverする。bridgeはlegacy install / update writerを維持し、new workspaceへのupdateをfail closedにしながら、legacy workspaceとnew workspaceのtooling-only uninstallを安全に提供する。

install / update Issueはbridge merge後にnew writerへcutoverする。これにより、new writerが公開したworkspaceはmerge済みuninstallが必ず理解する。bridgeをProduct contractとして受理できない場合は、install / update / uninstall / purgeを一つのproduction vertical Issueへ統合し、中間状態を公開しない。

behavior testの作成・移動・削除は対応production Issueが所有する。包括的tests-only Issueは置かない。CI execution graph、external required-check transition、old machinery retirement、final performance evidenceは、それぞれ独立したsafe-transition / closeout Issueが所有する。

各production-changing Issueは、単独merge後の`main`でaccepted public lifecycle command matrixをGREENにし、後続Issueを待たない。

## Lifecycle compatibility interface

長期dual engineではなく、有限なreader compatibilityとsingle writerを設計する。名称は実装時にrepository styleへ合わせられるが、責務は次のstable contractへ分ける。

- `LifecycleStateReaderV1`: legacy-ready、tooling-absent-preserved-data、ready-v2、updating-v2、legacy-recovery-active、blockedをread-only分類する。
- `InstallationRecordV2`: fixed pathにschema、state、installed / desired version、candidate digest、2 skill slot versionsだけを持つ。arbitrary path、per-file digest、checkpoint listを持たない。
- `SkillSlotMarkerV1`: schema、owner、exact slot、distribution versionだけを持つ。
- `ToolingDeletePlanV1`: fixed roots、valid owned exact slots、installation recordだけをtyped targetにする。
- `PurgeAuthorityV1`: tooling lifecycleから独立したaccepted target evidenceとconfirmationを持つ。
- `LifecyclePublicResultV1`: dry-run / apply、text / JSON、exit、cleanup-pendingを一意にmappingする。
- `InventoryHeadV1` / `RemovalReceiptDeltaV1`: merge parent、result SHA、node inventory digestを連鎖する。
- `CandidateArtifactReceiptV1`: source SHA、build invocation、wheel / sdist digestを固定する。
- `RequiredCheckTransitionReceiptV1`: external required contexts、review gate、変更owner、検証結果を記録する。

## Deep interface

product behaviorをper-file action APIではなく、次の3 service boundaryへ集約する。名称は実装Issueでrepository styleへ合わせられるが、責務は分割しない。

### `install_tooling(target, candidate)`

- durable / shared collisionをpreflightする。
- 4 provider rootsを完全stage・validateして配置する。
- absent fixed skill slotsをowner marker付きで配置する。
- ready markerを最後に書く。
- unknown existing skill slotやunexpected root typeではwrite前にblockする。

### `update_tooling(target, candidate)`

- operation processがtarget `scripts` の外側にあることを要求する。
- fixed root / parent bindingを確認する。
- 4 candidate rootsをtargetと同一filesystemに全てstageする。
- `docs` → `templates` → `system` → `scripts` の順で全量置換する。
- valid owner markerを持つcurrent skill slotsをroot単位で置換する。
- finite retired slotsをexact name + valid markerでだけ削除する。
- 全配置後にsmall ready markerをatomic file replaceする。
- cleanup failureをrollbackせず、診断付き成功またはbounded cleanup pendingとして扱う。
- rootsだけ、またはskillsだけがnew contractへ移行した状態をreadyとして扱わない。
- old per-file engineとnew root replacement engineをruntime toggleで併存させない。

### `uninstall_tooling(target)`

- fixed provider roots、owned fixed / retired skill slots、installation recordだけを削除する。
- durable user data、`.workbench`、generated projections、unrelated skills、unknown pathsを変更しない。
- spec history purge authorityを持たない。
- unexpected root type / binding / marker mismatchで対象delete前にblockする。

CLIはargument、confirmation、text / JSON、exit codeをmappingするadapterに限定し、ownership policy、recursive traversal、journal transitionを持たない。

## Proposed installer module boundary

`managed_distribution.py`の後継は、少なくとも次の責務を分離する。名称は実装Issueがrepository styleへ合わせる。

- model: fixed root / slot、marker schema、ready state、action order
- service: install / update / uninstall orchestration
- filesystem: no-follow binding、same-filesystem staging、root replacement
- migration: finite one-shot legacy recognition

arbitrary historical catalog、scheduler、baseline、journal state machineを新moduleへ移植しない。

## Update protocol

### Preflight

1. repository rootと `spec-dock` parentをsymlink-followなしでbindingする。
2. root allowlistがcompile-time fixedであることを確認する。
3. installation recordを読む。current schemaならroot ownershipを認め、legacy no-markerなら有限one-shot adapterだけを試す。
4. fixed skill slotsのmarkerを検証する。unknown collisionが一つでもあればtarget mutation前にblockする。

### Stage / validate

1. candidate packageから4 rootsとmanaged skill rootsをstagingへ展開する。
2. required entrypoint、mode、tree digest、slot markerをcandidate側で検証する。
3. action setにdurable / opaque / generated / allowlist外pathがないことを確認する。
4. すべて成功するまでtargetを変更しない。

### Replace / ready

1. root bindingを再確認する。
2. 4 provider rootsを固定順でdelete + renameする。
3. skill slotをfixed exact pathごとにreplaceする。
4. installation record / ready markerを最後にatomic replaceする。
5. staging残存をbest effortでcleanupする。

Python / Linux / macOSで非空directory同士のcross-platform atomic exchangeはpublic guaranteeにしない。各rootのdelete + renameと、複数rootの順次置換を正直なfailure modelとして受け入れる。

## State / failure model

### 最小state

- `absent`: provider roots / valid ready markerがない。
- `legacy-ready`: accepted finite evidenceで現行workspaceを認識できる。
- `tooling-absent-preserved-data`: provider toolingはなく、user data / generated projectionだけが残り、accepted install routeで再installできる。
- `ready(version A)`: ready markerとexpected fixed roots / slotsがAを示す。
- `updating-v2(desired B, digest D)`: stagingまたはold/new/missing rootが混在し、same desired version / digestのexternal rerunだけを許可する。
- `legacy-recovery-active`: accepted legacy journal / markerが残り、bounded recovery-only adapterまたはlast-compatible package pinが必要である。
- `blocked`: root binding、type、shared slot ownership、candidate integrityを証明できない。

per-file checkpoint、intent別journal、quarantine、rollback image、cross-intent resumeをstate modelへ持ち込まない。

### Failure contract

| failure | result | next action |
|---|---|---|
| stage / validate failure | target旧stateを維持 | candidate修正後に再実行 |
| root削除前のfailure | target旧stateを維持 | 再実行 |
| delete後・rename前 | 一root欠落、user data不変 | external updaterから再実行 |
| root間の停止 | mixed roots、ready markerは旧 | desired versionを再実行して全root再置換 |
| scripts後・ready前 | repo-local復旧不能の可能性 | installed package / `uvx`から再実行 |
| ready後cleanup failure | candidateはready、staging残存 | update成功。bounded cleanupを後実行 |
| symlink / rebind / marker mismatch | write前block | diagnosticに従い人間が境界を修復 |

whole-operation rollbackは提供しない。provider toolingの一時availabilityより、user dataとshared contentを削除しないことを優先する。

## Skill lifecycle

### Current slot

- absent: marker付きcomplete rootをinstallする。
- owned: complete candidate rootへ置換する。inner editsは保存しない。
- marker missing / invalid / foreign: preserveしてblockする。
- unrelated name: scanもmutationもしない。

### Retired slot

- exact slot nameをcode内の有限allowlistに持つ。
- valid `owner=spec-dock` とexact slot一致を削除条件にする。
- migration window終了時にslot entry、adapter、fixtures、testsを同時削除する。
- prefix patternやworkspace manifestでdelete対象を増やさない。

marker以前のcurrent 2 rootsは、一回限りのexact tree recognitionでmarker付きrootへ移す。このlegacy proofをgeneral historical catalogへ成長させない。

## Test portfolio

| layer | 証明する責務 | 証明しないもの | target cost |
|---|---|---|---:|
| pure/domain | fixed classification、marker schema、action order、state transition | real process / Git / package build | 30秒以内 |
| filesystem/service | whole-root replace、user data不変、fault後rerun、symlink / binding block | historical file cross-product | 3分以内 |
| CLI adapter | parser、confirmation、exit、JSON/text mapping | service matrixの再実行 | 1分以内 |
| artifact lifecycle | exact wheelでinit → update → tooling uninstall | pure rules、wheel/sdist全use-case反復 | Linux 4分以内 |
| platform delta | macOS固有mode / executable / rename behavior | Linux共通contract | macOS 4分以内 |

Linux canonical portfolioはcollection / variance headroomを含め10分以内とする。macOSでpure / CLI共通testを再実行しない。

test ownershipはlayerではなくbehavior ownerへ帰属させる。uninstall / purge bridgeはlegacy admission、tooling-only delete、purge、post-uninstall reinstallを同じIssueで証明する。install / update cutoverはroot replacement、ready / updating state、same-version rerun、skill write lifecycleを同じIssueで証明する。distribution外のactive failureはinventoryが示すdurable contract ownerへfan-outし、current authorityから期待動作を決められないnodeだけ個別decision Issueへ戻す。

CI Issueはlane assignment、selector、metrics、artifact receiptだけを所有し、production behaviorのsuccessor testを後付けしない。behaviorを変えないexact duplicate cleanupはinventoryが独立acceptanceを証明した場合だけsafe-transition Issueにできる。

### Keep

- allowlist外へ書かない・削除しないnegative proof
- root / parent symlink・rebind・unexpected typeのpre-write block
- durable user dataとunrelated skillのbyte-identical proof
- incomplete stagingがtarget mutationを開始しないproof
- root間fault後にsame desired updateが収束するproof
- skill owned / unknown / retired boundary
- exact candidate artifact lifecycleと実OS差

### Delete after replacement proof

- provider root内per-file modified / unknown / inode / historical digest matrix
- action pre/post SHA、per-checkpoint journal resume、cross-intent recovery
- provider file preservation / closed-set directory evidence
- normal uninstallとspec-history purgeの統合matrix
- obsolete skill fileを個別path / hashで追跡するcatalog tests
- 同一nodeをordinary / parity / Full Regressionで再実行するselector
- successor proofが揃ったfailure ledger、timing weights、shard runnerとmeta-tests

testがslowという理由だけでは削除しない。retired contractまたは同じinvariantのowner proofへ必ず結び付ける。新contractを追加して旧testも残すadditive migrationは禁止する。

## Candidate build / budget reporting

- candidate artifactはSHA-256とsource commitを固定して一度buildする。
- Linux / macOS smokeは同じbytesを使用し、jobごとにrebuildしない。
- sdistはpublic distribution requirementが同じならrelease / metadata / import proofへ縮小する。triggerはR5Bで確定する。
- CI summaryはwall、child user/system CPU、node、subprocess、temp workspace、copy bytes、duplicate node、artifact build countをcandidate SHAへ束縛する。
- budget violationはfailureであり、worker追加やtiming-weight調整で回避しない。
- reporterは標準time / pytest reportの薄い集約とし、新しいschedulerやbaseline frameworkにしない。

## Removal receipt

production route、test node、workflow machineryを削除するchangeは、次をlatest inventory head、merge parent SHA、result SHAへ束縛して記録する。

- owner Issue
- retired contractまたはsuccessor contract
- removed production symbols / manifest sections
- removed test node IDs
- successor test node IDs
- focused verification command
- result SHA
- parent / result node inventory digest

rebase後はdelta receiptを再生成し、並行PRはmerge順確定後に再照合する。testがslowであることだけをretirement authorityにしない。production contractの廃止authorityをtests-only Issueが後付けしない。

## Migration / compatibility

1. `iss-00388`、`iss-00389`、`iss-00390`のdecision-only Issuesと、fixed baseline SHAのrolling inventoryを並行して完成する。
2. inventoryがactive failureをdurable behavior ownerへ割り当て、判断不能nodeだけ個別decision gateへ戻す。
3. legacy install / update writerを維持したまま、tooling-only uninstall / purgeをdual-reader bridgeへcutoverし、post-uninstall reinstallを含むpublic lifecycle matrixをGREENにする。
4. bridge merge後、install / updateを4 roots + 2 slots + `InstallationRecordV2`へcutoverし、old package / writerのnew workspace mutationをfail closedにする。
5. 各production Issueがsuccessor testsとold route / test receiptを同じPRで完了する。active failure repairもbehavior ownerごとにmergeする。
6. new canonical gateをnon-required shadowとして追加し、artifact build once、Linux canonical、macOS delta、metricsを検証する。
7. external required contextsをold requiredからold + new required、new required + old non-requiredへ移す。
8. new checkだけがrequiredであることを再取得してから、old Provider CI / Full Regression、ledger、timing weights、shard machineryを別PRで撤去する。
9. fixed reference 5 runsとrolling 20 runsのacceptance evidenceを取得する。

old / new engineを長期dual modeにしない。destructive safety issueが見つかった場合はapply routeを停止し、read-only diagnosticへ戻す。旧engineへのautomatic fallbackは行わない。

test selector defect時のrollbackはshard / approved failureの再導入ではない。全correctness portfolioをsingle pytest processで実行するfail-closed gateへ戻す。

### Cross-version release sequence

```text
P0: legacy writer + legacy reader
  -> P1: legacy install/update writer + new uninstall/purge dual-reader
  -> P2: new install/update writer + new uninstall/purge dual-reader
  -> P3: new-only reader/writer after accepted sunset
```

- `P0 × ready-v2`、`P0 × updating-v2`はmutation前にfail closedにする。
- `P1 × legacy-ready`はlegacy install/updateとnew uninstall/purgeをGREENにする。
- `P1 × tooling-absent-preserved-data`はaccepted install routeで再installできる。
- `P1 × ready-v2`はuninstall / dry-runを許可し、update / init-forceはfail closedにする。
- `P2 × legacy-ready`はexact finite evidenceがあるone-shot migrationだけを許可する。
- `P2 × ready-v2`は全accepted lifecycleをGREENにする。
- `P2 × updating-v2`はsame desired external rerunだけを許可する。
- `P3 × legacy-ready`はactionable diagnostic付きでfail closedにする。

### CI transition state machine

```text
OLD_REQUIRED
  -> OLD_REQUIRED + NEW_SHADOW
  -> OLD_REQUIRED + NEW_REQUIRED
  -> NEW_REQUIRED + OLD_NON_REQUIRED
  -> NEW_REQUIRED_ONLY
```

new contextはold contextを残したままrequiredへ追加し、failure canaryでmerge blockを確認する。old workflowはnew-only requiredを再取得するまでrepositoryに残す。external settingsとcode PRは同一transactionとみなさず、各transitionにreceiptとrollback条件を持たせる。

## 変更対象

- `src/spec_dock/cli.py`
- `src/spec_dock/managed_distribution.py` またはそのreplacement service modules
- `src/spec_dock/assets/managed_distribution.json` の廃止 / finite migration化
- `src/spec_dock/assets/spec_dock/{docs,templates,system,scripts}`
- `src/spec_dock/assets/install_root/.agents/skills/{spec-dock,spec-dock-grill-with-docs}`
- distribution / init-update / cutover / package tests
- `tests/conftest.py` のpath-based policy
- Provider CI / Full Regression workflows、ledger、timing weights、verifier

維持する境界:

- user-owned canonical specsとArtifacts
- unknown / shared pathを削除しないfail-closed原則
- candidate SHA / artifact digestに束縛したevidence
- human PR merge gate
- Issue #372 candidateは別branch / Issueとして変更しない

## Risk

| risk | impact | mitigation |
|---|---|---|
| provider root内のlocal editが消える | undocumented customization loss | update前diagnosticとpublic warning。customizationはforkへ送る |
| mid-updateでtoolingが欠落する | repo-local commandを実行できない | external installer route、ready marker、same-version rerun手順を必須化 |
| allowlist実装誤り | user data削除 | compile-time fixed roots、root / parent binding、negative seeded fault |
| skill marker spoof / mismatch | foreign skillの上書き・削除 | fixed exact slot、marker schema / slot一致、unknown preserve-and-block |
| legacy adapterが恒久化 | complexity再増加 | version/date sunsetとadapter/test同時削除をacceptanceにする |
| behavior testを後続Issueへ送る | merge pointで保護が欠落する | production cutoverとsuccessor proof、old route / test deletionを同一Issueで受け入れる |
| test削減でOS退行を失う | filesystem/package defect | OS差のあるboundaryだけをbuilt-artifact smokeで残す |
| required checkの外部設定とworkflow削除がずれる | gate空白または永続pending | additive shadow、old+new required、new-only required、old removalを別transitionにする |

## Authority / open decisions

- accepted authority: `artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`
- detailed synthesis: `artifacts/20260831t005132z-disc-disposable-root-replacement-and-skill-lifecycle-design.md`
- superseded in part: Epic #365 ADRのper-file operation / journal / shared deprovision-purge engine
- open before affected Issue start: workflow ownership、legacy window、purge CLI migration、`.gitignore` seed policy、artifact/platform triggers

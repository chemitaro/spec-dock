---
種別: disc
ID: "20260830t235429z-disc"
タイトル: "Provider Test Strategy Simplification Decision Analysis"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-31"
親: ["epic-00384"]
template: "disc"
authority: "evidence"
derived_from: ["20260830t234548z-research", "chatgpt-use:required-repository-connector-context-repository-138"]
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
---

# 20260830t235429z-disc Provider Test Strategy Simplification Decision Analysis

最新repository / CI evidence、user observation、独立したChatGPT Use reviewを材料に、product / test architectureの選択肢を比較する。ChatGPT Useはadvisoryであり、最終判断はlocal source、実行artifact、Epicの制約に照合する。

## Inputs

- `20260830t234548z-research-provider-test-suite-root-cause-analysis-and-redesign.md`
- Issue #372 latest concurrent branch `7af12c54bb73de63fdca6ea94853138a17e275a0`
- Provider CI run https://github.com/chemitaro/spec-dock/actions/runs/33327601995
- Provider Full Regression run https://github.com/chemitaro/spec-dock/actions/runs/33327608584
- Issue #372 Step 10B local verifier evidence at `bc1560096593c645ec0309a37a080c53a7e7f35d`
- user requirement: 約4時間のtestを約10分へ短縮し、並列化によるCPU 100%依存ではなく、不要test削除とtest自体の単純化を行う。
- ChatGPT Use session `required-repository-connector-context-repository-138`。最新branchのsource / workflows / ledgerと、数値を固定したevidence bundleを添付した。

## Synthesis

### 結論

最優先で変えるべきものはshard数ではなく、distribution product contractである。現在のtest suiteは、22,332行の `managed_distribution.py` が持つ大きなstate spaceを異なるboundaryで重複証明している。product behaviorを維持したままtestだけを大量削除するとdestructive filesystem safetyを失い、workerだけを増やすとCPU / process costを悪化させる。

推奨方針は次の順序である。

1. init / update / uninstall / purgeの利用者価値を再定義する。
2. provider-owned bytesとuser-owned historyを分離する。
3. global journal / rollback型engineを、atomic actionを再評価して収束する有限state reconcilerへ縮小する。
4. durable invariantを最も安いlayerで一度だけ証明する。
5. exact artifactを一度buildし、OS差だけをplatform smokeへ残す。
6. 26 active failureをfix / obsolete delete / successor replaceし、ledger / sharderを撤去する。
7. 単一pytest process・10分・平均論理core使用数1.1以下・duplicate node 0をbudget gateにする。

### 一致する事実

- 4 shardはwallを短くするが、GitHub実測で約5.51 shard-process-hoursを残す。
- fast suiteはすでに10分50秒で、Full Regressionが同じ1,567 fast nodesを再実行する。
- managed distribution 575 casesは同一candidateでUbuntu ordinary、Ubuntu parity、macOS parity、Ubuntu Full Regressionの4回実行される。
- collectionは約8秒であり、test discoveryではなくtest bodyとboundary crossingがcost中心である。
- test LOCはproduction Pythonの約1.90倍で、distribution関連に集中する。
- path-based fast / full分類はcostとcontract ownerを表していない。
- approved failure lifecycleは移行証拠として有用だが、zero-failureへ収束しない限り恒久的なmeta-test負債になる。

### 未確定事項

- `--remove-specs`をproductとして維持する必要があるか。
- arbitrary crash checkpointからautomatic rollback / resumeすることが利用者要件か、過剰な実装要件か。
- direct updateすべきhistorical workspaceのwindow。
- repo-local copied runtime / offline self-contained behaviorの必要性。
- `init --force`、old payload保持数、cleanup failureをpublic failureとするか。
- wheel / sdist、macOS parity、exact dogfood parityを毎PRどこまで保証するか。
- CLI flags / JSON shapeのbreaking change / deprecation policy。
- latest exact SHAを単一processで実行したchild-inclusive CPU seconds。
- 全2,708 nodesの個別keep / delete判定。

上のProduct decision 6 groupsはProduct ownerが決める。未回答を下位Issueが暗黙に決めると、test削除の正当性またはproduct compatibilityのどちらかが崩れる。

### 根本原因と対策の対応

| root cause | 対策 | やらないこと |
|---|---|---|
| distribution state space | ownership分離、有限compatibility、収束型operation | 現行stateをすべて保持したままtestだけ削除 |
| contract重複 | invariantごとに一つのowner layer | unit / CLI / packageの全層で同じmatrix |
| CI重複 | node-setをlane間で排他的にしartifactを一度build | exact same Ubuntu nodeの再実行 |
| expensive mechanics | minimal synthetic workspace、in-process adapter test、少数artifact smoke | per-test venv / build / 44 MB clone |
| historical additive tests | durable invariantへ改名・successor統合 | Issue / Step prefixを永久契約にする |
| 26 approved failures | fix / delete / successor後にledger撤去 | signature承認をsteady stateにする |
| CPU saturation | 単一processで10分へ縮小 | shard / worker追加をprimary KPIにする |

## Options and trade-offs

### Option A — 現行product contractを維持し、shard / cache / timingだけ改善

内容:

- 22,332行のdistribution state machineと全historical compatibilityを維持する。
- shard balance、worker数、runner性能、fixture cacheを改善する。

利点:

- current behaviorを変えない。
- Issue #372の投資を直接利用できる。
- 短期のwall改善は最も早い。

制約:

- CPU / process-hoursは減らないか増える。
- 26 failure baseline、timing weights、shard runnerが恒久化する。
- test authoringとCI理解の複雑性を解消しない。
- 単一process10分という本Epicの受け入れ条件を満たしにくい。

判断: **却下**。緊急の一時措置にはなり得るが、利用者が求める根本解ではない。

### Option B — production contractは維持し、testだけlower layerへ移す

内容:

- CLI / package casesの多くをpure / filesystem contract testへ置換する。
- duplicate node、venv、clone、subprocessを削減する。

利点:

- public behavior変更が少ない。
- boundary costは大きく減らせる可能性がある。
- Option AよりCPU / wall双方を改善できる。

制約:

- 現行recovery stateの全組合せをどこかで証明する必要が残る。
- 22,332行のproduction complexityと保守負債は残る。
- test削減が「実装詳細をunitで固定しただけ」になる危険がある。

判断: **移行手段として一部採用、最終案としては不足**。

### Option C — product contractとtest portfolioを同時に簡素化

内容:

- provider-owned / user-owned境界を分離する。
- init / updateはimmutable payloadのstage + validate + activation record一つのatomic swapとする。
- uninstallはexact provider-owned bytesだけを削除し、historyを保持する。
- arbitrary automatic rollback / cross-intent resumeを外す。
- compatibilityを有限windowにする。
- pure、filesystem contract、CLI smoke、artifact/platform smokeの4責務へ集約する。

利点:

- test state spaceとproduction state spaceを同時に減らす。
- fail closedを保ちながらautomatic recoveryの複雑性を外せる。
- 単一process10分、duplicate zero、zero failureへ到達する説明力が最も高い。
- simple toolというproduct goalと一致する。

制約:

- Product判断とmigrationが必要。
- 一部historical workspaceはdirect updateできなくなる可能性がある。
- automatic recoveryに依存する利用者がいればbehavior changeになる。
- old/new engineを長期並置すると逆にtestが増えるため、cutover disciplineが必要。

判断: **第一推奨**。

### Option D — repo-local distribution / uninstallを廃止し、package-onlyへ寄せる

内容:

- provider runtimeはinstalled packageからのみ実行する。
- repositoryにはuser dataと最小configurationだけを置く。
- uninstallはpackage managerに委ね、repo historyの自動cleanupを行わない。

利点:

- product / test architectureは最も小さくなる。
- repo filesystem migrationと多くのdestructive testを廃止できる。

制約:

- offline / self-contained repository、checked-in runtime、agent skill / workflow配布の要件と衝突する可能性がある。
- consumer workflowとdistribution modelの大きな変更になる。
- Issue #372のhard-cutover goalを再評価する必要がある。

判断: **長期候補**。repo-local runtime不要が確認できた場合はOption C内の最小形として選ぶ。

### 推奨Product判断

| question | 推奨 | 理由 | 推奨を採らない場合のcost |
|---|---|---|---|
| spec-history purge | 自動 `--remove-specs` を廃止 | user data削除とprovider deprovisionを分離 | purge専用security contractとplatform smokeを維持 |
| lifecycle / recovery | `init --force`を廃止またはpayload reinstallに限定し、automatic rollback / arbitrary checkpoint resumeを外す。current + previousの最大2世代 | activation swap +再実行 + block診断でstateを有限にする | force / journal / GC / recovery matrixを維持 |
| compatibility | current + N-1 | 無期限historical identityを切る | 古いversionごとのmanifest / migration testsを維持 |
| repo-local runtime | 不要ならpackage execution、必要なら一つのversioned payload | provider-owned surfaceを縮小 | scattered mutable filesのreconcile testsを維持 |
| artifact / platform | wheelを通常PR、sdistをrelease、macOSはOS差だけ、dogfoodはmanifest / hash中心 | 同じlifecycleの再実行を避ける | package / OS / large-copy costを毎PR維持 |
| public compatibility | 旧CLI / JSONの廃止をdeprecationまたはbreaking changeとして明示 | adapterとtestのsunsetを可能にする | 旧flag / shape testsを無期限維持 |

### keep / move / consolidate / deleteの具体基準

#### Keep

- unknown / foreign pathを削除しない。
- symlinkをfollowしない、parent / root rebind時に書込み前停止する。
- provider content hash / artifact digest / candidate SHAを照合する。
- partial recognized stateへ同じcommandを再実行すると収束する。
- uninstall後もuser spec historyがbyte-identicalである。
- Linux / macOSで実際に差が出るatomic replace、mode、executable、symlink、package metadata。

#### Move

- manifest schema、path normalization、action ordering、state transition matrixをpure/domainへ移す。
- error codeからCLI JSON / text / exit codeへのmappingをin-process adapter testへ移す。
- fault checkpointの多くをfilesystem syscallではなくpure transition / injected portへ移す。
- package内で再検証しているdomain ruleをservice contractへ移す。

#### Consolidate

- `s35`〜`s70`、`i368`〜`i371` testsを現在のdurable invariant名へ統合する。
- fresh / update / uninstall / marker / retry / symlink / preserveを4 test filesで繰り返すmatrixをowner layer一つへ集約する。
- regular / symlink / hardlink / FIFO、before / after checkpointの完全直積を、equivalence partition + pairwise +少数property testへ変える。
- wheelとsdistの同一use case反復を、wheel end-to-end + sdist build / metadata / import proofへ縮小する。

#### Delete / Retire

- 廃止したautomatic rollback / cross-intent recovery / purge contractだけを守るtest。
- current public invariantへ追跡できず、historical Issue名だけが保持理由のtest。
- exact same node / invariantを別lane・同じOSで再実行するselection。
- lower layerで同じnegative behaviorを決定的に証明し、CLI / packageで新しいboundary riskを追加しないtest。
- fix / delete / successor receiptが揃った26 active failure nodeのledger row。
- zero-failure cutover後のbaseline evaluator、timing weights、4-shard runnerとそのmeta-tests。

testがslowという理由だけでは削除しない。上のいずれかとreplacement / retirement evidenceを満たす場合だけ削除する。

### 26-failure baselineの撤去順序

1. 26 nodesをcontract familyへgroup化する。
2. 各nodeを `valid-current-bug`、`obsolete-contract`、`duplicate-proof`、`renamed/replaced` に分類する。
3. current bugはfixし、obsoleteはRequirement / Designでretireし、duplicateはowner proofへlinkする。
4. successorはexactly once collected / executed、passed、not skippedを同一candidateで証明する。
5. active countを段階的に0へする。新しいactive row追加を禁止する。
6. zero-failure canonical commandを複数回通す。
7. ledger JSON、baseline parser / evaluator、pytest observation hook、timing weights、4-shard runner、関連meta-testsを一つのcutoverで削除する。
8. historical receiptはArtifact / Git historyに残し、runtime quality gateへ残さない。

### Issue granularity判定と条件付き候補

`assess-issue-granularity` の結果は `RETURN_TO_PARENT` である。R5AのProduct判断が未受理のため、現時点でIssue数をacceptedにせず、子Issueを作成しない。

判断後のproposal:

1. **evidence / invariant inventory** — 2,708 nodesを100%分類し、cost、duplicate、fault pack、replacement / retirement pathを固定する。
2. **immutable payload / atomic activation** — init / updateをstage、validate、single activation swapへ縮小し、対応testを同じsliceで統合する。
3. **provider-only uninstall / purge boundary** — history不変uninstallとpurge廃止または独立化をend-to-endで受け入れる。
4. **legacy migration / support sunset** — 必要な場合だけone-shot migratorと終了条件を受け入れる。
5. **active / context / GitHub resolution cluster** — active failures 12 nodesをplain GREENまたはaccepted retirementへする。
6. **import / sync cluster** — active failures 9 nodesを処理する。
7. **delete / shell / sync / workbench cluster** — remaining 5 nodesを処理してactive countを0にする。
8. **build-once artifact / compact platform portfolio** — exact artifact一回、wheel lifecycle、sdist / macOSのaccepted boundary、dogfood縮小を受け入れる。
9. **CI budget cutover / old machinery removal** — duplicate 0、単一process10分、平均論理core1.1以下、plain pytest GREENを確認し、ledger / weights / sharder / policy flagsを一括撤去する。

候補2〜4はproduction behaviorと対応testsを一緒に所有し、pure / filesystem / CLIというtechnical layerだけでIssueを分けない。候補5〜7は異なるpublic behavior clusterとして独立受け入れできる。候補9は他の全候補に依存する。

### 反証条件

推奨Option Cを次で反証する。

- 実利用者がarbitrary checkpointからのautomatic recoveryを必要とし、manual retry / re-initを受け入れられない。
- N-1より古いworkspaceが継続的に存在し、one-shot migrationでは運用不能である。
- repo-local copied runtimeがoffline / audit / agent operationの必須要件で、versioned payloadへ集約できない。
- pure / serviceへ移した後、mutation testingまたはhistorical bug reproductionで重要なboundary regressionを検出できない。
- single-process prototypeがcontract削減後も10分を大幅に超え、costの主因が別moduleにある。
- simplified reconcilerがunknown / drift / rebind時のfail-closed proofを満たさない。

一つでも成立すればRequirement / Designへ戻り、該当contractを残す。ただし残すcontractのcostを明示し、worker増加で隠さない。

### 却下する近道

- shardを4から8へ増やす。
- 高性能runnerへ変えるだけで合格にする。
- slow testをすべてpost-mergeへ移し、PRを速く見せる。
- approved failure上限を増やす。
- `pytest --durations`の上位だけを削除する。
- full dogfood cloneをRAM disk / cacheへ置くだけで契約重複を残す。
- path markerを細かく増やして新しいlane schedulerを作る。
- old/new distribution engineを恒久的に並置する。

## Reflection

- Option CをEpicの推奨targetとして `design.md` に反映した。
- 単一pytest process・10分、duplicate node 0、artifact build 1、approved failure 0を `requirement.md` のacceptanceへ反映した。
- Product判断6 groupsをimplementation開始前のgateとして `requirement.md` / `plan.md` に反映した。
- granularity result `RETURN_TO_PARENT` と、判断後の条件付き9候補を `plan.md` に反映した。
- 本ArtifactはProduct判断の代替ではない。R5Aが未回答の間、Epic documentsはdraftを維持し、子Issueを作成・開始しない。
- ChatGPT Use advisoryはlatest branch `7af12c54...` をGitHub connectorで照合し、production state spaceが支配的というlocal analysisを支持した。immutable payload / single activation swap、固定2 vCPU reference、seeded fault pack、legacy sunset、failure cluster分割を追加採用した。
- advisoryが提案した `p95 CPU ≤ 900 core-seconds` は、10分wallに対して平均1.5 coresを許し、利用者のCPU懸念に対して緩い。本Epicではより厳しいchild-inclusive平均論理core1.1以下を維持する。

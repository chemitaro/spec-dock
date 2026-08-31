---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-08-31"
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

詳細: [Requirement Guide](../../../../docs/authoring/requirement.md)

## 目的

SpecDock provider のテストを、並列実行で待ち時間だけを隠す仕組みから、必要な契約を最小の実行量で証明する仕組みへ置き換える。開発者が通常使う回帰確認は、shard や `pytest-xdist` を使わない単一の `pytest` process で10分以内に完了し、同じ candidate・OS で同じ契約を重複実行しない状態を成果とする。

テストだけを削るのではなく、テスト件数を生んでいる install / update / uninstall / spec-history purge の product contract も見直す。安全上必要な不変条件は残し、利用者価値を持たない自動復旧、歴史的互換性、状態の組合せは product contract から縮小してからテストを廃止する。

## 背景

Issue #372 は distribution hard cutover と parity を対象とし、Full Regression を4 shardで実行する仕組みを導入している。この仕組みは証拠を分割して壁時計を短縮するが、テスト実行量そのものは減らさない。最新 branch の実測では、2,708 tests の GitHub Full Regression が約99分の壁時計と約5.51 shard-process-hoursを使った。別のローカル実測でも約27分の壁時計に対して約87.65 shard-process-minutesを使っている。利用者からは、別時点の逐次実行が約4時間、並列実行中は約10分にわたりCPUがほぼ100%になるとの観測がある。

通常の PR gate も `1567 passed, 1141 skipped in 650.55s` であり、すでに目標の10分を超える。Full Regression はこの1,567 fast testsを再度実行する。distribution parity は Ubuntu 上で通常 gate と同じ575件の `test_managed_distribution.py` を再実行し、さらに Linux / macOS で cutover と package parity を繰り返す。

テスト量は production design と分離できない。`src/spec_dock/managed_distribution.py` は22,332行、41 classes、454 functions / methodsを持ち、provider Python sourceのおよそ44%を占める。対応する4つの主要 test filesだけで約35,000行ある。単純なローカルツールという product goal に対し、per-path identity、journal、retry marker、crash checkpoint、historical compatibility、deprovision、spec-history purge の組合せが永続的な契約になっていることが、テスト肥大化の主因候補である。

本 Epic は親 Initiative の architecture hardening 方針を維持しつつ、「安全であること」と「すべての歴史的・異常状態を自動回復すること」を分離する。Issue #372 の candidate を直接変更せず、独立した product / test architecture outcome として扱う。

## 観測可能な要件

### R1. 一つの実行時間予算

- 開発者向け canonical regression command は、単一の `pytest` processで全ての merge-required contractを実行する。
- 同一条件で連続5回計測した各回が、dependency installとlintを除く test bodyで600秒以内となる。
- CIのreference measurementはdependency install完了後、fresh workspace、network accessなし、Linux 2 vCPU hard quota、8 GiB memoryを基本とする。GitHub-hosted runnerがhard quotaを保証できない場合は2 vCPU containerまたはdedicated runnerでreferenceを取得する。
- canonical commandは内部でshard、`pytest-xdist`、並列test workerを起動しない。テストが起動するCLI subprocessも、1 test内で明示的に必要なものを除き直列とする。
- 計測はwall secondsだけでなく、user + system CPU seconds、subprocess数、temp workspace作成数、同一nodeの重複実行数を残す。
- child processを含む `user + system CPU seconds / wall seconds` を平均論理core使用数として扱い、canonical local regressionの5回すべてで1.1以下とする。これにより、短い起動overlapを許しつつ、複数coreを長時間使い切る設計を禁止する。

### R2. 重複実行ゼロ

- 同じcandidate・OS・契約について、merge判定までに同じtest nodeを複数laneで実行しない。
- platform固有の差分を確認するtestだけを各OSで実行し、OS非依存のdomain / service contractをLinuxとmacOSの双方で繰り返さない。
- wheelとsdistはcandidateごとに一度だけbuild・hash固定し、その同じartifactを必要なsmokeで再利用する。

### R3. 契約追跡可能性

- 残すすべてのtest familyは、現在のpublic behaviorまたはsecurity invariant、責務を持つlayer、実行lane、代表する失敗を一つ以上持つ。
- historical Issue / Step 名だけを根拠とするtestは、durable invariantへ改名・統合するか、対応契約とともに削除する。
- test削除は、同じ invariant をより低い層で証明するtest、または product contract の廃止記録に結び付ける。

### R4. layerごとの証明責務

- domain testは純粋な状態遷移・validation・propertyを網羅し、filesystem、Git、package build、CLI processを起動しない。
- filesystem / application contract testは、最小synthetic workspaceと注入可能なfaultを使い、OS境界の代表ケースだけを扱う。
- CLI testはargument / exit code / JSON・text mappingと、代表的なhappy path・fail-closed pathに限定する。
- package / platform testはbuilt artifactのprovenanceと、init・update・uninstallの最小end-to-end smokeだけを扱う。

### R5. distribution product contractの簡素化

- `spec-dock/initiatives/**` とnested Artifactsをdurable user dataとし、init / update / tooling uninstall / retry / cleanupの変更対象にしない。
- `spec-dock/active/**`、`spec-dock/.agent/**`、dashboard、tree / deps図、ADR mirrorなどの再生成可能なprojectionをprovider file inventoryやhistorical identityの管理対象にしない。
- provider-owned repo-local contentは `spec-dock/{docs,templates,system,scripts}` の4 fixed rootsとし、updateではcandidateを全てstage・validateした後、root内部を保存せずroot単位で全量置換する。`scripts` は最後に置換する。
- disposable root内部のuser editは保存しないことをpublic contractにする。inner fileごとのmodified / unknown / historical identityを判定しない。
- root allowlistはcodeに固定し、root / parent binding、symlink、unexpected typeをdestructive step直前に検証する。shared parentやallowlist外pathへ削除authorityを広げない。
- 4 root全体のatomic transaction、自動rollback、per-file checkpoint resume、cross-intent recoveryをpublic contractにしない。partial failure後は外部installerから同じdesired versionを再実行して収束させる。
- small installation record / ready markerは1つだけとし、schema、version、candidate digest、fixed skill slot versionを持つ。per-file stateや任意pathを持たない。
- 通常uninstallはprovider toolingだけを削除し、user-owned spec historyを常に保持する。spec history purgeは通常uninstallから分離する。

### R5A. managed skill contract

- `.agents/skills` 親全体を置換・探索・削除しない。
- managed skillを `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` の2 fixed slotsに限定する。
- 各slot rootへowner / slot / schema versionの小さなmarkerを置き、valid markerがあるexact slotだけをroot単位でupdate / uninstallする。
- marker欠落・不正・別ownerのslotは上書きも削除もせず、書込み前にblockする。unrelated skillsは常に保持する。
- retired skillはcodeに固定された有限のexact-slot allowlistとvalid old markerでだけ削除し、prefix match、arbitrary manifest path、per-file historical digestを削除authorityに使わない。
- marker導入前のcurrent 2 skill rootsは期限付きone-shot migrationでのみ認識し、移行終了後は旧identityとtestsを削除する。

### R5B. Product decision status

accepted ADR `20260831t005139z-adr` により、次を確定した。

1. user historyは常にuser-ownedであり、tooling lifecycleからpurge authorityを除外する。
2. repo-local runtime layoutは4 disposable rootsを維持し、immutable version payload / activation pointerではなくroot replacementを使う。
3. automatic rollback / arbitrary checkpoint resumeを廃止し、external rerun convergenceをfailure contractにする。
4. `.agents/skills` はfixed slot marker方式で管理する。

次は影響する実装Issueを作成・開始する前に個別確定する。未回答を実装者が推測しない。

1. `.github/workflows/ci.yml` のownershipと更新方法。
2. legacy direct updateのversion / date window。
3. `--remove-specs` の完全廃止または独立purge commandへの移行方法。
4. `.gitignore` init seedのcollision / customization policy。
5. wheel / sdist / macOS smokeのtriggerとpublic deprecation window。

### R6. failureを成功扱いしない

- canonical required testはzero unexpected failuresかつzero approved active failuresでGREENになる。
- 26件のactive failure signatureを成功として受理するledgerは、各nodeを「修正」「現行契約外として削除」「有効なsuccessorへ置換」のいずれかで処理した後に撤去する。
- quarantineが一時的に必要な場合はowner、reason、expiry、successorを必須とし、merge-required GREENの定義には含めない。
- cutover後のrolling 20 canonical runsでflake retryなし・unexpected failureなしを確認する。

### R7. 実行量の可視化

- CI summaryはlaneごとのwall time、CPU time、node count、artifact build count、workspace copy bytes、duplicate node countをcandidate SHAに束縛して表示する。
- budget超過はtest failureとして扱い、timing weight更新やworker追加だけで回避できない。

## スコープ

対象:

- provider test portfolio全体のinventory、重複・cost・contract ownershipの確定
- `managed_distribution.py` が公開しているper-file reconciliation / journal / recovery契約を4 root replacementへ縮小
- fixed skill slot marker、tooling-only uninstall、有限one-shot migration
- unit、service contract、CLI smoke、package / platform smokeへの再配置
- Full Regression ledger、timing weights、4-shard runnerの段階的撤去
- Provider CI / Provider Full Regressionの実行graph、artifact reuse、budget gate
- obsolete test、duplicate test、historical-step testの安全な削除

対象外:

- Issue #372 candidateへの横入り修正
- test時間短縮だけを目的としたworker数の増加、CI machineの大型化、恒久的なtiming-weight tuning
- Product判断なしでfail-closed path protectionを弱めること
- user-owned spec historyの自動削除範囲を黙って拡大すること
- このEpicの調査段階で全実装Issueを開始すること

## 失敗・境界条件

- production contractを残したままtestだけを削ると、path substitution、partial update、drift、destructive deleteの退行を見逃す。契約縮小とtest削除は同じIssueまたは明示的な依存で結ぶ。
- 逆に、すべてのcurrent testを安全要件とみなすと、歴史的実装詳細が永久にproduct contractとなる。public behavior / invariantへ追跡できないtestは保持理由を満たさない。
- filesystem挙動にはLinux / macOS差がある。pure/domainを両OSで繰り返すのではなく、差が生じるsyscall境界を選んでplatform smokeを残す。
- cold dependency install、GitHub runnerのnoisy-neighbor、network downloadをtest bodyと混同しない。artifact buildとtest実行を別計測する。
- wall timeだけを満たしてprocess-hoursが増える変更は失敗とする。
- R5Bの未決事項はProduct判断であり、影響する下位Issueが推測で決めない。

## 受け入れ条件

- [x] 4 disposable roots、fixed skill slots、user history保護、external rerun convergenceをaccepted ADR `20260831t005139z-adr` に記録している。
- [ ] R5Bの残るProduct判断を、影響する実装Issueの開始前にaccepted decisionとして記録している。
- [ ] 全test familyのcontract / layer / lane / cost / keep-move-consolidate-delete判定が追跡できる。
- [ ] canonical local regressionを単一pytest processで連続5回実行し、各回600秒以内、zero failures、zero policy skipsである。
- [ ] 上記5回のchild-inclusive平均論理core使用数が各1.1以下であり、同時pytest worker数が1である。
- [ ] canonical PR test bodyのcritical pathが同一runner classの連続5 successful runsで各600秒以内である。
- [ ] 同一candidate・OSにおけるduplicate test node数が0で、wheel / sdistの各artifact build回数が1である。
- [ ] default pathでshard runnerを使用せず、test worker concurrencyが1である。
- [ ] fixed 2-vCPU Linux referenceで同じbudgetを満たし、seeded fault pack（user data誤書込み、allowlist外削除、symlink follow、root間failure、skill marker mismatch、artifact欠落）を100%検出する。
- [ ] cutover後のrolling 20 canonical runsでflake 0、retry 0である。
- [ ] platform固有smokeがLinuxとmacOSでGREENになり、各OSのtest bodyが600秒以内である。
- [ ] active approved failureが0になり、`full-regression-ledger.json`、timing weights、baseline evaluator、4-shard verifierを削除またはmerge判定外の一時migration toolingへ退役させている。
- [ ] obsolete / duplicate testsの削除前後で、残すdurable invariantsのtraceabilityとnegative-path proofが維持されている。
- [ ] budget summaryがcandidate SHA、wall / CPU time、node / subprocess / workspace / duplicate countsを報告する。

## 制約・前提

- 現時点の計測はlatest concurrent branch `iss-00372-distribution-hard-cutover-and-parity` の `7af12c54...`、実装candidate `bc156009...`、GitHub candidate `53f309a4...` を区別して記録する。
- user-reported「約4時間」「CPUほぼ100%」は重要な問題入力だが、同一SHA・同一machineで今回再測定した数値ではない。
- 10分budgetはtest bodyの目標であり、初回dependency downloadなど外部network時間は別表示する。ただしartifactをlaneごとに再buildする時間は重複costとして対象に含める。
- destructive operationは既定でfail closedとし、path ownershipを証明できない対象を削除しない。
- 既存のhuman PR merge gateを維持する。
- accepted ADR `20260831t005139z-adr` の範囲は確定済みとし、R5Bの未決事項だけを実装上の既成事実にしない。

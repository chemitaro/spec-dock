---
種別: 計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md", "artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md"]
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 計画

詳細: [Scope Layering Guide](../../../../docs/authoring/scope-layering.md)

## 目標

現行2,708 testsを4 shardへ分配する運用を最終形とせず、distribution product contractとtest portfolioを同時に縮小する。完了時には、provider-owned contentを4 disposable rootsと2 fixed skill slotsで管理し、merge-required regressionを単一pytest processで10分以内に実行し、active approved failures、duplicate nodes、timing-weight schedulerを持たない。

本Planはaccepted ADR `20260831t005139z-adr` を実装境界のauthorityとする。子Issueはまだ作成・開始しない。各候補の開始前に残るProduct判断とcurrent evidenceを固定し、Issue作成時に改めてacceptanceを受理する。

## Issue granularity assessment

- **Result**: `PROPOSED_ISSUE_CANDIDATES`
- **Decision basis**:
  - 4 provider rootsのlifecycle、shared skill slots、tooling-only uninstall / public compatibility、test / CI cutoverは、それぞれ異なるobservable outcomeとfailure boundaryを持つ。
  - pure / filesystem / CLI / testsのようなtechnical layerでは分けない。各candidateは関係するproduction behavior、docs、tests、migrationをend-to-endで所有する。
  - candidate 4はproduction contract cutoverなしでは受け入れられないため、1〜3に依存する。
  - workflow ownership、legacy window、purge CLI migrationなどの未決事項は各candidateの詳細を変えるが、4つのobservable boundary自体は維持できる。
- **Assumptions / unresolved evidence**:
  - `.github/workflows/ci.yml` がconsumer-ownedかreusable workflow projectionかは未決。
  - legacy no-marker workspaceのsupport windowは未決。
  - `--remove-specs` のdeprecation / replacement shapeは未決。
  - candidateは提案であり、Issueとしてaccepted / created / startedではない。

## Parent acceptance coverage

| Epic acceptance | owner proposal |
|---|---|
| 4 disposable roots、root boundary safety、rerun convergence | candidate 1 |
| 2 fixed skill slots、owner marker、unrelated skill preserve | candidate 2 |
| tooling-only uninstall、user data byte-identical、purge separation、CLI移行 | candidate 3 |
| contract inventory、test replacement、single-process 10分、CPU 1.1、duplicate 0 | candidate 4 |
| 26 active failures、ledger / sharder / timing weights撤去 | candidate 4 |
| package build once、Linux / macOS delta evidence | candidate 4（trigger decisionはcandidate 3で確定） |
| workflow ownership / legacy / purge / `.gitignore` policy | affected candidate開始前のProduct gate |

## Dependency direction

```text
accepted ADR 20260831t005139z
  └─> Candidate 1: Disposable provider root lifecycle
        └─> Candidate 2: Fixed skill slot lifecycle
              └─> Candidate 3: Tooling-only uninstall and compatibility cutover
                    └─> Candidate 4: Test portfolio and CI budget cutover
```

Candidate 2はshared slot contractだけなら1と並行設計できるが、installation recordとupdate orchestrationのwriter競合を避けるため実装は1のstable service interface後に行う。Candidate 4は1〜3の旧test削除receiptを集約する最終cutoverであり、production contract未変更のまま先行しない。

## Candidate 1 proposal — Disposable provider root lifecycle

### Observable outcome

fresh / recognized workspaceのinit・updateが、`spec-dock/{docs,templates,system,scripts}` をcandidateと完全一致するrootへ置換し、obsolete inner fileを残さず、Initiatives / Artifacts / `.workbench` / unknown pathsを変更しない。

### Acceptance trace

- fixed allowlist以外をactionへ含めない。
- candidate 4 rootsを全てstage・validateするまでtarget mutationを開始しない。
- `docs` → `templates` → `system` → `scripts` の順でreplaceし、ready markerを最後に書く。
- root / parent symlink、rebind、unexpected typeでwrite前にblockする。
- root間fault後、external installerから同じversionを再実行するとcandidateへ収束する。
- provider root内のlocal editとobsolete fileは保存しないことをdocs / CLI diagnosticへ明記する。
- markerなしcurrent workspaceのfinite one-shot migrationとsunset evidenceを持つ。
- old per-file update route、journal / checkpoint / historical identity codeと対応testsを同じcandidateで削除する。

### Relevant boundaries

- installer / update CLI adapter
- root replacement application service
- filesystem safety adapter
- candidate assets / installation record
- migration docs and service contract tests

### Declared dependency / stable contract

- accepted ADRのfixed roots、user-data exclusion、external rerun contract。
- 開始前にlegacy support windowと `.gitignore` seed policyをProduct判断で確定する。

### Verification boundary

- minimal synthetic workspaceでfresh、current update、obsolete inner file、root間fault、symlink / rebind、user data byte identityを証明する。
- built wheelから一つのrepresentative update smokeを通す。
- removed old production symbols / manifest sections / test familiesのabsenceを確認する。

### Rollout / recovery

- old / new routeをruntime toggleで長期並置しない。
- destructive regression時はapplyを停止してread-only diagnosticへ戻す。old mutation engineへautomatic fallbackしない。

## Candidate 2 proposal — Fixed skill slot lifecycle

### Observable outcome

SpecDockの2 managed skillsをslot root単位で追加・更新・削除でき、`.agents/skills` 内のunrelated skillsを一切変更しない。

### Acceptance trace

- current slotをexactly `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` に固定する。
- owner / slot / schema version markerをprovider sourceへ同梱する。
- absent slotはinstallし、valid owned slotはcomplete rootへreplaceする。
- missing / invalid / foreign markerはpreserve-and-blockする。
- retired slotはfinite exact allowlist + valid old markerでのみ削除する。
- current markerless 2 slotsのone-shot migration後、per-file historical skill identitiesとtestsを削除する。
- provider sourceとdogfooding projectionがcomplete tree単位で一致する。

### Relevant boundaries

- `src/spec_dock/assets/install_root/.agents/skills/`
- shared-root ownership validation
- update / uninstall orchestration
- dogfooding projection and skill docs

### Declared dependency / stable contract

- Candidate 1のinstallation record / staging interface。
- exact slot namesはaccepted ADRで固定済み。

### Verification boundary

- install、owned update、inner obsolete removal、foreign collision、unrelated preserve、retired removalを一つのsmall workspace matrixで証明する。
- `.agents/skills` parent全体をdelete / replaceするactionがないことをnegative proofにする。

### Rollout / recovery

- markerless migration adapterにはversion/date sunsetを持たせる。
- ownershipを証明できないslotは自動repairせず、人間向けdiagnosticで停止する。

## Candidate 3 proposal — Tooling-only uninstall and compatibility cutover

### Observable outcome

通常uninstallがprovider toolingだけを削除し、Initiatives / Artifactsとshared contentをbyte-identicalに保つ。spec-history purgeとpublic CLI / JSON compatibilityの扱いが明示される。

### Acceptance trace

- 4 provider roots、valid owned skill slots、installation recordだけをdelete setにする。
- `spec-dock/initiatives/**`、Artifacts、`.workbench`、generated projections、unknown paths、unrelated skillsを変更しない。
- unexpected root binding / marker mismatchで該当delete前にblockする。
- `--remove-specs` を通常uninstall authorityから外し、完全廃止または独立purgeへ移行する。
- `.github/workflows/ci.yml` をinit-once consumer-ownedまたはreusable workflowへ確定し、normal updaterのshared-file reconciliationを残さない。
- existing text / JSON / exit behaviorのdeprecationまたはbreaking changeをdocsとtestsへ反映する。
- old deprovision / purge / cross-intent recovery routeとtestsを同じcandidateで削除する。

### Relevant boundaries

- uninstall CLI / application service
- fixed root / slot filesystem adapter
- public JSON and migration docs
- retained workflow / install seed ownership

### Declared dependency / stable contract

- Candidate 1のfixed provider roots。
- Candidate 2のvalid skill owner marker。
- 開始前にpurge CLI、workflow ownership、public compatibility windowをProduct判断で確定する。

### Verification boundary

- before / after tree digestでdurable user dataとunrelated skillのbyte identityを証明する。
- uninstall dry-run / applyのrepresentative text・JSON・exit mappingを証明する。
- purge権限がupdate / retry / uninstallから到達不能であることを証明する。

### Rollout / recovery

- destructive purgeをcompatibility aliasとしてsilent実行しない。
- deprecationを採る場合はsunset date / versionとremoval receiptを持つ。

## Candidate 4 proposal — Test portfolio and CI budget cutover

### Observable outcome

merge-required regressionが単一pytest process・worker 1で連続5回各600秒以内、child-inclusive平均論理core1.1以下、zero failures / skips / duplicate nodesで完了し、旧Full Regression machineryがない。

### Acceptance trace

- all collected nodesをcurrent contract、owner layer、lane、cost、keep / move / consolidate / deleteへ100%分類する。
- Candidate 1〜3でretiredしたcontractの旧testsをreplacement receiptとともに削除する。
- 26 active failure nodesをfix / accepted retirement / exactly-once successorへ処理し、active countを0にする。
- same candidate / OSでduplicate nodeを0にする。
- wheel / sdistをaccepted triggerごとに一度buildし、同じartifact bytesをsmokeで使う。
- macOSはOS差のあるboundaryだけを実行する。
- `full-regression-ledger.json`、timing weights、baseline evaluator、policy skip flags、4-shard verifier、関連meta-testsを削除する。
- CI summaryへcandidate SHA、wall / CPU、node、subprocess、workspace / copy、duplicate、build countを出す。

### Relevant boundaries

- tests / fixtures / markers
- Provider CI / Full Regression workflows
- artifact builder and thin budget report
- active failure ledger / timing machinery

### Declared dependency / stable contract

- Candidates 1〜3のproduction cutoverとold-test deletion receipt。
- artifact / platform triggerはCandidate 3でacceptedにする。

### Verification boundary

1. fixed 2-vCPU / 8 GiB / networkなしのreferenceでcanonical commandを5回実行する。
2. 各runのwallが600秒以内、`(user + system CPU) / wall <= 1.1`、worker数1を確認する。
3. Linux / macOSのexecuted node集合とartifact digestを比較し、duplicate 0 / build 1を確認する。
4. seeded fault packでuser data誤書込み、allowlist外削除、symlink follow、root間failure、skill marker mismatch、artifact欠落を100%検出する。
5. rolling 20 canonical CI runsでflake retry 0 / unexpected failure 0を確認する。

### Rollout / recovery

- selector omissionが見つかった場合はmergeを停止し、全correctness portfolioを単一processで実行するfail-closed commandへ戻す。
- shard / worker追加、approved failure追加、post-mergeへの先送りをtemporary recoveryに使わない。

## Sequence and decision gates

### Gate A — Candidate 1 start

- legacy direct-update support window
- `.gitignore` init seed / collision policy
- current markerless workspace migration evidence

### Gate B — Candidate 3 start

- `--remove-specs` のremove / deprecate / independent purge decision
- `.github/workflows/ci.yml` ownership
- CLI / JSON compatibility window

### Gate C — Candidate 4 start

- Candidates 1〜3のaccepted implementation evidence
- wheel / sdist / macOS trigger
- current 2,708-node inventoryと26 active failuresのexact candidate snapshot

未回答を下位Issueへ委譲しない。Gate回答によりcandidate boundaryがmaterialに変わる場合は、Issue作成前にgranularityを再評価する。

## Epic verification

1. canonical regressionをworker 1で連続5回実行する。
2. child-inclusive wall / user / system CPU、subprocess、temp workspace、copied bytesを記録する。
3. local / Linux / macOS laneのexecuted node集合を比較し、same OS duplicate 0を確認する。
4. artifact receiptのsource SHA / digest / build countを確認する。
5. fresh / current / accepted legacy、root-inner drift、symlink、parent rebind、permission failure、root間stopをnew owner layerで検証する。
6. init、update、tooling-only uninstallとskill lifecycleをLinux built artifactで通す。
7. user dataとunrelated skillsがbyte-identicalであることを確認する。
8. plain zero-failure / zero policy skipを確認する。
9. SpecDock validation、lint、typecheck、provider / dogfood parityを確認する。

performanceは最良値ではなく5回すべてを記録する。wall 600秒超、平均論理core1.1超、worker追加依存、duplicate node、active approved failureのいずれかがあればEpic acceptance未達とする。

## Exit / handoff

Epic完了条件:

- Requirementの全受け入れ条件を同一final candidateのevidenceで満たす。
- 4 disposable rootsとfixed skill slots以外へprovider delete authorityを持たない。
- canonical regressionがsingle process / 10分以内 / zero failure / zero policy skipである。
- duplicate nodes、approved failure ledger、4-shard runner、timing weightsが残っていない。
- distribution contractとtest ownershipをcode / test name / CI commandから理解できる。
- human merge gateへmerge-ready PRを渡し、agentはmergeを実行しない。

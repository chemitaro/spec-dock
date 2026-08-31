---
種別: research
ID: "20260830t234548z-research"
タイトル: "Provider Test Suite Root-Cause Analysis and Redesign"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-31"
親: ["epic-00384"]
template: "research"
authority: "evidence"
derived_from: ["iss-00372@7af12c54bb73de63fdca6ea94853138a17e275a0", "github-run-33327601995", "github-run-33327608584"]
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
---

# 20260830t234548z-research Provider Test Suite Root-Cause Analysis and Redesign

SpecDock provider test systemの現物、同一candidateに対するGitHub Actions実行、最新並行worktreeのpre-freeze evidenceを調査した記録である。設計選択肢と推奨判断は、別Artifact `20260830t235429z-disc-provider-test-strategy-simplification-decision-analysis.md` で統合する。

## Question

- 逐次実行が約4時間、shard実行がCPUを長時間使い切るという問題は、どのtest family・execution graph・production contractから生じているか。
- Issue #372の4-shard Full Regressionは、実行量を減らしているか、それともwall timeへ圧縮しているだけか。
- install / update / uninstall / spec-history purge testsは、現行の利用者価値とsecurity invariantに対して必要十分か。
- 不要・重複testを削除しても失わないdurable invariantは何か。
- 10分以内を「worker追加」なしで満たすには、どのproduct boundaryとtest boundaryを変える必要があるか。

## Source

確認日: 2026-08-31 JST。

### S1. latest concurrent worktree

- path: `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/01ae/spec-dock`
- branch: `iss-00372-distribution-hard-cutover-and-parity`
- HEAD / upstream: `7af12c54bb73de63fdca6ea94853138a17e275a0`
- 調査時のworking tree: clean
- last commitはIssue #372のpre-freeze acceptance evidence追記。測定対象の実装candidateは親の `bc1560096593c645ec0309a37a080c53a7e7f35d`。
- 読んだ主なsource:
  - `tests/conftest.py`
  - `.github/workflows/provider-ci.yml`
  - `.github/workflows/provider-full-regression.yml`
  - `scripts/quality/verify_full_regression.py`
  - `scripts/quality/full_regression_baseline.py`
  - `full-regression-ledger.json`
  - `full-regression-timing-weights.json`
  - `src/spec_dock/managed_distribution.py`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/managed_distribution.json`
  - `tests/unit/infra/test_managed_distribution.py`
  - `tests/unit/infra/test_init_update.py`
  - `tests/cli_runtime/test_distribution_cutover.py`
  - `tests/integration/test_epic_00343_distribution.py`
  - Issue #372 `requirement.md`, `design.md`, `plan.md`, `report.md`

`01ae` worktreeはread-onlyで調査し、test実行、edit、Git writeを行っていない。

### S2. Provider CI run

- URL: https://github.com/chemitaro/spec-dock/actions/runs/33327601995
- event: `pull_request`
- head SHA: `53f309a487484cbc6af1dd5a562ca2a3f31f2bbd`
- result: success
- jobs:
  - `provider-tests` job `99300402043`
  - Ubuntu parity job `99300402140`
  - macOS parity job `99300402164`
- GitHub APIから各job logを取得し、pytest summaryとtimestamped progressを照合した。

### S3. Provider Full Regression run

- URL: https://github.com/chemitaro/spec-dock/actions/runs/33327608584
- event: `workflow_dispatch`
- head SHA: `53f309a487484cbc6af1dd5a562ca2a3f31f2bbd`
- result: success
- uploaded `provider-full-regression-evidence`の `result.json`、`collection.log`、4 shardのJSON / logを取得した。
- S2とS3はexact same SHAであり、testの重複をcandidate差として説明できない。

### S4. latest local pre-freeze evidence

- Issue #372 report Step 10B。
- candidate: `bc1560096593c645ec0309a37a080c53a7e7f35d`
- result path recorded by Issue: `spec-dock/.workbench/full-regression/20260830T231104.876692Z/result.json`
- 2,708 collected、4 shards、`status=verified`、`active_verified=26`、`resolved_verified=1`、`total_elapsed_seconds=1630.669`。

### S5. historical timing evidence

- `full-regression-timing-weights.json` observed SHA `fc02e1215d2b9e056a2c18bd1411fe489efdf2f2`。
- 266 weighted nodes、observed seconds合計1,461.748、default 2.0 seconds。
- 以前のIssue #370 JUnit evidenceは2,507 tests、4 shards、wall約625秒、testcase duration合計約2,224秒。latest 2,708-test candidateの測定ではないため、per-test hotspotの方向確認だけに使った。

### S6. user observation

- 逐次実行は約4時間。
- 現在の並列実行では約10分間CPUをほぼ100%使う。

この観測は問題設定として採用したが、今回同一machine / SHAでCPU telemetryを再取得していない。wall、pytest process elapsed、CPU timeを混同しない。

### 調査方法

- Git / GitHub stateをread-only commandで確認。
- workflowとpytest plugin / runnerのcontrol flowをsourceから追跡。
- GitHub logのtimestampとsummaryからfile / job durationを算出。
- uploaded result / shard logsからcollection、shard wall、node outcomeを確認。
- `wc`、`rg`、Python ASTのread-only集計でLOC、class / function、subprocess / temp workspaceの静的規模を確認。
- test names、parametrize、fixture、helperを読み、同じinvariantがどのboundaryで反復されるかを分類。

## Findings

### F1. Full Regressionは実行量を減らしていない

GitHub Full Regressionの実測:

| metric | value |
|---|---:|
| collected | 2,708 tests |
| collection | 7.911 s |
| shard phase wall | 5,959.407 s（99分19秒） |
| shard 1 | 4,964.26 s |
| shard 2 | 5,958.94 s |
| shard 3 | 4,719.11 s |
| shard 4 | 4,208.80 s |
| shard-process elapsed合計 | 19,851.11 s（5.51時間） |
| active approved failures | 26 |
| resolved successor | 1 |

`verify_full_regression.py`は最初に `pytest --run-full-regression --collect-only -q` で全nodeを集め、timing weightで分割し、4つのpytest processへ全node IDを配る。`--run-full-regression`はheavy-only selectorではない。したがって4 shardは5.51 process-hoursを約99分へ圧縮しただけである。

collectionはwallの0.14%未満であり、test discovery最適化は主要解ではない。fast nodeを含む全nodeを明示的に再実行する設計が主要costである。

local Step 10Bでも同じ性質がある。

| shard | elapsed |
|---|---:|
| 1 | 1,328.62 s |
| 2 | 1,629.14 s |
| 3 | 1,212.36 s |
| 4 | 1,089.04 s |
| 合計 | 5,259.16 s（87分39秒） |
| overall | 1,630.669 s（27分10秒） |

平均約3.2 shard-processesが同時に稼働し、fastest / slowestの差は約9分ある。workerをさらに増やせばwallを短くできる可能性はあるが、CPU圧迫とprocess costを増やす方向であり、問題の定義に反する。

### F2. exact same candidateをlane間で重複実行している

S2 / S3はどちらもSHA `53f309a4...` である。

| test family | PR Ubuntu ordinary | PR Ubuntu parity | PR macOS parity | Full Regression Ubuntu | 実行回数 |
|---|:---:|:---:|:---:|:---:|---:|
| fast nodes一般 | 実行 | 一部 | 一部 | 実行 | 最低2 |
| `test_managed_distribution.py` 575 cases | 実行 | 実行 | 実行 | 実行 | 4 |
| `test_distribution_cutover.py` 158 cases | skip | 実行 | 実行 | 実行 | 3 |
| `test_epic_00343_distribution.py` 16 cases | skip | 実行 | 実行 | 実行 | 3 |

platform差を証明する必要があるtestは複数OSで実行してよい。しかしpure ruleやUbuntuで同じnodeをordinary / parity / fullの三回実行する根拠はない。現行workflowには「一つの契約をどのlaneが所有するか」という排他的責務がない。

### F3. merge前gateだけでも10分ではない

Provider PR fast gateのexact summaryは `1567 passed, 1141 skipped in 650.55s (0:10:50)` である。dependency install / lintとは別のtest bodyだけで目標を50秒超える。

timestamped progressによるapproximate file spans:

| file | cases observed | elapsed span | fast body比 |
|---|---:|---:|---:|
| `tests/unit/cli/test_cli_smoke.py` | 2 | 約63 s | 約9.7% |
| `tests/unit/infra/test_active_store.py` | 6 | 約66 s | 約10.1% |
| `tests/unit/infra/test_init_update.py` required-fast subset | 3 executed | 約60 s | 約9.2% |
| `tests/unit/infra/test_managed_distribution.py` | 575 | 約447 s | 約68.7% |

4 file spansで約636 / 651秒、約97.7%を占める。log timestampはper-test CPU durationではなくfile progressのwall spanだが、通常gateのbottleneckが広く分散していないことは確認できる。

同じ `test_managed_distribution.py` はfocused parityでUbuntu 70.47秒、macOS 55.19秒だった。通常suite内の約447秒との差は約6倍であり、filesystem / process系testがrunner variance、order、resource状態の影響を強く受けることを示す。これを「575 pure unit tests」としてfast laneへ置く分類は実態に合わない。

### F4. parity gateは少数testでも非常に重い

| OS | managed distribution | cutover | package parity | test body合計 |
|---|---:|---:|---:|---:|
| Ubuntu | 70.47 s | 3,191.19 s | 1,339.54 s | 4,601.20 s（76分41秒） |
| macOS | 55.19 s | 2,378.45 s | 965.17 s | 3,398.81 s（56分39秒） |

16 package casesが16〜22分を使う。test moduleはwheel / sdist、venv、pip install、consumer作成、exact candidate checkout / dogfood clone、update / importを一つのmatrixへ含む。これは「test数が少なければ速い」が成立しない例である。

同一SHAについて、recorded PR test processesとFull Regression shard processesのelapsed合計は約7.9時間になる。これは複数machineのwallを足したresource indicatorであり、CPU-hoursそのものではないが、10分の表示だけでは見えない総実行量を示す。

### F5. lane classificationがcost / contractを表していない

`tests/conftest.py` の `HEAVY_NODE_PREFIXES` は次をheavyへする。

- `tests/cli_runtime/`
- `tests/integration/`
- `tests/manual_tests/`
- `tests/unit/infra/test_init_update.py::`

そこから5つの `REQUIRED_FAST_NODE_IDS` を例外にし、それ以外のunmarked nodeをすべてfastへする。結果として:

- filesystem state machineの575 casesは`tests/unit/infra/test_managed_distribution.py`というpathなのでfast。
- in-process pure logicでも`tests/cli_runtime/`に置かれればheavy。
- markerはcontract ownerではなく実行抑制policyになる。
- ordinary `pytest -m full_regression`だけではbodyを実行できず、`--run-full-regression`という別permissionが必要になる。

このpolicyは移行時の安全策としては理解できるが、最終test architectureにはできない。

### F6. test suiteはproductionより大きく、distributionへ集中している

latest branchの静的規模:

| target | size |
|---|---:|
| production Python | 90 files / 約51,161 LOC |
| test Python | 86 files / 約97,395 LOC |
| test / production LOC ratio | 約1.90 |
| test definitions | 1,848 |
| collected cases | 2,708 |
| `TemporaryDirectory` occurrences | 768 |
| static subprocess-call occurrences | 78 |

distribution hotspot:

| file | LOC | shape |
|---|---:|---|
| `src/spec_dock/managed_distribution.py` | 22,332 | 41 classes、330 top-level functions、454 functions / methods |
| `tests/unit/infra/test_managed_distribution.py` | 19,572 | 346 definitions、575 cases |
| `tests/unit/infra/test_init_update.py` | 10,348 | 152 definitions、201 cases |
| `tests/cli_runtime/test_distribution_cutover.py` | 3,478 | 116 definitions、158 cases |
| `tests/integration/test_epic_00343_distribution.py` | 1,734 | 16 cases |

`managed_distribution.py`単体がproduction Pythonのおよそ44%である。テスト肥大化は単なるtest authoringの失敗ではなく、production behaviorのstate spaceをかなり忠実に反映している。

### F7. product contractが「simple tool」の範囲を超えている

`managed_distribution.py` と関連testsは少なくとも次をdurable behaviorとして扱う。

- per-path file / directory / symlink / hardlink identity
- parent chainとroot binding
- provider manifest / historical identity / version recognition
- generated projectionsとactive selectionの整合
- preservation witnessとclosed-set directory evidence
- mutation plan digest、journal、forward guard、retry marker
- crash checkpointごとのresume / cleanup
- create / upgrade / deprovision / explicit spec-history purgeのintent分離
- cross-intent recovery mismatch
- quarantine / rename-aside / predecessor reservation
- FIFO、malformed marker、same-bytes-new-inode、path rebind race
- historical Issue 368〜371のcompatibility / recovery behavior

unknown pathを削除しない、symlinkをfollowしない、drift時にfail closedといったinvariantは必要である。一方、arbitrary checkpointからautomatic recoveryすること、cross-intent journalを永続互換にすること、user history purgeまで同じengineが行うことは、product goalとして別の承認を要する。これらを残したままtestだけを大幅削減することは安全でない。

### F8. testはhistorical implementation stepsを単位に増えている

関連test namesは `s35`、`s40b`、`s45`、`s50`、`s55`、`s60`、`s65`、`s70`、`i368`、`i369`、`i370`、`i371` など、過去のIssue / implementation stepをprefixに持つ。同じ `fresh`、`update`、`uninstall`、`marker`、`retry`、`symlink`、`preserve` invariantがmanaged-distribution unit、installer、CLI cutover、package parityに現れる。

historical regressionを残すこと自体は正しい。しかしtest nameとownershipが「現在守る契約」へ正規化されず、issue完了ごとに新test familyが積み上がると、successorが古いtestを置換できず加算しか起きない。

### F9. fixture改善は局所的で、契約重複を解消しない

CLI-runtime harnessはすでにsession-scoped fresh-init templateとcopy-on-write cloneを導入している。これは繰返しinit costを減らす正しい局所最適化である。それでもsuiteは重い。理由は:

- 各commandがfresh Python processを起動する。
- temp Git repositories、fake `gh`、workspace copyを多く作る。
- 44 MB / 約2,320 filesのdogfood surfaceを扱うintegration pathがある。
- 一つのcontractを複数boundaryで再証明する。
- production state数が多いためfault matrixが大きい。

fixture sharingだけでは、実行するbehaviorの数とboundary crossingの数は減らない。

### F10. approved failure infrastructureは移行負債である

latest Full Regressionは各shardがexit 1でも、exact 26 active failure signaturesをshared evaluatorが承認してrunnerを`verified`にする。schema-v2のactive / resolved / retiredとsuccessor proofは、失敗を隠さず移行状態を記録する点で改善である。

しかしsteady stateとしては:

- failureをGREENへ変換する約974 LOCのquality code
- `full-regression-ledger.json`
- `full-regression-timing-weights.json`
- baseline / lane tests
- 4-shard observation / merge runner

を維持する。26件は主に旧CLI active / import / sync / workbench contractであり、各nodeをfix / obsolete delete / successor replaceへ進めなければ、test suiteとmeta-test suiteが同時に増え続ける。

### F11. 根本原因の優先順位

1. **production state space**: distribution engineがsimple toolの大部分を占め、組合せtestを必要にしている。
2. **contract ownershipの欠如**: 同じinvariantをunit、CLI、package、platform、fullで繰返す。
3. **execution graphの重複**: fast、focused parity、fullがexact same SHA / nodeを重複実行する。
4. **expensive boundary mechanics**: Python process、Git、venv、pip、build、large copyを多数起動する。
5. **historical additive tests**: durable contractへconsolidateせずIssue / Stepごとにtestが残る。
6. **approved failure migrationの恒久化**: failing testsとその管理testが両方残る。
7. **parallelism-first optimization**: 上記costを減らさず、CPU / process costとwall timeのtrade-offを隠す。

### F12. 現時点で確認していないこと

- 同一latest SHAを単一processで実行した新しいwall / CPU telemetry。重い実行を重複させず、既存canonical evidenceを優先した。
- 2,708 nodeすべての個別keep / delete判定。family-levelのroot analysisまでであり、node-level inventoryは計画上の条件付き候補1の成果とする。
- 26 active failuresの一件ごとの仕様妥当性。node listとoutcomeは確認したが、各contractのProduct decisionはしていない。
- 実利用で何世代前のworkspaceが存在するか、`--remove-specs`利用頻度、offline self-contained runtimeの必要性。telemetryがないためProduct owner判断へ戻す。
- process elapsedと実CPU secondsの一致。前者はrunner slot / work量のindicatorであり、後者の代替ではない。

## Reflection

- F1〜F12をEpic `requirement.md`、`design.md`、`plan.md`へ反映した。
- durable targetは「4 shardをより均等にする」ではなく、「全merge-required contractを単一processで10分以内にする」とした。
- test削除より先にdistribution product contractを縮小する必要があるため、spec-history purge、automatic recovery、compatibility window、repo-local runtime copyをProduct判断にした。
- zero approved failures、duplicate node zero、artifact build once、wall / CPU / subprocess / copy量のcandidate-bound evidenceを受け入れ条件にした。
- node-level deletion listはこの調査だけで断定せず、全nodeをcontractへmapする条件付き候補1へ渡した。
- 選択肢、推奨案、却下案、Issue分割はdisc Artifactへ分離した。

---
種別: ADR
ID: "20260831t152024z-adr"
タイトル: "Single Implementation Unit and Provider Hard Cutover Policy"
状態: "accepted"
決定日: "2026-08-31"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "91667235c6892f025a1d9ee69cf37525537a3c9e"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

## Context

Epic #384はdistribution lifecycle、legacy migration、public CLI、test portfolio、artifact build、provider CIを同時に変更する。旧案ではdecision、test restructuring、implementation、verificationを複数Issueへ横分割し、uninstall-first bridgeやintermediate generationを挟む可能性があった。

しかし、この分割は次の問題を生む。

- Product判断がimplementation Issueへ持ち越される。
- old/new writerとrecord formatが並存し、cross-generation recoveryを増やす。
- tests-only / verification-only Issueが、実装を受け入れられない独立unitになる。
- bridge generationをmainへmergeするたび、consumer migration matrixとdowngrade riskが増える。
- provider CIがold contractとnew contractを重複実行し、failure approvalを温存する。

Current exact revision `91667235c6892f025a1d9ee69cf37525537a3c9e`では、legacy per-file engine、purge、journal、failure ledger、timing sharderが実在する。Issue #387は別のCurrent-surface cleanupであり、これらを変更しない。

## Decision

### ADR-D1 — One implementation-and-verification Issue

Epic #384の唯一のimplementation-and-verification Issueを#392とする。investigation、Product decision、tests、CI transition、final verificationを別Issueへ分割しない。internal step、commit、複数PRは許可するが、全て#392の内部実行単位とする。

### ADR-D2 — Combined hard cutover

Final public generationへ一度に切り替える。次を採用しない。

- uninstall-first bridge
- intermediate package generation
- runtime toggle
- old/new dual writer
- automatic old engine fallback

Dormant successor codeを先にmergeしてもよいが、public routeはoldまたはfinalのどちらかであり、中間Product contractを公開しない。Public route cutoverを開始するPR-Bでは、I392-S40とI392-S50を同一branch/PR内のnon-main checkpointとし、いずれのcommitもmainへmergeしない。I392-S40、I392-S50、I392-S60の全proofが完了した後だけPR-Bをhuman mergeでき、mainはold public productからcomplete final lifecycleへ一度だけ遷移する。

### ADR-D3 — Fixed lifecycle contract

Persistent mutation authorityは4 roots、2 slots、`spec-dock/spec-dock.version`に限定する。fresh `init`だけ2 consumer seedをabsent時に作成できる。uninstall後はrecordを`tooling-absent-preserved-data`として保持する。purgeを削除し、`--remove-specs`をmutation-zero compatibility trapとする。

### ADR-D4 — Exact legacy boundary

exact clean `0.2.3`だけをsingle-version digest fixtureで認識する。active recovery、unsupported legacy、modified/foreign markerless slotは推測変換しない。final versionは`0.2.4`とし、legacy plain-text recordをstrict JSON recordへ置換する。

### ADR-D5 — Build-once provider gate

Wheelとsdistをone packaging invocationでbuildし、Linux canonicalとmacOS deltaへ同じwheelを配布する。Linux canonicalはsingle pytest process、worker 1。main-push 4-shard Full Regression、failure ledger、timing weights、sharder、policy skipをfinal stateから除去する。human PR merge gateは維持する。

## Alternatives considered

### A. Decision/implementation/test/verificationを別Issueへ分割する

**Rejected.** 各Issueが単独でend-to-end acceptanceを持たず、未決Product判断とcross-Issue dependencyを増やす。#388〜#390はこの構造を持つためsuperseded historical nodeとして維持し、reopenしない。

### B. Uninstall-first bridge generationを先にreleaseする

**Rejected.** consumerへ一時的なmigration順序を強制し、bridgeからfinalへの追加migrationとsupport期間を作る。tooling uninstallはfinal package自身がexact legacy stateに対して直接提供する。

### C. Old/new runtime toggleを置く

**Rejected.** two writers、two records、two recovery semanticsを同一binaryに残し、hard cutoverの複雑性削減を失う。rollbackはhuman-reviewed Git revertであり、runtime toggleではない。

### D. Historical per-file engineを縮小して再利用する

**Rejected.** arbitrary historical catalog、per-action journal、purge authority、per-file identityがfixed-root Product contractと不整合である。single exact legacy adapterだけを新設する。

### E. Full Regressionをshardのまま高速化する

**Rejected.** duplicate execution、timing weights、approved failure、policy skipを構造的に残す。single-process budgetを満たすようtest portfolio自体を所有契約へ再編する。

### F. Uninstall時にrecordを削除する

**Rejected.** never-installed absentとtooling-uninstalled workspaceを区別できず、reinstallがfresh-only seedを再作成し得る。

## Consequences

### Positive

- mutation authorityがcode-fixed pathsへ限定される。
- recoveryはsame-operation / same-candidate rerunだけになる。
- old package downgradeはrecord parser boundaryでpre-mutation blockできる。
- user history purgeのdestructive surfaceが消える。
- test failureをledgerで成功扱いする仕組みが消える。
- one artifact / one owner laneのtraceが明確になる。
- Issue #392だけでacceptanceとclosureを判断できる。

### Negative / cost

- #392は大きなcross-cutting changeであり、critical planning、fault injection、built-artifact proofを要する。
- Linux/macOS native rename primitiveへ明示的に依存する。
- exact `0.2.3`以外のlegacy workspaceはmanual recoveryが必要になる。
- combined cutover後はold engineへautomatic rollbackできない。
- required-context transitionにはhuman repository admin操作が必要である。

### Risk controls

- #387 post-merge deterministic admission
- successor-first direct proof
- stage-before-mutate
- ready-last record
- root/slot boundary fault injection
- old-package startup composite tripwire
- same-wheel Linux/macOS binding
- intentional RED required-context canary
- human-only merge
- forward-fix / fail-closed policy

## Supersession

- GitHub #388〜#390は実装前にIssue boundaryとしてsupersededされたhistorical nodeである。
- それらのdecision contentは本ADR、Epic R/D/P、Issue #392 R/D/Pへ統合する。
- close状態はimplementation completedを意味しない。
- reopen、reassignment、new work acceptanceに使用しない。

## Consistency contract

本ADRのdecisionは次と一致しなければならない。

- Epic `requirement.md`: E384-RQ-001〜016
- Epic `design.md`: E384-D-001〜019
- Epic `plan.md`: E384-P-001〜007
- Issue #392 `requirement.md`: I392-RQ-001〜020
- Issue #392 `design.md`: I392-D-001〜018
- Issue #392 `plan.md`: I392-S00〜I392-S80

矛盾が生じた場合はimplementationを停止し、canonical R/D/Pを先に整合させる。implementation agentが別案を選択してはならない。

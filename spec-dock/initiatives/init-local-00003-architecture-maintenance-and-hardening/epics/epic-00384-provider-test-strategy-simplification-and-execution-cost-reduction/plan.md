---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "91667235c6892f025a1d9ee69cf37525537a3c9e"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

## 1. Governance

Epic #384はProduct判断、scope、acceptance、implementation unit boundaryを管理する。実装作業は唯一のchild Issue #392で行う。#388〜#390をreopenせず、research、decision、tests、CI、final verificationを別Issueへ分割しない。

### E384-P-001 — Single-Issue boundary

- Authorized implementation-and-verification unit: `iss-00392` / GitHub #392。
- Internal step、commit、PRは#392の実行単位であり、新しいIssueではない。
- #392が未達の間はEpicをopenのままにする。
- failureをledgerで承認してEpicをcloseしない。

### E384-P-002 — Dependency gate

#392 implementation startより前に#387のhuman mergeとdeterministic post-merge admissionを完了する。admissionがfailした場合は実装を開始せず、exact evidenceをrepository ownerへ返す。unclassified driftをimplementation agentの裁量で吸収しない。

## 2. Ordered execution

Epic-level orderは次のとおりである。詳細なpath/symbol/commandは#392 `plan.md`を正本とする。

1. **Admission and baseline**
   #387 merge SHA、allowed drift、current gates、baseline old artifactを固定する。
2. **Dormant successor proof**
   fixed model、candidate、filesystem、serviceをold public routeに接続せず追加し、direct testsで証明する。
3. **Combined public hard cutover**
   `0.2.4`へversion bumpし、CLI、record、legacy migration、uninstall compatibilityを同一generationで切り替える。
4. **Old contract terminalization**
   successor proof後にper-file engine、purge、journal、legacy catalog、duplicate old testsを削除する。
5. **Portfolio and gate cutover**
   active failuresをterminal化し、build-once Linux/macOS gateへ切り替え、old Full Regression machineryを削除する。
6. **Qualification and handoff**
   five-run、CPU ratio、fault pack、rolling 20、dogfood、fresh consumer、required context、exact PR treeを同一candidateへ束縛する。
7. **Human merge and closure**
   human merge後にmerged SHAとverified PR SHAを照合し、Issue finish、その後Epic closeを行う。

## 3. Multi-PR policy

複数PRを使用する場合の推奨境界は次のとおりである。

| PR | Permitted content | Merge-point invariant |
|---|---|---|
| PR-A | dormant successor modules、single-version legacy fixture、direct tests | public CLIはold behaviorのまま。new runtime toggleなし。ordinary/current full gatesがGREEN。 |
| PR-B | I392-S40〜S60を同一branch/PRで連続実行する。`0.2.4` public route cutover、CLI/service wiring、migration/downgrade proof、purge trap、old engine removal、active failure terminalization、test ownership、successor tests | S40/S50はnon-main checkpointでありmerge禁止。S60の全proof完了後だけhuman mergeできる。merge後のmainはcomplete final lifecycleで、old engine fallback、approved failure、policy skipを持たない。 |
| PR-C | I392-S70〜S80のbuild-once CI、old Full Regression removal、docs/dogfood、qualification、final evidence | final gateだけがrequired provider authority。main-push rebuild/shardなし。 |

PR-A〜Cは例であり、必須数ではない。ただしpublic cutoverをbridge generationへ分割してはならない。PR-Bを使用する場合、S40でpublic routeを切り替えたbranchをS50、S60まで同じPRで進め、S40後またはS50後のcommitをmainへmergeしてはならない。PR-Bの唯一のmain merge gateはS60完了後である。

## 4. Human gates

### E384-P-003 — Review gate

各PRはhuman reviewを必要とする。agentはmerge、required context変更、branch protection変更を行わない。

### E384-P-004 — CI transition gate

Required-context transitionはhuman repository adminが次の順で行う。

1. existing classic protection、ruleset、required context、review requirement、merge queueをread-only captureする。
2. new `Provider CI / provider-gate`を追加し、old required contextを保持したままGREENを確認する。
3. controlled canaryでnew gateをintentional REDにし、merge blockingを確認する。
4. new gateをGREENへ戻す。
5. new gateをrequiredへ追加する。
6. required setが有効であることを再取得する。
7. old provider-only contextだけをremoveする。unrelated contextとreview requirementは変更しない。
8. before/after JSONとoperatorを#392 reportへ記録する。

settingsを読めない、new contextが出現しない、REDがblockしない、unrelated setting差分がある場合は停止する。

## 5. Evidence contract

### E384-P-005 — Evidence identity

全evidenceは少なくとも次へ束縛する。

- repository
- full source SHA
- wheel filename / SHA-256
- sdist filename / SHA-256
- candidate digest
- OS / architecture / Python version
- exact command
- exit code
- wall time
- process-tree CPU time where applicable
- test node inventory digest
- generated timestamp

Evidence artifactはcanonical R/D/Pを上書きせず、#392 `report.md`に結果とdigestを記録する。一時logやbinary artifactをcanonical directoryへcommitしない。

### E384-P-006 — Acceptance evidence groups

- #387 post-merge admission
- fixed path / state / result contract
- candidate stage-before-mutate and atomic publication
- install/update/uninstall/reinstall matrix
- same-candidate convergence / cross-intent block
- exact `0.2.3` migration / active recovery block
- old-package composite tripwire / native controls
- public CLI and compatibility trap
- active failure terminalization
- duplicate ownership zero
- one build invocation / same wheel
- Linux canonical / macOS delta
- required-context transition
- five-run / CPU / fault / rolling-20
- dogfood / fresh consumer / exact PR tree

## 6. Stop and forward-fix policy

### E384-P-007 — Fail closed

次の場合、当該step以降を実行しない。

- #387 admission mismatch
- fixed path外のmutation authorityが必要
- old packageがtarget mutationをattempt
- atomic rename primitiveまたはno-follow bindingが利用不能
- candidate/source/stage digest mismatch
- active failureをfix/successor/retirementへterminal化できない
- duplicate contract ownerが残る
- build invocation countが1でない
- Linux/macOS wheel digestが異なる
- budget/fault/rolling acceptance未達
- required-context stateが読めない、またはhuman gateが弱まる

未達は同じ#392でforward-fixする。shard追加、approved failure、policy skip、old engine fallbackで回避しない。

## 7. Closure states

### Implementation completion

Final PR headでRequirementの全technical acceptanceとevidenceが揃った状態。まだmerge済みとは扱わない。

### PR merge readiness

New required gate、human review requirement、exact PR SHA、rollback informationが揃い、humanがmerge判断できる状態。

### Human PR merge

Humanだけが実行する外部状態変更。agentは完了を主張しない。

### Issue finish

Human merge後、merged SHAがverified PR SHAと一致し、#392 reportがcompleteで、SpecDock lifecycle上finish可能な状態。

### Epic close

#392がfinished/closedで、Epic acceptanceが全て満たされ、追加implementation Issueが存在しない状態。#388〜#390はhistorical supersededのまま保持する。

## 8. Epic completion criteria

- Epic Requirement / Design / Plan / ADRと#392 R/D/Pが同じdecisionを表す。
- #387 dependency admissionがreportに記録される。
- #392だけでimplementationとverificationが受入可能である。
- human merge後のexact treeがverified PR treeと一致する。
- remaining owner decisionがない。execution時にstop conditionが発火した場合だけrepository ownerへescalateする。

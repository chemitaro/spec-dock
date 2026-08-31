---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 計画

詳細: [Epic Plan Guide](../../../../docs/authoring/epic-plan.md)

## 目標

Epic #384を一つのimplementation-and-verification Issueで完了する。調査、Product decision、production cutover、test replacement、CI transition、最終検証を別Issueへ流出させない。

## Issue granularity assessment

`Result: ONE_ISSUE`

Decision basis:

- 本ProductでIssueは実装と検証を一体で受入する実装ユニットである。
- 調査・分析・意思決定だけのscopeはIssueとして成立しない。
- install / update / uninstallは現行同一engineへ接続され、自然なindependent release seamがない。
- C4〜C11の分割はtechnical phase、layer、coordination、verificationによる横スライスである。
- splitを成立させるP0〜P3、receipt chain、cross-Issue fixtureはProduct価値を持たない中間contractである。
- lifecycle simplification、old contract removal、portfolio / CI cutoverは一つのobservable outcomeと一つのacceptance boundaryを持つ。

## Child graph

```text
epic-00384
  └─ iss-00392 Provider Lifecycle And Regression Gate Hard Cutover
```

`iss-00392`だけがproduction、public CLI、tests、workflow、migration、old machinery removal、performance / stability verificationを所有する。

## Former Issue disposition

- `iss-00388`: legacy / `.gitignore` / `init --force`判断をaccepted ADRとEpicへ統合。future unitとしてsuperseded-before-implementation。
- `iss-00389`: uninstall / purge / CLI判断をaccepted ADRとEpicへ統合。future unitとしてsuperseded-before-implementation。
- `iss-00390`: workflow / artifact / platform判断をaccepted ADRとEpicへ統合。future unitとしてsuperseded-before-implementation。
- C4〜C11、`DEC-*`、`FIX-*`:作成しない。

3件は実装済み / 完了済みではなく、誤ったIssue境界としてcloseする。ローカルnodeのhistorical removalは、SpecDock destructive deleteの明示authorizationなしには行わない。

## Authoring-time investigation completed

調査を後続Issueへ送らず、`iss-00392`作成前に次を完了した。

| evidence | result |
|---|---|
| exact branch / SHA | `codex/epic-00384-provider-test-strategy-planning` / `d8f9d02f...` |
| current package / recognized workspace | exact `0.2.3` |
| full collection | 2,710 nodes |
| sorted node-set digest | `f607b007d167231ed27f2a17391b0d8b3aa452d67ce6532565463e193486a04c` |
| ordinary gate | 1,574 passed / 1,136 skipped / 57.02s |
| resource reference | wall 58.42 / user 24.41 / sys 31.29 / CPU ratio≈0.953 |
| ledger | 27 total / 26 active / 1 resolved |
| active cohort focused rerun | 26 failed / 14.69s |
| current CI | ordinary + Ubuntu parity + macOS parity + main 4-shard full |
| rulesets API | 0 rulesets |
| repository owner capability | `chemitaro` admin |
| classic protection / required set | current tokenで403、未観測 |

static / historical root-cause analysis、accepted ADR、same ChatGPT 5.6 Pro strict conversationのadvisoryをlocal evidenceへ照合した。Product policyとして未決事項は残さない。

## Product decisions completed now

1. combined hard cutover。uninstall-first bridge、中間generation、runtime toggleなし。
2. exact clean `0.2.3`だけをper-workspace one-shot migrate。
3. active legacy recoveryはlast-compatible `0.2.3`へ戻し、new formatへ推測変換しない。
4. old `0.2.3` packageのfinal workspace mutation-zeroをmerge acceptanceにする。
5. `.gitignore`とconsumer `ci.yml`はfresh-init-only consumer-owned seeds。
6. `init --force`はinstall / update aliasで追加authorityなし。
7. uninstallはtooling-only、`--apply`がconfirmation、`--keep-specs`はalias。
8. purge capabilityを廃止し、`--remove-specs`はnon-mutating exit 2 trap。
9. candidateごとにone invocationでwheel / sdistをbuild。
10. Linux canonical / macOS deltaへ排他的に割り当て、main Full Regressionを廃止。
11. required contextは既存名再利用を優先し、human review gateを維持。

## Internal milestones

milestoneはIssueではなく、`iss-00392`内のexecution orderである。

### M1. Successor contract freeze

- ownership classes、record / marker schema、typed result
- exact `0.2.3` recognizer
- consumer seed matrix
- CLI state-result table
- Linux / macOS lane ownership

### M2. Minimal lifecycle core

- no-follow binding、fixed action set
- candidate stage / validate
- incomplete / ready record
- uninstall後も残る`tooling-absent-preserved-data` recordとnever-installed `absent`の識別
- root / slot replacement、fixed tombstone
- same-candidate rerun、fault seams

### M3. Combined public cutover

- init / init-force / update / uninstall / reinstall
- keep alias / remove trap
- public docs / migration / recovery guidance

### M4. Legacy / downgrade proof

- exact `0.2.3` migration
- active / unsupported / modified legacy block
- old-package mutation-zero
- target-scoped startup audit-hook tripwire event 0と補助tree digest不変

### M5. Old product / test removal

- per-file engine、historical catalog、journal / checkpoint
- cross-intent recovery、purge、obsolete exact files
- corresponding historical tests / docs

successor proof成立後だけ削除する。

### M6. Failure cohort / portfolio consolidation

- 26 active nodesをfix / successor / retirementへterminal化
- pure/domain、filesystem/service、CLI、artifact、macOS deltaへ再配置
- approved failure / policy skip / duplicateを0へ

### M7. Build-once provider gate

- wheel / sdist build invocation 1
- Linux single-process canonical
- macOS delta same-wheel consumer
- digest / candidate mismatch failure、metrics、duplicate detector
- required context observation / transition

### M8. Old CI removal

- duplicate parity
- `provider-full-regression.yml`
- 4-shard verifier、timing weights、ledger evaluator、policy hooks

new gateのGREEN / intentional RED block確認後だけ撤去する。

### M9. Final acceptance / human merge

- same final treeの5 reference runs
- seeded fault pack
- rolling 20
- Linux / macOS artifact smoke
- old package mutation-zero
- durable uninstall discriminatorとfresh-init-only seed非再作成
- required set final state
- human merge、merged tree equality

## Merge-point safety

一つのIssueを使うことは、最後までmainへ統合できない巨大PRを意味しない。必要に応じて複数PRを使うが、次を守る。

1. successor tests / internal modelをadditiveに導入するPRはexisting public behaviorを維持する。
2. public hard cutover PRはsuccessor implementation / tests / docsとold contract removalを同時に成立させる。
3. CI PRはold required contextを失わずnew gateを証明し、必要なexternal transition後にold machineryを撤去する。
4. 各PR merge直後にaccepted public commandsとrequired gateをGREENに保つ。
5. Issueは全milestone / acceptanceが完了するまでcloseしない。

## Dynamic facts, not deferred decisions

次はProduct判断ではなく、実装対象または外部状態が存在してからしか取得できないevidenceである。同じ`iss-00392`内で取得し、未達なら同Issueを修正する。

- final node set / wheel / sdist digests
- old `0.2.3` package mutation-zero
- seeded fault後rerun convergence
- final 5-run wall / CPU
- duplicate 0 / policy skip 0
- macOS delta result
- rolling 20
- effective required contexts / classic protection / merge queue
- final required-context canary
- merged tree / verified PR tree equality

これらのために調査Issueや検証Issueを作らない。

## Epic verification

- Epic / Issue Requirement / Design / Planのcross-referenceとaccepted ADR反映
- `./spec-dock/scripts/spec-dock sync --no-github --no-update-active`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock deps check --id iss-00392 --github --json`
- Markdown / trailing whitespace / link inspection
- GitHub #384 / #392 body sync
- #388〜#390 close reasonとsuperseded-before-implementationの記録
- human explanatory HTML / Tailscale preview更新
- clean pushed branchに対するindependent Strict review

## Exit / handoff

- Product decisionsはaccepted ADRとEpic docsで完了している。
- `iss-00392`がimplementation-readyで、他のchild implementation Issueを必要としない。
- dynamic external factsは具体的な取得step / fail-closed conditionを持つ。
- merge / closeは実装後の別lifecycle gateであり、本planning完了を実装完了と扱わない。

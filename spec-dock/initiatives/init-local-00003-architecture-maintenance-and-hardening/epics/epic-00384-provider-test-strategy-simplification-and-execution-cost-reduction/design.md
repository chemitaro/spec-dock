---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md"]
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

詳細: [Design Guide](../../../../docs/authoring/design.md)

## 設計目標

provider distributionの安全性を、per-file historical identityとarbitrary recoveryの広さではなく、狭いownership boundary、fixed action set、stage-before-mutate、fail-closed classification、same-candidate rerunで実現する。Product contract縮小とtest portfolio縮小を同じ実装ユニットへ結び、不要になったstateとtestを同じcutoverで除去する。

## Architecture

```text
Current
legacy per-file engine
  ├─ install / update
  ├─ deprovision / purge
  ├─ historical identity
  ├─ journal / checkpoint / cross-intent recovery
  └─ duplicate / sharded regression

Target
fixed-root lifecycle service
  ├─ domain/model: fixed targets, state, result
  ├─ filesystem: no-follow binding, stage, replace
  ├─ application: install/update/uninstall
  ├─ legacy_023: exact predecessor recognizer
  ├─ CLI: arguments and result mapping
  └─ build-once single-process gate
```

legacy lifecycleからtargetへcombined hard cutoverする。uninstall-first bridge、P0〜P3、split path、cross-Issue fixture API、runtime toggleを持たない。

## Ownership model

### Provider-owned fixed targets

```text
spec-dock/docs
spec-dock/templates
spec-dock/system
spec-dock/scripts
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
```

4 rootsと2 slotsはcode-fixedである。manifestやrecordからarbitrary pathを取得しない。

### Consumer-owned seeds

```text
spec-dock/.gitignore
.github/workflows/ci.yml
```

fresh initでabsentの場合だけ作成する。その後はconsumer-ownedで、provider update / reinstall / uninstallはfollow / overwrite / deleteしない。installation completeness、legacy recognition、uninstall targetにも含めない。

### Durable / opaque / generated

- durable user data: `spec-dock/initiatives/**`とnested Artifacts
- opaque preserve: `.workbench/**`、unknown paths、unrelated skills
- generated projection: `active/**`、`.agent/**`、dashboard、tree / deps図、ADR mirror

これらはprovider payload inventoryに含めず、lifecycle mutation対象にしない。unknown non-targetの存在だけではoperationをblockしない。

## State model

computed stateを次へ縮小する。

```text
absent
legacy-0.2.3
ready
incomplete(install|update|uninstall, candidate)
tooling-absent-preserved-data
blocked
```

`blocked`はserialized stateではなく、binding / type / marker / digest / active recoveryの観測結果である。

fixed installation recordはrepository rootへ置き、known schema、state、operation、version、candidate digest、2 slot versionsだけを持つ。exact pathはimplementationでold-engine mutation-zeroとforeign collisionを検証して固定する。

recordへ持たせないもの:

- arbitrary path / action list
- per-file digest
- per-action checkpoint / progress bit
- rollback image
- cross-intent authority
- historical version catalog

## Deep interfaces

```text
install_tooling(target, candidate) -> LifecycleResult
update_tooling(target, candidate) -> LifecycleResult
uninstall_tooling(target) -> LifecycleResult
```

CLIはservice内部のfilesystem planを知らず、typed resultをtext / JSON / exitへmappingする。

### Install

1. bind / classify / preflight
2. candidate stage / validate
3. incomplete install record
4. fixed roots / slots配置
5. ready record
6. best-effort owned temporary cleanup

### Update

1. bind / classify / preflight
2. candidate stage / validate
3. incomplete update record
4. `docs -> templates -> system -> scripts -> slots`
5. ready record
6. best-effort cleanup

### Uninstall

1. bind / classify / dry-run plan
2. apply時だけincomplete uninstall record
3. 4 roots
4. valid owned 2 slots
5. record delete
6. tooling-absent-preserved-data

skill slot処理でmarker authorityを失わないため、exact fixed tombstoneへのno-replace renameを許可する。arbitrary tombstone名、catalog、progress bitは持たず、rerunはexact tombstoneとvalid markerだけを認識する。

## Failure / recovery

- preflight / stage failure: target mutation 0
- mutation target unknown: preserve-and-block
- unknown non-target: preserve-and-ignore
- root / slot間failure: incomplete recordを残す
- same operation / same candidate: rerunで収束
- different operation / candidate: block
- ready後valid owned temporary cleanupだけ失敗: completed_with_warnings
- root / slot / recordがfinal stateでない: partial_failure
- automatic rollback / old-engine fallback:行わない

public result:

| result | exit | meaning |
|---|---:|---|
| planned | 0 | dry-run plan成立 |
| completed | 0 | desired state成立 |
| completed_with_warnings | 0 | desired state成立、owned cleanupのみ残存 |
| blocked | 1 | mutation前にauthority不成立 |
| partial_failure | 1 | mutation後にdesired state未成立 |
| error | 2 | invalid request / removed operation |

## Legacy 0.2.3 adapter

`Legacy023Recognizer`のinputはexact predecessor一件だけである。

- real repository / `spec-dock` binding
- exact `0.2.3` version evidence
- expected runtime script digest
- 4 rootsがexpected parent直下のreal directories
- active legacy journal / retry / purge recovery不存在
- 2 current slotsがabsentまたはexact markerless `0.2.3` tree

modified / foreign / symlink / unexpected typeではoperation全体をwrite 0でblockする。migration後はnew recordを優先し、legacy recognizerを二度と呼ばない。historical version catalog、range comparison、partial identity、consumer manifest authorityを移植しない。

old `0.2.3` packageのmutating commandsはfinal workspaceにmutation 0でなければならない。final marker / record / root evidenceをold engineがunknownとしてblockできるよう設計し、成立しない場合もbridge generationを追加しない。

## Public CLI

| surface | final semantics |
|---|---|
| `init` | absent / tooling-absentへinstall、exact 0.2.3へmigration |
| `init --force` | state別install / update alias、追加authorityなし |
| `update` | readyまたはsame incomplete candidateをupdate / resume |
| `uninstall` | tooling-only dry-run |
| `uninstall --apply` | tooling-only mutation |
| `--keep-specs` | default uninstallと同義 |
| `--remove-specs` | mutation 0、removed-operation error、exit 2 |

spec-history purge service、purge journal、purge retry、independent purge commandは存在しない。

## Test architecture

### Pure / domain

ownership classification、state transition、operation admission、typed result。filesystem、Git、package build、CLI subprocessを起動しない。

### Filesystem / application

minimal synthetic workspace、fixed action set、no-follow、stage-before-mutate、ready-last、same-candidate rerun、fault injection、byte preservationを証明する。

### CLI adapter

argument、text / JSON、exit、mutation_startedと代表happy / fail-closed pathsを証明する。

### Built artifact

exact `0.2.3 -> final -> tooling uninstall -> reinstall`、old-package mutation-zero、wheel lifecycle、sdist minimal smokeを証明する。

### Platform delta

macOSはexecutable mode、symlink/no-follow、rename/replacement、installed entry pointだけを所有する。Linux canonicalのplatform-independent nodeとintersection 0にする。

## Artifact / CI graph

```text
source SHA
  -> build invocation 1
       ├─ wheel + SHA-256
       └─ sdist + SHA-256
            |
            ├─ Linux canonical: pytest process 1, worker 1
            └─ macOS delta: same wheel, delta nodes only
```

- PRをauthoritative merge gateにする。
- main pushでFull Regressionやcandidate rebuildを行わない。
- `workflow_dispatch`をfinal 5-run / rolling-20 / fault evidenceに使えるnon-required routeにする。
- release publication workflowは作らない。
- required contextは既存名の再利用を優先する。
- 名前変更時だけ、old + new、intentional new-only RED、new-only requiredへ同じIssue / PRで遷移する。
- `Provider Receipt Binding`やappend-only coordination chainを作らない。

## Removal model

cross-Issue receipt chainを持たず、`iss-00392` reportに一枚のtraceability tableを置く。

| removed symbol / node / workflow | reason | successor / retirement authority | focused verification |
|---|---|---|---|

successor proof成立後だけold production route / tests / workflowを削除する。

## Rollback

- pre-merge: PRをmergeせず、external required setをbefore stateへ戻す。
- runtime: preflightでwrite 0、partial failureはsame-candidate rerun。
- destructive defect: apply routeをfail closedにし、read-only diagnosticを維持する。
- post-merge: human-reviewed revert。old engineへのruntime fallbackはしない。

## Risks

- fixed target classifierの欠陥によるuser data / shared content破壊
- exact `0.2.3` evidenceの過不足
- old packageがfinal workspaceを変更するdowngrade risk
- partial failureをsuccess扱いするresult mapping
- test consolidationでsecurity invariantを退役させる誤り
- required context切替時のgate空白 / pending
- large Issueによるreviewability低下。successor-firstのmilestone / PRで緩和し、Issue境界は増やさない。

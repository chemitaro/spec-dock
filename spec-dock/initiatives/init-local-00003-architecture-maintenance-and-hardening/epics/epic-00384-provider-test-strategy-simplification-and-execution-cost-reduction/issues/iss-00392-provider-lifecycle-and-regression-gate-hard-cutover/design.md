---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

historical per-file reconciliationとcross-intent recoveryを、fixed action set、small installation record、deep lifecycle servicesへ置換する。CLI、filesystem、state、legacy recognition、tests、CIの責務を分離しながら、public cutoverと検証は一つのIssueで完結させる。

## Current / Target

Current:

- `managed_distribution.py`がfresh / update / deprovision / purge、historical identity、journal、retry、CLI resultを集中所有する。
- `managed_distribution.json`がversion、historical current identities、obsolete exact filesを列挙する。
- ordinary / Ubuntu parity / macOS parity / 4-shard Full Regressionが同じcontractを重複実行する。
- 26 active failuresをledgerでapproved-no-opとして成功扱いする。

Target:

```text
legacy per-file engine
  -> combined hard cutover
  -> fixed-root lifecycle service
     + exact 0.2.3 recognizer
     + build-once single-process gate
```

- production generationはfinal形一つだけで、uninstall-first bridgeやruntime toggleを持たない。
- stateを`absent | legacy-0.2.3 | ready | incomplete | tooling-absent-preserved-data | blocked`へ縮小する。
- `blocked`はserialized stateではなくobserved evidenceから算出する。

## 責務・Interface

### Domain / model

- 4 fixed roots、2 fixed slots、operation、installation record、typed resultを定義する。
- action setはcode-fixedで、arbitrary pathやmanifest pathを受け取らない。

### Filesystem boundary

- repository / parent binding、no-follow、symlink、unexpected type、marker、byte identityを観測する。
- candidateをtarget外にstage / validateする。
- fixed root replacementとfixed slot tombstone renameを実行する。

### Application services

```text
install_tooling(target, candidate)
update_tooling(target, candidate)
uninstall_tooling(target)
```

- CLIやfilesystem detailを公開せず、typed resultを返す。
- same operation / same candidate rerunだけを収束させる。

### Legacy adapter

`Legacy023Recognizer`だけを持つ。exact version / runtime digest、root binding、active recovery absence、markerless slot exact treeをread-onlyで確認し、不一致はmutation前にblockする。

### CLI adapter

- parser、command/state dispatch、text / JSON / exit mappingだけを所有する。
- `init --force`、`--keep-specs`、`--remove-specs`のcompatibility semanticsをservice resultへ変換する。

### CI / reporter

- build invocation / candidate SHA / output digest / node set / OS / wall / CPU / duplicate countをthin evidenceとして出力する。
- lifecycle authorityやtest selection policyをreporterへ持たせない。

## data / failure

### Installation record

repository root直下のfixed pathにsmall recordを置く。exact pathはimplementation開始時にexisting collision / legacy-engine behaviorを確認して決め、foreign collisionではmutation前にblockする。

ready recordは少なくとも次を持つ。

```json
{
  "schema_version": 1,
  "state": "ready",
  "operation": null,
  "version": "<distribution-version>",
  "candidate_digest": "<sha256>",
  "skill_slots": {
    "spec-dock": "<distribution-version>",
    "spec-dock-grill-with-docs": "<distribution-version>"
  }
}
```

incomplete recordは`state=incomplete`、`operation=install|update|uninstall`、desired / installed version、candidate digestを持つ。arbitrary path、per-file digest、action list、checkpoint、progress bit、rollback image、historical catalogは持たない。

### Protocol

Install:

1. bind / classify / preflight
2. candidate stage / validate
3. incomplete install record
4. roots / slots配置
5. ready record
6. best-effort owned temporary cleanup

Update:

1. bind / classify / preflight
2. candidate stage / validate
3. incomplete update record
4. `docs -> templates -> system -> scripts -> slots`
5. ready record
6. best-effort cleanup

Uninstall:

1. bind / classify / dry-run plan
2. apply時だけincomplete uninstall record
3. 4 roots
4. valid owned 2 slots
5. record削除
6. tooling-absent-preserved-data

### Failure result

| condition | result | exit |
|---|---|---:|
| dry-run成立 | planned | 0 |
| desired state成立 | completed | 0 |
| desired state成立、valid owned cleanupのみ残存 | completed_with_warnings | 0 |
| ownership / binding不明、mutation前 | blocked | 1 |
| mutation後にroot / slot / record未完了 | partial_failure | 1 |
| invalid request / removed purge | error | 2 |

slot delete / replaceでmarker authorityを失わないため、exact fixed tombstoneへのno-replace renameを許可する。arbitrary tombstone name、catalog、progress bitは持たない。rerunはexact tombstoneとvalid markerだけを認識する。

## 変更対象

変更する:

- provider-side source under `src/spec_dock/`
- lifecycle model / filesystem / application services
- legacy `0.2.3` read-only recognizer
- CLI mappingとshipped docs / assets
- distribution / package / platform / fault tests
- provider workflow、metrics、duplicate detection
- ledger / timing / sharder / policy-skip machineryの撤去

変更しない:

- Issue #372のspec / evidence
- user-owned Initiatives / Artifacts
- unrelated skillsとunknown non-target paths
- human PR merge gate
- release publication pipeline

## 移行・互換性・rollback

- final public generationへcombined cutoverし、P1 bridgeやold/new writer toggleを公開しない。
- exact clean `0.2.3`だけをone-shot migrateする。new recordがあればlegacy recognizerを呼ばない。
- active legacy recoveryはwrite 0でblockし、last-compatible `0.2.3`でclean stateへ戻すguidanceを返す。
- `.gitignore` / consumer `ci.yml`はfresh initでabsentの場合だけseedし、それ以外はpreserveする。
- old package mutation-zeroが成立しなければfinal marker / formatを変更し、旧engineがunknownとしてblockするまでmergeしない。
- pre-merge rollbackはPRをmergeせず、変更したrequired setがあればcaptured before stateへ戻す。
- post-merge defectはhuman-reviewed revertを使う。runtimeでold engineへautomatic fallbackしない。
- destructive defectではapply routeをfail closedにし、read-only diagnosticを維持する。

## testability

### Pure / domain

- ownership classification、state transition、typed result、CLI mappingを外部I/Oなしで検証する。

### Filesystem / service

- fixed action set、no-follow、byte preservation、stage-before-mutate、ready-last、same-candidate rerunをsynthetic workspaceで検証する。
- record、各root、各slot、ready write、cleanup境界にseeded faultを注入する。

### CLI

- install / update / uninstall、compatibility aliases、text / JSON / exit、mutation_startedを検証する。

### Built artifact

- exact `0.2.3 -> final -> tooling uninstall -> reinstall`を同じfinal wheelで通す。
- old `0.2.3` commandsがfinal workspaceにmutation 0であることをtree digestで証明する。
- wheel / sdist source SHAとdigest mismatchをfailさせる。

### Platform / portfolio

- Linux canonicalはsingle processで全merge-required contractを実行する。
- macOS deltaはnode setを固定し、Linux canonicalとのintersectionが0であることを検証する。
- final node inventory、duplicate count、5-run、fault pack、rolling 20を同じcandidate SHAへ束縛する。

## risk

- fixed root allowlist / bindingの欠陥によるuser data削除。
- legacy `0.2.3` evidenceの過不足による誤migration / support拒否。
- old packageがfinal markerを認識せずnew workspaceを変更すること。
- incomplete stateをsuccess扱いすること。
- test削減時にsecurity invariantまで退役させること。
- required context切替時のgate空白または永続pending。
- big-bang diffがreviewabilityを失うこと。successor-firstの複数commit / PRを使い、各merge pointをreleasableに保つ。

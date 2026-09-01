---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["iss-00387", "../../requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["epic-00384", "init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d18ca60b2a6ff11571ee366f71c4528dcd668d99"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

## 1. Objective and acceptance unit

本IssueはEpic #384の唯一のimplementation-and-verification unitである。4 fixed roots、2 fixed skill slots、fixed JSON record、exact `0.2.3` migration、tooling-only uninstall、public compatibility、old contract removal、test portfolio terminalization、build-once provider gate、final qualificationを一つのend-to-end acceptanceとして完成させる。

本Issue内で複数step/PRを使ってよいが、research-only、decision-only、tests-only、verification-onlyの別Issueを作成しない。

## 2. Numbered end-to-end contract

### I392-RQ-001 — #387 post-merge admission

Implementationは#387がhuman mergeされた後だけ開始する。`AUTHORING_SHA=d18ca60b2a6ff11571ee366f71c4528dcd668d99`と`POST_387_SHA`のfull SHAを固定し、#387 exact allowlist/content restriction、current gates、package version `0.2.3`、baseline artifact hashesを検査する。unclassified drift、protected path drift、baseline failureがある場合はcode changeを開始しない。

### I392-RQ-002 — Exact persistent paths

Persistent provider mutation authorityは次だけである。

```text
spec-dock/docs
spec-dock/templates
spec-dock/system
spec-dock/scripts
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
```

fresh `init`でpath absentの場合だけ、次を作成できる。

```text
spec-dock/.gitignore
.github/workflows/ci.yml
```

`.github`と`.github/workflows`がabsentの場合、second seedのexact parent chainをreal directoryとして作成できる。これらのdirectory/fileは作成直後からconsumer-ownedであり、update/reinstall/uninstallで変更・削除しない。

### I392-RQ-003 — Protected data

`spec-dock/initiatives/**`、all nested artifacts、`.workbench/**`、active/generated state outside fixed roots、unknown non-target paths、unrelated skills、consumer-owned seedsをoperation前後でbyte/type/mode/link-target identityが等しい状態に保つ。providerはこれらをrecovery materialとして使用しない。

### I392-RQ-004 — Final version and record

`pyproject.toml`のfinal package versionを`0.2.4`とする。`spec-dock/spec-dock.version`をstrict JSON recordへhard cutoverする。recordはexact six top-level keysだけを持つ。

```json
{
  "schema_version": 1,
  "state": "ready",
  "operation": null,
  "version": "0.2.4",
  "candidate_digest": "<64 lowercase hex>",
  "skill_slots": {
    "spec-dock": "0.2.4",
    "spec-dock-grill-with-docs": "0.2.4"
  }
}
```

`state=incomplete`だけ`operation=install|update|uninstall`を要求する。`ready`と`tooling-absent-preserved-data`では`operation=null`を要求する。unknown key、missing key、duplicate JSON key、invalid value、invalid file typeはblockする。

### I392-RQ-005 — Slot authority

New-format slotは`.spec-dock-provider-slot.json`がrecordのslot、version、candidate digestと一致する場合だけownedである。markerless slotはexact legacy recognizerでwhole-tree digestが一致する場合だけownedである。foreign marker、invalid marker、markerless modified tree、slot symlinkをmutation前にblockする。

### I392-RQ-006 — Candidate

Candidateはpackage内の4 rootsと2 slotsからcode-fixedに構築する。seed、record、generated slot markerをdigest対象に含めない。candidate sourceとstaged treeにregular file/real directory以外、hard link、path traversal、absolute pathがあればtarget mutation zeroでblockする。candidate digestはversion、logical path、kind、mode、file content digestをcanonical orderでSHA-256する。

### I392-RQ-007 — Classification

Classifierは`absent | legacy-0.2.3 | ready | incomplete | tooling-absent-preserved-data | blocked`を返す。`blocked`はserialized stateではない。repository/parent symlink、root replacement、foreign collision、invalid record、invalid slot marker、active legacy recovery、unsupported legacy、unsafe transient stageをpre-mutationでblockする。

### I392-RQ-008 — Install semantics

- fresh `init`: absent fixed targetsへcandidateをinstallし、2 seedsをabsent時だけ作成する。
- `update` on never-installed absent: compatibility installを行うがseedを作成しない。
- reinstall from tooling-absent: candidateをinstallし、seedを作成しない。
- exact legacy migration: candidateへone-shot replaceし、seedを変更しない。
- install開始時はcandidate validation後に`incomplete(install)` recordを最初のdurable target writeとして公開し、ready recordを最後に公開する。

### I392-RQ-009 — Update semantics

ready workspaceでは4 rootsと2 slotsをcandidateへ収束させる。record-owned rootはwhole-root disposableであり、missing root/slotをrepairできる。root/slot publish orderは`docs -> templates -> system -> scripts -> spec-dock slot -> grill slot`である。seedとprotected dataは変更しない。

### I392-RQ-010 — Atomic replacement

Target absent publishはnative no-replace rename、valid existing directory replaceはnative exchange renameを使用する。Linuxでは`renameat2`、macOSでは`renameatx_np`を使用する。operationはrepository root lockとdescriptor-bound parent chain下で行う。atomic primitive不在、cross-device、identity drift、unexpected typeではfail closedとする。

### I392-RQ-011 — Tooling-only uninstall

`uninstall`はdefault dry-runである。`--apply`時だけ、valid recordまたはexact legacy evidenceがownedと証明する4 rootsと2 slotsを除去する。user history、unknown path、unrelated skill、seedを変更しない。successful apply後はrecordを削除せず`tooling-absent-preserved-data`へatomic replaceする。

### I392-RQ-012 — Reinstall discriminator

record absentのnever-installed `absent`と、record presentの`tooling-absent-preserved-data`をdurably区別する。tooling-absent stateでは4 roots/2 slotsがabsentでなければblockする。reinstallはmissing seedsをconsumer intentとして保持する。

### I392-RQ-013 — External convergence

Partial failure後はrecordのoperationとcandidate digestがcurrent requestに一致する場合だけresumeする。matching targetはno-op、missing/nonmatching owned targetはcandidateへ収束させる。cross-intent、cross-candidate、invalid transient stageはmutation前にblockする。automatic rollback、checkpoint selection、old engine fallbackを実装しない。

### I392-RQ-014 — Exact `0.2.3` migration

Post-#387 baseline `0.2.3` wheelから生成したplain marker、4 root whole-tree digests、2 slot whole-tree digestsだけをlegacy authorityにする。4 rootsは全てexact、2 slotsは各々absentまたはexactを許可する。legacy recovery markerが存在する場合は内容を推測せずblockし、last-compatible packageでclean stateへ戻すguidanceを返す。

### I392-RQ-015 — Old package mutation-zero

Final ready、final tooling-absentの代表workspaceに対し、old baseline `0.2.3` packageの次を実行する。

```text
init --force
update
uninstall --apply --keep-specs
uninstall --apply --remove-specs
```

Startup composite tripwireはtarget-scoped Python filesystem mutation eventsとnative `renameat2` / `renameatx_np` callをunderlying call前に捕捉する。各old commandはtripwire event 0、nonzero refusal exit、target tree digest不変でなければならない。各platformのPython write positive controlとnative symbol positive controlはcall前に捕捉されなければならない。

### I392-RQ-016 — Public CLI compatibility

Command/flag grammarを維持する。

```text
spec-dock init [path] [--force]
spec-dock update [path]
spec-dock uninstall [path] [--apply] [--keep-specs|--remove-specs] [--json]
```

- `init --force`はstate-based install/update aliasである。
- `uninstall --apply`はspecs modeなしでtooling-only applyを許可する。
- `--keep-specs`はdefaultと同義である。
- runtime shipped wrapperは`uvx --no-cache --from git+https://github.com/chemitaro/spec-dock` forwardingを維持する。
- accepted changes以外のsuccess output、stderr use、target resolutionを維持する。

### I392-RQ-017 — Purge removal

Purge service、purge intent、purge journal/recovery、history deletion testを削除する。`--remove-specs`はfilesystem classificationより前に処理し、targetがmissing/invalidでもmutation zero、status `error`、code `spec-history-purge-removed`、exit 2を返す。text/JSONの両modeで同じcodeを観測できる。

### I392-RQ-018 — Typed result and exit

Result statusとexitは次で固定する。

| Status | Exit | Required behavior |
|---|---:|---|
| `planned` | 0 | dry-run、mutation_started=false |
| `completed` | 0 | desired durable state成立 |
| `completed_with_warnings` | 0 | desired state成立、owned external cleanupだけ残存 |
| `blocked` | 1 | target durable mutationなし |
| `partial_failure` | 1 | mutation_started=true、same-operation retry guidance |
| `error` | 2 | invalid request / removed operation、mutation zero |

Uninstall JSONはexisting schema_version 1の主要fieldを維持し、additive `code`と`mutation_started`を持つ。`actions`にfixed set外pathを出力しない。

### I392-RQ-019 — Test portfolio and terminalization

- Pure/model testsはreal FS、Git、package build、CLI subprocessを使わない。
- Filesystem/service testsはsynthetic workspace、fault hook、actual descriptor/native renameを使う。
- CLI testsはparser、text/JSON/exit、representative fail-closedだけを所有する。
- Built-artifact testsはbaseline migration、final lifecycle、old package tripwire、artifact identityを所有する。
- macOS deltaはplatform-specific behaviorだけを所有する。
- post-#387 active failure entryをfix/successor/retirementへ全件terminal化する。
- `tests/provider_test_ownership.json`でcontract ownerを一意にし、duplicate `(candidate, os, contract_id)`を0にする。
- approved failure、path policy skip、retryによるsuccessを許可しない。

### I392-RQ-020 — Artifact, CI, qualification, handoff

- `0.2.4` final source SHAからwheel/sdistをone packaging invocationでbuildしmanifestへhashを固定する。
- Linux canonicalはsame wheelをinstallし、worker 1、one pytest processでcanonical nodesを実行する。
- macOS deltaはLinux-built same wheelをinstallし、exclusive platform nodesだけを実行する。
- sdistはLinux minimal metadata/package-data smokeを行う。
- final treeからold Full Regression workflow、ledger、timing、sharder、policy hooksを削除する。
- fixed Linux referenceでsame candidateを20回sequential実行し、first 5各600秒以内、CPU/wall <= 1.1、all 20 flake 0/retry 0を満たす。
- seeded fault pack detection 100%を満たす。
- new provider gateのGREENとintentional RED blockingを証明し、human review gateを維持する。
- final dogfood sync/validate、fresh consumer、exact PR head treeをreportへ記録する。
- human merge後にmerged SHAとverified PR SHAを照合する。

## 3. Command-to-state compatibility matrix

| Observed state | `init` | `init --force` | `update` | `uninstall` |
|---|---|---|---|---|
| `absent` | install + absent seeds | same | install, seed preserve-only | error `tooling-not-installed` |
| `legacy-0.2.3` | blocked `already-initialized` | migrate | migrate | dry-run/apply legacy tooling removal |
| `ready` | blocked `already-initialized` | update | update | dry-run/apply |
| `incomplete(install)` | same-candidate resume | same-candidate resume | same-candidate resume | cross-intent blocked |
| `incomplete(update)` | blocked | same-candidate resume | same-candidate resume | cross-intent blocked |
| `incomplete(uninstall)` | cross-intent blocked | cross-intent blocked | cross-intent blocked | same-candidate resume |
| `tooling-absent-preserved-data` | reinstall, no seeds | reinstall, no seeds | reinstall, no seeds | idempotent planned/completed |
| `blocked` | blocked | blocked | blocked | blocked |
| any + `--remove-specs` | N/A | N/A | N/A | compatibility trap takes precedence, exit 2 |

## 4. Failure behavior

- candidate build/stage validation failure: persistent target mutation 0、`blocked`。
- preflight collision/binding/marker failure: persistent target mutation 0、`blocked`。
- incomplete record publish後のroot/slot failure: `partial_failure`、recordを保持。
- ready/tooling-absent record publish後のexternal stage cleanup failure: `completed_with_warnings`。
- new recordとpackage candidate mismatch: cross-candidate `blocked`。
- active legacy recovery: `blocked`、legacy markerを変更しない。
- old package mutation attempt: acceptance failure。bridgeを追加せずrecord/marker boundaryを修正する。
- required context state unreadable: external setting mutation 0、transition停止。
- budget/fault/flake failure: same Issueでforward-fix。shard/skip/retryへ逃げない。

## 5. Completion distinction

- **Implementation complete**: final PR headでI392-RQ-001〜020のtechnical evidenceが揃う。
- **Issue report complete**: evidence table、hash、terminalization、stop/cleanup、known limitationsが`report.md`へ記録される。
- **PR merge ready**: required gateとhuman reviewがactiveで、exact PR SHAが固定される。
- **PR merged**: humanがmergeした外部事実。
- **Issue finished**: merged SHAがverified PR SHAと一致し、reportがcomplete。
- **Epic closed**: #392 finished後、Epic acceptanceが全て満たされる。

## 6. Acceptance checklist

- [ ] I392-RQ-001の#387 admissionがexact evidence付きで成立する。
- [ ] fixed mutation set外のprotected tree digestが全operationで不変である。
- [ ] record/slot schema、state matrix、candidate digestがstrictである。
- [ ] install/update/uninstall/reinstall/migrationがbuilt wheelでGREENである。
- [ ] fault境界ごとのsame-candidate convergenceとcross-intent blockがGREENである。
- [ ] old `0.2.3` command matrixがtripwire event 0、tree digest不変である。
- [ ] native/Python positive controlsがcall前に捕捉される。
- [ ] public text/JSON/exitとpurge trapがGREENである。
- [ ] active failure全件がterminal化され、ledgerが削除される。
- [ ] duplicate contract owner 0、policy skip 0、approved failure 0である。
- [ ] build invocation 1、same wheel、sdist smokeがGREENである。
- [ ] Linux canonical/macOS deltaがexclusive ownershipを満たす。
- [ ] five-run、CPU、fault pack、rolling 20が基準を満たす。
- [ ] old workflow/sharder/timing/policy machineryが存在しない。
- [ ] provider/dogfood/fresh consumer/SpecDock validateがGREENである。
- [ ] required contextとhuman review gateが維持される。
- [ ] human merge後のtree SHAがverified PR headと一致する。

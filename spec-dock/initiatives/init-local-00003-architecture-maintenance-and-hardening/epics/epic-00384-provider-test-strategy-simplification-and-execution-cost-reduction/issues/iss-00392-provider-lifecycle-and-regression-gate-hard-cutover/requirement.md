---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
親: ["epic-00384", "init-local-00003"]
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

Provider distribution lifecycle、public installer CLI、test portfolio、artifact validation、provider CIを一つの実装ユニットでhard cutoverする。実装と検証を分離せず、4 disposable rootsと2 fixed skill slotsだけを安全に管理するfinal product contract、旧contract撤去、single-process regressionの受入までを本Issueで完了する。

## 背景

現行providerは約1 MBの`managed_distribution.py`、historical per-file identity、operation journal、purge、recovery、4-shard Full Regressionと重複platform lanesを持つ。base SHA `d8f9d02f2400cbc084e5ee92a5fbba339f93f015`ではfull collectionが2,710 nodes、ordinary gateが`1574 passed, 1136 skipped in 57.02s`、failure ledgerは26 active entriesを抱える。

旧計画のdecision-only Issues #388〜#390とC4〜C11は、実装ユニットではなくtechnical phase / investigation / verificationによる横分割だった。accepted ADR `20260831t152024z-adr`は、Product判断をEpic authoringで完了し、本Issueだけがimplementation-and-verification unitになると定めた。

## 観測可能な要件

### R1. 管理対象と保護対象

- provider root mutation authorityを`spec-dock/{docs,templates,system,scripts}`の4 fixed rootsに限定する。
- skill mutation authorityを`.agents/skills/spec-dock`と`.agents/skills/spec-dock-grill-with-docs`の2 fixed slotsに限定する。
- `spec-dock/initiatives/**`、nested Artifacts、`.workbench/**`、generated projections、unknown non-target paths、unrelated skillsを探索・正規化・削除しない。
- mutation targetのownership不明、foreign marker、root / parent symlink、unexpected typeでは最初のtarget mutation前にwrite 0 / delete 0でblockする。
- `spec-dock/.gitignore`とshipped `.github/workflows/ci.yml`をfresh-init-only consumer-owned seedsとし、update / reinstall / uninstallで変更しない。

### R2. Lifecycle

- fresh、tooling-absent-preserved-data、exact clean `0.2.3` workspaceに対し、install、update、tooling-only uninstall、reinstallを提供する。
- exact `0.2.3`だけをone-shot migrateし、migration後はnew installation recordとslot markersだけをauthorityとする。
- active legacy recovery、unsupported legacy、modified / foreign markerless slotは推測変換せずmutation前にblockする。
- candidateを全てstage / validateしてから、`docs -> templates -> system -> scripts -> skill slots`の順で置換し、ready recordを最後に書く。
- root / slot間failure後は同じoperation・同じcandidateのexternal rerunだけで収束し、別candidate / cross-intent rerunをblockする。
- automatic rollback、arbitrary checkpoint、old engine fallbackをpublic contractにしない。

### R3. Public CLI

- `init --force`を独自authorityではなくstate別`install_tooling` / `update_tooling` aliasにする。
- uninstallはdefault dry-run、`--apply`でtooling-only mutationを行い、user historyを変更しない。
- `--keep-specs`をdefault uninstallと同義のcompatibility aliasとして残す。
- spec-history purge capabilityと独立purge commandを廃止する。
- `--remove-specs`はpermanent non-mutating compatibility trapとして全modeでmutation 0、code `spec-history-purge-removed`、exit 2を返す。
- planned / completed / completed_with_warnings / blocked / partial_failure / errorをtyped service resultからtext / JSON / exitへ一意にmappingする。

### R4. Test portfolio

- durable invariantごとにowner layer、authoritative lane、代表failureを一つ以上持つ。
- pure/domain testsはfilesystem、Git、package build、CLI subprocessを起動しない。
- filesystem/service testsは最小synthetic workspaceと注入可能なfaultを使う。
- CLI testsはarguments、text / JSON、exitと代表happy / fail-closed pathsに限定する。
- built-artifact testsはexact `0.2.3 -> final -> uninstall -> reinstall`、old-package mutation-zero、Linux lifecycle、macOS deltaを証明する。
- 26 active ledger nodesをfix、current successor、accepted contract retirementのいずれかへterminal化し、approved failure 0、policy skip 0にする。
- same candidate / OS / contractのduplicate nodeを0にする。

### R5. Artifact / CI / budget

- authoritative candidateごとに一つのpackaging invocationでwheelとsdistを生成し、source SHAとoutput digestsを固定する。
- LinuxとmacOSが同じwheel bytesを使う。sdistはLinux minimal smokeだけを所有する。
- Linux canonical regressionはsingle pytest process、worker 1でmerge-required contractを実行する。
- macOSはexecutable mode、symlink/no-follow、rename/replacement、installed entry pointなどplatform deltaだけを実行する。
- fixed Linux referenceで連続5回すべてwall 600秒以内、process-tree CPU / wall 1.1以下にする。
- seeded fault pack detection 100%、rolling 20でflake 0 / retry 0にする。
- main pushの4-shard Full Regression、failure ledger、timing weights、sharder、path-based policy-skip machineryを撤去する。
- required contextは既存名を可能な限り維持し、unrelated required contextsとhuman review gateを保持する。

## スコープ

対象:

- `src/spec_dock/cli.py`とdistribution lifecycleのreplacement modules
- `managed_distribution.py` / `managed_distribution.json`のretired contractとsuccessor
- provider assets、4 roots、2 skill slots、installation / slot markers
- init / update / uninstall public contract、docs、migration guidance
- distribution、init/update、CLI、package、platform tests
- `tests/conftest.py`のfull-regression policy、ledger、timing、sharder
- `.github/workflows/provider-ci.yml`と`provider-full-regression.yml`
- required context transitionに必要な同一Issue内のhuman operationとevidence

対象外:

- Issue #372のcandidate、canonical docs、acceptance evidenceの変更
- user-owned spec historyを削除する機能
- arbitrary historical version catalogの追加
- release publication workflowの新設
- worker / shard追加、xdist、machine大型化だけによるbudget回避
- decision-only、tests-only、verification-onlyの追加Issue

## 失敗・境界条件

- candidate stage / validation failureではtarget mutation 0とする。
- record、root、slot、parent binding、symlink、marker、candidate digestの不一致ではwrite前にblockする。
- incomplete recordがある場合、同じoperation・candidateだけを許可する。
- ready成立前にroot / slot処理が残ればpartial_failure / exit 1とする。
- ready成立後にvalid owned temporary cleanupだけが残る場合に限りcompleted_with_warnings / exit 0を許可する。
- old `0.2.3` packageがfinal workspaceを一つでも変更する場合はmergeしない。bridge generationを追加せずfinal marker / formatを修正する。
- required contextのlive stateを観測できない場合、外部設定を推測変更しない。

## 受け入れ条件

- [ ] 4 roots / 2 slots以外へprovider mutation authorityがない。
- [ ] user history、`.workbench`、unknown non-target、unrelated skills、consumer seedsがbyte-identicalである。
- [ ] fresh、exact `0.2.3` migration、ready update、tooling uninstall、tooling-absent reinstallがbuilt wheelでGREENである。
- [ ] active legacy recovery、unsupported legacy、foreign / invalid target、root / parent symlinkがmutation 0でblockされる。
- [ ] old `0.2.3`の`init --force`、update、tooling uninstall、`--remove-specs`がfinal workspaceにmutation 0である。
- [ ] `--remove-specs`がtext / JSONの両modeでremoved-operation error、exit 2、mutation 0を返す。
- [ ] root / slot境界のseeded faults後にsame-candidate rerunで収束し、cross-intent rerunをblockする。
- [ ] active ledger 26 nodesがfix / successor / retirementへterminal化し、ledger自体が削除されている。
- [ ] canonical regressionがunexpected failure 0、approved failure 0、policy skip 0、duplicate node 0である。
- [ ] final reference 5回が各600秒以内、CPU/wall 1.1以下である。
- [ ] final wheel / sdistのartifact build invocation countが1で、source SHA / digest mismatchがfailする。
- [ ] Linux canonicalとmacOS deltaが同じwheelを使い、macOSがplatform-independent nodesを再実行しない。
- [ ] seeded fault detection 100%、rolling 20 flakes 0 / retries 0である。
- [ ] old parity、4-shard Full Regression、sharder、timing weights、failure ledger、policy-skip hooksが削除されている。
- [ ] canonical provider contextがrequiredで、unrelated required contextsとhuman review gateが維持されている。
- [ ] human merge後のtreeが検証済みfinal PR treeと同一である。

## 制約・前提

- 本Issueは唯一のimplementation-and-verification unitであり、調査・意思決定・最終検証を別Issueへ送らない。
- 内部milestoneや複数PRを使ってよいが、各main merge pointをreleasableに保つ。
- successor proofより先に旧contract、test、workflowを削除しない。
- implementation Planning Levelは`critical`とする。
- PR mergeは人間が行う。

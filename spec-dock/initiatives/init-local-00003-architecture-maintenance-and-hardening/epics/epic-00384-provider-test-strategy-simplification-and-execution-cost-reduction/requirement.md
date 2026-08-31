---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

詳細: [Requirement Guide](../../../../docs/authoring/requirement.md)

## 目的

SpecDock providerのdistribution product contractとtest execution graphを一体で簡素化し、必要な契約を最小の実行量で証明する。4 fixed provider rootsと2 fixed skill slotsだけを管理するminimal lifecycleへhard cutoverし、user dataとshared contentを守りながら、merge-required regressionをsingle pytest process、worker 1、各600秒以内、zero failures、zero policy skips、duplicate node 0、artifact build invocation 1へ移行する。

本ProductではIssueを「実装とその検証を一体で完了・受入する一つの実装ユニット」と定義する。調査・分析・Product判断はIssue作成前のEpic / Issue authoringで完了し、decision-only、tests-only、verification-onlyのIssueを作らない。

## 背景とplanning baseline

Issue #372はdistribution parityを4-shard Full Regressionで証明したが、実行量自体は削減しない。現行productionはfresh / update / deprovision / purge、per-file identity、journal、retry、historical compatibilityを同じ巨大なdistribution engineで扱い、testsはそのstate spaceを反映している。

2026-09-01にbranch `codex/epic-00384-provider-test-strategy-planning`、base SHA `d8f9d02f2400cbc084e5ee92a5fbba339f93f015`で次を確認した。

- `managed_distribution.py`: 999,468 bytes
- `test_managed_distribution.py`: 774,072 bytes
- `test_init_update.py`: 454,511 bytes
- full collection: 2,710 nodes
- sorted node-set SHA-256: `f607b007d167231ed27f2a17391b0d8b3aa452d67ce6532565463e193486a04c`
- ordinary gate: `1574 passed, 1136 skipped in 57.02s`
- resource reference: wall 58.42s、user 24.41s、system 31.29s、CPU/wall約0.953
- failure ledger: 27 entries、26 active、1 resolved
- active cohort rerun: 26 failed in 14.69s
- current package / recognized workspace: exact `0.2.3`
- provider PR CIはordinary、Ubuntu parity、macOS parityでdistribution familyを重複実行し、main pushでさらに4-shard Full Regressionを実行する。

historical evidenceとして、別candidateのGitHub Full Regressionは2,708 tests、約99分wall、約5.51 shard-process-hoursを使用し、ordinary gateは650.55秒だった。これらは現SHAの性能証拠ではなく、根本原因の比較材料として扱う。

## Issue unit policy

### R0. One implementation unit

- Epicのimplementation-and-verification Issueは`iss-00392 Provider Lifecycle And Regression Gate Hard Cutover`の1件だけとする。
- investigation、Product decision、inventory、required-context operation、final verificationを独立Issueにしない。
- `iss-00388`〜`iss-00390`のdecision内容はaccepted ADR `20260831t152024z-adr`と本Epicへ統合し、future execution unitとしてcloseする。
- C4〜C11、`DEC-*`、`FIX-*`を作らない。
- `iss-00392`はproduction、public CLI、tests、workflow、migration、old machinery removal、performance / stability acceptanceを一体で所有する。
- 内部milestoneや複数PRを使ってよいが、各main merge pointをreleasableにし、successor proofを後続Issueへ延期しない。

## 確定Product contract

### R1. Ownership safety

- provider-owned repo-local surfaceを`spec-dock/{docs,templates,system,scripts}`の4 fixed rootsに限定する。
- managed skillsを`.agents/skills/spec-dock`と`.agents/skills/spec-dock-grill-with-docs`の2 fixed slotsに限定する。
- Initiatives、nested Artifacts、`.workbench`、generated projections、unknown non-target paths、unrelated skillsを探索・正規化・削除しない。
- mutation targetのunknownはpreserve-and-block、mutation target外のunknownはpreserve-and-ignoreとする。
- root / parent binding、symlink、unexpected type、foreign markerをdestructive step直前に検証する。

### R2. Minimal lifecycle

- combined hard cutoverを採用し、uninstall-first bridge、P1 generation、old/new runtime toggleを公開しない。
- fixed installation recordはknown schema、state、operation、version、candidate digest、2 slot versionsだけを持つ。
- arbitrary path、per-file digest、action list、progress bit、rollback image、historical catalogをrecordへ持たせない。
- candidateを全てstage / validateした後、`docs -> templates -> system -> scripts -> slots`の順で処理し、ready recordを最後に書く。
- same operation / same candidateのexternal rerunだけでpartial failureから収束させ、cross-intent recoveryとautomatic rollbackをpublic contractにしない。

### R3. Legacy / downgrade

- 自動recognizeするlegacy cohortをexact clean `0.2.3` workspaceに限定する。
- real root binding、version / runtime digest、active legacy recovery absence、markerless current slotsのexact treeをmutation前に確認する。
- migration後はnew record / markersだけをauthorityとし、legacy recognizerを再度参照しない。
- active legacy journal / retry / purge recoveryはnew formatへ推測変換せず、exact last-compatible `0.2.3`でclean stateへ戻すguidanceを返す。
- old `0.2.3`のmutating commandsがfinal workspaceへmutation 0であることをmerge前に証明する。成立しなければfinal marker / formatを修正し、bridge generationを追加しない。

### R4. Consumer-owned seeds

- `spec-dock/.gitignore`とshipped `.github/workflows/ci.yml`をfresh-init-only consumer-owned seedsとする。
- absent時だけfresh initで作成し、existing regular / custom / symlink / unexpected typeをfollow / overwrite / deleteしない。
- update、reinstall、tooling uninstallで変更しない。
- installation completeness、candidate digest、legacy ownership anchor、uninstall allowlistから除外する。

### R5. Public CLI / user data

- `init --force`をstate別install / update aliasとし、update以上のauthorityを与えない。
- uninstallはtooling-only、default dry-run、`--apply`を唯一のconfirmationとする。
- `--keep-specs`をdefault uninstallと同義のcompatibility aliasにする。
- spec-history purge capabilityと独立purge commandを廃止する。
- `--remove-specs`をpermanent non-mutating compatibility trapとして残し、mutation 0、code `spec-history-purge-removed`、exit 2を返す。
- tooling-absent-preserved-dataからuser data / seedsを保持してreinstallできる。

## Test / CI contract

### R6. Contract-owned test portfolio

- durable invariantごとにowner layer、authoritative lane、representative failureを一つ以上持つ。
- pure/domain、filesystem/service、CLI adapter、built artifact、macOS deltaの責務を分離する。
- 26 active failuresをexact nodeごとにfix / current successor / accepted retirementへterminal化する。
- approved failure 0、unexpected failure 0、policy skip 0をGREENの定義にする。
- retired historical step名だけを根拠とするtestをdurable invariantへ統合または削除する。
- same candidate / OS / contractのduplicate nodeを0にする。

### R7. Execution budget

- canonical Linux regressionをsingle pytest process、worker 1で実行し、shard / xdist / parallel test workerを起動しない。
- fixed Linux 2 vCPU / 8 GiB referenceで連続5回すべてtest body 600秒以内とする。
-各回のprocess-tree CPU seconds / wall secondsを1.1以下とする。
- node count、subprocess count、temp workspace count、copy bytes、duplicate countをcandidate SHAへ束縛する。
- seeded fault detection 100%、rolling 20 flakes 0 / retries 0をclose条件にする。

### R8. Artifact / platform / workflow

- authoritative PR candidateごとに一つのpackaging command invocationでwheel / sdistを生成し、source SHAと各digestを固定する。
- LinuxとmacOSが同じwheel bytesを使う。
- Linux canonicalはOS非依存contract、Linux boundary、wheel lifecycle、sdist minimal smokeを所有する。
- macOS deltaはexecutable mode、symlink/no-follow、rename/replacement、installed entry pointだけを所有する。
- main pushの4-shard Full Regression、ledger、timing weights、sharder、policy-skip machineryを撤去する。
- required contextは既存名の再利用を第一選択とし、unrelated contextsとhuman review gateを保持する。
- context名変更が不可避な場合だけ、同じIssue / PRでold+new required、intentional RED canary、new-only requiredへ遷移する。

## スコープ

対象:

- distribution product contractとprovider implementation
- 4 roots、2 slots、installation / slot markers
- exact `0.2.3` one-shot migration
- init / update / tooling uninstall / reinstallとpublic result
- test portfolio、active failure cohort、built artifacts、platform delta
- provider CI、metrics、required context transition、old machinery removal
- public docs、migration guidance、Issue / Epic evidence

対象外:

- Issue #372のcandidate / evidence変更
- user data purge
- arbitrary historical compatibilityの追加
- release publication workflow
- machine増強だけによるbudget回避
- future decision / investigation / verification Issueの予約

## 受け入れ条件

- [ ] `iss-00392`一件が全implementation / verificationを所有し、追加のdecision-only / tests-only / verification-only Issueがない。
- [ ] 4 roots / 2 slots以外へprovider mutation authorityがない。
- [ ] user data、unknown non-target、consumer seeds、unrelated skillsがbyte-identicalである。
- [ ] fresh、exact `0.2.3` migration、update、tooling uninstall、reinstallがbuilt artifactでGREENである。
- [ ] active legacy recovery、unsupported / foreign / symlink stateがmutation 0でblockされる。
- [ ] old `0.2.3` packageがfinal workspaceへmutation 0である。
- [ ] purge capabilityがなく、`--remove-specs`が全modeでmutation 0 / exit 2である。
- [ ] seeded root / slot faults後にsame-candidate rerunで収束し、cross-intent rerunをblockする。
- [ ] active failure 0、approved failure 0、policy skip 0、duplicate node 0である。
- [ ] final candidate artifact build invocation count 1である。
- [ ] single-process 5 runsが各600秒以内、CPU/wall 1.1以下である。
- [ ] seeded fault detection 100%、rolling 20 flakes 0 / retries 0である。
- [ ] macOS deltaとLinux canonicalのplatform-independent node intersectionが0である。
- [ ] old Full Regression / ledger / timing / sharder / skip machineryが削除されている。
- [ ] canonical provider contextがrequiredで、unrelated contextsとhuman review gateが維持されている。
- [ ] human merge後のtreeがverified PR treeと同一である。

## 制約・前提

- Product判断はaccepted ADR `20260831t152024z-adr`で完了しており、実装者が推測しない。
- classic branch protection / effective required contextsはcurrent tokenで403となり未観測である。CI transition直前にread-only取得し、未確認なら外部設定を変更しない。
- old-package mutation-zero、final metrics、rolling 20はfinal formatが存在しない現在は証明不能であり、調査の先送りではなく`iss-00392`の実装後acceptance evidenceである。
- PR mergeは人間が行う。

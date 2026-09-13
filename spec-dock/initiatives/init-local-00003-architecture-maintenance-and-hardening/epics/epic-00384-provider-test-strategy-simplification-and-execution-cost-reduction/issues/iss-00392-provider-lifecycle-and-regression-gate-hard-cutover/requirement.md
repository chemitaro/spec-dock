---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
詳細化状態: "draft"
最終更新: "2026-09-14"
依存:
  - "../../artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "dc638e936e763cc7a6087f258201ed9ed654e7fb"
  tree: "17ce38234033393c385c4b17e40c0ccdc78bfc19"
---

# #392 要件定義 — Provider lifecycleを固定所有境界へ切り替える

> **現行状態（2026-09-14）:** [same-EUID scope narrowing ADR](../../artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md)と[P392 sequence ADR](../../artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md)を採用済み。既存CP1–CP4 candidateは未受入であり、Product実装許可は独立review・clean pushed freeze/projection完了までfalseとする。#392 merge後はP392であり、B1/B2は#395 merge後の同一tipで判定する。

## 1. 結論

Issue #392は、現行のper-file managed-distribution engineを廃止し、四つのfixed tooling roots、二つのfixed skill slots、strict seven-key installation recordだけをdurable mutation authorityとする0.2.4 lifecycleへhard cutoverする、一つの実装・検証・PR受入単位です。

このIssueのPRは`codex/epic-00384-provider-test-strategy-planning`だけをbaseとし、人間が同Epic integration branchへmergeします。#392 candidateはP392としてmergeし、#395はそのexact tipからだけ開始します。#395 merge後の同一tipでB1/B2を判定し、B1がGREENになるまで#392を完了扱いにしません。#392をmainへ直接mergeしません。

親のpublic wire inventory、三Issue責務、14 active baseline、`E384-QUAL-001`、`E384-DEC-001/002`は再設計しません。E384-DEC-004が定めるthreat scopeだけを反映し、public code/relation/goldenは変更しません。実装開始許可は、Issue仕様の独立内容reviewと、この内容を反映したclean pushed freeze/projectionが実際に完了するまで`false`です。

## 2. 正本、優先順位、対象時点

現行の文書優先順位は次のとおりです。

1. Epic #384のaccepted [same-EUID scope narrowing ADR](../../artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md) — 現行のthreat boundaryと再開条件。accepted [P392 sequence ADR](../../artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md) — 暫定merge、#395 entry、B1/B2順序。
2. Epic #384の`provider-lifecycle-wire-contract.md` v12 — normative public wireとcooperative coordination契約。今回public inventoryは変更しない。
3. Epic #384のRequirement、Design、Plan、他のaccepted ADR、`active-failure-disposition-register.md`、`epic-integration-branch-contract.md`、`rolling-wave-issue-elaboration-contract.md`。
4. 本IssueのRequirement、Design、Plan — 独立review/freezeを待つ改訂候補。
5. superseded [same-EUID safe-stop ADR](../../artifacts/20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md) — 当時の脅威範囲と停止判断の履歴。
6. 本IssueのArtifactとverified commit `dc638e936e763cc7a6087f258201ed9ed654e7fb`のProduct source/test — 仕様履歴と証拠。

本仕様パックは上記verified commitを調査基準とします。親Wireのfinite inventoryは、6 status、41 code、23 phase、24 last-completed-phase、168 relation rows、40 public JSON goldens、4 durable record goldensです。実装でこの数を増減・再解釈してはなりません。

## 3. Goal

1. `spec-dock/docs`、`spec-dock/templates`、`spec-dock/system`、`spec-dock/scripts`を四つのfixed rootsとしてroot単位で交換します。
2. `.agents/skills/spec-dock`と`.agents/skills/spec-dock-grill-with-docs`を二つのexact skill slotsとして管理します。
3. `spec-dock/spec-dock.version`をWire v12のstrict seven-key compact JSON recordへ置換します。
4. `spec-dock/.gitignore`と`.github/workflows/ci.yml`をfresh-only create-if-absent seedとして扱い、既存bytesを更新・削除しません。
5. Candidate digest、slot marker、exact-clean 0.2.3 fixture、private ACTIVE/stage/receipt、native atomic filesystem Adapterをclosed formatで実装します。
6. WIR-PREP-001のP0/P1/P2、root間中断、terminal record、stage cleanup、completion receipt、response lossをexact recoveryへ収束させます。
7. repo-local runtimeはreplaceable module import前にrepository-root SH leaseを取得し、installerは全parser-valid lifecycle pathでEX leaseを取得します。
8. update/uninstall wrapperはrelease-to-exec handoffとし、外部installer開始後にold moduleへ戻りません。
9. managed Git checkout、worktree create/remove、managed helper、consumer make hookをsame-generationかつactual-target coordinationへ閉じます。
10. provider source、wheel、sdist、installed resources、checked-in dogfoodを同一candidateへ収束させ、旧writer・旧manifest・obsolete-only testを撤去します。
11. required-fast、current provider CI、full-regression machinery、15-row register、14 active node、1 resolved successor、243 timing entriesを弱めず維持します。

## 4. Non-goal

脅威境界: サポート対象の同時実行は、定義済みleaseを守るSpecDock commandに限ります。通常のfilesystem/I/O failure、process interruption、Wire-defined recovery、観測されたbinding drift、protected-data preservation、symlink/special-type拒否は引き続き保証対象です。一方、同一EUIDの非協調actorによる実行中のfilesystem/Git/process介入は対象外とし、creator provenance、non-interference、任意時点のintegrityを保証しません。異なるcredentialのactorについても、OSの書込み権限境界が有効な場合に限り、権限昇格や共有書込み権限を持つactorへの保証は追加しません。

owner/mode、lock、inode witness、descriptor-relative operation、atomic renameは、この境界内の協調・通常障害処理のために維持します。これらを同一EUID actorに対するsecurity boundaryとして扱わず、特権broker、daemon、OS policy、独自security subsystemは追加しません。

- #395が所有する14 active baseline failureの修正、skip、xfail、retirement、signature変更、lifecycle変更。
- #396が所有するbuild-once final gate、current policy removal、ledger/timing/sharder削除、`E384-QUAL-001`実装または数値変更。
- arbitrary legacy migration、best-effort migration、旧writer fallback、bridge generation、dual writer、generic journal。
- whole-operation automatic rollback、rootごとの過去世代履歴、利用者データのsnapshot/restore。
- initiatives、Artifact、active、`.agent`、diagrams、`.workbench`の生成・再構築・削除。
- unrelated skill、unknown shared path、consumer seedのscan、normalize、ownership取得。
- 任意のmanual Git/filesystem操作、任意consumer hook、停止していない0.2.3 processを協調対象とすること。
- checkpointを独立Issue、独立PR、独立merge単位にすること。
- agentによるPR merge、Issue PRのmain向け作成、integration branchへのdirect push。

## 5. Fixed ownershipとprotected data

| 種別 | Exact path | 要求 |
|---|---|---|
| Fixed root 1 | `spec-dock/docs` | ownership成立後はroot全体をcandidateへ交換。内部local editは保存対象にしない。 |
| Fixed root 2 | `spec-dock/templates` | 同上。 |
| Fixed root 3 | `spec-dock/system` | 同上。runtime内lockはcross-generation authorityにしない。 |
| Fixed root 4 | `spec-dock/scripts` | 同上。四root中最後に公開する。 |
| Skill slot 1 | `.agents/skills/spec-dock` | exact slotとvalid slot markerだけをauthorityとする。 |
| Skill slot 2 | `.agents/skills/spec-dock-grill-with-docs` | exact slotとvalid slot markerだけをauthorityとする。 |
| Installation record | `spec-dock/spec-dock.version` | strict seven-key compact JSON、one LF、mode0644、regular/link1。 |
| Fresh-only seed | `spec-dock/.gitignore` | operation開始時のimmutable seed policyに従い、missing時だけ作成。既存bytesは不変。 |
| Fresh-only seed | `.github/workflows/ci.yml` | 同上。`.github`と`.github/workflows`は必要なcontainerだけbounded creation。 |
| Private bookkeeping | Consumer外のsame-filesystem owner/repository-bound namespace | ACTIVE、stage、record temp、completion receiptだけ。public ownershipへ追加しない。 |
| Protected | `spec-dock/initiatives`、Artifact、`spec-dock/active`、`spec-dock/.agent`、`spec-dock/diagrams`、`spec-dock/.workbench` | lifecycleは内容を読んで再構築・削除・正規化しない。root-level no-follow preservation witnessだけを許す。 |
| Protected | unrelated skills、unknown path、consumer seeds | scan/delete/renameしない。collisionはpreserve-and-block。 |

## 6. Observable requirements

### I392-RQ-001 — 単一のhard-cutover outcome

0.2.4 public CLIが新lifecycle engineだけへ到達し、`src/spec_dock/managed_distribution.py`、`src/spec_dock/assets/managed_distribution.json`、旧journal/retry writer、旧per-file mutation planへのproduction import/callが0件であること。新moduleだけ、testだけ、dogfoodだけの部分導入は不合格です。

### I392-RQ-002 — Candidate identity

Candidate digestはDesignで固定したcanonical byte streamのSHA-256とし、四roots・二slotsのcontent/type/modeを包含します。slot marker、installation record、private state、inode/mtime/ctime、consumer seedはdigestへ含めません。source、wheel、sdist、isolated installed packageが同じdigestを生成しなければなりません。

### I392-RQ-003 — Installation recordとslot marker

Installation recordはWire v12のexact seven keys/order/type/nullabilityを満たし、duplicate、unknown、missing、wrong type、oversize、symlink、hard linkを拒否します。各slot markerはWire v12のexact four keys/orderを満たします。record/markerのpublic bytesはdeterministicで、末尾LFは一つです。`RECORD-TEMP`はpublic-record staging objectとして最終public mode0644で作成・fsyncし、native rename/exchangeでそのmodeを保ったまま公開します。Private metadata/tempのmode0600一般則からの唯一の例外で、post-publication chmodは禁止します。

### I392-RQ-004 — Seed policy

`seed_policy`はoperation admission時に一度だけ確定してrecord/ACTIVEへdurableに保持します。retry/re-entry時にseedの有無から再推論しません。さらに、固定seed（`spec-dock/.gitignore`、`.github/workflows/ci.yml`）ごとのadmission時状態をprivate `ACTIVE.seed_admission`へ`absent|present`でdurableに保持し、retry/re-entryとaction provenanceはこの保存値だけを使います。`create-if-absent`でもadmission時に`present`だったseedはread-onlyで、`preserve-only`ではmissing seedを作成しません。

### I392-RQ-005 — Exact-clean 0.2.3 migration

Designのclosed fixtureに一致する`0.2.3`だけをmigration対象とします。四roots・二slots・legacy recordのentry inventory、type、mode、content/targetのいずれかが異なる場合はpre-mutationで拒否します。seedsとprotected dataはfixture admissionに使用せず、そのbytes/type/inodeを不変に保ちます。初回migrationは`E384-DEC-001`のhuman maintenance windowを前提とし、external 0.2.4 installerだけを使用します。

### I392-RQ-006 — Private authorityとpreparation recovery

Private namespaceはConsumer外、repository parentと同一filesystem、effective user owner、mode0700、no-followです。Durable prepared ACTIVEより先にstage payloadまたはConsumer mutationを作成しません。

これらのowner/mode/binding checksはOS credential boundaryと協調commandを前提にし、同一EUIDの非協調actorに対する作成者証明や非干渉性を意味しません。観測できたunsafe type、permission failure、binding driftは既定どおりpreserve-and-blockまたはWire-defined recoveryへ収束します。

Private metadataとそのatomic tempはmode0600、private directoryはmode0700です。例外の`RECORD-TEMP`はexact expected public record、またはexchange後にACTIVEのoriginal-record witnessへ一致する旧public recordだけをmode0644で保持します。Foreign substitutionはcontent-equalでもpreserve-and-blockします。

- P0: initial private authorityを信頼可能にできない。operation/digest/policy null、retryなし、Consumer mutation false。
- P1: prepared ACTIVEはdurableだがstageがabsent/incomplete。registered fixed stage entryだけ再構築できます。
- P2: stage ownerと全stage payloadがdurable。再入場はstageを再検証・再利用し、stage書込みを繰り返しません。
- Initial record publication後はACTIVEを`running`へdurableに更新してからroot mutationへ進みます。
- Target verification後はACTIVEを`ready`へdurableに更新してからterminal recordを公開します。
- Terminal record成立後だけ`terminal-cleanup`へ遷移し、stage removal、receipt publication、ACTIVE unlinkを順に行います。

### I392-RQ-007 — Native atomic filesystem safety

Linuxは`renameat2`の`RENAME_NOREPLACE`/`RENAME_EXCHANGE`、macOSは`renameatx_np`の`RENAME_EXCL`/`RENAME_SWAP`をdescriptor-relativeに使用します。native primitiveが利用不能ならWireのclosed failureへ停止し、unlink-then-rename、copy fallback、path-only mutationを使用しません。全authority pathはno-follow、same-filesystem、identity再検証、hard-link/special-type拒否を満たします。これは通常障害と観測済みbinding driftへのfail-closed処理であり、一般のhostile-filesystem guaranteeではありません。

### I392-RQ-008 — Fixed publication and detach order

Install/updateは`docs → templates → system → scripts → slot spec-dock → slot spec-dock-grill-with-docs → seed(s) → verify → terminal record`の順です。Uninstall applyは`docs → templates → system → scripts → slot spec-dock → slot spec-dock-grill-with-docs → verify → tooling-absent record`の順です。四roots全体の一括atomicityは約束せず、各境界をACTIVE/stageからforward recoveryします。

### I392-RQ-009 — Tooling-only uninstall

Defaultはdry-runです。Applyは四roots・二slotsだけをdetachし、shared containerと`tooling-absent-preserved-data` recordを残します。`--remove-specs`はtarget/private state観測前の`invalid-request`/`spec-history-purge-removed` trapとしてexit 2、mutation 0です。旧purge authorityを復活させません。

### I392-RQ-010 — Closed public wire

全public result/action/text/JSON/exitはWire v12のfinite tableからのみ構築します。未列挙relation、free-form reason、catch-all、dictionary/filesystem orderは実装 defectとして失敗させます。40 public goldensと4 durable record goldensはbyte-preservingです。

### I392-RQ-011 — Runtime pre-import admission

`spec-dock/scripts/spec-dock`はstdlib-only frozen bootstrapとして、bytecode writeを無効化し、repository rootをno-followで開き、`flock(LOCK_SH|LOCK_NB)`を取得し、strict ready recordとfixed roots/slots/markersを検証した後にだけ`spec_dock_runtime`をimportします。busy、coordination unavailable、unsafe binding、not-readyはWIR-COORD-004のexact one-line stderr、empty stdout、exit 1です。

### I392-RQ-012 — Installer exclusive admissionとterminal exec

Parser error、removed purge trap以外のinit/init-force/update/uninstall（dry-run、cleanup replayを含む）は、target/private observation前に`flock(LOCK_EX|LOCK_NB)`を取得します。repo-local update/uninstallは、primitive external requestをbootstrapへ返し、全managed writerをreapしてAのleaseを閉じてから`exec`します。外部installerはBを独立再admitし、stdout/stderr/statusを直接伝達します。`uvx`不在はfrozen bootstrapだけがexact exit 127 diagnosticを出します。

### I392-RQ-013 — Managed helper lifetime

Repositoryへ書くmanaged Git/helper processには、必要なrepository lease fdだけを`pass_fds`で渡します。child helperはdevice/inodeを検証し、書込みdescendantの最後までfdを保持します。親だけをSIGKILLしてもinstaller EXはhelper終了までbusyです。明示的`LOCK_UN`、unrelated childへのfd leak、detached unprotected writerを禁止します。

### I392-RQ-014 — Same-generation checkout

Issue start/managed active checkoutはtarget refをcommitへpinし、target commitのprovider closureが現在admit済みgenerationと一致する場合だけcheckoutします。existing branchはclean、他worktree未checkout、merge/rebase/cherry-pick等の通常guardを通します。new branchはpin済みcurrent HEADから作成します。pre-check mismatch/unprovableは`runtime-generation-change-blocked`、post-checkout driftは`runtime-generation-drift`としてactive/sync前に停止し、実際のbranch副作用を報告してauto rollbackしません。

### I392-RQ-015 — Effective Git capability guard

Checkout/worktree materializationへ影響する`post-checkout`、`reference-transaction`、`post-index-change` hook、`core.hooksPath`、fsmonitor、clean/smudge/process filter、attributes、working-tree encoding、EOL conversion、textconv、sparse checkout、submodule、case/path collisionを実効値で検査します。設定を無断でdisableせず、同一bytesを証明できない状態はpre-mutationで拒否します。

### I392-RQ-016 — Worktree B create/remove

Createはsource commit/closureをpinし、empty Bをexclusive createしてB EXを取得し、public entrypointを保留したままGit worktree metadata/indexとpayloadをmaterialize・検証し、`spec-dock/scripts/spec-dock`をsame-directory atomic no-replaceで最後に公開します。RemoveはB EXをdestructive Git/helperとpost-cleanup終端まで保持します。former pathへdifferent-inode Cが出現した場合はCを保存し、`post_remove_cleanup_failed`を返してauto cleanup/rollbackしません。

### I392-RQ-017 — Consumer make hook terminal handoff

`make -n init`と`make init`はいずれもarbitrary consumer codeです。B publication後、B EX保持中に別open-file-descriptionのnonlocking B fdを取得・再検証し、全A/B locking fdを閉じた後、そのoriginal-B fdをcwdとしてfrozen bootstrapが実行します。Cへredirectせず、nested installerは通常admissionを使います。`skipped|detection_failed|succeeded|failed`、warning、outer exit 0の現行互換を維持し、hook後のreadyを再認証したとは表現しません。

### I392-RQ-018 — Provider-first、packaging、dogfood

まず`src/spec_dock/`とprovider assetsを完成させ、source testsをGREENにします。`spec-dock/system/.runtime`をsource candidateにも含めるため、provider-owned `src/spec_dock/assets/spec_dock/system/.runtime/README.md`を追加し、wheel/sdistでは対応するhidden package-data pathを明示的に含めます。Candidate algorithmとT13 node identityは変更しません。次にwheel/sdist/isolated installed resourcesで同じcandidate/fixture/bootstrap bytesを証明し、最後に`spec-dock/`と二skillのchecked-in dogfood mirrorをbyte-for-byte同期します。dogfoodを先行正本にしません。

### I392-RQ-019 — Old writer/test retirement

新保証のRED→GREEN証拠が揃う前に旧testを削除しません。揃った後、旧production writer、旧manifest、旧journal/retry interpretation、obsolete-only testを撤去します。削除済みimplementationやobsolete behaviorの不在だけを確認する永続testは残しません。T12はcurrent public CLIの結果・保護動作を検証し、実装削除は差分/code reviewで確認します。T14のretirement-classification-only testも残しません。実際のprotected-data保全やremoved purge requestのmutation-zeroは現行安全契約なので保持します。Four required-fast nodes、resolved successor、14 active baseline nodes、current provider CI/full verifierは維持します。

脅威範囲の変更により要件でなくなった`test_t06_bootstrap_creation_replacement_is_not_populated`はPlanの指定checkpointで削除し、out-of-scope状態だけを確認する後継testは作りません。EEXIST collision、観測されたwitness/binding drift、既存bootstrapの再bindを扱う別testは、それぞれの残る契約を検証するため保持します。

### I392-RQ-020 — P392、B1/B2 acceptanceと順序

#392 candidateでは#392所有のfocused Linux/macOS、default fast、required PR checks、packaging、dogfood、baseline integrityをGREENにし、current full verifierも実行します。#395所有active rowsの測定済みviolationだけが残る場合に限りhuman merge後のtipをP392とし、exact SHAとviolation-row対応を記録します。それ以外のfailureはmerge blockerです。P392はB1/Issue受入ではありません。#395はそのexact tipから修復し、merge後同一tipでB1（current required/full gates GREEN）とB2（15/0/15）を確認します。#392はB1後、#395はB2後に受入・closure可能です。

## 7. Acceptance criteria

| AC | 完了時に観測する事実 | 主なtest/evidence |
|---|---|---|
| AC-01 | Public init/update/uninstallがcurrent lifecycle contractどおりに動作する。旧writer/manifest removalは候補差分とcode reviewで確認し、absence-only regression testは残さない。 | T07、T12、source diff review |
| AC-02 | Candidate/record/marker/legacy fixtureがclosed formatとexact bytesを満たす。 | T01、T02 |
| AC-03 | Protected sentinelのbytes/type/device/inodeが全normal/fault caseで不変。 | T03、T06、T07、T13 |
| AC-04 | P0/P1/P2、全root/slot/record/receipt faultがWireのexact result/retryへ収束。 | T04、T05、T06 |
| AC-05 | Linux/macOS native atomic/no-follow/identity-drift proofが実platformでGREEN。 | T05、provider-ci matrix |
| AC-06 | Runtime pre-import SH、installer EX、two-SH coexistence、parent-only SIGKILL lifetimeが実processでGREEN。 | T08、T09 |
| AC-07 | Wrapper A→B/B→A、全retained flag、stream/status/127、no old-module returnがGREEN。 | T09 |
| AC-08 | Existing/new checkout、effective Git guard、pre/post driftがexact envelopeでGREEN。 | T10 |
| AC-09 | Worktree B create/remove、entrypoint-last、C reuse、consumer hook handoffがGREEN。 | T11 |
| AC-10 | Exact clean 0.2.3だけがmigrationし、保護データを維持し、purge requestはexit 2/mutation 0。 | T02、T07 |
| AC-11 | Source/wheel/sdist/isolated install/fresh install/dogfoodが同candidate、fixture、bootstrap、skills、docsを持つ。 | T13 |
| AC-12 | Four required-fast、15/14/1 register、resolved successor、243 timing entries、policyが不変。full verifier実測はP392記録に分離する。 | T14、P392 receipt |
| AC-13 | PR base、human merge、P392記録、B1/B2 same-tip verificationがIntegration Contractどおり。 | human gate receipt |
| AC-14 | Product test/merge未実行の時点ではReportが成功を主張せず、実装開始許可はfalse。 | document review |

## 8. Requirement-to-test trace

| Test ID | Scope |
|---|---|
| T01 | Wire inventory、relation constructor、record/marker parse/serialize、golden bytes。 |
| T02 | Candidate digest、legacy fixture generator/source、source/wheel/sdist identity。 |
| T03 | Fixed authority、seed immutability、protected/unknown preservation。 |
| T04 | Private namespace、ACTIVE/stage/receipt schemas、P0/P1/P2 re-entry。 |
| T05 | Linux/macOS native atomic Adapter、no-follow、same-filesystem、identity drift。 |
| T06 | Ordered engine fault campaign、root/slot/record/cleanup/receipt forward recovery。 |
| T07 | Exact legacy migration、tooling-only uninstall、purge trap、old-package mutation-zero。 |
| T08 | Frozen bootstrap、pre-import SH、busy/not-ready/unsafe/unavailable diagnostics。 |
| T09 | Installer EX、managed helper lifetime、wrapper release-to-exec、stream/status/127。 |
| T10 | Pinned existing/new checkout、effective Git capability guard、post-drift behavior。 |
| T11 | Worktree B create/remove、entrypoint-last、path C、consumer hook terminal handoff。 |
| T12 | Public init/uninstall CLI outcomes、current wire compatibility、protected-data preservation。 |
| T13 | Source/wheel/sdist/isolated installed package/fresh install/dogfoodのcandidate、fixture、bootstrap、docs、skills parityとprotected data。 |
| T14 | Required-fast、15/14/1、243 entries、current policy continuity、#395/#396 boundary。Retirement-only classification assertionは含めない。 |

詳細なKEEP/REPLACE/RETIRE分類は[ライフサイクルのテスト所有と移行対応](artifacts/20260908t011846z-01-lifecycle-test-ownership-and-migration.md)、checkpointの実行順は[実装計画](plan.md)、一回に一checkpointだけ渡すpacketは[Luna Max実装引継ぎ](artifacts/20260908t011846z-luna-max-implementation-handoff.md)を参照します。

## 9. Stop conditions

次のいずれかを観測したら、実装者はfallback、skip、別code、別schemaを発明せず停止します。

- Wire v12のfield/code/relation/orderでは実在failureを表現できない。
- Candidate digestまたはlegacy fixtureの正本sourceが一意に固定できない。
- Native atomic primitiveをLinux/macOSの実platformで証明できない。
- Private namespaceをsame-filesystem、owner-bound、no-followで確立できない。
- 14 active row、required-fast、resolved successor、243 timing entriesの変更が必要になる。
- #395のfailure repairまたは#396のfinal gate実装が必要になる。
- Consumer data、unrelated skill、existing seedへmutationが必要になる。
- Checkout/worktreeで通常のGit safetyを迂回しなければ同世代を証明できない。
- Source/wheel/sdist/installed/dogfoodのcandidate identityが一致しない。

## 10. 完了と人間gate

仕様作成完了、再開許可、Product実装完了、PR merge、B1 GREEN、Issue closureは別の状態です。CP1–CP4 candidateとそのテスト・package/dogfood/current-gate検証はsafe stop前に実施済みですが、最終受入されていません。Option 1反映後の独立review、clean pushed freeze/projectionおよび親gateは未完了です。したがって現在は`実装開始許可: false`を維持し、G0後はPlanの限定re-entryを行います。

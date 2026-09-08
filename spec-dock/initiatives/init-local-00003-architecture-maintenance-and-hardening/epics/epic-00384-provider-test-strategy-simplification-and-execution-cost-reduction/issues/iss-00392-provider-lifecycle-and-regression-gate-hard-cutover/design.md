---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "approved"
詳細化状態: "independent-review-passed"
最終更新: "2026-09-08"
依存:
  - "requirement.md"
  - "artifacts/20260908t011846z-01-lifecycle-test-ownership-and-migration.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: true
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "dc638e936e763cc7a6087f258201ed9ed654e7fb"
  tree: "17ce38234033393c385c4b17e40c0ccdc78bfc19"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. 設計結論

現行`src/spec_dock/managed_distribution.py`のper-file plan/journal/reconciliationを縮小改造しません。新しい`src/spec_dock/provider_lifecycle/`をsole lifecycle writerとして追加し、public route、runtime coordination、Git/worktree coordination、packaging/dogfoodが新境界へ移った後、旧moduleと`src/spec_dock/assets/managed_distribution.json`を同じIssueで削除します。

外部公開値は親Wire v12から生成・検証し、private schemaとcandidate/legacy encodingだけを本Designで固定します。Productionは親Markdownをruntimeで読みません。Development generatorがWireのfinite tableを`_wire_generated.py`へ投影し、testが親Artifactから再生成して差分0を要求します。これにより実装表は存在しますが、normative authorityは親Wire一つのままです。

## 2. Verified current state

verified commitで確認した主要接点は次のとおりです。

| Existing path / symbol | 観測した現在の責務 | #392での扱い |
|---|---|---|
| `src/spec_dock/cli.py::_exclusive_distribution_operation` | blocking EX flockと旧root identity admission | 削除。新coordination Adapterのnonblocking EXへ置換。 |
| `src/spec_dock/cli.py::_admit_distribution_cli` | 旧manifest/record/journal admission | 削除。`provider_lifecycle.engine.execute_provider_lifecycle`へ集約。 |
| `src/spec_dock/cli.py::_execute_fresh_distribution_unlocked` | 旧fresh service route | 削除。 |
| `src/spec_dock/cli.py::_install_recognized_distribution_unlocked` | 旧recognized service route | 削除。 |
| `src/spec_dock/cli.py::_run_uninstall_deprovision` | typed resultへ旧deprovision route | 削除。新tooling-only uninstallへ置換。 |
| `src/spec_dock/cli.py::_run_uninstall_explicit_spec_history_purge` | `--remove-specs` purge route | 削除。request trapへ置換。 |
| `src/spec_dock/managed_distribution.py` | 旧catalog、per-file plan、journal、recovery、deprovision、native rename | 全削除。ただしnative syscallの実装知見は新Adapter testへ移す。 |
| `src/spec_dock/assets/managed_distribution.json` | 0.2.3 anchorと大量obsolete exact files | 全削除。closed legacy fixtureへ置換。 |
| `src/spec_dock/assets/spec_dock/scripts/spec-dock` | `Path.resolve()`後、module存在確認、runtime import | 同pathをfrozen pre-import bootstrapへ全面置換。 |
| `spec_dock_runtime/commands/contracts.py::CommandOutcome` | `exit_code`と`CliText`のみ | terminal directiveを表せるclosed outcomeへ拡張。 |
| `spec_dock_runtime/cli/dispatch.py::dispatch` | command実行後、その場でstream emit | emitをbootstrapへ返す形へ変更。 |
| `spec_dock_runtime/commands/update.py::_run_update` | old module内で`subprocess.run(uvx...)` | primitive installer exec requestを返す。 |
| `spec_dock_runtime/commands/uninstall.py::_run_uninstall` | old module内で`subprocess.run(uvx...)` | 同上。`--remove-specs`はparser/request error。 |
| `application/set_active.py::checkout_active_target` | branch名だけでexisting/new checkout | pinned commit/closure guardへ置換。 |
| `application/issue_lifecycle.py::issue_start` | deps→checkout→active→sync | pre/post generation guardを加え、drift後はactive/syncしない。 |
| `application/worktree.py::worktree_create` | worktree add後にuse-case内でmake | B EX、entrypoint-last、terminal hook requestへ置換。 |
| `application/worktree.py::worktree_remove` | Git remove後にpathnameでcleanup | B EX、original inode binding、C preservationへ置換。 |
| `infra/git_cli.py` | direct `subprocess.run`、branch名ベース | pinned argv、capability guard、managed helper/pass_fdsへ置換。 |
| `infra/make_cli.py::run_make_init_if_available` | path cwdでmake検出/実行 | frozen bootstrap用terminal hook runnerへ移し、このsymbolは削除。 |
| `tests/unit/infra/test_init_update.py` | lifecycleとruntime/docs/packaging/current gateが混在 | file丸ごと削除禁止。分類表どおりKEEP/REPLACE/RETIRE。 |
| `tests/unit/infra/test_managed_distribution.py` | 旧engine internalsへ密結合 | successor T01–T07 GREEN後にretire。 |
| `tests/cli_runtime/test_distribution_cutover.py` | 旧lifecycleとresolved skill-slot successorが混在 | successor nodeをKEEPし、obsolete-only nodeだけretire。 |

## 3. Target module topology

### 3.1 Installer package

| Status | Exact path | Exact production symbols / responsibility |
|---|---|---|
| NEW | `src/spec_dock/provider_lifecycle/__init__.py` | `execute_provider_lifecycle`、`RuntimeInstallationAdmission`だけを公開。内部classをre-exportしない。 |
| NEW | `src/spec_dock/provider_lifecycle/contracts.py` | immutable dataclass/literal: `LifecycleRequest`、`LifecycleResult`、`LifecycleAction`、`InstallationRecord`、`SkillSlotMarker`、`CandidateIdentity`、`RepositoryBinding`、`InodeWitness`、`ActiveState`、`CompletionReceipt`、`StageOwner`。 |
| NEW | `src/spec_dock/provider_lifecycle/_wire_generated.py` | Wire v12から生成したfinite enums、168 relation rows、message/guidance/action profiles、40 public goldens、4 record goldens。手編集禁止。 |
| NEW | `src/spec_dock/provider_lifecycle/wire.py` | `parse_installation_record`、`serialize_installation_record`、`parse_slot_marker`、`serialize_slot_marker`、`build_public_result`、`validate_public_result`。 |
| NEW | `src/spec_dock/provider_lifecycle/candidate.py` | fixed domain inventory、canonical digest、packaged candidate capture、slot marker injection、stage verification。 |
| NEW | `src/spec_dock/provider_lifecycle/legacy_fixture.py` | closed 0.2.3 fixture parser、exact legacy classifier、aggregate digest検証。 |
| NEW | `src/spec_dock/provider_lifecycle/private_state.py` | private namespace resolution、ACTIVE/receipt/stage owner strict parser/writer、re-entry classification、expected-byte unlink。 |
| NEW | `src/spec_dock/provider_lifecycle/filesystem.py` | descriptor-relative no-follow operations、Linux/macOS native rename Adapter、tree capture、identity verification、fsync。 |
| NEW | `src/spec_dock/provider_lifecycle/coordination.py` | `acquire_shared_repository_lease`、`acquire_exclusive_repository_lease`、`validate_inherited_repository_lease`、`RepositoryLease`。 |
| NEW | `src/spec_dock/provider_lifecycle/engine.py` | `ProviderLifecycleEngine.execute`とfixed operation sequence。public resultは必ず`wire.py`経由。 |
| MODIFY | `src/spec_dock/cli.py` | parser、request normalization、target label、new engine呼出し、public emitだけに縮小。 |
| DELETE | `src/spec_dock/managed_distribution.py` | 新route・tests・dogfoodがGREENになった後に削除。compat shimは残さない。 |
| DELETE | `src/spec_dock/assets/managed_distribution.json` | closed legacy fixtureへ置換後に削除。 |

### 3.2 Generated development inputs

| Status | Exact path | Contract |
|---|---|---|
| NEW | `scripts/maintenance/generate_provider_lifecycle_wire.py` | 親Wire v12だけをparseし、counts/order/JSON LFを検査して`_wire_generated.py`をdeterministic生成。Product runtimeからimportしない。 |
| NEW | `scripts/maintenance/generate_provider_lifecycle_legacy_fixture.py` | exact commitのGit objectsから0.2.3 fixtureを生成。working-tree bytesを入力にしない。 |
| NEW | `src/spec_dock/assets/provider_lifecycle/legacy-0.2.3.json` | exact-clean admissionの唯一のruntime fixture。compact JSON one LF。 |

### 3.3 Runtime package and dogfood

Provider asset側をCP3で完成させ、checked-in dogfood側はCP4のartifact proof後にcomplete candidateとして一括同期します。CP3でのpartial dogfood projectionは禁止します。以下で`<RUNTIME>`は`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime`、`<DOGFOOD>`は`spec-dock/scripts/spec_dock_runtime`です。表のProvider source列はCP3 ownership、Dogfood mirror列はCP4 projection対象です。

| Status | Provider source | Dogfood mirror | Responsibility |
|---|---|---|---|
| MODIFY | `src/spec_dock/assets/spec_dock/scripts/spec-dock` | `spec-dock/scripts/spec-dock` | frozen stdlib bootstrap、SH admission、ordinary emit、installer exec、consumer hook terminal runner。 |
| MODIFY | `<RUNTIME>/app.py` | `<DOGFOOD>/app.py` | `run(argv, bootstrap_context) -> RuntimeProgramOutcome`。stream emit/exec/hook実行をしない。 |
| MODIFY | `<RUNTIME>/cli/dispatch.py` | mirror | `dispatch`は`CommandOutcome`を返し、`_emit`を削除。 |
| MODIFY | `<RUNTIME>/commands/contracts.py` | mirror | `CommandOutcome`、`InstallerExecRequest`、`ConsumerHookRequest`、`RuntimeProgramOutcome`のclosed union。 |
| MODIFY | `<RUNTIME>/commands/update.py` | mirror | installer argvをprimitive requestとして構築。 |
| MODIFY | `<RUNTIME>/commands/uninstall.py` | mirror | retained flagsをprimitive requestへ変換。purgeをforwardしない。 |
| MODIFY | `<RUNTIME>/application/contracts.py` | mirror | `PinnedProviderClosure`、`PinnedCheckout`、`WorktreeCreatePreparedResult`、terminal hook envelopeを追加。 |
| MODIFY | `<RUNTIME>/application/ports.py` | mirror | GitGatewayをpin/closure/pass-fd APIへ変更。BootstrapGatewayを削除。 |
| MODIFY | `<RUNTIME>/application/set_active.py` | mirror | `checkout_active_target`をpinned checkoutへ置換。 |
| MODIFY | `<RUNTIME>/application/issue_lifecycle.py` | mirror | post-checkout closure再検証をactive/sync前へ挿入。 |
| MODIFY | `<RUNTIME>/application/worktree.py` | mirror | B create/remove coordinationとterminal hook request。 |
| MODIFY | `<RUNTIME>/infra/git_cli.py` | mirror | capability guard、managed helper、pin済みGit argv、worktree no-checkout/materialization。 |
| NEW | `<RUNTIME>/infra/git_helper.py` | mirror | inherited lease fdを検証し、Git writing descendantの終端まで保持。 |
| MODIFY | `<RUNTIME>/infra/make_cli.py` | mirror | use-case gatewayを削除し、hook argv/status判定のpure helperだけを残す。実processはbootstrapが実行。 |

## 4. Fixed domains and candidate digest

### 4.1 Domain order

Candidate domain orderは次の6件に固定します。

1. `root:spec-dock/docs`
2. `root:spec-dock/templates`
3. `root:spec-dock/system`
4. `root:spec-dock/scripts`
5. `slot:.agents/skills/spec-dock`
6. `slot:.agents/skills/spec-dock-grill-with-docs`

Source mappingは、rootsを`src/spec_dock/assets/spec_dock/<root-name>`、slotsを`src/spec_dock/assets/install_root/<slot-path>`から取得します。Candidateはinstalled package resourceをno-followでcaptureし、source checkout fallbackを認めません。

### 4.2 Canonical digest stream

Candidate digestは次のbyte stream全体のSHA-256です。文字列はUTF-8、整数modeは4桁lowercase octal、pathはPOSIX、NULを拒否します。

```text
"spec-dock-fixed-provider-candidate-v1\0"
"0.2.4\0"
for domain in fixed-domain-order:
  "DOMAIN\0" + domain-kind + "\0" + public-root-path + "\0"
  for entry in descendant-relative-path UTF-8 byte order:
    directory: "D\0" + relative-path + "\0"
    regular:   "F\0" + relative-path + "\0" + mode + "\0" + sha256(file-bytes) + "\0"
    symlink:   "L\0" + relative-path + "\0" + raw-link-target + "\0"
```

Rules:

- Root自身は`DOMAIN`行で表し、empty directoryは`D`行で表します。
- Regular modeは`0644`または`0755`のみ。現在のpublic entrypointは`0755`です。
- Symlink targetはrelative、NULなし、lexical escapeなし。unsupported/special entryは`candidate-invalid`です。
- `.spec-dock-provider-slot.json`はdigest計算後に注入するため除外します。
- `spec-dock/spec-dock.version`、private state、seed、Git metadata、inode、ctime、mtimeは除外します。
- 同じalgorithmをsource、wheel、sdist、isolated installed package、Git provider closureで使用します。
- `spec-dock/scripts/spec-dock`はscripts domainに含まれます。bootstrap自身へcandidate digest literalを埋め込みません。

`CandidateIdentity`のexact fields/orderは`schema_version=1,version,aggregate_digest,domains`です。`domains`は上記順のexact six objectsで、各objectは`kind,path,tree_digest,entry_count`です。

## 5. Public installation record and skill marker

### 5.1 Installation record

`spec-dock/spec-dock.version`はWire v12のexact seven-key compact JSONです。key orderは次のとおりで、追加keyを禁止します。

1. `schema_version`
2. `state`
3. `operation`
4. `version`
5. `candidate_digest`
6. `seed_policy`
7. `skill_slots`

`skill_slots`のnested key orderは`spec-dock`、`spec-dock-grill-with-docs`です。UTF-8、compact separators、one LF、max4096、regular/link1/mode0644です。Public-record staging `RECORD-TEMP`は最終public mode0644でcreate/write/fsyncし、private namespace内でwitnessをdurable化してからrecord parentへnative rename/exchangeします。Rename/exchangeがmode0644を保存し、record parent fsync後に成立します。Publicへmode0600で公開してからchmodする遷移は禁止します。

### 5.2 Slot marker

各slot root直下に`.spec-dock-provider-slot.json`を置きます。exact key orderは`schema_version,slot,version,candidate_digest`、schema1、version0.2.4、max2048、regular/link1/mode0644、one LFです。`slot`は各exact slot path basenameではなく、exact public slot path文字列を使用します。

Markerがmissing、invalid、別slot、別version、別digest、symlink、hard linkの場合、そのslotはprovider authorityを証明しません。他slotや`.agents/skills`親をscanしません。

## 6. Exact-clean 0.2.3 legacy fixture

### 6.1 File and source

Runtime fixtureは`src/spec_dock/assets/provider_lifecycle/legacy-0.2.3.json`です。生成元はrepository `chemitaro/spec-dock`、commit `dc638e936e763cc7a6087f258201ed9ed654e7fb`のGit objectsです。このcommitの`spec-dock/spec-dock.version`はexact bytes `0.2.3\n`です。

Generatorは次のsource pathだけを読みます。

- `src/spec_dock/assets/spec_dock/docs`
- `src/spec_dock/assets/spec_dock/templates`
- `src/spec_dock/assets/spec_dock/system`
- `src/spec_dock/assets/spec_dock/scripts`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs`
- `spec-dock/spec-dock.version`

`git ls-tree -rz -t <commit> -- <paths>`と`git cat-file --batch`を使用し、working tree、build directory、dogfood mutation、networkを入力にしません。Commit、source path、mode、blob bytesが一つでも取得不能なら生成失敗です。

### 6.2 Closed fixture schema

Top-level exact key order:

1. `schema_version` = 1
2. `legacy_version` = `0.2.3`
3. `source_repository` = `chemitaro/spec-dock`
4. `source_commit` = verified 40-hex
5. `version_record`
6. `domains`
7. `aggregate_digest`

`version_record` exact keys: `path,kind,mode,sha256,bytes_base64`。`path`は`spec-dock/spec-dock.version`、`kind=regular`、`mode=0644`です。

`domains`はfixed domain orderの6 objectsです。各object exact keys: `kind,path,source_path,tree_digest,entries`。`entries`はcandidate digestと同じpath orderで、exact unionです。

- Directory: `kind,path`
- Regular: `kind,path,mode,sha256`
- Symlink: `kind,path,target`

Legacy aggregate digestはcandidate encodingと同じentry grammarを使用し、magicを`spec-dock-exact-legacy-fixture-v1\0`、versionを`0.2.3\0`とします。

### 6.3 Admission

Legacy recordと六domainのinventory/type/mode/content/targetがfixtureへexact一致した場合だけ`legacy-0.2.3`です。Extra descendant、missing descendant、mode drift、modified file、foreign slot marker、root/slot symlinkは`modified-legacy-workspace`または既存specific safety codeです。Seeds、initiatives、active、`.agent`、diagrams、`.workbench`、unknown siblingsはfixtureへ含めず、legacy admissionで読まないかroot-level preservation witnessに限定します。

## 7. Private namespace

### 7.1 Physical path

Bound repository rootのlexical parentをno-followで開き、parentとrepository rootの`st_dev`一致を要求します。Private pathは次のexact functionです。

```text
repository_key = sha256(compact-json-without-LF(
  ["spec-dock-repository-key-v1", root.st_dev, root.st_ino, effective_euid]
))
namespace = <repository-parent> /
  ".spec-dock-provider-lifecycle-v1-euid-<decimal-euid>" /
  repository_key
```

Top directoryとrepository-key directoryはowner=euid、mode0700、directory、no symlink、same deviceです。Createはexclusive mkdir→parent fsync→reopen/rebindです。Parentがwritableでない、別filesystem、owner/mode/type unsafeの場合はP0またはspecific stage-owner safety failureです。`/tmp`、home cache、environment override、fallback pathを使用しません。

Top directory内の他repository keyをlist/scanしません。Exact repository-key directory内は次のfixed entriesだけを許可します。

- `ACTIVE.json`
- `ACTIVE.json.tmp`
- `CLEANUP-COMPLETED.json`
- `CLEANUP-COMPLETED.json.tmp`
- `RECORD-TEMP`
- `STAGE`

Unknown entryはpreserve-and-blockです。Entry modeは次のclosed matrixです。

| Class | Exact entries | Type/owner/mode |
|---|---|---|
| Private metadata | `ACTIVE.json`、`CLEANUP-COMPLETED.json`、`STAGE/STAGE-OWNER.json` | regular/link1/owner euid/mode0600 |
| Private metadata atomic temp | `ACTIVE.json.tmp`、`CLEANUP-COMPLETED.json.tmp` | regular/link1/owner euid/mode0600 |
| Public-record staging | `RECORD-TEMP` | regular/link1/owner euid/mode0644/max4096 |
| Private directories | repository namespace、`STAGE` | directory/owner euid/mode0700 |

`RECORD-TEMP`はexact expected seven-key public record、またはexchange後にACTIVEのoriginal-record bytes/hash/inode witnessへ一致する旧public recordだけを許可します。Content-equalなforeign inodeを採用せずpreserve-and-blockします。Unsafe objectを削除して進みません。

### 7.2 Repository and tuple identities

```text
tuple_key = sha256(compact-json-without-LF(
  ["spec-dock-lifecycle-tuple-v1", operation, candidate_digest, seed_policy]
))
operation_generation = 128-bit cryptographic random, 32 lowercase hex
cleanup_token = Wire v12 WIR-INV-001 formula
```

Generationはfresh operationごとに新規作成し、resumeでは維持します。同じtupleでもtokenは異なります。

## 8. Closed private schemas

すべてcompact JSON、UTF-8、one LF、duplicate/unknown/missing key拒否です。Integerは非負、booleanとの混同を拒否します。

### 8.1 `InodeWitness`

Exact key order:

1. `kind`: `regular|directory`
2. `device`
3. `inode`
4. `ctime_ns`
5. `mode`
6. `link_count`
7. `size`: regularはinteger、directoryはnull
8. `sha256`: regularは64-hex、directoryはnull

Authority fileはregular/link1、authority directoryはdirectoryです。Pathは外側のclosed fieldが持ち、witness自身にabsolute pathを入れません。

### 8.2 `ACTIVE.json`

max32768、mode0600。Top-level exact key order:

1. `schema_version` = 1
2. `state`: `prepared|running|ready|terminal-cleanup`
3. `repository_key`
4. `repository_identity`: exact keys `device,inode,euid`
5. `tuple_key`
6. `operation_generation`
7. `operation`: `install|update|uninstall`
8. `candidate_digest`
9. `seed_policy`
10. `result_family`: `install|legacy-migration|update|uninstall`
11. `original_record`
12. `expected_incomplete_record`
13. `bootstrap_container`
14. `owned_target_witnesses`
15. `registered_stage_entries`
16. `record_temp_witness`
17. `terminal_record_digest`
18. `cleanup_token`
19. `cleanup_retry_invocation`
20. `deferred_invocation`

Nested exact schemas:

- `original_record`: `kind,bytes_base64,sha256,witness`。`kind=absent|legacy-0.2.3|final`。Absentでは後三件null、他はnon-null。
- `expected_incomplete_record`: `bytes_base64,sha256`。
- `bootstrap_container`: `disposition,witness`。`disposition=existing|planned-create|created`。planned-createだけwitness null。
- `owned_target_witnesses`: fixed six objects、domain order。各object exact keys `path,original_kind,original_tree_digest,original_inode,terminal_kind,terminal_tree_digest`。Kindは`absent|directory`、対応しないdigest/inodeはnull。
- `registered_stage_entries`: fixed six objects、domain order。各object exact keys `name,target_path,candidate_tree_digest,original_tree_digest`。`name`は`docs|templates|system|scripts|slot-spec-dock|slot-spec-dock-grill-with-docs`。
- `record_temp_witness`: nullまたは`InodeWitness`。Publish前はmode0644のexact expected record staging inodeを表します。Exchange後はmode0644で戻った旧public recordをACTIVEの`original_record` witnessと照合してexpected-bound unlink/fsyncするまで表します。No-replace後はabsentを確認します。Foreign/content-equal別inodeは採用せず、record parent fsyncとresidue cleanup後にnullへ戻します。
- `terminal_record_digest`: operation admission時に決定したexact expected terminal record bytesのSHA-256。
- `cleanup_retry_invocation`: exact keys `role,invocation_id,cleanup_token,rendered_command`。`role=cleanup-retry`。
- `deferred_invocation`: nullまたはexact keys `invocation_id,rendered_command`。

State invariants:

| State | Required invariant |
|---|---|
| prepared | Consumerはoriginal stateまたはown expected incomplete + unpublished roots。Stageはabsent/incomplete/completeのいずれか。root mutationは禁止。 |
| running | Expected incomplete recordとparent fsyncが成立。Fixed sequenceのtarget/stage配置から次phaseを推定する。 |
| ready | 全terminal target content検証済み。Terminal recordは未公開またはmatching。 |
| terminal-cleanup | Matching terminal recordあり。Lifecycle dispatchは禁止し、cleanup/receiptだけを実行。 |

ACTIVEはrootごとのmutable checkpointを持ちません。Progressは、各fixed targetと対応するfixed stage entryがcandidate/original/absentのどれに一致するかを再検証して一意に導きます。これによりper-file journalを復活させません。

### 8.3 `STAGE/STAGE-OWNER.json`

`STAGE`内のfixed entriesは`STAGE-OWNER.json`と上記6 domain namesだけです。Owner fileはmax8192、mode0600、exact key order:

1. `schema_version` = 1
2. `repository_key`
3. `tuple_key`
4. `operation_generation`
5. `operation`
6. `candidate_digest`
7. `seed_policy`
8. `result_family`
9. `entry_names`: exact six names/order
10. `candidate_domain_digests`: exact six 64-hex/null values
11. `original_domain_digests`: exact six 64-hex/null values

Install/update stage entryは公開前candidate、exchange後old rootを保持します。Uninstall stage entryはdetach前absent、detach後old rootです。P1だけ、safely bound registered entryを削除・再作成してstageを再構築できます。`STAGE-OWNER.json`と全required entryがdurableかつdigest一致するP2では、stageへ一byteも再書込みせず再利用します。

### 8.4 `CLEANUP-COMPLETED.json`

Wire v12 WIR-CLEANUP-002のexact 12 keysだけを持ちます。

`schema_version,repository_key,tuple_key,operation_generation,operation,candidate_digest,seed_policy,result_family,terminal_record_digest,cleanup_token,cleanup_retry_invocation,deferred_invocation`

max16384、mode0600。Stage removal/fsync後にreceiptをatomic publish/fsyncし、その後ACTIVEをexpected-byte unlink/fsyncします。Receiptだけのtoken replayはConsumerもreceiptも変更しません。新no-token mutationがcomplete admissionを通った直後、new ACTIVE前にだけold receiptをexpected-byte unlinkします。

## 9. Engine state machine and write order

### 9.1 Common admission

1. Parserでinvocationをnormalizeする。
2. Parser errorと`--remove-specs` trapを処理する。
3. Repository rootをno-followでopen/bindし、installer EXをNB取得する。
4. Private receipt/ACTIVEをexact pathで解決し、terminal cleanup/replayを先に処理する。
5. Target record、fixed domains、seeds/protected boundariesをnonmutating分類する。
6. Packaged candidateをcaptureし、candidate digestとslot markersを構築・検証する。
7. Operation、seed policy、result family、tuple、terminal record bytesを決定する。
8. New mutation admission時だけold completion receiptをinvalid化する。
9. ACTIVE preparedをatomic publish/fsyncする。
10. Stageを構築・fsyncする。P2 re-entryでは構築しない。

### 9.2 Install/update/migration

1. Absent toolingで必要なら`spec-dock` containerをbounded create/fsyncし、ACTIVEのbootstrap witnessを`created`へ更新する。
2. `RECORD-TEMP`をmode0644で作成し、expected incomplete recordを書いてfsyncし、そのwitnessをACTIVEへdurableに記録する。
3. Native no-replace/exchangeでrecordを公開し、mode0644とrecord parentをfsync・再検証する。No-replace後はtemp absent、exchange後はACTIVEのoriginal-record witnessへ一致する旧recordだけをexpected-bound unlink/fsyncし、foreign substitutionはpreserve-and-blockする。
4. ACTIVEを`running`へatomic publish/fsyncする。
5. `docs`をpublish/exchangeし、target/stage parentsをfsync・再検証する。
6. `templates`、`system`、`scripts`の順に同じ処理をする。
7. `slot-spec-dock`、`slot-spec-dock-grill-with-docs`の順に処理する。
8. `create-if-absent`の場合だけ`.gitignore`、consumer CIをnative no-replaceで作成する。既存ならbytesを読まずpreserved actionとする。
9. Six domains、markers、record relation、protected root witnessesを検証する。
10. ACTIVEを`ready`へpublish/fsyncする。
11. Mode0644の`RECORD-TEMP`からterminal ready recordをpublish/fsync・再検証し、exchange後の旧record residueを同じwitness規則でcleanupする。
12. ACTIVEを`terminal-cleanup`へpublish/fsyncする。
13. Registered stage entriesとSTAGEをremove/fsyncする。
14. Completion receiptをpublish/fsyncする。
15. ACTIVEをexpected-byte unlink/fsyncする。
16. Wire resultをemitする。

### 9.3 Uninstall apply

1. Tombstone STAGEをP1/P2規則で用意する。
2. Preserve-only incomplete uninstall recordをpublish/fsyncする。
3. ACTIVE running。
4. `docs`、`templates`、`system`、`scripts`をnative no-replace renameでSTAGEへdetachする。
5. 二slotsを同順でdetachする。
6. Six targets absent、seeds/protected state不変を検証する。
7. ACTIVE ready。
8. `tooling-absent-preserved-data` recordをpublish/fsyncする。
9. Terminal cleanup/receipt/ACTIVE unlinkを共通順で行う。

Dry-runはEX admissionと全read-only classificationを行いますが、ACTIVE、stage、record、receipt、seedを作成・更新しません。Prepared uninstallが存在するときだけ、original/expected-incompleteとstageをread-only検証してremaining planを返します。

## 10. Fault boundary and re-entry

### 10.1 P0/P1/P2

| Class | Durable state | Allowed next behavior |
|---|---|---|
| P0 | Trusted ACTIVEなし。Namespaceにsafe empty reservation/tempだけが残り得る。Consumer writeなし。 | I/O修復後、ordinary commandでfresh admission。Retry commandは返さない。 |
| P1 | ACTIVE preparedあり。STAGE absentまたはregistered entryがincomplete。Consumer writeなし。 | Exact tuple ordinary retry。Safe registered stage entryだけ再構築可。 |
| P2 | ACTIVE preparedあり。STAGE ownerと全stage payload durable。 | Exact tuple ordinary retry。Stage再検証・再利用のみ。Stage write禁止。 |
| P2a | Initial record pathはoriginal state、same-generation containerなし。 | blocked、empty actions、ordinary retry。 |
| P2b | Own containerまたはown expected incomplete recordがvisible/durable。 | partial_failure、AP-PREP-PARTIAL、ordinary retry。 |

### 10.2 Fixed fault points

Fault injectorは次のoperation IDだけを受け付け、Productにfree-form hookを残しません。

- `private-top-mkdir`、`private-top-fsync`、`private-repo-mkdir`、`private-repo-fsync`
- `active-temp-open/write/fsync/rename/parent-fsync`（prepared/running/ready/terminal-cleanup各transition）
- `stage-mkdir/owner-write/owner-fsync`、各six entryの`create/write/fsync`、`stage-parent-fsync`
- `bootstrap-container-mkdir/fsync`
- `record-temp-open/write/fsync`、`record-publish-no-replace|exchange`、`record-parent-fsync`、`record-exchange-residue-unlink`、`record-temp-parent-fsync`
- 各root/slotの`publish-or-detach`、`source-parent-fsync`、`target-parent-fsync`
- 各seedの`no-replace-create`、`parent-fsync`
- `target-verify`
- 各stage entry removal、`stage-remove`、`stage-parent-fsync`
- receiptの`temp-open/write/fsync/rename/parent-fsync`
- ACTIVEの`expected-unlink/parent-fsync`
- response emit直前の`response-loss`

各pointはbefore/after durable stateを別caseで検証します。Expected I/O failureだけをWire codeへmapし、assertion/programming errorを丸めません。

## 11. Filesystem Adapter

### 11.1 Shared interface

`NativeAtomicFilesystem`は次のexact methodsを持ちます。

- `open_directory_chain_no_follow(absolute_path) -> BoundDirectory`
- `capture_inode(parent_fd,name,expected_kind) -> InodeWitness|Absent`
- `capture_domain_tree(parent_fd,name) -> DomainTreeIdentity`
- `rename_no_replace(src_parent_fd,src_name,dst_parent_fd,dst_name)`
- `exchange(src_parent_fd,src_name,dst_parent_fd,dst_name)`
- `unlink_bound(parent_fd,name,expected_witness)`
- `remove_tree_bound(parent_fd,name,expected_tree)`
- `fsync_directory(fd)`

全methodはoperation直前・直後にfdとtarget witnessを再検証します。Rename/exchangeはsource inodeのmodeを変更せず、public record publicationでは前後ともmode0644であることをpostconditionに含めます。`Path.resolve`、recursive follow、absolute mutation pathを使いません。

### 11.2 Linux

`LinuxRenameAt2Adapter`はlibc `renameat2`を使用します。

- no-replace: `RENAME_NOREPLACE`
- exchange: `RENAME_EXCHANGE`

Symbol/flag/kernel supportがなければ`atomic-rename-unavailable`です。`os.rename`へのdowngrade、destination unlink、copytree fallbackは禁止です。

### 11.3 macOS

`MacOSRenameAtXAdapter`はlibc `renameatx_np`を使用します。

- no-replace: `RENAME_EXCL`
- exchange: `RENAME_SWAP`

Availabilityまたはflag support不成立は同じclosed failureです。`renamex_np`のpath-only fallbackは使用しません。

### 11.4 Unknown preservation

Fixed root/slot parentにunknown siblingがあってもlist/deleteしません。Exact targetだけをopenatします。Fixed root内部はauthority成立後root全体がdisposableですが、authority不成立なら内部scanによるadoptionをせず`foreign-tooling-root`/`foreign-skill-slot`へ停止します。Protected pathはroot-level witnessの比較だけで内容を取得しません。

## 12. Repository coordination and frozen bootstrap

### 12.1 Lease

Coordination objectはrepository root directory inodeです。`RepositoryLease`はroot fd、device、inode、mode、lease modeだけを保持します。

- Runtime: `LOCK_SH|LOCK_NB`
- Installer: `LOCK_EX|LOCK_NB`
- Release: fd closeだけ。`LOCK_UN`禁止。
- Contention判定前後にroot bindingを再検証。
- EAGAIN/EWOULDBLOCKだけbusy。
- Capability/system errorはcoordination unavailable。

`system/.runtime/create.lock`はSH lease内のcreate/import serializationとして維持可能ですが、cross-generation authorityには使用しません。

### 12.2 Frozen bootstrap control flow

`spec-dock/scripts/spec-dock`は次の順だけを実装します。

1. `sys.dont_write_bytecode=True`。
2. Script lexical locationからrepository rootをcomponent-wise `openat(O_DIRECTORY|O_NOFOLLOW)`する。
3. SH NB leaseを取得する。
4. Current `spec-dock.version`をdescriptor-relativeにstrict parseする。
5. `state=ready`、version/protocol 0.2.4、fixed domain/marker safe bindingを軽量検証する。Candidate全rehashはしない。
6. Runtime pathをcurrent filesystemから開き、`spec_dock_runtime.app.run`をimportする。
7. Ordinary outcomeではSHを保持したままstreamを出し、writer/helper終了後にcloseする。
8. Installer execまたはconsumer hook directiveではprimitive envelopeをcopyし、old moduleを以後呼ばず、lease close後にbootstrap自身がterminal actionを行う。

Bootstrap bytesは#392 acceptanceでsource/wheel/sdist/installed/dogfood間のSHA-256を固定します。#395/#396は変更不可です。

## 13. Terminal outcome design

### 13.1 Closed directive union

`CommandOutcome`はexact fields `exit_code,text,terminal`です。`terminal`はnullまたは次の一方です。

**InstallerExecRequest** exact fields:

`kind="installer-exec",argv,environment_policy`

- `argv`は既存固定upstream `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock ...`のstring array。
- `environment_policy="inherit-without-lock-bypass"`。
- fd/token/envによるtarget admission bypassを含めません。

**ConsumerHookRequest** exact fields:

`kind="consumer-hook",bound_cwd_fd,bound_device,bound_inode,detection_argv,execution_argv,result_format,result_payload`

- fdはB EXとは別open-file-descriptionで、flockしません。
- argvはそれぞれ`["make","-n","init"]`、`["make","init"]`。
- `result_format`は`worktree-create-text-v1|worktree-create-json-v1`。
- `result_payload`はhook前にmaterializeしたclosed worktree fieldsだけです。

### 13.2 Installer exec

Bootstrapは全managed helperをwait/reapし、A lease referencesをcloseしてから`os.execvpe`します。成功時はprocess imageが外部installerになり、old runtimeへ戻りません。失敗が`ENOENT`ならexact 127 diagnosticをbootstrapが出します。それ以外のexpected exec errorはcontent-free one-line error、untyped defectはtest failureとします。

### 13.3 Consumer hook

BootstrapはA/B locking fdを全closeし、nonlocking original-B fdを再`fstat`後、fork childで`fchdir`してmake detection/executionを行います。Pathを再resolveしません。Detectionでmissing init targetは`skipped`、make起動不能は`detection_failed`、init exit0は`succeeded`、nonzeroは`failed`です。結果はpre-materialized formatterで出し、outer exit 0を維持します。Hook後にruntime module、active、sync、lifecycleを呼びません。

## 14. Managed Git helper and effective capability guard

### 14.1 Helper lifetime

全writing Git argvは`python -m spec_dock_runtime.infra.git_helper`を介します。Parentは必要なA SH/B EX fdだけを`pass_fds`へ列挙します。Helperは次を行います。

1. fd number、expected device/inode、argvをprimitive引数で受ける。
2. 各fdを`fstat`し、directory、device/inode一致を検証する。
3. fdをinheritableのままGit childへ渡し、childをwait/reapする。
4. stdout/stderr/statusをcontent-preservingでparentへ返す。
5. 全writing descendants終了後にcloseする。

Unrelated read-only child、GitHub CLI、make hook、external installerへlease fdを渡しません。Parent-only SIGKILL testはreal helper processをpauseし、installer EXがbusyのままかを証明します。

### 14.2 Effective capability assessment

`GitCapabilityAssessment`はpin済みcommitとclosure pathsを入力に、次を検査します。

- repository/worktree clean status、unmerged index、merge/rebase/cherry-pick/revert/bisect state。
- branchがother worktreeでcheckout済みでないこと。
- defaultまたは`core.hooksPath`配下のexecutable `post-checkout`、`reference-transaction`、`post-index-change` hook不在。
- `core.fsmonitor`無効。
- sparse checkout無効、skip-worktree bit不在。
- `core.autocrlf=false`、`core.eol` unset、closureへの`eol`/`text`/`working-tree-encoding`/`ident`/`filter` attributeがunspecified。
- closureに対するclean/smudge/process filter、required filter、textconv、merge driverがeffectiveでない。
- target treeのclosure内にsubmodule mode160000がない。
- case-folding/Unicode normalization後のpath collisionがない。
- closure path/symlink targetがsafe relative POSIXである。

Target commit属性は`git check-attr --source=<pinned-sha> -z --all -- <closure paths>`で検査します。このoptionが利用不能ならgenerationはunprovableとしてblockします。設定を`-c`で上書き、hookをrename、filterをdisable、sparseを変更して通しません。

## 15. Pinned checkout

`PinnedCheckout` exact fields:

`target_branch,pinned_commit,before_branch,before_head,provider_closure_digest,checkout_kind`

`checkout_kind=existing|new`。

### Existing branch

1. branch refを`refs/heads/<name>^{commit}`へresolveしてpin。
2. clean/operation-state/other-worktree/capability guard。
3. pin済みcommitのprovider closureをGit object bytesから算出し、admitted generationへ一致確認。
4. `git update-ref refs/heads/<name> <pinned> <pinned>`で直前CAS確認。
5. normal `git switch <name>`をmanaged helperで実行。Git自体のguardを迂回しない。
6. HEAD/branch/closureを再検証。Pinned commit以外なら`runtime-generation-drift`。

### New branch

1. current HEADをpinし、current provider closureを再検証。
2. `git switch -c <name> <pinned-commit>`をmanaged helperで実行。
3. postconditionを同様に再検証。

Preflight failureはcheckout/active/sync 0。Post-driftはbranch変更済みの事実、before/after branch/headをexisting command envelopeへ含め、active/sync 0、auto rollback 0です。

## 16. Worktree B

### 16.1 Create

1. A SH下でsource HEAD/branchをpinし、provider closure一致とGit capabilityを確認する。
2. Existing containment/collision rulesを実行する。
3. B pathをexclusive mkdirし、empty、no-follow、same repository filesystemを確認する。
4. B EX NBを取得し、identity/emptinessを再確認する。
5. `git worktree add --no-checkout -b <branch> <B> <pinned>`をA/B fd付きmanaged helperで実行する。
6. `git read-tree --reset <pinned>`でindexをpinする。
7. Git object databaseからtracked blobs/symlinksをdescriptor-relativeにmaterializeする。ただし`spec-dock/scripts/spec-dock`だけを保留する。Filter/attribute/submodule/sparseはpreflightで禁止済み。
8. Bootstrapを除くtree、index、record、markers、provider closureを検証する。
9. Bootstrap blobをsame-directory tempへwrite/fsyncし、native no-replaceでpublish、parent fsyncする。
10. Full tree/index/HEADがpinned commitへclean一致することを検証する。
11. B EX下でnonlocking B fdを別openし、same inodeを確認する。
12. Worktree resultとhook requestをprimitive化してbootstrapへ返す。
13. BootstrapがA/B leaseを閉じ、original-B fdでmake hookを実行・renderする。

Failure時は実際に作成したempty root、Git worktree record、branch、payloadの有無をexisting envelopeで報告します。自動remove/rollbackしません。Entrypoint公開前はruntime実行不能、公開後は完全verified candidateです。

### 16.2 Remove

1. Existing target resolution、main/current/dirty/untracked/containment blockersを実行する。
2. Bをno-follow open/bindし、B EX NBを取得する。
3. Target/record/containmentをB EX下で再検証する。
4. `git worktree remove --force <B>`を必要なA/B fd付きmanaged helperで実行する。
5. Git helper終了後、B parentからformer basenameをno-followで確認する。
6. Absentならsuccess。Original same inodeが残る場合だけbound cleanupを許可する。
7. Different inodeまたはsymlink Cなら触らず`post_remove_cleanup_failed`、`removed_record=true`、`removed_directory=false`、unsafe-binding reasonを返す。
8. Branchは現行どおり自動deleteしない。

## 17. CLI and wire projection

### 17.1 Installer CLI

`src/spec_dock/cli.py`に残すproduction responsibilitiesは次だけです。

- `_assets_dir`
- `_tool_version`
- `_parse_args`
- parser-normalized `LifecycleRequest`構築
- root EX acquisitionを含む`execute_provider_lifecycle`呼出し
- exact public text/JSON emit
- `main`

CLIがACTIVE、stage、receipt、record、action checkpointを解釈しません。Engineが返すvalidated `LifecycleResult`だけをemitします。

### 17.2 Wire generation

Generatorは親Wire pathをexplicit引数で受け、次を機械検査します。

- ID `provider-lifecycle-wire-contract-v12`
- 6 status、41 code、23 phase、24 last phase、168 rows、40 public goldens、4 record goldens
- TARGET_PATH_ORDER 13 entries
- relation table全cellがknown enum/expression
- fenced JSONがparse可能、compact reserialize一致、one LF
- cleanup warning 7 rowsのretry/continuation/token relation

生成file先頭に`SOURCE_ID`と`SOURCE_SHA256`を持たせます。RuntimeはSHA driftを自動受理しません。Testがgeneratorをtemporary outputへ実行し、checked-in generated fileとのbyte equalityを要求します。

## 18. Compatibility and no-touch

### 18.1 Keep

- Current public command names、target forms、retained update/uninstall flags、text/JSON choice。
- WIR-TEXT-001/002/003とpublic JSON key order。
- `active set`のselection-only contract。
- `issue start`のguard→deps→checkout→active→syncの意味。ただしgeneration guardを追加。
- Worktree current/main/dirty/untracked/containment guards、partial-result fields、branch non-deletion。
- make failureでもworktree creation outer exit 0。
- current docs/skills/runtime behavior unrelated to lifecycle。
- provider CIのPR-only structureとLinux/macOS matrix。

### 18.2 Delete/replace

- `.distribution-journal.json`、`.distribution-retry.json`、`.uninstall-retry.json`のwriter/authority/reader。
- `OperationJournalStore`、`DistributionStageOwnership`、per-file action plan、obsolete manifest interpretation。
- Installerによるactive/context-pack/generated-state rebuild。
- Explicit purge serviceと`--remove-specs` forwarding。
- Wrapper内`subprocess.run(uvx...)`とold-module return。
- Pathname-only worktree cleanup。

### 18.3 No-touch

次のpathは#392で内容変更しません。

- `full-regression-ledger.json`のactive row node/signature/lifecycle。
- `full-regression-timing-weights.json`の243 entries。
- `scripts/quality/full_regression_baseline.py`、`scripts/quality/verify_full_regression.py`のpolicy semantics。
- `tests/conftest.py`のfour required-fast identities、full-regression permission/shard behavior。
- #395/#396 canonical R/D/PとProduct code。
- Parent Wire v12、`E384-QUAL-001`、accepted ADR。
- Consumer initiatives/Artifacts/active/`.agent`/diagrams/`.workbench` content。

`full-regression-ledger.json`のresolved rowは、concrete successor `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`を同nodeのまま維持します。Rebindを不要にします。

## 19. Packaging and dogfood

- CP2で`pyproject.toml` versionを0.2.4へ固定し、CP4ではread-only確認します。
- Provider runtime、provider-shipped docs、two provider skills、fixture、package inventoryをcomplete candidateとして先に完成させ、source testsをGREENにしてcandidate digestを固定します。
- Existing `assets/**/*` package dataへnew fixtureが入ることをwheel/sdist inventoryで検証します。
- `setup.py`のstale build pruningがnew fixture、provider_lifecycle package、bootstrapを削除しないことを確認し、必要な場合だけexact allowlistを更新します。
- 固定した同一source treeからwheel/sdistをbuildし、isolated installed packageのcandidate digest、fixture bytes、bootstrap SHA、docs、two skill tree digestsを比較します。Build後にprovider candidate bytesを変更した場合、artifact proofをやり直します。
- Artifact proofがGREENになった後だけ、`spec-dock/scripts/**`、`spec-dock/docs/**`、`.agents/skills/spec-dock/**`、`.agents/skills/spec-dock-grill-with-docs/**`へcomplete candidateを一括同期します。Partial dogfood projectionは禁止します。
- T13でsource、wheel、sdist、isolated installed package、fresh install、checked-in dogfoodのparityを検証します。
- `.github/workflows/provider-ci.yml`はcurrent PR jobsを維持し、旧`test_managed_distribution.py` commandをT01–T07のfocused commandへ置換します。full final gateを追加しません。

## 20. Security and privacy properties

- Private schemaはspec本文、Artifact content、credential、Git remote userinfo、任意のpath list、ambient cwd/home、environment dumpを保存しません。例外として、Wire v12が要求する`ACTIVE.cleanup_retry_invocation.rendered_command`、`ACTIVE.deferred_invocation.rendered_command`、および`CLEANUP-COMPLETED.json`内の同じ二fieldだけはWIR-TEXT-001のexact renderer出力をdurable保存し、normalized targetがabsoluteならabsolute pathを含み得ます。別のstandalone absolute-path fieldや任意commandは禁止し、operational metadataを不要なlog、telemetry、Reportへ転載しません。
- Public diagnosticはWireのcontent-free exact textだけです。
- Candidate/legacy fixtureはprovider-owned bytesのdigestと必要なlegacy record bytesだけを保持します。
- Unknown/foreign objectを削除・chmod・renameして進みません。
- Descriptor inheritanceはallowlist、close-on-exec default、real child validationです。
- Consumer hookへlock authorization、cleanup token、private namespace pathを渡しません。
- Completion tokenはidentity bindingでありauthorizationではありません。

## 21. Rejected alternatives

| Alternative | Reject reason |
|---|---|
| 旧`managed_distribution.py`を段階的に残す | dual writer/旧manifest dependencyが残り、hard cutover ACを満たさない。 |
| Record/markerをYAMLまたは`key=value`にする | Wire v12はcompact JSONをnormativeに固定済み。 |
| `/tmp`またはuser cacheへstageを置く | same-filesystemとrepository-bound identityを保証できない。 |
| Per-file journalを作る | bounded fixed-root recoveryという親判断を覆す。 |
| P2でcandidate stageを再copyする | durable stage reuse要件とfault determinismを壊す。 |
| flock fileを新設する | coordination objectはrepository root inodeと固定済み。 |
| runtimeを全command EXにする | accepted SH/EX modelを変更する。 |
| wrapperからexternal installer後にold moduleへ戻る | mixed generationとstream/status改変を生む。 |
| Git config/hook/filterを一時disableする | consumer設定を無断変更し、effective behaviorを証明できない。 |
| Worktree create後にentrypointを削除して再配置する | entrypointが一度公開されるraceを残す。 |
| former B pathnameをrecursive cleanupする | different-inode Cを削除し得る。 |
| make hookをB EX中に実行する | nested installerがself-contentionし、arbitrary codeをcooperative writerと誤認する。 |
| checkpointごとのmerge | Issueの一つのobservable hard-cutover outcomeを分割する。 |

## 22. Design completion condition

本Designは実装判断を閉じる候補です。ただし、独立内容reviewのP0/P1=0/passと、この内容を含むclean pushed freeze/projectionは未実施です。Product実装者はそのgate前に本Designを実行指示として扱いません。

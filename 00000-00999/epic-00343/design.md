---
種別: 設計書（Epic）
ID: "epic-00343"
タイトル: "Workbench Shell And Explicit File Artifact Import"
関連GitHub: ["#343"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
依存: ["requirement.md"]
親: ["init-local-00002"]
---

# epic-00343 Workbench Shell And Explicit File Artifact Import — 設計


## 1. Requirement Coverage

| Requirement | 設計上の受け皿 |
|---|---|
| E-RQ-001〜007 | fresh init判定、Workbench guidance README、Git ignore rule、既存opaque traversal、manual-only `workbench copy` |
| E-RQ-008〜012 | 独立`artifact import file` command、root/node target resolver、repo-root relative resolution、explicit-file source guard |
| E-RQ-013〜018 | FD identity固定、既存byte-preserving publisher、global slot allocator、generic `--` filename、publication state、privacy mapper |
| E-RQ-019〜020 | no-sidecar/no-canonical mutation、name-only validation、ADR mirrorからのsemantic isolation |
| E-RQ-021〜025 | 既存`chatgpt-output`/`new artifact`/`workbench copy`非変更、provider/package/dogfood parity、public docs |
| E-AC-020 | unit / CLI / installed-consumer / fault-injection / full regressionの実測traceとblocking finding解消 |

主要なE-AC traceは次の通りである。

- E-AC-001〜007: installer fresh-state fixture、README content/parity、node create matrix、`git check-ignore`、no-backfill mutation matrix、opacity、manual copy regression。
- E-AC-008〜016: command/application/domain/infra/presentationのtarget/source/file-form/collision/publication/privacy matrix。
- E-AC-017〜020: validate/sync opacity、compatibility、candidate wheelのfresh/update consumer、dogfood parityとfull regression。

## 2. Existing Context Findings

### 2.1 現行Workbench境界

- `src/spec_dock/assets/spec_dock/.gitignore`は現在`.workbench/`全体をignoreするため、tracked shell READMEを再包含できない。
- `src/spec_dock/cli.py::_install_spec_dock`はfresh initとupdateの双方から呼ばれ、`force`だけではfreshかexistingかを表せない。関数冒頭でwrite前の`specdock_dir`存在を観測しなければno-backfillを守れない。
- future Initiative / Epic / Issueは`application/create_node.py::execute_create_plan`からkind別template treeをcopyする。`_scaffold_file_paths`と`infra/template_scaffolder.py::copy_scaffolded_tree`はhidden directory内の通常fileも扱うため、各node templateへの`.workbench/README.md`追加でplanned pathと実fileを一致させられる。
- `.workbench`のsemantic opacityは`infra/fs_repo.py`、`application/delegated_authoring.py`、`application/delete_node.py`、authoring source manifestなどでtop-down prune済みである。本Epicはこの境界を緩めない。
- `application/workbench.py::workbench_copy`と`infra/fs_cli.py::copy_workbench`はexplicit one-shot source-wins helperとして存在する。自動hookや同期を追加する必要はない。

### 2.2 現行Artifact import / naming境界

- `commands/artifact_import.py`と`application/import_artifact.py::import_artifact`は`chatgpt-output`専用で、node scope、Workbench内lowercase `.md`、title/slug、blank identityを要求する。
- `infra/binary_artifact_publisher.py::FilesystemBinaryArtifactPublisher`はsource FD identity、stream/staged/source hash、same-directory temp、fsync、no-replace publication、post-publish warningを既に提供する。再実装すべきではない。
- 現行`guard_source`はWorkbench containment、lowercase `.md`、non-symlink ancestryを一体化しており、repository外sourceとancestor symlink許容にはそのまま使えない。
- `domain/artifacts.py`はtyped/blank Markdownだけをparseし、`scan_artifact_duplicate_state`とallocatorは`*.md`だけを見る。generic file familyを別parserで認識し、timestamp/suffix slotだけを共有する必要がある。
- `application/sync_state.py::_collect_adr_mirror_sources`はArtifact basenameがtyped ADRと判定された後だけbodyを読む。generic `--` familyをtyped parserへ混ぜなければ、original basenameが`adr-*.md`でもsemantic parseを回避できる。
- rootはgraph nodeではなく、現在`spec-dock/artifacts/`もroot用rules sourceもない。root targetはnode resolverへ擬似nodeを混ぜず、明示的なroot targetとして扱う必要がある。

## 3. Design Decisions

### D-001 Fresh-only guidance shell generation

意味のないempty markerは使わず、次の4 provider assetsへbyte-identicalな`.workbench/README.md`を置く。

- `src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md`

`templates/root`はfresh root Workbench shell専用のprovider assetとする。`_install_spec_dock`の最初に`fresh_specdock = not os.path.lexists(specdock_dir)`を固定し、managed asset copy後、`fresh_specdock`のときだけroot templateのREADMEを`spec-dock/.workbench/README.md`へcopyする。`update`、existing workspaceへの`init --force`、通常runtime commandからroot copyを呼ばない。

Initiative / Epic / Issueは既存kind別template treeのcopyでREADMEを生成する。これによりnew nodeのcreate plan、collision preflight、result pathsへREADMEが自然に含まれる。既存ancestor / siblingを走査してREADMEを補う処理は作らない。

4 READMEのcanonical guidance contractは同一で、少なくとも次の内容を平易なMarkdownで記載する。

```markdown
# SpecDock Workbench

This directory is a temporary, worktree-local workspace.

- `README.md` is the only file here intended for Git tracking.
- Other files are ignored by Git and are not canonical SpecDock state.
- Files may be discarded when this worktree is removed.
- To preserve one file, explicitly import it into the target `artifacts/`
  directory with `spec-dock artifact import file`.
- Workbench files are not copied or synchronized automatically. Use the
  manual `workbench copy` command only when needed.
- Git ignore is not a security boundary. Do not store prohibited secrets here.
- Models and tools must not treat Workbench files as canonical input.
  Explicitly naming a file only authorizes reading or importing it as evidence;
  canonical adoption is a separate reviewed workflow.
```

wordingの軽微な改善は許容するが、E-RQ-003の7要素を削除しない。4 assetsのbyte parityをtestで固定し、node kindごとの説明driftを防ぐ。

### D-002 Tracked README / ignored contents

provider `.gitignore`と`src/spec_dock/cli.py::_DEFAULT_SPEC_DOCK_GITIGNORE`の`.workbench/`を次へ置換する。

```gitignore
**/.workbench/*
!**/.workbench/README.md
```

Workbench directory自体をignoreせず、その直下entryをignoreすることで、top-level `README.md`だけを再包含する。ignored child directoryはそのsubtree全体をignoreする。nested `README.md`、case variant `readme.md`、near-name `.workbench-notes`は再包含しない。updateはignore contractとprovider template assetsだけを配布し、existing scopeの`.workbench/`へREADMEをcopyしない。

READMEはGit guidanceであってsemantic sourceではない。既存top-down Workbench pruneを維持し、validate / sync / dependency / ADR / authoring default discoveryはREADMEを含むWorkbench subtreeを読まない。利用者がgeneric importの`--file`でREADMEまたは別fileを明示した場合だけ、read/importのexplicit source authorizationとして扱う。この指定とimport結果はevidence-onlyであり、canonical adoptionには別のreviewed workflowが必要である。

### D-003 Generic import is an additive use case

既存`ArtifactImportRequest` / `import_artifact` / `artifact import chatgpt-output`は変更せず、次を追加する。

- `commands/artifact_import.py::ArtifactImportFileArgs`
- `application/contracts.py::FileArtifactImportRequest`
- `application/contracts.py::FileArtifactImportResult`
- `application/contracts.py::FileArtifactImportError`
- `application/import_file_artifact.py::import_file_artifact`
- `UseCases.import_file_artifact`
- parser leaf `artifact import file`

`FileArtifactImportRequest`は`source_path`と`ArtifactTargetSelector`だけを持ち、title、slug、kind catalogを持たない。

### D-004 Target resolver keeps root outside the node graph

`ArtifactTargetSelector`を次のclosed contractとする。

```text
kind: root | initiative | epic | issue
node_id: null for root; full/normalized id for node
```

- `root`は`specdock_dir / "artifacts"`、public target idは`root`。
- nodeはcurrent graphを`validate=False`でloadし、kindとidの一致をexactly oneへ解決する。
- zero/multiple selectorはargparseのrequired mutually-exclusive groupで拒否し、applicationでも再検証する。
- root `artifacts/`初回作成時は`docs/rules/root/artifacts.md`を`rules.md`へsymlinkする。node側は既存`_ensure_artifacts_setup`を再利用し、共通helperはtarget kindとdestinationだけを受ける。

### D-005 Explicit source guard and publication reuse

`FilesystemBinaryArtifactPublisher`のsource open、temp copy、hash、fsync、source stability確認をprivate `_stage_and_verify_guarded(...)`へ抽出し、二つのpublic entryを持たせる。

1. 現行`publish(BinaryArtifactPublishRequest)`:
   - 現行Workbench guardを通し、`chatgpt-output`互換を維持する。
2. 新規`publish_explicit_file(ExplicitFileArtifactPublishRequest)`:
   - generic explicit-file guardを通し、同じstaging / verification coreを使う。
   - mutableなtemp pathnameをsourceにせず、verified open `temp_fd`とsecurely opened `destination_parent_fd`をpublication primitiveへ渡す。
   - Linuxはdestination filesystem上で`O_TMPFILE`によりlinkable anonymous staging inodeを作り、保持中の`temp_fd`を指すcurrent-processの`/proc/self/fd/<temp_fd>`をsourceに、`linkat(..., destination_parent_fd, name, AT_SYMLINK_FOLLOW)`でno-replace hard linkする。formal nameへのlinkを許すため`O_EXCL`を伴わないanonymous inodeを使う。`/proc/self/fd`は任意pathnameの再解決ではなく、closeされていないverified FDのkernel-owned handleとしてだけ使う。Linuxではvisible named stagingを作らず、pre-commit abort/failureはFD closeだけで完了する。macOSは`fclonefileat(temp_fd, destination_parent_fd, name, 0)`を使う。いずれもverified FD identityとopened destination directoryへ拘束され、formal nameが既存なら置換しない。
   - publication直前にvisible destination parentのdevice/inodeをopened FDと照合する。照合後、FD-bound no-replace primitiveが成功した時点を単一のcommit pointとする。
   - FD-bound no-replace primitiveを提供できないplatformではformal destination作成前に`publication_unsupported`でfail closedにする。

portは`ExplicitFileArtifactPublisher`として新設し、bootstrapでは現行と同じ`FilesystemBinaryArtifactPublisher` instanceをwireする。generic use caseを`workbench_source_guard`へ依存させない。

Explicit source guardは次を行う。

1. relative inputはrepository root基準でabsolute lexical pathへする。`..`は禁止せず、指定された一fileだけを扱う。
2. `os.open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW)`相当でleaf symlinkを拒否し、ancestor symlinkはOS path resolutionに委ねて許容する。
3. `fstat`でreadable regular file、device/inode/modeを固定する。directory/FIFO/socket/deviceは拒否する。
4. publication中は同じFD、または再open後に同じdevice/inode/modeと検証したFDだけを読む。stage後の最終検証では、同じsource FDを先頭から再読してhash / byte countをstaged tempと照合し、その直後にFD statとvisible path identityを再検証する。観測できた変化は`source_changed`でpublishしない。
5. sourceの親directoryをenumerateしない。

source visibilityはfail-closedで分類する。lexical pathとstrict-resolved pathの双方がrepo内で、open FD identityとresolved path statが一致する場合だけ`repo_relative`とする。それ以外は`basename_only`とし、resolved absolute pathはapplicationへ返さない。

supported platformでleaf no-followとFD identity検証を満たせない場合、通常path openへdegradeせず`source_guard_unsupported`でpublish前にfail closedとする。

Publication capability matrix:

| Environment | Supported capability | Probe / outcome |
|---|---|---|
| Linux | destination filesystemが通常権限でlinkable `O_TMPFILE` anonymous inodeを作成でき、mounted `/proc`がcurrent-process FD referenceを公開し、directory durability primitiveを実行できる | preflightはvisible probe pathnameを一切作らず、anonymous FDのregularity、`/proc/self/fd/<fd>` reference availability、directory durabilityだけをnon-mutatingに確認する。anonymous FDをprobe nameへlinkして削除しない。`linkat(..., AT_SYMLINK_FOLLOW)`固有のcapability / policyはpreflightで判定せず、formal candidateへの最初のcommit syscallで確認する。`EEXIST`はexisting destination collisionとしてallocation retry、formal entry未作成のcapability / policy failureは個別errnoを公開せず`publication_unsupported`、`not_committed`、`safe_after_remediation`へ正規化する。`CAP_DAC_READ_SEARCH`を要求しない通常権限testを必須にする。supported Linux filesystem laneは縮小され、named-temp / visible-probe / pathname-cleanup fallbackはしない |
| macOS | destination directory内のnamed owned tempとformal destinationが同じclone-capable filesystemにあり、`fclonefileat` no-replace cloneとdirectory `fsync`を許可する | import前にdestination directory内のowned tempでcapability probeする。cleanupはhigh-entropy name、held FD、final FD/path identity check、uncertainty時retainを必須とする。最終check後から`unlink`までの意図的same-UID replacementだけはaccepted ADR `20260730t085831z-adr`の限定保証対象外。clone非対応volumeまたはpolicy拒否は`publication_unsupported`でformal destination作成前にfail closed |
| その他 | leaf no-follow、FD identity、FD-bound no-replace commit、directory durabilityの同等primitiveをproviderが明示実装した場合だけsupported | primitive未実装時は`source_guard_unsupported`または`publication_unsupported` |

original sourceはrepository外volumeを含む任意のreadable filesystemに置ける。bytesはdestination directory内のowned staged tempへstream copyするため、publication primitiveのsame-filesystem制約は**staged tempとformal destinationの間だけ**に適用し、original sourceとdestinationがcross-filesystemでもsuccess laneである。

Linux preflightはcontent-free errorへ正規化し、visible probe entryを作成しない。anonymous FDをformal candidate以外のpathnameへlinkしない。candidate wheelのinstalled-consumer testは通常権限Linuxのsupported filesystemとmacOSのclone-capable filesystemをsuccess laneとし、少なくとも一つのunsupported fixtureでfail-closed laneを確認する。OS名だけで成功を保証せず、上表のcapabilityを満たすenvironmentを本Epicのsupported environmentとする。

### D-006 Generic filename family and shared slot ledger

generic filenameは次の独立grammarとする。

```text
standard:  <timestamp>--<safe-original-basename>
collision: <timestamp>-<nn>--<safe-original-basename>
nn: 01..99
```

`domain/artifacts.py`へtyped/blank parserとは別の`GenericImportedArtifactFilename`と`parse_generic_imported_artifact_filename(name)`を置く。generic fileは`parse_artifact_filename`でtyped/blank Artifactにしない。stable public identityはdestination basename全体である。

`scan_artifact_duplicate_state`の内部をname-only slot scanへ拡張する。

- direct childだけを`iterdir`し、bodyを開かない。
- typed/blank Markdownは現行parserとmalformed checkを維持する。
- extensionを問わずgeneric `--` basenameを新parserで認識する。
- typed / blank / genericを共通`(timestamp, suffix|standard)` slotへ登録し、family横断duplicateをrejectする。
- generic-shaped symlink/directoryはvalid Artifactとして扱わずfail closedにする。
- その他のgrandfathered/noncandidate fileは現行どおりsemantic対象外にする。

typed/blank allocatorもこの共通slot ledgerを参照する。generic用`allocate_generic_import_filename_for_timestamp`も同じcreate lock内で同じledgerを使う。これにより`new artifact`、`chatgpt-output`、generic importが同一slotを二重使用しない。

### D-007 Minimal basename normalization

`normalize_imported_basename(original, name_max)`をdomainのpure functionとして追加し、次だけを行う。

- empty / `.` / `..`をrejectする。
- path separator、NUL、ASCII control、対象platformで使用不能なcomponent characterを`_`へ一対一置換する。
- trailing dot / spaceを`_`へ置換する。
- reserved componentと衝突する場合は最小の`_`を付与する。
- filesystem `NAME_MAX`から最大prefix`<timestamp>-99--`分を差し引いたbyte budgetへUTF-8 code point境界で切り詰める。可能な限りstemを先に切り詰め、extension chain、case、space、Unicodeは保持する。
- normalization後もemptyなら`source_ineligible`とする。

content、MIME、encoding、titleから名前を作らない。同じinput basenameとname budgetから同じsafe basenameを得る。

### D-008 Publication state and privacy are first-class result contracts

generic public successは次を返す。

```text
status: ok
target_kind: root | initiative | epic | issue
target_id: root | node id
artifact_id: full destination basename
source_visibility: repo_relative | basename_only
source: repo-relative path | basename
destination: repository-relative path
committed: true
publication_state: committed | committed_with_warning
cleanup_state: not_created | removed | retained
warning_codes: [...]
retry_disposition: not_needed
canonical: false
```

generic public outputはsource locationを問わずSHA-256、byte count、body、MIME、encodingを返さない。hash/byte countはpublication verificationとtest evidenceにだけ使う。これによりexternal sourceのcontent-derived valueを漏らさない。既存`chatgpt-output`のresult contractは変更しない。

pre-publication failureはexit 1とし、次だけを返す。

```text
status: error
code: stable content-free code
committed: false
publication_state: not_committed
cleanup_state: not_created | removed | retained
retry_disposition: safe_after_remediation
canonical: false
```

pre-publication errorにはsource path/basename、destination path、exception text、hash/countを含めない。unknown exceptionは`runtime_failed`へ潰す。publish後のdirectory fsync、owned temp cleanup failureはexit 0、`committed_with_warning`、`retry_disposition=not_needed`とし、重複retryを防ぐ。

target/source displayとrepository-relative destinationはpublication前に確定し、publisherが`committed=true`を返した後にfallible path解決を行わない。create lock release failureもpostcommit warningへ変換する。これにより、formal file公開後の内部整形失敗を`committed=false`へ誤分類しない。

generic pathではverified FDとopened parent FDをbindingするOS primitiveの成功を単一のcommit pointとし、別のmutable source pathnameを再解決しない。commit前failureは`not_committed`、commit後は`committed`またはdirectory fsync / owned temp cleanupだけの`committed_with_warning`である。現行`chatgpt-output` wrapperのwarning contractは互換性のため別finalizerに残す。

Threat modelは、shared create lockに従うSpecDock process間のcollision、initial copyまたは最終source再読/identity検証で観測できるexplicit sourceの外部変更、publication直前までに観測できるdestination ancestry変更を扱う。次はnon-cooperating writerに対してOS-level leaseを取得しない本command単独の保証対象外とする。

- 最終source再読とidentity検証が完了した後からFD-bound commit syscallまでの間に、別processが同じsource inodeへin-place writeすること。
- last visible-parent identity checkとFD-bound commit syscallの間に、別processがrepository directory自体をrename / replaceすること。
- commit後にrepository write権限を持つactorがArtifactを変更すること。
- macOS named staging cleanupの最終FD/path identity check後から`unlink` syscallまでに、同一UIDでdestination directoryを変更でき、internal staging nameを発見・監視するactorがそのpathnameを意図的に別entryへ置換すること。

この境界でもcommand自身はsourceを変更せず、staged bytesのhash / countとformal destinationのbytesは一致する。E-RQ-013の「検知したsource変更はsuccess公開しない」は最終source再読/identity検証までを検出境界とし、T3は境界の直前と直後を別fixtureで固定する。この除外はdestination file collisionまたはSpecDock同士のconcurrencyを除外しない。

Linuxはanonymous stagingを使うため、named-temp cleanupのsame-UID waiverを持たない。`O_TMPFILE`またはheld-FD publication capabilityが不足するenvironmentでは、visible staging pathnameを作らずformal destination前にfail closedする。根拠、必須mitigation、rollback / revisit条件はaccepted ADR `20260730t102747z-adr-linux-anonymous-staging-trust-boundary.md`を正本とする。

macOS cleanupの除外は包括的same-UID waiverではない。偶発collision、final checkまでに観測可能なreplacement、formal destination no-replace、source bytes / non-mutation / privacy、destination parent identity、mismatchまたはuncertainty時にunlinkせずretainする義務は対象内に残る。根拠、必須mitigation、rollback / revisit条件はaccepted ADR `20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`を正本とする。

### D-009 Opaque lifecycle

- generic fileはcanonical docs、report、EAL、ADR、assurance、sidecarを変更しない。
- `validate`はrootおよびnodeのArtifact directoryでbasename/symlink/slotだけを検証し、bodyをread/decodeしない。
- `sync`のADR mirrorは現行どおりtyped ADR basenameだけを候補にし、generic parserをtyped parserへ接続しない。generic `.md`もbasename判定でskipし、bodyを読まない。
- non-Markdown generic fileはdefault semantic discoveryに追加しない。
- dependency生成は`application/check_deps.py`が`SpecGraph` / dependency topology / Issue statusを、`presentation/json_state.py::render_deps_issues_artifact`と`render_deps_raw_artifact`がそのdomain resultを入力にする現行境界を維持する。generic Artifact directoryやbodyを新しい入力へ加えない。
- active context生成は`infra/active_store.py::_render_context_pack`および`presentation/json_state.py::render_context_pack`が`ActiveManifest` / derived index pathだけを入力にする現行境界を維持し、generic Artifactを列挙・decodeしない。
- authoring diff guard / source manifestで利用者がgeneric fileを明示指定した場合はopaque bytesのSHA-256算出を許すが、UTF-8 / Markdownとしてdecodeせず、default contextへ暗黙追加しない。
- import successは`canonical=false`を明示し、採用は別workflowに委ねる。

## 4. Alternatives Considered

### A. 現行`chatgpt-output`をgeneric modeへ拡張する

- 利点: command/use case数が少ない。
- 棄却理由: Workbench-only `.md`、title/slug、blank identity、既存result contractへ多数のoptional branchが入り、E-RQ-021の互換性とsource policyの局所性を損なう。

### B. generic fileをtyped `file` Artifactとしてcatalogへ追加する

- 利点:現行typed parser/templateへ寄せられる。
- 棄却理由: ユーザーがtyped token/catalogを明示的に不要とし、original basename/extension preservationとも衝突する。

### C. import sourceをrepository内またはnon-symlink ancestryへ制限する

- 利点:現行Workbench guardをそのまま使える。
- 棄却理由: repository外explicit fileとancestor symlink許容というE-RQ-010〜012に反する。

### D. Workbench shellをupdate/syncで一括backfillする

- 利点:既存scopeも見た目が揃う。
- 棄却理由: optional/no-backfill contractに反し、既存tree全走査と不要なGit差分を生む。

### E. rootをsynthetic `SpecNode`としてgraphへ混ぜる

- 利点:node resolverを再利用しやすい。
- 棄却理由:dependency/status/active projectionへroot概念が漏れ、Artifact importだけのためにgraph contractを拡張する。root targetはapplication-level value objectで十分である。

### F. Linux named staging cleanupのsame-UID waiverを受容する

- 利点: `O_TMPFILE`を持たないLinux filesystemでも現行のnamed staging success laneを維持できる。
- 棄却理由: macOS専用accepted ADRの限定例外をLinuxへ拡張し、final identity check後のnon-owned entry unlink riskを受容することになる。Linuxはanonymous staging capabilityを必須化し、未対応environmentをfail closedとする。

## 5. Boundary / Contract Model

- Title: Generic File Import Component Boundary
- Question answered: generic importをどのlayerへ追加し、既存publisherとnode graphをどう分離するか。
- Scope: CLI、application、domain、publisher port / adapter、root/node Artifact destination。
- Excluded details: exact function body、OS別system call、test fixture。
- Update trigger: component ownership、dependency direction、public request/result boundaryが変わるとき。

```plantuml
@startuml
skinparam monochrome true
left to right direction

component "CLI parser / command\nartifact import file" as CLI
component "Application\nimport_file_artifact" as APP
component "Domain\nfilename + slot ledger" as DOMAIN
component "ExplicitFileArtifactPublisher\nport" as PORT
component "FilesystemBinaryArtifactPublisher\nadapter" as INFRA
component "Node graph\nread only" as GRAPH
database "root/node artifacts/" as ART

CLI --> APP : FileArtifactImportRequest
APP --> GRAPH : resolve node target only
APP --> DOMAIN : normalize + allocate under create lock
APP --> PORT : explicit source + fixed destination
PORT <|.. INFRA
INFRA --> ART : verified no-replace publication
APP --> CLI : privacy-safe result / stable error
@enduml
```

境界ルール:

- CLIはarg cardinalityとpresentationだけを所有し、filesystem処理を行わない。
- Applicationはtarget resolution、create lock、allocation retry、result mappingを所有する。
- Domainはfilename grammar、normalization、slot uniquenessだけを所有し、file bodyを扱わない。
- Infraはsource FD identity、byte copy/hash/fsync/no-replace、cleanupを所有する。
- Sync/validationはgeneric fileのnameだけを知り、bodyの意味を知らない。

Deletion test:

- generic commandを削除しても`chatgpt-output`、`new artifact`、`workbench copy`が残る。
- `workbench copy`を削除してもshell generationとgeneric importが残る。
- generic parserをtyped parserから独立させるため、generic family削除時にADR mirror semanticsへ変更が波及しない。

## 6. Dependency Analysis

依存方向は次に固定する。

```text
commands/artifact_import.py
  -> application/import_file_artifact.py
      -> application/contracts.py
      -> application/create_node.py::_acquire_create_lock / _release_create_lock
      -> application/create_artifact_doc.py のartifact setup共有helper
      -> domain/artifacts.py
      -> application/ports.py::ExplicitFileArtifactPublisher
          <- infra/binary_artifact_publisher.py::FilesystemBinaryArtifactPublisher
presentation/cli_text.py
  <- application/contracts.py
```

- Infraからapplication/domainへの逆依存を追加しない。
- `import_file_artifact`から`application/workbench.py`へ依存しない。
- `domain/artifacts.py`はPath/name/stateless allocationに限定し、OS open/fsyncを持たない。
- create lockの共有はglobal slot coexistenceのため必要である。lock infrastructure自体の再設計はしない。
- root rules/setup共有のため、`create_artifact_doc.py`のprivate helperはtarget-kindを受ける小さなapplication helperへ抽出してよい。template creationとbinary publicationを一つのuse caseへ統合しない。

## 7. Source of Record

- implementation authority:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/**`
- consumer/dogfood projection:
  - `spec-dock/**`
- product contract:
  - fresh-reviewed `epic-00343/requirement.md`
  - fresh-reviewed canonical `design.md` / `plan.md`
  - `artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md`
  - accepted ADR `artifacts/20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`
  - accepted ADR `artifacts/20260730t102747z-adr-linux-anonymous-staging-trust-boundary.md`
- advisory evidence:
  - 旧`epic-00312` interviews / research / historical design
  - ChatGPT Pro ZIP evidence SHA-256 `ecd4c65a608ee4474fd5e06b0230150ba56106a5eee7418811367c9cbadca371`
  - 本artifact

Providerを先に変更し、dogfood側runtime/docs/templatesの手編集をimplementation authorityにしない。

## 8. Data Flow / Domain Model / Interface Contract

### 8.1 Import flow

- Title: Explicit Single-File Import Sequence
- Question answered: explicit sourceとtargetが、preflightからprivacy-safe resultまでどの順序で処理されるか。
- Scope: target resolution、source guard、slot allocation、verified no-replace publication、result mapping。
- Excluded details: chunk loop、normalization algorithm内部、exception class hierarchy。
- Update trigger: operation順序、commit point、lock / allocation ownership、public outcomeが変わるとき。

```plantuml
@startuml
hide footbox
actor User
participant CLI
participant Application
participant TargetResolver
participant SlotLedger
participant Publisher
database Artifacts

User -> CLI : artifact import file --file P --target T
CLI -> Application : request(P,T)
Application -> TargetResolver : resolve root or exact node
TargetResolver --> Application : artifacts directory
Application -> Publisher : preflight explicit file
Publisher --> Application : eligible + safe visibility
Application -> SlotLedger : allocate timestamp/suffix under create lock
SlotLedger --> Application : unique full basename
Application -> Publisher : publish_explicit_file(source,destination)
Publisher -> Publisher : open/fstat/copy/hash/fsync/reverify
Publisher -> Artifacts : no-replace publish
Publisher --> Application : committed + warnings
Application --> CLI : privacy-safe result
CLI --> User : exit 0, retry not needed
@enduml
```

### 8.2 State model

- Title: Generic Import Publication State
- Question answered: formal destinationの有無、integrity、warning、retry dispositionをどう区別するか。
- Scope: preflight、staged、not committed、FD-bound commit、verified committed、durability/cleanup warning。
- Excluded details: individual error code、filesystem primitive、UI wording。
- Update trigger: commit point、integrity verification、exit status、retry policyが変わるとき。

```plantuml
@startuml
[*] --> preflight
preflight --> not_committed : target/source invalid
preflight --> staged : source eligible + slot allocated
staged --> not_committed : copy/hash/source change/publish failure
staged --> committed : FD-bound no-replace commit succeeds
committed --> committed_with_warning : durability/cleanup warning
committed --> [*]
committed_with_warning --> [*]
not_committed --> [*]
@enduml
```

Invariant:

- `publication_state=not_committed` / `committed=false`は、本commandがformal destination entryを作成していないことを示す。allocation後の競合により、同名pathへ既存または他actor所有のentryが存在する場合はあるため、そのentryを本commandのArtifactとして返したり変更したりしない。
- `publication_state=committed|committed_with_warning`ならverified complete bytesがformal destinationに存在し、自動retryしない。
- sourceは全stateでcommandによりwrite/delete/move/renameされない。
- warningはcommitを巻き戻さない。

`destination_exists`は`not_committed`かつ`retry_disposition=safe_after_remediation`で返す。callerは競合entryを自動削除せず、次回実行でcreate lock配下のslot再割当を行う。target preflight等の非競合failureも同じstateを使うが、codeに応じた人間のremediation後だけretryする。

### 8.3 Failure code family

- request/target: `target_invalid`, `target_not_found`, `target_ambiguous`
- source: `source_missing`, `source_ineligible`, `source_unreadable`, `source_changed`
- allocation: `create_lock_failed`, `artifact_allocation_failed`, `artifact_slot_exhausted`
- publication: `temp_create_failed`, `hash_failed`, `hash_mismatch`, `file_fsync_failed`, `destination_exists`, `destination_ineligible`, `publication_unsupported`, `filesystem_failed`
- fallback: `runtime_not_configured`, `runtime_failed`

全codeはcontent-freeであり、underlying exception messageを連結しない。

## 9. File / Module Change Plan

```text
pyproject.toml                                                 # Modify: 4 Workbench READMEの明示package-dataと広域README除外の限定化
src/spec_dock/
├── cli.py                                                     # Modify: fresh root README copy判定、default ignore
└── assets/spec_dock/
    ├── .gitignore                                             # Modify: README再包含とcontents ignore
    ├── docs/
    │   ├── README.md                                          # Modify: public command要約
    │   ├── guide.md                                           # Modify: shell/import/manual-copy境界
    │   ├── reference_naming.md                                # Modify: generic `--` family/global slot
    │   ├── reference_worktree.md                              # Modify: manual-only copy positioning
    │   └── rules/root/artifacts.md                            # Add: root Artifact evidence rules
    ├── templates/
    │   ├── root/.workbench/README.md                           # Add: fresh root guidance source
    │   ├── initiative/.workbench/README.md                     # Add: future Initiative shell
    │   ├── epic/.workbench/README.md                           # Add: future Epic shell
    │   └── issue/.workbench/README.md                          # Add: future Issue shell
    └── scripts/spec_dock_runtime/
        ├── cli/
        │   ├── parser.py                                      # Modify: artifact import file leaf
        │   └── bootstrap.py                                   # Modify: use case/publisher wiring
        ├── commands/artifact_import.py                        # Modify: File args/spec/run
        ├── application/
        │   ├── contracts.py                                   # Modify: target/request/result/error
        │   ├── ports.py                                       # Modify: ExplicitFileArtifactPublisher
        │   ├── import_file_artifact.py                        # Add: generic use case
        │   ├── create_artifact_doc.py                         # Modify: shared target setup seam
        │   └── validate_tree.py                               # Modify: root Artifact name-only validation
        ├── domain/artifacts.py                                # Modify: generic grammar/normalizer/slot ledger
        ├── infra/binary_artifact_publisher.py                 # Modify: explicit guard + guarded publication reuse
        └── presentation/cli_text.py                           # Modify: generic privacy-safe text/JSON
tests/
├── unit/
│   ├── infra/
│   │   ├── test_init_update.py                                # Modify: fresh/no-backfill/package README
│   │   └── test_binary_artifact_publisher.py                  # Modify: external/ancestor symlink/faults
│   ├── domain/test_artifacts.py                               # Modify: generic grammar/global slots/normalization
│   ├── application/test_import_file_artifact.py               # Add: targets/states/privacy
│   ├── commands/test_artifact_import_file.py                  # Add: CLI cardinality
│   └── presentation/test_artifact_import_file.py              # Add: full privacy mapping
└── cli_runtime/
    ├── test_runtime_new_doc_s09.py                            # Modify: future node README + cross-family slot
    ├── test_artifact_import_chatgpt_output.py                 # Read/verify: compatibility
    ├── test_artifact_import_s04.py                            # Read/verify: publisher compatibility
    └── test_artifact_import_file.py                           # Add: root/node/file-form/opaque lifecycle
```

Exact test file placementは既存suiteの局所命名へ合わせて調整できるが、責務とtest seamは変えない。

\`pyproject.toml\`のcurrent \`assets/**/*\`はhidden directory配下の収録を保証しないため、次のREADME pathをpackage dataへ明示追加する。source treeだけで動作する状態をpassとしない。

- \`assets/spec_dock/templates/root/.workbench/README.md\`
- \`assets/spec_dock/templates/initiative/.workbench/README.md\`
- \`assets/spec_dock/templates/epic/.workbench/README.md\`
- \`assets/spec_dock/templates/issue/.workbench/README.md\`

同時に、current \`[tool.setuptools.exclude-package-data]\`の
\`assets/spec_dock/templates/*/**/README.md\`は上記4 fileにも一致するため、そのまま残さない。
この広域patternを削除し、除外が必要なlegacy READMEが実在する場合だけexact pathへ限定する。
package contractは「\`templates/README.md\`と上記4 Workbench READMEだけを許可し、
それ以外のnested template READMEはsource / wheel / sdist / installed resourcesの全surfaceで0件」とする。
これによりincludeとexcludeの優先順位へ依存せず、将来の意図しないREADME増殖もinventory testでfail closedにする。

## 10. Migration / Compatibility / Rollback

### Migration

- schema/database migrationなし。
- fresh initだけroot Workbench READMEをcopyする。
- updateはmanaged templates/runtime/docs/ignoreを更新するが、rootまたはexisting nodeにWorkbench READMEを作らない。
- update後に作成するnodeは更新済みtemplateからREADMEを得る。
- existing Workbench bytes/names/mtimesへ触れない。
- root `artifacts/`は最初のroot import時だけ作成する。

### Compatibility

- `artifact import chatgpt-output`: command spelling、Workbench-only lowercase `.md`、title/slug、blank filename、hash/count resultを維持する。
- `new artifact`: typed/blank grammarを維持し、allocatorだけgeneric予約slotを尊重する。
- `workbench copy`: explicit one-shot、source-wins、destination-only preserve、symlink object behaviorを維持する。
- `validate` / `sync`: generic Artifact bodyをdecodeしない。既存typed ADR mirrorを維持する。

### Rollback

- provider runtime/templates/docs/ignore変更を同一Epic commit単位でrevertできる。
- generic import済みArtifactはuser evidenceであり、rollback時に削除・renameしない。新commandがなくても通常tracked fileとして残る。
- `.gitignore` rollbackでWorkbench contentsがuntracked表示され得るため、rollback手順は旧`.workbench/` ignore ruleを先に復元してからruntime/templateを戻す。
- 生成済みWorkbench READMEはrollbackで自動削除しない。既存repositoryのtracked guidance / user-owned stateとして残ってもvalidである。

## 11. Observability

- success text/JSONはtarget、safe source display、destination、full artifact identity、commit/warning/retry/canonical stateを同じ意味で返す。
- precommit errorはstable codeとcommit/cleanup/retry stateだけを返す。
- durability / cleanupのpostcommit warningは`committed=true`を維持し、warning codeを列挙する。
- metrics/database/log sidecarは追加しない。
- debug exception tracebackをpublic resultへ混ぜない。開発時testはexception chainingを内部観測できるが、CLI output snapshotには出さない。
- Workbench shell生成はnew/initの既存created-path resultとfilesystemを照合し、専用telemetryは追加しない。

## 12. Test Strategy

### T1 Workbench shell

- fresh init: root `.workbench/README.md`が存在し、`git add -n`対象で、E-RQ-003の7 guidance要素を含む。
- future node: Initiative / Epic / Issueのplanned paths、result、filesystemにREADME。
- parity: root / Initiative / Epic / Issueの4 provider READMEと生成結果がbyte-identical。
- template inventory: `templates/README.md`を除くnested `README.md`は上記4 `.workbench/README.md`だけであり、既存の「node templateにREADMEなし」assertをこのexact allowlistへ置換する。
- ignore: root / 3 node kindsでtop-level `README.md`以外のtext/binary/nested/symlink entry、nested `README.md`、case variant `readme.md`が`git status`へ出ない。
- no-backfill: READMEなしexisting root / 3 nodeを用意し、existing init、update、sync、validate、active set、new Artifact、new ADRを実行してREADME / Workbench stat不変。
- new node作成時: new nodeだけREADMEあり、ancestor / sibling不変。
- opacity: tracked READMEを含むWorkbench subtreeのfake metadata、ADR-like `.md`、invalid UTF-8、broken subtreeでdiscovery / source manifest不変。

### T2 Domain / allocation

- generic standard/suffix parse、typed parserからのisolation。
- Unicode、space、case、multi-suffix、dotfile、no extension、path-unsafe、long UTF-8 component。
- typed/blank/generic同士のstandard/01..99 slot collisionとexhaustion。
- generic-shaped symlink/directory拒否、grandfathered file維持。
- concurrent importはcreate lock + no-replace retryでunique full basename。

### T3 Source / publication

- repo root/scoped Workbench、repo内non-Workbench、external absolute、repo-root relative `..`、nested cwdから同一source。
- ancestor symlink inside/outside成功、leaf symlink拒否。
- missing、directory、FIFO/socket/device、unreadable。
- empty、invalid UTF-8、NUL、PDF/image/ZIP、large streamのsource=staged=destination bytes/hash。
- stage中および最終再読中のsource content/identity change、最終source検証直後のnon-cooperating write境界、publication直前までのdestination ancestry swap、hash mismatch、fsync、FD-bound publication unsupported/failure、platform別cleanup fault injection。
- command起因failure時source stat/bytes不変。本commandがformal destinationを作成しないことを確認し、`destination_exists` fixtureでは競合actor所有entryが保持されることも確認する。
- Linux success時はformal destinationとverified tempが同一device/inode、macOS success時はFD-bound clone結果がverified source bytesと一致し、generic pathにdestination mismatch warningが存在しないことを確認する。
- Linux: 通常権限でvisible entryを一切作らず、formal candidate以外へanonymous FDをlinkせず、pre-commit failure / abortがFD closeだけでpathname unlinkを0回にする。formal candidateへの最初の`/proc/self/fd` + `AT_SYMLINK_FOLLOW` FD-bound commitで`EEXIST`をcollision retryとし、formal entry未作成のlinkat capability / policy failureを`publication_unsupported`へ正規化する。original sourceがdestinationとは別filesystemでもanonymous destination-side stagingでsuccessすることを実volumeまたはmount fixtureで確認する。
- macOS: existing named probe / cleanupとclone-capable filesystemのsuccess、clone非対応 / policy拒否の`publication_unsupported`、accepted ADR `20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`のcleanup boundaryを確認する。Linuxのanonymous FD close-only cleanup契約をmacOS laneへ共有しない。
- macOS named stagingのfinal identity checkまでに観測できるreplacement、missing、special entry、stat/open failureではunlinkせずretainし、replacement sentinelが残ることを確認する。final check後からunlinkまでの意図的same-UID replacementはaccepted ADR `20260730t085831z-adr`で限定された非保証であり、完全防御のpass条件として扱わない。

### T4 Privacy / state

- external sourceの全success/failure/warningでabsolute path、parent component、body fragment、SHA、byte countがtext/JSON/stderr/tracked fileにない。
- internal source successはrepo-relative、external successはbasenameだけ。
- unknown exceptionは`runtime_failed`へ縮退。
- durability / cleanup warningはexit 0、committed、retry不要。precommit failureはexit 1、not committed。

### T5 Opaque lifecycle / compatibility

- generic `.md` original basenameが`adr-decision.md` / `research-note.md`でもADR mirrorやtyped Artifactにならない。
- binary/invalid UTF-8 import後に`validate`、`sync --no-github`、default discoveryがpassし、bodyをopenしないtest doubleを使う。
- binary/invalid UTF-8 import後に`deps check --json`、deps derived artifact rendering、active context-pack再生成がpassし、`application/check_deps.py`、`presentation/json_state.py`、`infra/active_store.py`からgeneric bodyをopen/decodeしないことをspyで確認する。
- generic fileをauthoring contextへ明示指定した場合はbinary hashだけが生成でき、implicit source selectionやUTF-8 decodeが行われないことを確認する。
- existing `chatgpt-output`、`new artifact`、`workbench copy` suitesを変更なしまたは互換assert追加でpassさせる。

### T6 Distribution / dogfood

- candidate wheelからfresh consumerへinitしroot / future node READMEとgeneric importを確認。
- READMEなしexisting consumerへupdateしno-backfill、以後new node READMEを確認。
- `pyproject.toml`の広域nested README exclusionが除去またはexact legacy pathへ限定され、4 Workbench READMEがexcludeされないことを静的に確認。
- source / wheel / sdist / installed resourcesで、`templates/README.md`と4 hidden-directory Workbench READMEだけがREADME allowlistに一致し、全4 fileのbytesがprovider assetsと一致することを確認。
- dogfoodはprovider変更後に正式update経路でprojectionし、existing `epic-00343`へREADMEがbackfillされないことを確認。
- focused suites後に`uv run pytest`、manual external file/root/node import、fresh QA/code/spec reviewを行う。

## 13. ADR Candidates

Accepted ADR: **Generic imported-file Artifact identity and privacy boundary**

- ADR candidate: resolved by Epic-local accepted ADR。
- hard to reverse: yes。`--` filename family、full basename identity、external source非開示、postcommit retry semanticsはtracked fileとpublic CLIへ残る。
- surprising without context: yes。original basenameが`adr-*.md`でもtyped ADRではなく、SHA/countを外部source結果へ出さない。
- real tradeoff: yes。既存typed grammarへの統合より、semantic isolationとprivacyを優先する。
- Decision record: `artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md`をauthorityとし、D-006/D-008およびplanのIssue ownershipから参照する。

Accepted ADR: **macOS generic import staging cleanup trust boundary**

- Decision record: `artifacts/20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`をauthorityとし、macOS clone-capable successを維持しながら、named staging cleanupの同一UID final-window replacementだけを限定除外する。
- Mandatory mitigations: destination-parent FD identity、high-entropy `O_EXCL` / no-follow staging、held staging FD、final FD/path identity check、uncertainty時retain、non-mutating probe、commit-state保持、content-free resultを維持する。

Accepted ADR: **Linux generic import anonymous staging trust boundary**

- Decision record: `artifacts/20260730t102747z-adr-linux-anonymous-staging-trust-boundary.md`をauthorityとし、Linuxではsame-UID cleanup waiverを受容せず、linkable `O_TMPFILE` anonymous stagingとheld-FD publicationを必須化する。
- Mandatory boundary: preflightは`O_TMPFILE`、FD regularity、procfs reference、directory durabilityだけをnon-mutatingに確認する。held-FD `linkat`固有のcapability / policy failureはformal candidateへの最初のactual commitで検出し、formal entry未作成なら`publication_unsupported` / `not_committed` / `safe_after_remediation`へ正規化する。unsafe named-temp fallbackを導入せず、supported filesystem laneの縮小を明示する。

Workbench shellのfresh-only/no-backfillはrequirementで十分に固定され、独立ADRは不要である。

## 14. Risks

| Risk | 影響 | Mitigation |
|---|---|---|
| Git ignore negation誤り | READMEまでignore、またはcontents露出 | real Git repoで4 placement、nested/case-variant/near-name entriesを`git check-ignore -v`検証 |
| hidden-directory README package-data欠落 | installed consumerだけguidance shellなし | explicit package-data、広域README exclusionの限定化、4 surface exact allowlist、byte parity、candidate wheel fresh init |
| nested README広域exclude / include競合 | sourceではpassするがwheelから4 guidance fileが消える | `assets/spec_dock/templates/*/**/README.md`を残さず、exact allowlistをsource / wheel / sdist / installed resourcesで検証 |
| README内容drift | node kindごとにmodel guidanceが変わる | 4 provider assetsと生成結果のbyte parity test |
| ancestor symlink / source mutation race | 指定外file readまたはstale snapshot publish | `O_NOFOLLOW` leaf、FD identity固定、最終full reread、検出境界後のnon-cooperating in-place writeは明示的threat-model外、content-free fail |
| external path漏洩 | privacy violation | safe result object以外をrendererへ渡さず、全failure/warning snapshotでsecret path sentinel否定 |
| generic `.md` semantic誤認 | invalid UTF-8でsync失敗、ADR誤mirror | typed parserとgeneric parser分離、basename判定後のみbody read |
| family横断slot競合 | duplicate identity / overwrite risk | common name-only slot ledger、shared create lock、infra no-replace |
| filename portability差 | consumer platformごとに異なるsafe name | platform capabilityを明示したpure normalizer、NAME_MAX fixture、original保持優先 |
| root Artifact rule不整合 | rootだけauthoring guidanceなし | `docs/rules/root/artifacts.md`と初回setup symlink、root validate test |
| scanner範囲拡大 | artifact directoryが大きい場合の遅延 | direct child name/statだけ、body/MIME/archiveを読まない |
| rollback後Workbench露出 | untracked scratchが`git status`へ出る | ignore rule先行rollback、user content非削除 |
| filesystem capability不足 | supported OSでもimportが常時fail | OS名でなくFD-bound no-replace / directory durability capabilityをprobeし、supported matrixのsuccess laneとfail-closed laneを配布testで固定 |
| macOS named-staging cleanup final-window race | 同一UIDの意図的actorが別entryをunlinkさせ得る | accepted ADRでactor / pathname / time windowを限定し、high-entropy name、held FD、final identity check、uncertainty時retainを維持。untrusted same-UID共有directoryを正式supportする場合はOption B/Cを再判断 |

## 15. Requirement Clarification Requests

- blocking clarification: none。
- requirement gap: none observed。
- design-local choiceとして確定したもの:
  - public generic resultからhash/byte countを一律除外する。
  - root Artifact rulesを追加する。
  - external判定が不確かなsourceは`basename_only`へ倒す。
- resolved decision:
  - D-006/D-008の長期contractは`artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md`へ昇格し、accepted済みである。plan / IssueはこのADRを唯一のdecision recordとして参照し、候補として再判断しない。

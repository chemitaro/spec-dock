# S03 pre-step elaboration

GitHub connector で `chemitaro/spec-dock` の branch `iss-00346-integration-distribution-and-final-quality` を確認し、2026-08-02 時点の exact pushed HEAD を **`d8079e71a6e951b31d506840c3a4a130e3bdcb73`** と観測した。default branch fallback は使用していない。この commit は S02 の review Artifact と report への転記であり、S02 の未解決 P0/P1 が 0、S03 開始可であることを記録している。実装担当は最初の build/test 前に branch tip、local/remote 一致、working-tree state を再確認し、HEAD が移動していた場合は本 binding を stale として新しい candidate revision から開始する。

本資料の authority は添付された canonical `requirement.md`、`design.md`、`plan.md` であり、ここでの具体化は S03 §10.0–§10.6 を実行しやすくする補助 evidence に限る。既存 ADR、Issue 344/345 の ownership、public contract、platform trust boundary を変更しない。`unavailable`、skip、hermetic simulation は actual Linux/macOS success として数えない。   

## Step boundary and success criteria

**S03 の閉鎖対象**

| 成果物                            | 最小受入条件                                                                                                                                                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Current-head candidate receipt | 実行開始時の exact HEAD から current-cycle candidate wheel を一意に build・installし、wheel basename、distribution digest、installed origin、pre/post HEAD、clean-state判定を記録する。以前の wheel receiptはhelper・比較根拠として再利用できるが、current-cycle provenanceを黙って代用してはならない。 |
| Installed four-target evidence | candidate-wheel-installed runtimeで root / Initiative / Epic / Issue の4 targetへgeneric importを実行し、target binding、source unchanged、destination byte equality、no overwrite、`canonical=false`を確認する。                                            |
| External privacy evidence      | absolute external と nested-CWD relative externalをtext/JSONの両方で実行し、basename-only source representationと、path/body/digest/count/derived-value非開示を確認する。                                                                                       |
| Cross-filesystem evidence      | sourceとdestinationの`st_dev`が実際に異なるhost laneを少なくとも1件取得し、destination-side staging、source-device link/rename不使用、byte保持、privacy保持を確認する。利用可能なmountがなければ`unavailable`であり、S03は未閉鎖のままとする。                                                          |
| Linux host evidence            | actual supported Linux filesystemでanonymous `O_TMPFILE`、regularity、procfs identity、directory fsync、最初のactual formal no-replace link commitを確認する。visible stage/probe/pathname cleanupは0でなければならない。                                           |
| macOS host evidence            | actual clone-capable macOS destinationでdestination-side stageから`fclonefileat` no-replace commitを成功させる。cleanup uncertaintyはretain/no-unlinkとし、same-UID exclusionを超える保証を主張しない。                                                               |
| Hermetic failure evidence      | Linux capability不足とmacOS cleanup uncertaintyの既存fault hooksを再利用し、formal destination前fail-closed、no unsafe fallback、non-owned unlink不在を固定する。                                                                                                 |
| Review-ready packet            | changed-path-to-closure対応、test/host receipt、privacy matrix、`unavailable`一覧、production repair有無をcontent-freeに返す。workerはcanonical R/D/P/reportを編集しない。                                                                                        |

Canonical requirementはexternal privacy、Linux anonymous publication、macOS clone/cleanup boundary、platform honestyを独立したrequired acceptanceとして定義している。S03 closureにはhermetic Greenだけでなくactual Linux supported lane、actual macOS clone-capable lane、actual cross-filesystem evidenceが必要である。 

**Test-only 完了と production repair の判定**

* current candidate wheelが全カードを満たす場合は、S03をtest/probe-onlyで完了する。説明目的のproduction変更、共通化、refactorは行わない。
* production変更を許すのは、candidate-wheel-installed runtimeまたはactual host laneで再現するcontract defectがあり、既存allowed repair path内で根本原因を最小修正できる場合だけである。
* test harnessやoracleの誤りはtest-onlyで直し、production behaviorを変更しない。
* production/package/runtime変更でHEADが変わった場合はwheelを再buildし、S03 installed matrix、privacy、cross-FS、affected platform evidenceを新HEADで再取得する。
* required primitive、privacy contract、platform trust modelの変更が必要ならproduction workaroundを作らず、Amendment/Epic planning repairへ戻る。

Current implementationは既に4 target解決、held source lease、collision retry、`canonical=false` resultを持ち、publisherはLinux anonymous stagingとmacOS `fclonefileat`、cleanup identity checksを実装している。したがって開始時の暫定仮説は**test/probe-only completion**だが、これはcandidate-wheel実行前のinspect結果であり、Greenを意味しない。

**S02 evidence の再利用境界**

| Evidence                                                                            | S03での扱い                                                                                                              |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| S02 no-backfill、future-only shell、snapshot sensitivity、review pass                  | Upstream preconditionとして再利用する。S03がS02 helper、installer、provider assetsを変更しない限り、S02全カードの再実行は不要。                       |
| `candidate_wheel` fixture、isolated environment、installed runtime helper、node lookup | そのまま再利用し、S03 current-cycle wheelとfresh hierarchyを作る。S03専用の別build frameworkは追加しない。                                    |
| Existing CLI/publisher tests                                                        | `covered-existing` baselineとして再実行する。S03 closureに不足するinstalled-wheel matrix、actual hosts、content-free receiptだけを追加する。 |
| S01/S02の過去wheel digestやtest count                                                   | Historical evidenceとして保持するが、current S03 host receiptを閉じる値にはしない。current cycleで再確認する。                                  |
| S02 report-only successor chain                                                     | S02 closureのfreshness根拠として使用できる。S03のplatform/privacy実測結果には転用しない。                                                     |

Current integration harnessはwheel build/installとS01/S02 fixtureを既に提供しており、S03は同じfileを縦に拡張できる。

## Test-card matrix

| Test card                                                    | 前提と操作                                                                                                                                                                                                                                       | 観測・期待 oracle                                                                                                                                                                                                                                                                                                                                                                                         | 失敗時の意味                                                                                                                                                                                                                                                                                           | Closure IDs                                                                                                                                         |                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `tc-346-s03-001` — wheel-installed four-target import        | Current-cycle candidate wheelだけをinstallしたfresh consumerにInitiative/Epic/Issue hierarchyを作る。root、Initiative、Epic、Issueごとに異なるopaque payloadをpublic CLIでimportする。少なくとも1 targetでは同一timestamp slotに既存fileを置き、次slotへのno-replace allocationを発生させる。 | selectorごとの`target_kind`/`target_id`とdestination scopeが一致する。source path、identity、bytesは前後不変。destination bytesはsourceと一致。resultは`canonical=false`。既存destination bytesは不変で、新しいslotだけが作成される。JSONはexact public allowlistに一致する。                                                                                                                                                                           | Installed distributionでのselector routing gap、rootの誤node化、wrong artifacts directory、source mutation、overwrite、shared-slot regression、authority escalation。                                                                                                                                        | `CL-346-AC-007`                                                                                                                                     |                                  |
| `tc-346-s03-002` — external and nested-CWD privacy           | 無害なparent sentinel、body sentinel、path/hash/count風basenameを持つexternal sourceを作る。absolute externalとnested-CWD relative externalを、text modeとJSON modeの両方でimportする。test process内部だけでsource digestとdecimal byte countを計算する。                      | public `source`はbasename-only。scan対象はcaptured stdout/stderr、parsed JSON、import自身が作成・変更したpublic provenance fileだけ。absolute/parent path、body sentinel、内部計算digest、byte count、`sha256`/`byte_count`、MIME、encoding、content ID等が存在しない。tracked before/after manifestを取り、import以外のtracked text変更はprivacy scanへ混ぜずfixture-scope failureとする。controlled negative surfaceへ禁止sentinelを入れるとoracleが確実に失敗する。         | Public disclosure、raw exception leak、DTO再利用によるdigest/count公開、provenanceへのbody複製、scan範囲の過剰拡大またはfalse Green。privacy leakはrelease blocker。                                                                                                                                                          | `CL-346-AC-008`, `CL-346-CON-011`, `CL-346-EC-007`                                                                                                  |                                  |
| `tc-346-s03-003` — actual cross-filesystem source            | Actual host上でsourceとdestinationの`st_dev`が異なることをpreconditionとする。external sourceをcandidate-wheel-installed runtimeでrootまたはnode targetへimportする。                                                                                               | Receiptの`source_destination_same_device=false`。source identity/bytesは不変、destination bytesは一致。test-only syscall/descriptor observerでstage FDのdeviceがdestination directoryと同じことを確認する。source pathnameまたはsource device上のstageからformal destinationへのlink/renameを許さない。Linuxではformal link sourceがheld anonymous stage FDのprocfs reference、macOSではdestination-side stage FDからのcloneである。privacy oracleも同時に通る。 | EXDEV依存、source-device staging、source hard-link/rename、cross-FSをsame-device simulationで代替、path disclosure。実hostに異なるdeviceがなければ`unavailable`であり成功ではない。                                                                                                                                             | `CL-346-AC-008`, `CL-346-EC-008`                                                                                                                    |                                  |
| `tc-346-s03-004` — Linux supported anonymous publication     | Actual Linux ordinary-user lane。preflightでは`O_TMPFILE` open、anonymous inode regularity、`/proc/self/fd/<fd>` identity、destination directory fsyncだけを確認する。preflight中にlinkability probeを行わない。次にactual importを実行する。                             | Directory-entry observerを開始してから、最初のactual no-replace link対象がformal destination nameであることを確認する。precommit visible stage/probeは0、pathname unlink/cleanupは0。held anonymous FDからformal destinationへcommitし、bytes一致、source不変。collision caseではexisting fileを保持し、shared次slotへ進む。                                                                                                                             | Named temp、visible capability probe、formal commit前のpathname、非FD-bound commit、overwrite、preflightとformal commitの混同。                                                                                                                                                                               | `CL-346-AC-010`, `CL-346-CON-007`, `CL-346-EC-010`                                                                                                  |                                  |
| `tc-346-s03-005` — Linux capability-insufficient fail-closed | Preflight faultsとして`O_TMPFILE` absent/open failure、non-regular object、procfs absent/mismatch、directory fsync failureを注入する。formal-commit faultとして最初のformal linkにunsupported/policy errnoを注入する。                                               | `publication_unsupported`相当、`committed=false`、formal destination absent。visible stage/probe absent、pathname cleanup/unlink call absent、named fallback absent。raw errno message、host path、payloadはpublic outputへ出ない。preflight failureではformal commit callが0。link capability failureではcommit callがformal nameへの1回だけ。                                                                                   | Unsupported capabilityをsuccessへ降格、partial formal file、named fallback、cleanup path導入、raw error disclosure。Hermetic negativeはactual supported Linux successの代替にならない。                                                                                                                               | `CL-346-AC-011`, `CL-346-CON-007`, `CL-346-EC-009`                                                                                                  |                                  |
| `tc-346-s03-006` — macOS clone-capable success               | Actual macOS ordinary-user lane。clone-capable destination filesystemとexternal sourceを使い、可能ならsource/destination deviceが異なるcaseを選ぶ。                                                                                                           | Destination directory内にhigh-entropy、`O_EXCL                                                                                                                                                                                                                                                                                                                                                          | O_NOFOLLOW` named stageを作り、held FDでsource/stage stabilityとparent identityを確認する。formal commitは`fclonefileat` no-replace。source unchanged、destination equal、no overwrite。clone unsupported時にcopy/rename formal fallbackを行わない。cross-FSを使った場合はdevice equality booleanを記録する。owned stageだけがcleanupされる。 | Clone capability overclaim、source-link、wrong-parent commit、formal copy/rename fallback、existing destination overwrite、actual macOS不在をsimulationで代替。 | `CL-346-AC-012`, `CL-346-EC-011` |
| `tc-346-s03-007` — macOS cleanup trust boundary              | Existing cleanup hooksでmissing、replacement、unexpected path type、unexpected descriptor type、stat/fstat/open failure、reopen後replacement、final-check uncertaintyを注入する。clean owned-stage caseも保持する。                                             | Uncertaintyはすべて`cleanup_state=retained`かつunlink call 0。unlinkはheld stage、reopened FD、final pathが同一regular objectである最終確認を通ったowned stageだけに実行する。evidence文言はsame-UID actorによるfinal-check-to-unlink間の置換をaccepted exclusionとして明記し、それを防止したと主張しない。                                                                                                                                                          | Non-owned unlink、missingをremoved扱い、type/identity uncertaintyの無視、ADRを超える安全保証。                                                                                                                                                                                                                     | `CL-346-AC-012`, `CL-346-CON-008`, `CL-346-EC-012`                                                                                                  |                                  |

Existing focused testsには4 target、nested-CWD external、collision、Linux anonymous staging/fail-closed、cleanup uncertainty、public JSON allowlistの多くが既にある。S03では期待値を再実装せず、installed-wheelとactual-hostの不足分を追加し、既存fault hooksの感度を維持する。

**共通 public-output oracle**

JSON successの許可keyは現行contractどおり、`status`、`import_kind`、`storage_identity`、`target_kind`、`target_id`、`artifact_id`、`source_visibility`、`source`、`destination`、`committed`、`publication_state`、`cleanup_state`、`warning_codes`、`retry_disposition`、`canonical`に限定する。text outputは同じcommand-specific public semanticsだけを許し、dynamic valueは既存のcontrol-safe表現に従う。`sha256`、`byte_count`、MIME、encoding、adoption/review authorityはgeneric import resultへ追加しない。

Generic destination body、canonical requirement/design/plan/report、candidate wheel receipt、wheel distribution digestはexternal privacy scan対象外である。source/destinationのbyte equality、source digest、byte countはtest process内assertionにだけ使い、receiptには`bytes_matched=true`、`source_unchanged=true`のようなcontent-free booleanを残す。

## Host-evidence receipt

Actual host receiptはprobeごとに一意にし、少なくとも次のfieldsを持たせる。

| Field                                | 内容と制約                                                                                             |
| ------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `repository`                         | `chemitaro/spec-dock`                                                                             |
| `branch`                             | `iss-00346-integration-distribution-and-final-quality`                                            |
| `candidate_revision`                 | wheel/runtimeを生成したexact 40-hex revision。実行前後で同一でなければreceiptはstale。                                |
| `wheel_basename`                     | basename-only。host-local wheel pathは保存しない。                                                        |
| `wheel_distribution_sha256`          | candidate distribution identity。external user fileのdigestではない。                                    |
| `platform`                           | `linux` または `macos`                                                                               |
| `os_release`                         | 公開可能なOS version。hostnameは含めない。                                                                    |
| `kernel_release`                     | Linuxではkernel release、macOSで不要なら`not_applicable`。                                                 |
| `python_version`                     | `major.minor.patch`。                                                                              |
| `execution_kind`                     | `host` または `container`。                                                                           |
| `container_image_digest`             | Linux containerならresolved `sha256:...`。mutable tagだけは禁止。host実行は`not_applicable`。                  |
| `ordinary_user`                      | boolean。root/elevated権限でしか成功しないlaneはrequired ordinary-user evidenceを閉じない。UIDやusernameは保存しない。      |
| `destination_filesystem_type`        | filesystem typeだけ。volume名、mount pathは保存しない。                                                       |
| `source_destination_same_device`     | actual source/destinationのdevice equality boolean。cross-FS receiptでは必ず`false`。device番号そのものは保存しない。 |
| `capabilities`                       | 下記platform-specific boolean map。                                                                  |
| `command`                            | repository-relativeで再現可能なcommand。temporary checkout、venv、mountの展開後absolute pathを含めない。             |
| `test_node_or_probe_id`              | pytest node IDまたはversion管理されたprobe ID。                                                            |
| `exit_status`                        | `0` success、`1` test/contract failure、`77` capability unavailable。                                |
| `result`                             | `pass` / `fail` / `unavailable`。`77`は必ず`unavailable`でありpassではない。                                  |
| `result_evidence_ref`                | Issue report rowまたはexternal receipt IDへのcontent-free linkage。                                     |
| `observed_at`                        | 実測時刻。candidate revision freshness判定に使用する。                                                         |
| `bytes_matched` / `source_unchanged` | 値を保存せずbooleanだけを記録する。                                                                             |

**Linux capability booleans**

* `o_tmpfile_openable`
* `anonymous_stage_regular`
* `procfs_identity_matches_held_fd`
* `destination_directory_fsync_succeeds`
* `formal_no_replace_link_succeeds`
* `first_link_target_is_formal_destination`
* `visible_stage_or_probe_absent`
* `pathname_cleanup_absent`
* `existing_destination_preserved`

`formal_no_replace_link_succeeds`はpreflightで推測しない。`linux-supported-publication`の最初のactual formal commitによってのみ確定する。

**macOS capability booleans**

* `fclonefileat_available`
* `destination_clone_capable`
* `stage_is_destination_side`
* `stage_opened_exclusive_nofollow`
* `parent_identity_stable`
* `formal_no_replace_clone_succeeds`
* `copy_or_rename_fallback_absent`
* `owned_stage_cleanup_verified`
* `uncertain_stage_retained_without_unlink`
* `same_uid_exclusion_acknowledged`

Receipt、report、Artifactにはhost-local absolute path、hostname、username/UID、volume名、source basename以外のprivate source path、payload content、user-file digest、user-file byte countを保存しない。Canonical receiptとhost-honesty contractはこのcontent-free分離を要求している。 

## Worker sequence and file boundary

1. **Exact-head rebind**
   Branch tip、local HEAD、remote HEAD、working treeを確認する。current observed headは`d8079e71a6e951b31d506840c3a4a130e3bdcb73`だが、実行時に異なれば新HEADをcandidate revisionとする。build中またはhost test中にHEADが変わった場合は、そのcycleのevidenceを破棄する。

2. **Current-cycle wheelを既存fixtureで生成**
   `tests/integration/test_epic_00343_distribution.py`の`candidate_wheel` fixtureとIssue 69 harnessを再利用する。build helper、venv installer、runtime origin checkを複製しない。S03 testsは同じwheel pathをdigest、install、target/privacy matrixへ渡す。

3. **Installed integration cardsを先に追加**
   同じintegration fileへ`tc-346-s03-001`〜`003`を追加する。S01 fresh hierarchy helperを再利用し、4 target、external absolute、nested-CWD relative、text/JSON、cross-FSをrisk-basedに割り当てる。全Cartesian productや新しいsnapshot frameworkは作らない。

4. **Version管理されたhost probeを追加**
   `tests/integration/iss346_platform_probe.py`へ、計画済みprobe IDだけを実装する。probeはinstalled runtimeのactual primitiveを呼び、receipt用content-free JSONまたは終了状態を返す。production codeへtest mode、environment-driven behavior branch、receipt-specific APIを追加しない。

   Planned probe IDs:

   * `linux-capability-preflight`
   * `linux-supported-publication`
   * `linux-capability-insufficient`
   * `macos-capability-preflight`
   * `macos-clone-publication`

5. **既存unit/fault hooksで不足分だけ補う**
   `stage_barrier`、`fault_injector`、`_commit_descriptor_no_replace` wrapper、`os.open/stat/fstat/fsync/link/unlink` observersをtest-onlyで再利用する。Linux preflight/formal commit分離、macOS uncertainty matrix、visible entry/no-cleanup sensitivityに既存coverageがあるため、同じbranchを重複実装しない。

6. **Hermetic/focused verificationを実行**

```text
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py \
  -k 'explicit or privacy or cross or linux or macos or publication or cleanup'

uv run pytest tests/cli_runtime/test_artifact_import_file.py

uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 's03 or target_matrix or external or cross_filesystem or linux or macos' \
  --run-full-regression
```

7. **Actual host lanesを実行**

```text
ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-capability-preflight

ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-supported-publication

ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-capability-insufficient

ISS346_PLATFORM_DEST="$ISS346_MACOS_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe macos-capability-preflight

ISS346_PLATFORM_DEST="$ISS346_MACOS_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe macos-clone-publication
```

Expanded environment valuesやabsolute pathsはreceiptへ保存しない。required Linux/macOS hostまたはactual cross-FS sourceが得られない場合は`unavailable`として停止し、hermetic GreenだけでS03 closureやreview passを要求しない。

8. **Greenまたはroot-cause repairを分類**
   全実装が既存contractを満たす場合はtest-only candidateとする。欠陥が出た場合は、次のowner surface単位で1 root-cause familyずつ分離する。

| Root cause                                                           | Repair owner                                             |
| -------------------------------------------------------------------- | -------------------------------------------------------- |
| target解決、setup binding、collision retry、result assembly               | `application/import_file_artifact.py`                    |
| anonymous staging、clone、no-replace、cleanup、capability classification | `infra/binary_artifact_publisher.py`                     |
| public text/JSON field leak                                          | `presentation/cli_text.py`、必要な最小contract/command surface |
| filename allocation/no-overwrite                                     | `domain/artifacts.py`と直接のapplication caller              |
| ports/wiring不備                                                       | `application/ports.py`                                   |
| test oracle defect                                                   | testsのみ                                                  |

9. **Fresh pushed-head review packetを返す**
   changed files、exact test nodes、host receipt、`pass/fail/unavailable`、privacy boolean matrix、production repair有無、remaining limitations、`No material implementation decisions beyond the approved plan.`またはmaterial Ledger Noteを返す。canonical reportへの転記はorchestratorが行う。

**Allowed primary paths**

* `tests/integration/test_epic_00343_distribution.py`
* `tests/integration/iss346_platform_probe.py`
* `tests/cli_runtime/test_artifact_import_file.py`
* `tests/unit/infra/test_binary_artifact_publisher.py`
* `tests/unit/application/test_import_file_artifact.py`
* `tests/unit/application/test_binary_artifact_import_ports.py`
* `tests/unit/commands/test_artifact_import_file.py`
* `tests/unit/presentation/test_artifact_import_file.py`

**Repair-only paths**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`

列挙外path、新command、新target type、visible fallback、broad privacy sanitizer、Linux/macOS algorithmの統合refactorは提案・実装しない。

## Review gate and stop conditions

**P0 観点 — 即時停止**

| 観点               | Blocker condition                                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Privacy          | stdout/stderr、JSON、public provenanceにexternal absolute/parent path、body、user-file digest/count、derived contentが出る。漏えい値そのものをreview/reportへ転載してはならない。 |
| Data integrity   | sourceが変更・削除される、existing destinationが上書きされる、failed resultなのにformal destinationが残る。                                                                  |
| Linux safety     | named/visible stage、visible linkability probe、pathname cleanup fallback、source pathnameからのformal link、non-FD-bound overwrite可能commitがある。            |
| macOS cleanup    | owned identityを確定できないstageやreplacementをunlinkする。                                                                                                    |
| Platform honesty | simulation、skip、`unavailable`をactual Linux/macOS/cross-FS successとして記録する。                                                                           |
| Evidence binding | wheel/runtime/test/host receiptが異なるcandidate revisionを無表示で混在させる。                                                                                    |

**P1 観点 — closureを止める**

| 観点                       | Blocker condition                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| Test completeness        | 4 targetのいずれか、text/JSONのいずれか、absolute/nested-CWDのいずれかが欠ける。                                            |
| Oracle sensitivity       | privacy negativeが禁止値を検出できない、aggregate assertionが1 targetの誤配置を見逃す、collision testがexisting bytesを確認しない。 |
| Cross-FS validity        | device equalityを測定しない、実際はsame-deviceなのにcross-FSと表現する、stage deviceを確認しない。                              |
| Linux phase split        | preflightでlinkabilityをvisible/probe nameにより確認する、formal commitより前にlinkを実行する。                           |
| macOS assurance          | same-UID exclusionを省略する、accepted ADRより強い保護を主張する、clone unsupportedをcopy/rename successへ降格する。           |
| Receipt hygiene          | host-local path、payload、user-file digest/count、mutable container tag、UID/usernameを保存する。               |
| Scope                    | allowed paths外の変更、canonical R/D/P/reportのworker編集、Issue 344/345 behaviorの再設計。                         |
| Production contamination | test専用environment branch、probe hook、instrumentationをproductionへ残す。                                    |
| Regression weakening     | 既存expectationを削除・緩和してGreenにする、legacy behaviorをS03都合で変更する。                                             |

**Stop / Amendment routing**

| Trigger                                               | 必須処置                                                                                                                                                |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Privacy leakまたはunsafe fallback                        | 即時停止。漏えいclassとsurfaceだけを記録し、最小root-cause repairを別batchにする。修正後はnew HEADでwheel、privacy、host evidence、reviewを再取得する。                                    |
| Required Linux/macOS host unavailable                 | `unavailable` receiptを残し、S03をopen/blockedのままにする。別platformの成功やhermetic testsで補完しない。                                                                  |
| Actual cross-FS source unavailable                    | `source_destination_same_device=true`の実行をcross-FS successとしない。actual falseのreceiptを取得するまでclosureしない。                                                |
| Accepted primitiveがrequired hostsで実行不能                | named fallbackやstronger trust claimを作らず、Epic planning repair / ADR clarificationへ戻る。                                                                |
| New public field、command、target、platform semanticsが必要 | Issue-local repairを止め、Amendment対象とする。                                                                                                               |
| Source-device link/renameが必要                          | 実装を止める。canonical destination-side staging contractとの矛盾としてEpic planning repairへ送る。                                                                   |
| Allowed path外変更またはcanonical docs変更                    | 変更を分離・撤回し、scope amendmentなしでは継続しない。                                                                                                                 |
| Test-only production branch検出                         | branch/instrumentationを除去し、実際のpublic behaviorからtestsを再実行する。                                                                                         |
| HEAD移動                                                | 旧candidate receiptとaffected evidenceをstale化し、新HEADから再開する。                                                                                           |
| Review P0/P1                                          | findingをorchestratorが採否判定し、accepted blockerだけをbounded repairする。push後のexact headに同じsecurity/platform focusで再reviewする。P2/P3だけをscope expansionの理由にしない。 |

S03 review passは、全hermetic tests Green、actual Linux supported receipt、actual macOS clone receipt、actual cross-FS receipt、privacy leak 0、unsafe fallback 0、changed paths bounded、exact pushed headに対する未解決P0/P1 0のすべてが揃った場合だけ成立する。

## Open uncertainties

| 不確実性・未検証主張                               | 現在の状態                                                                                                  | 解消条件                                                                                                              |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Execution-time branch tip                | Elaborate時点では`d8079e71a6e951b31d506840c3a4a130e3bdcb73`。以後の移動有無は未検証。                                   | worker開始時と各host lane前後に再確認する。                                                                                     |
| Current-cycle wheel provenance           | Existing harnessと過去receiptはあるが、S03 exact current-cycle wheelはまだbuildされていない。                            | current candidate revisionでbuild/install/digest/origin receiptを取得する。                                              |
| `iss346_platform_probe.py`               | Current pushed headにはまだ存在しない。                                                                          | allowed path内へ最小probeを追加し、named probe IDsを固定する。                                                                   |
| Actual Linux capability                  | `O_TMPFILE`、procfs identity、directory fsync、formal linkabilityのcurrent host結果は未取得。                     | ordinary-user actual Linux supported probeを0で完了する。                                                                |
| Actual macOS capability                  | clone-capable destinationと`fclonefileat` successは未取得。                                                  | ordinary-user actual macOS hostでclone publicationを成功させる。                                                          |
| Actual cross-filesystem availability     | 異なる`st_dev`を持つsource/destination pairの利用可否は未確認。                                                        | device equality `false`のactual receiptを取得する。                                                                      |
| Public provenance fileの有無                | Current generic importがprovenance fileを変更するとは確認されていない。                                                 | tracked before/after manifestでimport-owned provenanceを列挙する。0件なら空集合を記録し、canonical docsやdestination bodyをscanへ含めない。 |
| Production defectの有無                     | Source inspectionでは明白なdefectを確認しておらず、test-only completionが有力。ただしactual candidate/host execution前の暫定判断。 | 7 cardsとactual host lanesの結果で確定する。                                                                                |
| S02で記録されたIssue 345 docs-boundary failure | S02 changed paths外の既存failureとして記録されており、S03 target/privacy/platform sliceのownerではない。                    | S03へ吸収しない。S03変更が同failureへ新たな影響を与えた場合だけ別途scope判定する。                                                                |
| same-UID cleanup window                  | Accepted macOS trust boundaryとして意図的に残る。                                                                | S03で解消済みと表現しない。将来変更するならIssue-local repairではなくADR/Epic planning対象とする。                                              |

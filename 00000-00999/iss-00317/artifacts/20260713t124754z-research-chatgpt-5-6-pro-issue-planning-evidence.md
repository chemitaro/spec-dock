# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a54d7e7-63b0-83ee-887d-e9fa0dce45e4

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00317-byte-preserving-chatgpt-output-artifact-import
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached planning brief as the task contract. Inspect the GitHub current branch first, then analyze the attached repository evidence and return the requested Japanese Issue planning candidates.

## Answer

repository_access: success

## REQUIREMENT_CANDIDATE

**候補状態:** `draft`
**対象:** `iss-00317` / GitHub Issue #317
**推奨 Issue Grade:** `standard`。ただし、canonical `requirement.md` 具体化後の `assurance classify` を権限根拠とする。
**基準リビジョン:** current branch `iss-00317-byte-preserving-chatgpt-output-artifact-import`、指定HEAD `5e8d122914be1e043ed85ff8a16a99753a7082b8`。当該HEADはGitHub connectorで取得できた。

本候補は添付 planning brief をtask contractとして作成した、コード未変更のevidence-only候補である。canonical採用、reviewer pass、execution readiness、Issue完了は主張しない。

### 1. 目的

Workbench内の利用者指定single `.md` regular fileを、sourceを残したまま、内容bytesを一切変更せず、指定Initiative/Epic/Issueの`artifacts/`へ明示的にimportする。

Importはtemplate-based `new artifact`とは別経路とし、既存Artifactを上書きせず、temporary fileへのbinary copy、SHA-256・byte count・source stability確認を完了したfileだけを正式Artifact pathへpublishする。Imported fileはevidence-onlyであり、command成功、filename、本文によってcanonical authority、accepted ADR、reviewer passを獲得しない。

### 2. 現在状態と依存関係

GitHub Issue #315と#316は`closed/completed`、#317は`open`である。

Issue 317 nodeのformal dependencyは`iss-00315`であり、これは親Epicの「W1完了後にW2とW3を並行可能」とする依存と整合する。Issue 316はformal dependencyではないが、現branch上で利用可能なpath guard、filesystem error、provider/dogfood実装パターンを提供する先行実装証跡として扱う。Issue 317の`requirement.md`は未具体化scaffold、`design.md`と`plan.md`は`awaiting-assurance-compose` placeholderであるため、実装前にrequirement具体化、assurance classification、profile-aware composeを順に完了する必要がある。

### 3. 親traceability

| 親契約                     | Issue 317で閉じる範囲                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------- |
| `E-RQ-019`              | Explicit and separate `artifact import`。自動import、background処理、`new artifact`のmode追加を禁止                          |
| `E-RQ-020`              | Current worktreeのroot/scoped Workbenchにあるsingle regular `.md`、copy-not-move、symlink/directory/outside rejection |
| `E-RQ-021`              | Bytes opaque、no frontmatter/template/format/encoding/newline conversion、SHA-256とbyte count確認                    |
| `E-RQ-022`              | Existing blank filename grammar、`chatgpt-output-<slug>`、collision suffix、no overwrite、no prefix reservation     |
| `E-RQ-023`              | Temporary copy、verified publication、pre-commit cleanup、post-commit warning semantics                            |
| `E-AC-013`              | Byte identityとsource survival                                                                                   |
| `E-AC-014`              | Blank grammar coexistence、collision、generic validation                                                          |
| `E-AC-015`              | Path、mutation、hash、fsync、publish、cleanup fault matrix                                                           |
| `DS-003` / W3           | CLI/application/domain/infra/presentationとfocused tests                                                         |
| `E-RQ-024` / `E-AC-016` | 本Issueでは「authorityを自己主張しない」「EALを自動編集しない」境界だけを守る。Workflow implementationはIssue 318                               |

親Epicは、`chatgpt-output`をArtifactのtyped storage tokenではなくimport operation kindとし、保存先をexisting blank grammarにすることを固定している。

Accepted ADRは、standard filenameを`<ts>-chatgpt-output-<slug>.md`、collision filenameを`<ts>-<nn>-chatgpt-output-<slug>.md`とし、parser上のArtifact identityはblankのtimestampまたはtimestamp-suffixとする。`new artifact blank --slug chatgpt-output-*`は禁止せず、creation routeはfilenameから推測しない。

### 4. Actorと代表シナリオ

| ID           | Actor                         | Trigger                                                      | 期待結果                                                                 |
| ------------ | ----------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------- |
| `SC-317-001` | Human operator / orchestrator | Rootまたはscoped Workbenchのfileを指定してimport                      | Bytesが同一のblank Artifactが作成され、sourceが残る                               |
| `SC-317-002` | Human operator / orchestrator | Sourceとは異なるscopeをdestinationに指定                              | Source provenanceとdestination scopeを独立して扱い、指定scopeの`artifacts/`へ保存   |
| `SC-317-003` | Runtime                       | 同一秒に`new artifact`または別importが実行される                           | Shared lockとexisting suffix grammarにより別IDを割り当て、既存fileを変更しない          |
| `SC-317-004` | Filesystem / fault injector   | Copy、hash、file fsync、source mutation、publish前cleanupでfailure | Formal Artifactを公開せず、command自身はsourceを変更しない                          |
| `SC-317-005` | Filesystem / fault injector   | Publish後にdirectory fsync、temp unlink、lock release等が失敗        | Committed pathを明示したwarningを返し、retry-safeな未commit failureに見せない        |
| `SC-317-006` | Validator / sync              | Import済みno-frontmatter fileを含むtreeをvalidate/sync             | Blank filenameとして検証し、本文をparseせず、ADR mirrorやcanonical authorityへ昇格しない |

### 5. 観測可能な成果

完了後、次を観測できる。

* `spec-dock artifact import chatgpt-output ...`という独立command surface。
* Exactly one destination scopeと、caller-specified source file。
* Repo-relative source/destination path、blank Artifact ID、SHA-256、byte count、commit/warning stateを含むcontent-free result。
* Source、staged copy、formal destinationのbytesとhashの一致。
* Success後もsource path、source bytes、source mode、source mtimeが保持される。Filesystem readに伴うatime変更は保証対象外。
* Existing Artifact、canonical docs、accepted ADR、`report.md` EAL、`.assurance.json`がcommandによって変更されない。
* `validate`がimported fileをexisting blank filenameとして受理する。
* `sync`、tree、index、contextが本文をcanonical inputとして扱わない。
* Filename内の`chatgpt-output`だけではimported outputとtemplate-created blankを区別できない。

次を観測できてはならない。

* Sourceのmove、rename、unlink、truncate、chmod。
* Frontmatter、template text、BOM、newline、encoding、final newlineの変更。
* Existing destinationのoverwrite。
* Hash不一致fileまたはcopy途中fileのformal Artifact公開。
* `new artifact chatgpt-output` type、typed parser branch、blank prefix reservation。
* Body、secret-like value、absolute host path、raw `OSError`のtext/JSON出力。
* Import成功をcanonical adoptionやreview passとして示すfield。

### 6. Scope

#### In scope

* Provider-side parser、registry、command、application request/result/error、ports、infra binary publisher、presentation。
* Independent `ImportArtifactRequest` / `ImportArtifactResult` use case。
* Existing Artifact scope resolution、rules setup、clock、blank allocator、duplicate scanner、create lockの再利用または意味論不変の最小共有化。
* Approved Workbench placement、regular-file、symlink、alias、containment preflight。
* Binary streaming、SHA-256、byte count、source-stability、temporary-file、file fsync、atomic no-replace publish。
* Collision、concurrency、pre-commit cleanup、post-commit warning。
* `new artifact`、generic validation、sync projection、ADR mirrorのfocused regression。
* Command-local help/text/JSON。
* 必要最小限のprovider→dogfood projection確認と、Issue 319向けrelay evidence。

#### Out of scope

* PDF、image、ZIP、directory、bundle、multiple files、raw conversation transcript。
* `RawCaptureBundle`、capture catalog、hash database、manifest、sidecar、receipt、TTL、retention、orphan-temp GC。
* Content classifier、Markdown parser、UTF-8 validator、MIME detection、secret scanner。
* Workbench outsideのarbitrary host path。
* Automatic import、watcher、workflow enforcement、canonical promotion、EAL自動編集。
* Issue 318が所有するfile/inline/ZIP decision workflow、skills、preservation status。
* Issue 319が所有するpackage data、fresh init/update、最終public docs、full parity/full suite、Epic PR。
* DevCoder/reviewer model configurationの追加変更。

#### Must not change

* `new artifact` direct/routing catalogとtemplate routing。
* `chatgpt-output-*` blank slugの有効性。
* Existing typed/blank parser precedence。
* Existing Artifact IDと`01..99` collision grammar。
* Issue 315のWorkbench opacity。
* Top-level `import initiative|epic|issue`のnode-import semantics。
* Existing ADR mirror eligibility contract。

### 7. Issue requirements

**RQ-317-001 — Separate explicit command.**
`artifact import chatgpt-output`を追加し、`new artifact`のmode、flag、source optionとして実装しない。Commandは明示実行時だけ作動する。

**RQ-317-002 — Command input.**
Inputは`import_kind=chatgpt-output`、exactly one scope selector、`--file`、`--title`、optional `--slug`、optional `--json`に限定する。`--move`、`--overwrite`、`--dest`、`--encoding`、`--template`、`--frontmatter`を設けない。

**RQ-317-003 — Approved source placement.**
Sourceはcurrent repository/worktree内の次のいずれかとする。

1. `<specdock_dir>/.workbench/**`
2. Resolved Initiative/Epic/Issue directoryのdirect child `.workbench/**`

Source Workbenchのscopeとdestination scopeは一致を要求しない。`--file`はdestination scopeから推定せず、callerが指定する。

**RQ-317-004 — Source kind and path safety.**
Sourceはexact lowercase `.md` suffixを持つsingle regular non-symlink fileとする。Repository rootからWorkbench rootおよびsource parentまでのexisting ancestorをcomponent-wise `lstat`し、symlink、non-directory、lexical escapeを拒否する。Directory、FIFO、socket、device、broken link、symlinked ancestorはread開始前にfailする。

**RQ-317-005 — Source/destination non-aliasing.**
Sourceのfilesystem identityがtarget scopeのexisting formal Artifactと同一である場合はrejectする。Staged temporary inodeはsource inodeと異ならなければならず、formal destinationはstaged fileからpublishし、source inodeから直接linkまたはrenameしてはならない。

**RQ-317-006 — Opaque bytes.**
Sourceをbinary streamとして扱う。Valid UTF-8を要求せず、BOM、NUL、invalid UTF-8、CRLF/LF、no-final-newline、zero-byteを変換・拒否しない。Markdown/frontmatter/authority claimをparseしない。

**RQ-317-007 — Blank naming and coexistence.**
Existing slug normalizationを使い、base slugからblank slug `chatgpt-output-<base-slug>`を生成する。Allocatorには`artifact_type="blank"`を渡す。`chatgpt-output`を`SUPPORTED_ARTIFACT_TYPES`へ追加せず、`new artifact blank --slug chatgpt-output-*`を許容し続ける。

**RQ-317-008 — Shared creation serialization.**
Importと`new artifact`は同一create lockを共有する。Filename stateのscanとallocationはlock内で行う。Current `new artifact`がlock取得前にallocationしたcandidateをそのまま使う構造は、concurrent import/new collisionを安全にsuffix allocationできるよう、意味論不変の最小共有化またはlock内再allocationへ修正する。

現実装では`create_artifact_doc`がdestinationをlock取得前にallocationし、lock内では同じpathの存在を再確認しているため、shared lockだけではimportが先に同じslotを取った場合のreallocationを保証できない。これはIssue 317で閉じるべき実装上のraceである。

**RQ-317-009 — Verified staging.**
Same-directory exclusive temporary fileへbinary copyする。Source pre-hash、copy-stream hash、temporary reread hash、source post-hash、全byte countを比較する。Source path identity、device/inode、regular-file mode、size、mtime_nsをpublish直前まで再確認する。

**RQ-317-010 — Atomic no-replace publication.**
Final pathが存在しない場合だけ、verified staged bytesを一操作で公開する。Overwrite可能な`os.replace`、`Path.replace`、check-then-replace fallbackは禁止する。`EEXIST`はexisting fileを触らず、lock内でstateを再scanして次suffixをboundedにallocateする。

**RQ-317-011 — Failure, cleanup, and warning boundary.**
Publish前failureではformal destinationを残さず、owned tempをcleanupする。Import codeは全経路でsourceにdestructive operationを行わない。Publish後のdirectory fsync、temp cleanup、post-write confirmation、create-lock release failureはfinalをrollbackせず、`committed=true`とrepo-relative committed pathを持つwarningとして返す。

**RQ-317-012 — Result and authority isolation.**
Resultはimport kind、storage artifact type `blank`、Artifact ID、scope ID、repo-relative source/destination、SHA-256、byte count、commit/durability/cleanup statusを返す。Body、absolute host path、canonical/adopted/reviewed claimを返さない。CommandはEAL、canonical docs、accepted ADR、assurance stateを編集しない。

**RQ-317-013 — Validation, sync, tree, context, and ADR behavior.**

* Generic validationとduplicate detectionではexisting blank Artifactとして扱う。
* Body/frontmatter validityを要求しない。
* `sync`のnode projectionにbodyまたはimport provenanceを追加しない。
* Current tree/index/contextのnode-centric behaviorを変更しない。
* Existing generic Artifact listingが存在する場合は`blank` ID/pathとして扱い、filenameからimport routeを推測しない。
* Typed `adr`でないためADR mirror sourceにしない。

Current validatorは`scan_artifact_duplicate_state()`だけを呼び、Artifact bodyを読まない。 Current ADR collectorはfilenameがtyped `adr`と解析できたfileだけをfrontmatter検査へ進めるため、blank importはmirror対象外となる。 Current JSON projectionは`future_artifacts`のdirectory path/presenceだけを出し、file bodyやfile catalogを追加しない。

**RQ-317-014 — Provider authority and bounded delivery.**
Primary implementationは`src/spec_dock/assets/spec_dock/**`に置く。`spec-dock/**`はnormal projectionによるconsumer/dogfood確認面とし、dogfood-only implementationを禁止する。Final package/init/update/docs/parity/full-quality/PRはIssue 319へrelayする。

**RQ-317-015 — No new managed state.**
New dependency、database、schema、catalog、manifest、transaction journal、background process、recovery daemonを追加しない。処理量はfile bytesに対して線形とし、whole-file memory bufferingを要求しない。

### 8. Acceptance criteria

| ID           | 前提・操作                                                                                                                                         | 期待結果・観測点                                                                                                     |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `AC-317-001` | Help/parseで`artifact import chatgpt-output`を実行                                                                                                | Exactly one scope、file、titleを要求。`new artifact` catalog/help/templateは不変。Top-level node `import`も不変           |
| `AC-317-002` | Repo-relative/absolute pathでroot/scoped Workbench fileを指定。Source scopeとdestination scopeを変える                                                  | 指定destinationへ保存。Source locationをdestinationから推定しない。Sourceは残る                                                |
| `AC-317-003` | LF、CRLF、UTF-8 BOM、no-final-newline、日本語、NUL、invalid UTF-8、arbitrary bytes、zero-byte fixtureをimport                                             | Source/pre-hash/copy/temp/post-hash/finalのSHA-256とbyte countが一致。Valid UTF-8を要求しない。Frontmatter/templateなし     |
| `AC-317-004` | Same timestampでimportと`new artifact blank --slug chatgpt-output-*`を作成                                                                         | 両方がexisting blank grammarでvalid。Prefix reservationなし。Parserは両者を`blank`として扱う                                  |
| `AC-317-005` | Two imports、import対new artifact、external writerのexact-path raceを注入                                                                            | Shared lockまたはatomic `EEXIST` handlingで別slotへallocate。Existing bytesは不変。`01..99` exhaustionでno-write failure |
| `AC-317-006` | Missing、outside Workbench、`.MD`、directory、special file、source symlink、ancestor symlink、target artifacts symlink、source/formal hard-link alias | Read/copy/publish前にstable content-free failure。External sentinelとexisting Artifactは不変                        |
| `AC-317-007` | Same-size mutation、source replacement/unlink、temp create/write、hash mismatch、file fsync、pre-publish cleanup faultを注入                          | Formal Artifactなし。Command自身はsourceを削除・変更しない。Owned temp cleanup stateを明示                                      |
| `AC-317-008` | Publish後のdirectory fsync、temp unlink、post-write scan、lock release faultを注入                                                                    | Finalを残し、committed path/hash/bytesとwarningを返す。Outputはretry-safe failureを示さない                                 |
| `AC-317-009` | Import後に`validate`、`sync`、tree/index/context、ADR mirrorを実行                                                                                    | Blank filename/duplicate validation pass。Bodyをparseしない。Node projectionにbodyなし。ADR mirrorなし                   |
| `AC-317-010` | Bodyに`authority: accepted`、`canonical`、`reviewer pass`等を含め、import前後のcanonical docs/EAL/assuranceをsnapshot                                     | Body claimからauthorityを得ず、snapshot不変。Text/JSONにbody、absolute path、raw errorなし                                 |
| `AC-317-011` | Provider focused tests、normal dogfood projection、manual Workbench→Artifact scenarioを実施                                                        | Focused evidenceとIssue 319 relay packageをreportに残す。Package/fresh init/update/full parity/PRを完了したとは扱わない       |

### 9. Exception and boundary cases

| ID           | 条件                                                            | 期待される扱い                                                                               |
| ------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `EC-317-001` | Relative source path                                          | Repository root基準でlexical normalizationし、approved containmentを確認                      |
| `EC-317-002` | Absolute source path                                          | Current repository内かつapproved Workbench placementの場合だけ許可                              |
| `EC-317-003` | Sourceとdestinationのscopeが異なる                                  | 許可。Source provenance boundaryとformal storage scopeは独立                                 |
| `EC-317-004` | `.MD`、`.markdown`                                             | Reject。MVP suffixはexact `.md`                                                         |
| `EC-317-005` | Empty file                                                    | Accept。Bytes opaqueでありcontent classifierを持たない                                         |
| `EC-317-006` | Sourceがexisting formal Artifactへのhard link                    | Alias rejection。既存formal Artifactを再import sourceとして扱わない                               |
| `EC-317-007` | Sourceがcopy中に同sizeで変更されmtimeを戻される                             | Pre/copy/temp/post hash mismatchで検出。元bytesへ完全に戻り全hashが一致した場合、保存bytesはpre-hashと同一なので許容 |
| `EC-317-008` | `artifacts/`またはscope ancestorがsymlink/non-directory           | Formal write前にfail                                                                    |
| `EC-317-009` | Publish時`EEXIST`                                              | Tempを保持したままrescan/reallocateし、bounded retry                                           |
| `EC-317-010` | Suffix `01..99` exhausted                                     | Existing stateを変更せずfailure                                                            |
| `EC-317-011` | Pre-commit temp cleanup failure                               | Formal pathなし。Cleanup-pendingをcontent-free errorで示し、自動GCは作らない                         |
| `EC-317-012` | Post-commit temp cleanup/directory fsync/lock release failure | `committed_with_warning`。Final rollbackなし                                             |
| `EC-317-013` | Process crash before publish                                  | Non-`.md` orphan tempが残り得る。Validator対象外。Automatic recovery/GCなし                       |
| `EC-317-014` | Platformにatomic no-replace primitiveがない                       | Unsafe fallbackを使わず`publication_unsupported` failure                                  |
| `EC-317-015` | Bodyがvalid Markdownでない、frontmatter-like、ADR-like              | Accept。Storage identityはblank、authorityはevidence-only                                 |

### 10. Compatibility, security, privacy

* Migration、existing Artifact rewrite、existing Workbench変換は行わない。
* Existing `new artifact`、validate、sync、ADR mirrorのpublic semanticsを維持する。
* Imported bytesは将来Git管理対象になり得る。Commandはsecret scannerを持たないため、operatorがimport前に内容のcommit適格性を判断する。
* Helpには「内容安全性を検査しない」「evidence-only」「sourceをcopyする」「canonical adoptionではない」を明示する。
* Error/outputにはbody、hash対象bytes、raw `OSError`、absolute download pathを含めない。
* Filesystem metadata、owner、ACL、xattr、source atime、device semanticsのfidelityは保証しない。契約対象はfile body bytesである。
* Power-loss完全durability、全TOCTOU排除、distributed lockingは保証しない。

### 11. Assumptions, risks, uncertainties

**仮定**

* Planning briefの「caller-specified source path」は、sourceをdestination scopeから推定しないという意味で採用する。一方、accepted parent requirement/ADRがsourceをcurrent worktreeのroot/scoped Workbenchへ限定しているため、arbitrary repository/host pathへは拡張しない。
* Relative pathとabsolute pathの双方を、同じcontainment policyの下で許可する。
* Zero-byteとinvalid UTF-8を受理する。これはopaque bytes契約から導く。
* `--slug`は`chatgpt-output-`を含まないbase slugとして説明し、applicationがprefixを付加する。

**リスク**

* Current `create_artifact_doc`のallocation-before-lockを変更する際、既存`new artifact`のcollision behaviorを回帰させる可能性がある。
* Large fileでは複数hash pass中にcreate lockを長く保持する。MVPでは単純性を優先し、size limitやpre-staging frameworkを追加しない。
* External processによる最終`lstat`後の極小TOCTOUは完全排除できない。No-replace publishとdescriptor-based hashで影響を限定する。
* Arbitrary bytesがsecretや個人情報を含む可能性はcommandが判定しない。
* Current Artifact rulesはblankをtemplate/frontmatter中心に説明しており、imported blank no-frontmatterとのdocumentation driftがある。Final public alignmentはIssue 319へrelayする。

**不確実性**

* Atomic no-replaceとdirectory fsyncの対象platform別実装はrepository内で未確定。Adapter probeとfault testsが必要。
* Dedicated Artifact `list/show` commandはinspected parser上で確認できない。新commandは追加せず、既存consumer inventoryでfilename-only consumerの有無を確認する。
* Exact error code、warning code、result field名はIssue-local design delta。ただし`committed`、path、hash、bytes、retry safetyの意味は固定する。
* 本回答ではtest、filesystem probe、assurance classify、reviewer実行を行っていない。

---

## DESIGN_CANDIDATE

### 1. 設計結論

最小設計は、**新しいtop-level `artifact` command groupの`import` leaf**、独立application use case、既存blank naming/create lock、専用binary publisherを組み合わせる構成とする。

Current parserには`new artifact`と、GitHub Issueをnodeへimportするtop-level `import initiative|epic|issue`があるが、Artifact resource groupはない。

これは現在のoperation-first surfaceとの軽微なsyntax driftを生む。しかし、親Epicとaccepted ADRが`artifact import`を「template-free第二作成経路」として明示しており、`import artifact`へ変更すると既存node-import familyへ異なるstorage operationを混在させる。したがって、親契約を優先して次を採用する。

```text
./spec-dock/scripts/spec-dock artifact import chatgpt-output \
  (--initiative <id> | --epic <id> | --issue <id>) \
  --file <path> \
  --title <title> \
  [--slug <base-slug>] \
  [--json]
```

`artifact` groupにはIssue 317で`import`以外のleafを追加しない。`new artifact` aliasを移動・複製しない。

### 2. Layered design

```text
cli/parser.py
  -> commands/artifact.py
    -> application/import_artifact.py
      -> shared Artifact creation support
         - scope resolution
         - artifacts setup
         - create lock
         - blank allocation / duplicate scan
      -> ArtifactBinaryPublisher port
         - source guard / regular-file inspection
         - binary stage / hash / fsync
         - atomic no-replace publish
         - cleanup / directory durability
    -> presentation/cli_text.py + JSON renderer
```

| Layer               | 責任                                                                                                 | 禁止                                        |
| ------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `cli/`              | `artifact import` parser wiring                                                                    | Filesystem判断、hash、path resolution         |
| `commands/`         | Args→request、result/error renderer選択、exit code                                                     | Copy、lock、allocation                      |
| `application/`      | Input normalization、scope/source-boundary resolution、lock orchestration、allocation/retry、warning統合 | Body parse、binary I/O                     |
| `domain/`           | Existing slug、blank filename parser/formatter、duplicate/collision grammar                          | Import provenance catalog、hash、filesystem |
| `application ports` | Narrow binary publisher contract                                                                   | Generic transaction framework             |
| `infra/`            | `lstat`、binary streams、hash、fsync、no-replace、temp cleanup                                          | Template rendering、authority判断            |
| `presentation/`     | Content-free text/JSON                                                                             | Raw exception/body/absolute path          |
| `tests/`            | Observable contract、fault injection、concurrency                                                    | Private implementation shapeへの過度な固定       |

### 3. Existing primitives to reuse

| Primitive                                                              | 扱い                                           |
| ---------------------------------------------------------------------- | -------------------------------------------- |
| `slugify`, `validate_input_slug_kebab`                                 | Reuse                                        |
| `parse_artifact_filename`                                              | Reuse。Import resultのstorage identityは`blank` |
| `scan_artifact_duplicate_state`                                        | Pre/post publishでreuse                       |
| `allocate_artifact_filename_for_timestamp(..., artifact_type="blank")` | Reuse                                        |
| Existing `01..99` suffix exhaustion                                    | Reuse                                        |
| Existing scope resolver / artifacts rules setup                        | 意味論不変で共有化                                    |
| Existing create lock                                                   | Importと`new artifact`で共有                     |
| Issue 316のcomponent-wise directory ancestry guard pattern              | Source parent/Workbench boundaryにreuseまたは共通化 |
| Clock timestamp formatter                                              | Reuse                                        |
| Existing text/JSON command convention                                  | Reuse                                        |

Current domain parserはtyped grammarを先に評価し、blank slugが現在のsupported type prefixで始まる場合だけrejectする。`chatgpt-output`はcatalogにないため、`chatgpt-output-*`はblankとして解析できる。Allocatorはsame timestampの全Artifact slotを見てstandardまたは`01..99` suffixを割り当てる。

### 4. APIs that must not be reused

* `CreateArtifactDocRequest`への`source_file`、`mode`、`import_kind`追加。
* `TemplateScaffolder.render_text()`。
* `TemplateScaffolder.write_text()`。
* `Path.read_text()` / `write_text()`。
* `FileArtifactWriter`。
* Issue 316のrecursive `copy_workbench()`。
* `shutil.copytree()`。
* Overwriting `replace()`。
* Markdown/frontmatter parser。

Current `create_artifact_doc`はtemplateを解決し、replacementをrenderしてtext writerで書くため、byte-preserving importには使用できない。

Issue 316の`copy_workbench`はrecursive source-wins mergeであり、destination leafをunlinkして`copy2`する。No-overwrite formal publicationとはfailure modelが異なるため、import publisherとしては再利用しない。

### 5. Request, result, and error contract

以下はsemantic contractであり、exact module/class nameは実装時のlocal deltaとする。

```python
@dataclass(frozen=True)
class ImportArtifactRequest:
    import_kind: Literal["chatgpt-output"]
    scope_node_id: str
    scope_kind: Literal["initiative", "epic", "issue"]
    source_file: Path
    title: str
    slug: str | None


@dataclass(frozen=True)
class ImportArtifactResult:
    import_kind: Literal["chatgpt-output"]
    artifact_type: Literal["blank"]
    artifact_id: str
    scope_node_id: str
    source_path: Path          # internal absolute; presentation makes repo-relative
    path: Path                 # committed formal path
    sha256: str                # lowercase hex
    byte_count: int
    status: Literal["committed", "committed_with_warning"]
    source_retained: bool
    canonical: bool            # always False
    evidence_only: bool        # always True
    durability_confirmed: bool
    cleanup_complete: bool
    warnings: tuple[str, ...]


class ArtifactImportError(RuntimeError):
    code: str
    committed: bool            # pre-commit errors are False
    retry_safe: bool
    destination_path: Path | None
    warnings: tuple[str, ...]
```

#### Stable error categories

| Category            | Candidate codes                                                                                                                 | `committed` |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Input               | `unsupported_import_kind`, `invalid_scope`, `invalid_title`, `invalid_slug`                                                     | false       |
| Source              | `source_missing`, `source_outside_workbench`, `source_not_markdown`, `source_not_regular`, `unsafe_source_path`, `source_alias` | false       |
| Destination state   | `unsafe_artifacts_dir`, `invalid_artifact_state`, `create_lock_failed`, `suffix_exhausted`                                      | false       |
| Staging             | `temp_create_failed`, `copy_failed`, `source_changed`, `hash_mismatch`, `file_fsync_failed`                                     | false       |
| Publication         | `publication_unsupported`, `publish_failed`, `publish_collision_exhausted`                                                      | false       |
| Pre-commit cleanup  | `temp_cleanup_failed`                                                                                                           | false       |
| Post-commit warning | `durability_not_confirmed`, `temp_cleanup_pending`, `post_publish_state_unconfirmed`, `create_lock_release_pending`             | true        |

Pre-commit failureはnon-zero exitとする。Committed warningはretryを誘発しないよう、exit code `0`、`status=committed_with_warning`、stderr warning、JSON `committed=true`を候補とする。Repositoryの既存warning conventionが別のexit policyを要求する場合も、committed pathを隠したnon-zero generic failureにはしてはならない。

### 6. Source path policy

#### 6.1 Lexical normalization

1. Relative pathは`ports.repo_root`基準でabsolute化する。
2. Absolute pathはそのままlexically normalizeする。
3. `resolve()`をcontainment checkの前に使わない。
4. Normalized pathがlexically current repo root外ならrejectする。
5. Exact suffixが`.md`でなければrejectする。

#### 6.2 Approved Workbench boundary

Applicationはcurrent graph/node recordsから次のallowed rootsを構築する。

```text
<specdock_dir>/.workbench
<initiative-dir>/.workbench
<epic-dir>/.workbench
<issue-dir>/.workbench
```

Sourceはallowed rootのdescendantでなければならない。Supported placementはrootまたはscope direct childに限定し、path内にたまたま`.workbench` componentがあるだけでは許可しない。

#### 6.3 Symlink and regular-file checks

* Repo rootからselected Workbench rootまで、さらにsource parentまでをcomponent-wise `lstat`。
* 全ancestorはreal directoryでなければならない。
* Source path自体を`lstat`し、symlinkをreject。
* `os.open(..., O_RDONLY | O_NOFOLLOW)`が利用可能なplatformでは`O_NOFOLLOW`を併用。
* Open後の`fstat`がregular fileであり、直前`lstat` identityと一致することを確認。
* Issue 316の`guard_workbench_ancestry`はendpointをdirectoryとして要求するため、source file自体へそのまま適用せず、`source.parent`までに使う。

#### 6.4 Alias checks

* Source pathがtarget `artifacts/`内にlexically入っていないこと。
* Existing target `artifacts/*.md`のnon-symlink regular file identitiesとsource identityが一致しないこと。
* Temp creation後、temp identityとsource identityが異なること。
* Final pathはpublish前に不存在であること。
* Finalはtempからpublishし、sourceからhard-linkしない。

### 7. Shared creation lock and allocation

Existing create lockはO_EXCL ownership tokenを使い、stale/wait semanticsとtoken確認付きreleaseを持つ。これを別lockで複製しない。

Recommended lock order:

1. Parseとnon-mutating source/scope preflight。
2. Acquire shared create lock。
3. Reload/reconfirm graph scopeとsource boundary。
4. Preflight Artifact rules sourceとexisting `artifacts/`。
5. Ensure standard `artifacts/` setup。
6. Scan malformed/duplicate state。
7. Capture operation timestamp。
8. Allocate blank candidate inside lock。
9. Stage/hash/verify source inside lock。
10. Atomic no-replace publish。
11. Post-publish scan。
12. Directory durability、temp cleanup。
13. Release lock。
14. Return clean resultまたはcommitted warning。

Lockをstage/hash中も保持するのはlarge fileに対する競合時間を増やすが、setup、allocation、new/import concurrencyを一つの単純なcritical sectionに閉じる。Pre-stagingを別framework化するよりMVPの整合性を優先する。

Existing `create_artifact_doc`もscan/allocationをlock内で再実行するよう最小修正し、importとnew artifactのconcurrent same-second behaviorを一致させる。Template routingとrendered bodyは変更しない。

### 8. Byte-preserving two-phase flow

#### Phase A — Verified staging

1. Source descriptorをopen。
2. Initial `fstat`を記録する。

   * `st_dev`
   * `st_ino`
   * regular-file mode
   * `st_size`
   * `st_mtime_ns`
   * 必要なら`st_ctime_ns`
3. Sourceを先頭からstream-readし、`source_pre_sha256`と`source_pre_bytes`を計算。
4. `artifacts/`と同じdirectoryに、non-`.md` random tempを`O_CREAT|O_EXCL`で作成。
5. Source descriptorを先頭へ戻し、fixed-size chunksでtempへwriteしながら`copy_sha256`と`copy_bytes`を計算。
6. Tempをflushし、file `fsync`。
7. Tempを独立readして`temp_sha256`と`temp_bytes`を計算。
8. Source descriptorを再読し、`source_post_sha256`と`source_post_bytes`を計算。
9. Source `fstat`とsource path `lstat`を再取得し、initial identity/statと比較。
10. 次をすべて要求する。

```text
source_pre_sha256
  == copy_sha256
  == temp_sha256
  == source_post_sha256

source_pre_bytes
  == copy_bytes
  == temp_bytes
  == source_post_bytes
```

11. 不一致ならformal publish前にfailし、owned tempをcleanup。

Valid UTF-8 validationは行わない。

#### Phase B — No-replace publication

1. Source pathがinitial identityをまだ指すことを再確認。
2. Candidate final pathへatomic no-replace publish。
3. POSIX候補はsame-filesystem `link(temp, final)`。
4. `EEXIST`ならexisting pathに触れず、duplicate stateをrescanし、次suffixをallocateして再試行。
5. `EEXIST`以外のunsupported errorではunsafe fallbackをせずfailure。
6. Publish成功後、final identityがstaged identityを指すことを確認。
7. Directory `fsync`を試みる。
8. Temp linkをunlink。
9. 必要ならdirectory `fsync`を再試行。
10. Post-publish duplicate scanでcommitted Artifact IDを確認。
11. Publish後のfailureはrollbackせずwarningへ変換。

Adapterはhard-link以外のnative no-replace primitiveを使ってよいが、次のcontractを満たさなければならない。

> Existing final pathを置換せず、verified staged bytesだけをformal nameで一操作公開する。

### 9. Temporary and setup effects

Temp basename候補:

```text
.specdock-artifact-import-<random>.tmp
```

* `.md` suffixを持たず、Artifact scanner対象外。
* Body、source filename、titleをtemp nameへ含めない。
* Pre-commit failureではowned tempを削除。
* Crash orphanの自動GCは作らない。
* `artifacts/`が未setupの場合、existing `_ensure_artifacts_setup`相当がdirectoryとmanaged `rules.md` linkを作り得る。このsetupはformal evidence Artifactではないため、後続stage failure時にtree-wide rollbackしない。
* Importが作るevidence Artifactは一件だけ。`rules.md`はmanaged setup surfaceとして区別する。

### 10. Naming and coexistence

```text
base_slug = validate_input_slug_kebab(
    request.slug if provided else slugify(request.title)
)
blank_slug = "chatgpt-output-" + base_slug

allocate_artifact_filename_for_timestamp(
    artifacts_dir,
    timestamp=timestamp,
    artifact_type="blank",
    slug=blank_slug,
)
```

Result example:

```text
artifact_type=blank
import_kind=chatgpt-output
artifact_id=20260713t130000z
path=.../artifacts/20260713t130000z-chatgpt-output-workbench-analysis.md
```

Collision example:

```text
artifact_id=20260713t130000z-01
path=.../artifacts/20260713t130000z-01-chatgpt-output-workbench-analysis.md
```

`SUPPORTED_ARTIFACT_TYPES`、typed regex、`is_ambiguous_blank_artifact_slug()`へ`chatgpt-output`を追加しない。

### 11. Presentation contract

Text success candidate:

```text
spec-dock: ok (artifact import) import_kind=chatgpt-output artifact_type=blank
id=20260713t130000z scope=epic-00312
source=spec-dock/.workbench/report.md
path=spec-dock/.../artifacts/20260713t130000z-chatgpt-output-report.md
sha256=<64-hex> bytes=<n>
committed=true source_retained=true canonical=false evidence_only=true
```

JSON candidate:

```json
{
  "command": "artifact import",
  "import_kind": "chatgpt-output",
  "artifact_type": "blank",
  "artifact_id": "20260713t130000z",
  "scope_id": "epic-00312",
  "source": "spec-dock/.workbench/report.md",
  "path": "spec-dock/.../artifacts/20260713t130000z-chatgpt-output-report.md",
  "sha256": "<64-hex>",
  "bytes": 1234,
  "status": "committed",
  "committed": true,
  "source_retained": true,
  "canonical": false,
  "evidence_only": true,
  "durability_confirmed": true,
  "cleanup_complete": true,
  "warnings": []
}
```

Failure outputはstable code、scope、repo-relative safe path、`committed`、`retry_safe`だけを含める。Source body、title body、absolute path、raw exception、candidate path listは出さない。

### 12. Validation, sync, listing, tree, context, ADR mirror

| Surface             | Imported fileの扱い                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| Artifact parser     | `artifact_type="blank"`                                                                          |
| Duplicate detection | Existing timestamp/suffix slot rules                                                             |
| Generic validate    | Filename、symlink、duplicateだけ。Body decodeなし                                                       |
| Sync validation     | Same generic validation                                                                          |
| `.agent` projection | Existing `future_artifacts.path/present`のみ                                                       |
| Tree/index          | Node treeのまま。Body/file catalog追加なし                                                               |
| Context             | Automatic body inclusionなし。Existing filename-only reference consumerがあればblank/pathとして扱う          |
| Artifact listing    | Current dedicated commandは追加しない。Existing generic consumerはblank ID/pathとして表示し、import routeを推測しない |
| ADR mirror          | Typed `adr`ではないため対象外                                                                             |
| Canonical authority | なし                                                                                               |
| Provenance          | Command resultと、Issue 318でorchestratorが更新するEAL                                                   |

### 13. Failure and rollback semantics

| Boundary                            | Formal file | Temp            | Source                 | Result                              |
| ----------------------------------- | ----------- | --------------- | ---------------------- | ----------------------------------- |
| Input/path preflight failure        | なし          | なし              | Commandは変更しない          | Failure、retry-safe                  |
| Stage/hash/file-fsync failure       | なし          | Cleanup attempt | Commandは変更しない          | Failure                             |
| Temp cleanup failure before publish | なし          | Orphanの可能性      | Commandは変更しない          | Failure + cleanup pending           |
| Publish `EEXIST`                    | Existingのみ  | 保持              | Commandは変更しない          | Reallocate/retry                    |
| Publish unsupported/failure         | なし          | Cleanup attempt | Commandは変更しない          | Failure                             |
| Publish成功                           | 完全file      | Cleanup対象       | Same identity/pathを再確認 | Committed                           |
| Directory fsync failure             | 完全file      | Cleanup継続       | 変更なし                   | Committed warning                   |
| Temp unlink failure                 | 完全file      | Orphan link     | 変更なし                   | Committed warning                   |
| Lock release failure                | 完全file      | 状況に応じる          | 変更なし                   | Committed warning + doctor guidance |
| Post-write scan failure             | 完全file      | Cleanup継続       | 変更なし                   | Committed warning、retry禁止           |

### 14. Provider/dogfood boundary

Primary変更候補:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  cli/parser.py
  cli/registry.py
  cli/bootstrap.py
  commands/artifact.py
  application/contracts.py
  application/ports.py
  application/import_artifact.py
  application/create_artifact_doc.py        # shared allocation refactor only
  application/create_node.py                # lock extraction only if needed
  domain/artifacts.py                       # catalog不変、必要最小helperのみ
  infra/artifact_binary_publisher.py
  presentation/cli_text.py
```

Dogfood `spec-dock/scripts/spec_dock_runtime/**`はnormal projection後のverification surfaceとする。Direct dogfood-only fixは禁止する。

### 15. Rejected alternatives and tradeoffs

| Alternative                        | Disposition                 | 理由                                                          |
| ---------------------------------- | --------------------------- | ----------------------------------------------------------- |
| `new artifact --file ...`          | Reject                      | Template/text pathとbinary import failure modelが混ざる          |
| `import artifact ...`              | Reject                      | Existing node-import familyへstorage importを混在し、親syntaxを変更する |
| New typed `chatgpt-output` token   | Reject                      | Accepted ADRとblank coexistenceに反する                          |
| Blank prefix reservation           | Reject                      | Existing valid inputを破壊                                     |
| Frontmatter injection              | Reject                      | Byte identityを破る                                            |
| Sidecar/receipt                    | Reject                      | Single-file MVPとno-catalog境界を破る                             |
| UTF-8 validation                   | Reject                      | Opaque bytes契約に反する                                          |
| `TemplateScaffolder` / text writer | Reject                      | Decode/render/newline変換の可能性                                 |
| `copy_workbench`                   | Reject                      | Recursive overwrite/source-wins semantics                   |
| `exists()`後に`replace()`            | Reject                      | TOCTOU overwrite race                                       |
| Sourceからfinalへ直接hard-link          | Reject                      | Source/final alias、copy contract違反                          |
| Pre-stage outside create lock      | Defer                       | Lock時間は減るがsetup/source-stability/concurrencyが複雑化            |
| Generic transaction/journal        | Reject for MVP              | Persistent stateとscope expansion                            |
| Auto sync/EAL/canonical rewrite    | Reject                      | Authority越権、Issue 318/319責務                                 |
| Secret scanner                     | Reject for MVP              | 内容分類surfaceの追加                                              |
| File-size limit                    | Reject unless observed need | Parent contractにないclassifier/policy追加                       |

### 16. Issue 318 / 319 relay

**Issue 318 receives**

* Exact command syntax。
* Result fields: source/destination/hash/bytes/commit/warnings。
* `artifact_type=blank`, `import_kind=chatgpt-output` distinction。
* `canonical=false`, `evidence_only=true`。
* Complete file / complete inline / unavailable inline / ZIP-tree workflow分岐のruntime前提。
* EALへ記録するpath/hash/capture boundary。
* CommandがEALを自動編集しないこと。

**Issue 319 receives**

* Provider changed-file inventoryとdogfood projection evidence。
* Focused test commands/results。
* Manual Workbench→Artifact hash/source-survival evidence。
* Existing `new artifact`、validate、sync、ADR mirror regression evidence。
* Cross-platform no-replace/directory-fsync limitations。
* Docs drift inventory、特に`docs/rules/*/artifacts.md`のtemplate/frontmatter中心説明。
* Remaining package-data、fresh init/update、final provider/dogfood parity、full suite/static analysis、public docs、Epic PR。

### 17. Requirement traceability

| Design                               | Requirements / AC             |
| ------------------------------------ | ----------------------------- |
| `DES-317-001` Command group          | RQ-001–002 / AC-001           |
| `DES-317-002` Request/result/error   | RQ-002, 011–012 / AC-008, 010 |
| `DES-317-003` Source boundary        | RQ-003–005 / AC-002, 006      |
| `DES-317-004` Opaque bytes           | RQ-006, 009 / AC-003, 007     |
| `DES-317-005` Blank allocation       | RQ-007–008 / AC-004–005       |
| `DES-317-006` Staging                | RQ-009 / AC-003, 007          |
| `DES-317-007` No-replace publish     | RQ-010 / AC-005, 007          |
| `DES-317-008` Cleanup/warnings       | RQ-011 / AC-007–008           |
| `DES-317-009` Presentation/authority | RQ-012 / AC-010               |
| `DES-317-010` Validate/sync/ADR      | RQ-013 / AC-009               |
| `DES-317-011` Provider/relay         | RQ-014–015 / AC-011           |

---

## PLAN_CANDIDATE

### 1. Plan status and execution order

本計画は実行候補であり、現時点のIssue 317 canonical `design.md` / `plan.md` placeholderへ直接書き込む順序ではない。まずrequirement具体化とassurance composeを完了し、compose後のprofile templateへ候補を統合する。

Issue 316は、`S00`から`S99`までのsmall-step、per-step reviewer、report update、commit、clean-tree、Issue 319 deferred deliveryを既存実行パターンとして採用している。Issue 317もこの粒度を踏襲する。

```text
S00 planning / assurance / baseline
  -> S01 shared Artifact creation characterization and lock-safe allocation
  -> S02 thin artifact-import vertical slice
  -> S03 source path / regular-file / alias boundary
  -> S04 byte-preserving stage / hash / source stability
  -> S05 atomic no-replace / collision / concurrency
  -> S06 failure cleanup / committed-warning semantics
  -> S07 validation / authority / regression / manual / relay
  -> S90 docs impact decision
  -> S99 final Issue quality / push / clean / finish
```

各stepは、前stepのrequired tests、fresh reviewer verdict、report evidence、commitまたはapproved no-op、clean treeが揃うまで開始しない。

### 2. Allowed and forbidden paths

#### Generally allowed

```text
spec-dock/.../issues/iss-00317-.../
  requirement.md
  design.md
  plan.md
  report.md
  artifacts/**

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  cli/**
  commands/**
  application/**
  domain/artifacts.py
  infra/**
  presentation/**

tests/unit/**
tests/cli_runtime/**

spec-dock/scripts/spec_dock_runtime/**
  # normal provider→dogfood projection only
```

#### Generally forbidden

```text
src/spec_dock/assets/spec_dock/templates/artifacts/**
spec-dock/templates/artifacts/**

.agents/skills/**
src/spec_dock/assets/install_root/.agents/skills/**
spec-dock/docs/workflow_*.md
src/spec_dock/assets/spec_dock/docs/workflow_*.md
  # Issue 318

installer/package-data/fresh-init/update final surfaces
public reference docs beyond S90 decision
Epic PR / merge preparation
  # Issue 319

.codex/agents/**
src/spec_dock/assets/install_root/.codex/agents/**
  # model configuration is not product scope

parent Epic requirement/design/plan/accepted ADR
  # unless a real contradiction requires amendment and fresh review
```

Dogfood runtimeを先に編集してproviderへbackportすることは禁止する。

### 3. Common DevCoder delegation contract

**Source of truth**

1. Accepted ADR。
2. Parent Epic requirement/design/plan。
3. Freshly reviewed Issue 317 requirement/design/plan。
4. Current provider implementation/tests。
5. Planning evidence。

**Required worker output**

* Changed files。
* Redまたはcharacterization evidence。
* Green commands/results。
* Refactor summary。
* AC/EC/closure IDs。
* Failure modes tested。
* Remaining risks。
* No-scope-expansion statement。
* Report向けLedger Note。

**Common stop conditions**

* Typed `chatgpt-output`追加が必要になる。
* Blank prefix reservationが必要になる。
* Arbitrary host pathを許可する必要が生じる。
* Unsafe no-replace fallbackしか実装できない。
* Sourceをmove/deleteする必要が生じる。
* General transaction/catalog/manifestが必要になる。
* Existing `new artifact` public semanticsを親契約外に変更する。
* Workflow/skill/EAL自動編集へ範囲が拡張する。
* Provider/dogfood authorityを逆転する。
* Requirement/ACを満たすためparent ADR変更が必要になる。

Stop condition発生時は実装を継続せず、reportに差分を記録してrequirement/design/plan amendmentとfresh `spec-reviewer`へ戻す。

### 4. Spec-locked closure index

| Closure ID | AC / EC               | Locked expectation                                               | Bug class                       |
| ---------- | --------------------- | ---------------------------------------------------------------- | ------------------------------- |
| `C317-01`  | AC-001                | Separate `artifact import`、exact args、no `new artifact` overload | CLI/scope drift                 |
| `C317-02`  | AC-002、EC-001–003     | Caller-specified root/scoped Workbench、source/destination独立      | Wrong provenance/path inference |
| `C317-03`  | AC-003、EC-005/007     | Opaque bytes、all hashes/counts equal、source stable               | Decode/normalization/torn copy  |
| `C317-04`  | AC-004、EC-004         | Blank parser/coexistence、no reservation/type token               | Filename compatibility break    |
| `C317-05`  | AC-005、EC-006/009/010 | Shared lock、lock-internal allocation、no overwrite                | Concurrent data loss            |
| `C317-06`  | AC-006、EC-006/008/014 | Symlink/containment/alias/platform fail-closed                   | Boundary escape                 |
| `C317-07`  | AC-007、EC-011         | Pre-commit failure leaves no formal Artifact                     | Partial publication/source loss |
| `C317-08`  | AC-008、EC-012/013     | Post-commit warning returns committed path                       | Duplicate retry/hidden commit   |
| `C317-09`  | AC-009、EC-015         | Validate blank、no body parse、no ADR mirror                       | Authority/parser drift          |
| `C317-10`  | AC-010                | No canonical/EAL/assurance mutation、content-free output          | Authority/secret leakage        |
| `C317-11`  | AC-011                | Provider implementation、focused/manual evidence、Issue319 relay   | Delivery boundary drift         |

### 5. Step plan

#### S00 — Requirement, assurance, planning, baseline

**Goal**

* Canonical requirementを具体化し、assurance authorityに基づいてdesign/plan/report templateをcomposeする。
* Existing `new artifact`、validator、sync、Issue315/316 behaviorのbaselineを固定する。

**Allowed**

* Issue 317 canonical docs/report/artifacts。
* Read-only provider/tests inventory。

**Forbidden**

* Production code、tests、dogfood runtime変更。

**Commands**

```sh
git rev-parse HEAD
git status --short

./spec-dock/scripts/spec-dock assurance classify \
  --stage requirement \
  --issue iss-00317

./spec-dock/scripts/spec-dock assurance compose \
  --artifact all \
  --issue iss-00317

./spec-dock/scripts/spec-dock assurance verify \
  --issue iss-00317

./spec-dock/scripts/spec-dock validate

uv run pytest tests/cli_runtime/test_new.py -k artifact
uv run pytest tests/cli_runtime/test_validate.py -k artifact
git diff --check
```

Assurance CLIは`--issue`、`--stage requirement`、`--artifact all`を現在のparser contractとして提供している。

**Test IDs**

* `tc-s00-001`: Existing blank/typed Artifact create baseline。
* `tc-s00-002`: Existing Artifact validate/duplicate baseline。
* `tc-s00-003`: Issue315 Workbench opacity and Issue316 source-wins focused baseline。
* `tc-s00-004`: Assurance classify/compose/verify sequence。

**Evidence**

* `report.md` Spec Authoring Gate。
* EAL/OAL。
* Grade Specialist Evidence。
* Baseline command log。
* Planning commit SHA、push、clean-tree。

**Gate**

Fresh requirement/design/plan `spec-reviewer` passが得られるまでS01へ進まない。現時点では未実行。

---

#### S01 — Shared Artifact creation support and lock-safe allocation

**Goal**

* Current Artifact parser/allocator/create-lock behaviorをcharacterizeする。
* `new artifact`とimportが同一lock内でscan/allocationできる最小shared boundaryを作る。
* `new artifact`のtemplate/body semanticsは不変に保つ。

**Candidate changes**

```text
application/create_artifact_doc.py
application/create_node.py
application/<small shared artifact-create support>.py
domain/artifacts.py              # helper必要時のみ
tests/unit/commands/test_runtime_new_s08.py
new focused application/domain test
```

**Red / characterization / Green**

* Characterization: Sequential same-second collision、blank ambiguity、suffix exhaustion、create lock ownership。
* Red: Parallel `new artifact`またはimport-compatible fake operationで、allocation-before-lockがsame candidateを保持するfailureを再現。
* Green: Scan/allocationをshared lock内で再実行し、parallel operationsがdistinct slotを得る。
* Refactor: Private helper duplicationを除去するが、template resolutionとrenderingは変更しない。

**Test IDs**

* `tc-s01-001`: `chatgpt-output-*` is valid blank slug。
* `tc-s01-002`: Parser returns `artifact_type=blank`。
* `tc-s01-003`: Same-second sequential allocation。
* `tc-s01-004`: Parallel create operations allocate distinct slots。
* `tc-s01-005`: `01..99` exhaustion unchanged。
* `tc-s01-006`: Existing `new artifact` rendered bytes/frontmatter unchanged。

**Focused commands**

```sh
uv run pytest tests/unit/commands/test_runtime_new_s08.py
uv run pytest tests/cli_runtime/test_new.py -k artifact
uv run pytest <new-domain-or-application-test>
uv run ruff check <changed-python-paths>
uv run ruff format --check <changed-python-paths>
git diff --check
```

**Reviewer focus**

* Lock acquisition before final allocation。
* No catalog/template change。
* No new lock。
* Existing create-lock release semantics regressionなし。
* No duplicated allocator。

**Commit candidate**

```text
refactor(artifact): share lock-safe artifact allocation
```

---

#### S02 — Thin vertical `artifact import` happy path

**Goal**

Parserからcontent-free resultまでのvertical pathを、fake/in-memory publisherで成立させる。

**Candidate changes**

```text
cli/parser.py
cli/registry.py
cli/bootstrap.py
commands/artifact.py
application/contracts.py
application/ports.py
application/import_artifact.py
presentation/cli_text.py
tests/cli_runtime/test_artifact_import.py
tests/unit/application/test_artifact_import.py
```

**Allowed**

* Request/result/error、parser/registry/wiring、fake publisher。
* Single clean happy path。

**Forbidden**

* Full symlink/hash/fault/concurrency implementation。
* Docs/skills。
* Generic import framework。

**Red / Green / Refactor**

* Red: `artifact` command unrecognized。
* Green: Fake publisher resultでone successful command。
* Refactor: Thin command handler、application-only orchestration、presentation-only formatting。

**Test IDs**

* `tc-s02-001`: Help shows `artifact import chatgpt-output`。
* `tc-s02-002`: Exactly one scope required。
* `tc-s02-003`: `--file`, `--title` required、`--slug`, `--json` optional。
* `tc-s02-004`: Unknown import kind rejected。
* `tc-s02-005`: Forbidden options absent。
* `tc-s02-006`: Happy text result。
* `tc-s02-007`: Happy JSON result with`blank`/`chatgpt-output` distinction。
* `tc-s02-008`: `new artifact` and node `import` help unchanged。

**Focused commands**

```sh
uv run pytest tests/cli_runtime/test_artifact_import.py -k "help or happy or parser"
uv run pytest tests/unit/application/test_artifact_import.py -k happy
uv run pytest tests/cli_runtime/test_new.py -k artifact
uv run pytest tests/unit/cli/test_cli.py
```

**Reviewer focus**

* Resource-first parent command preserved。
* Handlerにfilesystem logicなし。
* No body/title leakage。
* No authority claim。

**Commit candidate**

```text
feat(artifact): add explicit chatgpt-output import surface
```

---

#### S03 — Source placement, regular-file, symlink, alias boundary

**Goal**

Sourceを読む前にapproved Workbench placement、regular non-symlink `.md`、ancestor safety、source/formal non-aliasingを閉じる。

**Candidate changes**

```text
application/import_artifact.py
application/ports.py
infra/artifact_binary_publisher.py
必要なshared fs ancestry helper
tests/unit/application/test_artifact_import.py
tests/unit/infra/test_artifact_binary_publisher.py
```

**Red / Green / Refactor**

* Red: Outside path、source symlink、ancestor symlink、directoryがfake publisherへ到達する。
* Green: All invalid cases fail before source read/stage、external sentinel不変。
* Refactor: Issue316 directory ancestry guard patternを共有するが、recursive copy operationとは結合しない。

**Test IDs**

* `tc-s03-001`: Repo-relative root Workbench file accepted。
* `tc-s03-002`: Absolute root Workbench file accepted。
* `tc-s03-003`: Initiative/Epic/Issue scoped Workbench file accepted。
* `tc-s03-004`: Source and destination scopes may differ。
* `tc-s03-005`: Outside repo/Workbench rejected。
* `tc-s03-006`: `.MD`, directory, FIFO/socket rejected。
* `tc-s03-007`: Source symlink/broken symlink rejected。
* `tc-s03-008`: Repo→Workbench/source-parent ancestor symlink rejected。
* `tc-s03-009`: Target scope/artifacts unsafe ancestry rejected。
* `tc-s03-010`: Source hard-link alias toexisting formal Artifact rejected。
* `tc-s03-011`: Zero-byte regular `.md` accepted。

**Focused commands**

```sh
uv run pytest tests/unit/application/test_artifact_import.py -k "source or scope or alias"
uv run pytest tests/unit/infra/test_artifact_binary_publisher.py -k "path or symlink or regular"
uv run pytest tests/unit/infra/test_runtime_fs_cli_workbench.py -k ancestry
```

**Reviewer focus**

* No `resolve()`-before-guard bypass。
* Supported Workbench placement exactness。
* Source parent vsfile endpoint distinction。
* External target read/writeなし。
* Hard-link alias policy。

**Commit candidate**

```text
feat(artifact): enforce safe workbench import source boundary
```

---

#### S04 — Binary staging, hashes, source stability

**Goal**

Source/pre-copy/temp/post-copyのbyte identityとsource stabilityを証明してからpublish-ready staged fileを返す。

**Red / Green / Refactor**

* Red: Text APIによるinvalid UTF-8/BOM/CRLF failureまたはnormalization。
* Green: Binary streamingとfour-hash/count equality。
* Refactor: Hash/copy chunk loopをpublisher内に局所化。Persistent hash modelなし。

**Test IDs**

* `tc-s04-001`: LF fixture。
* `tc-s04-002`: CRLF fixture。
* `tc-s04-003`: UTF-8 BOM。
* `tc-s04-004`: Final newlineあり/なし。
* `tc-s04-005`: Japanese/non-ASCII。
* `tc-s04-006`: NUL/invalid UTF-8/arbitrary bytes。
* `tc-s04-007`: Empty file。
* `tc-s04-008`: Frontmatter-like/authority-like body。
* `tc-s04-009`: Same-size source mutation during copy。
* `tc-s04-010`: Source path inode replacement/unlink。
* `tc-s04-011`: Temp create/write failure。
* `tc-s04-012`: Injected hash mismatch。
* `tc-s04-013`: File flush/fsync failure。
* `tc-s04-014`: Source mode/mtime/path unchanged; atime excluded。
* `tc-s04-015`: Temp name has no `.md` suffix。

**Assertions**

```text
source_before == staged == formal_candidate bytes
pre_hash == copy_hash == temp_hash == post_hash
all byte counts equal
source file remains
no frontmatter/template added
```

**Focused commands**

```sh
uv run pytest tests/unit/infra/test_artifact_binary_publisher.py -k "bytes or hash or mutation or fsync"
uv run pytest tests/unit/application/test_artifact_import.py -k "hash or source_changed"
```

**Reviewer focus**

* No decode。
* Descriptor/path identity comparison。
* Same-size mutation。
* Whole-file bufferingなし。
* Source destructive callなし。

**Commit candidate**

```text
feat(artifact): stage and verify opaque source bytes
```

---

#### S05 — Atomic no-replace, collision, concurrency

**Goal**

Verified tempだけをformal pathへpublishし、import/import、import/new、external writer raceで既存fileを上書きしない。

**Red / Green / Refactor**

* Red: `exists()` + replaceまたはpreallocated pathでraceを再現。
* Green: Atomic no-replace、`EEXIST` rescan/reallocation、shared lock。
* Refactor: Publish primitiveをinfra adapterに閉じ、applicationはstatusだけを扱う。

**Test IDs**

* `tc-s05-001`: Empty timestamp slot standard filename。
* `tc-s05-002`: Existing standard slot→`01`。
* `tc-s05-003`: Sparse suffix slots→lowest free。
* `tc-s05-004`: Concurrent two imports。
* `tc-s05-005`: Concurrent import and `new artifact blank`。
* `tc-s05-006`: Concurrent import and typed `new artifact`。
* `tc-s05-007`: External writer creates candidate immediately before publish。
* `tc-s05-008`: Existing bytes unchanged after`EEXIST`。
* `tc-s05-009`: Suffix exhaustion。
* `tc-s05-010`: Unsupported no-replace platform fails safely。
* `tc-s05-011`: Final identity equalsstaged identity、not source identity。

**Focused commands**

```sh
uv run pytest tests/unit/infra/test_artifact_binary_publisher.py -k "publish or exists or no_replace"
uv run pytest tests/unit/application/test_artifact_import.py -k "collision or concurrent or suffix"
uv run pytest tests/unit/commands/test_runtime_new_s08.py -k "parallel or artifact"
uv run pytest tests/cli_runtime/test_new.py -k artifact
```

**Reviewer focus**

* No check-then-replace。
* Shared lock actually common。
* Allocation inside lock。
* External writer not respecting lockでもsafe。
* Bounded retry。
* Existing malformed/duplicate state fail-closed。

**Commit candidate**

```text
feat(artifact): publish verified imports without replacement
```

---

#### S06 — Cleanup and committed-warning semantics

**Goal**

Pre-commit failureとpost-commit warningを、source/formal stateとretry safetyに基づいて明確に区別する。

**Test IDs**

* `tc-s06-001`: Copy failure→formal absent/temp removed/source retained。
* `tc-s06-002`: Hash failure→formal absent/source retained。
* `tc-s06-003`: File fsync failure→formal absent。
* `tc-s06-004`: Pre-commit temp cleanup failure→formal absent、cleanup pending。
* `tc-s06-005`: Directory fsync failure after publish→committed warning/path returned。
* `tc-s06-006`: Temp unlink failure after publish→committed warning/path returned。
* `tc-s06-007`: Post-write duplicate scan failure→committed warning。
* `tc-s06-008`: Create lock release failure after publish→committed warning、doctor guidance。
* `tc-s06-009`: Committed warning JSON has`committed=true`, `retry_safe=false`。
* `tc-s06-010`: Pre-commit error JSON has`committed=false`。
* `tc-s06-011`: Orphan temp is ignored by Artifact scanner。

**Red / Green / Refactor**

* Red: Existing generic exception path hides committed destination。
* Green: Result accumulator distinguishes commit boundary。
* Refactor: Warning merge and renderer centralization。

**Focused commands**

```sh
uv run pytest tests/unit/infra/test_artifact_binary_publisher.py -k "cleanup or durability"
uv run pytest tests/unit/application/test_artifact_import.py -k "warning or committed or release"
uv run pytest tests/cli_runtime/test_artifact_import.py -k "warning or error or json"
```

**Reviewer focus**

* Final rollback禁止。
* Hidden commitなし。
* Unconditional retry誘導なし。
* Raw error/path/body leakageなし。
* Source cleanupとtemp cleanupの混同なし。

**Commit candidate**

```text
fix(artifact): report import commit and cleanup boundaries
```

---

#### S07 — Validation, sync, authority, regression, manual relay

**Goal**

Import runtimeのpublic contractと既存Artifact/runtime compatibilityを閉じ、Issue 319へ再現可能なevidenceを渡す。

**Automated test IDs**

* `tc-s07-001`: Imported no-frontmatter blank passes`validate`。
* `tc-s07-002`: Duplicate detection seesblank timestamp/suffix。
* `tc-s07-003`: Invalid UTF-8 imported body does not breakvalidate。
* `tc-s07-004`: `sync` completes without reading blank body。
* `tc-s07-005`: `document_surfaces.future_artifacts` remains directory-only。
* `tc-s07-006`: Imported blank is not ADR mirror source。
* `tc-s07-007`: Body authority claims have no runtime effect。
* `tc-s07-008`: Canonical docs、EAL、assurance snapshot unchanged。
* `tc-s07-009`: Text/JSON body/absolute path/raw error redaction。
* `tc-s07-010`: `new artifact blank --slug chatgpt-output-*` regression。
* `tc-s07-011`: Provider/dogfood changed runtime parity。
* `tc-s07-012`: Existing Workbench opacity regression。

**Focused commands**

```sh
uv run pytest tests/cli_runtime/test_artifact_import.py
uv run pytest tests/unit/application/test_artifact_import.py
uv run pytest tests/unit/infra/test_artifact_binary_publisher.py

uv run pytest tests/cli_runtime/test_new.py -k artifact
uv run pytest tests/cli_runtime/test_validate.py
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py \
  -k "artifact or adr_mirror or projection"
uv run pytest tests/cli_runtime/test_sync.py
uv run pytest tests/cli_runtime/test_workbench.py

./spec-dock/scripts/spec-dock validate
git diff --check
```

**Manual scenario**

1. Managed temp repositoryを作成。
2. Initiative/Epic/Issueを作成。
3. Root Workbenchとscoped Workbenchへbinary `.md` fixturesを配置。
4. Sourceとは異なるscopeへimport。
5. Sourceとdestinationをbinary compareし、SHA-256/byte countを確認。
6. Source path、mode、mtimeを確認。
7. 同timestampを固定し、import/new artifact collisionを実行。
8. `validate`と`sync`を実行。
9. ADR mirrorにimported blankがないことを確認。
10. Canonical docs/EAL snapshot不変を確認。
11. `--json`のcontent-free fieldsを確認。
12. Normal provider→dogfood projectionを行い、changed runtime filesを比較。

**Report evidence destination**

* Session Log / TDD。
* Implementation Delegation Gate。
* Delegated Worker Evidence。
* Step Contract Closure。
* Test Contract Closure / Closure Coverage。
* Reviewer Gate Status。
* Milestone / Commit Candidate Gate。
* Manual Evidence。
* Deferred Delivery / Issue 319 Relay。

Issue 316のmanual evidenceはdifferent-slug scope、binary、`.env`、nested `.git`、broken symlink、rerunを用いており、Issue 317のmanual fixture designの先例として再利用できるが、Issue 317のtest passとしては扱わない。

**Commit candidate**

```text
test(artifact): close import compatibility and authority contract
```

---

#### S90 — Docs impact decision

**Inspection targets**

```text
src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/artifacts.md
src/spec_dock/assets/spec_dock/docs/reference_naming.md
src/spec_dock/assets/spec_dock/docs/guide.md
src/spec_dock/assets/spec_dock/scripts/README.md
dogfood mirrors
artifact import --help
success/error text/JSON
```

**Decision rule**

* Command-local help/text/JSONはIssue 317で必須。
* Existing public docsがruntime behaviorを明示的に否定または誤って禁止する場合だけ、Issue 317で最小provider docs修正を許可する。
* Comprehensive Workbench/import/workflow/migration guideはIssue 319へdefer。
* Workflow/skill変更はIssue 318へdefer。
* No-opの場合も、inspected paths、current mismatch、Issue 319 relayをreportへ記録する。

**Known mismatch**

Current rulesはArtifactを`new artifact` surfaceと説明し、blank identityをfrontmatter `template: "blank"`へ結び付けている。Imported blankはno-frontmatterであるため、最終docsでは二つのcreation routeを区別する必要がある。

**Test ID**

* `tc-s90-001`: Docs ownership/misinformation inspection。

**Gate**

Fresh `spec-reviewer`。Docs commitまたはapproved no-op。Issue 318/319内容を先取りしない。

---

#### S99 — Final Issue quality, deferred delivery, push, clean, finish

**Required verification**

1. `C317-01–11`にobserved evidenceがある。
2. 全new/focused tests。
3. Existing `new artifact`、validate、sync、ADR mirror、Workbench opacity regression。
4. Manual scenario。
5. Provider/dogfood affected-file comparison。
6. `make lint`、またはrepository-authoritative Ruff/format/mypy command。
7. `./spec-dock/scripts/spec-dock assurance verify --issue iss-00317`。
8. `./spec-dock/scripts/spec-dock validate`。
9. `git diff --check`。
10. Fresh `qa-reviewer`。
11. Fresh issue-wide `code-reviewer`。
12. Fresh `spec-reviewer`。
13. Blocking findingがあればrepair後にfresh re-review。

**Commit/push/clean gate**

```sh
git status --short
git diff --check
git log --oneline --decorate -n <appropriate-count>
git push
git status --short
git rev-list --left-right --count @{upstream}...HEAD
```

Required state:

* Working tree clean。
* Intended commitsのみ。
* Branch pushed。
* Upstream ahead/behindがIssue reportに記録される。
* No unresolved blocking EAL/OAL/decision entry。
* `report.md`にall step evidence、reviewer verdict、commit SHAを記録。

**Deferred PR delivery**

Per-Issue PRは作らない。`report.md`へ次を記録する。

```text
deferred_to: iss-00319
reason: parent Epic reviewed deferred-delivery policy
pushed_head: <sha>
commits:
  - <sha...>
remaining_gates:
  - package data
  - fresh init
  - existing update preservation
  - final provider/dogfood inventory parity
  - public reference docs
  - full pytest/static analysis
  - Epic-wide manual workflow
  - Epic AC closure
  - mergeable Epic PR
merge_prepared: not_claimed
```

Issue 319はW1–W4のdistribution、docs、full quality、Epic closure、mergeable PRを所有する。

**Issue Finish conditions**

* Requirement/design/planがfresh reviewed。
* Assurance valid。
* `C317-01–11` closed with observed evidence。
* Required tests/manual checks completed。
* Final QA/code/spec reviewsにblocking findingなし。
* Report final ledgersにopen blocking entryなし。
* Commit/push/clean/deferred relay complete。
* その後にのみ`issue finish`を実行する。

本候補はこれらの条件が現在満たされたとは主張しない。

---

## ADOPTION_MATRIX

### A. Repository facts

| Claim                                                                        | Classification                               | Evidence                                           | Planning disposition             |
| ---------------------------------------------------------------------------- | -------------------------------------------- | -------------------------------------------------- | -------------------------------- |
| Current branchと指定HEADへアクセスできた                                                | Repository fact                              | GitHub connectorでHEAD取得。                           | Adopt as inspection baseline     |
| #315/#316 completed、#317 open                                                | Repository fact                              | GitHub issue state。                                | Adopt                            |
| Issue317 requirement/design/planは未完成scaffold                                 | Repository fact                              | Current branch files。                              | S00 prerequisite                 |
| Parent owns separate `artifact import`                                       | Repository fact / parent contract            | Epic requirement/design。                           | Adopt                            |
| `chatgpt-output` is import kind, storage identity is blank                   | Accepted repository decision                 | Accepted ADR。                                      | Adopt without reopening          |
| Blank prefix must not be reserved                                            | Accepted repository decision                 | Accepted ADR。                                      | Adopt                            |
| Current parser has `new artifact` and node `import`, but no `artifact` group | Repository fact                              | Current parser。                                    | Use to identify syntax drift     |
| Current Artifact catalog does not contain `chatgpt-output`                   | Repository fact                              | `SUPPORTED_ARTIFACT_TYPES`。                        | Preserve                         |
| `chatgpt-output-*` is currently valid blank grammar                          | Repository fact inferred from current parser | Blank prefix rejection checks onlysupported types。 | Preserve with regression         |
| Current allocator usesstandard + `01..99` slots                              | Repository fact                              | Allocator implementation。                          | Reuse                            |
| Current `create_artifact_doc` is text/template based                         | Repository fact                              | Template render/write path。                        | Do not reuse for body            |
| Current `create_artifact_doc` allocates before acquiring lock                | Repository fact                              | Allocation then lock order。                        | Refine in S01 for concurrency    |
| Existing create lock isO_EXCL/token-owned                                    | Repository fact                              | Lock implementation。                               | Reuse                            |
| Current validator does not parse generic Artifact body                       | Repository fact                              | Filename/duplicate scan only。                      | Reuse                            |
| Blank import will not enter ADR mirror                                       | Repository fact                              | Collector only acceptsparsed typed `adr`。          | Regression-test                  |
| Current sync projection exposes Artifact directory only                      | Repository fact                              | `future_artifacts.path/present`。                   | Keep unchanged                   |
| Current public Artifact rules arenew-artifact/frontmatter centric            | Repository fact                              | Rules text。                                        | Relay docs drift to S90/Issue319 |

### B. Recommended Issue-local claims

| Claim                                                                        | Classification                   | Rationale                                                                            | Required verification              |
| ---------------------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------- |
| Add top-level `artifact import` rather than `import artifact`                | Recommended                      | Parent is contract owner; avoids mixing with node import                             | Parser/help/spec review            |
| Accept repo-relative and absolute paths only within approved Workbench roots | Recommended                      | Caller-specified source without arbitrary host import                                | Path matrix                        |
| Hold shared create lock through allocation/stage/publish                     | Recommended                      | Smallest coherent race boundary                                                      | Concurrency and performance review |
| Reallocate `new artifact` destination inside lock                            | Recommended                      | Required for concurrent import/new suffix behavior                                   | Existing new artifact regression   |
| Add dedicated `ArtifactBinaryPublisher`                                      | Recommended                      | Text and recursive-copy adapters have wrong semantics                                | Layer/code review                  |
| Use same-directory temp without `.md` suffix                                 | Recommended                      | Same filesystem/no scanner visibility                                                | Temp and validate tests            |
| Use source pre/copy/temp/post SHA-256                                        | Recommended                      | Detects same-size mutation and torn copy                                             | Fault injection                    |
| Publish with atomic no-replace primitive                                     | Recommended                      | No-overwrite under external writer race                                              | Adapter/concurrency tests          |
| Treat post-publish cleanup/durability/lock release as committed warning      | Recommended                      | Avoid hidden commit and duplicate retry                                              | Result/presentation tests          |
| Accept invalid UTF-8, NUL, and zero bytes                                    | Recommended, derived from parent | Bytes are opaque; no classifier                                                      | Binary fixture matrix              |
| Reject source alias to existing formal Artifact                              | Recommended safety refinement    | Prevents Workbench hard-link from acting as formal Artifact source                   | Supported-host hard-link test      |
| Do not auto-run sync                                                         | Recommended compatibility        | Import changes evidence file only; current create artifact has no auto-sync contract | Sync regression                    |

### C. Explicit assumptions

| Assumption                                                          | Basis                                                                                  | Risk if wrong                                                      | Resolution point          |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------- |
| “Caller-specified path” remains restricted to root/scoped Workbench | Parent requirement and ADR are narrower than operator wording                          | Arbitrary repo/host import would require requirement/ADR amendment | Before requirement review |
| Absolute path inside current repo is acceptable                     | Existing CLI uses absolute paths for some filesystem selectors; no source syntax fixed | Product owner may prefer repo-relative only                        | Requirement/spec review   |
| `.md` means exact lowercase suffix                                  | Parent repeatedly writes `.md`; current Artifact grammar is lowercase                  | Case-insensitive filesystems may surprise users                    | CLI tests/docs            |
| Zero-byte source is valid                                           | Opaque bytes and no content classifier                                                 | Some operators may not view it as Markdown                         | Requirement review        |
| Shared lock may be held duringmultiple byte passes                  | Simplicity over throughput                                                             | Large imports block other creates                                  | QA/performance review     |
| Committed warnings should exit 0                                    | Warning is not retry-safe failure                                                      | Existing CLI policy may choose a distinct exit contract            | Design review             |
| Standard grade remains suitable                                     | Parent W3 suggests Standard and no migration/schema                                    | Assurance classifier may authorize stricter profile                | S00 classify              |
| Existing Artifact listing/context needs no new command              | No dedicated command found in inspected parser/projection                              | A private consumer may enumerate bodies                            | S07 consumer inventory    |

### D. Rejected alternatives

| Alternative                                  | Classification                                   | Rejection basis                                                                                 |
| -------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| Overload `new artifact`                      | Rejected                                         | Parent explicit separation; text/template semantics                                             |
| Add `chatgpt-output` totyped catalog         | Rejected                                         | Accepted ADR                                                                                    |
| Reserve `chatgpt-output-*` blank prefix      | Rejected                                         | Accepted user/ADR coexistence decision                                                          |
| Infer import provenance fromfilename         | Rejected                                         | Imported and template blank intentionally indistinguishable                                     |
| Frontmatter or sidecar receipt               | Rejected                                         | Byte-preserving/single-file/no-catalog boundary                                                 |
| UTF-8 validation                             | Rejected                                         | Opaque bytes                                                                                    |
| Markdown/content/secret classifier           | Rejected for MVP                                 | Parent non-scope                                                                                |
| `copy_workbench()` reuse                     | Rejected                                         | Recursive source-wins/overwrite semantics                                                       |
| `os.replace` or check-then-replace           | Rejected                                         | Existing destination overwrite race                                                             |
| Direct source→final hard-link                | Rejected                                         | Copy-not-move and source/destination aliasing                                                   |
| Generic transaction, journal, orphan GC      | Rejected for MVP                                 | Scope expansion and managed state                                                               |
| Automatic EAL/canonical modification         | Rejected                                         | Authority boundary and Issue318 ownership                                                       |
| Model/reviewer config changes                | Rejected from product plan                       | Execution infrastructure, explicitly excluded by brief                                          |
| Attached exception/failure-taxonomy proposal | Not applicable / rejected as source for Issue317 | It concerns an unrelated application exception hierarchy rather than SpecDock Artifact import.  |

### E. Information still insufficient or unverified

| Item                                            | Current status                                               | Required follow-up                                                 |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------ |
| Cross-platform atomic no-replace implementation | Insufficient                                                 | POSIX/Windows/filesystem adapter probe; unsafe fallback prohibited |
| Directory fsync support and warning names       | Insufficient                                                 | Platform tests and presentation review                             |
| Exact error/warning tokens                      | Issue-local open delta                                       | Freeze in design after current convention inventory                |
| Exact new module names                          | Issue-local open delta                                       | Choose smallest layout during S02/S04                              |
| Dedicated Artifact listing/context consumers    | No dedicated CLI found; full private inventory not completed | `rg`/callsite inventory in S07                                     |
| Lock duration for large files                   | Not measured                                                 | QA risk assessment; no size framework unless observed              |
| Source hard-link alias policy portability       | Not verified                                                 | Supported-host tests and explicit skip policy                      |
| Crash orphan-temp manual guidance               | Not written                                                  | S90/Issue319 docs relay                                            |
| Package/fresh init/update parity                | Not performed                                                | Issue319                                                           |
| Full suite/static analysis                      | Not performed by this analysis                               | S99 risk-calibrated checks and Issue319 full gate                  |
| Reviewer verdicts                               | None for this candidate                                      | Fresh requirement/design/plan reviewers                            |
| Runtime/test success                            | No commands executed by this ChatGPT analysis                | Codex-controlled implementation workflow                           |
| Canonical adoption                              | Not performed                                                | EAL disposition and human/reviewer-controlled integration          |

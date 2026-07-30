---
種別: 要件定義書（Epic）
ID: "epic-00343"
タイトル: "Workbench Shell And Explicit File Artifact Import"
関連GitHub: ["#343"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["init-local-00002"]
---

# epic-00343 Workbench Shell And Explicit File Artifact Import — 要件定義

## 1. 目的

このEpicは、SpecDockの一時作業領域と永続Artifactの境界を、利用者が迷わず使える二つのoperator-facing capabilityとして提供する。

1. fresh `spec-dock init`および今後作成するInitiative / Epic / Issueに、すぐ使えるWorkbench shellを自動配置する。
2. Workbench内外、repository内外を問わず、利用者が明示したsingle file一件を、指定scopeのArtifactへ安全にimportできるようにする。

Workbenchはcanonical stateではなく、存在しなくてもrepositoryはvalidである。利用方法を説明する`.workbench/README.md`だけをGit管理し、それ以外のWorkbench contentsはGit管理せず、worktree-localかつdisposableとする。永続化が必要なfileだけを明示importして`artifacts/`へ保存する。

## 2. Initiativeとの整合

親Initiative `init-local-00002 Prototype Feature Expansion`は、既存architecture guardrailを守りながら利用者が体感できる機能価値とoperator valueを追加するauthorityを持つ。本Epicは次の理由でそのscopeに属する。

- Workbench shell自動生成は、fresh repositoryとfuture nodeを作成した直後のoperator valueを追加する。
- explicit single-file importは、任意fileをdurable evidenceへ昇格する新しいworkflow capabilityを追加する。
- provider/generated source-of-truth、sync contract、persistent architectureは再定義しない。
- architecture maintenanceが必要になった場合は`init-local-00003`のguardrailをdependencyとして扱い、本Epicへcleanupを混在させない。

旧`epic-00312`はWorkbench copyとChatGPT Markdown preservationを中心とするhistorical contractとして保持する。本Epicはその旧Issueを再開せず、確定した新しいtarget stateだけを扱う。

## 3. Target state

### 3.1 Workbench shell

- fresh initはroot Workbench shellを生成する。
- 今後の`new initiative` / `new epic` / `new issue`は、作成nodeにWorkbench shellを生成する。
- shell fileは意味のないplaceholderではなく、Workbenchの目的・利用方法・非canonical境界を説明する`.workbench/README.md`とする。
- `.workbench/README.md`だけをGit tracking可能とし、Workbench内のその他のentryはignoreする。
- existing root / nodeへはbackfillしない。
- WorkbenchまたはREADMEが欠けていてもvalidとする。
- Workbench内容はworktree-localであり、worktreeを破棄すれば失われてよい。

### 3.2 Explicit single-file Artifact import

- 一つのcommandでexactly one source fileとexactly one target scopeを明示する。
- targetはroot / Initiative / Epic / Issueを扱う。
- sourceはWorkbench内外、repository内外のreadable regular fileを扱う。
- explicit source pathの指定自体をread authorizationとし、repository外専用の追加許可flagを要求しない。
- source bytes、source file、original basename / extensionを可能な限り保持する。
- destination filenameにはArtifact grammarと衝突回避に必要なprefixを自動付与する。
- title / slug、typed `file` token、source-kind catalogを要求しない。

### 3.3 Workbench copy

- linked worktree作成時にWorkbench内容は自動移行しない。
- 必要な場合だけ既存`workbench copy`を利用者が明示実行する。
- watcher、continuous sync、copy-back、自動hookを追加しない。
- 本Epicでは補助機能の互換性だけを扱い、新しいlifecycleの中心にしない。

## 4. スコープ

### 4.1 必須

- fresh-init-only root Workbench shell。
- future Initiative / Epic / Issue Workbench shell。
- tracked `.workbench/README.md`を除くWorkbench contentsのGit ignore。
- optional presence、no-backfill、opacity、disposable contract。
- generic single-file Artifact importのCLIからfilesystem publicationまで。
- root / Initiative / Epic / Issue target routing。
- repository内外のexplicit source path。
- original basename / extensionを保つfilename allocation。
- byte identity、source survival、collision safety、no-overwrite、content-free output。
- arbitrary binary / invalid UTF-8 Artifactと標準commandの互換性。
- provider assets、packaging、installed consumer、dogfood projection、docs、tests。
- existing `artifact import chatgpt-output`、`new artifact`、`workbench copy`の互換性。

### 4.2 禁止

- existing root / nodeへのWorkbench backfill。
- Workbench presenceのvalidation必須化。
- `.workbench/README.md`以外のWorkbench contentsのGit tracking。
- automatic handoff、watch、sync、copy-back。
- directory、glob、bulk、recursive、multiple-file import。
- source contentsのparse、classification、format conversion、archive extraction。
- typed `file` filename token、template、persistent source-kind catalog。
- source delete、move、overwrite。
- importによるrequirement / design / plan / report / ADR / assuranceの自動変更。
- architecture cleanupを利用者価値と無関係に抱え込むこと。

### 4.3 対象外

- Workbench retention / TTL / session model。
- directory bundle format。
- background index / provenance database。
- content safety certification。
- unrelated installer、scanner、artifact catalogの再設計。
- 旧Issue nodeの再利用または再開。

## 5. 非交渉制約

- implementation authorityは`src/spec_dock/`、shipped runtime/assetsは`src/spec_dock/assets/spec_dock/**`に置く。
- `spec-dock/**`はdogfood projection / validation surfaceであり、独立したprimary implementationを置かない。
- Workbenchはnon-canonical、worktree-local、disposableである。
- import destinationはrepository内のfixed `artifacts/`から外れない。
- sourceはexactly one readable regular fileとし、leaf symlinkは拒否する。
- explicit pathのancestor directoryにsymlinkが含まれることは許容する。ただし解決先のfile identityを固定し、指定外entryを走査しない。
- source bytesとsource fileを成功・失敗の両方で変更しない。
- import successはevidence保存の結果であり、canonical adoptionやreview resultを表さない。
- external absolute path、file body、content-derived valueを通常text / JSON / tracked provenanceへ出さない。
- existing public commandsとArtifact namingの互換性を維持する。

## 6. Epic requirements

### 6.1 Workbench shell

- E-RQ-001 Fresh root shell:
  - `spec-dock`が存在しないtargetへのfresh `spec-dock init`は、root Workbench directoryとtracked `.workbench/README.md`を生成する。
- E-RQ-002 Future node shell:
  - 今後の`new initiative` / `new epic` / `new issue`は、作成node直下にWorkbench directoryとtracked `.workbench/README.md`を生成する。
- E-RQ-003 Tracked shell / ignored contents:
  - tracked shell fileは`.workbench/README.md`とし、空placeholderや`.gitkeep`を新規生成しない。
  - READMEは、少なくともWorkbenchの目的、一時的・worktree-local・non-canonicalであること、README以外のcontentsはGit管理外であること、永続化する一fileは明示的に`artifact import file`で対象Artifactへ取り込むこと、worktree間のcopyは必要時だけmanual `workbench copy`を使うこと、Git ignoreはsecret保護境界ではないことを説明する。
  - READMEは人間とmodelへのguidanceであり、SpecDockがWorkbench contentsをsemantic discoveryする入口やcanonical authorityにはしない。
  - `.workbench/README.md`だけがGit tracking可能で、同じWorkbench内のその他すべてのentryはdepth、extension、contentによらずignoreされる。
- E-RQ-004 Optional presence:
  - WorkbenchまたはREADMEがないexisting root / nodeもvalidとし、利用者が手動作成できる。
- E-RQ-005 No backfill:
  - `init` against existing workspace、`update`、`sync`、`validate`、active切替、Artifact / ADR作成など既存scopeを対象とする通常mutationは、existing root / Initiative / Epic / IssueへWorkbench READMEを追加しない。
  - new node commandは新しく作成したnodeだけにREADMEを生成し、既存ancestor / siblingへはbackfillしない。
- E-RQ-006 Opaque and disposable:
  - Workbench subtreeはdefault semantic discoveryから除外し、その内容をnode、Artifact、ADR、dependency、authoring sourceとして解釈しない。
  - Workbench内容の欠落またはworktree削除はSpecDock validityやcanonical readinessを損なわない。
- E-RQ-007 Manual copy only:
  - `workbench copy`は利用者が明示実行する場合だけ動作し、自動hook、watch、sync、copy-backを持たない。

### 6.2 Generic single-file import

- E-RQ-008 Explicit command:
  - `artifact import file --file <path>`を提供し、exactly one target selectorを要求する。
- E-RQ-009 Target matrix:
  - targetは`--root`、`--initiative <id>`、`--epic <id>`、`--issue <id>`のいずれか一つとする。
  - root destinationは`spec-dock/artifacts/`、node destinationは各nodeの`artifacts/`とする。
- E-RQ-010 Source locations:
  - root / scoped Workbench、repository内のその他のpath、repository外のpathを同じcommandで受け付ける。
  - relative source pathはrepository rootを基準に解決する。repository外のrelative pathは`..`を含むexplicit pathとして同じ基準で解決する。
- E-RQ-011 Source eligibility:
  - exactly one readable regular leaf fileを許可する。
  - missing path、directory、leaf symlink、FIFO、socket、device、unreadable fileはformal destination作成前に拒否する。
  - ancestor symlinkは許容するが、解決先identityをimport中に一貫して検証する。
- E-RQ-012 Explicit-path authorization:
  - repository外sourceに追加optionを要求しない。
  - 指定fileの親directoryや周辺entryをenumerateしない。
- E-RQ-013 Byte and source preservation:
  - sourceをopaque byte streamとして保存し、最終Artifactのbyte countとSHA-256がsourceと一致する。
  - import command自身は、成功・失敗のいずれでもsourceをwrite、delete、move、renameしない。
  - external actorによるimport中のsource identity / bytes変更を検知した場合は、不完全または旧版のArtifactをsuccessとして公開しない。
- E-RQ-014 Filename contract:
  - standard filenameは`<timestamp>--<safe-original-basename>`とする。
  - collision時は`<timestamp>-<nn>--<safe-original-basename>`とし、bounded suffixを用いる。
  - `--`はgeneric imported-file familyをexisting typed / blank Markdown grammarから分離するdelimiterであり、typed `file` tokenまたはpersistent source-kind catalogではない。
  - original basename、extension chain、case、Unicode、spaceはpath safetyとcomponent lengthに必要な場合だけ変更する。
  - generic imported fileのstable public identityはfull destination basenameとする。
  - timestampとoptional numeric suffixからなるallocation slotはexisting typed / blank Artifactと共有し、同じslotを異なるfamilyへ二重割当しない。
- E-RQ-015 Minimal normalization:
  - path separator、control character、destination filesystemで使用不能な文字、末尾dot / space、component lengthだけを安全化する。
  - `--title` / `--slug`を要求せず、typed `file` tokenをfilenameへ追加しない。
- E-RQ-016 Collision and no-overwrite:
  - existing Artifactと同じidentity / pathを再利用せず、concurrent creationでも既存fileを置換しない。
  - 利用可能なbounded suffixがない場合は、既存fileを変更せず明示的に失敗する。
- E-RQ-017 Atomic visibility:
  - successとして返るArtifactは完全なverified bytesだけを公開する。
  - publish前failureはformal destinationを残さない。
  - publish後のdurability / cleanup warningは、committed destinationが存在する部分成功状態として、通常成功および未commit failureと機械判定可能に区別する。
  - callerが再実行不要と判断できるobservable stateを返し、自動retryで重複を作らない。exact status / exit / field名はdesignで固定する。
  - macOSのnamed staging cleanupでは、同一UIDでdestination directoryを変更でき、high-entropy internal staging nameを発見・監視し、最終FD/path identity check後から`unlink` syscallまでにそのpathnameを意図的に別entryへ置換するactorだけを保証対象外とする。この限定は包括的same-UID waiverではない。偶発collision、最終checkまでに観測可能なreplacement、formal destinationのno-replace、source bytes / non-mutation / privacy、destination parent identity、mismatchまたはuncertainty時にunlinkせずretainする義務は維持する。詳細はaccepted ADR `20260730t085831z-adr`を正本とする。
- E-RQ-018 Privacy / content-free output:
  - repository内sourceはrepo-relative pathを返せる。
  - repository外sourceはbasenameだけを返し、absolute path、body、content-derived valueを成功、preflight failure、publication failure、post-publication warningの全user-visible text / JSON / diagnosticとtracked provenanceへ含めない。
- E-RQ-019 Authority isolation:
  - importはcanonical docs、accepted ADR、report ledger、assurance stateを編集しない。
  - 保存結果はevidence-onlyであり、採否には別のreview / adoptionが必要である。
- E-RQ-020 Opaque Artifact lifecycle:
  - extension、MIME、encoding、archive content、file purposeを分類しない。
  - standard validate / sync / default discoveryはimported Artifactのname / identityだけを扱い、bodyをMarkdownやUTF-8としてdecode / parseしない。
  - binary、archive、invalid UTF-8をimportした後もrepositoryはvalidであり、標準commandがその内容を理由に失敗しない。
  - original basenameが`adr-`その他のexisting typed Artifact grammarと一致しても、generic imported fileをtyped Artifact、ADR、canonical sourceとして解釈しない。

### 6.3 Compatibility / distribution

- E-RQ-021 `chatgpt-output` compatibility:
  - current command、Workbench-only lowercase `.md` guard、title / slug behavior、blank naming、result contractを維持する。
- E-RQ-022 Existing Artifact compatibility:
  - `new artifact`のcatalog / templates / typed and blank Markdown identityを変更せず、generic importと安全にcoexistさせる。
- E-RQ-023 Workbench copy compatibility:
  - existing explicit one-shot source-wins behaviorとfailure boundaryを維持する。
- E-RQ-024 Provider / consumer parity:
  - provider implementation、packaged assets、fresh installed consumer、updated consumer、dogfood projectionで同じbehaviorを提供する。
- E-RQ-025 Documentation:
  - public guide、naming、authoring workflow、worktree referenceは、shell auto-generation、generic import、manual-only copy、evidence authority boundaryを説明する。

## 7. Epic acceptance criteria

### 7.1 Workbench

- E-AC-001 Fresh root shell:
  - fresh init後にroot `.workbench/README.md`が存在し、Git add対象になる。
  - README本文がE-RQ-003の目的、Git境界、Artifact import、manual copy、disposable、secret注意を説明する。
- E-AC-002 New-node matrix:
  - new Initiative / Epic / Issueの各nodeに`.workbench/README.md`が作られ、planned path / result / filesystemが一致する。
  - rootと3 node kindsのREADMEは同じcanonical guidance内容を持つ。
- E-AC-003 Ignore matrix:
  - rootと3 node kindsのWorkbenchにarbitrary nested filesを置いてもREADME以外は`git status`へ出ない。
- E-AC-004 No-backfill matrix:
  - READMEのないexisting root / Initiative / Epic / Issueを用意する。
  - existing workspaceへの`init`、`update`、`sync`、`validate`、active切替、Artifact / ADR作成を各scopeへ実行しても、どのexisting scopeにもREADMEを生成しない。
  - new node作成時はnew nodeだけにREADMEを生成し、existing ancestor / siblingのREADME状態とWorkbench bytes / names / mtimesを変更しない。
- E-AC-005 Optional validity:
  - Workbenchのないscopeと利用者が手動作成したWorkbenchの双方でvalidate / syncが成功する。
- E-AC-006 Opacity regression:
  - Workbench内のfake metadata、ADR-like Markdown、binary、large / broken subtreeがdiscovery result、error、source manifestへ影響しない。
- E-AC-007 Copy positioning:
  - linked worktree creationでcontentsは自動移行せず、明示`workbench copy`だけがcurrent one-shot behaviorを実行する。

### 7.2 Import

- E-AC-008 Target matrix:
  - arbitrary regular fileをroot / Initiative / Epic / Issueへimportできる。
  - zero / multiple target selectorはsourceまたはdestination mutation前に失敗する。
- E-AC-009 Source location matrix:
  - root Workbench、scoped Workbench、repository内のWorkbench外、repository外のabsolute / relative fileが追加flagなしで成功する。
  - nested working directoryから実行してもrelative source pathはrepository root基準で同じfileへ解決される。
- E-AC-010 Eligibility and ancestry matrix:
  - regular leaf file、ancestor symlinkを含むexplicit pathは同じresolved file identityで成功する。
  - missing、directory、leaf symlink、FIFO / socket / device、unreadable file、import中にidentityが変化するsourceはformal destinationを残さず失敗する。
- E-AC-011 File-form matrix:
  - `.md`、`.MD`、text、PDF、image、ZIP、multi-suffix、no-extension、empty、invalid UTF-8、NULをopaque bytesとして保存する。
- E-AC-012 Filename preservation:
  - normal basename / extensionは`--` delimiter後に保持され、Unicode / space / multi-suffixとpath-unsafe nameのdeterministic minimal normalizationが検証される。
  - `adr-decision.md`、`research-note.md`などexisting typed grammarと一致するoriginal basenameもgeneric imported-file familyとして識別され、semantic parseされない。
- E-AC-013 Byte identity / source survival:
  - sourceとfinalのbytes、SHA-256、byte countが一致し、source path / bytesは変わらない。
- E-AC-014 Collision and concurrency:
  - generic import同士、generic importと`new artifact`、generic importと`chatgpt-output`が既存fileを変えずunique identityを得る。
  - full destination basenameがgeneric importのstable identityとして返り、timestamp / optional suffix slotは全Artifact family間で一意になる。
  - bounded suffix exhaustionは既存fileを変えず明示失敗する。
- E-AC-015 Publication faults:
  - external actorによるsource mutation、hash mismatch、write / publish failure、post-publish durability / cleanup warningをfault injectionし、E-RQ-013、016〜017のobservable boundaryを満たす。
  - command自身がsourceへwrite / delete / move / renameを行わないことをfilesystem observationで確認する。
  - post-publish warningはcommitted destination、再試行不要、warningありをtext / JSON / process outcomeから機械判定できる。
  - macOS named staging cleanupについて、final FD/path identity checkまでに観測できるreplacement、missing、special entry、stat/open failureではunlinkせずreplacement sentinelを残す。final check後から`unlink`までの意図的same-UID replacementは、E-RQ-017の限定された保証対象外であり、完全防御のpass条件としては主張しない。
- E-AC-016 Privacy / authority:
  - external absolute path、body、content-derived valueを、成功、target preflight failure、source preflight failure、allocation / collision exhaustion、source mutation、publication failure、post-publication warning、unexpected runtime failureの全text / JSON / diagnosticとtracked provenanceへ出さない。
  - importによるcanonical docs / report / ADR / assurance mutationがない。
- E-AC-017 Opaque lifecycle compatibility:
  - representative binary、ZIP、invalid UTF-8、NUL fileを各targetへimportした後、`validate`、`sync`、default discovery、dependency / context生成がcontent decode errorなく成功する。
  - imported bodyはsemantic sourceやMarkdownとして解釈されない。
  - typed Artifactに見えるoriginal basenameを持つgeneric Markdown / binary fileもADR mirrorやtyped Artifact discoveryへ参加しない。
- E-AC-018 Existing command compatibility:
  - current `chatgpt-output`、`new artifact`、`workbench copy`のfocused testsがpublic behavior差分なしで成功する。

### 7.3 Distribution / closure

- E-AC-019 Distribution:
  - source tree、candidate wheel fresh init、pre-feature existing update、dogfood projectionでshell / import behaviorとno-backfillを確認する。
- E-AC-020 Final closure:
  - E-RQ-001〜025とE-AC-001〜019の実測結果がEpic reportへtraceされ、blocking findingが残らない。

## 8. Failure semantics

| Phase | Failure example | Required outcome |
|---|---|---|
| target preflight | invalid / ambiguous scope、multiple selectors、unsafe destination | mutationなし、formal fileなし |
| source preflight | missing、non-regular、leaf symlink、unreadable | destination fileなし |
| source stability | identity / bytes change | incomplete fileを公開せず失敗 |
| allocation | collision exhaustion、invalid current Artifact state | existing fileを変更せず失敗 |
| publication | write / verify / publish failure | successを返さず、不完全formal fileなし |
| post-publication | durability / cleanup warning | committed部分成功を通常成功・未commit failureから機械判定可能にし、自動retryしない |
| macOS named-staging cleanup | final check後からunlinkまでの意図的same-UID pathname replacement | E-RQ-017で限定した保証対象外。その他のmismatch / uncertaintyはunlinkせずretain |

## 9. 非機能要件

- Reliability:
  - no-overwrite、source survival、atomic visibilityをobservable contractとする。
- Security / privacy:
  - explicit file一件以外を探索せず、external absolute pathやbodyを通常outputへ出さない。
- Compatibility:
  - existing commands、old Artifact families、existing root / nodeのWorkbench README有無を変更しない。
- Portability:
  - supported platformで同じobservable guaranteeを満たす。macOS named staging cleanupの限定されたsame-UID final-window boundaryはaccepted ADR `20260730t085831z-adr`に従う。具体的filesystem primitiveはdesignで決定する。
- Maintainability:
  - provider-firstとcurrent layered architectureを維持する。
- Performance:
  - file全体をmemoryへ読み込まず、bounded memoryでcopyできること。

## 10. 証跡とauthority

- raw / advisory evidence:
  - 旧`epic-00312/artifacts/20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md`
  - 旧`epic-00312/artifacts/20260728t054625z-interview-workbench-tracked-shell-coverage.md`
  - 旧`epic-00312/artifacts/20260728t060417z-interview-generic-file-import-filename-contract.md`
  - 旧`epic-00312/artifacts/20260728t060706z-interview-external-file-import-policy.md`
  - 旧`epic-00312/artifacts/20260728t060909z-interview-workbench-copy-disposition.md`
  - 旧`epic-00312/artifacts/20260728t080013z-research-chatgpt-pro-epic-replanning-zip-evidence.md`
- canonical authority:
  - 本`requirement.md`
  - fresh reviewを通過した`design.md` / `plan.md`
  - accepted ADR
  - `report.md` Evidence Adoption Ledger
- ChatGPT ZIPはadvisory authoring packであり、main orchestratorの再記述とfresh reviewを経ない内容は正本ではない。

## 11. 後続Issue seed

- vertical capability候補:
  1. Workbench Shell Scaffolding。
  2. Generic Single-File Artifact Import。
  3. Integration / Distribution / Final Quality。
- Issue nodeはplanのfresh reviewと人間のslice承認後にだけ作成する。
- allowed local delta:
  - exact symbol / file placement、platform-feasible filesystem primitive、CLI error / result field detail、test fixture。
- forbidden parent boundary changes:
  - no-backfill違反、自動copy / sync、bulk import、content classifier、typed token、source delete、canonical auto-adoption。
- expected evidence:
  - focused unit / CLI / integration、candidate wheel fresh / update、dogfood parity、manual external-file scenario、fault injection、full quality review。

## 12. 未確定事項

なし。ユーザー判断、repository調査、ChatGPT advisory pack、fresh review指摘を本書の要件へ反映済みである。

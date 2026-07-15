---
種別: 要件定義書（Issue）
ID: "iss-00317"
タイトル: "Byte Preserving ChatGPT Output Artifact Import"
関連GitHub: ["#317"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312", "init-local-00003"]
---

# iss-00317 Byte Preserving ChatGPT Output Artifact Import — Issue 要件定義

## 目的
- Current worktreeのrootまたはscoped `.workbench/`にあるsingle Markdown fileを、sourceを残したまま、本文bytesを変更せず指定scopeの`artifacts/`へ明示的にimportできるようにする。
- Template-based `new artifact`と分離した保存経路により、完成済みChatGPT reportをCodexが要約・再構成する前のevidenceとして永続化する。

## 親trace
- Epic requirements: E-RQ-019–023。
- Epic acceptance: E-AC-013–015。
- Epic design: DS-003 Byte-preserving Artifact import、accepted ADR `adr-20260713t031808z-template-free-artifact-import-and-blank-filename-coexistence`。
- 依存: Issue 315のWorkbench ignore/opaque traversal foundationが完了していること。Issue 316はformal dependencyではないが、current branch上のpath guardとfilesystem adapter patternを実装参考にできる。
- 継承する不変条件:
  - `chatgpt-output`はimport operation kindであり、新しいtyped Artifact tokenではない。
  - Destinationはexisting blank Artifact grammarを使い、`new artifact blank --slug chatgpt-output-*`を許容し続ける。Filenameだけではcreation routeを区別しない。
  - Provider authorityは`src/spec_dock/assets/spec_dock/**`。Dogfood `spec-dock/**`はinstalled verification surface。
  - Imported outputはevidence-onlyであり、command success、filename、bodyからcanonical authority、accepted ADR、reviewer passを得ない。

## 観測可能な成果
- `artifact import chatgpt-output`が、exactly one destination scope、source `.md` file、title、任意slugを受け取る。
- Sourceはcurrent worktreeのrootまたはInitiative/Epic/Issue direct-child scoped `.workbench/`配下に限定され、destination scopeとは独立して指定できる。
- Destination basenameだけを`<timestamp>-chatgpt-output-<slug>.md`またはexisting collision suffix形で生成し、parser上はblank Artifactとして扱う。
- Source、staged copy、published destinationのSHA-256とbyte countが一致し、sourceは成功・失敗の双方で残る。
- Frontmatter、template、formatting、summary、encoding変換、newline正規化を行わず、bytesをopaqueとして扱う。
- Publish前failureではformal Artifactを残さず、owned temporary fileをcleanupする。Publish後warningではcommitted pathを明示し、無条件retryを誘発しない。
- Help、text、JSONはimport kind、blank storage identity、scope/source/destination、hash、byte count、commit/warning stateをcontent-freeに表現し、authorityをself-claimしない。
- Generic validateはimported fileをexisting blank grammarとして受理し、ADR mirror、canonical docs、EAL、assurance stateをcommandが自動変更しない。

## Issue要件
- RQ-317-001 Separate explicit command:
  - `artifact import chatgpt-output`を独立commandとして追加し、明示実行時だけ作動する。
  - `new artifact`のmode/flag、automatic promotion、copy-on-rewrite、background importとして実装しない。
- RQ-317-002 Minimal input contract:
  - InputはMVP import kind `chatgpt-output`、exactly one Initiative/Epic/Issue selector、`--file`、`--title`、optional `--slug`、existing global JSON conventionに限定する。
  - Move、overwrite、destination basename、encoding、template、frontmatter、multiple-file optionを設けない。
- RQ-317-003 Source placement and eligibility:
  - Sourceはcurrent worktreeの`spec-dock/.workbench/`またはresolved Initiative/Epic/Issue directory direct-child `.workbench/`配下のsingle regular non-symlink fileとする。
  - Lowercase `.md` filename以外、directory、symlink source、Workbench外path、multiple files、special filesystem entryはcopy開始前にfailする。
- RQ-317-004 Containment and source survival:
  - Repo rootからapproved Workbench rootとsourceまでのlexical/physical containmentを確認し、symlinked ancestorやscope外readを拒否する。
  - Commandはsourceをdelete、rename、truncate、rewrite、chmodせず、source inodeをdestinationとしてrename/hard-linkしない。
- RQ-317-005 Opaque byte preservation:
  - Binary streamとしてcopyし、encoding detection/validation/conversion、Markdown parse、frontmatter/template application、formatting、summary/restructure、newline/final-newline normalizationを行わない。
  - UTF-8 BOM、LF/CRLF、final newline有無、日本語、NUL、invalid UTF-8、zero-byteをcontent理由で変換・拒否しない。
- RQ-317-006 Blank naming coexistence:
  - Titleまたはexplicit slugをexisting normalizationへ通し、blank slug `chatgpt-output-<normalized-slug>`を生成する。
  - `chatgpt-output`を`SUPPORTED_ARTIFACT_TYPES`、template catalog、typed parser branch、reserved blank prefixへ追加しない。
  - Existing `new artifact blank --slug chatgpt-output-*`とimportを同一blank grammar上で共存させる。
- RQ-317-007 Shared allocation and no overwrite:
  - Existing timestamp/collision suffix allocationとArtifact create serializationを共有し、same-second import/import、import/new-artifact concurrencyでも別slotを割り当てる。
  - Existing Artifactを上書きせず、collision exhaustionはformal/source mutationなしでfailする。
- RQ-317-008 Verified staging:
  - Formal destinationと同じfilesystem上のowned temporary destinationへbinary copyする。
  - Publish前にsource、copy stream、staged fileのSHA-256とbyte countを照合し、source replacement/mutationを検知した場合はfailする。
- RQ-317-009 Atomic no-replace publication:
  - 検証済みstaged fileだけを、existing destinationを置換しないprimitiveでformal pathへpublishする。
  - Check-then-overwriteやoverwrite可能なreplaceを安全性根拠にせず、external writer raceでexisting bytesを変更しない。
- RQ-317-010 Failure and cleanup boundary:
  - Copy、hash、source mutation、file fsync、unsupported no-replace、bounded publish retry exhaustion等のpublish前failureではformal destinationを残さず、owned temp cleanup状態を返す。
  - Transient publish `EEXIST`はexisting fileを変更せずstateを再scanして別slotへbounded reallocationする。Suffixまたはretry exhaustion時だけno-formal-write failureとする。
  - Publish後のdirectory durability、cleanup、post-confirmation等のfailureはcommitted destinationをrollbackせず、committed pathを伴うwarningとして区別する。
  - General transaction journal、rollback framework、orphan-temp catalog/GCを追加しない。
- RQ-317-011 Output secrecy and authority isolation:
  - Resultはimport kind、storage identity `blank`、Artifact ID、scope ID、repo-relative source/destination、SHA-256、byte count、commit/durability/cleanup stateに限定する。
  - File body、secret-like value、absolute host path、raw OS exception、canonical/adopted/reviewed claimをtext/JSONへ含めない。
  - Commandはcanonical docs、accepted ADR、EAL、assurance stateを編集しない。
- RQ-317-012 Existing consumer compatibility:
  - Generic Artifact validation/duplicate detectionではexisting blank Artifactとして扱い、body/frontmatter validityを要求しない。
  - Typed `adr`ではないためADR mirror sourceにせず、sync projectionへ本文やimport provenance catalogを追加しない。
  - UTF-8/frontmatterを要求するexisting delegated-authoring diff guardを緩和せず、command-owned raw importを別laneとして扱うworkflow統合をIssue 318へrelayする。
  - Existing `new artifact` command/catalog/template、top-level node `import`、Issue 315 Workbench opacityを維持する。
- RQ-317-013 Provider delivery boundary:
  - Provider-side layered runtimeとfocused domain/application/infra/CLI/presentation testsを実装し、必要最小限のdogfood projection/manual importを確認する。
  - Workflow/skill checkpointはIssue 318、package/fresh init/update、public reference docs、final provider/dogfood parity、full quality gate、Epic PRはIssue 319へrelayする。

## 受け入れ条件
- AC-317-001 CLI separation:
  - Help/parseで`artifact import chatgpt-output`、exactly one scope、file、title、optional slugが確認でき、`new artifact` catalog/helpとnode `import` semanticsが不変である。
- AC-317-002 Source boundary:
  - Root/scoped Workbench内のrepo-relative/absolute sourceをdestination scopeから独立してimportできる。
  - Missing、Workbench外、directory、`.MD`、source/ancestor symlink、special entryではcopy/publishを開始せず、source/external sentinel/formal artifactsが不変である。
- AC-317-003 Byte identity and source survival:
  - LF、CRLF、BOM、final newline有無、日本語、NUL、invalid UTF-8、zero-byte fixtureでsource/staged/finalのSHA-256とbyte countが一致する。
  - Success後もsource path/bytesが残り、frontmatter/template/formattingが追加されない。
- AC-317-004 Naming coexistence:
  - Same-second importと`new artifact blank --slug chatgpt-output-*`がexisting blank grammar/collision suffixで共存し、validateされる。
  - `chatgpt-output` typed token、template、reserved prefixが追加されない。
- AC-317-005 No overwrite under collision:
  - Import/import、import/new artifact、external exact-path writerのraceでexisting bytesを変更せず別slotへallocateし、suffix exhaustionはno-write failureとなる。
- AC-317-006 Mutation and alias safety:
  - Same-size content mutation、source replacement/unlinkをdeterministicに注入し、検査前提が崩れた場合はformal publish前にfailする。
- AC-317-007 Pre-publish fault safety:
  - Temp create/write、copy/hash mismatch、file fsync、unsupported publication、bounded retry/suffix exhaustion、pre-publish cleanup faultで新しいformal Artifactとsource lossがなく、owned temp cleanup stateが観測できる。
  - Transient exact-path collisionはAC-317-005のreallocation成功経路として扱う。
- AC-317-008 Post-publish warning:
  - Publish後durability/cleanup/post-confirmation faultではfinal fileを保持し、committed path/hash/bytesとwarningを返して未commit failureと区別する。
- AC-317-009 Output contract:
  - Success/failure/warningのtext/JSONはcontent-freeで、body、absolute host path、raw OS error、canonical/reviewer/adoption claimを含まない。
- AC-317-010 Generic consumer compatibility:
  - Import後のvalidate/duplicate scan/sync projection/ADR mirror regressionでblank fileとして受理され、body/provenanceの新規projectionやADR mirrorが発生しない。
  - Existing delegated-authoring diff guardをraw byte importへ流用せず、Issue 318向け互換性relayを残す。
- AC-317-011 Distribution relay:
  - Provider implementation、focused regression、manual Workbench→Artifact import、必要最小限のdogfood projection、Issue 319向けdeferred delivery evidenceが揃う。

## 例外・境界条件
- EC-317-001: Empty source fileはopaque bytesとして有効であり、byte count 0とempty SHA-256を検証する。
- EC-317-002: Source pathがsymlinkまたはsymlinked ancestorを含む場合、targetがWorkbench内でも拒否する。
- EC-317-003: Staged fileはsource inodeをrename/hard-linkしたものではなく、command-owned binary copyである。
- EC-317-004: Same timestampのcollision suffixはexisting `01..99` contractに従い、exhaustion時はoverwriteしない。
- EC-317-005: Concurrent mutation/TOCTOUの完全排除を一般保証せず、owned boundaryで前提変化を検知した場合はfailする。安全なno-replace publishを提供できないhost/filesystemではunsafe fallbackを使わずfailする。
- EC-317-006: Publish成功後にdurability/cleanup warningが発生しても、source/finalを自動削除せずcommitted resultを返す。
- EC-317-007: Crashで残るowned tempの永続GC/catalogはMVP外。Temporary basenameはgeneric Artifact scannerに見えない形とし、manual recoveryはIssue 319 docs impactで扱う。
- EC-317-008: Import provenanceはfilenameから推定できない。Source/destination/hash/bytes/capture boundary/adoptionはorchestratorがreport EALへ記録する。

## 非機能・安全性
- New third-party dependency、database、schema、persistent manifest/catalog/sidecar、background processを追加しない。
- File sizeに対してlinear streamingで処理し、whole-file memory bufferingを要求しない。
- Existing layered architectureを維持し、binary publisherはtemplate/text writerやWorkbench recursive mergeと混同しない。
- Source/final contentをlog、exception、text、JSONへ露出しない。

## スコープ
- 必須:
  - Provider parser/registry/command/application/contracts/ports/domain/infra/presentation、focused tests、manual import、必要最小限のdogfood projection、Issue 319 relay。
- 対象外:
  - PDF/image/ZIP/directory/bundle/multiple-file/raw conversation import、RawCaptureBundle、content/encoding/MIME/secret classifier、frontmatter/sidecar/receipt、automatic import、EAL/canonical promotion、workflow/skill enforcement、public rollout/final Epic PR。
  - DevCoder/reviewer model設定の追加変更。

## Evidence / authority
- Raw planning evidence:
  - `artifacts/20260713t124754z-research-chatgpt-5-6-pro-issue-planning-evidence.md`（SHA-256 `8f05a598ea90385f1f0870973c8090555816af816d22dd7474e4c6501435f105`）。
- Canonical authority:
  - 本requirement、fresh review後のdesign/plan、parent Epic、accepted Artifact import ADR。
- Evidenceの採否、GitHub-synced baseline、reviewer verdictは`report.md` EAL/Spec Authoring Gateへ記録する。

## 未確定事項
- Product/parent boundaryを変更する未確定事項はない。
- Exact error/warning token、request/result field名、module allocation、cross-platform no-replace primitive、lock duration、post-publish exit semanticsは上記観測契約を変えないIssue-local design deltaとする。

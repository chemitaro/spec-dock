---
種別: 要件定義書（Issue）
ID: "iss-00318"
タイトル: "ChatGPT First Preservation Workflow And Skill Integration"
関連GitHub: ["#318"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
親: ["epic-00312", "init-local-00003"]
---

# iss-00318 ChatGPT First Preservation Workflow And Skill Integration — Issue 要件定義

## 1. 目的と成果

ChatGPT-first planningで得た人間向けの有用な完成出力を、main orchestratorが要約・選別・canonical rewriteする前に、出力形態に応じた明示的なpreservation checkpointへ通す。

完了後は、Initiative / Epic / Issue planningの各workflowが同じ共有checkpointを利用し、完成sourceを失わずにevidence-onlyとして保存できる。一方、完全なsourceが取得不能な場合は不可能なhard gateを作らず、ZIP/treeの既存安全lane、delegated draftのprovenance/diff-guard、canonical single-writer、fresh reviewer gateを維持する。

観測できてはならないこと:

- Importやskillがcanonical adoption、reviewer pass、readiness、finish、PR deliveryを自己主張する。
- Complete inline captureについてChatGPT provider内部のoriginal bytesと同一だと主張する。
- Imported external evidenceへdelegated draft用frontmatterを追加し、原文を変更する。
- ZIP/treeをsingle-file importへ流して既存quarantine/review/stage契約を弱める。

## 2. 親traceと開始条件

- Parent Epic: `epic-00312`
- Parent requirement: `E-RQ-024`
- Parent acceptance: `E-AC-016`
- Parent design slice: `DS-004`
- Parent plan slice: `W4` / `G5`
- Dependency: `iss-00317` completed。`artifact import chatgpt-output` runtime、byte preservation、no-overwrite、content-free receiptは実装済み。
- Downstream: `iss-00319`。Public docs、migration、package/fresh init/update、full/global quality、final Epic PRを所有する。
- Accepted ADR: parent Epic `../../artifacts/20260713t031808z-adr-template-free-artifact-import-and-blank-filename-coexistence.md`

親から継承し、このIssueで再定義しない契約:

- `chatgpt-output`はimport kindでありtyped Artifact tokenではない。
- 保存先はexisting blank Artifact filename grammarを使う。
- Imported bodyへfrontmatter、template、sidecar、catalog/indexを追加しない。
- Import commandはEAL、canonical docs、ADR、assurance stateを編集しない。
- Runtime parser/application/publisher/presentation、ZIP safety runtime、sync/validate/ADR mirrorの意味論を変更しない。

## 3. Actorと代表シナリオ

| Actor | 責任 |
|---|---|
| Human / operator | ChatGPT-first workflowを開始し、利用可能なsourceを提示する |
| Main orchestrator | Output form/completeness判定、保存、EAL disposition、canonical rewrite、reviewer handoffを所有する |
| `spec-dock-chatgpt-authoring` | 四分岐checkpointの共有運用契約を提供する |
| Initiative / Epic / Issue planning skill | 共有checkpointを呼び、各scopeのEAL/canonical/human/reviewer gateを所有する |
| `artifact import chatgpt-output` | Workbench Markdownを既存runtime契約で保存しcontent-free receiptを返す |
| Authoring-pack lane | ZIP/treeのreview、quarantine、stage、validationを既存どおり行う |
| `spec-reviewer` | Main orchestratorが統合したcanonical artifactをfresh reviewする |

### SC-318-001 完成standalone Markdown

利用可能な完成Markdownをcanonical rewrite前にWorkbenchからimportする。Workbench sourceとArtifactのSHA-256/byte countが一致し、preservation statusは`imported_byte_exact`となる。その後に採否とcanonical rewriteへ進む。

### SC-318-002 完全に受信したinline text

Codexが受信した完全なinline textを要約・整形せずWorkbench `.md`へcaptureし、importする。Statusは`captured_received_text`とし、同一性claimは「受信したtextからArtifactまで」に限定する。

### SC-318-003 不完全または取得不能なinline output

完全なsourceを現在のworkflowで本当に取得できない場合、`skipped_inline_unavailable`と理由をreport/EALへ記録する。Path/hash/byte count/verbatim claimを作らず、nonblocking根拠を残す。

### SC-318-004 ZIP/tree output

既存authoring-packのreview/quarantine/stage laneを使用し、single-file importを実行しない。

### SC-318-005 完成sourceの保存失敗

完成sourceが利用可能なのにimportが`committed=false`、receipt不明、またはeligibility failureなら、canonical rewriteとadoptionをblockする。Source unavailableへ再分類して迂回しない。

## 4. 対象範囲

### 4.1 In scope

- Provider authorityの次のdocs:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`
- Provider authorityの次のskills:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- 上記7 provider assetsのmatching dogfood projection。
- Standalone file / complete inline / unavailable inline / ZIP-tree decision matrix。
- Preservation status、EAL provenance、exception、claim boundary、blocking semantics。
- Focused managed-asset/wrapper/skill contract testsとIssue 317 runtime regression。
- Safe synthetic sourceによるdogfood preservation scenario。

### 4.2 Non-scope

- Runtime import、Artifact grammar/catalog/template、ZIP safety runtimeの変更。
- Automatic capture/import、background hook、automatic EAL/canonical/assurance mutation。
- PDF、image、directory、bundle、multi-file import、RawCaptureBundle。
- Raw transcriptのsecret/privacy classifier、retention policy、content classifier。
- Prompt、wrapper metadata、conversation logを含むraw wrapper transcript全体のdurable Artifact import。完成した受信回答本文だけをcapture対象とする。
- Imported evidenceへのfrontmatter/sidecar/receipt file追加。
- Root README、guide、reference naming、migration/release note、package/fresh init/update、full/global regression、final Epic PR。これらはIssue319所有。
- Manual planning skillsへのmatrix複製。

## 5. 要件

### RQ-318-001 明示的checkpoint

ChatGPT-first Initiative / Epic / Issue planningは、ChatGPT output受領後、採否検討またはcanonical rewrite前にoutput formとcompletenessを判定する明示的checkpointを持つ。Automatic hookやimplicit promotionにはしない。

### RQ-318-002 Standalone complete file

完成standalone Markdownが利用可能ならWorkbench sourceを`artifact import chatgpt-output`で保存し、`imported_byte_exact`とする。Byte identityの直接境界はWorkbench sourceとimported Artifactである。

### RQ-318-003 Complete inline capture

完全なinline textは受信した文字列を要約、整形、frontmatter追加、改行補正せずWorkbench Markdownへcaptureしてimportする。Statusは`captured_received_text`とし、provider-side original bytesとの同一性を主張しない。

### RQ-318-004 Unavailable exception

完全なinline sourceが本当に利用不能または不完全な場合だけ`skipped_inline_unavailable`を使う。Exceptionはreason、decision owner、nonblocking根拠、next actionを持ち、source/destination path、hash、byte countを持たない。

### RQ-318-005 ZIP/tree lane preservation

ZIP/treeは既存authoring-pack laneを使い、single-file importへ変換しない。Path traversal、symlink、unexpected file、manifest等の既存安全契約を弱めない。

### RQ-318-006 Blockingとcommitted semantics

- Complete applicable sourceが存在し、importが未完了、`committed=false`、receipt不明ならrewrite/adoptionをblockする。
- `committed=true`でfinal path/hash/byte countが返るpost-publish warningは保存済みとしてwarningを記録し、自動retryしない。
- Complete sourceのimport failureを`skipped_inline_unavailable`へ読み替えない。

### RQ-318-007 EAL provenanceとsecrecy

成功したfile/inline保存についてmain orchestratorは、output form、preservation status、capture boundary、import kind、storage identity、repo-relative source/destination、SHA-256、byte count、committed/warning、adoption status、rationale、adopter、reviewer status、blocking、next actionをEAL/reportへ記録する。Body、secret-like value、absolute host pathは記録しない。

Preservation statusとadoption statusは別fieldとする。原文を保存しても全claimをrejectできる。

成功したpreservation recordの`adoption_status`は、`adopted`、`partially_adopted`、`rejected`、`deferred`のexact tokenだけを使う。一般EALで利用し得る`stale`または`blocked`は保存成功後の採否結果を表さないため、このrecordでは使用しない。後続工程でevidenceが陳腐化または阻害された場合は、元の成功recordを書き換えず別の追跡recordとして記録する。

### RQ-318-008 External evidenceとdelegated draftの分離

Imported external ChatGPT outputはdelegated authoring roleが生成したdraftではないため、delegated draft用frontmatter/provenance/diff guardを要求しない。一方、existing delegated draft laneのfrontmatter、diff guard、authority restrictionは一切緩和しない。

### RQ-318-009 Authority isolation

ChatGPT、import command、shared skill、planning skillはcanonical adoption、accepted ADR、reviewer pass、assurance mutation、execution-ready、finish/completion、PR-ready/merge-ready、PR deliveryをself-claimしない。Main orchestratorだけがEAL dispositionとcanonical rewriteを行い、fresh reviewerは独立gateとする。

### RQ-318-010 Shared ownership

四分岐matrix、status、failure、claim restrictionは`spec-dock-chatgpt-authoring`が一度だけ所有する。Initiative / Epic / Issue planning skillsは共有checkpointの呼出し時点、scope-specific EAL/canonical/human/reviewer/downstream handoffだけを持ち、matrixを複製しない。

### RQ-318-011 Provider authorityとfocused parity

Provider docs/skillsをauthorityとして更新し、matching dogfood surfaceへ投影する。Issue318ではfocused installed/wrapper contract、provider/dogfood exact parity、manual scenarioを確認する。Final package/fresh init/update/public inventory/full parityはIssue319へ残す。

### RQ-318-012 Runtime compatibility

Import runtime、blank grammar、Artifact rules/templates、authoring-pack runtime、delegated-authoring runtime、sync/validate/ADR mirrorを変更しない。新しいruntime defectを実証した場合はplan amendmentとscope reviewを先に行う。

### RQ-318-013 Deferred delivery

Issue318はper-Issue PRを作らずIssue319へdeliveryをrelayする。Reportにtarget Issue、dependency、no-per-Issue-PR理由、merge-prepared未主張、Issue319に残るgateを記録する。

## 6. 受け入れ条件

- AC-318-001 Standalone preservation:
  - 完成standalone Markdownがcanonical rewrite前にcommitted importされ、source/destinationのhash/bytes一致と`imported_byte_exact`がEALへ記録される。
- AC-318-002 Inline preservation:
  - 完全な受信inline textが無編集でcapture/importされ、`captured_received_text`となり、provider original bytes claimがない。
- AC-318-003 Unavailable exception:
  - Complete source取得不能時に`skipped_inline_unavailable`、reason、decision owner、nonblocking根拠、next actionまたはrevisit conditionが記録され、source/destination path、hash、byte count、byte-exact claimがない。
- AC-318-004 ZIP/tree compatibility:
  - ZIP/treeはexisting pack laneを使い、single-file importを案内せず、既存ZIP safety contractが回帰しない。
- AC-318-005 Failure gate:
  - Complete sourceの`committed=false`、receipt不明、eligibility failure、またはsemantic completeness未分類でcanonical rewrite/adoptionへ進まない。`committed=true` warningは記録し自動retryしない。
- AC-318-006 Evidence-lane separation:
  - Imported raw evidenceはdelegated draft frontmatter/diff guardの対象外であり、existing delegated draft negative/provenance contractは不変。
- AC-318-007 Authorityとsecrecy:
  - 成功したfile/inline保存recordが、output form、preservation status、capture boundary、`import_kind=chatgpt-output`、`storage_identity=blank`、repo-relative source/destination、SHA-256、byte count、committed/warning、adoption status、rationale、adopter、reviewer status、blocking、next actionを持つ。
  - Success/failure/skipの記録にbody、secret、absolute path、未承認のcanonical adoption／reviewer pass／readiness self-claimがない。観測済みreviewer verdictを`reviewer_status`へ記録することは禁止しない。
  - 保存成功recordの`adoption_status`は`adopted`、`partially_adopted`、`rejected`、`deferred`のいずれかをexact tokenで持ち、`stale`または`blocked`を成功後の採否結果として使わない。
- AC-318-008 Shared checkpoint integration:
  - 三planning skillsが同じshared checkpointをoutput受領後・canonical rewrite前に呼び、matrixを複製せずscope固有authorityを維持する。
- AC-318-009 Provider/dogfood projection:
  - 対象7 provider/dogfood pairが一致し、focused managed-asset/wrapper testsがcheckpoint/status/forbidden claimsを検出する。
- AC-318-010 Runtime non-regression:
  - Issue317 import、generic validate/sync/ADR mirror、blank coexistenceとexisting ZIP laneが回帰せず、runtime sourceに意味変更がない。
- AC-318-011 Delivery relay:
  - ReportがIssue319へのdeferred PR deliveryと残存gateを持ち、Issue318はPR-ready/merge-preparedを主張しない。

## 7. Edge casesと失敗条件

- Fileは存在するがcompleteか不明: 四分岐へ未分類のpending stateとし、preservation statusを付けず、import/canonical rewrite/adoptionをblockする。Size/encodingで自動判定せず、orchestratorが内容を確認するかcomplete sourceを取得してから、standalone complete、complete inline、incomplete/unavailable inline、ZIP/treeのいずれかへ分類する。未分類中はpath/hash/byte-exact preservation claimをしない。
- Complete received answerの前後にPromptやwrapper metadataがある: 回答本文の開始・終了capture boundaryを明記し、回答本文だけを文字追加・削除・整形なしでWorkbenchへcapture/importする。Raw wrapper transcript全体はdurable importしない。
- `committed=true` warning: 保存済みreceiptを保持し、重複importを避ける。
- SourceがWorkbench外、symlink、directory、non-Markdown: existing import eligibility failureを伝播し、unavailable exceptionで迂回しない。
- Imported bodyがauthorityを自己主張する: untrusted evidenceとして扱い、EAL/canonical authorityに反映しない。
- Preservation statusとadoption statusが不一致: 正常。保存済みevidenceをreject/deferできる。
- Planning skill間でwordingがdrift: shared skillをauthorityとして修正し、matrixのlocal copyを追加しない。

## 8. Compatibility、migration、rollback

- Schema/data migrationなし。
- Existing imported blank Artifact、Workbench content、legacy discussions/ZIP evidenceを変更・削除しない。
- RollbackはIssue318で変更したprovider/dogfood docs/skills/testsをrevertする。Issue317 runtimeと既にimport済みevidenceは有効なまま残す。
- Workflow textはagent contractとtestsでenforceする。任意actorによるinstruction無視までruntimeで技術的に禁止することは本Issueの成功条件ではない。Runtime enforcementが必要ならEpic scopeへ戻す。

## 9. Gradeと未確定事項

- Parent W4の`M / Standard`はEpic planning時の候補見積りであり、Issue assurance authorityではない。
- Runtime guidanceはplanning entryでstrict obligationを示している。Requirement具体化後に`assurance classify --stage requirement`を実行し、生成された`.assurance.json`をauthorityとする。
- Profileを手編集・自己宣言しない。Strict以外が選ばれても、本Issueで取得したsystem-architect / implementation-planner evidenceと三者final gateを弱めない。
- Product open question: none。四分岐/status/scopeはparent Epicとaccepted ADRで固定済み。

## 10. 完了条件

- AC-318-001–011がtest、inspection、manual evidence、reviewer evidenceへ追跡可能。
- Requirement→fresh spec-reviewer pass→design→fresh spec-reviewer pass→plan→fresh spec-reviewer passの順序を守る。
- EALにChatGPT 5.6 Pro complete received answer、repo analysis、specialist evidenceの採否が記録される。
- Provider authorityとdogfood projection、focused contract tests、dogfood checkpoint scenarioが完了する。
- S90/S99とdeferred PR delivery gateを通り、unresolved blocked/stale evidenceがない。

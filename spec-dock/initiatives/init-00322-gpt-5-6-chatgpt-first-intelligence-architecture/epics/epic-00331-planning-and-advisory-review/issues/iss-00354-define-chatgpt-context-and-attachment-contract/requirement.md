---
種別: 要件定義書（Issue）
ID: "iss-00354"
タイトル: "ChatGPT Context and Attachment Contract — Oracle 0.17.0 互換性増分"
状態: "approved"
作成者: "ChatGPT Blue Team authoring planner"
最終更新: "2026-08-04"
親: ["epic-00331", "init-00322"]
---

# iss-00354 ChatGPT Context and Attachment Contract 要件定義書

> **Canonical / approved for Issue implementation preparation**
> 本文書は Candidate v2 の Red Team PASS と、ユーザーが承認した実装準備補足を統合した iss-00354 の正規要件である。
> Candidate v2 の immutable identity は `candidate-note.md` と `report.md` に保持し、current HEAD の確認値も report に記録する。
> この承認は実装準備のためのものであり、実装完了、commit、push、PR、merge、Issue close を意味しない。
> 今回の Red Team レビュー対象は本書、`design.md`、`plan.md`、
> `decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md` の四文書だけである。

## 1. 文書の位置づけ

本 Issue は、SpecDock の Issue Planning runtime が ChatGPT を Planning、Formal Review、Semantic Revision に
利用する際の **minimal body + direct attachment paths** 契約を定義する。今回の改訂は、source HEAD 時点で
計画済みの Option A / Option C、exact GitHub gate、direct Oracle、Blue/Red thread 分離、typed output validation を
維持し、Oracle `0.17.0` で必要となる互換性、失敗分類、限定回復、検証を増分追加する。

既存 Issue #334 が提供する Issue Planning lifecycle と、Issue #354 の既存 S01–S08 をゼロから作り直さない。
変更対象は、PATH から解決する Oracle 本体との versioned browser contract と、その周辺の prompt、model、attachment、
download evidence である。

本turnで要求されたmanual Blue CandidateはADRと補助artifactsを含むexpanded delivery inventoryである。これはproductionの
Issue Planning authoring ZIP validator（canonical three documents + exactly-one onboarding）のschema変更を意味しない。runtime output
inventoryを変更する場合は別の明示要件・validator change・reviewを必要とする。

## 2. 確認済み source identity

| 項目 | 値 / 確認結果 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Source HEAD | `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` |
| Branch vs requested HEAD | `identical` / ahead `0` / behind `0` |
| Default branch fallback | 使用していない |
| Initiative | `init-00322` / GPT-5.6 ChatGPT First Intelligence Architecture |
| Epic | `epic-00331` / Planning and Advisory Review |
| Issue | `iss-00354` / Define ChatGPT Context and Attachment Contract |
| Parent Issue | GitHub Issue `#334` |

GitHub Connector で指定 branch と exact source HEAD を確認した。添付、一般知識、default branch を repository source の
代替にしていない。

## 3. 根拠の区分

### 3.1 GitHub source HEAD で確認した事実

- product runtime は `shutil.which("oracle")` で PATH Oracle を解決し、実行ファイル identity を再検証する。
- 現行 adapter は Oracle version を `0.16.1` と完全一致で preflight し、required help flags を確認する。
- 現行 browser argv は logical selector `--model Pro`、`--browser-model-strategy select`、managed Chrome、
  `--browser-attachments always`、一つの `--prompt`、一つの generated prompt-pack `--file` を明示する。
- 現行 recovery は **stage-blind** である。Oracle process の nonzero exit / timeout または session state nonterminal を
  検出すると、`promptSubmitted` の `true` / `false` / unknown を判定せず `_recover_same_session` を呼ぶ。
- `_recover_same_session` は generic adapter 内で Oracle `0.16.1` 固有の
  `oracle session <session-id> --harvest --no-recover` argv を直接組み立てる。したがって現行 baseline は
  「prompt submit 後だけの recovery」ではなく、「submission evidence なしで harvest し得る stage-blind behavior」である。
- Oracle `0.16.1` session artifact reader は version、`meta.json`、browser mode、artifact inventory、SHA-256、ZIP / JSON を
  fail-closed で検証する。
- Oracle-native user / project config は Oracle 本体の責任境界として許容される。SpecDock は formal operation に必要な値を
  explicit argv で渡すが、Oracle config を隔離、削除、無効化しない。
- Issue #354 の canonical implementation report は scaffold であり、Option A / C や Oracle `0.17.0` 対応の実装完了証跡ではない。

### 3.2 GitHub 外のローカル観測証跡

添付 `oracle-browser-recovery-report.md` と作業 brief は、Oracle `0.17.0` と個人所有の `chatgpt-use` wrapper を用いた
browser execution の補足証跡であり、SpecDock production code の実行証跡ではない。

確認された観測:

- 同一 brief で `Prompt reconstruction did not match the exact input` が送信前に発生した。
- direct attachment、inline attachment、添付なし、standard target、project target、model picker `select` / `current` の
  組合せでも再現した。
- すべて `promptSubmitted=false` で、ChatGPT response と ZIP generation には到達していない。
- 後続の短い smoke では `GPT-5.6 Sol` が picker verified として送信された一例がある。
- explicit target の初回には `Available: Got it.` を伴う model option discovery failure が発生し、再試行で成功した一例がある。

### 3.3 仮説または未検証事項

- browser state、overlay、startup order、target URL、prompt length、attachment mode のどれが reconstruction mismatch の
  原因かは確定していない。
- 個人 wrapper の観測が PATH-resolved direct Oracle adapter で同じ形で再現するかは未検証である。
- Oracle `0.17.0` の exact help surface、session metadata schema、prompt submission evidence、model evidence、inline transport、
  download artifact schema は source HEAD の GitHub code からは確定できない。
- `GPT-5.6 Sol` は一観測であり、SpecDock の恒久的な model identifier または accepted mapping ではない。

## 4. 目的

1. Option A / C と direct Oracle boundary を維持して Oracle `0.17.0` を明示的に characterization できるようにする。
2. prompt reconstruction、model selection、attachment transport、generation、download / ZIP capture の失敗を段階別に区別する。
3. `promptSubmitted` と response / artifact state に基づき、同一 session 回復、新規 execution、停止を一意に決める。
4. version/config/artifact schema を一つの compatibility profile として検証し、unknown contract を fail-closed にする。
5. current code structure と S01–S08 を活かした増分実装・テスト・browser smoke を計画する。

## 5. 非目的

- personal `chatgpt-use` wrapper、absolute path、別 backend、OpenAI API、default branch を product fallback にすること。
- 無制限 retry、model `current` への黙示 fallback、別 model の自動選択、required attachment の削除。
- prompt text の意味を変える normalization、automatic ZIP、per-entry exclusion、content scan、directory prewalk。
- Oracle user / project config の隔離、独自 parser による全面管理、private target URL の public evidence 化。
- Oracle `0.17.0` の一観測を Initiative 全体の永続 architecture として固定すること。
- Candidate を canonical docs、review PASS、implementation evidence とみなすこと。

## 6. 用語

| 用語 | 定義 |
|---|---|
| Oracle execution | 一つの Oracle process invocation と session slug による transport attempt |
| ChatGPT submission | reconstructed prompt が UI へ送信され、`promptSubmitted=true` または同等 evidence を得た状態 |
| Blue / Red thread | ChatGPT conversation の authoring / review lane。Oracle execution と同義ではない |
| Pre-submit failure | `promptSubmitted=false` または unknown のまま終了した model / attachment / reconstruction / transport failure |
| Stage-blind harvest | submission evidenceを判定せずnonzero/timeout/nonterminalだけでsame-session harvestを呼ぶ現行0.16.1 behavior |
| Same-session recovery | `promptSubmitted=true` のときだけ、profile-owned version-specific commandで同一sessionをpoll / harvest / captureすること |
| New execution | 新しい Oracle process / session slug で同一 operation lineage を再実行すること |
| Compatibility profile | exact versionのcapability、browser argv、model/stage decoder、declared inline capability、artifact reader、harvest/capture argv buildersの束 |
| Logical model selector | product が要求する意味上の selector。現行値は `Pro`。UI の表示名とは分離する |
| Observed model label | Oracle が browser picker で実際に verified とした表示名。例の一つが `GPT-5.6 Sol` |
| Direct attachment | original file / directory path を Oracle の primary browser attachment transport に渡すこと |
| Inline fallback | direct attachment failure時に限り、profileが宣言したOracle-native inline modeを同じ original pathで一度だけ試すtransport recovery |
| Prompt reconstruction mismatch | Oracle が effective browser input と exact input の不一致を検出し、送信前に停止した状態 |
| Response completed | ChatGPT response generation が terminal completion に到達した状態 |
| Artifact captured | output fileを同一 sessionからsnapshotし、size/SHA/schema/ZIP contractを検証できた状態 |

## 7. 維持する既存判断

### 7.1 Option A — minimal body と detailed attachments

本文は operation、目的、repository / branch / HEAD、Initiative / Epic / Issue、authority、expected output、hard failure を
保持する。詳細手順、review criteria、revision rule、schema / examples は provider-owned attachments が保持する。

### 7.2 Option C — opaque directory path transport

SpecDock は attachment directory entry を walk、glob、stat、open、decode、hash、classify、filter、copy、rename、archive、
manifest 化しない。original top-level path を direct Oracle に渡す。

### 7.3 Blue / Red separation

Planning と Semantic Revision は verified Blue lineage を継続できる。Candidate version ごとの Formal Review は fresh、
read-only、defect-only Red conversation である。pre-submit failure は successful ChatGPT submission ではないため、
その execution 自体を Red review completion または Blue turn とみなさない。

### 7.4 Direct Oracle / exact source / typed output

PATH Oracle、managed Chrome、exact GitHub preflight / postflight、authoring ZIP、closed Review JSON、Candidate / Review / Human
identity binding、output safety validator を維持する。

## 8. 機能要件 — 既存契約

### ISS354-REQ-001 Exact GitHub identity
Formal operation 前に named current branch と exact source HEAD を検証し、default branch、添付、memory を代替にしない。

### ISS354-REQ-002 Minimal body
本文は目的、identity、authority、expected output、attached instructions、exact access hard failure に限定する。

### ISS354-REQ-003 Operation-specific resources
Planning、Review、Revision は provider-owned `prompt.md` と opaque `attachments/` を持つ。

### ISS354-REQ-004 Direct directory transport
Static attachment directory は path のまま direct Oracle へ渡す。

### ISS354-REQ-005 No input entry inspection
Runtime は attachment entry の読取り、分類、scan、size/count precheck、hash、変換を行わない。

### ISS354-REQ-006 Dynamic original paths
Candidate ZIP、Review JSON、revision request は複製せず original path を渡す。

### ISS354-REQ-007 No generated input pack
`context-NNN.md`、input manifest / provenance / source-manifest / stale-if を作る transport pack を廃止する。

### ISS354-REQ-008 Normal transport failure
entry exclusion、automatic conversion、別 backend、別 branch へ切り替えない。Oracle `0.17.0` の限定的な
transport-mode recovery は REQ-026–028 の明示条件にだけ従う。

### ISS354-REQ-009 Planning / Revision output
Planner / Semantic Revision は一つの authoring ZIP を返し、required canonical three documents と exactly-one onboarding の
既存 validator を維持する。

### ISS354-REQ-010 Review output
Formal Reviewer は fresh Red から一つの closed JSON を返し、strict parser と reviewed identity を維持する。

### ISS354-REQ-011 Blue continuity
Planning / Semantic Revision は repository、branch、HEAD、Issue、Candidate lineage が一致する verified Blue だけを継続する。

### ISS354-REQ-012 Fresh Red
Candidate version ごとに new Red conversation を作り、Blue、過去 Red、別 Candidate PASS を再利用しない。

### ISS354-REQ-013 Continuity recovery
Blue binding を検証できず lineage が一意なら complete current input で new Blue を開始し、曖昧なら Human block とする。

### ISS354-REQ-014 Thread evidence boundary
provider handle と raw transcript を Candidate、Review、canonical docs、public resultへ含めない。

### ISS354-REQ-015 Authority boundary
ChatGPT は mutation、adoption、approval、implementation authorization を行わない。

### ISS354-REQ-016 Direct Oracle only
product external dependency は PATH Oracle と managed Chrome であり、personal wrapper / API fallbackを追加しない。

### ISS354-REQ-017 Output validation retention
ZIP / JSON / identity / source freshness / publication / apply safetyを緩めない。

### ISS354-REQ-018 Provider / projection parity
provider source を正本とし、installed assets と dogfood projection を同一 closure で同期・検証する。

### ISS354-REQ-019 CLI migration
old `--context-manifest` を directory-oriented inputへhard cutoverし、silent compatibility materializationを作らない。

### ISS354-REQ-020 Parent documentation consistency
親 Epic、skills、workflow docsのbody/attachment/session wordingをIssue-local decisionと整合させる。

## 9. 機能要件 — Oracle 0.17.0 増分

### ISS354-REQ-021 Exact compatibility profile

Runtime は `oracle --version` の exact output から versioned `OracleCompatibilityProfile` を選ぶ。profile は少なくとも
次を一つのversion-specific contractとして束ねなければならない。

- required root / session capabilities と browser argv semantics。
- model evidence と prompt submission evidence の decoder。
- supported attachment modes と明示的な `inline_mode_characterized` capability。
- session artifact decoder / reader。
- same-session generation recovery用の `harvest_argv_builder`。
- response-complete後のdownload/capture recovery用の `capture_argv_builder`。

Generic adapter は `session`、`--harvest`、`--no-recover` または0.17固有の代替flagを直接組み立ててはならない。
`0.16.1` profileは現行commandをbehavior-preservingに所有し、`0.17.0` profileはS09で実測したcommandだけを所有する。
0.17でharvestとcaptureが同じcommandになる場合も、二つのsemantic builderへ同じcharacterized builderを明示的にbindする。

### ISS354-REQ-022 Unknown / partial contract は fail-closed

未登録 version、required help flag 欠落、artifact schema mismatch、submission / model evidenceを判定不能な profile では、
promptを送信せず `oracle_capability_unsupported` 相当で停止する。`>=0.17` のような広い semver rangeを無条件に受理しない。

### ISS354-REQ-023 Oracle-native config boundary

SpecDock は Oracle user / project config を隔離、削除、上書きしない。formal operationに不可欠な engine、logical model、
strategy、managed Chrome、attachment policy、session slug、promptは、characterized profileに従う explicit argvで固定する。
standard/project targetはOracle-native config / browser stateの観測軸であり、private URLをproduct contractに取り込まない。

### ISS354-REQ-024 Logical model と observed evidence

product contractはlogical selectorを要求し、UI表示名をgeneric domain constantにしない。formal runは、Oracleがmodel selectionを
verifiedとした evidenceと、non-empty observed model labelを保持できなければならない。`GPT-5.6 Sol` はdirect PATH Oracleの
characterizationでaccepted mappingになった場合だけversion profileに記録し、外部wrapper smokeだけでhardcodeしない。
`current`、別model、default modelへの黙示fallbackは禁止する。

### ISS354-REQ-025 Prompt reconstruction evidence

adapterはpromptを一つのargv valueとしてshellなしで一度だけ渡し、UTF-8、引用符、改行、末尾改行をapplication側で書き換えない。
Oracle `0.17.0` profileは、少なくともsubmission stateとreconstruction mismatchの有無を判定できなければならない。
raw promptはpublic evidenceに残さず、必要な内部correlationにはlength / SHA-256等のcontent-free digestを使用できる。

### ISS354-REQ-026 Direct primary / one-shot inline recovery

required attachmentsはdirect transportをprimaryとする。direct attachment failureが明示分類され、`promptSubmitted=false` で、
profileがinline modeをcharacterized済みの場合に限り、同一original pathsをOracle-native inline modeで一度だけ新規executionへ
渡せる。SpecDockはpathをopen、copy、archive、filterせず、required attachmentを落とさない。

inline modeはprompt reconstruction mismatch、model selection failure、response/download failureのfallbackではない。

### ISS354-REQ-027 Pre-submit decision boundary

- preflight / unknown profile: executionしない。
- `promptSubmitted=false` または unknown の全failure class: same-session harvest / capture command invocationはともに `0`。
- submission state unknown: `false`と推測せず、`blocked` / `oracle_capability_unsupported`で停止する。
- model picker transient failure: profileがretryableと明示し、`promptSubmitted=false` の場合だけ、一つのnew executionを許可する。
- direct attachment failure: REQ-026のinline new executionを一つだけ許可する。
- prompt reconstruction mismatch: automatic retry、mode変更、model変更を行わずblockする。再実行は、profile変更、Oracle patch、
  browser state reset、prompt synthesis修正など検証可能なprecondition変更後の明示operationだけである。
- pre-submit cleanup commandをsame-session recoveryの例外として導入しない。

### ISS354-REQ-028 Post-submit same-session only

`promptSubmitted=true` または同等 evidence を得た後は、promptの自動再送、新規execution、別conversationを禁止する。
timeout / generation nonterminalは、selected profileの`harvest_argv_builder`が返したexact argvだけをboundedに一度実行できる。
response-complete後のdownload pendingは、selected profileの`capture_argv_builder`が返したexact argvだけをboundedに一度実行できる。
Generic adapter内のhardcoded recovery argvは削除する。

`promptSubmitted=false` または unknown では、failure class、exit code、session stateにかかわらずharvest / captureを実行しない。

### ISS354-REQ-029 Response / download / ZIP capture separation

response completion、download request、file artifact出現、snapshot、ZIP validationを別stateとして扱う。response完成後の
download failureは、`promptSubmitted=true`かつprofile-owned `capture_argv_builder`がcharacterized済みの場合に限り、同一sessionで一度
capture recoveryを行う。generic adapterは0.16.1 commandを0.17へ流用しない。なおmissing / ambiguous / corruptなら既存typed artifact
reasonでfail-closedにし、新しいChatGPT responseを生成し直さない。

### ISS354-REQ-030 Authoritative public status / reason mapping

Internal failure classからpublic `PlanningInvocationResult.status` / `reason`へのmappingは次を唯一のcontractとする。

| Internal failure class | Public status | Public reason | Contract status |
|---|---|---|---|
| executable / managed Chrome unavailable | `blocked` | `oracle_unavailable` | existing reason retained |
| `profile_unsupported` / required capability missing / `prompt_submitted=unknown` / required profile builder missing | `blocked` | `oracle_capability_unsupported` | existing reason retained; allowed many-to-one capability family |
| `model_selection_unavailable` after the permitted retry is unavailable or exhausted | `blocked` | `oracle_model_selection_unavailable` | new public reason |
| `attachment_submission_failed` after the permitted inline path is unavailable or exhausted | `blocked` | `oracle_attachment_submission_failed` | new public reason |
| `prompt_reconstruction_mismatch` | `blocked` | `oracle_prompt_reconstruction_mismatch` | new public reason |
| `generation_incomplete` after one characterized same-session harvest | `blocked` | `oracle_generation_incomplete` | new public reason |
| characterized recovery command cannot be executed safely, or same-session state remains undecidable for infrastructure reasons | `blocked` | `oracle_session_recovery_required` | existing reason retained; not a known-stage catch-all |
| `output_download_failed` after one characterized same-session capture | `blocked` | `oracle_output_download_failed` | new public reason |
| expected artifact absent after terminal capture | `rejected` | `oracle_artifact_missing` | existing reason retained |
| multiple candidate artifacts | `rejected` | `oracle_artifact_ambiguous` | existing reason retained |
| path / mode / size / SHA / validation / ZIP / JSON defect | `rejected` | `oracle_artifact_rejected` | existing reason retained; allowed many-to-one validation family |

The mapping is closed and authoritative. The five stage-specific classes—model selection, attachment submission,
prompt reconstruction, generation, and output download—must not be collapsed into one another, into
`oracle_capability_unsupported`, or into `oracle_session_recovery_required`. Many-to-one normalization is allowed only for the
three explicitly listed same-semantics families: capability/profile validation, runtime unavailability, and artifact validation.
An unknown internal failure class has no default public mapping and must fail the mapper contract before serialization.

### ISS354-REQ-031 Execution attempt と ChatGPT thread の分離

pre-submit new executionはBlue/Red conversationを消費したとみなさない。Candidate versionのRed reviewは、最初のsuccessful submission
がfresh Redであり、successful submissionは最大一回とする。Blue bindingはsuccessful submission / verified continuationにだけ更新し、
pre-submit failureでadvanceしない。

### ISS354-REQ-032 Evidence / privacy boundary

内部evidenceはversion/profile、stage、logical model、observed model label、verified flag、attachment mode、promptSubmitted、
responseCompleted、artifact status、retry countを保持できる。raw prompt、attachment content、private absolute path、target URL、session handle、
raw transcriptをCandidate / Review / public resultへ出さない。

### ISS354-REQ-033 Oracle 0.17.0 verification matrix

unit / integrationに加え、opt-in browser smokeでshort control promptとrepresentative Issue #354 promptを検証する。direct、characterized
inline、required attachment、model verified、prompt submitted、response complete、download / ZIP captureをstage evidence付きで確認する。
外部wrapper smokeは補助証跡であり、direct PATH Oracleのformal compatibility PASSを代替しない。

## 10. 非機能要件

### ISS354-NFR-001 保守性
operation attachmentの増減はresource tree変更で完結し、application allowlistを要求しない。

### ISS354-NFR-002 単純性
applicationはtop-level pathとtyped identityだけを扱い、directory contentsを理解しない。

### ISS354-NFR-003 Content-free observability
failure stageとboolean / enum evidenceは記録できるが、prompt / content / private path / URL / handleを露出しない。

### ISS354-NFR-004 再現性
minimal bodyとargv assemblyはdeterministicとし、browser smokeはversion、profile、target kind、model evidence、attachment modeを記録する。

### ISS354-NFR-005 Portability
filesystem entryの意味はapplicationが解釈せず、Oracleのcharacterized path contractに委ねる。

### ISS354-NFR-006 後方境界
Candidate / Review / Human / apply lifecycleとpublic success semanticsを不要に変更しない。

### ISS354-NFR-007 Version locality
version差分はprofile / decoder / fixtureへ局所化し、generic application orchestrationへOracle-specific条件を散在させない。

### ISS354-NFR-008 Bounded recovery
自動new executionはpre-submitで最大一回の明示caseに限定し、post-submitはsame-sessionだけとする。総attempt budgetは有限でtest可能である。

### ISS354-NFR-009 Safe rollback
0.17.0 profileを撤回してもruntime内にsilent legacy/backend fallbackを残さない。rollbackはreviewed deployment / commit-level changeで行う。

## 11. 失敗分類と回復契約

| Stage | 代表 failure | Submission evidence | 自動処置 | Harvest / capture invocation |
|---|---|---|---|---|
| preflight | version/capability/schema unknown | not started | block | `0 / 0` |
| model selection | option unavailable / UI not ready | `false` | profile許可時に1回だけ同条件new execution | `0 / 0` |
| attachment transport | direct upload/stage failure | `false` | profile許可時に1回だけinline | `0 / 0` |
| prompt reconstruction | exact input mismatch | `false` | automatic retryなし | `0 / 0` |
| any pre-submit / undecodable state | submission unknown | unknown | capability unsupported | `0 / 0` |
| prompt submitted / generation | timeout / nonterminal | `true` | profile harvest builderを1回 | `1 / 0` maximum |
| response completed / download | download pending/failure | `true` | profile capture builderを1回 | `0 / 1` maximum |
| snapshot / validation | missing/ambiguous/corrupt ZIP/JSON | `true` | capture済みならreject | additional recovery `0` |

同一 operationで model retry と attachment inline retryを連鎖させてattempt数を増やしてはならない。実装は一つの
`RecoveryDecision`だけを選び、overall automatic new-execution budgetを最大1に固定する。model retry後にattachment
failureが出た場合はblockし、さらにinlineへ進まない。

Generic adapterはsame-session commandを構築せず、selected exact-version profileのbuilderだけを呼ぶ。builderの呼出し可否は
`promptSubmitted is True`でguardし、`False` / `None`ではbuilder call countを0にする。

## 12. 受け入れ基準

### 12.1 既存 AC の保持

| ID | Then |
|---|---|
| AC-001 | operation resource file増減でcode変更なく同じdirectory pathをOracleへ渡す |
| AC-002 | nested/hidden/symlink/FIFOをruntimeがwalk/open/hashせずpathだけ渡す |
| AC-003 | unsupported attachment entryでper-entry exclusion/ZIP/backend fallbackをしない |
| AC-004 | exact Blue bindingならsemantic revisionをverified continuationする |
| AC-005 | binding invalidだがlineage exactならcomplete inputでnew Blueを開始する |
| AC-006 | lineage ambiguousならsubmission前にHuman blockする |
| AC-007 | Candidate versionごとにfresh Redを開始する |
| AC-008 | authoring ZIPをexisting logical filename/root/inventory validatorで検証する |
| AC-009 | unknown/duplicate key Review JSONをrejectする |
| AC-010 | exact branch/HEAD不可ならdefault fallbackなしでblockする |
| AC-011 | provider/installed/dogfood recursive byte parityが一致する |
| AC-012 | old `--context-manifest`をsilent translationなしで拒否する |

### 12.2 Oracle 0.17.0 AC

| ID | Given / When | Then |
|---|---|---|
| AC-013 | Oracle reports `0.17.0` | exact profile、required help、stage decoder、inline capability、harvest/capture builders、artifact readerが揃う場合だけsubmission可能 |
| AC-014 | unknown version / schema / required builder missing | prompt processを開始せず`blocked` / `oracle_capability_unsupported` |
| AC-015 | representative promptでreconstruction mismatch | `promptSubmitted=false`を記録し、harvest/capture/inline/model change/auto retry 0 |
| AC-016 | profile-classified transient model failure | overall budget内でnew execution 1、logical model不変、successful submission最大1 |
| AC-017 | profile-classified direct attachment failure | same original pathsでinline new execution最大1、runtime file read/copy 0 |
| AC-018 | reconstruction mismatch | inline modeをfallbackとして選ばない |
| AC-019 | `promptSubmitted=true`後のtimeout | prompt call 1、selected profileのharvest builder exact argv 1、generic hardcoded session argv 0 |
| AC-020 | response complete後のdownload failure | selected profileのcapture builder exact argv 1、新規ChatGPT execution 0 |
| AC-021 | model selection成功 | verified=trueとobserved labelをprivate evidenceに保持し、generic codeに`GPT-5.6 Sol`をhardcodeしない |
| AC-022 | short promptとrepresentative prompt smoke | target kind / attachment mode別にstage evidenceを記録し、事実と未検証を分離する |
| AC-023 | fallback pathを監査 | personal wrapper、API、default branch、`current`、attachment drop、auto ZIP invocation 0 |
| AC-024 | public result / Candidateを検査 | raw prompt、private path、target URL、session handle、transcript 0 |
| AC-025 | 0.17 profile withdrawal trigger発生 | formal operationをblockし、silent 0.16 downgradeやalternate backendをしない |
| AC-026 | any failure with `promptSubmitted=false` or unknown | invocation-level harvest builder calls 0、capture builder calls 0 |
| AC-027 | each REQ-030 internal class | exact public status/reason pair equals the authoritative mapping; no alternative pair accepted |
| AC-028 | many-to-one mapping audit | only capability/profile、runtime unavailable、artifact validation families are many-to-one; five stage-specific classes remain distinct |

Authoritative mapping asserted by AC-027:

| Internal failure class | Public status | Public reason | Contract status |
|---|---|---|---|
| executable / managed Chrome unavailable | `blocked` | `oracle_unavailable` | existing reason retained |
| `profile_unsupported` / required capability missing / `prompt_submitted=unknown` / required profile builder missing | `blocked` | `oracle_capability_unsupported` | existing reason retained; allowed many-to-one capability family |
| `model_selection_unavailable` after the permitted retry is unavailable or exhausted | `blocked` | `oracle_model_selection_unavailable` | new public reason |
| `attachment_submission_failed` after the permitted inline path is unavailable or exhausted | `blocked` | `oracle_attachment_submission_failed` | new public reason |
| `prompt_reconstruction_mismatch` | `blocked` | `oracle_prompt_reconstruction_mismatch` | new public reason |
| `generation_incomplete` after one characterized same-session harvest | `blocked` | `oracle_generation_incomplete` | new public reason |
| characterized recovery command cannot be executed safely, or same-session state remains undecidable for infrastructure reasons | `blocked` | `oracle_session_recovery_required` | existing reason retained; not a known-stage catch-all |
| `output_download_failed` after one characterized same-session capture | `blocked` | `oracle_output_download_failed` | new public reason |
| expected artifact absent after terminal capture | `rejected` | `oracle_artifact_missing` | existing reason retained |
| multiple candidate artifacts | `rejected` | `oracle_artifact_ambiguous` | existing reason retained |
| path / mode / size / SHA / validation / ZIP / JSON defect | `rejected` | `oracle_artifact_rejected` | existing reason retained; allowed many-to-one validation family |

## 13. 停止・撤回条件

次のいずれかでは Oracle `0.17.0` profile を production formal operationへ昇格しない、または昇格済み profileを撤回する。

1. representative promptが複数のclean browser stateでreconstruction mismatchを再現する。
2. successful submissionに対するmodel verified / observed model evidenceを取得できない。
3. direct attachmentが不安定で、inlineを使うためにSpecDock側materializationが必要になる。
4. `promptSubmitted`相当を判定できず、pre-submit harvest/capture 0を保証できない。
5. 0.17のversion-specific harvest / capture commandをcharacterizeできない、またはgeneric hardcoded argvが残る。
6. `0.17.0` session metadata / artifact schemaをversioned readerで安全に検証できない。
7. response完成後のdownload / ZIP captureをsame-sessionで回復できず、output validator緩和が必要になる。
8. required configをexplicit argvで固定できず、private config / target URLの解析がproduct責務になる。
9. personal wrapper、API、alternate model、default branch fallbackが必要になる。
10. REQ-030 exact status/reason mappingまたはmany-to-one制約をdomain / CLI / testsで固定できない。
11. Candidate / Review / Human / apply regressionまたはprovider projection不一致が残る。

停止時はREQ-030のauthoritative content-free reasonとevidence gapを記録し、推測で続行しない。

## 14. トレーサビリティ

| Requirement | Design | Plan | Decision record |
|---|---|---|---|
| REQ-001–020 | Design 3–7, 14–19 | S01–S08 | prior D-001–D-010 retained |
| REQ-021–023 | Design 6–7 | S09 | ADR Decision 1–2 |
| REQ-024–025 | Design 8–9 | S09, S11 | ADR Decision 3 |
| REQ-026–028 | Design 6, 10–12 | S09–S11 | ADR Decision 1, 4 |
| REQ-029 | Design 6, 11, 13 | S09, S12 | ADR Decision 1, 5 |
| REQ-030 | Design 15 | S10, S12 | ADR Decision 6 |
| REQ-031–032 | Design 12, 16 | S10–S13 | ADR Decision 4, 7 |
| REQ-033 | Design 17 | S11–S13 | ADR migration / withdrawal |

## 15. 未検証主張

この Candidate は次をPASSと主張しない。

- PATH-resolved Oracle `0.17.0` がdirect / inline attachmentを正しく扱うこと。
- Oracle `0.17.0` が`promptSubmitted`、model verified、response completionをどのexact fieldで保存すること。
- `GPT-5.6 Sol` がlogical `Pro`の恒久mappingであること。
- standard targetとproject targetのどちらがformal operationに適すること。
- existing `0.16.1` artifact readerを定数変更だけで`0.17.0`に使えること。
- Issue #354 のproduction implementationが完了していること。

## 16. 完了条件

- 本Candidateがfresh Redでreviewされ、Humanが採用対象を明示する。
- S01–S08の既存Option A/C implementation planとS09–S13の0.17増分が実装・検証される。
- exact 0.17 profile、profile-owned harvest/capture builders、stage evidence、bounded recovery、authoritative public mapping、versioned artifact reader、browser smokeがpassする。
- output / source / authority / projection regressionがpassする。
- implementation reportのEvidence Adoption Ledgerに外部観測の採否とdirect Oracle evidenceを分けて記録する。
- PR、merge、Issue closeはowning workflowで別途判断する。

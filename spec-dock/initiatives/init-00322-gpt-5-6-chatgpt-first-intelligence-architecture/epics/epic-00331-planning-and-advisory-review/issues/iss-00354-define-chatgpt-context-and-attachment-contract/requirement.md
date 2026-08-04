---
種別: 要件定義書（Issue）
ID: "iss-00354"
タイトル: "ChatGPT Context and Attachment Contract"
状態: "draft"
作成者: "ChatGPT Blue Team authoring planner"
最終更新: "2026-08-04"
親: ["epic-00331", "init-00322"]
---

# iss-00354 ChatGPT Context and Attachment Contract 要件定義書

> **Candidate / evidence-only**  
> この文書は `CAND-ISS-00354-20260803T172642Z` に含まれる未採用の Blue Team Candidate である。canonical
> `requirement.md` を上書きせず、Red Team review、Human approval、`planning apply`、実装承認の
> いずれも表さない。

## 1. 文書の位置づけ

本 Issue は、SpecDock が ChatGPT を Issue planning、formal review、semantic revision で利用する際の
入力を、次の二層へ分離する契約を定義する。

1. ChatGPT のチャット本文: 作業を開始するための最小限の命令と identity。
2. 添付: 詳細な作業手順、判断観点、出力説明、対象 evidence、補足資料。

中心対象は既存の Issue Planning runtime である。clarification と将来の product-owned ChatGPT operation
については、同じ分離原則を再利用できる境界まで定義する。personal `chatgpt-use` wrapper や任意の
operator consultation は product runtime dependency にしない。

この Issue は既存の Candidate / Review / Human / apply lifecycle、direct Oracle adapter、exact GitHub
identity gate、output ZIP / closed JSON validator を置き換えない。変更対象は主として ChatGPT 呼出し前の
prompt synthesis と input attachment transport である。

## 2. 確認済み source identity

| 項目 | 値 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Source HEAD | `88a9fdb567f17f50bee421862d3b7859a5eb6384` |
| Initiative | `init-00322` / GPT-5.6 ChatGPT First Intelligence Architecture |
| Epic | `epic-00331` / Planning and Advisory Review |
| Issue | `iss-00354` / Define ChatGPT Context and Attachment Contract |
| Parent Issue | GitHub Issue `#334` |
| Assurance profile | `standard` / provisional |

指定 branch は GitHub Connector 上で存在し、指定 source HEAD と差分ゼロであることを確認した。
default branch は参照元へ切り替えていない。

## 3. 背景と現状

source HEAD 時点の実装は、Issue Planning lifecycle と output validation を既に備えている。一方、入力側は
次の強い契約を持つ。

- `issue_planning_prompt.py` が canonical document と `relevant_source_paths` を個別に読み込む。
- UTF-8、regular file、非 symlink、件数、byte 数、secret-like content、private path を検査する。
- role resource、GitHub gate、attachment index、SHA-256、output expectation、transport contract を
  一つの長い本文へ連結する。
- `issue_planning_chatgpt.py` が一時 prompt pack を生成し、`context-NNN.md`、`manifest.json`、
  `source-manifest.json`、`provenance.json`、`stale-if.json` を書き出す。
- `planning create --context-manifest` が individual path と operator context を closed JSON で受け取る。
- Planner / Semantic Revision は authoring ZIP、Reviewer は closed JSON を返し、Runtime が output を
  厳格に検証する。
- phase ごとに新しい Oracle session を作成し、同一 invocation 内の harvest recovery だけを行う。

入力側の前半四項目は、ユーザーが最終採用した Option A / Option C と矛盾する。後半の exact GitHub gate、
direct Oracle、output validation、Human authority は維持対象である。

## 4. 採用済み方針

### 4.1 Option A: 本文と添付の役割分離

- 本文は目的、operation、repository、branch、source HEAD、Issue / Epic / Initiative identity、
  authority / mutation prohibition、期待 output 種別に限定する。
- 詳細手順、レビュー観点、revision 規則、context 説明、出力 schema や例は Markdown 添付へ移す。
- operation ごとに本文 template と attachment directory を別々に保守する。
- `requirement.md`、`design.md`、`plan.md` の内容構成を過剰に固定せず、必要な completeness と
  traceability を満たす範囲で ChatGPT の判断力を使う。
- 添付文書は instruction を含み得る。既存の「attachments are reference-only / data-only」という
  親 Epic と runtime prompt の記述は更新対象である。

### 4.2 Option C: 添付ディレクトリの単純な引渡し

- operation-specific attachment directory は、その directory path 自体を Oracle transport へ渡す。
- SpecDock は directory tree を事前走査しない。entry ごとの `stat`、open、read、decode、hash、
  rename、copy、archive、filter、classification を行わない。
- filename、content、extension、hidden entry、symlink、special file、subdirectory の意味を判定しない。
- count、size、transport limit、path、secret 混入を独自 policy で検査しない。
- manifest、checksum、`context-NNN.md`、text conversion、automatic ZIP を入力側に生成しない。
- transport が扱えない場合は Oracle / ChatGPT の通常の失敗として扱う。特定 entry の除外、変換、
  retry、default branch fallback を自動実施しない。
- attachment directory へ適切な material を置く責任は operation pack の保守者または operator が負う。

### 4.3 継続スレッド

- Clarification、Planning、Blue Team Semantic Revision は、identity が再検証できる範囲で同一 Blue
  thread を継続する。
- Candidate version ごとの Formal Red Team Review は、必ず fresh read-only Red thread で実行する。
- Blue thread が利用不能、期限切れ、別 repository / branch、source HEAD 不一致、Candidate lineage
  不明である場合、旧 thread を黙って再利用しない。
- lineage が一意なら、現在の完全 identity、本文、添付一式で新規 Blue thread を開始する。
- lineage が曖昧なら Human confirmation まで停止する。
- input attachment manifest / checksum を thread 再開条件へ使わない。

## 5. 用語

| 用語 | 定義 |
|---|---|
| Minimal body | operation を開始するための目的、identity、authority、output 種別だけを含む本文 |
| Operation pack | operation 固有の minimal body template と attachment directory の組 |
| Static attachments | provider-owned operation directory 配下の詳細 instruction / guidance |
| Dynamic attachments | Candidate ZIP、Review JSON など invocation ごとに存在する既存 file path |
| Blue thread | clarification / planning / semantic revision の authoring 文脈を継続する thread |
| Red thread | Candidate version ごとに新規作成する read-only defect review thread |
| Output validation | ChatGPT が返した ZIP / JSON の形式、identity、inventory を Runtime が検査すること |
| Input inspection | 添付 directory の entry を SpecDock が事前に読み、分類、除外、変換、hash すること |
| Evidence-only | canonical adoption、review PASS、Human approval、execution-ready を付与しない状態 |

## 6. スコープ

### 6.1 In scope

- Issue Planning の prompt synthesis。
- provider-owned operation resources。
- operation-specific attachment directory の direct transport。
- Planner、Reviewer、Semantic Revision の dynamic attachment path 引渡し。
- Blue continuity / fresh Red policy を支える provider-owned thread binding。
- `planning create` の旧 `--context-manifest` から directory-oriented input への移行。
- provider source、installed assets、dogfooding projection の同期。
- focused unit / integration / CLI tests。
- Issue Planning skill、workflow docs、prompt pack reference、親 Epic の矛盾箇所の更新。
- clarification へ再利用可能な operation contract と入力例。

### 6.2 Out of scope

- personal `chatgpt-use` wrapper の product runtime 組込み。
- OpenAI API fallback、arbitrary backend、default branch fallback。
- ChatGPT による repository、Git、GitHub、canonical docs、Issue state の mutation。
- Candidate の自動採用、Red Team verdict の生成、Human approval の推測。
- output ZIP / Review JSON safety contract の緩和。
- generic content classifier、DLP、secret scanner、attachment quota manager。
- clarification の新しい public CLI を、既存の owning workflow を確認せず追加すること。
- PR、commit、push、merge、Issue close。

## 7. 利用者と責務

| Actor | 責務 |
|---|---|
| Human / Issue owner | scope、user intent、ambiguous lineage、final adoption を決定する |
| Main orchestrator / Codex | exact target を選び、operation を開始し、Candidate / Review / Human gate を管理する |
| SpecDock application | typed identity、preflight、operation selection、thread policy、postflight を制御する |
| Prompt synthesizer | minimal body を生成し、attachment path を materialize せず transport へ渡す |
| Direct Oracle adapter | provider-owned direct invocation、managed Chrome、session / thread transport、typed output 取得 |
| Operation pack maintainer | attachment directory に適切な instruction / material を置く |
| ChatGPT Blue | authoring / revision Candidate を生成する。mutation や adoption はしない |
| ChatGPT Red | fresh read-only defect review を closed JSON で返す。修正しない |
| Runtime output validator | ZIP / JSON、Candidate identity、Review identity を検証する |
| Human approver | exact PASS Review と Candidate identity に bind した adoption を承認する |

## 8. ユースケース

### UC-001 Issue planning

1. Runtime が current Issue、parent、repository、branch、HEAD を解決する。
2. exact GitHub preflight が pass する。
3. Runtime は planning minimal body を生成する。
4. provider planning attachment directory と optional operator attachment directory を path のまま渡す。
5. ChatGPT が repository を exact branch / HEAD で確認し、authoring ZIP を返す。
6. Runtime が ZIP を既存契約で検証し、evidence-only Candidate を発行する。

### UC-002 Formal review

1. exact Candidate identity と source identity を固定する。
2. fresh Red thread を開始する。
3. review minimal body、review attachment directory、Candidate ZIP、必要な formal evidence path を渡す。
4. Red は read-only defect-only review を行い、closed JSON を返す。
5. Runtime が Review identity と schema を検証する。

### UC-003 Semantic revision

1. P0 / P1 finding と exact failed Review を選ぶ。
2. verified Blue thread が継続可能なら同 thread を使う。
3. 継続不能なら、lineage を検証して新規 Blue threadへ完全入力を再提示する。
4. revision attachment directory、prior Candidate、Review result を path のまま渡す。
5. revised authoring ZIP を既存 output validator で検証し、新 Candidate とする。

### UC-004 Clarification reuse

clarification workflow は、minimal body と operation attachment directory の同じ構造を利用できる。
ただし source HEAD 時点では clarification は skill-owned workflow であり、Issue #354 は public command を
新設せず contract と resource convention を定義する。provider-owned direct Oracle invocation へ接続する
場合は owning workflow の後続 Issue で明示的に配線する。

## 9. 機能要件

### ISS354-REQ-001 Exact GitHub identity

Runtime は formal operation 前に `chemitaro/spec-dock` の named current branch と source HEAD を検証しなければ
ならない。default branch、別 branch、添付、memory、一般知識を代替 source にしてはならない。

### ISS354-REQ-002 Minimal body

各 operation の本文は、少なくとも次を含まなければならない。

- operation 名と目的。
- repository、branch、source HEAD。
- Initiative、Epic、Issue identity。
- ChatGPT の authority と mutation prohibition。
- 期待 output 種別。
- attached instructions を読む指示。
- exact GitHub access 不可時の hard failure。

本文へ詳細手順、全文 template、attachment inventory、attachment SHA、entry-specific policy を埋め込んでは
ならない。

### ISS354-REQ-003 Operation-specific resources

Planning、Review、Semantic Revision はそれぞれ provider-owned な `prompt.md` と `attachments/` を持たなければ
ならない。attachment file の追加・削除だけで application code の変更を要求してはならない。

### ISS354-REQ-004 Direct directory transport

Static attachment directory は directory path のまま direct Oracle へ渡さなければならない。SpecDock は
配下 entry を列挙して別の temporary pack へ再構成してはならない。

### ISS354-REQ-005 No input entry inspection

SpecDock は input attachment directory に対し、次を行ってはならない。

- filename / extension / hidden / symlink / special file / subdirectory classification。
- file read、UTF-8 decode、content scan、secret scan、private-path scan。
- size / count / quota / transport capability precheck。
- manifest / checksum / source hash の生成または照合。
- automatic exclude、rename、copy、text conversion、ZIP conversion。

既知の `prompt.md` を本文 template として読むこと、typed repository identity を検証すること、output を検証する
ことは、本要件が禁止する input entry inspection ではない。

### ISS354-REQ-006 Dynamic attachment paths

Candidate ZIP、Review JSON、revision request など既存の invocation-specific evidence は、内容を別ファイルへ
複製せず、その original path を direct Oracle の attachment 引数へ渡さなければならない。formal identity 用の
Candidate SHA / Review SHA は既存 evidence binding として維持できるが、attachment directory の manifest SHA
として扱ってはならない。

### ISS354-REQ-007 No generated input pack

現在の `context-NNN.md`、`.specdock-authoring-pack`、input `manifest.json`、`source-manifest.json`、
`provenance.json`、`stale-if.json` を生成する transport pack は廃止しなければならない。output Candidate が
持つ provenance / identity は別責務として維持する。

### ISS354-REQ-008 Normal transport failure

attachment submission が失敗した場合、既存の Oracle / ChatGPT transport error として operation を停止する。
SpecDock は失敗 entry を推測して除外、変換、分割、retry、別 backend、別 branch へ切り替えてはならない。

### ISS354-REQ-009 Planning / Revision output

Planner と Semantic Revision は、directory structure を保持した一つの downloadable authoring ZIP を返す。
canonical three documents と exactly-one onboarding companion の既存必須 inventory は維持する。
文書本文の heading 数、表現、diagram 数を必要以上に固定してはならない。

この手動 Candidate に含まれる補助 artifact は今回の evidence-only deliverable 固有であり、既存 runtime
authoring ZIP の canonical inventory を暗黙に拡張しない。

### ISS354-REQ-010 Review output

Formal Reviewer は fresh read-only thread から closed JSON を一つだけ返す。既存の reviewed identity、
identity digest、verdict、findings schema と P0 / P1 blocking rule を維持する。

### ISS354-REQ-011 Blue continuity

Planning と Semantic Revision は、同一 Issue の verified Blue thread を継続できなければならない。
thread binding は repository、branch、source HEAD、Issue、Candidate lineage と照合する。

### ISS354-REQ-012 Fresh Red

Review は Candidate version ごとに fresh Red thread を開始しなければならない。Blue thread、過去 Red thread、
別 Candidate の PASS を再利用してはならない。

### ISS354-REQ-013 Continuity recovery

Blue thread を検証できない場合は旧 thread を authoritative とみなさず、新規 Blue thread へ現在の minimal body、
static attachment directory、dynamic evidence path を完全に提示する。Candidate lineage が一意でない場合は
Human confirmation を要求する。

### ISS354-REQ-014 Thread evidence boundary

opaque thread handle は adapter-private operational state とし、Candidate ZIP、Review JSON、canonical docs、
public command result、raw transcript へ含めてはならない。durable evidence は「verified continuation」または
「new Blue after continuity failure」と source / Candidate identity を記録し、provider session identifier は記録しない。

### ISS354-REQ-015 Authority boundary

ChatGPT は canonical adoption、review approval、Human approval、implementation authorization、commit、push、
merge、Issue completion を行ってはならない。Candidate / Review は evidence-only である。

### ISS354-REQ-016 Direct Oracle only

Runtime の外部 product execution dependency は PATH-resolved direct Oracle と managed Chrome contract のまま
維持する。personal wrapper、API fallback、arbitrary backend を追加してはならない。

### ISS354-REQ-017 Output validation retention

次を維持しなければならない。

- authoring ZIP snapshot / logical filename / internal root / inventory validation。
- strict Review JSON parsing。
- Candidate / Review / Human identity binding。
- exact GitHub preflight / postflight と source staleness checks。
- managed Chrome / Oracle executable / session artifact boundary。
- Candidate publication と apply transaction safety。

### ISS354-REQ-018 Provider / projection parity

変更は provider source を正本とし、installed assets と dogfooding projection を同一 closure で更新する。
少なくとも runtime、operation resources、skills、docs の provider / dogfood parity を test で固定する。

### ISS354-REQ-019 CLI migration

`planning create --context-manifest` は individual source path / operator text の旧契約であるため、directory-oriented
input へ hard cutover する。推奨 public surface は optional repeatable `--attachment-dir <path>` とし、値は
content inspection せず attachment path として渡す。旧 JSON を黙って directory pack へ変換してはならない。

実際の flag 名と repeatability は既存 CLI grammar と Oracle capability characterization 後に確定するが、
旧 semantic を維持する compatibility parser は作らない。

### ISS354-REQ-020 Parent documentation consistency

親 Epic の「detailed role / task / output contract は本文に置き、attachments は reference-only」という記述、
Issue Planning skill の `--context-manifest` 説明、prompt pack docs の input manifest / safety 説明を、採用した
Option A / C と整合させなければならない。output ZIP safety lane は削除してはならない。

## 10. 非機能要件

### ISS354-NFR-001 保守性

operation attachment の追加・削除は resource tree の変更だけで完結し、application code と test inventory の
手修正を要求しない。

### ISS354-NFR-002 単純性

Runtime は attachment directory の内容を理解しない。責務は「選ばれた path を direct Oracle に渡す」までとする。

### ISS354-NFR-003 観測可能性

公開 status / reason は content-free とする。transport failure 時に filename、secret-like value、private absolute
path、raw transcript を diagnostic へ露出しない。ただし entry を安全判定して除外するための scanner は作らない。

### ISS354-NFR-004 再現性

minimal body は同一 typed identity / operation / output expectation に対して deterministic である。
attachment directory の contents order や transport 内部表現を SpecDock が再構成して deterministic にしようとしては
ならない。

### ISS354-NFR-005 Portability

macOS / Linux の filesystem entry 差異を application layer が意味解釈しない。Oracle が受け取る path contract の
みを使用する。

### ISS354-NFR-006 後方境界

Issue Planning lifecycle の public success / failure semantics、Candidate identity、Review schema、apply authority を
不要に変更しない。

## 11. 受け入れ基準

| ID | Given | When | Then |
|---|---|---|---|
| AC-001 | planning operation resource に nested file が追加された | `planning create` を組み立てる | code変更なしで同じ attachment directory path が Oracle へ渡る |
| AC-002 | directory に hidden file、symlink、FIFO などがある | adapter argv を組み立てる | SpecDock は tree を走査、open、hash、exclude せず directory path だけを渡す |
| AC-003 | Oracle が attachment を拒否する | operation を実行する | normal transport failure で停止し、個別除外、ZIP化、fallback を行わない |
| AC-004 | same Issue / branch / HEAD / lineage の verified Blue binding がある | semantic revision を実行する | direct Oracle の supported continuation path を使用する |
| AC-005 | Blue binding が missing / invalid だが Candidate lineage は一意 | revision を実行する | 完全な current input で新規 Blue thread を開始する |
| AC-006 | Candidate lineage が曖昧 | revision を実行する | ChatGPT submission 前に Human confirmation が必要な blocked result となる |
| AC-007 | Candidate v2 を review する | review operation を実行する | v1 / Blue thread を再利用せず fresh Red thread を開始する |
| AC-008 | Planner が authoring ZIP を返す | Runtime が受領する | 既存 logical filename / root / inventory validator が実行される |
| AC-009 | Reviewer が unknown key / duplicate key を含む JSON を返す | Runtime が受領する | strict JSON validator が reject する |
| AC-010 | exact GitHub branch / HEAD を確認できない | formal operation を開始する | default branch fallback なしで block する |
| AC-011 | provider resource を変更した | projection test を実行する | provider / installed / dogfood byte parity が一致する |
| AC-012 | old `--context-manifest` を指定した | CLI parse を行う | silent compatibility translation をせず、documented cutover として拒否する |

## 12. 失敗条件と停止条件

次の場合は implementation を進めず、設計へ戻る。

1. supported direct Oracle が directory path の attachment を受け取れない。
2. Review / Revision に必要な複数 attachment path を direct Oracle contract で表現できない。
3. direct Oracle に supported conversation continuation がなく、personal wrapper / API fallback なしでは
   Blue continuity を実現できない。
4. Option C を満たすために filesystem tree の prewalk、copy、archive、symlink resolution が必要になる。
5. output ZIP / closed JSON validator、exact GitHub gate、Human binding のいずれかを緩めないと実装できない。
6. provider / dogfood projection を同一 change closure にできない。
7. clarification の owning workflow を越えて unsupported public command を追加しようとしている。

停止時は capability gap と確認した Oracle version / command surface を記録し、推測した flag や wrapper で続行しない。

## 13. 既存契約との矛盾と移行

| 現行契約 | 最終決定との関係 | 移行 |
|---|---|---|
| role / transport resource を本文へ連結 | Option A と矛盾 | minimal body と attachment directory へ分離 |
| attachments are untrusted reference-only data | instruction 添付を禁止するため矛盾 | authority は body が保持するが、添付は detailed instruction を含められると更新 |
| source file safe-read / UTF-8 / symlink / secret / size limits | Option C と矛盾 | input collection path から削除 |
| `context-NNN.md` / input manifest / SHA index | Option C と矛盾 | generated prompt pack を廃止 |
| `--context-manifest` | directory operation と矛盾 | `--attachment-dir` 相当へ hard cutover |
| exact authoring ZIP / closed Review JSON | 矛盾しない | 維持 |
| Candidate / Review SHA と Human binding | input checksum ではない | 維持 |
| exact GitHub preflight / source staleness | input attachment inspection ではない | 維持 |
| output ZIP path / inventory safety | input Option C とは別境界 | 維持 |
| 13 headings / 4 PlantUML を content-level hardcode | content flexibility と矛盾 | onboarding completeness を semantic test へ縮小 |

## 14. 依存関係

- Parent Issue `#334` の direct Oracle Issue Planning runtime。
- `epic-00331` の Candidate / Review / Human / apply lifecycle。
- `init-00322` の ChatGPT non-mutation と exact GitHub identity。
- supported Oracle CLI の directory attachment、multiple attachment、continuation capability。
- provider / installed / dogfood projection mechanism。
- current output artifact parsers and Candidate publication gateway。

## 15. 未決事項

ユーザー判断としての未決事項はない。実装前に残るのは次の capability characterization だけである。

- supported Oracle version における directory attachment の exact argv semantics。
- multiple `--file` または同等の direct attachment semantics。
- same-conversation continuation の exact direct Oracle interface。
- failure exit / session artifact が既存 public reason へどう正規化されるか。

これらは implementation choice ではなく stop / proceed 判定であり、unsupported 時に別 backend を推測しない。

## 16. トレーサビリティ

| 要件群 | 主な設計セクション | 主な計画マイルストーン |
|---|---|---|
| REQ-001, 015–017 | Design 3, 10, 13 | S01, S04, S08 |
| REQ-002–007 | Design 4–8, 12 | S02–S04 |
| REQ-008–010 | Design 9, 13 | S04, S05 |
| REQ-011–014 | Design 10–11 | S01, S06 |
| REQ-018–020 | Design 14–17 | S07, S08 |
| NFR-001–006 | Design 3, 8, 15–17 | 全マイルストーン |

## 17. 完了条件

- requirement / design / plan の canonical adoption は別途 fresh review と Human gate を通過する。
- focused tests が Option C の「no prewalk / no materialization」を直接証明する。
- direct Oracle adapter と output validators の既存 regression が pass する。
- provider / installed / dogfood parity が pass する。
- parent Epic / skill / docs の矛盾が解消される。
- `spec-dock validate`、Ruff、MyPy、focused / integration tests、`git diff --check` が pass する。
- report に implementation evidence、test result、remaining capability / follow-up を記録する。
